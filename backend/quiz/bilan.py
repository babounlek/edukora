"""
Bilan de période : ce que l'élève a réellement fait avec son abonnement.

Calculé à la volée depuis les données déjà en base (séances terminées, réponses aux
quiz) - aucune table de plus, donc rien à tenir à jour ni à rattraper. Le bilan ne
raconte que ce qui est vrai : un élève peu actif reçoit un message d'invitation à
reprendre, jamais un reproche ni un chiffre gonflé.
"""
from datetime import datetime, time, timedelta

from django.utils import timezone

from subscriptions.models import Subscription

from .models import QuizAnswer, SeanceJournaliere, StatutSeance
from .services import SEUIL_MAITRISE

# Longueur de la période affichée. Un abonnement Mensuel dure 30 jours ; un abonnement
# "Jusqu'à l'Examen" est plus long, mais 30 jours reste la maille à laquelle un élève
# se souvient de ce qu'il a fait.
PERIODE_JOURS = 30

# Sous ce nombre de réponses cumulées, un thème n'est pas "consolidé" : 1 réponse juste
# sur 1 fait 100 %, ce qui ne prouve rien.
REPONSES_MIN_THEME_CONSOLIDE = 3

THEMES_CITES_MAX = 5
MATIERES_CITEES_MAX = 4


def _borne_haute(jour):
    """Dernier instant (aware, fuseau courant) du jour local `jour`."""
    return timezone.make_aware(datetime.combine(jour, time.max))


def _borne_basse(jour):
    return timezone.make_aware(datetime.combine(jour, time.min))


def _taux(reussies, total):
    return round(100 * reussies / total) if total else None


def bilan_de_periode(user, cursus, aujourdhui=None, jours=PERIODE_JOURS):
    """
    Renvoie le bilan des `jours` derniers jours (PERIODE_JOURS par défaut, 7 pour le bilan
    hebdomadaire) de l'abonnement de `user` à
    `cursus`, ou None si l'élève n'a jamais eu d'abonnement à ce cursus.

    La période se termine à la date du jour, ou à la date d'expiration si elle est déjà
    passée (un bilan "depuis l'expiration" ne parlerait que de jours sans accès), et ne
    remonte jamais avant la création de l'abonnement.

    "Taux avant" est le taux de réussite sur toutes les réponses antérieures à la
    période : le comparer au taux de la période dit si l'élève progresse, sans exiger
    d'historique de maîtrise qu'on ne stocke pas.

    Un thème est "consolidé" quand son taux cumulé passe de sous le seuil de maîtrise
    (ou d'un thème jamais travaillé) à au-dessus, avec au moins
    REPONSES_MIN_THEME_CONSOLIDE réponses. Même seuil que le parcours ; la maille est le
    thème (Tag), là où le parcours regroupe par savoir - c'est pourquoi le libellé
    affiché est "thèmes consolidés" et non "savoirs maîtrisés".
    """
    subscription = Subscription.objects.filter(user=user, cursus=cursus).first()
    if subscription is None:
        return None

    aujourdhui = aujourdhui or timezone.localdate()
    expiration = timezone.localtime(subscription.expires_at).date()
    fin = min(aujourdhui, expiration)
    debut = max(fin - timedelta(days=jours - 1), timezone.localtime(subscription.created_at).date())
    debut_dt, fin_dt = _borne_basse(debut), _borne_haute(fin)

    seances_qs = SeanceJournaliere.objects.filter(
        user=user, cursus=cursus, statut=StatutSeance.TERMINEE, date__gte=debut, date__lte=fin,
    )
    jours_actifs = set(seances_qs.values_list("date", flat=True))

    # Uniquement les réponses sourcées d'un CompetenceItem : thème unique et sans
    # ambiguïté, comme pour la maîtrise (voir quiz.services.maitrise_par_theme).
    reponses = (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
            answered_at__lte=fin_dt,
        )
        .select_related("quiz_question__competence_item__theme", "quiz_question__competence_item__subject")
        .order_by("answered_at")
    )

    avant = {"total": 0, "reussies": 0}
    periode = {"total": 0, "reussies": 0}
    par_matiere = {}
    par_theme = {}  # theme_id -> {"nom", "avant": [tot, ok], "fin": [tot, ok]}
    serie = meilleure_serie = 0

    for reponse in reponses:
        item = reponse.quiz_question.competence_item
        correcte = reponse.est_correcte
        dans_periode = reponse.answered_at >= debut_dt

        theme = par_theme.setdefault(
            item.theme_id, {"nom": item.theme.name, "subject": item.subject.label, "avant": [0, 0], "fin": [0, 0]},
        )
        theme["fin"][0] += 1
        theme["fin"][1] += int(correcte)

        matiere = par_matiere.setdefault(
            item.subject_id,
            {"subject_id": item.subject_id, "subject_label": item.subject.label,
             "avant": [0, 0], "periode": [0, 0]},
        )

        if dans_periode:
            periode["total"] += 1
            periode["reussies"] += int(correcte)
            matiere["periode"][0] += 1
            matiere["periode"][1] += int(correcte)
            jours_actifs.add(timezone.localtime(reponse.answered_at).date())
            serie = serie + 1 if correcte else 0
            meilleure_serie = max(meilleure_serie, serie)
        else:
            avant["total"] += 1
            avant["reussies"] += int(correcte)
            matiere["avant"][0] += 1
            matiere["avant"][1] += int(correcte)
            theme["avant"][0] += 1
            theme["avant"][1] += int(correcte)

    themes_travailles = 0
    consolides = []
    solides_total = solides_avant = 0
    for theme in par_theme.values():
        total_fin, ok_fin = theme["fin"]
        total_av, ok_av = theme["avant"]
        if total_fin > total_av:
            themes_travailles += 1
        taux_fin = _taux(ok_fin, total_fin)
        taux_av = _taux(ok_av, total_av)
        # Jalons : "solide" = même définition que "consolidé" (seuil de maîtrise, avec un
        # minimum de réponses), mais sur l'état cumulé - pas seulement sur la période.
        if total_fin >= REPONSES_MIN_THEME_CONSOLIDE and taux_fin >= SEUIL_MAITRISE:
            solides_total += 1
        if total_av >= REPONSES_MIN_THEME_CONSOLIDE and taux_av is not None and taux_av >= SEUIL_MAITRISE:
            solides_avant += 1
        if (
            total_fin >= REPONSES_MIN_THEME_CONSOLIDE
            and taux_fin >= SEUIL_MAITRISE
            and (taux_av is None or taux_av < SEUIL_MAITRISE or total_av < REPONSES_MIN_THEME_CONSOLIDE)
            and total_fin > total_av  # travaillé DANS la période, pas un état hérité
        ):
            consolides.append({"theme": theme["nom"], "subject_label": theme["subject"]})

    matieres = []
    for m in par_matiere.values():
        if m["periode"][0] == 0:
            continue
        taux_periode = _taux(m["periode"][1], m["periode"][0])
        taux_avant = _taux(m["avant"][1], m["avant"][0])
        matieres.append({
            "subject_id": m["subject_id"],
            "subject_label": m["subject_label"],
            "questions": m["periode"][0],
            "taux_avant": taux_avant,
            "taux_periode": taux_periode,
        })
    matieres.sort(key=lambda m: -m["questions"])

    seances = seances_qs.count()
    seances_total = SeanceJournaliere.objects.filter(
        user=user, cursus=cursus, statut=StatutSeance.TERMINEE, date__lte=fin,
    ).count()
    return {
        "debut": debut,
        "fin": fin,
        "expire_le": expiration,
        "abonnement_actif": subscription.is_active,
        "seances": seances,
        "jours_actifs": len(jours_actifs),
        "questions": periode["total"],
        "taux_reussite": _taux(periode["reussies"], periode["total"]),
        "taux_avant": _taux(avant["reussies"], avant["total"]),
        "meilleure_serie": meilleure_serie,
        "themes_travailles": themes_travailles,
        # Compteurs cumulés "avant la période" et "à la fin" : le front en tire les jalons
        # (paliers atteints, prochain palier) sans que le serveur en fixe la liste.
        "jalons": {
            "seances_total": seances_total,
            "seances_avant": seances_total - seances,
            "questions_total": avant["total"] + periode["total"],
            "questions_avant": avant["total"],
            "solides_total": solides_total,
            "solides_avant": solides_avant,
        },
        "themes_consolides_total": len(consolides),
        "themes_consolides": consolides[:THEMES_CITES_MAX],
        "matieres": matieres[:MATIERES_CITEES_MAX],
        # Sans activité, le front n'affiche pas de bilan : trois zéros ne convainquent
        # personne de renouveler, ils lui rappellent qu'il n'a rien fait.
        "a_de_l_activite": seances > 0 or periode["total"] > 0,
    }
