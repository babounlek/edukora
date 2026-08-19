"""
Abstraction d'envoi d'e-mail de développement - même esprit que users.sms_backends
côté SMS, mais une interface différente : c'est send_mail()/django.core.mail qui
pilote l'envoi ici, pas notre code, donc c'est SON contrat (BaseEmailBackend.
send_messages) qu'il faut respecter pour rester substituable au vrai backend SMTP de
Django en production (seul EMAIL_BACKEND change alors, voir settings.py - aucun autre
code à toucher).
"""

import logging

from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger("users.email")


class ConsoleEmailBackend(BaseEmailBackend):
    """
    Backend de développement : affiche chaque message dans le terminal au lieu de
    l'envoyer réellement. Une ligne compacte par destinataire plutôt que le message
    RFC-822 complet (en-têtes MIME compris) qu'écrit le backend console de Django, où
    le code de connexion se perd - la nôtre se relit comme celle du canal SMS (voir
    ConsoleSMSBackend), objet du message compris puisque c'est là que vit le code
    (voir users.email_service.request_email_code).
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        for message in email_messages:
            for destinataire in message.to:
                print(f"\n[E-MAIL -> {destinataire}] {message.subject}\n", flush=True)
                logger.info("[E-MAIL -> %s] %s", destinataire, message.subject)
        return len(email_messages)
