import json

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Country
from quiz.ingestion import (
    SELECTION_FLOOR,
    SELECTION_LIMIT,
    SELECTION_MIN_QUESTIONS,
    select_quiz_batch,
)


class Command(BaseCommand):
    help = (
        "Sélectionne jusqu'à --limit compétences sous-couvertes pour --pays et produit, "
        "sur stdout (ou --output), un tableau JSON de requêtes de génération au format "
        "attendu par le skill concepteur-quiz-competence - à lui donner telles quelles, "
        "une par une, pour produire les lots à ingérer ensuite via ingest_quiz_content."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", required=True, help="Code pays (ex. cm, sn, ci, bj).")
        parser.add_argument(
            "--limit", type=int, default=SELECTION_LIMIT,
            help=f"Nombre maximum de compétences à sélectionner (défaut {SELECTION_LIMIT}).",
        )
        parser.add_argument(
            "--floor", type=int, default=SELECTION_FLOOR,
            help=f"Couverture cible en CompetenceItem validés par compétence (défaut {SELECTION_FLOOR}).",
        )
        parser.add_argument(
            "--min-questions", type=int, default=SELECTION_MIN_QUESTIONS,
            help=(
                f"Nombre minimal de Question validées portant un couple (thème, matière) pour "
                f"qu'il soit proposé (défaut {SELECTION_MIN_QUESTIONS}). Abaisser à 1 rétablit "
                "l'ancien comportement, au prix de compétences adossées à un unique exercice - "
                "dont le nom du tag ne suffit alors pas à savoir ce qu'elles recouvrent."
            ),
        )
        parser.add_argument(
            "--matiere", help="Code de matière (ex. PROGRAMMATION, MATHS) : ne sélectionne que cette matière.",
        )
        parser.add_argument("--output", help="Fichier où écrire le JSON (défaut : stdout).")

    def handle(self, *args, **options):
        try:
            country = Country.objects.get(code__iexact=options["pays"])
        except Country.DoesNotExist:
            raise CommandError(f"Pays inconnu : {options['pays']!r}.")

        requests = select_quiz_batch(
            country,
            limit=options["limit"],
            floor=options["floor"],
            min_questions=options["min_questions"],
            subject_code=options["matiere"],
        )

        output = json.dumps(requests, ensure_ascii=False, indent=2)
        if options["output"]:
            with open(options["output"], "w", encoding="utf-8") as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f"{len(requests)} requête(s) écrite(s) dans {options['output']}."))
        else:
            self.stdout.write(output)

        if not requests:
            self.stderr.write(self.style.WARNING(
                f"Aucune compétence sous le plancher ({options['floor']}) pour {country} - "
                "soit tout est déjà couvert, soit aucune Question validée n'est encore taguée.",
            ))
