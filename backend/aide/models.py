from django.db import models


class CategorieAide(models.TextChoices):
    """
    Les rubriques du centre d'aide. Une liste FERMÉE et courte : les libellés affichés vivent côté
    frontend (clés `aide.cat.*`, traduites), le code ne sert qu'à ranger et ordonner. Ajouter une
    rubrique, c'est ajouter une ligne ici ET sa clé de traduction - jamais un texte libre en base.
    """

    DEMARRER = "demarrer", "Démarrer"
    CONNEXION = "connexion", "Connexion"
    PAIEMENT = "paiement", "Paiement et abonnement"
    UTILISER = "utiliser", "Utiliser EduKora"
    PARENTS = "parents", "Parents"
    AUTRES = "autres", "Autres questions"


class ArticleAide(models.Model):
    """
    Un article du centre d'aide, en français et, quand il est traduit, en anglais.

    Le texte vit en base pour pouvoir être corrigé dans l'admin sans rebuild (un délai, un moyen
    de paiement ou une campagne changent plus vite que le déploiement). La première version vient
    de fichiers Markdown versionnés (aide/articles/, chargés par `charger_aide`) : un article
    corrigé à la main dans l'admin est marqué `modifie_a_la_main` et n'est plus jamais réécrit par
    ce chargement sans `--forcer`.

    Les valeurs qui existent déjà ailleurs (WhatsApp, e-mail, délai de vérification d'un paiement,
    nom du site) s'écrivent `{{whatsapp}}`, `{{email}}`, `{{delai_verification}}`, `{{site}}`,
    `{{editeur}}` : le frontend les remplace au rendu depuis les constantes du site, pour qu'un
    numéro corrigé une fois le soit partout. Aucun montant en dur : on renvoie vers /tarifs.
    """

    slug = models.SlugField(max_length=80, unique=True)
    categorie = models.CharField(max_length=12, choices=CategorieAide.choices)
    ordre = models.PositiveSmallIntegerField(default=100, help_text="Plus petit = plus haut dans sa rubrique.")
    populaire = models.BooleanField(default=False, help_text="Affiché dans « Questions fréquentes » en tête du centre d'aide.")
    publie = models.BooleanField(default=True)

    titre_fr = models.CharField(max_length=160)
    resume_fr = models.CharField(max_length=300, help_text="Une phrase : ce que l'article répond.")
    corps_fr = models.TextField(help_text="Markdown (titres ##, listes, **gras**, liens internes /tarifs).")
    mots_cles_fr = models.TextField(blank=True, help_text="Synonymes et mots que l'élève tape, séparés par des virgules.")

    titre_en = models.CharField(max_length=160, blank=True)
    resume_en = models.CharField(max_length=300, blank=True)
    corps_en = models.TextField(blank=True)
    mots_cles_en = models.TextField(blank=True)

    pages_liees = models.CharField(
        max_length=200,
        blank=True,
        help_text="Chemins internes (français) où cet article est proposé en tête du panneau d'aide, séparés par des virgules. Ex. /connexion,/mes-paiements.",
    )
    modifie_a_la_main = models.BooleanField(default=False, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["categorie", "ordre", "slug"]
        verbose_name = "article d'aide"
        verbose_name_plural = "articles d'aide"

    def __str__(self):
        return self.titre_fr

    @property
    def traduit(self):
        return bool(self.titre_en and self.corps_en)

    def pages(self):
        return [p.strip() for p in self.pages_liees.split(",") if p.strip()]
