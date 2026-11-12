"""Chronologie de la vidéo : durées des scènes, mots minutés, sous-titres (.srt),
piste audio assemblée et normalisée à -16 LUFS.

Entrées : config.json, sources/voix/*.mots.json (voir tts.py)
Sorties : sources/timeline.json, sources/sous-titres.srt, sources/voix-off-mixee.wav, sources/voix-off.mp3
Usage : python outils/timeline.py
"""
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg

RACINE = Path(__file__).resolve().parent.parent
CFG = json.loads((RACINE / "config.json").read_text(encoding="utf-8"))
SRC = RACINE / "sources"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FPS = 30
ATTAQUE = 0.25          # silence avant la voix dans une scène
QUEUE = 0.60            # silence après la voix
QUEUE_FINALE = 2.9      # dernière scène : on laisse l'appel à l'action à l'écran
MAX_CHARS_LIGNE = 24    # sous-titres : 2 lignes de 24 caractères au plus
FIN_PHRASE = re.compile(r"[.…?!]$")


def jointure_mots(texte, mots_tts):
    """Associe chaque mot minuté par edge-tts au texte d'origine (avec sa ponctuation)."""
    bruts = texte.split()
    jetons = []
    for b in bruts:
        if re.fullmatch(r"[?!.…:;,]+", b) and jetons:
            jetons[-1] += " " + b if b in ("?", "!", ":", ";") else b
        else:
            jetons.append(b)
    if len(jetons) != len(mots_tts):
        raise SystemExit(f"Décalage mots/texte ({len(jetons)} vs {len(mots_tts)}) : {texte!r}")
    return jetons


def decouper_sous_titres(mots):
    """mots : [{texte, t0, t1}] -> blocs de sous-titres courts, coupés sur la ponctuation."""
    blocs, cur = [], []
    for m in mots:
        cur.append(m)
        long_ = len(" ".join(x["texte"] for x in cur))
        ponct = bool(FIN_PHRASE.search(m["texte"])) or m["texte"].endswith(",")
        if ponct or long_ >= MAX_CHARS_LIGNE * 2 - 8:
            blocs.append(cur)
            cur = []
    if cur:
        blocs.append(cur)
    out = []
    for i, b in enumerate(blocs):
        t0 = b[0]["t0"] - 0.05
        suivant = blocs[i + 1][0]["t0"] - 0.06 if i + 1 < len(blocs) else None
        t1 = b[-1]["t1"] + 0.45
        if suivant is not None:
            t1 = min(t1, suivant)
        out.append({"t0": max(t0, 0), "t1": t1, "texte": " ".join(x["texte"] for x in b)})
    return out


def fmt_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    debut = 0.0
    scenes, subs = [], []
    for i, sc in enumerate(CFG["scenes"]):
        d = json.loads((SRC / "voix" / f"{sc['id']}.mots.json").read_text(encoding="utf-8"))
        queue = QUEUE_FINALE if i == len(CFG["scenes"]) - 1 else QUEUE
        duree = ATTAQUE + d["duree"] + queue
        jetons = jointure_mots(sc["voix"], d["mots"])
        mots = [
            {"texte": j, "t0": debut + ATTAQUE + m["debut"], "t1": debut + ATTAQUE + m["debut"] + m["duree"]}
            for j, m in zip(jetons, d["mots"])
        ]
        subs += decouper_sous_titres(mots)
        scenes.append({"id": sc["id"], "debut": debut, "duree": duree, "voix_debut": debut + ATTAQUE, "mots": mots})
        debut += duree
    total = debut
    (SRC / "timeline.json").write_text(
        json.dumps({"fps": FPS, "total": total, "scenes": scenes, "subs": subs, "lien": CFG["lien_cta"]},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    # sous-titres SRT (2 lignes max, coupées au milieu)
    lignes = []
    for n, s in enumerate(subs, 1):
        txt = s["texte"]
        if len(txt) > MAX_CHARS_LIGNE:
            mots = txt.split(" ")
            meilleur, ecart = 1, 10 ** 9
            for k in range(1, len(mots)):
                e = abs(len(" ".join(mots[:k])) - len(" ".join(mots[k:])))
                if e < ecart:
                    meilleur, ecart = k, e
            txt = " ".join(mots[:meilleur]) + "\n" + " ".join(mots[meilleur:])
        lignes.append(f"{n}\n{fmt_srt(s['t0'])} --> {fmt_srt(s['t1'])}\n{txt}\n")
    (SRC / "sous-titres.srt").write_text("\n".join(lignes), encoding="utf-8")

    # piste audio : chaque scène posée à son instant, puis loudnorm en deux passes
    cmd = [FFMPEG, "-y", "-v", "error"]
    for sc in CFG["scenes"]:
        cmd += ["-i", str(SRC / "voix" / f"{sc['id']}.mp3")]
    filtres = []
    for i, s in enumerate(scenes):
        ms = int(round(s["voix_debut"] * 1000))
        filtres.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}:all=1[a{i}]")
    entrees = "".join(f"[a{i}]" for i in range(len(scenes)))
    filtres.append(f"{entrees}amix=inputs={len(scenes)}:normalize=0,apad=whole_dur={total:.3f},atrim=0:{total:.3f}[mix]")
    brut = SRC / "voix-off-brute.wav"
    subprocess.run(cmd + ["-filter_complex", ";".join(filtres), "-map", "[mix]", str(brut)], check=True)

    cible = "I=-16:TP=-1.5:LRA=11"
    mesure = subprocess.run(
        [FFMPEG, "-v", "info", "-i", str(brut), "-af", f"loudnorm={cible}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    bloc = mesure.stderr[mesure.stderr.rindex("{"):mesure.stderr.rindex("}") + 1]
    m = json.loads(bloc)
    af = (f"loudnorm={cible}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(brut), "-af", af, "-ar", "48000", str(SRC / "voix-off-mixee.wav")], check=True)
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(SRC / "voix-off-mixee.wav"), "-b:a", "192k", str(SRC / "voix-off.mp3")], check=True)
    brut.unlink()
    print(f"durée totale {total:.2f}s, {len(subs)} sous-titres, voix mesurée avant normalisation : {m['input_i']} LUFS")


main()
