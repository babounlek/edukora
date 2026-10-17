"""
Renseigne Exercise.points des épreuves GCE (Paper 2 et 3) où il est resté vide à l'ingestion.

Sans points d'exercice lisibles, la simulation (voir simulations.cadre.charger_exercices) donne le même
poids à chaque exercice : la note n'est plus sur les points du Board. Or les points de chaque question
sont déjà là (Question.points, « (3 marks) » du sujet, relevés à l'ingestion) : le total de l'exercice en
est la somme. Cette commande l'écrit, jamais plus que ça :

  - seulement les exercices VALIDES dont Exercise.points est vide ou illisible (jamais un total saisi) ;
  - seulement si TOUTES les questions de l'exercice portent leurs points (sinon on n'invente pas un
    total tronqué : l'exercice est listé comme ignoré) ;
  - seulement les Paper 2 et 3 (le Paper 1 est noté question par question, à 1 point).
  - dans un groupe à règle « ou » (un seul jeu de sous-questions à traiter), le total est celui du jeu le
    plus rémunérateur, pas la somme des deux ; l'exercice est alors listé « à relire ».

Le rapport donne le total de chaque épreuve touchée. Une colonne « à relire » signale les exercices où la
somme des marques lues dans les énoncés (« (3 marks) », « [3 marks] ») ne retombe pas sur la somme des
points : Question.points reste la source, ce signal sert à un relecteur humain, rien d'autre.

Idempotente (un exercice déjà renseigné n'est plus touché) et rejouable en production, APRÈS l'ingestion
des épreuves GCE : les JSON source ne portent pas ces totaux.

    python manage.py completer_points_gce                 # simulation (annulée), affiche le rapport
    python manage.py completer_points_gce --appliquer     # écrit Exercise.points
"""
import re
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import EXAMENS_GCE, Exercise, Lesson, LessonType, StatutContenu
from inedit.notation import parse_points

PAPERS_CONCERNES = (2, 3)
_MARQUES = re.compile(r"(?:\(\s*|\[\s*)(\d+(?:[.,]\d+)?)\s*marks?\s*(?:\)|\])", re.IGNORECASE)


def _texte(total):
    return str(int(total)) if total == total.to_integral_value() else str(total.normalize())


def _marques_lues(questions):
    return sum((Decimal(m.replace(",", ".")) for q in questions for m in _MARQUES.findall(q.enonce_markdown or "")), Decimal(0))


def _repere(texte):
    return " ".join(str(texte).split()).casefold()


def _total(exercice, questions, lesson):
    """(total, jeux). Total = somme des points des questions ; sauf dans un groupe à règle « ou »
    (l'élève ne traite QU'UN des jeux de sous-questions, ex. a-b-c ou d-e-f) : la somme compterait les
    deux jeux, le total est celui du jeu qui rapporte le plus, plus les questions communes. `jeux` :
    les totaux de chaque jeu (vide hors règle « ou »)."""
    groupes = {_repere(g) for g in exercice.groupes or []}
    for regle in lesson.regles_choix or []:
        if regle.get("type") != "ou" or _repere(regle.get("portee", "")) not in groupes:
            continue
        appartenance = {_repere(s): i for i, jeu in enumerate(regle["options"]) for s in jeu}
        communs = Decimal(0)
        par_jeu = [Decimal(0) for _ in regle["options"]]
        for question in questions:
            i = appartenance.get(_repere(question.numero))
            if i is None:
                communs += question.points
            else:
                par_jeu[i] += question.points
        jeux = [communs + p for p in par_jeu]
        return max(jeux), jeux
    return Decimal(sum(q.points for q in questions)), []


class Command(BaseCommand):
    help = "Renseigne Exercise.points (somme de Question.points) des épreuves GCE Paper 2/3 - voir la docstring du module."

    def add_arguments(self, parser):
        parser.add_argument("--appliquer", action="store_true", help="Écrire Exercise.points (sinon : simulation).")

    @transaction.atomic
    def handle(self, *args, **options):
        appliquer = options["appliquer"]
        lessons = (
            Lesson.objects.filter(
                lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, numero_paper__in=PAPERS_CONCERNES,
                cursus__examen__in=EXAMENS_GCE,
            )
            .distinct()
            .order_by("title")
        )
        completes = ignores = relire = epreuves = 0
        for lesson in lessons:
            exercices = list(Exercise.objects.filter(lesson=lesson, statut=StatutContenu.VALIDE).prefetch_related("questions"))
            total = Decimal(0)
            faits, laisses, a_relire = [], [], []
            for exercice in exercices:
                propres = parse_points(exercice.points)
                if propres > 0:
                    total += propres
                    continue
                questions = list(exercice.questions.all())
                if not questions or any(q.points is None for q in questions):
                    laisses.append(exercice.numero_exercice)
                    continue
                somme, jeux = _total(exercice, questions, lesson)
                total += somme
                faits.append(exercice.numero_exercice)
                lues = _marques_lues(questions)
                if jeux and len(set(jeux)) > 1:
                    a_relire.append(f"{exercice.numero_exercice} (règle « ou » : jeux de {', '.join(map(str, jeux))} points, {somme} retenus)")
                elif not jeux and lues > 0 and lues != somme:
                    a_relire.append(f"{exercice.numero_exercice} ({somme} points, {lues} lus)")
                if appliquer:
                    exercice.points = _texte(somme)
                    exercice.save(update_fields=["points"])
            if not faits and not laisses:
                continue
            epreuves += 1
            completes += len(faits)
            ignores += len(laisses)
            relire += len(a_relire)
            ligne = f"{lesson.title} : total {_texte(total)}, {len(faits)} complété(s)"
            if laisses:
                ligne += f", {len(laisses)} ignoré(s) (points manquants : exercices {', '.join(laisses)}) - total INCOMPLET"
            self.stdout.write(ligne)
            if a_relire:
                self.stdout.write(f"    à relire : {'; '.join(a_relire)}")
        self.stdout.write(
            f"{completes} exercice(s) complété(s) dans {epreuves} épreuve(s), {ignores} ignoré(s), {relire} à relire.",
        )
        if not appliquer:
            self.stdout.write("(simulation : rien n'a été écrit)")
