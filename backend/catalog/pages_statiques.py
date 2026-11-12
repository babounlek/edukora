"""Les pages publiques SANS identifiant : accueil du pays, listes (épreuves, cours, thèmes), tarifs, à propos, aide.

Même rôle que `pages_examen` pour les moteurs de recherche et les robots de partage : sans cela, ces pages n'avaient dans
leur HTML initial ni texte, ni titre propre, ni lien vers le reste du site (audit du 2026-11-12, SEO-06 et SEO-08).
`prerendu` les sert aux moteurs et `apercu_partage` aux robots de partage ; elles ne portent que ce qu'un visiteur anonyme
voit déjà : un texte d'introduction et des liens (les pages d'examen, les articles d'aide), jamais de contenu payant.

Les titres et descriptions reprennent ceux que le frontend pose à l'exécution (useSeo) : un moteur qui compare le HTML
initial au rendu ne doit pas y voir deux pages différentes. Un test le garde pour les gabarits partagés.
"""
import re

from django.conf import settings

from aide.models import ArticleAide

from . import pages_examen
from .models import Country, Langue
from .segments_url import chemin_public

# Le chemin INTERNE (français, sans « / » aux extrémités ni préfixe /en) : « », « cm », « cm/epreuves », « tarifs ».
CHEMIN_RE = re.compile(
    r"^(?:(?P<pays>[a-z]{2})(?:/(?P<liste>epreuves|cours|themes-frequents))?|(?P<page>tarifs|a-propos|aide))?$"
)

NOMS_PAYS_EN = {"CM": "Cameroon"}

TEXTES = {
    "fr": {
        "accueil_titre": "Corrigés {examens} - {pays}",
        "accueil_description": (
            "{pays} : chaque jour, on te dit quoi réviser pour {examens_prose}. Les thèmes qui tombent vraiment, avec "
            "corrigés d'annales, cours et quiz."
        ),
        "accueil_intro": (
            "Chaque jour, EduKora te dit quoi réviser : une séance de 25 minutes sur un thème qui tombe vraiment à ton "
            "examen, avec le cours pour la méthode, un exercice réellement posé et un quiz pour vérifier."
        ),
        "epreuves_titre": "Épreuves et corrigés - {pays}",
        "epreuves_description": "{pays} : sujets et corrigés d'annales, examens blancs et épreuves inédites, classés par matière, cursus et série.",
        "epreuves_intro": "Toutes les annales corrigées, examen par examen. Les sujets sont toujours consultables gratuitement.",
        "cours_titre": "Cours de révision - {pays}",
        "cours_description": "{pays} : cours structurés (méthode, exemple résolu, erreurs classiques, exercices) pour {examens_prose}.",
        "cours_intro": "Des cours structurés : la règle, un exemple résolu, les erreurs classiques et des exercices d'application.",
        "themes_titre": "Les thèmes qui reviennent le plus - {pays}",
        "themes_description": "{pays} : le classement des thèmes les plus fréquents aux épreuves officielles, matière par matière et cursus par cursus.",
        "themes_intro": "Le classement des thèmes les plus posés aux épreuves officielles, calculé sur les vraies annales : révise d'abord ce qui compte.",
        "tarifs_titre": "Tarifs : abonnement au mois par Mobile Money",
        "tarifs_description": "Abonnement {site} au mois par Mobile Money : tu choisis le nombre de mois, pour accéder à tous les corrigés et cours de ton cursus.",
        "tarifs_intro": (
            "Un abonnement au mois : tu choisis le nombre de mois, de un mois jusqu'à ton examen, et le total est affiché "
            "avant de payer. Paiement par Mobile Money (MTN, Orange), sans prélèvement automatique. Un seul compte peut "
            "servir plusieurs enfants, avec un tarif réduit à partir du deuxième."
        ),
        "tarifs_inclus": ["Corrigés complets en illimité", "Exercices d'application corrigés", "Le quiz qui cible tes révisions", "Épreuves inédites EduKora", "Les thèmes qui reviennent le plus"],
        "apropos_titre": "À propos",
        "apropos_description": "Qui est derrière {site}, comment fonctionnent la séance du jour et les corrigés, et pourquoi élèves, parents et établissements peuvent nous faire confiance.",
        "apropos_intro": (
            "{site} réunit les sujets officiels, les corrige pas à pas et en tire chaque jour une séance courte sur les "
            "thèmes les plus posés à ton examen. Accessible depuis un simple téléphone, payable en Mobile Money, sans carte "
            "bancaire ni engagement caché."
        ),
        "aide_titre": "Centre d'aide",
        "aide_description": "Les réponses aux questions sur {site} : connexion, paiement Mobile Money, cours, quiz, annales et comptes parents.",
        "aide_intro": "Les réponses à tes questions : compte, paiement, cours, quiz.",
        "examens": "Examens",
        "parcourir": "Parcourir",
        "n_epreuves": "{n} épreuves",
        "lien_epreuves": "Toutes les épreuves corrigées",
        "lien_cours": "Cours de révision",
        "lien_themes": "Les thèmes qui reviennent le plus",
        "lien_tarifs": "Tarifs",
        "lien_aide": "Centre d'aide",
        "inclus": "Ce qui est inclus",
        "articles": "Articles d'aide",
        "examens_prose": "le BEPC, le Probatoire et le BAC",
    },
    "en": {
        "accueil_titre": "Past papers with solutions: {examens} - {pays}",
        "accueil_description": (
            "{pays}: every day, we tell you what to revise for {examens_prose}. The topics that really come up, with past "
            "paper solutions, lessons and quizzes."
        ),
        "accueil_intro": (
            "Every day, EduKora tells you what to revise: a 25-minute session on a topic that really comes up in your "
            "exam, with the lesson for the method, a question that was actually set and a quiz to check yourself."
        ),
        "epreuves_titre": "Past papers and solutions - {pays}",
        "epreuves_description": "{pays}: past papers with solutions, mock exams and original papers, sorted by subject, exam and series.",
        "epreuves_intro": "Every past paper with its solution, exam by exam. The papers are always free to read.",
        "cours_titre": "Revision lessons - {pays}",
        "cours_description": "{pays}: structured lessons (method, worked example, common mistakes, exercises) for {examens_prose}.",
        "cours_intro": "Structured lessons: the rule, a worked example, the classic mistakes and practice exercises.",
        "themes_titre": "The topics that come up most - {pays}",
        "themes_description": "{pays}: the ranking of the topics that come up most in official papers, subject by subject and exam by exam.",
        "themes_intro": "The ranking of the topics set most often in official papers, calculated from the real past papers: revise what matters first.",
        "tarifs_titre": "Pricing: monthly subscription by Mobile Money",
        "tarifs_description": "{site} monthly subscription by Mobile Money: you choose the number of months, to access every solution and lesson for your exam.",
        "tarifs_intro": (
            "A monthly subscription: you choose the number of months, from one month up to your exam, and the total is shown "
            "before you pay. Payment by Mobile Money (MTN, Orange), with no automatic charges. One account can serve several "
            "children, with a reduced price from the second."
        ),
        "tarifs_inclus": ["Unlimited full solutions", "Worked practice exercises", "The quiz that targets your revision", "EduKora original papers", "The topics that come up most"],
        "apropos_titre": "About",
        "apropos_description": "Who is behind {site}, how the daily session and the solutions work, and why students, parents and schools can trust us.",
        "apropos_intro": (
            "{site} gathers the official papers, solves them step by step and turns them into a short daily session on the "
            "topics set most often in your exam. Works on a basic phone, payable by Mobile Money, with no bank card and no "
            "hidden commitment."
        ),
        "aide_titre": "Help centre",
        "aide_description": "Answers about {site}: logging in, Mobile Money payment, lessons, quizzes, past papers and parent accounts.",
        "aide_intro": "Answers to your questions: account, payment, lessons, quizzes.",
        "examens": "Exams",
        "parcourir": "Browse",
        "n_epreuves": "{n} papers",
        "lien_epreuves": "All past papers with solutions",
        "lien_cours": "Revision lessons",
        "lien_themes": "The topics that come up most",
        "lien_tarifs": "Pricing",
        "lien_aide": "Help centre",
        "inclus": "What is included",
        "articles": "Help articles",
        "examens_prose": "GCE O Level and GCE A Level",
    },
}

CLES_PAGE = {"tarifs": "tarifs", "a-propos": "apropos", "aide": "aide"}
CLES_LISTE = {None: "accueil", "epreuves": "epreuves", "cours": "cours", "themes-frequents": "themes"}


def _pays_par_defaut():
    pays = Country.objects.filter(actif=True).order_by("id").first()
    return pays.code.lower() if pays else None


def _nom_pays(code, langue):
    pays = Country.objects.filter(code__iexact=code, actif=True).first()
    if pays is None:
        return None
    return NOMS_PAYS_EN.get(pays.code.upper(), pays.label) if langue == "en" else pays.label


def _examens_du_pays(code, langue):
    """Les examens de la langue de la page qui ont une page d'atterrissage : [(libellé, chemin interne, n)]."""
    cible = Langue.EN if langue == "en" else Langue.FR
    return [
        (pages_examen.libelle_examen(c), f"/{code}/examens/{pages_examen.slug_cursus(c)}", n)
        for c, n in pages_examen.cursus_avec_epreuves(code)
        if c.langue == cible
    ]


def _noms_examens(code, langue):
    """« BEPC, Probatoire, BAC » : les examens (sans les séries) dans l'ordre où le site les présente."""
    vus = []
    for c, _n in pages_examen.cursus_avec_epreuves(code):
        if c.langue == (Langue.EN if langue == "en" else Langue.FR) and c.display_examen() not in vus:
            vus.append(c.display_examen())
    return ", ".join(vus)


def page_statique(interne, langue):
    """La page d'atterrissage d'un chemin interne sans identifiant (voir CHEMIN_RE), au format des pages du prérendu, ou
    None (chemin d'une autre sorte, pays inconnu ou sans épreuve dans cette langue)."""
    m = CHEMIN_RE.match(interne.strip("/"))
    if not m:
        return None
    textes = TEXTES[langue]
    site = "EduKora"
    if m.group("page"):
        cle = CLES_PAGE[m.group("page")]
        chemin = f"/{m.group('page')}"
        pays = None
        valeurs = {"site": site}
        liens = []
        corps = [textes[f"{cle}_intro"].format(site=site)]
        if cle == "tarifs":
            corps += ["", f"## {textes['inclus']}", ""] + [f"- {ligne}" for ligne in textes["tarifs_inclus"]]
        if cle == "aide":
            articles = ArticleAide.objects.filter(publie=True).order_by("categorie", "id")
            anglais = langue == "en"
            corps += ["", f"## {textes['articles']}", ""]
            for article in articles:
                titre = article.titre_en if anglais and article.traduit else article.titre_fr
                corps.append(f"- [{titre}]({chemin_public(f'/aide/{article.slug}', langue)})")
    else:
        pays = m.group("pays") or _pays_par_defaut()
        if pays is None:
            return None
        nom = _nom_pays(pays, langue)
        examens = _examens_du_pays(pays, langue)
        if nom is None or not examens:
            return None
        cle = CLES_LISTE[m.group("liste")]
        chemin = f"/{pays}" + (f"/{m.group('liste')}" if m.group("liste") else "")
        valeurs = {
            "pays": nom, "site": site, "examens": _noms_examens(pays, langue), "examens_prose": textes["examens_prose"],
        }
        liens = []
        corps = [textes[f"{cle}_intro"].format(**valeurs), "", f"## {textes['examens']}", ""]
        corps += [
            f"- [{libelle}]({chemin_public(page, langue)}) - {textes['n_epreuves'].format(n=n)}" for libelle, page, n in examens
        ]
        if cle != "epreuves":
            liens.append((textes["lien_epreuves"], f"/{pays}/epreuves"))
        if cle != "cours":
            liens.append((textes["lien_cours"], f"/{pays}/cours"))
        if cle != "themes":
            liens.append((textes["lien_themes"], f"/{pays}/themes-frequents"))
        if cle == "accueil":
            liens += [(textes["lien_tarifs"], "/tarifs"), (textes["lien_aide"], "/aide")]
    return {
        "titre": textes[f"{cle}_titre"].format(**valeurs),
        "description": textes[f"{cle}_description"].format(**valeurs),
        "interne": chemin,
        "bilingue": True,  # les pages d'ensemble existent dans les deux langues (comme au sitemap)
        "meta": [],
        "corps": "\n".join(corps),
        "liens": liens,
        "image": f"{settings.FRONTEND_URL}/partage-image/defaut.png" + ("?lang=en" if langue == "en" else ""),
    }
