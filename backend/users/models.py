import random
import string

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .phone import to_e164

_REFERRAL_CODE_ALPHABET = string.ascii_uppercase + string.digits
_REFERRAL_CODE_LENGTH = 6


def _generate_referral_code():
    """
    Code court, opaque, indépendant du numéro de téléphone - un lien de parrainage
    partagé publiquement ne doit jamais encoder une donnée personnelle comme le
    numéro de l'utilisateur qui le partage.
    """
    return "".join(random.choices(_REFERRAL_CODE_ALPHABET, k=_REFERRAL_CODE_LENGTH))


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        # Normalisé ici plutôt que chez chaque appelant : c'est le seul chemin de
        # création d'un User, donc le seul endroit où garantir que rien n'entre en
        # base au format local historique. Accepte de ce fait les deux formats, ce
        # qui laisse les ~200 appels de test existants (`phone_number="677100001"`)
        # valides sans réécriture.
        phone_number = to_e164(phone_number) if phone_number else None
        if "email" in extra_fields:
            extra_fields["email"] = self.normalize_email(extra_fields["email"]) or None
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        if not user.referral_code:
            user.referral_code = user._generate_unique_referral_code()
        user.save(using=self._db)

        # Invariant tenu ici et nulle part ailleurs : tout compte porteur d'un numéro
        # a son identité `phone`. Le faire seulement dans verify_otp laisserait sans
        # identité tout compte créé par un autre chemin (admin, createsuperuser,
        # scripts d'import), qui ne pourrait alors plus se connecter par OTP puisque
        # c'est l'identité, et non le champ, qui décide quel compte est ouvert.
        if phone_number:
            AuthIdentity.objects.using(self._db).get_or_create(
                provider=AuthProvider.PHONE, provider_uid=phone_number, defaults={"user": user},
            )
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Contrairement à create_user, le numéro reste obligatoire ici : c'est
        # USERNAME_FIELD, donc le seul identifiant de connexion à l'admin Django.
        # Un superuser sans numéro serait créé sans aucun moyen de se connecter.
        if not phone_number:
            raise ValueError("Le numéro de téléphone est obligatoire pour un superuser.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r"^6\d{8}$",
    message="Le numéro doit être un numéro camerounais valide (9 chiffres, commençant par 6).",
)
"""
Format local camerounais à 9 chiffres. Ne valide plus l'identité d'un compte (voir
e164_validator) mais reste le format des numéros Mobile Money de payments : le
numéro qui paie n'est pas un identifiant, il est saisi tel qu'il est imprimé sur
le téléphone du payeur et transmis tel quel à l'opérateur.
"""

e164_validator = RegexValidator(
    regex=r"^\+[1-9]\d{7,14}$",
    message="Le numéro doit être au format international, ex : +237677123456.",
)

pseudo_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]{3,20}$",
    message="Le pseudo doit contenir entre 3 et 20 caractères : lettres, chiffres ou underscore.",
)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[e164_validator],
        help_text="Numéro au format international E.164, ex : +237677123456.",
    )
    """
    Nullable depuis la refonte multi-méthodes : un compte créé via un fournisseur
    tiers (voir AuthIdentity) n'a pas de numéro tant que l'utilisateur n'en rattache
    pas un. `unique` reste vrai malgré `null=True` - Postgres n'assimile jamais deux
    NULL, plusieurs comptes sans numéro coexistent donc sans violer la contrainte.

    N'est plus le sujet du JWT (voir SIMPLE_JWT dans settings.py, repassé sur `id`) :
    un identifiant de token doit être immuable, or un numéro se change et se
    réattribue - un token émis pour un numéro rendu puis réattribué désignerait
    sinon le nouveau titulaire.
    """

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Facultatif. Renseigné par l'utilisateur ou remonté par un fournisseur tiers.",
    )
    email_verified = models.BooleanField(
        default=False,
        help_text="Vrai uniquement si un fournisseur a attesté l'adresse, ou après vérification par lien.",
    )
    """
    Séparé de `email` volontairement : rattacher une identité tierce à un compte
    existant en se fiant à l'égalité des adresses n'est sûr que si l'adresse est
    attestée. Une adresse non vérifiée est déclarative, donc usurpable - la rattacher
    offrirait une prise de contrôle gratuite du compte portant la même adresse.
    """

    full_name = models.CharField(max_length=150, blank=True)
    pseudo = models.CharField(
        max_length=20, unique=True, null=True, blank=True,
        validators=[pseudo_validator],
        help_text="Nom d'affichage public facultatif, distinct du nom réel - "
                   "null (pas chaîne vide) tant qu'il n'est pas renseigné, pour rester unique.",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    referral_code = models.CharField(
        max_length=10, unique=True, blank=True,
        help_text="Code de parrainage opaque, généré à la création - jamais le numéro de téléphone.",
    )
    referred_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="filleuls",
        help_text="Renseigné une seule fois, à l'inscription, si un code de parrainage valide a été fourni.",
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    """
    USERNAME_FIELD reste le numéro bien qu'il soit désormais nullable : c'est ce que
    saisit un membre du staff pour se connecter à l'admin, et `createsuperuser`
    continue de l'exiger (voir UserManager.create_superuser). Un compte sans numéro
    n'est jamais authentifié par ce champ - `get_by_natural_key(None)` ne peut rien
    renvoyer, une comparaison SQL à NULL n'étant jamais vraie - mais par son
    AuthIdentity, ce qui est exactement le comportement voulu.
    """

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        # Un compte créé via un fournisseur tiers n'a ni numéro ni forcément de nom :
        # l'id reste le seul libellé toujours disponible, et l'admin doit pouvoir
        # afficher la ligne sans lever.
        return self.phone_number or self.email or self.pseudo or f"utilisateur #{self.pk}"

    def _generate_unique_referral_code(self):
        for _ in range(10):
            code = _generate_referral_code()
            if not User.objects.filter(referral_code=code).exists():
                return code
        # Probabilité astronomiquement faible avec 36^6 combinaisons - filet de
        # sécurité seulement, jamais censé se produire en pratique.
        raise RuntimeError("Impossible de générer un code de parrainage unique.")


class OTPCode(models.Model):
    """
    Code à usage unique envoyé par SMS pour l'authentification par téléphone.

    Chaque ligne vaut aussi pour un SMS réellement envoyé (request_otp n'en crée une
    qu'après avoir passé tous les garde-fous, voir users.otp_service) : cette table sert
    donc de registre de facturation autant que de registre d'authentification, et c'est
    elle qu'interrogent les plafonds par IP et le plafond global quotidien - plutôt
    qu'un compteur en cache, qui serait local à chaque worker gunicorn et donc
    contournable en frappant l'API assez vite pour tomber sur un autre worker.
    """

    phone_number = models.CharField(max_length=16)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="Adresse du demandeur, uniquement pour plafonner les envois par "
                  "source (voir users.otp_service). Donnée personnelle : jamais "
                  "exploitée ailleurs, et purgée avec la ligne par purge_otp_codes.",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number", "is_used"]),
            # Sert la fenêtre glissante par IP de request_otp (filtre sur ip_address
            # + created_at récent), qui tourne sur CHAQUE demande de code - la table
            # n'est purgée que périodiquement, donc elle peut être longue.
            models.Index(fields=["ip_address", "created_at"]),
            # Idem pour le plafond global, qui ne filtre que sur created_at.
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.phone_number} ({'utilisé' if self.is_used else 'actif'})"


class AuthProvider(models.TextChoices):
    PHONE = "phone", "Téléphone (OTP)"
    GOOGLE = "google", "Google"
    APPLE = "apple", "Apple"
    EMAIL = "email", "E-mail (lien magique)"
    PASSKEY = "passkey", "Clé d'accès"


class AuthIdentity(models.Model):
    """
    Une manière de prouver qu'on est un User donné. Un User en a une ou plusieurs, ce
    qui est tout l'objet de la refonte : jusqu'ici la seule preuve possible était la
    possession du numéro, et le numéro *était* le compte. Séparer les deux permet à un
    élève de commencer au téléphone puis de rattacher Google, ou de changer de numéro,
    sans jamais créer de doublon ni perdre abonnement et progression.

    Aucune méthode d'authentification tierce n'est encore branchée : ce modèle est
    posé maintenant parce qu'il conditionne le schéma (et donc la migration), pas
    parce que Google serait implémenté. La ligne `phone` de chaque compte existant est
    créée par la migration de données, pour qu'il n'y ait jamais de compte sans
    identité et que le code à venir n'ait pas à gérer ce cas de transition.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="identities")
    provider = models.CharField(max_length=20, choices=AuthProvider.choices)
    provider_uid = models.CharField(
        max_length=255,
        help_text="Identifiant stable chez le fournisseur : numéro E.164 pour `phone`, "
                  "`sub` OpenID pour Google/Apple, identifiant de credential pour une passkey.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Adresse telle que remontée par le fournisseur, conservée pour audit - "
                  "l'adresse faisant foi pour le compte reste User.email.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "identité de connexion"
        verbose_name_plural = "identités de connexion"
        ordering = ["provider", "-created_at"]
        constraints = [
            # Une identité chez un fournisseur ne peut désigner qu'un seul compte :
            # c'est cette contrainte, et non du code applicatif, qui interdit
            # structurellement qu'un même compte Google ouvre deux comptes Edukora.
            models.UniqueConstraint(
                fields=["provider", "provider_uid"], name="unique_identity_per_provider",
            ),
            # Un seul rattachement par fournisseur et par compte : un utilisateur n'a
            # pas deux comptes Google sur le même profil. Volontairement absent pour
            # PASSKEY, qui est l'exception - une clé par appareil est le cas normal.
            models.UniqueConstraint(
                fields=["user", "provider"],
                condition=~models.Q(provider="passkey"),
                name="unique_provider_per_user_except_passkey",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "provider"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_provider_display()}"
