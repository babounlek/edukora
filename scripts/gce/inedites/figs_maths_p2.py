"""Figures SVG de l'epreuve inedite GCE O Level Mathematics Paper 2 n.1.

Une figure d'ENONCE (reseau de la question 6) et quatre figures de CORRIGE (droite numerique, Venn, construction,
parabole) : un trace attendu n'est jamais dans l'enonce. Toutes les coordonnees sont calculees.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_maths_p1 import _pt, DEG, MINUS, fs  # noqa: E402  (fs.DECIMAL = "." deja applique)
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402


# ----------------------------------------------------------------------------------------------- A6 (enonce)
SOMMETS = {"W": (60, 120), "X": (170, 45), "Y": (290, 120), "Z": (170, 195)}
ARETES = [("W", "X"), ("W", "X"), ("X", "Y"), ("Y", "Z"), ("Z", "W"), ("X", "Z")]


def reseau_wxyz():
    f = Fig(350, 250, "Reseau de quatre sommets et six aretes",
            "Sommets W, X, Y et Z. Deux aretes relient W a X. Les autres aretes sont XY, YZ, ZW et XZ. "
            "Aucune arete n'en coupe une autre.")
    (xw, yw), (xx, yx) = SOMMETS["W"], SOMMETS["X"]
    # les deux aretes W-X : deux arcs symetriques de part et d'autre du segment
    mx, my = (xw + xx) / 2, (yw + yx) / 2
    nx, ny = -(yx - yw), (xx - xw)
    n = math.hypot(nx, ny)
    nx, ny = nx / n * 36, ny / n * 36
    for s in (1, -1):
        f.chemin(f"M{xw},{yw} Q{mx + s * nx:.1f},{my + s * ny:.1f} {xx},{yx}", stroke=FG, sw=1.8)
    for a, b in ARETES[2:]:
        f.ligne(*SOMMETS[a], *SOMMETS[b], stroke=FG, sw=1.8, couche=1)
    for nom, (cx, cy) in SOMMETS.items():
        f.cercle(cx, cy, 15, fill=CARD, stroke=FG, sw=1.8)
        f.texte(cx, cy + 5, nom, taille=15, gras=True)
    f.legende("Figure 1", y=240)
    return f.render()


# ----------------------------------------------------------------------------------------------- A9 (corrige)
def droite_x_inferieur_moins5():
    f = Fig(440, 110, "Solution x inferieur ou egal a moins 5 sur une droite numerique",
            "Droite graduee de moins 9 a 1. Point plein en moins 5. Trait epais de moins 5 vers la gauche, avec une fleche.")
    x0, x1, y = 30, 410, 50
    vmin, vmax = -9, 1
    px = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    f.fleche(x0 - 10, y, x1 + 12, y, stroke=FG, sw=1.6, tete="plein")
    for v in range(vmin, vmax + 1):
        f.ligne(px(v), y - 5, px(v), y + 5, stroke=FG, sw=1.4)
        f.texte(px(v), y + 24, str(v).replace("-", MINUS), taille=13, fill=MU)
    f.fleche(px(-5), y, x0 - 8, y, stroke=PR, sw=5, tete="plein", taille_tete=14, couche=2)
    f.cercle(px(-5), y, 6, fill=FG, stroke=FG, sw=1.6)
    f.legende("Solution: x " + "≤" + " " + MINUS + "5", y=100)
    return f.render()


# ----------------------------------------------------------------------------------------------- B2 (ii) (corrige)
def venn_clubs():
    m_seul, commun, d_seul, dehors = 19, 8, 13, 12
    assert m_seul + commun == 27 and d_seul + commun == 21 and m_seul + commun + d_seul + dehors == 52
    f = Fig(440, 250, "Diagramme de Venn des clubs de musique et de theatre",
            f"Rectangle de 52 eleves. Seulement musique M : {m_seul}. Musique et theatre : {commun}. "
            f"Seulement theatre D : {d_seul}. Aucun des deux clubs : {dehors}.")
    f.rect(20, 14, 400, 190, rx=4, fill="none", stroke=FG, sw=1.6)
    f.texte(34, 36, "ξ", taille=16, ancre="start", italique=True)
    f.cercle(170, 112, 72, fill="none", stroke=PR, sw=2.2)
    f.cercle(270, 112, 72, fill="none", stroke=INFO, sw=2.2)
    f.texte(120, 52, "M", taille=16, fill=PR, gras=True)
    f.texte(320, 52, "D", taille=16, fill=INFO, gras=True)
    for x, v in ((125, m_seul), (220, commun), (315, d_seul)):
        f.texte(x, 118, str(v), taille=18)
    f.texte(392, 186, str(dehors), taille=18)
    f.legende("Solution: Venn diagram (52 learners)", y=234)
    return f.render()


# ----------------------------------------------------------------------------------------------- B3 (iii) (corrige)
AB, BC, AC = 6, 5, 4


def construction_triangle():
    k = 30
    x = (BC ** 2 - AC ** 2 + AB ** 2) / (2 * AB)
    y = math.sqrt(BC ** 2 - x ** 2)
    B = (50.0, 210.0)
    A = (B[0] + AB * k, B[1])
    C = (B[0] + x * k, B[1] - y * k)
    t = AB / (AB + BC)  # AD / AC = AB / (AB + BC)
    D = (A[0] + t * (C[0] - A[0]), A[1] + t * (C[1] - A[1]))
    bd = math.hypot((D[0] - B[0]) / k, (D[1] - B[1]) / k)
    assert abs(bd ** 2 - AB * BC * (1 - (AC / (AB + BC)) ** 2)) < 1e-9
    f = Fig(440, 260, "Triangle ABC et bissectrice de l'angle B",
            f"Triangle ABC avec AB egal 6 cm, BC egal 5 cm et AC egal 4 cm. La bissectrice de l'angle ABC coupe AC en D ; "
            f"BD mesure environ {bd:.1f} cm. Les arcs de construction sont traces en pointille.")
    f.polygone([B, A, C], fill="none", stroke=FG, sw=2)
    f.ligne(B[0], B[1], D[0], D[1], stroke=PR, sw=2.2, couche=2)
    ang_a = 0.0
    ang_c = math.degrees(math.atan2(C[1] - B[1], C[0] - B[0]))
    r = 52
    P, Q = _pt(B, r, ang_a), _pt(B, r, ang_c)
    f.chemin(f"M{P[0]:.1f},{P[1]:.1f} A{r},{r} 0 0 0 {Q[0]:.1f},{Q[1]:.1f}", stroke=MU, sw=1.2, dash="4 3", couche=3)
    bis = (ang_a + ang_c) / 2
    T = _pt(B, 80, bis)
    s = math.hypot(T[0] - P[0], T[1] - P[1])
    for centre in (P, Q):
        a0 = math.degrees(math.atan2(T[1] - centre[1], T[0] - centre[0]))
        p1, p2 = _pt(centre, s, a0 - 14), _pt(centre, s, a0 + 14)
        f.chemin(f"M{p1[0]:.1f},{p1[1]:.1f} A{s:.1f},{s:.1f} 0 0 1 {p2[0]:.1f},{p2[1]:.1f}", stroke=MU, sw=1.2, dash="4 3", couche=3)
    for pt, nom, dx, dy in ((B, "B", -12, 18), (A, "A", 12, 18), (C, "C", 0, -10), (D, "D", -4, -12)):
        f.cercle(pt[0], pt[1], 3, fill=FG, stroke=FG)
        f.texte(pt[0] + dx, pt[1] + dy, nom, taille=15, ancre="middle")
    f.texte((B[0] + A[0]) / 2, B[1] + 26, "6 cm", taille=14)
    f.texte((B[0] + C[0]) / 2 - 22, (B[1] + C[1]) / 2 - 4, "5 cm", taille=14)
    f.texte((A[0] + C[0]) / 2 + 12, (A[1] + C[1]) / 2 + 2, "4 cm", taille=14, ancre="start")
    f.texte((B[0] + D[0]) / 2 + 6, (B[1] + D[1]) / 2 + 22, "BD ≈ " + f"{bd:.1f} cm", taille=14, fill=PR, gras=True, ancre="start")
    f.legende("Solution: triangle ABC with the bisector of angle B", y=252)
    return f.render(), bd


# ----------------------------------------------------------------------------------------------- B4 (corrige)
def parabole_solution():
    f = Fig(460, 330, "Courbe de y egal x au carre plus x moins 6",
            "Parabole de sommet (moins 0,5 ; moins 6,25) qui coupe l'axe des abscisses en moins 3 et en 2 et l'axe des "
            "ordonnees en moins 6. Droite y egal moins 4 en pointille : elle coupe la courbe en x egal moins 2 et x egal 1. "
            "Axe de symetrie x egal moins 0,5 en pointille.")
    r = Repere(f, 46, 14, 390, 276, -4, 3.5, -7, 7, ypas=2, xetiq="x", yetiq="y")
    f_ = lambda x: x * x + x - 6
    r.segment(-0.5, -7, -0.5, 7, couleur=MU, dash="5 4", epaisseur=1.3)
    r.segment(-4, -4, 3.5, -4, couleur=DG, dash="5 4", epaisseur=1.5)
    r.courbe(f_, a=-4, b=3.2, nom="y = x² + x − 6", nom_pos=(r.px(3.3), r.py(-6.2)))
    for xv in range(-4, 4):
        r.point(xv, f_(xv), couleur=PR)
    r.point(-2, -4, couleur=DG)
    r.point(1, -4, couleur=DG)
    f.texte(r.px(-0.5) - 6, r.py(5.6), "x = −0.5", taille=13, ancre="end", fill=MU, halo=True)
    f.texte(r.px(1) + 6, r.py(-4) - 8, "y = −4", taille=13, ancre="start", fill=DG, halo=True)
    f.legende("Solution: graph of y = x² + x − 6", y=322)
    return f.render()


def toutes():
    constr, bd = construction_triangle()
    return {"reseau": reseau_wxyz(), "droite": droite_x_inferieur_moins5(), "venn": venn_clubs(),
            "construction": constr, "parabole": parabole_solution(), "_bd": bd}


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, svg if nom == "_bd" else len(svg))
