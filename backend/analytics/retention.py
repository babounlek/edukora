"""
Habitudes de retour, calculées à partir des tables qui existent déjà (réponses de quiz,
séances terminées, sessions de quiz) : lisible RÉTROACTIVEMENT sur tout l'historique,
comme analytics.funnel - c'est le point de départ à relever avant de changer quoi que ce
soit à la boucle de séance (XP, objectif quotidien), pour savoir ensuite si ça a bougé.

Trois questions, une par bloc :
  - reviennent-ils ? (retour à J+1, J+7 et dans la semaine qui suit le premier jour actif) ;
  - à quelle fréquence ? (jours actifs par élève actif, séances terminées par semaine) ;
  - vont-ils au bout ? (quiz terminés rapportés aux quiz commencés).

Un « jour actif » est un jour civil où le profil a répondu à une question de quiz ou terminé
une séance du jour : une simple ouverture de l'appli n'est pas une activité.
"""

from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from quiz.models import QuizAnswer, QuizSession, SeanceJournaliere, StatutSeance

from .models import AnalyticsEvent, EventName


def _pourcentage(partie, total):
    return round(100 * partie / total, 1) if total else None


def jours_actifs_par_profil(*, depuis=None):
    """{profil_id: {date, ...}} - jours civils (fuseau local) d'activité réelle."""
    jours = defaultdict(set)
    reponses = QuizAnswer.objects.all()
    seances = SeanceJournaliere.objects.filter(statut=StatutSeance.TERMINEE, termine_at__isnull=False)
    if depuis is not None:
        reponses = reponses.filter(answered_at__gte=depuis)
        seances = seances.filter(termine_at__gte=depuis)
    for profil_id, quand in reponses.values_list("quiz_question__session__profil_id", "answered_at"):
        jours[profil_id].add(timezone.localtime(quand).date())
    for profil_id, quand in seances.values_list("profil_id", "termine_at"):
        jours[profil_id].add(timezone.localtime(quand).date())
    return jours


def retention(jours=30, *, maintenant=None):
    """Retour des profils dont le PREMIER jour actif tombe dans les `jours` derniers jours."""
    maintenant = maintenant or timezone.now()
    aujourdhui = timezone.localtime(maintenant).date()
    debut = aujourdhui - timedelta(days=jours)

    # Le premier jour actif se lit sur tout l'historique, jamais seulement sur la fenêtre :
    # un élève actif depuis des mois n'est pas « nouveau » parce qu'on regarde 30 jours.
    par_profil = jours_actifs_par_profil()
    cohorte = {pid: min(j) for pid, j in par_profil.items() if j and min(j) >= debut}

    def mesure(decalage_min, decalage_max):
        """(profils assez anciens pour être jugés, dont revenus dans [min, max] jours après)."""
        eligibles = {pid: p for pid, p in cohorte.items() if p + timedelta(days=decalage_max) <= aujourdhui}
        revenus = [
            pid for pid, premier in eligibles.items()
            if any(premier + timedelta(days=decalage_min) <= j <= premier + timedelta(days=decalage_max)
                   for j in par_profil[pid])
        ]
        return len(eligibles), len(revenus)

    retour = {}
    for cle, (bas, haut) in {"j1": (1, 1), "j7": (7, 7), "semaine_suivante": (1, 7)}.items():
        eligibles, revenus = mesure(bas, haut)
        retour[cle] = {"eligibles": eligibles, "revenus": revenus, "part": _pourcentage(revenus, eligibles)}

    return {
        "fenetre_jours": jours,
        "genere_le": maintenant.isoformat(),
        "nouveaux_profils_actifs": len(cohorte),
        "retour": retour,
        "frequence": _frequence(par_profil, aujourdhui),
        "quiz": _quiz(maintenant, jours),
    }


def _frequence(par_profil, aujourdhui, fenetre=28):
    """Sur les `fenetre` derniers jours : parmi les profils actifs, combien de jours actifs
    chacun, et combien de séances du jour terminées par semaine."""
    debut = aujourdhui - timedelta(days=fenetre)
    actifs = {pid: [j for j in js if j > debut] for pid, js in par_profil.items()}
    actifs = {pid: js for pid, js in actifs.items() if js}
    semaines = fenetre / 7
    seances = SeanceJournaliere.objects.filter(
        statut=StatutSeance.TERMINEE, termine_at__date__gt=debut,
    ).count()
    nb = len(actifs)
    return {
        "fenetre_jours": fenetre,
        "profils_actifs": nb,
        "jours_actifs_par_profil": round(sum(len(js) for js in actifs.values()) / nb, 1) if nb else None,
        "profils_actifs_au_moins_4_jours": _pourcentage(sum(1 for js in actifs.values() if len(js) >= 4), nb),
        "seances_terminees_par_semaine_et_par_profil": round(seances / semaines / nb, 2) if nb else None,
    }


def _quiz(maintenant, jours):
    debut = maintenant - timedelta(days=jours)
    sessions = QuizSession.objects.filter(started_at__gte=debut)
    commencees = sessions.count()
    terminees = sessions.filter(completed_at__isnull=False).count()
    return {
        "commences": commencees,
        "termines": terminees,
        "part_terminee": _pourcentage(terminees, commencees),
        # Les abandons déclarés (clic sur « Quitter ») ne sont tracés que depuis l'ajout de
        # l'évènement : avant, seule la différence commencés/terminés existe.
        "abandons_declares": AnalyticsEvent.objects.filter(
            name=EventName.QUIZ_ABANDONNE, created_at__gte=debut,
        ).count(),
    }


def _lisible(valeur):
    return "-" if valeur is None else valeur


def rendre_texte(rapport):
    f = rapport["frequence"]
    q = rapport["quiz"]
    lignes = [
        f"Habitudes de retour : profils dont le premier jour actif tombe ces {rapport['fenetre_jours']} derniers jours "
        f"({rapport['nouveaux_profils_actifs']} profils)",
        "",
    ]
    for cle, libelle in (("j1", "Retour à J+1"), ("j7", "Retour à J+7"), ("semaine_suivante", "Retour dans les 7 jours")):
        r = rapport["retour"][cle]
        lignes.append(f"  {libelle:<26} {r['revenus']:>4} sur {r['eligibles']:<4} ({_lisible(r['part'])} %)")
    lignes += [
        "",
        f"Fréquence ({f['fenetre_jours']} derniers jours, {f['profils_actifs']} profils actifs) :",
        f"  jours actifs par profil : {_lisible(f['jours_actifs_par_profil'])}",
        f"  profils actifs au moins 4 jours : {_lisible(f['profils_actifs_au_moins_4_jours'])} %",
        f"  séances terminées par semaine et par profil : {_lisible(f['seances_terminees_par_semaine_et_par_profil'])}",
        "",
        f"Quiz : {q['termines']} terminés sur {q['commences']} commencés ({_lisible(q['part_terminee'])} %), "
        f"{q['abandons_declares']} abandon(s) déclaré(s)",
    ]
    return "\n".join(lignes)
