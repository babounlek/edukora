import re
import unicodedata

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Exercise, Question


def _exercice_anchor_id(numero_exercice):
    """Reproduit exactement frontend/src/components/EpreuveSommaire.tsx::exerciceAnchorId
    (minuscules, accents supprimés, tout non alphanumérique -> tiret) - sans ce miroir,
    le lien #exercice-... imprimé ici ne correspond pas à l'ancre réelle de la page dès
    que numero_exercice n'est pas un simple entier (ex. "Problème", "Section III")."""
    normalized = unicodedata.normalize("NFD", numero_exercice.lower())
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", stripped).strip("-")
    return f"exercice-{slug or 'sans-numero'}"


class Command(BaseCommand):
    help = (
        "Affiche le texte complet (énoncé + corrigé) de toutes les Question d'un "
        "Exercise, dans l'ordre - lecture seule, pour extraire les données déjà "
        "établies (expression de f, tangente, asymptotes, points) avant de produire "
        "une figure manquante (voir audit_traces_manquants)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--exercise", type=int, help="pk de l'Exercise.")
        parser.add_argument("--question", type=int, help="pk d'une Question de l'exercice (alternative à --exercise).")

    def handle(self, *args, **options):
        if options["question"]:
            try:
                exercise = Question.objects.select_related("exercise__lesson").get(pk=options["question"]).exercise
            except Question.DoesNotExist:
                raise CommandError(f"Question {options['question']} introuvable.")
        elif options["exercise"]:
            try:
                exercise = Exercise.objects.select_related("lesson").get(pk=options["exercise"])
            except Exercise.DoesNotExist:
                raise CommandError(f"Exercise {options['exercise']} introuvable.")
        else:
            raise CommandError("Fournir --exercise ou --question.")

        country = exercise.lesson.subject.country.code.lower()
        self.stdout.write(
            f"=== {exercise.lesson.epreuve_source or exercise.lesson.title} - Exercice {exercise.numero_exercice} (pk={exercise.pk}) ===\n"
            f"Lien de vérification : http://localhost/{country}/epreuves/{exercise.lesson.slug}/lire#{_exercice_anchor_id(exercise.numero_exercice)}\n",
        )
        if exercise.enonce_intro_markdown:
            self.stdout.write(f"--- Préambule ---\n{exercise.enonce_intro_markdown}\n")

        for question in exercise.questions.order_by("ordre"):
            self.stdout.write(f"\n--- Question {question.numero} (pk={question.pk}) - ÉNONCÉ ---\n{question.enonce_markdown}")
            self.stdout.write(f"\n--- Question {question.numero} (pk={question.pk}) - CORRIGÉ ---\n{question.corrige_markdown}")

        self.stdout.write(f"\n\nFigures déjà attachées : {[(f.external_id, f.origine, f.legende) for f in exercise.figures.all()]}")
