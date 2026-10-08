"""
L'accueil d'un abonné en UNE requête (GET /quiz/accueil/, voir views.accueil_view).

Six appels partaient en parallèle depuis le navigateur (plan du jour, résumé du
parcours, révisions dues, lecture en cours, bilan de la semaine, inédites) et
arrivaient dans le désordre : sur une 3G, les blocs apparaissaient un à un et la page
sautait. Une seule réponse, rendue en un seul passage, et des choses que six
requêtes indépendantes ne pouvaient pas dire :

- ce qui a changé DEPUIS LA DERNIÈRE VISITE (delta_depuis) - c'est le mouvement qui
  fait revenir, pas le niveau ;
- où mène le rythme actuel d'ici l'examen (trajectoire) - une projection honnête,
  jamais un encouragement inventé ;
- la PHASE de l'examen (phase_examen) - une page à J-140 n'est pas une page à J-1 ;
- la phrase du coach (phrase_coach) : une ligne spécifique, composée de faits déjà
  en base, jamais un slogan.

Tout ici RÉUTILISE les calculs existants (résumé du parcours, bilan, révision
espacée) : aucune nouvelle notion de maîtrise, aucun chiffre qu'un autre écran ne
pourrait contredire.
"""
from datetime import timedelta
from math import ceil

from django.utils import timezone

from access.models import LectureProgress
from catalog.models import Lesson, LessonType, Origine, StatutContenu

from .models import OrigineSeance, QuizAnswer, SeanceJournaliere, StatutSeance, VisiteAccueil
from .services import (
    DERNIERE_LIGNE_DROITE_JOURS, SEUIL_MAITRISE, _coefficient_par_subject, score_de_la_seance,
)

# Deux appels séparés de plus de quatre heures sont deux visites : ouvrir l'appli le
# matin dans le bus puis le soir à la maison, ce sont deux moments où l'élève veut
# savoir ce qui a bougé - trois rechargements dans la soirée n'en sont qu'un.
SEUIL_NOUVELLE_VISITE = timedelta(hours=4)

# Au-delà, l'élève "revient" : on l'accueille sans reproche et la séance du jour est
# raccourcie (voir BUDGET_RETOUR_MINUTES). Cinq jours, c'est la durée après laquelle
# la série est de toute façon perdue - le retour ne doit pas commencer par une dette.
ABSENCE_RETOUR_JOURS = 5
BUDGET_RETOUR_MINUTES = 10

# Sous ce nombre de réponses d'un côté ET de l'autre, une "hausse" d'une matière est
# du bruit : deux bonnes réponses après une mauvaise font +50 points.
REPONSES_MIN_HAUSSE_MATIERE = 5

# Même définition qu'un thème "consolidé" dans le bilan (voir quiz.bilan) : pas de
# seconde notion de maîtrise.
REPONSES_MIN_THEME_CONSOLIDE = 3
THEMES_CITES_MAX = 3

# Le rythme se lit sur trois semaines : assez pour lisser une semaine de devoirs ou de
# vacances, assez court pour refléter l'élève d'aujourd'hui et non celui de la rentrée.
# En dessous de trois séances dans la fenêtre, on ne projette rien : la première
# projection d'un élève qui a fait une séance dirait n'importe quoi.
FENETRE_RYTHME_JOURS = 21
SEANCES_MINIMUM_RYTHME = 3

# "Couvrir l'essentiel" : 80 % de ce qui tombe (pondéré, voir services.poids_savoir).
# Viser 100 % du programme le jour J n'est le cas de personne, et une cible impossible
# ne guide rien.
CIBLE_COUVERTURE = 0.8

# Quand la fenêtre ne montre aucun thème consolidé malgré des séances, le rendement
# observé est 0 et la projection diverge. On suppose alors qu'une séance sur deux
# consolide un thème - une hypothèse prudente, dite comme telle côté frontend, jamais
# présentée comme une mesure.
RENDEMENT_PLANCHER = 0.5

# Au-delà, "une séance de plus par semaine" n'a plus de sens : on ne demande pas huit
# séances par semaine. Le frontend bascule alors sur "vise l'essentiel".
SEANCES_DE_PLUS_MAX = 7

# Phases de l'examen, en jours restants (bornes incluses).
JOURS_SIMULATION = 30

# Une lecture plus vieille qu'une semaine n'est plus "à reprendre" : l'élève est passé
# à autre chose, la lui remettre sous le nez serait une corvée de plus.
LECTURE_A_REPRENDRE_JOURS = 7

REVISIONS_ACCUEIL_MAX = 2


# --- Visite ----------------------------------------------------------------------------


def enregistrer_visite(profil, maintenant=None):
    """
    Note ce passage sur l'accueil et dit si c'est le début d'une nouvelle visite.

    Renvoie (visite, nouvelle). `nouvelle` est vrai à la toute première ouverture et à
    chaque reprise après plus de SEUIL_NOUVELLE_VISITE d'inactivité - c'est à ce
    moment-là, et seulement là, que la borne du "depuis la dernière fois" avance.
    """
    maintenant = maintenant or timezone.now()
    visite, creee = VisiteAccueil.objects.get_or_create(
        profil=profil, defaults={"debut_at": maintenant, "derniere_at": maintenant},
    )
    if creee:
        return visite, True
    nouvelle = maintenant - visite.derniere_at > SEUIL_NOUVELLE_VISITE
    if nouvelle:
        visite.precedente_at = visite.derniere_at
        visite.debut_at = maintenant
    visite.derniere_at = maintenant
    visite.save(update_fields=["precedente_at", "debut_at", "derniere_at"])
    return visite, nouvelle


def absence_jours(visite):
    """Jours civils entre la fin de la visite précédente et le début de celle-ci ; 0 sans
    visite précédente (un premier jour n'est pas une absence)."""
    if visite.precedente_at is None:
        return 0
    debut = timezone.localtime(visite.debut_at).date()
    precedente = timezone.localtime(visite.precedente_at).date()
    return max(0, (debut - precedente).days)


# --- Phase de l'examen -------------------------------------------------------------------


def phase_examen(compte):
    """
    Dans quelle phase de sa préparation l'élève se trouve, d'après les jours restants :
      - `apres` : l'examen est passé (et la session suivante pas encore saisie) ;
      - `jour_j`, `veille` : le jour même, la veille ;
      - `derniere_ligne_droite` : à une semaine - on ne découvre plus, on consolide ;
      - `simulation` : à un mois - les annales en conditions réelles entrent en scène ;
      - `normal` : le reste du temps, et quand aucune date n'est connue.
    """
    if compte is None:
        return "normal"
    jours = compte["jours_restants"]
    if jours < 0:
        return "apres"
    if jours == 0:
        return "jour_j"
    if jours == 1:
        return "veille"
    if jours <= DERNIERE_LIGNE_DROITE_JOURS:
        return "derniere_ligne_droite"
    if jours <= JOURS_SIMULATION:
        return "simulation"
    return "normal"


def premiers_pas(profil, cursus):
    """Vrai tant que l'élève n'a jamais terminé une séance sur ce cursus : l'accueil n'a
    alors ni delta ni trajectoire à raconter, seulement la première séance."""
    return not SeanceJournaliere.objects.filter(profil=profil, cursus=cursus, statut=StatutSeance.TERMINEE).exists()


# --- Depuis la dernière fois ---------------------------------------------------------------


def _taux(reussies, total):
    return round(100 * reussies / total) if total else None


def _rejouer_reponses(profil, cursus, depuis_dt):
    """
    Une passe sur les réponses de l'élève (celles sourcées d'un CompetenceItem, comme
    partout), coupée en "avant `depuis_dt`" et "depuis" : thèmes consolidés dans
    l'intervalle, taux par matière de part et d'autre, nombre de questions.

    Même règle de consolidation que quiz.bilan (seuil de maîtrise, minimum de réponses,
    travaillé DANS l'intervalle) - c'est volontairement une réécriture locale et non un
    appel à bilan_de_periode, dont la fenêtre est bornée par l'abonnement et exprimée
    en jours entiers, là où une visite commence à une heure précise.
    """
    reponses = (
        QuizAnswer.objects.filter(
            quiz_question__session__profil=profil,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
        )
        .select_related("quiz_question__competence_item__theme", "quiz_question__competence_item__subject")
        .order_by("answered_at")
    )
    par_theme = {}
    par_matiere = {}
    questions = 0
    for reponse in reponses:
        item = reponse.quiz_question.competence_item
        correcte = int(reponse.est_correcte)
        recente = reponse.answered_at >= depuis_dt
        theme = par_theme.setdefault(
            item.theme_id, {"nom": item.theme.name, "subject": item.subject.label, "avant": [0, 0], "fin": [0, 0]},
        )
        theme["fin"][0] += 1
        theme["fin"][1] += correcte
        matiere = par_matiere.setdefault(
            item.subject_id, {"subject_id": item.subject_id, "label": item.subject.label, "avant": [0, 0], "depuis": [0, 0]},
        )
        if recente:
            questions += 1
            matiere["depuis"][0] += 1
            matiere["depuis"][1] += correcte
        else:
            theme["avant"][0] += 1
            theme["avant"][1] += correcte
            matiere["avant"][0] += 1
            matiere["avant"][1] += correcte

    consolides = []
    for theme in par_theme.values():
        total_fin, ok_fin = theme["fin"]
        total_av, ok_av = theme["avant"]
        taux_fin, taux_av = _taux(ok_fin, total_fin), _taux(ok_av, total_av)
        if (
            total_fin > total_av
            and total_fin >= REPONSES_MIN_THEME_CONSOLIDE
            and taux_fin >= SEUIL_MAITRISE
            and (taux_av is None or taux_av < SEUIL_MAITRISE or total_av < REPONSES_MIN_THEME_CONSOLIDE)
        ):
            consolides.append({"theme": theme["nom"], "subject_label": theme["subject"]})

    return {"consolides": consolides, "matieres": list(par_matiere.values()), "questions": questions}


def _matiere_en_hausse(matieres):
    """La matière dont le taux a le plus monté entre avant et depuis, avec assez de
    réponses des deux côtés pour que ce soit autre chose que du bruit. None sinon."""
    meilleure = None
    for m in matieres:
        if m["avant"][0] < REPONSES_MIN_HAUSSE_MATIERE or m["depuis"][0] < REPONSES_MIN_HAUSSE_MATIERE:
            continue
        gain = _taux(m["depuis"][1], m["depuis"][0]) - _taux(m["avant"][1], m["avant"][0])
        if gain > 0 and (meilleure is None or gain > meilleure["gain"]):
            meilleure = {"subject_id": m["subject_id"], "subject_label": m["label"], "gain": gain}
    return meilleure


def delta_depuis(profil, cursus, visite):
    """
    Ce qui a changé depuis la visite précédente : séances faites, thèmes passés en
    "consolidé", matière qui a le plus monté, révisions qui ont tenu. None quand il n'y
    a pas de visite précédente, ou quand rien n'a bougé - trois zéros ne sont pas un
    mouvement, et le bloc ne s'affiche pas.

    "Révision tenue" : une séance de révision (origine REVISION_DUE) terminée avec un
    quiz réussi au seuil de maîtrise - le thème raté est revenu, et cette fois il a
    tenu. C'est la boucle que la révision espacée promet ; la montrer, c'est prouver
    qu'elle marche.
    """
    if visite.precedente_at is None:
        return None
    depuis = visite.precedente_at
    stats = _rejouer_reponses(profil, cursus, depuis)
    seances = list(
        SeanceJournaliere.objects.filter(
            profil=profil, cursus=cursus, statut=StatutSeance.TERMINEE, termine_at__gte=depuis,
        ).select_related("quiz_session")
    )
    revisions_tenues = 0
    for seance in seances:
        if seance.origine != OrigineSeance.REVISION_DUE:
            continue
        score = score_de_la_seance(seance)
        if score and 100 * score["reussies"] / score["total"] >= SEUIL_MAITRISE:
            revisions_tenues += 1

    if not seances and not stats["questions"]:
        return None
    return {
        "depuis": timezone.localtime(depuis).date(),
        "seances": len(seances),
        "questions": stats["questions"],
        "themes_consolides_total": len(stats["consolides"]),
        "themes_consolides": stats["consolides"][:THEMES_CITES_MAX],
        "matiere_en_hausse": _matiere_en_hausse(stats["matieres"]),
        "revisions_tenues": revisions_tenues,
    }


# --- Où j'en suis ------------------------------------------------------------------------


def preparation(resume):
    """
    L'anneau de l'accueil : la part de "ce qui tombe vraiment" déjà maîtrisée (voir
    services.poids_savoir - coefficient x fréquence), et à côté le compte brut, pour
    que "12 savoirs sur 40" reste lisible sous le pourcentage pondéré.

    None sans savoir exploitable : un anneau à 0 % sur un cursus vide serait un
    reproche pour un contenu qui manque de notre côté.
    """
    poids_total = sum(m["poids_total"] for m in resume)
    poids_maitrise = sum(m["poids_maitrise"] for m in resume)
    exploitables = sum(m["total"] - m["sans_contenu"] for m in resume)
    maitrises = sum(m["maitrises"] for m in resume)
    if poids_total <= 0 or exploitables <= 0:
        return None
    return {
        "ponderee": round(poids_maitrise / poids_total, 4),
        "brute": round(maitrises / exploitables, 4),
        "maitrises": maitrises,
        "exploitables": exploitables,
    }


def trajectoire(profil, cursus, resume, compte, aujourdhui=None):
    """
    Où mène le rythme des trois dernières semaines d'ici le jour J.

    Unité de rythme : les thèmes consolidés dans la fenêtre (même définition que le
    bilan), rapportés au jour. Chaque thème consolidé est compté comme une unité du
    parcours au poids moyen des unités qui restent - une approximation (le parcours
    par fréquence regroupe parfois plusieurs tags en un thème), assumée et constante :
    elle ne flatte pas plus un élève qu'un autre.

    Ce qui est dit, et dans cet ordre d'honnêteté :
      - sans rythme mesurable (moins de SEANCES_MINIMUM_RYTHME séances) : rien n'est
        projeté, `couverture_projetee` est None ;
      - si la projection atteint CIBLE_COUVERTURE : `suffisant` ;
      - sinon : le nombre de séances hebdomadaires EN PLUS qui y mèneraient, ou None
        au-delà de SEANCES_DE_PLUS_MAX (le frontend dit alors de viser l'essentiel).

    None quand aucune date d'examen n'est connue, quand elle est passée, ou quand rien
    n'est exploitable dans le cursus.
    """
    if compte is None or compte["jours_restants"] <= 0:
        return None
    etat = preparation(resume)
    if etat is None:
        return None
    aujourdhui = aujourdhui or timezone.localdate()
    jours_restants = compte["jours_restants"]

    poids_total = sum(m["poids_total"] for m in resume)
    poids_maitrise = sum(m["poids_maitrise"] for m in resume)
    restantes = etat["exploitables"] - etat["maitrises"]
    poids_restant_moyen = (poids_total - poids_maitrise) / restantes if restantes > 0 else 0.0

    debut = aujourdhui - timedelta(days=FENETRE_RYTHME_JOURS)
    seances_fenetre = SeanceJournaliere.objects.filter(
        profil=profil, cursus=cursus, statut=StatutSeance.TERMINEE, date__gt=debut, date__lte=aujourdhui,
    ).count()

    base = {
        "jours_restants": jours_restants,
        "fenetre_jours": FENETRE_RYTHME_JOURS,
        "seances_fenetre": seances_fenetre,
        "seances_par_semaine": None,
        "couverture_actuelle": etat["ponderee"],
        "couverture_projetee": None,
        "cible": CIBLE_COUVERTURE,
        "suffisant": None,
        "seances_de_plus_par_semaine": None,
        "atteignable": None,
    }
    if seances_fenetre < SEANCES_MINIMUM_RYTHME:
        return base

    debut_dt = timezone.make_aware(timezone.datetime.combine(debut + timedelta(days=1), timezone.datetime.min.time()))
    consolides = len(_rejouer_reponses(profil, cursus, debut_dt)["consolides"])
    unites_par_jour = consolides / FENETRE_RYTHME_JOURS
    gain_poids = unites_par_jour * jours_restants * poids_restant_moyen
    projetee = min(1.0, (poids_maitrise + gain_poids) / poids_total) if poids_total else 0.0
    suffisant = projetee >= CIBLE_COUVERTURE

    seances_de_plus = None
    atteignable = True
    if not suffisant:
        rendement = max(RENDEMENT_PLANCHER, consolides / seances_fenetre)
        manque_poids = CIBLE_COUVERTURE * poids_total - poids_maitrise - gain_poids
        if poids_restant_moyen > 0:
            seances_manquantes = (manque_poids / poids_restant_moyen) / rendement
            seances_de_plus = max(1, ceil(seances_manquantes / jours_restants * 7))
            atteignable = seances_de_plus <= SEANCES_DE_PLUS_MAX
            if not atteignable:
                seances_de_plus = None
        else:
            atteignable = False

    return {
        **base,
        "seances_par_semaine": round(seances_fenetre / FENETRE_RYTHME_JOURS * 7, 1),
        "couverture_projetee": round(projetee, 4),
        "suffisant": suffisant,
        "seances_de_plus_par_semaine": seances_de_plus,
        "atteignable": True if suffisant else atteignable,
    }


# --- Autour de la séance -----------------------------------------------------------------


def lecture_a_reprendre(profil, cursus):
    """
    La dernière épreuve DE SON CURSUS ouverte cette semaine, s'il y en a une - de quoi
    finir ce qu'on a commencé sans passer par l'historique.

    Filtrée par cursus : la vitrine affiche un extrait de corrigé gratuit (une épreuve
    de BEPC) et cette lecture est enregistrée comme les autres - sans le filtre, un
    élève de Terminale se voyait proposer de "reprendre" une épreuve de 3e.
    """
    depuis = timezone.now() - timedelta(days=LECTURE_A_REPRENDRE_JOURS)
    lecture = (
        LectureProgress.objects.filter(profil=profil, lesson__isnull=False, last_read_at__gte=depuis, lesson__cursus=cursus)
        .filter(lesson__statut=StatutContenu.VALIDE, lesson__subject__country__actif=True)
        .select_related("lesson__subject__country")
        .order_by("-last_read_at")
        .first()
    )
    if lecture is None or not lecture.lesson.slug:
        return None
    return {
        "slug": lecture.lesson.slug,
        "title": lecture.lesson.title,
        "country": lecture.lesson.subject.country.code.lower(),
    }


def simulation_suggeree(profil, cursus, phase):
    """
    À un mois de l'examen, une annale à passer en conditions réelles : la matière qui
    pèse le plus au diplôme d'abord (coefficient transcrit des épreuves), la session
    la plus récente ensuite, et jamais une épreuve déjà simulée. None hors phase.
    """
    if phase not in ("simulation", "derniere_ligne_droite"):
        return None
    coefficients = _coefficient_par_subject(cursus)
    candidates = (
        Lesson.objects.visibles()
        .filter(cursus=cursus, lesson_type=LessonType.CORR, origine=Origine.OFFICIEL, exercises__isnull=False)
        .exclude(simulations__profil=profil)
        .select_related("subject")
        .distinct()
    )
    choisie = None
    for lesson in candidates:
        cle = (coefficients.get(lesson.subject_id, 0.0), lesson.year or 0)
        if choisie is None or cle > choisie[0]:
            choisie = (cle, lesson)
    if choisie is None:
        return None
    lesson = choisie[1]
    return {
        "id": lesson.id,
        "slug": lesson.slug,
        "title": lesson.title,
        "subject_label": lesson.subject.label,
        "year": lesson.year,
    }


def _majuscule(texte):
    return texte[:1].upper() + texte[1:] if texte else texte


def _titre(seance):
    if seance.get("theme"):
        return _majuscule(seance["theme"]["name"])
    if seance.get("savoir"):
        return _majuscule(seance["savoir"]["intitule"])
    return None


# Paliers de l'accroche de fréquence, du plus fort au plus faible : (part des épreuves
# concernées, formulation). En dessous du dernier palier, on ne dit rien de la fréquence -
# "tombe régulièrement" pour 3 épreuves sur 41 serait une phrase que la pastille juste
# dessous contredit, et la crédibilité de la recommandation en dépend (voir
# raisons_de_la_seance).
PALIERS_FREQUENCE = (
    (0.75, "tombe presque à chaque examen"),
    (0.5, "tombe à l'examen plus d'une fois sur deux"),
    (0.25, "tombe régulièrement à l'examen"),
)


def _accroche_frequence(frequence):
    """La formulation qui correspond à la part réelle des épreuves, ou None si elle est trop faible."""
    if not frequence or not frequence.get("occurrences") or not frequence.get("epreuves_total"):
        return None
    part = frequence["occurrences"] / frequence["epreuves_total"]
    return next((texte for seuil, texte in PALIERS_FREQUENCE if part >= seuil), None)


# Fins de phrase qui tournent d'un jour à l'autre : la même ligne chaque matin finit par ne plus
# être lue. Le choix ne dépend que de la date (voir _variante), donc une page rechargée dix
# fois dans la journée dit toujours la même chose.
FINS_FREQUENCE_PROCHE = (
    "{duree}\u00a0minutes pour ne pas le découvrir le jour J.",
    "{duree}\u00a0minutes pour l'avoir en main le jour J.",
    "{duree}\u00a0minutes pour arriver prêt le jour J.",
)
# À plusieurs mois de l'examen, « le jour J » est une échéance lointaine : on parle d'avance
# prise, pas d'urgence.
FINS_FREQUENCE_LOIN = (
    "{duree}\u00a0minutes pour prendre de l'avance.",
    "{duree}\u00a0minutes pour qu'il ne te surprenne pas.",
    "{duree}\u00a0minutes aujourd'hui, c'est autant que tu n'auras pas à rattraper plus tard.",
)
# Au-delà de ce nombre de jours avant l'examen, on parle d'avance plutôt que du jour J.
HORIZON_LOINTAIN_JOURS = 90
FINS_REVISION = (
    "{duree}\u00a0minutes pour le fixer avant qu'il ne s'efface.",
    "{duree}\u00a0minutes pour qu'il reste en mémoire.",
    "{duree}\u00a0minutes pour le rendre solide.",
)


def _variante(options, jour, **valeurs):
    """Une des formulations, stable pour la journée, avec ses valeurs substituées."""
    return options[jour.toordinal() % len(options)].format(**valeurs)


def phrase_coach(plan, phase, absence, premiers_pas_eleve=False, jour=None):
    """
    Une phrase, spécifique, composée de faits déjà dans la charge utile du plan (thème,
    durée, fréquence à l'examen, date du dernier ratage) - jamais un slogan. C'est ce
    qu'un coach dirait en une ligne avant de tendre le cahier.

    Le thème n'y est pas nommé : il s'affiche en grand juste dessous (voir TeteAccueil),
    et le répéter faisait lire deux fois les mêmes mots dans la même carte. La phrase dit
    « ce thème », le titre dit lequel.

    L'ordre des cas suit l'ordre d'importance pour l'élève : le jour de l'examen prime
    sur tout, puis la séance déjà faite, puis ce que la séance propose.

    `jour` : la date qui fixe la variante de formulation (aujourd'hui par défaut).
    """
    jour = jour or timezone.localdate()
    if phase == "apres":
        return "L'examen est passé. Tout ce que tu as travaillé reste à toi."
    if phase == "jour_j":
        return "C'est aujourd'hui. Respire : le travail est fait, il ne reste qu'à le montrer."
    if phase == "veille":
        return "C'est demain. Ce soir, on ne découvre rien : on relit, et on dort tôt."

    etat = plan.get("etat")
    seance = plan.get("seance")
    if etat == "deja_fait_aujourdhui" and seance:
        score = seance.get("score")
        if score and score["total"]:
            return f"Séance faite, {score['reussies']} sur {score['total']} au quiz. Demain, on continue."
        return "Séance faite. Demain, on continue."
    if etat != "plan_pret" or not seance:
        return "Rien à te proposer aujourd'hui : choisis un thème toi-même, on te suit."

    prefixe = ""
    if absence >= ABSENCE_RETOUR_JOURS:
        # « On reprend » suppose qu'il y a eu quelque chose avant : pas pour qui est
        # passé voir l'appli sans jamais terminer une séance.
        prefixe = "Content de te revoir. " if premiers_pas_eleve else "Content de te revoir. On reprend en douceur. "
    elif phase == "derniere_ligne_droite":
        prefixe = "Dernière ligne droite. "

    duree = seance.get("duree_estimee_min")
    titre = _titre(seance)
    origine = seance.get("origine")

    if origine == "DIAGNOSTIC":
        return prefixe + "Quinze questions pour situer ton niveau. Ensuite, chaque séance sera taillée pour toi."
    if titre is None:
        return prefixe + f"{duree}\u00a0minutes, et un quiz pour vérifier."

    if origine == "REVISION_DUE":
        # Le fait vient du serveur (voir raisons_de_la_seance) : « Tu as raté ce thème
        # hier. » ou « Ce thème t'a déjà posé problème. », repris tel quel.
        constat = next((r["texte"] for r in seance.get("raisons", []) if r["code"] == "echec"), None)
        constat = constat or "Ce thème t'a déjà résisté."
        return prefixe + f"{constat} " + _variante(FINS_REVISION, jour, duree=duree)

    if origine == "LECTURE_EN_COURS":
        return prefixe + f"Tu avais commencé ce cours. On finit ce qu'on a commencé : {duree}\u00a0minutes."

    if phase == "derniere_ligne_droite":
        return prefixe + f"On consolide ce thème : {duree}\u00a0minutes, sans rien de neuf."

    accroche = _accroche_frequence(seance.get("frequence"))
    if accroche:
        # Le chiffre exact ("35 sur 41 épreuves") vit dans un badge de la séance, juste
        # sous cette phrase (voir la pastille de fréquence côté frontend) - le redire ici
        # mot pour mot serait la même preuve deux fois. La phrase reste le crochet, mesuré
        # sur la part réelle des épreuves, le badge est la preuve.
        jours = (plan.get("compte_a_rebours") or {}).get("jours_restants")
        fins = FINS_FREQUENCE_LOIN if jours is not None and jours > HORIZON_LOINTAIN_JOURS else FINS_FREQUENCE_PROCHE
        # Une seule phrase : la fréquence est la raison, la durée la conséquence. Deux phrases
        # côte à côte laissaient au lecteur le soin de relier « tombe à chaque examen » à
        # « 25 minutes » (espace insécable avant les deux-points, comme pour la durée).
        return prefixe + f"Ce thème {accroche}\u00a0: " + _variante(fins, jour, duree=duree)
    if premiers_pas_eleve:
        return prefixe + f"On commence par ce thème : {duree}\u00a0minutes, et un quiz pour voir où tu en es."
    return prefixe + f"{duree}\u00a0minutes sur ce thème, et un quiz pour vérifier."
