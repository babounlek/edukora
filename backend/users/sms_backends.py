"""
Abstraction d'envoi de SMS, sur le modèle du EMAIL_BACKEND de Django : le
fournisseur réel se branche plus tard en changeant seulement SMS_BACKEND
dans les settings, sans toucher au reste du code OTP.
"""

import logging

from django.conf import settings
from django.utils.module_loading import import_string

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


def get_sms_backend():
    backend_class = import_string(settings.SMS_BACKEND)
    return backend_class()
