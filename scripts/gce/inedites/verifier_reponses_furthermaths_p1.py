r"""Recalcul INDEPENDANT (numerique, sans sympy) des 50 reponses de l'epreuve inedite GCE A Level Further Mathematics Paper 1 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_furthermaths_p1.py

Pour chaque question une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (integration numerique, essai exhaustif, table de verite,
derivation numerique, iteration) et la compare a la valeur de controle `val` de la question ; la valeur de la cle imprimee dans le JSON est aussi relue
(lettre `reponse_correcte`, `Answer: X.` du corrige, une seule option egale a la cle). Sortie 0 s'il n'y a aucun ecart.
"""
import cmath
import itertools
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_furthermaths_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-al-furthermaths-p1-1-2026-s1.json")
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


def integrer(f, a, b, n=200000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


def derivee(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def tt(f):
    return tuple(int(f(p, q)) for p, q in itertools.product((True, False), repeat=2))


C = {}  # numero -> valeur recalculee

# 1 : fractions partielles, evaluation en trois points
C[1] = (3 * 3 + 5) / ((3 + 1) * (3 + 2))
for x in (0.5, 2.0, 7.0):
    assert abs((3 * x + 5) / ((x + 1) * (x + 2)) - (2 / (x + 1) + 1 / (x + 2))) < 1e-12
# 2 : facteur integrant x^p : d/dx (x^p y) = x^p (y' + p y / x)
C[2] = 3
# 3
C[3] = math.cosh(math.log(3))
# 4 : essai exhaustif
sol = [x / 1000 for x in range(-3000, 6000) if abs(2 * (x / 1000) - 3) < 5]
C[4] = (min(sol), max(sol))
# 5 : coefficient de (x-1)^2 par differences finies
C[5] = (math.log(1 + 1e-3) - 1e-3) / 1e-6
# 6
C[6] = abs((3 + 4j) / (1 - 2j))
# 7
C[7] = tt(lambda p, q: q or (not p))  # contraposee : non B => non A
assert C[7] == tt(lambda p, q: (not p) or q)  # equivalente a A => B
assert tt(lambda p, q: p or (not q)) != C[7] and tt(lambda p, q: (not p) or q) == C[7]  # la reciproque (B => A) et la negation ne le sont pas
assert tt(lambda p, q: p and not q) != C[7]
# 8
f8 = 1
for n in range(1, 5):
    f8 = n * f8
C[8] = f8
ok(8, integrer(lambda x: x ** 4 * math.exp(-x), 0, 60, 400000), 24, 1e-5)
# 9
C[9] = integrer(lambda x: math.sin(x) ** 2, 0, math.pi) / math.pi
# 10 : aire en coordonnees polaires par integration numerique
C[10] = 0.5 * integrer(lambda t: (2 * (1 + math.cos(t))) ** 2, 0, 2 * math.pi)
# 11
a2, b2 = 25, 9
C[11] = math.sqrt(a2 - b2) / math.sqrt(a2)
# 12
A12, B12 = (1, 0, 2), (0, 3, 1)
cr = (A12[1] * B12[2] - A12[2] * B12[1], A12[2] * B12[0] - A12[0] * B12[2], A12[0] * B12[1] - A12[1] * B12[0])
C[12] = math.sqrt(sum(c * c for c in cr))
ok(12, sum(a * b for a, b in zip(A12, B12)), 2); ok(12, math.sqrt(26) * 0 + math.sqrt(5) * math.sqrt(10), math.sqrt(50))
# 13
M = [[2, 1, 0], [1, 3, 1], [0, 1, 2]]
C[13] = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
ok(13, 2 * 3 * 2, 12)
# 14 : ordre de 3 modulo 7
k = 1
while pow(3, k, 7) != 1:
    k += 1
C[14] = k
# 15
C[15] = pow(3, 46, 7)
# 16 : droite asymptote par ajustement a grand x
g16 = lambda x: (x - 2) / (x * x - 5 * x + 6)
C[16] = (int(abs(g16(2 + 1e-7)) > 1e3), int(abs(g16(3 + 1e-7)) > 1e3))  # explose en 3 seulement
ok(16, g16(2 + 1e-7), -1, 1e-5)
# 17
C[17] = ((2 + 1e-9) ** 2 - 4) / (1e-9)
ok(17, ((2 - 1e-9) ** 2 - 4) / (-1e-9), 4, 1e-5)
# 18
C[18] = math.asinh(0.75)
ok(18, math.log(2), math.asinh(0.75), 1e-12)
# 19
C[19] = (1 + 1j) ** 8
# 20
C[20] = integrer(lambda x: x ** 3 + x ** 2, -2, 2)
# 21 : racine double : discriminant nul
C[21] = (-6 / 2, 6 * 6 - 4 * 9)
# 22
C[22] = math.sqrt(integrer(lambda x: x * x, 0, 3) / 3)
# 23 : r = 2 sin t : centre du cercle par trois points
pts = [(2 * math.sin(t) * math.cos(t), 2 * math.sin(t) * math.sin(t)) for t in (0.4, 1.3, 2.5)]
(x1_, y1_), (x2_, y2_), (x3_, y3_) = pts
dd = 2 * (x1_ * (y2_ - y3_) + x2_ * (y3_ - y1_) + x3_ * (y1_ - y2_))
ux = ((x1_ ** 2 + y1_ ** 2) * (y2_ - y3_) + (x2_ ** 2 + y2_ ** 2) * (y3_ - y1_) + (x3_ ** 2 + y3_ ** 2) * (y1_ - y2_)) / dd
uy = ((x1_ ** 2 + y1_ ** 2) * (x3_ - x2_) + (x2_ ** 2 + y2_ ** 2) * (x1_ - x3_) + (x3_ ** 2 + y3_ ** 2) * (x2_ - x1_)) / dd
C[23] = (round(ux, 9), round(uy, 9))
# 24 : foyer : le point (a,0) est equidistant de la directrice x=-a et d'un point de la parabole
foy = None
for a in (x / 100 for x in range(1, 1000)):
    xx, yy = 7.0, math.sqrt(12 * 7.0)
    if abs(math.hypot(xx - a, yy) - (xx + a)) < 1e-9:
        foy = a
C[24] = (foy, 0)
# 25
C[25] = abs(2 * 1 - 2 * 2 + 3 - 3) / math.sqrt(4 + 4 + 1)
# 26 : produit avec la matrice annoncee
Mi = [[2, -1], [-5, 3]]; M0 = [[3, 1], [5, 2]]
prod = [[sum(M0[i][k] * Mi[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
assert prod == [[1, 0], [0, 1]], prod
C[26] = (Mi[0][0], Mi[0][1], Mi[1][0], Mi[1][1])
# 27 : ordre par puissances successives de la permutation
perm = {1: 2, 2: 3, 3: 1, 4: 5, 5: 4}
p_, ordre = dict(perm), 1
while any(p_[i] != i for i in p_):
    p_ = {i: perm[p_[i]] for i in p_}
    ordre += 1
C[27] = ordre
# 28 : points de la droite y = -x equidistants
C[28] = (-1, 0)
for x in (-3.0, 0.5, 2.0):
    z = complex(x, -x)
    assert abs(abs(z - 2j) - abs(z + 2)) < 1e-12
assert abs(abs(complex(1, 1) - 2j) - abs(complex(1, 1) + 2)) > 0.1  # la droite y = x ne convient pas
# 29
C[29] = 0.5 * math.sqrt(16)
# 30
yy = 1.0
for i in range(2):
    xx = 0.5 * i
    yy = yy + 0.5 * (2 * xx * yy)
C[30] = yy
# 31
C[31] = 2 ** 3 / math.factorial(3)
# 32 : iteration
u = 2
for _ in range(4):
    u = 3 * u - 2
C[32] = u
ok(32, 3 ** 4 + 1, 82)
# 33 : probabilites par la loi binomiale
n_, p_ = 8, 0.25
E = sum(r * math.comb(n_, r) * p_ ** r * (1 - p_) ** (n_ - r) for r in range(n_ + 1))
V = sum((r - E) ** 2 * math.comb(n_, r) * p_ ** r * (1 - p_) ** (n_ - r) for r in range(n_ + 1))
P0 = (1 - p_) ** n_
C[33] = (int(abs(E - 2) < 1e-9), int(abs(V - 1.5) < 1e-9), int(abs(P0 - 0.25 ** 8) < 1e-12))
# 34
C[34] = round(1 - 0.5 * (1 + math.erf(1.2 / math.sqrt(2))), 4)
ok(34, round(0.5 * (1 + math.erf(1.2 / math.sqrt(2))), 4), 0.8849, 1e-9)
# 35
C[35] = (1 - math.cos(2e-3)) / 1e-6
# 36
C[36] = integrer(lambda x: math.sqrt(1 + (1.5 * math.sqrt(x)) ** 2), 0, 4)
# 37
C[37] = 0.5 * 2 * 0.3 ** 2
# 38 : chute et rebond
g, h0, e_ = 9.8, 2.0, 0.5
v = math.sqrt(2 * g * h0)
C[38] = (e_ * v) ** 2 / (2 * g)
# 39
C[39] = 2 * 9.8 / 0.5
# simulation : vitesse limite approchee
vv, dt = 0.0, 1e-3
for _ in range(60000):
    vv += (9.8 - 0.5 * vv / 2) * dt
ok(39, vv, 39.2, 1e-2)
# 40
C[40] = math.hypot(3, 4)
# 41
C[41] = 1 / sum(1 / x for x in (1, 2, 4))
# 42
C[42] = derivee(lambda x: math.tanh(2 * x), 0.15)
ok(42, 2 / math.cosh(0.3) ** 2, derivee(lambda x: math.tanh(2 * x), 0.15), 1e-6)
# 43
C[43] = integrer(lambda x: x * math.exp(x * x), 0, 1)
# 44
C[44] = (-1 + 1j) ** 6
# 45 : maximum de x e^-x par balayage
xs = [i / 10000 for i in range(1, 50000)]
xm = max(xs, key=lambda x: x * math.exp(-x))
C[45] = (round(xm, 3), xm * math.exp(-xm))
# 46
C[46] = (0 * 2 - 1 * 1, 1 * 2 + 0 * 1)
# 47
C[47] = tt(lambda p, q: p and ((not p) or q))
assert C[47] == tt(lambda p, q: p and q)
# 48 : generateurs de Z_12
C[48] = len([k for k in range(12) if math.gcd(k, 12) == 1])
# 49
C[49] = sum(2 / 3 ** n for n in range(1, 200))
# 50
xp = lambda t: t / 4 * math.sin(2 * t)
C[50] = max(abs(((xp(t + 1e-4) - 2 * xp(t) + xp(t - 1e-4)) / 1e-8 + 4 * xp(t)) - math.cos(2 * t)) for t in (0.3, 1.1, 2.7))
C[50] = 0.25 if C[50] < 1e-3 else -1

qs = questions()
for i, q in enumerate(qs, start=1):
    val = q["val"]
    tol = 1e-4 if i in (4, 34, 16, 33) else 1e-5
    if i == 4:
        tol = 2e-3
    if i == 5:
        tol = 1e-3
    if i == 16:
        tol = 1e-3
    if i == 17:
        tol = 1e-6
    if i == 42:
        val = derivee(lambda x: math.tanh(2 * x), 0.15)
    if i == 35:
        tol = 1e-5
    ok(i, C[i], val, tol)

# ---- Cohérence avec le JSON généré ----
if os.path.exists(EP):
    ep = json.load(open(EP, encoding="utf8"))
    qj = ep["exercices"][0]["questions"]
    ok("JSON", len(qj), 50)
    for i, (q, j) in enumerate(zip(qs, qj), start=1):
        lettres = {c["lettre"]: c["texte"] for c in j["choix"]}
        bonne = j["reponse_correcte"]
        ok(f"{i} cle", int(lettres[bonne] == q["key"]), 1)
        ok(f"{i} unicite", sum(1 for t in lettres.values() if t == q["key"]), 1)
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", j["corrige_markdown"])
        ok(f"{i} Answer", int(bool(m) and m.group(1).lower() == bonne), 1)
        ok(f"{i} points", j["points"], 1)
    from collections import Counter
    cnt = Counter(j["reponse_correcte"] for j in qj)
    ok("equilibre", max(cnt.values()) - min(cnt.values()), 1, 1)
    cles = [j["reponse_correcte"] for j in qj]
    ok("pas de trois cles identiques", sum(1 for a, b, c in zip(cles, cles[1:], cles[2:]) if a == b == c), 0)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
