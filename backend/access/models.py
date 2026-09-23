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
