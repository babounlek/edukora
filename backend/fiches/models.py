from django.db import models
from django.utils.text import slugify

from catalog.models import Difficulte

from .storage import protected_storage


def _sujet_pdf_upload_to(fiche, filename):
    # Préfixé par le code pays - même convention que les autres storages de PDF
    # privés/publics du projet (voir catalog.sujet_pdf.sujet_pdf_filename,
    # inedit.models._sujet_pdf_upload_to) : sans lui, deux répétiteurs de pays
    # différents choisissant le même titre de fiche pourraient collider.
    return f"{fiche.cursus.country.code.lower()}/{fiche.owner_id}/{slugify(fiche.titre)}-sujet.pdf"


def _corrige_pdf_upload_to(fiche, filename):
    return f"{fiche.cursus.country.code.lower()}/{fiche.owner_id}/{slugify(fiche.titre)}-corrige.pdf"


class StatutGeneration(models.TextChoices):
    """
    Cycle de vie de la génération PDF d'une FicheGeneree - distinct de
    catalog.StatutContenu (éditorial, s'applique au contenu source comme
    CompetenceItem) : ici on suit une tâche asynchrone déclenchée par le répétiteur
    lui-même à la création, jamais une relecture humaine.
    """

    EN_COURS = "EN_COURS", "Génération en cours"
    PRETE = "PRETE", "Prête"
    ECHEC = "ECHEC", "Échec"


class FicheGeneree(models.Model):
    """
    Une fiche d'exercices assemblée par un répétiteur (voir fiches.services.generer_fiche)
    à partir de quiz.CompetenceItem déjà validés - jamais de génération IA live, jamais
    un extrait d'Exercise (voir la docstring de CompetenceItem, qui documente déjà
    pourquoi un item de cette banque se suffit à lui-même hors contexte, exactement ce
    qu'il faut pour composer une fiche autonome).

    Deux PDF distincts (voir fiches.pdf, décision produit du chantier "Outil Fiches pour
    répétiteurs") : `sujet_pdf` (à distribuer tel quel aux élèves) et `corrige_pdf`
    (usage personnel du répétiteur) - jamais un seul fichier combiné, pour que le
    répétiteur puisse partager l'un sans avoir à recouper l'autre lui-même.
    """

    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="fiches")
    cursus = models.ForeignKey("catalog.Cursus", on_delete=models.PROTECT, related_name="fiches")
    subject = models.ForeignKey("catalog.Subject", on_delete=models.PROTECT, related_name="fiches")
    themes = models.ManyToManyField(
        "catalog.Tag", related_name="fiches",
        help_text="Compétences choisies par le répétiteur au moment de la génération.",
    )

    titre = models.CharField(max_length=200)
    difficulte = models.CharField(
        max_length=10, choices=Difficulte.choices, blank=True,
        help_text="Filtre optionnel - vide veut dire toutes difficultés confondues.",
    )
    nombre_questions = models.PositiveSmallIntegerField(help_text="Nombre de questions demandé par le répétiteur.")

    statut = models.CharField(max_length=10, choices=StatutGeneration.choices, default=StatutGeneration.EN_COURS)
    sujet_pdf = models.FileField(storage=protected_storage, upload_to=_sujet_pdf_upload_to, blank=True)
    corrige_pdf = models.FileField(storage=protected_storage, upload_to=_corrige_pdf_upload_to, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.titre} ({self.owner})"


class FicheItem(models.Model):
    """
    Un CompetenceItem piochée pour cette fiche, dans un ordre donné - jamais recalculé
    après création (même patron que quiz.QuizQuestion.ordre : l'ordre de tirage est figé
    une fois pour toutes, pour que le PDF déjà généré corresponde toujours à ce que le
    répétiteur a vu à l'écran)."""

    fiche = models.ForeignKey(FicheGeneree, on_delete=models.CASCADE, related_name="items")
    competence_item = models.ForeignKey(
        "quiz.CompetenceItem", on_delete=models.PROTECT, related_name="fiche_items",
    )
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["fiche", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["fiche", "ordre"], name="unique_ordre_par_fiche"),
        ]

    def __str__(self):
        return f"{self.fiche} - Q{self.ordre}"
