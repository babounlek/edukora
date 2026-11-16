"""
Rattrapage des paiements CamPay restés « en attente ».

L'état d'une transaction n'était relu que par la page d'abonnement, qui cesse de sonder après deux
minutes (voir SubscribePage.tsx, MAX_POLL_ATTEMPTS). Un payeur qui valide tard sur son téléphone, ou
qui ferme la page, avait payé sans jamais recevoir son accès : plus personne n'interrogeait
l'agrégateur. Deux appelants relisent maintenant ces transactions :

- l'ordonnanceur des relances, une fois par heure, pour tout le monde (voir
  relances.management.commands.planifier_relances) ;
- l'application, à l'ouverture, pour le compte connecté (voir relances.views.paiement_a_reprendre_view) :
  l'accès revient dès le retour du payeur, sans attendre le tour suivant.

`Transaction.sync_status` reste le seul chemin d'activation : idempotent, sous verrou.
"""

import logging
from datetime import timedelta

from django.utils import timezone

from .models import StatutTransaction, Transaction

logger = logging.getLogger("payments")

# Au-delà, l'agrégateur a lui-même abandonné la demande depuis longtemps : inutile de l'interroger.
FENETRE_RATTRAPAGE = timedelta(hours=48)
# Pendant ses deux premières minutes, la transaction est sondée par la page elle-même.
DELAI_AVANT_RATTRAPAGE = timedelta(minutes=3)
# À l'ouverture de l'application : pas plus d'une interrogation par minute et par transaction
# (chaque relecture réécrit `updated_at`), quel que soit le nombre de pages ouvertes.
PAUSE_ENTRE_DEUX_LECTURES = timedelta(minutes=1)


def rattraper_paiements_en_attente(maintenant=None, *, user=None):
    """
    Relit auprès de l'agrégateur les transactions encore en attente, et active l'accès de celles
    qui ont abouti. Retourne le nombre d'accès activés. `user` : seulement les siennes, avec une
    pause d'une minute entre deux lectures. Ne lève jamais : une transaction illisible est
    journalisée et retentée au tour suivant.
    """
    maintenant = maintenant or timezone.now()
    en_attente = Transaction.objects.filter(
        status=StatutTransaction.PENDING,
        created_at__gte=maintenant - FENETRE_RATTRAPAGE,
        created_at__lte=maintenant - DELAI_AVANT_RATTRAPAGE,
    ).exclude(provider_reference="")
    if user is not None:
        en_attente = en_attente.filter(user=user, updated_at__lte=maintenant - PAUSE_ENTRE_DEUX_LECTURES)

    actives = 0
    for transaction in en_attente.select_related("plan", "user"):
        try:
            transaction.sync_status()
        except Exception:
            logger.exception("Rattrapage du paiement %s impossible", transaction.pk)
            continue
        if transaction.status == StatutTransaction.SUCCESSFUL:
            actives += 1
            logger.info("Paiement %s confirmé au rattrapage, accès activé", transaction.pk)
    return actives
