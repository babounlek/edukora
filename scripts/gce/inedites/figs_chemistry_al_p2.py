"""Figure SVG de l'epreuve inedite GCE A Level Chemistry Paper 2 n.1 : decroissance de la concentration d'une reaction du premier ordre
(exercice 3, question c), dans le CORRIGE seulement.

c(t) = 0.800 * (1/2)^(t/30) mol/dm3 ; les points marques (0, 30, 60, 90 min) sortent de la meme fonction que verifier_reponses_chemistry_al_p2.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402,F401  (fs.DECIMAL = "." deja applique, chemin de figures_svg ajoute)
from figures_svg import Fig, Repere, FG, MU, PR, INFO  # noqa: E402

C0 = 0.800
T_DEMI = 30.0


def conc(t):
    return C0 * 0.5 ** (t / T_DEMI)


def courbe_decroissance():
    f = Fig(450, 336, "Concentration de peroxyde d'hydrogene en fonction du temps (premier ordre)",
            "Courbe exponentielle decroissante : 0.800 mol/dm3 a 0 minute, 0.400 a 30 minutes, 0.200 a 60 minutes, 0.100 a 90 minutes. "
            "La concentration est divisee par deux a chaque intervalle de 30 minutes (demi-vie constante).")
    r = Repere(f, 62, 14, 362, 254, 0, 90, 0, 0.9, xpas=10, ypas=0.1, xetiq="", yetiq="")
    r.courbe(conc, a=0, b=90, couleur=PR, epaisseur=2.5)
    for t in (0, 30, 60, 90):
        c = conc(t)
        r.point(t, c, f"{c:.3f}", dx=(-10 if t == 90 else 10), dy=(-12 if t == 90 else -8), ancre=("end" if t == 90 else "start"))
        if t:
            r.segment(0, c, t, c, couleur=INFO, dash="5 4", epaisseur=1.2)
            r.segment(t, 0, t, c, couleur=INFO, dash="5 4", epaisseur=1.2)
    f.texte(r.x0 + r.w / 2, 308, "Time (min)", taille=14)
    f.texte(r.x0 + 12, r.y0 - 4, "[H₂O₂] (mol/dm³)", taille=13, ancre="start", fill=MU)
    f.legende("Solution: concentration against time", y=326)
    return f.render()


def toutes():
    return {"decroissance": courbe_decroissance()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
