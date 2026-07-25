from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from catalog.ingestion import run_ingestion


class Command(BaseCommand):
    help = (
        "Ingère les fichiers JSON produits par la compétence correction-experte "
        "(un objet ou une liste d'objets par fichier), qu'il s'agisse d'exercices "
        "(mode automatisation) ou de cours (mode cours), en modèles brouillons. "
        "Génère aussi, en fin de traitement, le PDF du sujet pour toute leçon qui "
        "n'en a pas encore (voir generate_sujet_pdfs)."
    )

    def add_arguments(self, parser):
        parser.add_argument("path", help="Fichier JSON ou dossier contenant des fichiers .json (recherche récursive).")

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Chemin introuvable : {path}")

        report = run_ingestion(path)
        if report["files_found"] == 0:
            self.stdout.write(self.style.WARNING("Aucun fichier .json trouvé."))
            return

        self.stdout.write(self.style.SUCCESS(f"{report['created']} objet(s) créé(s)."))
        if report["skipped"]:
            self.stdout.write(f"{report['skipped']} objet(s) déjà existant(s), ignoré(s).")
        if report["errors"]:
            self.stdout.write(self.style.ERROR(f"{len(report['errors'])} erreur(s) :"))
            for error in report["errors"]:
                self.stdout.write(self.style.ERROR(f"  - {error}"))

        # Chaîné ici plutôt que laissé à une exécution manuelle séparée : les deux
        # commandes tournent déjà hors du cycle requête/réponse (jamais depuis le
        # process serveur), le seul contexte où Playwright s'est montré fiable - voir
        # catalog/sujet_pdf.py. Couvre aussi, en passant, toute leçon plus ancienne
        # restée sans PDF suite à un run précédent (filtre sujet_pdf="" par défaut).
        self.stdout.write("Génération des PDF de sujet manquants...")
        call_command("generate_sujet_pdfs")
