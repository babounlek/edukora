"""
Crée les mini-inédites (2 exercices tirés d'épreuves inédites existantes) d'une matière. Idempotent : rejouer ne
crée aucun doublon. `--a-blanc` affiche le tirage sans rien écrire.

    python manage.py creer_mini_inedites --a-blanc
    python manage.py creer_mini_inedites --matiere MATHS --par-groupe 3
"""
from django.core.management.base import BaseCommand

from inedit.mini import creer_pour_matiere


class Command(BaseCommand):
    help = "Crée les mini-inédites d'une matière à partir des épreuves inédites publiées."

    def add_arguments(self, parser):
        parser.add_argument("--matiere", default="MATHS", help="Code de la matière (défaut : MATHS).")
        parser.add_argument("--par-groupe", type=int, default=3, help="Mini-inédites par ensemble de cursus (défaut : 3).")
        parser.add_argument("--a-blanc", action="store_true", help="Affiche le tirage sans rien écrire.")

    def handle(self, *args, **options):
        rapport = creer_pour_matiere(options["matiere"], options["par_groupe"], options["a_blanc"])
        for cle, titre, minutes, sources, creee in rapport:
            etat = "tirage" if creee is None else ("créée" if creee else "déjà là")
            self.stdout.write(f"{etat:8} {titre} | {minutes} min | sources {sources}")
        self.stdout.write(self.style.SUCCESS(f"{len(rapport)} mini-inédite(s)."))
