import random
import string

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

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
        if not phone_number:
            raise ValueError("Le numéro de téléphone est obligatoire.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        if not user.referral_code:
            user.referral_code = user._generate_unique_referral_code()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r"^6\d{8}$",
    message="Le numéro doit être un numéro camerounais valide (9 chiffres, commençant par 6).",
)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[phone_validator],
        help_text="Numéro camerounais sans indicatif, ex: 677123456",
    )
    full_name = models.CharField(max_length=150, blank=True)
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
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        return self.phone_number

    def _generate_unique_referral_code(self):
        for _ in range(10):
            code = _generate_referral_code()
            if not User.objects.filter(referral_code=code).exists():
                return code
        # Probabilité astronomiquement faible avec 36^6 combinaisons - filet de
        # sécurité seulement, jamais censé se produire en pratique.
        raise RuntimeError("Impossible de générer un code de parrainage unique.")


class OTPCode(models.Model):
    """Code à usage unique envoyé par SMS pour l'authentification par téléphone."""

    phone_number = models.CharField(max_length=9)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number", "is_used"]),
        ]

    def __str__(self):
        return f"{self.phone_number} ({'utilisé' if self.is_used else 'actif'})"
