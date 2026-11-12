"""Voix off : une piste mp3 par scène + minutage mot à mot (edge-tts).

Sortie : sources/voix/<id>.mp3 et sources/voix/<id>.mots.json
Usage : python outils/tts.py
"""
import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

RACINE = Path(__file__).resolve().parent.parent
CFG = json.loads((RACINE / "config.json").read_text(encoding="utf-8"))
SORTIE = RACINE / "sources" / "voix"
SORTIE.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def duree_mp3(chemin: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(chemin), "-f", "null", "-"], capture_output=True, text=True)
    for ligne in r.stderr.splitlines():
        if "time=" in ligne:
            dernier = ligne
    h, m, s = dernier.split("time=")[1].split()[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


async def une_scene(sc):
    com = edge_tts.Communicate(sc["voix"], CFG["voix"], rate=CFG["vitesse"], boundary="WordBoundary")
    mots = []
    chemin = SORTIE / f"{sc['id']}.mp3"
    with open(chemin, "wb") as f:
        async for ev in com.stream():
            if ev["type"] == "audio":
                f.write(ev["data"])
            elif ev["type"] == "WordBoundary":
                mots.append({
                    "mot": ev["text"],
                    "debut": ev["offset"] / 1e7,
                    "duree": ev["duration"] / 1e7,
                })
    d = duree_mp3(chemin)
    (SORTIE / f"{sc['id']}.mots.json").write_text(
        json.dumps({"duree": d, "mots": mots}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(sc["id"], f"{d:.2f}s", len(mots), "mots")


async def main():
    for sc in CFG["scenes"]:
        await une_scene(sc)


asyncio.run(main())
