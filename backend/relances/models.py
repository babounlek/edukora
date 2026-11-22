from django.db import models


class TypeRelance(models.TextChoices):
    RAPPEL_SEANCE = "rappel_seance", "Rappel de la séance du jour"
    PAIEMENT_ABANDONNE_1 = "paiement_abandonne_1", "Paiement non abouti - premier message"
    PAIEMENT_ABANDONNE_2 = "paiement_abandonne_2", "Paiement non abouti - dernier message"
    BILAN_PARENT = "bilan_parent", "Bilan de la semaine au parent"
    ABSENCE_1 = "absence_1", "Absence - deux jours sans séance"
    ABSENCE_2 = "absence_2", "Absence - une semaine sans séance, dernier message"
    FIN_ABONNEMENT_1 = "fin_abonnement_1", "Fin d'abonnement - trois jours avant"
    FIN_ABONNEMENT_2 = "fin_abonnement_2", "Fin d'abonnement - le jour même, dernier message"
    INSCRIT_SANS_PAIEMENT_1 = "inscrit_sans_paiement_1", "Inscrit sans paiement - écran d'abonnement ouvert, premier message"
    INSCRIT_SANS_PAIEMENT_2 = "inscrit_sans_paiement_2", "Inscrit sans paiement - dernier message"


class CanalRelance(models.TextChoices):
    EMAIL = "email", "E-mail"
    PUSH = "push", "Notification du navigateur"
    WHATSAPP = "whatsapp", "WhatsApp"


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


class FamilleRelance(models.TextChoices):
    INSCRIT_SANS_PAIEMENT = "inscrit_sans_paiement", "Inscrit sans paiement"


class RefusRelance(models.Model):
    """
    Le compte a ouvert le lien d'arrêt d'une famille de relances qui ne dépend d'aucun réglage du compte : plus aucun
    message de cette famille ne lui part, pour toujours.

    Le rappel quotidien et le bilan du parent ont chacun leur interrupteur sur le compte (User.rappels_actifs,
    User.bilan_parent_actif), que leur lien d'arrêt coupe. La relance d'un inscrit qui n'a pas payé (voir
    relances.inscrit_sans_paiement) part sans que le compte ait rien activé : il n'y a pas d'interrupteur à couper, et
    `rappels_actifs` à faux ne distingue pas « n'a jamais rien demandé » de « ne veut plus rien recevoir ». Le refus
    s'écrit donc ici.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="refus_relances")
    famille = models.CharField(max_length=30, choices=FamilleRelance.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "famille"], name="unique_refus_relance_par_famille"),
        ]

    def __str__(self):
        return f"Refus {self.get_famille_display()} - {self.user}"


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
