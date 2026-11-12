"""
Supprime les comptes invités abandonnés (voir users.invites) : essai d'une inédite gratuite jamais suivi d'une
inscription. Leur jeton dure 30 jours, ils sont conservés 60 jours, puis disparaissent avec leur copie.

À planifier une fois par jour (cron / tâche planifiée de l'hôte).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.invites import DUREE_CONSERVATION
from users.models import User


class Command(BaseCommand):
    help = "Supprime les comptes invités créés il y a plus de 60 jours (--dry-run pour compter sans supprimer)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Compte sans supprimer.")

    def handle(self, *args, **options):
        perimes = User.objects.filter(est_invite=True, date_joined__lt=timezone.now() - DUREE_CONSERVATION)
        n = perimes.count()
        if options["dry_run"]:
            self.stdout.write(f"{n} compte(s) invité(s) à supprimer (simulation, rien n'est supprimé).")
            return
        perimes.delete()
        self.stdout.write(self.style.SUCCESS(f"{n} compte(s) invité(s) supprimé(s)."))
