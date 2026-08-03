from django.core.management.base import BaseCommand

from catalog.models import Exercise, Lesson


class Command(BaseCommand):
    help = (
        "Filet de sécurité rétroactif : recompile enonce_markdown/corrige_markdown de "
        "chaque Exercise (et le content_markdown des Lesson concernées) - à lancer une "
        "fois après un changement de logique dans Exercise.compile_from_questions() "
        "(ex. réinjection du numero/choix des Question), pour que le contenu déjà "
        "ingéré en bénéficie sans réingestion complète."
    )

    def handle(self, *args, **options):
        exercise_count = 0
        for exercise in Exercise.objects.all():
            exercise.compile_from_questions()
            exercise_count += 1

        lesson_count = 0
        for lesson in Lesson.objects.filter(exercises__isnull=False).distinct():
            lesson.compile_from_exercises()
            lesson_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{exercise_count} exercice(s) recompilé(s), {lesson_count} épreuve(s) mise(s) à jour.",
        ))
