import json

from django.apps import apps
from django.core.management.base import BaseCommand

from catalog.ingestion_repairs import _repair_control_chars_in_math

APPS = ("catalog", "quiz", "inedit", "fiches", "programme")


class Command(BaseCommand):
    help = (
        "Restaure les backslash perdus des commandes LaTeX (\\ne, \\neq, \\times, \\text, "
        "\\nu...) lus à l'ingestion comme échappements JSON (saut de ligne, tabulation...) "
        "dans le contenu DÉJÀ en base - voir catalog.ingestion_repairs."
        "_repair_control_chars_in_math, la même réparation que l'ingestion applique "
        "désormais. Simulation par défaut ; --apply écrit."
    )

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Écrit les corrections (sinon simulation).")

    def handle(self, *args, **options):
        apply = options["apply"]
        rows = 0
        per_model = {}
        for model in apps.get_models():
            if model._meta.app_label not in APPS:
                continue
            names = [
                f.name for f in model._meta.get_fields()
                if getattr(f, "concrete", False) and f.get_internal_type() in ("TextField", "JSONField")
            ]
            if not names:
                continue
            # _base_manager : les managers « visibles » (Cours.objects...) masquent les
            # brouillons et dépubliés, qui doivent être réparés eux aussi.
            manager = model._base_manager
            for obj in manager.all().only("pk", *names).iterator(chunk_size=500):
                updates = {}
                for name in names:
                    value = getattr(obj, name)
                    if not value:
                        continue
                    fixed, changed = _repair_control_chars_in_math(value)
                    if changed:
                        updates[name] = fixed
                if not updates:
                    continue
                rows += 1
                per_model[model._meta.label] = per_model.get(model._meta.label, 0) + 1
                if apply:
                    # update() : pas d'auto_now, pas de signaux - le contenu corrigé
                    # n'est pas une modification éditoriale.
                    manager.filter(pk=obj.pk).update(**updates)

        verbe = "corrigées" if apply else "à corriger (simulation, --apply pour écrire)"
        self.stdout.write(f"{rows} ligne(s) {verbe}")
        self.stdout.write(json.dumps(per_model, ensure_ascii=False, indent=1))
