"""
Notifications push du navigateur : le rappel du jour envoyé à l'HEURE où l'élève travaille
d'habitude, plutôt que dans une fenêtre fixe. Un message par élève et par jour, tous canaux
confondus (voir RelanceEnvoyee : si l'e-mail est déjà parti, le push ne part pas, et inversement).

Le ton est celui du reste de l'application : un fait et une action, jamais un reproche. Quand une
série de plusieurs jours est en jeu, on le dit, parce que c'est une information qui sert l'élève -
pas pour le culpabiliser.

Rien ne part sans clés VAPID (voir settings.VAPID_*) : sans elles, `push_configure()` est faux et
l'application n'affiche même pas l'interrupteur.
"""

import json
import logging
from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from quiz.models import JourXP, QuizAnswer, SeanceJournaliere, StatutSeance
from quiz.serie import serie_de_jours
from quiz.services import revisions_dues
from quiz.xp import etat_du_jour
from users.models import User

from .models import AbonnementPush, CanalRelance, RelanceEnvoyee, TypeRelance
from .services import _formule_examen, _prenom

logger = logging.getLogger("relances")

# Heure à laquelle on envoie quand on ne connaît pas encore les habitudes de l'élève - la même
# fin de journée scolaire que la fenêtre du rappel par e-mail.
HEURE_PAR_DEFAUT = 18
# Il faut au moins ce nombre de jours travaillés dans les 30 derniers pour parler d'habitude.
JOURS_MINIMUM_HABITUDE = 3
FENETRE_HABITUDE_JOURS = 30
# Un envoi raté à l'heure H est retenté à H+1 et H+2 (le tour tourne toutes les heures), puis
# abandonné pour la journée : un rappel à 23 h ne sert plus à rien.
RETARD_MAX_HEURES = 2
# En dessous, une série n'est pas encore une habitude qu'on a envie de défendre.
SERIE_MINIMUM_ANNONCEE = 3


def push_configure():
    return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY and settings.VAPID_CLAIM_EMAIL)


def heure_habituelle(profil, maintenant=None):
    """Heure locale (0-23) à laquelle ce profil travaille le plus souvent, d'après ses séances
    terminées et ses réponses de quiz des 30 derniers jours ; HEURE_PAR_DEFAUT sans assez
    d'historique. Une heure par JOUR travaillé (la dernière activité du jour) : un élève qui
    enchaîne quarante questions un soir ne pèse pas quarante fois."""
    maintenant = maintenant or timezone.now()
    debut = maintenant - timedelta(days=FENETRE_HABITUDE_JOURS)
    derniere_par_jour = {}

    def noter(quand):
        local = timezone.localtime(quand)
        jour = local.date()
        if jour not in derniere_par_jour or local > derniere_par_jour[jour]:
            derniere_par_jour[jour] = local

    for quand in SeanceJournaliere.objects.filter(
        profil=profil, statut=StatutSeance.TERMINEE, termine_at__gte=debut,
    ).values_list("termine_at", flat=True):
        noter(quand)
    for quand in QuizAnswer.objects.filter(
        quiz_question__session__profil=profil, answered_at__gte=debut,
    ).values_list("answered_at", flat=True):
        noter(quand)

    if len(derniere_par_jour) < JOURS_MINIMUM_HABITUDE:
        return HEURE_PAR_DEFAUT
    # L'heure la plus fréquente ; à égalité, la plus tardive (mieux vaut arriver un peu après
    # l'habitude qu'avant : un rappel trop tôt est un rappel de plus qu'on ignore).
    heures = Counter(local.hour for local in derniere_par_jour.values())
    return max(heures, key=lambda h: (heures[h], h))


def composer_push(user, maintenant=None):
    """{title, body, url, tag} du rappel du jour. Une série d'au moins SERIE_MINIMUM_ANNONCEE
    jours encore à prolonger est dite en tête ; sinon la séance, avec ce qui la rend urgente."""
    profil = user.profils.first()
    cursus = user.cursus_prepare
    serie = serie_de_jours(profil, timezone.localtime(maintenant).date() if maintenant else None)
    etat = etat_du_jour(profil)
    prenom = _prenom(user)
    pays = cursus.country.code.lower()

    if serie["jours"] >= SERIE_MINIMUM_ANNONCEE and not serie["actif_aujourdhui"]:
        title = f"Ta série de {serie['jours']} jours se prolonge ce soir"
        body = f"{etat['objectif']} XP suffisent, soit environ 25 minutes."
    else:
        title = f"{prenom}, ta séance du jour est prête" if prenom else "Ta séance du jour est prête"
        morceaux = []
        formule = _formule_examen(cursus)
        if formule:
            morceaux.append(formule)
        dues = revisions_dues(profil, cursus).count()
        if dues:
            morceaux.append(f"{dues} thème{'s' if dues > 1 else ''} à revoir aujourd'hui.")
        body = " ".join(morceaux) or "Environ 25 minutes, choisies pour toi."
    return {"title": title, "body": body, "url": f"/{pays}", "tag": "rappel-du-jour"}


def destinataires_push(maintenant=None):
    """Comptes à qui le rappel peut partir aujourd'hui : au moins un appareil abonné, abonnement
    payant actif, examen déclaré, rien d'envoyé aujourd'hui (aucun canal), et la journée de
    travail pas déjà faite (séance terminée ou objectif d'XP atteint)."""
    maintenant = maintenant or timezone.now()
    aujourdhui = timezone.localtime(maintenant).date()
    deja_fait = set(
        SeanceJournaliere.objects.filter(date=aujourdhui, statut=StatutSeance.TERMINEE)
        .values_list("profil__compte_id", flat=True),
    ) | set(JourXP.objects.filter(jour=aujourdhui, atteint=True).values_list("profil__compte_id", flat=True))
    deja_relance = RelanceEnvoyee.objects.filter(
        type=TypeRelance.RAPPEL_SEANCE, reference=aujourdhui.isoformat(),
    ).values("user_id")
    return (
        User.objects.filter(
            abonnements_push__isnull=False, cursus_prepare__isnull=False, cursus_prepare__country__actif=True,
            subscriptions__expires_at__gt=maintenant,
        )
        .exclude(pk__in=deja_fait)
        .exclude(pk__in=deja_relance)
        .select_related("cursus_prepare__country", "cursus_prepare__series")
        .distinct()
    )


def _webpush(abonnement, charge):
    """Un envoi vers un appareil. Isolé pour les tests, qui ne parlent à aucun service push."""
    from pywebpush import webpush

    webpush(
        subscription_info={"endpoint": abonnement.endpoint, "keys": {"p256dh": abonnement.p256dh, "auth": abonnement.auth}},
        data=json.dumps(charge),
        vapid_private_key=settings.VAPID_PRIVATE_KEY,
        vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}"},
        ttl=6 * 3600,
    )


def envoyer_a_l_appareil(abonnement, charge):
    """True si le message est parti. Un appareil que le service push dit disparu (404, 410) est
    oublié ; toute autre erreur est journalisée et l'abonnement conservé (panne passagère)."""
    from pywebpush import WebPushException

    try:
        _webpush(abonnement, charge)
    except WebPushException as exc:
        statut = getattr(getattr(exc, "response", None), "status_code", None)
        if statut in (404, 410):
            abonnement.delete()
        else:
            logger.warning("Push non envoyé à l'abonnement %s : %s", abonnement.pk, exc)
        return False
    except Exception:
        logger.exception("Push non envoyé à l'abonnement %s", abonnement.pk)
        return False
    AbonnementPush.objects.filter(pk=abonnement.pk).update(derniere_reussite_at=timezone.now())
    return True


def envoyer_rappels_push(maintenant=None, *, dry_run=False):
    """Envoie le rappel du jour aux élèves dont c'est l'heure. Renvoie le nombre d'élèves
    prévenus (un élève compte une fois, même avec plusieurs appareils)."""
    if not push_configure():
        return 0
    maintenant = maintenant or timezone.now()
    local = timezone.localtime(maintenant)
    reference = local.date().isoformat()
    envoyes = 0
    for user in destinataires_push(maintenant):
        heure = heure_habituelle(user.profils.first(), maintenant)
        if not heure <= local.hour <= heure + RETARD_MAX_HEURES:
            continue
        if dry_run:
            envoyes += 1
            continue
        try:
            charge = composer_push(user, maintenant)
            appareils = list(user.abonnements_push.all())
            # Trace AVANT l'envoi : deux tours qui se chevauchent ne doivent jamais envoyer deux
            # fois. Retirée si aucun appareil n'a reçu, pour qu'un tour suivant retente.
            try:
                RelanceEnvoyee.objects.create(
                    user=user, type=TypeRelance.RAPPEL_SEANCE, reference=reference, canal=CanalRelance.PUSH,
                )
            except IntegrityError:
                continue
            if sum(envoyer_a_l_appareil(appareil, charge) for appareil in appareils) == 0:
                RelanceEnvoyee.objects.filter(
                    user=user, type=TypeRelance.RAPPEL_SEANCE, reference=reference, canal=CanalRelance.PUSH,
                ).delete()
                continue
            envoyes += 1
        except Exception:
            logger.exception("Rappel push non envoyé à l'élève %s", user.pk)
    return envoyes
