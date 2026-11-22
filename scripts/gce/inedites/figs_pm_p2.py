"""Figure SVG de l'epreuve inedite GCE A Level Pure Mathematics Paper 2 n.1 : courbe de l'exercice 9, dans le CORRIGE seulement.

f(x) = (x^2 - 4)/(x^2 - 1) = 1 - 3/(x^2 - 1). Les coordonnees sortent de la meme fonction que verifier_reponses_pm_p2.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402,F401  (fs.DECIMAL = "." deja applique, chemin de figures_svg ajoute)
from figures_svg import Fig, Repere, FG, MU, PR, INFO  # noqa: E402


def f9(x):
    return (x * x - 4) / (x * x - 1)


def courbe_f():
    f = Fig(450, 360, "Courbe de f(x) = (x^2 - 4)/(x^2 - 1)",
            "Courbe a trois branches, symetrique par rapport a l'axe des y. Asymptotes verticales x egal moins 1 et x egal 1, asymptote horizontale y egal 1. "
            "La branche centrale a son minimum en (0, 4) et monte vers plus l'infini le long des deux asymptotes verticales. "
            "Les deux branches exterieures viennent de moins l'infini le long de x egal plus ou moins 1, coupent l'axe des x en (-2, 0) et (2, 0) et se rapprochent de y egal 1 par en dessous.")
    r = Repere(f, 52, 14, 372, 290, -5, 5, -6, 8, xpas=1, ypas=2, xetiq="x", yetiq="y")
    r.asymptote_v(-1)
    f.texte(r.px(-1) - 5, r.y0 + 12, "x = -1", taille=12, ancre="end", fill=MU, halo=True)
    r.asymptote_v(1, "x = 1")
    r.asymptote_h(1, "y = 1")
    r.courbe(f9, a=-5, b=-1.0005, n=260, couleur=PR, epaisseur=2.5)
    r.courbe(f9, a=-0.9995, b=0.9995, n=260, couleur=PR, epaisseur=2.5)
    r.courbe(f9, a=1.0005, b=5, n=260, couleur=PR, epaisseur=2.5)
    r.point(-2, 0, "(-2, 0)", dx=-4, dy=32, ancre="end")
    r.point(2, 0, "(2, 0)", dx=4, dy=32)
    r.point(0, 4, "(0, 4)", dx=10, dy=-6)
    f.legende("Solution: graph of y = f(x)", y=350)
    return f.render()


def toutes():
    return {"courbe_f": courbe_f()}
