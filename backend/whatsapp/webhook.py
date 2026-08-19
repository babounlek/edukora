"""
Point d'entrée public de l'API Cloud WhatsApp de Meta - la seule route de l'app qui ne
demande aucune authentification applicative, puisqu'elle est appelée par Meta et non
par un client edukora. Deux usages bien distincts sous la même URL (voir whatsapp.urls) :

- GET : l'échange de vérification que Meta fait une seule fois, à l'enregistrement du
  webhook dans son tableau de bord (voir verifier_challenge).
- POST : chaque notification (message entrant, accusé de réception...) une fois le
  webhook enregistré (voir verifier_signature puis whatsapp.services.
  traiter_payload_entrant, qui applique les demandes d'arrêt qu'elle contient).

La signature du corps est la SEULE authentification du POST - accepter une notification
non signée reviendrait à laisser n'importe quel tiers déclencher des désabonnements de
masse en forgeant de faux "STOP".
"""

import hashlib
import hmac
import json
import logging

from decouple import config
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .services import traiter_payload_entrant

logger = logging.getLogger("whatsapp")


def verifier_challenge(params):
    """
    Défaut fermé : un WHATSAPP_VERIFY_TOKEN non configuré (`.env` incomplet) refuse la
    vérification plutôt que d'accepter n'importe quel jeton soumis - sans ce garde,
    l'absence de configuration se comporterait comme une configuration ouverte à tous.
    """
    jeton_attendu = config("WHATSAPP_VERIFY_TOKEN", default=None)
    if not jeton_attendu:
        return None
    if params.get("hub.mode") != "subscribe":
        return None
    if params.get("hub.verify_token") != jeton_attendu:
        return None
    return params.get("hub.challenge", "")


def verifier_signature(corps, entete_signature):
    """
    Comparaison à temps constant (hmac.compare_digest) : une comparaison `==` ordinaire
    sort dès le premier octet différent, ce qui fuite - mesurable sur le réseau - la
    longueur du préfixe correct et facilite une attaque par canal auxiliaire sur le
    secret. Même défaut fermé que verifier_challenge : un WHATSAPP_APP_SECRET non
    configuré refuse tout, y compris une notification par ailleurs bien formée.
    """
    secret = config("WHATSAPP_APP_SECRET", default=None)
    if not secret or not entete_signature:
        return False
    attendue = "sha256=" + hmac.new(secret.encode(), corps, hashlib.sha256).hexdigest()
    return hmac.compare_digest(attendue, entete_signature)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def webhook(request):
    if request.method == "GET":
        challenge = verifier_challenge(request.query_params)
        if challenge is None:
            return HttpResponse(status=403)
        return HttpResponse(challenge, content_type="text/plain")

    signature = request.META.get("HTTP_X_HUB_SIGNATURE_256", "")
    if not verifier_signature(request.body, signature):
        return Response(status=403)

    # Un corps illisible ne doit jamais faire lever d'exception : Meta retenterait la
    # même notification en boucle pendant des heures. `traiter_payload_entrant` tolère
    # déjà un payload de forme inattendue (voir sa docstring) - {} en est un de plus.
    try:
        payload = json.loads(request.body)
    except ValueError:
        logger.warning("Notification WhatsApp illisible (corps non-JSON), ignorée.")
        payload = {}

    desabonnements = traiter_payload_entrant(payload)
    return Response({"desabonnements": desabonnements})
