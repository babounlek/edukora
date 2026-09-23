from django.db import models

from catalog.models import Difficulte, StatutContenu, TypeReponse

from .storage import protected_storage


def _sujet_pdf_upload_to(session, filename):
    # Préfixé par le code pays puis l'utilisateur - même convention que les autres
    # storages de PDF privés du projet (voir fiches.models._sujet_pdf_upload_to,
    # inedit.models._sujet_pdf_upload_to) : sans lui, deux élèves de pays différents
    # dont les sessions partageraient un même id (impossible ici, id auto-incrémenté
    # global, mais la convention reste appliquée pour rester cohérent avec ces deux
    # autres apps) pourraient collider.
    return f"{session.cursus.country.code.lower()}/{session.user_id}/session-{session.pk}-fiche.pdf"


def _corrige_pdf_upload_to(session, filename):
    return f"{session.cursus.country.code.lower()}/{session.user_id}/session-{session.pk}-correction.pdf"


class ModeQuiz(models.TextChoices):
    PRATIQUE = "PRATIQUE", "Pratique libre"
    DIAGNOSTIC = "DIAGNOSTIC", "Test de niveau"


class StatutFichePdf(models.TextChoices):
    """
    Cycle de vie de la génération des DEUX PDF (sujet_pdf/corrige_pdf) d'une QuizSession -
    même patron que fiches.models.StatutGeneration (voir sa docstring, un seul statut y
    gouverne déjà sa propre paire sujet/corrigé), décliné ici pour une ressource créée à
    la demande de l'élève lui-même APRÈS coup (la QuizSession existe déjà bien avant
    qu'une fiche ne soit jamais demandée), d'où l'absence de valeur par défaut :
    QuizSession.fiche_pdf_statut reste vide tant qu'aucune génération n'a été demandée.
    """

    EN_COURS = "EN_COURS", "Génération en cours"
    PRETE = "PRETE", "Prête"
    ECHEC = "ECHEC", "Échec"


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

    fiche_pdf_statut = models.CharField(
        max_length=10, choices=StatutFichePdf.choices, blank=True,
        help_text="Vide tant qu'aucune fiche PDF n'a été demandée - voir StatutFichePdf.",
    )
    # Deux PDF distincts, générés ensemble (voir quiz.pdf.save_quiz_fiche_pdf) - même
    # décision produit que fiches.models.FicheGeneree (voir sa docstring) : l'élève doit
    # pouvoir imprimer/partager la fiche d'exercices seule (sujet_pdf) sans que le
    # corrigé y figure déjà, et retrouver la correction complète séparément.
    sujet_pdf = models.FileField(
        storage=protected_storage, upload_to=_sujet_pdf_upload_to, blank=True,
        help_text="Énoncés seuls de cette session, générés à la demande - voir quiz.pdf.",
    )
    corrige_pdf = models.FileField(
        storage=protected_storage, upload_to=_corrige_pdf_upload_to, blank=True,
        help_text="Énoncés + corrigé de cette session, générés à la demande - voir quiz.pdf.",
    )

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


class RevisionSchedule(models.Model):
    """
    Prochaine échéance de révision d'un thème pour un utilisateur, sur un cursus donné -
    algorithme Leitner à 3 paliers (J+1, J+3, J+7, voir LEITNER_INTERVALS_JOURS dans
    quiz.services) déclenché par les réponses en Quiz (voir
    quiz.services.enregistrer_resultat_pour_revision, appelé depuis
    quiz.views.answer_question, seul appelant).

    N'existe QUE pour un thème actuellement en difficulté : un thème jamais raté n'a
    jamais de ligne ici (rien à corriger), et une ligne est supprimée dès que l'élève
    l'a retraversé avec succès jusqu'au dernier palier - thème "gradué", plus besoin de
    révision programmée (voir enregistrer_resultat_pour_revision).
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="revision_schedules")
    cursus = models.ForeignKey("catalog.Cursus", on_delete=models.CASCADE, related_name="revision_schedules")
    subject = models.ForeignKey("catalog.Subject", on_delete=models.CASCADE, related_name="revision_schedules")
    theme = models.ForeignKey("catalog.Tag", on_delete=models.CASCADE, related_name="revision_schedules")

    palier = models.PositiveSmallIntegerField(
        default=0, help_text="Index dans LEITNER_INTERVALS_JOURS - remis à 0 à chaque échec.",
    )
    due_at = models.DateField(help_text="Prochaine date à laquelle ce thème doit être re-proposé en révision.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "cursus", "theme"], name="unique_revision_schedule"),
        ]

    def __str__(self):
        return f"{self.user} - {self.theme} ({self.due_at})"


class OrigineSeance(models.TextChoices):
    """D'où vient la séance proposée - voir quiz.services.plan_du_jour, qui les essaie
    dans cet ordre de priorité."""

    REVISION_DUE = "REVISION_DUE", "Révision due"
    LECTURE_EN_COURS = "LECTURE_EN_COURS", "Lecture en cours"
    DIAGNOSTIC = "DIAGNOSTIC", "Calibrage"
    PARCOURS = "PARCOURS", "Parcours"


class StatutSeance(models.TextChoices):
    PROPOSEE = "PROPOSEE", "Proposée"
    TERMINEE = "TERMINEE", "Terminée"
    # L'élève a dit "ce n'est pas ce que je veux réviser" et on lui en a proposé une
    # autre (voir quiz.services.remplacer_seance). Conservée plutôt que supprimée :
    # c'est la trace que notre sélection s'est trompée, et le seul contre-indicateur
    # honnête de la qualité du plan. Ne compte jamais comme une séance faite.
    REMPLACEE = "REMPLACEE", "Remplacée"


class SeanceJournaliere(models.Model):
    """
    La séance du jour d'un élève : une matière, un thème, quelques étapes, ~25 minutes.

    Cette table EST le cache de la journée, et c'est son intérêt principal. La
    promesse du plan quotidien ("une seule prochaine action") ne tient que si ouvrir
    l'appli trois fois dans la journée montre la MÊME séance : une proposition
    recalculée à chaque affichage redeviendrait un catalogue qui change tout seul,
    exactement ce à quoi elle doit se substituer. La ligne est donc écrite une fois
    par (user, cursus, jour), puis relue telle quelle.

    Sert aussi de mémoire à deux règles qui ont besoin du passé : la rotation des
    matières (voir plan_du_jour) et le compteur "n séances cette semaine".

    `date` est la date LOCALE (settings.TIME_ZONE = Africa/Douala), jamais UTC - en
    UTC la journée d'un élève camerounais basculerait à 1 h du matin. Le jour où un
    second pays s'ouvre sur un autre fuseau, c'est ici qu'il faudra un
    Country.timezone : aujourd'hui le réglage global EST le fuseau du seul pays servi.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="seances_journalieres")
    cursus = models.ForeignKey("catalog.Cursus", on_delete=models.CASCADE, related_name="seances_journalieres")
    date = models.DateField(help_text="Jour local de la séance - voir la docstring de la classe.")

    origine = models.CharField(max_length=20, choices=OrigineSeance.choices)
    subject = models.ForeignKey(
        "catalog.Subject", null=True, blank=True, on_delete=models.CASCADE, related_name="seances_journalieres",
        help_text="Nul pour un calibrage, qui porte sur tout le cursus et non sur une matière.",
    )
    theme = models.ForeignKey(
        "catalog.Tag", null=True, blank=True, on_delete=models.SET_NULL, related_name="seances_journalieres",
        help_text="Thème travaillé, quand la séance en cible un - voir aussi `savoir`.",
    )
    savoir = models.ForeignKey(
        "programme.Savoir", null=True, blank=True, on_delete=models.SET_NULL, related_name="seances_journalieres",
        help_text=(
            "Alternative à `theme` pour les matières dont le parcours suit le programme "
            "officiel plutôt que la fréquence des thèmes (français, philo, histoire-géo, "
            "anglais - voir SUBJECTS_PARCOURS_PAR_FREQUENCE)."
        ),
    )
    """
    `theme` et `savoir` sont tous deux SET_NULL et tous deux facultatifs : une séance
    déjà faite reste un fait historique (elle alimente la rotation des matières et le
    compteur hebdomadaire) même si le Tag qui la portait a été fusionné depuis - or
    les fusions de tags sont fréquentes sur ce corpus. La perdre en cascade
    réécrirait l'historique de l'élève pour une raison qui ne le concerne pas.
    """

    etapes = models.JSONField(
        default=list,
        help_text="Étapes de la séance, dans l'ordre - voir quiz.services._construire_etapes.",
    )
    budget_minutes = models.PositiveSmallIntegerField(
        default=25,
        help_text=(
            "Temps que l'élève s'est donné aujourd'hui (voir BUDGETS_SEANCE_MINUTES). "
            "Un PLAFOND, pas une promesse : la séance affiche sa durée réelle, souvent "
            "inférieure quand le contenu manque."
        ),
    )
    cours = models.ForeignKey(
        "catalog.Cours", null=True, blank=True, on_delete=models.SET_NULL, related_name="seances",
        help_text=(
            "Cours retenu pour l'étape méthode. Mémorisé plutôt que recalculé : sans "
            "lui, passer la séance à 10 minutes puis revenir à 25 la perdrait, le "
            "classement qui l'avait choisi n'étant pas rejoué à chaque ajustement."
        ),
    )
    quiz_session = models.ForeignKey(
        "quiz.QuizSession", null=True, blank=True, on_delete=models.SET_NULL, related_name="seances",
        help_text=(
            "Session lancée depuis l'étape quiz de cette séance - renseignée seulement "
            "si l'élève l'ouvre réellement. Donne le score affiché en fin de séance, et "
            "déclenche sa clôture automatique (voir quiz.views.complete_session)."
        ),
    )
    statut = models.CharField(max_length=10, choices=StatutSeance.choices, default=StatutSeance.PROPOSEE)
    ordre = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Rang de la séance dans la journée. 1 pour la séance du jour ; au-delà, "
            "une séance demandée EN PLUS par l'élève qui a fini la sienne et veut "
            "continuer (voir quiz.services.seance_supplementaire). Jamais créée "
            "d'office : c'est ce qui préserve la promesse d'une seule chose à faire."
        ),
    )
    termine_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Du plus récent au plus avancé dans la journée : `.first()` sur un jour donné
        # rend donc toujours la séance EN COURS, pas celle déjà terminée ce matin.
        ordering = ["-date", "-ordre"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "cursus", "date", "ordre"], name="unique_seance_par_rang_du_jour",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.date} ({self.get_origine_display()})"

    @property
    def duree_estimee_min(self):
        return sum(etape.get("duree_min", 0) for etape in self.etapes)
