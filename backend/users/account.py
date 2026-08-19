"""
Cycle de vie du compte : changer de numéro, détacher une méthode de connexion.

Ce qu'on peut automatiser et ce qu'on ne peut pas
-------------------------------------------------
Le vrai motif de perte de compte sur ce marché n'est pas l'oubli d'un mot de passe
(il n'y en a pas) mais la rotation des puces SIM : numéro rendu, perdu, réattribué.
Deux situations, qui n'ont pas du tout la même réponse :

1. L'utilisateur peut ENCORE ouvrir son compte (par son ancien numéro, ou par Google
   depuis la refonte multi-méthodes) et veut y attacher un nouveau numéro. C'est le
   changement de numéro ci-dessous : entièrement automatisable, parce que la session
   prouve la possession du compte et l'OTP prouve la possession du nouveau numéro.

2. L'utilisateur ne peut PLUS ouvrir son compte du tout. Aucun chemin automatique
   n'est sûr ici : à ce stade, rien ne distingue le titulaire légitime de quelqu'un
   qui aurait simplement obtenu son ancien numéro auprès de l'opérateur après
   recyclage - et c'est un cas fréquent, pas théorique. Toute vérification par
   « questions de sécurité » ou par historique d'achat est du ressort d'une revue
   humaine, avec sa politique de fraude propre. Volontairement hors code.

La conséquence produit est que la récupération se prépare AVANT la perte, en
rattachant une seconde méthode. C'est ce que `UserSerializer.auth_methods` expose,
pour que le compte puisse le rappeler tant que l'utilisateur a encore accès.
"""

import logging

from django.db import transaction

from .email_service import (
    EmailAlreadyTaken,
    consume_email_code,
    normalize_email,
    request_email_code,
)
from .models import AuthIdentity, AuthProvider, User
from .otp_service import consume_otp, request_otp
from .phone import to_e164, to_local
from .sms_backends import get_sms_backend

logger = logging.getLogger("users.account")


class PhoneAlreadyTaken(Exception):
    """Le numéro visé sert déjà à ouvrir un autre compte."""


class PhoneUnchanged(Exception):
    """Le numéro visé est déjà celui du compte - rien à faire, et un OTP serait gâché."""


class LastIdentityError(Exception):
    """Détacher cette méthode laisserait le compte sans aucun moyen de connexion."""


class IdentityNotFound(Exception):
    """La méthode demandée n'est pas rattachée à ce compte."""


def _verifier_disponible(nouveau_numero, user):
    """
    Le numéro ne doit ouvrir aucun autre compte - vérifié sur les DEUX tables. Regarder
    seulement User.phone_number laisserait passer un numéro encore rattaché comme
    identité à un compte qui, lui, en a changé : la contrainte unique sur
    AuthIdentity ferait alors échouer l'opération en base, après l'envoi du SMS et
    avec une erreur incompréhensible pour l'utilisateur.
    """
    conflit = (
        User.objects.filter(phone_number=nouveau_numero).exclude(pk=user.pk).exists()
        or AuthIdentity.objects.filter(
            provider=AuthProvider.PHONE, provider_uid=nouveau_numero,
        ).exclude(user=user).exists()
    )
    if conflit:
        raise PhoneAlreadyTaken(
            "Ce numéro est déjà utilisé par un autre compte. Connecte-toi avec ce "
            "numéro, ou utilise-en un autre.",
        )


def request_phone_change(user, nouveau_numero, ip_address=None):
    """
    Envoie un code au NOUVEAU numéro. La possession du compte est déjà prouvée par la
    session : c'est la possession du nouveau numéro qui reste à établir.

    Aucun code n'est envoyé à l'ancien numéro. C'est délibéré : exiger les deux rendrait
    le changement impossible dans le cas qui le motive - la puce est perdue ou hors
    service. L'ancien numéro est en revanche notifié APRÈS coup (voir
    confirm_phone_change), ce qui reste utile s'il est encore actif et laisse une trace
    à son titulaire.

    Réutilise request_otp, donc aussi tous ses garde-fous (cooldown par numéro,
    plafond par IP, plafond global) : un changement de numéro coûte un SMS exactement
    comme une connexion, et doit être borné pareil.
    """
    nouveau_numero = to_e164(nouveau_numero)
    if nouveau_numero == user.phone_number:
        raise PhoneUnchanged("Ce numéro est déjà celui de ton compte.")

    _verifier_disponible(nouveau_numero, user)
    request_otp(nouveau_numero, ip_address=ip_address)
    return nouveau_numero


@transaction.atomic
def confirm_phone_change(user, nouveau_numero, code):
    """
    Consomme le code puis bascule le compte sur le nouveau numéro.

    Passe par consume_otp et non verify_otp : ce dernier créerait un compte sur le
    nouveau numéro s'il n'en existait pas, ce qui est précisément le contraire du but.

    La disponibilité est revérifiée ici, après l'avoir déjà été à la demande du code :
    plusieurs minutes séparent les deux appels, et quelqu'un a pu s'inscrire avec ce
    numéro entre-temps. La transaction et les contraintes uniques restent le dernier
    filet en cas de course.
    """
    nouveau_numero = to_e164(nouveau_numero)
    _verifier_disponible(nouveau_numero, user)

    consume_otp(nouveau_numero, code)

    ancien_numero = user.phone_number
    user.phone_number = nouveau_numero
    user.save(update_fields=["phone_number"])

    # update_or_create et non create : un compte créé via Google n'a pas encore
    # d'identité `phone`, et ce changement est alors son premier rattachement.
    AuthIdentity.objects.update_or_create(
        user=user, provider=AuthProvider.PHONE,
        defaults={"provider_uid": nouveau_numero},
    )

    transaction.on_commit(lambda: _notifier_ancien_numero(ancien_numero, nouveau_numero))
    return user


def _notifier_ancien_numero(ancien_numero, nouveau_numero):
    """
    Alerte l'ancien numéro s'il est encore actif : c'est le seul signal qu'aurait son
    titulaire légitime si un changement lui échappait. Envoyé après commit, jamais
    pendant la transaction - un échec d'envoi ne doit pas annuler un changement déjà
    validé, et un SMS ne se rattrape pas par un rollback.

    Le nouveau numéro est tronqué : le message part vers un numéro qui n'appartient
    peut-être déjà plus à la personne concernée.
    """
    if not ancien_numero:
        return
    masque = f"{to_local(nouveau_numero)[:3]}...{to_local(nouveau_numero)[-2:]}"
    try:
        get_sms_backend().send(
            ancien_numero,
            f"Le numero de ton compte a ete change vers {masque}. "
            f"Si tu n'es pas a l'origine de ce changement, contacte-nous.",
        )
    except Exception:
        # Journalisé, jamais propagé : le changement est déjà acté en base, faire
        # échouer la requête laisserait croire à l'utilisateur qu'il n'a pas eu lieu.
        logger.exception("Notification de changement de numéro non envoyée")


def _verifier_email_disponible(email, user):
    """
    Même précaution que pour le numéro : l'adresse ne doit ouvrir aucun AUTRE compte, et
    c'est vérifié sur les deux tables. Regarder seulement User.email laisserait passer
    une adresse encore rattachée comme identité à un compte qui en a changé - la
    contrainte unique sur AuthIdentity ferait alors échouer l'opération après l'envoi du
    message, avec une erreur incompréhensible.
    """
    conflit = (
        User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists()
        or AuthIdentity.objects.filter(
            provider=AuthProvider.EMAIL, provider_uid=email,
        ).exclude(user=user).exists()
    )
    if conflit:
        raise EmailAlreadyTaken(
            "Cette adresse est déjà utilisée par un autre compte. Connecte-toi avec "
            "cette adresse, ou utilises-en une autre.",
        )


def request_email_link(user, email, ip_address=None):
    """
    Envoie un code à l'adresse que l'utilisateur veut rattacher. La session prouve déjà
    la possession du compte ; c'est la possession de la boîte qui reste à établir.

    La disponibilité est contrôlée AVANT l'envoi, comme pour le changement de numéro :
    sans ça, on ferait recopier un code à quelqu'un dont le rattachement est de toute
    façon condamné à échouer à l'étape suivante.
    """
    email = normalize_email(email)
    _verifier_email_disponible(email, user)
    request_email_code(email, ip_address=ip_address)
    return email


@transaction.atomic
def confirm_email_link(user, email, code):
    """
    Consomme le code puis rattache l'adresse au compte connecté.

    Passe par consume_email_code et non verify_email_code : ce dernier créerait un compte
    sur cette adresse s'il n'en existait pas, alors qu'ici le compte est déjà connu -
    c'est exactement la distinction consume_otp / verify_otp côté téléphone.

    La disponibilité est revérifiée après coup : plusieurs minutes séparent la demande de
    la confirmation, et quelqu'un a pu s'inscrire avec cette adresse entre-temps.
    """
    email = normalize_email(email)
    _verifier_email_disponible(email, user)

    consume_email_code(email, code)

    user.email = email
    user.email_verified = True
    user.save(update_fields=["email", "email_verified"])

    # update_or_create : l'utilisateur peut rattacher une adresse alors qu'il en avait
    # déjà une (il en change), auquel cas la contrainte unique par (user, provider)
    # rejetterait une seconde ligne.
    AuthIdentity.objects.update_or_create(
        user=user, provider=AuthProvider.EMAIL,
        defaults={"provider_uid": email, "email": email},
    )
    return user


def unlink_identity(user, provider):
    """
    Détache une méthode de connexion.

    Deux refus, tous deux destinés à empêcher l'utilisateur de s'enfermer dehors :
    la dernière identité n'est jamais détachable, et un membre du staff ne peut pas
    détacher son téléphone puisque c'est USERNAME_FIELD, donc son seul identifiant de
    connexion à l'admin Django.
    """
    identity = user.identities.filter(provider=provider).first()
    if identity is None:
        raise IdentityNotFound("Cette méthode de connexion n'est pas rattachée à ton compte.")

    if user.identities.count() <= 1:
        raise LastIdentityError(
            "C'est ta seule méthode de connexion : rattaches-en une autre avant de "
            "détacher celle-ci.",
        )

    if provider == AuthProvider.PHONE and user.is_staff:
        raise LastIdentityError(
            "Un compte administrateur ne peut pas détacher son numéro de téléphone.",
        )

    identity.delete()
    if provider == AuthProvider.PHONE:
        # Sinon User.phone_number continuerait de désigner un numéro que plus aucune
        # identité ne prouve - et le bloquerait pour tout autre compte, par unicité.
        user.phone_number = None
        user.save(update_fields=["phone_number"])
    elif provider == AuthProvider.EMAIL:
        # Exactement la même raison : User.email est unique lui aussi, le laisser en
        # place réserverait indéfiniment une adresse que plus rien ne prouve, et
        # empêcherait son titulaire réel de s'en servir sur un autre compte.
        user.email = None
        user.email_verified = False
        user.save(update_fields=["email", "email_verified"])
    return user
