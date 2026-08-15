import logging
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import AuthIdentity, AuthProvider, OTPCode, User
from .phone import to_e164
from .sms_backends import get_sms_backend

logger = logging.getLogger("users.otp")

OTP_VALIDITY_MINUTES = 5
OTP_MIN_INTERVAL_SECONDS = 60
OTP_MAX_ATTEMPTS = 5
# Fenêtres glissantes (pas des jours/heures calendaires) des deux plafonds ci-dessous :
# un plafond calendaire se réinitialise d'un coup à minuit et laisse passer deux pleines
# rafales à cheval sur le changement de jour. Les valeurs des plafonds eux-mêmes vivent
# dans les settings (OTP_MAX_PER_IP_PER_HOUR / OTP_DAILY_GLOBAL_CAP) : ce sont des
# réglages d'exploitation, à ajuster en production sans redéploiement de code.
OTP_IP_WINDOW = timedelta(hours=1)
OTP_GLOBAL_WINDOW = timedelta(hours=24)


class OTPThrottled(Exception):
    pass


class OTPCapReached(Exception):
    """
    Plafond global d'envois atteint : distinct de OTPThrottled, qui sanctionne UN
    demandeur trop pressé. Ici le demandeur n'a rien fait de mal, c'est le service qui
    se met en sécurité - donc message et code HTTP différents (503, voir la vue), et
    une alerte côté exploitation puisque c'est soit une attaque, soit un plafond
    devenu trop bas pour le trafic réel.
    """


class OTPInvalid(Exception):
    pass


def request_otp(phone_number, ip_address=None):
    """
    Trois garde-fous, du plus spécifique au plus général, pour que le demandeur reçoive
    toujours le message le plus actionnable :

    1. Un même numéro ne peut redemander un code qu'après OTP_MIN_INTERVAL_SECONDS.
    2. Une même IP ne peut dépasser OTP_MAX_PER_IP_PER_HOUR envois sur OTP_IP_WINDOW.
       Sans ce garde-fou, le point 1 ne coûte rien à contourner : il suffit de faire
       tourner les numéros demandés. Chaque SMS étant facturé, c'est une perte d'argent
       directe (« SMS pumping ») dès qu'un vrai fournisseur remplace ConsoleSMSBackend,
       pas seulement une nuisance.
    3. Plafond global OTP_DAILY_GLOBAL_CAP sur OTP_GLOBAL_WINDOW : dernier filet, qui
       borne la facture même si l'attaque vient de milliers d'IP distinctes (botnet),
       cas où le point 2 ne mord jamais.

    `ip_address` à None (appel interne, shell, test) désactive le point 2 seulement :
    on ne bloque jamais une demande légitime au motif qu'on n'a pas su déterminer sa
    source, et le point 3 continue de couvrir ce cas.
    """
    # Normalisé ici plutôt qu'en amont seulement : ces deux fonctions sont le service
    # d'authentification, appelé aussi hors sérialiseur (shell, scripts, tests). Si un
    # numéro entrait au format local, il créerait une ligne OTPCode que verify_otp -
    # qui cherche en E.164 - ne retrouverait jamais, et le code envoyé serait
    # inutilisable sans aucune erreur visible.
    phone_number = to_e164(phone_number)
    now = timezone.now()

    recent = OTPCode.objects.filter(phone_number=phone_number).order_by("-created_at").first()
    if recent and (now - recent.created_at).total_seconds() < OTP_MIN_INTERVAL_SECONDS:
        raise OTPThrottled("Merci de patienter avant de redemander un code.")

    if ip_address:
        sent_from_ip = OTPCode.objects.filter(
            ip_address=ip_address, created_at__gt=now - OTP_IP_WINDOW,
        ).count()
        if sent_from_ip >= settings.OTP_MAX_PER_IP_PER_HOUR:
            logger.warning(
                "Plafond OTP par IP atteint (%s envois sur la dernière heure) pour %s.",
                sent_from_ip, ip_address,
            )
            raise OTPThrottled(
                "Trop de demandes de code depuis cette connexion. Merci de réessayer dans une heure.",
            )

    sent_globally = OTPCode.objects.filter(created_at__gt=now - OTP_GLOBAL_WINDOW).count()
    if sent_globally >= settings.OTP_DAILY_GLOBAL_CAP:
        # ERROR et pas WARNING : remonte à Sentry (voir settings.SENTRY_DSN) parce que
        # plus aucun utilisateur ne peut se connecter tant que ça dure - c'est une
        # panne d'authentification, qu'elle soit subie ou provoquée.
        logger.error(
            "Plafond OTP global atteint : %s envois sur les dernières 24 h (plafond %s). "
            "Aucun code ne sera envoyé tant que la fenêtre ne s'est pas dégagée.",
            sent_globally, settings.OTP_DAILY_GLOBAL_CAP,
        )
        raise OTPCapReached(
            "Service d'envoi de code temporairement indisponible. Merci de réessayer plus tard.",
        )

    code = f"{random.randint(0, 999999):06d}"
    OTPCode.objects.create(
        phone_number=phone_number,
        code=code,
        expires_at=now + timedelta(minutes=OTP_VALIDITY_MINUTES),
        ip_address=ip_address,
    )
    get_sms_backend().send(
        phone_number, f"Votre code {settings.SITE_NAME} : {code} (valable {OTP_VALIDITY_MINUTES} minutes).",
    )


def consume_otp(phone_number, code):
    """
    Valide un code et le consomme, sans rien décider du compte : prouve seulement que
    le demandeur possède ce numéro à cet instant.

    Extrait de verify_otp parce que le changement de numéro (voir users.account) a
    besoin exactement de cette preuve, mais surtout PAS de la création de compte que
    verify_otp enchaîne - confirmer un changement ne doit jamais pouvoir faire naître
    un second compte sur le numéro visé.
    """
    phone_number = to_e164(phone_number)
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
    return phone_number


def verify_otp(phone_number, code, referral_code=""):
    """
    Vérifie le code puis retourne le User correspondant (créé s'il n'existait pas).
    `referral_code` n'est résolu et enregistré que lors de la toute première création
    du compte - un utilisateur déjà existant qui se reconnecte ne peut jamais se voir
    attribuer un parrain après coup.
    """
    phone_number = consume_otp(phone_number, code)

    # Recherche par identité plutôt que par User.phone_number : c'est AuthIdentity qui
    # porte désormais la notion de "preuve de possession de ce numéro". Les deux
    # coïncident aujourd'hui, mais un futur changement de numéro fera diverger l'un de
    # l'autre, et c'est bien l'identité qui doit décider quel compte est ouvert.
    identity = (
        AuthIdentity.objects.filter(provider=AuthProvider.PHONE, provider_uid=phone_number)
        .select_related("user").first()
    )
    user = identity.user if identity else None

    if user is None:
        # create_user pose lui-même l'identité `phone` (invariant "aucun compte sans
        # identité", voir UserManager._create_user) : on la relit plutôt que d'en
        # créer une seconde, que la contrainte unique par (user, provider) rejetterait.
        user = User.objects.create_user(phone_number=phone_number)
        identity = user.identities.get(provider=AuthProvider.PHONE)
        if referral_code:
            # Un code inconnu ou correspondant à soi-même (cas normalement impossible
            # ici puisque le compte vient d'être créé, mais gardé par prudence) est
            # ignoré silencieusement plutôt que de faire échouer l'inscription.
            parrain = User.objects.filter(referral_code=referral_code.strip().upper()).exclude(pk=user.pk).first()
            if parrain is not None:
                user.referred_by = parrain
                user.save(update_fields=["referred_by"])

    identity.last_used_at = timezone.now()
    identity.save(update_fields=["last_used_at"])

    return user
