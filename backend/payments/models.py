import uuid

from django.db import connection, models
from django.db import transaction as db_transaction

from subscriptions.models import Plan, Subscription, recompenser_parrainage

from . import campay_client


class StatutTransaction(models.TextChoices):
    PENDING = "PENDING", "En attente"
    SUCCESSFUL = "SUCCESSFUL", "Réussie"
    FAILED = "FAILED", "Échouée"


class Transaction(models.Model):
    """Une tentative de paiement Mobile Money : achat/renouvellement d'un Plan d'abonnement."""

    user = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="transactions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="transactions")
    subscription = models.ForeignKey(
        Subscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions",
        help_text="Renseigné une fois le paiement d'abonnement confirmé et l'abonnement activé/prolongé.",
    )

    amount = models.PositiveIntegerField(help_text="Montant en FCFA, capturé au moment du paiement (indépendant d'un changement de prix ultérieur).")
    phone_number = models.CharField(max_length=9)

    external_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    campay_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=StatutTransaction.choices, default=StatutTransaction.PENDING)
    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.plan} - {self.amount} FCFA ({self.status})"

    def initiate(self):
        """Envoie la demande de collecte CamPay et enregistre la référence retournée."""
        response = campay_client.init_collect(
            amount=self.amount,
            phone_number=self.phone_number,
            description=f"Abonnement {self.plan.name}",
            external_reference=str(self.external_reference),
        )
        self.campay_reference = response.get("reference", "")
        self.raw_response = response
        self.save(update_fields=["campay_reference", "raw_response", "updated_at"])

    def sync_status(self):
        """
        Interroge CamPay pour l'état réel (jamais un webhook non vérifié) et, à la
        première transition vers SUCCESSFUL, active/prolonge l'abonnement. Idempotent -
        y compris sous concurrence : un webhook et un polling client peuvent interroger
        et traiter la même transaction en même temps, sans jamais partager la même
        instance Python, donc le simple guard ci-dessus (`self.status == SUCCESSFUL`)
        ne suffit pas à lui seul à empêcher une double activation/récompense - voir le
        verrou de ligne plus bas.
        """
        if self.status == StatutTransaction.SUCCESSFUL:
            return self

        response = campay_client.get_transaction_status(self.campay_reference)
        self.raw_response = response
        self.status = response.get("status", self.status)
        self.save(update_fields=["status", "raw_response", "updated_at"])

        if self.status != StatutTransaction.SUCCESSFUL:
            return self

        with db_transaction.atomic():
            # select_for_update() : sérialise les appels concurrents sur CETTE ligne -
            # le deuxième appel bloque jusqu'à ce que le premier ait validé sa
            # transaction, puis relit un subscription_id déjà renseigné et n'agit
            # plus. Indisponible sur SQLite (utilisé pour les tests, voir
            # settings.DATABASES) : sans effet là-bas, mais le test unitaire ne
            # dépend pas d'un vrai verrou pour vérifier le contrat côté application.
            locked_qs = Transaction.objects.all()
            if connection.features.has_select_for_update:
                locked_qs = locked_qs.select_for_update()
            locked = locked_qs.get(pk=self.pk)

            if locked.subscription_id is not None:
                self.subscription = locked.subscription
                return self

            subscription = Subscription.objects.activate_or_extend(
                user=self.user, cursus=self.plan.cursus, duration_days=self.plan.effective_duration_days(),
            )
            locked.subscription = subscription
            locked.save(update_fields=["subscription", "updated_at"])
            self.subscription = subscription
            recompenser_parrainage(self)

        return self
