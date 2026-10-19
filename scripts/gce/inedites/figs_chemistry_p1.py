"""Figures SVG de l'epreuve inedite GCE O Level Chemistry Paper 1 n.1 (trois figures de DONNEES).

Courbe de solubilite, volume de gaz en fonction du temps, profil energetique d'une reaction. Les constantes ci-dessous sont les memes que celles du
texte des questions ; verifier_reponses_chemistry_p1.py les relit (pas la figure) pour recalculer les reponses.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

# ----------------------------------------------------------------------------------------------- donnees
SOLUBILITE = [(0, 20), (20, 40), (40, 80), (60, 120), (80, 180)]  # (degres C, g de sel X pour 100 g d'eau)
GAZ = [(0, 0), (1, 30), (2, 50), (3, 66), (4, 76), (5, 82), (6, 86), (7, 88), (8, 88)]  # (min, cm3 de gaz)
PROFIL = {"reactifs": 150, "sommet": 240, "produits": 90}  # kJ


def solubilite():
    f = Fig(450, 312, "Courbe de solubilite d'un sel X dans l'eau",
            "Solubilite du sel X en grammes pour 100 grammes d'eau : 20 a 0 degre, 40 a 20 degres, 80 a 40 degres, 120 a 60 degres, 180 a 80 degres.")
    r = Repere(f, 56, 14, 370, 224, 0, 80, 0, 200, xpas=10, ypas=20, xetiq="", yetiq="")
    r.f.polyligne([(r.px(t), r.py(s)) for t, s in SOLUBILITE], stroke=PR, sw=2.5, )
    for t, s in SOLUBILITE:
        r.point(t, s)
    f.texte(r.x0 + r.w / 2, 284, "Temperature (°C)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Solubility (g per 100 g of water)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def volume_gaz():
    f = Fig(450, 312, "Volume de gaz recueilli en fonction du temps",
            "Volume cumule de gaz en centimetres cubes : 0 a 0 minute, 30 a 1 minute, 50 a 2 minutes, 66 a 3 minutes, 76 a 4 minutes, "
            "82 a 5 minutes, 86 a 6 minutes, 88 a 7 minutes, 88 a 8 minutes.")
    r = Repere(f, 56, 14, 370, 224, 0, 8, 0, 100, xpas=1, ypas=10, xetiq="", yetiq="")
    r.f.polyligne([(r.px(t), r.py(v)) for t, v in GAZ], stroke=PR, sw=2.5)
    for t, v in GAZ:
        r.point(t, v)
    f.texte(r.x0 + r.w / 2, 284, "Time (min)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Volume of gas (cm³)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def profil_energie():
    p = PROFIL
    f = Fig(460, 312, "Profil energetique d'une reaction",
            f"Diagramme d'energie : les reactifs sont au niveau {p['reactifs']} kilojoules, le sommet de la courbe est a {p['sommet']} kilojoules et les "
            f"produits sont au niveau {p['produits']} kilojoules.")
    x0, x1, ybas, yhaut = 78, 440, 250, 22
    en = lambda e: ybas - e * (ybas - yhaut) / 300
    f.fleche(x0, ybas, x1 + 6, ybas, FG, 1.6)
    f.fleche(x0, ybas, x0, yhaut - 8, FG, 1.6)
    for e in (0, 100, 200, 300):
        f.ligne(x0 - 3, en(e), x0 + 3, en(e), MU, 1.2)
        f.texte(x0 - 8, en(e) + 4, str(e), taille=12, ancre="end", fill=MU, halo=True)
    for e in (p["reactifs"], p["sommet"], p["produits"]):
        f.ligne(x0, en(e), x0 + 330, en(e), BD, 1.2, "4 4", couche=0)
    f.chemin(f"M{x0 + 14},{en(p['reactifs']):.1f} L{x0 + 80},{en(p['reactifs']):.1f} "
             f"C{x0 + 125},{en(p['reactifs']):.1f} {x0 + 135},{en(p['sommet']):.1f} {x0 + 170},{en(p['sommet']):.1f} "
             f"C{x0 + 205},{en(p['sommet']):.1f} {x0 + 215},{en(p['produits']):.1f} {x0 + 260},{en(p['produits']):.1f} "
             f"L{x0 + 330},{en(p['produits']):.1f}", stroke=PR, sw=2.8)
    for nom, e in (("150", p["reactifs"]), ("240", p["sommet"]), ("90", p["produits"])):
        f.texte(x0 + 340, en(e) + 5, nom, taille=13, ancre="start", fill=DG, gras=True)
    f.texte(x0 + 250, en(0) - 12, "(values in kJ)", taille=12, ancre="start", fill=MU)
    f.texte(x0 + 46, en(p["reactifs"]) - 8, "Reactants", taille=13, fill=FG)
    f.texte(x0 + 296, en(p["produits"]) - 8, "Products", taille=13, fill=FG)
    f.texte(x0 + 4, yhaut - 6, "Energy (kJ)", taille=13, ancre="start", fill=MU)
    f.texte(x0 + 180, 284, "Progress of reaction", taille=14)
    f.legende("{FIG}", y=304)
    return f.render()


def toutes():
    return {"solubilite": solubilite(), "gaz": volume_gaz(), "profil": profil_energie()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
