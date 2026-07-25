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
