"""
Où se situe l'élève parmi les candidats de son cursus CETTE SEMAINE - un repère d'effort, pas de
niveau : il compare l'XP gagnée sur sept jours (voir quiz.xp, qui récompense la maîtrise), jamais
une note.

Trois garde-fous, parce qu'un classement faux ou humiliant fait plus de mal qu'une absence de
classement :
- il n'existe qu'à partir de SEUIL_COHORTE élèves actifs sur la semaine : en dessous, un
  « top 10 % » parmi huit personnes ne veut rien dire (même règle que partout dans l'application
  pour les petits échantillons) ;
- il ne dit jamais un rang ni un pourcentage précis, seulement une bande (le quart supérieur, la
  moitié supérieure), et il se tait pour la moitié basse : personne n'a besoin qu'on lui annonce
  qu'il est en dessous de la médiane, l'objectif du jour et la série font déjà ce travail ;
- il est agrégé et anonyme : aucun autre élève n'est nommé, ni identifiable, ni même compté
  individuellement dans la réponse.
"""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from subscriptions.models import Subscription

from .models import JourXP

SEUIL_COHORTE = 30
FENETRE_JOURS = 7

BANDE_QUART = "quart"
BANDE_MOITIE = "moitie"


def classement_hebdo(profil, cursus, aujourdhui=None):
    """{disponible, bande} : `disponible` dit si la cohorte est assez grande pour qu'un classement
    ait un sens ; `bande` vaut "quart", "moitie" ou None (moitié basse, ou rien gagné cette semaine)."""
    aujourdhui = aujourdhui or timezone.localdate()
    debut = aujourdhui - timedelta(days=FENETRE_JOURS - 1)
    # Cohorte : les profils abonnés à ce cursus qui ont gagné de l'XP sur la semaine. Un sous-
    # ensemble d'abonnements plutôt qu'une jointure : un profil qui a renouvelé a deux lignes
    # d'abonnement, et la jointure compterait son XP deux fois.
    totaux = dict(
        JourXP.objects.filter(
            jour__gte=debut, jour__lte=aujourdhui, xp__gt=0, profil__compte__is_staff=False,
            profil__in=Subscription.objects.filter(cursus=cursus).values("profil"),
        )
        .values("profil").annotate(total=Sum("xp")).values_list("profil", "total"),
    )
    if len(totaux) < SEUIL_COHORTE:
        return {"disponible": False, "bande": None}
    moi = totaux.get(profil.id, 0)
    if moi == 0:
        return {"disponible": True, "bande": None}
    part_en_dessous = sum(1 for total in totaux.values() if total < moi) / len(totaux)
    bande = BANDE_QUART if part_en_dessous >= 0.75 else BANDE_MOITIE if part_en_dessous >= 0.5 else None
    return {"disponible": True, "bande": bande}
