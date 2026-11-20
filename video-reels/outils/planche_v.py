"""Planche-contact de captures verticales : python planche_v.py sortie.png f1.png f2.png ... (6 par ligne, 300x533)"""
import sys
from PIL import Image
sortie, fs = sys.argv[1], sys.argv[2:]
tw, th, cols = 300, 533, 6
lignes = (len(fs) + cols - 1) // cols
sh = Image.new("RGB", (cols * tw, lignes * th), "white")
for k, f in enumerate(fs):
    sh.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
sh.save(sortie)
