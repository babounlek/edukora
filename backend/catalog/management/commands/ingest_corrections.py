from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from catalog.ingestion import read_ingestion_report, run_ingestion, write_ingestion_report


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
        parser.add_argument(
            "--report-json",
            help=(
                "Écrit le rapport du run dans ce fichier JSON. Utilisé par le bouton "
                "d'ingestion de l'admin, qui lance cette commande en arrière-plan et n'a "
                "donc plus la sortie console pour afficher le résultat (voir "
                "catalog.ingestion.queue_ingestion)."
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
            # run_ingestion encaisse déjà les erreurs fichier par fichier ; ce filet ne
            # couvre que ce qui la ferait échouer en bloc (dossier illisible, coupure DB).
            # Sans lui, l'admin resterait sur un rapport "running" indéfiniment, sans que
            # rien n'indique que le run est mort.
            if report_path:
                write_ingestion_report(
                    {"status": "error", "started_at": started_at.isoformat(),
                     "finished_at": timezone.now().isoformat(), "detail": str(exc)},
                    report_path,
                )
            raise

        if report_path:
            # Écrit dès la fin de l'ingestion, sans attendre les PDF : c'est le résultat
            # que l'admin attend, et la génération des PDF qui suit peut durer plusieurs
            # minutes de plus (pdf_status la suit séparément).
            write_ingestion_report(
                {
                    "status": "done",
                    "started_at": started_at.isoformat(),
                    "finished_at": timezone.now().isoformat(),
                    "files_found": report["files_found"],
                    "created": report["created"],
                    "skipped": report["skipped"],
                    "errors": report["errors"],
                    "pdf_status": "running",
                },
                report_path,
            )

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
        pdf_status = "done"
        try:
            call_command("generate_sujet_pdfs")
        except Exception:
            pdf_status = "error"
            raise
        finally:
            if report_path:
                # Relu puis réécrit plutôt que réécrit de zéro : le rapport d'ingestion
                # lui-même ne doit pas être perdu si la génération des PDF échoue (elle a
                # sa propre fragilité, Playwright - voir catalog/sujet_pdf.py), elle n'en
                # est que la suite.
                rapport_final = read_ingestion_report(report_path) or {}
                rapport_final["pdf_status"] = pdf_status
                write_ingestion_report(rapport_final, report_path)
