"""
La série de jours de travail d'un élève - le nombre de jours de suite où il a fait une séance.

Deux règles la rendent supportable plutôt que punitive, parce qu'un compteur qui retombe à
zéro au premier jour manqué fait abandonner ceux qui en ont le plus besoin :

- Un jour de repos est pardonné par semaine : un seul jour manquant, encadré de jours
  travaillés, ne casse pas la série (il ne s'ajoute pas au compte). Un second dans les
  sept jours la rompt.
- Aujourd'hui n'est jamais un jour manqué : tant que la journée n'est pas finie, la série
  reste vivante à son niveau d'hier.

Un jour compte dès qu'une séance du jour est terminée ce jour-là (date LOCALE, voir
SeanceJournaliere.date) - jamais une simple connexion, qui ne prouve aucun travail.
"""

from datetime import date, timedelta

from django.utils import timezone

from .models import SeanceJournaliere, StatutSeance

JOURS_ENTRE_DEUX_REPOS = 7


def jours_travailles(user):
    return set(
        SeanceJournaliere.objects.filter(user=user, statut=StatutSeance.TERMINEE)
        .values_list("date", flat=True),
    )


def _serie_se_terminant_le(jours, fin):
    """Longueur de la série qui se termine le jour `fin` (un jour travaillé), et si un
    repos y a été pris dans les JOURS_ENTRE_DEUX_REPOS derniers jours."""
    compte = 0
    dernier_repos = None
    jour = fin
    while True:
        if jour in jours:
            compte += 1
            jour -= timedelta(days=1)
            continue
        veille_travaillee = (jour - timedelta(days=1)) in jours
        repos_disponible = dernier_repos is None or (dernier_repos - jour).days >= JOURS_ENTRE_DEUX_REPOS
        if veille_travaillee and repos_disponible:
            dernier_repos = jour
            jour -= timedelta(days=1)
            continue
        break
    repos_recent = dernier_repos is not None and (fin - dernier_repos).days < JOURS_ENTRE_DEUX_REPOS
    return compte, repos_recent


def calculer_serie(jours, aujourdhui):
    """{jours, record, actif_aujourdhui, repos_pris} - fonction pure, sans base de données."""
    actif_aujourdhui = aujourdhui in jours
    # Aujourd'hui n'est jamais « manqué » : on calcule comme s'il était travaillé, puis on
    # retire ce jour fictif du compte. La série reste ainsi vivante tant qu'il reste la journée
    # pour la prolonger - y compris quand hier était le jour de repos pardonné.
    base = jours if actif_aujourdhui else jours | {aujourdhui}
    compte, repos_pris = _serie_se_terminant_le(base, aujourdhui)
    actuelle = compte if actif_aujourdhui else compte - 1
    record = max((_serie_se_terminant_le(jours, j)[0] for j in jours), default=0)
    return {
        "jours": actuelle,
        "record": max(record, actuelle),
        "actif_aujourdhui": actif_aujourdhui,
        "repos_pris": repos_pris and actuelle > 0,
    }


def serie_de_jours(user, aujourdhui: date | None = None):
    return calculer_serie(jours_travailles(user), aujourdhui or timezone.localdate())
