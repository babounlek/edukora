"""Figures SVG de l'epreuve inedite GCE O Level Biology Paper 1 n.1 : cinq figures de DONNEES (graphiques de resultats et reseau
trophique), calculees a partir des constantes ci-dessous. Aucun schema anatomique ou cellulaire (hors de portee, voir le guide).

Les constantes (DONNEES_*) servent aussi au verificateur : la reponse attendue est relue dans les donnees, pas dans la figure.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

# ----------------------------------------------------------------------------------------------- donnees
TEMP_OPTIMUM = 40  # degres Celsius : activite maximale de l'enzyme
PLATEAU_LUMIERE = 6  # intensite lumineuse (unites arbitraires) a partir de laquelle la courbe est plate
HEURES_TRANSPIRATION = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
TAUX_TRANSPIRATION = [1.0, 1.6, 2.6, 3.8, 5.0, 6.0, 6.8, 7.0, 6.6, 5.6, 4.2, 2.8, 1.6, 0.8, 0.5]  # g par heure
FC_MINUTES = list(range(0, 10))
FC_BATTEMENTS = [150, 125, 105, 90, 80, 74, 70, 70, 70, 70]  # rythme cardiaque apres l'effort
FC_REPOS = 70
RESEAU_ARETES = [("grass", "grasshopper"), ("grass", "rat"), ("maize", "rat"), ("grasshopper", "toad"), ("toad", "snake"),
                 ("rat", "snake"), ("snake", "hawk"), ("rat", "hawk")]


def _act_enzyme(t):
    s = 12 if t <= TEMP_OPTIMUM else 6
    return 10 * math.exp(-(((t - TEMP_OPTIMUM) / s) ** 2))


def enzyme_temperature():
    f = Fig(440, 312, "Effet de la temperature sur l'activite d'une enzyme",
            f"Courbe en cloche : l'activite de l'enzyme augmente de 0 a 40 degres Celsius, ou elle est maximale, puis chute "
            "rapidement et devient nulle vers 60 degres.")
    r = Repere(f, 52, 14, 360, 224, 0, 70, 0, 10, xpas=10, ypas=2, xetiq="", yetiq="")
    r.courbe(_act_enzyme, a=0, b=70, n=280)
    f.texte(r.x0 + r.w / 2, 284, "Temperature (°C)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Rate of reaction", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def photosynthese_lumiere():
    f = Fig(440, 312, "Effet de l'intensite lumineuse sur la vitesse de photosynthese",
            f"La vitesse de photosynthese augmente avec l'intensite lumineuse jusqu'au point P, a l'intensite {PLATEAU_LUMIERE}, "
            "puis reste constante.")
    r = Repere(f, 52, 14, 360, 224, 0, 10, 0, 10, xpas=2, ypas=2, xetiq="", yetiq="")
    r.courbe(lambda x: min(x * 8 / PLATEAU_LUMIERE, 8), a=0, b=10, n=120)
    r.point(PLATEAU_LUMIERE, 8, "P", dx=-4, dy=-10, ancre="end")
    f.texte(r.x0 + r.w / 2, 284, "Light intensity (arbitrary units)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Rate of photosynthesis", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def transpiration_heure():
    assert len(HEURES_TRANSPIRATION) == len(TAUX_TRANSPIRATION)
    f = Fig(460, 312, "Vitesse de transpiration d'une plante au cours de la journee",
            "Courbe en cloche de 6 heures a 20 heures : le taux de transpiration monte de 1,0 a 7,0 grammes par heure a 13 heures, "
            "puis redescend a 0,5 g par heure a 20 heures.")
    r = Repere(f, 54, 14, 380, 224, 6, 20, 0, 8, xpas=2, ypas=2, xetiq="", yetiq="")
    pts = list(zip(HEURES_TRANSPIRATION, TAUX_TRANSPIRATION))
    r.courbe(lambda x: _interp(pts, x), a=6, b=20, n=200)
    for h, v in pts:
        r.point(h, v, couleur=PR)
    f.texte(r.x0 + r.w / 2, 284, "Time of day (hours, 24-hour clock)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Transpiration (g per hour)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def _interp(pts, x):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return pts[-1][1]


def rythme_cardiaque():
    f = Fig(460, 312, "Rythme cardiaque d'un eleve apres un effort",
            "Rythme cardiaque en battements par minute : 150 a l'arret de l'effort, puis 125, 105, 90, 80, 74 et 70 a la sixieme minute ; "
            "il reste ensuite a 70 jusqu'a la neuvieme minute.")
    r = Repere(f, 54, 14, 380, 224, 0, 9, 40, 160, xpas=1, ypas=20, xetiq="", yetiq="")
    pts = list(zip(FC_MINUTES, FC_BATTEMENTS))
    r.courbe(lambda x: _interp(pts, x), a=0, b=9, n=180)
    for m, v in pts:
        r.point(m, v, couleur=PR)
    f.texte(r.x0 + r.w / 2, 284, "Time after exercise (minutes)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Heart rate (beats per minute)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


POSITIONS = {
    "hawk": (180, 30), "snake": (150, 105), "toad": (60, 160), "rat": (330, 175), "grasshopper": (60, 225),
    "grass": (190, 268), "maize": (350, 268),
}
NOMS = {"hawk": "Hawk", "snake": "Snake", "toad": "Toad", "rat": "Rat", "grasshopper": "Grasshopper", "grass": "Grass",
        "maize": "Maize"}


def reseau_trophique():
    f = Fig(440, 312, "Reseau trophique d'une ferme",
            "Les fleches vont de l'organisme mange vers celui qui le mange. Herbe vers sauterelle ; herbe vers rat ; mais vers rat ; "
            "sauterelle vers crapaud ; crapaud vers serpent ; rat vers serpent ; serpent vers faucon ; rat vers faucon.")
    for nom, (cx, cy) in POSITIONS.items():
        f.noeud(nom, cx, cy, 96, 28, forme="arrondi", fill=CARD)
    for a, b in RESEAU_ARETES:
        f.lien(a, b, tete="plein")
    for nom, (cx, cy) in POSITIONS.items():
        f.texte(cx, cy + 5, NOMS[nom], taille=14)
    f.legende("{FIG}", y=304)
    return f.render()


def toutes():
    return {"enzyme": enzyme_temperature(), "lumiere": photosynthese_lumiere(), "transpiration": transpiration_heure(),
            "coeur": rythme_cardiaque(), "reseau": reseau_trophique()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
