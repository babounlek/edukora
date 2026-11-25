"""
Un thème a-t-il de quoi remplir un lien « Quiz » ou « Cours » ? Un lien qui lance un quiz sans question (404) ou ouvre
une liste vide est pire que pas de lien : les écrans ne le proposent que si la réponse est oui. Partagé par les bilans
d'examen blanc (inédites et annales) et par « Mes erreurs ».
"""

from catalog.models import Cours, StatutContenu, langue_examen
from quiz.models import CompetenceItem


def themes_avec_quiz(theme_ids, cursus):
    return set(
        CompetenceItem.objects.filter(theme_id__in=theme_ids, cursus=cursus, statut=StatutContenu.VALIDE)
        .values_list("theme_id", flat=True)
    )


def themes_avec_cours(theme_ids, cursus):
    """Les thèmes qu'au moins un cours publié porte, dans la langue de l'examen (la liste des cours filtre par thème)."""
    cours = Cours.objects.visibles().filter(tags__id__in=theme_ids)
    if cursus is not None and cursus.examen:
        cours = cours.filter(subject__langue=langue_examen(cursus.examen))
    return set(cours.values_list("tags__id", flat=True)) & set(theme_ids)
