import json

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Country
from inedit.ingestion import SELECTION_FLOOR, SELECTION_LIMIT, select_inedit_batch


class Command(BaseCommand):
    help = (
        "Sélectionne jusqu'à --limit couples (matière, cursus) sous-couverts en "
        "Blueprint validé pour --pays et produit, sur stdout (ou --output), un tableau "
        "JSON de requêtes de génération de blueprint - à transmettre à la skill de "
        "conception d'épreuves inédites, une par une, pour produire les blueprints à "
        "ingérer ensuite via ingest_inedit_content (puis valider avant toute génération)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", required=True, help="Code pays (ex. cm, sn, ci, bj).")
        parser.add_argument(
            "--limit", type=int, default=SELECTION_LIMIT,
            help=f"Nombre maximum de couples matière/cursus à sélectionner (défaut {SELECTION_LIMIT}).",
        )
        parser.add_argument(
            "--floor", type=int, default=SELECTION_FLOOR,
            help=f"Couverture cible en Blueprint validés par couple matière/cursus (défaut {SELECTION_FLOOR}).",
        )
        parser.add_argument("--output", help="Fichier où écrire le JSON (défaut : stdout).")

    def handle(self, *args, **options):
        try:
            country = Country.objects.get(code__iexact=options["pays"])
        except Country.DoesNotExist:
            raise CommandError(f"Pays inconnu : {options['pays']!r}.")

        requests = select_inedit_batch(country, limit=options["limit"], floor=options["floor"])

        output = json.dumps(requests, ensure_ascii=False, indent=2)
        if options["output"]:
            with open(options["output"], "w", encoding="utf-8") as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f"{len(requests)} requête(s) écrite(s) dans {options['output']}."))
        else:
            self.stdout.write(output)

        if not requests:
            self.stderr.write(self.style.WARNING(
                f"Aucun couple matière/cursus sous le plancher ({options['floor']}) pour {country} - "
                "soit tout est déjà couvert, soit aucun Lesson validé n'existe encore pour ce pays.",
            ))
