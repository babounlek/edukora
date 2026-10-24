from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count

from access import quota
from access.models import CompteurQuota, ReglagesTelechargement, TelechargementPdf


class Command(BaseCommand):
    help = (
        "Statistiques des téléchargements de PDF sur les N derniers jours (7 par défaut) : volume par type de "
        "demandeur, quotas atteints et refus pour dépassement. Rien de personnel : des totaux par jour."
    )

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=7)

    def handle(self, *args, **options):
        aujourdhui, _ = quota.jour_et_reinitialisation(ReglagesTelechargement.charger())
        depuis = aujourdhui - timedelta(days=options["jours"] - 1)
        self.stdout.write(f"Du {depuis} au {aujourdhui}")

        self.stdout.write("\nPDF délivrés (crédits consommés) :")
        livres = (
            TelechargementPdf.objects.filter(jour__gte=depuis).values("jour", "type_demandeur")
            .annotate(n=Count("id")).order_by("jour", "type_demandeur")
        )
        for ligne in livres:
            self.stdout.write(f"  {ligne['jour']}  {ligne['type_demandeur']:<9} {ligne['n']}")

        self.stdout.write("\nQuotas atteints et refus :")
        stats = (
            CompteurQuota.objects.filter(jour__gte=depuis)
            .filter(portee__in=["quota_atteint", "refus_quota_depasse", "refus_plafond_reseau", "refus_budget_global"])
            .order_by("jour", "portee", "cle")
        )
        for ligne in stats:
            self.stdout.write(f"  {ligne.jour}  {ligne.portee:<22} {ligne.cle:<9} {ligne.nombre}")
