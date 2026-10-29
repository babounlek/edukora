"""
Agrandit une zone d'une figure avec des graduations rouges en coordonnées d'origine (pour MESURER, pas pour regarder).

Dans le conteneur backend :
    FIG=figures_avant_filigrane/2189_x.webp  ZONE=290,190,480,390  ECHELLE=4  python /tmp/agrandir.py
FIG est relatif au dossier media (/app/media) ; sans ZONE, toute l'image. Écrit /tmp/agrandi.png (à copier vers l'hôte
avec `docker compose cp backend:/tmp/agrandi.png ...` puis à lire avec Read). PAS = graduation tous les N px d'origine.
"""
import os

from PIL import Image, ImageDraw

fig = os.environ["FIG"]
echelle = int(os.environ.get("ECHELLE", "4"))
pas = int(os.environ.get("PAS", "20"))
im = Image.open(f"/app/media/{fig}").convert("RGB")
x0, y0, x1, y1 = (int(v) for v in os.environ["ZONE"].split(",")) if os.environ.get("ZONE") else (0, 0, *im.size)

crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * echelle, (y1 - y0) * echelle), Image.LANCZOS)
d = ImageDraw.Draw(crop)
ROUGE = (255, 0, 0)
for y in range(0, y1 - y0, pas):
    d.line([(0, y * echelle), (12, y * echelle)], fill=ROUGE)
    d.text((14, y * echelle - 5), str(y0 + y), fill=ROUGE)
for x in range(0, x1 - x0, pas):
    d.line([(x * echelle, 0), (x * echelle, 12)], fill=ROUGE)
    d.text((x * echelle - 8, 14), str(x0 + x), fill=ROUGE)
crop.save("/tmp/agrandi.png")
print("ok", im.size, (x0, y0, x1, y1), "echelle", echelle)
