from django.core.management.base import BaseCommand

from catalog.models import StatutContenu
from inedit.models import EpreuveInedite
from inedit.sujet_pdf import save_sujet_pdf


class Command(BaseCommand):
    help = (
        "Génère (hors ligne) le PDF du sujet - pour les épreuves inédites publiées "
        "qui n'en ont pas encore. Ne tourne jamais dans le cycle d'une requête HTTP : "
        "à exécuter manuellement, via une action admin, ou une tâche planifiée."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--epreuve", type=int, nargs="+", default=None,
            help="Ne traiter que ces épreuves (un ou plusieurs id), sinon toutes les épreuves éligibles.",
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Régénérer même les épreuves qui ont déjà un PDF de sujet.",
        )

    def handle(self, *args, **options):
        qs = EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE)
        if options["epreuve"]:
            qs = qs.filter(pk__in=options["epreuve"])
        if not options["force"]:
            qs = qs.filter(sujet_pdf="")

        epreuves = list(qs)
        if not epreuves:
            self.stdout.write(self.style.WARNING("Aucune épreuve à traiter."))
            return

        succes, echecs = 0, []
        for epreuve in epreuves:
            try:
                save_sujet_pdf(epreuve)
                succes += 1
                self.stdout.write(f"  - {epreuve} : OK")
            except Exception as exc:
                echecs.append(f"{epreuve} : {exc}")

        self.stdout.write(self.style.SUCCESS(f"{succes} PDF de sujet généré(s)."))
        if echecs:
            self.stdout.write(self.style.ERROR(f"{len(echecs)} échec(s) :"))
            for echec in echecs:
                self.stdout.write(self.style.ERROR(f"  - {echec}"))
