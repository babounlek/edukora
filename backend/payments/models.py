import uuid

from django.db import connection, models
from django.db import transaction as db_transaction
from django.utils import timezone

from subscriptions.models import (
    InscriptionInedite,
    InscriptionRepetiteur,
    Plan,
    ProductType,
    Subscription,
    recompenser_parrainage,
)
from users.models import phone_validator

from . import campay_client


class StatutTransaction(models.TextChoices):
    PENDING = "PENDING", "En attente"
    SUCCESSFUL = "SUCCESSFUL", "Réussie"
    FAILED = "FAILED", "Échouée"


def _activer_acces(plan, user):
    """
    Point de bascule unique entre les types de produit (voir
    subscriptions.models.ProductType) - jamais dupliqué entre Transaction.sync_status et
    ManualPayment.approve, qui l'appellent tous les deux au même point de leur flux
    (après verrouillage, avant écriture du statut final). Retourne un triplet
    (subscription, inscription_inedite, inscription_repetiteur) - au moins l'un des
    trois est renseigné ; subscription et inscription_inedite le sont tous les deux pour
    un Plan ABONNEMENT avec `inclut_inedit=True` (ex. la formule Max), qui active
    l'abonnement de base ET l'add-on Épreuves Inédites en un seul paiement, pour la même
    durée. `Transaction`/`ManualPayment` acceptent bien plusieurs FK renseignées à la
    fois (pas de contrainte base "exactement une seule") - seuls les cas ADDON_INEDIT et
    ADDON_REPETITEUR purs restent exclusifs (aucun sens à activer un abonnement de base
    pour l'achat d'un add-on seul).
    """
    duration_days = plan.effective_duration_days()
    if plan.product_type == ProductType.ADDON_INEDIT:
        inscription_inedite = InscriptionInedite.objects.activate_or_extend(
            user=user, cursus=plan.cursus, duration_days=duration_days,
        )
        return None, inscription_inedite, None
    if plan.product_type == ProductType.ADDON_REPETITEUR:
        inscription_repetiteur = InscriptionRepetiteur.objects.activate_or_extend(
            user=user, cursus=plan.cursus, duration_days=duration_days,
        )
        return None, None, inscription_repetiteur
    subscription = Subscription.objects.activate_or_extend(
        user=user, cursus=plan.cursus, duration_days=duration_days,
    )
    inscription_inedite = None
    if plan.inclut_inedit:
        inscription_inedite = InscriptionInedite.objects.activate_or_extend(
            user=user, cursus=plan.cursus, duration_days=duration_days,
        )
    return subscription, inscription_inedite, None


class Transaction(models.Model):
    """Une tentative de paiement Mobile Money : achat/renouvellement d'un Plan d'abonnement ou d'un add-on."""

    user = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="transactions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="transactions")
    subscription = models.ForeignKey(
        Subscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions",
        help_text="Renseigné une fois le paiement d'un Plan ABONNEMENT confirmé et l'abonnement activé/prolongé.",
    )
    inscription_inedite = models.ForeignKey(
        InscriptionInedite, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions",
        help_text="Renseigné une fois le paiement d'un Plan ADDON_INEDIT confirmé - exclusif avec `subscription` (voir _activer_acces).",
    )
    inscription_repetiteur = models.ForeignKey(
        InscriptionRepetiteur, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions",
        help_text="Renseigné une fois le paiement d'un Plan ADDON_REPETITEUR confirmé - exclusif avec `subscription` (voir _activer_acces).",
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

            if (
                locked.subscription_id is not None
                or locked.inscription_inedite_id is not None
                or locked.inscription_repetiteur_id is not None
            ):
                self.subscription = locked.subscription
                self.inscription_inedite = locked.inscription_inedite
                self.inscription_repetiteur = locked.inscription_repetiteur
                return self

            subscription, inscription_inedite, inscription_repetiteur = _activer_acces(self.plan, self.user)
            locked.subscription = subscription
            locked.inscription_inedite = inscription_inedite
            locked.inscription_repetiteur = inscription_repetiteur
            locked.save(update_fields=[
                "subscription", "inscription_inedite", "inscription_repetiteur", "updated_at",
            ])
            self.subscription = subscription
            self.inscription_inedite = inscription_inedite
            self.inscription_repetiteur = inscription_repetiteur
            recompenser_parrainage(self)

        return self


class MobileMoneyOperator(models.TextChoices):
    ORANGE = "ORANGE", "Orange Money"
    MTN = "MTN", "MTN Mobile Money"


class MobileMoneyAccount(models.Model):
    """
    Compte de réception configuré par un administrateur pour un opérateur - jamais
    codé en dur dans le frontend ni le backend (voir mission paiement manuel,
    section 11). `operator` unique : un seul compte affiché par opérateur, `active`
    permet de le retirer temporairement de l'étape "instructions de paiement" sans
    supprimer la configuration (ex. compte momentanément indisponible).
    """

    operator = models.CharField(max_length=10, choices=MobileMoneyOperator.choices, unique=True)
    phone_number = models.CharField(max_length=9, validators=[phone_validator])
    account_name = models.CharField(max_length=150, help_text="Nom du bénéficiaire affiché à l'utilisateur.")
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "compte Mobile Money"
        verbose_name_plural = "comptes Mobile Money"

    def __str__(self):
        return f"{self.get_operator_display()} - {self.phone_number}"


class ManualPaymentStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    APPROVED = "APPROVED", "Validé"
    REJECTED = "REJECTED", "Rejeté"


class ManualPaymentRejectReason(models.TextChoices):
    TRANSACTION_INTROUVABLE = "TRANSACTION_INTROUVABLE", "Transaction introuvable"
    MONTANT_INCORRECT = "MONTANT_INCORRECT", "Montant incorrect"
    TRANSACTION_DEJA_UTILISEE = "TRANSACTION_DEJA_UTILISEE", "Transaction déjà utilisée"
    MAUVAIS_OPERATEUR = "MAUVAIS_OPERATEUR", "Mauvais opérateur"
    PAIEMENT_NON_RECU = "PAIEMENT_NON_RECU", "Paiement non reçu"
    INFORMATIONS_INCOHERENTES = "INFORMATIONS_INCOHERENTES", "Informations incohérentes"
    AUTRE = "AUTRE", "Autre"


class ManualPaymentAlreadyReviewed(Exception):
    """
    Levée quand approve()/reject() est appelé sur une ligne qui n'est déjà plus
    PENDING - double-clic admin, deux administrateurs concurrents, ou tentative de
    re-décider un paiement déjà tranché. Jamais une simple no-op silencieuse : on
    veut que l'appelant (ManualPaymentAdmin.save_model) puisse le signaler
    explicitement plutôt que de laisser croire qu'une action vient d'avoir lieu.
    """


def _manual_payment_proof_path(instance, filename):
    return f"manual_payments/{instance.user_id}/{uuid.uuid4()}_{filename}"


def _notifier_utilisateur(phone_number, message):
    """Seul canal sortant vers l'utilisateur dans Edukora - voir users.sms_backends,
    déjà utilisé pour l'OTP. Pas de nouveau système de notification créé ici."""
    from users.sms_backends import get_sms_backend

    get_sms_backend().send(phone_number, message)


class ManualPaymentManager(models.Manager):
    def declare(self, *, user, plan, operator, amount_declared, payer_phone_number,
                transaction_reference, paid_at=None, proof=None, ip=None):
        """
        Point d'entrée unique de la déclaration utilisateur. `amount_expected` est
        TOUJOURS recalculé depuis `plan.effective_price()` ici - jamais accepté depuis
        le client, qui pourrait sinon déclarer n'importe quel montant pour un cursus à
        5000 FCFA (voir mission, section 8). `effective_price()` plutôt que `price` brut :
        pour un Plan JUSQUA_EXAMEN, le prix réel dépend de la date d'achat (voir
        subscriptions.models.Plan.effective_price), le prix attendu doit refléter la
        même règle que celle appliquée au paiement Campay. La référence est normalisée
        (espace/casse) pour empêcher un contournement trivial de la contrainte d'unicité.
        """
        reference = (transaction_reference or "").strip().upper()

        payment = self.create(
            user=user, plan=plan, operator=operator,
            amount_expected=plan.effective_price(), amount_declared=amount_declared,
            payer_phone_number=payer_phone_number, transaction_reference=reference,
            paid_at=paid_at, proof=proof, declared_ip=ip,
        )
        _notifier_utilisateur(
            user.phone_number,
            f"Edukora : ta déclaration de paiement #{payment.id} a bien été enregistrée. "
            "Elle est en cours de vérification par notre équipe.",
        )
        return payment


class ManualPayment(models.Model):
    """
    Déclaration par l'utilisateur d'un paiement Mobile Money effectué manuellement
    (hors API), en attente de vérification humaine contre le SMS reçu sur le compte
    Edukora. Ne vaut jamais activation d'abonnement à elle seule - voir approve().
    """

    user = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="manual_payments")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="manual_payments")
    subscription = models.ForeignKey(
        Subscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="manual_payments",
        help_text="Renseigné une fois un paiement de Plan ABONNEMENT approuvé et l'abonnement activé/prolongé.",
    )
    inscription_inedite = models.ForeignKey(
        InscriptionInedite, null=True, blank=True, on_delete=models.SET_NULL, related_name="manual_payments",
        help_text="Renseigné une fois un paiement de Plan ADDON_INEDIT approuvé - exclusif avec `subscription`.",
    )
    inscription_repetiteur = models.ForeignKey(
        InscriptionRepetiteur, null=True, blank=True, on_delete=models.SET_NULL, related_name="manual_payments",
        help_text="Renseigné une fois un paiement de Plan ADDON_REPETITEUR approuvé - exclusif avec `subscription`.",
    )

    operator = models.CharField(max_length=10, choices=MobileMoneyOperator.choices)
    amount_expected = models.PositiveIntegerField(
        help_text="Recalculé depuis plan.price au moment de la déclaration - jamais fourni par le client.",
    )
    amount_declared = models.PositiveIntegerField(help_text="Montant que l'utilisateur affirme avoir payé.")
    payer_phone_number = models.CharField(
        max_length=9, validators=[phone_validator],
        help_text="Numéro ayant réellement effectué le paiement (peut différer du compte Edukora du payeur).",
    )
    transaction_reference = models.CharField(max_length=100, help_text="Référence/numéro de transaction Mobile Money, normalisée (majuscules, sans espaces).")
    paid_at = models.DateTimeField(null=True, blank=True, help_text="Date/heure du paiement déclarée par l'utilisateur.")
    proof = models.FileField(
        upload_to=_manual_payment_proof_path, null=True, blank=True,
        help_text="Capture d'écran optionnelle du SMS de confirmation - jamais une preuve fiable à elle seule, la validation reste administrative.",
    )

    status = models.CharField(max_length=10, choices=ManualPaymentStatus.choices, default=ManualPaymentStatus.PENDING)
    rejection_reason = models.CharField(max_length=30, choices=ManualPaymentRejectReason.choices, blank=True)
    admin_comment = models.TextField(blank=True, help_text="Note interne libre de l'administrateur.")
    reviewed_by = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="manual_payments_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    declared_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ManualPaymentManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_reference"]),
        ]
        constraints = [
            # Une même référence ne peut pas être déclarée deux fois tant qu'une
            # déclaration est PENDING ou déjà APPROVED - mais une fois REJECTED, elle
            # se libère (permet de corriger une faute de frappe/un montant mal
            # déclaré sans changer de transaction réelle). Portée par opérateur, pas
            # par plan/utilisateur : couvre aussi bien la réutilisation par un autre
            # utilisateur que pour un autre cursus (voir mission, section 6).
            models.UniqueConstraint(
                fields=["operator", "transaction_reference"],
                condition=models.Q(status__in=["PENDING", "APPROVED"]),
                name="unique_active_manual_payment_reference_per_operator",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.plan} - {self.amount_declared} FCFA ({self.status})"

    def _locked(self):
        """Recharge cette ligne verrouillée (voir la même remarque dans
        Transaction.sync_status : select_for_update() est sans effet sur SQLite,
        utilisé pour les tests, mais la logique applicative ne doit pas en dépendre)."""
        qs = ManualPayment.objects.all()
        if connection.features.has_select_for_update:
            qs = qs.select_for_update()
        return qs.get(pk=self.pk)

    def approve(self, admin_user):
        """
        PENDING -> APPROVED. Réutilise le même point de convergence que Campay
        (_activer_acces) et la même récompense de parrainage - le paiement manuel ne
        doit jamais avoir sa propre logique d'activation. Le verrou + recheck du statut
        à l'intérieur de la transaction
        protège un double-clic ou deux administrateurs validant la même ligne en
        même temps (voir mission, section 15) : le perdant lève
        ManualPaymentAlreadyReviewed plutôt que de prolonger l'abonnement deux fois.
        """
        with db_transaction.atomic():
            locked = self._locked()
            if locked.status != ManualPaymentStatus.PENDING:
                raise ManualPaymentAlreadyReviewed(
                    f"Paiement #{locked.pk} déjà traité (statut actuel : {locked.status}).",
                )

            subscription, inscription_inedite, inscription_repetiteur = _activer_acces(locked.plan, locked.user)
            locked.status = ManualPaymentStatus.APPROVED
            locked.subscription = subscription
            locked.inscription_inedite = inscription_inedite
            locked.inscription_repetiteur = inscription_repetiteur
            locked.reviewed_by = admin_user
            locked.reviewed_at = timezone.now()
            locked.save(update_fields=[
                "status", "subscription", "inscription_inedite", "inscription_repetiteur",
                "reviewed_by", "reviewed_at", "updated_at",
            ])
            recompenser_parrainage(locked)

        _notifier_utilisateur(
            locked.user.phone_number,
            f"Edukora : ton paiement #{locked.id} est validé ! Ton abonnement est actif.",
        )
        return locked

    def reject(self, admin_user, reason, comment=""):
        """PENDING -> REJECTED. Motif obligatoire (voir ManualPaymentAdmin, qui le
        fait respecter côté formulaire) ; libère la référence pour une nouvelle
        déclaration (voir la contrainte d'unicité conditionnelle ci-dessus)."""
        with db_transaction.atomic():
            locked = self._locked()
            if locked.status != ManualPaymentStatus.PENDING:
                raise ManualPaymentAlreadyReviewed(
                    f"Paiement #{locked.pk} déjà traité (statut actuel : {locked.status}).",
                )

            locked.status = ManualPaymentStatus.REJECTED
            locked.rejection_reason = reason
            locked.admin_comment = comment
            locked.reviewed_by = admin_user
            locked.reviewed_at = timezone.now()
            locked.save(update_fields=[
                "status", "rejection_reason", "admin_comment", "reviewed_by", "reviewed_at", "updated_at",
            ])

        _notifier_utilisateur(
            locked.user.phone_number,
            f"Edukora : ton paiement #{locked.id} a été rejeté ({locked.get_rejection_reason_display()}). "
            "Tu peux déclarer un nouveau paiement.",
        )
        return locked
