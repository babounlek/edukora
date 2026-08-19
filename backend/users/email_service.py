"""
Connexion par code envoyé par e-mail - même patron que users.otp_service (canal SMS),
avec ses propres garde-fous et sa propre exception par type d'échec plutôt que de
réutiliser OTPThrottled/OTPCapReached/OTPInvalid : les deux canaux partagent la table
OTPCode (voir CodeCanal) mais pas leurs coûts (un SMS se facture, un e-mail non), et le
frontend doit pouvoir distinguer sans ambiguïté d'où vient chaque erreur.
"""

import logging
import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import AuthIdentity, AuthProvider, CodeCanal, OTPCode, User

logger = logging.getLogger("users.email")

EMAIL_CODE_VALIDITY_MINUTES = 5
EMAIL_CODE_MIN_INTERVAL_SECONDS = 60
EMAIL_CODE_MAX_ATTEMPTS = 5
# Mêmes fenêtres glissantes que le canal SMS (voir users.otp_service) - un plafond
# calendaire se réinitialiserait d'un coup à minuit et laisserait passer deux pleines
# rafales à cheval sur le changement de jour. Les plafonds eux-mêmes (EMAIL_CODE_
# MAX_PER_IP_PER_HOUR / EMAIL_CODE_DAILY_GLOBAL_CAP) vivent dans les settings.
EMAIL_CODE_IP_WINDOW = timedelta(hours=1)
EMAIL_CODE_GLOBAL_WINDOW = timedelta(hours=24)


class EmailThrottled(Exception):
    pass


class EmailCapReached(Exception):
    """Plafond global d'envois atteint - voir OTPCapReached, même rôle côté e-mail."""


class EmailInvalid(Exception):
    pass


class EmailSendFailed(Exception):
    """
    Échec de la remise (SMTP en panne, domaine expéditeur mal configuré...) - jamais
    laissé remonter tel quel : ni l'appelant HTTP ni le frontend ne savent quoi faire
    d'une OSError SMTP, alors qu'une indisponibilité de service (503) est actionnable.
    """


class EmailAlreadyTaken(Exception):
    """L'adresse visée sert déjà à ouvrir un autre compte."""


def normalize_email(email):
    """
    Tout en minuscules, partie locale comprise : à la différence de la RFC (qui
    laisse la partie locale sensible à la casse), en pratique aucun fournisseur grand
    public n'en tient compte, et laisser passer la casse ferait exister
    "Eleve@x.com" et "eleve@x.com" comme deux adresses distinctes aux yeux de la
    contrainte unique de User.email - une même boîte pourrait alors ouvrir deux comptes.
    """
    return email.strip().lower()


def request_email_code(email, ip_address=None):
    """Mêmes trois garde-fous que request_otp, adaptés au canal e-mail - voir sa
    docstring pour le détail de chacun."""
    email = normalize_email(email)
    now = timezone.now()

    recent = (
        OTPCode.objects.filter(canal=CodeCanal.EMAIL, destination=email)
        .order_by("-created_at").first()
    )
    if recent and (now - recent.created_at).total_seconds() < EMAIL_CODE_MIN_INTERVAL_SECONDS:
        raise EmailThrottled("Merci de patienter avant de redemander un code.")

    if ip_address:
        sent_from_ip = OTPCode.objects.filter(
            canal=CodeCanal.EMAIL, ip_address=ip_address, created_at__gt=now - EMAIL_CODE_IP_WINDOW,
        ).count()
        if sent_from_ip >= settings.EMAIL_CODE_MAX_PER_IP_PER_HOUR:
            logger.warning(
                "Plafond e-mail par IP atteint (%s envois sur la dernière heure) pour %s.",
                sent_from_ip, ip_address,
            )
            raise EmailThrottled(
                "Trop de demandes de code depuis cette connexion. Merci de réessayer dans une heure.",
            )

    sent_globally = OTPCode.objects.filter(
        canal=CodeCanal.EMAIL, created_at__gt=now - EMAIL_CODE_GLOBAL_WINDOW,
    ).count()
    if sent_globally >= settings.EMAIL_CODE_DAILY_GLOBAL_CAP:
        logger.error(
            "Plafond e-mail global atteint : %s envois sur les dernières 24 h (plafond %s). "
            "Aucun code ne sera envoyé tant que la fenêtre ne s'est pas dégagée.",
            sent_globally, settings.EMAIL_CODE_DAILY_GLOBAL_CAP,
        )
        raise EmailCapReached(
            "Service d'envoi de code temporairement indisponible. Merci de réessayer plus tard.",
        )

    code = f"{random.randint(0, 999999):06d}"
    # Créée AVANT l'envoi, et jamais retirée si celui-ci échoue (voir plus bas) : cette
    # ligne fait courir le délai anti-renvoi ci-dessus, sans quoi un échec SMTP
    # répété permettrait de recommencer immédiatement à chaque tentative.
    OTPCode.objects.create(
        canal=CodeCanal.EMAIL,
        destination=email,
        code=code,
        expires_at=now + timedelta(minutes=EMAIL_CODE_VALIDITY_MINUTES),
        ip_address=ip_address,
    )

    # Le code figure dans l'OBJET du message, pas seulement le corps : c'est ce qui le
    # rend lisible depuis une notification système sans ouvrir le message, comme le SMS
    # l'est depuis l'écran de verrouillage.
    try:
        send_mail(
            subject=f"Ton code {settings.SITE_NAME} : {code}",
            message=(
                f"Ton code de connexion {settings.SITE_NAME} est {code}.\n\n"
                f"Il est valable {EMAIL_CODE_VALIDITY_MINUTES} minutes. Si tu n'es pas à "
                f"l'origine de cette demande, ignore ce message."
            ),
            from_email=None,  # repli sur settings.DEFAULT_FROM_EMAIL
            recipient_list=[email],
        )
    except Exception as exc:
        logger.exception("Envoi du code e-mail échoué pour %s", email)
        raise EmailSendFailed(
            "Envoi du code impossible pour le moment. Merci de réessayer plus tard.",
        ) from exc


def consume_email_code(email, code):
    """
    Valide un code et le consomme, sans rien décider du compte - même rôle que
    consume_otp côté téléphone (voir users.account.confirm_email_link, qui en a
    besoin sans la création de compte que verify_email_code enchaîne).
    """
    email = normalize_email(email)
    entry = (
        OTPCode.objects.filter(canal=CodeCanal.EMAIL, destination=email, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if entry is None or entry.expires_at < timezone.now():
        raise EmailInvalid("Code invalide ou expiré.")

    if entry.attempts >= EMAIL_CODE_MAX_ATTEMPTS:
        raise EmailInvalid("Trop de tentatives pour ce code, redemandez-en un nouveau.")

    entry.attempts += 1
    entry.save(update_fields=["attempts"])

    if entry.code != code:
        raise EmailInvalid("Code invalide ou expiré.")

    entry.is_used = True
    entry.save(update_fields=["is_used"])
    return email


def verify_email_code(email, code, referral_code=""):
    """
    Vérifie le code puis retourne (User, créé) - même contrat que verify_otp.

    Trois cas, du plus courant au plus rare :
    1. Une identité `email` existe déjà pour cette adresse : on rouvre son compte.
    2. Aucune identité, mais un compte porte déjà cette adresse comme e-mail VÉRIFIÉ
       (attesté par un autre moyen, ex. Google) : le code vient de prouver exactement
       ce que Google attestait déjà, donc on rattache l'identité à ce même compte
       plutôt que d'ouvrir un doublon.
    3. Aucun des deux, mais un AUTRE compte porte cette adresse sans preuve (simple
       champ renseigné, jamais vérifié) : la création échouerait de toute façon sur la
       contrainte unique de User.email, avec une erreur incompréhensible - on le
       détecte avant, avec un message actionnable (EmailAlreadyTaken).
    """
    email = consume_email_code(email, code)

    identity = (
        AuthIdentity.objects.filter(provider=AuthProvider.EMAIL, provider_uid=email)
        .select_related("user").first()
    )
    user = identity.user if identity else None
    cree = False

    if user is None:
        attested = User.objects.filter(email=email, email_verified=True).first()
        if attested is not None:
            user = attested
            AuthIdentity.objects.update_or_create(
                user=user, provider=AuthProvider.EMAIL,
                defaults={"provider_uid": email, "email": email},
            )
        else:
            conflit = (
                User.objects.filter(email=email).exists()
                or AuthIdentity.objects.filter(provider=AuthProvider.EMAIL, provider_uid=email).exists()
            )
            if conflit:
                raise EmailAlreadyTaken(
                    "Cette adresse est déjà utilisée par un autre compte. Connecte-toi "
                    "avec cette adresse, ou utilises-en une autre.",
                )
            cree = True
            user = User.objects.create_user(phone_number=None, email=email, email_verified=True)
            # Contrairement au numéro, create_user ne pose pas elle-même l'identité
            # `email` (voir UserManager._create_user, qui ne le fait que pour le
            # numéro - c'est USERNAME_FIELD, l'e-mail ne l'est pas).
            AuthIdentity.objects.create(user=user, provider=AuthProvider.EMAIL, provider_uid=email, email=email)
            if referral_code:
                parrain = User.objects.filter(referral_code=referral_code.strip().upper()).exclude(pk=user.pk).first()
                if parrain is not None:
                    user.referred_by = parrain
                    user.save(update_fields=["referred_by"])

    identity = user.identities.get(provider=AuthProvider.EMAIL)
    identity.last_used_at = timezone.now()
    identity.save(update_fields=["last_used_at"])

    return user, cree
