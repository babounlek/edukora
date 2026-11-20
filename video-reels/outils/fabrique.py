"""Fabrique d'une vidéo verticale 1080x1920 à partir d'un fichier de spécification (specs/X.json).

  python outils/fabrique.py specs/A.json                  # voix, chronologie, audio, rendu, MP4
  python outils/fabrique.py specs/A.json --images 1 5 9   # seulement ces instants (aperçus PNG)
  python outils/fabrique.py specs/A.json --refaire-voix   # régénère la voix même si elle existe

Étapes : voix off (edge-tts, un mp3 par scène + minutage mot à mot) -> chronologie et sous-titres (.srt)
-> piste audio normalisée à -16 LUFS -> animation HTML photographiée image par image (Chromium)
-> encodage H.264 + AAC (ffmpeg).
"""
import argparse
import asyncio
import json
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
FACEBOOK = RACINE.parent / "video-facebook"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30
ATTAQUE, QUEUE, QUEUE_FINALE = 0.25, 0.45, 2.5
MAX_LIGNE = 24
FIN_PHRASE = re.compile(r"[.…?!]$")


# ---------------------------------------------------------------- voix
def duree_mp3(chemin):
    r = subprocess.run([FFMPEG, "-i", str(chemin), "-f", "null", "-"], capture_output=True, text=True)
    dernier = [l for l in r.stderr.splitlines() if "time=" in l][-1]
    h, m, s = dernier.split("time=")[1].split()[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


async def tts_scene(texte, voix, vitesse, mp3):
    com = edge_tts.Communicate(texte, voix, rate=vitesse, boundary="WordBoundary")
    mots = []
    with open(mp3, "wb") as f:
        async for ev in com.stream():
            if ev["type"] == "audio":
                f.write(ev["data"])
            elif ev["type"] == "WordBoundary":
                mots.append({"mot": ev["text"], "debut": ev["offset"] / 1e7, "duree": ev["duration"] / 1e7})
    return {"duree": duree_mp3(mp3), "mots": mots}


def faire_voix(spec, dossier, refaire):
    (dossier / "voix").mkdir(parents=True, exist_ok=True)
    for i, sc in enumerate(spec["scenes"]):
        mp3, js = dossier / "voix" / f"s{i + 1}.mp3", dossier / "voix" / f"s{i + 1}.mots.json"
        if js.exists() and mp3.exists() and not refaire:
            j = json.loads(js.read_text(encoding="utf-8"))
            if j.get("texte") == sc["voix"] and j.get("voix") == spec["voix"] and j.get("vitesse") == spec["vitesse"]:
                continue
        d = asyncio.run(tts_scene(sc["voix"], spec["voix"], spec["vitesse"], mp3))
        d.update(texte=sc["voix"], voix=spec["voix"], vitesse=spec["vitesse"])
        js.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"voix s{i + 1}: {d['duree']:.2f}s, {len(d['mots'])} mots")


# ---------------------------------------------------------------- chronologie
def _norm(x):
    return re.sub(r"[^0-9a-zà-ÿœ]", "", x.casefold())


def jetons(texte, mots_tts):
    """Aligne les mots minutés par edge-tts sur les mots du texte (avec leur ponctuation).
    edge-tts fusionne parfois un nombre et le mot suivant (« 26 épreuves ») ou coupe un mot en deux
    (« edukora.africa ») : on regroupe, et chaque groupe devient un « mot » de sous-titre minuté."""
    tok = []
    for b in texte.split():
        if re.fullmatch(r"[?!.…:;,]+", b) and tok:
            tok[-1] += (" " + b) if b in ("?", "!", ":", ";") else b
        else:
            tok.append(b)
    groupes, i, j = [], 0, 0
    while i < len(tok) and j < len(mots_tts):
        tn, sn = _norm(tok[i]), _norm(mots_tts[j]["mot"])
        if tn == sn:
            ii, jj = i + 1, j + 1
        elif tn.startswith(sn):                      # un jeton = plusieurs mots TTS
            acc, jj = sn, j + 1
            while acc != tn and jj < len(mots_tts) and tn.startswith(acc + _norm(mots_tts[jj]["mot"])):
                acc += _norm(mots_tts[jj]["mot"]); jj += 1
            ii = i + 1
            if acc != tn:
                raise SystemExit(f"Alignement impossible près de {tok[i]!r} dans {texte!r}")
        elif sn.startswith(tn):                      # un mot TTS = plusieurs jetons
            acc, ii = tn, i + 1
            while acc != sn and ii < len(tok) and sn.startswith(acc + _norm(tok[ii])):
                acc += _norm(tok[ii]); ii += 1
            jj = j + 1
            if acc != sn:
                raise SystemExit(f"Alignement impossible près de {tok[i]!r} dans {texte!r}")
        else:
            raise SystemExit(f"Alignement impossible : {tok[i]!r} / {mots_tts[j]['mot']!r} dans {texte!r}")
        premier, dernier = mots_tts[j], mots_tts[jj - 1]
        groupes.append({"texte": " ".join(tok[i:ii]), "debut": premier["debut"],
                        "duree": dernier["debut"] + dernier["duree"] - premier["debut"]})
        i, j = ii, jj
    if i != len(tok) or j != len(mots_tts):
        raise SystemExit(f"Alignement incomplet ({i}/{len(tok)} jetons, {j}/{len(mots_tts)} mots TTS) : {texte!r}")
    return groupes


def _fin(m):
    return bool(FIN_PHRASE.search(m["texte"])) or m["texte"].endswith(",")


def sous_titres(mots):
    """Blocs courts coupés sur la ponctuation ; on évite de laisser un ou deux mots orphelins en fin de phrase."""
    blocs, cur = [], []
    for k, m in enumerate(mots):
        cur.append(m)
        long_ = len(" ".join(x["texte"] for x in cur))
        trop_long = long_ >= MAX_LIGNE * 2 - 8
        if trop_long and not _fin(m):
            reste = []
            for x in mots[k + 1:]:
                reste.append(x)
                if _fin(x):
                    break
            if len(reste) <= 2 and long_ + sum(len(x["texte"]) + 1 for x in reste) <= 52:
                continue
        if _fin(m) or trop_long:
            blocs.append(cur)
            cur = []
    if cur:
        blocs.append(cur)
    out = []
    for i, b in enumerate(blocs):
        t0 = b[0]["t0"] - 0.05
        t1 = b[-1]["t1"] + 0.45
        if i + 1 < len(blocs):
            t1 = min(t1, blocs[i + 1][0]["t0"] - 0.06)
        out.append({"t0": max(t0, 0), "t1": t1, "texte": " ".join(x["texte"] for x in b)})
    return out


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


def fmt_srt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def remplacer(txt, remp):
    for a, b in (remp or {}).items():
        txt = txt.replace(a, b)
    return txt


def chronologie(spec, dossier):
    debut, scenes, subs = 0.0, [], []
    remp = spec.get("remplacements")
    n = len(spec["scenes"])
    for i, sc in enumerate(spec["scenes"]):
        d = json.loads((dossier / "voix" / f"s{i + 1}.mots.json").read_text(encoding="utf-8"))
        duree = ATTAQUE + d["duree"] + (QUEUE_FINALE if i == n - 1 else QUEUE)
        mots = [{"texte": remplacer(g["texte"], remp), "t0": debut + ATTAQUE + g["debut"], "t1": debut + ATTAQUE + g["debut"] + g["duree"]}
                for g in jetons(sc["voix"], d["mots"])]
        subs += sous_titres(mots)
        scenes.append({"debut": debut, "duree": duree, "voix_debut": debut + ATTAQUE, "mots": mots})
        debut += duree
    for s in subs:
        s["affiche"] = deux_lignes(s["texte"])
    tl = {"total": debut, "scenes": scenes, "subs": subs}
    (dossier / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (dossier / "sous-titres.srt").write_text(
        "\n".join(f"{k}\n{fmt_srt(s['t0'])} --> {fmt_srt(s['t1'])}\n{s['affiche']}\n" for k, s in enumerate(subs, 1)),
        encoding="utf-8")
    return tl


def audio(spec, dossier, tl):
    cmd = [FFMPEG, "-y", "-v", "error"]
    for i in range(len(tl["scenes"])):
        cmd += ["-i", str(dossier / "voix" / f"s{i + 1}.mp3")]
    f = []
    for i, s in enumerate(tl["scenes"]):
        f.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(round(s['voix_debut'] * 1000))}:all=1[a{i}]")
    ent = "".join(f"[a{i}]" for i in range(len(tl["scenes"])))
    f.append(f"{ent}amix=inputs={len(tl['scenes'])}:normalize=0,apad=whole_dur={tl['total']:.3f},atrim=0:{tl['total']:.3f}[mix]")
    brut = dossier / "voix-brute.wav"
    subprocess.run(cmd + ["-filter_complex", ";".join(f), "-map", "[mix]", str(brut)], check=True)
    cible = "I=-16:TP=-1.5:LRA=11"
    mes = subprocess.run([FFMPEG, "-v", "info", "-i", str(brut), "-af", f"loudnorm={cible}:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(mes[mes.rindex("{"):mes.rindex("}") + 1])
    af = (f"loudnorm={cible}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(brut), "-af", af, "-ar", "48000", str(dossier / "voix-off.wav")], check=True)
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(dossier / "voix-off.wav"), "-b:a", "192k", str(dossier / "voix-off.mp3")], check=True)
    brut.unlink()


# ---------------------------------------------------------------- données du rendu
def boite(boites, ref):
    """'@cle' ou '@cle1+cle2' (union) -> {x,y,w,h} ; un dict est renvoyé tel quel."""
    if ref is None or isinstance(ref, dict):
        return ref
    bs = [boites[k] for k in ref.lstrip("@").split("+")]
    x0, y0 = min(b["x"] for b in bs), min(b["y"] for b in bs)
    x1, y1 = max(b["x"] + b["w"] for b in bs), max(b["y"] + b["h"] for b in bs)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def donnees(spec, tl):
    cap = RACINE / "sources" / "captures"
    scenes = []
    for sc, t in zip(spec["scenes"], tl["scenes"]):
        s = {**sc, **t}
        if sc["type"] == "shot":
            png = cap / sc["image"]
            w, h = Image.open(png).size
            boites = json.loads((cap / sc["boites"]).read_text(encoding="utf-8")) if sc.get("boites") else {}
            s.update(imageUrl=png.as_uri(), W0=w / 3, H0=h / 3)
            s["depart"] = boite(boites, sc.get("depart"))
            s["beats"] = [{**b, "cadre": boite(boites, b["cadre"]), "mise": boite(boites, b.get("mise"))} for b in sc["beats"]]
        scenes.append(s)
    return {
        "fps": FPS, "total": tl["total"], "scenes": scenes, "subs": tl["subs"], "lien": spec["lien"],
        "fichiers": {"logo": (FACEBOOK / "sources" / "logo-vertical-fr.svg").as_uri(),
                     "icone": (FACEBOOK / "sources" / "icon-dark.svg").as_uri()},
    }


def ouvrir(p, data):
    nav = p.chromium.launch()
    page = nav.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    page.on("pageerror", lambda e: print("ERREUR PAGE :", e))
    page.add_init_script("window.DATA = " + json.dumps(data, ensure_ascii=False))
    page.goto((RACINE / "outils" / "rendu" / "reels.html").as_uri())
    page.evaluate("window.pret")
    page.wait_for_timeout(400)
    return nav, page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--images", nargs="*", type=float)
    ap.add_argument("--refaire-voix", action="store_true")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    dossier = RACINE / "sources" / spec["id"]
    dossier.mkdir(parents=True, exist_ok=True)
    faire_voix(spec, dossier, a.refaire_voix)
    tl = chronologie(spec, dossier)
    data = donnees(spec, tl)
    print(f"durée {tl['total']:.2f}s, {len(tl['subs'])} sous-titres")
    if a.images:
        sortie = dossier / "apercus"
        sortie.mkdir(exist_ok=True)
        with sync_playwright() as p:
            nav, page = ouvrir(p, data)
            for t in a.images:
                page.evaluate(f"render({t})")
                page.screenshot(path=sortie / f"t_{t:06.2f}.png")
            nav.close()
        print("aperçus :", sortie)
        return
    audio(spec, dossier, tl)
    n = int(round(tl["total"] * FPS))
    sortie = RACINE / spec["sortie"]
    cmd = [FFMPEG, "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "png", "-i", "-",
           "-i", str(dossier / "voix-off.wav"), "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), "-profile:v", "high",
           "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1",
           "-t", f"{tl['total']:.3f}", str(sortie)]
    with sync_playwright() as p:
        nav, page = ouvrir(p, data)
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            page.evaluate(f"render({i / FPS:.5f})")
            ff.stdin.write(page.screenshot(type="png"))
            if i % 200 == 0:
                print(f"image {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); nav.close()
    print("écrit :", sortie)


main()
