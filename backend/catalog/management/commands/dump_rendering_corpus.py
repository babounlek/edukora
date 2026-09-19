import json
import os

from django.core.management.base import BaseCommand, CommandError

from catalog.tunnel import collect_rendering_records, parse_since


class Command(BaseCommand):
    help = (
        "Dumpe en JSON tous les champs markdown de edukora réellement rendus côté "
        "élève (Lesson/Cours/Exercise/Question, quiz.CompetenceItem, "
        "inedit.EpreuveInedite/QuestionInedite), taggés par pipeline de rendu "
        "('full' = EpreuveMarkdown - preprocessing + remark-math/gfm/breaks + "
        "rehype-katex ; 'bare' = fragment inline sans preprocessing, remark-math + "
        "rehype-katex seuls, ex. texte d'un choix QCM). Voir "
        "frontend/src/lib/audit-rendu.test.ts, seul consommateur prévu de ce fichier - "
        "compétence audit-qualite-rendu, étape 1. --since restreint aux contenus "
        "créés/modifiés récemment (tunnel post-ingestion)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True, help="Chemin du fichier JSON à écrire.")
        parser.add_argument(
            "--since", default=None,
            help="Ne dumper que le contenu modifié depuis : 90m, 2h, 1d ou datetime ISO. Défaut : corpus entier.",
        )

    def handle(self, *args, **options):
        try:
            since = parse_since(options["since"]) if options["since"] else None
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        records = collect_rendering_records(since)

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
