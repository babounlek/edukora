from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from quiz.ingestion import run_ingestion


class Command(BaseCommand):
    help = (
        "Ingère les fichiers JSON produits par le skill concepteur-quiz-competence "
        "(un tableau de CompetenceItem par fichier) en items statut=VALIDE - publiés "
        "et servables en Quiz immédiatement, sans revue humaine préalable (voir "
        "quiz.ingestion.ingest_competence_item)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            help="Fichier JSON ou dossier ingest/_quiz/<code_pays>/... (recherche récursive).",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Chemin introuvable : {path}")

        report = run_ingestion(path)
        if report["files_found"] == 0:
            self.stdout.write(self.style.WARNING("Aucun fichier .json trouvé."))
            return

        self.stdout.write(self.style.SUCCESS(f"{report['created']} item(s) créé(s) (statut validé)."))
        if report["skipped"]:
            self.stdout.write(f"{report['skipped']} item(s) déjà existant(s) (external_id), ignoré(s).")
        if report["errors"]:
            self.stdout.write(self.style.ERROR(f"{len(report['errors'])} erreur(s) :"))
            for error in report["errors"]:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
