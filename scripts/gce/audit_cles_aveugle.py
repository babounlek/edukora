"""
Audit aveugle des clés de QCM d'une vague de quiz GCE (voir preparer_quiz_vague.js).

Le validateur par tranche ne sait pas qu'une `reponse_correcte` désigne un distracteur : seul un solveur qui ne VOIT PAS la clé
peut le dire. Deux temps :

  1. export  : écrit, par (niveau, matière), un fichier sans clé ni corrigé (énoncé et options seulement) dans
               backend/ingest/_quiz/_audit/aveugle/<id>.json ; un agent y répond (lettre choisie) dans <id>.reponses.json
               sous la forme {"<external_id>": "a|b|c|d|?"}.
  2. comparer: confronte ces réponses aux clés et liste les désaccords (clé fausse, ou énoncé ambigu : à relire).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\audit_cles_aveugle.py export
    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\audit_cles_aveugle.py comparer
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
QUIZ = RACINE / "backend" / "ingest" / "_quiz"
AUDIT = QUIZ / "_audit" / "aveugle"


def slug(texte):
    s = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def items_de_la_vague():
    """{(niveau, matiere_slug): [(tranche_id, fichier, item), ...]} - seulement les fichiers de la requête (pas ceux d'une autre campagne)."""
    index = json.loads((QUIZ / "_vague_nouvelles_matieres.json").read_text(encoding="utf-8"))
    groupes = defaultdict(list)
    for t in index:
        niveau, matiere = t["id"].split("-")[0], "-".join(t["id"].split("-")[1:-1])
        attendus = {slug(c) for c in t["competences"]}
        dossier = QUIZ / "cm" / t["dossier"]
        for f in sorted(dossier.glob("*.json")):
            items = json.loads(f.read_text(encoding="utf-8"))
            if not (isinstance(items, list) and items) or slug(items[0].get("theme", "")) not in attendus:
                continue
            for it in items:
                groupes[(niveau, matiere)].append((t["id"], f.name, it))
    return groupes


def exporter():
    AUDIT.mkdir(parents=True, exist_ok=True)
    total = 0
    for (niveau, matiere), lignes in sorted(items_de_la_vague().items()):
        qcm = [(tid, f, it) for tid, f, it in lignes if it.get("type_reponse") == "QCM"]
        # Paquets d'au plus 60 QCM : un agent y répond en une passe.
        for i in range(0, len(qcm), 60):
            paquet = qcm[i:i + 60]
            nom = f"{niveau}-{matiere}-{i // 60 + 1:02d}"
            sortie = [
                {
                    "external_id": it["external_id"],
                    "matiere": it["matiere"],
                    "niveau": "A Level" if niveau == "al" else "O Level",
                    "enonce": it["enonce_markdown"],
                    "options": {c["lettre"]: c["texte"] for c in it["choix"]},
                }
                for _, _, it in paquet
            ]
            (AUDIT / f"{nom}.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1), encoding="utf-8")
            total += len(paquet)
            print(nom, len(paquet))
    print(f"{total} QCM exportés dans {AUDIT}")


def comparer():
    cles = {}
    for lignes in items_de_la_vague().values():
        for tid, f, it in lignes:
            if it.get("type_reponse") == "QCM":
                cles[it["external_id"] + "|" + tid] = (it["reponse_correcte"], tid, f)
    par_id = defaultdict(list)
    for k, v in cles.items():
        par_id[k.split("|")[0]].append(v)
    desaccords, repondus, manquants = [], 0, 0
    for fichier in sorted(AUDIT.glob("*.reponses.json")):
        reponses = json.loads(fichier.read_text(encoding="utf-8"))
        for eid, lettre in reponses.items():
            repondus += 1
            for cle, tid, f in par_id.get(eid, []):
                if lettre != cle:
                    desaccords.append((tid, f, eid, cle, lettre))
    attendus = sum(1 for _ in cles)
    manquants = attendus - repondus
    print(f"{repondus} réponses lues sur {attendus} QCM ({manquants} sans réponse), {len(desaccords)} désaccord(s)")
    for tid, f, eid, cle, lettre in desaccords:
        print(f"  {tid}/{f}  {eid}  clé={cle}  solveur={lettre}")
    return 1 if desaccords or manquants else 0


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "export"
    if action == "export":
        exporter()
    else:
        sys.exit(comparer())
