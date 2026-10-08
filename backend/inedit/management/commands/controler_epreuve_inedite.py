import glob
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from inedit.controle import controler_epreuve


class Command(BaseCommand):
    help = (
        "Contrôle indépendant d'une épreuve inédite générée (JSON + fichiers de cours voisins), "
        "à lancer AVANT ingest_inedit_content : barème, Tags, numéro de question répété, rappels, "
        "cours rattachés. Sort en erreur s'il reste une anomalie bloquante (les avertissements "
        "n'échouent pas)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "epreuve",
            help="Chemin du fichier JSON de l'épreuve, ou son external_id (cherché sous ingest/_inedit).",
        )

    def _chemin(self, valeur):
        if os.path.isfile(valeur):
            return valeur
        racine = os.path.join(settings.BASE_DIR, "ingest", "_inedit")
        trouves = glob.glob(os.path.join(racine, "**", valeur + ".json"), recursive=True)
        if len(trouves) != 1:
            raise CommandError(f"Épreuve introuvable (ou ambiguë) : {valeur!r} ({len(trouves)} fichier(s) sous {racine}).")
        return trouves[0]

    def handle(self, *args, **options):
        resultat = controler_epreuve(self._chemin(options["epreuve"]))
        self.stdout.write(f"CHECK {resultat.external_id} : {resultat.resume()}")
        for erreur in resultat.erreurs:
            self.stdout.write(self.style.ERROR(f"ERREUR {erreur}"))
        for avertissement in resultat.avertissements:
            self.stdout.write(self.style.WARNING(f"AVERT {avertissement}"))
        if not resultat.ok:
            raise CommandError(f"CHECK_KO {len(resultat.erreurs)} erreur(s)")
        self.stdout.write(self.style.SUCCESS("CHECK_OK"))
