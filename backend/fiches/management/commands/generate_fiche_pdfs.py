from django.core.management.base import BaseCommand

from fiches.models import FicheGeneree, StatutGeneration
from fiches.pdf import save_fiche_pdfs


class Command(BaseCommand):
    help = (
        "Génère (hors ligne) les PDF sujet+corrigé d'une fiche répétiteur - déclenchée "
        "par fiches.views.create_fiche via queue_fiche_pdf_generation. Ne tourne jamais "
        "dans le cycle d'une requête HTTP."
    )

    def add_arguments(self, parser):
        parser.add_argument("--fiche", type=int, required=True, help="Id de la FicheGeneree à traiter.")

    def handle(self, *args, **options):
        try:
            fiche = FicheGeneree.objects.get(pk=options["fiche"])
        except FicheGeneree.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Fiche #{options['fiche']} introuvable."))
            return

        try:
            save_fiche_pdfs(fiche)
        except Exception as exc:
            FicheGeneree.objects.filter(pk=fiche.pk).update(statut=StatutGeneration.ECHEC)
            self.stdout.write(self.style.ERROR(f"Fiche #{fiche.pk} : échec de génération - {exc}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Fiche #{fiche.pk} : PDF sujet+corrigé générés."))
