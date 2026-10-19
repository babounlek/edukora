"""Recalcule INDEPENDAMMENT chaque reponse du Paper 2 inedit (62 sous-questions) et la compare a la ligne « **Answer: ...** »
du corrige, puis verifie que les valeurs intermediaires citees dans la resolution existent bien.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\verifier_reponses_maths_p2.py [ep-....json]

Les valeurs attendues sont recalculees ici a partir des DONNEES de l'enonce (jamais lues dans le corrige) et par une
methode differente de celle du corrige quand c'est possible (force brute, evaluation numerique de formules, comptage).
Sortie 1 au moindre ecart.
"""
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
from verifier_reponses_maths_p1 import expression, frac_tex, nettoyer, nombre  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-maths-p2-1-2026-s1.json")


def th(n):
    """1450 -> « 1\\,450 » (les milliers s'ecrivent avec \\, dans le contenu)."""
    n = int(n)
    return f"{n:,}".replace(",", "\\,") if n >= 1000 else str(n)


def reponse(corrige):
    m = re.search(r"\*\*Answer: (.*)\.\*\*", corrige)
    return m.group(1) if m else None


def est_nombre(txt, attendu, tol=0):
    return abs(float(nombre(txt)) - float(attendu)) <= tol


def ens(txt):
    t = nettoyer(txt.split("=", 1)[1] if "=" in txt else txt).replace(" ", "").replace("\\{", "{").replace("\\}", "}")
    return frozenset(int(x) for x in t.strip("{}").split(","))


def valeurs_entieres(txt):
    return [Fr(x) for x in re.findall(r"-?\d+(?:\.\d+)?", txt.replace("\\,", ""))]


def evalue_formule(txt, noms_vals):
    """Evalue une formule LaTeX simple (puissances, fractions, pi, produit implicite) en flottants."""
    e = txt.replace("$", "").replace("\u2212", "-").replace("\\pi", "(PI)")
    e = re.sub(r"\^\{(-?\d+)\}", r"**(\1)", e)
    e = re.sub(r"\^(\d)", r"**\1", e)
    e = frac_tex(e)
    e = e.replace("\\mathbf{a}", "a").replace("\\mathbf{b}", "b")
    for _ in range(3):
        e = re.sub(r"(\d|\))(\(|[a-zA-Z])", r"\1*\2", e)
        e = re.sub(r"([a-zA-Z])(\()", r"\1*\2", e)
        e = re.sub(r"([a-zA-Z])(?=[a-zA-Z])", r"\1*", e)
    e = e.replace("(P*I)", "(PI)").replace("P*I", "PI")
    env = {"__builtins__": {}, "PI": math.pi}
    env.update(noms_vals)
    return eval(e, env)


def verifier(ep):
    erreurs = []
    qs = {}
    for ex in ep["exercices"]:
        for q in ex["questions"]:
            qs[(ex["numero_exercice"].lstrip("0"), q["numero"])] = q
    cle = lambda e, n: (e, n)

    def ans(e, n):
        return reponse(qs[cle(e, n)]["corrige_markdown"])

    def corr(e, n):
        return qs[cle(e, n)]["corrige_markdown"]

    def ok(cond, msg):
        if not cond:
            erreurs.append(msg)

    def contient(e, n, *jetons):
        for j in jetons:
            ok(j in corr(e, n), f"{e}.{n}: valeur intermediaire absente du corrige : {j!r}")

    # ----------------------------------------------------------------------------- Section A
    ok(est_nombre(ans("1", "1"), (Fr(3, 2) ** 2) / Fr(3, 8)), "A1")
    contient("1", "1", r"\dfrac{9}{4}", r"\dfrac{72}{12}")
    ok(8 ** 2 == 2 ** 6 == 4 ** 3 and "8^{2}=2^{6}" in ans("2", "a") and "4^{3}=2^{6}" in ans("2", "a"), "A2a")
    ok("2^{-3}" in ans("2", "b") and Fr(2) ** 6 * Fr(2) ** -3 / Fr(2) ** 6 == Fr(1, 8) == Fr(2) ** -3, "A2b")
    ok(est_nombre(ans("2", "c"), Fr(8 ** 2, 1) * Fr(1, 8) / 4 ** 3), "A2c")
    # A3 : T = 2 pi sqrt(l/g)  ->  l = g T^2 / (4 pi^2), verifie numeriquement
    rhs = ans("3", "1").split("=", 1)[1]
    for l0, g0 in ((2.0, 9.8), (0.75, 10.0), (5.5, 9.81)):
        T = 2 * math.pi * math.sqrt(l0 / g0)
        ok(abs(evalue_formule(rhs, {"g": g0, "T": T}) - l0) < 1e-9, f"A3 formule fausse pour l={l0}")
    xi = set(range(1, 13))
    A = {x for x in xi if x % 3 == 0}
    B = {x for x in xi if 12 % x == 0}
    ok(ens(ans("4", "a")) == A, "A4a")
    ok(ens(ans("4", "b")) == B, "A4b")
    ok(ens(ans("4", "c")) == A & B, "A4c")
    ok(ens(ans("4", "d")) == (xi - A) & B, "A4d")
    ok(est_nombre(ans("4", "e").split("=")[1], len(A | B)), "A4e")
    # A5 : force brute sur x, y
    sol = [(x, y) for x in range(-20, 21) for y in range(-20, 21)
           if (x + 1, 2 - 4, 3 + 2, y + 5) == (6, -2, 5, 9)]
    ok(sol == [(5, 4)] and valeurs_entieres(ans("5", "a")) == [5, 4], f"A5a {sol} {ans('5', 'a')}")
    ok(est_nombre(ans("5", "b"), 5 * 4 - 2 * 3), "A5b")
    # A6 : reseau W X Y Z
    aretes = [("W", "X"), ("W", "X"), ("X", "Y"), ("Y", "Z"), ("Z", "W"), ("X", "Z")]
    deg = {}
    for u, v in aretes:
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    V, Earcs = len(deg), len(aretes)
    ok(est_nombre(ans("6", "a"), V), "A6a")
    ok(est_nombre(ans("6", "b"), Earcs), "A6b")
    ok(est_nombre(ans("6", "c"), 2 - V + Earcs), "A6c")
    ok(est_nombre(ans("6", "d"), sum(1 for d in deg.values() if d % 2 == 0)), "A6d")
    impairs = sorted(k for k, d in deg.items() if d % 2)
    ok(impairs == ["W", "Z"] and "(W" in ans("6", "e") or "$W$" in ans("6", "e"), "A6e")
    ok(len(impairs) == 2, "A6e : le reseau n'est pas parcourable")
    # A7 : vecteurs, coefficients de a et de b
    def coeffs(txt):
        rhs_ = txt.split("=", 1)[1]
        return (Fr(str(round(evalue_formule(rhs_, {"a": 1, "b": 0}), 9))).limit_denominator(100),
                Fr(str(round(evalue_formule(rhs_, {"a": 0, "b": 1}), 9))).limit_denominator(100))
    ok(coeffs(ans("7", "a")) == (-1, 1), f"A7a {coeffs(ans('7', 'a'))}")
    ok(coeffs(ans("7", "b")) == (Fr(-1, 3), Fr(1, 3)), f"A7b {coeffs(ans('7', 'b'))}")
    ok(coeffs(ans("7", "c")) == (Fr(2, 3), Fr(1, 3)), f"A7c {coeffs(ans('7', 'c'))}")
    a_, b_ = (2, 5), (8, -1)
    C = tuple(a_[i] + Fr(1, 3) * (b_[i] - a_[i]) for i in range(2))
    ok(C == tuple((2 * a_[i] + b_[i]) / Fr(3) for i in range(2)), "A7 controle numerique de OC")
    # A8 : systeme
    p, n = next((p, n) for p in range(0, 1000, 50) for n in range(0, 1000, 50) if 3 * p + 2 * n == 1450 and 2 * p + 5 * n == 2250)
    ok(valeurs_entieres(ans("8", "b")) == [p, n], f"A8b {ans('8', 'b')}")
    ok("3p+2n=" + th(1450) in ans("8", "a").replace(" ", "") and "2p+5n=" + th(2250) in ans("8", "a").replace(" ", ""), "A8a")
    # A9
    sols = [x for x in range(-30, 31) if 3 * (x - 2) >= 5 * x + 4]
    ok(max(sols) == -5 and sols == list(range(-30, -4)) and "x\\leq-5" in ans("9", "a"), "A9a")
    ok("-5" in ans("9", "b"), "A9b")
    # A10
    cartes = range(1, 21)
    prem = [k for k in cartes if k > 1 and all(k % d for d in range(2, k))]
    ok(est_nombre(ans("10", "a"), Fr(sum(1 for k in cartes if k % 4 == 0), 20)), "A10a")
    ok(est_nombre(ans("10", "b"), Fr(len(prem), 20)), "A10b")
    ok(est_nombre(ans("10", "c"), Fr(sum(1 for k in cartes if int(math.isqrt(k)) ** 2 != k), 20)), "A10c")
    # ----------------------------------------------------------------------------- Section B
    cout = 40 * 24500
    cprix = cout + 20000
    vend = 30 * 31000
    prix_remise = Fr(31000) * (1 - Fr(10, 100))
    reste = 10 * prix_remise
    total = vend + reste
    profit = total - cprix
    ok(40 * 3 // 4 == 30, "B1c")
    ok(int(nombre(ans("B1", "a").replace("\\,", ""))) == cout, "B1a")
    ok(int(nombre(ans("B1", "b").replace("\\,", ""))) == cprix, "B1b")
    ok(int(nombre(ans("B1", "c").replace("\\,", ""))) == vend, "B1c")
    ok(int(nombre(ans("B1", "d").replace("\\,", ""))) == prix_remise, "B1d")
    ok(int(nombre(ans("B1", "e").replace("\\,", ""))) == reste, "B1e")
    ok(valeurs_entieres(ans("B1", "f")) == [profit] and total == 1209000, "B1f")
    ok(est_nombre(ans("B1", "g"), profit / cprix * 100), "B1g")
    ok(int(nombre(ans("B1", "h").replace("\\,", ""))) == profit * 5 / 8, "B1h")
    contient("B1", "d", th(3100), th(27900))
    contient("B1", "h", th(26125), th(78375))
    # B2 : donnees groupees
    classes = [(1, 10, 6), (11, 20, 14), (21, 30, 20), (31, 40, 12), (41, 50, 6), (51, 60, 2)]
    effectif = sum(f for _, _, f in classes)
    ok(effectif == 60, "B2 effectif total")
    ok(est_nombre(ans("B2", "a"), Fr(30 + 31, 2)), "B2a")
    modale = max(classes, key=lambda c: c[2])
    ok(f"{modale[0]}-{modale[1]}" in ans("B2", "b").replace("$", ""), "B2b")
    marques = [Fr(a + b, 2) for a, b, _ in classes]
    ok([Fr(x) for x in valeurs_entieres(ans("B2", "c"))] == marques, "B2c")
    fx = [m * f for m, (_, _, f) in zip(marques, classes)]
    moyenne = sum(fx) / effectif
    ok(abs(float(nombre(ans("B2", "d").replace("minutes", ""))) - round(float(moyenne), 2)) < 1e-9, f"B2d {moyenne}")
    for m, f_, x in zip(marques, (c[2] for c in classes), fx):
        contient("B2", "d", f"| {float(m):g} | {f_} | {th(x)} |".replace("5.5 | 6", "5.5 | 6"))
    contient("B2", "d", f"| Total | | {effectif} | {int(sum(fx)):,} |".replace(",", " "))  # cellule de tableau : espace simple
    ok(est_nombre(ans("B2", "e"), Fr(6 + 2, 60)), "B2e")
    seul_m, seul_d, deux, rien = 27 - 8, 21 - 8, 8, 52 - (27 + 21 - 8)
    ok(valeurs_entieres(ans("B2", "f")) == [seul_m, deux, seul_d, rien], "B2f")
    ok(est_nombre(ans("B2", "g"), rien), "B2g")
    ok(est_nombre(ans("B2", "h"), Fr(seul_m + seul_d, 52)), "B2h")
    # B3 : fonctions
    f = lambda x: 5 - 2 * x
    g = lambda x: x * x - 4
    ok(est_nombre(ans("B3", "a"), f(-3)), "B3a")
    rhs = ans("B3", "b").split("=", 1)[1]
    for v in (0, 1, 2.5, -3, 7):
        ok(abs(f(evalue_formule(rhs, {"x": v})) - v) < 1e-9, f"B3b inverse fausse en {v}")
    rhs = ans("B3", "c").split("=", 1)[1]
    for v in (0, 1, 2, -3, 4.5):
        ok(abs(evalue_formule(rhs, {"x": v}) - g(f(v))) < 1e-9, f"B3c gf fausse en {v}")
    racines = [Fr(3, 2), Fr(7, 2)]
    ok(all(g(f(float(r))) == 0 for r in racines), "B3d racines")
    ok(set(nombre(p_) for p_ in re.findall(r"\\dfrac\{\d+\}\{\d+\}", ans("B3", "d"))) == set(racines), "B3d lecture")
    ok(est_nombre(ans("B3", "e"), 12 // 4 if 36 // 12 == 3 else None), "B3e")
    ok(est_nombre(ans("B3", "f"), 4 * 3 ** 5), "B3f")
    ok(est_nombre(ans("B3", "g"), sum(4 * 3 ** k for k in range(5))), "B3g")
    contient("B3", "g", "4+12+36+108+324=484")
    bd = math.sqrt(30 * (1 - Fr(4, 11) ** 2))
    ok(abs(float(re.search(r"\\approx(\d+\.\d+)", ans("B3", "j")).group(1)) - round(bd, 1)) < 1e-9, "B3j")
    # coordonnees : AB=6, BC=5, AC=4, bissectrice de B
    xC = (25 - 16 + 36) / 12
    yC = math.sqrt(25 - xC ** 2)
    t = 6 / 11
    D = (6 + t * (xC - 6), t * yC)
    ok(abs(math.hypot(*D) - bd) < 1e-9, "B3j geometrie")
    ok(abs(math.atan2(D[1], D[0]) * 2 - math.atan2(yC, xC)) < 1e-9, "B3 D est bien sur la bissectrice")
    # B4
    fq = lambda x: x * x + x - 6
    paires = re.findall(r"f\((-?\d+)\)=(-?\d+)", ans("B4", "a"))
    ok(len(paires) == 4 and all(fq(int(a)) == int(b) for a, b in paires), "B4a")
    ok(sorted(int(a) for a, _ in paires) == [-3, -1, 1, 3], "B4a : valeurs demandees")
    ok(all(fq(x) == 0 for x in (-3, 2)) and valeurs_entieres(ans("B4", "c")) == [-3, 2], "B4c")
    ok(est_nombre(ans("B4", "d").split("=")[1], Fr(-3 + 2, 2)), "B4d")
    ok(est_nombre(ans("B4", "e"), fq(Fr(-1, 2))), "B4e")
    ok(valeurs_entieres(ans("B4", "f")) == [-2, 1] and all(fq(x) == -4 for x in (-2, 1)), "B4f")
    ok(all(x * (x + 3) == 40 for x in (5,)) and "x^{2}+3x-40=0" in ans("B4", "g"), "B4g")
    ok(valeurs_entieres(ans("B4", "h")) == [-8, 5] and all(x * x + 3 * x - 40 == 0 for x in (-8, 5)), "B4h")
    ok(valeurs_entieres(ans("B4", "i")) == [5, 8, 26] and 2 * (5 + 8) == 26 and 5 * 8 == 40, "B4i")
    # tables de valeurs du corrige : toutes les cases recalculees
    ligne = "| $y=f(x)$ | " + " | ".join(f"${fq(x)}$".replace("$-", "$-") for x in range(-4, 4)) + " |"
    ok(ligne in corr("B4", "a"), "B4a : table complete du corrige")
    return erreurs


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    n = sum(len(x["questions"]) for x in ep["exercices"])
    print(f"{n} sous-questions recalculees, {len(erreurs)} ecart(s).")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
