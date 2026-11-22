"""Figures SVG de l'epreuve inedite GCE A Level ICT Paper 2 n.1, dans le CORRIGE seulement.

- "etoile" (exercice 3, question b) : reseau en etoile de N_ORDINATEURS postes autour d'un commutateur, un cable par poste (N_ORDINATEURS cables) ;
- "circuit" (exercice 8, question a) : circuit logique de X = S AND (D OR W), decrit par CIRCUIT (evalue par verifier_reponses_ict_al_p2.py).
Les coordonnees sont calculees, pas dessinees a l'oeil.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "outils_figures"))
import figures_svg as fs  # noqa: E402
from figures_svg import Fig, FG, MU, PR, CARD, icone_reseau  # noqa: E402

fs.DECIMAL = "."

N_ORDINATEURS = 12
CIRCUIT = ("AND", "S", ("OR", "D", "W"))  # X = S AND (D OR W)


def evaluer(noeud, valeurs):
    """Evalue le circuit pour un dictionnaire d'entrees {nom: 0/1}."""
    if isinstance(noeud, str):
        return valeurs[noeud]
    op, *args = noeud
    v = [evaluer(a, valeurs) for a in args]
    if op == "AND":
        return int(all(v))
    if op == "OR":
        return int(any(v))
    raise ValueError(op)


def etoile():
    n = N_ORDINATEURS
    f = Fig(420, 372, "Reseau en etoile de douze ordinateurs",
            f"Un commutateur au centre et {n} ordinateurs repartis regulierement autour, chacun relie au commutateur par son propre cable : {n} cables au total.")
    cx, cy, r = 210, 176, 128
    icone_reseau(f, "sw", "commutateur", cx, cy, "", position="bas")
    for i in range(n):
        ang = -90 + i * 360 / n
        x, y = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
        icone_reseau(f, f"pc{i}", "pc", x, y, str(i + 1), position="haut" if y < cy else "bas")
        f.lien("sw", f"pc{i}", stroke=PR, sw=1.6)
    f.legende(f"Star topology: central switch, {n} computers, {n} cables", y=366)
    return f.render()


def _or(f, x0, yc):
    """Porte OR de largeur 56 et de hauteur 44 ; entrees a yc-11 et yc+11, sortie a (x0+56, yc)."""
    f.chemin(f"M{x0},{yc - 22} Q{x0 + 30},{yc - 22} {x0 + 56},{yc} Q{x0 + 30},{yc + 22} {x0},{yc + 22} Q{x0 + 14},{yc} {x0},{yc - 22} Z",
             fill=CARD, stroke=FG, sw=1.6, couche=2)
    f.texte(x0 + 30, yc + 5, "OR", taille=13, fill=MU)
    return (x0 + 56, yc)


def _and(f, x0, yc):
    """Porte AND : entrees a (x0, yc-11) et (x0, yc+11), sortie a (x0+50, yc)."""
    f.chemin(f"M{x0},{yc - 22} H{x0 + 28} A22 22 0 0 1 {x0 + 28},{yc + 22} H{x0} Z", fill=CARD, stroke=FG, sw=1.6, couche=2)
    f.texte(x0 + 22, yc + 5, "AND", taille=13, fill=MU)
    return (x0 + 50, yc)


def circuit():
    f = Fig(400, 176, "Circuit logique de l'alarme X = S AND (D OR W)",
            "Une porte OR recoit D et W ; sa sortie et S entrent dans une porte AND dont la sortie est X.")
    or_x, or_y = 120, 94
    and_x, and_y = 236, 116
    # entrees D et W directement sur les entrees de la porte OR
    for nom, y in (("D", or_y - 11), ("W", or_y + 11)):
        f.texte(40, y + 5, nom, taille=15, ancre="end", gras=True)
        f.ligne(48, y, or_x + 7, y, stroke=FG, sw=1.5)
    sortie_or = _or(f, or_x, or_y)
    # sortie de OR vers l'entree haute de AND (decrochement vertical)
    xm = and_x - 18
    f.polyligne([sortie_or, (xm, or_y), (xm, and_y - 11), (and_x, and_y - 11)], stroke=FG, sw=1.5)
    # entree S sur l'entree basse de AND
    f.texte(40, and_y + 11 + 5, "S", taille=15, ancre="end", gras=True)
    f.ligne(48, and_y + 11, and_x, and_y + 11, stroke=FG, sw=1.5)
    sortie_and = _and(f, and_x, and_y)
    f.ligne(sortie_and[0], sortie_and[1], 340, and_y, stroke=FG, sw=1.5)
    f.texte(352, and_y + 5, "X", taille=15, ancre="start", gras=True)
    f.legende("X = S AND (D OR W)", y=170)
    return f.render()


def toutes():
    return {"etoile": etoile(), "circuit": circuit()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
