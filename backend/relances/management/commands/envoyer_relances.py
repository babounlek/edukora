from django.core.management.base import BaseCommand

from relances.services import envoyer_relances_paiement, envoyer_rappels_seance


class Command(BaseCommand):
    help = (
        "Envoie les relances par e-mail : rappel quotidien de la séance du jour (pour les élèves "
        "qui l'ont activé) et relance des paiements non aboutis (deux messages au plus par "
        "tentative). À planifier par une tâche externe : une exécution par jour en fin d'après-midi "
        "suffit pour le rappel, le paiement peut tourner toutes les heures. Chaque message ne part "
        "qu'une fois quoi qu'il arrive (voir relances.models.RelanceEnvoyee)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Compte les envois sans rien envoyer.")
        parser.add_argument(
            "--seulement", choices=["rappel", "paiement"],
            help="Ne traiter qu'un seul des deux types de message.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        prefixe = "[dry-run] " if dry_run else ""
        if options["seulement"] in (None, "rappel"):
            n = envoyer_rappels_seance(dry_run=dry_run)
            self.stdout.write(self.style.SUCCESS(f"{prefixe}{n} rappel(s) de séance."))
        if options["seulement"] in (None, "paiement"):
            n = envoyer_relances_paiement(dry_run=dry_run)
            self.stdout.write(self.style.SUCCESS(f"{prefixe}{n} relance(s) de paiement."))
