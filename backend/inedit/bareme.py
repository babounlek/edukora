"""
Contrôles du barème par question d'une épreuve inédite (QuestionInedite.points et
criteres_notation) - partagés par l'ingestion (contenu neuf), la commande de
rétro-remplissage et le contrôle de complétude d'une épreuve publiée.

Trois invariants, dans cet ordre :
1. Les critères d'une question ouverte (grille de notation) totalisent exactement ses points.
2. Un exercice dont une question porte un barème les porte TOUTES : un barème à moitié
   renseigné ferait deviner le reste à la plateforme, ce qui est précisément le « barème
   estimé » que ce contrôle sert à faire disparaître.
3. La somme des questions d'un exercice égale les points de l'exercice.

Tout est en Decimal (voir inedit.notation pour la raison) ; la tolérance d'un centième
n'absorbe que l'arrondi de saisie, jamais une vraie erreur de barème.
"""

from decimal import Decimal, InvalidOperation

from catalog.models import StatutContenu, TypeReponse

from .notation import POINTS_ANNONCES, ZERO, parse_points, points_annonces

TOLERANCE = Decimal("0.01")


def lire_points(valeur, contexte):
    """Points strictement positifs (nombre, ou texte « 1,5 ») - ValueError sinon."""
    try:
        points = Decimal(str(valeur).strip().replace(",", "."))
    except InvalidOperation:
        raise ValueError(f"{contexte} : points illisibles ({valeur!r}).") from None
    if not points.is_finite() or points <= 0:
        raise ValueError(f"{contexte} : les points doivent être supérieurs à 0 (reçu {valeur!r}).")
    return points


def normaliser_criteres(criteres, contexte):
    """[{libelle, points}] validé et normalisé (points numériques) - [] si absent."""
    if not criteres:
        return []
    if not isinstance(criteres, list):
        raise ValueError(f"{contexte} : criteres_notation doit être une liste.")
    normalises = []
    for indice, critere in enumerate(criteres, start=1):
        if not isinstance(critere, dict):
            raise ValueError(f"{contexte} : critère {indice} invalide (objet {{libelle, points}} attendu).")
        libelle = str(critere.get("libelle") or "").strip()
        if not libelle:
            raise ValueError(f"{contexte} : critère {indice} sans libelle.")
        points = lire_points(critere.get("points"), f"{contexte}, critère {indice}")
        normalises.append({"libelle": libelle, "points": float(points)})
    return normalises


def verifier_question(points, criteres, type_reponse, contexte):
    """Cohérence points/critères d'UNE question."""
    if criteres and type_reponse == TypeReponse.QCM:
        raise ValueError(f"{contexte} : une QCM se corrige tout ou rien, sans grille de critères.")
    if criteres and points is None:
        raise ValueError(f"{contexte} : criteres_notation sans points pour la question.")
    if criteres:
        total = sum((Decimal(str(c["points"])) for c in criteres), ZERO)
        if abs(total - points) > TOLERANCE:
            raise ValueError(f"{contexte} : les critères totalisent {total} pt alors que la question vaut {points}.")


def verifier_exercice(points_exercice, points_par_numero, contexte):
    """Barème d'un exercice : tout ou rien, puis somme = points de l'exercice.
    `points_par_numero` : {numero de question: Decimal ou None}."""
    renseignes = [p for p in points_par_numero.values() if p is not None]
    if not renseignes:
        return
    manquantes = [n for n, p in points_par_numero.items() if p is None]
    if manquantes:
        raise ValueError(f"{contexte} : barème absent pour les questions {manquantes} (tout ou rien par exercice).")
    total = sum(renseignes, ZERO)
    budget = parse_points(points_exercice)
    if budget and abs(total - budget) > TOLERANCE:
        raise ValueError(f"{contexte} : les questions totalisent {total} pt, l'exercice en annonce {budget}.")


def _annonce_coherente(annonce, questions_a_partir_d_ici):
    """Une mention « (4 points) » dans l'énoncé est le barème de CETTE question, ou le total
    d'une sous-partie ou d'une situation-problème annoncé en tête de sa première question
    (« Situation 1 (8 points) » suivie de deux questions à 5 et 3 points) : on l'accepte si
    elle égale la somme de cette question et des suivantes consécutives. Sans cette
    tolérance le contrôle refuserait des sujets parfaitement corrects, ou forcerait à
    mettre 0 point aux questions suivantes."""
    cumul = ZERO
    for question in questions_a_partir_d_ici:
        if question.points is None:
            return False
        cumul += question.points
        if abs(cumul - annonce) <= TOLERANCE:
            return True
        if cumul > annonce:
            return False
    return False


def verifier_epreuve(epreuve, *, exiger_complet=True):
    """Anomalies de barème d'une épreuve enregistrée - liste de messages, vide si conforme.
    exiger_complet : signale aussi les questions sans barème (état d'avant rétro-remplissage)."""
    anomalies = []
    for exercice in epreuve.exercices.prefetch_related("questions").order_by("numero_exercice"):
        contexte = f"{epreuve.external_id or epreuve.pk}, exercice {exercice.numero_exercice}"
        questions = list(exercice.questions.all())
        try:
            for question in questions:
                verifier_question(
                    question.points, question.criteres_notation, question.type_reponse,
                    f"{contexte}, question {question.numero}",
                )
            verifier_exercice(exercice.points, {q.numero: q.points for q in questions}, contexte)
        except ValueError as exc:
            anomalies.append(str(exc))
            continue
        if exiger_complet and any(q.points is None for q in questions):
            anomalies.append(f"{contexte} : barème par question absent.")
        for indice, question in enumerate(questions):
            annonce = points_annonces(question)
            if question.points is None or annonce is None:
                continue
            if not _annonce_coherente(annonce, questions[indice:]):
                anomalies.append(
                    f"{contexte}, question {question.numero} : l'énoncé annonce {annonce} pt, "
                    f"le barème enregistré est {question.points}.",
                )
    return anomalies


def verifier_epreuves_validees(*, exiger_complet=True):
    """{external_id: [anomalies]} pour toutes les épreuves publiées non conformes."""
    from .models import EpreuveInedite

    resultat = {}
    for epreuve in EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE).order_by("id"):
        anomalies = verifier_epreuve(epreuve, exiger_complet=exiger_complet)
        if anomalies:
            resultat[epreuve.external_id or str(epreuve.pk)] = anomalies
    return resultat


__all__ = [
    "POINTS_ANNONCES", "lire_points", "normaliser_criteres", "verifier_question",
    "verifier_exercice", "verifier_epreuve", "verifier_epreuves_validees",
]
