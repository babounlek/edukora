import re

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from users.models import phone_validator

# Décisions du fondateur (2026-10-26, voir docs-revendeurs/CAHIER-DES-CHARGES.md) :
# 14 % de base, palier réservé aux commerciaux, commission valable 12 mois, acquise
# 14 jours après le paiement.
TAUX_BASE_PCT = 14
PALIER_SEUIL_COMMERCIAL = 30
PALIER_TAUX_COMMERCIAL_PCT = 17
FENETRE_COMMISSION_JOURS = 365
DELAI_ACQUISITION_JOURS = 14

CODE_REGEX = re.compile(r"^[A-Z0-9]{4,10}$")


class TypeRevendeur(models.TextChoices):
    COMMERCIAL = "COMMERCIAL", "Commercial"
    REPETITEUR = "REPETITEUR", "Répétiteur"
    ECOLE_CENTRE = "ECOLE_CENTRE", "École / centre"


class StatutRevendeur(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente d'activation"
    ACTIF = "ACTIF", "Actif"
    SUSPENDU = "SUSPENDU", "Suspendu"
    RESILIE = "RESILIE", "Résilié"


class Revendeur(models.Model):
    """
    Un partenaire qui apporte des clients à Edukora contre une commission sur leurs
    paiements. Il n'encaisse jamais pour Edukora : le client paie Edukora directement
    (Campay ou Mobile Money manuel), le revendeur ne touche que sa commission.

    Le `code` partage l'espace de noms de `User.referral_code` : le champ du formulaire
    d'inscription est unique, il résout d'abord un code revendeur puis un code parrain.
    D'où la vérification d'unicité croisée dans `clean`/`save`, et le filtre symétrique dans
    `User._generate_unique_referral_code`.
    """

    user = models.OneToOneField(
        "users.User", on_delete=models.PROTECT, related_name="revendeur",
        help_text="Compte Edukora avec lequel le revendeur se connecte à son espace.",
    )
    type = models.CharField(max_length=15, choices=TypeRevendeur.choices)
    nom_affiche = models.CharField(max_length=150)
    code = models.CharField(
        max_length=10, unique=True,
        help_text="4 à 10 caractères, majuscules et chiffres. Mis en majuscules à l'enregistrement.",
    )
    statut = models.CharField(max_length=12, choices=StatutRevendeur.choices, default=StatutRevendeur.EN_ATTENTE)

    taux_base_pct = models.PositiveSmallIntegerField(default=TAUX_BASE_PCT, validators=[MaxValueValidator(100)])
    palier_seuil = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=(
            "Commerciaux seulement : nombre de ventes dans le mois civil à partir duquel le taux de "
            "palier s'applique aux ventes SUIVANTES (palier marginal, jamais rétroactif)."
        ),
    )
    palier_taux_pct = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)])

    contrat_accepte_le = models.DateTimeField(null=True, blank=True)
    operateur_versement = models.CharField(max_length=10, blank=True)
    numero_versement = models.CharField(
        max_length=9, blank=True, validators=[phone_validator],
        help_text="Numéro Mobile Money (9 chiffres) qui reçoit les versements.",
    )
    notes = models.TextField(blank=True, help_text="Note interne, jamais montrée au revendeur.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nom_affiche"]
        verbose_name = "revendeur"

    def __str__(self):
        return f"{self.nom_affiche} ({self.code})"

    def clean(self):
        super().clean()
        self.code = (self.code or "").strip().upper()
        if not CODE_REGEX.match(self.code):
            raise ValidationError({"code": "4 à 10 caractères : majuscules et chiffres uniquement."})
        from users.models import User

        if User.objects.filter(referral_code=self.code).exists():
            raise ValidationError({"code": "Ce code est déjà utilisé comme code de parrainage d'un compte."})
        if (self.palier_seuil is None) != (self.palier_taux_pct is None):
            raise ValidationError("Le seuil et le taux du palier vont ensemble : renseigne les deux ou aucun.")
        if self.palier_seuil is not None and self.type != TypeRevendeur.COMMERCIAL:
            raise ValidationError("Le palier de bonus est réservé aux commerciaux.")

    def save(self, *args, **kwargs):
        creation = self._state.adding
        # Appliqué à la création uniquement : modifier plus tard un palier retiré à la
        # main ne doit pas le faire revenir.
        if creation and self.type == TypeRevendeur.COMMERCIAL and self.palier_seuil is None and self.palier_taux_pct is None:
            self.palier_seuil = PALIER_SEUIL_COMMERCIAL
            self.palier_taux_pct = PALIER_TAUX_COMMERCIAL_PCT
        # Garde de dernier recours pour les créations hors admin : l'admin passe déjà
        # par full_clean, ce chemin protège un `Revendeur.objects.create(...)`.
        self.clean()
        super().save(*args, **kwargs)


class SourceAttribution(models.TextChoices):
    INSCRIPTION = "INSCRIPTION", "Code saisi à l'inscription"
    PAIEMENT = "PAIEMENT", "Code saisi avant le premier paiement"
    ADMIN = "ADMIN", "Attribué par un administrateur"


class AttributionRevendeur(models.Model):
    """
    Lien unique entre un compte client et le revendeur qui l'a apporté. Un compte n'a
    jamais plus d'un revendeur (OneToOne), et l'attribution est figée une fois créée :
    seul un administrateur la modifie (l'historique des changements est celui du journal
    d'administration Django).

    Table à part plutôt que deux colonnes sur `User` : pas de migration sur le modèle
    utilisateur, et pas de dépendance circulaire entre les deux applications.
    """

    client = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="attribution_revendeur")
    revendeur = models.ForeignKey(Revendeur, on_delete=models.PROTECT, related_name="attributions")
    attribue_le = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=12, choices=SourceAttribution.choices, default=SourceAttribution.INSCRIPTION)

    class Meta:
        indexes = [models.Index(fields=["revendeur", "attribue_le"])]
        verbose_name = "attribution à un revendeur"
        verbose_name_plural = "attributions à un revendeur"

    def __str__(self):
        return f"{self.client} → {self.revendeur}"


class StatutCommission(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ANNULEE = "ANNULEE", "Annulée"
    # Posé par le futur écran de versements (phase 3) ; aucune action de la phase 1 ne
    # produit ce statut.
    PAYEE = "PAYEE", "Payée"


class CommissionDejaAcquise(Exception):
    """Annuler une commission acquise sans motif de fraude n'est pas permis."""


class Commission(models.Model):
    """
    Une ligne par paiement validé d'un client attribué. « En attente » et « acquise » ne
    sont pas stockées : une commission ACTIVE est en attente jusqu'à `acquise_le`, acquise
    ensuite (voir `etat`), ce qui évite toute tâche planifiée.
    """

    revendeur = models.ForeignKey(Revendeur, on_delete=models.PROTECT, related_name="commissions")
    client = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="commissions_revendeur")
    plan = models.ForeignKey("subscriptions.Plan", on_delete=models.PROTECT, related_name="commissions_revendeur")
    transaction = models.OneToOneField(
        "payments.Transaction", null=True, blank=True, on_delete=models.PROTECT, related_name="commission_revendeur",
    )
    manual_payment = models.OneToOneField(
        "payments.ManualPayment", null=True, blank=True, on_delete=models.PROTECT, related_name="commission_revendeur",
    )

    base_fcfa = models.PositiveIntegerField(help_text="Montant réellement encaissé, figé à la création.")
    taux_pct = models.PositiveSmallIntegerField(help_text="Taux appliqué, figé à la création.")
    montant_fcfa = models.PositiveIntegerField(help_text="Commission, arrondie au franc inférieur.")

    statut = models.CharField(max_length=10, choices=StatutCommission.choices, default=StatutCommission.ACTIVE)
    acquise_le = models.DateTimeField()
    a_verifier = models.BooleanField(
        default=False,
        help_text="Retenue tant qu'un administrateur n'a pas levé le drapeau (montant suspect, revendeur suspendu…).",
    )
    motif_a_verifier = models.CharField(max_length=200, blank=True)
    motif_annulation = models.CharField(max_length=200, blank=True)
    annulee_le = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["revendeur", "created_at"]),
            models.Index(fields=["statut", "a_verifier"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(transaction__isnull=False) ^ models.Q(manual_payment__isnull=False),
                name="commission_revendeur_exactly_one_source",
            ),
        ]

    def __str__(self):
        return f"{self.revendeur} +{self.montant_fcfa} FCFA ({self.get_statut_display()})"

    @property
    def etat(self):
        """ANNULEE, PAYEE, EN_ATTENTE ou ACQUISE."""
        if self.statut != StatutCommission.ACTIVE:
            return self.statut
        return "ACQUISE" if timezone.now() >= self.acquise_le else "EN_ATTENTE"

    def annuler(self, motif, *, fraude=False):
        """
        Annule une commission ACTIVE. Après acquisition, seule une fraude avérée le permet
        (`fraude=True`) : le montant sera alors déduit du prochain versement (phase 3).
        """
        if self.statut != StatutCommission.ACTIVE:
            raise ValueError(f"Commission #{self.pk} déjà {self.get_statut_display().lower()}.")
        if self.etat == "ACQUISE" and not fraude:
            raise CommissionDejaAcquise(f"Commission #{self.pk} déjà acquise : seule une fraude permet de l'annuler.")
        self.statut = StatutCommission.ANNULEE
        self.motif_annulation = (motif or "")[:200]
        self.annulee_le = timezone.now()
        self.save(update_fields=["statut", "motif_annulation", "annulee_le"])
