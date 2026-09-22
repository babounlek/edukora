import re
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from catalog.ingestion import _compress_figure_image
from catalog.models import Figure, OrigineFigure, Question

_FIG_ID_RE = re.compile(r"^fig-(\d+)$")


class Command(BaseCommand):
    help = (
        "Attache une figure déjà produite (PNG sur disque) au corrigé d'une Question "
        "précise : crée le Figure (origine=CORRIGE), ajoute le placeholder à la fin de "
        "son corrige_markdown, puis recompile Exercise et Lesson. Complément mécanique "
        "à l'audit_traces_manquants - le travail mathématique (produire le bon tracé) "
        "reste fait en amont, cette commande ne fait que l'attacher correctement."
    )

    def add_arguments(self, parser):
        parser.add_argument("--question", type=int, required=True, help="pk de la Question à corriger.")
        parser.add_argument("--image", help="Chemin du PNG produit (dans le conteneur) - requis sauf avec --reuse-figure.")
        parser.add_argument("--legende", help="Légende courte de la figure - requis sauf avec --reuse-figure.")
        parser.add_argument(
            "--type", default="courbe",
            choices=["figure geometrique", "courbe", "tableau", "schema", "document", "carte", "graphique"],
        )
        parser.add_argument("--non-indispensable", action="store_true", help="Marque la figure comme non indispensable (défaut : indispensable).")
        parser.add_argument(
            "--reuse-figure",
            help="external_id (ex. fig-1) d'une Figure déjà attachée au MÊME exercice - "
                 "réutilise l'image existante (figure partagée par plusieurs sous-questions) "
                 "au lieu d'en créer une nouvelle.",
        )

    def handle(self, *args, **options):
        try:
            question = Question.objects.select_related("exercise", "exercise__lesson").get(pk=options["question"])
        except Question.DoesNotExist:
            raise CommandError(f"Question {options['question']} introuvable.")

        exercise = question.exercise

        if options["reuse_figure"]:
            try:
                figure = exercise.figures.get(external_id=options["reuse_figure"])
            except Figure.DoesNotExist:
                raise CommandError(f"Figure {options['reuse_figure']!r} introuvable sur l'exercice {exercise.pk}.")
        else:
            if not options["image"] or not options["legende"]:
                raise CommandError("--image et --legende sont requis sauf avec --reuse-figure.")
            image_path = Path(options["image"])
            if not image_path.is_file():
                raise CommandError(f"Fichier image introuvable : {image_path}")

            existing_numbers = [
                int(m.group(1))
                for f in exercise.figures.all()
                if (m := _FIG_ID_RE.match(f.external_id))
            ]
            fig_id = f"fig-{max(existing_numbers, default=0) + 1}"

            compressed_bytes, stored_filename = _compress_figure_image(image_path.read_bytes(), image_path.name)

            figure = Figure.objects.create(
                exercise=exercise,
                external_id=fig_id,
                image=ContentFile(compressed_bytes, name=stored_filename),
                page_source=None,
                type_figure=options["type"],
                legende=options["legende"],
                indispensable=not options["non_indispensable"],
                lisibilite="bonne",
                origine=OrigineFigure.CORRIGE,
            )

        alt_text = figure.legende or figure.type_figure
        placeholder = f"\n\n![{alt_text}]({figure.image.url})\n"
        question.corrige_markdown = (question.corrige_markdown or "").rstrip() + placeholder
        question.save(update_fields=["corrige_markdown", "updated_at"])

        exercise.compile_from_questions()
        exercise.lesson.compile_from_exercises()

        self.stdout.write(self.style.SUCCESS(
            f"{figure.external_id} attachée à Question {question.pk} (Exercice {exercise.pk}) : {figure.image.url}",
        ))
