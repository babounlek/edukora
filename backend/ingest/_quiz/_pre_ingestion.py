#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contrôle avant ingestion du Mode Quiz.

À lancer depuis le dossier `backend` (celui qui contient manage.py) :

    python manage.py shell < ingest/_quiz/_pre_ingestion.py

Ce script ne modifie RIEN. Il répond à une seule question : est-ce que
`quiz.ingestion.run_ingestion("ingest/_quiz")` va passer, ou est-ce qu'il va
rejeter des lots ?

Le point de rupture le plus probable est `_resolve_theme` : il exige qu'un
`Tag` porte EXACTEMENT le nom écrit dans le champ `theme` de chaque item
(correspondance stricte d'abord, repli insensible à la casse ensuite, et
échec si plusieurs Tag correspondent à la casse près). Un Tag manquant fait
échouer les 6 items du lot concerné, silencieusement pour l'utilisateur :
l'erreur n'apparaît que dans la liste `errors` du dictionnaire de retour.
"""

from pathlib import Path
import json
import sys

from catalog.models import Tag

RACINE = Path("ingest/_quiz/cm")

if not RACINE.exists():
    sys.stdout.write(f"Dossier introuvable : {RACINE.resolve()}\n")
    sys.stdout.write("Lance ce script depuis le dossier backend (celui de manage.py).\n")
else:
    themes = {}
    total_items = 0
    for chemin in sorted(RACINE.glob("*.json")):
        items = json.loads(chemin.read_text(encoding="utf-8"))
        total_items += len(items)
        for item in items:
            themes.setdefault(item["theme"], set()).add(chemin.name)

    exacts, casse, ambigus, absents = [], [], [], []
    for nom in sorted(themes):
        if Tag.objects.filter(name=nom).exists():
            exacts.append(nom)
            continue
        candidats = list(Tag.objects.filter(name__iexact=nom))
        if len(candidats) == 1:
            casse.append((nom, candidats[0].name))
        elif len(candidats) > 1:
            ambigus.append((nom, [c.name for c in candidats]))
        else:
            absents.append(nom)

    sortie = []
    sortie.append(f"{len(themes)} thèmes distincts, {total_items} items, "
                  f"{len(list(RACINE.glob('*.json')))} lots.\n")
    sortie.append(f"  Tag trouvé au caractère près : {len(exacts)}")
    sortie.append(f"  Tag trouvé à la casse près   : {len(casse)}  (ingéré, mais dérive à corriger)")
    sortie.append(f"  Ambigus (plusieurs Tag)      : {len(ambigus)}  BLOQUANT")
    sortie.append(f"  Aucun Tag correspondant      : {len(absents)}  BLOQUANT\n")

    if casse:
        sortie.append("Dérive de casse — le lot passera, mais autant aligner :")
        for nom, reel in casse:
            sortie.append(f"  theme={nom!r}  ->  Tag.name={reel!r}")
        sortie.append("")

    if ambigus:
        sortie.append("Ambigus — à corriger à la main, l'ingestion refusera :")
        for nom, cands in ambigus:
            sortie.append(f"  theme={nom!r}  ->  {cands}")
        sortie.append("")

    if absents:
        sortie.append("Tag manquants — chaque lot concerné sera intégralement rejeté :")
        for nom in absents:
            fichiers = ", ".join(sorted(themes[nom]))
            sortie.append(f"  {nom!r}   (lot : {fichiers})")
        sortie.append("")
        sortie.append("Ces Tag doivent être créés par correction-experte, jamais par le")
        sortie.append("pipeline quiz — c'est explicitement ce que dit _resolve_theme.")
        sortie.append("")

    if not absents and not ambigus:
        sortie.append("Aucun blocage côté Tag : run_ingestion peut être lancé.")

    sys.stdout.write("\n".join(sortie) + "\n")
