import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Lesson, Subject, generate_unique_slug
from catalog.slugs_renommes import FICHIER, recharger
from inedit.models import Blueprint, EpreuveInedite

ANCIEN = "Sciences de la Vie et de la Terre"
NOUVEAU = "Sciences"


class Command(BaseCommand):
    help = (
        "Corrige les titres et les adresses (slugs) du contenu de la matière Sciences (série A) : « Sciences de la Vie "
        "et de la Terre … » devient « Sciences … ». Les anciennes adresses restent valables (table "
        "catalog/slugs_renommes.json, lue par les API). SIMULATION par défaut ; idempotent ; aucune suppression."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", default="CM")
        parser.add_argument("--appliquer", action="store_true")

    def handle(self, *args, **options):
        try:
            sciences = Subject.objects.get(country__code__iexact=options["pays"], code="SCIENCES")
        except Subject.DoesNotExist:
            raise CommandError("Matière Sciences introuvable : lancer d'abord separer_sciences_serie_a.")
        ecrire = options["appliquer"]
        try:
            table = json.loads(FICHIER.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            table = {}

        with transaction.atomic():
            for nom, modele, champ in (("lesson", Lesson, "title"), ("epreuveinedite", EpreuveInedite, "titre"),
                                       ("blueprint", Blueprint, None)):
                champ = champ or "titre"
                n = 0
                for obj in modele.objects.filter(subject=sciences).order_by("id"):
                    titre = getattr(obj, champ)
                    if not titre.startswith(ANCIEN):
                        continue
                    nouveau_titre = NOUVEAU + titre[len(ANCIEN):]
                    maj = {champ: nouveau_titre}
                    if hasattr(obj, "slug"):
                        # Le slug suit le titre (même règle qu'à la création). Un slug déjà correct n'est pas touché.
                        nouveau_slug = generate_unique_slug(modele, nouveau_titre, existing_pk=obj.pk)
                        if nouveau_slug != obj.slug:
                            table.setdefault(nom, {})[obj.slug] = nouveau_slug
                            maj["slug"] = nouveau_slug
                    n += 1
                    self.stdout.write(f"  {nom} {obj.pk} : {titre!r} -> {nouveau_titre!r}"
                                      + (f"  [{obj.slug} -> {maj['slug']}]" if "slug" in maj else ""))
                    if ecrire:
                        modele.objects.filter(pk=obj.pk).update(**maj)
                self.stdout.write(f"{nom} à renommer : {n}")
            if not ecrire:
                transaction.set_rollback(True)

        if ecrire:
            Path(FICHIER).write_text(json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            recharger()
            self.stdout.write(self.style.SUCCESS(
                f"Terminé. Redirections écrites dans {FICHIER.name} ; à faire ensuite : `indexer_recherche`."))
        else:
            self.stdout.write("Simulation terminée : relancer avec --appliquer pour écrire.")
