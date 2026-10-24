"""
Historique des quiz d'un profil : liste des tentatives terminées, consultation en lecture
seule d'une tentative, rejeu.

Trois gestes distincts, jamais confondus :
- CONSULTER une tentative terminée : lecture seule, tout vient de l'instantané figé à sa
  création (voir quiz.instantane) - ce que l'élève a vu, la clé sur laquelle il a été jugé ;
- REJOUER : une NOUVELLE session, mêmes questions dans le même ordre (copiées de
  l'instantané, donc identiques même si le contenu a changé ou disparu), sans réponses
  préremplies. L'ancienne session n'est jamais touchée ;
- (REPRENDRE une session en cours n'est pas traité ici : voir la note de livraison.)

Un rejeu est NEUTRE pour la progression : aucun XP, aucun palier de révision gagné, absent de
la maîtrise. L'XP récompense la maîtrise, pas le volume (voir quiz.xp), et son plafond n'est
que quotidien : rejouer les mêmes questions chaque jour ferait gagner de l'XP et « graduer »
des thèmes par simple mémorisation. Une réponse FAUSSE en rejeu compte quand même pour le
suivi de révision (voir quiz.views.answer_question) : une erreur est un vrai signal. Le
marqueur est `QuizSession.rejeu_de` ; les requêtes de maîtrise l'excluent. `refaire_ratees`
n'est pas un rejeu (remédiation réelle) et garde son comportement.
"""

from collections import defaultdict
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from subscriptions.models import Subscription
from users.profils import profil_actif

from . import instantane, textes
from .models import CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession

TAILLE_PAGE = 20


def rejouer_session(profil, session):
    """
    Une nouvelle session indépendante, mêmes questions et même ordre que `session` (terminée),
    reconstruites depuis l'instantané. Renvoie (rejeu, cree) : `cree` est faux quand un rejeu
    encore vierge de la même chaîne existait déjà - un double clic ou une requête rejouée ne
    fabrique pas deux sessions.

    `rejeu_de` pointe toujours vers la session d'ORIGINE de la chaîne : rejouer un rejeu ne
    crée pas de chaîne profonde, et le numéro de tentative reste lisible. Mode PRATIQUE quel
    que soit celui d'origine : un rejeu de test de niveau ne doit pas passer pour un nouveau
    diagnostic (voir quiz.priorites).
    """
    origine_id = session.rejeu_de_id or session.pk
    with transaction.atomic():
        # Verrou sur l'origine : sérialise deux demandes simultanées de la même chaîne.
        QuizSession.objects.select_for_update().get(pk=origine_id)
        vierge = (
            QuizSession.objects.filter(profil=profil, rejeu_de_id=origine_id, completed_at__isnull=True)
            .exclude(quiz_questions__answer__isnull=False)
            .order_by("-started_at")
            .first()
        )
        if vierge is not None:
            return vierge, False

        rejeu = QuizSession.objects.create(
            profil=profil, cursus=session.cursus, subject=session.subject, theme=session.theme,
            mode=ModeQuiz.PRATIQUE, rejeu_de_id=origine_id,
        )
        questions = []
        for quiz_question in (
            session.quiz_questions.select_related("competence_item__theme", "competence_item__subject", "question")
            .order_by("ordre")
        ):
            figee = instantane.donnees(quiz_question)
            questions.append(QuizQuestion(
                session=rejeu, competence_item_id=quiz_question.competence_item_id,
                question_id=quiz_question.question_id, ordre=quiz_question.ordre, snapshot=figee,
                snapshot_retroactif=quiz_question.snapshot_retroactif,
            ))
        QuizQuestion.objects.bulk_create(questions)
    return rejeu, True


def _duree_secondes(reponses, total):
    """Somme des temps de réponse, seulement si TOUTES les questions ont une réponse chronométrée : une durée
    partielle serait un chiffre faux. Mesurés côté client, donc indicatifs - jamais utilisés
    pour noter ou classer."""
    if not reponses or len(reponses) < total or any(r.temps_secondes is None for r in reponses):
        return None
    return sum(r.temps_secondes for r in reponses)


def _numeros_de_tentative(profil, sessions):
    """{session_id: (numero, nombre)} dans la chaîne de rejeux de chaque session : l'origine
    est la tentative 1, chaque rejeu suit par date de début. Une seule requête pour la page."""
    origines = {s.rejeu_de_id or s.pk for s in sessions}
    chaine = defaultdict(list)
    for pk, rejeu_de_id in (
        QuizSession.objects.filter(Q(pk__in=origines) | Q(rejeu_de_id__in=origines), profil=profil)
        .order_by("started_at", "pk").values_list("pk", "rejeu_de_id")
    ):
        chaine[rejeu_de_id or pk].append(pk)
    resultat = {}
    for membres in chaine.values():
        for rang, pk in enumerate(membres, start=1):
            resultat[pk] = (rang, len(membres))
    return resultat


def _libelle_cursus(cursus, memo):
    """display_examen interroge ExamenLabel à chaque appel : un libellé par cursus et par page, pas par ligne."""
    if cursus.pk not in memo:
        examen = cursus.display_examen()
        memo[cursus.pk] = f"{examen} - Série {cursus.series.code}" if cursus.series else examen
    return memo[cursus.pk]


def _resume(session, reponses, numeros, libelles):
    total = session.nb_questions
    score = sum(1 for r in reponses if r.est_correcte)
    numero, nombre = numeros.get(session.pk, (1, 1))
    return {
        "id": session.id,
        "mode": session.mode,
        "cursus": session.cursus_id,
        "cursus_display": _libelle_cursus(session.cursus, libelles),
        "subject": session.subject_id,
        "subject_label": session.subject.label if session.subject_id else "",
        "theme": session.theme.name if session.theme_id else "",
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "duree_secondes": _duree_secondes(reponses, total),
        "score": score,
        "total_questions": total,
        "pourcentage": round(100 * score / total) if total else 0,
        "rejeu_de": session.rejeu_de_id,
        "numero_tentative": numero,
        "nb_tentatives": nombre,
    }


def _reponses_par_session(sessions):
    par_session = defaultdict(list)
    for reponse in QuizAnswer.objects.filter(quiz_question__session__in=sessions).select_related("quiz_question"):
        par_session[reponse.quiz_question.session_id].append(reponse)
    return par_session


@api_view(["GET"])
def historique(request):
    """
    GET /quiz/historique/ - les tentatives TERMINÉES du profil actif, la plus récente d'abord,
    paginées. Le filtre par profil est ici, côté serveur : l'URL ne désigne jamais l'élève.
    """
    profil = profil_actif(request)
    sessions = (
        QuizSession.objects.filter(profil=profil, completed_at__isnull=False)
        .select_related("cursus__country", "cursus__series", "subject", "theme")
        .annotate(nb_questions=Count("quiz_questions"))
        .order_by("-completed_at", "-pk")
    )
    paginateur = PageNumberPagination()
    paginateur.page_size = TAILLE_PAGE
    page = paginateur.paginate_queryset(sessions, request)

    reponses = _reponses_par_session(page)
    numeros = _numeros_de_tentative(profil, page)
    libelles = {}
    return paginateur.get_paginated_response([_resume(s, reponses.get(s.pk, []), numeros, libelles) for s in page])


def _question_historique(quiz_question, reponse):
    """Une question telle qu'elle a été présentée : tout vient de l'instantané. Les
    corrections sont incluses parce que la session est terminée."""
    from .views import _clean_quiz_markdown

    donnees = instantane.donnees(quiz_question)
    est_item = donnees["source"] == "competence_item"
    question = {
        "id": quiz_question.id,
        "ordre": quiz_question.ordre,
        "enonce_markdown": donnees["enonce_markdown"] if est_item else _clean_quiz_markdown(donnees["enonce_markdown"]),
        "type_reponse": donnees["type_reponse"],
        "choix": donnees["choix"],
        "theme": donnees["theme"]["name"] if est_item else "",
        "theme_id": donnees["theme"]["id"] if est_item else None,
        "subject_code": donnees["subject"]["code"] if est_item else None,
        "subject_label": donnees["subject"]["label"],
        "reponse_correcte": donnees["reponse_correcte"],
        "corrige_markdown": donnees["corrige_markdown"],
        # Contenu encore consultable aujourd'hui ? (faux si supprimé depuis)
        "contenu_disponible": quiz_question.competence_item_id is not None or quiz_question.question_id is not None,
        # La clé actuelle diffère de celle de cette tentative : simple mention « corrigé depuis ».
        # La note, elle, n'est jamais recalculée.
        "cle_modifiee": instantane.cle_a_change(quiz_question),
        "snapshot_retroactif": quiz_question.snapshot_retroactif,
        "reponse": None,
    }
    if not est_item:
        question["enonce_intro_markdown"] = _clean_quiz_markdown(donnees["enonce_intro_markdown"])
        question["numero"] = donnees["numero"]
    if reponse is not None:
        question["reponse"] = {
            "reponse_choisie": reponse.reponse_choisie,
            "resultat_declare": reponse.resultat_declare,
            "est_correcte": reponse.est_correcte,
            "temps_secondes": reponse.temps_secondes,
        }
    return question


@api_view(["GET"])
def historique_detail(request, session_id):
    """
    GET /quiz/historique/<id>/ - une tentative terminée, en lecture seule : questions, réponses
    données, bonnes réponses, corrigés, score. 404 pour la session d'un autre profil comme pour
    une session inexistante ou encore en cours (consulter ne s'applique qu'au terminé).
    """
    profil = profil_actif(request)
    session = get_object_or_404(
        QuizSession.objects.select_related("cursus__country", "cursus__series", "subject", "theme")
        .annotate(nb_questions=Count("quiz_questions")),
        pk=session_id, profil=profil, completed_at__isnull=False,
    )
    quiz_questions = list(
        session.quiz_questions.select_related("answer", "competence_item", "question").order_by("ordre"),
    )
    reponses = [qq.answer for qq in quiz_questions if hasattr(qq, "answer")]
    numeros = _numeros_de_tentative(profil, [session])

    payload = _resume(session, reponses, numeros, {})
    payload["questions"] = [_question_historique(qq, getattr(qq, "answer", None)) for qq in quiz_questions]
    payload["snapshot_retroactif"] = any(qq.snapshot_retroactif for qq in quiz_questions)
    payload["peut_rejouer"] = bool(quiz_questions)
    return Response(payload)


@api_view(["POST"])
def rejouer(request, session_id):
    """
    POST /quiz/historique/<id>/rejouer/ - crée un rejeu de cette tentative terminée (201), ou
    renvoie le rejeu encore vierge qui existe déjà (200). Mêmes règles d'accès que
    start_session, revérifiées à CHAQUE appel : abonnement actif sur le cursus, ou session
    entièrement composée d'items vitrine ; pays désactivé = introuvable.
    """
    from .views import _has_active_subscription, _session_payload

    profil = profil_actif(request)
    session = get_object_or_404(
        QuizSession.objects.select_related("cursus__country"), pk=session_id, profil=profil,
    )
    langue = textes.langue_de(session.cursus)
    if not session.completed_at:
        return Response({"error": textes.texte("quiz.rejeu_session_en_cours", langue)}, status=409)
    if not session.cursus.country.actif:
        return Response({"error": textes.texte("quiz.aucune_question", langue)}, status=404)

    if not _has_active_subscription(request.user, session.cursus, profil):
        ids = list(session.quiz_questions.values_list("competence_item_id", flat=True))
        tous_vitrine = bool(ids) and None not in ids and (
            CompetenceItem.objects.filter(pk__in=ids, est_vitrine=True).count() == len(set(ids))
        )
        if not tous_vitrine:
            return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    rejeu, cree = rejouer_session(profil, session)
    return Response(_session_payload(rejeu), status=201 if cree else 200)


# Au-delà de ce délai sans réponse, une séance commencée est supposée abandonnée : la proposer encore
# serait du bruit. Même valeur que le frontend l'avait pour son ancien pointeur local (lib/quizEnCours.ts).
EN_COURS_JOURS = 3
EN_COURS_MAX = 5


def _sessions_jouables(profil, user, sessions):
    """Parmi `sessions`, celles que ce profil a le droit de poursuivre : mêmes règles d'accès que
    start_session (abonnement actif sur le cursus, ou session faite uniquement d'items vitrine). Un
    abonnement expiré depuis ne doit pas faire revenir un quiz payant par la porte de la reprise."""
    cursus_abonnes = set(
        Subscription.objects.filter(user=user, profil=profil, expires_at__gt=timezone.now())
        .values_list("cursus_id", flat=True)
    )
    a_verifier = [s for s in sessions if s.cursus_id not in cursus_abonnes]
    non_vitrine = set()
    if a_verifier:
        # Un item supprimé depuis (clé nulle) n'est pas vitrine : sans abonnement, pas de reprise.
        non_vitrine = set(
            QuizQuestion.objects.filter(session__in=a_verifier)
            .exclude(competence_item__est_vitrine=True).values_list("session_id", flat=True)
        )
    return [s for s in sessions if s.cursus_id in cursus_abonnes or s.pk not in non_vitrine]


@api_view(["GET"])
def en_cours(request):
    """
    GET /quiz/en-cours/ - les tentatives commencées et non terminées du profil actif (au plus
    EN_COURS_MAX, la dernière réponse en tête). Source unique de « Reprendre le quiz », sur tous les
    appareils : la progression est déjà enregistrée à chaque réponse, il ne manquait que de pouvoir
    les retrouver. Reprendre = rouvrir CETTE session (elle se place sur la première question sans
    réponse) ; ce n'est ni consulter (terminée, lecture seule) ni rejouer (une nouvelle session).

    Une session sans aucune réponse n'est pas une tentative interrompue : elle n'est pas listée.
    """
    profil = profil_actif(request)
    limite = timezone.now() - timedelta(days=EN_COURS_JOURS)
    sessions = list(
        QuizSession.objects.filter(profil=profil, completed_at__isnull=True)
        .select_related("cursus__country", "cursus__series", "subject", "theme")
        .annotate(
            nb_questions=Count("quiz_questions", distinct=True),
            nb_repondues=Count("quiz_questions__answer", distinct=True),
            derniere_reponse=Max("quiz_questions__answer__answered_at"),
        )
        .filter(nb_repondues__gt=0, derniere_reponse__gte=limite)
        .order_by("-derniere_reponse", "-pk")[: EN_COURS_MAX * 4]
    )
    sessions = _sessions_jouables(profil, request.user, sessions)[:EN_COURS_MAX]
    libelles = {}
    return Response([
        {
            "id": s.id,
            "mode": s.mode,
            "cursus": s.cursus_id,
            "cursus_display": _libelle_cursus(s.cursus, libelles),
            "subject": s.subject_id,
            "subject_label": s.subject.label if s.subject_id else "",
            "theme": s.theme.name if s.theme_id else "",
            "started_at": s.started_at,
            "derniere_reponse_at": s.derniere_reponse,
            "nb_repondues": s.nb_repondues,
            "total_questions": s.nb_questions,
            # Tout répondu mais pas rendu : reprendre mène au résultat, pas à une question.
            "a_terminer": s.nb_repondues >= s.nb_questions,
            "rejeu_de": s.rejeu_de_id,
        }
        for s in sessions
    ])
