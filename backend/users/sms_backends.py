"""
Abstraction d'envoi de SMS, sur le modèle du EMAIL_BACKEND de Django : le
fournisseur réel se branche plus tard en changeant seulement SMS_BACKEND
dans les settings, sans toucher au reste du code OTP.

LMTSMSBackend n'est câblé qu'une fois LMT_API_KEY/LMT_SECRET/LMT_SENDER_ID
réellement configurés (voir .env.example) - tant que ce n'est pas le cas,
SMS_BACKEND reste sur ConsoleSMSBackend par défaut (settings.py), qui se
contente de journaliser ce qui aurait été envoyé. Même raisonnement que
whatsapp.backends.MetaCloudAPIBackend, à qui ce backend emprunte son patron.
"""

import logging

import requests
from decouple import config
from django.conf import settings
from django.utils.module_loading import import_string

from .phone import to_msisdn

logger = logging.getLogger("users.sms")


class ConsoleSMSBackend:
    """
    Backend de développement : affiche le SMS dans le terminal du serveur au lieu
    de l'envoyer réellement. print() plutôt que logger.info() pour être sûr que ça
    s'affiche même sans configuration LOGGING explicite dans settings.py.
    """

    def send(self, phone_number, message):
        print(f"\n[SMS -> {phone_number}] {message}\n", flush=True)
        logger.info("[SMS -> %s] %s", phone_number, message)


class LMTSMSError(Exception):
    pass


class LMTSMSBackend:
    """
    Envoie réellement via l'API SMS de LMT Group (Cameroun, sms.lmtgroup.com).

    Aucune documentation publique de cette API n'existe : la forme ci-dessous
    (GET, identifiants en en-tête, champs en query string) vient d'un sondage direct
    de l'endpoint avec de vrais identifiants (réponses d'erreur INP02 "Required
    request param is missing", qui énumèrent un champ manquant à la fois - msisdn,
    puis content, puis senderId). Un package Laravel non officiel
    (github.com/undjike/lmt-laravel-notification-channel) appelle le même endpoint
    en POST/JSON avec les mêmes noms de champs et les mêmes en-têtes d'authentification,
    ce qui corrobore ces noms sans lever toute ambiguïté sur d'éventuels champs
    optionnels (accusé de réception, encodage unicode, etc.) qu'une vraie fiche
    technique LMT documenterait. À revoir dès qu'elle est obtenue.
    """

    ENDPOINT = "https://sms.lmtgroup.com/api/v1/pushes"

    def send(self, phone_number, message):
        try:
            response = requests.get(
                self.ENDPOINT,
                params={
                    "msisdn": to_msisdn(phone_number),
                    "content": message,
                    "senderId": config("LMT_SENDER_ID"),
                },
                headers={
                    "X-Api-Key": config("LMT_API_KEY"),
                    "X-Secret": config("LMT_SECRET"),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=15,
            )
        except requests.exceptions.RequestException as exc:
            raise LMTSMSError(f"LMT Group injoignable pour le moment ({exc}).") from exc
        if response.status_code >= 400:
            raise LMTSMSError(f"Échec d'envoi SMS (LMT) : {response.text}")
        return response.json()


def get_sms_backend():
    backend_class = import_string(settings.SMS_BACKEND)
    return backend_class()
