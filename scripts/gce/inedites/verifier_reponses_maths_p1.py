"""Recalcule INDEPENDAMMENT la reponse de chacune des 50 questions de l'epreuve inedite et la compare aux options.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\verifier_reponses_maths_p1.py [ep-....json]

Pour chaque question : la valeur attendue est recalculee ici a partir des donnees de l'enonce (jamais lue dans le
corrige) ; chacune des quatre options est lue (nombre, ensemble, point, vecteur, matrice, expression evaluee en
plusieurs points) ; l'option cle doit etre la SEULE egale a la valeur attendue. Sortie 1 au moindre ecart.
"""
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-maths-p1-1-2026-s1.json")


# ------------------------------------------------------------------------------------------------ lecture des options
def nettoyer(t):
    t = t.replace("$", "")
    t = t.replace(r"\,", "").replace(r"\ ", " ").replace(r"\%", "").replace("%", "")
    t = t.replace(r"^\circ", "").replace("\u2212", "-")
    t = re.sub(r"\b(FCFA|cm|m)\b", "", t)
    return t.strip()


def frac_tex(t):
    """\\dfrac{a}{b} ou \\frac{a}{b} -> (a)/(b), de l'interieur vers l'exterieur."""
    while True:
        n = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", t)
        if n == t:
            return t
        t = n


def nombre(t):
    t = nettoyer(t)
    m = re.fullmatch(r"(-?)(\d+)\\dfrac\{(\d+)\}\{(\d+)\}", t.replace(" ", ""))
    if m:  # nombre mixte
        v = int(m.group(2)) + Fr(int(m.group(3)), int(m.group(4)))
        return -v if m.group(1) else v
    t = frac_tex(t)
    t = re.sub(r"\d+(\.\d+)?", lambda k: f"Fr('{k.group()}')", t)
    return Fr(eval(t, {"__builtins__": {}}, {"Fr": Fr}))


def standard(t):
    m = re.fullmatch(r"\$?(\d+(?:\.\d+)?)\\times10\^\{(-?\d+)\}\$?", t.strip())
    mant, n = Fr(m.group(1)), int(m.group(2))
    return (mant * Fr(10) ** n, 1 <= mant < 10)


def suite(t):
    return tuple(Fr(x) for x in nettoyer(t).replace(" ", "").split(","))


def paire(t):
    return tuple(nombre(x) for x in re.split(r",|\band\b", nettoyer(t).replace(r"\ ", " ")) if x.strip() and "=" not in x) \
        or tuple(nombre(x.split("=")[1]) for x in nettoyer(t).split(","))


def point(t):
    t = nettoyer(t).replace(" ", "")
    return tuple(nombre(x) for x in t.strip("()").split(","))


def ensemble(t):
    t = nettoyer(t).replace(" ", "").replace("\\{", "{").replace("\\}", "}")
    return frozenset(int(x) for x in t.strip("{}").split(","))


def solutions(t):
    return frozenset(nombre(p.replace("x=", "")) for p in nettoyer(t).split(" or "))


def matrice(t):
    t = t.replace("$", "")
    m = re.match(r"^(.*?)\\begin\{pmatrix\}(.*)\\end\{pmatrix\}$", t.strip())
    pref = m.group(1).strip()
    k = Fr(1) if not pref else nombre(pref)
    lignes = m.group(2).split("\\\\")
    return tuple(tuple(k * nombre(c) for c in lig.split("&")) for lig in lignes)


def expression(t, noms, points):
    """Evalue une expression algebrique (puissances, fractions, produit implicite) en plusieurs points."""
    e = t.replace("$", "").replace("\u2212", "-")
    e = re.sub(r"\^\{(-?\d+)\}", r"**(\1)", e)
    e = re.sub(r"\^(\d)", r"**\1", e)
    e = frac_tex(e)
    for _ in range(2):
        e = re.sub(r"(\d)([a-z(])", r"\1*\2", e)
        e = re.sub(r"([a-z)])(\()", r"\1*\2", e)
        e = re.sub(r"(\))([a-z0-9])", r"\1*\2", e)
        e = re.sub(r"([a-z])(?=[a-z])", r"\1*", e)
    e = re.sub(r"(?<![\w.])(\d+(\.\d+)?)", lambda k: f"Fr('{k.group()}')", e)
    out = []
    for p in points:
        env = {"Fr": Fr, "__builtins__": {}}
        env.update(dict(zip(noms, p)))
        out.append(Fr(eval(e, env)))
    return tuple(out)


# ------------------------------------------------------------------------------------------------ valeurs attendues
def attendus():
    E = {}
    E[1] = ("num", Fr(20) - Fr(3) * 4 / 2)
    E[2] = ("num", math.lcm(12, 18, 30))
    E[3] = ("suite", tuple(sorted((Fr(x) for x in ("0.409", "0.49", "0.4", "0.094")), reverse=True)))
    E[4] = ("num", Fr(9, 4) + Fr(5, 3))
    E[5] = ("std", (Fr("0.00047"), True))
    E[6] = ("num", Fr(round(48639, -3)))
    E[7] = ("num", Fr(240000, 3 + 5 + 4) * 5)
    E[8] = ("num", Fr(9200 - 8000, 8000) * 100)
    E[9] = ("num", 450000 + 450000 * Fr(6, 100) * 3)
    # figure 1 : A seul 9, commun 6, B seul 11, dehors 14 -> A' inter B = B seul
    E[10] = ("num", 11)
    E[11] = ("num", 2 ** 4)
    E[12] = ("num", 28 + 22 - (45 - 8))
    E[13] = ("texte", r"${\sim}q\to{\sim}p$")
    E[14] = ("ens", frozenset(x * x for x in (-1, 0, 1, 2)))
    E[15] = ("num", (lambda f, g: g(f(2)))(lambda x: 2 * x + 3, lambda x: x * x - 1))
    E[16] = ("expr", lambda x: (x + 4) / 3, ("x",), [(Fr(v),) for v in (0, 1, 5, 7)])
    E[17] = ("num", 180 - 118)
    n = next(k for k in range(3, 200) if (k - 2) * 180 == 1440)
    E[18] = ("num", Fr(360, n))
    E[19] = ("num", Fr(9, 6) * 14)
    E[20] = ("num", 12 * 8 - (12 - 7) * 3)
    E[21] = ("num", Fr(22, 7) * 70 ** 2 * 100 / 1000)
    E[22] = ("num", 2 * (9 * 5 + 9 * 4 + 5 * 4))
    E[23] = ("num", Fr(135, 360) * 2 * Fr(22, 7) * 14)
    E[24] = ("num", (180 - 2 * 34) / 2)
    E[25] = ("num", Fr(-7 - 5, 4 - (-2)))
    E[26] = ("paire", (Fr(-3), Fr(4)))  # 2y + 6x = 8 -> y = -3x + 4
    E[27] = ("point", (Fr(1), Fr(1 * 1 - 2 * 1 - 3)))  # sommet : x = (-1 + 3) / 2
    E[28] = ("expr", lambda x: x * x - 5 * x - 24, ("x",), [(Fr(v),) for v in (0, 1, 2, 5, 9)])
    a, b = -3, 2
    E[29] = ("num", a * a - 2 * a * b)
    x30 = Fr(5)
    assert (x30 + 1) / 2 - (x30 - 2) / 3 == 2
    E[30] = ("num", x30)
    E[31] = ("expr", lambda a, b: (3 * a * a * b) ** 3 / (9 * a ** 4 * b), ("a", "b"), [(Fr(2), Fr(3)), (Fr(5), Fr(7)), (Fr(1), Fr(2))])
    E[32] = ("exprS", None, ("u", "v", "a"), [(Fr(1), Fr(5), Fr(2)), (Fr(3), Fr(7), Fr(4)), (Fr(2), Fr(9), Fr(1))])
    E[33] = ("paire", (Fr(4), Fr(2)))
    assert 3 * 4 + 2 * 2 == 16 and 4 - 2 == 2
    E[34] = ("num", 3 + 19 * 4)
    k = Fr(9) * 2 ** 2
    E[35] = ("num", k / 6 ** 2)
    E[36] = ("texte", r"$-2\leq x<3$")
    E[37] = ("sol", frozenset([Fr(3), Fr(-1, 2)]))
    assert 2 * 9 - 15 - 3 == 0 and 2 * Fr(1, 4) + Fr(5, 2) - 3 == 0
    degres = {c: 0 for c in "ABCDE"}
    for u, v in [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("D", "E")]:
        degres[u] += 1
        degres[v] += 1
    E[38] = ("num", sum(1 for d in degres.values() if d % 2))
    E[39] = ("num", Fr(8, 15))
    assert 8 ** 2 + 15 ** 2 == 17 ** 2
    E[40] = ("num", Fr(str(round(6 * math.sin(math.radians(65)), 1))))
    E[41] = ("num", (72 + 180) % 360)
    E[42] = ("num", math.hypot(2 * 3 - 1, 2 * 5 + 2))
    E[43] = ("vec", (Fr(-4 - 2), Fr(5 + 3)))
    A = ((2, -1), (3, 4)); B = ((1, 0), (-2, 5))
    E[44] = ("mat", tuple(tuple(Fr(sum(A[i][k] * B[k][j] for k in range(2))) for j in range(2)) for i in range(2)))
    M = ((4, 3), (2, 2)); det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    E[45] = ("mat", tuple(tuple(Fr(c, det) for c in row) for row in ((M[1][1], -M[0][1]), (-M[1][0], M[0][0]))))
    refl = (3, 2)
    E[46] = ("point", (Fr(refl[0] - 1), Fr(refl[1] + 4)))
    marks = {1: 2, 2: 5, 3: 8, 4: 4, 5: 1}
    E[47] = ("num", Fr(sum(m * f for m, f in marks.items()), sum(marks.values())))
    freq = {0: 4, 1: 10, 2: 8, 3: 9, 4: 4}
    serie = sorted(v for v, f in freq.items() for _ in range(f))
    E[48] = ("num", serie[len(serie) // 2])
    E[49] = ("num", Fr(48, 120) * 75)
    E[50] = ("num", Fr(5, 8) * Fr(4, 7) + Fr(3, 8) * Fr(2, 7))
    return E


def lire(kind, texte, attendu_spec):
    if kind in ("num", "num_degres"):
        return nombre(texte)
    if kind == "std":
        return standard(texte)
    if kind == "suite":
        return suite(texte)
    if kind == "paire":
        return paire(texte)
    if kind == "point":
        return point(texte)
    if kind == "ens":
        return ensemble(texte)
    if kind == "sol":
        return solutions(texte)
    if kind == "mat":
        return matrice(texte)
    if kind == "vec":
        return tuple(row[0] for row in matrice(texte))
    if kind == "texte":
        return texte
    if kind == "expr":
        return expression(texte, attendu_spec[2], attendu_spec[3])
    if kind == "exprS":
        return expression(texte.replace("s=", ""), attendu_spec[2], attendu_spec[3])
    raise ValueError(kind)


def valeur_attendue(spec):
    kind = spec[0]
    if kind == "expr":
        f, noms, pts = spec[1], spec[2], spec[3]
        return tuple(Fr(f(*p)) for p in pts)
    if kind == "exprS":  # s de v^2 = u^2 + 2as, evalue en (u, v, a)
        pts = spec[3]
        return tuple(Fr(p[1] ** 2 - p[0] ** 2, 2 * p[2]) for p in pts)
    v = spec[1]
    if kind == "num":
        return Fr(v) if not isinstance(v, float) else Fr(str(round(v, 6)))
    return v


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    qs = ep["exercices"][0]["questions"]
    E = attendus()
    erreurs = 0
    for q in qs:
        n = int(q["numero"])
        spec = E[n]
        attendu = valeur_attendue(spec)
        lues = {}
        for c in q["choix"]:
            try:
                lues[c["lettre"]] = lire(spec[0], c["texte"], spec)
            except Exception as exc:  # une option illisible est une erreur de verification
                lues[c["lettre"]] = f"ILLISIBLE ({exc})"
        egales = [l for l, v in lues.items() if v == attendu]
        ok = egales == [q["reponse_correcte"]]
        if not ok:
            erreurs += 1
            print(f"ERREUR Q{n}: attendu {attendu!r}, cle {q['reponse_correcte']}, options egales a l'attendu {egales}, lues {lues}")
        elif spec[0] == "texte":
            pass
    print(f"{len(qs)} questions recalculees, {erreurs} ecart(s).")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
