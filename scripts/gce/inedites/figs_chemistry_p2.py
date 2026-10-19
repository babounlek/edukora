"""Figures SVG de l'epreuve inedite GCE O Level Chemistry Paper 2 n.1 : courbe de pH d'un titrage (Figure 1) et deux courbes de volume de gaz (Figure 2).

Figures de DONNEES (aucun schema de verrerie) ; les constantes sont relues par verifier_reponses_chemistry_p2.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

# ----------------------------------------------------------------------------------------------- donnees
PH = [(0, 13.0), (5, 12.8), (10, 12.6), (15, 12.4), (20, 12.0), (23, 11.4), (24, 11.1), (24.6, 7.0), (25.2, 2.9), (26, 2.6), (30, 1.9)]  # (cm3 d'acide, pH)
EXP1 = [(0, 0), (20, 36), (40, 60), (60, 78), (80, 92), (100, 104), (120, 112), (140, 118), (160, 120), (180, 120)]  # (s, cm3) : morceaux de marbre
EXP2 = [(0, 0), (20, 60), (40, 96), (60, 114), (80, 120), (100, 120)]  # (s, cm3) : poudre de marbre


def courbe_ph():
    f = Fig(450, 312, "Courbe de pH pendant l'ajout d'un acide a une solution d'hydroxyde de potassium",
            "pH en fonction du volume d'acide chlorhydrique ajoute : 13 au depart, qui diminue lentement jusqu'a environ 11 a 23 centimetres cubes, "
            "chute brutale entre 24 et 25 centimetres cubes, puis se stabilise vers 2.")
    r = Repere(f, 52, 14, 372, 224, 0, 30, 0, 14, xpas=5, ypas=1, xetiq="", yetiq="")
    r.f.polyligne([(r.px(v), r.py(p)) for v, p in PH], stroke=PR, sw=2.5)
    f.texte(r.x0 + r.w / 2, 284, "Volume of acid added (cm³)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "pH", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def courbes_gaz():
    f = Fig(450, 330, "Volume de dioxyde de carbone en fonction du temps pour deux experiences",
            "Experience 1 (morceaux de marbre) : 36 centimetres cubes a 20 secondes, 60 a 40 secondes, 78 a 60, 92 a 80, 104 a 100, 112 a 120, 118 a 140, puis 120 "
            "a partir de 160 secondes. Experience 2 (poudre de marbre) : 60 centimetres cubes a 20 secondes, 96 a 40, 114 a 60, puis 120 a partir de 80 secondes.")
    r = Repere(f, 52, 14, 372, 224, 0, 180, 0, 130, xpas=20, ypas=10, xetiq="", yetiq="")
    r.f.polyligne([(r.px(t), r.py(v)) for t, v in EXP1], stroke=PR, sw=2.5)
    r.f.polyligne([(r.px(t), r.py(v)) for t, v in EXP2], stroke=INFO, sw=2.5)
    f.texte(r.px(120), r.py(100), "Experiment 1", taille=13, fill=PR, gras=True, ancre="start")
    f.texte(r.px(3), r.py(112), "Experiment 2", taille=13, fill=INFO, gras=True, ancre="start")
    f.texte(r.x0 + r.w / 2, 284, "Time (s)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Volume of CO₂ (cm³)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=322)
    return f.render()


def toutes():
    return {"ph": courbe_ph(), "gaz2": courbes_gaz()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
