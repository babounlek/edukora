"""
PDF d'un cours, à télécharger ou à imprimer.

Deux versions d'un même cours, comme à l'écran (voir access.views.read_cours) :
  - « libre » : le cours SANS ses exercices d'application, payants (Cours.libre_markdown) ; la seule que reçoit un
    visiteur ou un connecté sans abonnement sur le cursus du cours ;
  - « complet » : le cours avec ses exercices et leurs solutions (Cours.content_markdown), pour un abonné.
La version n'est JAMAIS choisie par le client : elle découle de l'accès (variante_pour), sinon le PDF serait un
second chemin vers les exercices payants.

Un cache plutôt qu'un PDF pré-généré : il y a plusieurs milliers de cours, mais seuls quelques-uns sont réellement
téléchargés. Le premier téléchargement lance la génération dans un processus détaché (même contrainte que
catalog.sujet_pdf : Playwright ne tourne jamais dans le thread d'une requête), le client réessaie jusqu'à ce que le
fichier existe. Le nom du fichier porte l'empreinte du contenu : un cours corrigé change d'empreinte, l'ancien PDF
n'est plus servi et est supprimé à la génération suivante.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import markdown
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.template.loader import render_to_string

from catalog.libelles import matiere_dans_titre
from catalog.pdf_textes import langue_du_contenu, nom_pays, textes_pdf
from catalog.rendering import SECTIONS_PAYANTES_COURS
from catalog.segments_url import chemin_public
from catalog.sujet_pdf import (
    _FLAGS_DIR,
    _KATEX_DIR,
    _italicize_quotes,
    _protect_math,
    _qr_code_data_uri,
    _resolve_media_paths,
    _restore_math,
    html_vers_pdf,
)

LIBRE = "libre"
COMPLET = "complet"
VARIANTES = (LIBRE, COMPLET)

# À incrémenter quand le gabarit ou le rendu change : toutes les empreintes changent, les PDF déjà en cache ne sont
# plus servis.
VERSION_GABARIT = "1"

# Chromium est lourd : au plus ce nombre de générations en même temps, quel que soit le nombre de visiteurs.
MAX_GENERATIONS_SIMULTANEES = 2
# Un verrou plus vieux que cela est celui d'un processus mort (crash, redémarrage du conteneur).
VERROU_PERIME_S = 240
# Après un échec, on ne relance pas la même génération avant ce délai (sinon le client la relancerait à chaque essai).
ECHEC_PAUSE_S = 600

EN_PREPARATION = "en_preparation"
OCCUPE = "occupe"
ECHEC = "echec"


def stockage():
    return storages["cours_protected"]


def variante_pour(a_acces_exercices):
    return COMPLET if a_acces_exercices else LIBRE


def markdown_du_cours(cours, variante):
    return cours.content_markdown if variante == COMPLET else cours.libre_markdown()


def empreinte(cours, variante):
    """Identifie le contenu rendu sans le calculer : la version libre dérive de sections_raw, la complète de
    content_markdown (voir markdown_du_cours)."""
    source = cours.content_markdown if variante == COMPLET else json.dumps(
        [s for s in cours.sections_raw if s.get("type") not in SECTIONS_PAYANTES_COURS], sort_keys=True, ensure_ascii=False,
    )
    brut = f"{VERSION_GABARIT}\n{variante}\n{cours.titre}\n{source}"
    return hashlib.sha1(brut.encode("utf-8")).hexdigest()[:12]


def nom_fichier(cours, variante):
    return f"{variante}/{cours.pk}-{empreinte(cours, variante)}.pdf"


# --- Rendu -----------------------------------------------------------------------------------------------------

# Les titres que le rendu des sections écrit en français (catalog.rendering._render_cours_section), même pour un cours
# du GCE : le contenu est en anglais, pas ces repères. Mêmes mots que les étiquettes du site (cs.* du frontend).
_TITRES_EN = {
    "## Prérequis": "## Prerequisites",
    "## La règle": "## The rule",
    "## Exemple résolu": "## Worked example",
    "## Erreurs classiques": "## Common mistakes",
    "### Erreur": "### Mistake",
    "### Pourquoi c'est faux": "### Why it is wrong",
    "## Exercices d'application": "## Practice exercises",
    "### Exercice": "### Exercise",
    "## Ce qu'il faut retenir": "## What to remember",
}
_NIVEAUX_EN = {"facile": "easy", "moyen": "medium", "approfondissement": "challenge", "difficile": "hard"}
_EXERCICE_RE = re.compile(r"^### Exercice (\S*) \(([^)\n]*)\)[ \t]*$", re.MULTILINE)
_ETAPE_RE = re.compile(r"^\*\*Étape (\S*) - ", re.MULTILINE)
_QUAND_RE = re.compile(r"^\*Quand l'utiliser : ", re.MULTILINE)
_TITRE_LIGNE_RE = re.compile(r"^(#{2,3} .*?)[ \t]*$", re.MULTILINE)
# « [Théorème de Thalès](COURS_REF:slug) » : un renvoi vers un autre cours du site, sans objet sur papier.
_RENVOI_COURS_RE = re.compile(r"\[([^\]]+)\]\(COURS_REF:[^)\s]+\)")


def adapter_markdown_cours(markdown_text, langue):
    """Le Markdown d'un cours prêt à imprimer : renvois internes aplatis en texte, et - pour un cours en anglais -
    les titres de structure dans la langue du PDF. Ne touche qu'à des lignes entières connues : jamais au contenu."""
    texte = _RENVOI_COURS_RE.sub(r"\1", markdown_text)
    if langue != "en":
        return texte

    def titre(match):
        return _TITRES_EN.get(match.group(1), match.group(1))

    texte = _TITRE_LIGNE_RE.sub(titre, texte)
    texte = _EXERCICE_RE.sub(
        lambda m: f"### Exercise {m.group(1)} ({_NIVEAUX_EN.get(m.group(2).strip().lower(), m.group(2))})", texte,
    )
    texte = _ETAPE_RE.sub(lambda m: f"**Step {m.group(1)} - ", texte)
    return _QUAND_RE.sub("*When to use it: ", texte)


def _lien_cours(cours, langue):
    # settings.PDF_SITE_URL, pas FRONTEND_URL : le lien est imprimé dans un fichier qui circule (voir
    # catalog.sujet_pdf._lesson_deep_link). Le lecteur, où la carte des exercices propose l'abonnement.
    chemin = chemin_public(f"/cours/{cours.slug}/lire", langue)
    return f"{settings.PDF_SITE_URL}{chemin}?ref=pdf_cours"


def _meta_entete(cours, header):
    meta = []
    if not matiere_dans_titre(cours.titre, header["matiere"]):
        meta.append(header["matiere"])
    meta += [x for x in (header["serie_libelle"], header["sous_theme"]) if x]
    if header["duree_estimee_min"]:
        meta.append(f"{header['duree_estimee_min']} min")
    return meta


def rendre_html(cours, variante):
    langue = langue_du_contenu(subject=cours.subject)
    tx = textes_pdf(langue, site=settings.SITE_NAME)
    texte = adapter_markdown_cours(markdown_du_cours(cours, variante), langue)
    protege, math_spans = _protect_math(_resolve_media_paths(texte))
    contenu_html = markdown.markdown(_italicize_quotes(protege), extensions=["tables", "fenced_code", "nl2br"])
    contenu_html = _restore_math(contenu_html, math_spans)

    header = cours.header_info()
    header["pays"]["label"] = nom_pays(header["pays"]["code"], header["pays"]["label"], langue)
    flag_path = _FLAGS_DIR / f"{header['pays']['code'].lower()}.svg"
    cours_url = _lien_cours(cours, langue)
    prefixe = "cours_libre" if variante == LIBRE else "cours_complet"
    return render_to_string("catalog/cours_pdf_template.html", {
        "cours": cours,
        "header": header,
        "tx": tx,
        "meta": _meta_entete(cours, header),
        "content_html": contenu_html,
        "site_name": settings.SITE_NAME,
        "site_url_display": settings.PDF_SITE_URL.removeprefix("https://").removeprefix("http://"),
        "cours_url": cours_url,
        "qr_code_data_uri": _qr_code_data_uri(cours_url),
        "cta_titre": tx[f"{prefixe}_cta_titre"],
        "cta_corps": tx[f"{prefixe}_cta_corps"],
        "cta_lien": tx[f"{prefixe}_cta_lien"],
        "note_pied": tx[f"{prefixe}_note_pied"],
        "katex_css_url": (_KATEX_DIR / "katex.min.css").as_uri(),
        "katex_js_url": (_KATEX_DIR / "katex.min.js").as_uri(),
        "katex_auto_render_url": (_KATEX_DIR / "contrib" / "auto-render.min.js").as_uri(),
        "flag_url": flag_path.as_uri() if flag_path.is_file() else None,
    })


def generer_cours_pdf(cours, variante):
    """Les octets du PDF. Bas niveau : voir enregistrer_cours_pdf. Jamais appelé depuis une vue HTTP."""
    return html_vers_pdf(rendre_html(cours, variante))


def enregistrer_cours_pdf(cours, variante):
    """Génère le PDF et le range dans le cache ; supprime les PDF périmés du même cours. Retourne le nom du fichier."""
    nom = nom_fichier(cours, variante)
    pdf = generer_cours_pdf(cours, variante)
    storage = stockage()
    if storage.exists(nom):
        storage.delete(nom)
    nom = storage.save(nom, ContentFile(pdf))
    _supprimer_anciens(storage, cours, variante, garder=nom)
    return nom


def _supprimer_anciens(storage, cours, variante, garder):
    try:
        _, fichiers = storage.listdir(variante)
    except (FileNotFoundError, NotADirectoryError):
        return
    for fichier in fichiers:
        chemin = f"{variante}/{fichier}"
        if fichier.startswith(f"{cours.pk}-") and chemin != garder:
            storage.delete(chemin)


# --- File d'attente --------------------------------------------------------------------------------------------

def _dossier_verrous():
    # Le disque du conteneur qui sert les requêtes ET lance les générations : un seul processus backend, pas un
    # cache partagé nécessaire. Les verrous périmés (voir VERROU_PERIME_S) disparaissent d'eux-mêmes.
    dossier = Path(tempfile.gettempdir()) / "edukora_cours_pdf"
    dossier.mkdir(exist_ok=True)
    return dossier


def _verrou(cours, variante):
    return _dossier_verrous() / f"{variante}-{cours.pk}.lock"


def _echec(cours, variante):
    return _dossier_verrous() / f"{variante}-{cours.pk}.echec"


def liberer(cours, variante, *, echec=False):
    """Appelé en fin de génération par la commande : retire le verrou, et note l'échec le cas échéant."""
    _verrou(cours, variante).unlink(missing_ok=True)
    if echec:
        _echec(cours, variante).touch()


def _recent(chemin, duree):
    try:
        return time.time() - chemin.stat().st_mtime < duree
    except FileNotFoundError:
        return False


def mettre_en_file(cours, variante):
    """Lance la génération si elle n'est ni en cours, ni en pause après un échec, ni bloquée par la limite de
    générations simultanées. Retourne EN_PREPARATION, OCCUPE ou ECHEC."""
    if _recent(_echec(cours, variante), ECHEC_PAUSE_S):
        return ECHEC
    verrou = _verrou(cours, variante)
    if _recent(verrou, VERROU_PERIME_S):
        return EN_PREPARATION
    verrou.unlink(missing_ok=True)

    actifs = sum(1 for autre in _dossier_verrous().glob("*.lock") if _recent(autre, VERROU_PERIME_S))
    if actifs >= MAX_GENERATIONS_SIMULTANEES:
        return OCCUPE
    try:
        with open(verrou, "x"):
            pass
    except FileExistsError:
        return EN_PREPARATION

    try:
        _lancer(cours, variante)
    except OSError:
        liberer(cours, variante, echec=True)
        return ECHEC
    return EN_PREPARATION


def _lancer(cours, variante):
    """Processus détaché, comme catalog.sujet_pdf.queue_sujet_pdf_generation (voir ses explications : Playwright
    n'est pas fiable dans le thread d'une requête)."""
    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [sys.executable, str(manage_py), "generate_cours_pdfs", "--cours", str(cours.pk), "--variante", variante]
    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_f = open(logs_dir / "cours_pdf_generation.log", "ab")
    env = {**os.environ, "PYTHONUTF8": "1"}
    kwargs = {}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True
    processus = subprocess.Popen(
        args, cwd=settings.BASE_DIR, env=env,
        stdin=subprocess.DEVNULL, stdout=log_f, stderr=log_f,
        **kwargs,
    )
    # Récolte le processus fini (sinon il reste zombie tant que le serveur tourne) ; ne bloque pas la requête.
    threading.Thread(target=processus.wait, daemon=True).start()
