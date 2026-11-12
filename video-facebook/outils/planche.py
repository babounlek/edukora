"""Assemble des aperçus en planche-contact : python outils/planche.py sortie.png fichier1.png fichier2.png ..."""
import sys
from PIL import Image
sortie, fichiers = sys.argv[1], sys.argv[2:]
cols = 3 if len(fichiers) > 4 else 2
t = 540
lignes = (len(fichiers) + cols - 1) // cols
planche = Image.new("RGB", (cols * t, lignes * t), "white")
for i, f in enumerate(fichiers):
    planche.paste(Image.open(f).convert("RGB").resize((t, t), Image.LANCZOS), ((i % cols) * t, (i // cols) * t))
planche.save(sortie)
