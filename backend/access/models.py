from django.db import models


class LectureProgress(models.Model):
    """Trace qu'un profil a ouvert la lecture complète d'une Lesson ou d'un Cours (jamais l'aperçu)."""

    profil = models.ForeignKey("users.Profil", on_delete=models.CASCADE, related_name="lectures")
    lesson = models.ForeignKey("catalog.Lesson", null=True, blank=True, on_delete=models.CASCADE, related_name="lectures")
    cours = models.ForeignKey("catalog.Cours", null=True, blank=True, on_delete=models.CASCADE, related_name="lectures")

    first_read_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_read_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(lesson__isnull=False, cours__isnull=True)
                    | models.Q(lesson__isnull=True, cours__isnull=False)
                ),
                name="lectureprogress_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["profil", "lesson"], name="unique_lecture_lesson", condition=models.Q(lesson__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["profil", "cours"], name="unique_lecture_cours", condition=models.Q(cours__isnull=False),
            ),
        ]

    def __str__(self):
        cible = self.lesson or self.cours
        return f"{self.profil} - {cible}"


class ExerciceFait(models.Model):
    """
    Trace qu'un profil a DÉCLARÉ avoir traité un exercice précis.

    Déclaré, jamais déduit : ouvrir une épreuve ne dit pas qu'on l'a travaillée, et
    LectureProgress ci-dessus n'enregistre justement que l'ouverture, au niveau de la
    Lesson entière. Sans cette table, une file d'entraînement afficherait des coches
    devinées - un suivi faux est pire que pas de suivi, surtout sur la seule surface
    où l'élève vient mesurer son avancement.

    Le pendant de "J'ai fini" sur la séance du jour (voir quiz.SeanceJournaliere) :
    même principe, l'élève dit ce qu'il a fait. On ne prétend pas savoir s'il l'a
    RÉUSSI - un exercice d'annale se lit et se compare à son corrigé, il ne se note
    pas automatiquement.
    """

    profil = models.ForeignKey("users.Profil", on_delete=models.CASCADE, related_name="exercices_faits")
    exercise = models.ForeignKey("catalog.Exercise", on_delete=models.CASCADE, related_name="faits")
    fait_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fait_at"]
        constraints = [
            models.UniqueConstraint(fields=["profil", "exercise"], name="unique_exercice_fait"),
        ]

    def __str__(self):
        return f"{self.profil} - {self.exercise}"


class MarqueEtude(models.Model):
    """
    Ce qu'un élève garde d'une section qu'il étudie : l'avoir comprise, l'avoir mise de
    côté (signet), et sa propre note. Une ligne par (profil, document, section) : les
    trois vivent ensemble parce qu'ils se posent au même endroit et se lisent ensemble
    dans le carnet - et une ligne devenue vide est supprimée (voir
    access.etude.enregistrer_marque), jamais conservée à zéro.

    `cle` est l'ancre de la section dans le lecteur ("regle", "exercice-3") : c'est aussi
    ce qui permet au carnet de renvoyer à l'endroit exact. "compris" est DÉCLARÉ par
    l'élève, comme ExerciceFait : ouvrir une section ne dit pas qu'on l'a comprise, et un
    suivi qu'on remplit sans travailler ne mesure plus rien.
    """

    profil = models.ForeignKey("users.Profil", on_delete=models.CASCADE, related_name="marques_etude")
    lesson = models.ForeignKey("catalog.Lesson", null=True, blank=True, on_delete=models.CASCADE, related_name="marques_etude")
    cours = models.ForeignKey("catalog.Cours", null=True, blank=True, on_delete=models.CASCADE, related_name="marques_etude")
    cle = models.CharField(max_length=60)

    compris = models.BooleanField(default=False)
    signet = models.BooleanField(default=False)
    note = models.TextField(blank=True, max_length=2000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(lesson__isnull=False, cours__isnull=True)
                    | models.Q(lesson__isnull=True, cours__isnull=False)
                ),
                name="marqueetude_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["profil", "lesson", "cle"], name="unique_marque_lesson", condition=models.Q(lesson__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["profil", "cours", "cle"], name="unique_marque_cours", condition=models.Q(cours__isnull=False),
            ),
        ]

    def __str__(self):
        return f"{self.profil} - {self.lesson or self.cours} - {self.cle}"


class ReglagesTelechargement(models.Model):
    """
    Réglages des quotas quotidiens de téléchargement de PDF (voir access.quota) : UNE seule ligne, modifiable depuis
    l'admin. Rien n'est codé en dur ailleurs : ni les quotas, ni le fuseau qui décide de la journée.
    """

    actif = models.BooleanField(
        default=True, help_text="Décoche pour suspendre tous les quotas (téléchargements illimités). Les contrôles d'accès restent.",
    )
    quota_visiteur = models.PositiveIntegerField(
        default=3, help_text="PDF par jour pour un visiteur ou un compte sans abonnement actif.",
    )
    quota_abonne = models.PositiveIntegerField(default=12, help_text="PDF par jour pour un profil avec un abonnement actif.")
    fuseau = models.CharField(
        max_length=40, default="Africa/Douala",
        help_text="Fuseau IANA qui décide de la journée : le quota repart à zéro à minuit dans ce fuseau.",
    )
    plafond_identites_reseau = models.PositiveIntegerField(
        default=40,
        help_text=(
            "Nouveaux visiteurs (cookies) reconnus par jour pour un même réseau. Au-delà, les visiteurs sans cookie "
            "valide de ce réseau partagent UN seul quota : effacer son cookie n'ouvre pas de quota supplémentaire."
        ),
    )
    plafond_reseau = models.PositiveIntegerField(
        default=60,
        help_text=(
            "PDF par jour pour un même réseau (IPv4 exacte, ou /64 en IPv6), tous visiteurs et comptes sans abonnement "
            "confondus. Large : un réseau scolaire ou mobile partagé ne doit pas être bloqué par quelques élèves."
        ),
    )
    plafond_reseau_large = models.PositiveIntegerField(
        default=200, help_text="Même plafond pour un bloc plus large (/24 en IPv4, /48 en IPv6) : limite la rotation d'adresses.",
    )
    budget_global_anonyme = models.PositiveIntegerField(
        default=3000,
        help_text="Disjoncteur : PDF par jour pour l'ensemble des visiteurs anonymes. Les abonnés ne sont jamais concernés.",
    )
    retention_jours = models.PositiveIntegerField(
        default=90, help_text="Ancienneté maximale du journal des téléchargements (commande purger_telechargements).",
    )

    class Meta:
        verbose_name = "réglages des téléchargements PDF"
        verbose_name_plural = "réglages des téléchargements PDF"

    def __str__(self):
        return f"Quotas PDF : {self.quota_visiteur}/jour (visiteur), {self.quota_abonne}/jour (abonné)"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def charger(cls):
        return cls.objects.get_or_create(pk=1)[0]


class CompteurQuota(models.Model):
    """
    Compteur d'une journée pour une portée : le demandeur lui-même (`demandeur`), son réseau (`reseau`,
    `reseau_large`), les nouveaux visiteurs d'un réseau (`identites`), le budget de tous les anonymes
    (`global_anonyme`), et les statistiques agrégées (`refus_*`, `quota_atteint`). La ligne est verrouillée
    (select_for_update) le temps de la décision : deux requêtes simultanées ne peuvent pas dépasser le quota.
    """

    jour = models.DateField()
    portee = models.CharField(max_length=20)
    cle = models.CharField(max_length=64, blank=True)
    nombre = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["jour", "portee", "cle"], name="unique_compteur_quota")]
        indexes = [models.Index(fields=["jour"])]

    def __str__(self):
        return f"{self.jour} {self.portee} {self.cle or '-'} = {self.nombre}"


class TelechargementPdf(models.Model):
    """
    Un PDF délivré, une fois par (jour, demandeur, document) : c'est à la fois le journal et l'« unité » de quota.
    Redemander le même PDF le même jour, ou reprendre un transfert interrompu, retombe sur cette ligne et ne coûte
    rien. Aucune donnée personnelle : `demandeur` est un identifiant pseudonyme (c:<compte>, p:<profil>,
    v:<visiteur aléatoire>, r:<réseau haché>), jamais une IP, un en-tête ni un jeton.
    """

    jour = models.DateField()
    demandeur = models.CharField(max_length=40)
    type_demandeur = models.CharField(max_length=10)
    document = models.CharField(max_length=80)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["jour", "demandeur", "document"], name="unique_telechargement_pdf")]
        indexes = [models.Index(fields=["jour"])]
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.jour} {self.demandeur} {self.document}"
