#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Retrouve le PDF d'origine (celui du site source, avec filigrane) d'une epreuve deja ingeree.

Usage : python resoudre_source.py NOM_EPREUVE [--racine DOSSIER_PDF]
        python resoudre_source.py --couverture NOM1 NOM2 ...        (taux de resolution)

NOM_EPREUVE : nom du dossier d'ingestion / de l'epreuve, ex. `gce-ol-human-biology-2021-p1-officiel-cameroun`
(ou le champ `epreuve_source` des JSON, avec ou sans `.pdf`).

ATTENTION : le `sujet_pdf` stocke dans la base N'EST PAS le PDF d'origine (document regenere, ou les figures sont deja
les images filigranees) : ne jamais s'en servir pour refaire une figure propre.

Cle d'appariement (niveau, matiere normalisee, annee, paper). Un nom ambigu ou inconnu n'est JAMAIS devine : le script
rend la liste des candidats et un code de sortie 1.
"""
import argparse
import os
import re
import sys

RACINE_DEFAUT = r"D:\edukora\backend\ingest\_telechargements_gce_2026-10-13"

# equivalences de noms de matiere entre les conventions des sites sources
SYNONYMES = {
    "mathematics": "maths", "math": "maths", "mathematiques": "maths",
    "chimie": "chemistry", "biologie": "biology", "physique": "physics",
    "additional-mathematics": "additional-maths", "english-language": "english", "literature-in-english": "literature",
    "food-and-nutrition": "food-nutrition", "computer-science": "computer-science",
    "citizenship-education": "citizenship", "english-langue": "english", "pm-mechanics": "maths-mechanics", "pm-statistics": "maths-statistics",
}


def norm_matiere(m):
    m = m.lower().strip("-_ ")
    m = re.sub(r"[_\s]+", "-", m)
    return SYNONYMES.get(m, m)


def cle_depuis_nom(nom):
    """(niveau, matiere, annee, paper) depuis un nom de dossier d'ingestion ou de PDF ; None si non reconnu."""
    s = os.path.basename(nom).lower()
    s = re.sub(r"\.pdf$", "", s)
    s = s.replace("_", "-")
    s = re.sub(r"-copy(-\d+)?$", "", s)
    s = re.sub(r"-(officiel|mock|zero|blanc)(-.*)?$", "", s)           # suffixes de dossier
    s = re.sub(r"-cameroun$", "", s)
    m = re.match(r"^gce-(ol|al)-(.+)-(\d{4})-p(\d)$", s)                 # GCE_OL_MATHS_2021_P2
    if m:
        return (m.group(1), norm_matiere(m.group(2)), int(m.group(3)), int(m.group(4)))
    m = re.match(r"^(?:o-?level|ol)-(\d{4})-(.+)-(\d)$", s)               # O-LEVEL-2025-CHEMISTRY-1
    if m:
        return ("ol", norm_matiere(m.group(2)), int(m.group(1)), int(m.group(3)))
    m = re.match(r"^(?:a-?level|al)-(\d{4})-(.+)-(\d)$", s)
    if m:
        return ("al", norm_matiere(m.group(2)), int(m.group(1)), int(m.group(3)))
    return None


def indexer(racine):
    idx = {}
    for dp, _, fs in os.walk(racine):
        for f in fs:
            if f.lower().endswith(".pdf"):
                c = cle_depuis_nom(f)
                if c:
                    idx.setdefault(c, []).append(os.path.join(dp, f))
    return idx


def resoudre(nom, idx):
    c = cle_depuis_nom(nom)
    if not c:
        return None, []
    return c, idx.get(c, [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("noms", nargs="+")
    ap.add_argument("--racine", default=RACINE_DEFAUT)
    ap.add_argument("--couverture", action="store_true")
    a = ap.parse_args()
    idx = indexer(a.racine)
    if a.couverture:
        ok = amb = non = 0
        for n in a.noms:
            c, cands = resoudre(n, idx)
            if len(cands) == 1:
                ok += 1
            elif len(cands) > 1:
                amb += 1
            else:
                non += 1
        print(f"resolus={ok} ambigus={amb} introuvables={non} / {len(a.noms)}")
        return 0
    c, cands = resoudre(a.noms[0], idx)
    if len(cands) == 1:
        print(cands[0])
        return 0
    print(f"cle={c} candidats={cands}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
