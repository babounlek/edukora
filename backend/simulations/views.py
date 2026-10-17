"""
Simulation d'épreuve officielle : mêmes règles que les épreuves inédites (voir inedit.views),
au niveau de l'exercice. Le payload reprend la forme de TentativeInedite - un exercice = un
bloc d'une seule « question » - pour que la page d'épreuve du frontend serve aux deux sans
connaître la différence.
"""

from decimal import Decimal, InvalidOperation

from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from access.services import has_access
from catalog.libelles import libelle_cursus
from catalog.models import EXAMENS_GCE, Lesson, LessonType, Question, TypeReponse
from inedit import notation, rapport
from inedit.models import CausePerte, ResultatDeclare
from quiz.services import enregistrer_resultat_pour_revision
from users.profils import profil_actif

from . import choix
from .cadre import charger_exercices, duree_minutes_pour_lesson, simulation_a_la_question
from .models import SimulationEpreuve, SimulationReponse

DIFFICULTE_CORRIGE_MASQUE = "Le corrigé n'est pas encore disponible pour cette simulation."


# --------------------------------------------------------------------------- règles communes


def _correction_disponible(simulation):
    """Même frontière anti-triche que les épreuves inédites : le corrigé n'est masqué que
    pendant une fenêtre chronométrée active et non rendue."""
    return simulation.submitted_at is not None or simulation.exam_mode_started_at is None


def _duree_info(simulation):
    """(minutes, estimee) - voir cadre.duree_minutes_pour_lesson. `estimee` dit que la durée
    vient des autres sessions de cette épreuve, jamais de son propre en-tête."""
    return duree_minutes_pour_lesson(simulation.lesson)


def _duree(simulation):
    return _duree_info(simulation)[0]


def _deadline(simulation):
    duree = _duree(simulation)
    if not simulation.exam_mode_started_at or not duree:
        return None
    return simulation.exam_mode_started_at + timezone.timedelta(minutes=duree)


def _cursus(simulation):
    return list(simulation.lesson.cursus.select_related("country", "series"))


def _alimenter_revision(simulation, exercice, correcte):
    """Un exercice raté ou laissé de côté fait revenir ses thèmes principaux dans la séance du
    jour - même mécanisme que pour les quiz et les épreuves inédites."""
    _alimenter_revision_themes(simulation, exercice.questions.all()[0].themes.all(), correcte)


def _alimenter_revision_themes(simulation, themes, correcte):
    for cursus in _cursus(simulation):
        for theme in themes:
            enregistrer_resultat_pour_revision(
                simulation.profil, cursus, simulation.lesson.subject, theme, correcte,
            )


def _bilan(simulation, exercices=None):
    exercices = exercices if exercices is not None else charger_exercices(simulation.lesson)
    return choix.calculer(simulation, exercices), exercices


def _est_gce(simulation):
    return any(c.examen in EXAMENS_GCE for c in _cursus(simulation))


def _resume(simulation, bilan):
    """notation.resume, sans note sur 20 pour le GCE : le Board note en grades (A-E, A-F), jamais
    sur 20 ; un 20 inventé tromperait l'élève. Le pourcentage et les points restent."""
    resume = notation.resume(simulation, bilan)
    if _est_gce(simulation):
        resume["note_sur_20"] = None
    return resume


def _complete(simulation):
    if simulation.submitted_at:
        return _resultat_payload(simulation)
    simulation.submitted_at = timezone.now()
    simulation.save(update_fields=["submitted_at"])
    bilan, exercices = _bilan(simulation)
    notation.enregistrer_note(simulation, bilan)
    # Exercices laissés de côté : leur thème est une faiblesse comme un exercice raté.
    reponses = {r.question_id: r for r in simulation.reponses.all()}
    if simulation_a_la_question(simulation.lesson):
        for exercice in exercices:
            for question in exercice.questions.all():
                if not notation.est_traitee(question, reponses.get(question.pk)):
                    _alimenter_revision_themes(simulation, question.themes.all(), False)
        return _resultat_payload(simulation, bilan, exercices)
    for exercice in exercices:
        if exercice.id in bilan["non_comptes"]:
            continue
        question = exercice.questions.all()[0]
        if not notation.est_traitee(question, reponses.get(question.pk)):
            _alimenter_revision(simulation, exercice, False)
    return _resultat_payload(simulation, bilan, exercices)


def _auto_complete_if_expired(simulation):
    if simulation.submitted_at is not None:
        return
    deadline = _deadline(simulation)
    if deadline is not None and timezone.now() >= deadline:
        _complete(simulation)


# --------------------------------------------------------------------------- charges utiles


_cursus_display = libelle_cursus


def _exercice_payload(simulation, exercice, reponse, correction, points_info):
    question = exercice.questions.all()[0]
    points, estime = points_info
    payload = {
        "id": exercice.id,
        "numero": exercice.numero_exercice,
        "ordre": exercice.id,
        "groupe_local": "",
        "enonce_markdown": exercice.enonce_markdown,
        "type_reponse": "OUVERTE",
        "choix": [],
        "traitee": notation.est_traitee(question, reponse),
        "points": notation.en_nombre(points),
        "bareme_estime": estime,
    }
    if reponse:
        payload["reponse"] = {"reponse_choisie": "", "resultat_declare": reponse.resultat_declare}
        if correction:
            notee = notation.est_notee(question, reponse)
            payload["reponse"].update({
                "est_correcte": reponse.est_correcte,
                "notee": notee,
                "criteres_valides": [],
                "cause_perte": reponse.cause_perte,
                "points_obtenus": notation.en_nombre(notation.points_obtenus(question, reponse, points)) if notee else None,
            })
    if correction:
        payload["corrige_markdown"] = exercice.corrige_markdown
        payload["reponse_correcte"] = ""
        payload["criteres_notation"] = []
    return payload


def _question_payload(question, reponse, correction, points_info):
    """Une question d'un Paper 1 (simulation à la question) - même forme que
    inedit.views._question_payload. Le résultat d'un QCM n'est exposé qu'avec le corrigé."""
    points, estime = points_info
    ouverte = question.type_reponse != TypeReponse.QCM
    payload = {
        "id": question.pk,
        "numero": question.numero,
        "ordre": question.ordre,
        "groupe_local": "",
        "enonce_markdown": question.enonce_markdown,
        "type_reponse": question.type_reponse,
        "choix": question.choix,
        "traitee": notation.est_traitee(question, reponse),
        "points": notation.en_nombre(points),
        "bareme_estime": estime,
    }
    if reponse:
        payload["reponse"] = {
            "reponse_choisie": reponse.reponse_choisie,
            "resultat_declare": reponse.resultat_declare if (ouverte or correction) else "",
        }
        if correction:
            notee = notation.est_notee(question, reponse)
            payload["reponse"].update({
                "est_correcte": reponse.est_correcte,
                "notee": notee,
                "criteres_valides": [],
                "cause_perte": reponse.cause_perte,
                "points_obtenus": notation.en_nombre(notation.points_obtenus(question, reponse, points)) if notee else None,
            })
    if correction:
        payload["corrige_markdown"] = question.corrige_markdown
        payload["reponse_correcte"] = question.reponse_correcte
        payload["criteres_notation"] = []
    return payload


def _marquees(simulation):
    if simulation_a_la_question(simulation.lesson):
        return list(simulation.questions_marquees_qcm.values_list("pk", flat=True))
    return list(simulation.exercices_marques.values_list("pk", flat=True))


def _payload(simulation):
    lesson = simulation.lesson
    correction = _correction_disponible(simulation)
    exercices = charger_exercices(lesson)
    bilan = choix.calculer(simulation, exercices)
    points_par_question = notation.points_par_question(exercices)
    reponses = {r.question_id: r for r in simulation.reponses.all()}
    par_question = simulation_a_la_question(lesson)
    cursus = _cursus(simulation)
    duree, duree_estimee = _duree_info(simulation)
    return {
        "id": simulation.id,
        "source": "officielle",
        # Chaque exercice est noté d'un bloc, sauf un Paper 1 (QCM) qui se répond question par question.
        "granularite": "question" if par_question else "exercice",
        "epreuve": lesson.id,
        "epreuve_titre": lesson.title,
        "country": lesson.subject.country.code,
        "cursus_display": _cursus_display(cursus),
        "duree_minutes": duree,
        # Cette épreuve n'annonce pas sa propre durée : déduite des autres sessions de la même
        # (matière, examen, série, nature d'épreuve) - voir cadre.duree_minutes_pour_lesson.
        "duree_estimee": duree_estimee,
        "sujet_pdf_disponible": bool(lesson.sujet_pdf),
        "sujet_pdf_url": lesson.sujet_pdf.url if lesson.sujet_pdf else None,
        "started_at": simulation.started_at,
        "exam_mode_started_at": simulation.exam_mode_started_at,
        "mode_papier": simulation.mode_papier,
        "submitted_at": simulation.submitted_at,
        "score_obtenu": simulation.score_obtenu,
        "note_obtenue": notation.en_nombre(simulation.note_obtenue),
        "bareme_snapshot": notation.en_nombre(simulation.bareme_snapshot),
        "bareme": notation.en_nombre(bilan["bareme"]),
        "bareme_estime": bilan["bareme_estime"],
        "notation": _resume(simulation, bilan) if correction else None,
        "regles_choix": choix.regles_exposees(lesson, exercices),
        "non_comptes": sorted(bilan["non_comptes"]) if correction else [],
        "correction_disponible": correction,
        "questions_marquees": _marquees(simulation),
        "exercices": [
            {
                "id": e.id,
                "numero_exercice": e.numero_exercice,
                "points": e.points,
                "groupes": e.groupes,
                "enonce_intro_markdown": e.enonce_intro_markdown,
                "questions": [
                    _question_payload(q, reponses.get(q.pk), correction, points_par_question[q.pk])
                    for q in e.questions.all()
                ] if par_question else [
                    _exercice_payload(
                        simulation, e, reponses.get(e.id), correction, points_par_question[e.questions.all()[0].pk],
                    ),
                ],
            }
            for e in exercices
        ],
    }


def _question_payload_avec_notation(simulation, exercice_id, reponse):
    """Payload de l'exercice (ou de la question, pour un Paper 1) + note provisoire, renvoyé après
    toute écriture (même contrat que inedit.views._question_payload_avec_notation)."""
    exercices = charger_exercices(simulation.lesson)
    correction = _correction_disponible(simulation)
    bilan = choix.calculer(simulation, exercices)
    if simulation.submitted_at is not None:
        notation.enregistrer_note(simulation, bilan)
    points = notation.points_par_question(exercices)
    if simulation_a_la_question(simulation.lesson):
        question = next(q for e in exercices for q in e.questions.all() if q.pk == exercice_id)
        payload = _question_payload(question, reponse, correction, points[question.pk])
        payload["notation"] = _resume(simulation, bilan) if correction else None
        return payload
    exercice = next(e for e in exercices if e.id == exercice_id)
    points_info = points[exercice.questions.all()[0].pk]
    payload = _exercice_payload(simulation, exercice, reponse, correction, points_info)
    payload["notation"] = _resume(simulation, bilan) if correction else None
    if correction:
        # Les « parmi » se recalculent à chaque note : l'écran met à jour tous les exercices.
        payload["non_comptes"] = sorted(bilan["non_comptes"])
    return payload


def _themes_a_reviser(simulation, bilan, exercices):
    from quiz.models import RevisionSchedule

    perdus = {}
    for exercice in exercices:
        if exercice.id in bilan["non_comptes"]:
            continue
        for question in exercice.questions.all():
            for theme in question.themes.all():
                stats = bilan["par_theme"].get(theme.name)
                if stats and stats["points_obtenus"] < stats["points_possibles"]:
                    perdus[theme.name] = theme.pk
    if not perdus:
        return []
    echeances = {}
    for planification in RevisionSchedule.objects.filter(profil=simulation.profil, theme__name__in=perdus):
        actuelle = echeances.get(planification.theme.name)
        if actuelle is None or planification.due_at < actuelle:
            echeances[planification.theme.name] = planification.due_at
    return [
        {"theme": nom, "theme_id": perdus[nom], "echeance": echeance.isoformat()}
        for nom, echeance in sorted(echeances.items(), key=lambda item: (item[1], item[0]))
    ]


def _comparaison(simulation, resume):
    if simulation.exam_mode_started_at is None or not resume["definitive"] or resume["note"] is None:
        return None
    autres = (
        SimulationEpreuve.objects.filter(
            lesson_id=simulation.lesson_id, exam_mode_started_at__isnull=False,
            submitted_at__isnull=False, note_obtenue__isnull=False,
        )
        .exclude(profil_id=simulation.profil_id)
        .values("profil_id")
        .annotate(meilleure=Max("note_obtenue"))
    )
    return rapport.situer(Decimal(str(resume["note"])), [ligne["meilleure"] for ligne in autres])


def _resultat_payload(simulation, bilan=None, exercices=None):
    par_question = simulation_a_la_question(simulation.lesson)
    if bilan is None:
        bilan, exercices = _bilan(simulation)
    resume = _resume(simulation, bilan)
    temps = rapport.temps_par_exercice(bilan["lignes"], simulation.exam_mode_started_at)
    cursus = _cursus(simulation)
    return {
        "id": simulation.id,
        "epreuve": simulation.lesson_id,
        "epreuve_titre": simulation.lesson.title,
        "country": simulation.lesson.subject.country.code,
        "total_questions": bilan["questions_total"],
        "questions_repondues": bilan["questions_traitees"],
        "questions_non_traitees": bilan["questions_non_traitees"],
        "questions_a_noter": bilan["questions_a_noter"],
        "score": notation.score_pourcentage(bilan["note"], bilan["bareme"]),
        "note": resume["note"],
        "bareme": resume["bareme"],
        "note_sur_20": resume["note_sur_20"],
        "bareme_estime": resume["bareme_estime"],
        "definitive": resume["definitive"],
        "mode": (
            "libre" if simulation.exam_mode_started_at is None else "papier" if simulation.mode_papier else "examen"
        ),
        "temps_total_secondes": (
            int((simulation.submitted_at - simulation.started_at).total_seconds()) if simulation.submitted_at else None
        ),
        "pertes": rapport.pertes_par_cause(bilan["lignes"], unite="question" if par_question else "exercice"),
        "granularite": "question" if par_question else "exercice",
        "temps_par_exercice": temps,
        "exercice_chronophage": rapport.exercice_chronophage(temps),
        "comparaison": _comparaison(simulation, resume),
        "cursus_id": cursus[0].pk if cursus else (simulation.profil.compte.cursus_prepare_id or None),
        "par_exercice": [
            {
                "numero_exercice": e["numero_exercice"],
                "points_possibles": notation.en_nombre(e["points_possibles"]),
                "points_obtenus": notation.en_nombre(e["points_obtenus"]),
                "compte": e["compte"],
            }
            for e in bilan["par_exercice"]
        ],
        "regles_choix": choix.regles_exposees(simulation.lesson, exercices or charger_exercices(simulation.lesson)),
        "themes_a_reviser": _themes_a_reviser(simulation, bilan, exercices or charger_exercices(simulation.lesson)),
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


# --------------------------------------------------------------------------- vues


def _simulation_de(request, simulation_id):
    return get_object_or_404(
        SimulationEpreuve.objects.select_related("lesson__subject__country"),
        pk=simulation_id, profil=profil_actif(request),
    )


@api_view(["POST"])
def start_simulation(request):
    """Ouvre une simulation sur une épreuve officielle. Même accès que la lecture du corrigé
    (abonnement au cursus, ou épreuve « vitrine ») : la simulation donne le corrigé à la fin."""
    lesson = get_object_or_404(
        Lesson.objects.visibles().select_related("subject__country"),
        pk=request.data.get("epreuve"), lesson_type=LessonType.CORR,
    )
    if not has_access(request.user, lesson, profil_actif(request)):
        return Response({"error": "Abonnement requis pour simuler cette épreuve."}, status=403)
    if not charger_exercices(lesson):
        return Response({"error": "Cette épreuve n'est pas découpée en exercices : simulation impossible."}, status=400)
    simulation = SimulationEpreuve.objects.create(profil=profil_actif(request), lesson=lesson)
    return Response(_payload(simulation), status=201)


@api_view(["GET"])
def simulation_detail(request, simulation_id):
    simulation = _simulation_de(request, simulation_id)
    _auto_complete_if_expired(simulation)
    return Response(_payload(simulation))


@api_view(["GET"])
def mes_simulations(request):
    simulations = (
        SimulationEpreuve.objects.filter(profil=profil_actif(request)).select_related("lesson").order_by("-started_at")
    )
    return Response([
        {
            "id": s.id,
            "epreuve": s.lesson_id,
            "epreuve_titre": s.lesson.title,
            "started_at": s.started_at,
            "submitted_at": s.submitted_at,
            "note_obtenue": notation.en_nombre(s.note_obtenue),
            "bareme_snapshot": notation.en_nombre(s.bareme_snapshot),
            "score_obtenu": s.score_obtenu,
        }
        for s in simulations
    ])


def _as_bool(valeur):
    return valeur is True or str(valeur).lower() in ("true", "1")


@api_view(["POST"])
def start_exam_mode(request, simulation_id):
    simulation = _simulation_de(request, simulation_id)
    if simulation.submitted_at is not None:
        return Response({"error": "Cette simulation est déjà terminée."}, status=409)
    if simulation.exam_mode_started_at is not None:
        return Response(_payload(simulation))
    if not _duree(simulation):
        return Response(
            {"error": "La durée de cette épreuve n'est pas connue : le mode examen n'est pas disponible."}, status=400,
        )
    if simulation.reponses.exists():
        return Response({"error": "Le mode examen doit être activé avant de commencer."}, status=409)
    papier = _as_bool(request.data.get("papier"))
    if papier and not simulation.lesson.sujet_pdf:
        return Response({"error": "Cette épreuve n'a pas de sujet PDF à imprimer."}, status=400)
    simulation.exam_mode_started_at = timezone.now()
    simulation.mode_papier = papier
    simulation.save(update_fields=["exam_mode_started_at", "mode_papier"])
    return Response(_payload(simulation))


@api_view(["POST"])
def toggle_marque(request, simulation_id, exercice_id):
    simulation = _simulation_de(request, simulation_id)
    if simulation_a_la_question(simulation.lesson):
        question = get_object_or_404(Question, pk=exercice_id, exercise__lesson_id=simulation.lesson_id)
        if simulation.questions_marquees_qcm.filter(pk=question.pk).exists():
            simulation.questions_marquees_qcm.remove(question)
        else:
            simulation.questions_marquees_qcm.add(question)
        return Response({"questions_marquees": _marquees(simulation)})
    exercice = get_object_or_404(simulation.lesson.exercises.all(), pk=exercice_id)
    if simulation.exercices_marques.filter(pk=exercice.pk).exists():
        simulation.exercices_marques.remove(exercice)
    else:
        simulation.exercices_marques.add(exercice)
    return Response({"questions_marquees": list(simulation.exercices_marques.values_list("pk", flat=True))})


@api_view(["POST"])
def noter_exercice(request, simulation_id, exercice_id):
    """Déclare un exercice traité, le note, ou en donne la cause de perte - mêmes règles que
    inedit.views.noter_question : `traitee` possible en plein chrono, notation et cause seulement
    une fois le corrigé disponible, une question notée est automatiquement traitée."""
    simulation = _simulation_de(request, simulation_id)
    _auto_complete_if_expired(simulation)
    exercices = charger_exercices(simulation.lesson)
    if simulation_a_la_question(simulation.lesson):
        # Paper 1 : « exercice_id » désigne ici une QUESTION.
        cible = next(((e, q) for e in exercices for q in e.questions.all() if q.pk == exercice_id), None)
        if cible is None:
            return Response({"error": "Question inconnue."}, status=404)
        exercice, question = cible
        if question.type_reponse == TypeReponse.QCM:
            return Response({"error": "Un QCM se répond, il ne se note pas : utiliser « repondre »."}, status=400)
        lien = {"exercise_id": exercice.id, "sous_question_id": question.pk}
    else:
        exercice = next((e for e in exercices if e.id == exercice_id), None)
        if exercice is None:
            return Response({"error": "Exercice inconnu."}, status=404)
        question = exercice.questions.all()[0]
        lien = {"exercise_id": exercice_id}
    data = request.data
    reponse = SimulationReponse.objects.filter(simulation=simulation, **lien).first()
    a_noter = "points_obtenus" in data

    if "traitee" in data and not a_noter:
        if _as_bool(data["traitee"]):
            if reponse is None:
                reponse = SimulationReponse.objects.create(
                    simulation=simulation, **lien, traitee_at=timezone.now(),
                )
            elif reponse.traitee_at is None:
                reponse.traitee_at = timezone.now()
                reponse.save(update_fields=["traitee_at"])
        else:
            if simulation.submitted_at is not None:
                return Response({"error": "Cette simulation est terminée, impossible de retirer cet exercice."}, status=409)
            if reponse is not None:
                reponse.delete()
                reponse = None
        return Response(_question_payload_avec_notation(simulation, exercice_id, reponse))

    if "cause_perte" in data and not a_noter:
        if not _correction_disponible(simulation):
            return Response({"error": DIFFICULTE_CORRIGE_MASQUE}, status=403)
        cause = data["cause_perte"] or ""
        if cause and cause not in CausePerte.values:
            return Response({"error": f"cause_perte invalide : {cause!r}."}, status=400)
        if reponse is None:
            if not cause:
                return Response(_question_payload_avec_notation(simulation, exercice_id, None))
            reponse = SimulationReponse(simulation=simulation, **lien)
        reponse.cause_perte = cause
        reponse.save()
        return Response(_question_payload_avec_notation(simulation, exercice_id, reponse))

    if not a_noter:
        return Response({"error": "Rien à enregistrer : traitee, points_obtenus ou cause_perte attendu."}, status=400)
    if not _correction_disponible(simulation):
        return Response({"error": DIFFICULTE_CORRIGE_MASQUE}, status=403)

    points, _estime = notation.points_par_question(exercices)[question.pk]
    try:
        obtenus = Decimal(str(data["points_obtenus"]).replace(",", "."))
    except InvalidOperation:
        return Response({"error": "points_obtenus doit être un nombre."}, status=400)
    if not obtenus.is_finite() or obtenus < 0 or obtenus > points:
        return Response({"error": f"points_obtenus doit être compris entre 0 et {notation.en_nombre(points)}."}, status=400)
    obtenus = min(notation.arrondi(obtenus), points)

    premiere_notation = reponse is None or (reponse.points_obtenus is None and not reponse.resultat_declare)
    if reponse is None:
        reponse = SimulationReponse(simulation=simulation, **lien)
    reponse.traitee_at = reponse.traitee_at or timezone.now()
    reponse.points_obtenus = obtenus
    reponse.resultat_declare = notation.resultat_declare_depuis_points(obtenus, points)
    reponse.save()
    if premiere_notation:
        _alimenter_revision_themes(simulation, question.themes.all(), reponse.est_correcte)
    return Response(_question_payload_avec_notation(simulation, exercice_id, reponse))


@api_view(["POST"])
def repondre_question(request, simulation_id, question_id):
    """Réponse à un QCM d'un Paper 1. Le serveur pose lui-même REUSSI / ECHEC : la correction est
    automatique, mais n'est exposée qu'avec le corrigé (voir _question_payload). Idempotent."""
    simulation = _simulation_de(request, simulation_id)
    _auto_complete_if_expired(simulation)
    if simulation.submitted_at is not None:
        return Response({"error": "Cette simulation est terminée, impossible de modifier une réponse."}, status=409)
    if not simulation_a_la_question(simulation.lesson):
        return Response({"error": "Cette épreuve se répond exercice par exercice."}, status=400)
    exercices = charger_exercices(simulation.lesson)
    cible = next(((e, q) for e in exercices for q in e.questions.all() if q.pk == question_id), None)
    if cible is None:
        return Response({"error": "Question inconnue."}, status=404)
    exercice, question = cible
    if question.type_reponse != TypeReponse.QCM:
        return Response({"error": "Cette question n'est pas un QCM : utiliser « noter »."}, status=400)
    lettre = str(request.data.get("reponse_choisie") or "").strip()
    if lettre not in {c.get("lettre") for c in question.choix or []}:
        return Response({"error": "reponse_choisie doit être l'une des lettres proposées."}, status=400)

    correcte = lettre == (question.reponse_correcte or "")
    reponse, _ = SimulationReponse.objects.update_or_create(
        simulation=simulation, exercise_id=exercice.id, sous_question_id=question.pk,
        defaults={
            "reponse_choisie": lettre,
            "resultat_declare": ResultatDeclare.REUSSI if correcte else ResultatDeclare.ECHEC,
            "traitee_at": timezone.now(),
        },
    )
    _alimenter_revision_themes(simulation, question.themes.all(), correcte)
    return Response(_question_payload_avec_notation(simulation, question.pk, reponse))


@api_view(["POST"])
def complete_simulation(request, simulation_id):
    return Response(_complete(_simulation_de(request, simulation_id)))
