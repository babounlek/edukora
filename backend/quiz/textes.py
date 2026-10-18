"""
Textes que le SERVEUR écrit lui-même pour l'élève : la phrase du coach de l'accueil, les raisons d'une séance,
les libellés d'étape. Ils dépendent de chiffres que seul le serveur a (durée, jours, score), donc le frontend ne
peut pas les traduire après coup.

Le français est la référence : ses formulations sont celles que les tests existants vérifient, mot pour mot. La langue
est celle du cursus visé (`Cursus.langue`, dérivée de l'examen : anglais pour le GCE) - la règle produit « l'examen
visé fixe la langue » - jamais devinée d'un texte. Une clé ou une langue inconnue retombe sur le français plutôt que
de lever : un libellé en français vaut mieux qu'une erreur sur l'accueil.

Le français met une espace insécable avant « : » et entre un nombre et « minutes » ; l'anglais n'en met pas.
"""

NBSP = " "

FR, EN = "fr", "en"

# Libellés de `Seance.origine`, affichés quand une séance n'a ni thème ni savoir (voir OrigineSeance).
ORIGINES = {
    "REVISION_DUE": {FR: "Révision due", EN: "Due for review"},
    "LECTURE_EN_COURS": {FR: "Lecture en cours", EN: "Reading in progress"},
    "DIAGNOSTIC": {FR: "Calibrage", EN: "Calibration"},
    "PARCOURS": {FR: "Parcours", EN: "Pathway"},
}

TEXTES = {
    # --- Phrase du coach (quiz.accueil.phrase_coach) ---
    "coach.apres": {
        FR: "L'examen est passé. Tout ce que tu as travaillé reste à toi.",
        EN: "The exam is over. Everything you worked on stays with you.",
    },
    "coach.jour_j": {
        FR: "C'est aujourd'hui. Respire : le travail est fait, il ne reste qu'à le montrer.",
        EN: "It's today. Breathe: the work is done, all that's left is to show it.",
    },
    "coach.veille": {
        FR: "C'est demain. Ce soir, on ne découvre rien : on relit, et on dort tôt.",
        EN: "It's tomorrow. Tonight we learn nothing new: we review, and go to bed early.",
    },
    "coach.fait_score": {
        FR: "Séance faite, {reussies} sur {total} au quiz. Demain, on continue.",
        EN: "Session done, {reussies} out of {total} in the quiz. Tomorrow, we continue.",
    },
    "coach.fait": {
        FR: "Séance faite. Demain, on continue.",
        EN: "Session done. Tomorrow, we continue.",
    },
    "coach.rien": {
        FR: "Rien à te proposer aujourd'hui : choisis un thème toi-même, on te suit.",
        EN: "Nothing to suggest today: pick a topic yourself, we'll follow you.",
    },
    "coach.retour_reprise": {
        FR: "Content de te revoir. On reprend en douceur. ",
        EN: "Good to see you again. Let's ease back in. ",
    },
    "coach.retour": {FR: "Content de te revoir. ", EN: "Good to see you again. "},
    "coach.derniere_ligne": {FR: "Dernière ligne droite. ", EN: "Final stretch. "},
    "coach.diagnostic": {
        FR: "Quinze questions pour situer ton niveau. Ensuite, chaque séance sera taillée pour toi.",
        EN: "Fifteen questions to find your level. After that, every session will be tailored to you.",
    },
    "coach.sans_theme": {
        FR: "{duree}" + NBSP + "minutes, et un quiz pour vérifier.",
        EN: "{duree} minutes, and a quiz to check.",
    },
    "coach.echec_defaut": {FR: "Ce thème t'a déjà résisté.", EN: "This topic has already given you trouble."},
    # Entre le constat d'échec et la durée : « … hier : 25 minutes pour … ».
    "coach.deux_points": {FR: NBSP + ": ", EN: ": "},
    "coach.lecture": {
        FR: "Tu avais commencé ce cours. On finit ce qu'on a commencé : {duree}" + NBSP + "minutes.",
        EN: "You had started this course. We finish what we start: {duree} minutes.",
    },
    "coach.consolider": {
        FR: "On consolide ce thème : {duree}" + NBSP + "minutes, sans rien de neuf.",
        EN: "We consolidate this topic: {duree} minutes, nothing new.",
    },
    "coach.frequence": {FR: "Ce thème {accroche}" + NBSP + ": ", EN: "This topic {accroche}: "},
    "coach.premiers_pas": {
        FR: "On commence par ce thème : {duree}" + NBSP + "minutes, et un quiz pour voir où tu en es.",
        EN: "We start with this topic: {duree} minutes, and a quiz to see where you stand.",
    },
    "coach.defaut": {
        FR: "{duree}" + NBSP + "minutes sur ce thème, et un quiz pour vérifier.",
        EN: "{duree} minutes on this topic, and a quiz to check.",
    },
    # --- Raisons d'une séance (quiz.services.raisons_de_la_seance) ---
    "raison.calibrage": {
        FR: "On ne sait pas encore où tu en es - ces questions servent à le situer.",
        EN: "We don't know yet where you stand - these questions are there to find out.",
    },
    "raison.coefficient": {
        FR: "{matiere} est coefficient {valeur} à ton examen.",
        EN: "{matiere} has coefficient {valeur} in your exam.",
    },
    "raison.objectif": {
        FR: "Tu as choisi de te concentrer sur {matiere} jusqu'au {date}.",
        EN: "You chose to focus on {matiere} until {date}.",
    },
    "raison.echec": {FR: "Tu as raté ce thème {quand}.", EN: "You got this topic wrong {quand}."},
    "raison.echec_aujourdhui": {FR: "aujourd'hui", EN: "today"},
    "raison.echec_hier": {FR: "hier", EN: "yesterday"},
    "raison.echec_jours": {FR: "il y a {jours} jours", EN: "{jours} days ago"},
    "raison.echec_defaut": {FR: "Ce thème t'a déjà posé problème.", EN: "This topic has already given you trouble."},
    "raison.lecture": {
        FR: "Tu as ouvert ce cours il y a moins de deux jours.",
        EN: "You opened this course less than two days ago.",
    },
    "raison.maitrise": {
        FR: "Tu réussis déjà ce thème : on passe directement à la pratique.",
        EN: "You already do well on this topic: we go straight to practice.",
    },
    "raison.jamais": {FR: "Tu ne l'as encore jamais travaillé.", EN: "You have never worked on it yet."},
    # --- Libellés d'étape (quiz.services.libelle_etape) ---
    "etape.cours": {FR: "Relire la méthode", EN: "Review the method"},
    "etape.diagnostic": {FR: "{n} questions pour situer ton niveau", EN: "{n} questions to find your level"},
    "etape.quiz": {FR: "{n} questions", EN: "{n} questions"},
    "etape.exercice": {FR: "Exercice {numero} - {titre}", EN: "Exercise {numero} - {titre}"},
    "etape.exercice_verrouille": {FR: "Un exercice tombé à l'examen", EN: "An exercise from a past exam"},
}

# Formulations qui tournent d'un jour à l'autre (voir quiz.accueil._variante) : le choix ne dépend que de la date.
ACCROCHES_FREQUENCE = {
    FR: (
        "tombe presque à chaque examen",
        "tombe à l'examen plus d'une fois sur deux",
        "tombe régulièrement à l'examen",
    ),
    EN: (
        "comes up at almost every exam",
        "comes up in more than half of the exams",
        "comes up regularly at the exam",
    ),
}
FINS_FREQUENCE_PROCHE = {
    FR: (
        "{duree}" + NBSP + "minutes pour ne pas le découvrir le jour J.",
        "{duree}" + NBSP + "minutes pour l'avoir en main le jour J.",
        "{duree}" + NBSP + "minutes pour arriver prêt le jour J.",
    ),
    EN: (
        "{duree} minutes so you don't discover it on exam day.",
        "{duree} minutes to have it in hand on exam day.",
        "{duree} minutes to arrive ready on exam day.",
    ),
}
FINS_FREQUENCE_LOIN = {
    FR: (
        "{duree}" + NBSP + "minutes pour prendre de l'avance.",
        "{duree}" + NBSP + "minutes pour qu'il ne te surprenne pas.",
        "{duree}" + NBSP + "minutes aujourd'hui, c'est autant que tu n'auras pas à rattraper plus tard.",
    ),
    EN: (
        "{duree} minutes to get ahead.",
        "{duree} minutes so it doesn't catch you off guard.",
        "{duree} minutes today is that much you won't have to catch up on later.",
    ),
}
FINS_REVISION = {
    FR: (
        "{duree}" + NBSP + "minutes pour le fixer avant qu'il ne s'efface.",
        "{duree}" + NBSP + "minutes pour qu'il reste en mémoire.",
        "{duree}" + NBSP + "minutes pour le rendre solide.",
    ),
    EN: (
        "{duree} minutes to lock it in before it fades.",
        "{duree} minutes to keep it in memory.",
        "{duree} minutes to make it solid.",
    ),
}


def langue_de(cursus):
    """'fr' ou 'en' : la langue du cursus visé (`Cursus.langue`), français à défaut de cursus."""
    if cursus is None:
        return FR
    valeur = getattr(cursus.langue, "value", cursus.langue)
    return valeur if valeur in (FR, EN) else FR


def texte(cle, langue=FR, **valeurs):
    """Le texte `cle` dans `langue` (français si elle manque), avec ses valeurs substituées."""
    variantes = TEXTES[cle]
    return variantes.get(langue, variantes[FR]).format(**valeurs)


def variantes(table, langue=FR):
    """Les formulations d'une table (FINS_*, ACCROCHES_FREQUENCE) dans `langue`, français par défaut."""
    return table.get(langue, table[FR])


def origine(code, langue=FR):
    """Libellé de `Seance.origine` dans `langue` ; le code lui-même s'il est inconnu."""
    libelles = ORIGINES.get(code)
    return libelles.get(langue, libelles[FR]) if libelles else code
