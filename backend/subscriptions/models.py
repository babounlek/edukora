from django.db import connection, models
from django.db import transaction as db_transaction
from django.utils import timezone

from catalog.models import Cursus, ExamSession


class DureeMode(models.TextChoices):
    FIXE = "FIXE", "Durée fixe"
    JUSQUA_EXAMEN = "JUSQUA_EXAMEN", "Jusqu'à l'examen"


class Plan(models.Model):
    """Offre commerciale : ce qu'un utilisateur achète (prix, durée, périmètre d'accès)."""

    name = models.CharField(max_length=100)
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="plans")
    price = models.PositiveIntegerField(help_text="Prix en FCFA.")
    duration_mode = models.CharField(max_length=20, choices=DureeMode.choices, default=DureeMode.FIXE)
    duration_days = models.PositiveSmallIntegerField(
        default=30,
        help_text="Utilisé tel quel si duration_mode=FIXE. Ignoré (valeur de repli seulement, voir effective_duration_days) si duration_mode=JUSQUA_EXAMEN.",
    )
    is_active = models.BooleanField(default=True, help_text="Décoche pour retirer une offre du catalogue sans la supprimer.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cursus", "price"]

    def __str__(self):
        return f"{self.name} ({self.price} FCFA / {self.duration_days}j)"

    def effective_duration_days(self):
        """
        Durée réelle en jours à appliquer à l'activation/l'affichage. Pour
        JUSQUA_EXAMEN, calculée dynamiquement depuis la prochaine ExamSession de
        l'examen du cursus - jamais figée dans duration_days, pour rester correcte
        d'une session d'examen sur l'autre sans avoir à rééditer le Plan chaque année.
        """
        if self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            return self.duration_days
        session = ExamSession.prochaine_pour(self.cursus.country, self.cursus.examen)
        if session is None:
            # Aucune date d'examen configurée pour ce (pays, examen) : filet de
            # sécurité, on retombe sur duration_days plutôt que de bloquer un
            # paiement déjà encaissé ou d'afficher une durée absurde.
            return self.duration_days
        jours = (session.date_debut - timezone.now().date()).days
        return max(jours, 1)


class SubscriptionManager(models.Manager):
    def activate_or_extend(self, user, cursus, duration_days):
        """
        Point de passage unique pour toute prolongation d'abonnement (paiement direct
        du filleul comme récompense de parrainage au parrain) - deux appels concurrents
        sur le même (user, cursus) (ex. le paiement du filleul et sa récompense au
        parrain qui se chevauchent, ou deux paiements distincts qui se terminent en
        même temps) ne doivent jamais s'écraser l'un l'autre : chacun doit s'appliquer
        sur la valeur déjà prolongée par l'autre, pas sur une valeur périmée lue avant
        que l'autre n'ait sauvegardé.
        """
        with db_transaction.atomic():
            subscription, created = self.get_or_create(
                user=user, cursus=cursus,
                defaults={"expires_at": timezone.now() + timezone.timedelta(days=duration_days)},
            )
            if not created:
                # select_for_update() : verrouille la ligne avant de (re)lire
                # expires_at, pour que le calcul d'extend() reparte toujours de la
                # valeur la plus à jour. Indisponible sur SQLite (tests) - voir la
                # même remarque dans payments.models.Transaction.sync_status.
                locked_qs = self.select_for_update() if connection.features.has_select_for_update else self
                subscription = locked_qs.get(pk=subscription.pk)
                subscription.extend(duration_days)
        return subscription


class Subscription(models.Model):
    """
    Accès actif d'un utilisateur à un Cursus. Une seule ligne par (user, cursus) :
    chaque paiement réussi prolonge expires_at plutôt que de créer une nouvelle ligne.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="subscriptions")
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="subscriptions")
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SubscriptionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "cursus"], name="unique_subscription_per_cursus"),
        ]

    def __str__(self):
        return f"{self.user} - {self.cursus} (expire {self.expires_at:%d/%m/%Y})"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def extend(self, duration_days):
        """Prolonge à partir de la date d'expiration existante si encore active, sinon à partir de maintenant."""
        base = self.expires_at if self.is_active else timezone.now()
        self.expires_at = base + timezone.timedelta(days=duration_days)
        self.save(update_fields=["expires_at", "updated_at"])


PARRAINAGE_JOURS_OFFERTS = 7


class ParrainageRecompense(models.Model):
    """
    Trace qu'un parrainage a été récompensé, une ligne par transaction filleul ayant
    déclenché la récompense - sert à la fois de garde-fou anti double-crédit (la
    OneToOneField sur `transaction` empêche toute création en double) et d'historique
    consultable (combien de jours offerts, à qui, pour quel filleul).
    """

    parrain = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainages_recompenses")
    filleul = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainage_recompense")
    transaction = models.OneToOneField(
        "payments.Transaction", on_delete=models.CASCADE, related_name="parrainage_recompense",
    )
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT)
    jours_offerts = models.PositiveSmallIntegerField(default=PARRAINAGE_JOURS_OFFERTS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parrain} récompensé pour le parrainage de {self.filleul} (+{self.jours_offerts}j)"


def recompenser_parrainage(transaction):
    """
    Si l'utilisateur de `transaction` a été parrainé ET que cette transaction est sa
    toute première réussie, prolonge l'abonnement du parrain (sur le même cursus que
    l'achat du filleul) de PARRAINAGE_JOURS_OFFERTS jours. Ne récompense jamais un
    réabonnement du filleul - seulement sa toute première conversion - pour éviter
    qu'un parrain accumule des jours à chaque renouvellement de son filleul.

    Appelée depuis Transaction.sync_status() une fois l'abonnement du filleul déjà
    activé - l'import de StatutTransaction est local pour éviter un import circulaire
    (payments.models importe déjà subscriptions.models au niveau module).
    """
    from payments.models import StatutTransaction

    filleul = transaction.user
    parrain = filleul.referred_by
    if parrain is None:
        return

    premiere_conversion = not filleul.transactions.filter(
        status=StatutTransaction.SUCCESSFUL,
    ).exclude(pk=transaction.pk).exists()
    if not premiere_conversion:
        return

    Subscription.objects.activate_or_extend(
        user=parrain, cursus=transaction.plan.cursus, duration_days=PARRAINAGE_JOURS_OFFERTS,
    )
    ParrainageRecompense.objects.get_or_create(
        transaction=transaction,
        defaults={
            "parrain": parrain, "filleul": filleul,
            "cursus": transaction.plan.cursus, "jours_offerts": PARRAINAGE_JOURS_OFFERTS,
        },
    )
