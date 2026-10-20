r"""Recalcule INDEPENDAMMENT la reponse de chacune des 50 questions du Paper 1 n.2 Additional Mathematics inedit et la compare aux options.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_addmaths_p1n2.py [ep-....json]

Meme principe que verifier_reponses_addmaths_p1.py (dont on reprend les lecteurs d'options) : l'attendu est recalcule par force brute,
evaluation numerique, derivation/integration numeriques ou parcours de grille ; l'option cle doit etre la SEULE egale a l'attendu.
"""
import itertools
import json
import math
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_s2 as F  # noqa: E402
from verifier_reponses_addmaths_p1 import comparer, derivee, integrale, nettoyer  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-addmaths-p1-2-2026-s1.json")


def racines2(a, b, c):
    d = math.sqrt(b * b - 4 * a * c)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def sous_groupe_mod9(t):
    s = {int(x) for x in nettoyer(t).replace("\\{", "").replace("\\}", "").split(",")}
    G = {1, 2, 4, 5, 7, 8}
    if not s <= G or 1 not in s:
        return False
    return all((a * b) % 9 in s for a in s for b in s)


def inegalites_texte(solution):
    """Intervalle ou reunion lu par balayage d'une grille de reels : retourne le predicat sous forme de texte de reference."""
    return solution


def attendus():
    E = {}
    E[1] = ("f", (27 / 8) ** (-1 / 3))
    E[2] = ("f", math.sqrt(75) - math.sqrt(12))
    E[3] = ("f", math.log2(40) - math.log2(5))
    a1, a2 = racines2(1, -7, 5)
    E[4] = ("f", a1 ** 2 + a2 ** 2)
    E[5] = ("f", next(k for k in range(-20, 21) if k and (-4) ** 2 - 4 * k * 1 == 0))
    f6 = lambda x: 4 * x ** 3 - 3 * x + 5
    E[6] = ("f", f6(0.5))
    E[7] = ("f", next(p for p in range(-30, 31) if 3 ** 3 - 2 * 3 ** 2 + p * 3 + 6 == 0))
    E[8] = ("f", [4 + 5 * i for i in range(10)][-1])
    d9 = Fr(59 - 2, 19)
    E[9] = ("f", float(sum(2 + d9 * i for i in range(20))))
    E[10] = ("f", sum(3 * 2 ** i for i in range(8)))
    E[11] = ("f", sum(10 * (-1 / 4) ** i for i in range(400)))
    # coefficient de x^3 dans (3 - x)^5 : developpement polynomial par multiplication
    poly = [1]
    for _ in range(5):
        nxt = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            nxt[i] += 3 * c
            nxt[i + 1] += -c
        poly = nxt
    E[12] = ("f", poly[3])
    pol = [1.0]
    for _ in range(6):  # (1 + x/2)^6
        nxt = [0.0] * (len(pol) + 1)
        for i, c in enumerate(pol):
            nxt[i] += c
            nxt[i + 1] += c / 2
        pol = nxt
    E[13] = ("fx", lambda x: sum(c * x ** i for i, c in enumerate(pol[:3])))
    E[14] = ("f", len(set(itertools.permutations("BANANA"))))
    E[15] = ("f", sum(1 for c in itertools.combinations(range(10), 4) if 0 in c and 1 in c))
    # sin(theta) = 3/5 aigu : tan(180 - theta)
    th = math.asin(3 / 5)
    E[16] = ("f", math.tan(math.pi - th))
    E[17] = ("f", math.cos(math.radians(150)) + math.sin(math.radians(30)))
    E[18] = ("trig2", lambda A: (1 - math.cos(2 * A)) / 2)
    E[19] = ("set", frozenset(float(x) for x in range(0, 361) if abs(math.tan(math.radians(x)) - 1) < 1e-9))
    E[20] = ("f", 8 * 0.75)
    # periode de 2 sin 3x : plus petit T > 0 tel que f(x+T) = f(x) en degres
    f21 = lambda x: 2 * math.sin(math.radians(3 * x))
    E[21] = ("f", next(T for T in range(1, 361) if all(abs(f21(x + T) - f21(x)) < 1e-9 for x in range(0, 360, 7))))
    t = F.TRIANGLE
    angle_c = 180 - t["A"] - t["B"]
    ab = t["BC"] * math.sin(math.radians(angle_c)) / math.sin(math.radians(t["A"]))
    ac = t["BC"] * math.sin(math.radians(t["B"])) / math.sin(math.radians(t["A"]))
    # recoupement : le triangle construit a partir des longueurs redonne bien les angles
    cos_c = (t["BC"] ** 2 + ac ** 2 - ab ** 2) / (2 * t["BC"] * ac)
    assert abs(math.degrees(math.acos(cos_c)) - angle_c) < 1e-6
    E[22] = ("f", ac)
    E[23] = ("f", (5 ** 2 + 6 ** 2 - 7 ** 2) / (2 * 5 * 6))
    E[24] = ("f", (-9 - 3) / (4 - (-2)))
    (xa, ya), (xb, yb) = F.DROITE["x_int"], F.DROITE["y_int"]
    E[25] = ("droite", [(xa, ya), (xb, yb)])
    # mediatrice de A(0,2), B(6,-2) : lieu des points equidistants de A et B
    E[26] = ("droite_eq", lambda x, y: x * x + (y - 2) ** 2 == (x - 6) ** 2 + (y + 2) ** 2)
    E[27] = ("intervalle", lambda x: abs(2 * x + 1) < 5)
    E[28] = ("intervalle", lambda x: x * x - 5 * x + 4 >= 0)
    E[29] = ("set", frozenset(x for x in (Fr(n, 6) for n in range(-60, 61)) if abs(x - 3) == 2 * x))
    E[30] = ("systeme", lambda x, y: x + y >= 10 and y <= 2 * x)
    g = F.REGION
    E[31] = ("systeme3", lambda x, y: x >= 0 and y >= g["y"] and x + y <= g["somme"])
    f32 = lambda x: x + 4
    g32 = lambda x: x ** 2
    E[32] = ("f", f32(g32(3)))
    f33 = lambda x: (3 * x + 1) / (x - 2)
    E[33] = ("f", next(x for x in range(-100, 100) if x != 2 and abs(f33(x) - 4) < 1e-9))
    f34 = lambda x: 2 * x if x <= 1 else x * x + 1
    E[34] = ("f", f34(0) + f34(2))
    E[35] = ("f", 4 * 3 - (-1) * 2)
    A, B = ((1, 0), (2, 1)), ((3, 1), (0, 2))
    AB = tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    E[36] = ("mat", AB)
    # rotation anticlockwise de 90 degres : images de (1,0) et (0,1)
    img = lambda x, y: (round(x * math.cos(math.pi / 2) - y * math.sin(math.pi / 2)), round(x * math.sin(math.pi / 2) + y * math.cos(math.pi / 2)))
    c1, c2 = img(1, 0), img(0, 1)
    E[37] = ("mat", ((c1[0], c2[0]), (c1[1], c2[1])))
    E[38] = ("f", 3 * 4 - 3)
    E[39] = ("f", (2 * 4 + 3 * 5) % 6)
    E[40] = ("sousgroupe", True)
    E[41] = ("vecn", (8 / 17, 15 / 17))
    E[42] = ("vec", (-1 + 3 * 3, 4 - 2 * 3))
    E[43] = ("f", (3 * 5 + 4 * -12) / (math.hypot(3, 4) * math.hypot(5, -12)))
    E[44] = ("deriv", lambda x: x ** 1.5)
    E[45] = ("deriv", lambda x: x ** 2 * (x + 1), "fonction")
    E[46] = ("f", -1 / derivee(lambda x: x * x - 3 * x, 2))
    E[47] = ("primitive", lambda x: 4 * x ** 3 - 2 / x ** 2)
    E[48] = ("primitive", lambda x: math.sin(x) + 3)
    E[49] = ("f", integrale(lambda x: 3 * x * x - 4 * x + 2, 1, 3))
    E[50] = ("f", integrale(lambda x: x - x * x, 0, 1))
    return E


def balayage(pred, bornes=(-8.0, 8.0), pas=0.01):
    n = int((bornes[1] - bornes[0]) / pas)
    return tuple(pred(bornes[0] + i * pas) for i in range(n + 1))


def intervalle_texte(t):
    """Option de type '-3<x<2', 'x<=1 or x>=4' -> predicat."""
    e = nettoyer(t).replace("\\leq", "<=").replace("\\geq", ">=").replace(" ", "")
    parties = e.split("or")
    import re

    def predicat(morceau):
        m = re.fullmatch(r"(-?\d+)(<=|<)x(<=|<)(-?\d+)", morceau)
        if m:
            a, o1, o2, b = m.groups()
            a, b = int(a), int(b)
            return lambda x: (a < x if o1 == "<" else a <= x) and (x < b if o2 == "<" else x <= b)
        m = re.fullmatch(r"x(<=|>=|<|>)(-?\d+)", morceau)
        op, v = m.group(1), int(m.group(2))
        return {"<": lambda x: x < v, "<=": lambda x: x <= v, ">": lambda x: x > v, ">=": lambda x: x >= v}[op]
    ps = [predicat(p) for p in parties]
    return lambda x: any(p(x) for p in ps)


def systeme_texte(t):
    import re
    e = nettoyer(t).replace("\\leq", "<=").replace("\\geq", ">=").replace("\\ ", " ").replace(" ", "")
    pts = []
    for p in e.split(","):
        m = re.fullmatch(r"(x|y|x\+y)(<=|>=|<|>)(\d*)([xy]?)", p)
        gauche, op, k, avec_x = m.groups()
        pts.append((gauche, op, k, avec_x))

    def f(x, y):
        ok = True
        for gauche, op, k, avec_x in pts:
            lhs = {"x": x, "y": y, "x+y": x + y}[gauche]
            rhs = (int(k or 1) * (x if avec_x == "x" else y)) if avec_x else int(k)
            ok = ok and {"<=": lhs <= rhs, ">=": lhs >= rhs, "<": lhs < rhs, ">": lhs > rhs}[op]
        return ok
    return f


def comparer_n2(spec, texte):
    import re
    k = spec[0]
    texte = texte.replace(r"^{\circ}", "")
    if k in ("deriv", "primitive"):
        texte = re.sub(r"\^\{\\frac\{(\d+)\}\{(\d+)\}\}", r"**(\1/\2)", texte)
    if k in ("deriv", "primitive"):
        texte = re.sub(r"\^\{(\d+)/(\d+)\}", r"**(\1/\2)", texte)
    if k == "droite":
        m = re.fullmatch(r"(\d*)x([+-])(\d*)y=(-?\d+)", nettoyer(texte).replace(" ", ""))
        a, b, c = int(m.group(1) or 1), int(m.group(3) or 1) * (1 if m.group(2) == "+" else -1), int(m.group(4))
        return all(a * x + b * y == c for x, y in spec[1])
    if k == "trig2":
        e = nettoyer(texte)
        e = re.sub(r"\\(sin|cos|tan)\^\{2\}\s*A", lambda m: f"math.{m.group(1)}(A)**2", e)
        e = re.sub(r"\\(sin|cos|tan)\s*A", lambda m: f"math.{m.group(1)}(A)", e)
        return all(abs(eval(e, {"__builtins__": {}, "math": math}, {"A": A}) - spec[1](A)) < 1e-9 for A in (0.3, 0.8, 1.1, 2.0))
    if k == "droite_eq":
        m = re.fullmatch(r"(\d*)x([+-])(\d*)y=(-?\d+)", nettoyer(texte).replace(" ", ""))
        a, b, c = int(m.group(1) or 1), int(m.group(3) or 1) * (1 if m.group(2) == "+" else -1), int(m.group(4))
        # lieu des points : la droite ax+by=c doit contenir exactement les points equidistants (verifie sur une grille de rationnels)
        pts = [(Fr(i, 2), Fr(j, 2)) for i in range(-12, 25) for j in range(-12, 25)]
        return all((a * x + b * y == c) == spec[1](x, y) for x, y in pts)
    if k == "intervalle":
        p = intervalle_texte(texte)
        return all(p(x) == spec[1](x) for x in (i / 100 for i in range(-800, 801)))
    if k in ("systeme", "systeme3"):
        p = systeme_texte(texte)
        pts = [(Fr(i, 2), Fr(j, 2)) for i in range(-6, 25) for j in range(-6, 25)]
        return all(p(x, y) == spec[1](x, y) for x, y in pts)
    if k == "sousgroupe":
        return sous_groupe_mod9(texte) is spec[1]
    if k == "vecn":
        import re as _re
        t = nettoyer(texte).replace(" ", "").replace("\\dfrac", "\\frac")
        i = _re.search(r"(?:\\frac\{(-?\d+)\}\{(\d+)\}|(-?\d+))\\mathbf\{i\}", t)
        j = _re.search(r"\+(?:\\frac\{(-?\d+)\}\{(\d+)\}|(-?\d+))\\mathbf\{j\}", t)

        def val(m):
            return (int(m.group(1)) / int(m.group(2))) if m.group(1) else float(m.group(3))
        return abs(val(i) - spec[1][0]) < 1e-9 and abs(val(j) - spec[1][1]) < 1e-9
    if k == "deriv" and len(spec) == 3:
        # derivee d'un produit x^2 (x+1) calculee numeriquement
        from verifier_reponses_addmaths_p1 import fonction_x
        f = fonction_x(texte)
        return all(abs(f(x) - derivee(spec[1], x)) < 1e-4 * max(1.0, abs(f(x))) for x in (0.7, 1.3, 2.0, 3.1))
    if k == "mat":
        return matrice_lue(texte) == spec[1]
    if k == "set" and "and" not in texte and "only" in texte:
        import re as _re
        m = _re.search(r"x=(-?\d+)", nettoyer(texte))
        vals = frozenset([Fr(int(m.group(1)))])
        if "and" in texte:
            return False
        return vals == spec[1]
    if k == "set" and "and" in texte and "x=" in texte:
        import re as _re
        vals = frozenset(Fr(int(v)) for v in _re.findall(r"x=(-?\d+)", nettoyer(texte)))
        return vals == spec[1]
    return comparer(spec, texte)


def matrice_lue(t):
    import re
    corps = re.search(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", t.replace("\n", ""))
    lignes = corps.group(1).split("\\\\")
    return tuple(tuple(int(c) for c in l.split("&")) for l in lignes)


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
                if comparer_n2(spec, c["texte"]):
                    egales.append(c["lettre"])
            except Exception as exc:
                print(f"  option illisible Q{n} {c['lettre']}: {exc!r} ({c['texte']})")
                egales.append("?")
        if egales != [q["reponse_correcte"]]:
            erreurs += 1
            print(f"ERREUR Q{n}: cle {q['reponse_correcte']}, options egales a l'attendu {egales}")
    print(f"{len(qs)} questions recalculees, {erreurs} ecart(s).")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
