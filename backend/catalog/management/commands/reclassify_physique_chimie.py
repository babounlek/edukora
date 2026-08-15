import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.ingestion import MATIERE_MAP, _normalize
from catalog.models import Cours, Lesson, Origine, Subject, SUBJECT_FAMILIES, _join_fr

INGEST_DIR = Path(settings.BASE_DIR) / "ingest"


def _exercise_json_path(lesson, exercise):
    """Même convention que ExerciseAdmin.reingerer_depuis_fichier :
    ingest/<pays>/<epreuve>/<epreuve>_exercice_<numero>.json."""
    nom_epreuve = lesson.epreuve_source.removesuffix(".pdf")
    country_code = lesson.subject.country.code.lower()
    return INGEST_DIR / country_code / nom_epreuve / f"{nom_epreuve}_exercice_{exercise.numero_exercice}.json"


def _target_code_for_codes(codes):
    """Réplique la logique de promotion de catalog.ingestion._subject_family_codes,
    mais depuis un ensemble de codes déjà connu (relecture rétroactive) plutôt que
    découverte fichier par fichier. Un seul code distinct -> ce code. Plusieurs codes
    distincts appartenant tous à la même famille combinée (ex. PHYSIQUE et CHIMIE,
    tous deux -> PHYSIQUE_CHIMIE) -> le code combiné. Mélange hors famille connue
    (jamais rencontré en pratique) -> None, pour ne jamais deviner."""
    distinct = set(codes)
    if len(distinct) == 1:
        return distinct.pop()
    combined_codes = {SUBJECT_FAMILIES.get(code, code) for code in distinct}
    return combined_codes.pop() if len(combined_codes) == 1 else None


class Command(BaseCommand):
    help = (
        "Reclassification rétroactive : relit le matiere (Physique/Chimie/Physique-"
        "Chimie) de chaque exercice source déjà ingéré sous Subject=PHYSIQUE_CHIMIE, "
        "et réaffecte la Lesson (puis les Cours dérivés) vers PHYSIQUE/CHIMIE quand "
        "toutes ses épreuves/exercices sources s'accordent sur une seule discipline. "
        "N'invente jamais rien depuis le nom de fichier : si le JSON source d'un "
        "exercice est introuvable ou si les exercices d'une même épreuve désignent "
        "des disciplines différentes, la Lesson reste sous Physique-Chimie et est "
        "listée pour revue manuelle. Ne touche jamais aux slugs (URLs préservées) ni "
        "au contenu (enonce/corrige/sections) - seulement subject et, pour Lesson, "
        "title (dérivé du label de la matière)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="N'écrit rien en base, affiche seulement ce qui serait fait.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        lessons_reclassified = 0
        lessons_unchanged = 0
        lessons_skipped = []

        physique_chimie_subjects = Subject.objects.filter(code="PHYSIQUE_CHIMIE")
        lessons = (
            Lesson.objects.filter(subject__in=physique_chimie_subjects)
            .select_related("subject__country")
            .prefetch_related("exercises", "cursus__series")
        )

        for lesson in lessons:
            exercises = list(lesson.exercises.all())
            if not exercises:
                lessons_skipped.append(f"{lesson} (#{lesson.pk}) : aucun exercice rattaché")
                continue

            codes = []
            missing_reason = None
            for exercise in exercises:
                json_path = _exercise_json_path(lesson, exercise)
                if not json_path.is_file():
                    missing_reason = f"fichier source introuvable ({json_path.name})"
                    break
                try:
                    data = json.loads(json_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    missing_reason = f"fichier source illisible ({json_path.name} : {exc})"
                    break
                code = MATIERE_MAP.get(_normalize(data.get("matiere")))
                if not code:
                    missing_reason = f"matiere non reconnu dans {json_path.name} : {data.get('matiere')!r}"
                    break
                codes.append(code)

            if missing_reason:
                lessons_skipped.append(f"{lesson} (#{lesson.pk}) : {missing_reason}")
                continue

            target_code = _target_code_for_codes(codes)
            if not target_code:
                lessons_skipped.append(f"{lesson} (#{lesson.pk}) : disciplines mélangées hors famille connue ({sorted(set(codes))})")
                continue

            if target_code == lesson.subject.code:
                lessons_unchanged += 1
                continue

            target_subject = Subject.objects.get(code=target_code, country=lesson.subject.country)

            # Même logique de titre que catalog.ingestion.ingest_exercise (groupement
            # par examen, préservation du suffixe établissement) - seul le label de
            # matière change. Le slug n'est jamais régénéré (voir generate_unique_slug,
            # gelé après création) : les URLs déjà partagées restent valides.
            groups = {}
            for c in lesson.cursus.all():
                group = groups.setdefault(c.examen, {"examen_display": c.display_examen(), "series": []})
                if c.series:
                    group["series"].append(c.series.code)
            cursus_label = " / ".join(
                f"{g['examen_display']} {_join_fr(g['series'])}" if g["series"] else g["examen_display"]
                for g in groups.values()
            )
            new_title = f"{target_subject.label} {cursus_label} {lesson.year or ''}".replace("  ", " ").strip()
            if lesson.origine == Origine.ETABLISSEMENT and lesson.etablissement:
                new_title = f"{new_title} - {lesson.etablissement}"

            self.stdout.write(
                f"{'[dry-run] ' if dry_run else ''}{lesson.subject.label} -> {target_subject.label} : "
                f"{lesson.epreuve_source} (#{lesson.pk}) - « {lesson.title} » -> « {new_title} »",
            )
            if not dry_run:
                lesson.subject = target_subject
                lesson.title = new_title
                lesson.save(update_fields=["subject", "title", "updated_at"])
            lessons_reclassified += 1

        # --- Cours : hérite de la Subject de son/ses exercice(s) source déjà
        # reclassifié(s) ci-dessus, sans relire aucun JSON - le lien Cours -> Exercise
        # (via RappelDeMethode.exercise) est déjà la source de vérité en base.
        cours_reclassified = 0
        cours_unchanged = 0
        cours_skipped = []

        cours_qs = (
            Cours.objects.filter(subject__in=physique_chimie_subjects)
            .select_related("subject")
            .prefetch_related("rappels_source__exercise__lesson__subject")
        )

        for cours in cours_qs:
            rappels = list(cours.rappels_source.all())
            if not rappels:
                cours_skipped.append(f"{cours} (#{cours.pk}) : aucun rappel de méthode source rattaché")
                continue

            subject_ids = {r.exercise.lesson.subject_id for r in rappels}
            if len(subject_ids) == 1:
                target_subject = rappels[0].exercise.lesson.subject
            else:
                codes = {r.exercise.lesson.subject.code for r in rappels}
                target_code = _target_code_for_codes(codes)
                if not target_code:
                    cours_skipped.append(f"{cours} (#{cours.pk}) : exercices sources sous des disciplines mélangées ({sorted(codes)})")
                    continue
                target_subject = Subject.objects.get(code=target_code, country=cours.subject.country)

            if target_subject.code == cours.subject.code:
                cours_unchanged += 1
                continue

            self.stdout.write(
                f"{'[dry-run] ' if dry_run else ''}{cours.subject.label} -> {target_subject.label} : "
                f"{cours.titre} (#{cours.pk})",
            )
            if not dry_run:
                cours.subject = target_subject
                cours.save(update_fields=["subject", "updated_at"])
            cours_reclassified += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nLesson : {lessons_reclassified} reclassée(s), {lessons_unchanged} déjà correcte(s), "
            f"{len(lessons_skipped)} ignorée(s).\n"
            f"Cours : {cours_reclassified} reclassé(s), {cours_unchanged} déjà correct(s), "
            f"{len(cours_skipped)} ignoré(s)."
            + (" (dry-run, rien n'a été écrit)" if dry_run else ""),
        ))

        if lessons_skipped:
            self.stdout.write(self.style.WARNING("\nLesson ignorées (à revoir manuellement) :"))
            for line in lessons_skipped:
                self.stdout.write(f"  - {line}")
        if cours_skipped:
            self.stdout.write(self.style.WARNING("\nCours ignorés (à revoir manuellement) :"))
            for line in cours_skipped:
                self.stdout.write(f"  - {line}")
