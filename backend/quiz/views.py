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


def _question_payload(quiz_question):
    """
    Contenu d'une QuizQuestion pour le client. corrige_markdown/reponse_correcte ne
    sont JAMAIS inclus tant que l'élève n'a pas répondu - sans quoi la bonne réponse
    serait consultable via l'onglet réseau du navigateur avant de répondre, ce qui vide
    le test/quiz de tout sens. Révélés uniquement une fois une QuizAnswer enregistrée.
    """
    question = quiz_question.question
    payload = {
        "id": quiz_question.id,
        "ordre": quiz_question.ordre,
        "numero": question.numero,
        "enonce_intro_markdown": question.exercise.enonce_intro_markdown,
        "enonce_markdown": question.enonce_markdown,
        "type_reponse": question.type_reponse,
        "choix": question.choix,
    }

    answer = _get_answer(quiz_question)
    if answer:
        payload["corrige_markdown"] = question.corrige_markdown
        payload["reponse_correcte"] = question.reponse_correcte
        payload["reponse"] = {
            "reponse_choisie": answer.reponse_choisie,
            "resultat_declare": answer.resultat_declare,
            "est_correcte": answer.est_correcte,
        }

    return payload


def _session_payload(session):
    quiz_questions = (
        session.quiz_questions
        .select_related("question__exercise", "answer")
        .order_by("ordre")
    )
    return {
        "id": session.id,
        "mode": session.mode,
        "cursus": session.cursus_id,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "total_questions": quiz_questions.count(),
        "questions": [_question_payload(qq) for qq in quiz_questions],
    }


def _resultat_payload(session):
    quiz_questions = (
        session.quiz_questions
        .select_related("answer", "question")
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
        for theme in quiz_question.question.themes.all():
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
    cursus = get_object_or_404(Cursus, pk=request.data.get("cursus"))

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
        QuizQuestion.objects.select_related("question"),
        pk=quiz_question_id, session_id=session_id, session__user=request.user,
    )
    question = quiz_question.question
    return Response({"corrige_markdown": question.corrige_markdown, "reponse_correcte": question.reponse_correcte})


@api_view(["POST"])
def answer_question(request, session_id, quiz_question_id):
    quiz_question = get_object_or_404(
        QuizQuestion.objects.select_related("question"),
        pk=quiz_question_id, session_id=session_id, session__user=request.user,
    )
    question = quiz_question.question

    defaults = {}
    temps = request.data.get("temps_secondes")
    if temps not in (None, ""):
        try:
            defaults["temps_secondes"] = int(temps)
        except (TypeError, ValueError):
            return Response({"error": "temps_secondes doit être un entier."}, status=400)

    if question.type_reponse == TypeReponse.QCM:
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
