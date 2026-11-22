r"""Recalcul INDEPENDANT (numerique, sans sympy) des 50 reponses de l'epreuve inedite GCE A Level Pure Mathematics Paper 1 n.1 (options Mechanics et Statistics).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_pm_p1.py

Pour chaque question une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (bissection, essai exhaustif, table de verite, integration
numerique, derivation numerique, iteration de Runge-Kutta, comptage direct) et la compare a la valeur de controle `val` de la question ; certains distracteurs
sont aussi evalues pour prouver qu'ils sont faux. Les DEUX JSON generes sont relus (lettre `reponse_correcte`, `Answer: X.` du corrige, une seule option egale a
la cle, equilibre des cles, contenu identique d'une option a l'autre). Sortie 0 s'il n'y a aucun ecart.
"""
import cmath
import itertools
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_pm_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DOSSIER = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
EPS = [os.path.join(DOSSIER, "ep-cm-gce-al-pmmechanics-p1-1-2026-s1.json"), os.path.join(DOSSIER, "ep-cm-gce-al-pmstatistics-p1-1-2026-s1.json")]
ecarts = []
nverif = 0


def proche(a, b, tol):
    if isinstance(a, (tuple, list)) or isinstance(b, (tuple, list)):
        return len(a) == len(b) and all(proche(x, y, tol) for x, y in zip(a, b))
    return abs(a - b) <= tol


def ok(num, calcule, annonce, tol=1e-6):
    global nverif
    nverif += 1
    if not proche(calcule, annonce, tol):
        ecarts.append(f"Q{num}: recalcule {calcule}, annonce {annonce}")


def differe(num, a, b, tol=1e-6):
    """Un distracteur doit donner une valeur DIFFERENTE de la bonne reponse."""
    global nverif
    nverif += 1
    if proche(a, b, tol):
        ecarts.append(f"Q{num}: un distracteur vaut la bonne reponse ({a})")


def integrer(f, a, b, n=200000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


def derivee(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def bissection(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        fm = f(m)
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def racines_par_signe(f, a, b, pas):
    """Racines simples de f sur [a, b] par changements de signe puis bissection."""
    res = []
    x = a
    while x < b:
        if (f(x) < 0) != (f(x + pas) < 0):
            res.append(bissection(f, x, x + pas))
        x += pas
    return res


def tt(f):
    return tuple(int(f(p, q)) for p, q in itertools.product((True, False), repeat=2))


C = {}  # numero -> valeur recalculee

# 1 : composition evaluee en x = 2 et identite testee en plusieurs points
f1 = lambda x: 3 * x - 2
g1 = lambda x: x * x + 1
C[1] = f1(g1(2))
ok(1, max(abs(f1(g1(x)) - (3 * x * x + 1)) for x in (-2.5, 0.3, 1.7, 4)), 0)
differe(1, g1(f1(2)), C[1]); differe(1, f1(2) * g1(2), C[1]); differe(1, 3 * 4 - 2, C[1])
# 2 : on resout f(t) = 5 par bissection (f decroit sur t > 1)
C[2] = bissection(lambda t: (2 * t + 3) / (t - 1) - 5, 1.0001, 100)
ok(2, max(abs((2 * ((x + 3) / (x - 2)) + 3) / (((x + 3) / (x - 2)) - 1) - x) for x in (5, 7, -4, 0.5)), 0, 1e-9)
# 3 : racine de log2 x + log2 (x - 2) - 3 sur ]2, 50[ (croissante)
C[3] = bissection(lambda x: math.log2(x) + math.log2(x - 2) - 3, 2.0000001, 50)
# 4 : pente et ordonnee a l'origine de l'asymptote par deux grandes valeurs de x
g4 = lambda x: (x * x + x - 3) / (x - 1)
sl = (g4(2e6) - g4(1e6)) / 1e6
C[4] = (sl, g4(1e6) - sl * 1e6)
# 5 : on teste chaque candidat (2, -3, -2) : l'expression explose-t-elle ?
g5 = lambda x: (x * x - 4) / ((x - 2) * (x + 3))
C[5] = sum(1 for x0 in (2, -3, -2) if max(abs(g5(x0 + 1e-7)), abs(g5(x0 - 1e-7))) > 1e4)
# 6 : k tel que p(-2) = 0 (bissection) et reste de Horner pour (x + 2)
p6 = lambda x, k: 2 * x ** 3 + x ** 2 + k * x - 6
C[6] = bissection(lambda k: p6(-2, k), -100, 100)
reste = 0
for coef in (2, 1, round(C[6]), -6):
    reste = reste * (-2) + coef
ok(6, reste, 0)
differe(6, p6(-2, 9), 0.0); differe(6, p6(-2, -7), 0.0); differe(6, p6(-2, -11), 0.0)
# 7 : verites de |x + 2| < 2 |x - 1| en 8 points
P7 = [-6, -1, -0.01, 0.01, 2, 3.99, 4.01, 7]
C[7] = tuple(int(abs(x + 2) < 2 * abs(x - 1)) for x in P7)
# 8
P8 = [-3, -1.5, -0.5, 0, 3.9, 4, 4.1, 10]
C[8] = tuple(int((2 * x - 3) / (x + 1) <= 1 + 1e-12) for x in P8)
# 9
g9 = lambda x: (x ** 3 - 8) / (x * x - 4)
C[9] = (g9(2 + 1e-6) + g9(2 - 1e-6)) / 2
# 10
C[10] = (1 - math.cos(2e-3)) / 1e-6
# 11
C[11] = math.sqrt(1e6 ** 2 + 4e6) - 1e6
# 12 : table de verite de la negation de p => q
C[12] = tt(lambda p, q: not ((not p) or q))
assert C[12] == tt(lambda p, q: p and not q)
for autre in (lambda p, q: (not p) and q, lambda p, q: (not (not p)) or (not q), lambda p, q: p or (not q)):
    differe(12, tt(autre), C[12])
# 13
C[13] = sum(1 for p, q, r in itertools.product((True, False), repeat=3) if (not p) or (q and r))
# 14 : proprietes de la relation par essai exhaustif
S = (1, 2, 3)
R = {(1, 1), (2, 2), (3, 3), (1, 2), (2, 1), (2, 3), (3, 2)}
refl = all((a, a) in R for a in S)
sym = all((b, a) in R for (a, b) in R)
trans = all((a, d) in R for (a, b) in R for (c, d) in R if b == c)
C[14] = (int(refl), int(sym), int(trans))
# 15
n15, a15 = (2, -1, 3), (1, 2, -1)
C[15] = sum(u * v for u, v in zip(n15, a15))
ok(15, sum(u * v for u, v in zip(n15, (0, 0, -1))), -3)  # un autre point de la meme equation
ok(15, sum(u * (x - y) for u, x, y in zip(n15, (0, 0, -1), a15)), 0)
# 16 : direction (2, p, 1) perpendiculaire a la normale (3, -2, 1)
C[16] = bissection(lambda p: 2 * 3 + p * (-2) + 1 * 1, -50, 50)
# 17 : racines de det(k) = k (k + 1) - 6
dk = lambda k: k * (k + 1) - 3 * 2
rs = sorted(racines_par_signe(dk, -9.37, 9.41, 0.0137), reverse=True)
C[17] = tuple(rs)
# 18 : l'expression et son developpement en trois points
P18 = (3, 0.5, -4)
C[18] = tuple((x * x + 1) / (x * x - 1) for x in P18)
ok(18, tuple(1 + 1 / (x - 1) - 1 / (x + 1) for x in P18), C[18], 1e-12)
differe(18, 1 + 1 / (3 - 1) + 1 / (3 + 1), C[18][0]); differe(18, 1 / (3 - 1) - 1 / (3 + 1), C[18][0]); differe(18, 1 + 2 / (3 - 1) - 2 / (3 + 1), C[18][0])
# 19 : C = limite de (x - 2)^2 f(x) quand x tend vers 2
f19 = lambda x: (4 * x - 1) / ((x + 1) * (x - 2) ** 2)
C[19] = f19(2 + 1e-6) * 1e-12
# 20 : racines numeriques de x^2 - 6x + 4
r20 = racines_par_signe(lambda x: x * x - 6 * x + 4, -0.3, 6.1, 0.0137)
C[20] = sum(r * r for r in r20)
# 21
r21 = sorted(racines_par_signe(lambda x: 9 ** x - 4 * 3 ** x + 3, -5.01, 5.0, 0.0137))
C[21] = tuple(r21)
# 22
C[22] = bissection(lambda x: 2 ** (x + 1) * 4 ** x - 32, -10, 10)
# 23 : Runge-Kutta d'ordre 4 de y' = x / y, y(0) = 2, jusqu'a x = 1.5
def rk4(f, x, y, xf, n):
    h = (xf - x) / n
    for _ in range(n):
        k1 = f(x, y); k2 = f(x + h / 2, y + h * k1 / 2); k3 = f(x + h / 2, y + h * k2 / 2); k4 = f(x + h, y + h * k3)
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x += h
    return y


C[23] = rk4(lambda x, y: x / y, 0.0, 2.0, 1.5, 3000)
differe(23, math.sqrt(1.5 ** 2 + 2), C[23]); differe(23, 1.5 ** 2 / 2 + 2, C[23]); differe(23, math.sqrt(2 * 1.5 ** 2 + 4), C[23])
# 24 : residu de l'equation x y' - 3 y - x^4 pour y = x^4 + C x^3
def residu24(y, x):
    return x * derivee(y, x) - 3 * y(x) - x ** 4


C[24] = tuple(round(residu24(lambda t: t ** 4 + 0.7 * t ** 3, x), 6) for x in (1.3, 2.1, 0.7))
differe(24, tuple(round(residu24(lambda t: t ** 4 / 7 + 0.7 / t ** 3, x), 6) for x in (1.3, 2.1, 0.7)), (0, 0, 0))
differe(24, tuple(round(residu24(lambda t: t ** 3 + 0.7 * t ** 4, x), 6) for x in (1.3, 2.1, 0.7)), (0, 0, 0))
# 25 : distance de l'origine a la droite 3x + 4y = 25 et passage par (3, 4)
C[25] = (25 / math.hypot(3, 4), 3 * 3 + 4 * 4 - 25)
# 26 : centre = milieu, puis carres des distances du centre a A et B
cx, cy = (1 + 7) / 2, (2 + 10) / 2
ok(26, (cx, cy), (4, 6))
C[26] = ((1 - cx) ** 2 + (2 - cy) ** 2, (7 - cx) ** 2 + (10 - cy) ** 2)
# 27 : produit de polynomes (3 - 2x)^6, coefficient de x^3
poly = [1]
for _ in range(6):
    nouveau = [0] * (len(poly) + 1)
    for i, c in enumerate(poly):
        nouveau[i] += 3 * c
        nouveau[i + 1] += -2 * c
    poly = nouveau
C[27] = poly[3]
# 28
C[28] = math.cos(2 * math.asin(5 / 13))
# 29 : angles entiers en degres qui annulent 2 sin^2 x + sin x - 1 (toutes les solutions sont entieres)
C[29] = sum(1 for d in range(0, 361) if abs(2 * math.sin(math.radians(d)) ** 2 + math.sin(math.radians(d)) - 1) < 1e-9)
# 30 : maximum sur une grille fine
C[30] = max(5 * math.cos(t / 1e4) - 12 * math.sin(t / 1e4) + 3 for t in range(0, 62832))
# 31
C[31] = (2 + 1j) / (1 - 3j)
# 32
C[32] = cmath.phase(complex(-math.sqrt(3), 1))
# 33 : produits successifs
z33 = 1 + 1j * math.sqrt(3)
w33 = 1
for _ in range(6):
    w33 *= z33
C[33] = w33
# 34 : recherche exhaustive de (a, d) entiers
sol34 = [(a, d) for a in range(-50, 51) for d in range(-20, 21) if a + 4 * d == 17 and a + 11 * d == 38]
a34, d34 = sol34[0]
C[34] = sum(a34 + k * d34 for k in range(20))
# 35 : on cherche r dont la somme partielle de 12 r^k vaut 16
C[35] = min((abs(sum(12 * (r / 100) ** k for k in range(3000)) - 16), r / 100) for r in range(-99, 100))[1]
# 36
C[36] = integrer(lambda x: abs(2 * x - x * x), 0, 2)
# 37
C[37] = integrer(lambda x: x * math.exp(2 * x), 0, 1)
# 38
C[38] = derivee(lambda x: x * math.exp(-2 * x), 1.0)
# 39 : maximum local sur une grille
g39 = lambda x: x ** 3 - 6 * x ** 2 + 9 * x + 1
xs = [-2 + 0.01 * i for i in range(701)]
C[39] = [round(x, 2) for i, x in enumerate(xs[1:-1], 1) if g39(x) > g39(xs[i - 1]) and g39(x) > g39(xs[i + 1])][0]
# 40 : produit de matrices
def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


A40 = [[1, 2], [0, 1]]
M = mul(mul(A40, A40), A40)
C[40] = (M[0][0], M[0][1], M[1][0], M[1][1])
# 41 : avec des matrices 2 x 2 particulieres
def inv(M2):
    d = M2[0][0] * M2[1][1] - M2[0][1] * M2[1][0]
    return [[M2[1][1] / d, -M2[0][1] / d], [-M2[1][0] / d, M2[0][0] / d]]


A41, B41 = [[2, 1], [1, 1]], [[1, 2], [3, 5]]
gauche = inv(mul(A41, B41))
droite = mul(inv(B41), inv(A41))
autre = mul(inv(A41), inv(B41))
ecart_droite = max(abs(gauche[i][j] - droite[i][j]) for i in range(2) for j in range(2))
ecart_autre = max(abs(gauche[i][j] - autre[i][j]) for i in range(2) for j in range(2))
C[41] = int(ecart_droite < 1e-12 and ecart_autre > 1e-3)
# 42 : produit vectoriel par le tenseur de Levi-Civita (autre voie que la regle des composantes)
def eps(i, j, k):
    return ((i - j) * (j - k) * (k - i)) / 2


a42, b42 = (2, -1, 3), (1, 4, -2)
C[42] = tuple(sum(eps(i, j, k) * a42[i] * b42[j] for i in range(3) for j in range(3)) for k in range(3))
ok(42, sum(u * v for u, v in zip(C[42], a42)), 0); ok(42, sum(u * v for u, v in zip(C[42], b42)), 0)
# 43 : loi des cosinus dans le triangle forme par a, b et a - b
a43, b43 = (1, 2, 2), (2, -3, 6)
na, nb = math.sqrt(sum(x * x for x in a43)), math.sqrt(sum(x * x for x in b43))
nd2 = sum((x - y) ** 2 for x, y in zip(a43, b43))
C[43] = (na ** 2 + nb ** 2 - nd2) / (2 * na * nb)
# 44 : comptage direct des permutations distinctes
C[44] = len(set(itertools.permutations("SEPTEMBER")))
# 45 : iteration de Newton avec derivee numerique
f45 = lambda x: x * x - 7
C[45] = 3 - f45(3) / derivee(f45, 3.0)
# 46 : maximum et minimum sur une grille de x
fx = [1 / (x * x + 1) for x in range(-1000, 1001)]
C[46] = (max(fx), int(min(fx) > 0))
# 47
xt = lambda t: t * t + 1
yt = lambda t: t ** 3 - t
C[47] = (yt(2 + 1e-4) - yt(2 - 1e-4)) / (xt(2 + 1e-4) - xt(2 - 1e-4))
differe(47, yt(2) / xt(2), C[47])
# 48 : droite obtenue en portant ln y en fonction de ln x pour y = e^2 x^3
y48 = lambda x: math.exp(2) * x ** 3
g48 = (math.log(y48(math.e ** 2)) - math.log(y48(math.e))) / (2 - 1)
C[48] = (g48, math.log(y48(math.e)) - g48)
# 49 : le minimum de 2x^2 + kx + 8 est atteint en x = -k/4 ; pas de racine reelle s'il est strictement positif
P49 = [-9, -8, -7.9, 0, 7.9, 8, 9]
C[49] = tuple(int(2 * (-k / 4) ** 2 + k * (-k / 4) + 8 > 1e-9) for k in P49)
# 50 : comptage direct (6 hommes, 5 femmes)
pers = ["H"] * 6 + ["F"] * 5
C[50] = sum(1 for c in itertools.combinations(range(11), 4) if sum(1 for i in c if pers[i] == "F") >= 2)

qs = questions()
for i, q in enumerate(qs, start=1):
    val = q["val"]
    tol = 1e-6
    if i in (4,):
        tol = 1e-4
    if i in (9, 10, 11):
        tol = 1e-4
    if i == 19:
        tol = 1e-5
    if i == 29:
        tol = 0
    if i == 30:
        tol = 1e-6
    if i == 23:
        tol = 1e-9
    if i == 38:
        tol = 1e-8
    ok(i, C[i], val, tol)

# ---- Coherence avec les JSON generes ----
contenus = []
for chemin in EPS:
    if not os.path.exists(chemin):
        ecarts.append("JSON manquant : " + chemin)
        continue
    ep = json.load(open(chemin, encoding="utf8"))
    ep_id = ep["external_id"]
    qj = ep["exercices"][0]["questions"]
    ok("JSON " + ep_id, len(qj), 50)
    for i, (q, j) in enumerate(zip(qs, qj), start=1):
        lettres = {c["lettre"]: c["texte"] for c in j["choix"]}
        bonne = j["reponse_correcte"]
        ok(f"{i} cle", int(lettres[bonne] == q["key"]), 1)
        ok(f"{i} unicite", sum(1 for t in lettres.values() if t == q["key"]), 1)
        ok(f"{i} quatre options distinctes", len(set(lettres.values())), 4)
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", j["corrige_markdown"])
        ok(f"{i} Answer", int(bool(m) and m.group(1).lower() == bonne), 1)
        ok(f"{i} points", j["points"], 1)
        ok(f"{i} id rappel", int(j["rappels_de_methode"][0]["id"] == f"rdi-{ep_id}-ex1-q{i}-0"), 1)
    from collections import Counter
    cnt = Counter(j["reponse_correcte"] for j in qj)
    ok("equilibre " + ep_id, max(cnt.values()) - min(cnt.values()), 1, 1)
    cles = [j["reponse_correcte"] for j in qj]
    ok("pas de trois cles identiques", sum(1 for a, b, c in zip(cles, cles[1:], cles[2:]) if a == b == c), 0)
    contenus.append([(j["enonce_markdown"], j["choix"], j["reponse_correcte"], j["corrige_markdown"]) for j in qj])
if len(contenus) == 2:
    ok("meme contenu dans les deux epreuves", int(contenus[0] == contenus[1]), 1)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
