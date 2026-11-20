"""
Points d'XP et objectif du jour.

L'XP récompense la MAÎTRISE, jamais le volume : sinon les élèves enchaîneraient des quiz
faciles pour faire monter un compteur, et le compteur cesserait de dire quoi que ce soit de
leur préparation. Donc :

- une bonne réponse du PREMIER essai rapporte (XP_QCM_JUSTE pour un QCM, moins pour une
  question ouverte, dont le résultat est auto-déclaré donc triable) ; une réponse fausse ne
  rapporte rien, et ne retire rien ;
- un thème DÛ en révision (voir RevisionSchedule) rapporte un bonus de plus : revenir sur ce
  qu'on avait raté est ce qu'on veut le plus encourager ;
- finir la séance du jour rapporte un bonus, une fois par jour (pas par séance supplémentaire) ;
- une même question ne rapporte qu'une fois par jour, et rejouer la requête ne crédite rien.

L'objectif du jour (10, 20 ou 30 points, choisi par l'élève) est atteint quand le total du jour
le rejoint. Un jour atteint compte pour la série comme une séance terminée (voir quiz.serie) :
un élève très actif en quiz libre ne perd pas sa série parce qu'il n'a pas suivi le plan.
"""

import logging

from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone


from . import instantane
from .models import GainXP, JourXP, ResultatDeclare, RevisionSchedule, SourceXP

logger = logging.getLogger(__name__)

OBJECTIFS_POSSIBLES = (10, 20, 30)
OBJECTIF_DEFAUT = 20

XP_QCM_JUSTE = 10
XP_OUVERTE = {ResultatDeclare.REUSSI: 5, ResultatDeclare.PARTIEL: 2}
BONUS_REVISION = 5
XP_SEANCE = 10

# Hors quiz : lire et faire comptent aussi, un peu - une section de cours déclarée comprise, un exercice déclaré fait.
# Ces deux gains sont AUTO-DÉCLARÉS (comme une question ouverte) : ils restent petits, ne rapportent qu'une fois par objet
# pour toujours (décocher puis recocher ne rapporte rien) et sont plafonnés par jour - le plafond empêche de gonfler
# un compteur en cochant tout un cours d'un coup.
XP_COURS_SECTION = 2
XP_EXERCICE = 5
XP_COURS_LU = 3  # un cours lu jusqu'au bout (voir access.views.cours_lu) : le geste de lire, un peu moins que celui de comprendre
PLAFOND_ACTIVITE_JOUR = 15
# Une carte de révision revue À SON ÉCHÉANCE (nouvelle, ou due : voir quiz.cartes.est_attendue) : le geste de revenir, que
# l'élève ait su ou non - récompenser « Je savais » seul pousserait à le toucher sans réfléchir. Auto-déclaré comme les deux
# gains ci-dessus, donc petit et dans le MÊME plafond du jour : un paquet de vingt cartes ne fait pas l'objectif à lui seul.
# Une fois par carte et par jour ; une revue anticipée ne rapporte rien (elle ne change pas non plus l'échéance).
XP_CARTE = 1
SOURCES_ACTIVITE = (SourceXP.COURS, SourceXP.EXERCICE, SourceXP.CARTE)
# Un examen blanc passé en conditions réelles (chrono ou papier) puis rendu : le plus exigeant des efforts, jusqu'ici le seul
# qui ne rapportait rien. Vaut l'objectif par défaut : le jour compte pour la série (voir quiz.serie). Une fois par jour,
# jamais pour un entraînement libre ni une copie rendue vide ; hors plafond d'activité, qui ne vise que les cases cochées.
XP_SIMULATION = 20

# Seuils d'XP cumulée des niveaux (rang 1 à 15). Les NOMS sont côté interface, par langue : le serveur ne dit que le rang.
# Cinq rangs jusqu'au 2026-11-14 : le dernier tombait au bout de quelques semaines à l'objectif par défaut, et plus rien
# ne bougeait jusqu'à l'examen (audit produit R12). Les cinq premiers seuils sont inchangés : personne ne perd son rang.
NIVEAUX = (0, 60, 200, 500, 1000, 1600, 2400, 3400, 4600, 6000, 7600, 9400, 11400, 13600, 16000)


def points_de_base(answer):
    """Points d'une réponse avant bonus : QCM juste -> XP_QCM_JUSTE ; question ouverte
    selon ce que l'élève a déclaré ; 0 pour tout le reste."""
    if instantane.est_qcm(answer.quiz_question):
        return XP_QCM_JUSTE if answer.est_correcte else 0
    return XP_OUVERTE.get(answer.resultat_declare, 0)


def theme_du_en_revision(profil, cursus, theme):
    """À appeler AVANT enregistrer_resultat_pour_revision : une réponse fausse (ré)ouvre le
    suivi du thème pour demain, et une bonne avance son échéance - dans les deux cas le thème
    cesse d'être « dû » et le bonus serait perdu."""
    return RevisionSchedule.objects.filter(
        profil=profil, cursus=cursus, theme=theme, due_at__lte=timezone.localdate(),
    ).exists()


def _tracer_objectif_atteint(profil, jour_xp):
    # Même règle que les autres évènements serveur : jamais au prix de la requête en cours.
    try:
        from analytics.models import AnalyticsEvent, EventName

        AnalyticsEvent.objects.create(
            name=EventName.OBJECTIF_XP_ATTEINT, user=profil.compte,
            properties={"profil_id": profil.id, "objectif": jour_xp.objectif, "xp": jour_xp.xp},
        )
    except Exception:  # noqa: BLE001
        logger.exception("Évènement objectif_xp_atteint non enregistré")


def _crediter(profil, jour, source, points, **champs):
    """Écrit le gain et met à jour le total du jour. None si une contrainte d'unicité dit que
    ce gain existe déjà (deux requêtes simultanées pour la même réponse)."""
    try:
        with transaction.atomic():
            gain = GainXP.objects.create(profil=profil, jour=jour, source=source, points=points, **champs)
            jour_xp, _ = JourXP.objects.select_for_update().get_or_create(
                profil=profil, jour=jour, defaults={"objectif": profil.objectif_xp_quotidien},
            )
            jour_xp.xp += points
            vient_d_atteindre = not jour_xp.atteint and jour_xp.xp >= jour_xp.objectif
            if vient_d_atteindre:
                jour_xp.atteint = True
            jour_xp.save(update_fields=["xp", "atteint"])
    except IntegrityError:
        return None
    if vient_d_atteindre:
        _tracer_objectif_atteint(profil, jour_xp)
    return gain


def crediter_reponse(profil, quiz_question, answer, *, premiere_reponse, bonus_revision):
    """
    Crédite la réponse qui vient d'être donnée. `premiere_reponse` : la réponse vient d'être
    CRÉÉE (jamais une mise à jour de la même question). Seuls les items de compétence
    rapportent : l'historique d'avant la bascule (catalog.Question) n'a pas de thème unique.
    """
    if not premiere_reponse or not quiz_question.competence_item_id:
        return None
    base = points_de_base(answer)
    if base == 0:
        return None
    jour = timezone.localdate()
    # Plafond : un item qui revient dans deux quiz le même jour ne rapporte qu'une fois.
    if GainXP.objects.filter(profil=profil, jour=jour, competence_item_id=quiz_question.competence_item_id).exists():
        return None
    bonus = bonus_revision and answer.est_correcte
    return _crediter(
        profil, jour, SourceXP.REPONSE, base + (BONUS_REVISION if bonus else 0),
        bonus_revision=bonus, quiz_answer=answer, competence_item_id=quiz_question.competence_item_id,
    )


def crediter_seance(seance):
    """Bonus de la séance du jour terminée - un seul par jour, même si l'élève enchaîne des
    séances supplémentaires (voir quiz.services.seance_supplementaire)."""
    jour = timezone.localdate()
    profil = seance.profil
    if GainXP.objects.filter(profil=profil, jour=jour, source=SourceXP.SEANCE).exists():
        return None
    return _crediter(profil, jour, SourceXP.SEANCE, XP_SEANCE, seance=seance)


def crediter_activite(profil, source, reference, points):
    """
    Crédite une activité hors quiz (SOURCES_ACTIVITE : cours, exercice, carte) : None si cet objet a déjà rapporté, si le plafond du jour
    est atteint ou si une contrainte d'unicité dit que le gain existe. Le plafond ne rogne qu'à son bord : à 3 points de
    marge, un gain de 5 rapporte 3.
    """
    if not reference or GainXP.objects.filter(profil=profil, source=source, reference=reference).exists():
        return None
    jour = timezone.localdate()
    deja = (
        GainXP.objects.filter(profil=profil, jour=jour, source__in=SOURCES_ACTIVITE)
        .aggregate(total=Sum("points"))["total"] or 0
    )
    points = min(points, PLAFOND_ACTIVITE_JOUR - deja)
    if points <= 0:
        return None
    return _crediter(profil, jour, source, points, reference=reference)


def crediter_carte(profil, cours_id, cle):
    """
    Crédite la revue d'une carte de révision. L'appelant garantit que la carte était attendue (voir quiz.cartes.est_attendue).
    Le jour est dans la référence : la même carte rapporte de nouveau à sa prochaine échéance, jamais deux fois le même jour
    (ratée puis revue dans la foulée). None si elle a déjà rapporté aujourd'hui ou si le plafond d'activité est atteint.
    """
    jour = timezone.localdate()
    return crediter_activite(profil, SourceXP.CARTE, f"carte:{cours_id}:{cle}:{jour.isoformat()}", XP_CARTE)


def crediter_simulation(profil, simulation_id):
    """
    Crédite un examen blanc terminé (voir simulations.views._complete) : None s'il a déjà rapporté, ou si une simulation a
    déjà rapporté aujourd'hui (rendre dix copies vides à la suite ne doit pas gonfler un compteur).
    """
    reference = f"simulation:{simulation_id}"
    jour = timezone.localdate()
    if GainXP.objects.filter(profil=profil, source=SourceXP.SIMULATION).filter(
        Q(reference=reference) | Q(jour=jour),
    ).exists():
        return None
    return _crediter(profil, jour, SourceXP.SIMULATION, XP_SIMULATION, reference=reference)


def crediter_inedite(profil, tentative_id):
    """
    Crédite une copie d'épreuve inédite ou de mini-inédite (défi de la semaine compris) rendue en conditions réelles ou sur
    papier (voir inedit.views._complete) : une copie rendue sans le moindre mal ne rapportait rien, alors qu'un examen blanc
    sur annale rapporte XP_SIMULATION (passe élève du 2026-11-17). Même garde que crediter_simulation : une seule copie
    par jour et par copie, pour que rendre dix copies à la suite ne gonfle pas le compteur. Compte pour la série comme tout gain.
    """
    reference = f"inedite:{tentative_id}"
    jour = timezone.localdate()
    if GainXP.objects.filter(profil=profil, source=SourceXP.SIMULATION, reference__startswith="inedite:").filter(
        Q(reference=reference) | Q(jour=jour),
    ).exists():
        return None
    return _crediter(profil, jour, SourceXP.SIMULATION, XP_SIMULATION, reference=reference)


def gain_inedite(profil, tentative_id):
    """Les points que cette copie a rapportés (0 si aucun) : de quoi les annoncer dans le résultat."""
    gain = GainXP.objects.filter(profil=profil, source=SourceXP.SIMULATION, reference=f"inedite:{tentative_id}").first()
    return gain.points if gain else 0


def niveau_du_profil(profil):
    """
    Le niveau atteint : rang (1 à len(NIVEAUX)), XP cumulée depuis le début, seuil du rang et du suivant (None au sommet).
    L'XP cumulée est la somme du registre des gains (GainXP) : aucune ligne n'est jamais retirée, donc un niveau ne se perd pas.
    """
    total = GainXP.objects.filter(profil=profil).aggregate(total=Sum("points"))["total"] or 0
    rang = max(i for i, seuil in enumerate(NIVEAUX, start=1) if total >= seuil)
    return {
        "rang": rang,
        "xp_total": total,
        "seuil": NIVEAUX[rang - 1],
        "seuil_suivant": NIVEAUX[rang] if rang < len(NIVEAUX) else None,
    }


def etat_du_jour(profil, jour=None):
    """Où en est le profil aujourd'hui : XP gagnée, objectif en vigueur, atteint ou non, et son niveau."""
    jour = jour or timezone.localdate()
    ligne = JourXP.objects.filter(profil=profil, jour=jour).first()
    return {
        "xp": ligne.xp if ligne else 0,
        "objectif": ligne.objectif if ligne else profil.objectif_xp_quotidien,
        "atteint": bool(ligne and ligne.atteint),
        "objectifs_possibles": list(OBJECTIFS_POSSIBLES),
        "niveau": niveau_du_profil(profil),
    }


def jours_atteints(profil):
    """Jours civils où l'objectif d'XP a été atteint - lus par quiz.serie."""
    return set(JourXP.objects.filter(profil=profil, atteint=True).values_list("jour", flat=True))


def definir_objectif(profil, valeur):
    """Change le rythme du profil. ValueError pour une valeur hors OBJECTIFS_POSSIBLES.

    L'objectif d'AUJOURD'HUI suit le changement (l'élève qui choisit 30 le matin vise 30 ce
    soir) ; les jours passés gardent le leur. Baisser l'objectif peut faire passer le jour
    en « atteint » ; le monter ne retire jamais un jour déjà atteint."""
    if valeur not in OBJECTIFS_POSSIBLES:
        raise ValueError(f"objectif invalide : {valeur!r}. Attendu {OBJECTIFS_POSSIBLES}.")
    profil.objectif_xp_quotidien = valeur
    profil.save(update_fields=["objectif_xp_quotidien"])
    ligne = JourXP.objects.filter(profil=profil, jour=timezone.localdate()).first()
    if ligne:
        ligne.objectif = valeur
        ligne.atteint = ligne.atteint or ligne.xp >= valeur
        ligne.save(update_fields=["objectif", "atteint"])
    return etat_du_jour(profil)


def bilan_session(session):
    """XP gagnée grâce à cette session : réponses, et bonus de la séance qu'elle a clôturée."""
    gains = GainXP.objects.filter(profil=session.profil).filter(
        quiz_answer__quiz_question__session=session,
    )
    reponses = sum(gains.values_list("points", flat=True))
    seance = sum(
        GainXP.objects.filter(profil=session.profil, seance__in=session.seances.all()).values_list("points", flat=True),
    )
    return {"reponses": reponses, "seance": seance, "total": reponses + seance}
