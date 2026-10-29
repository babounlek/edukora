"""
Redessin de la figure 2189 (Probatoire A SVT 2024, exercice 2, caryotypes X/Y), d'après l'image floue : formes mesurées
sur l'original agrandi (repères gradués). Pas de PDF d'origine pour les épreuves francophones.

    python dessiner_chromosomes.py   -> /tmp/fig_nouvelle.png et .webp (1200 x 407)
"""
import math

from PIL import Image, ImageDraw, ImageFont

S = 4
W, H = 1200, 407
NOIR, BLANC = (17, 17, 17), (255, 255, 255)
img = Image.new("RGB", (W * S, H * S), BLANC)
d = ImageDraw.Draw(img)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def police(chemin, taille):
    return ImageFont.truetype(chemin, int(taille * S))


def ligne(x0, y0, x1, y1, ep=2):
    d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=NOIR, width=int(ep * S))


def texte(x, y, s, f, ancre="lm"):
    d.text((x * S, y * S), s, font=f, fill=NOIR, anchor=ancre)


def interp(profil, y):
    """Demi-largeur à la hauteur y (cosinus entre les repères, lissé)."""
    for (y0, h0), (y1, h1) in zip(profil, profil[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0) if y1 > y0 else 0
            t = (1 - math.cos(math.pi * t)) / 2
            return h0 + (h1 - h0) * t
    return profil[-1][1]


def bras(cx, top, profil, k, marge, graine, bosses, dec):
    """Polygone d'un bras. profil = [(distance depuis le haut, demi-largeur)] ; marge > 0 : intérieur du contour."""
    longueur = profil[-1][0]
    ya = marge if marge else 0
    yb = longueur - marge if marge else longueur
    n = 90
    g, dr = [], []
    for i in range(n + 1):
        y = ya + (yb - ya) * i / n
        hw = interp(profil, y)
        gauche = hw * (1 + bosses * math.sin(0.21 * y + graine)) - marge
        droite = hw * (1 - bosses * math.cos(0.17 * y + 2 * graine)) - marge
        x_axe = cx + dec * k
        g.append(((x_axe - max(0.5, gauche) * k) * S, (top + y * k) * S))
        dr.append(((x_axe + max(0.5, droite) * k) * S, (top + y * k) * S))
    return g + dr[::-1]


def bague(cx, cy, rx, ry, ep=2.6, k=1.0):
    d.ellipse([(cx - rx * k) * S, (cy - ry * k) * S, (cx + rx * k) * S, (cy + ry * k) * S], fill=NOIR)
    rx2, ry2 = rx * k - ep, ry * k - ep
    d.ellipse([(cx - rx2) * S, (cy - ry2) * S, (cx + rx2) * S, (cy + ry2) * S], fill=BLANC)


# Profils mesurés sur l'original (demi-largeurs en px d'origine, depuis le haut du bras).
X_HAUT = [(0, 16), (3, 20), (8, 22), (20, 22.5), (35, 22), (45, 19), (52, 14), (58, 8), (63, 4), (70, 1.5)]
X_BAS = [(0, 1.5), (7, 9), (14, 16), (22, 20), (32, 22), (47, 22.5), (62, 22.5), (72, 21), (79, 17), (84, 12), (87, 8)]
Y_HAUT = [(0, 8), (4, 15), (10, 20), (20, 21.5), (30, 21), (38, 15), (44, 8), (48, 4), (50, 2)]
Y_BAS = [(0, 3), (6, 11), (14, 19), (24, 20.5), (45, 20.5), (56, 17), (63, 12), (68, 10)]


def chromosome_x(cx, top, k=1.0, graine=0.0):
    """X : contour. Bras court (haut) de 65 px, anneau central, bras long (bas) de 85 px."""
    for marge in (0, 3.4):
        d.polygon(bras(cx, top, X_HAUT, k, marge, graine, 0.03, 1.0), fill=BLANC if marge else NOIR)
        d.polygon(bras(cx, top + 84 * k, X_BAS, k, marge, graine + 1.3, 0.03, -1.0), fill=BLANC if marge else NOIR)
    bague(cx, top + 77 * k, 10, 9, 2.8, k)


def chromosome_y(cx, top, k=1.0, graine=0.0):
    """Y : plein. Masse arrondie (haut), petit anneau ouvert, corps allongé à pans coupés (bas)."""
    d.polygon(bras(cx + 1, top, Y_HAUT, k, 0, graine, 0.045, 0.5), fill=NOIR)
    d.polygon(bras(cx, top + 65 * k, Y_BAS, k, 0, graine + 1.1, 0.035, -1.0), fill=NOIR)
    bague(cx, top + 56 * k, 9, 8.5, 2.2, k)


G, D_, T, B = 35, 890, 25, 390
for x in (G, D_):
    ligne(x, T, x, B)
for y in (T, 75, 128, 185, B):
    ligne(G, y, D_, y)
for x in (283, 478, 686):
    ligne(x, T, x, B)

f_lib = police(SERIF, 22)
f_val = police(SANS, 30)
f_n = police(SERIF, 24)
texte(60, 50, "Individu", f_lib)
texte(60, 102, "Sexe", f_lib)
texte(60, 157, "Autosomes", f_lib)
texte(60, 272, "Chromosomes", f_lib)
texte(60, 302, "sexuels", f_lib)
for cx, n, sexe in ((380, "n°1", "masculin"), (582, "n°2", "féminin"), (788, "n°3", "féminin")):
    texte(cx, 50, n, f_n, "mm")
    texte(cx, 102, sexe, f_val, "mm")
    texte(cx, 157, "22 paires", f_n, "mm")

chromosome_x(353, 205, 1.0, 0.3)      # n°1 : X
chromosome_y(423, 224, 1.0, 1.1)      # n°1 : Y
chromosome_x(574, 207, 1.0, 2.0)      # n°2 : X X
chromosome_x(639, 207, 1.0, 0.8)
chromosome_x(798, 207, 1.0, 1.5)      # n°3 : X seul

chromosome_x(938, 39, 0.976, 0.5)     # légende
chromosome_y(932, 236, 1.0, 1.3)
f_leg = police(SERIF, 25)
texte(982, 87, "Gonosome X", f_leg)
texte(982, 310, "Gonosome Y", f_leg)

out = img.resize((W, H), Image.LANCZOS)
out.save("/tmp/fig_nouvelle.png")
out.save("/tmp/fig_nouvelle.webp", "WEBP", quality=92)
print("ok", out.size)
