"""
Reprise du contenu DÉJÀ en base après la décision utilisateur du 2026-09-07 de
dissocier Histoire et Géographie (voir SUBJECT_FAMILIES dans catalog.models et
MATIERE_MAP dans catalog.ingestion) - le nouveau mapping ne vaut que pour les
ingestions FUTURES, ré-ingérer ne retouche jamais un Lesson déjà en base dont la
Subject a changé (voir la "promotion, jamais de retour en arrière" dans
ingest_exercise : elle protège les épreuves réellement combinées, mais empêche
symétriquement de corriger celles qui n'auraient jamais dû l'être).

15 Lesson étaient rattachées à HISTOIRE_GEO au 2026-09-07, vérifiées une par une sur
le "matiere" du JSON source de chacun de leurs exercices (voir HISTOIRE_SEULE/
GEOGRAPHIE_SEULE ci-dessous) : 12 n'examinent qu'une seule discipline (mal
rattachées à l'époque où "histoire"/"geographie" pointaient toutes deux vers
HISTOIRE_GEO) et sont reclassées ici. Les 3 restantes (bepc-histoire-2008/2017/2020-
officiel-cameroun) ont bien "matiere": "Histoire-Géographie" dans leur JSON source -
laissées sous HISTOIRE_GEO, volontairement absentes des listes ci-dessous.

Non destructive - modifie Lesson.subject/Lesson.title/Module.subject en place (id,
slug, Exercise/Question/Savoir/Tag.savoir_officiel inchangés - voir la docstring de
build_lesson_title : jamais le slug, figé à la création), jamais un ré-import.

Idempotente : relancer ne change plus rien une fois la reprise faite (recherche par
epreuve_source, pas par Subject.code actuel - fonctionne aussi bien avant qu'après la
reprise, donc sans danger si la commande a déjà tourné une première fois avant l'ajout
du recalcul de titre).

    python manage.py corriger_histoire_geographie_split            # simulation
    python manage.py corriger_histoire_geographie_split --apply
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import build_lesson_title
from catalog.models import Lesson, Subject
from programme.models import Module

# epreuve_source -> nouveau code Subject, pour les Lesson dont TOUS les exercices du
# JSON source n'ont qu'une seule matière (voir la docstring ci-dessus).
HISTOIRE_SEULE = {
    "bepc-histoire-2025-cameroun.pdf",
    "bepc-histoire-2024-blanc-cameroun",
    "bepc-histoire-2018-cameroun.pdf",
}
GEOGRAPHIE_SEULE = {
    "bac-c-d-ti-geographie-2025-cameroun.pdf",
    "bac-c-d-ti-geographie-2024-cameroun.pdf",
    "bac-c-d-ti-geographie-2023-cameroun.pdf",
    "bac-c-d-e-ti-geographie-2022-cameroun.pdf",
    "probatoire-a-abi-geographie-2022-cameroun.pdf",
    "bepc-geographie-2021-zero-cameroun.pdf",
    "bepc-geographie-2019-cameroun.pdf",
    "probatoire-c-d-e-ti-geographie-2018-cameroun.pdf",
    "bepc-geographie-2026-cameroun",
}


class Command(BaseCommand):
    help = "Applique au contenu déjà en base la dissociation Histoire/Géographie."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Écrit réellement les corrections (sans cette option : simulation seule).",
        )

    def handle(self, *args, **options):
        appliquer = options["apply"]

        # Recherche par epreuve_source seul (pas par Subject.code actuel) : reste
        # correct que le Lesson soit encore sous HISTOIRE_GEO ou déjà reclassé par un
        # run précédent de cette commande.
        lessons_par_code = {}
        for epreuve_source, code in [*((s, "HISTOIRE") for s in HISTOIRE_SEULE), *((s, "GEOGRAPHIE") for s in GEOGRAPHIE_SEULE)]:
            lesson = Lesson.objects.filter(epreuve_source=epreuve_source).select_related("subject__country").prefetch_related("cursus").first()
            if lesson is None:
                self.stdout.write(self.style.WARNING(f"Lesson introuvable pour epreuve_source={epreuve_source!r}"))
                continue
            lessons_par_code.setdefault(code, []).append(lesson)

        modules_h = Module.objects.filter(subject__code="HISTOIRE_GEO", numero__startswith="H")
        modules_g = Module.objects.filter(subject__code="HISTOIRE_GEO", numero__startswith="G")

        # Titre recalculé (jamais le slug, figé à la création - voir la docstring de
        # build_lesson_title) seulement si l'actuel correspond exactement à ce que
        # build_lesson_title aurait produit sous l'ancienne Subject HISTOIRE_GEO -
        # récupérée explicitement par (pays, code) plutôt que via lesson.subject, qui
        # peut déjà pointer vers la nouvelle Subject si la commande a déjà tourné une
        # première fois. Un titre retouché à la main depuis (même logique de garde-fou
        # que corriger_series_et_reperes) est laissé tel quel.
        plan = []
        for code, lessons in lessons_par_code.items():
            for lesson in lessons:
                cursus_list = list(lesson.cursus.all())
                histoire_geo = Subject.objects.get(country=lesson.subject.country, code="HISTOIRE_GEO")
                nouveau_subject = Subject.objects.get(country=lesson.subject.country, code=code)
                ancien_attendu = build_lesson_title(
                    histoire_geo, cursus_list, lesson.year, lesson.origine, lesson.etablissement,
                    lesson.nature_epreuve, lesson.partie_epreuve_francais, lesson.variante_sujet,
                    lesson.filiere_serie_a,
                )
                nouveau_attendu = build_lesson_title(
                    nouveau_subject, cursus_list, lesson.year, lesson.origine, lesson.etablissement,
                    lesson.nature_epreuve, lesson.partie_epreuve_francais, lesson.variante_sujet,
                    lesson.filiere_serie_a,
                )
                # lesson.title == nouveau_attendu : déjà repris par un run précédent,
                # rien à re-signaler comme "retouché à la main".
                auto_genere = lesson.title in (ancien_attendu, nouveau_attendu)
                nouveau_titre = nouveau_attendu if auto_genere else None
                plan.append((lesson, nouveau_subject, nouveau_titre))
                if not auto_genere:
                    self.stdout.write(self.style.WARNING(
                        f"  {lesson.title!r} : titre retouché à la main, subject seul changé vers {code} "
                        f"(titre attendu si auto-généré : {ancien_attendu!r}).",
                    ))
                elif lesson.title != nouveau_attendu:
                    self.stdout.write(f"  {lesson.title!r} -> {nouveau_attendu!r} ({code})")
                else:
                    self.stdout.write(f"  {lesson.title!r} : déjà à jour ({code})")

        self.stdout.write(
            f"{len(lessons_par_code.get('HISTOIRE', []))} Lesson -> HISTOIRE, "
            f"{len(lessons_par_code.get('GEOGRAPHIE', []))} Lesson -> GEOGRAPHIE, "
            f"{modules_h.count()} Module -> HISTOIRE, {modules_g.count()} Module -> GEOGRAPHIE.",
        )
        if not appliquer:
            self.stdout.write(self.style.WARNING("Simulation seule (--apply pour écrire)."))
            return

        with transaction.atomic():
            for lesson, nouveau_subject, nouveau_titre in plan:
                lesson.subject = nouveau_subject
                update_fields = ["subject", "updated_at"]
                if nouveau_titre is not None and nouveau_titre != lesson.title:
                    lesson.title = nouveau_titre
                    update_fields.append("title")
                lesson.save(update_fields=update_fields)

            for modules_qs, code in [(modules_h, "HISTOIRE"), (modules_g, "GEOGRAPHIE")]:
                for module in modules_qs.select_related("subject__country"):
                    module.subject = Subject.objects.get(country=module.subject.country, code=code)
                    module.save(update_fields=["subject"])

        self.stdout.write(self.style.SUCCESS("Dissociation Histoire/Géographie appliquée."))
