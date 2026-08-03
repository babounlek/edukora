from django.db import models

from catalog.models import Difficulte, StatutContenu, TypeReponse


class ModeQuiz(models.TextChoices):
    PRATIQUE = "PRATIQUE", "Pratique libre"
    DIAGNOSTIC = "DIAGNOSTIC", "Test de niveau"


class ResultatDeclare(models.TextChoices):
    REUSSI = "REUSSI", "Réussi"
    PARTIEL = "PARTIEL", "Partiellement réussi"
    ECHEC = "ECHEC", "Échec"


class CompetenceItem(models.Model):
    """
    Question de quiz écrite pour une compétence (voir Tag) - jamais un fragment de
    sous-question d'Exercise. Remplace catalog.Question comme source du Mode Quiz (voir
    quiz.services.generer_session) : une catalog.Question est un extrait fidèle d'une
    épreuve réelle, pensée pour être lue dans le récit complet de son Exercise (elle
    reste la source de vérité pour la lecture d'épreuve et le PDF de sujet) ; un
    CompetenceItem est écrit dès l'origine pour se suffire à lui-même hors de tout
    contexte - il n'a jamais fait partie d'un récit plus large dans lequel puiser une
    Partie ou le résultat d'une question précédente, donc rien de ce genre ne peut lui
    manquer une fois servi seul.

    `source_exercises` ne sert qu'à la traçabilité/l'audit (justifier d'où vient la
    technique testée) - jamais exposé à l'élève, jamais recopié verbatim.
    """

    external_id = models.CharField(
        max_length=255, blank=True,
        help_text=(
            "Identifiant déterministe fourni par le skill concepteur-quiz-competence en "
            "mode automatisation - clé d'idempotence pour quiz.ingestion (voir la "
            "contrainte unique_competenceitem_external_id_when_set). Vide pour un item "
            "créé manuellement depuis l'admin."
        ),
    )
    theme = models.ForeignKey(
        "catalog.Tag", on_delete=models.PROTECT, related_name="competence_items",
        help_text=(
            "Compétence unique ciblée par cet item - contrairement à Question.themes "
            "(M2M), un item généré vise une seule compétence précise."
        ),
    )
    subject = models.ForeignKey("catalog.Subject", on_delete=models.PROTECT, related_name="competence_items")
    cursus = models.ManyToManyField(
        "catalog.Cursus", related_name="competence_items",
        help_text="Plusieurs cursus si la compétence est commune à plusieurs séries (même logique que Lesson.cursus).",
    )

    enonce_markdown = models.TextField(help_text="Rédigé pour se lire seul - jamais extrait/copié d'une épreuve source.")
    corrige_markdown = models.TextField()
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

    statut = models.CharField(
        max_length=10, choices=StatutContenu.choices, default=StatutContenu.BROUILLON,
        help_text="VALIDE requis avant d'entrer dans le pool de quiz - voir quiz.services._questions_eligibles.",
    )
    source_exercises = models.ManyToManyField(
        "catalog.Exercise", blank=True, related_name="competence_items_generes",
        help_text="Traçabilité de la technique source uniquement - jamais affiché à l'élève.",
    )

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
                name="unique_competenceitem_external_id_when_set",
            ),
        ]

    def __str__(self):
        return f"{self.theme} ({self.get_difficulte_estimee_display() or 'difficulté non estimée'})"


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
    Un item piochée pour cette session, dans un ordre donné - jamais modifiée après
    création. `competence_item` est la seule source peuplée par generer_session depuis
    la bascule vers CompetenceItem : catalog.Question n'est plus jamais tirée pour une
    nouvelle session (une sous-question d'épreuve extraite peut être illisible hors du
    récit de son Exercise - Partie, résultat d'une question précédente... - alors qu'un
    CompetenceItem est écrit dès l'origine pour se suffire seul). `question` reste en
    lecture seule pour les QuizQuestion créées avant la bascule : purger cet historique
    reviendrait à effacer des sessions de quiz réellement passées par des élèves, ce que
    la bascule de source ne demande pas. Exactement un des deux doit être renseigné (voir
    la contrainte quizquestion_exactly_one_source). related_name volontairement vide
    (`+`) des deux côtés : le lien utile se lit depuis QuizQuestion, pas l'inverse (un
    même item peut apparaître dans de nombreuses sessions).

    CASCADE plutôt que PROTECT sur les deux FK : la purge admin (voir
    catalog.admin.LessonAdmin.purge_view) supprime tout le contenu pédagogique en bloc
    (Exercise -> Question en cascade) et doit pouvoir aboutir même si des Question ont
    déjà été piochées dans des quiz - un historique de quiz sur du contenu supprimé n'a
    plus de sens à conserver, PROTECT bloquerait la purge entière pour cette seule raison.
    """

    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="quiz_questions")
    question = models.ForeignKey(
        "catalog.Question", null=True, blank=True, on_delete=models.CASCADE, related_name="+",
        help_text="Historique pré-bascule uniquement - generer_session ne peuple plus jamais ce champ.",
    )
    competence_item = models.ForeignKey(
        CompetenceItem, null=True, blank=True, on_delete=models.CASCADE, related_name="+",
        help_text="Seule source peuplée par generer_session depuis la bascule vers CompetenceItem.",
    )
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["session", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["session", "ordre"], name="unique_ordre_par_session"),
            models.CheckConstraint(
                condition=(
                    models.Q(question__isnull=False, competence_item__isnull=True)
                    | models.Q(question__isnull=True, competence_item__isnull=False)
                ),
                name="quizquestion_exactly_one_source",
            ),
        ]

    def __str__(self):
        return f"{self.session} - Q{self.ordre}"

    @property
    def contenu(self):
        """Item réel, quelle que soit la source (voir la contrainte exactly_one_source)."""
        return self.competence_item or self.question


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
        QCM : comparaison objective à reponse_correcte (vérité terrain connue).
        Question ouverte : pas de vérité terrain automatisable (dissertation, calcul à
        développement libre) - on fait confiance à l'auto-déclaration de l'élève, faite
        après qu'il a vu le corrigé complet. `contenu` : voir QuizQuestion.contenu, valable
        aussi bien pour l'historique pré-bascule (catalog.Question) que pour un
        CompetenceItem.
        """
        contenu = self.quiz_question.contenu
        if contenu.type_reponse == TypeReponse.QCM:
            return bool(self.reponse_choisie) and self.reponse_choisie == contenu.reponse_correcte
        return self.resultat_declare == ResultatDeclare.REUSSI
