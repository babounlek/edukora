#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnostic par page d'un PDF d'epreuve : quel regime de filigrane, quelles figures embarquees.

Usage : python diagnostiquer.py PDF [--extraire DOSSIER]

Pour chaque page : regime (A_calques / B_cuit / C_natif), nombre d'objets parasites, et la liste des images
embarquees qui NE SONT PAS des parasites (candidates a une extraction native, sans aucun filigrane).
Avec --extraire, ces images sont ecrites telles quelles (resolution d'origine) dans DOSSIER.
"""
import argparse
import os
import sys

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from page_propre import image_de_base, images_repetees, empreinte  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--extraire", default="")
    a = ap.parse_args()
    doc = fitz.open(a.pdf)
    repetees, cache = images_repetees(doc)
    if a.extraire:
        os.makedirs(a.extraire, exist_ok=True)
    for i, p in enumerate(doc, 1):
        base = image_de_base(p)
        infos = p.get_image_info(xrefs=True)
        parasites = [x for x in infos if (base is not None and x["xref"] != base["xref"])
                     or empreinte(doc, x["xref"], cache) in repetees]
        figures = [x for x in infos if x not in parasites and (base is None or x["xref"] != base["xref"])]
        regime = "C_natif" if base is None else ("A_calques" if parasites else "B_cuit")
        ligne = f"p{i:>2} {regime:<9} parasites={len(parasites)} rot={p.rotation}"
        if base is not None:
            ligne += f" scan={base['width']}x{base['height']}"
        print(ligne)
        for x in figures:
            bb = [round(v) for v in x["bbox"]]
            print(f"     figure xref={x['xref']} {x['width']}x{x['height']}px bbox_pt={bb}")
            if a.extraire:
                pix = fitz.Pixmap(doc, x["xref"])
                if pix.n > 3 or pix.alpha:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(os.path.join(a.extraire, f"p{i}_xref{x['xref']}.png"))


if __name__ == "__main__":
    main()
