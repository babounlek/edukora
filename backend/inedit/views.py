"""
Endpoints DRF de consommation élève - calqués sur quiz.views (start_session/
session_detail/reveal_corrige/answer_question/complete_session), mêmes garanties :
corrige_markdown/reponse_correcte jamais exposés avant réponse (sauf reveal_corrige,
appelé explicitement par l'élève pour s'auto-évaluer sur une question ouverte - voir sa
docstring), sous-endpoints gatés par ownership (tentative.user == request.user)
seulement, jamais une re-vérification d'abonnement à chaque question (même compromis
que quiz, voir quiz.views - accepté une fois, pas la peine de le retrancher ici).
"""

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from access.services import has_access_inedite
from catalog.inedit_bridge import epreuve_inedite_catalogue_payload
from catalog.models import Cursus, StatutContenu, TypeReponse
from catalog.rendering import annotate_cours_links
from catalog.serializers import CursusSerializer
from quiz.models import ResultatDeclare
from quiz.services import enregistrer_resultat_pour_revision
from subscriptions.models import InscriptionInedite

from .models import EpreuveInedite, QuestionInedite, TentativeInedite, TentativeReponse


def _corrige_markdown_with_cours_links(question, exercice):
    """Injecte les marqueurs [COURS_LINK:<slug>] dans le corrigé d'une question, pour
    que le frontend affiche "Voir le cours complet" sous le rappel de méthode
    correspondant (voir catalog.rendering.annotate_cours_links) - jusqu'ici jamais
    branché côté inédit, alors que RappelDeMethodeInedite.cours est peuplé exactement
    comme son homologue classique (voir inedit.ingestion.ingest_cours_inedite).
    append_unmatched=False : RappelDeMethodeInedite est rattaché à l'EXERCICE (voir sa
    docstring, plusieurs questions par exercice), jamais à la question elle-même - un
    rappel qui ne matche aucun bloc dans CE corrigé appartient presque sûrement à une
    autre question du même exercice, jamais à injecter ici (contrairement à catalog, où
    le corrigé annoté couvre déjà tout l'exercice - voir annotate_cours_links)."""
    return annotate_cours_links(question.corrige_markdown, exercice.rappels_de_methode.all(), append_unmatched=False)


def _question_payload(question, reponse, *, correction_disponible, exercice=None):
    """corrige_markdown/reponse_correcte/est_correcte gatés au niveau de la tentative
    (voir _correction_disponible), pas au niveau de la question - une réponse déjà
    enregistrée reste visible pour l'élève (ce qu'il a coché), mais sans trahir si
    c'est juste tant que la correction n'est pas disponible pour cette tentative."""
    payload = {
        "id": question.id,
        "numero": question.numero,
        "ordre": question.ordre,
        # Voir QuestionInedite.groupe_local - jamais gaté par correction_disponible,
        # contrairement à corrige_markdown/reponse_correcte plus bas : c'est un repère
        # structurel de l'énoncé, pas une information qui trahirait la correction.
        "groupe_local": question.groupe_local,
        "enonce_markdown": question.enonce_markdown,
        "type_reponse": question.type_reponse,
        "choix": question.choix,
    }
    if reponse:
        payload["reponse"] = {
            "reponse_choisie": reponse.reponse_choisie,
            "resultat_declare": reponse.resultat_declare,
        }
        if correction_disponible:
            payload["reponse"]["est_correcte"] = reponse.est_correcte
    if correction_disponible:
        payload["corrige_markdown"] = _corrige_markdown_with_cours_links(question, exercice or question.exercice)
        payload["reponse_correcte"] = question.reponse_correcte
    return payload


def _cursus_display(cursus_iterable):
    return ", ".join(
        f"{c.display_examen()} - Série {c.series.code}" if c.series else c.display_examen()
        for c in cursus_iterable
    )


def _correction_disponible(tentative):
    """Le corrigé est disponible dès que la tentative est soumise, ou dès lors que le
    mode examen n'a jamais été engagé (même confiance que le lecteur classique, voir
    catalog.views.EpreuveReaderPage côté frontend - aucune pression temporelle à
    protéger). False seulement pendant une fenêtre mode-examen active et non encore
    soumise : c'est la seule vraie frontière anti-triche de ce module."""
    return tentative.submitted_at is not None or tentative.exam_mode_started_at is None


def _deadline(tentative):
    if not tentative.exam_mode_started_at:
        return None
    duree = tentative.epreuve.blueprint.duree_minutes
    if not duree:
        return None
    return tentative.exam_mode_started_at + timezone.timedelta(minutes=duree)


def _complete(tentative):
    """Logique de complétion partagée entre l'endpoint explicite complete_tentative et
    l'auto-verrouillage à expiration (_auto_complete_if_expired) - une seule voie de
    calcul de score, idempotente (submitted_at n'est jamais réécrit une fois posé).
    submitted_at DOIT être affecté avant de construire le payload de résultat : sinon
    temps_total_secondes (qui lit tentative.submitted_at) resterait null dans la toute
    première réponse qui vient de compléter la tentative."""
    if not tentative.submitted_at:
        tentative.submitted_at = timezone.now()
        payload = _tentative_resultat_payload(tentative)
        tentative.score_obtenu = payload["score"]
        tentative.save(update_fields=["submitted_at", "score_obtenu"])
        return payload
    return _tentative_resultat_payload(tentative)


def _auto_complete_if_expired(tentative):
    """Transition paresseuse : appelée en tête de tout endpoint qui touche une
    tentative en mode examen. Jamais de cron - la prochaine requête qui touche la
    tentative (GET au retour d'onglet, ou answer_question) fait la transition."""
    if tentative.submitted_at is not None:
        return
    deadline = _deadline(tentative)
    if deadline is not None and timezone.now() >= deadline:
        _complete(tentative)


def _tentative_payload(tentative):
    correction_disponible = _correction_disponible(tentative)
    exercices = (
        tentative.epreuve.exercices
        .prefetch_related("questions__themes", "rappels_de_methode__cours")
        .order_by("numero_exercice")
    )
    reponses_by_question = {r.question_id: r for r in tentative.reponses.all()}
    return {
        "id": tentative.id,
        "epreuve": tentative.epreuve_id,
        "epreuve_titre": tentative.epreuve.titre,
        # Code pays (ex. "CM") - permet au frontend de reconstruire une URL de
        # catalogue préfixée pays (voir InediteTentativePage.tsx) sans requête
        # supplémentaire : TentativeInedite n'expose sinon aucun lien vers Country.
        "country": tentative.epreuve.cursus.first().country.code,
        "cursus_display": _cursus_display(tentative.epreuve.cursus.all()),
        # Indicatif seulement (voir InediteTentativePage.tsx) - null si le Blueprint
        # source n'en a jamais renseigné (champ optionnel, voir Blueprint.duree_minutes).
        "duree_minutes": tentative.epreuve.blueprint.duree_minutes,
        # Permet d'ouvrir le sujet en PDF depuis la page de tentative elle-même (énoncé,
        # mode examen, correction) - même bouton que sur la fiche épreuve, voir
        # inedit.views.download_sujet_pdf.
        "sujet_pdf_disponible": bool(tentative.epreuve.sujet_pdf),
        "started_at": tentative.started_at,
        "exam_mode_started_at": tentative.exam_mode_started_at,
        "submitted_at": tentative.submitted_at,
        "score_obtenu": tentative.score_obtenu,
        "correction_disponible": correction_disponible,
        "questions_marquees": list(tentative.questions_marquees.values_list("pk", flat=True)),
        "exercices": [
            {
                "id": exercice.id,
                "numero_exercice": exercice.numero_exercice,
                "points": exercice.points,
                # Pile de repères de groupe (Partie/section/matière) - [] pour la grande
                # majorité des épreuves. Consommé côté frontend pour afficher un en-tête
                # de groupe au-dessus du badge "Exercice N" quand il change (voir
                # InediteTentativePage.tsx) - pas de navigation libre, contrairement au
                # sommaire des épreuves classiques (voir EpreuveSommaire.tsx), pour ne
                # pas laisser l'élève prévisualiser toute l'épreuve pendant l'examen.
                "groupes": exercice.groupes,
                # Support partagé, affiché une fois en tête d'exercice côté frontend (voir
                # ExerciceInedite.enonce_intro_markdown) - jamais recopié dans chaque
                # _question_payload, qui resterait sinon illisible en mode correction.
                "enonce_intro_markdown": exercice.enonce_intro_markdown,
                "questions": [
                    _question_payload(
                        question, reponses_by_question.get(question.pk), correction_disponible=correction_disponible,
                        exercice=exercice,
                    )
                    for question in exercice.questions.all()
                ],
            }
            for exercice in exercices
        ],
    }


def _tentative_resultat_payload(tentative):
    reponses = tentative.reponses.select_related("question").prefetch_related("question__themes")

    repondues = 0
    reussies = 0
    par_theme = {}
    for reponse in reponses:
        repondues += 1
        correcte = reponse.est_correcte
        if correcte:
            reussies += 1
        for theme in reponse.question.themes.all():
            stats = par_theme.setdefault(theme.name, {"total": 0, "reussies": 0})
            stats["total"] += 1
            if correcte:
                stats["reussies"] += 1

    total_questions = QuestionInedite.objects.filter(exercice__epreuve=tentative.epreuve).count()
    score = round(100 * reussies / repondues) if repondues else None

    return {
        "id": tentative.id,
        "epreuve": tentative.epreuve_id,
        # Voir la note équivalente dans _tentative_payload.
        "country": tentative.epreuve.cursus.first().country.code,
        "total_questions": total_questions,
        "questions_repondues": repondues,
        "score": score,
        "temps_total_secondes": (
            int((tentative.submitted_at - tentative.started_at).total_seconds())
            if tentative.submitted_at else None
        ),
        "par_theme": [
            {"theme": nom, "total": s["total"], "reussies": s["reussies"]}
            for nom, s in sorted(par_theme.items())
        ],
    }


@api_view(["GET"])
def list_my_inscriptions_inedites(request):
    """
    Mes inscriptions à l'add-on Épreuves Inédites - même rôle que
    subscriptions.views.MySubscriptionsView pour Subscription, nécessaire au frontend
    pour savoir, par cursus, s'il faut proposer "Commencer" ou une mise en avant Max
    avant même que l'élève ne clique (voir start_tentative pour le point réellement
    gaté). Fonction plate comme le reste de ce module (aucun serializer ailleurs dans
    inedit) - seul le cursus imbriqué réutilise CursusSerializer, déjà la même forme
    attendue côté frontend (type Cursus) que celle exposée par MySubscriptionsView.
    """
    inscriptions = (
        InscriptionInedite.objects.filter(user=request.user)
        .select_related("cursus__series", "cursus__country")
    )
    return Response([
        {
            "id": inscription.id,
            "cursus": CursusSerializer(inscription.cursus).data,
            "expires_at": inscription.expires_at,
            "is_active": inscription.is_active,
        }
        for inscription in inscriptions
    ])


@api_view(["GET"])
def list_epreuves(request):
    """Épreuves publiées (statut=VALIDE) pour un cursus - liste seule, jamais le
    contenu (voir start_tentative pour le point réellement gaté par has_access_inedite)."""
    cursus_id = request.GET.get("cursus")
    if not cursus_id:
        return Response({"error": "cursus est requis."}, status=400)
    cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=cursus_id)

    if not cursus.country.actif:
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

    epreuves = (
        EpreuveInedite.objects.filter(cursus=cursus, statut=StatutContenu.VALIDE)
        .select_related("subject", "blueprint")
        .order_by("-created_at")
    )
    return Response([
        {
            "id": e.id, "titre": e.titre, "subject_label": e.subject.label,
            "duree_minutes": e.blueprint.duree_minutes, "created_at": e.created_at,
        }
        for e in epreuves
    ])


@api_view(["GET"])
@permission_classes([AllowAny])
def epreuve_inedite_detail(request, id):
    """Fiche détail d'une EpreuveInedite - toujours 200, même pour un visiteur anonyme
    (has_access=false) : même patron que catalog.views.LessonDetailView, le gating vit
    dans le champ has_access du payload, jamais dans le statut HTTP. 404 pour
    BROUILLON/REJETE, même garantie que list_epreuves (statut=VALIDE uniquement).
    Réutilise epreuve_inedite_catalogue_payload - même forme que dans le catalogue
    fusionné (voir catalog.views.LessonListView.list), jamais un mapping dupliqué.

    `id` accepte le slug (URL publique) OU l'id numérique (liens partagés avant
    l'introduction d'EpreuveInedite.slug) - même principe que
    catalog.models.VisibleQuerySet.par_slug_ou_id, réimplémenté ici en une ligne plutôt
    que d'y faire dépendre EpreuveInedite (son filtre `.visibles()` ne conviendrait pas :
    voir cursus__country__actif ci-dessous, pas subject__country__actif)."""
    qs = (
        EpreuveInedite.objects.select_related("subject__country", "blueprint")
        .prefetch_related("cursus__series", "cursus__country", "blueprint__competences")
    )
    qs = qs.filter(pk=id) if id.isdigit() else qs.filter(slug=id)
    epreuve = get_object_or_404(qs, statut=StatutContenu.VALIDE)
    return Response(epreuve_inedite_catalogue_payload(epreuve, request, include_apercu=True))


@api_view(["GET"])
def list_my_tentatives_inedites(request):
    """Historique des tentatives de l'utilisateur (AccountPage, "Mes épreuves
    inédites") - toutes confondues, en cours et soumises (voir TentativeInedite.en_cours,
    le frontend distingue les deux via submitted_at)."""
    tentatives = (
        TentativeInedite.objects.filter(user=request.user)
        .select_related("epreuve__subject")
        .prefetch_related("epreuve__cursus__series", "epreuve__cursus__country")
        .order_by("-started_at")
    )
    return Response([
        {
            "id": tentative.id,
            "epreuve": tentative.epreuve_id,
            "epreuve_titre": tentative.epreuve.titre,
            "subject_label": tentative.epreuve.subject.label,
            "cursus_display": _cursus_display(tentative.epreuve.cursus.all()),
            "started_at": tentative.started_at,
            "submitted_at": tentative.submitted_at,
            "score_obtenu": tentative.score_obtenu,
        }
        for tentative in tentatives
    ])


@api_view(["POST"])
def start_tentative(request):
    """
    Crée une TentativeInedite pour l'utilisateur connecté - gating par
    has_access_inedite (add-on Épreuves Inédites sur ce cursus), jamais has_access
    (le corrigé de ce cursus n'est pas assez : décision "corrigé gaté comme le reste",
    audit "Épreuves Inédites"). Plusieurs tentatives autorisées sur une même épreuve,
    comme quiz.QuizSession (pas de contrainte d'unicité sur TentativeInedite).
    """
    epreuve = get_object_or_404(
        EpreuveInedite.objects.prefetch_related("cursus__country"),
        pk=request.data.get("epreuve"), statut=StatutContenu.VALIDE,
    )
    if not epreuve.cursus.first().country.actif:
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)
    if not has_access_inedite(request.user, epreuve):
        return Response({"error": "Add-on Épreuves Inédites requis pour ce cursus."}, status=403)

    tentative = TentativeInedite.objects.create(user=request.user, epreuve=epreuve)
    return Response(_tentative_payload(tentative), status=201)


@api_view(["GET"])
def tentative_detail(request, tentative_id):
    tentative = get_object_or_404(
        TentativeInedite.objects.select_related("epreuve__blueprint"), pk=tentative_id, user=request.user,
    )
    _auto_complete_if_expired(tentative)
    return Response(_tentative_payload(tentative))


@api_view(["GET"])
def reveal_corrige(request, tentative_id, question_id):
    """Voir quiz.views.reveal_corrige - même rôle : révèle le corrigé à la demande,
    sans enregistrer de réponse, pour que l'élève puisse s'auto-évaluer sur une
    question ouverte avant de soumettre resultat_declare via answer_question. Gaté par
    _correction_disponible (contrairement à quiz.views.reveal_corrige, sans mode
    examen) : sans ce gate, un élève pourrait appeler cet endpoint directement pendant
    une fenêtre mode-examen active et lire le corrigé de n'importe quelle question."""
    tentative = get_object_or_404(
        TentativeInedite.objects.select_related("epreuve__blueprint"), pk=tentative_id, user=request.user,
    )
    _auto_complete_if_expired(tentative)
    if not _correction_disponible(tentative):
        return Response({"error": "Le corrigé n'est pas encore disponible pour cette tentative."}, status=403)
    question = get_object_or_404(
        QuestionInedite.objects.select_related("exercice"), pk=question_id, exercice__epreuve_id=tentative.epreuve_id,
    )
    return Response({
        "corrige_markdown": _corrige_markdown_with_cours_links(question, question.exercice),
        "reponse_correcte": question.reponse_correcte,
    })


@api_view(["POST"])
def answer_question(request, tentative_id, question_id):
    tentative = get_object_or_404(
        TentativeInedite.objects.select_related("epreuve__blueprint"), pk=tentative_id, user=request.user,
    )
    _auto_complete_if_expired(tentative)
    if tentative.submitted_at is not None:
        return Response({"error": "Cette tentative est terminée, impossible de modifier une réponse."}, status=409)

    question = get_object_or_404(QuestionInedite, pk=question_id, exercice__epreuve_id=tentative.epreuve_id)

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

    reponse, _created = TentativeReponse.objects.update_or_create(
        tentative=tentative, question=question, defaults=defaults,
    )

    # Alimente quiz.RevisionSchedule - réutilisé tel quel plutôt qu'un second mécanisme
    # de suivi de faiblesse (voir l'audit "Épreuves Inédites") : (user, cursus, theme)
    # est la même clé quelle que soit la source (Quiz ou Épreuves Inédites). Une épreuve
    # commune à plusieurs séries (voir EpreuveInedite.cursus, M2M) crédite la révision sur
    # CHAQUE série couverte, pas seulement la première - la faiblesse détectée concerne
    # l'élève sur ce thème, indépendamment de la série qu'il vise.
    for theme in question.themes.all():
        for cursus in tentative.epreuve.cursus.all():
            enregistrer_resultat_pour_revision(
                tentative.user, cursus, tentative.epreuve.subject, theme, reponse.est_correcte,
            )

    return Response(_question_payload(question, reponse, correction_disponible=_correction_disponible(tentative)))


@api_view(["POST"])
def start_exam_mode(request, tentative_id):
    """Active le mode examen (chronométré) pour cette tentative - idempotent si déjà
    engagé. Rejeté une fois qu'une réponse existe : activer rétroactivement masquerait
    un corrigé déjà potentiellement affiché côté client depuis un chargement en mode
    libre (voir _correction_disponible), ce qui viderait la protection de son sens."""
    tentative = get_object_or_404(
        TentativeInedite.objects.select_related("epreuve__blueprint"), pk=tentative_id, user=request.user,
    )
    if tentative.submitted_at is not None:
        return Response({"error": "Cette tentative est déjà terminée."}, status=409)
    if tentative.exam_mode_started_at is not None:
        return Response(_tentative_payload(tentative))
    if not tentative.epreuve.blueprint.duree_minutes:
        return Response(
            {"error": "Cette épreuve n'a pas de durée définie, le mode examen n'est pas disponible."}, status=400,
        )
    if tentative.reponses.exists():
        return Response(
            {"error": "Le mode examen doit être activé avant de répondre à la première question."}, status=409,
        )

    tentative.exam_mode_started_at = timezone.now()
    tentative.save(update_fields=["exam_mode_started_at"])
    return Response(_tentative_payload(tentative))


@api_view(["POST"])
def toggle_question_marquee(request, tentative_id, question_id):
    """Marquage « à revoir », indépendant d'avoir répondu ou non - aucune implication
    anti-triche, donc autorisé avant comme après soumission de la tentative."""
    tentative = get_object_or_404(TentativeInedite, pk=tentative_id, user=request.user)
    question = get_object_or_404(QuestionInedite, pk=question_id, exercice__epreuve_id=tentative.epreuve_id)
    if tentative.questions_marquees.filter(pk=question.pk).exists():
        tentative.questions_marquees.remove(question)
    else:
        tentative.questions_marquees.add(question)
    return Response({"questions_marquees": list(tentative.questions_marquees.values_list("pk", flat=True))})


@api_view(["POST"])
def complete_tentative(request, tentative_id):
    tentative = get_object_or_404(TentativeInedite, pk=tentative_id, user=request.user)
    return Response(_complete(tentative))


@api_view(["GET"])
def download_sujet_pdf(request, epreuve_id):
    """
    Seul point de sortie du PDF sujet (voir EpreuveInedite.sujet_pdf, stocké sur un
    storage privé, voir inedit.storage.protected_storage) - jamais l'URL du storage
    renvoyée au client, le fichier est lu et streamé ici côté serveur, après la même
    vérification d'accès qu'une tentative (has_access_inedite). Proposé sur la fiche
    épreuve, avant toute tentative. Le corrigé, lui, ne génère jamais de PDF (voir
    inedit.sujet_pdf, docstring de module) : il reste consultable uniquement en ligne,
    question par question, après tentative (voir reveal_corrige ci-dessus).
    """
    epreuve = get_object_or_404(EpreuveInedite, pk=epreuve_id, statut=StatutContenu.VALIDE)
    if not has_access_inedite(request.user, epreuve):
        return Response({"error": "Add-on Épreuves Inédites requis pour ce cursus."}, status=403)
    if not epreuve.sujet_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)

    return FileResponse(
        epreuve.sujet_pdf.open("rb"),
        as_attachment=False,
        filename=f"{slugify(epreuve.titre)}-sujet.pdf",
        content_type="application/pdf",
    )
