"""
Aligne `Lesson.nature_epreuve` sur la valeur portée par les JSON source.

Une ré-ingestion classique ne suffit pas : `run_ingestion` est idempotente et
n'retouche jamais un Exercise déjà importé, donc une valeur ajoutée après coup dans
le JSON ne redescend jamais en base. C'était le cas des 4 seules épreuves marquées
PRATIQUE au 2026-08-15 : la valeur ne vivait QU'en base (posée à la main depuis
l'admin), et aurait disparu à la première ré-ingestion réelle.

Ne remplit que ce que le JSON affirme : une épreuve dont le JSON ne dit rien garde sa
valeur actuelle, y compris vide - "vide" signifie "distinction non applicable à cette
matière ou non déterminable", jamais "pas encore regardé" (voir Lesson.nature_epreuve).

    python manage.py synchroniser_nature_epreuve            # simulation
    python manage.py synchroniser_nature_epreuve --apply
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.ingestion import IngestionError, _resolve_nature_epreuve
from catalog.models import Lesson, LessonType

INGEST_DIR = Path(settings.BASE_DIR) / "ingest"


class Command(BaseCommand):
    help = "Reporte en base le champ nature_epreuve des JSON source (théorique/pratique)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Écrit réellement les valeurs (sans cette option : simulation seule).",
        )

    def handle(self, *args, **options):
        appliquer = options["apply"]
        self.stdout.write(self.style.MIGRATE_HEADING(
            "APPLICATION" if appliquer else "SIMULATION (relancer avec --apply pour écrire)",
        ))

        modifiees = 0
        lessons = (
            Lesson.objects.filter(lesson_type=LessonType.CORR)
            .exclude(epreuve_source="")
            .select_related("subject__country")
        )
        for lesson in lessons:
            nom = lesson.epreuve_source.removesuffix(".pdf")
            dossier = INGEST_DIR / lesson.subject.country.code.lower() / nom
            if not dossier.is_dir():
                continue

            valeurs = set()
            for fichier in sorted(dossier.glob(f"{nom}_exercice_*.json")):
                try:
                    brut = json.loads(fichier.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                for data in brut if isinstance(brut, list) else [brut]:
                    if isinstance(data, dict) and data.get("nature_epreuve"):
                        valeurs.add(data["nature_epreuve"])

            if not valeurs:
                continue
            if len(valeurs) > 1:
                self.stdout.write(self.style.WARNING(
                    f"  {nom} : valeurs contradictoires entre exercices {sorted(valeurs)} - ignorée.",
                ))
                continue

            try:
                nature = _resolve_nature_epreuve(valeurs.pop())
            except IngestionError as exc:
                self.stdout.write(self.style.WARNING(f"  {nom} : {exc}"))
                continue

            if nature == lesson.nature_epreuve:
                continue
            ancienne = lesson.nature_epreuve or "(vide)"
            self.stdout.write(f"  {nom:50s} {ancienne} -> {nature}")
            modifiees += 1
            if appliquer:
                lesson.nature_epreuve = nature
                lesson.save(update_fields=["nature_epreuve", "updated_at"])

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{modifiees} leçon(s) mise(s) à jour."))
