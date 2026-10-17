#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Refait propre une figure DEJA INGEREE (PNG/WebP de la base ou du dossier ingest) a partir du PDF source.

Usage : python retraiter_figure.py FIGURE PDF SORTIE.png [--page N] [--largeur L] [--sans-pdf]

Principe : la figure ingeree est un recadrage d'un rendu de page qui portait le filigrane. On la RETROUVE dans la page
(recherche multi-echelle sur le rendu brut, filigrane compris, donc identique), puis on recoupe la MEME zone dans la page
propre (calques retires / filtre) a la resolution native. Aucune zone n'est devinee : si le score de correspondance est
faible, on le dit et on ne remplace rien.

--page N     page du PDF (1-based) ; sinon toutes les pages sont essayees.
--largeur L  largeur de sortie (defaut : celle de la figure d'origine, pour ne pas bouger la mise en page).
--sans-pdf   pas de PDF (ou correspondance introuvable) : filtre de niveaux directement sur la figure (repli).

Sortie : un PNG + un rapport JSON (statut, page, score, region, difference brut/propre). Codes : 0 ok, 2 a revoir.
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from page_propre import rendre_propre, filtre_niveaux  # noqa: E402
import fitz  # noqa: E402

SEUIL_COUVERTURE = 0.22     # part de pixels non blancs de la figure : au-dela, photo / demi-teintes (calibre sur 7 figures)
SEUIL_COULEUR = 0.0008      # part de pixels a chroma > 90 : figure en couleur franche (redessin propre, carte...) ; un logo pastel vaut 0
SEUIL_SCORE = 0.55          # TM_CCOEFF_NORMED : en dessous, la correspondance n'est pas fiable
LARGEUR_TRAVAIL = 1100      # largeur de la page pour la recherche (rapide), la coupe finale se fait en natif


def charger_gris(chemin):
    im = Image.open(chemin)
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        fond = Image.new("RGB", im.size, "white")
        im = im.convert("RGBA")
        fond.paste(im, mask=im.split()[-1])
        im = fond
    return np.array(im.convert("L")), np.array(im.convert("RGB"))[:, :, ::-1].copy()


def couleur_franche(bgr):
    """Part de pixels tres colores : un filigrane (logo pastel, gris) vaut ~0, un redessin couleur ou une carte non."""
    a = bgr.astype(np.int16)
    return float(((a.max(axis=2) - a.min(axis=2)) > 90).mean())


def chercher(page_gris, modele, echelles):
    """Meilleure (score, x, y, f) de `modele` redimensionne par f dans page_gris."""
    meilleur = (-1.0, 0, 0, 1.0)
    H, W = page_gris.shape
    for f in echelles:
        tw, th = int(round(modele.shape[1] * f)), int(round(modele.shape[0] * f))
        if tw < 24 or th < 24 or tw >= W or th >= H:
            continue
        t = cv2.resize(modele, (tw, th), interpolation=cv2.INTER_AREA)
        r = cv2.matchTemplate(page_gris, t, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(r)
        if mx > meilleur[0]:
            meilleur = (float(mx), loc[0], loc[1], f)
    return meilleur


def localiser(pdf, figure_gris, pages):
    doc = fitz.open(pdf)
    grossier = np.geomspace(0.3, 2.6, 22)
    meilleur = None
    for p in pages:
        brut, rap = rendre_propre(pdf, p, propre=False, doc=fitz.open(pdf))
        g = cv2.cvtColor(brut, cv2.COLOR_BGR2GRAY) if brut.ndim == 3 else brut
        s = LARGEUR_TRAVAIL / g.shape[1]
        gt = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        sc, x, y, f = chercher(gt, figure_gris, grossier)
        if meilleur is None or sc > meilleur["score"]:
            meilleur = {"score": sc, "page": p, "x": x, "y": y, "f": f, "s": s, "dpi": rap["dpi"], "gt": gt, "g": g}
    if meilleur is None:
        return None
    # affinage autour de la meilleure echelle, sur la meilleure page
    f0 = meilleur["f"]
    fin = np.linspace(f0 * 0.93, f0 * 1.07, 15)
    sc, x, y, f = chercher(meilleur["gt"], figure_gris, fin)
    if sc >= meilleur["score"]:
        meilleur.update(score=sc, x=x, y=y, f=f)
    return meilleur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figure")
    ap.add_argument("pdf", nargs="?", default="")
    ap.add_argument("sortie")
    ap.add_argument("--page", type=int, default=0)
    ap.add_argument("--largeur", type=int, default=0)
    ap.add_argument("--sans-pdf", action="store_true")
    a = ap.parse_args()
    if not a.sortie.lower().endswith(".png"):  # permet `retraiter_figure.py fig.webp --sans-pdf sortie.png`
        a.pdf, a.sortie = "", a.pdf or a.sortie
    fig_gris, fig_bgr = charger_gris(a.figure)
    H0, W0 = fig_gris.shape
    largeur = a.largeur or W0
    rapport = {"figure": os.path.basename(a.figure), "taille_origine": [W0, H0]}

    sortie = None
    if a.pdf and not a.sans_pdf and os.path.exists(a.pdf):
        n = len(fitz.open(a.pdf))
        pages = [a.page] if a.page else list(range(1, n + 1))
        loc = localiser(a.pdf, fig_gris, pages)
        if loc and loc["score"] >= SEUIL_SCORE:
            propre, rap = rendre_propre(a.pdf, loc["page"])
            native_w = propre.shape[1]
            k = native_w / (loc["g"].shape[1] * loc["s"])           # travail -> natif
            tw = W0 * loc["f"] * k
            th = H0 * loc["f"] * k
            x0, y0 = loc["x"] * k, loc["y"] * k
            x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x0 + tw)), int(round(y0 + th))
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(propre.shape[1], x1), min(propre.shape[0], y1)
            coupe = propre[y0:y1, x0:x1]
            brut, _ = rendre_propre(a.pdf, loc["page"], propre=False)
            coupe_brut = brut[y0:y1, x0:x1]
            gb = cv2.cvtColor(coupe_brut, cv2.COLOR_BGR2GRAY) if coupe_brut.ndim == 3 else coupe_brut
            gp = cv2.cvtColor(coupe, cv2.COLOR_BGR2GRAY) if coupe.ndim == 3 else coupe
            diff = float(np.abs(gb.astype(np.int16) - gp.astype(np.int16)).mean())
            sortie = coupe
            couverture = float((fig_gris < 235).mean())
            rapport["couverture_non_blanc"] = round(couverture, 3)
            couleur = couleur_franche(fig_bgr)
            rapport["couleur_franche"] = round(couleur, 4)
            if rap["filtre_niveaux"] and (couverture > SEUIL_COUVERTURE or couleur > SEUIL_COULEUR):
                # photo, carte grisee, ombrages : le filtre de niveaux detruit les demi-teintes. On rend la page SANS
                # filtre (calques retires, filigrane incruste conserve) et on laisse un humain decider.
                nf, _ = rendre_propre(a.pdf, loc["page"], filtre="non")
                sortie = nf[y0:y1, x0:x1]
                rapport["demi_teintes"] = True
            rapport.update(statut="retrouvee", methode="pdf_source", page=loc["page"], score=round(loc["score"], 3),
                           regime_page=rap["regime"], region_px=[x0, y0, x1, y1],
                           difference_brut_propre=round(diff, 2), filtre_niveaux=rap["filtre_niveaux"])
        else:
            rapport.update(statut="introuvable_dans_pdf", score=round(loc["score"], 3) if loc else None)
    if sortie is None and couleur_franche(fig_bgr) > SEUIL_COULEUR:
        # figure en couleur, absente du PDF : tres probablement un redessin propre (matplotlib/SVG) : on n'y touche pas,
        # le filtre de niveaux la passerait en noir et blanc
        rapport.update(statut="couleur_ignoree", methode="aucune", couleur_franche=round(couleur_franche(fig_bgr), 4))
        print(json.dumps(rapport, ensure_ascii=False))
        return 2
    if sortie is None:
        # repli : filtre de niveaux sur la figure elle-meme (marche pour un filigrane pale, jamais pour un voile sur
        # des zones ombrees ; la verification a l'oeil est obligatoire)
        sortie = filtre_niveaux(cv2.cvtColor(fig_bgr, cv2.COLOR_BGR2RGB))
        rapport.update(methode="filtre_sur_figure" if rapport.get("statut") is None else "repli_filtre_sur_figure")
        rapport.setdefault("statut", "filtree_sans_pdf")

    if sortie.shape[1] != largeur:
        s = largeur / sortie.shape[1]
        sortie = cv2.resize(sortie, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".png", sortie)
    buf.tofile(a.sortie)
    rapport["taille_sortie"] = [sortie.shape[1], sortie.shape[0]]
    if rapport.get("demi_teintes"):
        rapport["statut"] = "demi_teintes"
    print(json.dumps(rapport, ensure_ascii=False))
    return 0 if rapport["statut"] == "retrouvee" else 2


if __name__ == "__main__":
    sys.exit(main())
