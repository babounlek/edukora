"""
Reprise du contenu DÉJÀ en base après deux correctifs d'ingestion du 2026-08-15 :

1. `_merge_series_from_folder_name` : séries annoncées par le nom du dossier mais
   absentes du champ `serie` du JSON (62 dossiers / 244 fichiers) - une épreuve
   "bac-c-d-chimie-2003-cameroun" n'était rattachée qu'au cursus Série C, donc
   introuvable pour un candidat de Série D.
2. `_dedupe_exercise_heading` : repère "Exercice N" porté à la fois par l'intro de
   l'exercice et par la tête d'une de ses questions (108 fichiers / 32 épreuves),
   affiché jusqu'à trois fois d'affilée au lecteur.

Les deux correctifs ne valent que pour les ingestions FUTURES : ré-ingérer ne
retouche jamais un Exercise déjà importé (idempotence volontaire de run_ingestion).
D'où cette reprise, délibérément NON DESTRUCTIVE - elle modifie les lignes existantes
en place plutôt que de passer par `ingest_exercise(force=True)`, qui supprime puis
recrée l'Exercise et perdrait au passage les liens de traçabilité
quiz.CompetenceItem.source_exercises ainsi que toute correction faite à la main
depuis l'admin.

Idempotente : relancer ne change plus rien une fois la reprise faite.

    python manage.py corriger_series_et_reperes            # simulation
    python manage.py corriger_series_et_reperes --apply
"""

import re

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import SERIE_MAP, build_lesson_title
from catalog.ingestion_repairs import (
    _dedupe_exercise_heading,
    _dedupe_question_enonce,
    _series_tokens_from_folder_name,
)
from catalog.models import Cursus, Lesson, LessonType
from catalog.rendering import _render_question_enonce

# Le nom du dossier et le contenu du JSON se contredisent franchement (pas un simple
# oubli) : l'arbitrage se fait sur le PDF source, jamais ici - voir la docstring de
# _merge_series_from_folder_name.
CONTRADICTIONS = {
    "bac-a-maths-2003-cameroun",
    "bac-c-svt-2015-cameroun",
    "probatoire-c-d-chimie-2013-cameroun",
}


class Command(BaseCommand):
    help = "Applique au contenu déjà en base les correctifs séries + repères d'exercice."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Écrit réellement les corrections (sans cette option : simulation seule).",
        )

    def handle(self, *args, **options):
        appliquer = options["apply"]
        self.stdout.write(self.style.MIGRATE_HEADING(
            "APPLICATION" if appliquer else "SIMULATION (relancer avec --apply pour écrire)",
        ))
        series = self._corriger_series(appliquer)
        titres = self._corriger_titres(appliquer)
        reperes = self._corriger_reperes(appliquer)
        corps = self._corriger_corps_recopie(appliquer)
        romains = self._recompiler_marqueurs_romains(appliquer)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Séries : {series} leçon(s) complétée(s) | Titres : {titres} rafraîchi(s) | "
            f"Repères : {reperes} exercice(s) dédupliqué(s) | Corps recopié : {corps} question(s) | "
            f"Marqueurs romains : {romains} exercice(s) recompilé(s)",
        ))

    def _recompiler_marqueurs_romains(self, appliquer):
        """
        `Exercise.enonce_markdown` est un champ COMPILÉ depuis les Question : le
        correctif de rendering._strip_redundant_local_marker (marqueur "ii." redoublé
        par le préfixe compilé) ne se voit donc qu'après recompilation.

        Ne recompile que les exercices réellement concernés - une sous-question dont le
        dernier segment de `numero` est alphabétique ET dont le texte commence par ce
        même marqueur - plutôt que tout le corpus : recompiler 1200 exercices pour en
        corriger une poignée ferait remonter autant de dates de modification sans raison.
        """
        self.stdout.write("\n== Marqueurs romains redoublés (recompilation) ==")
        touches = 0
        lessons = Lesson.objects.filter(lesson_type=LessonType.CORR).prefetch_related(
            "exercises__questions",
        )
        for lesson in lessons:
            for exercise in lesson.exercises.all():
                questions = list(exercise.questions.order_by("ordre"))
                concerne = False
                for question in questions:
                    segment = str(question.numero or "").rsplit(".", 1)[-1]
                    if not segment.isalpha():
                        continue
                    if re.match(rf"^\s*{re.escape(segment)}\s*[.):]", question.enonce_markdown, re.IGNORECASE):
                        concerne = True
                        break
                if not concerne:
                    continue
                # Recompilation à blanc, à l'identique de compile_exercise_from_questions,
                # pour que la simulation annonce ce qui CHANGERAIT et non ce qui a
                # simplement l'allure d'un cas concerné : la majorité de ces exercices
                # n'écopent d'aucun préfixe compilé (sous-question unique, ou repère déjà
                # reconnu par _ENONCE_ALREADY_LABELED_RE) et leur rendu est donc déjà bon.
                intro = f"{exercise.enonce_intro_markdown}\n\n" if exercise.enonce_intro_markdown else ""
                attendu = intro + "\n\n".join(
                    _render_question_enonce(question, len(questions) > 1) for question in questions
                )
                if attendu == exercise.enonce_markdown:
                    continue
                self.stdout.write(f"  {lesson.epreuve_source} ex.{exercise.numero_exercice}")
                touches += 1
                if appliquer:
                    exercise.compile_from_questions()
                    lesson.compile_from_exercises()
        return touches

    def _corriger_corps_recopie(self, appliquer):
        """
        Préambule de l'exercice recopié tel quel en tête de sa première sous-question :
        le lecteur le voit deux fois d'affilée, puisque la plateforme affiche l'intro
        puis chaque sous-question.

        `_dedupe_question_enonce` corrige déjà ce défaut, mais seulement à l'ingestion :
        le contenu importé avant son introduction ne l'a jamais vu passer. On rejoue
        donc la rustine sur l'existant. Idempotent par construction - elle ne retire que
        ce qui est un doublon exact du préambule, donc une seconde exécution ne trouve
        plus rien.
        """
        self.stdout.write("\n== Préambule recopié en tête de sous-question ==")
        touchees = 0
        lessons = Lesson.objects.filter(lesson_type=LessonType.CORR).prefetch_related(
            "exercises__questions",
        )
        for lesson in lessons:
            for exercise in lesson.exercises.all():
                modifiees = []
                for question in exercise.questions.order_by("ordre"):
                    nouveau = _dedupe_question_enonce(
                        question.enonce_markdown, exercise.enonce_intro_markdown,
                    )
                    if nouveau != question.enonce_markdown:
                        modifiees.append((question, nouveau))
                if not modifiees:
                    continue
                self.stdout.write(
                    f"  {lesson.epreuve_source} ex.{exercise.numero_exercice} "
                    f"({len(modifiees)} sous-question(s))",
                )
                touchees += len(modifiees)
                if not appliquer:
                    continue
                with transaction.atomic():
                    for question, nouveau in modifiees:
                        question.enonce_markdown = nouveau
                        question.save(update_fields=["enonce_markdown"])
                    exercise.compile_from_questions()
                lesson.compile_from_exercises()
        return touchees

    def _corriger_titres(self, appliquer):
        """
        Le titre n'est calculé qu'à la création du Lesson : une série rattachée après
        coup (voir _corriger_series juste au-dessus) laisse un titre périmé, du genre
        "Chimie BAC C et D 2025" pour une épreuve désormais ouverte à la Série E.

        Ne réécrit QUE les titres manifestement auto-générés (ils commencent par le
        libellé de la matière et se terminent par l'année) : un titre retouché à la
        main depuis l'admin ne correspond plus à cette forme et reste intact. Le slug
        n'est jamais touché - il est figé à la création pour ne pas casser les URL déjà
        partagées et indexées.
        """
        self.stdout.write("\n== Titres périmés après complément de cursus ==")
        touches = 0
        lessons = (
            Lesson.objects.filter(lesson_type=LessonType.CORR)
            .prefetch_related("cursus__series", "cursus__country")
            .select_related("subject")
        )
        for lesson in lessons:
            cursus_list = list(lesson.cursus.all())
            if not cursus_list:
                continue
            attendu = build_lesson_title(
                lesson.subject, cursus_list, lesson.year, lesson.origine, lesson.etablissement,
                lesson.nature_epreuve, lesson.partie_epreuve_francais, lesson.variante_sujet,
                lesson.filiere_serie_a,
            )
            if attendu == lesson.title:
                continue
            auto_genere = lesson.title.startswith(lesson.subject.label) and (
                not lesson.year or lesson.title.rstrip().endswith(str(lesson.year))
            )
            if not auto_genere:
                self.stdout.write(self.style.WARNING(
                    f"  {lesson.title!r} : titre retouché à la main, laissé tel quel "
                    f"(attendu : {attendu!r}).",
                ))
                continue
            self.stdout.write(f"  {lesson.title!r} -> {attendu!r}")
            touches += 1
            if appliquer:
                lesson.title = attendu
                lesson.save(update_fields=["title", "updated_at"])
        return touches

    def _corriger_series(self, appliquer):
        self.stdout.write("\n== Séries manquantes sur le cursus des leçons ==")
        touchees = 0
        lessons = (
            Lesson.objects.filter(lesson_type=LessonType.CORR)
            .exclude(epreuve_source="")
            .prefetch_related("cursus__series")
            .select_related("subject__country")
        )
        for lesson in lessons:
            nom = lesson.epreuve_source.removesuffix(".pdf")
            if nom in CONTRADICTIONS:
                continue
            attendues = _series_tokens_from_folder_name(nom, SERIE_MAP)
            if not attendues:
                continue

            existants = list(lesson.cursus.all())
            if not existants:
                continue
            # Toutes les entrées d'une même leçon partagent examen et pays : la série
            # est la seule dimension qui varie d'un cursus à l'autre.
            examen = existants[0].examen
            country = existants[0].country_id
            deja = {c.series.code for c in existants if c.series}

            manquants = []
            for token in attendues:
                code = SERIE_MAP.get(token)
                if not code or code in deja:
                    continue
                cursus = Cursus.objects.filter(
                    country_id=country, examen=examen, series__code=code,
                ).first()
                if cursus is None:
                    self.stdout.write(self.style.WARNING(
                        f"  {nom} : aucun Cursus ({examen}, série {code}) pour ce pays - ignoré.",
                    ))
                    continue
                manquants.append(cursus)

            if not manquants:
                continue
            ajoutes = ", ".join(c.series.code for c in manquants)
            self.stdout.write(f"  {nom:52s} + série(s) {ajoutes}")
            if appliquer:
                lesson.cursus.add(*manquants)
            touchees += 1
        return touchees

    def _corriger_reperes(self, appliquer):
        self.stdout.write("\n== Repères d'exercice dupliqués (intro + tête de question) ==")
        touches = 0
        lessons = Lesson.objects.filter(lesson_type=LessonType.CORR).prefetch_related(
            "exercises__questions",
        )
        for lesson in lessons:
            for exercise in lesson.exercises.all():
                questions = list(exercise.questions.order_by("ordre"))
                if not questions:
                    continue
                payload = {
                    "enonce_intro_markdown": exercise.enonce_intro_markdown,
                    "questions": [
                        {"enonce_markdown": q.enonce_markdown, "pk": q.pk} for q in questions
                    ],
                }
                corrige, modifie = _dedupe_exercise_heading(payload)
                if not modifie:
                    continue

                nouvelle_intro = corrige["enonce_intro_markdown"]
                par_pk = {}
                for entree in corrige["questions"]:
                    # Même enchaînement qu'à l'ingestion : le repère retiré, le corps de
                    # l'intro éventuellement recopié dans la question l'est à son tour.
                    par_pk[entree["pk"]] = _dedupe_question_enonce(
                        entree["enonce_markdown"], nouvelle_intro,
                    )

                self.stdout.write(f"  {lesson.epreuve_source} ex.{exercise.numero_exercice}")
                touches += 1
                if not appliquer:
                    continue
                with transaction.atomic():
                    exercise.enonce_intro_markdown = nouvelle_intro
                    exercise.save(update_fields=["enonce_intro_markdown"])
                    for question in questions:
                        nouveau = par_pk.get(question.pk)
                        if nouveau is not None and nouveau != question.enonce_markdown:
                            question.enonce_markdown = nouveau
                            question.save(update_fields=["enonce_markdown"])
                    # enonce_markdown de l'Exercise est un champ COMPILÉ depuis les
                    # questions (voir rendering.compile_exercise_from_questions) : sans
                    # cette recompilation, le lecteur continuerait d'afficher le doublon.
                    exercise.compile_from_questions()
                lesson.compile_from_exercises()
        return touches
