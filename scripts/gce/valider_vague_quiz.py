"""
Contrôle global d'une vague de quiz GCE (voir preparer_quiz_vague.js) avant ingestion.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\valider_vague_quiz.py

Pour chaque tranche de `_vague_nouvelles_matieres.json` : lance valider_quiz_gce.py (code de sortie), puis contrôle
transversal que le validateur par tranche ne voit pas :
  - external_id unique dans TOUTE la vague (et dans les dossiers déjà ingérés) ;
  - chaque tranche a bien ses 5 (ou moins) fichiers attendus ;
  - répartition des lettres de bonne réponse (par matière : une lettre ne doit pas dépasser 45 % des QCM) ;
  - aucun titre de corrigé français ni tiret cadratin, aucune figure.
Code de sortie 0 = rien de bloquant.
"""
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
QUIZ = RACINE / "backend" / "ingest" / "_quiz"
VALIDATEUR = RACINE / "scripts" / "gce" / "valider_quiz_gce.py"


def main():
    index = json.loads((QUIZ / "_vague_nouvelles_matieres.json").read_text(encoding="utf-8"))
    anomalies, lettres_par_matiere, ids = [], defaultdict(Counter), defaultdict(list)
    for tranche in index:
        dossier = QUIZ / "cm" / tranche["dossier"]
        batch = QUIZ / tranche["batch"]
        if not dossier.is_dir():
            anomalies.append(f"{tranche['id']}: dossier absent")
            continue
        sortie = subprocess.run(
            [sys.executable, str(VALIDATEUR), str(batch), str(dossier)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        )
        if sortie.returncode != 0:
            anomalies.append(f"{tranche['id']}: validateur en échec\n{sortie.stdout[-600:]}")
        attendus = {re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-") for c in tranche["competences"]}
        for fichier in dossier.glob("*.json"):
            items = json.loads(fichier.read_text(encoding="utf-8"))
            if not isinstance(items, list) or not items:
                continue
            theme = items[0].get("theme", "")
            slug = re.sub(r"[^a-z0-9]+", "-", __import__("unicodedata").normalize("NFKD", theme).encode("ascii", "ignore").decode().lower()).strip("-")
            if slug not in attendus:
                continue  # fichier d'une autre campagne (ex. gce-al-biology-NN déjà ingéré)
            for it in items:
                ids[it["external_id"]].append(f"{tranche['id']}/{fichier.name}")
                texte = it.get("corrige_markdown", "") + it.get("enonce_markdown", "")
                if re.search(r"Rappel de méthode|### Corrigé", texte):
                    anomalies.append(f"{tranche['id']}/{fichier.name}: titre de corrigé français")
                if "—" in texte or "–" in texte:
                    anomalies.append(f"{tranche['id']}/{fichier.name}: tiret cadratin")
                if it.get("figures"):
                    anomalies.append(f"{tranche['id']}/{fichier.name}: figure inattendue")
                if it.get("type_reponse") == "QCM":
                    lettres_par_matiere[tranche["matiere"] + " " + tranche["niveau"]][it.get("reponse_correcte")] += 1
    for eid, sources in ids.items():
        if len(sources) > 1:
            anomalies.append(f"external_id en double {eid}: {sources}")
    print("== Lettres de bonne réponse par matière et niveau ==")
    for cle, c in sorted(lettres_par_matiere.items()):
        total = sum(c.values())
        pire = max(c.values()) / total
        marque = "  <-- déséquilibre" if pire > 0.45 else ""
        print(f"  {cle:46} {dict(sorted(c.items()))} (max {pire:.0%}){marque}")
    print(f"\n{len(index)} tranches, {len(ids)} items distincts, {len(anomalies)} anomalie(s)")
    for a in anomalies[:60]:
        print(" -", a)
    return 1 if anomalies else 0


if __name__ == "__main__":
    sys.exit(main())
