"""Balayage à blanc : que réparerait _repair_literal_dollars sur les sources ingest/ actuelles ?
Lancer dans un conteneur : python /app/ingest/_audit/scan_dollars_dryrun.py"""
import glob
import importlib.util
import json

spec = importlib.util.spec_from_file_location("ra", "/app/catalog/reparations_auto.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)

fichiers = touches = total = 0
exemples = []


def diffs(a, b, cle=None):
    if isinstance(a, str):
        if a != b:
            k = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
            yield cle, a[max(0, k - 30):k + 60].replace("\n", " ")
    elif isinstance(a, list):
        for x, y in zip(a, b):
            yield from diffs(x, y, cle)
    elif isinstance(a, dict):
        for k in a:
            yield from diffs(a[k], b[k], k)


for f in glob.glob("/app/ingest/**/*.json", recursive=True):
    if any(p.startswith("_") for p in f.replace("/app/ingest/", "").split("/")):
        continue
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    fichiers += 1
    nouveau, n = ra._walk_dollars(d)
    if n:
        touches += 1
        total += n
        if len(exemples) < 40:
            exemples.append((f.split("/")[-1][:50], *next(diffs(d, nouveau))))

print(fichiers, "fichiers,", touches, "touchés,", total, "$ échappés")
for e in exemples:
    print(e)
