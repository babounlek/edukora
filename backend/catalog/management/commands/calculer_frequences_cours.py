import time

from django.core.management.base import BaseCommand

from catalog.frequences_cours import recalculer_cursus
from catalog.models import Cursus


class Command(BaseCommand):
    help = (
        "Reconstruit catalog.FrequenceCours : les cours qui tombent souvent à l'examen de chaque cursus "
        "(badge et filtre « Tombe souvent » du catalogue de cours). À lancer après un lot d'ingestion ou "
        "une campagne de tags (fusions, alias) : la table n'est pas mise à jour au fil des enregistrements. "
        "scripts/ingerer_et_valider.sh le fait à la fin d'un lot validé ; un cron nocturne sert de filet."
    )

    def add_arguments(self, parser):
        parser.add_argument("--cursus", nargs="+", type=int, help="Ne recalculer que ces cursus (id).")

    def handle(self, *args, **options):
        cursus_qs = Cursus.objects.filter(country__actif=True).select_related("series", "country")
        if options["cursus"]:
            cursus_qs = cursus_qs.filter(pk__in=options["cursus"])
        debut = time.monotonic()
        total = 0
        for cursus in cursus_qs:
            par_matiere = recalculer_cursus(cursus)
            nombre = sum(par_matiere.values())
            total += nombre
            if nombre:
                detail = ", ".join(f"{code} {n}" for code, n in sorted(par_matiere.items()))
                self.stdout.write(f"{cursus.examen} {cursus.series.code if cursus.series else '-'} (#{cursus.pk}) : {nombre} cours ({detail})")
        self.stdout.write(self.style.SUCCESS(f"Terminé en {time.monotonic() - debut:.1f} s : {total} cours fréquents."))
