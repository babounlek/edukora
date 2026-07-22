import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import OTPCode, User
from .sms_backends import get_sms_backend

OTP_VALIDITY_MINUTES = 5
OTP_MIN_INTERVAL_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


class OTPThrottled(Exception):
    pass


class OTPInvalid(Exception):
    pass


def request_otp(phone_number):
    recent = OTPCode.objects.filter(phone_number=phone_number).order_by("-created_at").first()
    if recent and (timezone.now() - recent.created_at).total_seconds() < OTP_MIN_INTERVAL_SECONDS:
        raise OTPThrottled("Merci de patienter avant de redemander un code.")

    code = f"{random.randint(0, 999999):06d}"
    OTPCode.objects.create(
        phone_number=phone_number,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES),
    )
    get_sms_backend().send(
        phone_number, f"Votre code {settings.SITE_NAME} : {code} (valable {OTP_VALIDITY_MINUTES} minutes).",
    )


def verify_otp(phone_number, code, referral_code=""):
    """
    Vérifie le code puis retourne le User correspondant (créé s'il n'existait pas).
    `referral_code` n'est résolu et enregistré que lors de la toute première création
    du compte - un utilisateur déjà existant qui se reconnecte ne peut jamais se voir
    attribuer un parrain après coup.
    """
    otp = (
        OTPCode.objects.filter(phone_number=phone_number, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if otp is None or otp.expires_at < timezone.now():
        raise OTPInvalid("Code invalide ou expiré.")

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        raise OTPInvalid("Trop de tentatives pour ce code, redemandez-en un nouveau.")

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if otp.code != code:
        raise OTPInvalid("Code invalide ou expiré.")

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user = User.objects.filter(phone_number=phone_number).first()
    if user is None:
        user = User.objects.create_user(phone_number=phone_number)
        if referral_code:
            # Un code inconnu ou correspondant à soi-même (cas normalement impossible
            # ici puisque le compte vient d'être créé, mais gardé par prudence) est
            # ignoré silencieusement plutôt que de faire échouer l'inscription.
            parrain = User.objects.filter(referral_code=referral_code.strip().upper()).exclude(pk=user.pk).first()
            if parrain is not None:
                user.referred_by = parrain
                user.save(update_fields=["referred_by"])

    return user
