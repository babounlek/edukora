#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recadre une figure dans une page propre, et fabrique une comparaison avant/apres.

  python recadrer.py recadrer PAGE.png x0 y0 x1 y1 SORTIE.png [--fraction] [--marge 12] [--largeur-max 900]
      x0..y1 en pixels, ou en fractions 0-1 de la page avec --fraction.

  python recadrer.py comparer A.png B.png SORTIE.png [--largeur 900]
      A au-dessus, B en dessous (bande rouge entre les deux), meme largeur : pour verifier le resultat a l'oeil.

  python recadrer.py reperer PAGE.png SORTIE.png
      Superpose une grille numerotee en fractions de la page (0.0-1.0) pour lire les coordonnees d'un recadrage.
"""
import argparse
import sys

import cv2
import numpy as np


def lire(chemin):
    img = cv2.imdecode(np.fromfile(chemin, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"image illisible : {chemin}")
    return img


def ecrire(chemin, img):
    ok, buf = cv2.imencode(".png", img)
    buf.tofile(chemin)


def recadrer(a):
    img = lire(a.page)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = a.x0, a.y0, a.x1, a.y1
    if a.fraction:
        x0, x1, y0, y1 = x0 * w, x1 * w, y0 * h, y1 * h
    x0, y0 = max(0, int(x0 - a.marge)), max(0, int(y0 - a.marge))
    x1, y1 = min(w, int(x1 + a.marge)), min(h, int(y1 + a.marge))
    c = img[y0:y1, x0:x1]
    if c.shape[1] > a.largeur_max:
        s = a.largeur_max / c.shape[1]
        c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    ecrire(a.sortie, c)
    print(f"{a.sortie} : {c.shape[1]}x{c.shape[0]} px")


def comparer(a):
    x, y = lire(a.a), lire(a.b)
    s1, s2 = a.largeur / x.shape[1], a.largeur / y.shape[1]
    x = cv2.resize(x, None, fx=s1, fy=s1, interpolation=cv2.INTER_AREA)
    y = cv2.resize(y, None, fx=s2, fy=s2, interpolation=cv2.INTER_AREA)
    bande = np.full((8, a.largeur, 3), (0, 0, 255), np.uint8)
    ecrire(a.sortie, np.vstack([x, bande, y]))
    print(a.sortie)


def reperer(a):
    img = lire(a.page)
    h, w = img.shape[:2]
    s = min(1.0, 1400 / max(h, w))
    img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    for i in range(0, 11):
        f = i / 10
        cv2.line(img, (int(f * w), 0), (int(f * w), h), (0, 0, 255), 1)
        cv2.line(img, (0, int(f * h)), (w, int(f * h)), (0, 0, 255), 1)
        cv2.putText(img, f"{f:.1f}", (int(f * w) + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(img, f"{f:.1f}", (2, int(f * h) + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    ecrire(a.sortie, img)
    print(a.sortie)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("recadrer")
    r.add_argument("page"); r.add_argument("x0", type=float); r.add_argument("y0", type=float)
    r.add_argument("x1", type=float); r.add_argument("y1", type=float); r.add_argument("sortie")
    r.add_argument("--fraction", action="store_true"); r.add_argument("--marge", type=int, default=12)
    r.add_argument("--largeur-max", type=int, default=900)
    c = sp.add_parser("comparer")
    c.add_argument("a"); c.add_argument("b"); c.add_argument("sortie"); c.add_argument("--largeur", type=int, default=900)
    g = sp.add_parser("reperer")
    g.add_argument("page"); g.add_argument("sortie")
    a = ap.parse_args()
    {"recadrer": recadrer, "comparer": comparer, "reperer": reperer}[a.cmd](a)


if __name__ == "__main__":
    main()
