import json
import os

from django.core.management.base import BaseCommand

from catalog.models import Figure


class Command(BaseCommand):
    help = (
        "Exporte la liste des figures ingérées (id, fichier, page source, nom d'épreuve) en JSON : "
        "entrée du skill reproduire-figure-sans-filigrane (retraiter_lot.py). Lecture seule."
    )

    def add_arguments(self, parser):
        parser.add_argument("--sortie", required=True, help="Chemin du JSON à écrire (dans le conteneur).")
        parser.add_argument("--prefixe", default="", help="Ne garder que les figures dont le fichier commence par ce préfixe "
                                                           "(ex. gce- pour le GCE).")

    def handle(self, *args, **options):
        manifeste = []
        for f in Figure.objects.all().order_by("id"):
            base = os.path.basename(f.image.name)
            if options["prefixe"] and not base.lower().startswith(options["prefixe"].lower()):
                continue
            epreuve = base.split("_exercice")[0].split("_probleme")[0]
            manifeste.append({"id": f.id, "fichier": f.image.name, "page": f.page_source, "epreuve": epreuve})
        with open(options["sortie"], "w", encoding="utf-8") as fh:
            json.dump(manifeste, fh, ensure_ascii=False)
        self.stdout.write(self.style.SUCCESS(f"{len(manifeste)} figures exportées dans {options['sortie']}"))
