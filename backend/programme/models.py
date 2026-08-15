from django.db import models


class Module(models.Model):
    """
    Chapitre pédagogique officiel (programme MINESEC, approche par compétences) :
    une unité rattachée à une "famille de situations" de la vie courante, avec son
    propre crédit horaire, déclinée séparément par série lorsque le programme les
    distingue. Alimenté par une extraction manuelle des programmes officiels (voir
    programme/fixtures/programme_officiel_cm_maths.json et la commande
    load_programme_officiel) - pas de source API, ces documents ne sont publiés
    qu'en PDF/Word.

    Rattaché à `Cursus` (pas à un `Series`/`Examen` direct) pour englober le cas
    BEPC : un seul Cursus (series=None) mais 4 classes distinctes (6e à 3e), d'où le
    champ `classe` à part - la relation structurante pour retrouver le contenu
    (Lesson.cursus, CompetenceItem.cursus, etc.) reste `cursus`, `classe` n'est
    qu'informatif pour l'affichage/tri.

    M2M vers Cursus (pas une FK) : le programme groupe parfois plusieurs séries sous
    un seul module (ex: "C-E" au lycée scientifique) alors qu'edukora garde C et E
    comme deux Series distinctes - même raisonnement que SUBJECT_FAMILIES dans
    catalog.models pour Physique/Chimie.
    """

    subject = models.ForeignKey("catalog.Subject", on_delete=models.PROTECT, related_name="modules_officiels")
    cursus = models.ManyToManyField(
        "catalog.Cursus", blank=True, related_name="modules_officiels",
        help_text="Vide pour une classe sans examen national (ex: 2nde) - le module reste dans le référentiel mais n'est rattaché à aucun contenu edukora pour l'instant.",
    )
    classe = models.CharField(
        max_length=10, blank=True,
        help_text="6e, 5e, 4e, 3e, 2nde, 1ère, Tle - descriptif seulement (distingue les classes d'un même Cursus BEPC). La relation structurante reste `cursus`.",
    )
    serie_label = models.CharField(
        max_length=20, blank=True,
        help_text=(
            "Libellé de série tel qu'écrit dans le programme source (\"C-E\", \"D\", \"TI\"...), "
            "vide pour le BEPC. Sert de discriminant : chaque série repart de son propre "
            "numéro de module au sein d'une classe (ex : 1ère D et 1ère C-E ont toutes deux "
            "un \"Module 21\") - `numero` seul ne suffit donc pas à identifier un module."
        ),
    )
    numero = models.CharField(max_length=10, help_text="Numéro officiel du module dans le programme (ex : \"25\").")
    titre = models.CharField(max_length=255)
    credit_heures = models.PositiveIntegerField(null=True, blank=True)
    famille_situations = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre"]
        constraints = [
            models.UniqueConstraint(fields=["subject", "classe", "serie_label", "numero"], name="unique_module_officiel"),
        ]

    def __str__(self):
        classe_label = f"{self.classe} {self.serie_label}".strip()
        return f"{classe_label} - Module {self.numero} : {self.titre}"


class Savoir(models.Model):
    """
    Sous-thème mathématique classique (ex : "Suites numériques") à l'intérieur d'un
    Module - le grain auquel `catalog.Tag` se rattache (voir Tag.savoir_officiel).
    `numero` vide pour les rares modules à un seul savoir : le programme source ne
    numérote (I., II., ...) que lorsqu'il y a plusieurs items à énumérer.
    """

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="savoirs")
    numero = models.CharField(max_length=10, blank=True)
    intitule = models.CharField(max_length=255)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.numero}. {self.intitule}" if self.numero else self.intitule
