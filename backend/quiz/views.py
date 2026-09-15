import re

from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Cours, Cursus, StatutContenu, Subject, Tag, TypeReponse
from catalog.rendering import annotate_single_cours_link
from catalog.serializers import CoursSummarySerializer, SubjectSerializer
from programme.models import Savoir
from subscriptions.models import Subscription

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare, StatutFichePdf
from .pdf import queue_quiz_fiche_pdf_generation
from .services import (
    construire_parcours, enregistrer_resultat_pour_revision, generer_session, maitrise_par_theme, resume_parcours,
    revisions_dues,
)


def _has_active_subscription(user, cursus):
    """Même vérification que start_session (voir sa docstring) - revérifiée à chaque
    téléchargement de fiche PDF puisqu'un abonnement peut avoir expiré depuis la fin
    du quiz, même principe que inedit.views.download_sujet_pdf."""
    return Subscription.objects.filter(user=user, cursus=cursus, expires_at__gt=timezone.now()).exists()


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


# Longueur minimale du libellé de compétence avant d'autoriser le rapprochement
# approximatif du niveau 3 : « Fonctions » ou « Suites » matcheraient des dizaines de
# cours sans rapport, alors que « Arithmétique » ou « Équations différentielles »
# désignent bien un chapitre. En dessous, on préfère aucun lien à un lien douteux.
_LIBELLE_MIN = 8


def _cours_pour_competence(item):
    """
    Le Cours publié qui correspond le mieux à la compétence d'un CompetenceItem, cherché
    en trois passes de précision décroissante. La première qui rend un résultat gagne.

    Pourquoi une cascade plutôt qu'un seul appariement par tag : deux vocabulaires de
    tags coexistent dans le catalogue, à deux granularités différentes. correction-experte
    pose des tags de TECHNIQUE sur les cours et les exercices (« algorithme d'Euclide »,
    « pavage »), tandis que le quiz porte des tags de CHAPITRE alignés sur les savoirs
    officiels et suffixés par série pour éviter les collisions entre programmes
    (« Arithmétique (Tle C) »). Les deux ne se recouvrent que par accident : l'égalité
    stricte de tag ne reliait que 108 items sur 336, alors que les cours existaient.

    1. Tag identique - le signal le plus fort, un cours explicitement rattaché à cette
       compétence.
    2. Savoir officiel partagé - le cours et la compétence pointent le même savoir du
       programme, par des tags différents. Sémantiquement aussi sûr que le niveau 1.
    3. Libellé du chapitre retrouvé dans le sous-thème ou le titre du cours, une fois
       retiré le suffixe de série. Approximatif, donc encadré par _LIBELLE_MIN.

    Tri explicite par identifiant à chaque niveau : sans lui, `.first()` rend un cours
    arbitraire que le SGBD peut changer d'une requête à l'autre, et l'élève verrait le
    lien pointer ailleurs d'une session à la suivante.
    """
    publies = (
        Cours.objects.visibles()
        .filter(subject=item.subject)
        .filter(Q(cursus__in=item.cursus.all()) | Q(cursus__isnull=True))
        .distinct()
        .order_by("id")
    )

    exact = publies.filter(tags=item.theme).first()
    if exact:
        return exact

    savoir_id = item.theme.savoir_officiel_id
    if savoir_id:
        par_savoir = publies.filter(tags__savoir_officiel_id=savoir_id).first()
        if par_savoir:
            return par_savoir

    libelle = item.theme.name.split("(")[0].strip()
    if len(libelle) >= _LIBELLE_MIN:
        return publies.filter(
            Q(sous_theme__icontains=libelle) | Q(titre__icontains=libelle),
        ).first()
    return None


def _competence_item_corrige(item):
    """
    corrige_markdown d'un CompetenceItem, avec un lien "Voir le cours complet" injecté
    quand un Cours publié couvre déjà sa compétence (voir _cours_pour_competence) - jamais
    généré ou deviné par le skill de génération (concepteur-quiz-competence n'a aucun moyen
    fiable de connaître un slug de Cours au moment de la génération), toujours recalculé à la
    lecture pour rester exact même si le Cours correspondant est publié après coup.
    Même principe que catalog.rendering._clean_exercise_corrige pour Exercise, jamais
    persisté sur item.corrige_markdown lui-même.
    """
    cours = _cours_pour_competence(item)
    if not cours:
        return item.corrige_markdown
    return annotate_single_cours_link(item.corrige_markdown, cours.slug)


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
            payload["corrige_markdown"] = _competence_item_corrige(item)
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
        "cursus": session.cursus_id,
        "subject": session.subject_id,
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

    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    mode = request.data.get("mode") or ModeQuiz.PRATIQUE
    if mode not in ModeQuiz.values:
        return Response({"error": f"mode invalide : {mode!r}. Attendu {ModeQuiz.values}."}, status=400)

    subject = get_object_or_404(Subject, pk=request.data["subject"]) if request.data.get("subject") else None
    theme = get_object_or_404(Tag, pk=request.data["theme"]) if request.data.get("theme") else None
    savoir = get_object_or_404(Savoir, pk=request.data["savoir"]) if request.data.get("savoir") else None

    try:
        n = int(request.data.get("n") or 10)
    except (TypeError, ValueError):
        n = 10

    try:
        session = generer_session(request.user, cursus, mode, subject=subject, theme=theme, savoir=savoir, n=n)
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
    corrige_markdown = (
        _competence_item_corrige(contenu) if quiz_question.competence_item_id else contenu.corrige_markdown
    )
    return Response({"corrige_markdown": corrige_markdown, "reponse_correcte": contenu.reponse_correcte})


@api_view(["POST"])
def answer_question(request, session_id, quiz_question_id):
    quiz_question = get_object_or_404(
        QuizQuestion.objects.select_related(
            "session", "question__exercise__lesson__subject", "competence_item",
        ),
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

    answer, _created = QuizAnswer.objects.update_or_create(quiz_question=quiz_question, defaults=defaults)

    if quiz_question.competence_item_id:
        item = quiz_question.competence_item
        enregistrer_resultat_pour_revision(
            request.user, quiz_question.session.cursus, item.subject, item.theme, answer.est_correcte,
        )

    return Response(_question_payload(quiz_question))


@api_view(["POST"])
def complete_session(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    if not session.completed_at:
        session.completed_at = timezone.now()
        session.save(update_fields=["completed_at"])
    return Response(_resultat_payload(session))


def _fiche_pdf_payload(session):
    return {
        "statut": session.fiche_pdf_statut,
        "sujet_pdf_disponible": bool(session.sujet_pdf),
        "corrige_pdf_disponible": bool(session.corrige_pdf),
    }


@api_view(["GET", "POST"])
def quiz_fiche_pdf(request, session_id):
    """
    Statut des deux PDF (Fiche = énoncés seuls, Correction = énoncés+corrigé) d'une
    QuizSession - réservée aux abonnés actifs sur le cursus de la session, revérifié à
    CHAQUE appel (l'abonnement peut avoir expiré depuis, voir _has_active_subscription).
    Disponible dès le début de la session, pas seulement une fois terminée : le tirage
    des QuizQuestion est figé à la création (voir QuizQuestion, "jamais modifiée après
    création"), donc le contenu des deux PDF ne dépend pas de l'avancement de l'élève -
    rien n'empêche de les vouloir imprimer avant même d'avoir répondu à la première
    question. POST déclenche la génération des deux en arrière-plan (no-op si déjà en
    cours ou déjà prête - le contenu ne change jamais après le tirage initial, jamais
    besoin de régénérer) ; GET sert au poll pendant qu'ils se génèrent hors ligne (voir
    quiz.pdf, jamais dans le thread de cette requête). Même couple GET/POST que
    fiches.views.create_fiche + fiche_detail, fusionné ici en une seule vue car les deux
    portent sur la même ressource (LA paire de PDF de CETTE session, pas une collection).
    """
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    if not _has_active_subscription(request.user, session.cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    if request.method == "POST" and session.fiche_pdf_statut not in (StatutFichePdf.EN_COURS, StatutFichePdf.PRETE):
        session.fiche_pdf_statut = StatutFichePdf.EN_COURS
        session.save(update_fields=["fiche_pdf_statut"])
        queue_quiz_fiche_pdf_generation(session.id)

    return Response(_fiche_pdf_payload(session))


@api_view(["GET"])
def download_quiz_sujet_pdf(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    if not _has_active_subscription(request.user, session.cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)
    if not session.sujet_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)
    return FileResponse(
        session.sujet_pdf.open("rb"), as_attachment=False,
        filename=f"quiz-{session.pk}-fiche.pdf", content_type="application/pdf",
    )


@api_view(["GET"])
def download_quiz_corrige_pdf(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    if not _has_active_subscription(request.user, session.cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)
    if not session.corrige_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)
    return FileResponse(
        session.corrige_pdf.open("rb"), as_attachment=False,
        filename=f"quiz-{session.pk}-correction.pdf", content_type="application/pdf",
    )


@api_view(["GET"])
def list_revisions_dues(request):
    """
    File "à réviser aujourd'hui" (voir quiz.services.revisions_dues) : un thème par
    ligne, avec de quoi le reprendre tout de suite - un raccourci vers un quiz ciblé sur
    ce seul thème (même cursus/matière, voir startQuizSession côté frontend) et les
    cours déjà publiés qui le couvrent, s'il y en a.
    """
    today = timezone.localdate()
    payload = []
    for schedule in revisions_dues(request.user):
        cours_qs = (
            Cours.objects.visibles()
            .filter(subject=schedule.subject, tags=schedule.theme)
            .filter(Q(cursus=schedule.cursus) | Q(cursus__isnull=True))
            .distinct()
        )
        payload.append({
            "id": schedule.id,
            "theme": schedule.theme.name,
            "theme_id": schedule.theme_id,
            "subject_id": schedule.subject_id,
            "subject_label": schedule.subject.label,
            "cursus": schedule.cursus_id,
            "cursus_display": _cursus_display(schedule.cursus),
            "jours_retard": (today - schedule.due_at).days,
            "cours": CoursSummarySerializer(cours_qs, many=True, context={"request": request}).data,
        })
    return Response(payload)


@api_view(["GET"])
def list_quiz_subjects(request):
    """
    Matières ayant au moins un CompetenceItem VALIDE pour le cursus donné - seule liste
    que QuizStartPage doit proposer : lister toutes les matières du pays (comme
    catalog.SubjectListView) laisserait choisir une matière sans aucune banque de quiz
    générée pour ce cursus, et generer_session échouerait (ValueError "Aucune question
    disponible") une fois le quiz lancé plutôt que de le signaler avant.
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    qs = (
        Subject.objects.filter(competence_items__statut=StatutContenu.VALIDE, competence_items__cursus=cursus)
        .select_related("country")
        .distinct()
        .order_by("label")
    )
    return Response(SubjectSerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET"])
def maitrise(request):
    """
    Vue d'ensemble de la maîtrise par thème (voir quiz.services.maitrise_par_theme) -
    alimente le tableau "Ma maîtrise" de la page Compte. `cursus` optionnel : sans lui,
    l'historique complet de l'utilisateur tous cursus confondus.
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"]) if request.GET.get("cursus") else None
    return Response(maitrise_par_theme(request.user, cursus=cursus))


@api_view(["GET"])
def parcours(request):
    """
    Vue séquencée du programme officiel pour un cursus/matière donnés (voir
    quiz.services.construire_parcours) - alimente la page /parcours. `cursus` et
    `subject` sont tous deux requis : contrairement à `maitrise`/`revisions`, la
    page qui consomme cet endpoint affiche un seul programme à la fois, jamais un
    historique agrégé tous cursus/matières confondus.
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    subject = get_object_or_404(Subject, pk=request.GET["subject"])
    return Response(construire_parcours(request.user, cursus, subject))


@api_view(["GET"])
def parcours_resume(request):
    """
    Tableau de bord "toutes tes matières" (voir quiz.services.resume_parcours) : une
    ligne par matière ayant un programme officiel pour ce cursus, réduite à un
    histogramme de statuts par savoir. Point d'entrée au-dessus de `parcours`
    (détail séquencé d'une seule matière).
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    return Response(resume_parcours(request.user, cursus))
