"""Aperçu d'un lien partagé (WhatsApp, Facebook, Telegram...) : titre, description et image propres
à l'épreuve ou au cours, au lieu de la carte générique du site.

Le frontend est une SPA servie en statique : les balises Open Graph de chaque page sont posées en
JavaScript (voir frontend/src/lib/seo.ts), que les robots d'aperçu n'exécutent pas. Ils ne voient
donc que celles d'index.html, les mêmes pour tous les liens. Caddy détecte ces robots par leur
User-Agent et leur envoie la page ici, qui ne contient que des balises <meta> (voir
docker/caddy/Caddyfile). Les visiteurs, eux, ne passent jamais par cette vue.

L'image est dessinée à la demande avec Pillow (1200x630, le format attendu par les messageries).

Chaque page existe en français (`/cm/epreuves/x`) et en anglais (`/en/cm/past-papers/x`, segments traduits :
voir segments_url) : l'aperçu suit le préfixe de l'URL - textes, `og:locale`, `<html lang>`, lien canonique et
image (`?lang=en`). Une ancienne forme française sous `/en` (`/en/cm/epreuves/x`) reçoit le même aperçu, dont le
canonical est la forme anglaise.
"""
import re
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.html import escape

from inedit.models import EpreuveInedite

from .libelles import libelle_cursus
from .models import Cours, Cursus, Lesson, StatutContenu, Subject, Tag
from .segments_url import chemin_anglais, chemin_interne

LARGEUR, HAUTEUR = 1200, 630

# Le chemin INTERNE (français, sans le préfixe /en) : l'URL publique anglaise y est ramenée d'abord (voir infos_page).
_CHEMIN_RE = re.compile(
    r"^(?:(?P<pays>[a-z]{2})/)?(?P<genre>epreuves|cours|epreuves-inedites)/(?P<ident>[^/]+)(?:/lire)?$"
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
        "quiz_titre": "Quiz gratuit : {theme}",
        "quiz_description": "{n} questions de {matiere} ({public}) : un quiz gratuit, sans compte, avec le corrigé de chaque question.",
        "quiz_etiquette": "Quiz gratuit · {matiere}",
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
        "quiz_titre": "Free quiz: {theme}",
        "quiz_description": "{n} questions on {matiere} ({public}): a free quiz, no account needed, with the correction of every question.",
        "quiz_etiquette": "Free quiz · {matiere}",
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


def _infos_quiz_essai(cursus_id, subject_id, theme_id, langue="fr"):
    """Le quiz gratuit partagé (/quiz/essai/<cursus>/<matière>/<thème>) : le nom du thème, la matière et le public
    visé. Même garde que le lancement de l'essai : un périmètre qui n'est pas entièrement gratuit n'a pas d'aperçu
    propre (lien périmé ou identifiants inventés : carte générique)."""
    from quiz.services import perimetre_est_vitrine, _items_eligibles

    cursus = Cursus.objects.filter(pk=cursus_id, country__actif=True).select_related("country", "series").first()
    subject = Subject.objects.filter(pk=subject_id).first()
    theme = Tag.objects.filter(pk=theme_id).first()
    if not (cursus and subject and theme) or not perimetre_est_vitrine(cursus, subject=subject, theme=theme):
        return None
    textes = TEXTES[langue]
    n = len(_items_eligibles(cursus, subject=subject, theme=theme))
    public = libelle_cursus([cursus])
    return {
        "titre": textes["quiz_titre"].format(theme=theme.name),
        "titre_carte": theme.name,  # l'étiquette de la carte dit déjà « Quiz gratuit »
        "description": textes["quiz_description"].format(n=n, matiere=subject.label, public=public),
        "etiquette": textes["quiz_etiquette"].format(matiere=subject.label),
        "public": public,
        "chemin": f"quiz/essai/{cursus.id}/{subject.id}/{theme.id}",
        "image": _image_url("quiz", f"{cursus.id}-{subject.id}-{theme.id}", langue),
    }


_RESOLVEURS = {"epreuves": _infos_epreuve, "cours": _infos_cours, "epreuves-inedites": _infos_inedite}
# Le quiz gratuit n'a ni pays ni slug dans son adresse : trois identifiants numériques.
_QUIZ_ESSAI_RE = re.compile(r"^quiz/essai/(\d+)/(\d+)/(\d+)$")


def langue_du_chemin(chemin):
    """« en » pour un chemin sous le préfixe /en, « fr » sinon."""
    return "en" if re.match(r"^en(/|$)", chemin.strip("/")) else "fr"


def infos_page(chemin):
    """Les informations d'aperçu pour un chemin de page du frontend (sans « / » initial), ou None.

    Un chemin sous `en/` donne l'aperçu anglais : textes du gabarit, image `?lang=en` et chemin
    canonique public (`en/cm/past-papers/x`)."""
    langue = langue_du_chemin(chemin)
    brut = chemin.strip("/")
    interne = chemin_interne("/" + re.sub(r"^en(/|$)", "", brut)).strip("/") if langue == "en" else brut
    quiz = _QUIZ_ESSAI_RE.match(interne)
    if quiz:
        infos = _infos_quiz_essai(*map(int, quiz.groups()), langue)
        if infos and langue == "en":
            infos["chemin"] = "en" + chemin_anglais("/" + infos["chemin"])
        return infos
    m = _CHEMIN_RE.match(interne)
    if not m:
        return None
    infos = _RESOLVEURS[m.group("genre")](m.group("ident"), langue)
    if infos and m.group("pays") and m.group("genre") == "epreuves":
        infos["chemin"] = f"{m.group('pays')}/{infos['chemin']}"
    if infos and langue == "en":
        infos["chemin"] = "en" + chemin_anglais("/" + infos["chemin"])
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
        f'<meta property="og:image:alt" content="{t}">'
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
# Identité visuelle : logos PNG et polices (Fraunces, Work Sans) fournis par frontend/scripts/brand/build-brand.mjs
# dans static/catalog/marque/. À défaut (fichier absent, police illisible), la carte se dessine avec les polices
# du système et le nom du site en texte : un aperçu dégradé vaut mieux qu'une erreur 500 sur un lien partagé.

MARQUE = Path(__file__).resolve().parent / "static" / "catalog" / "marque"
FOND = "#064a2b"  # vert profond : le vert clair #39B54A du logo y reste net (contraste ~3,9:1)
HALO = "#006837"  # vert institutionnel
GOLD = "#f5c84b"
CLAIR = "#d6efe6"
SLOGANS = {"fr": "RÉUSSIS TON EXAMEN", "en": "PASS YOUR EXAM"}

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
# Ce que couvre le sous-ensemble latin des polices de la marque ; un titre qui en sort (lettres grecques d'un
# énoncé de maths, par exemple) se dessine avec la police du système, qui a plus de glyphes.
_COUVERT_PAR_MARQUE = re.compile("^[\u0000-\u00ff\u0131\u0152\u0153\u2000-\u206f\u20ac\u2122\u2212]*$")


@lru_cache(maxsize=32)
def _police(gras, taille, marque=None):
    """`marque` : nom d'un fichier de static/catalog/marque/ à préférer aux polices du système."""
    from PIL import ImageFont

    candidats = ([str(MARQUE / marque)] if marque else []) + (_POLICES_GRAS if gras else _POLICES_NORMALES)
    for chemin in candidats:
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            continue
    return ImageFont.load_default(size=taille)


@lru_cache(maxsize=8)
def _logo(nom):
    """Le PNG de logo (RGBA), ou None s'il manque."""
    from PIL import Image

    try:
        return Image.open(MARQUE / nom).convert("RGBA")
    except OSError:
        return None


def _poser_logo(image, nom, largeur=None, hauteur=None, x=0, y=0):
    """Colle le logo `nom` à (x, y), à la largeur ou à la hauteur donnée. Retourne (largeur, hauteur), ou None sans logo."""
    from PIL import Image

    logo = _logo(nom)
    if logo is None:
        return None
    if largeur:
        taille = (largeur, round(logo.height * largeur / logo.width))
    else:
        taille = (round(logo.width * hauteur / logo.height), hauteur)
    reduit = logo.resize(taille, Image.LANCZOS)
    image.paste(reduit, (x, y), reduit)
    return taille


def _texte_espace(draw, xy, texte, police, fill, interlettre, droite=False):
    """Texte en capitales espacées, à gauche de `xy` ou, avec `droite`, calé à droite."""
    x, y = xy
    largeur = sum(draw.textlength(c, font=police) + interlettre for c in texte) - interlettre
    if droite:
        x -= largeur
    for c in texte:
        draw.text((x, y), c, font=police, fill=fill)
        x += draw.textlength(c, font=police) + interlettre


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


def _rgb(couleur):
    return tuple(int(couleur[i:i + 2], 16) for i in (1, 3, 5))


def dessiner_carte(titre, etiquette="", public="", langue="fr", generique=False):
    """La carte 1200x630 d'un lien partagé. `generique` : la carte du site entier (le logo complet, avec son slogan,
    occupe le haut) plutôt que celle d'une page (logo compact en haut à gauche, slogan en bas à droite)."""
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    calque = Image.new("RGBA", (LARGEUR, HAUTEUR), (0, 0, 0, 0))
    ImageDraw.Draw(calque).ellipse((LARGEUR - 460, -300, LARGEUR + 200, 360), fill=(*_rgb(HALO), 150))
    image.paste(calque, (0, 0), calque)
    draw = ImageDraw.Draw(image)

    marge = 80
    police_titre = _police(True, 64, "fraunces-latin-700-normal.woff") if _COUVERT_PAR_MARQUE.match(titre) else _police(True, 64)
    police_texte = _police(False, 34, "work-sans-latin-500-normal.woff")

    if generique:
        logo = _poser_logo(image, f"logo-{langue}.png", largeur=780, x=marge, y=64)
        y = 64 + (logo[1] if logo else 0) + 44
        if not logo:
            draw.text((marge, 64), settings.SITE_NAME, font=_police(True, 96), fill="#ffffff")
            y = 64 + 96 + 44
        for ligne in _lignes(draw, titre, police_titre, LARGEUR - 2 * marge, 2):
            draw.text((marge, y), ligne, font=police_titre, fill="#ffffff")
            y += 78
        if etiquette:
            draw.text((marge, y + 14), etiquette, font=police_texte, fill=GOLD)
    else:
        logo = _poser_logo(image, "logo-minimal.png", hauteur=76, x=marge, y=56)
        if not logo:
            draw.text((marge, 70), settings.SITE_NAME, font=_police(True, 48), fill="#ffffff")
        if etiquette:
            draw.text((marge, 160), etiquette, font=police_texte, fill=GOLD)
        y = 225
        for ligne in _lignes(draw, titre, police_titre, LARGEUR - 2 * marge, 3):
            draw.text((marge, y), ligne, font=police_titre, fill="#ffffff")
            y += 78
        if public:
            draw.text((marge, HAUTEUR - 142), public, font=police_texte, fill="#ffffff")

    # Pied : l'adresse du site ; le slogan, à droite, sur les cartes de page
    # (la carte générique l'a déjà dans son logo).
    url = settings.FRONTEND_URL.replace("https://", "").replace("http://", "")
    draw.text((marge, HAUTEUR - 80), url, font=_police(False, 30, "work-sans-latin-500-normal.woff"), fill=CLAIR)
    if not generique:
        _texte_espace(
            draw, (LARGEUR - marge, HAUTEUR - 76), SLOGANS[langue], _police(False, 26, "work-sans-latin-600-normal.woff"),
            "#bfe5c6", 5, droite=True,
        )
    tampon = BytesIO()
    image.save(tampon, "PNG", optimize=True)
    return tampon.getvalue()


def image_partage(request, genre, ident):
    langue = "en" if request.GET.get("lang") == "en" else "fr"
    if genre == "defaut":
        textes = TEXTES[langue]
        infos = {"titre": textes["defaut_titre_image"], "etiquette": textes["defaut_etiquette"], "public": ""}
    elif genre == "quiz":
        ids = re.fullmatch(r"(\d+)-(\d+)-(\d+)", ident)
        infos = _infos_quiz_essai(*map(int, ids.groups()), langue) if ids else None
    else:
        resolveur = {"epreuves": _infos_epreuve, "cours": _infos_cours, "inedites": _infos_inedite}.get(genre)
        infos = resolveur(ident, langue) if resolveur else None
    if not infos:
        raise Http404("Aperçu introuvable.")
    png = dessiner_carte(infos.get("titre_carte", infos["titre"]), infos["etiquette"], infos["public"], langue, generique=genre == "defaut")
    response = HttpResponse(png, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response
