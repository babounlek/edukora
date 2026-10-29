"""
Gabarit de redessin d'une figure floue (à copier, puis remplir la section « DESSIN » avec les mesures relevées).

Dans le conteneur backend :
    cat mon_dessin.py | docker compose exec -T backend sh -c "cat > /tmp/mon_dessin.py"
    docker compose exec -T backend sh -c "python /tmp/mon_dessin.py"      -> /tmp/fig_nouvelle.png et .webp

Tout se trace en COORDONNÉES D'ORIGINE (celles des graduations de agrandir.py) ; le suréchantillonnage S est interne.
Largeur et hauteur de la figure : celles de l'original, sans exception.
"""
import math

from PIL import Image, ImageDraw, ImageFont

S = 4                       # suréchantillonnage : on dessine x4 puis on réduit (lissage des bords)
W, H = 1200, 407            # TAILLE DE L'ORIGINAL (à remplacer)
NOIR, BLANC = (17, 17, 17), (255, 255, 255)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

img = Image.new("RGB", (W * S, H * S), BLANC)
d = ImageDraw.Draw(img)


def police(chemin, taille):
    return ImageFont.truetype(chemin, int(taille * S))


def ligne(x0, y0, x1, y1, ep=2):
    d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=NOIR, width=int(ep * S))


def texte(x, y, s, f, ancre="lm"):
    """ancre : lm = à gauche, centré en hauteur ; mm = centré ; voir la doc de Pillow."""
    d.text((x * S, y * S), s, font=f, fill=NOIR, anchor=ancre)


def bague(cx, cy, rx, ry, ep=2.6, k=1.0):
    """Anneau (ellipse noire, intérieur blanc) : centromère, point de repère, etc."""
    d.ellipse([(cx - rx * k) * S, (cy - ry * k) * S, (cx + rx * k) * S, (cy + ry * k) * S], fill=NOIR)
    rx2, ry2 = rx * k - ep, ry * k - ep
    d.ellipse([(cx - rx2) * S, (cy - ry2) * S, (cx + rx2) * S, (cy + ry2) * S], fill=BLANC)


def interp(profil, y):
    """Demi-largeur à la distance y du haut, d'après un profil [(distance, demi-largeur), ...] (cosinus, lissé)."""
    for (y0, h0), (y1, h1) in zip(profil, profil[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0) if y1 > y0 else 0
            t = (1 - math.cos(math.pi * t)) / 2
            return h0 + (h1 - h0) * t
    return profil[-1][1]


def forme(cx, top, profil, k=1.0, marge=0.0, graine=0.0, bosses=0.03, dec=0.0):
    """
    Polygone d'une forme verticale définie par un PROFIL MESURÉ. marge > 0 : intérieur du contour (épaisseur du trait),
    pour faire une forme « contour » : noir d'abord (marge=0), puis blanc (marge=épaisseur). bosses : irrégularité
    (0,03 = discrète, c'est ce qu'on voit sur un scan) ; dec : décalage de l'axe.
    """
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


# ---------------------------------------------------------------- DESSIN (à remplir avec les mesures)
# Exemple : une forme « contour » (marge = épaisseur du trait) à profil mesuré.
# PROFIL = [(0, 16), (3, 20), (8, 22), (20, 22.5), (35, 22), (45, 19), (52, 14), (58, 8), (63, 4), (70, 1.5)]
# for marge in (0, 3.4):
#     d.polygon(forme(353, 205, PROFIL, marge=marge), fill=BLANC if marge else NOIR)
# texte(60, 50, "Individu", police(SERIF, 22))

out = img.resize((W, H), Image.LANCZOS)
out.save("/tmp/fig_nouvelle.png")
out.save("/tmp/fig_nouvelle.webp", "WEBP", quality=92)
print("ok", out.size)
