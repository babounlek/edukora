"""
Génère un PDF brandé du SUJET uniquement (énoncés, jamais le corrigé - voir
Lesson.preview_markdown) : un support marketing librement partageable, pas une
copie du produit payant. Distinct de l'ancien pipeline PDF supprimé, qui rendait
le corrigé complet et devait donc être protégé - ici la fuite est le but.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.text import slugify

# PLAYWRIGHT_BROWSERS_PATH=0 : installe/résout les navigateurs sous
# venv/Lib/site-packages/playwright/.../.local-browsers (dans le projet) plutôt que
# dans le cache utilisateur par défaut (%LOCALAPPDATA%\ms-playwright, hors du projet).
# Nécessaire ici, pas juste une préférence : selon l'environnement d'exécution du
# serveur, ce cache hors-projet peut être invisible au process serveur (constaté en
# pratique - un chemin identique, mais un répertoire qui semble vide depuis ce
# process) alors que tout ce qui vit sous le projet lui reste accessible. Doit être
# posé avant l'import de playwright, qui résout ses chemins par défaut à l'import.
# Installé via `PLAYWRIGHT_BROWSERS_PATH=0 python -m playwright install chromium`.
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

from playwright.sync_api import sync_playwright  # noqa: E402

# KaTeX servi depuis des fichiers locaux (copiés depuis frontend/node_modules/katex/dist,
# même structure relative pour que katex.min.css retrouve ses polices dans fonts/) plutôt
# que depuis un CDN externe : la génération PDF tourne côté serveur et ne doit pas dépendre
# de la disponibilité réseau d'un tiers à chaque requête (timeouts constatés avec jsdelivr).
_KATEX_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "katex"

# Drapeaux SVG (paquet npm flag-icons, copiés depuis frontend/node_modules/flag-icons/flags/4x3
# comme KaTeX ci-dessus) plutôt qu'un émoji drapeau : Chromium sous Windows ne rend pas les
# regional indicator symbols par défaut (même raison que countryFlag.ts côté frontend), et le
# rendu PDF ne doit pas dépendre de la police système de la machine qui génère.
_FLAGS_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "flags" / "4x3"


def _footer_template():
    # Fonction plutôt que constante de module : settings.SITE_NAME doit être lu au
    # moment de la génération, pas figé dans une chaîne construite à l'import.
    return (
        '<div style="font-size:9px; width:100%; text-align:center; color:#888;">'
        f"{settings.SITE_NAME} - "
        '<span class="pageNumber"></span> / <span class="totalPages"></span>'
        "</div>"
    )

# La bibliothèque Python `markdown` ne connaît pas le contexte mathématique (contrairement
# à remark-math côté React) : un caractère LaTeX aussi courant que * (ex. \mathbb{N}^*)
# est interprété comme une emphase Markdown, qui se referme sur le * suivant trouvé dans
# le texte (souvent bien plus loin, ex. *(0,5 pt)*) et casse tout ce qu'il y a entre les
# deux. On protège donc chaque bloc $$...$$/$...$ par un jeton neutre avant conversion,
# puis on restaure le LaTeX d'origine intact dans le HTML obtenu.
_MATH_SPAN_RE = re.compile(r"\$\$[\s\S]+?\$\$|\$[^$\n]+?\$")


def _protect_math(markdown_text):
    spans = []

    def _replace(match):
        spans.append(match.group(0))
        return f"@@MATH{len(spans) - 1}@@"

    return _MATH_SPAN_RE.sub(_replace, markdown_text), spans


def _restore_math(html, spans):
    for index, span in enumerate(spans):
        html = html.replace(f"@@MATH{index}@@", span)
    return html


# Convention typographique demandée pour les citations : tout texte entre guillemets
# (« » ou "...") passe en italique, guillemets compris. Appliqué sur le Markdown déjà
# protégé par _protect_math (les $...$ sont alors de simples jetons @@MATH{n}@@), donc
# un guillemet à l'intérieur d'une formule LaTeX ne peut jamais être touché ici -
# même garantie que côté frontend (voir frontend/src/lib/markdown.ts, italicizeQuotes).
_GUILLEMET_RE = re.compile(r"«([^»\n*$]+)»")
_STRAIGHT_QUOTE_RE = re.compile(r'"([^"\n*$]+)"')


def _italicize_quotes(markdown_text):
    markdown_text = _GUILLEMET_RE.sub(lambda m: f"*«{m.group(1)}»*", markdown_text)
    markdown_text = _STRAIGHT_QUOTE_RE.sub(lambda m: f'*"{m.group(1)}"*', markdown_text)
    return markdown_text


# Les figures d'exercice (voir catalog.models.Figure) sont référencées dans le
# Markdown par une URL relative (/media/figures/...), correcte pour le frontend React
# qui la sert via HTTP - mais invalide ici : Playwright charge ce HTML via file://
# (voir generate_sujet_pdf), où un chemin commençant par / part de la racine du
# disque, pas du dossier media Django. On les réécrit donc vers de vrais file://
# locaux, même logique que pour les polices/JS KaTeX ci-dessus.
_MEDIA_IMAGE_RE = re.compile(r"\]\(/media/([^)\s]+)\)")


def _resolve_media_paths(markdown_text):
    media_root = Path(settings.MEDIA_ROOT)

    def _replace(match):
        local_path = media_root / match.group(1)
        return f"]({local_path.as_uri()})" if local_path.is_file() else match.group(0)

    return _MEDIA_IMAGE_RE.sub(_replace, markdown_text)


def _render_html(lesson):
    markdown_text = _resolve_media_paths(lesson.preview_markdown())
    protected_markdown, math_spans = _protect_math(markdown_text)
    protected_markdown = _italicize_quotes(protected_markdown)
    content_html = markdown.markdown(
        protected_markdown,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    content_html = _restore_math(content_html, math_spans)
    header = lesson.header_info()
    flag_path = _FLAGS_DIR / f"{header['pays']['code'].lower()}.svg"
    return render_to_string("catalog/sujet_pdf_template.html", {
        "lesson": lesson,
        "header": header,
        "content_html": content_html,
        "site_name": settings.SITE_NAME,
        "site_url": settings.FRONTEND_URL,
        "site_url_display": settings.FRONTEND_URL.removeprefix("https://").removeprefix("http://"),
        "katex_css_url": (_KATEX_DIR / "katex.min.css").as_uri(),
        "katex_js_url": (_KATEX_DIR / "katex.min.js").as_uri(),
        "katex_auto_render_url": (_KATEX_DIR / "contrib" / "auto-render.min.js").as_uri(),
        "flag_url": flag_path.as_uri() if flag_path.is_file() else None,
    })


def generate_sujet_pdf(lesson):
    """Retourne les octets du PDF du sujet. Bas niveau : voir save_sujet_pdf pour l'usage normal."""
    html = _render_html(lesson)

    # page.set_content() donne à la page une origine "about:blank" : Chromium bloque
    # alors le chargement des ressources file:// (nos fichiers KaTeX locaux) depuis
    # cette origine, ce qui fait silencieusement échouer katex.min.js/auto-render.min.js
    # (le try/catch du template avale l'erreur, __katexDone finit quand même par passer
    # à true) - résultat : du LaTeX brut non rendu dans le PDF, sans aucune erreur.
    # On écrit donc un vrai fichier HTML temporaire et on y navigue via file://, pour
    # que la page ait la même origine que les ressources locales qu'elle charge.
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            # `launch()` sans argument : passer explicitement executable_path (même la
            # valeur exacte retournée par p.chromium.executable_path) fait échouer le
            # spawn ("spawn UNKNOWN") sur cette machine - laisser Playwright résoudre
            # l'exécutable lui-même fonctionne de façon fiable. Comme la génération ne
            # tourne plus jamais dans le process serveur (voir save_sujet_pdf), le souci
            # de résolution "headless shell" observé dans ce contexte-là ne s'applique plus.
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_path.as_uri(), wait_until="load")
            page.wait_for_function("() => window.__katexDone === true", timeout=15000)
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                # bottom généreux : le corps du texte ne doit jamais chevaucher le pied
                # de page injecté par footer_template (constaté avec 36px - la marge
                # CSS @page:0 du template, supprimée, aggravait aussi le problème en
                # empêchant Chromium de réserver cet espace lors de la pagination).
                margin={"top": "20px", "bottom": "56px", "left": "0px", "right": "0px"},
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=_footer_template(),
            )
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)

    return pdf_bytes


def sujet_pdf_filename(lesson):
    """
    Préfixé par le code pays (même convention que `ingest/<code_pays>/...`, voir
    catalog.ingestion._country_code_from_path) : sans lui, le nom de fichier ne
    dépend que du titre de la leçon (slugify(lesson.title)), qui peut coïncider
    entre deux pays pour une même épreuve (ex. "Mathématiques BAC A 2016") - le
    second écraserait alors silencieusement le PDF du premier dans le dossier plat
    sujets_pdf/. Décision utilisateur du 2026-08-03 : n'affecte que les PDF générés
    à partir de maintenant, le contenu déjà généré (chemin plat historique) n'est
    pas migré - voir le même choix déjà fait pour la bascule vers Spaces
    (edtech_cm/settings.py, STORAGES).
    """
    country_code = lesson.subject.country.code.lower()
    return f"{country_code}/{slugify(lesson.title)}-sujet.pdf"


def save_sujet_pdf(lesson):
    """
    Génère le PDF du sujet et l'enregistre sur le Lesson. Point d'entrée normal -
    à appeler hors ligne (commande `generate_sujet_pdfs`), jamais depuis une vue
    HTTP : Playwright lance un processus Chromium, ce qui n'a pas sa place dans le
    cycle requête/réponse d'un serveur web (lenteur, non mise en cache, et - constaté
    en pratique, pas seulement en théorie : voir queue_sujet_pdf_generation ci-dessous
    - un lancement de Chromium depuis le thread d'une requête admin y est nettement
    moins fiable que le même appel hors ligne, pour des raisons qui n'ont jamais pu
    être épinglées précisément malgré plusieurs tentatives de correction).
    """
    pdf_bytes = generate_sujet_pdf(lesson)
    # Le nom de fichier cible est déterministe (voir sujet_pdf_filename) : une
    # régénération (ex. après correction du contenu) vise donc le même chemin que le
    # PDF déjà en place. Sans suppression explicite au préalable, FieldFile.save() ne
    # supprime jamais l'ancien fichier référencé - le storage lui trouve juste un nom
    # disponible différent (suffixe aléatoire), et l'ancien PDF reste orphelin.
    if lesson.sujet_pdf:
        lesson.sujet_pdf.delete(save=False)
    lesson.sujet_pdf.save(sujet_pdf_filename(lesson), ContentFile(pdf_bytes), save=True)


def queue_sujet_pdf_generation(lesson_ids, force=False):
    """
    Déclenche `generate_sujet_pdfs` dans un processus détaché, complètement en dehors
    du process serveur. Point d'entrée pour les vues/actions admin (voir
    catalog.admin) : contrairement à save_sujet_pdf, ne bloque jamais le cycle
    requête/réponse et ne fait tourner Playwright dans aucun thread de ce process -
    exactement le pattern déjà utilisé de façon fiable par la commande
    `ingest_corrections` (via une exécution CLI/tâche planifiée), qu'on réplique ici
    au lieu de réessayer, encore une fois, de faire fonctionner Playwright depuis le
    thread d'une requête. Fire-and-forget : le résultat n'apparaît qu'à l'actualisation
    de la page admin, pas dans la réponse à cette requête.

    Volontairement un Popen "nu", sans DETACHED_PROCESS/CREATE_NEW_PROCESS_GROUP
    (Windows) : ces flags peuvent tout simplement empêcher le sous-processus de
    démarrer selon la façon dont le process serveur lui-même a été lancé (supervision/
    bac à sable) - constaté en pratique, pas seulement en théorie. Le process reste de
    toute façon indépendant du thread de requête une fois lancé (Python ne l'attend
    jamais) ; le seul risque perdu est qu'un signal Ctrl+C dans la console du serveur
    puisse aussi l'atteindre - acceptable pour une génération de quelques secondes.
    """
    if not lesson_ids:
        return

    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [sys.executable, str(manage_py), "generate_sujet_pdfs", "--lesson", *(str(pk) for pk in lesson_ids)]
    if force:
        args.append("--force")

    # PYTHONUTF8 forcé : stdout/stderr redirigés vers un fichier (pas une vraie
    # console) retombent sinon sur le codepage ANSI de la machine, qui plante sur le
    # moindre caractère accentué dans un message d'erreur - or generate_sujet_pdfs
    # écrit ses erreurs en français. Sans ce forçage, une vraie erreur de génération
    # PDF fait planter le *logging* de cette erreur, qui disparaît alors sans laisser
    # de trace exploitable.
    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_f = open(logs_dir / "sujet_pdf_generation.log", "ab")
    env = {**os.environ, "PYTHONUTF8": "1"}

    kwargs = {}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True

    subprocess.Popen(
        args, cwd=settings.BASE_DIR, env=env,
        stdin=subprocess.DEVNULL, stdout=log_f, stderr=log_f,
        **kwargs,
    )
