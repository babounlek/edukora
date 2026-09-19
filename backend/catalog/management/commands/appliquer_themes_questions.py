"""
Ajoute des thèmes aux Question qui n'en ont AUCUN, depuis un fichier {"<pk>": ["thème", ...]}
(produit par la campagne « questions sans thème », voir le tunnel de validation :
`valider_ingestion` bloque toute Question sans thème).

Additif et idempotent : ne touche jamais une Question qui a déjà au moins un thème,
réutilise un Tag existant (correspondance exacte, puis insensible à la casse, via
`_resolve_or_create_tag`) avant d'en créer un.

    python manage.py appliquer_themes_questions /app/ingest/_audit/themes_out_<slug>.json --dry-run
    python manage.py appliquer_themes_questions /app/ingest/_audit/themes_out_<slug>.json
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from catalog.ingestion import IngestionError, _get_or_create_tags
from catalog.models import Question, Tag
from catalog.tunnel import tag_key


class Command(BaseCommand):
    help = "Ajoute des thèmes aux Question sans aucun thème, depuis un JSON {pk: [thèmes]}."

    def add_arguments(self, parser):
        parser.add_argument("fichier")
        parser.add_argument("--dry-run", action="store_true", help="N'écrit rien, affiche le bilan.")

    def handle(self, *args, **options):
        try:
            mapping = json.loads(Path(options["fichier"]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CommandError(f"Lecture impossible de {options['fichier']} : {exc}") from exc
        if not isinstance(mapping, dict):
            raise CommandError("Format attendu : {\"<pk>\": [\"thème\", ...]}.")

        # Un thème proposé qui n'existe pas tel quel mais dont la clé (accents/casse/pluriel/
        # tirets, voir tunnel.tag_key) correspond à un Tag existant reprend la forme du
        # Tag le plus utilisé : c'est ce qui évite de recréer des quasi-doublons.
        par_cle = {}
        for tag in Tag.objects.annotate(n=Count("questions_as_theme") + Count("cours")).order_by("n", "id"):
            par_cle[tag_key(tag.name)] = tag.name
        existants = set(Tag.objects.values_list("name", flat=True))

        def canonique(theme):
            theme = theme.strip()
            if theme in existants:
                return theme
            forme = par_cle.setdefault(tag_key(theme), theme)
            return forme

        appliquees = ignorees = 0
        nouveaux = set()
        with transaction.atomic():
            for pk, themes in mapping.items():
                if not isinstance(themes, list) or not (1 <= len(themes) <= 6) or not all(isinstance(t, str) for t in themes):
                    raise CommandError(f"Question {pk} : 1 à 6 thèmes texte attendus, reçu {themes!r}.")
                question = Question.objects.filter(pk=int(pk)).first()
                if question is None or question.themes.exists():
                    ignorees += 1
                    continue
                try:
                    tags = _get_or_create_tags(list(dict.fromkeys(canonique(t) for t in themes)))
                except IngestionError as exc:
                    raise CommandError(f"Question {pk} : {exc}") from exc
                question.themes.add(*tags)
                nouveaux.update(t.name for t in tags)
                appliquees += 1
            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(
            f"{'Simulé' if options['dry_run'] else 'Appliqué'} : {appliquees} question(s) complétée(s), "
            f"{ignorees} ignorée(s) (déjà thématisées ou introuvables).",
        )
