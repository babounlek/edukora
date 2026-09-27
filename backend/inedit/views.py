"""
Endpoints DRF de consommation élève - calqués sur quiz.views (start_session/
session_detail/reveal_corrige/answer_question/complete_session), mêmes garanties :
corrige_markdown/reponse_correcte jamais exposés avant réponse (sauf reveal_corrige,
appelé explicitement par l'élève pour s'auto-évaluer sur une question ouverte - voir sa
docstring), sous-endpoints gatés par ownership (tentative.user == request.user)
seulement, jamais une re-vérification d'abonnement à chaque question (même compromis
que quiz, voir quiz.views - accepté une fois, pas la peine de le retrancher ici).
"""

from decimal import Decimal, InvalidOperation

from django.db.models import Max
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

from . import notation, rapport
from .models import CausePerte, EpreuveInedite, QuestionInedite, TentativeInedite, TentativeReponse


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


def _question_payload(question, reponse, *, correction_disponible, exercice=None, points_info=None):
    """corrige_markdown/reponse_correcte/est_correcte gatés au niveau de la tentative
    (voir _correction_disponible), pas au niveau de la question - une réponse déjà
    enregistrée reste visible pour l'élève (ce qu'il a coché), mais sans trahir si
    c'est juste tant que la correction n'est pas disponible pour cette tentative.

    Même règle pour la grille de notation (criteres_notation) et les points obtenus : la
    grille décrit la solution attendue, elle ne sort jamais avant le corrigé."""
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
        # « Traitée » : l'élève a répondu (QCM) ou déclaré avoir traité la question
        # (ouverte) - ce que compte la barre d'avancement pendant l'épreuve.
        "traitee": notation.est_traitee(question, reponse),
    }
    points = None
    if points_info is not None:
        points, estime = points_info
        payload["points"] = notation.en_nombre(points)
        payload["bareme_estime"] = estime
    if reponse:
        payload["reponse"] = {
            "reponse_choisie": reponse.reponse_choisie,
            "resultat_declare": reponse.resultat_declare,
        }
        if correction_disponible:
            payload["reponse"]["est_correcte"] = reponse.est_correcte
            notee = notation.est_notee(question, reponse)
            payload["reponse"]["notee"] = notee
            payload["reponse"]["criteres_valides"] = reponse.criteres_valides
            payload["reponse"]["cause_perte"] = reponse.cause_perte
            if points is not None:
                payload["reponse"]["points_obtenus"] = (
                    notation.en_nombre(notation.points_obtenus(question, reponse, points)) if notee else None
                )
    if correction_disponible:
        payload["corrige_markdown"] = _corrige_markdown_with_cours_links(question, exercice or question.exercice)
        payload["reponse_correcte"] = question.reponse_correcte
        payload["criteres_notation"] = question.criteres_notation
    return payload


def _exercices_pour_notation(epreuve):
    return list(epreuve.exercices.prefetch_related("questions__themes").order_by("numero_exercice"))


def _question_payload_avec_notation(tentative, question, reponse):
    """Payload de question + bloc `notation` (note provisoire mise à jour) renvoyé après
    toute écriture, pour que le frontend n'ait jamais à recalculer une note lui-même. Si la
    tentative est déjà rendue, la note stockée suit chaque notation (voir
    notation.enregistrer_note) : `note_obtenue` n'est jamais périmée."""
    exercices = _exercices_pour_notation(tentative.epreuve)
    correction_disponible = _correction_disponible(tentative)
    bilan = notation.calculer(tentative, exercices)
    if tentative.submitted_at is not None:
        notation.enregistrer_note(tentative, bilan)
    payload = _question_payload(
        question, reponse, correction_disponible=correction_disponible, exercice=question.exercice,
        points_info=notation.points_par_question(exercices)[question.pk],
    )
    payload["notation"] = notation.resume(tentative, bilan) if correction_disponible else None
    return payload


def _alimenter_revision(tentative, question, correcte):
    """Alimente quiz.RevisionSchedule - réutilisé tel quel plutôt qu'un second mécanisme
    de suivi de faiblesse (voir l'audit "Épreuves Inédites") : (user, cursus, theme)
    est la même clé quelle que soit la source (Quiz ou Épreuves Inédites). Une épreuve
    commune à plusieurs séries (voir EpreuveInedite.cursus, M2M) crédite la révision sur
    CHAQUE série couverte, pas seulement la première - la faiblesse détectée concerne
    l'élève sur ce thème, indépendamment de la série qu'il vise."""
    for theme in question.themes.all():
        for cursus in tentative.epreuve.cursus.all():
            enregistrer_resultat_pour_revision(
                tentative.user, cursus, tentative.epreuve.subject, theme, correcte,
            )


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
    première réponse qui vient de compléter la tentative, et `definitive` (note terminée
    ET épreuve rendue) serait faux."""
    if not tentative.submitted_at:
        tentative.submitted_at = timezone.now()
        tentative.save(update_fields=["submitted_at"])
        exercices = _exercices_pour_notation(tentative.epreuve)
        bilan = notation.calculer(tentative, exercices)
        notation.enregistrer_note(tentative, bilan)
        _planifier_revisions_des_questions_non_traitees(tentative, exercices)
        return _tentative_resultat_payload(tentative, bilan)
    return _tentative_resultat_payload(tentative)


def _planifier_revisions_des_questions_non_traitees(tentative, exercices):
    """Une question laissée de côté à l'examen est une faiblesse comme une question ratée :
    son thème revient dans la séance du jour, exactement comme un thème raté (voir
    quiz.services.enregistrer_resultat_pour_revision). Appelé UNE seule fois, à la
    première soumission - les questions traitées, elles, alimentent la révision au moment
    où l'élève les note (voir noter_question)."""
    reponses = {r.question_id: r for r in tentative.reponses.all()}
    for exercice in exercices:
        for question in exercice.questions.all():
            if not notation.est_traitee(question, reponses.get(question.pk)):
                _alimenter_revision(tentative, question, False)


def _comparaison(tentative, resume):
    """Où l'élève se situe parmi les autres candidats de la MÊME épreuve passée en conditions
    réelles - jamais pour un entraînement libre, et seulement quand l'effectif le permet
    (voir rapport.situer). On compare la meilleure note de chaque autre élève : quelqu'un qui
    a refait dix fois l'épreuve n'y pèse pas dix fois."""
    if tentative.exam_mode_started_at is None or not resume["definitive"] or resume["note"] is None:
        return None
    autres = (
        TentativeInedite.objects.filter(
            epreuve_id=tentative.epreuve_id, exam_mode_started_at__isnull=False,
            submitted_at__isnull=False, note_obtenue__isnull=False,
        )
        .exclude(user_id=tentative.user_id)
        .values("user_id")
        .annotate(meilleure=Max("note_obtenue"))
    )
    return rapport.situer(Decimal(str(resume["note"])), [ligne["meilleure"] for ligne in autres])


def _themes_a_reviser(tentative, bilan):
    """Thèmes de cette épreuve qui reviennent dans la séance du jour de l'élève : ceux où il
    a perdu des points ET pour lesquels une révision est planifiée, avec leur échéance."""
    from quiz.models import RevisionSchedule

    perdus = {
        nom for nom, stats in bilan["par_theme"].items() if stats["points_obtenus"] < stats["points_possibles"]
    }
    ids = {nom: stats["id"] for nom, stats in bilan["par_theme"].items()}
    if not perdus:
        return []
    echeances = {}
    for planification in RevisionSchedule.objects.filter(user=tentative.user, theme__name__in=perdus):
        actuelle = echeances.get(planification.theme.name)
        if actuelle is None or planification.due_at < actuelle:
            echeances[planification.theme.name] = planification.due_at
    return [
        {"theme": nom, "theme_id": ids[nom], "echeance": echeance.isoformat()}
        for nom, echeance in sorted(echeances.items(), key=lambda item: (item[1], item[0]))
    ]


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
    exercices = list(
        tentative.epreuve.exercices
        .prefetch_related("questions__themes", "rappels_de_methode__cours")
        .order_by("numero_exercice")
    )
    reponses_by_question = {r.question_id: r for r in tentative.reponses.all()}
    points_by_question = notation.points_par_question(exercices)
    bilan = notation.calculer(tentative, exercices)
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
        "mode_papier": tentative.mode_papier,
        "submitted_at": tentative.submitted_at,
        "score_obtenu": tentative.score_obtenu,
        "note_obtenue": notation.en_nombre(tentative.note_obtenue),
        "bareme_snapshot": notation.en_nombre(tentative.bareme_snapshot),
        # Barème total (somme des points de toutes les questions) - connu dès le départ,
        # affiché « 0 / 20 » avant toute réponse ; jamais gaté : ce n'est pas la solution.
        "bareme": notation.en_nombre(bilan["bareme"]),
        "bareme_estime": bilan["bareme_estime"],
        # La note inclut les QCM : servie seulement quand le corrigé l'est aussi, sinon
        # elle révélerait en plein examen si chaque QCM déjà coché est juste.
        "notation": notation.resume(tentative, bilan) if correction_disponible else None,
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
                        exercice=exercice, points_info=points_by_question[question.pk],
                    )
                    for question in exercice.questions.all()
                ],
            }
            for exercice in exercices
        ],
    }


def _tentative_resultat_payload(tentative, bilan=None):
    if bilan is None:
        bilan = notation.calculer(tentative, _exercices_pour_notation(tentative.epreuve))
    resume = notation.resume(tentative, bilan)
    temps = rapport.temps_par_exercice(bilan["lignes"], tentative.exam_mode_started_at)

    return {
        "id": tentative.id,
        "epreuve": tentative.epreuve_id,
        # Voir la note équivalente dans _tentative_payload.
        "country": tentative.epreuve.cursus.first().country.code,
        "total_questions": bilan["questions_total"],
        # Questions traitées (et non plus « répondues ») : seules les QCM se répondent
        # dans l'application, une question ouverte est traitée sur brouillon ou papier.
        "questions_repondues": bilan["questions_traitees"],
        "questions_non_traitees": bilan["questions_non_traitees"],
        "questions_a_noter": bilan["questions_a_noter"],
        # Pourcentage du barème COMPLET : une question non traitée pèse comme un échec.
        "score": notation.score_pourcentage(bilan["note"], bilan["bareme"]),
        "note": resume["note"],
        "bareme": resume["bareme"],
        "note_sur_20": resume["note_sur_20"],
        "bareme_estime": resume["bareme_estime"],
        "definitive": resume["definitive"],
        # Comment l'épreuve a été passée : une note d'entraînement ne se lit pas comme une note
        # obtenue en conditions réelles.
        "mode": (
            "libre" if tentative.exam_mode_started_at is None else "papier" if tentative.mode_papier else "examen"
        ),
        "temps_total_secondes": (
            int((tentative.submitted_at - tentative.started_at).total_seconds())
            if tentative.submitted_at else None
        ),
        # Où sont partis les points, où est passé le temps, où l'élève se situe.
        "pertes": rapport.pertes_par_cause(bilan["lignes"]),
        "granularite": "question",
        "temps_par_exercice": temps,
        "exercice_chronophage": rapport.exercice_chronophage(temps),
        "comparaison": _comparaison(tentative, resume),
        "cursus_id": tentative.epreuve.cursus.first().pk,
        "par_exercice": [
            {
                "numero_exercice": e["numero_exercice"],
                "points_possibles": notation.en_nombre(e["points_possibles"]),
                "points_obtenus": notation.en_nombre(e["points_obtenus"]),
            }
            for e in bilan["par_exercice"]
        ],
        # Ce que devient cette épreuve dans la suite du travail : les thèmes ratés ou
        # laissés de côté reviennent dans la séance du jour (voir _themes_a_reviser).
        "themes_a_reviser": _themes_a_reviser(tentative, bilan),
        "par_theme": [
            {
                "theme": nom,
                "theme_id": s["id"],
                "total": s["total"],
                "reussies": s["reussies"],
                "points_possibles": notation.en_nombre(s["points_possibles"]),
                "points_obtenus": notation.en_nombre(s["points_obtenus"]),
            }
            for nom, s in sorted(bilan["par_theme"].items())
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
            "note_obtenue": notation.en_nombre(tentative.note_obtenue),
            "bareme_snapshot": notation.en_nombre(tentative.bareme_snapshot),
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

    _alimenter_revision(tentative, question, reponse.est_correcte)

    return Response(_question_payload_avec_notation(tentative, question, reponse))


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

    papier = _as_bool(request.data.get("papier"))
    if papier and not tentative.epreuve.sujet_pdf:
        return Response({"error": "Cette épreuve n'a pas de sujet PDF à imprimer."}, status=400)

    tentative.exam_mode_started_at = timezone.now()
    tentative.mode_papier = papier
    tentative.save(update_fields=["exam_mode_started_at", "mode_papier"])
    return Response(_tentative_payload(tentative))


def _as_bool(valeur):
    return valeur is True or str(valeur).lower() in ("true", "1")


@api_view(["POST"])
def noter_question(request, tentative_id, question_id):
    """Traitement et notation d'une question OUVERTE - distinct de answer_question, qui
    reste réservé aux QCM (et à l'ancien resultat_declare) et refuse toute écriture une
    fois la tentative rendue. Ici, deux gestes de nature différente :

    - `traitee` : « j'ai traité cette question ». Possible en plein mode examen (le
      corrigé est masqué, on ne note pas encore) ; APRÈS la soumission, seul
      `traitee: true` reste permis (question faite sur papier), jamais le retrait - un
      élève ne peut pas effacer après coup une question qu'il a rendue.
    - `criteres_valides` (indices cochés de la grille) ou `points_obtenus` (saisie
      directe, question sans grille) : la notation elle-même, qui exige le corrigé
      (_correction_disponible) - sans ça un élève pourrait se noter à l'aveugle pendant
      l'examen. Autorisée avant comme après la soumission : c'est justement après la
      soumission, corrigé ouvert, que l'élève se note.

    Une question notée devient automatiquement traitée : noter, c'est avoir traité."""
    tentative = get_object_or_404(
        TentativeInedite.objects.select_related("epreuve__blueprint"), pk=tentative_id, user=request.user,
    )
    _auto_complete_if_expired(tentative)
    question = get_object_or_404(
        QuestionInedite.objects.select_related("exercice").prefetch_related("themes"),
        pk=question_id, exercice__epreuve_id=tentative.epreuve_id,
    )
    if question.type_reponse == TypeReponse.QCM:
        return Response({"error": "Une question à choix multiple se répond en choisissant une proposition."}, status=400)

    data = request.data
    reponse = TentativeReponse.objects.filter(tentative=tentative, question=question).first()
    a_noter = "criteres_valides" in data or "points_obtenus" in data

    if "traitee" in data and not a_noter:
        if _as_bool(data["traitee"]):
            if reponse is None:
                reponse = TentativeReponse.objects.create(tentative=tentative, question=question, traitee_at=timezone.now())
            elif reponse.traitee_at is None:
                reponse.traitee_at = timezone.now()
                reponse.save(update_fields=["traitee_at"])
        else:
            if tentative.submitted_at is not None:
                return Response({"error": "Cette tentative est terminée, impossible de retirer cette question."}, status=409)
            if reponse is not None:
                reponse.delete()
                reponse = None
        return Response(_question_payload_avec_notation(tentative, question, reponse))

    if "cause_perte" in data and not a_noter:
        if not _correction_disponible(tentative):
            return Response({"error": "Le corrigé n'est pas encore disponible : impossible d'en donner la cause."}, status=403)
        cause = data["cause_perte"] or ""
        if cause not in CausePerte.values and cause != "":
            return Response({"error": f"cause_perte invalide : {cause!r}. Attendu {CausePerte.values} ou vide."}, status=400)
        if reponse is None:
            if not cause:
                return Response(_question_payload_avec_notation(tentative, question, None))
            reponse = TentativeReponse(tentative=tentative, question=question)
        reponse.cause_perte = cause
        reponse.save()
        return Response(_question_payload_avec_notation(tentative, question, reponse))

    if not a_noter:
        return Response({"error": "Rien à enregistrer : traitee, criteres_valides, points_obtenus ou cause_perte attendu."}, status=400)
    if not _correction_disponible(tentative):
        return Response({"error": "Le corrigé n'est pas encore disponible : impossible de noter cette question."}, status=403)

    exercices = _exercices_pour_notation(tentative.epreuve)
    points, _estime = notation.points_par_question(exercices)[question.pk]

    if "criteres_valides" in data:
        if not question.criteres_notation:
            return Response({"error": "Cette question n'a pas de grille de notation."}, status=400)
        try:
            obtenus = notation.points_depuis_criteres(question, data["criteres_valides"])
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        criteres_valides = sorted(data["criteres_valides"])
    else:
        if question.criteres_notation:
            return Response({"error": "Cette question se note en cochant les critères de sa grille."}, status=400)
        try:
            obtenus = Decimal(str(data["points_obtenus"]).replace(",", "."))
        except InvalidOperation:
            return Response({"error": "points_obtenus doit être un nombre."}, status=400)
        if not obtenus.is_finite() or obtenus < 0 or obtenus > points:
            return Response({"error": f"points_obtenus doit être compris entre 0 et {notation.en_nombre(points)}."}, status=400)
        criteres_valides = []
    obtenus = min(notation.arrondi(obtenus), points)

    premiere_notation = reponse is None or (reponse.points_obtenus is None and not reponse.resultat_declare)
    if reponse is None:
        reponse = TentativeReponse(tentative=tentative, question=question)
    reponse.traitee_at = reponse.traitee_at or timezone.now()
    reponse.points_obtenus = obtenus
    reponse.criteres_valides = criteres_valides
    reponse.resultat_declare = notation.resultat_declare_depuis_points(obtenus, points)
    reponse.save()

    # Une seule fois par question : cocher/décocher un critère ne doit pas faire avancer
    # (ou reculer) plusieurs fois le palier de révision du thème (voir _alimenter_revision).
    if premiere_notation:
        _alimenter_revision(tentative, question, reponse.est_correcte)

    return Response(_question_payload_avec_notation(tentative, question, reponse))


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
