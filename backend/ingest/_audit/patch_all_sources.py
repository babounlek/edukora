"""Reporte tous les themes_out_<slug>.json dans les JSON sources (dossier retrouvé via epreuve_source).
Garde-fou : ignore (avec avertissement) un exercice absent de la source, abandonne ce dossier si une question a bougé."""
import json, sys
from pathlib import Path

audit = Path(__file__).parent
ingest = audit.parent
resume = {"ecrit": 0, "dossier_introuvable": [], "exercices_base_seulement": 0, "abandon": []}
for f_in in sorted(audit.glob("themes_in_*.json")):
    slug = f_in.name[len("themes_in_"):-5]
    f_out = audit / f"themes_out_{slug}.json"
    if not f_out.exists():
        continue
    entree = json.loads(f_in.read_text(encoding="utf-8"))
    sortie = json.loads(f_out.read_text(encoding="utf-8"))
    stem = (entree.get("epreuve_source") or "").removesuffix(".pdf")
    dossiers = [d for d in ingest.glob(f"*/{stem}") if d.is_dir()] if stem else []
    if not dossiers:
        resume["dossier_introuvable"].append(slug); continue
    racine = dossiers[0]
    par_ex = {}
    for q in entree["questions"]:
        par_ex.setdefault(str(q["exercice"]), {})[str(q["numero"])] = sortie[str(q["pk"])]
    fichiers = {}
    for f in racine.glob("*_exercice_*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        fichiers[str(d.get("numero_exercice"))] = (f, d)
    a_ecrire, ok = [], True
    for ex, qs in par_ex.items():
        if ex not in fichiers:
            resume["exercices_base_seulement"] += 1; continue
        f, d = fichiers[ex]
        presentes = {str(q.get("numero")): q for q in d.get("questions", [])}
        if set(qs) - set(presentes):
            resume["abandon"].append(f"{slug} ex.{ex}"); ok = False; break
        for n, th in qs.items():
            if not presentes[n].get("themes"):
                presentes[n]["themes"] = th
        a_ecrire.append((f, d))
    if ok:
        for f, d in a_ecrire:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        resume["ecrit"] += len(a_ecrire)
print(json.dumps(resume, ensure_ascii=False, indent=1))
