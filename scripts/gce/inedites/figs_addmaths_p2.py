"""Figures SVG de l'epreuve inedite GCE O Level Additional Mathematics Paper 2 n.1.

Une figure d'ENONCE (machine d'Atwood, Figure 1) et deux figures de CORRIGE (region des contraintes, courbe trigonometrique) : un trace
attendu n'est jamais dans l'enonce. Toutes les coordonnees sont calculees a partir des constantes ci-dessous, relues par
verifier_reponses_addmaths_p2.py.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

ATWOOD = {"m1": 3, "m2": 5}  # kg
# contraintes de la question 5 : 4x + 3y <= 44, x >= 2y, x >= 0, y >= 0 ; sommets de la region
SOMMETS_REGION = [(0, 0), (11, 0), (8, 4)]
FONCTION_TRIG = lambda x: 3 * math.cos(2 * x)  # f(x) = 3 cos 2x sur [0, pi]


def atwood():
    m1, m2 = ATWOOD["m1"], ATWOOD["m2"]
    f = Fig(300, 300, "Deux masses reliees par un fil passant sur une poulie",
            f"Une poulie fixe. Un fil leger la traverse. Une masse de {m1} kilogrammes pend d'un cote et une masse de {m2} kilogrammes de l'autre.")
    cx, cy, r = 150, 62, 42
    f.ligne(cx, 14, cx, cy - r, stroke=FG, sw=3)
    f.cercle(cx, cy, r, fill=CARD, stroke=FG, sw=2.4)
    f.cercle(cx, cy, 4, fill=FG, stroke=FG, sw=1)
    xg, xd = cx - r, cx + r
    yg, yd = 190, 190  # les deux masses au meme niveau : l'instant du lacher ne dit pas quelle masse descend
    f.ligne(xg, cy, xg, yg, stroke=FG, sw=2)
    f.ligne(xd, cy, xd, yd, stroke=FG, sw=2)
    for x, y, m in ((xg, yg, m1), (xd, yd, m2)):
        h = 26 + 5 * m
        f.rect(x - 24, y, 48, h, rx=3, fill=fs.ACC, stroke=FG, sw=2)
        f.texte(x, y + h / 2 + 5, f"{m} kg", taille=14, gras=True)
    f.legende("{FIG}", y=292)
    return f.render()


def _pt_region(r, x, y):
    return (r.px(x), r.py(y))


def region_contraintes():
    f = Fig(450, 340, "Region definie par quatre inequations",
            "Triangle de sommets (0, 0), (11, 0) et (8, 4), delimite par l'axe des abscisses, la droite x egal 2y et la droite 4x plus 3y egal 44.")
    r = Repere(f, 52, 14, 372, 248, 0, 12, 0, 8, xpas=1, ypas=1, xetiq="", yetiq="")
    f.polygone([_pt_region(r, x, y) for x, y in SOMMETS_REGION], fill=fs.ACC, stroke="none", sw=0, couche=0)
    f.ligne(*_pt_region(r, 0, 0), *_pt_region(r, 12, 6), stroke=PR, sw=2.2)
    f.ligne(*_pt_region(r, 11, 0), *_pt_region(r, 5, 8), stroke=INFO, sw=2.2)
    f.texte(r.px(11.9), r.py(6) - 12, "x = 2y", taille=13, fill=PR, gras=True, ancre="end")
    f.texte(r.px(5.7), r.py(7.2), "4x + 3y = 44", taille=13, fill=INFO, gras=True, ancre="start")
    f.texte(r.px(4.5), r.py(1.2), "R", taille=18, gras=True)
    r.point(8, 4, "(8, 4)", dx=12, dy=22)
    f.texte(r.x0 + r.w / 2, 306, "x (bags of rice)", taille=14)
    f.texte(r.x0 + 8, r.y0 + 10, "y (bags of beans)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=330)
    return f.render()


def courbe_trig():
    f = Fig(470, 340, "Graphe de y egal trois cosinus deux x pour x de 0 a pi",
            "Courbe qui part du maximum 3 en x egal 0, coupe l'axe en pi sur 4, atteint le minimum moins 3 en pi sur 2, coupe l'axe en 3 pi sur 4 "
            "et revient au maximum 3 en x egal pi.")
    x0, y0, w, h = 60, 16, 380, 250
    ymin, ymax = -4, 4
    px = lambda x: x0 + x / math.pi * w
    py = lambda y: y0 + h - (y - ymin) / (ymax - ymin) * h
    for k in range(0, 5):
        f.ligne(px(k * math.pi / 4), y0, px(k * math.pi / 4), y0 + h, BD, 1, couche=0)
    for v in range(ymin, ymax + 1):
        f.ligne(x0, py(v), x0 + w, py(v), BD, 1, couche=0)
        f.ligne(x0 - 3, py(v), x0 + 3, py(v), MU, 1.2)
        f.texte(x0 - 8, py(v) + 4, str(v).replace("-", "\u2212"), taille=12, ancre="end", fill=MU, halo=True)
    f.fleche(x0, py(0), x0 + w + 8, py(0), FG, 1.6)
    f.fleche(x0, y0 + h, x0, y0 - 6, FG, 1.6)
    for k, e in enumerate(["0", "\u03c0/4", "\u03c0/2", "3\u03c0/4", "\u03c0"]):
        f.ligne(px(k * math.pi / 4), py(0) - 3, px(k * math.pi / 4), py(0) + 3, MU, 1.2)
        f.texte(px(k * math.pi / 4), py(0) + 18 if k else py(0) + 18, e, taille=12, fill=MU, halo=True)
    pts = [(px(i * math.pi / 120), py(FONCTION_TRIG(i * math.pi / 120))) for i in range(0, 121)]
    f.polyligne(pts, stroke=PR, sw=2.6)
    cles = [(0, "(0, 3)", 10, -8, "start"), (math.pi / 2, "(\u03c0/2, \u22123)", 10, 16, "start"), (math.pi, "(\u03c0, 3)", -8, -8, "end")]
    for xk, lab, dx, dy, anc in cles:
        f.cercle(px(xk), py(FONCTION_TRIG(xk)), 3.5, fill=DG, stroke=DG, sw=1)
        f.texte(px(xk) + dx, py(FONCTION_TRIG(xk)) + dy, lab, taille=12, fill=DG, ancre=anc, halo=True)
    for xk in (math.pi / 4, 3 * math.pi / 4):
        f.cercle(px(xk), py(0), 3.5, fill=DG, stroke=DG, sw=1)
    f.texte(x0 + w / 2, 304, "x (radians)", taille=14)
    f.texte(x0 + 8, y0 + 8, "y", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=330)
    return f.render()


def toutes():
    return {"atwood": atwood(), "region": region_contraintes(), "trig": courbe_trig()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
