"""Rendu de la vidéo : l'animation HTML (outils/rendu/index.html) est photographiée image par image
avec Chromium (Playwright), puis encodée avec ffmpeg (H.264 + AAC, 1080x1080, 30 i/s).

Usage :
  python outils/rendu.py                      # vidéo complète -> edukora-facebook-1x1.mp4
  python outils/rendu.py --images 1.0 5.5 12  # seulement ces instants -> sources/apercus/t_<s>.png
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
SRC = RACINE / "sources"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MAX_LIGNE = 24


def deux_lignes(txt):
    if len(txt) <= MAX_LIGNE:
        return txt
    mots = txt.split(" ")
    meilleur, ecart = 1, 10 ** 9
    for k in range(1, len(mots)):
        e = abs(len(" ".join(mots[:k])) - len(" ".join(mots[k:])))
        if e < ecart:
            meilleur, ecart = k, e
    return " ".join(mots[:meilleur]) + "\n" + " ".join(mots[meilleur:])


def beats3(g):
    """Trois temps de la scène 3, cadrés sur les blocs repérés dans la capture (exercice.json)."""
    def boite(cle, h=None, y0=None):
        b = g[cle]
        return {"x": b["x"], "y": b["y"] if y0 is None else y0, "w": b["w"], "h": b["h"] if h is None else h}

    verif, concl = g["q2_verification"], g["q2_conclusion"]
    b3 = {"x": verif["x"], "y": verif["y"] - 96, "w": verif["w"], "h": concl["y"] + concl["h"] - verif["y"] + 96}
    en = g["q1_enonce"]
    r = {"x": en["x"], "y": en["y"], "w": en["w"], "h": g["q1_rappel"]["y"] + 190 - en["y"]}
    d = boite("q1_developpement", h=160)
    return [
        {"cadre": r, "mise": r, "legende": "La méthode est rappelée"},
        {"cadre": d, "mise": d, "legende": "Chaque calcul est posé"},
        {"cadre": b3, "mise": boite("q2_verification"), "legende": "Le résultat est vérifié"},
    ]


def construire_data():
    tl = json.loads((SRC / "timeline.json").read_text(encoding="utf-8"))
    cap = SRC / "captures"
    scenes = {s["id"]: s for s in tl["scenes"]}
    s3 = scenes["s3"]
    exo = json.loads((cap / "exercice.json").read_text(encoding="utf-8"))

    def t_mot(sc, motif):
        for m in sc["mots"]:
            if re.match(motif, m["texte"]):
                return m["t0"]
        raise SystemExit(f"mot introuvable : {motif}")

    marks3 = [s3["debut"], t_mot(s3, r"^Chaque") - 0.12, t_mot(s3, r"^Et$") - 0.12]
    data = {
        "fps": tl["fps"], "total": tl["total"], "scenes": tl["scenes"], "lien": tl["lien"],
        "subs": [{**s, "affiche": deux_lignes(s["texte"])} for s in tl["subs"]],
        "exercice": exo,
        "fichiers": {
            "pageHaut": (cap / "page-haut.png").as_uri(),
            "exercice": (cap / "exercice.png").as_uri(),
            "bandeau": (cap / "bandeau-examens.png").as_uri(),
            "logo": (SRC / "logo-vertical-fr.svg").as_uri(),
            "icone": (SRC / "icon-dark.svg").as_uri(),
        },
        "beats3": beats3(exo),
        "marks3": marks3,
        "defil2": 1000,
    }
    return data


def ouvrir(p, data):
    nav = p.chromium.launch()
    page = nav.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
    page.add_init_script("window.DATA = " + json.dumps(data, ensure_ascii=False))
    page.goto((RACINE / "outils" / "rendu" / "index.html").as_uri())
    page.evaluate("window.pret")
    page.wait_for_timeout(400)
    return nav, page


def apercus(temps):
    data = construire_data()
    sortie = SRC / "apercus"
    sortie.mkdir(exist_ok=True)
    with sync_playwright() as p:
        nav, page = ouvrir(p, data)
        for t in temps:
            page.evaluate(f"render({t})")
            page.screenshot(path=sortie / f"t_{t:06.2f}.png")
        nav.close()
    print("aperçus dans", sortie)


def complet():
    data = construire_data()
    n = int(round(data["total"] * data["fps"]))
    sortie = RACINE / "edukora-facebook-1x1.mp4"
    cmd = [
        FFMPEG, "-y", "-v", "error",
        "-f", "image2pipe", "-framerate", str(data["fps"]), "-vcodec", "png", "-i", "-",
        "-i", str(SRC / "voix-off-mixee.wav"),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(data["fps"]),
        "-profile:v", "high", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1",
        "-t", f"{data['total']:.3f}", str(sortie),
    ]
    with sync_playwright() as p:
        nav, page = ouvrir(p, data)
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            page.evaluate(f"render({i / data['fps']:.5f})")
            ff.stdin.write(page.screenshot(type="png"))
            if i % 150 == 0:
                print(f"image {i}/{n}", flush=True)
        ff.stdin.close()
        ff.wait()
        nav.close()
    print("écrit :", sortie)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--images":
        apercus([float(x) for x in sys.argv[2:]])
    else:
        complet()
