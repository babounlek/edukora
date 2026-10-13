from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from catalog.ingestion import write_ingestion_report
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

        parser.add_argument(
            "--report-json",
            help=(
                "Écrit le rapport du run dans ce fichier JSON. Utilisé par le bouton "
                "d'ingestion de l'admin, qui lance cette commande en arrière-plan (un "
                "passage complet de ingest/_quiz dépasse le --timeout 30 de gunicorn)."
            ),
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        report_path = options["report_json"]
        if not path.exists():
            if report_path:
                write_ingestion_report(
                    {"status": "error", "finished_at": timezone.now().isoformat(),
                     "detail": f"Chemin introuvable : {path}"},
                    report_path,
                )
            raise CommandError(f"Chemin introuvable : {path}")

        started_at = timezone.now()
        try:
            report = run_ingestion(path)
        except Exception as exc:
            if report_path:
                write_ingestion_report(
                    {"status": "error", "started_at": started_at.isoformat(),
                     "finished_at": timezone.now().isoformat(), "detail": str(exc)},
                    report_path,
                )
            raise

        if report_path:
            write_ingestion_report(
                {
                    "status": "done",
                    "started_at": started_at.isoformat(),
                    "finished_at": timezone.now().isoformat(),
                    "files_found": report["files_found"],
                    "created": report["created"],
                    "skipped": report["skipped"],
                    "errors": report["errors"],
                },
                report_path,
            )

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
