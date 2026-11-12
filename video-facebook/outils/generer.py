"""Régénère toute la vidéo : voix -> chronologie/audio -> (captures) -> rendu.

Usage (depuis le dossier video-facebook, avec .venv\\Scripts\\python.exe) :
  python outils/generer.py              # voix + chronologie + rendu (captures existantes)
  python outils/generer.py --captures   # refait aussi les captures sur le site
"""
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OUTILS = RACINE / "outils"

etapes = []
if "--captures" in sys.argv:
    etapes.append("capture.py")
etapes += ["tts.py", "timeline.py", "rendu.py"]

for e in etapes:
    print(f"\n=== {e} ===", flush=True)
    subprocess.run([sys.executable, str(OUTILS / e)], check=True, cwd=RACINE)
print("\nTerminé : edukora-facebook-1x1.mp4")
