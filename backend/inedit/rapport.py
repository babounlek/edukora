"""
Rapport de fin d'épreuve : ce que la note ne dit pas - où sont partis les points, où est passé
le temps, comment l'élève se situe. Des fonctions PURES sur des lignes simples (une par
question, ou par exercice pour une épreuve officielle), pour que les épreuves inédites et les
simulations d'épreuves officielles produisent exactement le même rapport.

Une « ligne » : {exercice, points, obtenus, traitee, cause, quand} - `quand` est l'instant où
l'élève a déclaré traiter la question (ou None).
"""

from decimal import Decimal

from .notation import ZERO, en_nombre

# Effectif minimal pour situer un élève parmi les autres : en dessous, un « top 10 % » ne
# reposerait que sur quelques personnes et n'apprendrait rien de fiable.
EFFECTIF_MIN_COMPARAISON = 20

# Une question laissée de côté n'a pas de cause déclarée : c'est en soi la cause.
NON_TRAITEE = "NON_TRAITEE"
NON_PRECISEE = "NON_PRECISEE"

LIBELLES_CAUSES = {
    NON_TRAITEE: "Questions non traitées",
    "TEMPS": "Manque de temps",
    "CONNAISSANCE": "Notion à revoir",
    "METHODE": "Erreur de méthode",
    "CALCUL": "Erreur de calcul",
    "INATTENTION": "Inattention à l'énoncé",
    NON_PRECISEE: "Cause non précisée",
}


def pertes_par_cause(lignes, unite="question"):
    """Points perdus, regroupés par cause, du plus lourd au plus léger.
    Renvoie {total_perdu, causes: [{cause, libelle, points, part}]}. `unite` : ce que compte une
    ligne (« question » pour une épreuve inédite, « exercice » pour une annale officielle)."""
    libelles = dict(LIBELLES_CAUSES)
    if unite == "exercice":
        libelles[NON_TRAITEE] = "Exercices non traités"
    par_cause = {}
    for ligne in lignes:
        perdu = ligne["points"] - ligne["obtenus"]
        if perdu <= 0:
            continue
        if ligne["cause"]:
            cause = ligne["cause"]
        elif not ligne["traitee"]:
            cause = NON_TRAITEE
        else:
            cause = NON_PRECISEE
        par_cause[cause] = par_cause.get(cause, ZERO) + perdu

    total = sum(par_cause.values(), ZERO)
    causes = [
        {
            "cause": cause,
            "libelle": libelles.get(cause, cause),
            "points": en_nombre(points),
            "part": round(100 * points / total) if total else 0,
        }
        for cause, points in sorted(par_cause.items(), key=lambda item: item[1], reverse=True)
    ]
    return {"total_perdu": en_nombre(total), "causes": causes}


def temps_par_exercice(lignes, debut):
    """Temps passé par exercice, estimé depuis les instants où l'élève a coché ses questions :
    l'intervalle qui précède chaque case est attribué à l'exercice de cette question. Une
    estimation - il n'y a pas de chronomètre par question - mais elle suffit à montrer un
    exercice qui a englouti la moitié du temps pour peu de points.

    None quand l'estimation n'aurait aucun sens : pas de chrono (entraînement libre), ou moins
    de trois questions cochées."""
    if debut is None:
        return None
    evenements = sorted((ligne["quand"], ligne["exercice"]) for ligne in lignes if ligne["quand"] is not None)
    if len(evenements) < 3:
        return None

    secondes = {}
    precedent = debut
    for quand, exercice in evenements:
        intervalle = max((quand - precedent).total_seconds(), 0)
        secondes[exercice] = secondes.get(exercice, 0) + intervalle
        precedent = quand

    points = {}
    for ligne in lignes:
        points[ligne["exercice"]] = points.get(ligne["exercice"], ZERO) + ligne["points"]
    total_secondes = sum(secondes.values()) or 1
    total_points = sum(points.values(), ZERO) or Decimal(1)

    resultat = []
    for exercice in dict.fromkeys(ligne["exercice"] for ligne in lignes):
        part_temps = round(100 * secondes.get(exercice, 0) / total_secondes)
        part_points = round(100 * points.get(exercice, ZERO) / total_points)
        resultat.append({
            "numero_exercice": exercice,
            "secondes": int(secondes.get(exercice, 0)),
            "part_du_temps": part_temps,
            "part_des_points": part_points,
        })
    return resultat


def exercice_chronophage(temps):
    """L'exercice qui a pris nettement plus de temps qu'il ne rapportait de points, s'il y en a
    un : au moins 15 points de pourcentage d'écart ET 30 % du temps au moins."""
    if not temps:
        return None
    pire = max(temps, key=lambda ligne: ligne["part_du_temps"] - ligne["part_des_points"])
    ecart = pire["part_du_temps"] - pire["part_des_points"]
    return pire["numero_exercice"] if ecart >= 15 and pire["part_du_temps"] >= 30 else None


def situer(ma_note, notes_des_autres, minimum=EFFECTIF_MIN_COMPARAISON):
    """{effectif, percentile, moyenne} - ou None sous l'effectif minimal.
    `notes_des_autres` : une note par autre candidat (sa meilleure), en points."""
    notes = [Decimal(str(n)) for n in notes_des_autres]
    if len(notes) < minimum:
        return None
    dessous = sum(1 for n in notes if n < ma_note)
    egales = sum(1 for n in notes if n == ma_note)
    return {
        "effectif": len(notes) + 1,
        # Les égalités comptent pour moitié : deux élèves à la même note n'ont pas battu l'autre.
        "percentile": round(100 * (dessous + egales / 2) / len(notes)),
        "moyenne": en_nombre(sum(notes, ZERO) / len(notes)),
    }


__all__ = [
    "EFFECTIF_MIN_COMPARAISON", "LIBELLES_CAUSES", "NON_PRECISEE", "NON_TRAITEE", "exercice_chronophage",
    "pertes_par_cause", "situer", "temps_par_exercice",
]
