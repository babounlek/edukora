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
from pathlib import Path

import markdown
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from catalog.libelles import libelle_cursus
from catalog.pdf_fin import adresse_du_site, contexte_fin
from catalog.pdf_textes import (
    EXTENSIONS_MARKDOWN_QUIZ,
    adapter_markdown,
    bonne_reponse_markdown,
    langue_du_contenu,
    propositions_markdown,
    textes_pdf,
)
from catalog.segments_url import chemin_public
from catalog.sujet_pdf import (
    _italicize_quotes,
    _protect_math,
    _resolve_media_paths,
    _restore_math,
    html_vers_pdf,
)

from . import instantane

# Même dossier statique que catalog.sujet_pdf._KATEX_DIR (fichiers copiés depuis
# frontend/node_modules/katex/dist) - pas un import direct de cette constante privée,
# même raisonnement qu'inedit/sujet_pdf.py et fiches/pdf.py : reste correct même si son
# chemin venait à changer indépendamment (calculé relatif à catalog, pas à quiz).
_KATEX_DIR = Path(settings.BASE_DIR) / "catalog" / "static" / "katex"


def _cursus_display(cursus):
    # libelle_cursus connaît les séries du GCE (« Technical », jamais « Série GCE_TECHNICAL »).
    return libelle_cursus([cursus])


def _textes(session):
    """Les textes du PDF dans la langue du CONTENU de la session (voir catalog.pdf_textes) : un quiz du
    GCE sort en anglais de bout en bout."""
    langue = langue_du_contenu(subject=session.subject if session.subject_id else None, cursus=session.cursus)
    return textes_pdf(langue, site=settings.SITE_NAME)


# _competence_item_corrige (quiz.views) injecte un marqueur "[COURS_LINK:slug]" isolé -
# jamais du Markdown standard, seulement compris par le frontend React (voir
# frontend/src/components/EpreuveMarkdown.tsx, COURS_LINK_SENTINEL) pour afficher un
# bouton "Voir le cours complet". Sans conversion ici, `markdown.markdown()` (bibliothèque
# Python, ne connaît pas ce marqueur) l'aurait laissé tel quel dans le PDF, en texte brut
# illisible - on le convertit donc en vrai lien Markdown avant le rendu.
_COURS_LINK_RE = re.compile(r"^\[COURS_LINK:([a-zA-Z0-9_-]+)\]$", re.MULTILINE)


def _resolve_cours_links(markdown_text, libelle="Voir le cours complet →", langue="fr"):
    # settings.PDF_SITE_URL, pas FRONTEND_URL - voir catalog.sujet_pdf._lesson_deep_link.
    # Dans la langue du PDF : un quiz anglais mène à la page anglaise du cours (`/en/lessons/x`).
    return _COURS_LINK_RE.sub(
        lambda m: f"[{libelle}]({settings.PDF_SITE_URL}{chemin_public(f'/cours/{m.group(1)}', langue)})", markdown_text,
    )


# ?ref=pdf_quiz_fiche / ?ref=pdf_quiz_correction distinguent la provenance de chaque
# variante (même convention ?ref= que catalog.sujet_pdf._lesson_deep_link et
# fiches/pdf.py._sujet_deep_link/_corrige_deep_link) - seule façon de mesurer combien de
# visites viennent réellement de l'une ou l'autre fiche téléchargée.
def _sujet_deep_link(session):
    country_code = session.cursus.country.code.lower()
    return f"{settings.PDF_SITE_URL}/{country_code}?ref=pdf_quiz_fiche"


def _corrige_deep_link(session):
    country_code = session.cursus.country.code.lower()
    return f"{settings.PDF_SITE_URL}/{country_code}?ref=pdf_quiz_correction"


# Au-delà, le titre ne tient plus sur une ligne de l'en-tête : il dit « Plusieurs matières », et chaque
# question porte la sienne.
MATIERES_NOMMEES_MAX = 3


def _questions(session):
    return (
        session.quiz_questions
        .select_related("question__exercise__lesson__subject", "competence_item__theme", "competence_item__subject")
        .order_by("ordre")
    )


def _matiere_de_la_question(quiz_question):
    return ((instantane.donnees(quiz_question) or {}).get("subject") or {}).get("label") or ""


def matieres_de_la_session(session, quiz_questions=None):
    """
    Les matières de la fiche, dans l'ordre où elles apparaissent. La session n'en porte une que si l'élève
    a choisi une matière au lancement : un quiz lancé depuis un thème, une révision ou un quiz mêlé n'en a
    pas, et la fiche sortait alors sans titre. On la lit donc sur les questions elles-mêmes (leur instantané).
    """
    if session.subject_id:
        return [session.subject.label]
    matieres = []
    for quiz_question in _questions(session) if quiz_questions is None else quiz_questions:
        matiere = _matiere_de_la_question(quiz_question)
        if matiere and matiere not in matieres:
            matieres.append(matiere)
    return matieres


def _titre_matieres(matieres, tx):
    if len(matieres) > MATIERES_NOMMEES_MAX:
        return tx["quiz_plusieurs_matieres"]
    return " · ".join(matieres)


def _bloc_question(quiz_question, *, avec_corrige, tx, avec_matiere=False):
    """
    Un bloc "Question N" du PDF - énoncé seul si avec_corrige=False (le PDF "Fiche"),
    énoncé puis corrigé sinon (le PDF "Correction") ; jamais la réponse donnée par
    l'élève ni une indication correct/incorrect (voir la docstring de module). L'énoncé
    d'une QCM vient avec ses propositions (voir catalog.pdf_textes.propositions_markdown),
    et sa correction nomme la bonne lettre avant de l'expliquer. Import
    différé de quiz.views : quiz.views importe ce module au niveau top-level (voir
    queue_quiz_fiche_pdf_generation, appelée depuis quiz.views.quiz_fiche_pdf), un
    import top-level symétrique ici créerait un cycle. `avec_matiere` : la fiche mêle plusieurs
    matières, chaque question nomme la sienne dans son titre.
    """
    from .views import _clean_quiz_markdown, _corrige_de_la_question

    # L'instantané, pas le contenu vivant : le PDF reprend ce que l'élève a réellement vu.
    donnees = instantane.donnees(quiz_question)
    if donnees["source"] == "competence_item":
        enonce = donnees["enonce_markdown"].strip()
    else:
        enonce = _clean_quiz_markdown(donnees["enonce_markdown"]).strip()

    titre = f"## Question {quiz_question.ordre}"
    matiere = avec_matiere and _matiere_de_la_question(quiz_question)
    if matiere:
        titre = f"{titre} - {matiere}"
    blocs = [titre, enonce]
    choix = donnees.get("choix")
    # La Fiche laisse les cases vides, à cocher ; la Correction coche celle de la bonne réponse.
    propositions = propositions_markdown(choix, cochee=donnees.get("reponse_correcte") if avec_corrige else None)
    if propositions:
        blocs.append(propositions)
    if avec_corrige:
        bonne_reponse = propositions and bonne_reponse_markdown(choix, donnees.get("reponse_correcte"), tx)
        if bonne_reponse:
            blocs.append(bonne_reponse)
        if donnees["source"] == "competence_item":
            corrige = _corrige_de_la_question(quiz_question, donnees).strip()
        else:
            corrige = donnees["corrige_markdown"].strip()
        # Les items générés par concepteur-quiz-competence ouvrent déjà sur leurs propres
        # titres ("### Rappel de méthode", puis "### Corrigé") ; les plus anciens (et
        # l'historique catalog.Question) n'en ont aucun - sans ce repli, l'énoncé et sa
        # solution se toucheraient sans démarcation visible (même logique que
        # fiches.pdf._bloc_question).
        if not corrige.startswith("#"):
            corrige = f"### {tx['titre_corrige']}\n\n{corrige}"
        blocs.append(corrige)

    return "\n\n".join(blocs)


def _combined_markdown(session, *, avec_corrige):
    tx = _textes(session)
    quiz_questions = list(_questions(session))
    avec_matiere = len(matieres_de_la_session(session, quiz_questions)) > 1
    return adapter_markdown(
        "\n\n".join(
            _bloc_question(qq, avec_corrige=avec_corrige, tx=tx, avec_matiere=avec_matiere) for qq in quiz_questions
        ),
        tx["langue"],
    )


def _render_html(session, *, avec_corrige, template_name, deep_link):
    tx = _textes(session)
    markdown_text = _resolve_cours_links(
        _resolve_media_paths(_combined_markdown(session, avec_corrige=avec_corrige)), tx["voir_cours"], tx["langue"],
    )
    protected_markdown, math_spans = _protect_math(markdown_text)
    protected_markdown = _italicize_quotes(protected_markdown)
    content_html = markdown.markdown(protected_markdown, extensions=EXTENSIONS_MARKDOWN_QUIZ)
    content_html = _restore_math(content_html, math_spans)

    return render_to_string(template_name, {
        "session": session,
        "tx": tx,
        "subject_label": _titre_matieres(matieres_de_la_session(session), tx),
        "cursus_display": _cursus_display(session.cursus),
        "total_questions": session.quiz_questions.count(),
        "content_html": content_html,
        "site_name": settings.SITE_NAME,
        # Le lien ramène à l'accueil du pays : une adresse assez courte pour être tapée telle quelle.
        "fin": contexte_fin(
            tx, lien=deep_link, titre=tx["quiz_cta_titre"], corps=tx["quiz_cta_corps"], bouton=tx["quiz_cta_lien"],
            qr_alt=tx["quiz_qr_alt"], legende=tx["quiz_qr_legende"],
            adresse=f"{adresse_du_site()}/{session.cursus.country.code.lower()}",
        ),
        "katex_css_url": (_KATEX_DIR / "katex.min.css").as_uri(),
        "katex_js_url": (_KATEX_DIR / "katex.min.js").as_uri(),
        "katex_auto_render_url": (_KATEX_DIR / "contrib" / "auto-render.min.js").as_uri(),
    })


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
    return html_vers_pdf(sujet_html), html_vers_pdf(corrige_html)


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
