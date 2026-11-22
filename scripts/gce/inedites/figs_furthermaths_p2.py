"""Figure SVG de l'epreuve inedite GCE A Level Further Mathematics Paper 2 n.1 : courbe de l'exercice 9, dans le CORRIGE seulement.

f(x) = (x^2 - x - 6)/(x - 1) = x - 6/(x - 1). Les coordonnees sortent de la meme fonction que verifier_reponses_furthermaths_p2.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402,F401  (fs.DECIMAL = "." deja applique, chemin de figures_svg ajoute)
from figures_svg import Fig, Repere, FG, MU, PR, INFO  # noqa: E402


def f9(x):
    return (x * x - x - 6) / (x - 1)


def courbe_f():
    f = Fig(450, 360, "Courbe de f(x) = (x^2 - x - 6)/(x - 1)",
            "Courbe a deux branches. Asymptote verticale x egal 1 et asymptote oblique y egal x. La branche de gauche passe par (-2, 0) et (0, 6) et monte vers plus l'infini le long de x egal 1. "
            "La branche de droite vient de moins l'infini le long de x egal 1, passe par (3, 0) et se rapproche de y egal x.")
    r = Repere(f, 52, 14, 372, 290, -6, 8, -8, 12, xpas=2, ypas=2, xetiq="x", yetiq="y")
    r.asymptote_v(1, "x = 1")
    r.droite(1, 0, couleur=INFO, nom="y = x", nom_pos=(r.px(6.2), r.py(8.4)))
    r.courbe(f9, a=-6, b=0.999, couleur=PR, epaisseur=2.5)
    r.courbe(f9, a=1.001, b=8, couleur=PR, epaisseur=2.5)
    r.point(-2, 0, "(-2, 0)", dx=-6, dy=-10, ancre="end")
    r.point(3, 0, "(3, 0)", dx=0, dy=34, ancre="middle")
    r.point(0, 6, "(0, 6)", dx=10, dy=-6)
    f.legende("Solution: graph of y = f(x)", y=350)
    return f.render()


def toutes():
    return {"courbe_f": courbe_f()}
