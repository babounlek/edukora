import re

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Cursus, Subject, Tag, TypeReponse
from subscriptions.models import Subscription

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare
from .services import generer_session


def _get_answer(quiz_question):
    try:
        return quiz_question.answer
    except QuizAnswer.DoesNotExist:
        return None


# "### Exercice 1 (5 points)" ou "### Problème (10 points)" (parfois en gras plutôt
# qu'en titre) - correction-experte transcrit fidèlement l'en-tête de l'épreuve source
# au tout début de enonce_intro_markdown, ou directement dans l'enonce_markdown de la
# première sous-question quand l'exercice n'a pas d'enonce_intro_markdown propre.
# Légitime en lecture d'une épreuve complète (Lesson), mais une question de quiz doit
# se lire seule - jamais retiré des données stockées, seulement de ce payload.
_QUIZ_SECTION_HEADING_RE = re.compile(
    r"^\s*(?:#{1,4}\s*|\*\*\s*)(?:Exercice|Probl[eè]me)\b[^\n]*?(?:\*\*)?\s*\n+",
    re.IGNORECASE,
)
# Consigne d'épreuve papier ("écrivez-la sur votre feuille...") et barème - sans objet
# dans une question de quiz web (pas de copie à rendre, pas de points sur 20).
_QUIZ_EXAM_INSTRUCTION_RE = re.compile(
    r"[,;:]?\s*écrivez-la sur (?:votre feuille|votre copie)[^.]*\.",
    re.IGNORECASE,
)
_QUIZ_BAREME_RE = re.compile(r"\(\s*Bar[eè]me\s*:[^)]*\)", re.IGNORECASE)


def _clean_quiz_markdown(text):
    """Retire le cadre "épreuve papier" (en-tête Exercice/Problème, consigne de
    copie, barème) d'un texte affiché dans le Quiz - voir les regex ci-dessus."""
    if not text:
        return text
    text = _QUIZ_SECTION_HEADING_RE.sub("", text, count=1)
    text = _QUIZ_EXAM_INSTRUCTION_RE.sub("", text)
    text = _QUIZ_BAREME_RE.sub("", text)
    return text.strip()


def _question_payload(quiz_question):
    """
    Contenu d'une QuizQuestion pour le client. corrige_markdown/reponse_correcte ne
    sont JAMAIS inclus tant que l'élève n'a pas répondu - sans quoi la bonne réponse
    serait consultable via l'onglet réseau du navigateur avant de répondre, ce qui vide
    le test/quiz de tout sens. Révélés uniquement une fois une QuizAnswer enregistrée.

    Deux formes selon la source (voir QuizQuestion.contenu) : un CompetenceItem n'a ni
    numero ni enonce_intro_markdown/lesson d'origine (il n'appartient à aucun Exercise)
    et n'a pas besoin de _clean_quiz_markdown (jamais rédigé avec le cadre "épreuve
    papier" en premier lieu) ; une catalog.Question (historique pré-bascule
    uniquement - generer_session n'en pioche plus) garde le payload d'origine.
    """
    answer = _get_answer(quiz_question)

    if quiz_question.competence_item_id:
        item = quiz_question.competence_item
        payload = {
            "id": quiz_question.id,
            "ordre": quiz_question.ordre,
            "enonce_markdown": item.enonce_markdown,
            "type_reponse": item.type_reponse,
            "choix": item.choix,
            "theme": item.theme.name,
            "subject_label": item.subject.label,
        }
        if answer:
            payload["corrige_markdown"] = item.corrige_markdown
            payload["reponse_correcte"] = item.reponse_correcte
    else:
        question = quiz_question.question
        exercise = question.exercise
        payload = {
            "id": quiz_question.id,
            "ordre": quiz_question.ordre,
            "numero": question.numero,
            "enonce_intro_markdown": _clean_quiz_markdown(exercise.enonce_intro_markdown),
            "enonce_markdown": _clean_quiz_markdown(question.enonce_markdown),
            "type_reponse": question.type_reponse,
            "choix": question.choix,
            # Lien "Voir la leçon d'origine" et matière - une session peut mélanger des
            # questions de plusieurs leçons/matières (mode Pratique libre sans filtre),
            # donc portés par question, pas par session (voir QuizSessionPage.tsx).
            "lesson_id": exercise.lesson_id,
            "lesson_title": exercise.lesson.title,
            "subject_label": exercise.lesson.subject.label,
        }
        if answer:
            payload["corrige_markdown"] = question.corrige_markdown
            payload["reponse_correcte"] = question.reponse_correcte

    if answer:
        payload["reponse"] = {
            "reponse_choisie": answer.reponse_choisie,
            "resultat_declare": answer.resultat_declare,
            "est_correcte": answer.est_correcte,
        }

    return payload


def _cursus_display(cursus):
    return f"{cursus.display_examen()} - Série {cursus.series.code}" if cursus.series else cursus.display_examen()


def _session_payload(session):
    quiz_questions = (
        session.quiz_questions
        .select_related(
            "question__exercise__lesson__subject", "competence_item__theme", "competence_item__subject", "answer",
        )
        .order_by("ordre")
    )
    return {
        "id": session.id,
        "mode": session.mode,
        "cursus": session.cursus_id,
        # Uniforme pour toute la session (generer_session filtre sur un seul cursus),
        # contrairement à la matière qui peut varier d'une question à l'autre - voir
        # _question_payload.
        "cursus_display": _cursus_display(session.cursus),
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "total_questions": quiz_questions.count(),
        "questions": [_question_payload(qq) for qq in quiz_questions],
    }


def _resultat_payload(session):
    quiz_questions = (
        session.quiz_questions
        .select_related("answer", "question", "competence_item__theme")
        .prefetch_related("question__themes")
    )

    repondues = 0
    reussies = 0
    par_theme = {}

    for quiz_question in quiz_questions:
        answer = _get_answer(quiz_question)
        if not answer:
            continue
        repondues += 1
        correcte = answer.est_correcte
        if correcte:
            reussies += 1
        # CompetenceItem : un seul theme (FK) ; catalog.Question historique : plusieurs
        # (M2M) - voir QuizQuestion.contenu et CompetenceItem.theme.
        themes = (
            [quiz_question.competence_item.theme]
            if quiz_question.competence_item_id
            else list(quiz_question.question.themes.all())
        )
        for theme in themes:
            stats = par_theme.setdefault(theme.name, {"total": 0, "reussies": 0})
            stats["total"] += 1
            if correcte:
                stats["reussies"] += 1

    return {
        "id": session.id,
        "total_questions": quiz_questions.count(),
        "questions_repondues": repondues,
        "score": reussies,
        "par_theme": [
            {"theme": nom, "total": s["total"], "reussies": s["reussies"]}
            for nom, s in sorted(par_theme.items())
        ],
    }


@api_view(["POST"])
def start_session(request):
    """Crée une QuizSession pour l'utilisateur connecté - gating : réservé aux cursus
    pour lesquels un abonnement actif existe, même logique que access.services.has_access."""
    cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=request.data.get("cursus"))

    if not cursus.country.actif:
        # Un pays désactivé doit être invisible partout, y compris pour démarrer un
        # quiz sur l'un de ses cursus - 404 plutôt que 403 : il n'existe pas, on ne
        # refuse pas juste l'accès (voir catalog.models.VisibleQuerySet).
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

    if not Subscription.objects.filter(
        user=request.user, cursus=cursus, expires_at__gt=timezone.now(),
    ).exists():
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    mode = request.data.get("mode") or ModeQuiz.PRATIQUE
    if mode not in ModeQuiz.values:
        return Response({"error": f"mode invalide : {mode!r}. Attendu {ModeQuiz.values}."}, status=400)

    subject = get_object_or_404(Subject, pk=request.data["subject"]) if request.data.get("subject") else None
    theme = get_object_or_404(Tag, pk=request.data["theme"]) if request.data.get("theme") else None

    try:
        n = int(request.data.get("n") or 10)
    except (TypeError, ValueError):
        n = 10

    try:
        session = generer_session(request.user, cursus, mode, subject=subject, theme=theme, n=n)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=404)

    return Response(_session_payload(session), status=201)


@api_view(["GET"])
def session_detail(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    return Response(_session_payload(session))


@api_view(["GET"])
def reveal_corrige(request, session_id, quiz_question_id):
    """Révèle le corrigé d'une question à la demande de l'élève, sans enregistrer de
    réponse - étape distincte de answer_question pour les questions ouvertes, où
    l'élève doit pouvoir comparer sa propre tentative au corrigé avant de s'auto-évaluer
    (Réussi/Partiel/Échec). Le QCM n'en a pas besoin : la correction y est automatique
    dès la réponse."""
    quiz_question = get_object_or_404(
        QuizQuestion.objects.select_related("question", "competence_item"),
        pk=quiz_question_id, session_id=session_id, session__user=request.user,
    )
    contenu = quiz_question.contenu
    return Response({"corrige_markdown": contenu.corrige_markdown, "reponse_correcte": contenu.reponse_correcte})


@api_view(["POST"])
def answer_question(request, session_id, quiz_question_id):
    quiz_question = get_object_or_404(
        QuizQuestion.objects.select_related("question__exercise__lesson__subject", "competence_item"),
        pk=quiz_question_id, session_id=session_id, session__user=request.user,
    )
    contenu = quiz_question.contenu

    defaults = {}
    temps = request.data.get("temps_secondes")
    if temps not in (None, ""):
        try:
            defaults["temps_secondes"] = int(temps)
        except (TypeError, ValueError):
            return Response({"error": "temps_secondes doit être un entier."}, status=400)

    if contenu.type_reponse == TypeReponse.QCM:
        reponse_choisie = str(request.data.get("reponse_choisie") or "")
        if not reponse_choisie:
            return Response({"error": "reponse_choisie est requis pour une question QCM."}, status=400)
        defaults["reponse_choisie"] = reponse_choisie
    else:
        resultat = request.data.get("resultat_declare")
        if resultat not in ResultatDeclare.values:
            return Response(
                {"error": f"resultat_declare invalide : {resultat!r}. Attendu {ResultatDeclare.values}."}, status=400,
            )
        defaults["resultat_declare"] = resultat

    QuizAnswer.objects.update_or_create(quiz_question=quiz_question, defaults=defaults)

    return Response(_question_payload(quiz_question))


@api_view(["POST"])
def complete_session(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    if not session.completed_at:
        session.completed_at = timezone.now()
        session.save(update_fields=["completed_at"])
    return Response(_resultat_payload(session))
