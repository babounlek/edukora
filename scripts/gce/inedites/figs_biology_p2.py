"""Figure de CORRIGE du Paper 2 Biology inedit : reseau trophique de l'etang (question 4a). Le trace attendu n'est jamais dans l'enonce."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402
from figures_svg import Fig, CARD  # noqa: E402

ETANG_ARETES = [("algae", "tadpole"), ("lily", "snail"), ("tadpole", "dragonfly"), ("dragonfly", "fish"), ("snail", "fish"), ("fish", "heron")]
NOMS = {"algae": "Algae", "lily": "Water lily", "tadpole": "Tadpole", "snail": "Snail", "dragonfly": "Dragonfly larva",
        "fish": "Small fish", "heron": "Heron"}
POSITIONS = {"heron": (235, 30), "fish": (235, 100), "dragonfly": (90, 165), "snail": (380, 165), "tadpole": (90, 230),
             "algae": (90, 292), "lily": (380, 292)}


def reseau_etang():
    f = Fig(480, 340, "Reseau trophique d'un etang",
            "Les fleches vont de l'organisme mange vers celui qui le mange. Algues vers tetard ; nenuphar vers escargot ; tetard vers "
            "larve de libellule ; larve de libellule vers petit poisson ; escargot vers petit poisson ; petit poisson vers heron.")
    for nom, (cx, cy) in POSITIONS.items():
        f.noeud(nom, cx, cy, 124, 30, forme="arrondi", fill=CARD)
    for a, b in ETANG_ARETES:
        f.lien(a, b, tete="plein")
    for nom, (cx, cy) in POSITIONS.items():
        f.texte(cx, cy + 5, NOMS[nom], taille=14)
    f.legende("Solution: the food web of the pond", y=332)
    return f.render()


def toutes():
    return {"reseau_etang": reseau_etang()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
