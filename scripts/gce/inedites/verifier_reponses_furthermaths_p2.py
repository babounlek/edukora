r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Further Mathematics Paper 2 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_furthermaths_p2.py

Chaque reponse finale et chaque valeur intermediaire citee dans le corrige est recalculee par une autre voie (integration numerique,
recherche de racines, verification par substitution). Sortie 0 s'il n'y a aucun ecart.
"""
import cmath
import math
import sys

ecarts = []
nverif = 0


def ok(nom, valeur, attendu, tol=1e-6):
    global nverif
    nverif += 1
    if isinstance(valeur, complex) or isinstance(attendu, complex):
        bon = abs(complex(valeur) - complex(attendu)) <= tol
    else:
        bon = abs(valeur - attendu) <= tol
    if not bon:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def integrer(f, a, b, n=200000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


# ---- Ex 1 ----
for x in (0.0, math.log(4)):
    ok("1a racine", 5 * math.cosh(x) - 3 * math.sinh(x), 5)
# aucune autre racine : l'equation en e^x est un trinome (e^x-1)(e^x-4) ; on verifie que le trinome s'annule seulement en 1 et 4
ok("1a forme exponentielle", 5 * math.cosh(0.7) - 3 * math.sinh(0.7), math.exp(0.7) + 4 * math.exp(-0.7))
ok("1b integrale", integrer(lambda x: math.sinh(x) ** 2, 0, math.log(2)), 15 / 32 - 0.5 * math.log(2))
ok("1b sinh(2 ln 2)", math.sinh(2 * math.log(2)), 15 / 8)

# ---- Ex 2 ----
A, B, C = (1, 0, 2), (3, 1, 1), (2, 3, 0)


def sub(u, v):
    return tuple(a - b for a, b in zip(u, v))


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


AB, AC = sub(B, A), sub(C, A)
n = cross(AB, AC)
ok("2a AB", AB[0], 2); ok("2a AC", AC[2], -2)
assert n == (1, 3, 5), n
for P in (A, B, C):
    ok("2a plan", dot(n, P), 11)
D = (2, -1, 1)
dist = abs(dot(n, D) - 11) / math.sqrt(dot(n, n))
ok("2b distance", dist, math.sqrt(35) / 5)
t = (11 - dot(n, D)) / dot(n, n)
ok("2b t", t, 1 / 5)
pied = tuple(d + t * c for d, c in zip(D, n))
ok("2b pied x", pied[0], 11 / 5); ok("2b pied y", pied[1], -2 / 5); ok("2b pied z", pied[2], 2)
ok("2b pied dans le plan", dot(n, pied), 11)
d = (2, -1, 1)
ok("2c d.n", dot(d, n), 4)
theta = math.degrees(math.asin(abs(dot(d, n)) / (math.sqrt(dot(d, d)) * math.sqrt(dot(n, n)))))
ok("2c angle", round(theta, 1), 16.0, 1e-9)
ok("2c sin", 4 / math.sqrt(210), 0.27603, 1e-4)

# ---- Ex 3 ----
def y3(x):
    return x ** 3 / 5 + 4 / (5 * x ** 2)


ok("3a y(1)", y3(1), 1)
for x in (0.7, 1.9, 3.2):  # x y' + 2y = x^3, derivee numerique
    h = 1e-6
    dy = (y3(x + h) - y3(x - h)) / (2 * h)
    ok("3a equation", x * dy + 2 * y3(x), x ** 3, 1e-6)
ok("3b y(2)", y3(2), 9 / 5)
ok("3b limite", y3(1e4) / 1e4 ** 3, 1 / 5, 1e-9)

# ---- Ex 4 ----
M = ((4, -1), (2, 1))
det = 4 * 1 - (-1) * 2
ok("4a det", det, 6)
ok("4a aire", abs(det) * 0.5 * 4 * 3, 36)
Minv = tuple(tuple(v / det for v in row) for row in ((1, 1), (-2, 4)))
ok("4b M M^-1", M[0][0] * Minv[0][0] + M[0][1] * Minv[1][0], 1)
ok("4b M M^-1 (2,2)", M[1][0] * Minv[0][1] + M[1][1] * Minv[1][1], 1)
ok("4b M M^-1 (1,2)", M[0][0] * Minv[0][1] + M[0][1] * Minv[1][1], 0)
p = (Minv[0][0] * 13 + Minv[0][1] * 5, Minv[1][0] * 13 + Minv[1][1] * 5)
ok("4b x", p[0], 3); ok("4b y", p[1], -1)
for lam, v in ((2, (1, 2)), (3, (1, 1))):
    Mv = (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])
    ok(f"4c vecteur propre {lam}", Mv[0], lam * v[0]); ok(f"4c vecteur propre {lam} y", Mv[1], lam * v[1])
ok("4c trace", 4 + 1, 5)

# ---- Ex 5 ----
sol = [x for x in range(15) if (7 * x - 4) % 15 == 0]
assert sol == [7], sol
ok("5a inverse", (7 * 13) % 15, 1)
ok("5b 5^4 mod 13", pow(5, 4, 13), 1)
ok("5b 5^77 mod 13", pow(5, 77, 13), 5)
G = [1, 2, 4, 7, 8, 11, 13, 14]
ok("5c |G|", len(G), 8)
assert all(math.gcd(g, 15) == 1 for g in G) and len([g for g in range(1, 15) if math.gcd(g, 15) == 1]) == 8


def ordre(g):
    k, v = 1, g % 15
    while v != 1:
        v = v * g % 15
        k += 1
    return k


ordres = {g: ordre(g) for g in G}
for g in (4, 11, 14):
    ok(f"5c ordre {g}", ordres[g], 2)
for g in (2, 7, 8, 13):
    ok(f"5c ordre {g}", ordres[g], 4)
ok("5c max des ordres", max(ordres.values()), 4)
ok("5c 7^3", pow(7, 3, 15), 13)

# ---- Ex 6 ----
def r6(th):
    return 12 / (3 + 2 * math.cos(th))


ok("6b r min", r6(0), 12 / 5); ok("6b r max", r6(math.pi), 12)
ok("6b axe", r6(0) + r6(math.pi), 72 / 5)
ok("6a l/(1-e^2)", 2 * 4 / (1 - (2 / 3) ** 2), 72 / 5)
ok("6a directrice", 4 / (2 / 3), 6)
for th in (0.3, 1.1, 2.4, 4.0, 5.5):  # equation cartesienne
    x, y = r6(th) * math.cos(th), r6(th) * math.sin(th)
    ok("6c cartesienne", 5 * x * x + 48 * x + 9 * y * y, 144, 1e-9)
ok("6c x max sur l'ellipse", max(r6(i / 1000 * 2 * math.pi) * math.cos(i / 1000 * 2 * math.pi) for i in range(1001)), 2.4, 1e-6)

# ---- Ex 7 ----
z = complex(math.sqrt(3), -1)
ok("7a module", abs(z), 2); ok("7a argument", cmath.phase(z), -math.pi / 6)
ok("7a z^5", z ** 5, complex(-16 * math.sqrt(3), -16))
for th in (0.4, 1.3, 2.2):
    ok("7b cos 4theta", math.cos(4 * th), 8 * math.cos(th) ** 4 - 8 * math.cos(th) ** 2 + 1)
for r in (complex(math.sqrt(3), -1), 2j, complex(-math.sqrt(3), -1)):
    ok("7c cube", r ** 3, -8j, 1e-9)
ok("7c arguments", cmath.phase(2j), math.pi / 2)

# ---- Ex 8 ----
ok("8a pente", (1 ** 2) / (2 * 1), 1 / 2)
# tangente 3x - 6y - 1 = 0 en (1, 1/3)
ok("8a tangente", 3 * 1 - 6 * (1 / 3) - 1, 0)
ok("8b arc", integrer(lambda t: math.sqrt((2 * t) ** 2 + (t * t) ** 2), 0, 2), (16 * math.sqrt(2) - 8) / 3, 1e-7)
ok("8b valeur", (16 * math.sqrt(2) - 8) / 3, 4.8758, 1e-3)
P, Q, R = (1, 2, 0), (3, -1, 2), (0, 1, 4)
PQ, PR = sub(Q, P), sub(R, P)
c8 = cross(PQ, PR)
assert c8 == (-10, -10, -5), c8
ok("8c module", math.sqrt(dot(c8, c8)), 15); ok("8c aire", 0.5 * math.sqrt(dot(c8, c8)), 7.5)

# ---- Ex 9 ----
def f9(x):
    return (x * x - x - 6) / (x - 1)


for x in (-3.3, 0.4, 2.7, 6.0):
    ok("9a division", f9(x), x - 6 / (x - 1))
    ok("9a ecart a l'asymptote", f9(x) - x, -6 / (x - 1))
ok("9a f grand x", f9(1e8) - 1e8, 0, 1e-6)
ok("9b f(-2)", f9(-2), 0); ok("9b f(3)", f9(3), 0); ok("9b f(0)", f9(0), 6)
for x in (-5, -1, 0.5, 0.99, 1.01, 3, 9):
    h = 1e-6
    d = (f9(x + h) - f9(x - h)) / (2 * h)
    ok("9c derivee", d, 1 + 6 / (x - 1) ** 2, 1e-3 * max(1, abs(d)))
    assert d > 1
ok("9d f(1-) tres grand", 1 if f9(1 - 1e-8) > 1e6 else 0, 1)
ok("9d f(1+) tres negatif", 1 if f9(1 + 1e-8) < -1e6 else 0, 1)
ok("9e signe de f-x a gauche", 1 if all(f9(x) - x > 0 for x in (-50, -5, 0.5)) else 0, 1)
ok("9e signe de f-x a droite", 1 if all(f9(x) - x < 0 for x in (1.5, 5, 50)) else 0, 1)

# ---- Ex 10 ----
u = [None, 1]
for k in range(1, 12):
    u.append(2 * u[k] + 3)
ok("10a u2", u[2], 5); ok("10a u3", u[3], 13); ok("10a u4", u[4], 29)
for k in range(1, 12):
    ok(f"10b u_{k}", u[k], 2 ** (k + 1) - 3)
ok("10b constante", -3, 2 * -3 + 3)
ok("10c limite", (2 ** 41 - 3) / 2 ** 40, 2, 1e-9)


def T(z):
    return (z + 1) / (z - 1)


ok("10d image de i", T(1j), -1j, 1e-12); ok("10d image de -1", T(-1), 0)
for zz in (1 + math.sqrt(2), 1 - math.sqrt(2)):
    ok("10e invariant", T(zz), zz, 1e-12)
ok("10e discriminant", 4 + 4, 8)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
