"""Figures SVG de l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.1 (trois figures calculees).

Triangle de la regle des sinus, droite coupant les axes, region definie par trois droites. Les constantes sont relues par
verifier_reponses_addmaths_p1.py pour recalculer les reponses (pas la figure).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs, _arc  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

TRIANGLE = {"A": 30, "B": 45, "BC": 10}  # degres, degres, cm
DROITE = {"x_int": (6, 0), "y_int": (0, 4)}
REGION = {"x": 1, "y": 4}  # droites x = 1, y = 4 et y = x ; sommets (1, 1), (1, 4), (4, 4)


def triangle():
    t = TRIANGLE
    angle_c = 180 - t["A"] - t["B"]
    ech = 12.0  # pixels par cm
    ab = t["BC"] * math.sin(math.radians(angle_c)) / math.sin(math.radians(t["A"]))
    B = (50.0, 236.0)
    C = (B[0] + t["BC"] * ech, B[1])
    A = (B[0] + ab * ech * math.cos(math.radians(t["B"])), B[1] - ab * ech * math.sin(math.radians(t["B"])))
    f = Fig(380, 290, "Triangle ABC",
            f"Triangle ABC avec un angle de {t['A']} degres en A, un angle de {t['B']} degres en B et BC egal a {t['BC']} centimetres.")
    f.polygone([A, B, C], fill=fs.ACC, stroke=FG, sw=2.2)
    f.texte(A[0] + 10, A[1] - 6, "A", taille=16, gras=True, ancre="start")
    f.texte(B[0] - 14, B[1] + 6, "B", taille=16, gras=True)
    f.texte(C[0] + 12, C[1] + 6, "C", taille=16, gras=True)
    f.texte((B[0] + C[0]) / 2, B[1] + 24, f"{t['BC']} cm", taille=14, fill=INFO, gras=True)
    # angle B : entre BA (-45 degres ecran) et BC (0 degre)
    _arc(f, B, 30, -t["B"], 0)
    f.texte(B[0] + 46, B[1] - 12, f"{t['B']}°", taille=13, fill=DG)
    # angle A : entre AC et AB (directions mesurees depuis A)
    dir_b = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    dir_c = math.degrees(math.atan2(C[1] - A[1], C[0] - A[0]))
    _arc(f, A, 34, min(dir_b, dir_c), max(dir_b, dir_c))
    f.texte(A[0] - 30, A[1] + 56, f"{t['A']}°", taille=13, fill=DG)
    f.legende("{FIG}", y=282)
    return f.render()


def droite():
    (xa, ya), (xb, yb) = DROITE["x_int"], DROITE["y_int"]
    f = Fig(420, 312, "Droite L coupant les deux axes",
            f"Droite L passant par le point ({xb}, {yb}) sur l'axe des ordonnees et par le point ({xa}, {ya}) sur l'axe des abscisses.")
    r = Repere(f, 52, 14, 340, 240, -1, 8, -1, 6, xpas=1, ypas=1, xetiq="", yetiq="")
    pente = (yb - ya) / (xb - xa)
    r.courbe(lambda x: yb + pente * x, a=-0.9, b=7.6, n=60, couleur=PR)
    r.point(xb, yb, "(0, 4)", dx=10, dy=-6)
    r.point(xa, ya, "(6, 0)", dx=12, dy=-12, ancre="start")
    f.texte(r.px(1.2), r.py(4 + pente * 1.2) - 10, "L", taille=16, fill=PR, gras=True)
    f.texte(r.x0 + r.w / 2, 284, "x", taille=14, fill=MU)
    f.texte(r.x0 + 12, r.y0 + 10, "y", taille=14, fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def region():
    g = REGION
    f = Fig(420, 312, "Region R delimitee par trois droites",
            f"Region R en triangle, delimitee par les droites x egal {g['x']}, y egal {g['y']} et y egal x, avec les sommets (1, 1), (1, 4) et (4, 4).")
    r = Repere(f, 52, 14, 340, 240, 0, 7, 0, 5.5, xpas=1, ypas=1, xetiq="", yetiq="")
    sommets = [(g["x"], g["x"]), (g["x"], g["y"]), (g["y"], g["y"])]
    f.polygone([(r.px(x), r.py(y)) for x, y in sommets], fill=fs.ACC, stroke="none", sw=0, couche=0)
    f.ligne(r.px(g["x"]), r.py(0), r.px(g["x"]), r.py(5.3), stroke=PR, sw=2.2)
    f.ligne(r.px(0), r.py(g["y"]), r.px(6.8), r.py(g["y"]), stroke=PR, sw=2.2)
    f.ligne(r.px(0), r.py(0), r.px(5.3), r.py(5.3), stroke=PR, sw=2.2)
    f.texte(r.px(g["x"]) + 8, r.py(5.2), f"x = {g['x']}", taille=13, fill=PR, gras=True, ancre="start")
    f.texte(r.px(6.8), r.py(g["y"]) - 8, f"y = {g['y']}", taille=13, fill=PR, gras=True, ancre="end")
    f.texte(r.px(4.9), r.py(5.0), "y = x", taille=13, fill=PR, gras=True, ancre="start")
    f.texte(r.px(2.1), r.py(3.2), "R", taille=18, fill=FG, gras=True)
    f.texte(r.x0 + r.w / 2, 284, "x", taille=14, fill=MU)
    f.texte(r.x0 + 12, r.y0 + 10, "y", taille=14, fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def toutes():
    return {"triangle": triangle(), "droite": droite(), "region": region()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
