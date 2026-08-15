"""
Génère le PDF du SUJET (énoncé seul) d'une EpreuveInedite - réutilise les briques de
rendu de catalog.sujet_pdf (Playwright hors ligne, protection LaTeX, résolution des
chemins média). Voir EpreuveInedite.sujet_pdf pour ce que ce PDF représente : celui
proposé sur la fiche épreuve, avant toute tentative.

Le corrigé, lui, ne génère JAMAIS de PDF - décision produit (2026-08-12) : un PDF
téléchargé n'a aucune protection contre la redistribution, même stocké sur un storage
privé (voir catalog.sujet_pdf, dont la docstring de module documente déjà ce choix côté
catalogue "classique" - l'ancien pipeline inedit.corrige_pdf, qui faisait exactement
cette erreur pour une Épreuve Inédite, a été supprimé pour la même raison). Le corrigé
d'une épreuve inédite reste donc consultable uniquement en ligne, question par question,
après tentative - voir QuestionInedite.corrige_markdown et inedit.views.reveal_corrige.

Storage PRIVÉ (contrairement à catalog.sujet_pdf, public) : une épreuve inédite jamais
publiée ailleurs reste payante même sans les réponses - voir EpreuveInedite.sujet_pdf et
inedit.views.download_sujet_pdf (gated has_access_inedite).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.text import slugify

from catalog.sujet_pdf import (
    _FLAGS_DIR,
    _footer_template,
    _italicize_quotes,
    _protect_math,
    _qr_code_data_uri,
    _resolve_media_paths,
    _restore_math,
)
from playwright.sync_api import sync_playwright

# Même dossier statique que catalog.sujet_pdf._KATEX_DIR (fichiers copiés depuis
# frontend/node_modules/katex/dist) - pas un import direct de cette constante privée,
# pour rester correct même si son chemin venait à changer indépendamment (calculé
# relatif à catalog, pas à inedit).
_KATEX_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "katex"


def _cursus_display(cursus_iterable):
    return ", ".join(
        f"{c.display_examen()} - Série {c.series.code}" if c.series else c.display_examen()
        for c in cursus_iterable
    )


# ?ref=pdf_sujet_inedit distingue cette provenance de celle du sujet catalog (voir
# catalog.sujet_pdf._lesson_deep_link, ?ref=pdf_sujet) : ce PDF est privé (voir
# docstring de module) et n'a donc pas la même intention côté analytics - jamais de
# l'acquisition (le lecteur est déjà abonné), plutôt de l'usage (retrouve-t-on l'appli
# depuis un sujet imprimé pour lancer sa tentative chronométrée ?).
def _epreuve_deep_link(epreuve):
    country_code = epreuve.cursus.first().country.code.lower()
    return f"{settings.FRONTEND_URL}/{country_code}/epreuves-inedites/{epreuve.slug}?ref=pdf_sujet_inedit"


def _render_html(epreuve):
    markdown_text = _resolve_media_paths(epreuve.enonce_markdown)
    protected_markdown, math_spans = _protect_math(markdown_text)
    protected_markdown = _italicize_quotes(protected_markdown)
    content_html = markdown.markdown(protected_markdown, extensions=["tables", "fenced_code", "nl2br"])
    content_html = _restore_math(content_html, math_spans)

    country = epreuve.cursus.first().country
    flag_path = _FLAGS_DIR / f"{country.code.lower()}.svg"
    blueprint = epreuve.blueprint
    epreuve_url = _epreuve_deep_link(epreuve)

    return render_to_string("inedit/sujet_pdf_template.html", {
        "epreuve": epreuve,
        "header": {
            "matiere": epreuve.subject.label,
            "cursus_display": _cursus_display(epreuve.cursus.all()),
            "pays_label": country.label,
            "duree_minutes": blueprint.duree_minutes,
            "bareme_total": blueprint.bareme_total,
        },
        "content_html": content_html,
        "site_name": settings.SITE_NAME,
        "site_url": settings.FRONTEND_URL,
        "site_url_display": settings.FRONTEND_URL.removeprefix("https://").removeprefix("http://"),
        "epreuve_url": epreuve_url,
        "qr_code_data_uri": _qr_code_data_uri(epreuve_url),
        "katex_css_url": (_KATEX_DIR / "katex.min.css").as_uri(),
        "katex_js_url": (_KATEX_DIR / "katex.min.js").as_uri(),
        "katex_auto_render_url": (_KATEX_DIR / "contrib" / "auto-render.min.js").as_uri(),
        "flag_url": flag_path.as_uri() if flag_path.is_file() else None,
    })


def generate_sujet_pdf(epreuve):
    """Retourne les octets du PDF du sujet. Voir catalog.sujet_pdf.generate_sujet_pdf
    pour le détail de chaque contournement Playwright ci-dessous, identique."""
    html = _render_html(epreuve)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_path.as_uri(), wait_until="load")
            page.wait_for_function("() => window.__katexDone === true", timeout=15000)
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "20px", "bottom": "56px", "left": "0px", "right": "0px"},
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=_footer_template(),
            )
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)

    return pdf_bytes


def sujet_pdf_filename(epreuve):
    """Préfixé par le code pays - même convention que catalog.sujet_pdf.sujet_pdf_filename."""
    country_code = epreuve.cursus.first().country.code.lower()
    return f"{country_code}/{slugify(epreuve.titre)}-sujet.pdf"


def save_sujet_pdf(epreuve):
    """
    Génère le PDF du sujet et l'enregistre sur l'EpreuveInedite. Point d'entrée normal -
    à appeler hors ligne (commande `generate_sujet_pdfs` ou l'action admin "Marquer
    Validé"/"Générer le PDF du sujet"), jamais depuis une vue HTTP - voir la docstring
    de module.
    """
    pdf_bytes = generate_sujet_pdf(epreuve)
    if epreuve.sujet_pdf:
        epreuve.sujet_pdf.delete(save=False)
    epreuve.sujet_pdf.save(sujet_pdf_filename(epreuve), ContentFile(pdf_bytes), save=True)


def queue_sujet_pdf_generation(epreuve_ids, force=False):
    """Voir catalog.sujet_pdf.queue_sujet_pdf_generation - même pattern (processus
    détaché, Popen nu, PYTHONUTF8 forcé), répliqué ici plutôt qu'importé : la commande
    cible (generate_inedit_sujet_pdfs) et le fichier de log diffèrent."""
    if not epreuve_ids:
        return

    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [
        sys.executable, str(manage_py), "generate_inedit_sujet_pdfs",
        "--epreuve", *(str(pk) for pk in epreuve_ids),
    ]
    if force:
        args.append("--force")

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
