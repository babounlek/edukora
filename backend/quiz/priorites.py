"""
Priorités d'un élève pour son examen : où concentrer son temps, et pourquoi.

Montrées à la fin du diagnostic d'accueil, sur une base volontairement modeste : trois
réponses par matière ne mesurent pas un niveau. Le classement combine donc ce qui est
solide (le coefficient de la matière, lu dans les épreuves réelles) et ce qui est
indicatif (les réponses de l'élève, tirées vers 50 % tant qu'elles sont peu nombreuses).
Jamais de pourcentage affiché sur un si petit échantillon : la restitution parle en
"réussies sur posées".
"""
from catalog.models import ExamSession, StatutContenu, Subject

from .models import ModeQuiz, QuizAnswer, QuizSession
from .services import COEFFICIENT_PAR_DEFAUT, _coefficient_par_subject

# Poids, en réponses, de l'a priori "50 %" : avec 3 réponses la moyenne bouge d'environ
# un dixième, avec 30 elle domine. Un diagnostic nuance le classement par coefficient,
# il ne le renverse pas - ce qui est exactement ce que trois questions justifient.
POIDS_A_PRIORI = 10
PRIORITES_EN_TETE = 3
THEMES_A_TRAVAILLER_MAX = 5


def _niveau(reussies, total):
    """Repère qualitatif, jamais un chiffre : sous deux réponses, on ne dit rien."""
    if total < 2:
        return "a_situer"
    taux = reussies / total
    if taux < 0.4:
        return "fragile"
    if taux < 0.7:
        return "moyen"
    return "solide"


def priorites_examen(user, cursus):
    subjects = list(
        Subject.objects.filter(lessons__statut=StatutContenu.VALIDE, lessons__cursus=cursus).distinct(),
    )
    coefficients = _coefficient_par_subject(cursus)

    stats = {s.id: {"total": 0, "reussies": 0} for s in subjects}
    for reponse in (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
        )
        .select_related("quiz_question__competence_item")
    ):
        s = stats.get(reponse.quiz_question.competence_item.subject_id)
        if s is None:
            continue
        s["total"] += 1
        s["reussies"] += int(reponse.est_correcte)

    lignes = []
    for subject in subjects:
        s = stats[subject.id]
        coefficient = coefficients.get(subject.id)
        poids = coefficient if coefficient is not None else COEFFICIENT_PAR_DEFAUT
        estimation = (s["reussies"] + POIDS_A_PRIORI / 2) / (s["total"] + POIDS_A_PRIORI)
        lignes.append({
            "subject_id": subject.id,
            "subject_label": subject.label,
            "subject_code": subject.code,
            "coefficient": coefficient,
            "reussies": s["reussies"],
            "total": s["total"],
            "niveau": _niveau(s["reussies"], s["total"]),
            "_score": poids * (1 - estimation),
        })

    lignes.sort(key=lambda ligne: (-ligne["_score"], ligne["subject_label"]))
    score_max = lignes[0]["_score"] if lignes and lignes[0]["_score"] > 0 else 1
    for rang, ligne in enumerate(lignes, start=1):
        # Longueur de barre relative à la première : lisible d'un coup d'œil, sans
        # prétendre à une valeur absolue.
        ligne["urgence"] = round(100 * ligne.pop("_score") / score_max)
        ligne["rang"] = rang
        ligne["prioritaire"] = rang <= PRIORITES_EN_TETE

    diagnostic = (
        QuizSession.objects.filter(
            user=user, cursus=cursus, mode=ModeQuiz.DIAGNOSTIC, completed_at__isnull=False,
        )
        .order_by("-completed_at")
        .first()
    )

    compte = ExamSession.compte_a_rebours_pour(cursus)
    return {
        "a_deja_repondu": any(s["total"] for s in stats.values()),
        "diagnostic_fait": diagnostic is not None,
        "compte_a_rebours": compte,
        "matieres": lignes,
        "themes_a_travailler": _themes_rates(diagnostic),
    }


def _themes_rates(session):
    """Les thèmes ratés au dernier diagnostic : du concret, et exactement ce que l'élève
    a vu passer - jamais une déduction. Vide sans diagnostic."""
    if session is None:
        return []
    themes = []
    vus = set()
    for quiz_question in (
        session.quiz_questions
        .select_related("answer", "competence_item__theme", "competence_item__subject")
        .order_by("ordre")
    ):
        item = quiz_question.competence_item
        answer = getattr(quiz_question, "answer", None)
        if item is None or answer is None or answer.est_correcte or item.theme_id in vus:
            continue
        vus.add(item.theme_id)
        themes.append({"theme": item.theme.name, "subject_label": item.subject.label})
    return themes[:THEMES_A_TRAVAILLER_MAX]
