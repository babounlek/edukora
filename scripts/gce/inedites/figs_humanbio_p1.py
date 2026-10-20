"""Figures SVG de l'epreuve inedite GCE O Level Human Biology Paper 1 n.1 (trois figures de DONNEES, aucun schema anatomique).

Trace d'un spirometre, frequence du pouls apres un effort, arbre genealogique d'un couple. Les constantes sont relues par
verifier_reponses_humanbio_p1.py (pas la figure) pour recalculer les reponses.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

SPIRO = {"min": 2500, "max": 3000, "respirations": 3, "duree": 12}  # cm3, cm3, nombre, secondes
POULS = [(0, 130), (1, 110), (2, 100), (3, 90), (4, 80), (5, 76), (6, 74), (7, 72), (8, 72)]  # (min, battements par minute)
ARBRE = {"parents": ("sain", "sain"), "enfant1": "atteint", "enfant2": "sain"}


def spirometre():
    s = SPIRO
    f = Fig(450, 312, "Volume d'air dans les poumons d'une personne au repos pendant douze secondes",
            f"Le volume oscille {s['respirations']} fois entre {s['min']} et {s['max']} centimetres cubes en {s['duree']} secondes.")
    r = Repere(f, 64, 14, 360, 224, 0, s["duree"], 2400, 3100, xpas=2, ypas=100, xetiq="", yetiq="")
    moy, amp = (s["min"] + s["max"]) / 2, (s["max"] - s["min"]) / 2
    periode = s["duree"] / s["respirations"]
    pts = [(r.px(t), r.py(moy - amp * math.cos(2 * math.pi * t / periode))) for t in [i * s["duree"] / 240 for i in range(241)]]
    f.polyligne(pts, stroke=PR, sw=2.6)
    f.texte(r.x0 + r.w / 2, 284, "Time (s)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Volume of air in the lungs (cm³)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def pouls():
    f = Fig(450, 312, "Pouls d'un eleve apres une course",
            "Pouls en battements par minute : 130 a 0 minute, 110 a 1, 100 a 2, 90 a 3, 80 a 4, 76 a 5, 74 a 6, 72 a 7 et 72 a 8 minutes.")
    r = Repere(f, 56, 14, 370, 224, 0, 8, 60, 140, xpas=1, ypas=10, xetiq="", yetiq="", axes_origine=False)
    f.polyligne([(r.px(t), r.py(v)) for t, v in POULS], stroke=PR, sw=2.5)
    for t, v in POULS:
        r.point(t, v)
    f.texte(r.x0 + r.w / 2, 284, "Time after the run (min)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Pulse rate (beats per minute)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def arbre():
    f = Fig(420, 340, "Arbre genealogique d'une famille : deux parents et deux enfants",
            "Un homme sain et une femme saine ont deux enfants : un garcon atteint d'anemie drepanocytaire (colore) et une fille saine.")
    haut, taille = 70, 44
    p1, p2 = (140, haut), (280, haut)
    f.rect(p1[0] - taille / 2, p1[1] - taille / 2, taille, taille, rx=0, fill=CARD, stroke=FG, sw=2.4)
    f.cercle(p2[0], p2[1], taille / 2, fill=CARD, stroke=FG, sw=2.4)
    f.ligne(p1[0] + taille / 2, haut, p2[0] - taille / 2, haut, stroke=FG, sw=2.2)
    milieu = (p1[0] + p2[0]) / 2
    bas = 200
    f.ligne(milieu, haut, milieu, bas - 50, stroke=FG, sw=2.2)
    e1, e2 = (milieu - 70, bas), (milieu + 70, bas)
    f.ligne(e1[0], bas - 50, e2[0], bas - 50, stroke=FG, sw=2.2)
    f.ligne(e1[0], bas - 50, e1[0], bas - taille / 2, stroke=FG, sw=2.2)
    f.ligne(e2[0], bas - 50, e2[0], bas - taille / 2, stroke=FG, sw=2.2)
    f.rect(e1[0] - taille / 2, bas - taille / 2, taille, taille, rx=0, fill=DG, stroke=FG, sw=2.4)
    f.cercle(e2[0], bas, taille / 2, fill=CARD, stroke=FG, sw=2.4)
    f.texte(p1[0], p1[1] - 34, "Father", taille=13, fill=MU)
    f.texte(p2[0], p2[1] - 34, "Mother", taille=13, fill=MU)
    f.rect(120, 252, 18, 18, rx=0, fill=DG, stroke=FG, sw=1.6)
    f.texte(146, 266, "affected by sickle cell anaemia", taille=13, ancre="start")
    f.texte(120, 296, "square: male     circle: female", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=330)
    return f.render()


def toutes():
    return {"spiro": spirometre(), "pouls": pouls(), "pedigree": arbre()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
