from django.db import models


class OptIn(models.Model):
    """
    Consentement explicite d'un utilisateur à recevoir des messages WhatsApp
    proactifs (rappels de révision) - jamais présumé depuis le numéro déjà en base
    (users.User.phone_number sert à l'authentification/l'OTP, pas à un consentement
    marketing/utilitaire distinct - exigence de la politique WhatsApp Business, pas
    une prudence ajoutée ici sans raison).

    Une ligne par évènement marche/arrêt plutôt qu'un simple booléen sur User :
    conserve l'historique complet (quand, combien de fois) - utile pour prouver le
    consentement si jamais contesté, même logique d'audit que
    subscriptions.ParrainageRecompense/payments.Transaction ailleurs dans ce projet.
    Un utilisateur qui se réinscrit après s'être désinscrit crée une NOUVELLE ligne,
    ne réactive jamais l'ancienne.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="whatsapp_optins")
    opted_in_at = models.DateTimeField(auto_now_add=True)
    opted_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opted_in_at"]

    def __str__(self):
        etat = "actif" if self.is_active else f"arrêté le {self.opted_out_at:%d/%m/%Y}"
        return f"{self.user} ({etat})"

    @property
    def is_active(self):
        return self.opted_out_at is None
