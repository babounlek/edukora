from django.core.management.base import BaseCommand

from quiz.models import QuizSession
from quiz.pdf import save_quiz_fiche_pdfs


def sessions_a_refaire():
    """Les sessions qui ont déjà leurs PDF et pas de matière propre : celles dont la fiche est sortie sans titre."""
    return (
        QuizSession.objects.exclude(sujet_pdf="").filter(subject__isnull=True)
        .select_related("cursus__country").order_by("pk")
    )


class Command(BaseCommand):
    help = (
        "Refait les PDF (Fiche + Correction) des sessions de quiz sans matière propre : quiz lancé depuis un thème, "
        "révision, quiz mêlé. Avant le correctif, leur en-tête sortait sans la matière ; un PDF déjà généré est "
        "servi tel quel et ne se corrige pas tout seul. Hors ligne uniquement (Playwright), en série. Un échec "
        "laisse l'ancien PDF en place et passe au suivant. --simuler compte sans rien refaire."
    )

    def add_arguments(self, parser):
        parser.add_argument("--simuler", action="store_true", help="Compte ce qui serait refait, sans rien générer.")

    def handle(self, *args, **options):
        sessions = sessions_a_refaire()
        total = sessions.count()
        if options["simuler"]:
            self.stdout.write(f"Sessions à refaire : {total}")
            return
        refaites = echecs = 0
        for session in sessions.iterator():
            try:
                # Les octets sont générés AVANT toute écriture (voir save_quiz_fiche_pdfs) : un échec de rendu
                # ne retire rien à l'élève.
                save_quiz_fiche_pdfs(session)
                refaites += 1
            except Exception as exc:
                echecs += 1
                self.stdout.write(self.style.ERROR(f"Session #{session.pk} : échec, ancien PDF conservé - {exc}"))
        self.stdout.write(self.style.SUCCESS(f"Sessions : {refaites} refaite(s) sur {total}, {echecs} échec(s)."))
