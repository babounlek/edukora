from django.core.management.base import BaseCommand

from catalog.cours_pdf import COMPLET, LIBRE, enregistrer_cours_pdf, liberer
from catalog.models import Cours, StatutContenu


class Command(BaseCommand):
    help = (
        "Génère (hors ligne) le PDF de cours : version libre (sans les exercices d'application) ou complète. "
        "Lancé en processus détaché par catalog.cours_pdf.mettre_en_file à la première demande de téléchargement ; "
        "peut aussi servir à préparer des PDF à l'avance. Ne tourne jamais dans le cycle d'une requête HTTP."
    )

    def add_arguments(self, parser):
        parser.add_argument("--cours", type=int, nargs="+", required=True, help="Id des cours à traiter.")
        parser.add_argument(
            "--variante", choices=[LIBRE, COMPLET, "toutes"], default="toutes",
            help="Version à générer (défaut : les deux).",
        )

    def handle(self, *args, **options):
        variantes = [LIBRE, COMPLET] if options["variante"] == "toutes" else [options["variante"]]
        succes, echecs = 0, []
        for cours in Cours.objects.filter(pk__in=options["cours"], statut=StatutContenu.VALIDE).select_related(
            "subject__country",
        ):
            for variante in variantes:
                try:
                    enregistrer_cours_pdf(cours, variante)
                    succes += 1
                    self.stdout.write(f"  - {cours} ({variante}) : OK")
                except Exception as exc:
                    echecs.append(f"{cours} ({variante}) : {exc}")
                    liberer(cours, variante, echec=True)
                else:
                    liberer(cours, variante)

        self.stdout.write(self.style.SUCCESS(f"{succes} PDF de cours généré(s)."))
        for echec in echecs:
            self.stdout.write(self.style.ERROR(f"  - {echec}"))
