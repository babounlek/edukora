"""
Mode parent et session enfant.

- Session enfant (`restreint` dans le token) : ouverte par l'enfant avec son propre numéro
  (Profil.connexion_phone). Elle ne peut ni changer de profil ni faire une action du compte.
- Mode parent : si le compte a un PIN parent, les actions du compte (paiement, gestion des
  enfants et des codes, changement de numéro) exigent un jeton court, obtenu en saisissant
  ce PIN (POST /auth/parent/verifier/) et envoyé dans l'en-tête X-Parent-Token. Sans PIN
  parent défini, rien ne change pour les familles qui n'en veulent pas.
"""

from django.core import signing
from rest_framework.response import Response

SALT = "edukora-mode-parent"
DUREE_SECONDES = 15 * 60
ENTETE = "HTTP_X_PARENT_TOKEN"


def session_restreinte(request):
    auth = getattr(request, "auth", None)
    try:
        return bool(auth.get("restreint")) if auth else False
    except AttributeError:
        return False


def creer_jeton(user):
    return signing.dumps({"u": user.pk}, salt=SALT)


def jeton_parent_valide(request):
    brut = request.META.get(ENTETE, "")
    if not brut:
        return False
    try:
        data = signing.loads(brut, salt=SALT, max_age=DUREE_SECONDES)
    except signing.BadSignature:
        return False
    return data.get("u") == request.user.pk


def exiger_mode_parent(request):
    """None si l'action est permise, sinon la Response 403 à renvoyer telle quelle."""
    if session_restreinte(request):
        return Response(
            {"error": "Cette action est réservée au parent.", "code": "session_restreinte"}, status=403,
        )
    if request.user.pin_parent_hash and not jeton_parent_valide(request):
        return Response(
            {"error": "Saisis le code parent pour continuer.", "code": "parent_requis"}, status=403,
        )
    return None
