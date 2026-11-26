"""
Client CamPay minimal, calqué sur le SDK officiel (github.com/CamPay/campay-python-sdk).
Ne couvre que collect (non bloquant) + vérification de statut : CamPay ne documente
aucun webhook dans son SDK officiel, le pattern supporté est le polling côté serveur.
"""

import threading
import time

import requests
from decouple import config

from users.phone import to_msisdn

from .providers.base import PaiementFournisseurError

CAMPAY_HOST = "https://demo.campay.net" if config("CAMPAY_ENVIRONMENT", default="DEV") == "DEV" else "https://www.campay.net"

# Le jeton était redemandé à chaque appel : deux requêtes vers CamPay par sondage de statut, soit
# environ 80 pour un seul paiement suivi pendant deux minutes. Il est gardé cinq minutes par
# processus - durée courte choisie faute de validité documentée - et redemandé une fois si CamPay
# le refuse avant (voir _appel_authentifie).
DUREE_JETON_SECONDES = 300
_jeton = {"valeur": None, "expire": 0.0}
_verrou_jeton = threading.Lock()


class CampayError(PaiementFournisseurError):
    pass


def _request(method, url, **kwargs):
    """
    Enveloppe requests pour que toute panne réseau (timeout, DNS, connexion refusée)
    devienne une CampayError plutôt qu'une exception non gérée : `initiate_payment` et
    `check_payment_status` (payments/views.py) ne rattrapent que CampayError et
    renvoient alors une réponse JSON propre (503) au frontend - sans ceci, une panne
    réseau vers CamPay finit en 500 générique, sans message exploitable côté client.
    """
    try:
        return requests.request(method, url, **kwargs)
    except requests.exceptions.RequestException as exc:
        raise CampayError(f"CamPay est injoignable pour le moment ({exc}).") from exc


def _json(response, error_message):
    try:
        return response.json()
    except ValueError as exc:
        raise CampayError(f"{error_message} (réponse invalide : {response.text[:200]!r}).") from exc


def oublier_jeton():
    """Vide le jeton gardé en mémoire (tests, et refus du jeton par CamPay)."""
    with _verrou_jeton:
        _jeton.update(valeur=None, expire=0.0)


def _get_token(*, neuf=False):
    with _verrou_jeton:
        if not neuf and _jeton["valeur"] and time.monotonic() < _jeton["expire"]:
            return _jeton["valeur"]
    response = _request(
        "post",
        f"{CAMPAY_HOST}/api/token/",
        json={
            "username": config("CAMPAY_APP_USERNAME"),
            "password": config("CAMPAY_APP_PASSWORD"),
        },
        timeout=10,
    )
    body = _json(response, "Échec d'authentification CamPay")
    if response.status_code != 200:
        raise CampayError(f"Échec d'authentification CamPay : {response.text}")
    with _verrou_jeton:
        _jeton.update(valeur=body["token"], expire=time.monotonic() + DUREE_JETON_SECONDES)
    return body["token"]


def _appel_authentifie(method, url, **kwargs):
    """Un appel avec le jeton gardé en mémoire ; refusé (401 ou 403), il est rejoué une fois avec un jeton neuf."""
    response = _request(method, url, headers={"Authorization": f"Token {_get_token()}"}, **kwargs)
    if response.status_code in (401, 403):
        response = _request(method, url, headers={"Authorization": f"Token {_get_token(neuf=True)}"}, **kwargs)
    return response


def init_collect(amount, phone_number, description, external_reference):
    """Déclenche une demande de paiement Mobile Money. Retourne la référence CamPay (statut PENDING)."""
    # CamPay exige le format international sans '+'. Passe par to_msisdn plutôt que de
    # concaténer "237" : depuis la refonte du compte unique, un numéro peut arriver ici
    # au format local (payments.Transaction, saisi par le payeur) comme en E.164
    # (users.User.phone_number) - concaténer produirait "237+237..." dans le second cas.
    international_number = to_msisdn(phone_number)
    response = _appel_authentifie(
        "post",
        f"{CAMPAY_HOST}/api/collect/",
        json={
            "amount": str(amount),
            "currency": "XAF",
            "from": international_number,
            "description": description,
            "external_reference": external_reference,
        },
        timeout=15,
    )
    body = _json(response, "Échec de la demande de paiement CamPay")
    if response.status_code != 200:
        detail = body.get("message") if isinstance(body, dict) else None
        raise CampayError(
            f"Demande de paiement refusée par CamPay ({response.status_code}) : {detail or response.text[:200]}",
            # Une demande mal reçue (400) tient presque toujours au numéro : autre opérateur que MTN ou
            # Orange, numéro sans compte Mobile Money. Le reste (401, 403, 5xx) est une panne de notre côté
            # ou du leur, que le payeur ne peut pas corriger.
            code="numero_refuse" if response.status_code == 400 else None,
        )
    if not isinstance(body, dict) or not body.get("reference"):
        # Sans référence, rien ne permettrait de relire le statut : la transaction resterait « en attente »
        # jusqu'au délai de l'écran, pour une demande que CamPay n'a peut-être jamais envoyée.
        raise CampayError(f"Réponse CamPay sans référence de transaction : {str(body)[:200]}")
    return body


def get_transaction_status(reference):
    """Interroge CamPay pour l'état réel d'une transaction. Ne jamais faire confiance à une source non vérifiée : c'est le seul moyen fiable de confirmer un paiement."""
    response = _appel_authentifie(
        "get",
        f"{CAMPAY_HOST}/api/transaction/{reference}/",
        timeout=15,
    )
    if response.status_code != 200:
        raise CampayError(f"Échec de vérification du statut CamPay : {response.text}")
    return _json(response, "Échec de vérification du statut CamPay")
