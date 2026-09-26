"""
Note d'une TentativeInedite sur le barème réel de l'épreuve.

Règles (voir aussi les champs QuestionInedite.points/criteres_notation et
TentativeReponse.traitee_at/points_obtenus) :

- Le dénominateur est TOUJOURS le barème complet, questions non traitées incluses : une
  question jamais traitée vaut zéro. L'ancien score (bonnes réponses / réponses données)
  donnait 100 % à un élève qui n'avait traité que les trois questions faciles.
- Barème d'une question, par ordre de priorité : `points` renseigné (ou somme de ses
  critères de notation) ; sinon le barème annoncé dans son énoncé (« ... (1 pt) »), tant
  qu'il reste cohérent avec le total de l'exercice ; sinon les points restants de
  l'exercice répartis à parts égales. Ce dernier repli est signalé « barème estimé » à
  l'élève, jamais présenté comme exact.
- Points obtenus : QCM tout ou rien ; question ouverte = somme des critères cochés, ou
  saisie directe (par quarts de point) quand la question n'a pas de critères, ou - pour
  les réponses enregistrées avant l'introduction du barème - conversion de
  resultat_declare (réussi = tout, partiel = moitié, échec = rien).

Tout est calculé en Decimal : additionner des flottants ferait dériver la note
(3 x 1,33 != 4) et les tests d'égalité avec le barème du Blueprint deviendraient fragiles.
"""

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from catalog.models import TypeReponse

ZERO = Decimal("0")
CENTIEME = Decimal("0.01")
QUART = Decimal("0.25")
PARTIEL_FRACTION = Decimal("0.5")


def parse_points(texte):
    """Points d'un exercice, saisis en texte libre ("4", "2,5", " 10 ") - 0 si illisible."""
    try:
        valeur = Decimal(str(texte or "").strip().replace(",", "."))
    except InvalidOperation:
        return ZERO
    return valeur if valeur.is_finite() and valeur > 0 else ZERO


def arrondi(valeur):
    return valeur.quantize(CENTIEME, rounding=ROUND_HALF_UP)


def en_nombre(valeur):
    """Decimal -> float pour le JSON (2 décimales), None reste None."""
    return None if valeur is None else float(arrondi(valeur))


# « (1 pt) », « (1,5 point) », « (2 pts) » en fin d'énoncé : le barème que l'élève lit sur
# son sujet. Sur les épreuves validées, quand toutes les questions d'un exercice en portent un,
# leur somme égale toujours les points de l'exercice - mais un énoncé isolé peut citer
# des points sans être notable, d'où la vérification de cohérence dans points_par_question.
POINTS_ANNONCES = re.compile(r"\(\s*(\d+(?:[.,]\d+)?)\s*(?:pts?|points?)\s*\)", re.IGNORECASE)


def points_annonces(question):
    """Barème annoncé dans l'énoncé de la question (dernière mention), ou None."""
    mentions = POINTS_ANNONCES.findall(question.enonce_markdown or "")
    return parse_points(mentions[-1]) if mentions else None


def points_explicites(question):
    """Barème exact d'une question, ou None si à estimer."""
    if question.points is not None:
        return question.points
    if question.criteres_notation:
        total = sum((Decimal(str(c.get("points", 0))) for c in question.criteres_notation), ZERO)
        if total > 0:
            return total
    return None


def _repartir(total, nombre):
    """Répartit `total` en `nombre` parts, sans reste : par quarts de point quand c'est
    possible (1,5 + 1,25 + 1,25 pour 4 points sur 3 questions), sinon au centième."""
    if nombre == 0:
        return []
    for pas in (QUART, CENTIEME):
        unites = total / pas
        if unites != unites.to_integral_value():
            continue
        unites = int(unites)
        if unites < nombre and pas == QUART:
            continue
        base, reste = divmod(unites, nombre)
        return [(base + (1 if i < reste else 0)) * pas for i in range(nombre)]
    # Total non multiple du centième (saisie exotique) : arrondi, le reste va à la dernière.
    part = (total / nombre).quantize(CENTIEME, rounding=ROUND_HALF_UP)
    parts = [part] * nombre
    parts[-1] = total - part * (nombre - 1)
    return parts


def points_par_question(exercices):
    """{question.pk: (points, estime)} pour une épreuve. `exercices` : itérable
    d'ExerciceInedite dont `questions` est idéalement préchargé."""
    resultat = {}
    for exercice in exercices:
        questions = list(exercice.questions.all())
        budget = parse_points(exercice.points)
        fixes = {q.pk: points_explicites(q) for q in questions}
        annonces = {q.pk: points_annonces(q) for q in questions if fixes[q.pk] is None}
        annonces = {pk: p for pk, p in annonces.items() if p}
        total_connu = sum((p for p in fixes.values() if p is not None), ZERO) + sum(annonces.values(), ZERO)
        if not budget or total_connu <= budget:
            fixes.update(annonces)
        deja = sum((p for p in fixes.values() if p is not None), ZERO)
        sans_bareme = [q for q in questions if fixes[q.pk] is None]
        reste = max(budget - deja, ZERO)
        parts = _repartir(reste, len(sans_bareme))
        for question in questions:
            if fixes[question.pk] is not None:
                resultat[question.pk] = (fixes[question.pk], False)
        for question, part in zip(sans_bareme, parts):
            resultat[question.pk] = (part, True)

    if resultat and all(p == 0 for p, _ in resultat.values()):
        # Aucun point lisible nulle part : chaque question pèse 1, estimé. Mieux qu'une
        # note sur 0, qui n'a aucun sens pour l'élève.
        resultat = {pk: (Decimal("1"), True) for pk in resultat}
    return resultat


def est_traitee(question, reponse):
    if reponse is None:
        return False
    if question.type_reponse == TypeReponse.QCM:
        return bool(reponse.reponse_choisie)
    return bool(reponse.traitee_at or reponse.points_obtenus is not None or reponse.resultat_declare)


def est_notee(question, reponse):
    """Une question QCM est notée dès qu'elle est traitée ; une question ouverte, une fois
    ses points attribués (ou son ancien resultat_declare converti)."""
    if not est_traitee(question, reponse):
        return False
    if question.type_reponse == TypeReponse.QCM:
        return True
    return reponse.points_obtenus is not None or bool(reponse.resultat_declare)


def points_obtenus(question, reponse, points):
    if reponse is None or not est_notee(question, reponse):
        return ZERO
    if question.type_reponse == TypeReponse.QCM:
        return points if reponse.est_correcte else ZERO
    if reponse.points_obtenus is not None:
        return min(reponse.points_obtenus, points)
    if reponse.resultat_declare == "REUSSI":
        return points
    if reponse.resultat_declare == "PARTIEL":
        return arrondi(points * PARTIEL_FRACTION)
    return ZERO


def resultat_declare_depuis_points(obtenus, points):
    """Valeur de compatibilité pour TentativeReponse.resultat_declare (lue par
    est_correcte et les statistiques de révision) : tout = réussi, rien = échec."""
    if points > 0 and obtenus >= points:
        return "REUSSI"
    if obtenus <= 0:
        return "ECHEC"
    return "PARTIEL"


def calculer(tentative, exercices):
    """Bilan complet d'une tentative. `exercices` : queryset/itérable d'ExerciceInedite
    de l'épreuve (questions et thèmes idéalement préchargés)."""
    exercices = list(exercices)
    par_question = points_par_question(exercices)
    reponses = {r.question_id: r for r in tentative.reponses.all()}

    note = ZERO
    bareme = ZERO
    estime = False
    traitees = a_noter = reussies = total = 0
    par_exercice = []
    par_theme = {}

    for exercice in exercices:
        exo_bareme = exo_note = ZERO
        for question in exercice.questions.all():
            points, est_estime = par_question[question.pk]
            reponse = reponses.get(question.pk)
            obtenus = points_obtenus(question, reponse, points)
            traitee = est_traitee(question, reponse)

            total += 1
            bareme += points
            note += obtenus
            exo_bareme += points
            exo_note += obtenus
            estime = estime or est_estime
            traitees += traitee
            a_noter += traitee and not est_notee(question, reponse)
            entier = points > 0 and obtenus >= points
            reussies += entier

            for theme in question.themes.all():
                stats = par_theme.setdefault(
                    theme.name, {"points_possibles": ZERO, "points_obtenus": ZERO, "total": 0, "reussies": 0},
                )
                stats["points_possibles"] += points
                stats["points_obtenus"] += obtenus
                stats["total"] += 1
                stats["reussies"] += entier

        par_exercice.append({
            "numero_exercice": exercice.numero_exercice,
            "points_possibles": exo_bareme,
            "points_obtenus": exo_note,
        })

    return {
        "note": note,
        "bareme": bareme,
        "bareme_estime": estime,
        "questions_total": total,
        "questions_traitees": traitees,
        "questions_non_traitees": total - traitees,
        "questions_a_noter": a_noter,
        "questions_reussies": reussies,
        "par_exercice": par_exercice,
        "par_theme": par_theme,
    }


def score_pourcentage(note, bareme):
    return round(100 * note / bareme) if bareme else None


def note_sur_20(note, bareme):
    return arrondi(note * 20 / bareme) if bareme else None


def resume(tentative, bilan):
    """Bloc `notation` exposé à l'élève - jamais avant que le corrigé soit disponible :
    la note inclut les QCM, elle trahirait leur correction pendant le mode examen."""
    return {
        "note": en_nombre(bilan["note"]),
        "bareme": en_nombre(bilan["bareme"]),
        "note_sur_20": en_nombre(note_sur_20(bilan["note"], bilan["bareme"])),
        "bareme_estime": bilan["bareme_estime"],
        "questions_total": bilan["questions_total"],
        "questions_traitees": bilan["questions_traitees"],
        "questions_non_traitees": bilan["questions_non_traitees"],
        "questions_a_noter": bilan["questions_a_noter"],
        # Définitive seulement une fois l'épreuve rendue ET toutes les questions traitées notées.
        "definitive": tentative.submitted_at is not None and bilan["questions_a_noter"] == 0,
    }


def enregistrer_note(tentative, bilan):
    """Persiste note/barème/score sur la tentative (voir TentativeInedite.note_obtenue)."""
    tentative.note_obtenue = arrondi(bilan["note"])
    tentative.bareme_snapshot = arrondi(bilan["bareme"])
    tentative.score_obtenu = score_pourcentage(bilan["note"], bilan["bareme"])
    tentative.save(update_fields=["note_obtenue", "bareme_snapshot", "score_obtenu"])


def points_depuis_criteres(question, indices):
    """Somme des critères cochés. Lève ValueError si un indice est invalide."""
    criteres = question.criteres_notation
    if not isinstance(indices, list) or len(set(indices)) != len(indices):
        raise ValueError("criteres_valides doit être une liste d'indices distincts.")
    total = ZERO
    for indice in indices:
        if isinstance(indice, bool) or not isinstance(indice, int) or not 0 <= indice < len(criteres):
            raise ValueError(f"Critère inconnu : {indice!r}.")
        total += Decimal(str(criteres[indice].get("points", 0)))
    return total
