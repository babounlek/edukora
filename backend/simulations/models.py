from django.db import models

from inedit.models import CausePerte, ResultatDeclare


class SimulationEpreuve(models.Model):
    """
    Passage d'un élève sur une épreuve OFFICIELLE (catalog.Lesson) en conditions d'examen :
    chrono, corrigé masqué jusqu'à la fin, auto-notation sur le barème réel, rapport de fin.
    Le pendant, pour les annales, de inedit.TentativeInedite - et volontairement avec les mêmes
    noms de champs (exam_mode_started_at, submitted_at, note_obtenue...) : le calcul de la note
    (inedit.notation) et le rapport (inedit.rapport) s'appliquent aux deux sans rien savoir de
    leur différence.

    Granularité : l'EXERCICE, pas la sous-question. Un corrigé officiel est rédigé et lu exercice
    par exercice, et le barème d'une annale ne descend presque jamais sous l'exercice - noter à
    ce niveau est ce que ferait un correcteur, et évite de demander 25 cases à cocher.
    """

    profil = models.ForeignKey("users.Profil", on_delete=models.CASCADE, related_name="simulations_epreuves")
    lesson = models.ForeignKey("catalog.Lesson", on_delete=models.CASCADE, related_name="simulations")

    started_at = models.DateTimeField(auto_now_add=True)
    exam_mode_started_at = models.DateTimeField(null=True, blank=True)
    mode_papier = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    exercices_marques = models.ManyToManyField(
        "catalog.Exercise", blank=True, related_name="+",
        help_text="Exercices marqués « à revoir » par l'élève.",
    )
    note_obtenue = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bareme_snapshot = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    score_obtenu = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.profil} - {self.lesson}"


class SimulationReponse(models.Model):
    """État d'un exercice pour l'élève : déclaré traité, points obtenus, cause de la perte.
    Le nom `question_id` (propriété) est celui qu'attend inedit.notation : ici la « question »
    notée est l'exercice entier."""

    simulation = models.ForeignKey(SimulationEpreuve, on_delete=models.CASCADE, related_name="reponses")
    exercise = models.ForeignKey("catalog.Exercise", on_delete=models.CASCADE, related_name="+")

    traitee_at = models.DateTimeField(null=True, blank=True)
    points_obtenus = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    resultat_declare = models.CharField(max_length=10, choices=ResultatDeclare.choices, blank=True)
    cause_perte = models.CharField(max_length=15, choices=CausePerte.choices, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["simulation", "exercise"], name="unique_reponse_par_exercice_et_simulation"),
        ]

    # Interface attendue par inedit.notation (qui ne connaît que des « questions »).
    @property
    def question_id(self):
        return self.exercise_id

    reponse_choisie = ""
    criteres_valides = ()

    @property
    def est_correcte(self):
        return self.resultat_declare == ResultatDeclare.REUSSI
