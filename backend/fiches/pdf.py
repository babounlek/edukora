"""
Génère les deux PDF d'une FicheGeneree - sujet seul (à distribuer tel quel aux élèves)
et corrigé seul (usage personnel du répétiteur), décision produit du chantier "Outil
Fiches pour répétiteurs" (voir FicheGeneree, docstring de modèle) - jamais un fichier
combiné. Réutilise les briques bas niveau de catalog.sujet_pdf (Playwright hors ligne,
protection LaTeX, résolution des chemins média), même pattern qu'inedit/sujet_pdf.py.

Contrainte dure héritée de catalog.sujet_pdf (voir sa docstring de module, source de
vérité) : Playwright ne doit JAMAIS tourner dans le thread d'une requête HTTP (lenteur,
non-fiabilité constatée en pratique) - toujours un processus détaché, voir
queue_fiche_pdf_generation. generate_fiche_pdfs()/save_fiche_pdfs() ci-dessous ne sont
JAMAIS appelées depuis une vue HTTP, seulement depuis la commande de gestion
`generate_fiche_pdfs`.
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
# même raisonnement qu'inedit/sujet_pdf.py : reste correct même si son chemin venait à
# changer indépendamment (calculé relatif à catalog, pas à fiches).
_KATEX_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "katex"


def _cursus_display(cursus):
    return f"{cursus.display_examen()} - Série {cursus.series.code}" if cursus.series else cursus.display_examen()


def _prepared_by(fiche):
    return fiche.owner.pseudo or fiche.owner.full_name or "un répétiteur"


# ?ref=pdf_fiche_sujet / ?ref=pdf_fiche_corrige distinguent la provenance de chaque
# variante (même convention ?ref= que catalog.sujet_pdf._lesson_deep_link) - seule
# façon de mesurer combien de visites viennent réellement d'une fiche imprimée/partagée
# hors plateforme plutôt que de le supposer sans donnée. Deux destinations différentes
# à dessein : le PDF sujet circule auprès des ÉLÈVES du répétiteur (jamais inscrits sur
# edukora à ce stade) - le catalogue public est le point d'entrée pertinent pour eux ;
# le PDF corrigé reste, lui, entre les mains du répétiteur (voir la mention "réservé à
# l'usage personnel" dans son propre template) - /fiches (générer la prochaine) est ce
# qu'il a le plus de raisons de vouloir rouvrir.
def _sujet_deep_link(fiche):
    country_code = fiche.cursus.country.code.lower()
    return f"{settings.FRONTEND_URL}/{country_code}?ref=pdf_fiche_sujet"


def _corrige_deep_link(fiche):
    return f"{settings.FRONTEND_URL}/fiches?ref=pdf_fiche_corrige"


def _bloc_question(item, *, avec_corrige):
    """
    Un bloc "Question N" du PDF. Le corrigé reprend l'énoncé AVANT la solution : le
    répétiteur travaille sur le seul document qu'il garde (voir _corrige_deep_link), il
    ne doit pas avoir à le lire à côté du PDF sujet distribué à ses élèves pour savoir
    de quoi parle la solution qu'il relit.
    """
    competence_item = item.competence_item
    blocs = [f"## Question {item.ordre}", competence_item.enonce_markdown.strip()]
    if avec_corrige:
        corrige = competence_item.corrige_markdown.strip()
        # Les items générés par concepteur-quiz-competence ouvrent déjà sur leurs propres
        # titres ("### Rappel de méthode", puis "### Corrigé") ; les plus anciens n'en ont
        # aucun - sans ce repli, l'énoncé et sa solution se toucheraient sans démarcation
        # visible, exactement ce que l'ordre voulu ci-dessus cherche à éviter.
        if not corrige.startswith("#"):
            corrige = f"### Corrigé\n\n{corrige}"
        blocs.append(corrige)
    return "\n\n".join(blocs)


def _combined_markdown(fiche, *, avec_corrige):
    items = fiche.items.select_related("competence_item").order_by("ordre")
    return "\n\n".join(_bloc_question(item, avec_corrige=avec_corrige) for item in items)


def _render_html(fiche, *, avec_corrige, template_name, deep_link):
    markdown_text = _resolve_media_paths(_combined_markdown(fiche, avec_corrige=avec_corrige))
    protected_markdown, math_spans = _protect_math(markdown_text)
    protected_markdown = _italicize_quotes(protected_markdown)
    content_html = markdown.markdown(protected_markdown, extensions=["tables", "fenced_code", "nl2br"])
    content_html = _restore_math(content_html, math_spans)

    return render_to_string(template_name, {
        "fiche": fiche,
        "cursus_display": _cursus_display(fiche.cursus),
        "prepared_by": _prepared_by(fiche),
        "content_html": content_html,
        "site_name": settings.SITE_NAME,
        "site_url_display": settings.FRONTEND_URL.removeprefix("https://").removeprefix("http://"),
        "deep_link": deep_link,
        "qr_code_data_uri": _qr_code_data_uri(deep_link),
        "katex_css_url": (_KATEX_DIR / "katex.min.css").as_uri(),
        "katex_js_url": (_KATEX_DIR / "katex.min.js").as_uri(),
        "katex_auto_render_url": (_KATEX_DIR / "contrib" / "auto-render.min.js").as_uri(),
    })


def _render_pdf_bytes(html):
    # page.set_content() bloquerait le chargement des ressources file:// locales (voir
    # catalog.sujet_pdf.generate_sujet_pdf, docstring inline) - même détour par un vrai
    # fichier temporaire, même origine que les ressources KaTeX qu'il charge.
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


def generate_fiche_pdfs(fiche):
    """Retourne (sujet_bytes, corrige_bytes). Bas niveau : voir save_fiche_pdfs pour l'usage normal."""
    sujet_html = _render_html(
        fiche, avec_corrige=False, template_name="fiches/fiche_sujet_pdf_template.html",
        deep_link=_sujet_deep_link(fiche),
    )
    corrige_html = _render_html(
        fiche, avec_corrige=True, template_name="fiches/fiche_corrige_pdf_template.html",
        deep_link=_corrige_deep_link(fiche),
    )
    return _render_pdf_bytes(sujet_html), _render_pdf_bytes(corrige_html)


def save_fiche_pdfs(fiche):
    """
    Génère les deux PDF et les enregistre sur la FicheGeneree, statut PRETE si les deux
    réussissent. Point d'entrée normal - à appeler hors ligne uniquement (commande
    `generate_fiche_pdfs`), jamais depuis une vue HTTP (voir docstring de module). Laisse
    toute exception remonter : l'appelant (la commande de gestion) est responsable de
    passer `statut` à ECHEC et de logger - jamais avalée silencieusement ici.
    """
    from .models import StatutGeneration

    sujet_bytes, corrige_bytes = generate_fiche_pdfs(fiche)
    fiche.sujet_pdf.save(f"{slugify(fiche.titre)}-sujet.pdf", ContentFile(sujet_bytes), save=False)
    fiche.corrige_pdf.save(f"{slugify(fiche.titre)}-corrige.pdf", ContentFile(corrige_bytes), save=False)
    fiche.statut = StatutGeneration.PRETE
    fiche.save(update_fields=["sujet_pdf", "corrige_pdf", "statut"])


def queue_fiche_pdf_generation(fiche_id):
    """
    Déclenche `generate_fiche_pdfs` (commande de gestion) dans un processus détaché,
    complètement en dehors du process serveur - voir
    catalog.sujet_pdf.queue_sujet_pdf_generation, même pattern (Popen nu, PYTHONUTF8
    forcé), répliqué ici plutôt qu'importé (commande cible et fichier de log
    différents). Point d'entrée normal depuis une vue (contrairement à
    generate_fiche_pdfs/save_fiche_pdfs, jamais appelées depuis une requête HTTP).
    """
    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [sys.executable, str(manage_py), "generate_fiche_pdfs", "--fiche", str(fiche_id)]

    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_f = open(logs_dir / "fiche_pdf_generation.log", "ab")
    env = {**os.environ, "PYTHONUTF8": "1"}

    kwargs = {}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True

    subprocess.Popen(
        args, cwd=settings.BASE_DIR, env=env,
        stdin=subprocess.DEVNULL, stdout=log_f, stderr=log_f,
        **kwargs,
    )
