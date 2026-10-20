r"""Recalcule INDEPENDAMMENT chaque reponse chiffree du Paper 2 Additional Mathematics inedit et verifie qu'elle figure dans le corrige ecrit.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_addmaths_p2.py [ep-....json]

Les valeurs sont recalculees ici a partir des DONNEES de l'enonce (force brute, derivation et integration numeriques, parcours de points entiers,
verification des axiomes d'un groupe) ; chaque valeur attendue doit apparaitre dans le corrige de la sous-question. Les tables a completer, les
sommets de la region et la courbe sont relus dans les constantes des figures. Sortie 1 au moindre ecart.
"""
import itertools
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_p2 as F  # noqa: E402
import questions_addmaths_p2_a as QA  # noqa: E402
from questions_addmaths_p2_a import numero_affiche  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-addmaths-p2-1-2026-s1.json")
G = 10.0


def sous_question(ep, ex, num):
    num = numero_affiche(ex, num)[0]
    for e in ep["exercices"]:
        if e["numero_exercice"] == ex:
            for q in e["questions"]:
                if q["numero"] == num:
                    return q
    raise KeyError((ex, num))


def derivee(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def simpson(f, a, b, n=2000):
    h = (b - a) / n
    return (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n))) * h / 3


def table_stem(markdown):
    """Table Markdown 5x5 d'une operation -> dict {(ligne, colonne): valeur ou None}."""
    lignes = [l for l in markdown.splitlines() if l.startswith("| **")]
    t = {}
    for i, l in enumerate(lignes, start=1):
        cases = [c.strip() for c in l.strip("|").split("|")][1:]
        for j, c in enumerate(cases, start=1):
            t[(i, j)] = int(c) if c else None
    return t


def attendues():
    A = []
    # --- Section A
    k = next(k for k in range(-20, 21) if 2 ** 3 + k * 2 ** 2 - 4 * 2 - 12 == 0)
    A.append(("1", "i-a", [f"k={k}"], "valeur de k"))
    f = lambda x: x ** 3 + k * x ** 2 - 4 * x - 12
    racines = sorted(x for x in range(-20, 21) if f(x) == 0)
    assert racines == [-3, -2, 2], racines
    A.append(("1", "i-b", ["(x+3)(x-2)(x+2)", "(x-2)(x+2)(x+3)"], "factorisation"))
    # 2x^2 - 6x + 3 = 0
    somme, produit = Fr(6, 2), Fr(3, 2)
    d = math.sqrt(36 - 24)
    al, be = (6 + d) / 4, (6 - d) / 4
    assert abs(al + be - float(somme)) < 1e-9 and abs(al * be - float(produit)) < 1e-9
    A.append(("1", "ii-a", ["3", "\\dfrac{3}{2}"], "somme et produit"))
    assert all(abs(3 * (1 / r) ** 2 - 6 * (1 / r) + 2) < 1e-9 for r in (al, be))
    A.append(("1", "ii-b", ["3x^{2}-6x+2=0", "\\dfrac{2}{3}"], "equation aux inverses"))
    total = sum(math.comb(7, h) * math.comb(5, 6 - h) for h in range(4, 7))
    brute = sum(1 for c in itertools.combinations(range(12), 6) if sum(1 for p in c if p < 7) >= 4)  # hommes = 0..6, femmes = 7..11
    assert total == brute == 462
    A.append(("2", "i", ["350", "105", "462"], "comites"))
    coeffs = {}
    for r in range(8):  # (2x + 1/x)^7 : terme en x^(7-2r)
        coeffs[7 - 2 * r] = coeffs.get(7 - 2 * r, 0) + math.comb(7, r) * 2 ** (7 - r)
    A.append(("2", "ii", [f"{coeffs[3]}x^{{3}}"], "terme en x^3"))
    t12 = 5 + 11 * 3
    A.append(("3", "a", [str(t12)], "12e rangee"))
    A.append(("3", "b", [str(sum(5 + 3 * i for i in range(12)))], "total des 12 rangees"))
    n = next(n for n in range(1, 100) if 5 + 3 * (n - 1) > 60)
    A.append(("3", "c", [str(n)], "premiere rangee de plus de 60 arbres"))
    # groupe : x*y = xy mod 10 sur {1, 3, 7, 9}
    S = [1, 3, 7, 9]
    op = {(x, y): (x * y) % 10 for x in S for y in S}
    stem = table_stem(QA.TABLE_GROUPE)
    pos = {(i + 1, j + 1): (S[i], S[j]) for i in range(4) for j in range(4)}
    manque = {c for c, val in stem.items() if val is None}
    assert all(stem[c] == op[pos[c]] for c in stem if stem[c] is not None), "valeur donnee fausse dans la table de l'enonce"
    assert len(manque) == 4
    sol = sous_question(JSON, "4", "i-a")["corrige_markdown"]
    sol_table = table_stem("\n".join(l for l in sol.splitlines() if l.startswith("| **")))
    assert all(sol_table[c] == op[pos[c]] for c in sol_table) and len(sol_table) == 16, "la table du corrige differe de la table recalculee"
    A.append(("4", "i-a", ["1*7=7", "3*3=9", "7*9=63", "9*1=9"], "table completee"))
    assert all(op[(a, b)] in S for a in S for b in S)
    assert all(op[(1, a)] == a == op[(a, 1)] for a in S)
    inverses = {a: next(b for b in S if op[(a, b)] == 1) for a in S}
    assert inverses == {1: 1, 3: 7, 7: 3, 9: 9}
    A.append(("4", "i-b", ["1^{-1}=1", "3^{-1}=7", "7^{-1}=3", "9^{-1}=9"], "axiomes du groupe"))
    pts = [(x, y) for x in range(-20, 21) for y in range(-20, 21) if (3 * x + y, 5 * x + 2 * y) == (7, 12)]
    assert pts == [(2, 1)]
    A.append(("4", "ii", ["(2,1)", "\\begin{pmatrix}2\\\\1\\end{pmatrix}"], "antecedent"))
    # inequations
    A.append(("5", "a", ["4x+3y\\leq44"], "inequation de cout"))
    x_int = Fr(44, 4 + 3 * Fr(1, 2))  # intersection de x = 2y et 4x + 3y = 44 : y = 4, x = 8
    assert x_int == 8
    sommets = sorted([(0, 0), (11, 0), (8, 4)])
    assert sorted(F.SOMMETS_REGION) == sommets, "sommets de la figure"
    assert 4 * 11 + 3 * 0 == 44 and 4 * 8 + 3 * 4 == 44 and 8 == 2 * 4
    A.append(("5", "c", ["(11,0)", "(5,8)", "(8,4)"], "region"))
    meilleur = max(((x, y) for x in range(0, 13) for y in range(0, 9) if 4 * x + 3 * y <= 44 and x >= 2 * y), key=lambda p: p[0] + p[1])
    assert meilleur == (8, 4)
    A.append(("5", "d", [str(meilleur[0] + meilleur[1])], "total maximal de sacs"))
    # trigonometrie
    assert all(abs(math.cos(a) ** 4 - math.sin(a) ** 4 - math.cos(2 * a)) < 1e-12 for a in (0.2, 0.9, 1.7, 2.6))
    fx = F.FONCTION_TRIG
    assert max(fx(i * math.pi / 5000) for i in range(0, 5001)) == 3.0 and abs(fx(math.pi / 2) + 3) < 1e-9
    assert all(abs(fx(x + math.pi) - fx(x)) < 1e-9 for x in (0.1, 0.7, 1.9)) and abs(fx(0.3 + math.pi / 2) - fx(0.3)) > 1e-3  # periode pi
    A.append(("6", "ii-a", ["3", "\\pi"], "amplitude et periode"))
    assert abs(fx(math.pi / 4)) < 1e-9 and abs(fx(3 * math.pi / 4)) < 1e-9
    A.append(("6", "ii-b", ["\\dfrac{\\pi}{4}", "\\dfrac{3\\pi}{4}", "(0,3)"], "points remarquables"))
    n_sol = sum(1 for i in range(0, 20000) if (fx(i * math.pi / 20000) - 2) * (fx((i + 1) * math.pi / 20000) - 2) < 0)
    assert n_sol == 2
    A.append(("6", "ii-c", ["2"], "nombre de solutions"))
    # vecteurs : l1 = (2,1) + s(1,3) ; l2 = (-1,3) + t(5,4)
    sol_st = [(s, t) for s in range(-10, 11) for t in range(-10, 11) if (2 + s, 1 + 3 * s) == (-1 + 5 * t, 3 + 4 * t)]
    assert sol_st == [(2, 1)]
    A.append(("7", "a", ["t=1", "s=2"], "parametres"))
    A.append(("7", "b", ["4\\mathbf{i}+7\\mathbf{j}"], "point d'intersection"))
    cos = (1 * 5 + 3 * 4) / (math.hypot(1, 3) * math.hypot(5, 4))
    assert abs(cos - 17 / math.sqrt(410)) < 1e-12 and round(cos, 2) == 0.84
    A.append(("7", "c", ["\\dfrac{17}{\\sqrt{410}}", "0.84"], "cosinus de l'angle"))
    # calcul differentiel et integral
    fq = lambda x: x ** 2 * math.sqrt(1 + 2 * x)
    assert all(abs(derivee(fq, x) - (5 * x ** 2 + 2 * x) / math.sqrt(1 + 2 * x)) < 1e-5 for x in (0.5, 1.0, 2.5, 4.0))
    A.append(("8", "i", ["\\dfrac{5x^{2}+2x}{\\sqrt{1+2x}}"], "derivee d'un produit"))
    integrale = simpson(lambda x: 3 * math.sqrt(x) + 2 / x ** 2, 1, 4)
    assert abs(integrale - 15.5) < 1e-6
    A.append(("8", "ii", ["\\dfrac{31}{2}"], "integrale definie"))
    # --- Section B : mecanique
    vP = lambda t: (4 * t, 6.0)
    vQ = lambda t: (1.0, -2 * t)
    assert vP(2) == (8.0, 6.0) and abs(math.hypot(*vP(2)) - 10) < 1e-12
    # controle par derivation numerique des positions
    rP = lambda t: (2 * t ** 2, 6 * t)
    rQ = lambda t: (t + 4, -t ** 2)
    assert all(abs(derivee(lambda t, i=i: rP(t)[i], 2) - vP(2)[i]) < 1e-5 for i in (0, 1))
    assert all(abs(derivee(lambda t, i=i: rQ(t)[i], 2) - vQ(2)[i]) < 1e-5 for i in (0, 1))
    A.append(("9", "i-a", ["8\\mathbf{i}+6\\mathbf{j}", "10"], "vitesse et module"))
    rel = (vP(2)[0] - vQ(2)[0], vP(2)[1] - vQ(2)[1])
    assert rel == (7.0, 10.0)
    A.append(("9", "i-b", ["7\\mathbf{i}+10\\mathbf{j}"], "vitesse relative"))
    vB = (3 * 8 + 5 * 2 - 3 * 3) / 5
    assert vB == 5.0
    A.append(("9", "ii-a", ["v=5", "34"], "vitesse apres le choc"))
    ec_avant = 0.5 * 3 * 8 ** 2 + 0.5 * 5 * 2 ** 2
    ec_apres = 0.5 * 3 * 3 ** 2 + 0.5 * 5 * vB ** 2
    assert (ec_avant, ec_apres, ec_avant - ec_apres) == (106.0, 76.0, 30.0)
    A.append(("9", "ii-b", ["106", "76", "30"], "perte d'energie cinetique"))
    m1, m2 = F.ATWOOD["m1"], F.ATWOOD["m2"]
    a = (m2 - m1) * G / (m1 + m2)
    T = m1 * (G + a)
    assert a == 2.5 and T == 37.5 and abs(m2 * (G - a) - T) < 1e-12
    A.append(("9", "iii-b", ["20=8a", "2.5"], "acceleration"))
    A.append(("9", "iii-c", ["37.5"], "tension"))
    # forces
    x, y = 5, -4
    assert (3 + x - 6 + 2, 2 - 4 + y + 5) == (4, -1)
    A.append(("10", "i-a", ["x=5", "y=-4"], "composantes inconnues"))
    A.append(("10", "i-b", ["-4\\mathbf{i}+\\mathbf{j}"], "cinquieme force"))
    norme = math.hypot(-4, 1)
    angle = 180 - math.degrees(math.atan2(1, 4))
    assert round(norme, 1) == 4.1 and round(angle, 1) == 166.0 and round(math.degrees(math.atan2(1, 4)), 1) == 14.0
    A.append(("10", "i-c", ["4.1", "166.0", "14.0"], "module et direction"))
    F_trav = 25 * G * math.sin(math.radians(30))
    assert abs(F_trav - 125) < 1e-9 and abs(F_trav * 12 - 1500) < 1e-8
    A.append(("10", "ii", ["125", "1500"], "travail"))
    force = 24000 / 20
    assert force == 1200.0
    A.append(("10", "iii-a", ["1200"], "force motrice"))
    resistance = force - 800 * G * (1 / 10)
    assert resistance == 400.0
    A.append(("10", "iii-b", ["400", "800"], "resistance"))
    assert resistance * 20 == 8000.0
    A.append(("10", "iii-c", ["8000"], "puissance sur route plane"))
    return A


JSON = None


def verifier(ep):
    global JSON
    JSON = ep
    erreurs = []
    n = 0
    for ex, num, textes, desc in attendues():
        q = sous_question(ep, ex, num)
        corr = re.sub(r"\s+", "", q["corrige_markdown"].replace("\\,", ""))
        n += 1
        if not any(re.sub(r"\s+", "", t) in corr for t in textes) if desc in ("factorisation",) else any(re.sub(r"\s+", "", t) not in corr for t in textes):
            manquantes = [t for t in textes if re.sub(r"\s+", "", t) not in corr]
            erreurs.append(f"{ex}{num} ({desc}): valeur(s) recalculee(s) absente(s) du corrige : {manquantes}")
    return erreurs, n


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    nq = sum(len(e["questions"]) for e in ep["exercices"])
    total = sum(q["points"] for e in ep["exercices"] for q in e["questions"])
    print(f"{n} sous-questions recalculees sur {nq}, {len(erreurs)} ecart(s) ; total des points {total}.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
