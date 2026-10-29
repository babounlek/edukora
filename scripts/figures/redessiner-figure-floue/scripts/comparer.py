"""
Original (à gauche) et nouveau dessin (à droite), même zone, côte à côte et agrandis, pour juger les écarts de FORME.

Dans le conteneur backend (après avoir produit /tmp/fig_nouvelle.png) :
    FIG=figures_avant_filigrane/2189_x.webp  ZONE=290,190,480,390  python /tmp/comparer.py
Écrit /tmp/comparaison.png. ECHELLE (défaut 3).
"""
import os

from PIL import Image

echelle = int(os.environ.get("ECHELLE", "3"))
orig = Image.open(f"/app/media/{os.environ['FIG']}").convert("RGB")
neuf = Image.open("/tmp/fig_nouvelle.png").convert("RGB")
x0, y0, x1, y1 = (int(v) for v in os.environ["ZONE"].split(",")) if os.environ.get("ZONE") else (0, 0, *orig.size)
a, b = orig.crop((x0, y0, x1, y1)), neuf.crop((x0, y0, x1, y1))
largeur, hauteur = x1 - x0, y1 - y0
c = Image.new("RGB", (largeur * 2 + 10, hauteur), (255, 0, 0))
c.paste(a, (0, 0))
c.paste(b, (largeur + 10, 0))
c.resize((c.width * echelle, c.height * echelle), Image.LANCZOS).save("/tmp/comparaison.png")
print("ok", c.size)
