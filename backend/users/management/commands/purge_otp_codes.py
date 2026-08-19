"""
Purge des codes à usage unique périmés (users.models.OTPCode, tous canaux).

Cette table ne se vidait jamais : chaque demande de code y laisse une ligne définitive,
alors qu'un code ne vaut que quelques minutes. C'est à la fois de la donnée personnelle
conservée sans raison (numéro ou adresse, plus l'IP du demandeur) et une table qui ne
fait que croître alors que les garde-fous d'envoi la relisent à chaque demande.

Les deux canaux vivent dans la même table et sont purgés ensemble : ils posent
exactement le même problème, et deux tâches planifiées distinctes pour une même règle de
rétention finiraient par diverger. Le décompte reste ventilé par canal à l'affichage,
parce que c'est le nombre de SMS - et lui seul - qui se lit aussi comme une facture.

À planifier une fois par jour (cron / tâche planifiée de l'hôte).
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from users.email_service import EMAIL_CODE_GLOBAL_WINDOW, EMAIL_CODE_IP_WINDOW
from users.models import CodeCanal, OTPCode
from users.otp_service import OTP_GLOBAL_WINDOW, OTP_IP_WINDOW

# Les plafonds d'envoi comptent les lignes récentes : purger à l'intérieur de leur
# fenêtre effacerait les preuves d'envoi sur lesquelles ils s'appuient et rendrait le
# pumping à nouveau gratuit (il suffirait d'attendre la purge). La rétention minimale
# est donc la plus longue fenêtre des deux canaux, avec une marge d'un jour.
_LONGEST_WINDOW = max(OTP_IP_WINDOW, OTP_GLOBAL_WINDOW, EMAIL_CODE_IP_WINDOW, EMAIL_CODE_GLOBAL_WINDOW)
MIN_RETENTION_DAYS = int((_LONGEST_WINDOW + timedelta(days=1)).total_seconds() // 86400)
DEFAULT_RETENTION_DAYS = 7


class Command(BaseCommand):
    help = "Supprime les codes OTP et e-mail créés il y a plus de --days jours (défaut : 7)."

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
        perimes = OTPCode.objects.filter(created_at__lt=cutoff)
        sms_qs = perimes.filter(canal=CodeCanal.SMS)
        email_qs = perimes.filter(canal=CodeCanal.EMAIL)

        if options["dry_run"]:
            self.stdout.write(
                f"{sms_qs.count()} code(s) SMS et {email_qs.count()} code(s) e-mail "
                f"antérieur(s) au {cutoff:%Y-%m-%d %H:%M} seraient supprimés.",
            )
            return

        # Comptés AVANT la suppression : une fois `perimes` exécuté, les deux
        # sous-requêtes ne renverraient plus rien à compter.
        sms_deleted = sms_qs.count()
        email_deleted = email_qs.count()
        perimes.delete()
        self.stdout.write(self.style.SUCCESS(
            f"{sms_deleted} code(s) SMS et {email_deleted} code(s) e-mail supprimé(s) "
            f"(antérieurs au {cutoff:%Y-%m-%d %H:%M}).",
        ))
