"""Portrait du fondateur pour l'accueil : recadrage 4:5, arrière-plan adouci, lumière légèrement relevée.

Rien n'est changé au visage : ni peau lissée, ni traits retouchés. Le sujet reste net, seul le décor du bureau
(écran, dossiers, affiche) est flouté et un peu éclairci pour ne plus se lire.
"""
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

source, sortie = sys.argv[1], sys.argv[2]
image = Image.open(source).convert("RGB")

# Masque du sujet, en coordonnées de la photo d'origine (960 x 1280) : la tête, puis les épaules.
masque = Image.new("L", image.size, 0)
dessin = ImageDraw.Draw(masque)
dessin.ellipse((480 - 236, 742 - 338, 480 + 236, 742 + 338), fill=255)
dessin.polygon(
    [(0, 1088), (120, 1030), (215, 982), (300, 925), (680, 925), (770, 972), (860, 1000), (960, 1028), (960, 1280), (0, 1280)],
    fill=255,
)
masque = masque.filter(ImageFilter.GaussianBlur(14))

fond = image.filter(ImageFilter.GaussianBlur(11))
fond = ImageEnhance.Color(fond).enhance(0.8)
fond = ImageEnhance.Brightness(fond).enhance(1.06)
portrait = Image.composite(image, fond, masque)

# Cadre 4:5 : de l air au-dessus de la tête, les épaules et le col de chemise en bas.
portrait = portrait.crop((60, 230, 900, 1280))

portrait = ImageEnhance.Brightness(portrait).enhance(1.07)
portrait = ImageEnhance.Contrast(portrait).enhance(1.04)
portrait = ImageEnhance.Color(portrait).enhance(1.03)
portrait = portrait.resize((480, 600), Image.LANCZOS)
portrait = portrait.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=3))
portrait.save(sortie, "WEBP", quality=84, method=6)
print(portrait.size)
