"""
Quiz chronométrés, au choix de l'élève.

Le chrono est un OUTIL D'ENTRAÎNEMENT À L'EXAMEN, pas une note :
- la durée est globale (une échéance pour toute la session), jamais par question ;
- elle est figée à la création de la session (nombre de questions, majoration choisie comprise) ;
- le SERVEUR en est la source de vérité : l'échéance est `started_at + duree_limite_secondes`,
  le compte à rebours du navigateur n'est qu'un affichage. Fermer l'onglet ne l'arrête pas ;
- elle se termine en douceur : à l'échéance, les réponses déjà données sont gardées et l'élève
  rend sa copie, rien n'est effacé ni jugé de force (voir quiz.views.answer_question : seule une
  NOUVELLE réponse après l'échéance est refusée) ;
- une session chronométrée est NEUTRE pour la progression, comme un rejeu : ni XP, ni palier de
  révision, absente de la maîtrise (voir `QuizSession.chrono_actif`). Une erreur faite faute de temps
  ne dit rien du niveau ; les requêtes de maîtrise l'excluent comme elles excluent les rejeux.
"""

import math
from datetime import timedelta

from django.db.models import Count, Max
from django.utils import timezone

from catalog.models import TypeReponse

from . import instantane
from .models import QuizSession

# Temps de base par question : large exprès, un chrono trop serré angoisse sans rien apprendre. Un
# QCM se lit et se coche ; une question ouverte demande de chercher, calculer, rédiger au brouillon.
SECONDES_PAR_QCM = 60
SECONDES_PAR_QUESTION_OUVERTE = 150

# Majoration au choix (élèves dys, connexion lente, lecture dans une langue seconde). 0 = temps normal.
TEMPS_ADDITIONNEL_POSSIBLES = (0, 25, 50, 100)

# Marge d'une réponse partie juste avant l'échéance et arrivée juste après (réseau lent) : la refuser
# ferait perdre à l'élève une réponse qu'il a bien donnée dans les temps.
TOLERANCE_RESEAU_SECONDES = 8


def duree_de_base(quiz_questions):
    """Secondes allouées sans majoration, selon le type de chaque question."""
    total = 0
    for quiz_question in quiz_questions:
        type_reponse = instantane.type_et_cle(quiz_question)[0]
        total += SECONDES_PAR_QCM if type_reponse == TypeReponse.QCM else SECONDES_PAR_QUESTION_OUVERTE
    return total


def duree_limite(quiz_questions, temps_additionnel_pct=0):
    """Durée totale en secondes, majoration comprise - arrondie au-dessus."""
    return math.ceil(duree_de_base(quiz_questions) * (100 + temps_additionnel_pct) / 100)


def activer(session, temps_additionnel_pct=0):
    """Pose le chrono sur une session fraîchement créée, questions déjà créées. À appeler avant tout
    affichage au client : la durée est figée ici et ne change plus."""
    session.chrono_actif = True
    session.temps_additionnel_pct = temps_additionnel_pct
    session.duree_limite_secondes = duree_limite(session.quiz_questions.all(), temps_additionnel_pct)
    session.save(update_fields=["chrono_actif", "temps_additionnel_pct", "duree_limite_secondes"])


def echeance(session):
    """Instant limite, ou None si la session n'est pas chronométrée."""
    if not session.chrono_actif or not session.duree_limite_secondes:
        return None
    return session.started_at + timedelta(seconds=session.duree_limite_secondes)


def est_ecoule(session, maintenant=None, tolerance=0):
    """Vrai si l'échéance est passée (plus `tolerance` secondes). Faux sans chrono."""
    limite = echeance(session)
    if limite is None:
        return False
    return (maintenant or timezone.now()) > limite + timedelta(seconds=tolerance)


def payload(session):
    """Ce que le client affiche : lui donner l'échéance absolue et l'heure du serveur lui évite de se
    fier à son horloge (voir maintenantServeur côté frontend)."""
    limite = echeance(session)
    return {
        "chrono_actif": session.chrono_actif,
        "duree_limite_secondes": session.duree_limite_secondes if session.chrono_actif else None,
        "temps_additionnel_pct": session.temps_additionnel_pct if session.chrono_actif else 0,
        "echeance": limite,
        "chrono_ecoule": est_ecoule(session),
    }


def _bilan_temps(session):
    """(temps utilisé, toutes les questions répondues ?) d'une session chronométrée terminée. Si tout est
    répondu, le temps va au dernier clic de réponse (rendre la copie dix minutes plus tard n'allonge pas le
    temps mis) ; sinon à la clôture. Plafonné à l'allocation : une copie rendue longtemps après l'échéance
    n'a pas « utilisé » plus que ce qu'on lui a laissé."""
    agregat = session.quiz_questions.aggregate(
        total=Count("id", distinct=True), repondues=Count("answer", distinct=True), derniere=Max("answer__answered_at"),
    )
    tout_repondu = agregat["total"] > 0 and agregat["repondues"] == agregat["total"] and agregat["derniere"] is not None
    fin = agregat["derniere"] if tout_repondu else session.completed_at
    ecoule = max((fin - session.started_at).total_seconds(), 0)
    plafond = session.duree_limite_secondes or ecoule
    return int(min(ecoule, plafond)), tout_repondu


def temps_utilise_secondes(session):
    """Temps passé sur une session chronométrée terminée. None si non terminée ou sans chrono."""
    if not session.chrono_actif or not session.completed_at:
        return None
    return _bilan_temps(session)[0]


# Combien de tentatives passées on compare pour le record : au-delà, le chiffre n'a plus de sens utile.
RECORD_TENTATIVES_MAX = 50


def record(session):
    """
    Record personnel de temps sur le même périmètre (même cursus, matière, thème et nombre de questions),
    parmi les sessions chronométrées FINIES avec toutes les questions répondues - une copie rendue à moitié
    vide n'est pas un temps à battre. Renvoie {"record_secondes", "nouveau_record"} ; record_secondes est None
    tant qu'aucune session éligible n'existe, y compris celle-ci. Jamais un classement entre élèves.
    """
    total = session.quiz_questions.count()
    candidates = QuizSession.objects.filter(
        profil=session.profil, cursus_id=session.cursus_id, subject_id=session.subject_id,
        theme_id=session.theme_id, chrono_actif=True, completed_at__isnull=False,
    ).order_by("-completed_at", "-pk")[:RECORD_TENTATIVES_MAX]
    temps_de_la_session = None
    autres = []
    for autre in candidates:
        if autre.quiz_questions.count() != total:
            continue
        secondes, tout_repondu = _bilan_temps(autre)
        if not tout_repondu:
            continue
        if autre.pk == session.pk:
            temps_de_la_session = secondes
        else:
            autres.append(secondes)
    meilleur_avant = min(autres) if autres else None
    tous = autres + ([temps_de_la_session] if temps_de_la_session is not None else [])
    return {
        "record_secondes": min(tous) if tous else None,
        # Un premier temps n'est pas un record « battu » : il faut avoir quelque chose à battre.
        "nouveau_record": temps_de_la_session is not None and meilleur_avant is not None and temps_de_la_session < meilleur_avant,
    }
