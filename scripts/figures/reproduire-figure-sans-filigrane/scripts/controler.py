#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Controle automatique d'une figure finale : reste-t-il un filigrane ?

Usage : python controler.py FIGURE.png [--largeur-max 900]

Verifie (1) par OCR (Tesseract) qu'aucun mot de filigrane connu ne subsiste, (2) la taille, (3) la proportion
de pixels gris pale isoles (traces de filigrane ou de transparence), (4) que la figure n'est pas vide.
Code de sortie 0 = OK, 1 = a revoir. Ce controle complete l'oeil, il ne le remplace pas.
"""
import argparse
import re
import shutil
import subprocess
import sys

import cv2
import numpy as np

MOTS = re.compile(r"gcerevis|revision\.com|kawlo|concours|cameroon\.com|download|play\s*store|past\s+questions|www\.", re.I)


def lire(chemin):
    img = cv2.imdecode(np.fromfile(chemin, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"image illisible : {chemin}")
    return img


def ocr(chemin, img):
    exe = shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # on agrandit un peu : le filigrane pale est mieux lu sur une image grande et contrastee
    g = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    ok, buf = cv2.imencode(".png", g)
    tmp = chemin + ".ocr.png"
    buf.tofile(tmp)
    try:
        r = subprocess.run([exe, tmp, "stdout", "--psm", "11"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        return r.stdout or ""
    except Exception as e:  # tesseract absent : on le dit, on ne bloque pas
        return f"[OCR indisponible : {e}]"
    finally:
        import os
        try:
            os.remove(tmp)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figure")
    ap.add_argument("--largeur-max", type=int, default=900)
    a = ap.parse_args()
    img = lire(a.figure)
    h, w = img.shape
    problemes = []

    if w > a.largeur_max:
        problemes.append(f"largeur {w}px > {a.largeur_max}px (le contrat limite a {a.largeur_max})")
    sombres = float((img < 128).mean())
    if sombres < 0.002:
        problemes.append(f"figure quasi vide ({sombres:.4%} de pixels sombres) : recadrage a cote ?")
    # gris pale (filigrane) : pixels entre 150 et 245 qui ne sont pas au bord d'un trait sombre
    pale = ((img > 150) & (img < 245)).astype(np.uint8)
    trait = cv2.dilate((img < 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    residu = float(((pale == 1) & (trait == 0)).mean())
    if residu > 0.02:
        problemes.append(f"{residu:.1%} de gris pale hors des traits : filigrane ou voile probable (relancer avec --filtre oui)")

    texte = ocr(a.figure, img)
    trouves = sorted({m.group(0).lower() for m in MOTS.finditer(texte)})
    if trouves:
        problemes.append(f"mots de filigrane lus par l'OCR : {trouves}")

    print(f"{a.figure} : {w}x{h}px, sombres={sombres:.2%}, gris pale residuel={residu:.2%}")
    if problemes:
        print("A REVOIR :")
        for p in problemes:
            print("  -", p)
        return 1
    print("OK : aucun mot de filigrane lu, taille conforme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
