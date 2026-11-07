import json

from django.core.management.base import BaseCommand

from aide.rapport import rapport_aide, rendre_texte


class Command(BaseCommand):
    help = (
        "Le centre d'aide sert-il ? Lectures, avis utile oui/non et clics vers le support, article par article, "
        "avec la liste de ce qu'il faut réécrire (voir aide.rapport). Même rapport que dans l'admin."
    )

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=30, help="Fenêtre, en jours (défaut : 30).")
        parser.add_argument("--json", action="store_true", help="Sortie JSON plutôt que texte.")

    def handle(self, *args, **options):
        rapport = rapport_aide(options["jours"])
        if options["json"]:
            self.stdout.write(json.dumps(rapport, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(rendre_texte(rapport))
