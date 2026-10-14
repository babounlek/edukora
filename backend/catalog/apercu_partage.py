"""Aperçu d'un lien partagé (WhatsApp, Facebook, Telegram...) : titre, description et image propres
à l'épreuve ou au cours, au lieu de la carte générique du site.

Le frontend est une SPA servie en statique : les balises Open Graph de chaque page sont posées en
JavaScript (voir frontend/src/lib/seo.ts), que les robots d'aperçu n'exécutent pas. Ils ne voient
donc que celles d'index.html, les mêmes pour tous les liens. Caddy détecte ces robots par leur
User-Agent et leur envoie la page ici, qui ne contient que des balises <meta> (voir
docker/caddy/Caddyfile). Les visiteurs, eux, ne passent jamais par cette vue.

L'image est dessinée à la demande avec Pillow (1200x630, le format attendu par les messageries).

Chaque page existe en français (`/cm/epreuves/x`) et en anglais (`/en/cm/epreuves/x`) : l'aperçu suit le
préfixe de l'URL - textes, `og:locale`, `<html lang>`, lien canonique et image (`?lang=en`).
"""
import re
from functools import lru_cache
from io import BytesIO

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.html import escape

from inedit.models import EpreuveInedite

from .libelles import libelle_cursus
from .models import Cours, Lesson, StatutContenu

LARGEUR, HAUTEUR = 1200, 630

_CHEMIN_RE = re.compile(
    r"^(?:(?P<langue>en)/)?(?:(?P<pays>[a-z]{2})/)?(?P<genre>epreuves|cours|epreuves-inedites)/(?P<ident>[^/]+)(?:/lire)?$"
)

# Textes de l'aperçu par langue. Les titres viennent du contenu lui-même (déjà dans sa langue) ;
# seul le texte du gabarit est traduit.
TEXTES = {
    "fr": {
        "defaut_description": (
            "Chaque jour, on te dit quoi réviser pour le BEPC, le Probatoire et le BAC : "
            "corrigés d'annales et quiz rédigés par des enseignants."
        ),
        "defaut_titre_page": "Corrigés BEPC, Probatoire et BAC",
        "defaut_titre_image": "Chaque jour, on te dit quoi réviser",
        "defaut_etiquette": "BEPC · Probatoire · BAC",
        "epreuve_description": "{type} de {matiere}{annee} - sujet en accès libre, corrigé détaillé par abonnement.",
        "cours_description": "Cours de {matiere}{theme} : méthode, exemple résolu, erreurs classiques et exercices d'appropriation.",
        "inedite_description": "{matiere} - épreuve inédite originale conçue par {site}, jamais tirée des annales.",
        "cours_etiquette": "Cours · {matiere}",
        "inedite_etiquette": "Épreuve inédite · {matiere}",
        "types": {},
    },
    "en": {
        "defaut_description": (
            "Every day, we tell you what to revise for your exam: GCE O Level and A Level past papers "
            "with detailed corrections, and quizzes written by teachers."
        ),
        "defaut_titre_page": "GCE, BEPC, Probatoire and BAC corrections",
        "defaut_titre_image": "Know what to revise, every day",
        "defaut_etiquette": "GCE O Level · A Level",
        "epreuve_description": "{type} - {matiere}{annee} - free access to the paper, detailed correction with a subscription.",
        "cours_description": "{matiere} lesson{theme}: method, worked example, classic mistakes and practice exercises.",
        "inedite_description": "{matiere} - original practice paper written by {site}, never taken from past papers.",
        "cours_etiquette": "Lesson · {matiere}",
        "inedite_etiquette": "Original paper · {matiere}",
        "types": {"FICHE": "Revision sheet", "CORR": "Past paper with correction", "SUJET": "Original paper"},
    },
}

LOCALES_OG = {"fr": "fr_FR", "en": "en_GB"}


def _image_url(genre, ident, langue="fr"):
    suffixe = "?lang=en" if langue == "en" else ""
    return f"{settings.FRONTEND_URL}/partage-image/{genre}/{ident}.png{suffixe}"


def _infos_epreuve(ident, langue="fr"):
    lesson = (
        Lesson.objects.visibles().par_slug_ou_id(ident)
        .select_related("subject").prefetch_related("cursus__series").first()
    )
    if not lesson:
        return None
    textes = TEXTES[langue]
    public = libelle_cursus(lesson.cursus.all())
    annee = f" ({lesson.year})" if lesson.year else ""
    type_affiche = textes["types"].get(lesson.lesson_type) or lesson.get_lesson_type_display()
    return {
        "titre": lesson.title,
        "description": textes["epreuve_description"].format(type=type_affiche, matiere=lesson.subject.label, annee=annee),
        "etiquette": f"{type_affiche} · {lesson.subject.label}" + (f" · {lesson.year}" if lesson.year else ""),
        "public": public,
        "chemin": f"epreuves/{lesson.slug}",
        "image": _image_url("epreuves", lesson.slug, langue),
    }


def _infos_cours(ident, langue="fr"):
    cours = Cours.objects.visibles().par_slug_ou_id(ident).select_related("subject").first()
    if not cours:
        return None
    textes = TEXTES[langue]
    theme = f" - {cours.sous_theme}" if cours.sous_theme else ""
    return {
        "titre": cours.titre,
        "description": textes["cours_description"].format(matiere=cours.subject.label, theme=theme),
        "etiquette": textes["cours_etiquette"].format(matiere=cours.subject.label),
        "public": "",
        "chemin": f"cours/{cours.slug}",
        "image": _image_url("cours", cours.slug, langue),
    }


def _infos_inedite(ident, langue="fr"):
    qs = EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE, cursus__country__actif=True)
    qs = qs.filter(pk=ident) if ident.isdigit() else qs.filter(slug=ident)
    epreuve = qs.select_related("subject").prefetch_related("cursus__series", "cursus__country").distinct().first()
    if not epreuve:
        return None
    textes = TEXTES[langue]
    pays = epreuve.cursus.first().country.code.lower()
    return {
        "titre": epreuve.titre,
        "description": textes["inedite_description"].format(matiere=epreuve.subject.label, site=settings.SITE_NAME),
        "etiquette": textes["inedite_etiquette"].format(matiere=epreuve.subject.label),
        "public": libelle_cursus(epreuve.cursus.all()),
        "chemin": f"{pays}/epreuves-inedites/{epreuve.slug}",
        "image": _image_url("inedites", epreuve.slug, langue),
    }


_RESOLVEURS = {"epreuves": _infos_epreuve, "cours": _infos_cours, "epreuves-inedites": _infos_inedite}


def langue_du_chemin(chemin):
    """« en » pour un chemin sous le préfixe /en, « fr » sinon."""
    return "en" if re.match(r"^en(/|$)", chemin.strip("/")) else "fr"


def infos_page(chemin):
    """Les informations d'aperçu pour un chemin de page du frontend (sans « / » initial), ou None.

    Un chemin sous `en/` donne l'aperçu anglais : textes du gabarit, image `?lang=en` et chemin
    canonique préfixé (`en/cm/epreuves/x`)."""
    m = _CHEMIN_RE.match(chemin.strip("/"))
    if not m:
        return None
    langue = "en" if m.group("langue") else "fr"
    infos = _RESOLVEURS[m.group("genre")](m.group("ident"), langue)
    if infos and m.group("pays") and m.group("genre") == "epreuves":
        infos["chemin"] = f"{m.group('pays')}/{infos['chemin']}"
    if infos and langue == "en":
        infos["chemin"] = f"en/{infos['chemin']}"
    return infos


def apercu_partage(request, chemin=""):
    infos = infos_page(chemin)
    site = settings.SITE_NAME
    langue = langue_du_chemin(chemin)
    textes = TEXTES[langue]
    if infos:
        titre = f"{infos['titre']} | {site}"
        description = infos["description"]
        url = f"{settings.FRONTEND_URL}/{infos['chemin']}"
        image = infos["image"]
    else:
        titre = f"{site} - {textes['defaut_titre_page']}"
        description = textes["defaut_description"]
        url = f"{settings.FRONTEND_URL}/{chemin.strip('/')}".rstrip("/")
        image = f"{settings.FRONTEND_URL}/partage-image/defaut.png" + ("?lang=en" if langue == "en" else "")

    t, d, u, i = escape(titre), escape(description), escape(url), escape(image)
    html = (
        f'<!doctype html><html lang="{langue}"><head><meta charset="utf-8">'
        f"<title>{t}</title>"
        f'<meta name="description" content="{d}">'
        f'<link rel="canonical" href="{u}">'
        f'<meta property="og:site_name" content="{escape(site)}">'
        f'<meta property="og:type" content="website"><meta property="og:locale" content="{LOCALES_OG[langue]}">'
        f'<meta property="og:url" content="{u}">'
        f'<meta property="og:title" content="{t}">'
        f'<meta property="og:description" content="{d}">'
        f'<meta property="og:image" content="{i}">'
        f'<meta property="og:image:width" content="{LARGEUR}"><meta property="og:image:height" content="{HAUTEUR}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{t}">'
        f'<meta name="twitter:description" content="{d}">'
        f'<meta name="twitter:image" content="{i}">'
        f'</head><body><p><a href="{u}">{t}</a></p></body></html>'
    )
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "public, max-age=300"
    return response


# --- Image -------------------------------------------------------------------------------------

_POLICES_GRAS = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "C:/Windows/Fonts/georgiab.ttf",
]
_POLICES_NORMALES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


@lru_cache(maxsize=32)
def _police(gras, taille):
    from PIL import ImageFont

    for chemin in _POLICES_GRAS if gras else _POLICES_NORMALES:
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            continue
    return ImageFont.load_default(size=taille)


def _lignes(draw, texte, police, largeur_max, max_lignes):
    """Retour à la ligne par mots ; le texte trop long est tronqué par « … » sur la dernière ligne."""
    mots = texte.split()
    lignes, courante = [], ""
    for i, mot in enumerate(mots):
        essai = f"{courante} {mot}".strip()
        if draw.textlength(essai, font=police) <= largeur_max or not courante:
            courante = essai
            continue
        lignes.append(courante)
        courante = mot
        if len(lignes) == max_lignes:
            break
    else:
        lignes.append(courante)
        return lignes
    derniere = lignes[max_lignes - 1]
    while derniere and draw.textlength(derniere + "…", font=police) > largeur_max:
        derniere = derniere[:-1].rstrip()
    lignes[max_lignes - 1] = derniere + "…"
    return lignes[:max_lignes]


def dessiner_carte(titre, etiquette="", public=""):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (LARGEUR, HAUTEUR), "#0a6e4e")
    calque = Image.new("RGBA", (LARGEUR, HAUTEUR), (0, 0, 0, 0))
    ImageDraw.Draw(calque).ellipse((LARGEUR - 420, -260, LARGEUR + 180, 340), fill=(255, 255, 255, 22))
    image.paste(calque, (0, 0), calque)
    draw = ImageDraw.Draw(image)

    marge = 80
    draw.text((marge, 70), settings.SITE_NAME, font=_police(True, 48), fill="#ffffff")
    if etiquette:
        draw.text((marge, 150), etiquette, font=_police(False, 34), fill="#f5c84b")

    police_titre = _police(True, 68)
    lignes = _lignes(draw, titre, police_titre, LARGEUR - 2 * marge, 4)
    y = 230
    for ligne in lignes:
        draw.text((marge, y), ligne, font=police_titre, fill="#ffffff")
        y += 86

    if public:
        draw.text((marge, HAUTEUR - 130), public, font=_police(False, 34), fill=(255, 255, 255, 230))
    draw.text(
        (marge, HAUTEUR - 80), settings.FRONTEND_URL.replace("https://", "").replace("http://", ""),
        font=_police(False, 30), fill="#d6efe6",
    )
    tampon = BytesIO()
    image.save(tampon, "PNG", optimize=True)
    return tampon.getvalue()


def image_partage(request, genre, ident):
    langue = "en" if request.GET.get("lang") == "en" else "fr"
    if genre == "defaut":
        textes = TEXTES[langue]
        infos = {"titre": textes["defaut_titre_image"], "etiquette": textes["defaut_etiquette"], "public": ""}
    else:
        resolveur = {"epreuves": _infos_epreuve, "cours": _infos_cours, "inedites": _infos_inedite}.get(genre)
        infos = resolveur(ident, langue) if resolveur else None
    if not infos:
        raise Http404("Aperçu introuvable.")
    png = dessiner_carte(infos["titre"], infos["etiquette"], infos["public"])
    response = HttpResponse(png, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response
