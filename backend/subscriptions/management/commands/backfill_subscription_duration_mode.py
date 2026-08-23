from django.core.management.base import BaseCommand

from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from subscriptions.models import DureeMode, ProductType, Subscription


class Command(BaseCommand):
    help = (
        "Remplit Subscription.duration_mode (ajouté après coup - voir la migration "
        "0012) pour les lignes déjà en base, à partir de l'historique de paiement : une "
        "Subscription passe à JUSQUA_EXAMEN si l'utilisateur a au moins un paiement "
        "réussi (Transaction SUCCESSFUL ou ManualPayment APPROVED) sur un Plan "
        "ABONNEMENT en mode JUSQUA_EXAMEN pour ce cursus - jamais deviné depuis "
        "expires_at ou une autre heuristique. Non destructif : ne touche que les lignes "
        "encore à la valeur par défaut FIXE qui devraient être JUSQUA_EXAMEN, ne "
        "rétrograde jamais une ligne déjà à JUSQUA_EXAMEN. Toujours par --dry-run d'abord."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="N'écrit rien en base, affiche seulement le rapport.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        a_mettre_a_jour = []
        for subscription in Subscription.objects.exclude(duration_mode=DureeMode.JUSQUA_EXAMEN).select_related("user", "cursus"):
            a_paye_jusqua_examen = (
                Transaction.objects.filter(
                    user=subscription.user, plan__cursus=subscription.cursus,
                    plan__product_type=ProductType.ABONNEMENT, plan__duration_mode=DureeMode.JUSQUA_EXAMEN,
                    status=StatutTransaction.SUCCESSFUL,
                ).exists()
                or ManualPayment.objects.filter(
                    user=subscription.user, plan__cursus=subscription.cursus,
                    plan__product_type=ProductType.ABONNEMENT, plan__duration_mode=DureeMode.JUSQUA_EXAMEN,
                    status=ManualPaymentStatus.APPROVED,
                ).exists()
            )
            if a_paye_jusqua_examen:
                a_mettre_a_jour.append(subscription)

        for subscription in a_mettre_a_jour:
            self.stdout.write(
                f"{'[dry-run] ' if dry_run else ''}{subscription.user} - {subscription.cursus} -> JUSQUA_EXAMEN",
            )
            if not dry_run:
                subscription.duration_mode = DureeMode.JUSQUA_EXAMEN
                subscription.save(update_fields=["duration_mode"])

        self.stdout.write(self.style.SUCCESS(
            f"\n{len(a_mettre_a_jour)} Subscription(s) passée(s) à JUSQUA_EXAMEN"
            + (" (dry-run, rien n'a été écrit)" if dry_run else "") + ".",
        ))
