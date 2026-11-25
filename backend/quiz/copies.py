"""
Ce que les copies d'examen blanc (épreuves inédites et annales) disent de l'élève, pour les écrans qui parlent de sa
progression. Avant ce module, une copie ne nourrissait que la file de révision : un thème réussi à l'examen restait
« jamais travaillé » et le bilan envoyé au parent ne donnait aucune note (audit du 2026-11-25).

Deux lectures :
- les QCM corrigés par la machine, qui comptent dans la maîtrise (voir `reponses_qcm_de_copies`) ;
- les copies rendues sur une période, avec leur note (voir `copies_rendues`).

Ce qui ne compte PAS dans la maîtrise : les questions ouvertes, notées par l'élève lui-même. Leur donner un poids est une
décision de produit qui n'est pas prise.
"""

from django.db.models import F

from catalog.models import TypeReponse
from inedit import notation
from inedit.models import TentativeInedite, TentativeReponse
from simulations import choix
from simulations.cadre import charger_exercices
from simulations.models import SimulationEpreuve, SimulationReponse


def reponses_qcm_de_copies(profil, cursus=None):
    """
    Les QCM répondus dans une copie rendue en conditions réelles : une ligne par réponse, avec le thème qu'elle prouve.

    Mêmes précautions que pour les quiz :
    - conditions réelles à l'écran seulement : en entraînement libre le corrigé est visible, et sur papier les lettres se
      saisissent après coup ;
    - une question à UN seul thème : avec plusieurs, on ne sait pas lequel la réponse prouve.
    """
    inedites = TentativeReponse.objects.filter(
        tentative__profil=profil, tentative__submitted_at__isnull=False,
        tentative__exam_mode_started_at__isnull=False, tentative__mode_papier=False,
        question__type_reponse=TypeReponse.QCM, answered_at__lte=F("tentative__submitted_at"),
    ).exclude(reponse_choisie="")
    annales = SimulationReponse.objects.filter(
        simulation__profil=profil, simulation__submitted_at__isnull=False,
        simulation__exam_mode_started_at__isnull=False, simulation__mode_papier=False,
        sous_question__type_reponse=TypeReponse.QCM,
    ).exclude(reponse_choisie="")
    if cursus is not None:
        inedites = inedites.filter(tentative__epreuve__cursus=cursus)
        annales = annales.filter(simulation__lesson__cursus=cursus)

    lignes = []
    for reponse in inedites.select_related("question", "tentative__epreuve__subject").prefetch_related("question__themes__savoir_officiel"):
        correcte = reponse.reponse_choisie.strip().lower() == (reponse.question.reponse_correcte or "").strip().lower()
        _ajouter(lignes, reponse.question.themes.all(), reponse.tentative.epreuve.subject, correcte)
    for reponse in annales.select_related("sous_question", "simulation__lesson__subject").prefetch_related("sous_question__themes"):
        correcte = reponse.reponse_choisie.strip().lower() == (reponse.sous_question.reponse_correcte or "").strip().lower()
        _ajouter(lignes, reponse.sous_question.themes.all(), reponse.simulation.lesson.subject, correcte)
    return lignes


def _ajouter(lignes, themes, subject, correcte):
    themes = list(themes)
    if len(themes) != 1:
        return
    theme = themes[0]
    lignes.append({
        "theme_id": theme.pk, "theme": theme.name, "savoir_id": theme.savoir_officiel_id,
        "subject_id": subject.pk, "subject_label": subject.label, "correcte": correcte,
    })


def _fiche_de_copie(copie, bilan, *, titre, subject, entiere):
    return {
        "titre": titre,
        "subject_id": subject.pk,
        "subject_label": subject.label,
        "rendue_at": copie.submitted_at,
        "conditions_reelles": copie.exam_mode_started_at is not None,
        # Une mini-inédite tient en quelques points : sa note ne se compare pas à celle d'une épreuve entière.
        "entiere": entiere,
        "note": notation.en_nombre(copie.note_obtenue),
        "bareme": notation.en_nombre(copie.bareme_snapshot),
        # Une copie dont des questions restent à noter n'a qu'une note provisoire.
        "definitive": bilan["questions_a_noter"] == 0,
    }


def copies_rendues(profil, cursus, jusqu_a, limite=20):
    """
    Les dernières copies rendues avant `jusqu_a` sur ce cursus, la plus récente d'abord, chacune avec sa note. Une copie
    sans aucune question traitée est écartée : sa note de zéro ne dit rien.
    """
    fiches = []
    inedites = (
        TentativeInedite.objects.filter(
            profil=profil, epreuve__cursus=cursus, submitted_at__isnull=False, submitted_at__lte=jusqu_a,
            note_obtenue__isnull=False,
        )
        .select_related("epreuve__subject").order_by("-submitted_at")[:limite]
    )
    for tentative in inedites:
        bilan = notation.calculer(tentative, tentative.epreuve.exercices_ordonnes("questions__themes"))
        if bilan["questions_traitees"]:
            fiches.append(_fiche_de_copie(
                tentative, bilan, titre=tentative.epreuve.titre, subject=tentative.epreuve.subject,
                entiere=not tentative.epreuve.est_mini,
            ))
    annales = (
        SimulationEpreuve.objects.filter(
            profil=profil, lesson__cursus=cursus, submitted_at__isnull=False, submitted_at__lte=jusqu_a,
            note_obtenue__isnull=False,
        )
        .select_related("lesson__subject").order_by("-submitted_at")[:limite]
    )
    for simulation in annales:
        bilan = choix.calculer(simulation, charger_exercices(simulation.lesson))
        if bilan["questions_traitees"]:
            fiches.append(_fiche_de_copie(
                simulation, bilan, titre=simulation.lesson.title, subject=simulation.lesson.subject, entiere=True,
            ))
    return sorted(fiches, key=lambda f: f["rendue_at"], reverse=True)[:limite]
