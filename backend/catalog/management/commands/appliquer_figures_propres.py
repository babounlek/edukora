import json
import os
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

from catalog.ingestion import _compress_figure_image
from catalog.models import Figure


class Command(BaseCommand):
    help = (
        "Remplace l'image de figures déjà ingérées par leur version SANS filigrane produite par le skill "
        "reproduire-figure-sans-filigrane (dossier de PNG `<id>.png` + rapport.jsonl). SIMULATION par défaut : "
        "rien n'est écrit sans --appliquer. Le nom du fichier est CONSERVÉ (les URL sont écrites en dur dans le "
        "Markdown des questions/exercices/épreuves) ; l'ancienne image est sauvegardée dans "
        "media/figures_avant_filigrane/ avant remplacement."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dossier", required=True, help="Dossier du lot (contient <id>.png et rapport.jsonl).")
        parser.add_argument("--statuts", default="retrouvee",
                            help="Statuts du rapport à appliquer, séparés par des virgules (défaut : retrouvee ; "
                                 "filtree_sans_pdf = filtre sur la figure seule, à valider à l'œil).")
        parser.add_argument("--score-min", type=float, default=0.8, help="Score de correspondance minimal (défaut 0.8).")
        parser.add_argument("--ids", default="", help="Limiter à ces ids de Figure (virgules).")
        parser.add_argument("--appliquer", action="store_true", help="Écrire réellement (sinon simulation).")

    def handle(self, *args, **options):
        dossier = Path(options["dossier"])
        rapport_path = dossier / "rapport.jsonl"
        if not rapport_path.is_file():
            raise CommandError(f"rapport.jsonl introuvable dans {dossier}")
        statuts = {s.strip() for s in options["statuts"].split(",") if s.strip()}
        voulus = {int(x) for x in options["ids"].split(",") if x.strip()} if options["ids"] else None

        retenus, ignores = [], {}
        for ligne in rapport_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(ligne)
            if voulus is not None and r["id"] not in voulus:
                continue
            if r.get("statut") not in statuts:
                ignores[r.get("statut")] = ignores.get(r.get("statut"), 0) + 1
                continue
            if r.get("statut") == "retrouvee" and (r.get("score") or 0) < options["score_min"]:
                ignores["score_faible"] = ignores.get("score_faible", 0) + 1
                continue
            if not (dossier / f"{r['id']}.png").is_file():
                ignores["png_absent"] = ignores.get("png_absent", 0) + 1
                continue
            retenus.append(r)

        self.stdout.write(f"{len(retenus)} figure(s) à remplacer ; ignorées : {ignores or 'aucune'}")
        faits = 0
        for r in retenus:
            try:
                figure = Figure.objects.get(pk=r["id"])
            except Figure.DoesNotExist:
                self.stdout.write(f"  Figure {r['id']} absente de la base : ignorée")
                continue
            nom = figure.image.name
            png = (dossier / f"{r['id']}.png").read_bytes()
            if nom.lower().endswith(".webp"):
                octets, _ = _compress_figure_image(png, os.path.basename(nom))
            else:  # figures historiques restées en PNG : on garde le format
                tampon = BytesIO()
                Image.open(BytesIO(png)).convert("RGB").save(tampon, format="PNG", optimize=True)
                octets = tampon.getvalue()
            if not options["appliquer"]:
                self.stdout.write(f"  [simulation] Figure {figure.id} {nom} <- {r['id']}.png ({len(octets)} o)")
                continue
            sauvegarde = f"figures_avant_filigrane/{figure.id}_{os.path.basename(nom)}"
            if figure.image.storage.exists(nom) and not default_storage.exists(sauvegarde):
                with figure.image.storage.open(nom, "rb") as src:
                    default_storage.save(sauvegarde, ContentFile(src.read()))
            figure.image.storage.delete(nom)           # même nom : delete puis save, sinon suffixe aléatoire
            sauve = figure.image.storage.save(nom, ContentFile(octets))
            if sauve != nom:
                raise CommandError(f"Nom de fichier modifié par le stockage ({nom} -> {sauve}) : arrêt.")
            faits += 1
        if options["appliquer"]:
            self.stdout.write(self.style.SUCCESS(f"{faits} figure(s) remplacée(s)."))
        else:
            self.stdout.write("Simulation terminée : relancer avec --appliquer pour écrire.")
