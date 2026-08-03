import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

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

# "La courbe ci-contre...", "le tableau ci-dessous..." : renvoi explicite à une figure
# supposée visible - voir Question.references_missing_figure.
_MISSING_FIGURE_REFERENCE_RE = re.compile(r"\bci[- ]contre\b|\bci[- ]dessous\b|\bci[- ]apr[eè]s\b", re.IGNORECASE)
_IMAGE_PLACEHOLDER_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")

# Une sous-question transcrit souvent déjà son propre repère visible telle qu'elle
# apparaît sur l'épreuve source - un titre en gras ("**Partie A**"), sa numérotation
# d'origine ("1. ", "2) "), ou une lettre suivie de ":"/"." ("A : «...»") - voir
# Exercise._render_question_enonce, qui ne préfixe le `numero` interne que si le texte
# n'affiche déjà aucun repère de ce genre, pour ne jamais doubler l'information.
_ENONCE_ALREADY_LABELED_RE = re.compile(r"^\s*(\*\*|\d+\s*[.)]\s|[A-Za-z]\s*[.):])")


def _strip_redundant_local_marker(text, numero):
    """
    Retire un marqueur local du type "(b)" en tête du texte quand il redouble
    exactement le dernier segment du `numero` complet déjà affiché en préfixe (ex.
    numero="A.3.b", texte="(b) Étudier...") - correction-experte ne recopie que la
    lettre/le chiffre local hérité de l'énoncé source, jamais le chemin complet de la
    partie, donc sans ceci le lecteur voit le même repère deux fois : une fois dans le
    préfixe compilé ("**A.3.b.**"), une fois dans le texte d'origine ("(b)").
    """
    last_segment = numero.rsplit(".", 1)[-1]
    marker_re = re.compile(rf"^\(\s*{re.escape(last_segment)}\s*\)[.:]?\s*", re.IGNORECASE)
    return marker_re.sub("", text, count=1)


def _join_fr(items):
    """Joint des éléments à la française : "C", "C et E", "C, D et E" - pour ne pas
    répéter le diplôme quand une épreuve concerne plusieurs séries (ex: "BAC C et E")."""
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return " et ".join(items)
    return f"{', '.join(items[:-1])} et {items[-1]}"


def _exercice_application_enonce(item):
    """
    Énoncé d'un exercice de la section 6 (mode cours) : soit un bloc unique
    (`enonce_markdown`), soit - pour un exercice à sous-questions - un préambule
    partagé (`enonce_intro_markdown`) suivi de l'énoncé de chaque `questions[]`, même
    convention que Exercise.compile_from_questions() côté corrigé d'épreuve.
    """
    questions = item.get("questions")
    if not questions:
        return item.get("enonce_markdown", "")
    intro = item.get("enonce_intro_markdown") or ""
    corps = "\n\n".join(q.get("enonce_markdown", "") for q in questions)
    return f"{intro}\n\n{corps}" if intro else corps


def _exercice_application_solution(item):
    """
    Solution d'un exercice de la section 6 : soit `solution_markdown` unique, soit la
    concaténation de la solution de chaque `questions[]` - `solution_markdown` et
    `corrige_markdown` acceptés au niveau sous-question (la compétence peut nommer le
    champ selon l'un ou l'autre de ses deux modes, corrigé d'épreuve vs cours)."""
    questions = item.get("questions")
    if not questions:
        return item.get("solution_markdown", "")
    return "\n\n".join(q.get("solution_markdown") or q.get("corrige_markdown", "") for q in questions)


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
        Accepte soit le slug (URL publique, "/epreuves/<slug>/lire"), soit l'id
        numérique - compat historique pour le seul lien pas encore migré vers un slug
        (QuizSessionPage.tsx, construit depuis Question.lesson_id sur d'anciennes
        sessions de quiz pré-bascule vers CompetenceItem, qui n'a pas de lesson_id).
        """
        return self.filter(pk=value) if str(value).isdigit() else self.filter(slug=value)


def _generate_unique_slug(model_cls, title, existing_pk=None):
    """
    Slug lisible (SEO, partage) dérivé du titre, unique dans `model_cls` - un simple
    id numérique dans l'URL ("/epreuves/723/lire") ne dit rien du contenu et n'incite
    pas au partage. `existing_pk` exclut l'objet en cours d'enregistrement de la
    vérification d'unicité (mise à jour) ; None (objet pas encore créé) ne fausse rien
    ici, exclude(pk=None) équivaut à "pk IS NOT NULL", donc à aucune exclusion réelle.
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(Lesson, self.title, existing_pk=self.pk)
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
            # Depuis Subject.country plutôt que cursus_list : toujours renseigné (FK
            # obligatoire), contrairement à cursus qui peut être vide pour un Cours
            # "toutes séries" - source fiable unique pour indiquer le pays au visiteur.
            "pays": {"code": self.subject.country.code, "label": self.subject.country.label},
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

    @staticmethod
    def _render_question_enonce(question, numbered):
        """
        Reconstruit le texte affiché d'une sous-question à partir des champs
        structurés qu'elle porte déjà (numero, choix) - correction-experte les
        fournit systématiquement à part (voir Question.choix) plutôt que de les
        recopier en prose dans enonce_markdown, pour éviter la duplication qu'on
        obtiendrait sinon entre texte libre et champ structuré. Sans cette
        reconstruction, le numero et les options d'un QCM ne seraient jamais visibles
        en dehors du Quiz (qui les lit directement depuis l'API, pas depuis ce texte
        compilé) : le lecteur d'une épreuve verrait un énoncé nu suivi d'un corrigé
        qui référence "la bonne réponse c)" sans qu'aucune option n'ait été montrée.

        `numbered` ne préfixe le numero que si l'exercice a plusieurs sous-questions -
        inutile d'afficher "1." pour l'unique question d'un exercice simple. Le
        préfixe est aussi sauté quand `enonce_markdown` affiche déjà son propre repère
        (numérotation d'origine, lettre, titre de Partie...) - voir
        _ENONCE_ALREADY_LABELED_RE : sans ce garde-fou, un exercice dont chaque
        sous-question transcrit fidèlement sa numérotation source afficherait un
        repère en double ("**2.** 2. Déduire...", "**A.1.** **Partie A**"). Quand le
        préfixe est bien ajouté, un marqueur local redondant en tête de texte ("(b)"
        pour un numero "A.3.b") est retiré - voir _strip_redundant_local_marker :
        sinon le lecteur voit "**A.3.b.** (b) ..." plutôt que "**A.3.b.** ...".
        """
        already_labeled = bool(_ENONCE_ALREADY_LABELED_RE.match(question.enonce_markdown))
        texte = (
            f"**{question.numero}.** {_strip_redundant_local_marker(question.enonce_markdown, question.numero)}"
            if numbered and not already_labeled
            else question.enonce_markdown
        )
        if question.type_reponse == TypeReponse.QCM and question.choix:
            options = "\n".join(f"{choix['lettre']}) {choix['texte']}" for choix in question.choix)
            texte = f"{texte}\n\n{options}"
        return texte

    @staticmethod
    def _render_question_corrige(question, numbered):
        """
        Miroir de _render_question_enonce côté corrigé : sans réafficher la question
        posée, un exercice à plusieurs sous-questions affiche une série de "### Rappel
        de méthode" à la suite sans aucun moyen de savoir à quelle question chacun
        répond - l'élève doit remonter au sujet, parfois des dizaines de lignes plus
        haut, pour retrouver l'énoncé correspondant. On réutilise donc
        _render_question_enonce (numero + son garde-fou "already_labeled", déjà
        éprouvé côté énoncé) comme préambule de chaque bloc corrigé, avant
        corrige_markdown lui-même - qui ne recopie jamais son propre repère : il
        commence toujours par un des titres de niveau 3 imposés par SKILL.md ("###
        Rappel de méthode", "### Piège à éviter", "### Conseil" ou directement "###
        Corrige").
        """
        if not numbered:
            return question.corrige_markdown
        return f"{Exercise._render_question_enonce(question, numbered)}\n\n{question.corrige_markdown}"

    def compile_from_questions(self):
        """
        Concatène les Question rattachées (dans l'ordre) pour peupler enonce_markdown/
        corrige_markdown - même principe que Lesson.compile_from_exercises(). Appelée
        à l'ingestion après création des Question et attache des figures (voir
        catalog.ingestion.ingest_exercise), et par clean_em_dash après correction du
        contenu source des Question.

        Peuple aussi self.themes en union des thèmes de chaque Question : themes vit
        maintenant au niveau de la Question (granularité utile au Mode Quiz), mais
        Lesson.compile_from_exercises() lit encore exercise.themes.all() pour bâtir les
        thèmes de la Lesson (recherche plein texte) - sans ce recopiage, cette agrégation
        se viderait silencieusement.
        """
        questions = list(self.questions.prefetch_related("themes").order_by("ordre"))
        intro = f"{self.enonce_intro_markdown}\n\n" if self.enonce_intro_markdown else ""
        numbered = len(questions) > 1
        self.enonce_markdown = intro + "\n\n".join(
            self._render_question_enonce(q, numbered) for q in questions
        )
        self.corrige_markdown = "\n\n".join(
            self._render_question_corrige(q, numbered) for q in questions
        )
        self.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])

        themes = set()
        for question in questions:
            themes.update(question.themes.all())
        self.themes.set(themes)


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
        max_length=10,
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
    objects = VisibleQuerySet.as_manager()

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
            "pays": {"code": self.subject.country.code, "label": self.subject.country.label},
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
                parts.append(
                    f"### Exercice {item.get('numero', '')} ({item.get('difficulte', '')})\n\n"
                    f"{_exercice_application_enonce(item)}",
                )
                parts.append(f"### Solution\n\n{_exercice_application_solution(item)}")
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
