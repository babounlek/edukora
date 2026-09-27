"""
L'épreuve officielle vue comme le voit inedit.notation : des « exercices » contenant des
« questions ». Ici chaque exercice contient UNE seule question notable, l'exercice lui-même -
ce qui permet de réutiliser tel quel le calcul de la note (barème, non traité = 0, répartition)
et le rapport de fin d'épreuve des épreuves inédites, sans les dupliquer ni les modifier.
"""

import re
from collections import Counter

from catalog import rendering
from catalog.models import Lesson, LessonType, StatutContenu
from inedit import notation

_DUREE_HEURES = re.compile(r"(\d+)\s*(?:h|heures?)\s*(\d{1,2})?", re.IGNORECASE)
_DUREE_MINUTES = re.compile(r"(\d+)\s*(?:mn|min|minutes?)\b", re.IGNORECASE)
NOMBRE_DE_THEMES_PAR_EXERCICE = 3

# Une durée déduite des autres sessions n'est retenue que si elle est unanime, ou si au moins
# ACCORD_MINIMAL des FENETRE_RECENTE dernières années CONNUES s'accordent - jamais la valeur la
# plus récente prise seule : une session isolée dont la durée diffère de tout l'historique est
# presque toujours une faute de saisie dans l'en-tête source, pas un vrai changement de barème
# (ex. Physique BAC C à 4h depuis des années, "1h" sur la seule session la plus récente).
FENETRE_RECENTE_ANNEES = 3
ACCORD_MINIMAL = 2


def duree_minutes(texte):
    """« 3h », « 1h30 », « 2 heures », « 45 mn » -> minutes ; None si illisible ou absent.
    L'en-tête d'une annale est du texte libre : mieux vaut ne pas proposer de chrono que
    de deviner une durée."""
    texte = (texte or "").strip()
    if not texte:
        return None
    heures = _DUREE_HEURES.search(texte)
    if heures:
        return int(heures.group(1)) * 60 + int(heures.group(2) or 0)
    minutes = _DUREE_MINUTES.search(texte)
    return int(minutes.group(1)) if minutes else None


def _duree_connue_du_groupe(*, country_id, examen, subject_id, series_id, nature_epreuve, partie_epreuve_francais, exclude_pk):
    """Durée déduite des AUTRES annales du même (pays, examen, matière, série, nature d'épreuve,
    partie) - None si aucune n'est assez fiable (voir le commentaire sur FENETRE_RECENTE_ANNEES).
    Le regroupement doit être fin : matière+examen seuls mélangent l'épreuve pratique (souvent
    1h) et théorique (souvent 3h) d'une même matière, ou les séries d'un même examen, qui n'ont
    pas la même durée (Maths BAC C : 4h, BAC A : 2h)."""
    candidats = (
        Lesson.objects.visibles()
        .filter(
            subject_id=subject_id, lesson_type=LessonType.CORR, nature_epreuve=nature_epreuve,
            partie_epreuve_francais=partie_epreuve_francais, cursus__country_id=country_id,
            cursus__examen=examen, cursus__series_id=series_id,
        )
        .exclude(pk=exclude_pk)
        .distinct()
    )
    par_annee = {}
    for lesson in candidats:
        minutes = duree_minutes(lesson.duree_epreuve)
        if minutes is None:
            continue
        # Deux annales de la même année qui divergent (rare) : la plus fréquente cette année-là.
        par_annee.setdefault(lesson.year or 0, Counter())[minutes] += 1
    if not par_annee:
        return None

    valeur_par_annee = {annee: compte.most_common(1)[0][0] for annee, compte in par_annee.items()}
    if len(set(valeur_par_annee.values())) == 1:
        return next(iter(valeur_par_annee.values()))

    annees_recentes = sorted(valeur_par_annee, reverse=True)[:FENETRE_RECENTE_ANNEES]
    compte_recent = Counter(valeur_par_annee[annee] for annee in annees_recentes)
    valeur, effectif = compte_recent.most_common(1)[0]
    return valeur if effectif >= ACCORD_MINIMAL else None


def duree_minutes_pour_lesson(lesson):
    """(minutes, estimee) : la durée propre de l'épreuve si elle est lisible ; sinon déduite des
    autres sessions du même groupe (voir _duree_connue_du_groupe) - seulement si TOUS les cursus
    de cette épreuve s'accordent sur la même valeur déduite (une annale qui vise plusieurs séries
    aux durées historiquement différentes n'a pas de durée unique à inférer). (None, False) sinon :
    mieux vaut aucun chrono qu'un chrono faux."""
    propre = duree_minutes(lesson.duree_epreuve)
    if propre is not None:
        return propre, False

    cursus_list = list(lesson.cursus.all())
    if not cursus_list:
        return None, False

    deduites = {
        _duree_connue_du_groupe(
            country_id=cursus.country_id, examen=cursus.examen, subject_id=lesson.subject_id,
            series_id=cursus.series_id, nature_epreuve=lesson.nature_epreuve,
            partie_epreuve_francais=lesson.partie_epreuve_francais, exclude_pk=lesson.pk,
        )
        for cursus in cursus_list
    }
    deduites.discard(None)
    if len(deduites) == 1:
        return next(iter(deduites)), True
    return None, False


class _Liste:
    """Ce que fait `manager.all()` pour inedit.notation : rendre les éléments."""

    def __init__(self, elements):
        self._elements = elements

    def all(self):
        return self._elements


class QuestionExercice:
    """Un exercice entier, présenté comme une unique question ouverte dont le barème est celui de
    l'exercice - explicite quand tous les exercices ont des points lisibles, sinon à estimer - et
    sans énoncé (sinon inedit.notation croirait lire un « (1 pt) » de sous-question comme barème)."""

    type_reponse = "OUVERTE"
    criteres_notation = ()
    enonce_markdown = ""

    def __init__(self, exercise, themes, points):
        self.pk = exercise.pk
        self.numero = exercise.numero_exercice
        self.themes = _Liste(themes)
        self.points = points


class ExerciceAdapte:
    def __init__(self, exercise, contenu, points, themes):
        self.id = exercise.pk
        self.numero_exercice = exercise.numero_exercice
        self.points = points
        self.groupes = contenu.get("groupes", [])
        self.enonce_intro_markdown = contenu.get("enonce_intro_markdown", "")
        self.enonce_markdown = contenu.get("enonce_markdown", "")
        self.corrige_markdown = contenu.get("corrige_markdown", "")
        explicite = notation.parse_points(points) if points else None
        self.questions = _Liste([QuestionExercice(exercise, themes, explicite)])


def _themes_principaux(exercise):
    """Les thèmes que l'exercice travaille VRAIMENT : Exercise.themes cumule ceux de toutes
    ses sous-questions (jusqu'à 24 pour un exercice), or faire revenir 24 thèmes en séance du
    jour pour un exercice raté serait absurde. On garde les plus fréquents."""
    frequences = Counter()
    par_id = {}
    for question in exercise.questions.all():
        for theme in question.themes.all():
            frequences[theme.pk] += 1
            par_id[theme.pk] = theme
    if frequences:
        return [par_id[pk] for pk, _ in frequences.most_common(NOMBRE_DE_THEMES_PAR_EXERCICE)]
    return list(exercise.themes.all())[:NOMBRE_DE_THEMES_PAR_EXERCICE]


def charger_exercices(lesson):
    """[ExerciceAdapte] dans l'ordre de l'épreuve. Le barème n'est celui des exercices que si
    TOUS ont des points lisibles : sinon chaque exercice pèse autant (barème estimé), plutôt
    qu'une note sur un total tronqué."""
    contenus = rendering.lesson_exercises_breakdown(lesson)
    par_id = {
        e.pk: e
        for e in lesson.exercises.filter(statut=StatutContenu.VALIDE).prefetch_related("themes", "questions__themes")
    }
    exercises = [par_id[c["id"]] for c in contenus if c["id"] in par_id]
    tous_lisibles = bool(exercises) and all(notation.parse_points(e.points) > 0 for e in exercises)
    contenus_par_id = {c["id"]: c for c in contenus}
    return [
        ExerciceAdapte(
            e, contenus_par_id[e.pk], e.points if tous_lisibles else "", _themes_principaux(e),
        )
        for e in exercises
    ]
