"""
Depuis quand un compte n'a plus travaillé - ce que lisent le rappel quotidien (tous canaux) et les relances d'absence.

Un jour « travaillé » est un jour où un profil du compte a gagné des points ou terminé une séance (voir quiz.xp, quiz.serie) :
une simple connexion ne compte pas. Un compte qui n'a encore jamais travaillé est daté de son inscription.

La règle (audit 14, F2) : le rappel quotidien accompagne un élève qui travaille ; il se tait dès que l'élève a manqué deux
jours pleins. Deux messages seulement prennent alors le relais (voir relances.absence), puis plus rien tant qu'il n'est pas
revenu : un rappel par jour envoyé pendant des mois à quelqu'un qui ne vient plus n'aide personne et finit en indésirable.
"""
from django.db.models import Max
from django.utils import timezone

from quiz.models import JourXP, SeanceJournaliere, StatutSeance
from users.models import User

# Nombre de jours écoulés depuis le dernier jour travaillé. 1 : il a travaillé hier. 2 : il a manqué hier (un jour de repos,
# que la série pardonne). À partir de 3, deux jours pleins sont manqués : le rappel quotidien se tait.
PAUSE_A_PARTIR_DE = 3


def dernier_jour_travaille(comptes):
    """{compte_id: date du dernier jour travaillé} pour ces comptes (ids) ; absent du dictionnaire : jamais travaillé."""
    comptes = list(comptes)
    derniers = dict(
        JourXP.objects.filter(profil__compte_id__in=comptes, xp__gt=0)
        .values_list("profil__compte_id").annotate(dernier=Max("jour")),
    )
    seances = (
        SeanceJournaliere.objects.filter(profil__compte_id__in=comptes, statut=StatutSeance.TERMINEE)
        .values_list("profil__compte_id").annotate(dernier=Max("date"))
    )
    for compte_id, jour in seances:
        if compte_id not in derniers or jour > derniers[compte_id]:
            derniers[compte_id] = jour
    return derniers


def jours_sans_travail(comptes, aujourdhui):
    """
    {compte_id: (jours écoulés depuis le dernier jour travaillé, ce jour)} pour ces comptes. Un compte qui n'a jamais
    travaillé est compté depuis son inscription.
    """
    comptes = list(comptes)
    derniers = dernier_jour_travaille(comptes)
    jamais = [c for c in comptes if c not in derniers]
    if jamais:
        for compte_id, inscrit in User.objects.filter(pk__in=jamais).values_list("pk", "date_joined"):
            derniers[compte_id] = timezone.localtime(inscrit).date()
    return {compte_id: ((aujourdhui - jour).days, jour) for compte_id, jour in derniers.items()}


def comptes_en_pause(comptes, aujourdhui):
    """Parmi ces comptes, ceux à qui le rappel quotidien ne doit plus partir : deux jours pleins manqués, ou plus."""
    return {
        compte_id
        for compte_id, (jours, _dernier) in jours_sans_travail(comptes, aujourdhui).items()
        if jours >= PAUSE_A_PARTIR_DE
    }
