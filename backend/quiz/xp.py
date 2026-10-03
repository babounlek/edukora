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
from django.utils import timezone

from catalog.models import TypeReponse

from .models import GainXP, JourXP, ResultatDeclare, RevisionSchedule, SourceXP

logger = logging.getLogger(__name__)

OBJECTIFS_POSSIBLES = (10, 20, 30)
OBJECTIF_DEFAUT = 20

XP_QCM_JUSTE = 10
XP_OUVERTE = {ResultatDeclare.REUSSI: 5, ResultatDeclare.PARTIEL: 2}
BONUS_REVISION = 5
XP_SEANCE = 10


def points_de_base(answer):
    """Points d'une réponse avant bonus : QCM juste -> XP_QCM_JUSTE ; question ouverte
    selon ce que l'élève a déclaré ; 0 pour tout le reste."""
    if answer.quiz_question.contenu.type_reponse == TypeReponse.QCM:
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


def etat_du_jour(profil, jour=None):
    """Où en est le profil aujourd'hui : XP gagnée, objectif en vigueur, atteint ou non."""
    jour = jour or timezone.localdate()
    ligne = JourXP.objects.filter(profil=profil, jour=jour).first()
    return {
        "xp": ligne.xp if ligne else 0,
        "objectif": ligne.objectif if ligne else profil.objectif_xp_quotidien,
        "atteint": bool(ligne and ligne.atteint),
        "objectifs_possibles": list(OBJECTIFS_POSSIBLES),
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
