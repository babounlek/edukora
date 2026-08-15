from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from inedit.ingestion import run_ingestion


class Command(BaseCommand):
    help = (
        "Ingère les fichiers JSON produits par la skill de conception d'épreuves "
        "inédites (un objet Blueprint, EpreuveInedite OU cours par fichier, champ "
        "'type' discriminant) - blueprint/épreuve en statut=BROUILLON (jamais publié "
        "automatiquement), cours publié directement, voir inedit.ingestion."
        "ingest_blueprint/ingest_epreuve_inedite/ingest_cours_inedite."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            help="Fichier JSON ou dossier ingest/_inedit/<code_pays>/... (recherche récursive).",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Chemin introuvable : {path}")

        report = run_ingestion(path)
        if report["files_found"] == 0:
            self.stdout.write(self.style.WARNING("Aucun fichier .json trouvé."))
            return

        self.stdout.write(self.style.SUCCESS(
            f"{report['blueprints_created']} blueprint(s), {report['epreuves_created']} épreuve(s) "
            f"(statut brouillon - validation manuelle requise) et {report['cours_created']} cours "
            "créé(s) (publié directement).",
        ))
        if report["skipped"]:
            self.stdout.write(f"{report['skipped']} élément(s) déjà existant(s) (external_id), ignoré(s).")
        if report["errors"]:
            self.stdout.write(self.style.ERROR(f"{len(report['errors'])} erreur(s) :"))
            for error in report["errors"]:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
