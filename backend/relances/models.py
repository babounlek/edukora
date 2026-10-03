from django.db import models


class TypeRelance(models.TextChoices):
    RAPPEL_SEANCE = "rappel_seance", "Rappel de la séance du jour"
    PAIEMENT_ABANDONNE_1 = "paiement_abandonne_1", "Paiement non abouti - premier message"
    PAIEMENT_ABANDONNE_2 = "paiement_abandonne_2", "Paiement non abouti - dernier message"
    BILAN_PARENT = "bilan_parent", "Bilan de la semaine au parent"


class CanalRelance(models.TextChoices):
    EMAIL = "email", "E-mail"
    PUSH = "push", "Notification du navigateur"


class RelanceEnvoyee(models.Model):
    """
    Trace d'un message de relance envoyé - l'unique moyen d'envoyer chaque message UNE
    seule fois, même si la commande tourne deux fois dans la journée ou qu'un
    ordonnanceur la relance après une panne.

    `reference` dit À PROPOS DE QUOI le message est parti : la date (ISO) pour le rappel
    quotidien, l'identifiant de la transaction pour une relance de paiement. La
    contrainte d'unicité porte sur (élève, type, référence, canal) : un rappel par jour,
    deux messages au plus par paiement non abouti, jamais un de plus.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="relances")
    type = models.CharField(max_length=30, choices=TypeRelance.choices)
    reference = models.CharField(max_length=40)
    canal = models.CharField(max_length=10, choices=CanalRelance.choices, default=CanalRelance.EMAIL)
    envoyee_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-envoyee_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "type", "reference", "canal"], name="unique_relance_par_objet"),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.user} ({self.reference})"


class AbonnementPush(models.Model):
    """
    Un appareil qui a accepté les notifications du navigateur (Web Push) : l'adresse que son
    navigateur nous a donnée et les deux clés qui permettent de chiffrer un message pour lui seul.

    Le compte porte l'abonnement, un appareil par ligne (téléphone et ordinateur ont chacun le
    leur). `endpoint` est unique : le même appareil se réabonne en écrasant sa ligne plutôt qu'en
    en ajoutant une. Une ligne disparaît quand le service push répond que l'appareil n'existe plus
    (404/410, voir relances.push) ou quand l'élève coupe les notifications depuis ses réglages.

    Accepter la permission du navigateur EST le consentement : pas de case à cocher en plus, et
    aucun envoi sans abonnement.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="abonnements_push")
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    derniere_reussite_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Push {self.user} ({self.endpoint[:40]}...)"
