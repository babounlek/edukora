import random

from catalog.models import Difficulte, Question, StatutContenu

from .models import ModeQuiz, QuizQuestion, QuizSession

# Répartition cible pour un test de niveau (mode DIAGNOSTIC) : couvrir tout le spectre
# de difficulté plutôt que de refléter la composition du catalogue (qui peut être
# majoritairement "moyenne" par exemple, ce qui donnerait un diagnostic peu discriminant).
_REPARTITION_DIAGNOSTIC = {
    Difficulte.FAIBLE: 0.4,
    Difficulte.MOYENNE: 0.4,
    Difficulte.ELEVEE: 0.2,
}


def _questions_eligibles(cursus, subject=None, theme=None):
    qs = Question.objects.filter(
        exercise__statut=StatutContenu.VALIDE,
        exercise__lesson__statut=StatutContenu.VALIDE,
        exercise__lesson__cursus=cursus,
    ).distinct()
    if subject:
        qs = qs.filter(exercise__lesson__subject=subject)
    if theme:
        qs = qs.filter(themes=theme)
    return qs


def _selection_stratifiee_par_difficulte(questions, n):
    """
    Pioche selon _REPARTITION_DIAGNOSTIC. Si une tranche de difficulté n'a pas assez de
    questions disponibles, complète avec les questions restantes des autres tranches
    plutôt que de renvoyer moins de n questions - un test de niveau incomplet est moins
    utile qu'un test légèrement moins équilibré.
    """
    by_difficulte = {}
    for question in questions:
        by_difficulte.setdefault(question.difficulte_estimee, []).append(question)
    for bucket in by_difficulte.values():
        random.shuffle(bucket)

    selection = []
    for difficulte, part in _REPARTITION_DIAGNOSTIC.items():
        cible = round(n * part)
        bucket = by_difficulte.get(difficulte, [])
        selection.extend(bucket[:cible])
        by_difficulte[difficulte] = bucket[cible:]

    if len(selection) < n:
        restants = [q for bucket in by_difficulte.values() for q in bucket]
        random.shuffle(restants)
        selection.extend(restants[: n - len(selection)])

    return selection[:n]


def generer_session(user, cursus, mode, subject=None, theme=None, n=10):
    """
    Sélectionne jusqu'à n Question et crée une QuizSession. Lève ValueError si aucune
    Question n'est éligible pour ces critères (pas encore de contenu adapté) - à la
    vue de traduire en réponse HTTP appropriée.

    mode=DIAGNOSTIC : répartition stratifiée par difficulté (voir
    _selection_stratifiee_par_difficulte). mode=PRATIQUE : tirage aléatoire simple pour
    cette V1 - pondérer par thèmes où l'élève échoue le plus est un fast-follow naturel
    une fois QuizAnswer réellement peuplé par l'usage, pas construit contre zéro donnée.
    """
    questions = list(_questions_eligibles(cursus, subject=subject, theme=theme))
    if not questions:
        raise ValueError("Aucune question disponible pour ces critères.")

    if mode == ModeQuiz.DIAGNOSTIC:
        selection = _selection_stratifiee_par_difficulte(questions, n)
    else:
        random.shuffle(questions)
        selection = questions[:n]

    session = QuizSession.objects.create(user=user, cursus=cursus, subject=subject, theme=theme, mode=mode)
    QuizQuestion.objects.bulk_create([
        QuizQuestion(session=session, question=question, ordre=ordre)
        for ordre, question in enumerate(selection, start=1)
    ])
    return session
