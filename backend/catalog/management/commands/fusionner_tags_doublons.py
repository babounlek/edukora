"""
Fusionne les `Tag` en doublon - même nom à la casse/aux espaces près (ex. "Alcanes"
vs "alcanes"). Cause racine : `catalog.ingestion._get_or_create_tags` faisait un
`get_or_create(name=name)` sensible à la casse ; deux ingestions indépendantes du
même thème avec une casse différente créaient deux `Tag` distincts. Corrigé
séparément (voir `_resolve_or_create_tag`) pour que l'ingestion future ne recrée
plus ces doublons - cette commande ne traite que l'existant déjà en base.

Sur les 619 groupes de doublons trouvés le 2026-09-15, 92 ont des tags pointant
vers un `savoir_officiel` DIFFÉRENT (ex. "lecture graphique" rattaché à un savoir de
Maths pour l'un, de Chimie pour l'autre - collision de nom entre matières/séries,
voir memory `reference_quiz_savoir_theme_collision_bug`). Ces groupes ne sont
JAMAIS fusionnés automatiquement : fusionner à l'aveugle rattacherait silencieusement
du contenu au mauvais Savoir. Ils sont seulement listés, pour arbitrage manuel.

Pour les groupes sans conflit, le survivant est choisi ainsi :
1. Le tag qui a un `savoir_officiel` renseigné, si un seul des tags du groupe l'a.
2. Sinon celui qui porte le plus de contenu lié (Cours/Exercise/Lesson/Question/
   CompetenceItem/...) - découvert dynamiquement via `Tag._meta.related_objects`
   plutôt qu'une liste figée, pour ne pas se désynchroniser si une nouvelle relation
   vers Tag apparaît plus tard.
3. Sinon le plus ancien (id le plus bas).

Toutes les relations (M2M et FK, y compris `quiz.CompetenceItem.theme` qui est en
`on_delete=PROTECT` et `quiz.RevisionSchedule.theme` qui est en `on_delete=CASCADE`)
sont réattribuées au survivant AVANT suppression des doublons, pour ne jamais perdre
de ligne par cascade.

Idempotente : relancer après une première passe ne retrouve plus les groupes déjà
fusionnés.

    python manage.py fusionner_tags_doublons              # simulation
    python manage.py fusionner_tags_doublons --apply
"""

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import ManyToManyRel

from catalog.models import Tag


def _related_count(tag):
    total = 0
    for rel in Tag._meta.related_objects:
        total += getattr(tag, rel.get_accessor_name()).count()
    return total


def _merge_relations(survivor, loser):
    for rel in Tag._meta.related_objects:
        accessor = rel.get_accessor_name()
        if isinstance(rel, ManyToManyRel):
            getattr(survivor, accessor).add(*getattr(loser, accessor).all())
        else:
            getattr(loser, accessor).update(**{rel.field.name: survivor})


class Command(BaseCommand):
    help = "Fusionne les Tag en doublon (même nom insensible à la casse/aux espaces)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Écrit réellement les fusions (sans cette option : simulation seule).",
        )

    def handle(self, *args, **options):
        appliquer = options["apply"]

        groupes = defaultdict(list)
        for tag in Tag.objects.all().order_by("id"):
            groupes[tag.name.strip().lower()].append(tag)
        doublons = {cle: tags for cle, tags in groupes.items() if len(tags) > 1}

        conflits = []
        a_fusionner = []
        for tags in doublons.values():
            savoirs = {t.savoir_officiel_id for t in tags if t.savoir_officiel_id is not None}
            (conflits if len(savoirs) > 1 else a_fusionner).append(tags)

        self.stdout.write(
            f"{len(doublons)} groupes de doublons ({sum(len(v) for v in doublons.values())} Tag) : "
            f"{len(conflits)} en conflit de savoir_officiel (non touchés), "
            f"{len(a_fusionner)} sans conflit ({'fusion' if appliquer else 'simulation'}).",
        )

        if conflits:
            self.stdout.write("\n--- Conflits à arbitrer manuellement (savoir_officiel différent) ---")
            for tags in conflits:
                desc = ", ".join(f"id={t.id} {t.name!r} savoir_officiel_id={t.savoir_officiel_id}" for t in tags)
                self.stdout.write(f"  {desc}")

        total_supprimes = 0
        self.stdout.write("\n--- Fusions ---")
        with transaction.atomic():
            for tags in a_fusionner:
                avec_savoir = [t for t in tags if t.savoir_officiel_id is not None]
                if len(avec_savoir) == 1:
                    survivor = avec_savoir[0]
                else:
                    survivor = max(tags, key=lambda t: (_related_count(t), -t.id))
                perdants = [t for t in tags if t.id != survivor.id]

                if appliquer:
                    for loser in perdants:
                        _merge_relations(survivor, loser)
                    survivor_name = survivor.name.strip()
                    if survivor_name != survivor.name:
                        survivor.name = survivor_name
                        survivor.save(update_fields=["name"])
                    Tag.objects.filter(id__in=[t.id for t in perdants]).delete()

                total_supprimes += len(perdants)
                self.stdout.write(
                    f"  survivant id={survivor.id} {survivor.name!r} <- "
                    + ", ".join(f"id={t.id} {t.name!r}" for t in perdants),
                )

            if not appliquer:
                transaction.set_rollback(True)

        self.stdout.write(
            f"\n{'Fusionné' if appliquer else 'Simulerait la fusion de'} {len(a_fusionner)} groupes, "
            f"{total_supprimes} Tag {'supprimés' if appliquer else 'à supprimer'}.",
        )
        if not appliquer:
            self.stdout.write("Relancer avec --apply pour écrire.")
