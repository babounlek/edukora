"""Pages prérendues pour les moteurs de recherche (Googlebot, Bingbot...).

Le frontend est une SPA : le HTML d'origine est le même pour toutes les pages (titre générique, aucun texte), et
le vrai contenu n'apparaît qu'après l'exécution du JavaScript et deux appels d'API. Un moteur de recherche qui
n'attend pas assez, ou qui juge le résultat trop proche d'une autre page, classe l'URL « Explorée, actuellement
non indexée » ou « Google n'a pas choisi la même URL canonique » (Search Console). Caddy détecte ces robots par
leur User-Agent et leur envoie la page ici : le HTML complet de la page - titre, description, lien canonique,
hreflang, texte - sans attendre de JavaScript (voir docker/caddy/Caddyfile). Les visiteurs n'y passent jamais.

Règle d'or : on ne sert que ce qu'un visiteur ANONYME voit déjà dans l'application. Un cours : la version libre,
sans ses exercices d'application (payants). Une épreuve : le sujet, jamais le corrigé - sauf une épreuve vitrine
(Lesson.est_vitrine), dont le corrigé est en accès libre pour un visiteur anonyme : elle sert tout le contenu du
lecteur. Une épreuve inédite :
seulement sa fiche (titre, matière, public), jamais l'énoncé. Servir autre chose serait à la fois une fuite de
contenu payant et un contenu différent de celui des visiteurs (ce que les moteurs sanctionnent).

Une page, une adresse :
- un contenu rédigé en anglais (GCE) existe en français (`/cours/x/lire`) et en anglais (`/en/lessons/x/read`),
  chacune son propre canonical, avec hreflang des deux côtés (comme le sitemap) ;
- un contenu français n'a qu'une adresse : sous `/en/...` (lien de partage, bascule de langue) le canonical est
  la forme française et aucun hreflang n'est annoncé - sinon deux pages quasi identiques se disputeraient l'index ;
- le lecteur de cours est la page canonique d'un cours (la fiche `/cours/x` y redirige les visiteurs) ; le lecteur
  d'une épreuve exige un compte, c'est donc la fiche `/<pays>/epreuves/x` qui est canonique - sauf pour une
  épreuve vitrine, dont le lecteur est ouvert à tous : c'est lui, la page canonique, comme un cours.
"""
import json
import re
from html import escape as echapper_texte

import markdown
from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.html import escape

from aide.models import ArticleAide
from inedit.models import EpreuveInedite

from . import pages_examen
from .apercu_partage import _CHEMIN_RE, LOCALES_OG, TEXTES, description_epreuve, langue_du_chemin, titre_epreuve
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


def _page_cours(ident, langue_page, pays=None):
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
        "fil": [("accueil", f"/{code_pays}"), ("liste_cours", f"/{code_pays}/cours"), (cours.titre, f"/cours/{cours.slug}/lire")],
        "liens": [("liste_cours", f"/{code_pays}/cours")],
        "image": f"{settings.FRONTEND_URL}/partage-image/cours/{cours.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


def _page_epreuve(ident, langue_page, pays=None):
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
    premier_cursus = next(iter(lesson.cursus.all()), None)
    fil = [("accueil", f"/{code_pays}")]
    if premier_cursus is not None:
        fil.append((pages_examen.libelle_examen(premier_cursus), f"/{code_pays}/examens/{pages_examen.slug_cursus(premier_cursus)}"))
    return {
        "titre": lesson.title,
        # Le <title> porte « corrigé » pour une annale corrigée ; le h1 garde le titre de l'épreuve.
        "titre_page": titre_epreuve(lesson, langue),
        "fil": fil + [(lesson.title, f"/{code_pays}/epreuves/{lesson.slug}")],
        "description": description_epreuve(
            lesson, textes, type_affiche, libelle_cursus(lesson.cursus.all()), annee,
        ),
        # Une épreuve vitrine (corrigé en accès libre, voir Lesson.est_vitrine) : le lecteur est ouvert à tous, c'est
        # lui la page canonique (comme un cours) et on y sert le corrigé complet, exactement ce que lit un visiteur
        # anonyme sur /lire (access.views.read_lesson, has_access). Les autres : la fiche et le sujet seulement.
        "interne": f"/{code_pays}/epreuves/{lesson.slug}" + ("/lire" if lesson.est_vitrine else ""),
        "bilingue": bilingue,
        "meta": [m for m in meta if m],
        # Sinon, le sujet public (voir access.views.preview_lesson) : tous les énoncés, jamais le corrigé.
        "corps": lesson.content_markdown if lesson.est_vitrine else lesson.preview_markdown(),
        "liens": [("liste_epreuves", f"/{code_pays}/epreuves")],
        "image": f"{settings.FRONTEND_URL}/partage-image/epreuves/{lesson.slug}.png" + ("?lang=en" if langue_page == "en" else ""),
    }


def _page_inedite(ident, langue_page, pays=None):
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


def _page_aide(ident, langue_page, pays=None):
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


def _page_examen(ident, langue_page, pays=None):
    """La page d'atterrissage d'un examen (voir catalog.pages_examen) : un texte d'introduction et la liste des
    épreuves récentes, avec un lien vers chacune. Une adresse sans pays n'existe pas (404)."""
    if not pays:
        return None
    donnees = pages_examen.donnees_examen(pays, ident)
    if donnees is None:
        return None
    langue = pages_examen.langue_du_contenu(donnees)
    textes = pages_examen.textes_page(donnees, langue)
    return {
        "titre": textes["titre"],
        "description": textes["description"],
        "interne": f"/{donnees['country']}/examens/{donnees['slug']}",
        "bilingue": langue == "en",
        "meta": [donnees["libelle"]],
        "fil": [("accueil", f"/{donnees['country']}"), (donnees["libelle"], f"/{donnees['country']}/examens/{donnees['slug']}")],
        "corps": pages_examen.corps_markdown(
            donnees, langue, lambda slug: chemin_public(f"/{donnees['country']}/epreuves/{slug}", langue_page),
        ),
        "liens": [("liste_epreuves", f"/{donnees['country']}/epreuves")],
        "image": f"{settings.FRONTEND_URL}/partage-image/defaut.png" + ("?lang=en" if langue_page == "en" else ""),
    }


_PAGES = {
    "epreuves": _page_epreuve, "cours": _page_cours, "epreuves-inedites": _page_inedite, "aide": _page_aide,
    "examens": _page_examen,
}

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


def _fil_d_ariane_json_ld(fil, libelles, langue_page, canonical):
    """Le balisage BreadcrumbList d'une page (Accueil > examen > épreuve), ou "" sans fil d'Ariane. `fil` : liste de
    (libellé ou clé de LIBELLES, chemin interne) ; le dernier maillon est la page elle-même (son canonical). Le même
    fil est visible sur la page (composant FilAriane) : un balisage doit refléter ce que lit le visiteur."""
    if not fil:
        return ""
    base = settings.FRONTEND_URL
    elements = []
    for position, (nom, chemin) in enumerate(fil, start=1):
        elements.append({
            "@type": "ListItem",
            "position": position,
            "name": libelles.get(nom, nom),
            "item": canonical if position == len(fil) else f"{base}{chemin_public(chemin, langue_page)}",
        })
    donnees = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}
    # « < » échappé : un titre ne doit jamais pouvoir fermer la balise <script>.
    texte = json.dumps(donnees, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{texte}</script>'


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
    page = _PAGES[m.group("genre")](m.group("ident"), langue_page, m.group("pays")) if m else None
    if not page:
        return _introuvable(langue_page)

    site = settings.SITE_NAME
    # <html lang> : la langue du TEXTE servi, qui est celle du contenu (jamais celle d'une interface qu'on ne sert pas).
    langue_texte = "en" if page["bilingue"] else "fr"
    canonical, hreflang = adresses(page, langue_page)
    titre = _sans_gabarits(page["titre"])
    description = _sans_gabarits(page["description"])
    titre_complet = f"{_sans_gabarits(page.get('titre_page', page['titre']))} | {site}"
    t, d, u, i = escape(titre_complet), escape(description), escape(canonical), escape(page["image"])
    alternates = "".join(
        f'<link rel="alternate" hreflang="{escape(lg)}" href="{escape(href)}">' for lg, href in hreflang.items()
    )
    libelles = LIBELLES[langue_page]
    json_ld = _fil_d_ariane_json_ld(page.get("fil"), libelles, langue_page, canonical)
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
        f"{json_ld}"
        f"</head><body><header><a href=\"{escape(chemin_public('/', langue_page))}\">{escape(site)}</a></header>"
        f"<main><article><h1>{escape(titre)}</h1>{meta}{corps}</article></main>"
        f"<nav><ul>{nav}</ul></nav></body></html>"
    )
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    # Réponse propre au User-Agent : jamais mise en cache par un intermédiaire (Cloudflare) pour les autres visiteurs.
    response["Cache-Control"] = "private, no-cache"
    patch_vary_headers(response, ["User-Agent"])
    return response
