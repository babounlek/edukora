"""
Client CamPay minimal, calqué sur le SDK officiel (github.com/CamPay/campay-python-sdk).
Ne couvre que collect (non bloquant) + vérification de statut : CamPay ne documente
aucun webhook dans son SDK officiel, le pattern supporté est le polling côté serveur.
"""

import requests
from decouple import config

CAMPAY_HOST = "https://demo.campay.net" if config("CAMPAY_ENVIRONMENT", default="DEV") == "DEV" else "https://www.campay.net"


class CampayError(Exception):
    pass


def _request(method, url, **kwargs):
    """
    Enveloppe requests pour que toute panne réseau (timeout, DNS, connexion refusée)
    devienne une CampayError plutôt qu'une exception non gérée : `initiate_payment` et
    `check_payment_status` (payments/views.py) ne rattrapent que CampayError et
    renvoient alors une réponse JSON propre (502) au frontend - sans ceci, une panne
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


def _get_token():
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
    return body["token"]


def init_collect(amount, phone_number, description, external_reference):
    """Déclenche une demande de paiement Mobile Money. Retourne la référence CamPay (statut PENDING)."""
    token = _get_token()
    # CamPay exige le format international ; on stocke/affiche partout ailleurs le format
    # local à 9 chiffres, donc l'indicatif Cameroun n'est ajouté qu'à cette frontière API.
    international_number = f"237{phone_number}"
    response = _request(
        "post",
        f"{CAMPAY_HOST}/api/collect/",
        json={
            "amount": str(amount),
            "currency": "XAF",
            "from": international_number,
            "description": description,
            "external_reference": external_reference,
        },
        headers={"Authorization": f"Token {token}"},
        timeout=15,
    )
    body = _json(response, "Échec de la demande de paiement CamPay")
    if response.status_code != 200:
        raise CampayError(body.get("message", "Échec de la demande de paiement CamPay."))
    return body


def get_transaction_status(reference):
    """Interroge CamPay pour l'état réel d'une transaction. Ne jamais faire confiance à une source non vérifiée : c'est le seul moyen fiable de confirmer un paiement."""
    token = _get_token()
    response = _request(
        "get",
        f"{CAMPAY_HOST}/api/transaction/{reference}/",
        headers={"Authorization": f"Token {token}"},
        timeout=15,
    )
    if response.status_code != 200:
        raise CampayError(f"Échec de vérification du statut CamPay : {response.text}")
    return _json(response, "Échec de vérification du statut CamPay")
