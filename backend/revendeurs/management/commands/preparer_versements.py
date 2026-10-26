from django.core.management.base import BaseCommand

from revendeurs.models import Revendeur, StatutRevendeur
from revendeurs.services import commissions_a_verser, preparer_versements, reprises_dues


class Command(BaseCommand):
    help = (
        "Prépare le versement mensuel de chaque revendeur (commissions acquises moins reprises, seuil minimum). "
        "Avec --simuler, affiche ce qui serait préparé sans rien écrire."
    )

    def add_arguments(self, parser):
        parser.add_argument("--simuler", action="store_true", help="Ne rien écrire, afficher le détail.")
        parser.add_argument("--code", help="Un seul revendeur, par son code.")

    def handle(self, *args, simuler=False, code=None, **options):
        revendeurs = Revendeur.objects.exclude(statut=StatutRevendeur.EN_ATTENTE).select_related("user")
        if code:
            revendeurs = revendeurs.filter(code=code.upper())

        if simuler:
            for r in revendeurs:
                brut = sum(c.montant_fcfa for c in commissions_a_verser(r))
                reprises = sum(c.montant_fcfa for c in reprises_dues(r))
                self.stdout.write(f"{r.nom_affiche} ({r.code}) : brut {brut}, reprises {reprises}, net {brut - reprises} FCFA")
            return

        versements, ignores = preparer_versements(revendeurs)
        for v in versements:
            self.stdout.write(self.style.SUCCESS(f"Préparé #{v.pk} : {v.revendeur.nom_affiche} {v.montant_net} FCFA"))
        for r, raison in ignores:
            self.stdout.write(f"Ignoré {r.nom_affiche} : {raison}")
        self.stdout.write(f"{len(versements)} versement(s) préparé(s), {len(ignores)} ignoré(s).")
