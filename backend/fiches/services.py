import random

from catalog.models import StatutContenu
from quiz.models import CompetenceItem

from .models import FicheGeneree, FicheItem


def themes_eligibles(cursus, subject):
    """
    Pour chaque Tag couvert par au moins un CompetenceItem VALIDE sur ce (cursus,
    subject), le nombre d'items disponibles - total et par difficulté. Alimente
    l'endpoint d'éligibilité (voir fiches.views) : le formulaire côté frontend ne doit
    jamais laisser un répétiteur cocher un thème vide, ni demander plus de questions que
    le pool n'en contient - ce garde-fou est construit ici, pas deviné côté client.
    """
    items = (
        CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus, subject=subject)
        .select_related("theme")
    )
    par_theme = {}
    for item in items:
        entry = par_theme.setdefault(item.theme_id, {
            "theme_id": item.theme_id, "theme": item.theme.name, "total": 0, "par_difficulte": {},
        })
        entry["total"] += 1
        entry["par_difficulte"][item.difficulte_estimee] = entry["par_difficulte"].get(item.difficulte_estimee, 0) + 1
    return sorted(par_theme.values(), key=lambda e: e["theme"])


def generer_fiche(*, user, cursus, subject, themes, difficulte, n, titre):
    """
    Sélectionne jusqu'à n CompetenceItem (répartis entre les thèmes choisis) et crée la
    FicheGeneree + ses FicheItem. Lève ValueError si le pool est vide pour ces critères -
    même contrat que quiz.services.generer_session, à la vue de traduire en réponse HTTP
    appropriée. Tirage aléatoire simple, sans pondération par échec de l'élève
    (contrairement à quiz.services._selection_ponderee_par_theme) : le répétiteur a déjà
    choisi lui-même les compétences à travailler, rien à corriger ici.
    """
    qs = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus, subject=subject, theme__in=themes)
    if difficulte:
        qs = qs.filter(difficulte_estimee=difficulte)
    items = list(qs)
    if not items:
        raise ValueError("Aucune question disponible pour ces critères.")

    random.shuffle(items)
    selection = items[:n]

    fiche = FicheGeneree.objects.create(
        owner=user, cursus=cursus, subject=subject, titre=titre, difficulte=difficulte, nombre_questions=len(selection),
    )
    fiche.themes.set(themes)
    FicheItem.objects.bulk_create([
        FicheItem(fiche=fiche, competence_item=item, ordre=ordre)
        for ordre, item in enumerate(selection, start=1)
    ])
    return fiche
