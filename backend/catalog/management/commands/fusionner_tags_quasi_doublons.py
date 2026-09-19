"""
Fusionne les `Tag` quasi-doublons : même nom aux accents, à la casse, aux tirets et au
pluriel simple près (ex. "elimination" / "élimination", "Lois de Kepler" / "loi de Kepler"),
clé de rapprochement `catalog.tunnel.tag_key`. Prolonge `fusionner_tags_doublons`, qui ne
traitait que la casse et les espaces.

Un groupe dont les Tag pointent vers un `savoir_officiel` DIFFÉRENT n'est jamais fusionné
(même règle que `fusionner_tags_doublons`, listé pour arbitrage). Le survivant est le Tag
qui porte un `savoir_officiel` si un seul en a un, sinon celui qui a le plus de contenu lié ;
si un autre membre du groupe est la même forme AVEC les accents, le survivant en prend
l'orthographe. Chaque groupe est fusionné dans un savepoint : une contrainte d'unicité
(ex. un même élève déjà lié aux deux thèmes) saute le groupe sans bloquer les autres.

    python manage.py fusionner_tags_quasi_doublons            # simulation
    python manage.py fusionner_tags_quasi_doublons --apply
"""

import unicodedata
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from catalog.management.commands.fusionner_tags_doublons import _merge_relations, _related_count
from catalog.models import Tag
from catalog.tunnel import tag_key


def _accent_fold(name):
    decomposed = unicodedata.normalize("NFKD", name)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def _accent_count(name):
    return sum(1 for c in unicodedata.normalize("NFKD", name) if unicodedata.combining(c))


class Command(BaseCommand):
    help = "Fusionne les Tag quasi-doublons (accents, casse, tirets, pluriel simple)."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Écrit réellement les fusions (sinon simulation).")

    def handle(self, *args, **options):
        appliquer = options["apply"]

        groupes = defaultdict(list)
        for tag in Tag.objects.order_by("id"):
            groupes[tag_key(tag.name)].append(tag)
        groupes = [tags for tags in groupes.values() if len(tags) > 1]

        conflits, sautes, fusionnes, supprimes = [], [], 0, 0
        for tags in groupes:
            savoirs = {t.savoir_officiel_id for t in tags if t.savoir_officiel_id is not None}
            if len(savoirs) > 1:
                conflits.append(tags)
                continue

            avec_savoir = [t for t in tags if t.savoir_officiel_id is not None]
            survivant = avec_savoir[0] if len(avec_savoir) == 1 else max(tags, key=lambda t: (_related_count(t), -t.id))
            perdants = [t for t in tags if t.id != survivant.id]
            meilleure_forme = max(
                (t for t in tags if _accent_fold(t.name) == _accent_fold(survivant.name)),
                key=lambda t: (_accent_count(t.name), _related_count(t)),
            ).name.strip()

            try:
                with transaction.atomic():
                    if appliquer:
                        for perdant in perdants:
                            _merge_relations(survivant, perdant)
                        Tag.objects.filter(id__in=[t.id for t in perdants]).delete()
                        if survivant.name != meilleure_forme:
                            survivant.name = meilleure_forme
                            survivant.save(update_fields=["name"])
            except IntegrityError as exc:
                sautes.append((tags, str(exc).splitlines()[0]))
                continue

            fusionnes += 1
            supprimes += len(perdants)
            self.stdout.write(
                f"  survivant id={survivant.id} {meilleure_forme!r} <- " + ", ".join(f"{t.name!r}" for t in perdants),
            )

        self.stdout.write(
            f"\n{len(groupes)} groupes : {fusionnes} {'fusionnés' if appliquer else 'fusionnables'} "
            f"({supprimes} Tag {'supprimés' if appliquer else 'à supprimer'}), "
            f"{len(conflits)} en conflit de savoir_officiel (non touchés), {len(sautes)} sautés (contrainte).",
        )
        for tags, raison in sautes[:20]:
            self.stdout.write(f"  sauté : {[t.name for t in tags]} - {raison[:120]}")
        if not appliquer:
            self.stdout.write("Simulation seule : relancer avec --apply pour écrire.")
