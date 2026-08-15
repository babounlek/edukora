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

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import SERIE_MAP
from catalog.ingestion_repairs import (
    _dedupe_exercise_heading,
    _dedupe_question_enonce,
    _series_tokens_from_folder_name,
)
from catalog.models import Cursus, Lesson, LessonType

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
        reperes = self._corriger_reperes(appliquer)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Séries : {series} leçon(s) complétée(s) | Repères : {reperes} exercice(s) dédupliqué(s)",
        ))

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
