import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# "La courbe ci-contre...", "le tableau ci-dessous..." : renvoi explicite à une figure
# supposée visible - voir Question.references_missing_figure.
_MISSING_FIGURE_REFERENCE_RE = re.compile(r"\bci[- ]contre\b|\bci[- ]dessous\b|\bci[- ]apr[eè]s\b", re.IGNORECASE)
_IMAGE_PLACEHOLDER_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")


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


class TypeReponse(models.TextChoices):
    OUVERTE = "OUVERTE", "Réponse ouverte (auto-évaluation)"
    QCM = "QCM", "Choix multiple (correction automatique)"


class NatureEpreuve(models.TextChoices):
    """
    Nature de l'épreuve (théorique/pratique), indépendante de la discipline (Subject) -
    ex : "Physique" + Théorique, "Physique" + Pratique, "Chimie" + Pratique. Générique,
    pas spécifique à la Physique-Chimie : n'importe quelle matière future à double
    épreuve peut réutiliser ce même champ sans code supplémentaire. Vide (pas de choix)
    pour toute épreuve où cette distinction n'existe pas ou n'est pas déterminable -
    voir Lesson.nature_epreuve, jamais deviné à l'ingestion.
    """

    THEORIQUE = "THEORIQUE", "Théorique"
    PRATIQUE = "PRATIQUE", "Pratique"


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


# Familles de Subject.code "combinables" pour une même épreuve : quand une épreuve
# mélange plusieurs disciplines d'une même famille (ex. exercices de Physique et de
# Chimie au sein d'un même sujet, épreuve historique jamais séparée en deux copies),
# elle est classée sous le code combiné plutôt que fragmentée en plusieurs Lesson -
# voir catalog.ingestion._subject_family_codes (résolution/promotion à l'ingestion) et
# catalog.views.LessonListView (paramètre ?discipline=, recherche "contient X" par
# opposition à ?subject= qui reste une correspondance exacte). Vit ici (pas dans
# ingestion.py) pour rester importable par le code de lecture (API) sans tirer les
# dépendances lourdes du module d'ingestion. Seule famille aujourd'hui ; une future
# matière composite ajouterait sa propre entrée plutôt que de généraliser un mécanisme
# encore jamais rencontré pour un autre couple de matières.
SUBJECT_FAMILIES = {
    "PHYSIQUE": "PHYSIQUE_CHIMIE",
    "CHIMIE": "PHYSIQUE_CHIMIE",
}


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
    actif = models.BooleanField(
        default=True,
        help_text=(
            "Décoche pour retirer entièrement ce pays du frontend (catalogue, cours, "
            "quiz, sitemap) sans supprimer ses données ni bloquer son ingestion - "
            "utile pour préparer un pays avant son lancement public, ou le retirer "
            "temporairement. L'ingestion (catalog.ingestion) ne consulte jamais ce "
            "champ : elle continue d'accepter du contenu pour un pays désactivé."
        ),
    )

    class Meta:
        ordering = ["label"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.label


class ExamenLabel(models.Model):
    """
    Nom réellement affiché d'un niveau d'examen (Examen) pour un pays, quand il diffère
    du libellé générique - ex : le Sénégal appelle son BEPC "BFEM". Examen reste un code
    interne fixe et partagé (stable pour l'ingestion et la logique métier, voir
    catalog.ingestion.EXAMEN_MAP) ; cette table ne fait que l'habiller différemment
    selon le pays. Absence de ligne pour un (country, examen) -> on retombe sur le
    libellé générique de Examen.choices - voir resolve_examen_label().
    """

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="examen_labels")
    examen = models.CharField(max_length=20, choices=Examen.choices)
    label = models.CharField(max_length=100, help_text="Ex : BFEM (pour le Sénégal, examen=BEPC).")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "examen"], name="unique_examen_label_par_pays"),
        ]
        ordering = ["country", "examen"]

    def __str__(self):
        return f"{self.country} - {self.get_examen_display()} -> {self.label}"


def resolve_examen_label(country, examen_code):
    """
    Nom affiché de l'examen pour ce pays : l'override de ExamenLabel s'il existe, sinon
    le libellé générique (Examen.choices). Partagé par Cursus/ExamSession/Lesson plutôt
    que dupliqué, pour qu'un seul endroit résolve cette règle.
    """
    override = ExamenLabel.objects.filter(country=country, examen=examen_code).values_list("label", flat=True).first()
    return override or dict(Examen.choices).get(examen_code, examen_code)


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
            return f"{self.display_examen()} - {self.series}"
        return self.display_examen()

    def display_examen(self):
        return resolve_examen_label(self.country, self.examen)

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
        return f"{self.display_examen()} {self.annee} ({self.country}) - {self.date_debut:%d/%m/%Y}"

    def display_examen(self):
        return resolve_examen_label(self.country, self.examen)

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
    savoir_officiel = models.ForeignKey(
        "programme.Savoir", null=True, blank=True, on_delete=models.SET_NULL, related_name="tags",
        help_text=(
            "Rattachement au référentiel programme officiel (voir programme.Savoir) - "
            "additif et rempli progressivement, rien ne dépend de ce champ pour "
            "fonctionner. Le vocabulaire Tag reste plus fin qu'un Savoir (plusieurs "
            "tags par savoir) : ce n'est pas un remplacement, juste un regroupement "
            "pédagogique par-dessus."
        ),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VisibleQuerySet(models.QuerySet):
    """QuerySet partagé par Lesson et Cours : `.visibles()` filtre à la fois le statut
    de validation et le pays d'origine, via `subject.country` - le seul chemin
    toujours renseigné et non-ambigu vers Country (contrairement à `cursus.country`,
    vide pour un Cours "toutes séries" et jamais garanti identique à celui du sujet).
    Point d'entrée unique à utiliser dans toute vue publique (catalogue, détail, quiz,
    sitemap) : un pays désactivé (`Country.actif=False`) doit disparaître de la
    plateforme sans que son contenu soit supprimé ni bloqué à l'ingestion, qui ne
    consulte jamais ce champ.
    """

    def visibles(self):
        return self.filter(statut=StatutContenu.VALIDE, subject__country__actif=True)

    def par_slug_ou_id(self, value):
        """
        Accepte soit le slug (URL publique, "/epreuves/<slug>/lire", "/cours/<slug>/lire"),
        soit l'id numérique - compat historique pour les liens pas encore migrés vers un
        slug (QuizSessionPage.tsx, construit depuis Question.lesson_id sur d'anciennes
        sessions de quiz pré-bascule vers CompetenceItem, qui n'a pas de lesson_id ; et
        tout marqueur [COURS_LINK:<id>]/COURS_REF:<id> déjà figé dans un content_markdown
        compilé avant l'introduction de Cours.slug).
        """
        return self.filter(pk=value) if str(value).isdigit() else self.filter(slug=value)


def generate_unique_slug(model_cls, title, existing_pk=None):
    """
    Slug lisible (SEO, partage) dérivé du titre, unique dans `model_cls` - un simple
    id numérique dans l'URL ("/epreuves/723/lire") ne dit rien du contenu et n'incite
    pas au partage. `existing_pk` exclut l'objet en cours d'enregistrement de la
    vérification d'unicité (mise à jour) ; None (objet pas encore créé) ne fausse rien
    ici, exclude(pk=None) équivaut à "pk IS NOT NULL", donc à aucune exclusion réelle.

    Pas préfixé d'un underscore malgré son usage historique interne à ce module :
    utilitaire pur (ne dépend que du `model_cls` passé en argument), désormais
    partagé avec inedit.models.EpreuveInedite - voir sa docstring de champ slug.
    """
    base = slugify(title) or "contenu"
    slug = base
    counter = 2
    while model_cls.objects.filter(slug=slug).exclude(pk=existing_pk).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


class Lesson(models.Model):
    """Le produit vendable : une ligne = un contenu lu en ligne par les abonnés."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, blank=True,
        help_text="Généré automatiquement depuis le titre à la création - ne pas modifier après publication.",
    )
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="lessons")
    objects = VisibleQuerySet.as_manager()
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
    nature_epreuve = models.CharField(
        max_length=10, choices=NatureEpreuve.choices, blank=True,
        help_text=(
            "Théorique/Pratique quand l'épreuve source le précise (ex : Physique "
            "pratique au BAC C) - vide si cette distinction n'existe pas pour cette "
            "matière ou n'est pas déterminable, jamais deviné à l'ingestion."
        ),
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

    est_vitrine = models.BooleanField(
        default=False,
        help_text=(
            "Corrigé complet en accès libre, sans abonnement ni connexion - pour qu'un "
            "visiteur juge la qualité réelle avant de payer. À réserver à une épreuve par "
            "cursus, choisie à la main : rien n'empêche techniquement d'en cocher plusieurs."
        ),
    )

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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Lesson, self.title, existing_pk=self.pk)
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = [*update_fields, "slug"]
        super().save(*args, **kwargs)

    def header_info(self):
        """
        Métadonnées d'identification (matière/série/examen/année/durée/coefficient)
        destinées à l'en-tête affiché par le frontend - jamais insérées dans
        content_markdown. Construites depuis les champs structurés plutôt que
        depuis du texte généré par l'IA (peu fiable : correction-experte peut
        l'omettre ou changer sa mise en forme selon les sessions).
        """
        cursus_list = list(self.cursus.select_related("series", "country").all())
        series_codes = [c.series.code for c in cursus_list if c.series]
        # display_examen() plutôt que Examen.choices brut : un même code interne (ex.
        # BEPC) peut s'appeler différemment selon le pays - voir ExamenLabel.
        examen_display = " / ".join(sorted({c.display_examen() for c in cursus_list})) or None

        return {
            "matiere": self.subject.label,
            "serie": _join_fr(series_codes) or None,
            "examen": examen_display,
            "annee": self.year,
            "duree": self.duree_epreuve or None,
            "coefficient": self.coefficient or None,
            "origine": self.get_origine_display() if self.origine != Origine.OFFICIEL else None,
            "etablissement": self.etablissement or None,
            "nature": self.get_nature_epreuve_display() if self.nature_epreuve else None,
            # Depuis Subject.country plutôt que cursus_list : toujours renseigné (FK
            # obligatoire), contrairement à cursus qui peut être vide pour un Cours
            # "toutes séries" - source fiable unique pour indiquer le pays au visiteur.
            "pays": {"code": self.subject.country.code, "label": self.subject.country.label},
        }

    def preview_markdown(self):
        """Contenu public (non-abonné) - voir catalog.rendering.lesson_preview_markdown."""
        from . import rendering

        return rendering.lesson_preview_markdown(self)

    def preview_exercises(self):
        """Sujet public découpé par exercice, sans aucun corrigé - voir catalog.rendering.lesson_preview_exercises."""
        from . import rendering

        return rendering.lesson_preview_exercises(self)

    def exercises_breakdown(self):
        """Énoncé/corrigé par exercice, séparément - voir catalog.rendering.lesson_exercises_breakdown."""
        from . import rendering

        return rendering.lesson_exercises_breakdown(self)

    def compile_from_exercises(self):
        """Agrège les Exercise validés dans ce Lesson - voir catalog.rendering.compile_lesson_from_exercises."""
        from . import rendering

        rendering.compile_lesson_from_exercises(self)


class Exercise(models.Model):
    """
    Ingéré depuis la sortie JSON de la compétence correction-experte (mode automatisé),
    validé et compilé automatiquement à l'ingestion (voir catalog.ingestion). Un exercice
    = une unité ; plusieurs exercices d'une même épreuve sont compilés ensemble en un
    seul Lesson (lesson_type=CORR).

    Un exercice peut avoir plusieurs sous-questions notées indépendamment (QCM à
    plusieurs items, problème à sous-parties numérotées) - voir Question, l'unité
    atomique de correction. enonce_markdown/corrige_markdown ne sont plus saisis
    directement : ils sont compilés depuis les Question rattachées (voir
    compile_from_questions()), exactement comme Lesson.content_markdown est compilé
    depuis les Exercise validés - aucun consommateur de ces deux champs n'a besoin de
    changer, ils restent de vrais champs stockés.
    """

    numero_exercice = models.CharField(
        max_length=30,
        help_text="Ex : 1, 2, 3a - mais aussi tout autre repère utilisé par l'épreuve source (ex. 'Section III' sur certaines épreuves d'anglais), pas seulement une numérotation simple.",
    )
    points = models.CharField(max_length=20, blank=True)

    enonce_intro_markdown = models.TextField(
        blank=True,
        help_text=(
            "Préambule partagé par toutes les sous-questions (ex. consigne commune d'un "
            "QCM), affiché avant la première Question. Vide si l'exercice n'a pas de "
            "préambule propre (le cas le plus courant)."
        ),
    )
    enonce_markdown = models.TextField(
        blank=True,
        help_text="Compilé depuis les Question rattachées - voir compile_from_questions().",
    )
    corrige_markdown = models.TextField(
        blank=True,
        help_text="Compilé depuis les Question rattachées - voir compile_from_questions().",
    )

    # themes est un cumul des Question rattachées (voir compile_from_questions) -
    # difficulte_estimee, elle, n'a pas d'équivalent utile au niveau de l'exercice
    # entier (une moyenne/un max seraient arbitraires) : elle vit uniquement sur
    # Question désormais, seule granularité pertinente pour le Mode Quiz.
    themes = models.ManyToManyField(Tag, blank=True, related_name="exercises_as_theme")
    mots_cles_recherche = models.ManyToManyField(Tag, blank=True, related_name="exercises_as_keyword")
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

    def compile_from_questions(self):
        """Concatène les Question rattachées - voir catalog.rendering.compile_exercise_from_questions."""
        from . import rendering

        rendering.compile_exercise_from_questions(self)


class Question(models.Model):
    """
    Sous-question atomique d'un Exercise - unité de correction indépendante, unité de
    base pour le Mode Quiz (auto-évaluation/test de niveau). Un exercice simple (le cas
    le plus courant) a une seule Question ; un exercice à tiroirs (QCM à plusieurs
    items, problème à sous-parties numérotées) en a plusieurs - la décomposition vient
    de correction-experte, qui la connaît déjà en interne au moment de rédiger le
    corrigé (étape de segmentation), jamais reconstruite après coup par un parsing du
    texte assemblé.
    """

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="questions")
    numero = models.CharField(
        # 10 ne suffisait pas : "Présentation" (12 caractères, un item de barème récurrent
        # sur les épreuves de maths - clarté/soin de la copie, sans rapport avec une
        # sous-question numérotée) est apparu identique sur 3 lots d'épreuves distincts et
        # sans rapport (bac-c-maths-2026, bac-d-maths-2023, bepc-maths-2024-cameroun),
        # signe d'une convention réelle et récurrente plutôt que d'une coquille isolée -
        # contrairement au cas "2.2.1-2.2.2" (une fusion de sous-questions à un seul autre
        # endroit du corpus) qui avait été corrigé côté contenu plutôt que par une
        # migration. Marge conservée au-delà de 12 pour tolérer une variante similaire
        # ("Orthographe", 11) sans nouvelle migration.
        max_length=20,
        help_text="Repère au sein de l'exercice parent (ex : 1, 2, a, b) - pas forcément numero_exercice.",
    )
    ordre = models.PositiveSmallIntegerField(help_text="Ordre d'affichage/résolution au sein de l'exercice.")

    enonce_markdown = models.TextField()
    corrige_markdown = models.TextField()

    themes = models.ManyToManyField(Tag, blank=True, related_name="questions_as_theme")
    difficulte_estimee = models.CharField(max_length=10, choices=Difficulte.choices, blank=True)

    type_reponse = models.CharField(max_length=10, choices=TypeReponse.choices, default=TypeReponse.OUVERTE)
    choix = models.JSONField(
        default=list, blank=True,
        help_text="[{\"lettre\": \"a\", \"texte\": \"...\"}] si type_reponse=QCM, sinon vide.",
    )
    reponse_correcte = models.CharField(
        max_length=10, blank=True,
        help_text="Lettre correcte si type_reponse=QCM (ex : 'b'), sinon vide.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["exercise", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["exercise", "numero"], name="unique_question_par_exercice"),
        ]

    def __str__(self):
        return f"{self.exercise} - Q{self.numero}"

    @property
    def references_missing_figure(self):
        """
        True si l'énoncé renvoie explicitement à une figure ("la courbe ci-contre",
        "le tableau ci-dessous"...) sans qu'aucune image ne soit réellement attachée -
        ni dans son propre enonce_markdown, ni dans enonce_intro_markdown de son
        Exercise (où une figure partagée par plusieurs sous-questions peut vivre).
        Repéré en production : une sous-question ainsi mal formée pose une question de
        lecture de graphique littéralement insoluble, faute d'extraction de la figure
        source par correction-experte - à exclure du Quiz (voir
        quiz.services._questions_eligibles), où elle serait servie seule, hors du
        contexte de l'exercice complet où elle reste au moins visible dans la Lesson.
        """
        text = f"{self.exercise.enonce_intro_markdown}\n\n{self.enonce_markdown}"
        if not _MISSING_FIGURE_REFERENCE_RE.search(text):
            return False
        return not _IMAGE_PLACEHOLDER_RE.search(text)


class OrigineFigure(models.TextChoices):
    ENONCE = "ENONCE", "Énoncé"
    CORRIGE = "CORRIGE", "Corrigé"


def figure_upload_to(instance, filename):
    """
    Préfixé par le code pays (même convention que sujets_pdf/<code_pays>/... - voir
    catalog.sujet_pdf.sujet_pdf_filename) : sans lui, le nom de fichier original
    (souvent générique, ex. "figure1.png", livré tel quel par correction-experte -
    voir catalog.ingestion._attach_figures) peut coïncider entre deux pays pour une
    figure sans rapport, le second écrasant alors silencieusement l'image du premier
    dans le dossier plat figures/. N'affecte que les figures ingérées à partir de
    maintenant ; celles déjà stockées (chemin plat historique) ne sont pas migrées -
    même choix déjà fait pour les PDF de sujet.
    """
    country_code = instance.exercise.lesson.subject.country.code.lower()
    return f"figures/{country_code}/{filename}"


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
        max_length=255,
        help_text="Identifiant du placeholder dans le Markdown (ex: fig-1) - unique seulement au sein d'un exercice.",
    )
    image = models.FileField(upload_to=figure_upload_to)
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
    objects = VisibleQuerySet.as_manager()

    titre = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, blank=True,
        help_text="Généré automatiquement depuis le titre à la création - ne pas modifier après publication.",
    )
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Cours, self.titre, existing_pk=self.pk)
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = [*update_fields, "slug"]
        super().save(*args, **kwargs)

    def header_info(self):
        series_codes = [c.series.code for c in self.cursus.select_related("series").all() if c.series]
        return {
            "matiere": self.subject.label,
            "serie": _join_fr(series_codes) or None,
            "sous_theme": self.sous_theme or None,
            "duree_estimee_min": self.duree_estimee_min,
            "pays": {"code": self.subject.country.code, "label": self.subject.country.label},
        }

    def _render_section(self, section):
        """Rend une section de sections_raw - voir catalog.rendering._render_cours_section."""
        from . import rendering

        return rendering._render_cours_section(self, section)

    def compile_from_sections(self):
        """Aplatit sections_raw en Markdown affichable - voir catalog.rendering.compile_cours_from_sections."""
        from . import rendering

        rendering.compile_cours_from_sections(self)

    def preview_markdown(self):
        """Aperçu public (non-abonné) - voir catalog.rendering.cours_preview_markdown."""
        from . import rendering

        return rendering.cours_preview_markdown(self)

    def sections_breakdown(self, allowed_types=None):
        """Sections individuellement typées, pour la lecture en ligne - voir catalog.rendering.cours_sections_breakdown."""
        from . import rendering

        return rendering.cours_sections_breakdown(self, allowed_types=allowed_types)


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


class TemoignageQuerySet(models.QuerySet):
    def publies(self):
        return self.filter(est_publie=True)


class Temoignage(models.Model):
    """
    Avis d'un élève, saisi et publié à la main depuis l'admin - jamais généré ni
    déduit automatiquement (voir l'audit UX, reco 8.3 : preuve sociale réelle ou
    absente, jamais fabriquée). `est_publie` par défaut à False : un témoignage
    récolté (ex. par message) reste invisible du public tant qu'un admin ne l'a pas
    relu et publié explicitement - même logique que Country.actif pour seed_country.
    """

    auteur_nom = models.CharField(max_length=100)
    auteur_description = models.CharField(
        max_length=150, blank=True,
        help_text="Ex : « Terminale D, Cameroun » ou « Bachelière 2025 » - jamais de numéro de téléphone ni d'identifiant.",
    )
    contenu = models.TextField(max_length=600)
    note = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Note sur 5, optionnelle - laisser vide si le témoignage n'en comporte pas.",
    )
    est_publie = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TemoignageQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.auteur_nom} ({'publié' if self.est_publie else 'brouillon'})"

    def clean(self):
        if self.note is not None and not (1 <= self.note <= 5):
            raise ValidationError({"note": "La note doit être comprise entre 1 et 5."})
