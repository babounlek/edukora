from django.db import models

from catalog.models import TypeReponse


class ModeQuiz(models.TextChoices):
    PRATIQUE = "PRATIQUE", "Pratique libre"
    DIAGNOSTIC = "DIAGNOSTIC", "Test de niveau"


class ResultatDeclare(models.TextChoices):
    REUSSI = "REUSSI", "Réussi"
    PARTIEL = "PARTIEL", "Partiellement réussi"
    ECHEC = "ECHEC", "Échec"


class QuizSession(models.Model):
    """Une série de Question générée pour un utilisateur - voir quiz.services.generer_session."""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="quiz_sessions")
    cursus = models.ForeignKey("catalog.Cursus", on_delete=models.PROTECT, related_name="quiz_sessions")
    subject = models.ForeignKey(
        "catalog.Subject", null=True, blank=True, on_delete=models.SET_NULL, related_name="quiz_sessions",
    )
    theme = models.ForeignKey(
        "catalog.Tag", null=True, blank=True, on_delete=models.SET_NULL, related_name="quiz_sessions",
    )
    mode = models.CharField(max_length=10, choices=ModeQuiz.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.get_mode_display()} - {self.user} ({self.cursus})"


class QuizQuestion(models.Model):
    """
    Une catalog.Question piochée pour cette session, dans un ordre donné - jamais
    modifiée après création, le contenu vient toujours de catalog.Question. related_name
    volontairement vide (`+`) côté Question : le lien utile se lit depuis QuizQuestion,
    pas l'inverse (une Question peut apparaître dans de nombreuses sessions).
    """

    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="quiz_questions")
    question = models.ForeignKey("catalog.Question", on_delete=models.PROTECT, related_name="+")
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["session", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["session", "ordre"], name="unique_ordre_par_session"),
        ]

    def __str__(self):
        return f"{self.session} - Q{self.ordre}"


class QuizAnswer(models.Model):
    """Réponse de l'élève à une QuizQuestion - QCM (reponse_choisie, vérifiable
    objectivement) ou question ouverte (resultat_declare, auto-évalué par l'élève après
    avoir vu le corrigé)."""

    quiz_question = models.OneToOneField(QuizQuestion, on_delete=models.CASCADE, related_name="answer")
    reponse_choisie = models.CharField(
        max_length=10, blank=True,
        help_text="Lettre choisie, uniquement si la Question est un QCM (type_reponse=QCM).",
    )
    resultat_declare = models.CharField(
        max_length=10, choices=ResultatDeclare.choices, blank=True,
        help_text="Auto-déclaré par l'élève, uniquement si la Question est ouverte.",
    )
    temps_secondes = models.PositiveIntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_question} - {'correct' if self.est_correcte else 'incorrect'}"

    @property
    def est_correcte(self):
        """
        QCM : comparaison objective à Question.reponse_correcte (vérité terrain connue).
        Question ouverte : pas de vérité terrain automatisable (dissertation, calcul à
        développement libre) - on fait confiance à l'auto-déclaration de l'élève, faite
        après qu'il a vu le corrigé complet.
        """
        question = self.quiz_question.question
        if question.type_reponse == TypeReponse.QCM:
            return bool(self.reponse_choisie) and self.reponse_choisie == question.reponse_correcte
        return self.resultat_declare == ResultatDeclare.REUSSI
