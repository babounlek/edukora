"""Pages prérendues pour les moteurs de recherche (Googlebot, Bingbot...).

Le frontend est une SPA : le HTML d'origine est le même pour toutes les pages (titre générique, aucun texte), et
le vrai contenu n'apparaît qu'après l'exécution du JavaScript et deux appels d'API. Un moteur de recherche qui
n'attend pas assez, ou qui juge le résultat trop proche d'une autre page, classe l'URL « Explorée, actuellement
non indexée » ou « Google n'a pas choisi la même URL canonique » (Search Console). Caddy détecte ces robots par
leur User-Agent et leur envoie la page ici : le HTML complet de la page - titre, description, lien canonique,
hreflang, texte - sans attendre de JavaScript (voir docker/caddy/Caddyfile). Les visiteurs n'y passent jamais.

Règle d'or : on ne sert que ce qu'un visiteur ANONYME voit déjà dans l'application. Un cours : la version libre,
sans ses exercices d'application (payants). Une épreuve : le sujet, jamais le corrigé. Une épreuve inédite :
seulement sa fiche (titre, matière, public), jamais l'énoncé. Servir autre chose serait à la fois une fuite de
contenu payant et un contenu différent de celui des visiteurs (ce que les moteurs sanctionnent).

Une page, une adresse :
- un contenu rédigé en anglais (GCE) existe en français (`/cours/x/lire`) et en anglais (`/en/lessons/x/read`),
  chacune son propre canonical, avec hreflang des deux côtés (comme le sitemap) ;
- un contenu français n'a qu'une adresse : sous `/en/...` (lien de partage, bascule de langue) le canonical est
  la forme française et aucun hreflang n'est annoncé - sinon deux pages quasi identiques se disputeraient l'index ;
- le lecteur de cours est la page canonique d'un cours (la fiche `/cours/x` y redirige les visiteurs) ; le lecteur
  d'une épreuve exige un compte, c'est donc la fiche `/<pays>/epreuves/x` qui est canonique.
"""
import re
from html import escape as echapper_texte

import markdown
from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.html import escape

from aide.models import ArticleAide
from inedit.models import EpreuveInedite

from .apercu_partage import _CHEMIN_RE, LOCALES_OG, TEXTES, langue_du_chemin
from .libelles import libelle_cursus
from .models import Cours, Langue, Lesson, StatutContenu
from .segments_url import chemin_interne, chemin_public

# Les formules LaTeX sont mises à l'abri du Markdown (les `_` et `*` d'une formule seraient lus comme de
# l'italique), puis remises telles quelles, échappées : le texte reste lisible pour un robot.
_MATH_RE = re.compile(r"\$\$[\s\S]+?\$\$|\$[^$\n]+?\$")
# Renvois internes des contenus : « [Thalès](COURS_REF:theoreme-de-thales) » et le marqueur seul « [COURS_LINK:slug] ».
_RENVOI_COURS_RE = re.compile(r"\]\(COURS_REF:([^)\s]+)\)")
_MARQUEUR_COURS_RE = re.compile(r"^\[COURS_LINK:([^\]\s]+)\]\s*$", re.MULTILINE)

LIBELLES = {
    "fr": {"accueil": "Accueil", "liste_cours": "Tous les cours", "liste_epreuves": "Toutes les épreuves",
           "voir_cours": "Voir le cours", "introuvable": "Page introuvable"},
    "en": {"accueil": "Home", "liste_cours": "All lessons", "liste_epreuves": "All past papers",
           "voir_cours": "See the lesson", "introuvable": "Page not found"},
}


def _html(texte_markdown, langue_page):
    """Le Markdown d'un contenu en HTML, renvois entre cours résolus vers de vraies adresses."""
    def adresse_cours(slug):
        return chemin_public(f"/cours/{slug}/lire", langue_page)

    texte = _RENVOI_COURS_RE.sub(lambda m: f"]({adresse_cours(m.group(1))})", texte_markdown or "")
    voir = LIBELLES[langue_page]["voir_cours"]
    texte = _MARQUEUR_COURS_RE.sub(lambda m: f"[{voir}]({adresse_cours(m.group(1))})", texte)

    spans = []

    def abriter(match):
        spans.append(match.group(0))
        return f"@@MATH{len(spans) - 1}@@"

    html = markdown.markdown(_MATH_RE.sub(abriter, texte), extensions=["tables", "fenced_code", "nl2br"])
    for index, span in enumerate(spans):
        html = html.replace(f"@@MATH{index}@@", echapper_texte(span, quote=False))
    return html


def _page_cours(ident, langue_page):
    cours = Cours.objects.visibles().par_slug_ou_id(ident).select_related("subject__country").first()
    if not cours:
        return None
    bilingue = cours.subject.langue == Langue.EN
    langue = "en" if bilingue else "fr"
    header = cours.header_info()
    theme = f" - {cours.sous_theme}" if cours.sous_theme else ""
    meta = [header["matiere"], header["serie_libelle"], cours.sous_theme]
    if cours.duree_estimee_min:
        meta.append(f"{cours.duree_estimee_min} min")
    code_pays = cours.subject.country.code.lower()
    return {
        "titre": cours.titre,
        "description": TEXTES[langue]["cours_description"].format(matiere=cours.subject.label, theme=theme),
        "interne": f"/cours/{cours.slug}/lire",
        "bilingue": bilingue,
        "meta": [m for m in meta if m],
        # Ce que lit un visiteur anonyme (voir access.views.read_cours) : jamais les exercices d'application.
        "corps": cours.libre_markdown(),
        "liens": [("liste_cours", f"/{code_pays}/cours")],
        "image": f"{settings.FRONTEND_URL}/partage-image/cours/{cours.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


def _page_epreuve(ident, langue_page):
    lesson = (
        Lesson.objects.visibles().par_slug_ou_id(ident)
        .select_related("subject__country").prefetch_related("cursus__series").first()
    )
    if not lesson:
        return None
    bilingue = lesson.subject.langue == Langue.EN
    langue = "en" if bilingue else "fr"
    textes = TEXTES[langue]
    type_affiche = textes["types"].get(lesson.lesson_type) or lesson.get_lesson_type_display()
    annee = f" ({lesson.year})" if lesson.year else ""
    code_pays = lesson.subject.country.code.lower()
    meta = [type_affiche, lesson.subject.label, libelle_cursus(lesson.cursus.all()), str(lesson.year or "")]
    return {
        "titre": lesson.title,
        "description": textes["epreuve_description"].format(type=type_affiche, matiere=lesson.subject.label, annee=annee),
        "interne": f"/{code_pays}/epreuves/{lesson.slug}",
        "bilingue": bilingue,
        "meta": [m for m in meta if m],
        # Le sujet public (voir access.views.preview_lesson) : tous les énoncés, jamais le corrigé.
        "corps": lesson.preview_markdown(),
        "liens": [("liste_epreuves", f"/{code_pays}/epreuves")],
        "image": f"{settings.FRONTEND_URL}/partage-image/epreuves/{lesson.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


def _page_inedite(ident, langue_page):
    qs = EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE, cursus__country__actif=True)
    qs = qs.filter(pk=ident) if ident.isdigit() else qs.filter(slug=ident)
    epreuve = qs.select_related("subject__country").prefetch_related("cursus__series").distinct().first()
    if not epreuve:
        return None
    bilingue = epreuve.subject.langue == Langue.EN
    langue = "en" if bilingue else "fr"
    cle = "mini" if epreuve.est_mini else "inedite"
    # Même pays que celui vers lequel la page recanonicalise (EpreuveInediteDetailPage : subject.country).
    code_pays = epreuve.subject.country.code.lower()
    return {
        "titre": epreuve.titre,
        "description": TEXTES[langue][f"{cle}_description"].format(matiere=epreuve.subject.label, site=settings.SITE_NAME),
        "interne": f"/{code_pays}/epreuves-inedites/{epreuve.slug}",
        "bilingue": bilingue,
        "meta": [epreuve.subject.label, libelle_cursus(epreuve.cursus.all())],
        "corps": "",  # l'énoncé d'une inédite est réservé : seule la fiche est publique
        "liens": [("liste_epreuves", f"/{code_pays}/epreuves")],
        "image": f"{settings.FRONTEND_URL}/partage-image/inedites/{epreuve.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


def _page_aide(ident, langue_page):
    article = ArticleAide.objects.filter(slug=ident, publie=True).first()
    if not article:
        return None
    bilingue = article.traduit
    anglais = langue_page == "en" and bilingue
    return {
        "titre": article.titre_en if anglais else article.titre_fr,
        "description": article.resume_en if anglais else article.resume_fr,
        "interne": f"/aide/{article.slug}",
        "bilingue": bilingue,
        "meta": [],
        "corps": article.corps_en if anglais else article.corps_fr,
        "liens": [],
        "image": f"{settings.FRONTEND_URL}/partage-image/aide/{article.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


_PAGES = {"epreuves": _page_epreuve, "cours": _page_cours, "epreuves-inedites": _page_inedite, "aide": _page_aide}

# Le gabarit `{{site}}` des articles d'aide (les autres ne se remplissent que dans le frontend, voir apercu_partage).
_GABARIT_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _sans_gabarits(texte):
    return _GABARIT_RE.sub(lambda m: settings.SITE_NAME if m.group(1) == "site" else "", texte or "").strip()


def adresses(page, langue_page):
    """(canonical, hreflang) d'une page : voir la docstring du module. `hreflang` : {langue: url}, vide pour un
    contenu français (une seule adresse)."""
    base = settings.FRONTEND_URL
    fr = f"{base}{page['interne']}"
    if not page["bilingue"]:
        return fr, {}
    en = f"{base}{chemin_public(page['interne'], 'en')}"
    return (en if langue_page == "en" else fr), {"fr": fr, "en": en, "x-default": fr}


def _introuvable(langue_page):
    html = (
        f'<!doctype html><html lang="{langue_page}"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex">'
        f"<title>{LIBELLES[langue_page]['introuvable']} | {escape(settings.SITE_NAME)}</title></head>"
        f"<body><h1>{LIBELLES[langue_page]['introuvable']}</h1></body></html>"
    )
    return HttpResponse(html, status=404, content_type="text/html; charset=utf-8")


def prerendu(request, chemin=""):
    """La page complète à `chemin` (sans « / » initial, avec le préfixe /en le cas échéant), pour un moteur de
    recherche. 404 pour un contenu qui n'existe pas (ou plus, ou pas encore publié) : un vrai statut, plus le
    « 200 » de la SPA qui oblige les moteurs à deviner une erreur (soft 404)."""
    langue_page = langue_du_chemin(chemin)
    brut = chemin.strip("/")
    interne = chemin_interne("/" + re.sub(r"^en(/|$)", "", brut)).strip("/") if langue_page == "en" else brut
    m = _CHEMIN_RE.match(interne)
    page = _PAGES[m.group("genre")](m.group("ident"), langue_page) if m else None
    if not page:
        return _introuvable(langue_page)

    site = settings.SITE_NAME
    # <html lang> : la langue du TEXTE servi, qui est celle du contenu (jamais celle d'une interface qu'on ne sert pas).
    langue_texte = "en" if page["bilingue"] else "fr"
    canonical, hreflang = adresses(page, langue_page)
    titre = _sans_gabarits(page["titre"])
    description = _sans_gabarits(page["description"])
    titre_complet = f"{titre} | {site}"
    t, d, u, i = escape(titre_complet), escape(description), escape(canonical), escape(page["image"])
    alternates = "".join(
        f'<link rel="alternate" hreflang="{escape(lg)}" href="{escape(href)}">' for lg, href in hreflang.items()
    )
    libelles = LIBELLES[langue_page]
    meta = f"<p>{escape(' · '.join(page['meta']))}</p>" if page["meta"] else ""
    corps = _html(_sans_gabarits(page["corps"]) if page["corps"] else "", langue_page)
    liens = [(libelles["accueil"], chemin_public("/", langue_page))] + [
        (libelles[cle], chemin_public(href, langue_page)) for cle, href in page["liens"]
    ]
    nav = "".join(f'<li><a href="{escape(href)}">{escape(libelle)}</a></li>' for libelle, href in liens)

    html = (
        f'<!doctype html><html lang="{langue_texte}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{t}</title>"
        f'<meta name="description" content="{d}">'
        f'<link rel="canonical" href="{u}">'
        f"{alternates}"
        f'<meta property="og:site_name" content="{escape(site)}">'
        f'<meta property="og:type" content="article"><meta property="og:locale" content="{LOCALES_OG[langue_texte]}">'
        f'<meta property="og:url" content="{u}">'
        f'<meta property="og:title" content="{t}">'
        f'<meta property="og:description" content="{d}">'
        f'<meta property="og:image" content="{i}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f"</head><body><header><a href=\"{escape(chemin_public('/', langue_page))}\">{escape(site)}</a></header>"
        f"<main><article><h1>{escape(titre)}</h1>{meta}{corps}</article></main>"
        f"<nav><ul>{nav}</ul></nav></body></html>"
    )
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    # Réponse propre au User-Agent : jamais mise en cache par un intermédiaire (Cloudflare) pour les autres visiteurs.
    response["Cache-Control"] = "private, no-cache"
    patch_vary_headers(response, ["User-Agent"])
    return response
