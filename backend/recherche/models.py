from django.db import models


class TypeResultat(models.TextChoices):
    # L'ordre de déclaration est l'ordre d'affichage des groupes (voir moteur.ORDRE_GROUPES).
    THEME = "THEME", "Thèmes"
    COURS = "COURS", "Cours"
    EPREUVE = "EPREUVE", "Épreuves"
    INEDITE = "INEDITE", "Épreuves inédites"
    EXERCICE = "EXERCICE", "Exercices"
    QUIZ = "QUIZ", "Questions de quiz"


class EntreeRecherche(models.Model):
    """
    Une ligne de l'index de recherche globale : une version à plat, normalisée et plafonnée
    d'un contenu du catalogue (thème, cours, épreuve, exercice, question de quiz...). Jamais
    une source de vérité - reconstruite à volonté par `manage.py indexer_recherche` depuis les
    vrais modèles (voir recherche.indexation), donc supprimable sans perte.

    Ce qui est INDEXÉ est borné à ce qu'un visiteur non abonné peut déjà lire sur le site :
    l'énoncé d'une épreuve (le sujet est public, seul le corrigé est payant), l'aperçu public
    d'un cours (accroche, prérequis, règle - voir catalog.rendering.cours_preview_markdown).
    Jamais un corrigé. Pour une question de quiz, l'énoncé est indexé (pour la retrouver) mais
    n'est montré qu'à qui y a accès (voir recherche.moteur.serialiser) : une session de quiz
    est réservée aux abonnés hors thème vitrine.
    """

    type = models.CharField(max_length=10, choices=TypeResultat.choices, db_index=True)
    objet_id = models.PositiveIntegerField(
        help_text="Clé primaire de l'objet source : Tag (THEME), Cours, Lesson, EpreuveInedite, Exercise ou CompetenceItem.",
    )
    pays = models.ForeignKey("catalog.Country", on_delete=models.CASCADE, related_name="+")
    # Toujours renseignée (chaque source a une matière) : fait partie de la clé d'unicité, car un
    # même thème (Tag) peut exister dans deux matières - une entrée par couple (thème, matière).
    matiere = models.ForeignKey("catalog.Subject", on_delete=models.CASCADE, related_name="+")
    cursus = models.ManyToManyField(
        "catalog.Cursus", blank=True, related_name="+",
        help_text="Cursus auxquels ce résultat est PROPOSÉ (pas forcément ceux de l'accès - voir meta['acces_ids']).",
    )
    tous_cursus = models.BooleanField(
        default=False,
        help_text="Proposé à tout cursus (notion commune) : retenu quel que soit le filtre d'examen.",
    )

    titre = models.CharField(max_length=255)
    titre_norm = models.CharField(max_length=255)
    # Clés courtes (titre, matière, séries, thèmes) : de quoi retrouver le contenu par ses mots
    # d'identité. Entourées d'espaces pour que « " " + mot » cherche un DÉBUT de mot.
    cles_norm = models.TextField()
    # Texte public plafonné (énoncé, aperçu de cours) : seulement pour retrouver une notion
    # absente du titre. Jamais renvoyé à l'élève tel quel.
    texte_norm = models.TextField(blank=True)
    apercu = models.CharField(max_length=255, blank=True)

    annee = models.PositiveSmallIntegerField(null=True, blank=True)
    # « tag:matière » pour un THEME et pour les QUIZ de ce thème : regroupe les questions d'un même
    # thème en UN résultat, et masque ce résultat quand le thème lui-même est déjà proposé.
    groupe = models.CharField(max_length=40, blank=True)
    # Volume de contenu rattaché (THEME : cours + questions + exercices) - départage à pertinence égale
    # et ordonne les thèmes proposés quand la recherche ne donne rien.
    poids = models.PositiveIntegerField(default=0)
    est_gratuit = models.BooleanField(
        default=False, help_text="Lisible sans abonnement (vitrine / épreuve offerte).",
    )
    meta = models.JSONField(
        default=dict, blank=True,
        help_text="Champs propres au type : slug, numéro d'exercice, id de thème, compteurs, cursus d'accès...",
    )

    class Meta:
        verbose_name = "entrée de recherche"
        verbose_name_plural = "entrées de recherche"
        constraints = [
            models.UniqueConstraint(fields=["type", "objet_id", "matiere"], name="unique_entree_recherche_par_objet"),
        ]
        indexes = [
            models.Index(fields=["pays", "type"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} · {self.titre}"


class TermeRecherche(models.Model):
    """
    Mot du vocabulaire du catalogue (titres, thèmes, matières) avec sa fréquence - sert
    uniquement à proposer « Vouliez-vous dire ... ? » quand un mot tapé n'existe nulle part
    (voir recherche.moteur.corriger). Reconstruit avec l'index.
    """

    terme = models.CharField(max_length=60, unique=True)
    frequence = models.PositiveIntegerField(default=1)
    # Clé de prononciation (voir texte.phonetique) : « teoreme » retrouve « theoreme » même quand la distance
    # d'édition hésite entre plusieurs mots.
    phonetique = models.CharField(max_length=60, blank=True, default="", db_index=True)

    class Meta:
        verbose_name = "terme de recherche"
        verbose_name_plural = "termes de recherche"


class RechercheSansResultat(models.Model):
    """
    Requêtes qui n'ont rien donné, AGRÉGÉES : une ligne par texte normalisé avec un compteur.
    Montre ce que les élèves cherchent et que le catalogue ne contient pas - de quoi orienter les
    prochaines campagnes de contenu.

    Écart assumé avec analytics.AnalyticsEvent, qui s'interdit tout texte saisi : ici le texte
    est justement la donnée utile. D'où les garde-fous (voir recherche.moteur.journaliser_vide) :
    aucun identifiant de personne ni de session, requête normalisée et plafonnée en longueur,
    refus de tout ce qui ressemble à un numéro (téléphone, matricule) ou à une adresse e-mail,
    et seule la recherche VALIDÉE (page de résultats) est comptée, jamais chaque frappe.
    """

    requete = models.CharField(max_length=80)
    pays_code = models.CharField(max_length=10)
    nb = models.PositiveIntegerField(default=1)
    premiere_fois = models.DateTimeField(auto_now_add=True)
    derniere_fois = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "recherche sans résultat"
        verbose_name_plural = "recherches sans résultat"
        ordering = ["-nb", "-derniere_fois"]
        constraints = [
            models.UniqueConstraint(fields=["requete", "pays_code"], name="unique_recherche_vide_par_pays"),
        ]

    def __str__(self):
        return f"{self.requete} ({self.nb})"
