"""Figures SVG de l'epreuve inedite GCE O Level Physics Paper 1 n.1 (six figures) et helpers de circuit reutilises par le Paper 2.

Toutes les figures sortent des constantes ci-dessous ; le verificateur relit ces constantes (pas la figure) pour recalculer les reponses.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import fs, _pt  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

OHM = "Ω"
# ----------------------------------------------------------------------------------------------- donnees
VT_POINTS = [(0, 0), (6, 12), (10, 12)]  # velocity-time : (s, m/s)
REGLE = {"pivot": 50, "poids_connu": 4, "position_connue": 20, "poids_inconnu": 6}  # cm, N
CHAUFFE = [(0, -10), (2, 0), (6, 0), (9, 100), (15, 100), (17, 130)]  # (min, degres C) : points A..F
ANGLE_INCIDENCE = 35
CIRCUIT_P1 = {"U": 12, "R1": 4, "R2": 6, "R3": 3}
GRAPHES_OPTIONS = {"a": "droite ne passant pas par l'origine", "b": "courbe", "c": "droite passant par l'origine", "d": "horizontale"}
CLE_GRAPHES = "c"


# ----------------------------------------------------------------------------------------------- p05 : velocity-time
def vitesse_temps():
    f = Fig(440, 312, "Graphique vitesse-temps d'une voiture",
            "La vitesse augmente regulierement de 0 a 12 metres par seconde en 6 secondes, puis reste constante a 12 metres par "
            "seconde jusqu'a 10 secondes.")
    r = Repere(f, 52, 14, 360, 224, 0, 12, 0, 14, xpas=2, ypas=2, xetiq="", yetiq="")
    r.courbe(lambda x: min(x * 2, 12) if x <= 10 else None, a=0, b=10, n=100)
    f.texte(r.x0 + r.w / 2, 284, "Time (s)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Velocity (m/s)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


# ----------------------------------------------------------------------------------------------- p11 : regle en equilibre
def regle_equilibre():
    f = Fig(480, 200, "Regle uniforme en equilibre sur un pivot",
            f"Regle d'un metre de long posee sur un pivot a la graduation {REGLE['pivot']} centimetres. Un poids de {REGLE['poids_connu']} newtons est "
            f"suspendu a la graduation {REGLE['position_connue']} centimetres. Un poids de {REGLE['poids_inconnu']} newtons doit etre suspendu du "
            "cote droit pour que la regle reste horizontale.")
    x0, x1, y = 30, 450, 90
    px = lambda cm: x0 + cm / 100 * (x1 - x0)
    f.rect(x0, y, x1 - x0, 14, rx=2, fill=fs.ACC, stroke=FG, sw=1.6)
    for cm in range(0, 101, 10):
        f.ligne(px(cm), y + 14, px(cm), y + 20, stroke=FG, sw=1.2)
        if cm != REGLE["pivot"]:  # la graduation du pivot est cachee par le triangle : le texte l'indique
            f.texte(px(cm), y + 36, str(cm), taille=12, fill=MU)
    f.polygone([(px(REGLE["pivot"]) - 14, y + 52), (px(REGLE["pivot"]) + 14, y + 52), (px(REGLE["pivot"]), y + 14)], fill=CARD, stroke=FG, sw=1.6)
    f.texte(px(REGLE["pivot"]), y + 70, "pivot", taille=13, fill=MU)
    xa = px(REGLE["position_connue"])
    f.fleche(xa, y - 4, xa, y - 52, stroke=DG, sw=2, tete="plein")
    f.texte(xa, y - 58, f"{REGLE['poids_connu']} N", taille=14, fill=DG, gras=True)
    xb = px(70)
    f.fleche(xb, y - 4, xb, y - 52, stroke=INFO, sw=2, tete="plein", dash="5 4")
    f.texte(xb, y - 58, f"{REGLE['poids_inconnu']} N", taille=14, fill=INFO, gras=True)
    f.texte(xb, y - 74, "position ?", taille=13, fill=INFO)
    f.legende("{FIG}", y=192)
    return f.render()


# ----------------------------------------------------------------------------------------------- p24 : courbe de chauffe
def courbe_chauffe():
    f = Fig(460, 312, "Courbe de chauffe d'une substance",
            "Temperature en fonction du temps : elle monte de moins 10 a 0 degre Celsius (A a B), reste a 0 degre pendant 4 minutes (B a C), "
            "monte a 100 degres (C a D), reste a 100 degres pendant 6 minutes (D a E), puis monte a 130 degres (E a F).")
    r = Repere(f, 56, 14, 380, 224, 0, 18, -20, 140, xpas=2, ypas=20, xetiq="", yetiq="", axes_origine=False)
    pts = CHAUFFE
    r.courbe(lambda x: _interp(pts, x), a=0, b=17, n=170)
    for i, ((t, v), nom) in enumerate(zip(pts, "ABCDEF")):
        if i == 0:
            r.point(t, v, nom, dx=10, dy=18, ancre="start", couleur=DG)
        else:
            r.point(t, v, nom, dx=-4, dy=-9, ancre="end", couleur=DG)
    f.texte(r.x0 + r.w / 2, 284, "Time (min)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Temperature (°C)", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=304)
    return f.render()


def _interp(pts, x):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return pts[-1][1]


# ----------------------------------------------------------------------------------------------- p29 : reflexion
def reflexion():
    f = Fig(440, 250, "Reflexion d'un rayon sur un miroir plan",
            f"Un rayon lumineux arrive sur un miroir plan horizontal avec un angle de {ANGLE_INCIDENCE} degres par rapport a la normale ; "
            "le rayon reflechi part de l'autre cote de la normale.")
    O = (220, 150)
    f.ligne(60, O[1], 380, O[1], stroke=FG, sw=3)
    for x in range(70, 380, 14):
        f.ligne(x, O[1], x - 8, O[1] + 12, stroke=MU, sw=1.2)
    f.ligne(O[0], 30, O[0], O[1], stroke=MU, sw=1.4, dash="5 4")
    f.texte(O[0] + 8, 40, "normal", taille=13, ancre="start", fill=MU)
    a = math.radians(ANGLE_INCIDENCE)
    L = 120
    pi = (O[0] - L * math.sin(a), O[1] - L * math.cos(a))
    pr = (O[0] + L * math.sin(a), O[1] - L * math.cos(a))
    f.fleche(pi[0], pi[1], O[0], O[1], stroke=INFO, sw=2.2, tete="plein")
    f.fleche(O[0], O[1], pr[0], pr[1], stroke=INFO, sw=2.2, tete="plein")
    p1, p2 = _pt(O, 52, -90 - ANGLE_INCIDENCE), _pt(O, 52, -90)
    f.chemin(f"M{p1[0]:.1f},{p1[1]:.1f} A52,52 0 0 1 {p2[0]:.1f},{p2[1]:.1f}", stroke=DG, sw=1.6, couche=3)
    m = _pt(O, 84, -90 - ANGLE_INCIDENCE / 2)
    f.texte(m[0] + 2, m[1] - 4, f"{ANGLE_INCIDENCE}°", taille=14, fill=DG, gras=True, ancre="end")
    f.texte(pi[0] - 8, pi[1] - 6, "incident ray", taille=13, ancre="end")
    f.texte(pr[0] + 8, pr[1] - 6, "reflected ray", taille=13, ancre="start")
    f.legende("{FIG}", y=242)
    return f.render()


# ----------------------------------------------------------------------------------------------- circuits (p36 et Paper 2)
def _resistance(f, cx, cy, etiquette, vertical=False, w=44, h=18):
    if vertical:
        f.rect(cx - h / 2, cy - w / 2, h, w, rx=2, fill=CARD, stroke=FG, sw=1.6, couche=2)
        f.texte(cx + h / 2 + 8, cy + 5, etiquette, taille=14, ancre="start", couche=3)
    else:
        f.rect(cx - w / 2, cy - h / 2, w, h, rx=2, fill=CARD, stroke=FG, sw=1.6, couche=2)
        f.texte(cx, cy - h / 2 - 7, etiquette, taille=14, couche=3)


def circuit_serie_parallele(U, R1, R2, R3, legende, titre, desc):
    """Pile U en serie avec un amperemetre et R1, puis R2 et R3 en parallele."""
    f = Fig(460, 250, titre, desc)
    xl, xr, yt, yb = 50, 330, 50, 190
    xa, xb = 250, 330  # branches R2 et R3
    for seg in ((xl, yt, xb, yt), (xl, yb, xb, yb), (xa, yt, xa, yb), (xb, yt, xb, yb)):
        f.ligne(*seg, stroke=FG, sw=1.6)
    f.ligne(xl, yt, xl, yb, stroke=FG, sw=1.6)
    # pile : deux plaques sur le fil de gauche
    ym = (yt + yb) / 2
    f.rect(xl - 20, ym - 14, 40, 28, rx=0, fill=CARD, stroke=CARD, sw=0, couche=2)
    f.ligne(xl - 16, ym - 7, xl + 16, ym - 7, stroke=FG, sw=2, couche=3)
    f.ligne(xl - 8, ym + 7, xl + 8, ym + 7, stroke=FG, sw=4, couche=3)
    f.texte(xl - 24, ym + 5, f"{U} V", taille=14, ancre="end", couche=3)
    _resistance(f, 135, yt, f"{R1} {OHM}")
    f.cercle(150, yb, 15, fill=CARD, stroke=FG, sw=1.8)
    f.texte(150, yb + 5, "A", taille=15, gras=True)
    _resistance(f, xa, ym, f"{R2} {OHM}", vertical=True)
    _resistance(f, xb, ym, f"{R3} {OHM}", vertical=True)
    f.legende(legende, y=242)
    return f.render()


def circuit_p1():
    c = CIRCUIT_P1
    return circuit_serie_parallele(
        c["U"], c["R1"], c["R2"], c["R3"], "{FIG}", "Circuit avec une pile, un amperemetre et trois resistances",
        f"Pile de {c['U']} volts en serie avec un amperemetre et une resistance de {c['R1']} ohms, puis deux resistances de {c['R2']} ohms et "
        f"{c['R3']} ohms montees en parallele.")


# ----------------------------------------------------------------------------------------------- p50 : quatre graphiques en options
def graphes_options():
    f = Fig(480, 280, "Quatre graphiques de la force en fonction de l'allongement",
            "Quatre petits graphiques A, B, C et D, force en ordonnee et allongement en abscisse. A : droite qui ne passe pas par l'origine. "
            "B : courbe. C : droite qui passe par l'origine. D : droite horizontale.")
    cases = {"a": (30, 24), "b": (260, 24), "c": (30, 156), "d": (260, 156)}
    formes = {"a": lambda x: 0.25 + 0.7 * x, "b": lambda x: x ** 2 * 0.95 + 0.04, "c": lambda x: 0.95 * x, "d": lambda x: 0.55}
    # le panneau « c » est celui de la proportionnalite directe : CLE_GRAPHES = "c"
    for lettre, (x0, y0) in cases.items():
        w, h = 190, 100
        f.ligne(x0, y0, x0, y0 + h, stroke=FG, sw=1.6)
        f.ligne(x0, y0 + h, x0 + w, y0 + h, stroke=FG, sw=1.6)
        pts = [(x0 + w * t / 20, y0 + h - h * max(0.0, min(1.0, formes[lettre](t / 20))) ) for t in range(0, 21)]
        f.polyligne(pts, stroke=PR, sw=2.4)
        f.texte(x0 + 6, y0 + 12, lettre.upper(), taille=16, gras=True, ancre="start")
        f.texte(x0 + w / 2, y0 + h + 18, "extension", taille=12, fill=MU)
        f.texte(x0 - 6, y0 + 10, "F", taille=12, ancre="end", fill=MU)
    f.legende("{FIG}", y=272)
    return f.render()


def toutes():
    return {"vt": vitesse_temps(), "regle": regle_equilibre(), "chauffe": courbe_chauffe(), "reflexion": reflexion(),
            "circuit": circuit_p1(), "graphes": graphes_options()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
