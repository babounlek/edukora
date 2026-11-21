from django.core.management.base import BaseCommand
from django.db.models import Q

from catalog.models import TypeReponse
from fiches.models import FicheGeneree
from fiches.pdf import save_fiche_pdfs
from quiz.models import QuizSession
from quiz.pdf import save_quiz_fiche_pdfs


def sessions_a_refaire():
    """Les sessions de quiz qui ont déjà leurs PDF et au moins une QCM (instantané, à défaut contenu vivant)."""
    qcm = Q(quiz_questions__snapshot__type_reponse=TypeReponse.QCM) | Q(
        quiz_questions__snapshot__isnull=True, quiz_questions__competence_item__type_reponse=TypeReponse.QCM,
    ) | Q(quiz_questions__snapshot__isnull=True, quiz_questions__question__type_reponse=TypeReponse.QCM)
    return (
        QuizSession.objects.exclude(sujet_pdf="").filter(qcm).distinct()
        .select_related("cursus__country", "subject").order_by("pk")
    )


def fiches_a_refaire():
    """Les fiches de répétiteur qui ont déjà leurs PDF et au moins une QCM."""
    return (
        FicheGeneree.objects.exclude(sujet_pdf="")
        .filter(items__competence_item__type_reponse=TypeReponse.QCM).distinct().order_by("pk")
    )


class Command(BaseCommand):
    help = (
        "Refait les PDF déjà générés qui contiennent des QCM : sessions de quiz (Fiche + Correction) et fiches "
        "de répétiteur (sujet + corrigé). Avant le correctif des propositions, ces PDF imprimaient l'énoncé des "
        "QCM sans leurs propositions ; un PDF déjà généré est servi tel quel et ne se corrige pas tout seul. "
        "Hors ligne uniquement (Playwright), en série. Un échec laisse l'ancien PDF en place et passe au suivant. "
        "--simuler compte sans rien refaire."
    )

    def add_arguments(self, parser):
        parser.add_argument("--simuler", action="store_true", help="Compte ce qui serait refait, sans rien générer.")

    def handle(self, *args, **options):
        lots = (
            ("Session", sessions_a_refaire(), save_quiz_fiche_pdfs),
            ("Fiche", fiches_a_refaire(), save_fiche_pdfs),
        )
        for nom, objets, refaire in lots:
            total = objets.count()
            if options["simuler"]:
                self.stdout.write(f"{nom}s à refaire : {total}")
                continue
            refaits = echecs = 0
            for objet in objets.iterator():
                try:
                    # Les octets sont générés AVANT toute écriture (voir save_quiz_fiche_pdfs et save_fiche_pdfs) :
                    # un échec de rendu ne retire donc rien à l'élève.
                    refaire(objet)
                    refaits += 1
                except Exception as exc:
                    echecs += 1
                    self.stdout.write(self.style.ERROR(f"{nom} #{objet.pk} : échec, ancien PDF conservé - {exc}"))
            self.stdout.write(self.style.SUCCESS(f"{nom}s : {refaits} refait(s) sur {total}, {echecs} échec(s)."))
