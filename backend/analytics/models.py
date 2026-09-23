from django.db import models


class EventName(models.TextChoices):
    """
    Vocabulaire fermé plutôt qu'un nom d'évènement libre - voir l'audit UX, reco 5.3 :
    "léger et respectueux de la vie privée" est ici pris au sens propre, un sink
    générique où n'importe quelle page peut loguer n'importe quoi dériverait vite vers
    du texte libre (recherches saisies, etc.), jamais l'intention. Chaque nom couvre un
    point de friction précis déjà identifié dans le rapport - à étendre au cas par cas,
    jamais en ouvrant le champ à une valeur arbitraire (voir AnalyticsEventSerializer).
    """

    SEARCH_NO_RESULTS = "search_no_results", "Recherche sans résultat"
    PAYMENT_INITIATED = "payment_initiated", "Paiement initié"
    PAYMENT_SUCCEEDED = "payment_succeeded", "Paiement réussi"
    PAYMENT_FAILED = "payment_failed", "Paiement échoué"
    PAYMENT_TIMEOUT = "payment_timeout", "Paiement - confirmation trop longue"
    QUIZ_STARTED = "quiz_started", "Quiz démarré"
    QUIZ_COMPLETED = "quiz_completed", "Quiz terminé"
    INEDIT_TENTATIVE_STARTED = "inedit_tentative_started", "Épreuve inédite démarrée"
    INEDIT_TENTATIVE_COMPLETED = "inedit_tentative_completed", "Épreuve inédite terminée"
    PDF_SUJET_LANDING = "pdf_sujet_landing", "Arrivée depuis le PDF sujet partagé"
    PDF_SUJET_INEDIT_LANDING = "pdf_sujet_inedit_landing", "Arrivée depuis le PDF sujet d'une épreuve inédite"
    PDF_FICHE_SUJET_LANDING = "pdf_fiche_sujet_landing", "Arrivée depuis le PDF énoncé d'une fiche répétiteur"
    PDF_FICHE_CORRIGE_LANDING = "pdf_fiche_corrige_landing", "Arrivée depuis le PDF corrigé d'une fiche répétiteur"
    # Plan du jour (voir quiz.services.plan_du_jour). Le seul chiffre qui tranchera :
    # la part d'élèves qui reviennent faire une séance 7 jours après leur première,
    # soit plan_seance_terminee rapporté à plan_affiche dans le temps. PLAN_THEME_IGNORE
    # est son contre-indicateur - au-delà d'environ 30 % des séances affichées, c'est
    # que la sélection n'est pas crédible, et il faut regarder ce que les élèves
    # choisissent à la place plutôt qu'ajouter des fonctionnalités par-dessus.
    PLAN_AFFICHE = "plan_affiche", "Séance du jour affichée"
    PLAN_SEANCE_DEMARREE = "plan_seance_demarree", "Séance du jour démarrée"
    PLAN_SEANCE_TERMINEE = "plan_seance_terminee", "Séance du jour terminée"
    PLAN_VERROUILLE_CLIC = "plan_verrouille_clic", "Clic sur une séance verrouillée"
    PLAN_THEME_IGNORE = "plan_theme_ignore", "Thème proposé ignoré"


class AnalyticsEvent(models.Model):
    """
    Un évènement produit horodaté - voir l'audit UX, reco 5.3 ("chaque décision
    produit se prend aujourd'hui à l'aveugle"). Volontairement minimal : pas de
    tiers, pas de cookie, pas d'identifiant persistant pour un visiteur anonyme
    (`user` reste NULL dans ce cas plutôt que d'inventer un identifiant de session à
    faire vivre côté client) - seulement de quoi répondre aux questions posées dans le
    rapport (recherche sans résultat, abandon de paiement, sessions de quiz commencées
    vs terminées), jamais de reconstituer le parcours individuel d'un visiteur précis.

    `properties` : contexte minimal non-identifiant (ex. {"cursus_id": 3} ou
    {"subject_code": "MATHS"}) - jamais de texte libre saisi par l'utilisateur (une
    requête de recherche, par exemple) qui pourrait s'avérer identifiant ou sensible.
    """

    name = models.CharField(max_length=30, choices=EventName.choices, db_index=True)
    user = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="analytics_events",
        help_text="NULL pour un visiteur anonyme - jamais d'identifiant de remplacement inventé pour ce cas.",
    )
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_name_display()} - {self.created_at:%Y-%m-%d %H:%M}"
