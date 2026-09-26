from django.db import models


class LectureProgress(models.Model):
    """Trace qu'un utilisateur a ouvert la lecture complète d'une Lesson ou d'un Cours (jamais l'aperçu)."""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="lectures")
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
                fields=["user", "lesson"], name="unique_lecture_lesson", condition=models.Q(lesson__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "cours"], name="unique_lecture_cours", condition=models.Q(cours__isnull=False),
            ),
        ]

    def __str__(self):
        cible = self.lesson or self.cours
        return f"{self.user} - {cible}"


class ExerciceFait(models.Model):
    """
    Trace qu'un utilisateur a DÉCLARÉ avoir traité un exercice précis.

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

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="exercices_faits")
    exercise = models.ForeignKey("catalog.Exercise", on_delete=models.CASCADE, related_name="faits")
    fait_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fait_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "exercise"], name="unique_exercice_fait"),
        ]

    def __str__(self):
        return f"{self.user} - {self.exercise}"


class MarqueEtude(models.Model):
    """
    Ce qu'un élève garde d'une section qu'il étudie : l'avoir comprise, l'avoir mise de
    côté (signet), et sa propre note. Une ligne par (élève, document, section) : les
    trois vivent ensemble parce qu'ils se posent au même endroit et se lisent ensemble
    dans le carnet - et une ligne devenue vide est supprimée (voir
    access.etude.enregistrer_marque), jamais conservée à zéro.

    `cle` est l'ancre de la section dans le lecteur ("regle", "exercice-3") : c'est aussi
    ce qui permet au carnet de renvoyer à l'endroit exact. "compris" est DÉCLARÉ par
    l'élève, comme ExerciceFait : ouvrir une section ne dit pas qu'on l'a comprise, et un
    suivi qu'on remplit sans travailler ne mesure plus rien.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="marques_etude")
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
                fields=["user", "lesson", "cle"], name="unique_marque_lesson", condition=models.Q(lesson__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "cours", "cle"], name="unique_marque_cours", condition=models.Q(cours__isnull=False),
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.lesson or self.cours} - {self.cle}"
