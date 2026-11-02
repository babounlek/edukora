"""
Où en est un profil dans les questions d'un périmètre (matière, thème) : combien il en a vues dans le tour en cours, et
combien de tours complets il a terminés. Alimente les compteurs « 12/30 » des listes de quiz.

Un tour est fini quand chaque question du périmètre a été répondue au moins une fois depuis le début du tour. Il se
rejoue depuis l'historique, sans état à stocker : on parcourt les réponses dans l'ordre, et le tour redémarre à zéro
dès que la dernière question manquante est répondue. Une ratée répondue deux fois dans le même tour ne compte qu'une
fois, et une question ajoutée au catalogue après un tour terminé rouvre un tour (le tirage la sert d'abord, voir
quiz.services._selection_par_reprise, qui sert de son côté les réussies de la plus ancienne à la plus récente).

Mêmes réponses que le tirage : items de compétence uniquement, rejeux exclus (un rejeu est neutre).
"""
from catalog.models import StatutContenu

from .models import CompetenceItem, QuizAnswer


def _reponses_chronologiques(profil, cursus):
    """Les competence_item_id des réponses du profil sur ce cursus, de la plus ancienne à la plus récente."""
    return list(
        QuizAnswer.objects.filter(
            quiz_question__session__profil=profil,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
            quiz_question__session__rejeu_de__isnull=True,
            quiz_question__session__chrono_actif=False,  # neutre pour la maîtrise aussi (voir quiz.chrono)
        )
        .order_by("answered_at", "id")
        .values_list("quiz_question__competence_item_id", flat=True),
    )


def etat_du_tour(ensemble, reponses):
    """(questions vues dans le tour en cours, tours terminés) pour un ensemble d'ids de questions."""
    if not ensemble:
        return 0, 0
    vues, tours = set(), 0
    for item_id in reponses:
        if item_id not in ensemble:
            continue
        vues.add(item_id)
        if len(vues) == len(ensemble):
            tours += 1
            vues = set()
    return len(vues), tours


def progression_par_matiere(profil, cursus):
    """subject_id -> {"vues", "tours"}, seulement pour les matières où le profil a déjà répondu."""
    reponses = _reponses_chronologiques(profil, cursus)
    if not reponses:
        return {}
    par_matiere = {}
    for item_id, subject_id in (
        CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus).values_list("id", "subject_id").distinct()
    ):
        par_matiere.setdefault(subject_id, set()).add(item_id)

    progression = {}
    for subject_id, ensemble in par_matiere.items():
        vues, tours = etat_du_tour(ensemble, reponses)
        if vues or tours:
            progression[subject_id] = {"vues": vues, "tours": tours}
    return progression


def progression_par_theme(profil, cursus, themes, subject=None):
    """
    tag_id -> {"total", "vues", "tours"} pour les thèmes donnés (objets Tag), avec le même périmètre que le lancement
    d'un quiz de thème (quiz.services._items_eligibles) : les questions rangées sous ce tag, sinon, à défaut, celles de son
    savoir officiel. `subject` restreint à une matière, comme le lancement depuis la page d'une matière. Un thème sans
    question n'a pas d'entrée.
    """
    items = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus)
    if subject is not None:
        items = items.filter(subject=subject)
    par_tag, par_savoir = {}, {}
    for item_id, tag_id, savoir_id in items.values_list("id", "theme_id", "theme__savoir_officiel_id").distinct():
        par_tag.setdefault(tag_id, set()).add(item_id)
        if savoir_id is not None:
            par_savoir.setdefault(savoir_id, set()).add(item_id)

    reponses = _reponses_chronologiques(profil, cursus)
    progression = {}
    for theme in themes:
        ensemble = par_tag.get(theme.id) or par_savoir.get(theme.savoir_officiel_id) or set()
        if not ensemble:
            continue
        vues, tours = etat_du_tour(ensemble, reponses)
        progression[theme.id] = {"total": len(ensemble), "vues": vues, "tours": tours}
    return progression
