import re
import unicodedata

from django.db.models import Count, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from analytics.models import AnalyticsEvent, EventName
from catalog.models import (
    Cours, Cursus, ExamSession, Lesson, Origine, StatutContenu, Subject, Tag, TypeReponse,
    q_cours_du_cursus,
)
from catalog.rendering import annotate_single_cours_link
from catalog.serializers import CoursSummarySerializer, CursusSerializer, SubjectSerializer, SubjectWithQuizCountSerializer
from programme.models import Savoir
from subscriptions.models import Subscription
from users.profils import profil_actif

from .models import (
    CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare, SeanceJournaliere,
    StatutFichePdf, StatutSeance,
)
from . import accueil
from .pdf import queue_quiz_fiche_pdf_generation
from .serie import serie_de_jours
from .services import (
    SEUIL_MAITRISE, cloturer_seance_si_quiz_termine, construire_parcours, enregistrer_resultat_pour_revision,
    generer_session, maitrise_par_theme, plan_du_jour, rattacher_quiz_a_la_seance, resume_parcours, revisions_dues,
    BUDGETS_SEANCE_MINUTES, ajuster_duree_seance, cle_etape, etape_ouverte, marquer_etape_ouverte, definir_objectif_matiere, matieres_pour_objectif, objectif_matiere_actif, retirer_objectif_matiere, exercices_du_theme, prochaine_revision, raisons_de_la_seance,
    perimetre_est_vitrine,
    remplacer_seance,
    score_de_la_seance,
    seance_du_jour,
    seance_supplementaire,
    seances_terminees_cette_semaine, terminer_seance,
)


def _has_active_subscription(user, cursus):
    """Même vérification que start_session (voir sa docstring) - revérifiée à chaque
    téléchargement de fiche PDF puisqu'un abonnement peut avoir expiré depuis la fin
    du quiz, même principe que inedit.views.download_sujet_pdf."""
    return Subscription.objects.filter(user=user, cursus=cursus, expires_at__gt=timezone.now()).exists()


# Années d'épreuves listées derrière "tombé dans N des M dernières épreuves" - assez
# pour que le chiffre devienne vérifiable, pas assez pour transformer la carte en
# tableau de bord.
ANNEES_FREQUENCE_MAX = 6


def _tracer_seance_terminee(seance):
    """
    "Séance terminée" est enregistré côté SERVEUR, contrairement aux autres évènements
    du plan qui partent du navigateur - parce que la voie principale n'est pas un clic :
    une séance se clôt toute seule quand son quiz est bouclé (voir
    cloturer_seance_si_quiz_termine). La tracer depuis le frontend raterait justement
    le cas le plus fréquent, et compterait deux fois celles qui passent par les deux
    chemins. Fire-and-forget comme son équivalent frontend : un évènement perdu ne doit
    jamais faire échouer la requête qu'il observe.
    """
    if seance is None:
        return
    try:
        AnalyticsEvent.objects.create(
            name=EventName.PLAN_SEANCE_TERMINEE,
            user=seance.profil.compte,
            properties={"origine": seance.origine, "cursus_id": seance.cursus_id},
        )
    except Exception:  # noqa: BLE001 - jamais au prix de la requête en cours
        pass


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


def _cours_pour_theme(theme, subject, cursus_ids, texte=""):
    """
    Le Cours publié qui correspond le mieux à un (thème, matière), cherché en trois
    passes de précision décroissante. La première qui rend un résultat gagne.

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

    À chaque niveau, plusieurs cours peuvent convenir (un thème générique comme
    « identité remarquable » en porte des dizaines, de la 3e à la Terminale) : le gagnant
    est celui dont le titre partage le plus de mots avec `texte` (énoncé + corrigé de
    l'item), puis le plus petit id - ordre stable, sans quoi l'élève verrait le lien
    pointer ailleurs d'une session à la suivante. Avant ce départage, le plus petit id
    gagnait seul : un rappel BEPC sur a²-b² pointait vers un cours de Terminale C sur
    le point fixe d'une transformation complexe, porteur du même tag.

    `cursus_ids` : un itérable d'id de Cursus (pas un seul) - un CompetenceItem peut
    couvrir plusieurs cursus (voir CompetenceItem.cursus, M2M), souvent du BEPC au BAC :
    passer de préférence le seul cursus de la session. Un Cours sans cursus n'est retenu
    que si sa lignée le rattache à l'un d'eux (voir q_cours_du_cursus).
    """
    publies = Cours.objects.visibles().filter(subject=subject).filter(q_cours_du_cursus(cursus_ids))

    niveaux = [Q(tags=theme)]
    if theme.savoir_officiel_id:
        niveaux.append(Q(tags__savoir_officiel_id=theme.savoir_officiel_id))
    libelle = theme.name.split("(")[0].strip()
    if len(libelle) >= _LIBELLE_MIN:
        niveaux.append(Q(sous_theme__icontains=libelle) | Q(titre__icontains=libelle))

    mots_texte = _mots_significatifs(texte)
    for niveau in niveaux:
        candidats = list(publies.filter(niveau).values_list("id", "titre").distinct())
        if candidats:
            meilleur_id, _ = min(
                candidats, key=lambda c: (-len(_mots_significatifs(c[1]) & mots_texte), c[0]),
            )
            return Cours.objects.get(pk=meilleur_id)
    return None


_LATEX_RE = re.compile(r"\$\$?[^$]*\$\$?")
_MOT_RE = re.compile(r"[a-z0-9]+")
_MOTS_VIDES = {
    "alors", "ainsi", "avec", "avoir", "bien", "cette", "chaque", "comme", "dans", "donc",
    "dont", "elle", "elles", "entre", "etre", "faire", "leur", "leurs", "meme", "moins",
    "nous", "partir", "plus", "pour", "puis", "quand", "sans", "sont", "sous", "suffit",
    "tous", "tout", "toute", "toutes", "vous",
}


def _mots_significatifs(texte):
    """Mots de 4 lettres et plus, sans accents ni formules LaTeX, hors mots vides -
    base du départage par pertinence de _cours_pour_theme."""
    texte = unicodedata.normalize("NFKD", _LATEX_RE.sub(" ", texte or "").lower())
    texte = "".join(ch for ch in texte if not unicodedata.combining(ch))
    return {m for m in _MOT_RE.findall(texte) if len(m) >= 4 and m not in _MOTS_VIDES}


def _texte_item(item):
    return f"{item.enonce_markdown}\n{item.corrige_markdown}"


def _competence_item_corrige(item, cursus_ids=None):
    """
    corrige_markdown d'un CompetenceItem, avec un lien "Voir le cours complet" injecté
    quand un Cours publié couvre déjà sa compétence (voir _cours_pour_theme) - jamais
    généré ou deviné par le skill de génération (concepteur-quiz-competence n'a aucun moyen
    fiable de connaître un slug de Cours au moment de la génération), toujours recalculé à la
    lecture pour rester exact même si le Cours correspondant est publié après coup.
    Même principe que catalog.rendering._clean_exercise_corrige pour Exercise, jamais
    persisté sur item.corrige_markdown lui-même. `cursus_ids` : le cursus de la session
    quand il est connu, à défaut ceux de l'item.
    """
    if cursus_ids is None:
        cursus_ids = item.cursus.values_list("id", flat=True)
    cours = _cours_pour_theme(item.theme, item.subject, cursus_ids, _texte_item(item))
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
            # Id du thème et code matière : liens "Exercices corrigés sur ce thème" (page
            # /themes-frequents/<id>/exercices, qui attend le code matière) depuis le quiz.
            "theme_id": item.theme_id,
            "subject_code": item.subject.code,
            "subject_label": item.subject.label,
        }
        if answer:
            payload["corrige_markdown"] = _competence_item_corrige(item, [quiz_question.session.cursus_id])
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
        # _question_payload. Repris tel quel dans _resultat_payload (même origine
        # Parcours) pour que "Quitter le quiz" en cours de session et "Retour au
        # parcours" en fin de session pointent vers la même page.
        "subject": session.subject_id,
        "cursus_display": _cursus_display(session.cursus),
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "total_questions": quiz_questions.count(),
        "questions": [_question_payload(qq) for qq in quiz_questions],
    }


def _items_rates(session):
    from .services import items_rates

    return items_rates(session)


def _resultat_payload(session, request):
    quiz_questions = (
        session.quiz_questions
        .select_related("answer", "question", "competence_item__theme", "competence_item__subject")
        .prefetch_related("question__themes", "competence_item__cursus")
    )

    repondues = 0
    reussies = 0
    par_theme = {}
    # Meilleure série de bonnes réponses d'affilée DANS ce quiz (jamais une série de
    # jours, voir seances_terminees_cette_semaine).
    serie = meilleure_serie = 0

    for quiz_question in quiz_questions:
        answer = _get_answer(quiz_question)
        if not answer:
            continue
        repondues += 1
        correcte = answer.est_correcte
        if correcte:
            reussies += 1
            serie += 1
            meilleure_serie = max(meilleure_serie, serie)
        else:
            serie = 0
        # CompetenceItem : un seul theme (FK) ; catalog.Question historique : plusieurs
        # (M2M) - voir QuizQuestion.contenu et CompetenceItem.theme.
        themes = (
            [quiz_question.competence_item.theme]
            if quiz_question.competence_item_id
            else list(quiz_question.question.themes.all())
        )
        for theme in themes:
            stats = par_theme.setdefault(
                theme.name, {"total": 0, "reussies": 0, "theme": None, "competence_item": None, "theme_id": theme.pk},
            )
            stats["total"] += 1
            if correcte:
                stats["reussies"] += 1
            # Retenus pour la suggestion de cours ci-dessous - uniquement depuis un
            # CompetenceItem (thème et matière non ambigus, même restriction que
            # _poids_par_theme/enregistrer_resultat_pour_revision : un catalog.Question
            # historique porte plusieurs thèmes sans qu'on sache lequel a fait échouer,
            # et generer_session n'en tire de toute façon plus depuis la bascule).
            if quiz_question.competence_item_id:
                stats["theme"] = theme
                stats["competence_item"] = quiz_question.competence_item

    par_theme_payload = []
    for nom, s in sorted(par_theme.items()):
        entree = {
            "theme": nom,
            "theme_id": s["theme_id"],
            # Code matière connu seulement via un CompetenceItem (voir plus haut) : sert
            # au lien vers les exercices corrigés du thème, absent sinon.
            "subject_code": s["competence_item"].subject.code if s["competence_item"] else None,
            "total": s["total"],
            "reussies": s["reussies"],
            "cours": None,
        }
        # Cours suggéré seulement sous le seuil de maîtrise habituel (même barre que
        # partout ailleurs dans l'app, voir quiz.services.SEUIL_MAITRISE) - jamais sous
        # un thème déjà réussi, qui n'a besoin de rien. La séance de calibrage day-one
        # (5 questions, un seul thème parfois raté une fois) profite ainsi de la même
        # suggestion qu'une séance normale, sans règle spéciale.
        if s["theme"] is not None and 100 * s["reussies"] / s["total"] < SEUIL_MAITRISE:
            item = s["competence_item"]
            cours = _cours_pour_theme(s["theme"], item.subject, [session.cursus_id], _texte_item(item))
            if cours:
                entree["cours"] = CoursSummarySerializer(cours, context={"request": request}).data
        par_theme_payload.append(entree)

    return {
        "id": session.id,
        "cursus": session.cursus_id,
        "subject": session.subject_id,
        "total_questions": quiz_questions.count(),
        "questions_repondues": repondues,
        "mode": session.mode,
        "nb_ratees": len(_items_rates(session)),
        "score": reussies,
        "meilleure_serie": meilleure_serie,
        "seances_cette_semaine": seances_terminees_cette_semaine(session.profil, session.cursus),
        "par_theme": par_theme_payload,
        # Ce quiz était l'étape finale d'une séance du jour, et l'a clôturée : la page
        # de résultat le dit et ramène à « Aujourd'hui ». Faux pour un quiz lancé seul.
        "seance_validee": session.seances.filter(statut=StatutSeance.TERMINEE).exists(),
    }


@api_view(["POST"])
def start_session(request):
    """Crée une QuizSession pour l'utilisateur connecté - gating : réservé aux cursus
    pour lesquels un abonnement actif existe, SAUF si le périmètre demandé (theme/
    savoir/subject) est entièrement composé d'items est_vitrine=True (voir
    CompetenceItem.est_vitrine) - même principe que access.services.has_access pour
    Lesson.est_vitrine, mais vérifié ici sur le périmètre exact demandé plutôt que sur
    un objet unique."""
    cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=request.data.get("cursus"))

    if not cursus.country.actif:
        # Un pays désactivé doit être invisible partout, y compris pour démarrer un
        # quiz sur l'un de ses cursus - 404 plutôt que 403 : il n'existe pas, on ne
        # refuse pas juste l'accès (voir catalog.models.VisibleQuerySet).
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

    mode = request.data.get("mode") or ModeQuiz.PRATIQUE
    if mode not in ModeQuiz.values:
        return Response({"error": f"mode invalide : {mode!r}. Attendu {ModeQuiz.values}."}, status=400)

    subject = get_object_or_404(Subject, pk=request.data["subject"]) if request.data.get("subject") else None
    theme = get_object_or_404(Tag, pk=request.data["theme"]) if request.data.get("theme") else None
    savoir = get_object_or_404(Savoir, pk=request.data["savoir"]) if request.data.get("savoir") else None

    if not _has_active_subscription(request.user, cursus) and not perimetre_est_vitrine(cursus, subject=subject, theme=theme, savoir=savoir):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    try:
        n = int(request.data.get("n") or 10)
    except (TypeError, ValueError):
        n = 10

    profil = profil_actif(request)
    try:
        session = generer_session(profil, cursus, mode, subject=subject, theme=theme, savoir=savoir, n=n)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=404)

    # `seance` n'est qu'un drapeau "je viens du plan du jour" posé par le lien de
    # l'étape quiz : sa valeur n'est pas de confiance (une URL se bricole), donc on ne
    # s'en sert jamais pour DÉSIGNER une séance - rattacher_quiz_a_la_seance ne touche
    # que la séance du jour de ce profil, sur ce cursus.
    if request.data.get("seance"):
        rattacher_quiz_a_la_seance(profil, session)

    return Response(_session_payload(session), status=201)


@api_view(["GET"])
def session_detail(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, profil=profil_actif(request))
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
        pk=quiz_question_id, session_id=session_id, session__profil=profil_actif(request),
    )
    contenu = quiz_question.contenu
    corrige_markdown = (
        _competence_item_corrige(contenu, [quiz_question.session.cursus_id]) if quiz_question.competence_item_id else contenu.corrige_markdown
    )
    return Response({"corrige_markdown": corrige_markdown, "reponse_correcte": contenu.reponse_correcte})


@api_view(["POST"])
def answer_question(request, session_id, quiz_question_id):
    profil = profil_actif(request)
    quiz_question = get_object_or_404(
        QuizQuestion.objects.select_related(
            "session", "question__exercise__lesson__subject", "competence_item",
        ),
        pk=quiz_question_id, session_id=session_id, session__profil=profil,
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
            profil, quiz_question.session.cursus, item.subject, item.theme, answer.est_correcte,
        )

    return Response(_question_payload(quiz_question))


@api_view(["POST"])
def complete_session(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, profil=profil_actif(request))
    if not session.completed_at:
        session.completed_at = timezone.now()
        session.save(update_fields=["completed_at"])
        # Le quiz est toujours la dernière étape d'une séance : le boucler, c'est
        # avoir fait la séance. Sous le `if` : une session rouverte plus tard ne doit
        # pas reclôturer quoi que ce soit.
        _tracer_seance_terminee(cloturer_seance_si_quiz_termine(session))
    return Response(_resultat_payload(session, request))


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
    session = get_object_or_404(QuizSession, pk=session_id, profil=profil_actif(request))
    if not _has_active_subscription(request.user, session.cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    if request.method == "POST" and session.fiche_pdf_statut not in (StatutFichePdf.EN_COURS, StatutFichePdf.PRETE):
        session.fiche_pdf_statut = StatutFichePdf.EN_COURS
        session.save(update_fields=["fiche_pdf_statut"])
        queue_quiz_fiche_pdf_generation(session.id)

    return Response(_fiche_pdf_payload(session))


@api_view(["GET"])
def download_quiz_sujet_pdf(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, profil=profil_actif(request))
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
    session = get_object_or_404(QuizSession, pk=session_id, profil=profil_actif(request))
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
    for schedule in revisions_dues(profil_actif(request)):
        cours_qs = (
            Cours.objects.visibles()
            .filter(subject=schedule.subject, tags=schedule.theme)
            .filter(q_cours_du_cursus([schedule.cursus_id]))
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

    Aucune vérification d'abonnement ici (comme le reste de cette vue avant elle) :
    affichée à un utilisateur connecté sans abonnement actif sur ce cursus pour montrer
    la structure réelle avant le mur payant (voir SubjectWithQuizCountSerializer et
    project_gating_non_abonne_quiz_parcours) - seul le lancement d'une session
    (start_session) reste gated par _has_active_subscription (sauf périmètre vitrine,
    voir perimetre_est_vitrine).
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    subjects = list(
        Subject.objects.filter(competence_items__statut=StatutContenu.VALIDE, competence_items__cursus=cursus)
        .annotate(
            nb_questions=Count(
                "competence_items",
                filter=Q(competence_items__statut=StatutContenu.VALIDE, competence_items__cursus=cursus),
                distinct=True,
            ),
        )
        .select_related("country")
        .distinct()
        .order_by("label"),
    )

    # Thème vitrine de chaque matière (voir CompetenceItem.est_vitrine), pour que le
    # frontend puisse proposer un essai gratuit en entier plutôt qu'un simple "abonne-
    # toi" - un attribut Python posé après coup (pas une annotation SQL, la relation
    # theme_id n'a pas d'agrégat naturel), premier thème trouvé si plusieurs par
    # matière (la curation vise un thème par cursus, jamais davantage en pratique).
    vitrine_par_matiere = {}
    for subject_id, theme_id in (
        CompetenceItem.objects.filter(
            cursus=cursus, est_vitrine=True, subject_id__in=[s.id for s in subjects],
        ).values_list("subject_id", "theme_id").distinct()
    ):
        vitrine_par_matiere.setdefault(subject_id, theme_id)
    for s in subjects:
        s.vitrine_theme_id = vitrine_par_matiere.get(s.id)

    return Response(SubjectWithQuizCountSerializer(subjects, many=True, context={"request": request}).data)


@api_view(["GET"])
def maitrise(request):
    """
    Vue d'ensemble de la maîtrise par thème (voir quiz.services.maitrise_par_theme) -
    alimente le tableau "Ma maîtrise" de la page Compte. `cursus` optionnel : sans lui,
    l'historique complet de l'utilisateur tous cursus confondus.
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"]) if request.GET.get("cursus") else None
    return Response(maitrise_par_theme(profil_actif(request), cursus=cursus))


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
    return Response(construire_parcours(profil_actif(request), cursus, subject))


@api_view(["GET"])
def parcours_resume(request):
    """
    Tableau de bord "toutes tes matières" (voir quiz.services.resume_parcours) : une
    ligne par matière ayant un programme officiel pour ce cursus, réduite à un
    histogramme de statuts par savoir. Point d'entrée au-dessus de `parcours`
    (détail séquencé d'une seule matière).
    """
    cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    return Response(resume_parcours(profil_actif(request), cursus))


def _etape_verrouillee(etape):
    """
    Ce qui reste d'une étape quand l'abonnement n'est pas actif : son type et sa durée,
    jamais ce qui identifie le contenu précis (slug, exercice, année de l'épreuve
    source) - le frontend affiche donc "Ton parcours" au complet, chaque étape à sa
    place, mais aucune n'ouvre quoi que ce soit. Le libellé d'un exercice porte
    d'ordinaire l'épreuve source ("Exercice 2 - BAC C Maths 2022") ; verrouillé, il ne
    doit pas en dire plus que "Un exercice tombé à l'examen" ne le fait déjà pour le
    thème entier.
    """
    type_ = etape.get("type")
    libelle = "Un exercice tombé à l'examen" if type_ == "exercice" else etape.get("libelle")
    return {"type": type_, "libelle": libelle, "duree_min": etape.get("duree_min")}


def _serialiser_seance(seance, verrouillee):
    """
    Une séance verrouillée expose TOUT sauf de quoi ouvrir le contenu : la matière, le
    thème, sa fréquence à l'examen, la durée, le nombre d'étapes, et jusqu'à la
    structure même du parcours (voir _etape_verrouillee) - un exercice y garde son
    type et sa durée, jamais l'épreuve source qui le identifierait. Le paywall tombe
    sur le bouton, jamais sur l'information - c'est le seul endroit de l'app où la
    valeur se démontre au lieu de s'affirmer, et cacher le thème reviendrait à
    demander à un visiteur de payer pour savoir ce qu'il achète.
    """
    return {
        "id": seance.id,
        "origine": seance.origine,
        "origine_display": seance.get_origine_display(),
        "subject": SubjectSerializer(seance.subject).data if seance.subject else None,
        "theme": {"id": seance.theme_id, "name": seance.theme.name} if seance.theme else None,
        "savoir": {"id": seance.savoir_id, "intitule": seance.savoir.intitule} if seance.savoir else None,
        "duree_estimee_min": seance.duree_estimee_min,
        # Le temps que l'élève s'est donné, et les choix possibles - c'est un plafond,
        # la durée réelle ci-dessus peut être inférieure.
        "budget_minutes": seance.budget_minutes,
        "budgets_possibles": list(BUDGETS_SEANCE_MINUTES),
        "nb_etapes": len(seance.etapes),
        "etapes": [_etape_verrouillee(etape) for etape in seance.etapes] if verrouillee else [
            {**etape, "cle": cle_etape(etape), "ouverte": etape_ouverte(seance, etape)}
            for etape in seance.etapes
        ],
        "frequence": _frequence_du_theme(seance),
        # Pourquoi cette séance-là : des faits déjà en base, jamais une reformulation
        # de l'intention (voir raisons_de_la_seance). C'est ce qui distingue une
        # recommandation crédible d'une recommandation à croire sur parole.
        "raisons": raisons_de_la_seance(seance),
        # Échéance de révision de ce thème, quand il y en a une - le chiffre existait
        # déjà (paliers Leitner) et n'était jamais montré.
        "prochaine_revision": prochaine_revision(seance),
        # Profondeur disponible derrière l'étape d'entraînement : la séance n'en propose
        # qu'un ou deux par budget de temps, pas par manque de contenu.
        "exercices_total": exercices_du_theme(seance.cursus, seance.subject, seance.theme),
        "statut": seance.statut,
        # "4/5" en fin de séance - None quand il n'y a rien à noter (pas d'étape quiz,
        # ou quiz pas terminé), jamais un 0/0 qui se lirait comme un échec.
        "score": score_de_la_seance(seance),
        "verrouillee": verrouillee,
    }


def _frequence_du_theme(seance):
    """
    "Tombé dans 8 des 10 dernières épreuves" - le seul chiffre que personne d'autre ne
    peut afficher, et la meilleure raison de faire CETTE séance plutôt qu'une autre.

    Compté sur les épreuves OFFICIELLES du (cursus, matière) uniquement : un examen
    blanc reste utile à pratiquer mais ne dit rien de ce qui tombe vraiment, et c'est
    bien une promesse sur le vrai examen qu'on fait ici. Renvoie None dès qu'un des
    éléments manque plutôt qu'un 0 sur 0, qui se lirait comme "ne tombe jamais".
    """
    if seance.theme_id is None or seance.subject_id is None:
        return None
    lessons = Lesson.objects.filter(
        statut=StatutContenu.VALIDE, subject_id=seance.subject_id,
        cursus=seance.cursus_id, origine=Origine.OFFICIEL,
    ).distinct()
    total = lessons.count()
    if not total:
        return None
    concernees = lessons.filter(exercises__questions__themes__id=seance.theme_id).distinct().order_by("-year")
    occurrences = concernees.count()
    if not occurrences:
        return None
    return {
        "occurrences": occurrences,
        "epreuves_total": total,
        # Les années réellement concernées, les plus récentes d'abord. "Tombé dans 11
        # des 21 dernières épreuves" est une affirmation que l'élève doit pouvoir
        # vérifier : sans la liste, c'est un chiffre à croire sur parole. Plafonnée -
        # la promesse est de rendre le chiffre concret, pas de dérouler un historique.
        "annees": [annee for annee in concernees.values_list("year", flat=True)[:ANNEES_FREQUENCE_MAX] if annee],
    }


@api_view(["GET"])
def plan_du_jour_view(request):
    """
    Une seule requête pour tout l'écran d'accueil d'un élève : son compte à rebours et
    sa séance du jour, avec un `etat` que le frontend affiche tel quel sans
    réimplémenter la moindre règle métier.

    `etat` :
      - `cursus_inconnu` : rien n'est déclaré, il n'y a pas de plan à faire ;
      - `examen_passe` : la date est dépassée et la session suivante pas encore saisie ;
      - `rien_a_proposer` : cursus sans contenu exploitable (filet, jamais nominal) ;
      - `deja_fait_aujourdhui` : la séance du jour est terminée ;
      - `plan_pret` : il y a quelque chose à faire maintenant.
    """
    user = request.user
    cursus = user.cursus_prepare
    if cursus is None or not cursus.country.actif:
        return Response({"etat": "cursus_inconnu", "cursus": None, "compte_a_rebours": None, "seance": None})

    compte = ExamSession.compte_a_rebours_pour(cursus)
    if compte is not None and compte["jours_restants"] < 0:
        # La session est passée et la suivante n'est pas saisie : proposer une séance
        # "jusqu'à l'examen" vers une date révolue n'aurait aucun sens.
        return Response({
            "etat": "examen_passe",
            "cursus": CursusSerializer(cursus).data,
            "compte_a_rebours": compte,
            "seance": None,
        })

    profil = profil_actif(request)
    return Response(_charge_utile_plan(profil, cursus, plan_du_jour(profil, cursus), compte))


def _serialiser_objectif(objectif):
    if objectif is None:
        return None
    return {
        "subject": objectif.subject_id,
        "label": objectif.subject.label,
        "jusqu_au": objectif.jusqu_au.isoformat(),
    }


def _charge_utile_plan(profil, cursus, seance, compte):
    """
    Réponse commune à plan_du_jour_view et continuer_view : les deux rendent le même
    écran, et le frontend remplace simplement sa donnée par celle qu'on lui renvoie -
    deux charges utiles distinctes finiraient par diverger sur un champ.
    """
    base = {
        "cursus": CursusSerializer(cursus).data,
        "compte_a_rebours": compte,
        "seances_cette_semaine": seances_terminees_cette_semaine(profil, cursus),
        "serie": serie_de_jours(profil),
        "objectif_matiere": _serialiser_objectif(objectif_matiere_actif(profil, cursus)),
        "matieres_objectif": [{"id": m.id, "label": m.label} for m in matieres_pour_objectif(cursus)],
    }
    if seance is None:
        return {**base, "etat": "rien_a_proposer", "seance": None}

    verrouillee = not _has_active_subscription(profil.compte, cursus)
    etat = "deja_fait_aujourdhui" if seance.statut == StatutSeance.TERMINEE else "plan_pret"
    return {**base, "etat": etat, "seance": _serialiser_seance(seance, verrouillee)}


@api_view(["GET"])
def accueil_view(request):
    """
    L'accueil d'un abonné en une seule requête - voir quiz.accueil pour le pourquoi.

    Enregistre le passage (VisiteAccueil) : un GET avec un effet de bord, assumé - la
    visite EST l'évènement qu'on mesure, et "depuis la dernière fois" n'a de sens que
    si quelqu'un note la dernière fois. Au retour après une longue absence (voir
    ABSENCE_RETOUR_JOURS), la séance du jour est raccourcie une fois, au début de la
    visite seulement : jamais par-dessus une durée que l'élève aurait choisie ensuite.
    """
    user = request.user
    cursus = user.cursus_prepare
    if cursus is None or not cursus.country.actif:
        return Response({
            "plan": {"etat": "cursus_inconnu", "cursus": None, "compte_a_rebours": None, "seance": None},
            "phase": "normal", "absence_jours": 0, "premiers_pas": True, "nouvelle_visite": False,
            "phrase_coach": "", "depuis": None, "trajectoire": None, "resume": [], "preparation": None,
            "revisions": [], "lecture": None, "simulation_suggeree": None, "bilan_semaine": None,
        })

    profil = profil_actif(request)
    compte = ExamSession.compte_a_rebours_pour(cursus)
    visite, nouvelle = accueil.enregistrer_visite(profil)
    absence = accueil.absence_jours(visite)
    phase = accueil.phase_examen(compte)

    if phase == "apres":
        plan = {
            "etat": "examen_passe",
            "cursus": CursusSerializer(cursus).data,
            "compte_a_rebours": compte,
            "seance": None,
        }
    else:
        seance = plan_du_jour(profil, cursus)
        if (
            nouvelle and absence >= accueil.ABSENCE_RETOUR_JOURS and seance is not None
            and seance.statut == StatutSeance.PROPOSEE and not seance.etapes_ouvertes
        ):
            seance = ajuster_duree_seance(profil, cursus, accueil.BUDGET_RETOUR_MINUTES) or seance
        plan = _charge_utile_plan(profil, cursus, seance, compte)

    resume = resume_parcours(profil, cursus)
    debutant = accueil.premiers_pas(profil, cursus)
    today = timezone.localdate()
    revisions = [
        {
            "id": schedule.id,
            "theme": schedule.theme.name,
            "theme_id": schedule.theme_id,
            "subject_id": schedule.subject_id,
            "subject_label": schedule.subject.label,
            "cursus": schedule.cursus_id,
            "jours_retard": (today - schedule.due_at).days,
        }
        for schedule in revisions_dues(profil, cursus)[: accueil.REVISIONS_ACCUEIL_MAX]
    ]
    from .bilan import bilan_de_periode

    return Response({
        "plan": plan,
        "phase": phase,
        "absence_jours": absence,
        "premiers_pas": debutant,
        "nouvelle_visite": nouvelle,
        "phrase_coach": accueil.phrase_coach(plan, phase, absence, premiers_pas_eleve=debutant),
        "depuis": None if debutant else accueil.delta_depuis(profil, cursus, visite),
        "trajectoire": None if debutant else accueil.trajectoire(profil, cursus, resume, compte),
        "resume": resume,
        "preparation": accueil.preparation(resume),
        "revisions": revisions,
        "lecture": accueil.lecture_a_reprendre(profil, cursus),
        "simulation_suggeree": accueil.simulation_suggeree(profil, cursus, phase),
        "bilan_semaine": bilan_de_periode(profil, cursus, jours=7),
    })


@api_view(["POST"])
def terminer_seance_view(request):
    """
    Marque la séance du jour comme faite. Réservé à l'abonné actif, comme le contenu
    qu'elle enchaîne : sans cela un visiteur verrouillé pourrait "terminer" une séance
    qu'il n'a pas pu ouvrir, et fausser le seul chiffre qui dira si ce plan marche.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    profil = profil_actif(request)
    seance = seance_du_jour(profil, cursus)
    if seance is None:
        return Response({"error": "Aucune séance aujourd'hui."}, status=404)

    # Uniquement si elle ne l'était pas déjà : reconfirmer une séance close (double
    # clic, onglet resté ouvert) ne doit pas la compter une seconde fois.
    if seance.statut != StatutSeance.TERMINEE:
        terminer_seance(seance)
        _tracer_seance_terminee(seance)
    return Response({
        "statut": seance.statut,
        "seances_cette_semaine": seances_terminees_cette_semaine(profil, cursus),
        "serie": serie_de_jours(profil),
    })


@api_view(["POST"])
def continuer_view(request):
    """
    "J'ai fini ma séance et je veux continuer" : propose une séance de PLUS plutôt que
    de renvoyer vers un catalogue (voir quiz.services.seance_supplementaire).

    POST et non GET : l'appel CRÉE une séance. C'est aussi pourquoi il faut un clic -
    une séance supplémentaire fabriquée à la simple lecture de la page détruirait
    l'état "séance faite", qui est la récompense de la journée.

    Réservé à l'abonné actif, comme le contenu qu'elle enchaîne.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    profil = profil_actif(request)
    seance = seance_supplementaire(profil, cursus)
    compte = ExamSession.compte_a_rebours_pour(cursus)
    return Response(_charge_utile_plan(profil, cursus, seance, compte))


@api_view(["POST", "DELETE"])
def objectif_matiere_view(request):
    """
    "Cette semaine, je me concentre sur <matière>" (POST {subject}) ou retour à la
    sélection automatique (DELETE) - voir quiz.models.ObjectifMatiere pour pourquoi le
    choix est limité dans le temps.

    Renvoie la charge utile habituelle du plan, que le frontend substitue à la sienne.
    Réservé à l'abonné actif, comme le plan lui-même.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    profil = profil_actif(request)
    if request.method == "DELETE":
        retirer_objectif_matiere(profil, cursus)
    else:
        subject = get_object_or_404(Subject, pk=request.data.get("subject"))
        if definir_objectif_matiere(profil, cursus, subject) is None:
            return Response({"error": "Cette matière n'a pas encore de quiz pour ton examen."}, status=400)

    compte = ExamSession.compte_a_rebours_pour(cursus)
    return Response(_charge_utile_plan(profil, cursus, plan_du_jour(profil, cursus), compte))


@api_view(["POST"])
def autre_chose_view(request):
    """
    "Ce n'est pas ce que je veux réviser" : remplace la séance du jour par une autre
    (voir quiz.services.remplacer_seance), au lieu de renvoyer vers le catalogue.

    Renvoie la charge utile habituelle du plan - avec l'état "rien_a_proposer" quand
    il n'y a plus d'alternative ou que l'élève a atteint REFUS_MAX_PAR_JOUR, cas où le
    frontend lui rend la main sur le catalogue.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    profil = profil_actif(request)
    seance = remplacer_seance(profil, cursus)
    compte = ExamSession.compte_a_rebours_pour(cursus)
    return Response(_charge_utile_plan(profil, cursus, seance, compte))


@api_view(["POST"])
def etape_ouverte_view(request):
    """
    L'élève vient d'ouvrir une étape (cours, exercice) de sa séance : on le retient
    pour cocher l'étape et proposer « Reprendre la séance » à son retour.

    Sans effet sur le statut de la séance - une ouverture ne prouve pas qu'on a lu.
    Même garde que le reste du plan : cursus déclaré, abonnement actif.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    seance = marquer_etape_ouverte(profil_actif(request), cursus, str(request.data.get("cle") or ""))
    if seance is None:
        return Response({"error": "Étape inconnue pour la séance du jour."}, status=404)
    return Response({"etapes_ouvertes": seance.etapes_ouvertes})


@api_view(["POST"])
def duree_seance_view(request):
    """
    "Combien de temps as-tu ?" - recompose la séance du jour pour la durée demandée
    (voir quiz.services.ajuster_duree_seance), sans changer de thème.

    POST : l'appel réécrit la séance. Réservé à l'abonné actif, comme le contenu
    qu'elle enchaîne.
    """
    cursus = request.user.cursus_prepare
    if cursus is None:
        return Response({"error": "Aucun cursus déclaré."}, status=400)
    if not _has_active_subscription(request.user, cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)

    try:
        minutes = int(request.data.get("minutes"))
    except (TypeError, ValueError):
        return Response({"error": "minutes doit être un entier."}, status=400)

    profil = profil_actif(request)
    seance = ajuster_duree_seance(profil, cursus, minutes)
    compte = ExamSession.compte_a_rebours_pour(cursus)
    return Response(_charge_utile_plan(profil, cursus, seance, compte))


@api_view(["GET"])
def bilan_periode_view(request):
    """
    Bilan des 30 derniers jours de l'abonnement (voir quiz.bilan.bilan_de_periode).

    `?cursus=` optionnel : par défaut le cursus préparé. Lecture de SA propre activité,
    donc aussi disponible après expiration - c'est justement là qu'il sert à décider de
    se réabonner. 404 quand l'élève n'a jamais été abonné à ce cursus.
    """
    from .bilan import bilan_de_periode

    if request.GET.get("cursus"):
        cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    else:
        cursus = request.user.cursus_prepare
        if cursus is None:
            return Response({"error": "Aucun cursus déclaré."}, status=400)
    # Deux fenêtres seulement : la semaine (accueil) et le mois (renouvellement). Toute
    # autre valeur retombe sur le mois plutôt que d'ouvrir un calcul arbitrairement long.
    jours = 7 if request.GET.get("jours") == "7" else 30
    bilan = bilan_de_periode(profil_actif(request), cursus, jours=jours)
    if bilan is None:
        return Response({"error": "Aucun abonnement pour ce cursus."}, status=404)
    return Response(bilan)


@api_view(["GET"])
def priorites_view(request):
    """
    Où concentrer son temps pour cet examen (voir quiz.priorites.priorites_examen) :
    restitution du diagnostic d'accueil, mais valable à tout moment. `?cursus=` optionnel,
    par défaut le cursus préparé. Réservé à qui a (ou a eu) un abonnement à ce cursus.
    """
    from .priorites import priorites_examen

    if request.GET.get("cursus"):
        cursus = get_object_or_404(Cursus, pk=request.GET["cursus"])
    else:
        cursus = request.user.cursus_prepare
        if cursus is None:
            return Response({"error": "Aucun cursus déclaré."}, status=400)
    profil = profil_actif(request)
    if not Subscription.objects.filter(profil=profil, cursus=cursus).exists():
        return Response({"error": "Aucun abonnement pour ce cursus."}, status=404)
    return Response(priorites_examen(profil, cursus))


@api_view(["POST"])
def refaire_ratees_view(request, session_id):
    """
    Nouvelle session limitée aux questions ratées de celle-ci (voir
    quiz.services.session_des_ratees) - le bouton "Refaire celles que j'ai ratées" de la
    page de résultat. Même règle d'accès que start_session : abonnement actif sur le
    cursus, revérifié à chaque appel.
    """
    from .services import session_des_ratees

    profil = profil_actif(request)
    session = get_object_or_404(QuizSession.objects.select_related("cursus"), pk=session_id, profil=profil)
    if not _has_active_subscription(request.user, session.cursus):
        return Response({"error": "Abonnement requis pour ce cursus."}, status=403)
    try:
        refaite = session_des_ratees(profil, session)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response(_session_payload(refaite), status=201)
