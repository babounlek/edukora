import json

from django.core.management.base import BaseCommand

from analytics.funnel import entonnoir, rendre_texte


class Command(BaseCommand):
    help = (
        "Où les élèves s'arrêtent-ils entre l'inscription et le paiement ? Entonnoir des comptes "
        "créés dans la fenêtre, retour à J+7 et état des paiements, lus sur les tables existantes "
        "(voir analytics.funnel) - donc valable sur tout l'historique dès maintenant."
    )

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=30, help="Fenêtre d'inscription, en jours (défaut : 30).")
        parser.add_argument("--json", action="store_true", help="Sortie JSON plutôt que texte.")

    def handle(self, *args, **options):
        rapport = entonnoir(options["jours"])
        if options["json"]:
            self.stdout.write(json.dumps(rapport, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(rendre_texte(rapport))
