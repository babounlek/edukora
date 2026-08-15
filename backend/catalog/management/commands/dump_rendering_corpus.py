import json
import os

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Cours, Exercise, Lesson, Question
from inedit.models import EpreuveInedite, QuestionInedite
from quiz.models import CompetenceItem


class Command(BaseCommand):
    help = (
        "Dumpe en JSON tous les champs markdown de edukora réellement rendus côté "
        "élève (Lesson/Cours/Exercise/Question, quiz.CompetenceItem, "
        "inedit.EpreuveInedite/QuestionInedite), taggés par pipeline de rendu "
        "('full' = EpreuveMarkdown - preprocessing + remark-math/gfm/breaks + "
        "rehype-katex ; 'bare' = fragment inline sans preprocessing, remark-math + "
        "rehype-katex seuls, ex. texte d'un choix QCM). Voir "
        "frontend/scripts/audit-rendu.test.ts, seul consommateur prévu de ce fichier - "
        "compétence audit-qualite-rendu, étape 1."
    )

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True, help="Chemin du fichier JSON à écrire.")

    def handle(self, *args, **options):
        records = []

        for lesson in Lesson.objects.all():
            records.append(self._record("Lesson", lesson.pk, lesson.slug, "content_markdown", "full", lesson.content_markdown))

        for cours in Cours.objects.all():
            records.append(self._record("Cours", cours.pk, cours.slug, "content_markdown", "full", cours.content_markdown))

        for exercise in Exercise.objects.select_related("lesson"):
            ref = f"{exercise.lesson.slug}#{exercise.numero_exercice}"
            records.append(self._record("Exercise", exercise.pk, ref, "enonce_markdown", "full", exercise.enonce_markdown))
            records.append(self._record("Exercise", exercise.pk, ref, "corrige_markdown", "full", exercise.corrige_markdown))

        for question in Question.objects.select_related("exercise__lesson"):
            ref = f"{question.exercise.lesson.slug}#{question.exercise.numero_exercice}.{question.numero}"
            records.append(self._record("Question", question.pk, ref, "enonce_markdown", "full", question.enonce_markdown))
            records.append(self._record("Question", question.pk, ref, "corrige_markdown", "full", question.corrige_markdown))
            records.extend(self._choix_records("Question", question.pk, ref, question.choix))

        for item in CompetenceItem.objects.select_related("theme"):
            ref = f"competence:{item.theme.name}#{item.pk}"
            records.append(self._record("CompetenceItem", item.pk, ref, "enonce_markdown", "full", item.enonce_markdown))
            records.append(self._record("CompetenceItem", item.pk, ref, "corrige_markdown", "full", item.corrige_markdown))
            records.extend(self._choix_records("CompetenceItem", item.pk, ref, item.choix))

        for epreuve in EpreuveInedite.objects.all():
            records.append(self._record("EpreuveInedite", epreuve.pk, epreuve.slug, "enonce_markdown", "full", epreuve.enonce_markdown))
            records.append(self._record("EpreuveInedite", epreuve.pk, epreuve.slug, "corrige_markdown", "full", epreuve.corrige_markdown))

        for question in QuestionInedite.objects.select_related("exercice__epreuve"):
            ref = f"{question.exercice.epreuve.slug}#{question.exercice.numero_exercice}.{question.numero}"
            records.append(self._record("QuestionInedite", question.pk, ref, "enonce_markdown", "full", question.enonce_markdown))
            records.append(self._record("QuestionInedite", question.pk, ref, "corrige_markdown", "full", question.corrige_markdown))
            records.extend(self._choix_records("QuestionInedite", question.pk, ref, question.choix))

        output_path = options["output"]
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        try:
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump(records, fh, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise CommandError(f"Écriture impossible vers {output_path} : {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"{len(records)} enregistrement(s) écrits dans {output_path}."))

    @staticmethod
    def _record(model, pk, ref, field, pipeline, markdown):
        return {
            "model": model,
            "pk": pk,
            "ref": ref,
            "field": field,
            "pipeline": pipeline,
            "markdown": markdown or "",
        }

    @classmethod
    def _choix_records(cls, model, pk, ref, choix):
        """Une entrée par texte de choix QCM - fragment court rendu inline (pipeline
        'bare', voir ChoixText/CardQuestion côté frontend), jamais via EpreuveMarkdown."""
        records = []
        for entry in choix or []:
            if not isinstance(entry, dict):
                continue
            texte = entry.get("texte")
            if texte:
                lettre = entry.get("lettre", "?")
                records.append(cls._record(model, pk, f"{ref} choix {lettre}", "choix.texte", "bare", texte))
        return records
