"""
Rattache Question.savoir_officiel a posteriori, pour du contenu déjà ingéré AVANT que
ce champ n'existe dans le JSON source (voir la section savoir_officiel du skill
correction-experte, et catalog.ingestion._resolve_savoir_officiel pour la résolution
elle-même). Relit les fichiers JSON sous BASE_DIR/ingest, retrouve l'Exercise déjà en
base via ingest_exercise (idempotent par défaut - ne modifie ni ne recrée un Exercise
existant, on ne se sert que de la valeur de retour) puis complète les Question dont
savoir_officiel est encore NULL.

Ne touche jamais une Question déjà rattachée, à la main ou par une ingestion
antérieure - même règle que _link_tags_to_savoir (voir Tag.savoir_officiel) : un
rattachement déjà là prime toujours sur ce que dit le fichier source.

    python manage.py backfill_question_savoir_officiel            # applique
    python manage.py backfill_question_savoir_officiel --dry-run  # simule seulement
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import IngestionError, _resolve_savoir_officiel, ingest_exercise


class Command(BaseCommand):
    help = "Rattache Question.savoir_officiel depuis le JSON source, pour le contenu déjà ingéré."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="N'écrit rien, affiche seulement ce qui serait rattaché.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        ingest_dir = Path(settings.BASE_DIR) / "ingest"
        rattachees = 0

        for json_path in sorted(ingest_dir.rglob("*.json")):
            try:
                raw = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue

            objets = raw if isinstance(raw, list) else [raw]
            for data in objets:
                if not isinstance(data, dict) or not data.get("questions"):
                    continue
                if not any(q.get("savoir_officiel") for q in data["questions"]):
                    continue

                try:
                    exercise, created = ingest_exercise(dict(data), source_dir=json_path.parent)
                except IngestionError as exc:
                    self.stdout.write(self.style.WARNING(f"  {json_path} : ignoré ({exc})"))
                    continue
                if created:
                    # Le backfill ne doit jamais être la première ingestion d'un
                    # exercice - un fichier qui en arrive là n'était pas encore en
                    # base pour une autre raison, hors du périmètre de cette commande.
                    continue

                questions = list(exercise.questions.order_by("ordre"))
                for question, q_data in zip(questions, data["questions"]):
                    if question.savoir_officiel_id is not None:
                        continue
                    ref = q_data.get("savoir_officiel")
                    if not ref:
                        continue
                    try:
                        savoir = _resolve_savoir_officiel(ref, exercise.lesson.subject)
                    except IngestionError as exc:
                        self.stdout.write(self.style.WARNING(
                            f"  {json_path} : question {question.numero} ignorée ({exc})",
                        ))
                        continue
                    if savoir is None:
                        continue

                    self.stdout.write(f"  {json_path} : question {question.numero} -> {savoir}")
                    rattachees += 1
                    if not dry_run:
                        with transaction.atomic():
                            question.savoir_officiel = savoir
                            question.save(update_fields=["savoir_officiel"])

        suffixe = " (dry-run, rien n'a été écrit)" if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"{rattachees} question(s) rattachée(s){suffixe}."))
