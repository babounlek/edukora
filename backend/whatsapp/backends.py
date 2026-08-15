"""
Abstraction d'envoi WhatsApp, même patron que users.sms_backends (voir sa
docstring) : le fournisseur réel se branche en changeant seulement WHATSAPP_BACKEND
dans les settings, sans toucher au reste du code des rappels.

MetaCloudAPIBackend n'est câblé qu'une fois WHATSAPP_ACCESS_TOKEN/WHATSAPP_PHONE_NUMBER_ID
réellement configurés (voir .env.example) - tant que ce n'est pas le cas,
WHATSAPP_BACKEND reste sur ConsoleWhatsAppBackend par défaut (settings.py), qui se
contente de journaliser ce qui aurait été envoyé.
"""

import logging

import requests
from decouple import config

from users.phone import to_msisdn
from django.conf import settings
from django.utils.module_loading import import_string

logger = logging.getLogger("whatsapp")

GRAPH_API_VERSION = "v20.0"


class MetaWhatsAppError(Exception):
    pass


class ConsoleWhatsAppBackend:
    """
    Backend de développement : affiche le message dans le terminal du serveur au lieu
    de l'envoyer réellement. print() plutôt que logger.info() pour être sûr que ça
    s'affiche même sans configuration LOGGING explicite dans settings.py - même
    raisonnement que users.sms_backends.ConsoleSMSBackend.
    """

    def send_template(self, phone_number, template_name, params):
        print(f"\n[WHATSAPP -> {phone_number}] template={template_name} params={params}\n", flush=True)
        logger.info("[WHATSAPP -> %s] template=%s params=%s", phone_number, template_name, params)


class MetaCloudAPIBackend:
    """
    Envoie réellement via l'API Cloud WhatsApp de Meta (Graph API). N'envoie qu'un
    message basé sur un template pré-approuvé - seul type de message autorisé hors
    de la fenêtre de conversation de 24h (voir la doc Meta), notre seul besoin pour
    un rappel proactif (jamais initié par une réponse de l'utilisateur).
    """

    def send_template(self, phone_number, template_name, params):
        phone_number_id = config("WHATSAPP_PHONE_NUMBER_ID")
        token = config("WHATSAPP_ACCESS_TOKEN")
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"
        # Format international exigé par l'API Graph - même frontière que
        # payments.campay_client.init_collect, et même raison de passer par to_msisdn
        # plutôt que de concaténer l'indicatif : le numéro arrive ici en E.164 depuis
        # users.User.phone_number, et concaténer donnerait "237+237...".
        international_number = to_msisdn(phone_number)
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": international_number,
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {"code": "fr"},
                        "components": [{
                            "type": "body",
                            "parameters": [{"type": "text", "text": str(p)} for p in params],
                        }],
                    },
                },
                timeout=15,
            )
        except requests.exceptions.RequestException as exc:
            raise MetaWhatsAppError(f"WhatsApp (Meta) injoignable pour le moment ({exc}).") from exc
        if response.status_code >= 400:
            raise MetaWhatsAppError(f"Échec d'envoi WhatsApp : {response.text}")
        return response.json()


def get_whatsapp_backend():
    backend_class = import_string(settings.WHATSAPP_BACKEND)
    return backend_class()
