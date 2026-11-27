"""
Filme les vidéos TikTok d'une semaine : chaque vidéo de <semaine>/sources/videos.html est rendue image par image
(Chromium, 30 images par seconde), puis encodée en MP4 (H.264, 1080 × 1920) dans <semaine>/videos/.

    python filmer.py <dossier de la semaine> [j1-pythagore ...]

Sans nom de vidéo, toutes les vidéos de la semaine. La piste son est muette : le son se choisit dans TikTok au moment de
publier (sa bibliothèque est autorisée sur TikTok, une musique ajoutée ici ne le serait pas forcément).
Il faut Playwright et imageio-ffmpeg (le venv de video-facebook les a) : ..\\..\\video-facebook\\.venv\\Scripts\\python.exe
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

if len(sys.argv) < 2 or not (Path(sys.argv[1]) / "sources" / "videos.html").exists():
    sys.exit("Usage : python filmer.py <dossier de la semaine> [noms de vidéos] (lancer d'abord node construire.mjs)")
SEMAINE = Path(sys.argv[1]).resolve()
CHOIX = set(sys.argv[2:])
PAGE = SEMAINE / "sources" / "videos.html"
SORTIE = SEMAINE / "videos"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
IPS = 30

SORTIE.mkdir(exist_ok=True)
with sync_playwright() as p:
    navigateur = p.chromium.launch()
    onglet = navigateur.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    onglet.goto(PAGE.as_uri())
    onglet.evaluate("window.pret")
    videos = onglet.evaluate("window.DATA.videos.map(v => v.nom)")
    faites, signalees = set(), []
    for i, nom in enumerate(videos):
        if CHOIX and nom not in CHOIX:
            # Vidéo non refaite cette fois : elle et sa couverture restent.
            faites.update({f"{nom}.mp4", f"{nom}.jpg"})
            continue
        debut = time.time()
        infos = onglet.evaluate(f"choisir({i})")
        total = infos["total"]
        for s in infos["tailles"]:
            if s["deborde"] or s["taille"] < 34:
                signalees.append((nom, s))
        cible = SORTIE / f"{nom}.mp4"
        cmd = [
            FFMPEG, "-y", "-v", "error",
            "-f", "image2pipe", "-framerate", str(IPS), "-vcodec", "mjpeg", "-i", "-",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(IPS),
            "-profile:v", "high", "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "96k", "-shortest", "-t", f"{total:.3f}", str(cible),
        ]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(round(total * IPS))
        derniere_cle, image, photos = None, None, 0
        for k in range(n):
            cle = onglet.evaluate(f"render({k / IPS:.4f})")
            # Une image identique à la précédente (texte immobile) n'est pas rephotographiée.
            if cle != derniere_cle:
                image = onglet.screenshot(type="jpeg", quality=93)
                derniere_cle, photos = cle, photos + 1
            ff.stdin.write(image)
        ff.stdin.close()
        if ff.wait() != 0:
            sys.exit(f"ffmpeg a échoué pour {nom}")
        faites.add(cible.name)
        print(f"{nom}.mp4 : {total:.1f} s, {photos} photos pour {n} images, {time.time() - debut:.0f} s de rendu", flush=True)

        # Une image de la scène « À toi » sert d'aperçu (couverture possible dans TikTok).
        apercu = SORTIE / f"{nom}.jpg"
        onglet.evaluate(f"render({infos['total'] * 0.45:.3f})")
        apercu.write_bytes(onglet.screenshot(type="jpeg", quality=85))
        faites.add(apercu.name)
        # Une planche de 10 images prises dans la vidéo, pour la regarder d'un coup d'œil (sources/, pas à publier).
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(cible), "-vf",
                        f"fps=10/{total:.2f},scale=360:-1,tile=5x2:padding=6:color=gray", "-frames:v", "1",
                        str(SEMAINE / "sources" / f"planche-{nom}.png")], check=True)
    navigateur.close()

obsoletes = [f for f in SORTIE.iterdir() if f.suffix in (".mp4", ".jpg") and f.name not in faites]
for f in obsoletes:
    f.unlink()
print(len(obsoletes), "fichiers obsolètes supprimés ; à surveiller :", signalees or "aucune",
      "\n  (à surveiller = une scène dont le texte descend sous 34 px ou déborde : la regarder dans la vidéo)")
