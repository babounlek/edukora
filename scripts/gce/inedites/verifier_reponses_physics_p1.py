r"""Recalcule INDEPENDAMMENT les reponses chiffrees ou lues sur les donnees des figures du Paper 1 Physics inedit.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_physics_p1.py [ep-....json]

Pour chaque question recalculable : la valeur attendue est recalculee ici a partir de l'enonce (ou des constantes de la figure), les quatre
options sont lues, et la cle doit etre la SEULE egale. Les questions de pur rappel de cours sont relues a la main.
Sortie 1 au moindre ecart.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_p1 as F  # noqa: E402
from questions_physics_p1 import questions  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-physics-p1-1-2026-s1.json")


def nombre(txt):
    t = txt.replace("$", "").replace("\\,", "").replace("\\ ", " ")
    t = re.sub(r"\\text\{[^}]*\}", "", t)
    t = t.replace("^{\\circ}", "").replace("\\Omega", "").replace("\\%", "").replace("%", "")
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*\\times\s*10\^\{(-?\d+)\}", t)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2))
    m = re.search(r"\\dfrac\{(\d+)\}\{(\d+)\}", t)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.search(r"-?\d+(?:\.\d+)?", t.replace(" ", ""))
    return float(m.group()) if m else None


def aire_vt(pts):
    return sum((t2 - t1) * (v1 + v2) / 2 for (t1, v1), (t2, v2) in zip(pts, pts[1:]))


def attendues():
    E = {}
    E["p02"] = (nombre, 2.5 + 34 * 0.01)
    E["p03"] = (nombre, 540 / 200)
    E["p04"] = (nombre, 150 / 2.5)
    E["p05"] = (nombre, aire_vt(F.VT_POINTS))
    E["p06"] = (nombre, (16 - 4) / 3)
    E["p07"] = (nombre, 30 / 6)
    E["p08"] = (nombre, 12 * 1.6)
    E["p09"] = (nombre, (2 * 3 + 1 * 0) / (2 + 1))
    r = F.REGLE
    E["p11"] = (nombre, r["pivot"] + r["poids_connu"] * (r["pivot"] - r["position_connue"]) / r["poids_inconnu"])
    E["p12"] = (nombre, 4 * 25 / 10)
    E["p13"] = (nombre, 600 / 0.03)
    E["p14"] = (nombre, 1000 * 10 * 15)
    E["p15"] = (nombre, (200 / 50) / 5 * 100)
    E["p16"] = (nombre, 50 * 4)
    E["p17"] = (nombre, 200 * 10 * 6 / 20)
    E["p18"] = (nombre, 0.5 * 4 * 5 ** 2)
    E["p20"] = (nombre, 2 * 4200 * (70 - 20))
    E["p21"] = (nombre, 0.5 * 336000)
    E["p22"] = (nombre, (10 - 4) / (24 - 4) * 100)
    # p24 : palier a la temperature d'ebullition (la plus haute des deux paliers)
    paliers = [(a, b, ta) for (a, ta), (b, tb) in zip(F.CHAUFFE, F.CHAUFFE[1:]) if False]
    pts = F.CHAUFFE
    plats = [(i, i + 1) for i in range(len(pts) - 1) if pts[i][1] == pts[i + 1][1]]
    haut = max(plats, key=lambda p: pts[p[0]][1])
    E["p24"] = (lambda t: t.strip(". "), f"{'ABCDEF'[haut[0]]} and {'ABCDEF'[haut[1]]}")
    E["p25"] = (nombre, 25 * 12)
    E["p26"] = (nombre, 1500 * 0.8 / 2)
    E["p29"] = (nombre, 2 * F.ANGLE_INCIDENCE)
    E["p30"] = (nombre, 1 / (1 / 10 - 1 / 30))
    E["p31"] = (nombre, round(math.sin(math.radians(45)) / math.sin(math.radians(30)), 1))
    c = F.CIRCUIT_P1
    rt = c["R1"] + 1 / (1 / c["R2"] + 1 / c["R3"])
    E["p36"] = (nombre, c["U"] / rt)
    E["p34"] = (nombre, 3 * 2 * 60)
    E["p35"] = (nombre, 12 / 0.4)
    E["p37"] = (nombre, 60 / 1000 * 5)
    E["p40"] = (nombre, 240 * 50 / 200)
    E["p44"] = (nombre, 0.5 ** (24 // 6))
    E["p47"] = (nombre, 27 - 13)
    E["p49"] = (nombre, 36 / 20)
    E["p50"] = (lambda t: t.strip(". ").lower(), F.CLE_GRAPHES if F.GRAPHES_OPTIONS[F.CLE_GRAPHES].startswith("droite passant par l'origine") else None)
    return E


def verifier(ep):
    erreurs = []
    qs = ep["exercices"][0]["questions"]
    source = {q["id"]: q for q in questions()}
    E = attendues()
    trouvees = 0

    def cible(qid):
        sol = source[qid]["sol"]
        return [q for q in qs if sol in q["corrige_markdown"]]

    for qid, (lire, attendu) in E.items():
        c = cible(qid)
        if len(c) != 1:
            erreurs.append(f"{qid}: question introuvable ou ambigue ({len(c)})")
            continue
        q = c[0]
        trouvees += 1
        egales = []
        for ch in q["choix"]:
            v = lire(ch["texte"])
            if v == attendu or (isinstance(attendu, float) and isinstance(v, float) and abs(v - attendu) < 1e-9):
                egales.append(ch["lettre"])
        if qid == "p50":
            egales = [ch["lettre"] for ch in q["choix"] if lire(ch["texte"]) == attendu]
            if egales != [q["reponse_correcte"]] or q["reponse_correcte"] != F.CLE_GRAPHES:
                erreurs.append(f"p50: la cle doit etre le panneau {F.CLE_GRAPHES.upper()} de la figure, trouve {q['reponse_correcte']} / {egales}")
            continue
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"{qid} (Q{q['numero']}): attendu {attendu!r}, cle {q['reponse_correcte']}, options egales {egales}")
    # p32 : angle critique, l'option la plus proche de arcsin(1/n)
    c = cible("p32")
    if len(c) == 1:
        trouvees += 1
        q = c[0]
        ang = math.degrees(math.asin(1 / 1.5))
        ecarts = sorted((abs(nombre(ch["texte"]) - ang), ch["lettre"]) for ch in q["choix"])
        if ecarts[0][1] != q["reponse_correcte"] or ecarts[1][0] - ecarts[0][0] < 3:
            erreurs.append(f"p32: l'option la plus proche de {ang:.1f} degres est {ecarts[0][1]}, cle {q['reponse_correcte']}, marge {ecarts[1][0] - ecarts[0][0]:.1f}")
    # p45 : alpha sur U-238
    c = cible("p45")
    if len(c) == 1:
        trouvees += 1
        q = c[0]
        att = (238 - 4, 92 - 2)
        egales = [ch["lettre"] for ch in q["choix"] if tuple(int(x) for x in re.findall(r"\d+", ch["texte"])) == att]
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"p45: attendu {att}, cle {q['reponse_correcte']}, egales {egales}")
    # coherence des constantes de figure avec l'enonce
    if F.VT_POINTS != [(0, 0), (6, 12), (10, 12)]:
        erreurs.append("figure vitesse-temps modifiee")
    return erreurs, trouvees


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    print(f"{n} questions recalculees sur {len(ep['exercices'][0]['questions'])}, {len(erreurs)} ecart(s). Les autres sont du rappel de cours, relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
