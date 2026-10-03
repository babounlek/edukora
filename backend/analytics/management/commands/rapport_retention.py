import json

from django.core.management.base import BaseCommand

from analytics.retention import rendre_texte, retention


class Command(BaseCommand):
    help = (
        "Les élèves reviennent-ils, à quelle fréquence, et vont-ils au bout d'un quiz ? Retour à J+1 et J+7, "
        "jours actifs par profil et part de quiz terminés, lus sur les tables existantes "
        "(voir analytics.retention) - donc valable sur tout l'historique dès maintenant."
    )

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=30, help="Fenêtre d'arrivée des nouveaux profils, en jours (défaut : 30).")
        parser.add_argument("--json", action="store_true", help="Sortie JSON plutôt que texte.")

    def handle(self, *args, **options):
        rapport = retention(options["jours"])
        if options["json"]:
            self.stdout.write(json.dumps(rapport, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(rendre_texte(rapport))
