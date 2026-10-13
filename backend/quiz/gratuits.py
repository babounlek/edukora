"""
Quels quiz gratuits MONTRER pour un cursus : un seul thème par matière.

CompetenceItem.est_vitrine se pose sur l'ITEM, mais un item appartient souvent à plusieurs cursus
(CompetenceItem.cursus est M2M) : un thème coché pour la Terminale C devient gratuit aussi en D, en E
et en Probatoire. Sans tri, la liste d'un cursus empilait donc 5 à 7 thèmes de Maths (ou 5 d'Anglais)
alors que le BEPC en montrait un par matière. Ce module ne change pas ce qui est jouable - un thème
entièrement gratuit se joue toujours - il choisit ce qu'on PROPOSE : pour chaque (cursus, matière), le
thème gratuit le plus souvent tombé aux épreuves officielles du cursus.

Un thème est gratuit pour un cursus quand TOUS ses items publiés dans ce cursus sont vitrine (le même
critère que quiz.services.perimetre_est_vitrine, appliqué en deux requêtes groupées).
"""
from django.db.models import Count

from catalog.models import Lesson, StatutContenu

from .models import CompetenceItem


def themes_gratuits_par_matiere(cursus_ids):
    """
    Un thème gratuit par (cursus, matière) : [{"cursus", "subject", "theme", "nb_questions"}, ...].
    Départage par fréquence aux épreuves officielles du cursus, puis par nombre de questions, puis
    par id du thème - jamais un ordre qui dépende du SGBD.
    """
    base = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus__in=cursus_ids)
    cle = ("cursus", "subject", "theme")
    gratuits = {
        (r["cursus"], r["subject"], r["theme"]): r["n"]
        for r in base.filter(est_vitrine=True).values(*cle).annotate(n=Count("id", distinct=True)).order_by()
    }
    if not gratuits:
        return []
    totaux = {
        (r["cursus"], r["subject"], r["theme"]): r["n"]
        for r in base.values(*cle).annotate(n=Count("id", distinct=True)).order_by()
        if (r["cursus"], r["subject"], r["theme"]) in gratuits
    }
    complets = [c for c, n in gratuits.items() if totaux.get(c) == n]

    # Fréquence : nombre d'épreuves du cursus où le thème est tombé. Une seule requête pour tous.
    themes = {t for _, _, t in complets}
    frequence = {
        (r["cursus"], r["exercises__questions__themes"]): r["n"]
        for r in Lesson.objects.filter(
            statut=StatutContenu.VALIDE, cursus__in={c for c, _, _ in complets},
            exercises__questions__themes__in=themes,
        ).values("cursus", "exercises__questions__themes").annotate(n=Count("id", distinct=True)).order_by()
    }

    meilleur = {}
    for c, s, t in complets:
        rang = (frequence.get((c, t), 0), gratuits[(c, s, t)], t)
        if (c, s) not in meilleur or rang > meilleur[(c, s)][0]:
            meilleur[(c, s)] = (rang, t)
    return [
        {"cursus": c, "subject": s, "theme": t, "nb_questions": gratuits[(c, s, t)]}
        for (c, s), (_, t) in sorted(meilleur.items())
    ]
