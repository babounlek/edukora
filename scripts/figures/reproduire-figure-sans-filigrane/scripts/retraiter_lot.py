#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Retraite en lot des figures deja ingerees : manifeste JSON -> un PNG propre par figure + rapport.

Usage : python retraiter_lot.py MANIFESTE.json RACINE_MEDIA SORTIE_DIR [--racine-pdf DOSSIER] [--ids 1,2,3] [--filtre-gce]
                                 [--workers 6]

MANIFESTE : liste de {"id": 4171, "fichier": "figures/cm/xxx.webp", "page": 2, "epreuve": "gce-ol-biology-2026-p1-officiel-cameroun"}
RACINE_MEDIA : dossier qui contient `figures/...` (copie de /app/media). Ecrit `SORTIE_DIR/<id>.png` et `rapport.jsonl`.
Chaque ligne du rapport : id, statut (retrouvee / introuvable_dans_pdf / source_introuvable / filtree_sans_pdf / erreur),
score, page, difference brut/propre. Rien n'est ecrit en base : voir `manage.py appliquer_figures_propres`.
"""
import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Pool

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import resoudre_source  # noqa: E402

PY = sys.executable


def travail(args):
    fig, media, sortie, idx = args
    fid = fig["id"]
    out = os.path.join(sortie, f"{fid}.png")
    src = os.path.join(media, fig["fichier"].replace("/", os.sep))
    c, cands = resoudre_source.resoudre(fig.get("epreuve", ""), idx)
    cmd = [PY, os.path.join(ICI, "retraiter_figure.py"), src]
    if len(cands) == 1:
        cmd.append(cands[0])
    else:
        cmd += ["--sans-pdf"]
    cmd.append(out)
    if len(cands) == 1 and fig.get("page"):
        cmd += ["--page", str(fig["page"])]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        rap = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"statut": "erreur", "stderr": r.stderr[-300:]}
    except Exception as e:  # noqa: BLE001
        rap = {"statut": "erreur", "stderr": str(e)[:300]}
    if len(cands) != 1 and rap.get("statut") == "filtree_sans_pdf":
        rap["statut"] = "source_introuvable" if not cands else "source_ambigue"
    rap["id"] = fid
    rap["epreuve"] = fig.get("epreuve")
    return rap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifeste")
    ap.add_argument("media")
    ap.add_argument("sortie")
    ap.add_argument("--racine-pdf", default=resoudre_source.RACINE_DEFAUT)
    ap.add_argument("--ids", default="")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    figs = json.load(open(a.manifeste, encoding="utf-8"))
    if a.ids:
        voulus = {int(x) for x in a.ids.split(",")}
        figs = [f for f in figs if f["id"] in voulus]
    os.makedirs(a.sortie, exist_ok=True)
    idx = resoudre_source.indexer(a.racine_pdf)
    with Pool(a.workers) as pool, open(os.path.join(a.sortie, "rapport.jsonl"), "w", encoding="utf-8") as rapport:
        for i, rap in enumerate(pool.imap_unordered(travail, [(f, a.media, a.sortie, idx) for f in figs], chunksize=2), 1):
            rapport.write(json.dumps(rap, ensure_ascii=False) + "\n")
            rapport.flush()
            if i % 50 == 0:
                print(i, "/", len(figs), flush=True)
    print("fini", len(figs))


if __name__ == "__main__":
    main()
