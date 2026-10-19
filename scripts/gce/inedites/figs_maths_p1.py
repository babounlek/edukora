"""Figures SVG de l'epreuve inedite GCE O Level Mathematics Paper 1 n.1.

Chaque figure est calculee (coordonnees, angles) et non dessinee a l'oeil. Les valeurs de l'enonce
(118 degres, 8-15-17, 072 degres...) sont les memes constantes que celles du texte et du corrige.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "outils_figures"))
import figures_svg as fs  # noqa: E402
from figures_svg import Fig, Repere, FG, MU, BD, BG, CARD, PR, INFO, GD, DG  # noqa: E402


fs.DECIMAL = "."  # graduations a l'anglaise : point decimal (le GCE est anglophone)

MINUS = "−"
DEG = "°"


def _pt(c, r, angle_deg):
    """Point a la distance r de c dans la direction `angle_deg` mesuree dans le sens des aiguilles
    d'une montre depuis l'horizontale droite (repere ecran : y vers le bas)."""
    a = math.radians(angle_deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def _arc(f, c, r, a1, a2, stroke=DG, sw=1.6):
    """Arc de cercle de rayon r du cap a1 au cap a2 (degres ecran, sens horaire)."""
    p1, p2 = _pt(c, r, a1), _pt(c, r, a2)
    large = 1 if abs(a2 - a1) > 180 else 0
    f.chemin(f"M{p1[0]:.1f},{p1[1]:.1f} A{r},{r} 0 {large} 1 {p2[0]:.1f},{p2[1]:.1f}", stroke=stroke, sw=sw, couche=3)


# ----------------------------------------------------------------------------------------------- Q10
def venn():
    n_a_seul, n_commun, n_b_seul, n_dehors = 9, 6, 11, 14
    f = Fig(440, 250, "Diagramme de Venn de deux clubs A et B",
            f"Rectangle E contenant deux cercles A et B qui se chevauchent. Seulement dans A : {n_a_seul}. "
            f"Dans A et B : {n_commun}. Seulement dans B : {n_b_seul}. Dans aucun des deux : {n_dehors}.")
    f.rect(20, 14, 400, 190, rx=4, fill="none", stroke=FG, sw=1.6)
    f.texte(34, 36, "ξ", taille=16, ancre="start", italique=True)
    f.cercle(170, 112, 72, fill="none", stroke=PR, sw=2.2)
    f.cercle(270, 112, 72, fill="none", stroke=INFO, sw=2.2)
    f.texte(120, 52, "A", taille=16, fill=PR, gras=True)
    f.texte(320, 52, "B", taille=16, fill=INFO, gras=True)
    f.texte(125, 118, str(n_a_seul), taille=18)
    f.texte(220, 118, str(n_commun), taille=18)
    f.texte(315, 118, str(n_b_seul), taille=18)
    f.texte(392, 186, str(n_dehors), taille=18)
    f.legende("Figure 1", y=234)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q14
def mapping():
    f = Fig(440, 270, "Diagramme sagittal de x vers x au carre",
            "Ensemble de depart a gauche : moins 1, 0, 1, 2. Ensemble d'arrivee a droite : 0, 1, 2, 4, 5. "
            "Fleches : moins 1 vers 1, 0 vers 0, 1 vers 1, 2 vers 4. Les nombres 2 et 5 ne recoivent aucune fleche.")
    f.ellipse(120, 125, 56, 100, fill="none", stroke=PR, sw=2)
    f.ellipse(330, 125, 56, 112, fill="none", stroke=INFO, sw=2)
    f.texte(120, 22, "Domain", taille=14, fill=PR, gras=True)
    f.texte(330, 12, "Codomain", taille=14, fill=INFO, gras=True)
    gauche = {-1: 55, 0: 100, 1: 150, 2: 195}
    droite = {0: 45, 1: 85, 2: 125, 4: 165, 5: 205}
    for v, y in gauche.items():
        f.texte(108, y + 5, str(v).replace("-", MINUS), taille=15)
    for v, y in droite.items():
        f.texte(318, y + 5, str(v), taille=15)
    for x, img in ((-1, 1), (0, 0), (1, 1), (2, 4)):
        assert img == x * x
        f.fleche(130, gauche[x], 304, droite[img], stroke=FG, sw=1.5)
    f.legende("Figure 2", y=262)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q17
ANGLE_BPQ = 118


def paralleles():
    f = Fig(440, 250, "Deux droites paralleles coupees par une secante",
            f"Les droites AB et CD sont paralleles. La secante PQ coupe AB en P et CD en Q. "
            f"L'angle BPQ vaut {ANGLE_BPQ} degres. L'angle PQD est marque x.")
    yab, ycd = 70, 180
    P = (270, yab)
    t = (ycd - yab) / math.sin(math.radians(ANGLE_BPQ))
    Q = _pt(P, t, ANGLE_BPQ)
    assert abs(Q[1] - ycd) < 1e-6
    f.ligne(28, yab, 412, yab, stroke=FG, sw=1.8)
    f.ligne(28, ycd, 412, ycd, stroke=FG, sw=1.8)
    for yy in (yab, ycd):  # marques de parallelisme
        f.polyligne([(120, yy - 6), (127, yy), (120, yy + 6)], stroke=FG, sw=1.6)
    haut = _pt(P, -42, ANGLE_BPQ)
    bas = _pt(Q, 42, ANGLE_BPQ)
    f.ligne(haut[0], haut[1], bas[0], bas[1], stroke=FG, sw=1.8)
    f.texte(20, yab + 5, "A", taille=15, ancre="end")
    f.texte(420, yab + 5, "B", taille=15, ancre="start")
    f.texte(20, ycd + 5, "C", taille=15, ancre="end")
    f.texte(420, ycd + 5, "D", taille=15, ancre="start")
    f.texte(P[0] - 12, P[1] - 10, "P", taille=15, ancre="end")
    f.texte(Q[0] + 12, Q[1] + 20, "Q", taille=15, ancre="start")
    _arc(f, P, 32, 0, ANGLE_BPQ)
    m = _pt(P, 56, ANGLE_BPQ / 2)
    f.texte(m[0] + 4, m[1] + 4, f"{ANGLE_BPQ}{DEG}", taille=14, fill=DG, gras=True)
    ang_q = 180 - ANGLE_BPQ
    _arc(f, Q, 32, -ang_q, 0)
    m2 = _pt(Q, 50, -ang_q / 2)
    f.texte(m2[0] + 4, m2[1] + 4, "x", taille=15, fill=DG, italique=True, gras=True)
    f.legende("Figure 3", y=240)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q20
def forme_en_L():
    k = 20
    f = Fig(440, 240, "Forme plane en L",
            "Forme dont tous les angles sont droits. Hauteur totale 8 cm, largeur totale 12 cm. "
            "Le bord superieur gauche mesure 7 cm, puis la forme descend de 3 cm.")
    x0, y0 = 70, 30
    pts = [(x0, y0), (x0 + 7 * k, y0), (x0 + 7 * k, y0 + 3 * k), (x0 + 12 * k, y0 + 3 * k),
           (x0 + 12 * k, y0 + 8 * k), (x0, y0 + 8 * k)]
    f.polygone(pts, fill=fs.ACC, stroke=FG, sw=2)
    # marques d'angle droit aux coins
    def eq(cx, cy, dx, dy, s=9):
        f.polyligne([(cx + dx * s, cy), (cx + dx * s, cy + dy * s), (cx, cy + dy * s)], stroke=MU, sw=1.2, couche=3)
    eq(x0, y0, 1, 1)
    eq(x0 + 12 * k, y0 + 8 * k, -1, -1)
    eq(x0, y0 + 8 * k, 1, -1)
    f.texte(x0 + 3.5 * k, y0 - 8, "7 cm", taille=14)
    f.texte(x0 - 10, y0 + 4 * k + 5, "8 cm", taille=14, ancre="end")
    f.texte(x0 + 6 * k, y0 + 8 * k + 20, "12 cm", taille=14)
    f.texte(x0 + 7 * k + 8, y0 + 1.5 * k + 5, "3 cm", taille=14, ancre="start")
    f.legende("Figure 4", y=234)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q22
def cuboid():
    f = Fig(440, 250, "Parallelepipede rectangle",
            "Parallelepipede de longueur 9 cm, largeur 5 cm et hauteur 4 cm, dessine en perspective.")
    x, y, L, H = 60, 100, 9 * 20, 4 * 20
    dx, dy = 5 * 10, -5 * 7
    avant = [(x, y), (x + L, y), (x + L, y + H), (x, y + H)]
    haut = [(x, y), (x + dx, y + dy), (x + L + dx, y + dy), (x + L, y)]
    droite = [(x + L, y), (x + L + dx, y + dy), (x + L + dx, y + dy + H), (x + L, y + H)]
    f.polygone(haut, fill=fs.ACC, stroke=FG, sw=1.8)
    f.polygone(droite, fill=fs.ACC, stroke=FG, sw=1.8)
    f.polygone(avant, fill=CARD, stroke=FG, sw=1.8)
    f.ligne(x, y + H, x + dx, y + H + dy, stroke=MU, sw=1.3, dash="5 4")
    f.ligne(x + dx, y + dy, x + dx, y + dy + H, stroke=MU, sw=1.3, dash="5 4")
    f.ligne(x + dx, y + dy + H, x + L + dx, y + dy + H, stroke=MU, sw=1.3, dash="5 4")
    f.texte(x + L / 2, y + H + 22, "9 cm", taille=14)
    f.texte(x - 8, y + H / 2 + 5, "4 cm", taille=14, ancre="end")
    f.texte(x + L + dx + 8, y + dy + H / 2 + 5, "5 cm", taille=14, ancre="start")
    f.legende("Figure 5", y=240)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q24
ANGLE_C = 34


def cercle_theoreme():
    f = Fig(440, 260, "Cercle de centre O avec un angle inscrit",
            f"Cercle de centre O. Les points A, B et C sont sur le cercle. L'angle ACB vaut {ANGLE_C} degres. "
            "Les segments OA, OB, CA, CB et AB sont traces.")
    O = (220, 125)
    r = 95
    A = _pt(O, r, 90 + ANGLE_C)    # arc AB en bas, angle au centre 2 x 38
    B = _pt(O, r, 90 - ANGLE_C)
    C = _pt(O, r, 270)
    f.cercle(O[0], O[1], r, fill="none", stroke=FG, sw=1.8)
    f.ligne(O[0], O[1], A[0], A[1], stroke=FG, sw=1.6)
    f.ligne(O[0], O[1], B[0], B[1], stroke=FG, sw=1.6)
    f.ligne(C[0], C[1], A[0], A[1], stroke=FG, sw=1.6)
    f.ligne(C[0], C[1], B[0], B[1], stroke=FG, sw=1.6)
    f.ligne(A[0], A[1], B[0], B[1], stroke=FG, sw=1.6)
    f.cercle(O[0], O[1], 3, fill=FG, stroke=FG)
    f.texte(O[0] + 12, O[1] - 6, "O", taille=15)
    f.texte(A[0] - 14, A[1] + 14, "A", taille=15)
    f.texte(B[0] + 14, B[1] + 14, "B", taille=15)
    f.texte(C[0], C[1] - 10, "C", taille=15)
    cA = math.degrees(math.atan2(A[1] - C[1], A[0] - C[0]))
    cB = math.degrees(math.atan2(B[1] - C[1], B[0] - C[0]))
    _arc(f, C, 30, min(cA, cB), max(cA, cB))
    f.texte(C[0], C[1] + 52, f"{ANGLE_C}{DEG}", taille=14, fill=DG, gras=True)
    f.legende("Figure 6", y=252)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q27
def parabole():
    f = Fig(440, 310, "Courbe de y egal x au carre moins 2x moins 3",
            "Parabole ouverte vers le haut qui coupe l'axe des abscisses en moins 1 et en 3 et l'axe des "
            "ordonnees en moins 3. Graduations de moins 3 a 5 sur x et de moins 5 a 6 sur y.")
    r = Repere(f, 44, 14, 370, 252, -3, 5, -5, 6, xetiq="x", yetiq="y")
    r.courbe(lambda x: x * x - 2 * x - 3, a=-2.2, b=4.2, nom="y = x² − 2x − 3", nom_pos=(r.px(2.7), r.y0 + 16))
    f.legende("Figure 7", y=300)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q36
def droite_numerique():
    f = Fig(440, 120, "Droite numerique avec une inegalite",
            "Droite graduee de moins 5 a 6. Point plein en moins 2, cercle vide en 3, segment epais entre les deux.")
    x0, x1, y = 30, 410, 52
    vmin, vmax = -5, 6
    px = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    f.fleche(x0 - 10, y, x1 + 12, y, stroke=FG, sw=1.6, tete="plein")
    for v in range(vmin, vmax + 1):
        f.ligne(px(v), y - 5, px(v), y + 5, stroke=FG, sw=1.4)
        f.texte(px(v), y + 24, str(v).replace("-", MINUS), taille=13, fill=MU)
    f.ligne(px(-2), y, px(3), y, stroke=PR, sw=5, couche=2)
    f.cercle(px(-2), y, 6, fill=FG, stroke=FG, sw=1.6)
    f.cercle(px(3), y, 6, fill=BG, stroke=FG, sw=2)
    f.legende("Figure 8", y=108)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q38
EDGES = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("D", "E")]
COORD = {"A": (50, 125), "B": (150, 50), "C": (150, 200), "D": (270, 50), "E": (270, 200)}


def reseau():
    f = Fig(340, 270, "Reseau de cinq sommets et sept aretes",
            "Sommets A, B, C, D, E. Aretes : AB, AC, BC, BD, BE, CE, DE. Aucune arete n'en coupe une autre.")
    for a, b in EDGES:
        f.ligne(*COORD[a], *COORD[b], stroke=FG, sw=1.8, couche=1)
    for nom, (cx, cy) in COORD.items():
        f.cercle(cx, cy, 15, fill=CARD, stroke=FG, sw=1.8)
        f.texte(cx, cy + 5, nom, taille=15, gras=True)
    f.legende("Figure 9", y=258)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q39
def triangle_rectangle():
    f = Fig(440, 250, "Triangle PQR rectangle en Q",
            "Triangle rectangle en Q. PQ mesure 8 cm, QR mesure 15 cm et PR mesure 17 cm. "
            "L'angle theta est en R, entre RQ et RP.")
    k = 14
    Q = (80, 200)
    R = (Q[0] + 15 * k, Q[1])
    P = (Q[0], Q[1] - 8 * k)
    f.polygone([P, Q, R], fill=fs.ACC, stroke=FG, sw=2)
    f.polyligne([(Q[0] + 12, Q[1]), (Q[0] + 12, Q[1] - 12), (Q[0], Q[1] - 12)], stroke=FG, sw=1.4, couche=3)
    f.texte(P[0] - 10, P[1] - 4, "P", taille=15, ancre="end")
    f.texte(Q[0] - 10, Q[1] + 16, "Q", taille=15, ancre="end")
    f.texte(R[0] + 12, R[1] + 5, "R", taille=15, ancre="start")
    f.texte(Q[0] - 10, (P[1] + Q[1]) / 2 + 5, "8 cm", taille=14, ancre="end")
    f.texte((Q[0] + R[0]) / 2, Q[1] + 22, "15 cm", taille=14)
    f.texte((P[0] + R[0]) / 2 + 14, (P[1] + R[1]) / 2 - 10, "17 cm", taille=14, ancre="start")
    a = math.degrees(math.atan2(P[1] - R[1], P[0] - R[0]))  # direction R vers P
    # arc en R : de la direction RP (angle a, en degres ecran) a la direction RQ (180)
    p1, p2 = _pt(R, 40, 180), _pt(R, 40, a + 360 if a < 0 else a)
    f.chemin(f"M{p1[0]:.1f},{p1[1]:.1f} A40,40 0 0 1 {p2[0]:.1f},{p2[1]:.1f}", stroke=DG, sw=1.6, couche=3)
    f.texte(R[0] - 62, R[1] - 12, "θ", taille=16, fill=DG, italique=True, gras=True)
    f.legende("Figure 10", y=244)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q41
BEARING = 72


def bearing():
    f = Fig(440, 260, "Route d'un bateau de P vers Q",
            f"Le bateau part de P et navigue vers Q selon le cap {BEARING} degres mesure depuis le nord dans le sens "
            "des aiguilles d'une montre. Une ligne nord est tracee en P et en Q.")
    P = (110, 190)
    Q = _pt(P, 200, BEARING - 90)  # cap mesure depuis le nord : cap - 90 en angle ecran
    f.fleche(P[0], P[1], P[0], 40, stroke=MU, sw=1.5, dash="5 4", tete="plein")
    f.fleche(Q[0], Q[1], Q[0], 40 if Q[1] > 80 else 10, stroke=MU, sw=1.5, dash="5 4", tete="plein")
    f.texte(P[0] - 8, 48, "N", taille=14, ancre="end", fill=MU)
    f.texte(Q[0] - 8, 48, "N", taille=14, ancre="end", fill=MU)
    f.fleche(P[0], P[1], Q[0] - 4, Q[1] + 1, stroke=FG, sw=2.2, tete="plein")
    f.cercle(P[0], P[1], 3.5, fill=FG, stroke=FG)
    f.cercle(Q[0], Q[1], 3.5, fill=FG, stroke=FG)
    f.texte(P[0] - 10, P[1] + 20, "P", taille=15, ancre="end")
    f.texte(Q[0] + 10, Q[1] + 20, "Q", taille=15, ancre="start")
    _arc(f, P, 50, -90, BEARING - 90)
    m = _pt(P, 72, (BEARING - 180) / 2)
    f.texte(m[0] + 2, m[1], f"{BEARING:03d}{DEG}", taille=14, fill=DG, gras=True)
    f.legende("Figure 11", y=252)
    return f.render()


# ----------------------------------------------------------------------------------------------- Q48
FRATRIE = {0: 4, 1: 10, 2: 8, 3: 9, 4: 4}


def diagramme_barres():
    total = sum(FRATRIE.values())
    assert total == 35
    f = Fig(440, 300, "Diagramme en barres du nombre de freres et soeurs",
            "Nombre de freres et soeurs de 35 eleves. Effectifs : 0 frere ou soeur, 4 eleves ; 1, 10 eleves ; "
            "2, 8 eleves ; 3, 9 eleves ; 4, 4 eleves.")
    x0, y0, w, h, ymax = 62, 20, 350, 210, 12
    py = lambda v: y0 + h - v / ymax * h
    for v in range(0, ymax + 1, 2):
        f.ligne(x0, py(v), x0 + w, py(v), BD, 1, couche=0)
        f.texte(x0 - 8, py(v) + 5, str(v), taille=13, ancre="end", fill=MU)
    f.fleche(x0, py(0), x0 + w + 8, py(0), stroke=FG, sw=1.6)
    f.fleche(x0, py(0), x0, y0 - 8, stroke=FG, sw=1.6)
    k = len(FRATRIE)
    for i, (cat, val) in enumerate(FRATRIE.items()):
        cx = x0 + (i + 0.5) * w / k
        bw = w / k * 0.55
        f.rect(cx - bw / 2, py(val), bw, py(0) - py(val), 0, fill=PR, stroke=FG, sw=1.2)
        f.texte(cx, py(0) + 20, str(cat), taille=14)
    f.texte(x0 + w / 2, 274, "Number of brothers and sisters", taille=14)
    f.texte(x0 + 6, y0 - 4, "Frequency", taille=13, ancre="start", fill=MU)
    f.legende("Figure 12", y=292)
    return f.render()


def toutes():
    return {
        "venn": venn(), "mapping": mapping(), "paralleles": paralleles(), "forme_L": forme_en_L(),
        "cuboid": cuboid(), "cercle": cercle_theoreme(), "parabole": parabole(), "droite": droite_numerique(),
        "reseau": reseau(), "triangle": triangle_rectangle(), "bearing": bearing(), "barres": diagramme_barres(),
    }


if __name__ == "__main__":
    for nom, svg in toutes().items():
        print(nom, len(svg))
