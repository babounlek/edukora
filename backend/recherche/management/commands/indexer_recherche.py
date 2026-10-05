import time

from django.core.management.base import BaseCommand

from recherche.indexation import reconstruire
from recherche.models import EntreeRecherche, TypeResultat


class Command(BaseCommand):
    help = (
        "Reconstruit l'index de la recherche globale depuis le catalogue (voir recherche.indexation). "
        "À lancer après un lot d'ingestion ou une campagne de contenu : l'index n'est pas mis à jour "
        "au fil des enregistrements, il se refait en entier (quelques dizaines de secondes)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--types", nargs="+", choices=[t.value for t in TypeResultat],
            help="Ne reconstruire que ces types (tous par défaut).",
        )
        parser.add_argument(
            "--si-vide", action="store_true",
            help="Ne rien faire si l'index contient déjà des entrées (démarrage du conteneur).",
        )

    def handle(self, *args, **options):
        if options["si_vide"] and EntreeRecherche.objects.exists():
            self.stdout.write("Index de recherche déjà présent : rien à faire.")
            return
        debut = time.monotonic()
        self.stdout.write("Indexation de la recherche globale...")
        bilan = reconstruire(options["types"], ecrire=self.stdout.write)
        self.stdout.write(self.style.SUCCESS(f"Terminé en {time.monotonic() - debut:.1f} s ({sum(bilan.values())} lignes)."))
