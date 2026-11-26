from django.core.management.base import BaseCommand, CommandError

from memos import redaction


class Command(BaseCommand):
    help = (
        "Importe des Fiches EduKora rédigées (memos/donnees/<nom>.json). Elles naissent BROUILLON : un enseignant les relit "
        "dans l'administration avant publication. Rejouable sans doublon."
    )

    def add_arguments(self, parser):
        parser.add_argument("nom", help="Nom du fichier sans .json, par exemple education_civique_lycee.")
        parser.add_argument("--dry-run", action="store_true", help="Compte sans rien enregistrer.")

    def handle(self, *args, **options):
        try:
            bilan = redaction.importer(redaction.lire(options["nom"]), dry_run=options["dry_run"])
        except redaction.FichierInvalide as exc:
            raise CommandError(str(exc))
        for titre in bilan["epreuves_absentes"]:
            self.stdout.write(self.style.WARNING(f"Épreuve introuvable : {titre}"))
        for nom in bilan["themes_absents"]:
            self.stdout.write(self.style.WARNING(f"Thème introuvable : {nom}"))
        self.stdout.write(self.style.SUCCESS(
            f"{bilan['creees']} créée(s), {bilan['completees']} complétée(s), {bilan['mises_a_jour']} mise(s) à jour, "
            f"{bilan['ignorees']} ignorée(s) faute d'épreuve."
            + (" (essai : rien enregistré)" if options["dry_run"] else "")
        ))
