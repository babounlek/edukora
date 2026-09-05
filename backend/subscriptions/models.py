from django.db import connection, models
from django.db import transaction as db_transaction
from django.utils import timezone

from catalog.models import Cursus, ExamSession


class DureeMode(models.TextChoices):
    FIXE = "FIXE", "Durée fixe"
    JUSQUA_EXAMEN = "JUSQUA_EXAMEN", "Jusqu'à l'examen"


# Grille de Plan.effective_price pour Jusqu'à l'Examen : un palier de
# INCREMENT_PAR_TRANCHE FCFA par tranche entamée de JOURS_PAR_TRANCHE jours restants,
# du plancher PLANCHER_JUSQUA_EXAMEN jusqu'au plafond `price` du Plan. Décision
# utilisateur du 2026-08-19 - reprend telle quelle la grille "Septembre 12 000 F ...
# Juin 3 000 F" (paliers mensuels explicites), recalculée en tranches de jours
# glissantes plutôt qu'en mois calendaires pour rester exacte quel que soit le mois
# réel de la session (BEPC/Probatoire/BAC n'ont pas tous la même date, ni d'un pays à
# l'autre - voir _calculer_duree_jusqua_examen). Remplace l'ancienne règle continue
# ("jamais plus cher au jour que Mensuel"), elle-même un remplacement d'un filet de
# seuils choisis à la main.
#
# Plancher et plafond relevés le 2026-09-05 (2 000 → 3 000, 12 000 → 15 000, voir
# migration 0014) : décision utilisateur, la grille du 30/08 sous-évaluait les deux
# bornes. Le plancher retrouve son niveau d'avant le 30/08 (la raison de l'avoir
# baissé - ne jamais dépasser le prix de l'ancien Mensuel à 2 000 F - ne tient plus
# depuis que Mensuel est retiré de la vente par la même migration). Le plafond
# retrouve le niveau de l'ancien palier "Max" (365j), qui existait avant la fusion à 2
# paliers du 19/08 - un repère déjà éprouvé, pas un montant choisi au hasard.
# INCREMENT_PAR_TRANCHE relevé à 1 500 en même temps (au lieu de rester à 1 000) pour
# que le plafond reste atteint par qui achète tôt (8 tranches, 240 jours) plutôt que
# de reculer à 360 jours - hors de portée du calendrier scolaire réel (rentrée en
# septembre, examens en juin, ~280-300 jours) et donc jamais payé en pratique.
JOURS_PAR_TRANCHE = 30
INCREMENT_PAR_TRANCHE = 1500
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
        méthode plusieurs fois par plan (durée affichée, puis effective_price qui
        l'utilise aussi), chaque appel coûtant sinon une requête ExamSession. Sans
        effet sur la fraîcheur - une instance ne vit que le temps d'une requête HTTP.
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
        (payé par qui achète loin de l'examen, à partir de 9 tranches entamées) : le
        prix descend par palier de INCREMENT_PAR_TRANCHE FCFA à chaque tranche de
        JOURS_PAR_TRANCHE jours entamée, jusqu'à PLANCHER_JUSQUA_EXAMEN qui protège
        un ticket minimum même acheté la veille de l'examen. Toujours achetable, à
        n'importe quel moment de l'année scolaire (l'ancien Plan.est_achetable/
        FENETRE_URGENCE_JOURS a été retiré) : le plafond fait déjà le travail
        qu'assurait cette fenêtre d'urgence. Voir effective_duration_days pour le
        même principe appliqué à la durée.
        """
        if self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            return self.price
        jours = self.effective_duration_days()
        tranche = jours // JOURS_PAR_TRANCHE
        return min(self.price, PLANCHER_JUSQUA_EXAMEN + tranche * INCREMENT_PAR_TRANCHE)


class SubscriptionManager(models.Manager):
    def activate_or_extend(self, user, cursus, duration_days, duration_mode=DureeMode.FIXE):
        """
        Point de passage unique pour toute prolongation d'abonnement (paiement direct
        du filleul comme récompense de parrainage au parrain) - deux appels concurrents
        sur le même (user, cursus) (ex. le paiement du filleul et sa récompense au
        parrain qui se chevauchent, ou deux paiements distincts qui se terminent en
        même temps) ne doivent jamais s'écraser l'un l'autre : chacun doit s'appliquer
        sur la valeur déjà prolongée par l'autre, pas sur une valeur périmée lue avant
        que l'autre n'ait sauvegardé.

        `duration_mode` : palier du Plan qui finance cette prolongation (voir
        Subscription.duration_mode) - jamais rétrogradé sur une ligne existante (voir
        Subscription.extend) : un top-up Mensuel après un achat Jusqu'à l'Examen ne doit
        pas faire perdre l'accès aux fonctionnalités exclusives à ce palier pour le
        reste de la période déjà payée.
        """
        with db_transaction.atomic():
            subscription, created = self.get_or_create(
                user=user, cursus=cursus,
                defaults={
                    "expires_at": timezone.now() + timezone.timedelta(days=duration_days),
                    "duration_mode": duration_mode,
                },
            )
            if not created:
                # select_for_update() : verrouille la ligne avant de (re)lire
                # expires_at, pour que le calcul d'extend() reparte toujours de la
                # valeur la plus à jour. Indisponible sur SQLite (tests) - voir la
                # même remarque dans payments.models.Transaction.sync_status.
                locked_qs = self.select_for_update() if connection.features.has_select_for_update else self
                subscription = locked_qs.get(pk=subscription.pk)
                subscription.extend(duration_days, duration_mode=duration_mode)
        return subscription


class Subscription(models.Model):
    """
    Accès actif d'un utilisateur à un Cursus. Une seule ligne par (user, cursus) :
    chaque paiement réussi prolonge expires_at plutôt que de créer une nouvelle ligne.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="subscriptions")
    cursus = models.ForeignKey(Cursus, on_delete=models.PROTECT, related_name="subscriptions")
    expires_at = models.DateTimeField()
    duration_mode = models.CharField(
        max_length=20, choices=DureeMode.choices, default=DureeMode.FIXE,
        help_text=(
            "Palier du Plan qui a (au moins une fois) financé cette ligne - copié depuis "
            "Plan.duration_mode à l'activation (voir SubscriptionManager.activate_or_extend), "
            "jamais déduit après coup. Distinct de has_access (qui ignore ce champ, "
            "n'importe quel palier donne accès au contenu de base) : sert uniquement à "
            "gater les fonctionnalités pensées comme argument de vente propre à Jusqu'à "
            "l'Examen (voir access.services.has_access_jusqua_examen)."
        ),
    )

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

    @property
    def is_jusqua_examen(self):
        return self.duration_mode == DureeMode.JUSQUA_EXAMEN

    def extend(self, duration_days, duration_mode=None):
        """
        Prolonge à partir de la date d'expiration existante si encore active, sinon à
        partir de maintenant. `duration_mode` ne peut que faire monter le palier
        (FIXE -> JUSQUA_EXAMEN), jamais l'inverse - voir SubscriptionManager.activate_or_extend.
        """
        base = self.expires_at if self.is_active else timezone.now()
        self.expires_at = base + timezone.timedelta(days=duration_days)
        update_fields = ["expires_at", "updated_at"]
        if duration_mode == DureeMode.JUSQUA_EXAMEN and self.duration_mode != DureeMode.JUSQUA_EXAMEN:
            self.duration_mode = DureeMode.JUSQUA_EXAMEN
            update_fields.append("duration_mode")
        self.save(update_fields=update_fields)


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


# Décision du 2026-08-22 : la récompense de parrainage n'étend plus l'abonnement du
# parrain (voir l'ancien PARRAINAGE_JOURS_OFFERTS) - sur un Plan JUSQUA_EXAMEN, dont
# l'échéance est calée sur la date d'examen, les jours offerts atterrissaient après
# l'examen (valeur perçue nulle, voir project_parrainage_eleve_recalibrage). Un
# crédit FCFA dépensable sur n'importe quel achat futur, sur n'importe quel cursus,
# ne dépend d'aucune date d'examen et garde donc toujours sa valeur.
PARRAINAGE_CREDIT_MONTANT = 500
PARRAINAGE_CREDIT_VALIDITE_JOURS = 365


class ParrainageRecompense(models.Model):
    """
    Trace qu'un parrainage a été récompensé, une ligne par paiement filleul ayant
    déclenché la récompense - Campay (`transaction`) ou paiement manuel approuvé
    (`manual_payment`), exactement l'un des deux étant renseigné (voir la contrainte
    ci-dessous). Sert à la fois de garde-fou anti double-crédit (chaque
    OneToOneField empêche toute création en double pour un même paiement), de
    ligne de crédit dépensable par le parrain (`montant_restant`, voir
    consommer_credit_parrainage) et d'historique consultable.
    """

    parrain = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainages_recompenses")
    filleul = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="parrainage_recompense")
    transaction = models.OneToOneField(
        "payments.Transaction", null=True, blank=True, on_delete=models.CASCADE, related_name="parrainage_recompense",
    )
    manual_payment = models.OneToOneField(
        "payments.ManualPayment", null=True, blank=True, on_delete=models.CASCADE, related_name="parrainage_recompense",
    )
    cursus = models.ForeignKey(
        Cursus, on_delete=models.PROTECT,
        help_text="Cursus dont l'achat du filleul a déclenché la récompense - purement informatif, le crédit lui-même est dépensable sur n'importe quel cursus.",
    )
    montant_offert = models.PositiveIntegerField(default=PARRAINAGE_CREDIT_MONTANT, help_text="Montant FCFA accordé au parrain, figé à l'octroi.")
    montant_restant = models.PositiveIntegerField(default=PARRAINAGE_CREDIT_MONTANT, help_text="Solde encore dépensable de ce crédit - voir consommer_credit_parrainage.")
    expires_at = models.DateTimeField(help_text="Au-delà, ce crédit n'est plus comptabilisé dans le solde même si montant_restant > 0.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(transaction__isnull=False) ^ models.Q(manual_payment__isnull=False),
                name="parrainage_recompense_exactly_one_source",
            ),
        ]

    def __str__(self):
        return f"{self.parrain} récompensé pour le parrainage de {self.filleul} (+{self.montant_offert} FCFA, {self.montant_restant} restants)"


def solde_credit_parrainage(user):
    """Somme des crédits de parrainage encore valides (non expirés) et non
    entièrement dépensés d'un utilisateur - voir consommer_credit_parrainage pour
    la dépense."""
    total = ParrainageRecompense.objects.filter(
        parrain=user, expires_at__gt=timezone.now(),
    ).aggregate(total=models.Sum("montant_restant"))["total"]
    return total or 0


def consommer_credit_parrainage(user, montant):
    """
    Déduit jusqu'à `montant` FCFA du solde de crédit parrainage de `user`, en
    consommant d'abord les crédits qui expirent le plus tôt (jamais les plus gros
    en premier) pour ne pas laisser expirer inutilement un crédit encore valable.
    Retourne le montant réellement déduit - peut être inférieur à `montant` si le
    solde s'est réduit entre la cotation (affichée à l'utilisateur avant paiement)
    et cet appel (ex. un autre paiement concurrent l'a déjà consommé) ; l'appelant
    doit toujours appeler ceci sous verrou (select_for_update via l'appelant, voir
    Transaction._confirmer_succes/ManualPayment.approve) plutôt que de faire
    confiance à la cotation seule.
    """
    if montant <= 0:
        return 0
    qs = ParrainageRecompense.objects.select_for_update() if connection.features.has_select_for_update else ParrainageRecompense.objects
    credits = qs.filter(
        parrain=user, expires_at__gt=timezone.now(), montant_restant__gt=0,
    ).order_by("expires_at")

    restant_a_deduire = montant
    deduit_total = 0
    for credit in credits:
        if restant_a_deduire <= 0:
            break
        deduction = min(credit.montant_restant, restant_a_deduire)
        credit.montant_restant -= deduction
        credit.save(update_fields=["montant_restant"])
        restant_a_deduire -= deduction
        deduit_total += deduction
    return deduit_total


def recompenser_parrainage(paiement):
    """
    Si l'utilisateur de `paiement` a été parrainé ET que ce paiement est sa toute
    première conversion réussie - tous moyens de paiement confondus (Campay
    SUCCESSFUL ou paiement manuel APPROVED) - crédite le parrain de
    PARRAINAGE_CREDIT_MONTANT FCFA (voir ParrainageRecompense/solde_credit_parrainage),
    dépensable sur n'importe lequel de ses futurs achats. Ne récompense jamais un
    réabonnement du filleul - seulement sa toute première conversion, peu importe le
    canal - pour éviter qu'un parrain accumule du crédit à chaque renouvellement de
    son filleul.

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

    source_field = "transaction" if isinstance(paiement, Transaction) else "manual_payment"
    ParrainageRecompense.objects.get_or_create(
        **{source_field: paiement},
        defaults={
            "parrain": parrain, "filleul": filleul, "cursus": paiement.plan.cursus,
            "montant_offert": PARRAINAGE_CREDIT_MONTANT, "montant_restant": PARRAINAGE_CREDIT_MONTANT,
            "expires_at": timezone.now() + timezone.timedelta(days=PARRAINAGE_CREDIT_VALIDITE_JOURS),
        },
    )
