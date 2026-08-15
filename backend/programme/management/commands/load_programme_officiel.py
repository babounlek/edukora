import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Country, Cursus, Series, Subject
from programme.models import Module, Savoir


class Command(BaseCommand):
    help = (
        "Charge un référentiel de programme officiel (Module/Savoir) depuis un fichier "
        "JSON produit hors ligne - ces documents MINESEC ne sont publiés qu'en PDF/Word, "
        "il n'existe pas de source API à interroger. Idempotent : ré-exécuter met à jour "
        "les Module déjà présents (par subject+classe+numero) au lieu d'en dupliquer, et "
        "synchronise leurs Savoir un par un (par numero) plutôt que de tout supprimer et "
        "recréer - un Savoir qui n'a pas changé garde le même id, donc garde les Tag qui "
        "le référencent déjà (voir Tag.savoir_officiel) ; seuls les savoirs disparus du "
        "JSON sont supprimés. Un "
        "module dont `examen` est vide dans le JSON (ex: la classe de 2nde, qui n'a pas "
        "d'examen national donc pas de Cursus) est chargé sans rattachement à Cursus - il "
        "reste dans le référentiel mais n'apparaît nulle part côté contenu edukora."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "path", nargs="?",
            default=str(Path(__file__).resolve().parent.parent.parent / "fixtures" / "programme_officiel_cm_maths.json"),
            help="Fichier JSON à charger (défaut : programme/fixtures/programme_officiel_cm_maths.json).",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Fichier introuvable : {path}")

        entries = json.loads(path.read_text(encoding="utf-8"))

        modules_crees = 0
        modules_maj = 0
        savoirs_total = 0
        non_rattaches = 0

        with transaction.atomic():
            for entry in entries:
                country = Country.objects.get(code=entry["country"])
                subject = Subject.objects.get(country=country, code=entry["subject"])

                module, created = Module.objects.update_or_create(
                    subject=subject, classe=entry["classe"], serie_label=entry["serie_label"], numero=entry["numero"],
                    defaults={
                        "titre": entry["titre"],
                        "credit_heures": entry["credit_heures"],
                        "famille_situations": entry["famille_situations"],
                        "ordre": entry["ordre"],
                    },
                )
                modules_crees += int(created)
                modules_maj += int(not created)

                examen = entry["examen"]
                if examen is None:
                    module.cursus.clear()
                    non_rattaches += 1
                else:
                    series_codes = entry["series"]
                    if series_codes:
                        series_qs = Series.objects.filter(country=country, code__in=series_codes)
                        cursus_qs = Cursus.objects.filter(country=country, examen=examen, series__in=series_qs)
                    else:
                        cursus_qs = Cursus.objects.filter(country=country, examen=examen, series__isnull=True)
                    module.cursus.set(cursus_qs)

                # Synchronisation par numero (clé naturelle au sein d'un module) plutôt
                # qu'un delete-all + bulk_create - voir l'aide de la commande ci-dessus.
                # Incident du 2026-08-12 : un premier passage tout-supprimer-recréer a
                # silencieusement effacé les 459 liens Tag.savoir_officiel déjà établis
                # par une passe de curation (SET_NULL en cascade sur la suppression des
                # Savoir), alors même que _link_tags_to_savoir ne les aurait jamais
                # écrasés - la perte passait par un autre chemin (DELETE) que celui
                # protégé. update_or_create préserve l'id (donc les FK existantes) pour
                # tout savoir dont le numero n'a pas changé, même si son intitulé a été
                # corrigé entre-temps.
                numeros_attendus = set()
                for s in entry["savoirs"]:
                    numeros_attendus.add(s["numero"])
                    Savoir.objects.update_or_create(
                        module=module, numero=s["numero"],
                        defaults={"intitule": s["intitule"], "ordre": s["ordre"]},
                    )
                module.savoirs.exclude(numero__in=numeros_attendus).delete()
                savoirs_total += len(entry["savoirs"])

        self.stdout.write(self.style.SUCCESS(
            f"{modules_crees} module(s) créé(s), {modules_maj} mis à jour, {savoirs_total} savoir(s) chargé(s).",
        ))
        if non_rattaches:
            self.stdout.write(
                f"{non_rattaches} module(s) sans Cursus correspondant (classe sans examen national) - "
                "chargés dans le référentiel mais non rattachés au contenu.",
            )
