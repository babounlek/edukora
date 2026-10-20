r"""Recalcule INDEPENDAMMENT la reponse de chacune des 50 questions du Paper 1 Additional Mathematics inedit et la compare aux options.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_addmaths_p1.py [ep-....json]

La valeur attendue est recalculee ici a partir des DONNEES de l'enonce par une autre voie que le corrige (force brute, evaluation numerique,
derivation numerique, parcours de grille) ; chacune des quatre options est lue (nombre, expression, ensemble, point, vecteur, matrice,
inequation, region) et l'option cle doit etre la SEULE egale a l'attendu. Sortie 1 au moindre ecart.
"""
import itertools
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_p1 as F  # noqa: E402
from verifier_reponses_maths_p1 import frac_tex, matrice, point as lire_point  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-addmaths-p1-1-2026-s1.json")
TOL = 1e-9


def nettoyer(t):
    t = t.replace("$", "").replace("\u2212", "-").replace(r"\,", "").replace(r"\ ", " ")
    t = re.sub(r"\\text\{[^}]*\}(\^\{?\d\}?)?", "", t)
    t = re.sub(r"\bcm\b", "", t)
    return t.strip()


def valf(t):
    """Nombre reel d'une option : entiers, decimaux, fractions, racines (\\sqrt{n}), signes."""
    e = nettoyer(t)
    e = re.sub(r"\\sqrt\{(\d+)\}", r"math.sqrt(\1)", e)
    e = frac_tex(e)
    e = re.sub(r"(\d|\))(math\.sqrt)", r"\1*\2", e)
    e = re.sub(r"(\))(\()", r"\1*\2", e)
    return float(eval(e, {"__builtins__": {}, "math": math}))


def egal(a, b):
    return abs(a - b) <= TOL * max(1.0, abs(b))


def liste_nombres(t):
    return frozenset(float(valf(x)) for x in re.split(r"\band\b", nettoyer(t).replace("^{\\circ}", "")) if x.strip())


def vec_ij(t):
    t = nettoyer(t).replace(" ", "")
    i = re.search(r"(-?\d*)\\mathbf\{i\}", t)
    j = re.search(r"([+-]?\d*)\\mathbf\{j\}", t)

    def coef(m):
        if not m:
            return 0
        s = m.group(1)
        return -1 if s == "-" else 1 if s in ("", "+") else int(s)
    return (coef(i), coef(j))


def inequation(t):
    """\\(a x + b y \\leq c\\) -> (a, b, c, signe), signe '<=', '>=', '<' ou '>'."""
    t = nettoyer(t).replace(" ", "").replace("\\leq", "<=").replace("\\geq", ">=")
    m = re.fullmatch(r"(\d*)x\+(\d*)y(<=|>=|<|>)(\d+)", t)
    a = int(m.group(1) or 1)
    b = int(m.group(2) or 1)
    return (a, b, int(m.group(4)), m.group(3))


def region_options(t):
    """Trois inequations simples (x >= 1, y <= x ...) -> ensemble des points d'une grille qui les verifient tous."""
    morceaux = [p for p in nettoyer(t).replace("\\leq", "<=").replace("\\geq", ">=").replace(r"\ ", " ").split(",") if p.strip()]
    pts = set()
    for i in range(0, 14):
        for j in range(0, 12):
            x, y = Fr(i, 2), Fr(j, 2)
            ok = True
            for p in morceaux:
                m = re.fullmatch(r"\s*(x|y)\s*(<=|>=)\s*(x|\d+)\s*", p)
                g, op, d = m.groups()
                lhs = x if g == "x" else y
                rhs = x if d == "x" else Fr(int(d))
                ok = ok and (lhs <= rhs if op == "<=" else lhs >= rhs)
            if ok:
                pts.add((x, y))
    return frozenset(pts)


def fonction_x(t, noms=("x",)):
    """Option algebrique -> fonction x -> float (puissances, fractions, trig simples \\sin2x, \\cos2x, produit implicite)."""
    e = nettoyer(t)
    e = re.sub(r"\\(sin|cos)\s*(\d*)x", lambda m: f"math.{m.group(1)}({m.group(2) or '1'}*x)", e)
    e = re.sub(r"\^\{(-?\d+)\}", r"**(\1)", e)
    e = frac_tex(e)
    for _ in range(3):
        e = re.sub(r"(\d|\))(x|\(|math)", r"\1*\2", e)
        e = re.sub(r"(x)(\()", r"\1*\2", e)
    code = compile(e, "<option>", "eval")
    return lambda x, k=0.0: float(eval(code, {"__builtins__": {}, "math": math}, {"x": x, "k": k}))


def derivee(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


def integrale(f, a, b, n=2000):
    h = (b - a) / n
    s = f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n))
    return s * h / 3


def sous_groupe(t):
    s = {int(x) for x in nettoyer(t).replace("\\{", "").replace("\\}", "").split(",")}
    G = {1, 3, 5, 7}
    if not s <= G or 1 not in s:
        return False
    return all((a * b) % 8 in s for a in s for b in s)


def attendus():
    E = {}
    E[1] = ("f", (2 / 5) ** -2)
    E[2] = ("f", 6 / (math.sqrt(3) + 1))
    E[3] = ("f", math.log10(20) + math.log10(5))
    d = math.sqrt(5 ** 2 + 4 * 2 * 8)  # 2x^2 - 5x - 8 = 0
    a1, a2 = (5 + d) / 4, (5 - d) / 4
    E[4] = ("f", a1 + a2 + a1 * a2)
    # x^2 + kx + 9 sans racine reelle : k^2 - 36 < 0, bornes lues sur les racines de k^2 = 36
    bornes = sorted([-math.sqrt(36), math.sqrt(36)])
    E[5] = ("texte", f"$-{int(abs(bornes[0]))}<k<{int(bornes[1])}$")
    E[6] = ("f", (-2) ** 3 - 3 * (-2) + 4)
    p = next(p for p in range(-20, 21) if 3 ** 3 - p * 3 ** 2 + 3 - 3 == 0)
    E[7] = ("f", p)
    E[8] = ("f", [7 + i * (-3) for i in range(5)][-1])
    E[9] = ("f", sum(3 + 4 * i for i in range(12)))
    E[10] = ("f", next(r for r in range(2, 20) if 6 * r ** 3 == 162))
    E[11] = ("f", sum(8 * (1 / 4) ** i for i in range(200)))
    poly = [1]
    for _ in range(5):  # (2 + x)^5
        nxt = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            nxt[i] += 2 * c
            nxt[i + 1] += c
        poly = nxt
    E[12] = ("f", poly[2])
    pol = [1]
    for _ in range(4):  # (1 - 2x)^4
        nxt = [0] * (len(pol) + 1)
        for i, c in enumerate(pol):
            nxt[i] += c
            nxt[i + 1] += -2 * c
        pol = nxt
    E[13] = ("fx", lambda x: sum(c * x ** i for i, c in enumerate(pol[:3])))
    E[14] = ("f", len(set(itertools.permutations("LEVEL"))))
    E[15] = ("f", len(list(itertools.combinations(range(8), 3))))
    cadrans = {1: (1, 1), 2: (1, -1), 3: (-1, -1), 4: (-1, 1)}  # (signe sin, signe cos)
    E[16] = ("texte", {1: "first", 2: "second", 3: "third", 4: "fourth"}[next(k for k, v in cadrans.items() if v == (-1, 1))] + " quadrant")
    E[17] = ("f", math.cos(math.radians(150)))
    E[18] = ("trig", lambda A: math.sin(2 * A) / (2 * math.sin(A)))
    E[19] = ("set", frozenset(float(x) for x in range(0, 361) if abs(2 * math.sin(math.radians(x)) - 1) < 1e-9))
    E[20] = ("f", 0.5 * 6 ** 2 * 1.5)
    E[21] = ("f", min(4 - 3 * math.cos(i / 1000) for i in range(0, 7000)))
    t = F.TRIANGLE
    E[22] = ("f", t["BC"] * math.sin(math.radians(t["B"])) / math.sin(math.radians(t["A"])))
    E[23] = ("f", (8 ** 2 + 9 ** 2 - 7 ** 2) / (2 * 8 * 9))
    E[24] = ("point", ((-3 + 7) / 2, (5 + -1) / 2))
    (xa, ya), (xb, yb) = F.DROITE["x_int"], F.DROITE["y_int"]
    E[25] = ("droite", [(xa, ya), (xb, yb)])
    E[26] = ("f", abs(3 * 3 + 4 * 1 - 20) / math.hypot(3, 4))
    E[27] = ("texte", "$-1\\leq x<4$")
    E[28] = ("texte", "$-2<x<3$")
    E[29] = ("set", frozenset(x for x in (3.0, -5 / 3) if abs(abs(3 * x - 2) - 7) < 1e-9))
    E[30] = ("ineq", (2, 5, 40, "<="))
    g = F.REGION
    sommets = [(g["x"], g["x"]), (g["x"], g["y"]), (g["y"], g["y"])]
    grille = set()
    for i in range(0, 14):
        for j in range(0, 12):
            x, y = Fr(i, 2), Fr(j, 2)
            if x >= g["x"] and y <= g["y"] and y >= x:  # triangle ferme : controle croise avec les sommets
                grille.add((x, y))
    assert all((Fr(sx), Fr(sy)) in grille for sx, sy in sommets)
    E[31] = ("region", frozenset(grille))
    E[32] = ("f", (lambda f, gg: gg(f(2)))(lambda x: 2 * x - 1, lambda x: x ** 2 + 3))
    E[33] = ("f", next(x for x in range(-100, 100) if (2 * x - 3) / 5 == 3))
    fp = lambda x: x ** 2 - 1 if x >= 2 else 3 - x
    E[34] = ("f", fp(-1) + fp(3))
    E[35] = ("f", 3 * 5 - (-2) * 4)
    E[36] = ("f", next(k / 2 for k in range(-40, 41) if 4 * (k / 2) - 6 == 0))
    M = ((1, 2), (3, -1))
    E[37] = ("point", (M[0][0] * 2 + M[0][1] * -1, M[1][0] * 2 + M[1][1] * -1))
    E[38] = ("f", 3 + 2 - 3 * 2)
    E[39] = ("f", (3 * 4 + 3) % 5)
    E[40] = ("sousgroupe", True)
    E[41] = ("vec", (6 - 2, 1 - 7))
    E[42] = ("vec", (2 + 2 * 5, -1 + 2 * 3))
    E[43] = ("f", next(p for p in range(-50, 51) if 2 * 6 + 3 * p == 0))
    E[44] = ("deriv", lambda x: 3 / x ** 2)
    E[45] = ("deriv", lambda x: (2 * x + 1) ** 4)
    E[46] = ("f", min(x * x - 8 * x + 3 for x in [i / 100 for i in range(-1000, 2000)]))
    E[47] = ("primitive", lambda x: 6 * x ** 2 - 4 * x)
    E[48] = ("primitive", lambda x: math.cos(3 * x) + 2 * x)
    E[49] = ("f", integrale(lambda x: 2 * x + 1, 1, 3))
    E[50] = ("f", integrale(lambda x: 4 - x * x, -2, 2))
    return E


def comparer(spec, texte):
    kind = spec[0]
    if kind == "f":
        return egal(valf(texte), spec[1])
    if kind == "texte":
        return nettoyer(texte) == nettoyer(spec[1])
    if kind == "set":
        return liste_nombres(texte) == spec[1] if "and" in texte else frozenset(valf(texte) for _ in [0]) == spec[1]
    if kind == "point":
        return tuple(float(x) for x in lire_point(texte)) == tuple(float(x) for x in spec[1])
    if kind == "vec":
        return vec_ij(texte) == tuple(spec[1])
    if kind == "mat":
        return matrice(texte) == spec[1]
    if kind == "fx":
        f = fonction_x(texte)
        return all(abs(f(x) - spec[1](x)) < 1e-8 for x in (-2.0, -0.5, 0.7, 1.3, 3.0))
    if kind == "trig":
        e = nettoyer(texte)
        e = re.sub(r"\\(sin|cos|tan)\s*A", lambda m: f"math.{m.group(1)}(A)", e)
        e = re.sub(r"(\d)(math)", r"\1*\2", e)
        return all(abs(eval(e, {"__builtins__": {}, "math": math}, {"A": A}) - spec[1](A)) < 1e-9 for A in (0.3, 0.8, 1.1, 2.0))
    if kind == "droite":
        m = re.fullmatch(r"(\d*)x([+-])(\d*)y=(\d+)", nettoyer(texte).replace(" ", ""))
        a, b, c = int(m.group(1) or 1), int(m.group(3) or 1) * (1 if m.group(2) == "+" else -1), int(m.group(4))
        return all(a * x + b * y == c for x, y in spec[1])
    if kind == "ineq":
        return inequation(texte) == spec[1]
    if kind == "region":
        return region_options(texte) == spec[1]
    if kind == "sousgroupe":
        return sous_groupe(texte) is spec[1]
    if kind == "deriv":
        f = fonction_x(texte)
        return all(abs(f(x) - derivee(spec[1], x)) < 1e-4 * max(1.0, abs(f(x))) for x in (0.7, 1.3, 2.0, 3.1))
    if kind == "primitive":
        f = fonction_x(texte)
        return all(abs(derivee(f, x) - spec[1](x)) < 1e-4 * max(1.0, abs(spec[1](x))) for x in (-1.2, 0.4, 1.3, 2.5))
    raise ValueError(kind)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    qs = ep["exercices"][0]["questions"]
    E = attendus()
    erreurs = 0
    for q in qs:
        n = int(q["numero"])
        spec = E[n]
        egales = []
        for c in q["choix"]:
            try:
                if comparer(spec, c["texte"]):
                    egales.append(c["lettre"])
            except Exception as exc:
                print(f"  option illisible Q{n} {c['lettre']}: {exc} ({c['texte']})")
                egales.append("?")
        if egales != [q["reponse_correcte"]]:
            erreurs += 1
            print(f"ERREUR Q{n}: cle {q['reponse_correcte']}, options egales a l'attendu {egales}")
    print(f"{len(qs)} questions recalculees, {erreurs} ecart(s).")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
