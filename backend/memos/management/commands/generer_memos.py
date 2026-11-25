from django.core.management.base import BaseCommand, CommandError

from catalog.models import Subject
from memos import extraction


class Command(BaseCommand):
    help = (
        "Propose des Fiches EduKora à partir des définitions déjà rédigées dans les corrigés d'une matière. "
        "Les fiches naissent BROUILLON : un enseignant les relit dans l'administration avant publication."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", default="CM")
        parser.add_argument("--matiere", required=True, help="Code de la matière, par exemple EDUCATION_CIVIQUE.")
        parser.add_argument("--dry-run", action="store_true", help="Affiche le relevé sans rien enregistrer.")

    def handle(self, *args, **options):
        subject = Subject.objects.filter(country__code__iexact=options["pays"], code=options["matiere"]).first()
        if subject is None:
            raise CommandError("Matière introuvable pour ce pays.")
        relevees = extraction.relever(subject)
        if options["dry_run"]:
            for n in relevees:
                annees = ", ".join(str(s["annee"]) for s in n["sessions"])
                self.stdout.write(f"- {n['terme']} ({annees}) : {n['definition'][:90]}")
            self.stdout.write(f"{len(relevees)} notion(s) relevée(s), rien enregistré.")
            return
        bilan = extraction.enregistrer(subject, relevees)
        self.stdout.write(self.style.SUCCESS(
            f"{bilan['creees']} créée(s), {bilan['mises_a_jour']} mise(s) à jour, {bilan['laissees']} laissée(s) à l'admin."
        ))
