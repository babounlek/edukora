from django.core.management.base import BaseCommand

from catalog.ingestion_repairs import _strip_duplicated_trailing_reference
from catalog.models import Exercise, Lesson


class Command(BaseCommand):
    help = (
        "Filet de sécurité rétroactif : retire, de la PREMIÈRE Question.enonce_markdown "
        "de chaque Exercise, le repère \"Exercice N\"/\"Problème\" déjà porté par la "
        "dernière ligne de Exercise.enonce_intro_markdown - doublon que "
        "catalog.ingestion.ingest_exercise évite désormais à la source (voir "
        "_dedupe_trailing_exercise_reference dans ingestion_repairs.py). Variante de "
        "_dedupe_exercise_heading/clean_duplicate_question_text pour le cas où le "
        "repère de l'intro n'est PAS sur sa première ligne (une fiche d'identité ou un "
        "chapeau partagé par l'épreuve entière le précède) - voir la docstring de "
        "_last_bold_reference_line."
    )

    def handle(self, *args, **options):
        exercise_fixed = 0
        exercises_a_recompiler = set()
        for exercise in Exercise.objects.all().order_by("pk"):
            premiere_question = exercise.questions.order_by("ordre").first()
            if premiere_question is None:
                continue
            nouveau = _strip_duplicated_trailing_reference(
                exercise.enonce_intro_markdown, premiere_question.enonce_markdown,
            )
            if nouveau is None:
                continue
            premiere_question.enonce_markdown = nouveau
            premiere_question.save(update_fields=["enonce_markdown", "updated_at"])
            exercise_fixed += 1
            exercises_a_recompiler.add(exercise.pk)

        for exercise in Exercise.objects.filter(pk__in=exercises_a_recompiler):
            exercise.compile_from_questions()

        lessons_recompilees = 0
        for lesson in Lesson.objects.filter(exercises__in=exercises_a_recompiler).distinct():
            lesson.compile_from_exercises()
            lessons_recompilees += 1

        self.stdout.write(self.style.SUCCESS(
            f"{exercise_fixed} exercice(s) corrigé(s) ({lessons_recompilees} leçon(s) recompilée(s)).",
        ))
