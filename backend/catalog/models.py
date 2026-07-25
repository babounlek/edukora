import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# correction-experte ouvre CHAQUE corrigé d'exercice par une "fiche d'identité"
# (matière/série/examen/année) - pertinent quand un exercice est traité seul, mais
# redondant une fois plusieurs exercices d'une même épreuve fusionnés en un Lesson.
# On n'en garde qu'une seule occurrence, juste après le titre. Deux formats observés
# selon les sessions de la compétence : bloc de code, ou tableau Markdown.
_FICHE_IDENTITE_RE = re.compile(r"```\nMatière\s*:.*?```\n*(?:---\n*)?", re.DOTALL)
_FICHE_IDENTITE_TABLE_RE = re.compile(r"##\s*Fiche d['’]identité\s*\n+(?:\|.*\|\n)+\n*(?:---\n*)?")

# corrige_markdown répète aussi "## Exercice N" en tête (déjà porté par le titre qu'on
# injecte nous-mêmes) - on la retire pour ne garder qu'un simple séparateur de section.
_EXERCICE_HEADING_RE = re.compile(r"^##\s*Exercice\s+\S+[^\n]*\n+", re.IGNORECASE)

# Isole chaque bloc "### Rappel de méthode" (un exercice peut en contenir plusieurs,
# un par sous-question) pour y injecter un marqueur [COURS_LINK:id] quand ce rappel a
# donné naissance à un Cours - voir Lesson._annotate_cours_links.
_RAPPEL_BLOCK_RE = re.compile(r"###\s*Rappel de méthode\s*\n+.*?(?=\n#{1,6}[ \t]|\n---|\Z)", re.IGNORECASE | re.DOTALL)

# Marqueur de secours que correction-experte ajoute quand un rappel_de_methode ne peut
# pas être fait à correspondre verbatim au corrigé (voir SKILL.md) - la publication étant
# désormais automatique (aucune relecture humaine), on le retire par sécurité pour ne
# jamais l'exposer tel quel à un élève si un moteur de rendu venait à afficher les
# commentaires HTML.
_RAPPEL_ORPHELIN_RE = re.compile(r"<!--\s*RAPPEL_NON_APPARIE\s*:.*?-->\n*", re.IGNORECASE | re.DOTALL)


def _join_fr(items):
    """Joint des éléments à la française : "C", "C et E", "C, D et E" - pour ne pas
    répéter le diplôme quand une épreuve concerne plusieurs séries (ex: "BAC C et E")."""
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return " et ".join(items)
    return f"{', '.join(items[:-1])} et {items[-1]}"


class Examen(models.TextChoices):
    BEPC = "BEPC", "BEPC"
    PROBATOIRE = "PROBATOIRE", "Probatoire"
    BAC = "BAC", "BAC"
    AUTRE = "AUTRE", "Devoir surveillé / Autre"


class Origine(models.TextChoices):
    """
    Nature de l'épreuve, indépendante de son niveau (Examen) : un examen blanc ou une
    épreuve d'établissement cible quand même un (examen, série) existant - "BAC C blanc"
    reste BAC C - donc ce n'est pas une variante d'Examen mais un attribut à part, utile
    pour rester transparent avec l'élève (sujet officiel vs. maison) et pour filtrer.
    """

    OFFICIEL = "OFFICIEL", "Sujet officiel"
    BLANC = "BLANC", "Examen blanc"
    ETABLISSEMENT = "ETABLISSEMENT", "Épreuve d'établissement"
    AUTRE = "AUTRE", "Autre"


class Difficulte(models.TextChoices):
    FAIBLE = "FAIBLE", "Faible"
    MOYENNE = "MOYENNE", "Moyenne"
    ELEVEE = "ELEVEE", "Élevée"


class StatutContenu(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon"
    VALIDE = "VALIDE", "Validé"
    REJETE = "REJETE", "Rejeté"


class LessonType(models.TextChoices):
    FICHE = "FICHE", "Fiche de révision"
    CORR = "CORR", "Corrigé d'annale"
    SUJET = "SUJET", "Sujet inédit"


class Subject(models.Model):
    """
    Référentiel des matières. Table dédiée pour accueillir plus tard icône/couleur/
    coefficient. Rattaché à Country : un intitulé ou une liste de matières peut
    différer d'un pays à l'autre (voir Series pour le même raisonnement).
    """

    country = models.ForeignKey("Country", on_delete=models.PROTECT, related_name="subjects")
    code = models.CharField(max_length=20)
    label = models.CharField(max_length=100)

    class Meta:
        ordering = ["label"]
        constraints = [
            models.UniqueConstraint(fields=["country", "code"], name="unique_subject_par_pays"),
        ]

    def __str__(self):
        return self.label


class Series(models.Model):
    """
    Référentiel des séries (A, SES, C, D, E, TI, COM). Rattaché à Country : rien ne
    garantit qu'un code de série désigne la même chose (ni même qu'il existe) d'un
    pays à l'autre du système éducatif francophone - voir Cursus.clean() qui vérifie
    la cohérence (country, series.country).
    """

    country = models.ForeignKey("Country", on_delete=models.PROTECT, related_name="series_set")
    code = models.CharField(max_length=10)
    label = models.CharField(max_length=100)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "séries"
        constraints = [
            models.UniqueConstraint(fields=["country", "code"], name="unique_series_par_pays"),
        ]

    def __str__(self):
        return f"Série {self.code} ({self.label})"


class Country(models.Model):
    """
    Référentiel des pays. La plateforme ne sert aujourd'hui que le Cameroun, mais
    Examen/Series/le contenu de correction-experte sont spécifiques au système scolaire
    d'un pays donné : rattacher Cursus à un Country dès maintenant évite une migration
    de données plus tard si la plateforme s'étend à un autre pays (voir Cursus).
    """

    code = models.CharField(max_length=10, unique=True)
    label = models.CharField(max_length=100)
    dial_code = models.CharField(
        max_length=5, blank=True,
        help_text="Indicatif téléphonique international, sans le + (ex : 237).",
    )
    currency = models.CharField(
        max_length=3, blank=True,
        help_text=(
            "Code devise ISO 4217 (ex : XAF). Donnée seule pour l'instant - aucun code "
            "ne s'en sert encore : le paiement (Campay) ne gère que le Cameroun."
        ),
    )

    class Meta:
        ordering = ["label"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.label


class Cursus(models.Model):
    """
    Combinaison valide (pays, examen, série) d'un système scolaire donné.
    Référentiel figé : sert à empêcher des associations impossibles
    (ex: examen=BEPC avec une série, qui n'existe pas en cycle collège).
    """

    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cursus_set")
    examen = models.CharField(max_length=20, choices=Examen.choices)
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.PROTECT, related_name="cursus_set")

    class Meta:
        verbose_name_plural = "cursus"
        constraints = [
            models.UniqueConstraint(fields=["country", "examen", "series"], name="unique_cursus_combo"),
        ]
        ordering = ["country", "examen", "series"]

    def __str__(self):
        if self.series:
            return f"{self.get_examen_display()} - {self.series}"
        return self.get_examen_display()

    def clean(self):
        """
        Series est maintenant rattachée à un Country (voir Series) : rien n'empêche
        au niveau des FK de lier un Cursus à la Series d'un AUTRE pays que le sien -
        vérifié ici plutôt que par une contrainte SQL (impossible à exprimer proprement
        entre deux FK dans une UniqueConstraint/CheckConstraint standard).
        """
        if self.series_id and self.country_id and self.series.country_id != self.country_id:
            raise ValidationError("La série doit appartenir au même pays que le cursus.")


class ExamSession(models.Model):
    """
    Date de démarrage d'une session d'examen (BEPC/Probatoire/BAC) pour un pays et une
    année donnés - saisie manuellement par un administrateur à partir du calendrier
    officiel (ex. MINESEC au Cameroun), jamais déduite ni devinée : ces dates changent
    chaque année et ne sont publiées qu'à l'approche de la session. Sert de base au
    Plan "jusqu'à l'examen" (voir subscriptions.models.Plan.effective_duration_days).
    """

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="exam_sessions")
    examen = models.CharField(max_length=20, choices=Examen.choices)
    annee = models.PositiveSmallIntegerField()
    date_debut = models.DateField(help_text="Premier jour de la session d'examen (calendrier officiel).")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "examen", "annee"], name="unique_exam_session"),
        ]
        ordering = ["annee", "examen"]

    def __str__(self):
        return f"{self.get_examen_display()} {self.annee} ({self.country}) - {self.date_debut:%d/%m/%Y}"

    @classmethod
    def prochaine_pour(cls, country, examen):
        """La prochaine session à venir (date_debut future ou aujourd'hui) pour ce (pays, examen), ou None."""
        return (
            cls.objects.filter(country=country, examen=examen, date_debut__gte=timezone.now().date())
            .order_by("date_debut")
            .first()
        )


class Tag(models.Model):
    """Vocabulaire partagé pour les thèmes pédagogiques et les mots-clés de recherche."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """Le produit vendable : une ligne = un contenu lu en ligne par les abonnés."""

    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="lessons")
    cursus = models.ManyToManyField(
        Cursus, related_name="lessons",
        help_text="Plusieurs cursus si l'épreuve est commune à plusieurs séries (ex: Maths BAC C/E).",
    )
    lesson_type = models.CharField(max_length=10, choices=LessonType.choices)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    epreuve_source = models.CharField(
        max_length=255, blank=True,
        help_text="Nom du fichier PDF d'origine (CORR uniquement, vide pour FICHE/SUJET).",
    )
    origine = models.CharField(
        max_length=20, choices=Origine.choices, default=Origine.OFFICIEL,
        help_text="Sujet officiel, examen blanc ou épreuve d'établissement.",
    )
    etablissement = models.CharField(
        max_length=255, blank=True,
        help_text="Nom de l'établissement (ORIGINE=ETABLISSEMENT uniquement).",
    )

    themes = models.ManyToManyField(Tag, blank=True, related_name="lessons_as_theme")
    mots_cles_recherche = models.ManyToManyField(Tag, blank=True, related_name="lessons_as_keyword")

    content_markdown = models.TextField(
        blank=True,
        help_text=(
            "Source Markdown rendue en lecture en ligne. "
            "Rédigée directement pour FICHE/SUJET, ou compilée depuis les Exercise validés pour CORR."
        ),
    )

    duree_epreuve = models.CharField(
        max_length=50, blank=True,
        help_text="Ex : 4h. Affiché dans l'en-tête, jamais dans le corps du contenu.",
    )
    coefficient = models.CharField(
        max_length=20, blank=True,
        help_text="Ex : 7. Affiché dans l'en-tête, jamais dans le corps du contenu.",
    )

    statut = models.CharField(max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON)
    published_at = models.DateTimeField(null=True, blank=True)

    sujet_pdf = models.FileField(
        upload_to="sujets_pdf/", blank=True,
        help_text=(
            "PDF brandé du sujet (énoncés uniquement, jamais le corrigé) - support "
            "marketing librement partageable. Généré hors ligne, jamais à la volée : "
            "voir la commande `generate_sujet_pdfs` ou l'action admin correspondante."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "title"]
        indexes = [
            models.Index(fields=["subject", "lesson_type"]),
        ]

    def __str__(self):
        return self.title

    def header_info(self):
        """
        Métadonnées d'identification (matière/série/examen/année/durée/coefficient)
        destinées à l'en-tête affiché par le frontend - jamais insérées dans
        content_markdown. Construites depuis les champs structurés plutôt que
        depuis du texte généré par l'IA (peu fiable : correction-experte peut
        l'omettre ou changer sa mise en forme selon les sessions).
        """
        series_codes = [c.series.code for c in self.cursus.select_related("series").all() if c.series]
        examens = sorted({c.examen for c in self.cursus.all()})
        examen_display = " / ".join(dict(Examen.choices).get(e, e) for e in examens) or None

        return {
            "matiere": self.subject.label,
            "serie": _join_fr(series_codes) or None,
            "examen": examen_display,
            "annee": self.year,
            "duree": self.duree_epreuve or None,
            "coefficient": self.coefficient or None,
            "origine": self.get_origine_display() if self.origine != Origine.OFFICIEL else None,
            "etablissement": self.etablissement or None,
        }

    @staticmethod
    def _annotate_cours_links(corrige, exercise):
        """
        Insère un marqueur `[COURS_LINK:<id>]` juste après chaque bloc "### Rappel de
        méthode" dont le RappelDeMethode correspondant a donné naissance à un Cours -
        le frontend le détecte pour afficher un lien "Voir le cours complet" sur le
        callout. La correspondance entre un bloc du texte et son RappelDeMethode se
        fait par inclusion du texte exact extrait à l'ingestion (contenu_markdown),
        seule donnée fiable puisque le Markdown compilé ne porte pas de FK.

        Un même bloc peut correspondre à plusieurs RappelDeMethode : la compétence
        fusionne parfois plusieurs sous-questions sous un unique "### Rappel de méthode"
        plutôt que d'en écrire un par sous-question - dans ce cas tous les cours
        associés sont insérés à la suite du bloc.

        Il arrive aussi que `contenu_markdown` soit une reformulation plutôt qu'une
        citation exacte du corrigé (l'IA ne respecte pas toujours cette consigne) : le
        rappel ne matche alors aucun bloc. Son marqueur est ajouté en fin d'exercice
        plutôt que d'être perdu silencieusement - imprécis, mais le lien reste visible.
        """
        rappels = [r for r in exercise.rappels_de_methode.all() if r.cours_id and r.contenu_markdown.strip()]
        if not rappels:
            return corrige

        injected_ids = set()

        def _inject(match):
            block = match.group(0)
            cours_ids = [r.cours_id for r in rappels if r.contenu_markdown.strip() in block]
            if not cours_ids:
                return block
            injected_ids.update(cours_ids)
            markers = "\n\n".join(f"[COURS_LINK:{cid}]" for cid in cours_ids)
            # Le lookahead de _RAPPEL_BLOCK_RE ne consomme qu'un seul \n avant la
            # frontière suivante (### / ---) : la ligne blanche d'origine perd donc une
            # de ses deux newlines dans le texte restant non capturé. Sans ce \n final,
            # un "---" juste après transformerait le marqueur en titre Setext (<h2>)
            # au lieu de rester un simple paragraphe.
            return f"{block.rstrip()}\n\n{markers}\n"

        corrige = _RAPPEL_BLOCK_RE.sub(_inject, corrige)

        remaining_ids = [r.cours_id for r in rappels if r.cours_id not in injected_ids]
        if remaining_ids:
            markers = "\n\n".join(f"[COURS_LINK:{cid}]" for cid in remaining_ids)
            corrige = f"{corrige.rstrip()}\n\n{markers}"

        return corrige

    @classmethod
    def _render_exercise_block(cls, exercise):
        """
        Rend un Exercise validé en bloc Markdown autonome (énoncé + corrigé nettoyé),
        partagé par compile_from_exercises() et preview_markdown(). Pas de "## Exercice
        N" injecté ici : enonce_markdown porte déjà cette numérotation lui-même (ex.
        "**Exercice 1 (5 points).**"), telle que transcrite depuis l'épreuve source -
        l'ajouter en plus produirait un doublon visible.
        """
        # Si l'IA a quand même inclus une fiche d'identité par exercice (ancien format
        # bloc de code, ou nouveau format tableau - oubli de consigne dans les deux cas),
        # on la retire : ces informations vivent uniquement dans header_info().
        corrige = _FICHE_IDENTITE_RE.sub("", exercise.corrige_markdown, count=1).lstrip()
        corrige = _FICHE_IDENTITE_TABLE_RE.sub("", corrige, count=1).lstrip()
        corrige = _EXERCICE_HEADING_RE.sub("### Corrigé\n\n", corrige, count=1)
        corrige = _RAPPEL_ORPHELIN_RE.sub("", corrige)
        corrige = cls._annotate_cours_links(corrige, exercise)
        return f"{exercise.enonce_markdown}\n\n{corrige}"

    def preview_markdown(self):
        """
        Contenu public (non-abonné, identique connecté ou non) : l'énoncé complet de
        CHAQUE exercice - l'équivalent d'un sujet d'épreuve non corrigé, mis à
        disposition gratuitement. Le corrigé (rappel de méthode, résolution, piège,
        conseil) reste toujours réservé aux abonnés, quel que soit le nombre
        d'exercices - ce n'est plus un aperçu partiel mais le sujet dans son entier.

        Pour une FICHE/SUJET non sectionnée (sans Exercise du tout), le contenu
        n'a pas de séparation énoncé/corrigé : il reste montré tel quel.
        """
        exercises = self.exercises.filter(statut=StatutContenu.VALIDE).order_by("numero_exercice")
        if not exercises.exists():
            return self.content_markdown

        blocs = [exercise.enonce_markdown for exercise in exercises]
        return "\n\n---\n\n".join(blocs)

    def compile_from_exercises(self):
        """
        Agrège les Exercise validés (rattachés via leur FK) dans ce Lesson :
        concatène le contenu Markdown et fusionne thèmes/mots-clés sans doublon.
        N'inclut jamais un Exercise encore en BROUILLON ou REJETE.
        """
        exercises = (
            self.exercises.filter(statut=StatutContenu.VALIDE)
            .order_by("numero_exercice")
            .prefetch_related("themes", "mots_cles_recherche", "rappels_de_methode")
        )

        blocs = []
        themes = set(self.themes.all())
        mots_cles = set(self.mots_cles_recherche.all())

        for exercise in exercises:
            blocs.append(self._render_exercise_block(exercise))
            themes.update(exercise.themes.all())
            mots_cles.update(exercise.mots_cles_recherche.all())

        self.content_markdown = "\n\n---\n\n".join(blocs)
        self.save(update_fields=["content_markdown", "updated_at"])
        self.themes.set(themes)
        self.mots_cles_recherche.set(mots_cles)


class Exercise(models.Model):
    """
    Ingéré depuis la sortie JSON de la compétence correction-experte (mode automatisé),
    validé et compilé automatiquement à l'ingestion (voir catalog.ingestion). Un exercice
    = une unité ; plusieurs exercices d'une même épreuve sont compilés ensemble en un
    seul Lesson (lesson_type=CORR).
    """

    numero_exercice = models.CharField(
        max_length=30,
        help_text="Ex : 1, 2, 3a - mais aussi tout autre repère utilisé par l'épreuve source (ex. 'Section III' sur certaines épreuves d'anglais), pas seulement une numérotation simple.",
    )
    points = models.CharField(max_length=20, blank=True)

    enonce_markdown = models.TextField()
    corrige_markdown = models.TextField()

    themes = models.ManyToManyField(Tag, blank=True, related_name="exercises_as_theme")
    mots_cles_recherche = models.ManyToManyField(Tag, blank=True, related_name="exercises_as_keyword")
    difficulte_estimee = models.CharField(max_length=10, choices=Difficulte.choices, blank=True)
    incertitudes = models.JSONField(default=list, blank=True)

    statut = models.CharField(max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON)

    lesson = models.ForeignKey(
        Lesson, on_delete=models.PROTECT, related_name="exercises",
        help_text="Épreuve/groupe auquel appartient cet exercice, renseigné dès l'ingestion.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lesson", "numero_exercice"]
        indexes = [
            models.Index(fields=["statut"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["lesson", "numero_exercice"], name="unique_exercice_par_lesson"),
        ]

    def __str__(self):
        return f"{self.lesson.epreuve_source or self.lesson.title} - Ex. {self.numero_exercice}"


class OrigineFigure(models.TextChoices):
    ENONCE = "ENONCE", "Énoncé"
    CORRIGE = "CORRIGE", "Corrigé"


class Figure(models.Model):
    """
    Image (figure géométrique, courbe, tableau scanné, schéma...) rattachée à un
    Exercise - voir la section "Traitement des figures et images" du SKILL.md de
    correction-experte. Référencée dans enonce_markdown/corrige_markdown par un
    placeholder Markdown `![fig-N](...)` que l'ingestion réécrit vers l'URL réelle
    du fichier stocké ici (voir catalog.ingestion._attach_figures).
    """

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="figures")
    external_id = models.CharField(
        max_length=20,
        help_text="Identifiant du placeholder dans le Markdown (ex: fig-1) - unique seulement au sein d'un exercice.",
    )
    image = models.FileField(upload_to="figures/")
    page_source = models.PositiveSmallIntegerField(null=True, blank=True)
    type_figure = models.CharField(
        max_length=30, blank=True,
        help_text="Ex : figure geometrique, courbe, tableau, schema, document, carte, graphique (valeur libre, non contrainte).",
    )
    legende = models.CharField(max_length=500, blank=True)
    indispensable = models.BooleanField(default=True)
    lisibilite = models.CharField(
        max_length=10, blank=True,
        help_text="bonne / partielle / illisible (valeur libre, non contrainte).",
    )
    origine = models.CharField(max_length=10, choices=OrigineFigure.choices, default=OrigineFigure.ENONCE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["exercise", "external_id"]
        constraints = [
            models.UniqueConstraint(fields=["exercise", "external_id"], name="unique_figure_par_exercice"),
        ]

    def __str__(self):
        return f"{self.exercise} - {self.external_id}"


class Cours(models.Model):
    """
    Contenu pédagogique généré par correction-experte (mode cours) à partir d'un
    RappelDeMethode : vendu au même titre qu'un corrigé, mais organisé en 7 sections
    structurées (accroche, prérequis, règle, exemple résolu, erreurs classiques,
    exercices, synthèse) plutôt qu'en Markdown libre.
    """

    external_id = models.CharField(
        max_length=255, unique=True,
        help_text="cours_id fourni par correction-experte (ex. cours-resolution-equations-second-degre-...) - sert de clé d'idempotence.",
    )
    titre = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="cours")
    cursus = models.ManyToManyField(
        Cursus, related_name="cours", blank=True,
        help_text="Vide = notion commune à toutes les séries, accessible à tout abonné actif quel que soit son cursus.",
    )
    sous_theme = models.CharField(max_length=255, blank=True)
    duree_estimee_min = models.PositiveSmallIntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="cours")

    sections_raw = models.JSONField(
        default=list, blank=True,
        help_text="Sections structurées telles que fournies par correction-experte (mode cours), conservées pour un rendu plus riche ultérieur.",
    )
    content_markdown = models.TextField(
        blank=True,
        help_text="Rendu Markdown aplati des sections, généré par compile_from_sections().",
    )

    statut = models.CharField(max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["titre"]
        verbose_name_plural = "cours"

    def __str__(self):
        return self.titre

    def header_info(self):
        series_codes = [c.series.code for c in self.cursus.select_related("series").all() if c.series]
        return {
            "matiere": self.subject.label,
            "serie": _join_fr(series_codes) or None,
            "sous_theme": self.sous_theme or None,
            "duree_estimee_min": self.duree_estimee_min,
        }

    def _render_section(self, section):
        section_type = section.get("type")

        if section_type == "accroche":
            return section.get("contenu_markdown", "")

        if section_type == "prerequis":
            # Lie chaque prérequis au Cours correspondant quand son titre matche
            # exactement (insensible à la casse) - best-effort : un intitulé de
            # prérequis générique ("Calcul littéral") ne matchera pas toujours un
            # titre de Cours (plus spécifique), auquel cas il reste un texte simple.
            items = section.get("items") or []
            lines = []
            for item in items:
                match = (
                    Cours.objects.filter(titre__iexact=item.strip(), statut=StatutContenu.VALIDE)
                    .exclude(pk=self.pk)
                    .first()
                )
                lines.append(f"- [{item}](COURS_REF:{match.id})" if match else f"- {item}")
            return "## Prérequis\n\n" + "\n".join(lines)

        if section_type == "regle":
            parts = [f"## {section.get('titre') or 'La règle'}", section.get("contenu_markdown", "")]
            if section.get("formule_principale"):
                parts.append(f"$${section['formule_principale']}$$")
            for variante in section.get("variantes") or []:
                # correction-experte produit tantôt un objet {nom, quand_utiliser,
                # contenu_markdown}, tantôt - pour une simple variante de formule,
                # sans sous-titre ni précision d'usage - une chaîne nue de LaTeX brut
                # (ex. une règle "ln x>k" à côté de ses variantes "ln x<k", "ln x≥k"...,
                # constaté sans délimiteurs $$, comme formule_principale ci-dessus avant
                # d'être enveloppée). Les deux sont un contenu légitime de la
                # compétence, pas une erreur à rejeter.
                if isinstance(variante, str):
                    parts.append(f"$${variante}$$")
                    continue
                parts.append(f"### {variante.get('nom', '')}")
                if variante.get("quand_utiliser"):
                    parts.append(f"*Quand l'utiliser : {variante['quand_utiliser']}*")
                parts.append(variante.get("contenu_markdown", ""))
            return "\n\n".join(p for p in parts if p)

        if section_type == "exemple_resolu":
            parts = ["## Exemple résolu", section.get("enonce_markdown", "")]
            for etape in section.get("etapes") or []:
                parts.append(f"**Étape {etape.get('numero', '')} - {etape.get('action', '')}**")
                if etape.get("justification"):
                    parts.append(etape["justification"])
                if etape.get("resultat_markdown"):
                    parts.append(etape["resultat_markdown"])
            if section.get("conclusion_markdown"):
                parts.append(section["conclusion_markdown"])
            return "\n\n".join(p for p in parts if p)

        if section_type == "erreurs_classiques":
            parts = ["## Erreurs classiques"]
            for item in section.get("items") or []:
                parts.append(f"### Erreur\n\n{item.get('erreur_markdown', '')}")
                parts.append(f"### Pourquoi c'est faux\n\n{item.get('pourquoi_faux', '')}")
                parts.append(f"### Correction\n\n{item.get('correction_markdown', '')}")
            return "\n\n".join(parts)

        if section_type == "exercices_application":
            # Titre distinct de "### Corrigé" (utilisé ailleurs pour le corrigé payant
            # d'une épreuve, toujours visible) : le frontend masque spécifiquement
            # "### Solution" derrière un bouton, pour que l'élève cherche par lui-même
            # avant de voir la réponse - c'est le principe même de l'auto-évaluation.
            parts = ["## Exercices d'application"]
            for item in section.get("items") or []:
                parts.append(f"### Exercice {item.get('numero', '')} ({item.get('difficulte', '')})\n\n{item.get('enonce_markdown', '')}")
                parts.append(f"### Solution\n\n{item.get('solution_markdown', '')}")
            return "\n\n".join(parts)

        if section_type == "synthese":
            items = section.get("items_markdown") or []
            return "## Ce qu'il faut retenir\n\n" + "\n".join(f"- {item}" for item in items)

        return ""

    def compile_from_sections(self):
        """Aplatit sections_raw (fourni par correction-experte) en Markdown affichable."""
        blocs = [self._render_section(section) for section in self.sections_raw]
        self.content_markdown = "\n\n---\n\n".join(bloc for bloc in blocs if bloc)
        self.save(update_fields=["content_markdown", "updated_at"])

    def preview_markdown(self):
        """
        Aperçu public (non-abonné) : accroche + prérequis + règle seulement - assez pour
        comprendre la méthode, jamais l'exemple résolu, les erreurs classiques, les
        exercices ni la synthèse, qui restent le contenu vendu. Dérivé directement de
        sections_raw (pas d'un découpage de content_markdown déjà compilé).
        """
        allowed_types = {"accroche", "prerequis", "regle"}
        blocs = [
            self._render_section(section) for section in self.sections_raw
            if section.get("type") in allowed_types
        ]
        return "\n\n---\n\n".join(bloc for bloc in blocs if bloc)


class RappelDeMethode(models.Model):
    """
    Un bloc "### Rappel de méthode" extrait d'un Exercise par correction-experte,
    candidat à devenir un Cours indépendant (mode cours). Le lien vers le Cours
    généré est tracé dans les deux sens : cours_genere/cours_id côté sortie JSON
    de la compétence correspondent respectivement à `cours_id is not None` et
    `cours_id` ici.
    """

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="rappels_de_methode")
    external_id = models.CharField(
        max_length=255, unique=True,
        help_text="id fourni par correction-experte (ex. rdm-<epreuve>-ex<numero>-<index>) - sert de clé d'idempotence et de référence pour le mode cours.",
    )
    competence = models.CharField(max_length=255)
    contenu_markdown = models.TextField()
    cours = models.ForeignKey(Cours, null=True, blank=True, on_delete=models.SET_NULL, related_name="rappels_source")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["exercise", "external_id"]

    def __str__(self):
        return f"{self.competence} ({self.exercise})"

    @property
    def cours_genere(self):
        return self.cours_id is not None
