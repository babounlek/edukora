"""Corrige les 29 échecs de rendu KaTeX relevés par l'audit corpus-entier du 2026-09-19.

Exécuter dans le conteneur : manage.py shell -c "exec(open('/app/ingest/_audit/fix_rendu_dollars.py', encoding='utf-8').read())"
Variable d'environnement DRY=1 : n'écrit rien en base, affiche seulement le bilan.

Causes : (1) `$` PHP/tableur en prose ou en code non protégé, lu comme délimiteur de formule ;
(2) coquilles LaTeX en chimie ; (3) formules de type « chemin/directive » injectées dans `formule_principale`.
"""
import copy
import json
import os
import re
from pathlib import Path

from catalog.models import Cours, Question

DRY = os.environ.get("DRY") == "1"
INGEST = Path("/app/ingest")

COURS_DOLLARS = [8037, 8038, 8122, 8254, 8288, 8291, 8307, 8319, 8347, 8366, 8370, 8388, 8395, 8401, 8402]
COURS_REPLACE = {
    7621: [("NH_4^+_{(aq)}", "{NH_4^+}_{(aq)}")],
    7696: [("C_4H_{10}O}", "C_4H_{10}O")],
    7703: [("0{,}34\\ V}", "0{,}34\\ V")],
}
FORMULES = {
    8388: ("$nomDeVariable = valeur;", r"\texttt{\$nomDeVariable = valeur;}"),
    8122: ("#include <nom_bibliotheque.h>", r"\texttt{\#include <nom\_bibliotheque.h>}"),
    8307: (
        r"C:\wamp64\www\ (ou C:\wamp\www\ en version 32 bits)",
        r"\texttt{C:\textbackslash wamp64\textbackslash www\textbackslash}\ \text{(ou }\texttt{C:\textbackslash wamp\textbackslash www\textbackslash}\text{ en version 32 bits)}",
    ),
}
QUESTIONS = [54684, 56093, 56631, 56640]

_PROTEGE = re.compile(r"(```.*?```|~~~.*?~~~|\$\$.*?\$\$|`[^`\n]*`)", re.DOTALL)


def escape_dollars(text):
    """Échappe tout `$` hors bloc de code, span de code et formule display `$$...$$`."""
    parts = _PROTEGE.split(text)
    return "".join(p if i % 2 else re.sub(r"(?<!\\)\$", r"\\$", p) for i, p in enumerate(parts))


def walk(obj, fn, key=None, parent_key=None):
    if isinstance(obj, str):
        if key == "formule_principale" or parent_key == "variantes":
            return obj
        return fn(obj)
    if isinstance(obj, list):
        return [walk(x, fn, None, key) for x in obj]
    if isinstance(obj, dict):
        return {k: walk(v, fn, k, key) for k, v in obj.items()}
    return obj


def patch_sections(sections, cours_pk):
    new = copy.deepcopy(sections)
    if cours_pk in COURS_DOLLARS:
        new = walk(new, escape_dollars)
    for old, rep in COURS_REPLACE.get(cours_pk, []):
        new = walk(new, lambda s: s.replace(old, rep), None, None)
    if cours_pk in FORMULES:
        old, rep = FORMULES[cours_pk]
        def fix_formula(o):
            if isinstance(o, dict):
                return {k: (rep if k == "formule_principale" and v == old else fix_formula(v)) for k, v in o.items()}
            if isinstance(o, list):
                return [fix_formula(x) for x in o]
            return o
        new = fix_formula(new)
    return new


_SOURCES = {}


def index_sources():
    for f in INGEST.glob("*/*/*_cours*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("cours_id"):
            _SOURCES.setdefault(data["cours_id"], (f, data))


def patch_source_file(cours, cours_pk):
    found = _SOURCES.get(cours.external_id)
    if not found:
        return None
    f, data = found
    new = patch_sections(data.get("sections") or [], cours_pk)
    if new == data.get("sections"):
        return "(source déjà à jour)"
    data["sections"] = new
    if not DRY:
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(f.relative_to(INGEST))


index_sources()


bilan = []
for pk in COURS_DOLLARS + list(COURS_REPLACE) + list(FORMULES):
    if pk in [b[0] for b in bilan]:
        continue
    cours = Cours.objects.get(pk=pk)
    new = patch_sections(cours.sections_raw, pk)
    changed = new != cours.sections_raw
    src = patch_source_file(cours, pk)
    if changed and not DRY:
        cours.sections_raw = new
        cours.save(update_fields=["sections_raw"])
        cours.compile_from_sections()
    bilan.append((pk, changed, src))

for pk in QUESTIONS:
    q = Question.objects.get(pk=pk)
    new = escape_dollars(q.corrige_markdown)
    changed = new != q.corrige_markdown
    if changed and not DRY:
        q.corrige_markdown = new
        q.save(update_fields=["corrige_markdown"])
    bilan.append((f"Question#{pk}", changed, None))

for b in bilan:
    print(b)
print("DRY-RUN" if DRY else "APPLIQUÉ")
