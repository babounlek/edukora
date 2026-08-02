import random

from catalog.models import Difficulte, StatutContenu

from .models import CompetenceItem, ModeQuiz, QuizQuestion, QuizSession

# Répartition cible pour un test de niveau (mode DIAGNOSTIC) : couvrir tout le spectre
# de difficulté plutôt que de refléter la composition du catalogue (qui peut être
# majoritairement "moyenne" par exemple, ce qui donnerait un diagnostic peu discriminant).
_REPARTITION_DIAGNOSTIC = {
    Difficulte.FAIBLE: 0.4,
    Difficulte.MOYENNE: 0.4,
    Difficulte.ELEVEE: 0.2,
}


def _items_eligibles(cursus, subject=None, theme=None):
    """
    Source unique du Mode Quiz depuis la bascule : CompetenceItem, jamais
    catalog.Question. Contrairement à l'ancien pool (Question extraite d'un Exercise,
    filtrée après coup par Question.references_missing_figure faute de mieux), un
    CompetenceItem est écrit dès l'origine pour se suffire seul - aucun filtre de
    rattrapage n'est nécessaire ici : statut=VALIDE est la seule porte d'entrée.
    """
    qs = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus).distinct()
    if subject:
        qs = qs.filter(subject=subject)
    if theme:
        qs = qs.filter(theme=theme)
    return list(qs)


def _selection_stratifiee_par_difficulte(items, n):
    """
    Pioche selon _REPARTITION_DIAGNOSTIC. Si une tranche de difficulté n'a pas assez
    d'items disponibles, complète avec les items restants des autres tranches plutôt
    que de renvoyer moins de n items - un test de niveau incomplet est moins utile
    qu'un test légèrement moins équilibré.
    """
    by_difficulte = {}
    for item in items:
        by_difficulte.setdefault(item.difficulte_estimee, []).append(item)
    for bucket in by_difficulte.values():
        random.shuffle(bucket)

    selection = []
    for difficulte, part in _REPARTITION_DIAGNOSTIC.items():
        cible = round(n * part)
        bucket = by_difficulte.get(difficulte, [])
        selection.extend(bucket[:cible])
        by_difficulte[difficulte] = bucket[cible:]

    if len(selection) < n:
        restants = [item for bucket in by_difficulte.values() for item in bucket]
        random.shuffle(restants)
        selection.extend(restants[: n - len(selection)])

    return selection[:n]


def generer_session(user, cursus, mode, subject=None, theme=None, n=10):
    """
    Sélectionne jusqu'à n CompetenceItem et crée une QuizSession. Lève ValueError si
    aucun item n'est éligible pour ces critères (pas encore de banque générée pour
    cette compétence/ce cursus) - à la vue de traduire en réponse HTTP appropriée. Ce
    ValueError est attendu tant que la banque CompetenceItem n'est pas encore peuplée
    pour un cursus/thème donné - ce n'est pas un bug, voir la discussion de bascule.

    mode=DIAGNOSTIC : répartition stratifiée par difficulté (voir
    _selection_stratifiee_par_difficulte). mode=PRATIQUE : tirage aléatoire simple pour
    cette V1 - pondérer par thèmes où l'élève échoue le plus est un fast-follow naturel
    une fois QuizAnswer réellement peuplé par l'usage, pas construit contre zéro donnée.
    """
    items = _items_eligibles(cursus, subject=subject, theme=theme)
    if not items:
        raise ValueError("Aucune question disponible pour ces critères.")

    if mode == ModeQuiz.DIAGNOSTIC:
        selection = _selection_stratifiee_par_difficulte(items, n)
    else:
        random.shuffle(items)
        selection = items[:n]

    session = QuizSession.objects.create(user=user, cursus=cursus, subject=subject, theme=theme, mode=mode)
    QuizQuestion.objects.bulk_create([
        QuizQuestion(session=session, competence_item=item, ordre=ordre)
        for ordre, item in enumerate(selection, start=1)
    ])
    return session
