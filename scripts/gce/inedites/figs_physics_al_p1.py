"""Figures SVG de l'epreuve inedite GCE A Level Physics Paper 1 n.1 (huit figures simples, calculees).

Les constantes ci-dessous sont les memes que celles ecrites dans les enonces (questions_physics_al_p1.py) ; le verificateur les relit.
Chaque cle de l'enonce se retrouve par calcul sur les donnees ecrites en texte, la figure ne fait que les montrer.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_p1 as fp1  # noqa: E402  (helpers de circuit ; fixe aussi le point decimal)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402

OHM = "Ω"
MOINS = "−"
# ----------------------------------------------------------------------------------------------- donnees
VT = [(0, 0), (5, 12), (20, 12), (30, 0)]  # (s, m/s)
FORCE_EXT = {"F": 12.0, "x_cm": 4.0}
CIRCUIT = {"U": 24, "R1": 5, "R2": 12, "R3": 4}
DIVISEUR = {"U": 12, "R1": 4.0, "R2": 2.0, "RV": 2.0}  # kilo-ohms
NIVEAUX = [-8.0, -3.0, -1.2]  # eV
ACTIVITE = {"A0": 800, "T": 12.0, "t1": 36, "A1": 100}
CORDE = {"L": 1.20, "boucles": 3}
CHAMP = {"v": 2.0e7, "B_mT": 1.0}


def _interp(pts, x):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return pts[-1][1]


# ----------------------------------------------------------------------------------------------- vitesse-temps
def vitesse_temps():
    f = Fig(460, 300, "Velocity-time graph of a train",
            "Velocity rises uniformly from 0 to 12 metres per second in 5 seconds, stays at 12 metres per second until 20 seconds, "
            "then falls uniformly to 0 at 30 seconds.")
    r = Repere(f, 56, 14, 380, 214, 0, 30, 0, 14, xpas=5, ypas=2, xetiq="", yetiq="")
    r.courbe(lambda x: _interp(VT, x), a=0, b=30, n=120)
    f.texte(r.x0 + r.w / 2, 262, "Time / s", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Velocity / m/s", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=290)
    return f.render()


# ----------------------------------------------------------------------------------------------- force-extension
def force_extension():
    F, x = FORCE_EXT["F"], FORCE_EXT["x_cm"]
    f = Fig(440, 290, "Force-extension graph of a spring",
            f"A straight line through the origin reaching a force of {F:g} newtons at an extension of {x:g} centimetres.")
    r = Repere(f, 56, 14, 360, 200, 0, 6, 0, 16, xpas=1, ypas=4, xetiq="", yetiq="")
    r.courbe(lambda t: F / x * t, a=0, b=x, n=40)
    r.segment(x, 0, x, F, couleur=MU, dash="5 4", epaisseur=1.2)
    r.segment(0, F, x, F, couleur=MU, dash="5 4", epaisseur=1.2)
    r.point(x, F, f"{F:g} N, {x:g} cm", dx=10, dy=-6)
    f.texte(r.x0 + r.w / 2, 252, "Extension / cm", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Force / N", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=280)
    return f.render()


# ----------------------------------------------------------------------------------------------- circuit serie-parallele
def circuit_serie_parallele():
    c = CIRCUIT
    return fp1.circuit_serie_parallele(
        c["U"], c["R1"], c["R2"], c["R3"], "{FIG}", "Circuit with a battery, an ammeter and three resistors",
        f"A {c['U']} volt battery in series with an ammeter and a {c['R1']} ohm resistor, then a {c['R2']} ohm and a {c['R3']} ohm resistor in parallel.")


# ----------------------------------------------------------------------------------------------- diviseur avec voltmetre
def diviseur_voltmetre():
    d = DIVISEUR
    f = Fig(480, 250, "Potential divider with a voltmeter",
            f"A {d['U']} volt battery in series with a {d['R1']:.1f} kilo-ohm resistor and a {d['R2']:.1f} kilo-ohm resistor. "
            f"A voltmeter of resistance {d['RV']:.1f} kilo-ohms is connected across the {d['R2']:.1f} kilo-ohm resistor.")
    xl, x2, xv, yt, yb = 50, 270, 370, 50, 190
    for seg in ((xl, yt, xv, yt), (xl, yb, xv, yb), (xl, yt, xl, yb), (x2, yt, x2, yb), (xv, yt, xv, yb)):
        f.ligne(*seg, stroke=FG, sw=1.6)
    ym = (yt + yb) / 2
    f.rect(xl - 20, ym - 14, 40, 28, rx=0, fill=CARD, stroke=CARD, sw=0, couche=2)
    f.ligne(xl - 16, ym - 7, xl + 16, ym - 7, stroke=FG, sw=2, couche=3)
    f.ligne(xl - 8, ym + 7, xl + 8, ym + 7, stroke=FG, sw=4, couche=3)
    f.texte(xl - 24, ym + 5, f"{d['U']} V", taille=14, ancre="end", couche=3)
    fp1._resistance(f, 150, yt, f"{d['R1']:.1f} k{OHM}")
    fp1._resistance(f, x2, ym, f"{d['R2']:.1f} k{OHM}", vertical=True)
    f.cercle(xv, ym, 16, fill=CARD, stroke=FG, sw=1.8, couche=2)
    f.texte(xv, ym + 5, "V", taille=15, gras=True)
    f.legende("{FIG}", y=242)
    return f.render()


# ----------------------------------------------------------------------------------------------- niveaux d'energie
def niveaux_energie():
    f = Fig(440, 290, "Energy levels of an atom",
            "Three energy levels at minus 8.0, minus 3.0 and minus 1.2 electronvolts, drawn as horizontal lines.")
    ytop, ybot = 34, 250
    ypos = lambda e: ytop + (-e) * (ybot - ytop) / 8.0 * (8.0 / 8.0)
    f.texte(70, 22, "Energy / eV", taille=13, ancre="start", fill=MU)
    for e in NIVEAUX:
        y = ypos(e)
        f.ligne(140, y, 340, y, stroke=FG, sw=2.4)
        f.texte(132, y + 5, f"{MOINS}{abs(e):.1f}", taille=14, ancre="end")
    f.ligne(140, ytop - 6, 340, ytop - 6, stroke=MU, sw=1, dash="4 4")
    f.texte(348, ytop - 2, "0", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=282)
    return f.render()


# ----------------------------------------------------------------------------------------------- courbe d'activite
def activite():
    a = ACTIVITE
    f = Fig(460, 300, "Activity of a radioactive sample",
            f"Activity falls exponentially from {a['A0']} becquerel at time zero to {a['A1']} becquerel at {a['t1']} hours.")
    r = Repere(f, 60, 14, 380, 214, 0, 48, 0, 900, xpas=12, ypas=100, xetiq="", yetiq="")
    r.courbe(lambda t: a["A0"] * 0.5 ** (t / a["T"]), a=0, b=48, n=160)
    r.point(0, a["A0"], f"{a['A0']} Bq", dx=10, dy=4)
    r.point(a["t1"], a["A1"], f"{a['A1']} Bq at {a['t1']} h", dx=0, dy=19, ancre="middle")
    f.texte(r.x0 + r.w / 2, 262, "Time / h", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Activity / Bq", taille=13, ancre="start", fill=MU)
    f.legende("{FIG}", y=290)
    return f.render()


# ----------------------------------------------------------------------------------------------- onde stationnaire sur une corde
def corde():
    n = CORDE["boucles"]
    f = Fig(480, 230, "Stationary wave with three loops on a string",
            f"A string of length {CORDE['L']:.2f} metres fixed at both ends vibrates with {n} loops and four nodes, two of them at the ends.")
    x0, x1, yc, amp = 50, 430, 100, 52
    pts_h = [(x0 + (x1 - x0) * i / 240, yc - amp * math.sin(n * math.pi * i / 240)) for i in range(241)]
    pts_b = [(x, 2 * yc - y) for x, y in pts_h]
    f.polyligne(pts_h, stroke=PR, sw=2.4)
    f.polyligne(pts_b, stroke=PR, sw=2.4)
    for k in range(n + 1):
        f.cercle(x0 + (x1 - x0) * k / n, yc, 4.5, fill=DG, stroke=DG, sw=1)
    f.rect(x0 - 12, yc - 32, 12, 64, rx=1, fill=BD, stroke=FG, sw=1.2)
    f.rect(x1, yc - 32, 12, 64, rx=1, fill=BD, stroke=FG, sw=1.2)
    f.fleche(x0, 182, x1, 182, stroke=FG, sw=1.4, tete="plein")
    f.fleche(x1, 182, x0, 182, stroke=FG, sw=1.4, tete="plein")
    f.texte((x0 + x1) / 2, 176, f"{CORDE['L']:.2f} m", taille=14, halo=True)
    f.legende("{FIG}", y=222)
    return f.render()


# ----------------------------------------------------------------------------------------------- electron dans un champ magnetique
def champ_magnetique():
    f = Fig(440, 270, "Electron moving in a magnetic field",
            "A magnetic field directed into the page, shown by crosses. An electron enters the field moving to the right and follows a circular path.")
    for i in range(7):
        for j in range(4):
            x, y = 60 + i * 52, 40 + j * 52
            f.ligne(x - 4, y - 4, x + 4, y + 4, stroke=MU, sw=1.2)
            f.ligne(x - 4, y + 4, x + 4, y - 4, stroke=MU, sw=1.2)
    r = 62
    f.chemin(f"M 220 88 A {r} {r} 0 1 1 219.99 88", stroke=PR, sw=2.4)
    f.cercle(220, 88, 5, fill=DG, stroke=DG, sw=1)
    f.fleche(220, 88, 290, 88, stroke=DG, sw=2, tete="plein")
    f.texte(300, 93, "v", taille=15, ancre="start", fill=DG, gras=True)
    f.texte(204, 78, "e" + MOINS, taille=14, ancre="end", fill=DG, halo=True)
    f.texte(396, 24, "B into page", taille=13, ancre="end", fill=MU)
    f.legende("{FIG}", y=262)
    return f.render()


def toutes():
    return {"vt": vitesse_temps(), "force": force_extension(), "circuit": circuit_serie_parallele(), "diviseur": diviseur_voltmetre(),
            "niveaux": niveaux_energie(), "activite": activite(), "corde": corde(), "champ": champ_magnetique()}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
