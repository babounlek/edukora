"""Aperçu d'un lien partagé (WhatsApp, Facebook, Telegram...) : titre, description et image propres
à l'épreuve ou au cours, au lieu de la carte générique du site.

Le frontend est une SPA servie en statique : les balises Open Graph de chaque page sont posées en
JavaScript (voir frontend/src/lib/seo.ts), que les robots d'aperçu n'exécutent pas. Ils ne voient
donc que celles d'index.html, les mêmes pour tous les liens. Caddy détecte ces robots par leur
User-Agent et leur envoie la page ici, qui ne contient que des balises <meta> (voir
docker/caddy/Caddyfile). Les visiteurs, eux, ne passent jamais par cette vue.

L'image est dessinée à la demande avec Pillow (1200x630, le format attendu par les messageries).
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
    r"^(?:(?P<pays>[a-z]{2})/)?(?P<genre>epreuves|cours|epreuves-inedites)/(?P<ident>[^/]+)(?:/lire)?$"
)

DESCRIPTION_DEFAUT = (
    "Chaque jour, on te dit quoi réviser pour le BEPC, le Probatoire et le BAC : "
    "corrigés d'annales et quiz rédigés par des enseignants."
)


def _image_url(genre, ident):
    return f"{settings.FRONTEND_URL}/partage-image/{genre}/{ident}.png"


def _infos_epreuve(ident):
    lesson = (
        Lesson.objects.visibles().par_slug_ou_id(ident)
        .select_related("subject").prefetch_related("cursus__series").first()
    )
    if not lesson:
        return None
    public = libelle_cursus(lesson.cursus.all())
    annee = f" ({lesson.year})" if lesson.year else ""
    return {
        "titre": lesson.title,
        "description": (
            f"{lesson.get_lesson_type_display()} de {lesson.subject.label}{annee} - "
            "sujet en accès libre, corrigé détaillé par abonnement."
        ),
        "etiquette": f"{lesson.get_lesson_type_display()} · {lesson.subject.label}" + (f" · {lesson.year}" if lesson.year else ""),
        "public": public,
        "chemin": f"epreuves/{lesson.slug}",
        "image": _image_url("epreuves", lesson.slug),
    }


def _infos_cours(ident):
    cours = Cours.objects.visibles().par_slug_ou_id(ident).select_related("subject").first()
    if not cours:
        return None
    theme = f" - {cours.sous_theme}" if cours.sous_theme else ""
    return {
        "titre": cours.titre,
        "description": (
            f"Cours de {cours.subject.label}{theme} : méthode, exemple résolu, "
            "erreurs classiques et exercices d'appropriation."
        ),
        "etiquette": f"Cours · {cours.subject.label}",
        "public": "",
        "chemin": f"cours/{cours.slug}",
        "image": _image_url("cours", cours.slug),
    }


def _infos_inedite(ident):
    qs = EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE, cursus__country__actif=True)
    qs = qs.filter(pk=ident) if ident.isdigit() else qs.filter(slug=ident)
    epreuve = qs.select_related("subject").prefetch_related("cursus__series", "cursus__country").distinct().first()
    if not epreuve:
        return None
    pays = epreuve.cursus.first().country.code.lower()
    return {
        "titre": epreuve.titre,
        "description": f"{epreuve.subject.label} - épreuve inédite originale conçue par {settings.SITE_NAME}, jamais tirée des annales.",
        "etiquette": f"Épreuve inédite · {epreuve.subject.label}",
        "public": libelle_cursus(epreuve.cursus.all()),
        "chemin": f"{pays}/epreuves-inedites/{epreuve.slug}",
        "image": _image_url("inedites", epreuve.slug),
    }


_RESOLVEURS = {"epreuves": _infos_epreuve, "cours": _infos_cours, "epreuves-inedites": _infos_inedite}


def infos_page(chemin):
    """Les informations d'aperçu pour un chemin de page du frontend (sans « / » initial), ou None."""
    m = _CHEMIN_RE.match(chemin.strip("/"))
    if not m:
        return None
    infos = _RESOLVEURS[m.group("genre")](m.group("ident"))
    if infos and m.group("pays") and m.group("genre") == "epreuves":
        infos["chemin"] = f"{m.group('pays')}/{infos['chemin']}"
    return infos


def apercu_partage(request, chemin=""):
    infos = infos_page(chemin)
    site = settings.SITE_NAME
    if infos:
        titre = f"{infos['titre']} | {site}"
        description = infos["description"]
        url = f"{settings.FRONTEND_URL}/{infos['chemin']}"
        image = infos["image"]
    else:
        titre = f"{site} - Corrigés BEPC, Probatoire et BAC"
        description = DESCRIPTION_DEFAUT
        url = f"{settings.FRONTEND_URL}/{chemin.strip('/')}".rstrip("/")
        image = f"{settings.FRONTEND_URL}/partage-image/defaut.png"

    t, d, u, i = escape(titre), escape(description), escape(url), escape(image)
    html = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        f"<title>{t}</title>"
        f'<meta name="description" content="{d}">'
        f'<link rel="canonical" href="{u}">'
        f'<meta property="og:site_name" content="{escape(site)}">'
        '<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR">'
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
    if genre == "defaut":
        infos = {"titre": "Chaque jour, on te dit quoi réviser", "etiquette": "BEPC · Probatoire · BAC", "public": ""}
    else:
        resolveur = {"epreuves": _infos_epreuve, "cours": _infos_cours, "inedites": _infos_inedite}.get(genre)
        infos = resolveur(ident) if resolveur else None
    if not infos:
        raise Http404("Aperçu introuvable.")
    png = dessiner_carte(infos["titre"], infos["etiquette"], infos["public"])
    response = HttpResponse(png, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response
