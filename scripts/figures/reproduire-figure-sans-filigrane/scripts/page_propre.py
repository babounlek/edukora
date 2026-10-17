#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rend UNE page de PDF sans filigrane, a la resolution native de la numerisation.

Usage : python page_propre.py PDF PAGE SORTIE.png [--dpi N] [--filtre auto|oui|non] [--garder-texte]

PAGE est numerotee a partir de 1. Ecrit le PNG et imprime un rapport JSON sur stdout.

Trois regimes (le script detecte lequel s'applique) :
  A_calques : la page = une numerisation (image pleine page) + des objets AJOUTES par-dessus
              (logo, tuiles de texte diagonal, bandeaux, texte rouge en haut et en bas).
              On supprime ces objets puis on rend la page : la numerisation est intacte, rien n'est invente.
  B_cuit    : numerisation seule, filigrane gris pale deja incruste dans les pixels.
              Aucun objet a supprimer : filtre de niveaux (aplatir l'eclairage, ecraser le gris pale vers le blanc).
  C_natif   : PDF natif (texte + dessins vectoriels + petites images). Le filigrane diagonal est un trace
              vectoriel a 50 % d'opacite : filtre de niveaux apres suppression des images/textes parasites.
"""
import argparse
import hashlib
import json
import re
import sys

import cv2
import fitz  # PyMuPDF
import numpy as np

TEXTE_PARASITE = re.compile(
    r"gcerevision|concours\s*cameroon|kawlo|past\s+questions|download\s+(our\s+)?app|google\s*play|play\s*store"
    r"|https?://|www\.",
    re.I,
)


def image_de_base(page):
    """Plus grande image couvrant plus de 40 % de la page (>= 1000 px), ou None."""
    aire = page.rect.get_area()
    candidates = []
    for info in page.get_image_info(xrefs=True):
        r = fitz.Rect(info["bbox"]) & page.rect
        if r.get_area() > 0.4 * aire and info["width"] >= 1000:
            candidates.append((r.get_area(), info))
    return max(candidates, key=lambda c: c[0])[1] if candidates else None


def empreinte(doc, xref, cache):
    if xref not in cache:
        try:
            cache[xref] = hashlib.md5(doc.extract_image(xref)["image"]).hexdigest()
        except Exception:
            cache[xref] = None
    return cache[xref]


def images_repetees(doc, seuil=3):
    """Empreintes des images qui reviennent sur au moins `seuil` pages : logos, tuiles, bandeaux."""
    cache, compte = {}, {}
    for p in doc:
        vus = set()
        for info in p.get_image_info(xrefs=True):
            h = empreinte(doc, info["xref"], cache)
            if h and h not in vus:
                vus.add(h)
                compte[h] = compte.get(h, 0) + 1
    return {h for h, c in compte.items() if c >= seuil and len(doc) >= seuil}, cache


def filtre_niveaux(rgb, lo=110, hi=205):
    """Aplatit l'eclairage puis ecrase les gris pales (filigrane) vers le blanc. Renvoie une image en gris."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    fond = cv2.GaussianBlur(cv2.dilate(g, k), (0, 0), 25)
    n = np.clip(g / np.maximum(fond, 1) * 255, 0, 255)
    return (np.clip((n - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)


def gris_pale_residuel(rgb):
    """Part de pixels gris pale loin de tout trait sombre : signature d'un filigrane (ou d'un voile)."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    pale = (g > 150) & (g < 245)
    trait = cv2.dilate((g < 128).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    return float((pale & ~trait).mean())


def rendre_propre(pdf, page_no, dpi=0, filtre="auto", garder_texte=False, lo=110, hi=205, propre=True, doc=None):
    """Rend la page `page_no` (1-based). propre=False : rendu brut tel qu'un lecteur le montre (avec filigrane),
    utile pour retrouver une figure deja recadree. Renvoie (image BGR ou gris uint8, rapport dict)."""
    doc = doc or fitz.open(pdf)
    page = doc[page_no - 1]
    base = image_de_base(page)
    repetees, cache = images_repetees(doc) if propre else (set(), {})

    retirees, textes = [], []
    if propre:
        # 1. supprimer les images parasites (TOUTES les images des ressources de la page, pas seulement celles
        #    dessinees : les tuiles de filigrane sont portees par des formulaires imbriques)
        for img in page.get_images(full=True):
            x = img[0]
            if base is not None and x == base["xref"]:
                continue
            h = empreinte(doc, x, cache)
            if base is not None or h in repetees:
                page.delete_image(x)
                retirees.append({"xref": x, "taille": [img[2], img[3]]})
        # 2. supprimer les textes parasites : on retire la LIGNE entiere des qu'un de ses segments est parasite
        #    (« ... Google play store or visit http://www... » est coupe en plusieurs segments)
        if not garder_texte:
            for b in page.get_text("dict")["blocks"]:
                for l in b.get("lines", []):
                    texte = "".join(s["text"] for s in l["spans"])
                    if TEXTE_PARASITE.search(texte):
                        page.add_redact_annot(fitz.Rect(l["bbox"]))
                        textes.append(texte[:60])
            if textes:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)

    # 3. resolution : native si une numerisation de base existe
    if dpi:
        pass
    elif base is not None:
        largeur_pt = fitz.Rect(base["bbox"]).width
        dpi = int(min(400, max(100, round(base["width"] / (largeur_pt / 72)))))
    else:
        dpi = 200

    pix = page.get_pixmap(dpi=dpi, alpha=False)
    rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy()

    regime = "C_natif" if base is None else ("A_calques" if retirees else "B_cuit")
    residuel = gris_pale_residuel(rgb)
    # auto : filtre pour B et C ; pour A seulement s'il reste du gris pale apres retrait des calques
    # (filigrane MIXTE : calques + texte incruste dans la numerisation)
    appliquer = propre and (filtre == "oui" or (
        filtre == "auto" and (regime in ("B_cuit", "C_natif") or residuel > 0.02)))
    if regime == "A_calques" and appliquer and filtre == "auto":
        regime = "A_calques+cuit"
    sortie = filtre_niveaux(rgb, lo, hi) if appliquer else cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    rapport = {
        "regime": regime, "dpi": dpi, "taille_px": [pix.width, pix.height],
        "objets_supprimes": len(retirees), "textes_supprimes": textes[:6],
        "filtre_niveaux": appliquer, "gris_pale_avant_filtre": round(residuel, 4), "rotation_page": page.rotation,
    }
    return sortie, rapport


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("page", type=int)
    ap.add_argument("sortie")
    ap.add_argument("--dpi", type=int, default=0, help="defaut : resolution native de la numerisation, sinon 200")
    ap.add_argument("--filtre", choices=["auto", "oui", "non"], default="auto")
    ap.add_argument("--garder-texte", action="store_true", help="ne pas supprimer les textes parasites")
    ap.add_argument("--lo", type=int, default=110)
    ap.add_argument("--hi", type=int, default=205)
    a = ap.parse_args()
    sortie, rapport = rendre_propre(a.pdf, a.page, a.dpi, a.filtre, a.garder_texte, a.lo, a.hi)
    # imencode + tofile : evite les soucis de chemins non ASCII sous Windows
    ok, buf = cv2.imencode(".png", sortie)
    buf.tofile(a.sortie)
    print(json.dumps(rapport, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
