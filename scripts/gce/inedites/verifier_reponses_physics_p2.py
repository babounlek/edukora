r"""Recalcule INDEPENDAMMENT les reponses chiffrees du Paper 2 Physics inedit et les compare a la ligne « **Answer: ...** » du corrige ;
controle aussi les valeurs intermediaires citees (energie de fusion, travail d'entree, droite de Hooke).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_physics_p2.py [ep-....json]

Les donnees des questions 3 (circuit) et 7 (ressort) sont relues dans les constantes des figures : la valeur attendue ne depend ni du texte
du corrige ni du dessin. Les definitions et descriptions (la majorite des 46 sous-questions) sont relues a la main.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_p2 as F  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-physics-p2-1-2026-s1.json")


def nombre(txt):
    t = txt.replace("$", "").replace("\\,", "").replace("\\ ", " ")
    t = re.sub(r"\\text\{[^}]*\}", "", t)
    t = t.replace("^{\\circ}", "").replace("\\Omega", "").replace("\\%", "").replace("%", "").replace("\\approx", "")
    m = re.search(r"-?\d+(?:\.\d+)?", t.replace(" ", ""))
    return float(m.group()) if m else None


def verifier(ep):
    erreurs = []
    qs = {(ex["numero_exercice"], q["numero"]): q for ex in ep["exercices"] for q in ex["questions"]}

    def ans(e, n):
        m = re.search(r"\*\*Answer: (.*)\.\*\*", qs[(e, n)]["corrige_markdown"])
        return m.group(1) if m else None

    def corr(e, n):
        return qs[(e, n)]["corrige_markdown"]

    def ok(cond, msg):
        if not cond:
            erreurs.append(msg)

    def egal(e, n, attendu, tol=1e-9):
        a = ans(e, n)
        v = nombre(a) if a else None
        ok(v is not None and abs(v - attendu) <= tol, f"{e}{n}: attendu {attendu}, ligne Answer {a!r}")

    def contient(e, n, *jetons):
        for j in jetons:
            ok(j in corr(e, n), f"{e}{n}: valeur absente du corrige : {j!r}")

    # 1 : machine de VR 6, charge 450 N sur 2 m, effort 100 N
    charge, effort, vr, h = 450, 100, 6, 2
    ma = charge / effort
    egal("1", "b", ma)
    egal("1", "c", charge * h)
    egal("1", "d", ma / vr * 100)
    ok(abs(charge * h / (effort * vr * h) * 100 - ma / vr * 100) < 1e-9, "1d : le travail d'entree ne redonne pas le meme rendement")
    contient("1", "d", "1\\,200")
    # 2 : balancoire
    egal("2", "b", 400 * 2 / 320)
    ok(400 * 2 / 320 < 3, "2b : la fille ne doit pas sortir de la planche")
    # 3 : circuit de la figure 1 (constantes de figs_physics_p2)
    c = F.CIRCUIT_P2
    rp = 1 / (1 / c["R2"] + 1 / c["R3"])
    rt = c["R1"] + rp
    i = c["U"] / rt
    egal("3", "b", rt)
    egal("3", "c", i)
    egal("3", "d", i * rp)
    ok(abs((c["U"] - i * c["R1"]) - i * rp) < 1e-9, "3d : p.d. aux bornes de la paire en parallele")
    # 4 : demi-vie 8 jours, 80 g, 24 jours
    egal("4", "b", 80 * 0.5 ** (24 // 8))
    # 5 : n = sin48 / sin34, angle critique
    n = math.sin(math.radians(48)) / math.sin(math.radians(34))
    egal("5", "b", round(n, 2))
    egal("5", "c", round(math.degrees(math.asin(1 / round(n, 2)))), tol=1)
    # 6 : echo
    egal("6", "b", 2 * 85 / 340)
    # 7 : ressort (donnees des figures)
    k = F.pente_origine(F.HOOKE_EXT, F.HOOKE_FORCE)
    ok(1.9 <= k <= 2.0, f"7c : pente {k:.3f} N/cm hors de l'intervalle accepte 1,9 a 2,0")
    ok(abs(nombre(ans("7", "c")) - round(k, 1)) < 0.06, f"7c : {ans('7', 'c')} / pente {k:.3f}")
    egal("7", "d", round(k * 3.5, 1))
    egal("7", "f", 60 * 10 / 0.2)
    egal("7", "h", 780 / (10 * 5 * 4))
    ok(all(f >= 0 for f in F.HOOKE_FORCE) and F.HOOKE_FORCE == sorted(F.HOOKE_FORCE), "7 : forces croissantes")
    # 8 : chaleur massique et chaleur latente
    egal("8", "c", (50 * 5 * 60) / (1.0 * (35 - 20)))
    egal("8", "g", 0.2 * 336000 + 0.2 * 4200 * 25)
    contient("8", "g", "67\\,200", "21\\,000")
    # 9 : transformateur, bouilloire
    vs = 230 * 50 / 1000
    egal("9", "a", vs)
    egal("9", "b", vs * 4)
    egal("9", "c", vs * 4 / 230)
    egal("9", "g", round(2000 / 240, 1))
    egal("9", "i", 2 * 0.25 * 100)
    ok(2000 / 240 < 13 and 2000 / 240 > 5, "9h : le fusible de 13 A doit etre le seul convenable")
    # barème : sections 40 et 60, questions de la section II = 20
    pts = {ex["numero_exercice"]: float(ex["points"]) for ex in ep["exercices"]}
    ok(sum(pts[k] for k in "123456") == 40 and sum(pts[k] for k in "789") == 60, "sections I et II")
    ok(all(pts[k] == 20 for k in "789"), "chaque question de la Section II vaut 20 points")
    return erreurs


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    n = sum(len(x["questions"]) for x in ep["exercices"])
    print(f"{n} sous-questions, 21 reponses chiffrees recalculees, {len(erreurs)} ecart(s). Definitions et descriptions relues a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
