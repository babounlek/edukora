"""
« Fiches EduKora » : des fiches de révision toutes faites, écrites par EduKora, à côté des notes que l'élève écrit lui-même.

Une fiche = une notion à savoir par cœur (une définition d'éducation civique, par exemple), dite en quelques lignes, avec
les sessions d'examen où elle est tombée. Plus courte qu'un cours (qui a déjà sa section « La règle ») : la définition,
un exemple, et « tombé au BEPC 2018, 2019 ». L'élève peut la garder dans ses notes : elle entre alors dans sa révision
espacée, ses rappels et son partage, comme une note à lui (voir memos.services.garder_dans_les_notes).

Jamais publiée sans relecture : une fiche naît BROUILLON (extraite des corrigés déjà validés, voir
memos.extraction), un enseignant la relit, l'administrateur la publie.
"""

from django.db import models


class StatutMemo(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon (à relire)"
    PUBLIE = "PUBLIE", "Publiée"


class Memo(models.Model):
    subject = models.ForeignKey("catalog.Subject", on_delete=models.CASCADE, related_name="memos")
    cursus = models.ManyToManyField("catalog.Cursus", related_name="memos", help_text="Les examens que cette fiche prépare.")
    theme = models.ForeignKey(
        "catalog.Tag", null=True, blank=True, on_delete=models.SET_NULL, related_name="memos",
        help_text="Le thème de la notion : la note gardée par l'élève revient quand il retravaille ce thème.",
    )
    terme = models.CharField(max_length=160, help_text="La notion : « Scrutin », « Suffrage universel ».")
    definition = models.TextField(help_text="La définition à retenir, en quelques lignes (Markdown, formules entre $).")
    exemple = models.TextField(blank=True, help_text="Un exemple ou une précision, facultatif.")
    sessions = models.JSONField(
        default=list, blank=True,
        help_text='Où la notion est tombée : [{"annee": 2019, "origine": "OFFICIEL"}, …] (voir catalog.Lesson.origine).',
    )
    sources = models.ManyToManyField(
        "catalog.Lesson", blank=True, related_name="memos",
        help_text="Les épreuves dont la fiche est tirée : la trace de ce qui est affirmé.",
    )
    gratuit = models.BooleanField(default=False, help_text="Lisible sans abonnement (quelques fiches par matière).")
    statut = models.CharField(max_length=10, choices=StatutMemo.choices, default=StatutMemo.BROUILLON)
    relu_par_enseignant = models.BooleanField(default=False, help_text="Un enseignant a relu la définition.")
    modifie_a_la_main = models.BooleanField(
        default=False, help_text="Retouchée dans l'administration : l'extraction ne la réécrit plus.",
    )
    ordre = models.PositiveIntegerField(default=100, help_text="Plus petit = plus haut ; les plus souvent tombées d'abord.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subject_id", "ordre", "terme"]
        constraints = [models.UniqueConstraint(fields=["subject", "terme"], name="unique_memo_par_matiere_et_terme")]
        verbose_name = "fiche EduKora"
        verbose_name_plural = "fiches EduKora"

    def __str__(self):
        return f"{self.subject_id} - {self.terme}"

    def save(self, *args, **kwargs):
        # Une fiche publiée sans relecture ne peut pas exister : c'est la relecture qui autorise la publication.
        if self.statut == StatutMemo.PUBLIE and not self.relu_par_enseignant:
            self.statut = StatutMemo.BROUILLON
        super().save(*args, **kwargs)
