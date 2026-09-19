"""Relie le rappel ex3-q4-1 (décalage d'indice avec ex3-q4-0 cité par le cours) au cours hyperviseur existant,
et ajoute l'identifiant réel à source.rappels_lies du JSON source pour qu'une réingestion garde le lien."""
import json
from pathlib import Path

from catalog.models import Cours, RappelDeMethode

RAPPEL = "rdm-bac-blanc-ti-reseau-2021-nkongsamba-cameroun-ex3-q4-1"
COURS = "cours-hyperviseur-type1-type2-nkongsamba-2021"

cours = Cours.objects.get(external_id=COURS)
n = RappelDeMethode.objects.filter(external_id=RAPPEL, cours__isnull=True).update(cours=cours)
print("rappels reliés en base:", n)

f = Path("/app/ingest/cm/bac-blanc-ti-reseau-2021-nkongsamba-cameroun/bac-blanc-ti-reseau-2021-nkongsamba-cameroun_cours_hyperviseur-type1-type2.json")
data = json.loads(f.read_text(encoding="utf-8"))
lies = data["source"].setdefault("rappels_lies", [])
if RAPPEL not in lies:
    lies.append(RAPPEL)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("source patchée:", lies)
print("rappels sans cours dans la leçon:", RappelDeMethode.objects.filter(exercise__lesson__slug="informatique-bac-ti-2021-blanc", cours__isnull=True).count())
