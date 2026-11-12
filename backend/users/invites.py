"""
Le visiteur qui essaie une épreuve inédite gratuite SANS s'inscrire.

Une copie d'inédite est rattachée à un profil (réponses, chrono, notation, XP) : plutôt que de réécrire tout cela pour
un visiteur sans compte, on lui ouvre un compte INVITÉ (`User.est_invite`), sans aucune identité, avec son profil. Le
reste de la plateforme ne le sait pas : il n'a de droits que sur `/inedit/` (voir users.authentication) et le frontend
ne lui attache son jeton que sur ces routes (voir api/client.ts) - pour tout le reste du site, il reste un visiteur.

Quand il crée un vrai compte (OTP, e-mail, Google), la copie ne se perd pas : `rattacher` la lui transmet.

Le jeton est un access token de 30 jours SANS refresh ni cookie : il ne peut ni ouvrir de session, ni renouveler quoi
que ce soit. Perdu (stockage vidé), l'invité en reçoit un autre et recommence - la copie de l'ancien est abandonnée.
"""
import logging
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import Profil, User

logger = logging.getLogger(__name__)

# Jeton d'un invité : 30 jours, comme un refresh token de vrai compte - l'élève revient finir sa copie.
DUREE_JETON = timedelta(days=30)
# Un invité abandonné disparaît passé ce délai (le jeton est expiré depuis un mois).
DUREE_CONSERVATION = timedelta(days=60)
# En-tête qui porte le jeton d'invité vers les routes de connexion (voir rattacher_depuis_requete).
EN_TETE_JETON = "HTTP_X_INVITE_TOKEN"

# Plafonds de création. Larges pour la même raison que OTP_MAX_PER_IP_PER_HOUR : derrière le CGNAT d'un opérateur ou
# dans un cybercafé, des centaines d'élèves légitimes partagent une IP. Le plafond par IP ne vise que le robot
# grossier ; c'est le plafond global (exact, lu en base) qui borne le nombre de comptes créés par jour.
MAX_PAR_IP_PAR_HEURE = 60
MAX_GLOBAL_PAR_JOUR = 5000


class InviteRefuse(Exception):
    """Trop de créations : le message est montré tel quel à l'élève."""


def _cle_ip(ip):
    return f"invite:ip:{ip}"


def creer_invite(ip=None):
    """Un compte invité neuf et son jeton. Lève InviteRefuse si les plafonds sont atteints."""
    if User.objects.filter(est_invite=True, date_joined__gte=timezone.now() - timedelta(days=1)).count() >= MAX_GLOBAL_PAR_JOUR:
        logger.error("Plafond global de comptes invités atteint (%s/jour).", MAX_GLOBAL_PAR_JOUR)
        raise InviteRefuse("Trop d'essais en ce moment. Réessaie dans quelques minutes ou crée ton compte.")
    if ip:
        cle = _cle_ip(ip)
        # add() puis incr() : le compteur naît avec son expiration, sans jamais la repousser.
        cache.add(cle, 0, timeout=3600)
        try:
            n = cache.incr(cle)
        except ValueError:  # expirée entre add et incr
            cache.set(cle, 1, timeout=3600)
            n = 1
        if n > MAX_PAR_IP_PAR_HEURE:
            raise InviteRefuse("Trop d'essais depuis ce réseau. Réessaie plus tard ou crée ton compte.")
    # Sans numéro ni mot de passe : rien ne permet de se connecter à ce compte, sauf son jeton.
    user = User.objects.create_user(None, est_invite=True)
    return user


def jeton_invite(user):
    """Le jeton d'accès de l'invité (30 jours, aucun refresh)."""
    jeton = AccessToken.for_user(user)
    jeton.set_exp(lifetime=DUREE_JETON)
    jeton["invite"] = True
    return str(jeton)


def invite_du_jeton(brut):
    """L'invité que désigne ce jeton, ou None (absent, expiré, falsifié, compte devenu réel ou supprimé)."""
    if not brut:
        return None
    try:
        jeton = AccessToken(brut)
        return User.objects.filter(pk=jeton["user_id"], est_invite=True, is_active=True).first()
    except (TokenError, KeyError, ValueError):
        return None


def _profil_vierge(profil):
    """Aucune activité d'aucune sorte sur ce profil (tout ce qui pointe vers lui, séances, quiz, XP, copies...)."""
    for rel in Profil._meta.related_objects:
        if rel.related_model._default_manager.filter(**{rel.field.name: profil}).exists():
            return False
    return True


def rattacher(invite, user):
    """
    Transmet la copie de l'invité au compte réel `user`, puis supprime l'invité.

    - compte neuf (un seul profil, sans aucune activité) : le profil de l'invité DEVIENT le sien, avec tout ce qu'il
      porte (copie, XP, révisions). Rien à fusionner, donc rien à perdre ;
    - compte déjà utilisé : seules les copies d'inédites passent sur son profil actif. Le reste (XP, révisions de
      l'invité, très peu de chose) est abandonné plutôt que fusionné au risque de heurter des contraintes d'unicité.
    """
    from inedit.models import TentativeInedite

    if invite is None or invite.pk == user.pk or user.est_invite:
        return
    with transaction.atomic():
        invite = User.objects.select_for_update().filter(pk=invite.pk, est_invite=True).first()
        if invite is None:
            return
        profil_invite = invite.profils.first()
        profils = list(user.profils.all())
        if profil_invite is not None:
            if len(profils) == 1 and _profil_vierge(profils[0]):
                vierge = profils[0]
                if not profil_invite.prenom:
                    profil_invite.prenom = vierge.prenom
                if profil_invite.cursus_prepare_id is None:
                    profil_invite.cursus_prepare_id = vierge.cursus_prepare_id
                profil_invite.compte = user
                vierge.delete()
                profil_invite.save()
            elif profils:
                TentativeInedite.objects.filter(profil=profil_invite).update(profil=profils[0])
        invite.delete()


def rattacher_depuis_requete(request, user):
    """
    À appeler quand une connexion ou une inscription vient de réussir (OTP, e-mail, Google). Lit le jeton d'invité que
    le frontend joint (en-tête X-Invite-Token) et lui fait passer sa copie. Ne fait JAMAIS échouer la connexion :
    la copie d'un essai gratuit ne vaut pas un élève qui ne peut plus entrer.
    """
    brut = request.META.get(EN_TETE_JETON)
    if not brut:
        return
    try:
        rattacher(invite_du_jeton(brut), user)
    except Exception:  # noqa: BLE001 - voir la docstring
        logger.exception("Rattachement d'un invité au compte %s échoué.", user.pk)
