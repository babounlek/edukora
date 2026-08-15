"""
Purge des codes OTP périmés (voir users.models.OTPCode).

Cette table ne se vidait jamais : chaque demande de code y laisse une ligne définitive,
alors qu'un code ne vaut que 5 minutes (OTP_VALIDITY_MINUTES). C'est à la fois de la
donnée personnelle conservée sans raison (numéro de téléphone + IP du demandeur) et une
table qui ne fait que croître alors que request_otp la relit à chaque demande.

À planifier une fois par jour (cron / tâche planifiée de l'hôte).
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from users.models import OTPCode
from users.otp_service import OTP_GLOBAL_WINDOW, OTP_IP_WINDOW

# Les plafonds de request_otp comptent les lignes récentes : purger à l'intérieur de
# leur fenêtre effacerait les preuves d'envoi sur lesquelles ils s'appuient et rendrait
# le pumping à nouveau gratuit (il suffirait d'attendre la purge). La rétention minimale
# est donc la plus longue des deux fenêtres, avec une marge d'un jour.
MIN_RETENTION_DAYS = int((max(OTP_IP_WINDOW, OTP_GLOBAL_WINDOW) + timedelta(days=1)).total_seconds() // 86400)
DEFAULT_RETENTION_DAYS = 7


class Command(BaseCommand):
    help = "Supprime les codes OTP créés il y a plus de --days jours (défaut : 7)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=DEFAULT_RETENTION_DAYS,
            help=f"Durée de rétention en jours (minimum {MIN_RETENTION_DAYS}).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Affiche le nombre de lignes concernées sans rien supprimer.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days < MIN_RETENTION_DAYS:
            raise CommandError(
                f"--days doit valoir au moins {MIN_RETENTION_DAYS} : en dessous, la purge "
                f"effacerait les envois que les plafonds de users.otp_service comptent encore.",
            )

        cutoff = timezone.now() - timedelta(days=days)
        qs = OTPCode.objects.filter(created_at__lt=cutoff)

        if options["dry_run"]:
            self.stdout.write(f"{qs.count()} code(s) OTP antérieur(s) au {cutoff:%Y-%m-%d %H:%M} seraient supprimés.")
            return

        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted} code(s) OTP supprimé(s) (antérieurs au {cutoff:%Y-%m-%d %H:%M})."))
