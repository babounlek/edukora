"""
Liste le vocabulaire de thèmes (Tag) déjà utilisé pour une matière, à donner au skill de
génération (correction-experte, concepteur-quiz-competence) AVANT rédaction pour qu'il
réutilise les noms existants plutôt que d'en inventer des variantes.

    python manage.py vocabulaire_themes --pays cm --matiere MATHS
    python manage.py vocabulaire_themes --pays cm --matiere SYSTEMES_INFORMATION --min 2

Un thème est "utilisé pour la matière" s'il est porté par une Question d'une leçon de cette
matière, ou par un Cours de cette matière. Sortie : un thème par ligne, du plus utilisé
au moins utilisé (les plus utilisés sont les noms canoniques à privilégier).
"""

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Subject
from catalog.reparations_auto import vocabulaire_matiere


class Command(BaseCommand):
    help = "Liste les thèmes (Tag) déjà utilisés pour une matière, du plus au moins fréquent."

    def add_arguments(self, parser):
        parser.add_argument("--pays", required=True, help="Code pays, ex. cm.")
        parser.add_argument("--matiere", required=True, help="Code de matière, ex. MATHS, SYSTEMES_INFORMATION.")
        parser.add_argument("--min", type=int, default=1, help="Nombre minimal d'usages pour figurer dans la liste.")

    def handle(self, *args, **options):
        subject = Subject.objects.filter(country__code__iexact=options["pays"], code=options["matiere"]).first()
        if subject is None:
            codes = ", ".join(
                Subject.objects.filter(country__code__iexact=options["pays"]).order_by("code").values_list("code", flat=True),
            )
            raise CommandError(f"Matière {options['matiere']!r} inconnue pour {options['pays']!r}. Codes valides : {codes}")

        for name, n in vocabulaire_matiere(subject).most_common():
            if n >= options["min"]:
                self.stdout.write(name)
