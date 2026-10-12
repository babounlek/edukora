"""
Calcul des cours qui « tombent souvent » à l'examen (table catalog.FrequenceCours).

La fréquence est celle du THÈME (voir quiz.services.groupes_par_frequence, partagée avec le
Parcours par fréquence) : un cours n'a pas de score propre, il hérite de celui du thème auquel ses
tags le rattachent. Même règle d'étoile dorée que le parcours (frontend lib/frequenceOr) : le quart
supérieur des thèmes classés d'une matière, jamais sous PLANCHER_OR % des épreuves.

Un cours n'est retenu que s'il vient d'une épreuve du cursus (lignée RappelDeMethode -> Exercise ->
Lesson.cursus) ET que le parcours le propose pour un thème fréquent (cours_prioritaires_du_theme) :
jamais un cours « commun » sans source, ni tous les cours qui portent par hasard un tag du thème.
"""
from collections import defaultdict

from django.db import transaction
from django.db.models import Count

from quiz.services import (
    SUBJECTS_PARCOURS_PAR_FREQUENCE,
    _classee_par_theme_pour_cet_examen,
    cours_prioritaires_du_theme,
    groupes_par_frequence,
    plancher_occurrences,
)

from .models import Cours, FrequenceCours, Subject

PLANCHER_OR = 30


def seuil_or(frequences):
    """Miroir de seuilOr (frontend lib/frequenceOr.ts) : le quart supérieur, avec un plancher ;
    None s'il y a moins de quatre fréquences connues (rien n'est alors « fréquent »)."""
    valeurs = sorted((v for v in frequences if v is not None), reverse=True)
    if len(valeurs) < 4:
        return None
    rang = -(-len(valeurs) // 4)  # plafond de n / 4
    return max(valeurs[rang - 1], PLANCHER_OR)


def matieres_classees(cursus):
    return [
        subject for subject in Subject.objects.filter(country=cursus.country)
        if subject.code in SUBJECTS_PARCOURS_PAR_FREQUENCE or _classee_par_theme_pour_cet_examen(subject, cursus)
    ]


def lignes_pour_matiere(cursus, subject):
    """Les FrequenceCours (non enregistrées) d'une matière, ou [] si elle n'est pas classable."""
    contexte = groupes_par_frequence(cursus, subject)
    if contexte is None:
        return []
    mince, _lessons, nb_sessions, groupes, _tous = contexte
    if not groupes:
        return []

    plancher = plancher_occurrences(groupes, mince, nb_sessions)
    classes = [g for g in groupes.values() if g["nb_epreuves"] >= plancher]
    for g in classes:
        g["frequence_pct"] = round(100 * g["nb_epreuves"] / nb_sessions)
    seuil = seuil_or([g["frequence_pct"] for g in classes])
    if seuil is None:
        return []
    frequents = [g for g in classes if g["frequence_pct"] >= seuil]
    tag_ids_frequents = {tag_id for g in frequents for tag_id in g["tag_ids"]}

    # Mêmes candidats que le parcours (lignée vers une épreuve du cursus), puis le même choix par
    # thème : sans lui, tous les cours portant un tag d'un thème fréquent étaient retenus (40 % du
    # BEPC), et le badge ne distinguait plus rien.
    candidats = list(
        Cours.objects.visibles()
        .filter(subject=subject, tags__id__in=tag_ids_frequents, rappels_source__exercise__lesson__cursus=cursus)
        .annotate(nb_rappels=Count("rappels_source", distinct=True))
        .prefetch_related("tags")
        .only("id", "slug", "titre", "sous_theme")
        .distinct()
    )
    meilleur = {}  # cours_id -> groupe de plus forte fréquence parmi ceux qui le retiennent
    for g in frequents:
        du_theme = [c for c in candidats if g["tag_ids"] & {t.id for t in c.tags.all()}]
        for c in cours_prioritaires_du_theme(du_theme, g["nom"]):
            if c.id not in meilleur or g["nb_epreuves"] > meilleur[c.id]["nb_epreuves"]:
                meilleur[c.id] = g

    return [
        FrequenceCours(
            cursus=cursus, cours_id=cours_id, theme=g["nom"][:100],
            nb_epreuves=g["nb_epreuves"], nb_sessions=nb_sessions, frequence_pct=g["frequence_pct"],
        )
        for cours_id, g in meilleur.items()
    ]


def recalculer_cursus(cursus):
    """Remplace d'un bloc les lignes du cursus ; renvoie {matière: nombre de cours fréquents}."""
    lignes, par_matiere = [], defaultdict(int)
    for subject in matieres_classees(cursus):
        trouvees = lignes_pour_matiere(cursus, subject)
        lignes.extend(trouvees)
        if trouvees:
            par_matiere[subject.code] = len(trouvees)
    # Un cours porté par deux matières classées n'aurait qu'une ligne par (cursus, cours) : on garde la plus forte.
    par_cours = {}
    for ligne in lignes:
        courante = par_cours.get(ligne.cours_id)
        if courante is None or ligne.frequence_pct > courante.frequence_pct:
            par_cours[ligne.cours_id] = ligne
    with transaction.atomic():
        FrequenceCours.objects.filter(cursus=cursus).delete()
        FrequenceCours.objects.bulk_create(par_cours.values())
    return dict(par_matiere)
