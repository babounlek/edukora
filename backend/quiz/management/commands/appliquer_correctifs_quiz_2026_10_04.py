"""
Rejoue sur n'importe quelle base les correctifs de contenu du Mode Quiz faits le
2026-10-03/04 sur la base locale (le contenu vit en base, pas dans git) :

1. 284 figures ajoutées aux corrigés d'items existants (CompetenceItemFigure) ;
2. 19 items dont l'énoncé renvoyait à un contexte absent, réécrits (« le montage
   précédent »...) ;
3. 2 remplacements de texte ponctuels.

Les items sont retrouvés par `external_id`, jamais par id (les ids diffèrent d'une base
à l'autre). Chaque correctif n'est appliqué que si l'item est encore dans son état
d'origine : un item déjà corrigé est ignoré (idempotent), un item modifié à la main
depuis est signalé et laissé intact. Simulation par défaut ; `--apply` écrit.

Ordre conseillé en production : `reparer_caracteres_controle_maths --apply` puis cette
commande (les comparaisons tolèrent l'ordre inverse : elles passent toutes par la même
réparation des commandes LaTeX).
"""

import json
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.ingestion_repairs import _repair_control_chars_in_math, _strip_em_dash
from quiz.models import CompetenceItem, CompetenceItemFigure

DEFAULT_BUNDLE = Path(__file__).resolve().parents[2] / "data" / "correctifs_2026_10_04.json"


def _norm(text):
    """Forme comparable : mêmes réparations de commandes LaTeX que l'ingestion, fins de ligne unifiées."""
    fixed, _ = _repair_control_chars_in_math(text or "")
    return fixed.replace("\r\n", "\n").strip()


class Command(BaseCommand):
    help = "Rejoue les correctifs de contenu du Mode Quiz du 2026-10-04 (figures, énoncés réécrits). Simulation par défaut."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Écrit les corrections (sinon simulation).")
        parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE), help="Fichier JSON des correctifs.")
        parser.add_argument(
            "--images-dir", default=None,
            help="Dossier des images WebP si elles ne sont pas déjà dans le stockage "
                 "(défaut : MEDIA_ROOT/figures/cm/quiz, la copie suivie par git).",
        )

    def handle(self, *args, **options):
        self.apply = options["apply"]
        bundle_path = Path(options["bundle"])
        if not bundle_path.is_file():
            raise CommandError(f"Fichier de correctifs introuvable : {bundle_path}")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        self.images_dir = Path(options["images_dir"]) if options["images_dir"] else Path(settings.MEDIA_ROOT) / "figures" / "cm" / "quiz"

        self.stdout.write(f"Correctifs du {bundle.get('date')} - {'ÉCRITURE' if self.apply else 'simulation'}")
        self._remplacements(bundle.get("remplacements", []))
        self._reecritures(bundle.get("reecritures", []))
        self._figures(bundle.get("figures", []))

    # ------------------------------------------------------------------ remplacements
    def _remplacements(self, remplacements):
        total = 0
        for rep in remplacements:
            for champ in rep["champs"]:
                label, field = champ.rsplit(".", 1)
                model = apps.get_model(label)
                qs = model._base_manager.filter(**{f"{field}__contains": rep["old"]})
                n = qs.count()
                total += n
                if self.apply:
                    for pk, value in list(qs.values_list("pk", field)):
                        model._base_manager.filter(pk=pk).update(**{field: value.replace(rep["old"], rep["new"])})
        self.stdout.write(f"Remplacements de texte : {total} champ(s) {'corrigé(s)' if self.apply else 'à corriger'}")

    # ------------------------------------------------------------------ réécritures
    def _reecritures(self, reecritures):
        stats = {"appliquées": 0, "déjà faites": 0, "absentes": 0, "divergentes": 0}
        for r in reecritures:
            item = CompetenceItem.objects.filter(external_id=r["external_id"]).first()
            if item is None:
                stats["absentes"] += 1
                continue
            e, c = _norm(item.enonce_markdown), _norm(item.corrige_markdown)
            if e == _norm(r["enonce_apres"]) and c == _norm(r["corrige_apres"]):
                stats["déjà faites"] += 1
            elif e == _norm(r["enonce_avant"]) and c == _norm(r["corrige_avant"]):
                stats["appliquées"] += 1
                if self.apply:
                    item.enonce_markdown = _strip_em_dash(r["enonce_apres"])
                    item.corrige_markdown = _strip_em_dash(r["corrige_apres"])
                    item.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])
            else:
                stats["divergentes"] += 1
                self.stdout.write(self.style.WARNING(f"  réécriture ignorée, item modifié depuis : {r['external_id']}"))
        self.stdout.write(f"Énoncés réécrits : {stats}")

    # ------------------------------------------------------------------ figures
    def _stocker_image(self, chemin):
        """Garantit que l'image est dans le stockage par défaut (disque ou Spaces) ; retourne son nom."""
        if default_storage.exists(chemin):
            return chemin
        source = self.images_dir / Path(chemin).name
        if not source.is_file():
            raise CommandError(f"Image absente du stockage et de {self.images_dir} : {chemin}")
        return default_storage.save(chemin, ContentFile(source.read_bytes()))

    def _figures(self, figures):
        stats = {"appliquées": 0, "déjà faites": 0, "absentes": 0, "divergentes": 0}
        for f in figures:
            item = CompetenceItem.objects.filter(external_id=f["external_id"]).first()
            if item is None:
                stats["absentes"] += 1
                continue
            if item.figures.exists():
                stats["déjà faites"] += 1
                continue
            if _norm(item.corrige_markdown) != _norm(f["corrige_avant"]):
                stats["divergentes"] += 1
                self.stdout.write(self.style.WARNING(f"  figure ignorée, corrigé modifié depuis : {f['external_id']}"))
                continue
            stats["appliquées"] += 1
            if not self.apply:
                continue
            with transaction.atomic():
                corrige = f["corrige_modele"]
                for fg in f["figures"]:
                    chemin = self._stocker_image(fg["image"])
                    figure = CompetenceItemFigure.objects.create(
                        item=item, external_id=fg["id"], image=chemin,
                        type_figure=(fg.get("type") or "")[:30], legende=fg.get("legende") or "",
                        origine="ENONCE" if fg.get("origine") == "enonce" else "CORRIGE",
                    )
                    alt = figure.legende or figure.type_figure or "Figure du corrigé"
                    placeholder = re.compile(r"!\[" + re.escape(fg["id"]) + r"\]\(" + re.escape(fg["fichier"]) + r"\)")
                    corrige, n = placeholder.subn(lambda _m: f"![{alt}]({figure.image.url})", corrige)
                    if n == 0:
                        raise CommandError(f"Placeholder {fg['id']} introuvable dans le modèle de {f['external_id']}")
                item.corrige_markdown = _repair_control_chars_in_math(_strip_em_dash(corrige))[0]
                item.save(update_fields=["corrige_markdown", "updated_at"])
        self.stdout.write(f"Figures : {stats}")
