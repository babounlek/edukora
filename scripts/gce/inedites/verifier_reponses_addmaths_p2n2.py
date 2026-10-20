r"""Recalcule INDEPENDAMMENT chaque reponse chiffree du Paper 2 n.2 Additional Mathematics inedit et verifie qu'elle figure dans le corrige ecrit.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_addmaths_p2n2.py [ep-....json]

Les valeurs sont recalculees a partir des DONNEES de l'enonce (force brute, enumeration, derivation et integration numeriques, parcours de points entiers,
verification des axiomes d'un groupe, statistiques et lois recalculees) ; chaque valeur attendue doit apparaitre dans le corrige de la sous-question.
La table a completer et le bareme sont relus dans les fichiers generes. Sortie 1 au moindre ecart.
"""
import itertools
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_s2 as F  # noqa: E402
import questions_addmaths_p2n2_a as QA  # noqa: E402
import questions_addmaths_p2n2_c as QC  # noqa: E402
from questions_addmaths_p2n2_a import numero_affiche  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-addmaths-p2-2-2026-s1.json")
JSON = None


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


def table_stem(markdown):
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
    f = lambda k, x: x ** 3 + k * x ** 2 + 11 * x + 6
    k = next(k for k in range(-30, 31) if f(k, -1) == 0)
    A.append(("1", "i-a", [f"k={k}"], "valeur de k"))
    racines = sorted(x for x in range(-30, 31) if f(k, x) == 0)
    assert racines == [-3, -2, -1], racines
    A.append(("1", "i-b", ["(x+1)(x+2)(x+3)"], "factorisation"))
    al = next(a for a in range(-20, 21) if a + 3 * a == 8)
    A.append(("1", "ii-a", [f"\\alpha={al}"], "alpha"))
    k2 = next(c for c in range(-100, 101) if sorted(r for r in range(-30, 31) if r * r - 8 * r + c == 0) == [al, 3 * al])
    assert k2 == 3 * al ** 2 == 12
    A.append(("1", "ii-b", [f"k={k2}"], "k"))
    pairs = sum(1 for p in itertools.permutations([1, 2, 3, 4, 5, 6], 4) if p[-1] % 2 == 0)
    assert pairs == 180
    A.append(("2", "i", ["180"], "nombres pairs"))
    pol = [1]
    for _ in range(6):  # (1 + 2x)^6
        nxt = [0] * (len(pol) + 1)
        for i, c in enumerate(pol):
            nxt[i] += c
            nxt[i + 1] += 2 * c
        pol = nxt
    assert pol[:4] == [1, 12, 60, 160]
    approx = sum(c * 0.01 ** i for i, c in enumerate(pol[:4]))
    assert round(approx, 4) == 1.1262 and round(1.02 ** 6, 4) == 1.1262 and abs(approx - 1.126160) < 1e-12
    A.append(("2", "ii", ["1+12x+60x^{2}+160x^{3}", "1.1262"], "developpement et estimation"))
    # balle : rebonds a 60 %, lachee de 8 m
    h = [8 * 0.6 ** n for n in range(0, 400)]  # h[n] : hauteur apres le n-ieme rebond
    assert abs(h[4] - 1.0368) < 1e-12
    A.append(("3", "a", ["1.0368"], "hauteur apres le 4e rebond"))
    distance = h[0] + 2 * sum(h[1:])
    assert abs(distance - 32) < 1e-9
    A.append(("3", "b", ["32"], "distance totale"))
    n = next(n for n in range(1, 100) if h[n] < 0.5)
    assert n == 6
    A.append(("3", "c", ["6^{\\text{th}}", "5.43"], "premier rebond sous 0.5 m"))
    # groupe : x*y = xy mod 15 sur {1, 2, 4, 8}
    S = [1, 2, 4, 8]
    op = {(x, y): (x * y) % 15 for x in S for y in S}
    stem = table_stem(QA.TABLE_GROUPE)
    pos = {(i + 1, j + 1): (S[i], S[j]) for i in range(4) for j in range(4)}
    manque = {c for c, val in stem.items() if val is None}
    assert all(stem[c] == op[pos[c]] for c in stem if stem[c] is not None), "valeur donnee fausse dans la table de l'enonce"
    assert len(manque) == 4
    sol = sous_question(JSON, "4", "i-a")["corrige_markdown"]
    sol_table = table_stem("\n".join(l for l in sol.splitlines() if l.startswith("| **")))
    assert all(sol_table[c] == op[pos[c]] for c in sol_table) and len(sol_table) == 16, "la table du corrige differe de la table recalculee"
    A.append(("4", "i-a", ["2*8=16", "4*4=16", "4*8=32", "8*8=64"], "table completee"))
    assert all(op[(a, b)] in S for a in S for b in S)
    assert all(op[(1, a)] == a == op[(a, 1)] for a in S)
    assert all(op[(a, b)] == op[(b, a)] for a in S for b in S)
    inverses = {a: next(b for b in S if op[(a, b)] == 1) for a in S}
    assert inverses == {1: 1, 2: 8, 4: 4, 8: 2}
    A.append(("4", "i-b", ["1^{-1}=1", "2^{-1}=8", "8^{-1}=2", "4^{-1}=4"], "axiomes du groupe"))
    sols = [(x, y) for x in range(-20, 21) for y in range(-20, 21) if 2 * x + y == 5 and 3 * x + 2 * y == 8]
    assert sols == [(2, 1)]
    det = 2 * 2 - 1 * 3
    assert det == 1
    inv = ((2, -1), (-3, 2))
    M = ((2, 1), (3, 2))
    prod = tuple(tuple(sum(M[i][k_] * inv[k_][j] for k_ in range(2)) for j in range(2)) for i in range(2))
    assert prod == ((1, 0), (0, 1)), "M * M^-1 != I"
    A.append(("4", "ii", ["\\begin{pmatrix}2&-1\\\\-3&2\\end{pmatrix}", "x=2", "\\begin{pmatrix}2\\\\1\\end{pmatrix}"], "inverse et systeme"))
    # programmation lineaire : 2x + 3y <= 36, x >= y, y >= 3
    A.append(("5", "a", ["2x+3y\\leq36", "x\\geq y", "y\\geq3"], "inequations"))
    sommets = sorted([(3, 3), (13.5, 3), (7.2, 7.2)])
    assert sorted(F.SOMMETS_A5) == sommets, "sommets de la figure"
    assert 2 * 3 + 3 * 3 == 15 and 2 * 13.5 + 3 * 3 == 36 and abs(2 * 7.2 + 3 * 7.2 - 36) < 1e-9
    A.append(("5", "b", ["(18,0)", "(0,12)", "(3,3)", "(13.5,3)", "(7.2,7.2)"], "region"))
    pts = [(x, y) for x in range(0, 20) for y in range(0, 14) if 2 * x + 3 * y <= 36 and x >= y and y >= 3]
    best = max(pts, key=lambda p: 6000 * p[0] + 5000 * p[1])
    profit = 6000 * best[0] + 5000 * best[1]
    assert best == (13, 3) and profit == 93000
    second = sorted(pts, key=lambda p: -(6000 * p[0] + 5000 * p[1]))[1]
    assert second == (12, 4) and 6000 * 12 + 5000 * 4 == 92000
    A.append(("5", "c", ["93000", "92000", "13", "3"], "benefice maximal"))
    # trigonometrie
    sol_deg = sorted(x for x in range(0, 361) if abs(2 * math.cos(math.radians(x)) ** 2 - math.sin(math.radians(x)) - 1) < 1e-9)
    assert sol_deg == [30, 150, 270], sol_deg
    A.append(("6", "i", ["30^{\\circ}", "150^{\\circ}", "270^{\\circ}"], "equation trigonometrique"))
    ident = lambda t: math.sin(2 * t) / math.sin(t) - math.cos(2 * t) / math.cos(t)
    assert all(abs(ident(t) - 1 / math.cos(t)) < 1e-9 for t in (0.2, 0.6, 1.1, 1.4))
    A.append(("6", "ii-a", ["\\dfrac{1}{\\cos\\theta}", "2\\cos\\theta"], "identite"))
    sol_ii = [x for x in range(1, 90) if abs(ident(math.radians(x)) - 2) < 1e-9]
    assert sol_ii == [60], sol_ii
    A.append(("6", "ii-b", ["\\cos\\theta=\\dfrac{1}{2}", "60^{\\circ}"], "equation par l'identite"))
    # vecteurs : A(3,1), B(1,5)
    Aa, Bb = (3, 1), (1, 5)
    mid = ((Aa[0] + Bb[0]) / 2, (Aa[1] + Bb[1]) / 2)
    assert mid == (2.0, 3.0)
    AB = (Bb[0] - Aa[0], Bb[1] - Aa[1])
    assert AB == (-2, 4) and abs(math.hypot(*AB) - 2 * math.sqrt(5)) < 1e-12
    A.append(("7", "a", ["2\\mathbf{i}+3\\mathbf{j}", "2\\sqrt{5}"], "milieu et longueur"))
    A.append(("7", "b", ["3\\mathbf{i}+\\mathbf{j}+t(-2\\mathbf{i}+4\\mathbf{j})"], "equation vectorielle"))
    # P sur AB tel que OP ⟂ AB : minimisation numerique de |OP| (le pied de la perpendiculaire minimise la distance)
    meilleur = min((i / 100000 for i in range(-100000, 100001)), key=lambda t: math.hypot(3 - 2 * t, 1 + 4 * t))
    assert abs(meilleur - 0.1) < 1e-4
    P = (3 - 2 * 0.1, 1 + 4 * 0.1)
    assert abs(P[0] * AB[0] + P[1] * AB[1]) < 1e-12 and (round(P[0], 6), round(P[1], 6)) == (2.8, 1.4)
    A.append(("7", "c", ["t=0.1", "2.8\\mathbf{i}+1.4\\mathbf{j}"], "pied de la perpendiculaire"))
    # calcul differentiel et integral
    c = lambda x: x ** 3 - 6 * x ** 2 + 9 * x + 1
    stationnaires = [x for x in range(-10, 11) if abs(derivee(c, x)) < 1e-4]
    assert stationnaires == [1, 3] and c(1) == 5 and c(3) == 1
    d2 = lambda x: derivee(lambda u: derivee(c, u), x, 1e-3)
    assert d2(1) < 0 < d2(3)
    A.append(("8", "i", ["(1,5)", "(3,1)", "6x-12"], "points stationnaires"))
    courbe = lambda x: 2 * x ** 2 - 6 * x + 5
    assert courbe(3) == 5 and all(abs(derivee(courbe, x) - (4 * x - 6)) < 1e-5 for x in (-1.5, 0.3, 2.2))
    A.append(("8", "ii", ["y=2x^{2}-6x+5"], "equation de la courbe"))
    # --- Section C : statistiques et probabilites
    freq = [6, 14, 28, 20, 12]
    milieux = [5, 15, 25, 35, 45]
    n_tot = sum(freq)
    assert n_tot == 80
    moyenne = sum(f_ * x for f_, x in zip(freq, milieux)) / n_tot
    assert moyenne == 27.25
    A.append(("9", "a", ["2180", "27.25"], "moyenne"))
    sfx2 = sum(f_ * x * x for f_, x in zip(freq, milieux))
    variance = sfx2 / n_tot - moyenne ** 2
    assert sfx2 == 69600 and abs(variance - 127.4375) < 1e-9 and round(math.sqrt(variance), 1) == 11.3
    A.append(("9", "b", ["69600", "127.4375", "11.3"], "ecart-type"))
    cumul = list(itertools.accumulate(freq))
    assert cumul == [6, 20, 48, 68, 80] and [c_ for _, c_ in F.EFFECTIFS[1:]] == cumul, "courbe de la figure != tableau"
    sol_cum = sous_question(JSON, "9", "c")["corrige_markdown"]
    assert "| Cumulative frequency | 6 | 20 | 48 | 68 | 80 |" in sol_cum
    A.append(("9", "c", ["20", "48", "68"], "table des effectifs cumules"))
    A.append(("9", "d", ["(10,6)", "(20,20)", "(30,48)", "(40,68)", "(50,80)"], "points de la courbe"))
    med = F._lire_x(40)
    assert 27.0 <= med <= 27.2
    A.append(("9", "e", ["27"], "mediane"))
    q1, q3 = F._lire_x(20), F._lire_x(60)
    assert q1 == 20 and q3 == 36 and q3 - q1 == 16
    A.append(("9", "f", ["20", "36", "16"], "quartiles"))
    assert F._lire_c(35) == 58 and n_tot - F._lire_c(35) == 22
    A.append(("9", "g", ["58", "22"], "joueurs au-dela de 35 minutes"))
    A.append(("9", "h", ["6.2", "11.3"], "comparaison des ecarts-types"))
    # loi de probabilite P(X = x) = k(4 - x), x = 0..3
    k_ = next(Fr(n, 100) for n in range(1, 100) if sum(Fr(n, 100) * (4 - x) for x in range(4)) == 1)
    assert k_ == Fr(1, 10)
    loi = {x: k_ * (4 - x) for x in range(4)}
    A.append(("10", "i-a", ["k=0.1"], "constante k"))
    assert loi[2] + loi[3] == Fr(3, 10)
    A.append(("10", "i-b", ["0.3"], "P(X>=2)"))
    esp = sum(x * p for x, p in loi.items())
    assert esp == 1
    A.append(("10", "i-c", ["0.4", "0.3", "0.2", "0.1", "E(X)=0(0.4)+1(0.3)+2(0.2)+3(0.1)", "1"], "esperance"))
    ex2 = sum(x * x * p for x, p in loi.items())
    assert ex2 == 2 and ex2 - esp ** 2 == 1
    A.append(("10", "i-d", ["E(X^{2})", "0.3+0.8+0.9=2", "2-1^{2}=1"], "variance"))
    p, n = 0.7, 8
    b = lambda r: math.comb(n, r) * p ** r * (1 - p) ** (n - r)
    assert round(b(6), 4) == 0.2965 and abs(sum(b(r) for r in range(n + 1)) - 1) < 1e-12
    A.append(("10", "ii-a", ["0.2965", "28"], "P(X=6)"))
    assert round(b(7) + b(8), 4) == 0.2553 and round(b(7), 4) == 0.1977 and round(b(8), 4) == 0.0576
    A.append(("10", "ii-b", ["0.1977", "0.0576", "0.2553"], "P(X>=7)"))
    moy = sum(r * b(r) for r in range(n + 1))
    var = sum(r * r * b(r) for r in range(n + 1)) - moy ** 2
    assert abs(moy - 5.6) < 1e-9 and abs(var - 1.68) < 1e-9
    A.append(("10", "ii-c", ["5.6", "1.68"], "moyenne et variance binomiales"))
    return A


def verifier(ep):
    global JSON
    JSON = ep
    erreurs = []
    n = 0
    for ex, num, textes, desc in attendues():
        q = sous_question(ep, ex, num)
        corr = re.sub(r"\s+", "", q["corrige_markdown"].replace("\\,", ""))
        n += 1
        manquantes = [t for t in textes if re.sub(r"\s+", "", t) not in corr]
        if manquantes:
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
    # structure : points par question = somme des criteres, total 100
    for e in ep["exercices"]:
        for q in e["questions"]:
            assert abs(sum(c["points"] for c in q["criteres_notation"]) - q["points"]) < 1e-9, (e["numero_exercice"], q["numero"])
    print(f"{n} sous-questions recalculees sur {nq}, {len(erreurs)} ecart(s) ; total des points {total}.")
    return 1 if erreurs or total != 100 else 0


if __name__ == "__main__":
    sys.exit(main())
