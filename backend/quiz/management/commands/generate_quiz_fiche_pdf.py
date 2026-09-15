from django.core.management.base import BaseCommand

from quiz.models import QuizSession, StatutFichePdf
from quiz.pdf import save_quiz_fiche_pdfs


class Command(BaseCommand):
    help = (
        "Génère (hors ligne) les PDF Fiche (énoncés) + Correction (énoncés+corrigé) d'une "
        "QuizSession terminée - déclenchée par quiz.views.quiz_fiche_pdf via "
        "queue_quiz_fiche_pdf_generation. Ne tourne jamais dans le cycle d'une requête HTTP."
    )

    def add_arguments(self, parser):
        parser.add_argument("--session", type=int, required=True, help="Id de la QuizSession à traiter.")

    def handle(self, *args, **options):
        try:
            session = QuizSession.objects.select_related("cursus__country", "subject").get(pk=options["session"])
        except QuizSession.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Session #{options['session']} introuvable."))
            return

        try:
            save_quiz_fiche_pdfs(session)
        except Exception as exc:
            QuizSession.objects.filter(pk=session.pk).update(fiche_pdf_statut=StatutFichePdf.ECHEC)
            self.stdout.write(self.style.ERROR(f"Session #{session.pk} : échec de génération - {exc}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Session #{session.pk} : PDF Fiche+Correction générés."))
