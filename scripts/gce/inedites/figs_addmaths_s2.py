"""Figures SVG de la session Additional Mathematics O Level n.2 (Paper 1 n.2 : triangle, droite, region ; Paper 2 n.2 : region et courbe des
effectifs cumules, toutes deux dans le corrige seulement).

Les constantes sont relues par verifier_reponses_addmaths_p1n2.py et verifier_reponses_addmaths_p2n2.py pour recalculer les reponses.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs, _arc  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

TRIANGLE = {"A": 60, "B": 45, "BC": 9}  # degres, degres, cm
DROITE = {"x_int": (4, 0), "y_int": (0, -3)}
REGION = {"y": 2, "somme": 6}  # x >= 0, y >= 2, x + y <= 6 ; sommets (0, 2), (0, 6), (4, 2)
SOMMETS_A5 = [(3, 3), (13.5, 3), (7.2, 7.2)]  # 2x + 3y <= 36, x >= y, y >= 3
EFFECTIFS = [(0, 0), (10, 6), (20, 20), (30, 48), (40, 68), (50, 80)]  # (limite superieure, effectif cumule)


def triangle():
    t = TRIANGLE
    angle_c = 180 - t["A"] - t["B"]
    ech = 13.0
    ab = t["BC"] * math.sin(math.radians(angle_c)) / math.sin(math.radians(t["A"]))
    B = (50.0, 150.0)
    C = (B[0] + t["BC"] * ech, B[1])
    A = (B[0] + ab * ech * math.cos(math.radians(t["B"])), B[1] - ab * ech * math.sin(math.radians(t["B"])))
    f = Fig(380, 206, "Triangle ABC",
            f"Triangle ABC avec un angle de {t['A']} degres en A, un angle de {t['B']} degres en B et BC egal a {t['BC']} centimetres.")
    f.polygone([A, B, C], fill=fs.ACC, stroke=FG, sw=2.2)
    f.texte(A[0] + 10, A[1] - 6, "A", taille=16, gras=True, ancre="start")
    f.texte(B[0] - 14, B[1] + 6, "B", taille=16, gras=True)
    f.texte(C[0] + 12, C[1] + 6, "C", taille=16, gras=True)
    f.texte((B[0] + C[0]) / 2, B[1] + 24, f"{t['BC']} cm", taille=14, fill=INFO, gras=True)
    _arc(f, B, 30, -t["B"], 0)
    f.texte(B[0] + 46, B[1] - 12, f"{t['B']}°", taille=13, fill=DG)
    dir_b = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    dir_c = math.degrees(math.atan2(C[1] - A[1], C[0] - A[0]))
    _arc(f, A, 34, min(dir_b, dir_c), max(dir_b, dir_c))
    f.texte(A[0] - 6, A[1] + 62, f"{t['A']}°", taille=13, fill=DG)
    f.legende("{FIG}", y=198)
    return f.render()


def droite():
    (xa, ya), (xb, yb) = DROITE["x_int"], DROITE["y_int"]
    f = Fig(420, 312, "Droite M coupant les deux axes",
            f"Droite M passant par le point ({xb}, {yb}) sur l'axe des ordonnees et par le point ({xa}, {ya}) sur l'axe des abscisses.")
    r = Repere(f, 52, 14, 340, 240, -2, 7, -4, 3, xpas=1, ypas=1, xetiq="", yetiq="")
    pente = (yb - ya) / (xb - xa)
    r.courbe(lambda x: yb + pente * x, a=-1.2, b=6.2, n=60, couleur=PR)
    r.point(xb, yb, "(0, −3)", dx=10, dy=18)
    r.point(xa, ya, "(4, 0)", dx=-6, dy=-12, ancre="end")
    f.texte(r.px(5.0), r.py(yb + pente * 5.0) - 10, "M", taille=16, fill=PR, gras=True)
    f.texte(r.x0 + r.w / 2, 284, "x", taille=14, fill=MU)
    f.texte(r.x0 + 12, r.y0 + 10, "y", taille=14, fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def region():
    g = REGION
    f = Fig(420, 312, "Region R delimitee par trois droites",
            f"Region R en triangle, delimitee par l'axe des ordonnees, la droite y egal {g['y']} et la droite x plus y egal {g['somme']}, "
            f"avec les sommets (0, {g['y']}), (0, {g['somme']}) et ({g['somme'] - g['y']}, {g['y']}).")
    r = Repere(f, 52, 14, 340, 240, 0, 8, 0, 7, xpas=1, ypas=1, xetiq="", yetiq="")
    sommets = [(0, g["y"]), (0, g["somme"]), (g["somme"] - g["y"], g["y"])]
    f.polygone([(r.px(x), r.py(y)) for x, y in sommets], fill=fs.ACC, stroke="none", sw=0, couche=0)
    f.ligne(r.px(0), r.py(g["y"]), r.px(7.6), r.py(g["y"]), stroke=PR, sw=2.2)
    f.ligne(r.px(0), r.py(g["somme"]), r.px(g["somme"]), r.py(0), stroke=PR, sw=2.2)
    f.texte(r.px(7.6), r.py(g["y"]) - 8, f"y = {g['y']}", taille=13, fill=PR, gras=True, ancre="end")
    f.texte(r.px(4.2), r.py(2.4) - 4, f"x + y = {g['somme']}", taille=13, fill=PR, gras=True, ancre="start")
    f.texte(r.px(0.9), r.py(3.4), "R", taille=18, fill=FG, gras=True)
    f.texte(r.x0 + r.w / 2, 284, "x", taille=14, fill=MU)
    f.texte(r.x0 + 12, r.y0 + 10, "y", taille=14, fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def region_a5():
    f = Fig(450, 340, "Region definie par trois inequations",
            "Triangle de sommets (3, 3), (13,5 ; 3) et (7,2 ; 7,2), delimite par les droites y egal 3, x egal y et 2x plus 3y egal 36.")
    r = Repere(f, 52, 14, 372, 248, 0, 16, 0, 12, xpas=2, ypas=2, xetiq="", yetiq="")
    f.polygone([(r.px(x), r.py(y)) for x, y in SOMMETS_A5], fill=fs.ACC, stroke="none", sw=0, couche=0)
    f.ligne(r.px(0), r.py(3), r.px(15.5), r.py(3), stroke=PR, sw=2.2)
    f.ligne(r.px(0), r.py(0), r.px(11.5), r.py(11.5), stroke=INFO, sw=2.2)
    f.ligne(r.px(16), r.py(4 / 3), r.px(4.5), r.py(9), stroke=DG, sw=2.2)
    f.texte(r.px(15.8), r.py(3) - 8, "y = 3", taille=13, fill=PR, gras=True, ancre="end")
    f.texte(r.px(10.0), r.py(11.3), "y = x", taille=13, fill=INFO, gras=True, ancre="end")
    f.texte(r.px(10.6), r.py(6.5), "2x + 3y = 36", taille=13, fill=DG, gras=True, ancre="start")
    f.texte(r.px(7.2), r.py(4.6), "R", taille=18, gras=True)
    r.point(7.2, 7.2, "(7.2, 7.2)", dx=10, dy=-6)
    r.point(3, 3, "(3, 3)", dx=-10, dy=18, ancre="end")
    r.point(13.5, 3, "(13.5, 3)", dx=-6, dy=20, ancre="end")
    f.texte(r.x0 + r.w / 2, 306, "x (shirts)", taille=14)
    f.texte(r.x0 + 8, r.y0 + 10, "y (pairs of trousers)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=330)
    return f.render()


def effectifs_cumules():
    f = Fig(470, 340, "Courbe des effectifs cumules des temps de jeu",
            "Effectifs cumules : 6 a 10 minutes, 20 a 20, 48 a 30, 68 a 40 et 80 a 50 minutes.")
    r = Repere(f, 56, 14, 380, 248, 0, 50, 0, 80, xpas=10, ypas=10, xetiq="", yetiq="")
    f.polyligne([(r.px(x), r.py(c)) for x, c in EFFECTIFS], stroke=PR, sw=2.6)
    for x, c in EFFECTIFS:
        r.point(x, c)
    # lecture de la mediane (40e valeur), des quartiles (20e et 60e) et du nombre de joueurs de plus de 35 minutes
    for c, nom in ((20, "Q1"), (40, "median"), (60, "Q3")):
        f.ligne(r.px(0), r.py(c), r.px(_lire_x(c)), r.py(c), stroke=DG, sw=1.2, dash="4 4")
        f.ligne(r.px(_lire_x(c)), r.py(c), r.px(_lire_x(c)), r.py(0), stroke=DG, sw=1.2, dash="4 4")
        f.texte(r.px(0) + 6, r.py(c) - 6, nom, taille=12, fill=DG, ancre="start", halo=True)
    f.ligne(r.px(35), r.py(0), r.px(35), r.py(_lire_c(35)), stroke=INFO, sw=1.2, dash="4 4")
    f.ligne(r.px(35), r.py(_lire_c(35)), r.px(0), r.py(_lire_c(35)), stroke=INFO, sw=1.2, dash="4 4")
    f.texte(r.x0 + r.w / 2, 306, "Time (minutes)", taille=14)
    f.texte(r.x0 + 8, r.y0 + 10, "Cumulative frequency", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=330)
    return f.render()


def _lire_x(c):
    """Abscisse de la courbe (interpolation lineaire) pour un effectif cumule c."""
    for (x1, c1), (x2, c2) in zip(EFFECTIFS, EFFECTIFS[1:]):
        if c1 <= c <= c2:
            return x1 + (x2 - x1) * (c - c1) / (c2 - c1)
    raise ValueError(c)


def _lire_c(x):
    for (x1, c1), (x2, c2) in zip(EFFECTIFS, EFFECTIFS[1:]):
        if x1 <= x <= x2:
            return c1 + (c2 - c1) * (x - x1) / (x2 - x1)
    raise ValueError(x)


def toutes():
    return {"triangle": triangle(), "droite": droite(), "region": region(), "region_a5": region_a5(), "cf": effectifs_cumules()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
