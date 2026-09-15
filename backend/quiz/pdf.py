"""
Génère les deux PDF d'une QuizSession, disponibles dès sa création (pas seulement une
fois terminée - voir la docstring de quiz.views.quiz_fiche_pdf) - "Fiche" (énoncés seuls, à retravailler
sans la correction sous les yeux) et "Correction" (énoncés + corrigé, pour ne pas avoir à
rouvrir la Fiche à côté) - jamais un seul document combiné, décision produit du
2026-09-15. Ni l'un ni l'autre ne fait référence à la tentative de l'élève (pas de "ta
réponse" ni de score) : les deux restent utilisables comme support de révision même
longtemps après, indépendamment de ce qu'il avait répondu ce jour-là. Réutilise les
briques bas niveau de catalog.sujet_pdf (Playwright hors ligne, protection LaTeX,
résolution des chemins média), même pattern que fiches/pdf.py (sujet/corrigé séparés,
même raisonnement) et inedit/sujet_pdf.py.

Contrainte dure héritée de catalog.sujet_pdf (voir sa docstring de module, source de
vérité) : Playwright ne doit JAMAIS tourner dans le thread d'une requête HTTP (lenteur,
non-fiabilité constatée en pratique) - toujours un processus détaché, voir
queue_quiz_fiche_pdf_generation. generate_quiz_fiche_pdfs()/save_quiz_fiche_pdfs()
ci-dessous ne sont JAMAIS appelées depuis une vue HTTP, seulement depuis la commande de
gestion `generate_quiz_fiche_pdf`.
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
# même raisonnement qu'inedit/sujet_pdf.py et fiches/pdf.py : reste correct même si son
# chemin venait à changer indépendamment (calculé relatif à catalog, pas à quiz).
_KATEX_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "katex"


def _cursus_display(cursus):
    return f"{cursus.display_examen()} - Série {cursus.series.code}" if cursus.series else cursus.display_examen()


# _competence_item_corrige (quiz.views) injecte un marqueur "[COURS_LINK:slug]" isolé -
# jamais du Markdown standard, seulement compris par le frontend React (voir
# frontend/src/components/EpreuveMarkdown.tsx, COURS_LINK_SENTINEL) pour afficher un
# bouton "Voir le cours complet". Sans conversion ici, `markdown.markdown()` (bibliothèque
# Python, ne connaît pas ce marqueur) l'aurait laissé tel quel dans le PDF, en texte brut
# illisible - on le convertit donc en vrai lien Markdown avant le rendu.
_COURS_LINK_RE = re.compile(r"^\[COURS_LINK:([a-zA-Z0-9_-]+)\]$", re.MULTILINE)


def _resolve_cours_links(markdown_text):
    return _COURS_LINK_RE.sub(
        lambda m: f"[Voir le cours complet →]({settings.FRONTEND_URL}/cours/{m.group(1)})", markdown_text,
    )


# ?ref=pdf_quiz_fiche / ?ref=pdf_quiz_correction distinguent la provenance de chaque
# variante (même convention ?ref= que catalog.sujet_pdf._lesson_deep_link et
# fiches/pdf.py._sujet_deep_link/_corrige_deep_link) - seule façon de mesurer combien de
# visites viennent réellement de l'une ou l'autre fiche téléchargée.
def _sujet_deep_link(session):
    country_code = session.cursus.country.code.lower()
    return f"{settings.FRONTEND_URL}/{country_code}?ref=pdf_quiz_fiche"


def _corrige_deep_link(session):
    country_code = session.cursus.country.code.lower()
    return f"{settings.FRONTEND_URL}/{country_code}?ref=pdf_quiz_correction"


def _bloc_question(quiz_question, *, avec_corrige):
    """
    Un bloc "Question N" du PDF - énoncé seul si avec_corrige=False (le PDF "Fiche"),
    énoncé puis corrigé sinon (le PDF "Correction") ; jamais la réponse donnée par
    l'élève ni une indication correct/incorrect (voir la docstring de module). Import
    différé de quiz.views : quiz.views importe ce module au niveau top-level (voir
    queue_quiz_fiche_pdf_generation, appelée depuis quiz.views.quiz_fiche_pdf), un
    import top-level symétrique ici créerait un cycle.
    """
    from .views import _clean_quiz_markdown, _competence_item_corrige

    contenu = quiz_question.contenu
    if quiz_question.competence_item_id:
        enonce = contenu.enonce_markdown.strip()
    else:
        enonce = _clean_quiz_markdown(contenu.enonce_markdown).strip()

    blocs = [f"## Question {quiz_question.ordre}", enonce]
    if avec_corrige:
        if quiz_question.competence_item_id:
            corrige = _competence_item_corrige(contenu).strip()
        else:
            corrige = contenu.corrige_markdown.strip()
        # Les items générés par concepteur-quiz-competence ouvrent déjà sur leurs propres
        # titres ("### Rappel de méthode", puis "### Corrigé") ; les plus anciens (et
        # l'historique catalog.Question) n'en ont aucun - sans ce repli, l'énoncé et sa
        # solution se toucheraient sans démarcation visible (même logique que
        # fiches.pdf._bloc_question).
        if not corrige.startswith("#"):
            corrige = f"### Corrigé\n\n{corrige}"
        blocs.append(corrige)

    return "\n\n".join(blocs)


def _combined_markdown(session, *, avec_corrige):
    quiz_questions = (
        session.quiz_questions
        .select_related("question__exercise__lesson__subject", "competence_item__theme", "competence_item__subject")
        .order_by("ordre")
    )
    return "\n\n".join(_bloc_question(qq, avec_corrige=avec_corrige) for qq in quiz_questions)


def _render_html(session, *, avec_corrige, template_name, deep_link):
    markdown_text = _resolve_cours_links(_resolve_media_paths(_combined_markdown(session, avec_corrige=avec_corrige)))
    protected_markdown, math_spans = _protect_math(markdown_text)
    protected_markdown = _italicize_quotes(protected_markdown)
    content_html = markdown.markdown(protected_markdown, extensions=["tables", "fenced_code", "nl2br"])
    content_html = _restore_math(content_html, math_spans)

    return render_to_string(template_name, {
        "session": session,
        "subject_label": session.subject.label if session.subject_id else "",
        "cursus_display": _cursus_display(session.cursus),
        "total_questions": session.quiz_questions.count(),
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


def generate_quiz_fiche_pdfs(session):
    """Retourne (sujet_bytes, corrige_bytes). Bas niveau : voir save_quiz_fiche_pdfs pour l'usage normal."""
    sujet_html = _render_html(
        session, avec_corrige=False, template_name="quiz/fiche_sujet_pdf_template.html",
        deep_link=_sujet_deep_link(session),
    )
    corrige_html = _render_html(
        session, avec_corrige=True, template_name="quiz/fiche_corrige_pdf_template.html",
        deep_link=_corrige_deep_link(session),
    )
    return _render_pdf_bytes(sujet_html), _render_pdf_bytes(corrige_html)


def save_quiz_fiche_pdfs(session):
    """
    Génère les deux PDF et les enregistre sur la QuizSession, statut PRETE si les deux
    réussissent. Point d'entrée normal - à appeler hors ligne uniquement (commande
    `generate_quiz_fiche_pdf`), jamais depuis une vue HTTP (voir docstring de module).
    Laisse toute exception remonter : l'appelant (la commande de gestion) est
    responsable de passer `fiche_pdf_statut` à ECHEC et de logger - jamais avalée
    silencieusement ici.
    """
    from .models import StatutFichePdf

    sujet_bytes, corrige_bytes = generate_quiz_fiche_pdfs(session)
    if session.sujet_pdf:
        session.sujet_pdf.delete(save=False)
    if session.corrige_pdf:
        session.corrige_pdf.delete(save=False)
    session.sujet_pdf.save(f"session-{session.pk}-fiche.pdf", ContentFile(sujet_bytes), save=False)
    session.corrige_pdf.save(f"session-{session.pk}-correction.pdf", ContentFile(corrige_bytes), save=False)
    session.fiche_pdf_statut = StatutFichePdf.PRETE
    session.save(update_fields=["sujet_pdf", "corrige_pdf", "fiche_pdf_statut"])


def queue_quiz_fiche_pdf_generation(session_id):
    """
    Déclenche `generate_quiz_fiche_pdf` (commande de gestion) dans un processus détaché,
    complètement en dehors du process serveur - voir catalog.sujet_pdf.
    queue_sujet_pdf_generation, même pattern (Popen nu, PYTHONUTF8 forcé), répliqué ici
    plutôt qu'importé (commande cible et fichier de log différents, même choix que
    fiches.pdf.queue_fiche_pdf_generation). Point d'entrée normal depuis une vue
    (contrairement à generate_quiz_fiche_pdfs/save_quiz_fiche_pdfs, jamais appelées depuis
    une requête HTTP).
    """
    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [sys.executable, str(manage_py), "generate_quiz_fiche_pdf", "--session", str(session_id)]

    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_f = open(logs_dir / "quiz_fiche_pdf_generation.log", "ab")
    env = {**os.environ, "PYTHONUTF8": "1"}

    kwargs = {}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True

    subprocess.Popen(
        args, cwd=settings.BASE_DIR, env=env,
        stdin=subprocess.DEVNULL, stdout=log_f, stderr=log_f,
        **kwargs,
    )
