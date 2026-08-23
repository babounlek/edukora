from django.db import models
from django.utils.text import slugify

from catalog.models import Difficulte, StatutContenu, TypeReponse, generate_unique_slug

from .storage import protected_storage


def _corrige_pdf_upload_to(epreuve, filename):
    """Champ EpreuveInedite.corrige_pdf supprimé (voir migration
    000X_remove_epreuveinedite_corrige_pdf : le corrigé ne génère plus jamais de PDF,
    voir inedit/sujet_pdf.py) - cette fonction reste néanmoins importable : les
    migrations historiques 0004/0007 sérialisent une référence directe à cet objet
    (upload_to=inedit.models._corrige_pdf_upload_to), rejouées telles quelles à chaque
    reconstruction de la base de test depuis zéro. La supprimer casserait leur replay."""
    return f"{epreuve.cursus.first().country.code.lower()}/{slugify(epreuve.titre)}-corrige.pdf"


def _sujet_pdf_upload_to(epreuve, filename):
    """Voir inedit/sujet_pdf.py:sujet_pdf_filename, seul appelant réel."""
    return f"{epreuve.cursus.first().country.code.lower()}/{slugify(epreuve.titre)}-sujet.pdf"


class ResultatDeclare(models.TextChoices):
    """Copie volontaire de quiz.models.ResultatDeclare (même 3 valeurs) plutôt qu'un
    import inter-app : quiz est aujourd'hui une app feuille dont rien ne dépend, et ces
    trois valeurs sont un détail d'implémentation trop mineur pour justifier de casser
    ça pour ce seul champ - à remonter dans catalog si un troisième usage apparaît."""

    REUSSI = "REUSSI", "Réussi"
    PARTIEL = "PARTIEL", "Partiellement réussi"
    ECHEC = "ECHEC", "Échec"


class Blueprint(models.Model):
    """
    Plan validé d'une épreuve inédite, avant toute génération de contenu - voir
    EpreuveInedite. Un même Blueprint peut être régénéré plusieurs fois en des
    EpreuveInedite distinctes (ex. "examen blanc hebdomadaire" sur la même structure) :
    Blueprint capture la structure (sections, barème, compétences visées), EpreuveInedite
    capture une génération concrète de cette structure - jamais fusionnés en un seul
    modèle, pour permettre cette réutilisation sans dupliquer la structure à chaque
    génération (voir l'audit "Épreuves Inédites", décision "génération pré-calculée").

    statut joue exactement le même rôle que sur CompetenceItem/Cours (voir
    catalog.models.StatutContenu) : VALIDE requis avant qu'une génération puisse s'appuyer
    dessus (décision "statut de publication par défaut = Brouillon", même audit) - aucun
    contenu élève n'est jamais produit à partir d'un Blueprint encore BROUILLON.
    """

    external_id = models.CharField(
        max_length=255, blank=True,
        help_text=(
            "Identifiant déterministe fourni par la skill de conception en mode "
            "automatisation - clé d'idempotence pour une future inedit.ingestion (voir "
            "la contrainte unique_blueprint_external_id_when_set, même patron que "
            "CompetenceItem.external_id). Vide pour un blueprint créé manuellement "
            "depuis l'admin."
        ),
    )
    subject = models.ForeignKey("catalog.Subject", on_delete=models.PROTECT, related_name="blueprints")
    cursus = models.ManyToManyField(
        "catalog.Cursus", related_name="blueprints",
        help_text="Plusieurs cursus si l'épreuve est commune à plusieurs séries (ex: Maths BAC C/E).",
    )
    competences = models.ManyToManyField(
        "catalog.Tag", related_name="blueprints",
        help_text="Compétences visées par l'épreuve - au moins une, jamais déduites après coup depuis le contenu généré.",
    )

    titre = models.CharField(max_length=255)
    sections_plan = models.JSONField(
        default=list, blank=True,
        help_text=(
            "Structure de l'épreuve (nombre d'exercices, points et compétences par "
            "section, difficulté visée) - format affiné à l'usage par la future skill "
            "de conception, pas figé ici (voir catalog.models.Cours.sections_raw pour "
            "le même choix de rester en JSON libre plutôt qu'un schéma relationnel rigide)."
        ),
    )
    duree_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    bareme_total = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Total des points, ex. 20.")

    statut = models.CharField(max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["statut"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["external_id"], condition=~models.Q(external_id=""),
                name="unique_blueprint_external_id_when_set",
            ),
        ]

    def __str__(self):
        return f"{self.titre} ({', '.join(str(c) for c in self.cursus.all())})"


class EpreuveInedite(models.Model):
    """
    Épreuve générée à partir d'un Blueprint validé - jamais une paraphrase d'une épreuve
    existante du catalogue (voir Blueprint). enonce_markdown/corrige_markdown sont
    compilés depuis les ExerciceInedite rattachés (voir compile_from_exercices, appelée
    en fin d'inedit.ingestion.ingest_epreuve_inedite) - même schéma que
    Lesson.content_markdown/Exercise.compile_from_questions (voir catalog.rendering).

    score_originalite/score_qualite conditionnent la publication (contrainte non
    négociable de l'audit d'origine) - null tant que non évalués, jamais 0 par défaut
    pour ne pas confondre "pas encore évalué" et "évalué, score nul".

    Accès (décision "corrigé gaté comme le reste", audit "Épreuves Inédites") : aucune
    exception ici - énoncé, tentative et corrigé sont gatés uniformément par le futur
    access.has_access_inedite, même granularité que access.has_access sur Lesson/Cours.
    """

    blueprint = models.ForeignKey(Blueprint, on_delete=models.PROTECT, related_name="epreuves")
    external_id = models.CharField(
        max_length=255, blank=True,
        help_text="Clé d'idempotence pour une future inedit.ingestion - même rôle que Blueprint.external_id.",
    )
    subject = models.ForeignKey("catalog.Subject", on_delete=models.PROTECT, related_name="epreuves_inedites")
    cursus = models.ManyToManyField(
        "catalog.Cursus", related_name="epreuves_inedites",
        help_text="Plusieurs cursus si l'épreuve est commune à plusieurs séries (ex: Maths BAC C/E) - hérité du Blueprint source à l'ingestion.",
    )

    titre = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, blank=True,
        help_text=(
            "Généré automatiquement depuis le titre à la création - ne pas modifier après "
            "publication. Même mécanisme que catalog.models.Lesson.slug/Cours.slug (voir "
            "generate_unique_slug) : un id numérique dans l'URL ('/epreuves-inedites/6') ne "
            "dit rien du contenu et n'incite pas au partage. L'ancien lien par id reste "
            "résolu en lecture (voir inedit.views.epreuve_inedite_detail) pour ne pas casser "
            "les liens déjà partagés avant l'introduction de ce champ."
        ),
    )
    enonce_markdown = models.TextField(blank=True)
    corrige_markdown = models.TextField(blank=True)
    sujet_pdf = models.FileField(
        storage=protected_storage, upload_to=_sujet_pdf_upload_to, blank=True,
        help_text=(
            "Généré hors ligne (voir inedit.sujet_pdf.save_sujet_pdf), jamais dans le cycle "
            "d'une requête HTTP - même contrainte que catalog.sujet_pdf. Storage PRIVÉ "
            "(contrairement à Lesson.sujet_pdf, public) : une épreuve inédite jamais publiée "
            "ailleurs reste un contenu payant même sans les réponses. Seul point de sortie "
            "inedit.views.download_sujet_pdf (gated has_access_inedite). Le corrigé, lui, ne "
            "génère jamais de PDF - voir QuestionInedite.corrige_markdown/reveal_corrige, "
            "consulté uniquement en ligne, question par question, après tentative."
        ),
    )

    score_originalite = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Score 0-100, calculé lors du contrôle qualité (phase pipeline) - null tant que non évalué.",
    )
    score_qualite = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Score 0-100, calculé lors du contrôle qualité (phase pipeline) - null tant que non évalué.",
    )

    statut = models.CharField(max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["statut"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["external_id"], condition=~models.Q(external_id=""),
                name="unique_epreuveinedite_external_id_when_set",
            ),
        ]

    def __str__(self):
        return f"{self.titre} ({', '.join(str(c) for c in self.cursus.all())})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(EpreuveInedite, self.titre, existing_pk=self.pk)
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = [*update_fields, "slug"]
        super().save(*args, **kwargs)

    def compile_from_exercices(self):
        """
        Aplatit les ExerciceInedite/QuestionInedite rattachés en enonce_markdown/
        corrige_markdown - voir catalog.rendering.compile_exercise_from_questions pour
        le même principe (concaténation ordonnée, pas de logique éditoriale).
        Sauvegarde immédiatement : appelée une fois, en fin d'ingestion, jamais
        recalculée à la volée à la lecture.

        corrige_markdown restitue l'énoncé de chaque question avant sa correction - pas
        seulement la réponse seule (contrairement à QuestionInedite.corrige_markdown,
        écrit pour être lu juste après avoir déjà vu l'énoncé à l'écran, voir
        inedit.views._question_payload) : ce champ compilé est le document "corrigé"
        autonome - illisible seul si la question n'y est pas restituée. Jamais exposé en
        PDF (voir sujet_pdf pour le seul PDF généré côté épreuve inédite, sujet uniquement).
        """
        exercices = self.exercices.prefetch_related("questions").order_by("numero_exercice")
        enonce_parts = []
        corrige_parts = []
        for exercice in exercices:
            entete = f"### Exercice {exercice.numero_exercice}"
            if exercice.points:
                entete += f" ({exercice.points} pts)"
            enonce_parts.append(entete)
            corrige_parts.append(entete)
            # Le support partagé précède les questions dans les DEUX documents compilés :
            # sans lui, le corrigé autonome (et le PDF du sujet, rendu depuis
            # enonce_markdown - voir inedit.sujet_pdf._render_html) poserait des questions
            # portant sur un document absent.
            if exercice.enonce_intro_markdown:
                enonce_parts.append(exercice.enonce_intro_markdown)
                corrige_parts.append(exercice.enonce_intro_markdown)
            for question in exercice.questions.order_by("ordre"):
                enonce_parts.append(f"**{question.numero}.** {question.enonce_markdown}")
                corrige_parts.append(f"**{question.numero}.** {question.enonce_markdown}\n\n{question.corrige_markdown}")

        self.enonce_markdown = "\n\n".join(enonce_parts)
        self.corrige_markdown = "\n\n".join(corrige_parts)
        self.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])


class ExerciceInedite(models.Model):
    """Sous-partie numérotée d'une EpreuveInedite - même rôle que catalog.Exercise, pas
    réutilisé directement (voir la docstring de module de quiz.models pour le même choix
    fait pour CompetenceItem : un contenu inédit ne doit jamais dépendre d'un récit plus
    large emprunté au catalogue existant)."""

    epreuve = models.ForeignKey(EpreuveInedite, on_delete=models.CASCADE, related_name="exercices")
    numero_exercice = models.CharField(max_length=30)
    points = models.CharField(max_length=20, blank=True)
    groupes = models.JSONField(
        default=list, blank=True,
        help_text=(
            "Pile ordonnée des repères de groupe (Partie/section/matière) portés par cet "
            "exercice, renseignée directement par la skill de conception - même rôle que "
            "catalog.Exercise.groupes, mais ici pas de repli par analyse de texte : une "
            "épreuve inédite est générée, pas transcrite, donc rien à deviner depuis un "
            "en-tête d'énoncé. Vide pour la grande majorité des épreuves (structure plate)."
        ),
    )

    enonce_intro_markdown = models.TextField(
        blank=True,
        help_text=(
            "Support commun à toutes les questions de l'exercice (document à exploiter, "
            "tableau de résultats expérimentaux, données chiffrées, consigne partagée), "
            "affiché avant la première question. Même rôle que "
            "catalog.Exercise.enonce_intro_markdown, mais ici c'est le SEUL endroit où un "
            "support partagé peut vivre : le lecteur d'une tentative aplatit les exercices "
            "en une liste de questions rendues chacune depuis son propre enonce_markdown "
            "(voir InediteTentativePage.tsx) - sans ce champ, un document exploité par "
            "quatre questions devrait être recopié dans les quatre. Vide pour la plupart "
            "des exercices ; indispensable en SVT, bâtie sur l'exploitation de documents "
            "(voir le SKILL.md de concepteur-epreuve-inedite). Aucune image possible ici : "
            "la verticale inédite n'a pas d'équivalent de catalog.Figure (rien à extraire, "
            "le contenu est généré et non transcrit d'un PDF réel), donc un support doit "
            "être entièrement textuel ou tabulaire."
        ),
    )

    class Meta:
        ordering = ["epreuve", "numero_exercice"]
        constraints = [
            models.UniqueConstraint(fields=["epreuve", "numero_exercice"], name="unique_exerciceinedite_par_epreuve"),
        ]

    def __str__(self):
        return f"{self.epreuve} - Ex. {self.numero_exercice}"


class QuestionInedite(models.Model):
    """Sous-question atomique d'un ExerciceInedite - même rôle que catalog.Question."""

    exercice = models.ForeignKey(ExerciceInedite, on_delete=models.CASCADE, related_name="questions")
    numero = models.CharField(max_length=20)
    ordre = models.PositiveSmallIntegerField(help_text="Ordre d'affichage/résolution au sein de l'exercice.")

    enonce_markdown = models.TextField()
    corrige_markdown = models.TextField()

    themes = models.ManyToManyField(
        "catalog.Tag", blank=True, related_name="questions_inedites_as_theme",
        help_text=(
            "Compétence(s) réellement testées par cette question précise - sous-ensemble "
            "des Blueprint.competences visées. Optionnel par question, mais nécessaire au "
            "calcul de score_qualite (couverture des compétences visées, voir "
            "inedit.quality.score_qualite) : une question non taguée ne compte pour "
            "aucune compétence, jamais devinée depuis son contenu."
        ),
    )
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

    class Meta:
        ordering = ["exercice", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["exercice", "numero"], name="unique_questioninedite_par_exercice"),
        ]

    def __str__(self):
        return f"{self.exercice} - Q{self.numero}"


class RappelDeMethodeInedite(models.Model):
    """
    Miroir de catalog.models.RappelDeMethode pour la verticale inédite - un bloc
    "### Rappel de méthode" extrait d'une QuestionInedite par concepteur-epreuve-inedite,
    candidat à devenir un Cours indépendant (mode cours en lot, voir SKILL.md).

    Rattaché à ExerciceInedite (pas QuestionInedite), même choix que RappelDeMethode.
    exercise côté catalog : Cours se génère au niveau de l'exercice, jamais de la
    sous-question, même si authored par question dans le JSON source.

    `cours` pointe vers catalog.Cours - LE MÊME modèle que RappelDeMethode.cours,
    jamais un Cours "inédite" séparé : Cours n'a aucun champ d'origine, ce qui permet
    au dédoublonnage par titre (voir inedit.ingestion.ingest_cours_inedite) de porter
    sur TOUT Cours déjà validé, classique ou inédite, sans qu'aucun code n'ait besoin
    de distinguer les deux origines.

    related_name="rappels_source_inedit" - jamais "rappels_source" (déjà pris par
    RappelDeMethode.cours sur ce même Cours cible) : Django refuse un reverse accessor
    dupliqué sur un même modèle cible (system check fields.E304).
    """

    exercice = models.ForeignKey(ExerciceInedite, on_delete=models.CASCADE, related_name="rappels_de_methode")
    external_id = models.CharField(
        max_length=255, unique=True,
        help_text=(
            "id fourni par concepteur-epreuve-inedite (ex. rdi-<epreuve>-ex<numero>-<index>, "
            "préfixe rdi- pour rester visuellement distinct du rdm- classique dans les logs) - "
            "sert de clé d'idempotence et de référence pour le mode cours."
        ),
    )
    competence = models.CharField(max_length=255)
    contenu_markdown = models.TextField()
    cours = models.ForeignKey(
        "catalog.Cours", null=True, blank=True, on_delete=models.SET_NULL, related_name="rappels_source_inedit",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["exercice", "external_id"]

    def __str__(self):
        return f"{self.competence} ({self.exercice})"

    @property
    def cours_genere(self):
        return self.cours_id is not None


class TentativeInedite(models.Model):
    """
    Passage d'un utilisateur sur une EpreuveInedite - miroir quiz.QuizSession
    (started_at/submitted_at plutôt qu'un champ statut séparé, même choix que
    QuizSession.started_at/completed_at : "en cours" se déduit de submitted_at nul,
    jamais un état à synchroniser en plus).

    CASCADE sur `epreuve` (et, en cascade, sur TentativeReponse.question) plutôt que
    PROTECT : même arbitrage que quiz.QuizQuestion (voir sa docstring) - un admin doit
    pouvoir purger une EpreuveInedite rejetée/mauvaise même si des élèves l'ont déjà
    tentée, un historique de tentative sur du contenu supprimé n'a plus de sens à
    conserver, PROTECT bloquerait la purge entière pour cette seule raison.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="tentatives_inedites")
    epreuve = models.ForeignKey(EpreuveInedite, on_delete=models.CASCADE, related_name="tentatives")

    started_at = models.DateTimeField(auto_now_add=True)
    exam_mode_started_at = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Renseigné uniquement si l'élève a explicitement activé le mode examen "
            "(chronométré) - distinct de started_at (création de la tentative). Null "
            "pendant toute la tentative = mode libre non chronométré : le corrigé y est "
            "toujours disponible (voir _correction_disponible), aucune pression "
            "temporelle à protéger."
        ),
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    questions_marquees = models.ManyToManyField(
        QuestionInedite, blank=True, related_name="+",
        help_text="Questions marquées « à revoir » par l'élève - indépendant d'avoir répondu ou non.",
    )
    score_obtenu = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=(
            "Pourcentage de bonnes réponses parmi les questions répondues (0-100, même "
            "échelle que EpreuveInedite.score_originalite/score_qualite - pas une note sur "
            "Blueprint.bareme_total, non fiable à sommer depuis ExerciceInedite.points qui "
            "reste un texte libre). Null tant que la tentative n'est pas soumise."
        ),
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.epreuve}"

    @property
    def en_cours(self):
        return self.submitted_at is None


class TentativeReponse(models.Model):
    """
    Réponse de l'élève à une QuestionInedite au sein d'une TentativeInedite - miroir
    quiz.QuizAnswer (QCM vérifiable objectivement via reponse_choisie, question ouverte
    auto-évaluée par l'élève après le corrigé via resultat_declare). Pas de champ pour le
    texte réellement rédigé par l'élève sur une question ouverte : quiz.QuizAnswer n'en a
    jamais eu non plus, ce n'est pas un oubli propre à ce modèle.

    FK directe vers `question` (pas de pivot intermédiaire type QuizQuestion) : la
    différence avec quiz vient de la source du contenu - un CompetenceItem est pioché
    dynamiquement par utilisateur/session parmi tout un pool (d'où un pivot qui fixe le
    tirage), alors que les QuestionInedite d'une EpreuveInedite sont un ensemble fixe,
    identique pour tout élève tentant cette épreuve - rien à fixer par tentative.
    """

    tentative = models.ForeignKey(TentativeInedite, on_delete=models.CASCADE, related_name="reponses")
    question = models.ForeignKey(QuestionInedite, on_delete=models.CASCADE, related_name="+")

    reponse_choisie = models.CharField(
        max_length=10, blank=True, help_text="Lettre choisie, uniquement si QuestionInedite.type_reponse=QCM.",
    )
    resultat_declare = models.CharField(
        max_length=10, choices=ResultatDeclare.choices, blank=True,
        help_text="Auto-déclaré par l'élève après avoir vu le corrigé, uniquement si la question est ouverte.",
    )
    temps_secondes = models.PositiveIntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["tentative", "question__ordre"]
        constraints = [
            models.UniqueConstraint(fields=["tentative", "question"], name="unique_reponse_par_question_et_tentative"),
        ]

    def __str__(self):
        return f"{self.tentative} - Q{self.question.numero}"

    @property
    def est_correcte(self):
        """Voir QuizAnswer.est_correcte pour le même arbitrage QCM/ouverte."""
        if self.question.type_reponse == TypeReponse.QCM:
            return bool(self.reponse_choisie) and self.reponse_choisie == self.question.reponse_correcte
        return self.resultat_declare == ResultatDeclare.REUSSI
