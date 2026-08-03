from django.core.management.base import BaseCommand

from catalog.ingestion import _dedupe_question_enonce
from catalog.models import Exercise, Lesson, Question


class Command(BaseCommand):
    help = (
        "Filet de sécurité rétroactif : retire de Question.enonce_markdown déjà en "
        "base les deux doublons que catalog.ingestion.ingest_exercise évite désormais "
        "à la source (voir _dedupe_question_enonce) - la phrase de contexte partagée "
        "recopiée depuis l'intro de l'exercice, et la lettre de sous-question "
        "dupliquée (\"(a) (a)\")."
    )

    def handle(self, *args, **options):
        question_fixed = 0
        exercises_a_recompiler = set()
        for question in Question.objects.select_related("exercise"):
            enonce = _dedupe_question_enonce(question.enonce_markdown, question.exercise.enonce_intro_markdown)
            if enonce != question.enonce_markdown:
                question.enonce_markdown = enonce
                question.save(update_fields=["enonce_markdown", "updated_at"])
                question_fixed += 1
                exercises_a_recompiler.add(question.exercise_id)

        for exercise in Exercise.objects.filter(pk__in=exercises_a_recompiler):
            exercise.compile_from_questions()

        for lesson in Lesson.objects.filter(exercises__in=exercises_a_recompiler).distinct():
            lesson.compile_from_exercises()

        self.stdout.write(self.style.SUCCESS(
            f"{question_fixed} question(s) corrigée(s) ({len(exercises_a_recompiler)} exercice(s) "
            "et leur(s) leçon(s) recompilé(s)).",
        ))
