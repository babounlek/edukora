from datetime import timedelta

from django.core.management.base import BaseCommand

from access import quota
from access.models import CompteurQuota, ReglagesTelechargement, TelechargementPdf


class Command(BaseCommand):
    help = (
        "Supprime le journal des téléchargements de PDF et les compteurs de quota plus vieux que la rétention des "
        "réglages (90 jours par défaut). Les abonnements et les paiements ne sont pas touchés. À planifier une fois "
        "par jour ou par semaine."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Compte sans rien supprimer.")

    def handle(self, *args, **options):
        reglages = ReglagesTelechargement.charger()
        aujourdhui, _ = quota.jour_et_reinitialisation(reglages)
        limite = aujourdhui - timedelta(days=reglages.retention_jours)
        journal = TelechargementPdf.objects.filter(jour__lt=limite)
        compteurs = CompteurQuota.objects.filter(jour__lt=limite)
        n_journal, n_compteurs = journal.count(), compteurs.count()
        if not options["dry_run"]:
            journal.delete()
            compteurs.delete()
        verbe = "à supprimer" if options["dry_run"] else "supprimés"
        self.stdout.write(f"Avant le {limite} : {n_journal} téléchargements et {n_compteurs} compteurs {verbe}.")
