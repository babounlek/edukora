"""
Connexion « Continuer avec Google ».

Deux responsabilités distinctes, volontairement séparées : vérifier l'ID token
(cryptographie, sans aucune notion de compte Edukora) et décider quel compte il
ouvre (politique de rattachement, sans aucune notion de JWT). La seconde est la
partie sensible - c'est elle qui peut, mal écrite, offrir la prise de contrôle d'un
compte existant à qui contrôle une adresse e-mail.

Le flux est celui de Google Identity Services : le navigateur obtient un ID token
signé par Google et le poste ici. Le backend ne parle jamais directement à Google
en OAuth (pas de code, pas de client_secret, pas de redirect_uri à gérer) - il ne
fait que vérifier une signature contre les clés publiques de Google.

Aucune dépendance ajoutée : PyJWT (déjà présent pour simplejwt) sait récupérer et
mettre en cache le JWKS de Google via PyJWKClient. Une dépendance de moins sur un
chemin d'authentification est une surface d'attaque de moins.
"""

import logging

import jwt
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from jwt import PyJWKClient

from .models import AuthIdentity, AuthProvider, User

logger = logging.getLogger("users.google")

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

# Google émet l'un ou l'autre selon l'ancienneté du client - les deux sont valides
# et documentés, refuser le premier casserait une partie des connexions.
GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}

# Tolérance d'horloge. Volontairement courte : elle n'existe que pour absorber la
# dérive d'horloge du serveur, pas pour prolonger la validité d'un token.
LEEWAY_SECONDS = 30

_jwk_client = PyJWKClient(GOOGLE_CERTS_URL)


class GoogleAuthError(Exception):
    """ID token absent, mal signé, expiré, ou émis pour une autre application."""


class GoogleNotConfigured(Exception):
    """GOOGLE_CLIENT_ID absent des settings - l'endpoint ne peut pas fonctionner."""


class GoogleAccountConflict(Exception):
    """
    L'adresse Google correspond à un compte existant qu'on refuse de rattacher
    automatiquement. Jamais une erreur technique : c'est le refus délibéré décrit
    dans resolve_google_account.
    """


def verify_google_id_token(raw_token):
    """
    Vérifie la signature et les claims d'un ID token Google, et retourne son payload.

    `audience` est le contrôle décisif et non optionnel : sans lui, un ID token émis
    par Google pour *n'importe quelle autre application* serait accepté ici, et
    n'importe quel développeur tiers pourrait ouvrir n'importe quel compte Edukora.
    """
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise GoogleNotConfigured("GOOGLE_CLIENT_ID n'est pas configuré.")
    if not raw_token:
        raise GoogleAuthError("Jeton Google manquant.")

    try:
        signing_key = _jwk_client.get_signing_key_from_jwt(raw_token)
        claims = jwt.decode(
            raw_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            leeway=LEEWAY_SECONDS,
            options={"require": ["exp", "iat", "aud", "iss", "sub"]},
        )
    except jwt.PyJWTError as exc:
        # Message générique côté client, détail seulement dans les logs : distinguer
        # « signature invalide » de « expiré » renseignerait un attaquant sur l'état
        # exact de sa tentative sans jamais aider un utilisateur légitime.
        logger.warning("ID token Google rejeté : %s", exc)
        raise GoogleAuthError("Connexion Google refusée.") from exc

    if claims.get("iss") not in GOOGLE_ISSUERS:
        logger.warning("ID token Google d'un émetteur inattendu : %r", claims.get("iss"))
        raise GoogleAuthError("Connexion Google refusée.")

    if not claims.get("sub"):
        raise GoogleAuthError("Connexion Google refusée.")

    return claims


@transaction.atomic
def resolve_google_account(claims, referral_code=""):
    """
    Détermine le compte qu'ouvre un ID token déjà vérifié, en le créant au besoin.

    Trois cas, dans cet ordre :

    1. Identité Google déjà connue -> ce compte, sans condition. `sub` est
       l'identifiant stable de Google, indépendant de l'adresse : un utilisateur qui
       change l'adresse de son compte Google retrouve bien le sien.

    2. Adresse attestée des DEUX côtés -> rattachement au compte existant. Exiger la
       double attestation (`email_verified` chez Google *et* sur le compte Edukora)
       est ce qui interdit la prise de contrôle : sans cela, il suffirait de créer un
       compte Edukora déclarant l'adresse de quelqu'un d'autre, puis d'attendre que
       la victime se connecte avec Google pour hériter de son compte - ou l'inverse.

    3. Sinon -> nouveau compte, sans numéro de téléphone. C'est précisément ce que la
       refonte du modèle a rendu possible.

    Le cas « adresse connue mais non attestée des deux côtés » ne crée pas un second
    compte (la contrainte d'unicité sur l'e-mail l'interdirait de toute façon) : il
    lève GoogleAccountConflict, à charge pour l'utilisateur de se connecter par son
    moyen habituel puis de rattacher Google depuis son compte (voir link_google_identity).
    """
    sub = claims["sub"]
    email = (claims.get("email") or "").strip().lower() or None
    email_atteste = bool(claims.get("email_verified")) and email is not None

    identity = (
        AuthIdentity.objects.select_for_update()
        .filter(provider=AuthProvider.GOOGLE, provider_uid=sub)
        .select_related("user").first()
    )
    if identity is not None:
        _marquer_utilisee(identity, email)
        return identity.user, False

    if email_atteste:
        existant = User.objects.filter(email__iexact=email).first()
        if existant is not None:
            if not existant.email_verified:
                raise GoogleAccountConflict(
                    "Un compte utilise déjà cette adresse e-mail. Connectez-vous avec "
                    "votre numéro de téléphone, puis rattachez Google depuis votre compte.",
                )
            identity = AuthIdentity.objects.create(
                user=existant, provider=AuthProvider.GOOGLE, provider_uid=sub,
                email=email or "", last_used_at=timezone.now(),
            )
            return existant, False

    user = User.objects.create_user(
        phone_number=None,
        email=email if email_atteste else None,
        email_verified=email_atteste,
        full_name=(claims.get("name") or "")[:150],
    )
    AuthIdentity.objects.create(
        user=user, provider=AuthProvider.GOOGLE, provider_uid=sub,
        email=email or "", last_used_at=timezone.now(),
    )
    _appliquer_parrainage(user, referral_code)
    return user, True


def link_google_identity(user, claims):
    """
    Rattache une identité Google à un compte DÉJÀ authentifié - le chemin sûr pour
    fusionner un compte téléphone et un compte Google, puisque la possession du
    compte est prouvée par la session en cours et non déduite d'une adresse.

    Refuse si cette identité Google appartient déjà à quelqu'un d'autre : sans ce
    contrôle, deux comptes Edukora partageraient le même moyen de connexion, et
    lequel s'ouvre dépendrait de l'ordre des lignes en base.
    """
    sub = claims["sub"]
    email = (claims.get("email") or "").strip().lower()

    deja = AuthIdentity.objects.filter(provider=AuthProvider.GOOGLE, provider_uid=sub).first()
    if deja is not None:
        if deja.user_id != user.pk:
            raise GoogleAccountConflict("Ce compte Google est déjà rattaché à un autre compte.")
        _marquer_utilisee(deja, email)
        return deja

    identity, _ = AuthIdentity.objects.get_or_create(
        user=user, provider=AuthProvider.GOOGLE,
        defaults={"provider_uid": sub, "email": email, "last_used_at": timezone.now()},
    )
    # L'adresse Google n'écrase jamais User.email : ce compte a pu en renseigner une
    # autre délibérément. Elle n'est reprise que si le champ est encore vide.
    if email and claims.get("email_verified") and not user.email:
        user.email = email
        user.email_verified = True
        user.save(update_fields=["email", "email_verified"])
    return identity


def _marquer_utilisee(identity, email):
    champs = ["last_used_at"]
    identity.last_used_at = timezone.now()
    if email and identity.email != email:
        identity.email = email
        champs.append("email")
    identity.save(update_fields=champs)


def _appliquer_parrainage(user, referral_code):
    """Même règle que verify_otp : uniquement à la création, jamais rétroactivement."""
    if not referral_code:
        return
    parrain = (
        User.objects.filter(referral_code=referral_code.strip().upper())
        .exclude(pk=user.pk).first()
    )
    if parrain is not None:
        user.referred_by = parrain
        user.save(update_fields=["referred_by"])
