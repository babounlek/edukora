from django.db import connection, models
from django.db import transaction as db_transaction
from django.utils import timezone

from catalog.models import Cursus, ExamSession


class DureeMode(models.TextChoices):
    FIXE = "FIXE", "Durée fixe"
    JUSQUA_EXAMEN = "JUSQUA_EXAMEN", "Jusqu'à l'examen"


# Référence de prix pour Plan.effective_price : le palier Jusqu'à l'Examen ne coûte
# jamais plus cher au jour que Mensuel (PRIX_MENSUEL_REFERENCE / DUREE_MENSUEL_REFERENCE_JOURS),
# jusqu'à un plancher minimum. Décision utilisateur du 2026-08-19 - remplace un filet de
# sécurité à seuils choisis à la main par une règle continue ancrée sur des nombres déjà
# déterminés ailleurs dans la grille (le prix de Mensuel, le plancher historique de
# l'ancien Pack Examen) plutôt que des seuils arbitraires.
PRIX_MENSUEL_REFERENCE = 2000
DUREE_MENSUEL_REFERENCE_JOURS = 30
PLANCHER_JUSQUA_EXAMEN = 3000


class ProductType(models.TextChoices):
    """
    Ce que l'achat de ce Plan active - ABONNEMENT active/prolonge Subscription (accès de
    base au Cursus), ADDON_INEDIT active/prolonge InscriptionInedite (add-on Épreuves
    Inédites, voir sa docstring), ADDON_REPETITEUR active/prolonge InscriptionRepetiteur
    (add-on Fiches, voir sa docstring - même patron qu'ADDON_INEDIT). Décision "C2" de
    l'audit "Épreuves Inédites" : un type de produit supplémentaire sur le même modèle
    Plan/Transaction/ManualPayment plutôt qu'une facturation parallèle -
    Transaction.sync_status/ManualPayment.approve lisent ce champ pour savoir laquelle
    des activations appeler.
    """

    ABONNEMENT = "ABONNEMENT", "Abonnement cursus"
    ADDON_INEDIT = "ADDON_INEDIT", "Add-on Épreuves Inédites"
    ADDON_REPETITEUR = "ADDON_REPETITEUR", "Add-on Fiches Répétiteur"


# Fenêtre pendant laquelle un Plan "jusqu'à l'examen" est proposé à la vente (voir
# Plan.est_achetable). Au-delà, "jusqu'à ton examen" ne crée plus aucune urgence
# réelle et le pack revient moins cher au jour que l'abonnement annuel.
FENETRE_URGENCE_JOURS = 60


class Plan(models.Model):
    """Offre commerciale : ce qu'un utilisateur achète (prix, durée, périmètre d'accès)."""

    name = models.CharField(max_length=100)
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="plans")
    product_type = models.CharField(max_length=20, choices=ProductType.choices, default=ProductType.ABONNEMENT)
    price = models.PositiveIntegerField(help_text="Prix en FCFA.")
    duration_mode = models.CharField(max_length=20, choices=DureeMode.choices, default=DureeMode.FIXE)
    duration_days = models.PositiveSmallIntegerField(
        default=30,
        help_text="Utilisé tel quel si duration_mode=FIXE. Ignoré (valeur de repli seulement, voir effective_duration_days) si duration_mode=JUSQUA_EXAMEN.",
    )
    is_active = models.BooleanField(default=True, help_text="Décoche pour retirer une offre du catalogue sans la supprimer.")
    inclut_inedit = models.BooleanField(
        default=False,
        help_text=(
            "Un Plan ABONNEMENT qui coche ceci active aussi l'add-on Épreuves Inédites "
            "(InscriptionInedite) en plus de l'abonnement, pour la même durée - sans "
            "achat séparé d'un Plan ADDON_INEDIT. Décision produit du 2026-08-09 : la "
            "formule Max (1 an) inclut l'accès aux inédites. Sans effet sur un Plan "
            "ADDON_INEDIT lui-même (déjà exclusivement dédié à cet accès, voir "
            "_activer_acces) - n'a de sens que pour product_type=ABONNEMENT."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Attribut de classe (pas un champ) servant de valeur par défaut au mémo
    # d'instance de effective_duration_days - voir sa docstring.
    _effective_days_cache = None

    class Meta:
        ordering = ["cursus", "price"]

    def __str__(self):
        return f"{self.name} ({self.price} FCFA / {self.duration_days}j)"

    def effective_duration_days(self):
        """
        Durée réelle en jours à appliquer à l'activation/l'affichage. Pour
        JUSQUA_EXAMEN, calculée dynamiquement depuis la prochaine ExamSession de
        l'examen du cursus - jamais figée dans duration_days, pour rester correcte
        d'une session d'examen sur l'autre sans avoir à rééditer le Plan chaque année.

        Mémoïsé par instance : la sérialisation d'une liste de plans appelle cette
        méthode plusieurs fois par plan (durée affichée puis est_achetable), chaque
        appel coûtant sinon une requête ExamSession. Sans effet sur la fraîcheur -
        une instance ne vit que le temps d'une requête HTTP.
        """
        if self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            return self.duration_days
        if self._effective_days_cache is None:
            self._effective_days_cache = self._calculer_duree_jusqua_examen()
        return self._effective_days_cache

    def _calculer_duree_jusqua_examen(self):
        session = ExamSession.prochaine_pour(self.cursus.country, self.cursus.examen)
        if session is None:
            # Aucune date d'examen configurée pour ce (pays, examen) : filet de
            # sécurité, on retombe sur duration_days plutôt que de bloquer un
            # paiement déjà encaissé ou d'afficher une durée absurde.
            return self.duration_days
        jours = (session.date_debut - timezone.now().date()).days
        return max(jours, 1)

    def effective_price(self):
        """
        Prix réel à facturer/afficher. Pour JUSQUA_EXAMEN, `price` sert de plafond
        (payé par qui achète loin de l'examen) : en dessous, le prix suit
        exactement le taux journalier de Mensuel (jamais plus cher au jour qu'un
        abonnement mensuel), jusqu'à PLANCHER_JUSQUA_EXAMEN qui protège un ticket
        minimum même acheté la veille de l'examen. Voir effective_duration_days
        pour le même principe appliqué à la durée.
        """
        if self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            return self.price
        jours = self.effective_duration_days()
        taux_journalier = PRIX_MENSUEL_REFERENCE / DUREE_MENSUEL_REFERENCE_JOURS
        return min(self.price, max(PLANCHER_JUSQUA_EXAMEN, round(jours * taux_journalier)))

    def est_achetable(self):
        """
        `is_active` dit qu'une offre existe au catalogue ; ceci dit qu'elle est
        vendable MAINTENANT. Seul le Pack Examen (JUSQUA_EXAMEN) fait la différence :
        à 3 000 FCFA il n'a de sens que dans la fenêtre d'urgence qui précède la
        session. Hors fenêtre il donnerait, ex. à 281 jours de la session, presque un
        an d'accès pour un cinquième du prix de la formule Max (15 000 FCFA / 365 j) -
        la règle est donc portée par le modèle et appliquée à TOUS les points
        d'entrée (liste des offres, paiement Campay, déclaration de paiement manuel),
        jamais seulement par un filtre d'affichage côté frontend qu'un simple POST
        avec le bon plan_id contournerait.
        """
        if self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            return True
        return self.effective_duration_days() <= FENETRE_URGENCE_JOURS


class SubscriptionManager(models.Manager):
    def activate_or_extend(self, user, cursus, duration_days):
        """
        Point de passage unique pour toute prolongation d'abonnement (paiement direct
        du filleul comme récompense de parrainage au parrain) - deux appels concurrents
        sur le même (user, cursus) (ex. le paiement du filleul et sa récompense au
        parrain qui se chevauchent, ou deux paiements distincts qui se terminent en
        même temps) ne doivent jamais s'écraser l'un l'autre : chacun doit s'appliquer
        sur la valeur déjà prolongée par l'autre, pas sur une valeur périmée lue avant
        que l'autre n'ait sauvegardé.
        """
        with db_transaction.atomic():
            subscription, created = self.get_or_create(
                user=user, cursus=cursus,
                defaults={"expires_at": timezone.now() + timezone.timedelta(days=duration_days)},
            )
            if not created:
                # select_for_update() : verrouille la ligne avant de (re)lire
                # expires_at, pour que le calcul d'extend() reparte toujours de la
                # valeur la plus à jour. Indisponible sur SQLite (tests) - voir la
                # même remarque dans payments.models.Transaction.sync_status.
                locked_qs = self.select_for_update() if connection.features.has_select_for_update else self
                subscription = locked_qs.get(pk=subscription.pk)
                subscription.extend(duration_days)
        return subscription


class Subscription(models.Model):
    """
    Accès actif d'un utilisateur à un Cursus. Une seule ligne par (user, cursus) :
    chaque paiement réussi prolonge expires_at plutôt que de créer une nouvelle ligne.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="subscriptions")
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="subscriptions")
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SubscriptionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "cursus"], name="unique_subscription_per_cursus"),
        ]

    def __str__(self):
        return f"{self.user} - {self.cursus} (expire {self.expires_at:%d/%m/%Y})"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def extend(self, duration_days):
        """Prolonge à partir de la date d'expiration existante si encore active, sinon à partir de maintenant."""
        base = self.expires_at if self.is_active else timezone.now()
        self.expires_at = base + timezone.timedelta(days=duration_days)
        self.save(update_fields=["expires_at", "updated_at"])


class InscriptionInediteManager(models.Manager):
    def activate_or_extend(self, user, cursus, duration_days):
        """Miroir exact de SubscriptionManager.activate_or_extend - même raison de
        verrouillage (voir sa docstring), jamais dupliquée en logique divergente."""
        with db_transaction.atomic():
            inscription, created = self.get_or_create(
                user=user, cursus=cursus,
                defaults={"expires_at": timezone.now() + timezone.timedelta(days=duration_days)},
            )
            if not created:
                locked_qs = self.select_for_update() if connection.features.has_select_for_update else self
                inscription = locked_qs.get(pk=inscription.pk)
                inscription.extend(duration_days)
        return inscription


class InscriptionInedite(models.Model):
    """
    Accès actif d'un utilisateur à l'add-on Épreuves Inédites pour un Cursus - miroir
    exact de Subscription (même grain user+cursus, même contrainte d'unicité, même
    activate_or_extend), mais modèle séparé plutôt qu'un champ ajouté sur Subscription
    (décision "C2" de l'audit "Épreuves Inédites") : ne touche aucune ligne déjà
    exploitée par SubscriptionManager.activate_or_extend/recompenser_parrainage, et son
    cycle de vie (expiration, renouvellement) reste indépendant de l'abonnement de base
    sur le même cursus - un utilisateur peut laisser expirer l'un sans affecter l'autre.

    Accès (voir access.services.has_access_inedite) : contrairement à Subscription (dont
    has_access court-circuite via Lesson.est_vitrine), aucune notion de vitrine ici -
    décision produit "corrigé gaté comme le reste" de l'audit, aucune exception.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="inscriptions_inedites")
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="inscriptions_inedites")
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InscriptionInediteManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "cursus"], name="unique_inscription_inedite_per_cursus"),
        ]

    def __str__(self):
        return f"{self.user} - {self.cursus} inédit (expire {self.expires_at:%d/%m/%Y})"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def extend(self, duration_days):
        """Voir Subscription.extend - même règle."""
        base = self.expires_at if self.is_active else timezone.now()
        self.expires_at = base + timezone.timedelta(days=duration_days)
        self.save(update_fields=["expires_at", "updated_at"])


class InscriptionRepetiteurManager(models.Manager):
    def activate_or_extend(self, user, cursus, duration_days):
        """Miroir exact de SubscriptionManager.activate_or_extend - même raison de
        verrouillage (voir sa docstring), jamais dupliquée en logique divergente."""
        with db_transaction.atomic():
            inscription, created = self.get_or_create(
                user=user, cursus=cursus,
                defaults={"expires_at": timezone.now() + timezone.timedelta(days=duration_days)},
            )
            if not created:
                locked_qs = self.select_for_update() if connection.features.has_select_for_update else self
                inscription = locked_qs.get(pk=inscription.pk)
                inscription.extend(duration_days)
        return inscription


class InscriptionRepetiteur(models.Model):
    """
    Accès actif d'un utilisateur à l'add-on Fiches (répétiteur) pour un Cursus - miroir
    exact d'InscriptionInedite (même grain user+cursus, même contrainte d'unicité, même
    activate_or_extend) : accès temporel illimité en volume, pas de système de crédits
    (décision produit du chantier "Outil Fiches pour répétiteurs") - pendant que
    l'inscription est active, aucune limite sur le nombre de fiches générées.

    Accès (voir access.services.has_access_fiches) : aucune notion de vitrine ici, même
    choix qu'InscriptionInedite - l'outil de génération de fiches est entièrement gaté
    par cet add-on, sans exception.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="inscriptions_repetiteur")
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="inscriptions_repetiteur")
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InscriptionRepetiteurManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "cursus"], name="unique_inscription_repetiteur_per_cursus"),
        ]

    def __str__(self):
        return f"{self.user} - {self.cursus} répétiteur (expire {self.expires_at:%d/%m/%Y})"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def extend(self, duration_days):
        """Voir Subscription.extend - même règle."""
        base = self.expires_at if self.is_active else timezone.now()
        self.expires_at = base + timezone.timedelta(days=duration_days)
        self.save(update_fields=["expires_at", "updated_at"])


PARRAINAGE_JOURS_OFFERTS = 7


class ParrainageRecompense(models.Model):
    """
    Trace qu'un parrainage a été récompensé, une ligne par paiement filleul ayant
    déclenché la récompense - Campay (`transaction`) ou paiement manuel approuvé
    (`manual_payment`), exactement l'un des deux étant renseigné (voir la contrainte
    ci-dessous). Sert à la fois de garde-fou anti double-crédit (chaque
    OneToOneField empêche toute création en double pour un même paiement) et
    d'historique consultable (combien de jours offerts, à qui, pour quel filleul).
    """

    parrain = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainages_recompenses")
    filleul = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainage_recompense")
    transaction = models.OneToOneField(
        "payments.Transaction", null=True, blank=True, on_delete=models.CASCADE, related_name="parrainage_recompense",
    )
    manual_payment = models.OneToOneField(
        "payments.ManualPayment", null=True, blank=True, on_delete=models.CASCADE, related_name="parrainage_recompense",
    )
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT)
    jours_offerts = models.PositiveSmallIntegerField(default=PARRAINAGE_JOURS_OFFERTS)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(transaction__isnull=False) ^ models.Q(manual_payment__isnull=False),
                name="parrainage_recompense_exactly_one_source",
            ),
        ]

    def __str__(self):
        return f"{self.parrain} récompensé pour le parrainage de {self.filleul} (+{self.jours_offerts}j)"


def recompenser_parrainage(paiement):
    """
    Si l'utilisateur de `paiement` a été parrainé ET que ce paiement est sa toute
    première conversion réussie - tous moyens de paiement confondus (Campay
    SUCCESSFUL ou paiement manuel APPROVED) - prolonge l'abonnement du parrain (sur
    le même cursus que l'achat du filleul) de PARRAINAGE_JOURS_OFFERTS jours. Ne
    récompense jamais un réabonnement du filleul - seulement sa toute première
    conversion, peu importe le canal - pour éviter qu'un parrain accumule des jours
    à chaque renouvellement de son filleul.

    `paiement` : une instance payments.Transaction (déjà SUCCESSFUL) ou
    payments.ManualPayment (déjà APPROVED). Appelée depuis Transaction.sync_status()
    et ManualPayment.approve() une fois l'abonnement du filleul déjà activé -
    les imports sont locaux pour éviter un import circulaire (payments.models
    importe déjà subscriptions.models au niveau module).
    """
    from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction

    # Portée volontairement limitée à l'abonnement de base : récompenser un parrain
    # pour l'achat d'un add-on Épreuves Inédites par son filleul n'a jamais été demandé
    # (voir l'audit "Épreuves Inédites", phase "Accès") - étendre le parrainage à ce
    # second type de produit est une vraie décision produit (quel montant/durée offrir ?
    # sur quel produit ?), pas une extension mécanique à trancher silencieusement ici.
    if paiement.plan.product_type != ProductType.ABONNEMENT:
        return

    filleul = paiement.user
    parrain = filleul.referred_by
    if parrain is None:
        return

    # Première conversion évaluée sur les DEUX canaux à la fois : un filleul qui a
    # déjà un Transaction SUCCESSFUL ou un ManualPayment APPROVED antérieur (peu
    # importe lequel) a déjà converti son parrain une fois.
    reussies = filleul.transactions.filter(status=StatutTransaction.SUCCESSFUL)
    approuves = filleul.manual_payments.filter(status=ManualPaymentStatus.APPROVED)
    if isinstance(paiement, Transaction):
        reussies = reussies.exclude(pk=paiement.pk)
    elif isinstance(paiement, ManualPayment):
        approuves = approuves.exclude(pk=paiement.pk)

    premiere_conversion = not reussies.exists() and not approuves.exists()
    if not premiere_conversion:
        return

    Subscription.objects.activate_or_extend(
        user=parrain, cursus=paiement.plan.cursus, duration_days=PARRAINAGE_JOURS_OFFERTS,
    )
    source_field = "transaction" if isinstance(paiement, Transaction) else "manual_payment"
    ParrainageRecompense.objects.get_or_create(
        **{source_field: paiement},
        defaults={
            "parrain": parrain, "filleul": filleul,
            "cursus": paiement.plan.cursus, "jours_offerts": PARRAINAGE_JOURS_OFFERTS,
        },
    )
