r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Pure Mathematics Paper 2 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_pm_p2.py

Chaque reponse finale et chaque valeur intermediaire citee dans le corrige est recalculee par une autre voie (integration et derivation numeriques,
recherche de racines, substitution, sommes). Sortie 0 s'il n'y a aucun ecart.
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


def deriver(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def racines_reelles(f, a, b, n=40000):
    """Racines de f sur [a, b] par balayage + bissection."""
    res = []
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    for x0, x1 in zip(xs, xs[1:]):
        try:
            y0, y1 = f(x0), f(x1)
        except ZeroDivisionError:
            continue
        if y0 == 0:
            res.append(x0)
        elif y0 * y1 < 0:
            lo, hi = x0, x1
            try:
                for _ in range(80):
                    mid = (lo + hi) / 2
                    if f(lo) * f(mid) <= 0:
                        hi = mid
                    else:
                        lo = mid
            except ZeroDivisionError:
                continue  # changement de signe a travers un pole, pas une racine
            res.append((lo + hi) / 2)
    return res


# ---- Ex 1 ----
def f1(x, a, b):
    return x ** 3 + a * x * x + b * x + 6


# resolution du systeme par balayage entier des couples (a, b) : f(1) = 0 et f(2) = -4
sols = [(a, b) for a in range(-30, 31) for b in range(-30, 31) if f1(1, a, b) == 0 and f1(2, a, b) == -4]
assert sols == [(-2, -5)], sols
ok("1a f(1)", f1(1, -2, -5), 0); ok("1a f(2)", f1(2, -2, -5), -4)
ok("1a a+b", -2 + -5, -7); ok("1a 2a+b", 2 * -2 + -5, -9)
for x in (-2, 1, 3):
    ok(f"1b racine {x}", f1(x, -2, -5), 0)
for x in (-3.3, 0.4, 2.2, 5.0):  # factorisation et quotient
    ok("1b factorisation", f1(x, -2, -5), (x - 1) * (x - 3) * (x + 2))
    ok("1b quotient", f1(x, -2, -5), (x - 1) * (x * x - x - 6))
rr = racines_reelles(lambda x: f1(x, -2, -5), -10, 10)
ok("1b nombre de racines", len(rr), 3)
# 1c : pas de racine reelle <=> discriminant < 0 : balayage de k
for k in (-2.5, -2.0, -1.0, 0.0, 3.0, 5.9, 6.0, 6.5, -2.1):
    disc = k * k - 4 * (k + 3)
    ok(f"1c disc k={k}", disc, (k - 6) * (k + 2))
    ok(f"1c aucune racine k={k}", 1 if disc < 0 else 0, 1 if -2 < k < 6 else 0)
ok("1c k=0 : x^2+3", 0 ** 2 - 4 * 3, -12)

# ---- Ex 2 ----
# 2x^2 - 9x + 3 = 0 : racines numeriques
d = 81 - 24
al, be = (9 + math.sqrt(d)) / 4, (9 - math.sqrt(d)) / 4
ok("2a racine alpha", 2 * al * al - 9 * al + 3, 0); ok("2a racine beta", 2 * be * be - 9 * be + 3, 0)
ok("2a somme", al + be, 9 / 2); ok("2a produit", al * be, 3 / 2); ok("2a carres", al * al + be * be, 69 / 4)
ok("2b somme des nouvelles racines", al / be + be / al, 23 / 2); ok("2b produit", (al / be) * (be / al), 1)
for r in (al / be, be / al):
    ok("2b racine de 2x^2-23x+2", 2 * r * r - 23 * r + 2, 0, 1e-9)
ok("2b discriminant de 2x^2-23x+2", 23 ** 2 - 4 * 2 * 2, 513)


def f2(x, p):
    return x ** 3 - 14 * x * x + p * x - 64


for r in (2, 4, 8):
    ok(f"2c racine {r}", f2(r, 56), 0)
rr = racines_reelles(lambda x: f2(x, 56), -5, 20)
ok("2c nombre de racines", len(rr), 3)
ok("2c produit", rr[0] * rr[1] * rr[2], 64, 1e-6); ok("2c somme", sum(rr), 14, 1e-6)
ok("2c rapport", rr[1] / rr[0], rr[2] / rr[1], 1e-6)
ok("2c p par paires", 2 * 4 + 2 * 8 + 4 * 8, 56)
ok("2c a^3", 4 ** 3, 64)
# aucun autre p ne donne trois racines en progression geometrique parmi les entiers testes
autres = []
for p in range(-200, 400):
    rp = racines_reelles(lambda x: f2(x, p), -30, 30, 6000)
    if len(rp) == 3 and abs(rp[1] ** 2 - rp[0] * rp[2]) < 1e-4:
        autres.append(p)
ok("2c p unique", len(autres), 1); ok("2c p valeur", autres[0], 56)
ok("2c r+1/r", 2 + 1 / 2, 5 / 2); ok("2c 2r^2-5r+2 en r=2", 2 * 4 - 10 + 2, 0); ok("2c 2r^2-5r+2 en r=1/2", 2 * 0.25 - 2.5 + 2, 0)

# ---- Ex 3 ----
def f3(x):
    return (x * x + 10 * x + 7) / ((x - 1) * (x + 2) ** 2)


for x in (1.5, 2.0, 3.3, 7.0, 40.0):
    ok("3a fractions partielles", f3(x), 2 / (x - 1) - 1 / (x + 2) + 3 / (x + 2) ** 2, 1e-12)
ok("3a A", (1 + 10 + 7) / (1 + 2) ** 2, 2)   # (x+2)^2 en x=1 : 9 ; 18/9
ok("3a C", (4 - 20 + 7) / (-2 - 1), 3)
ok("3a B (x^2)", 2 + -1, 1)
ok("3b integrale", integrer(f3, 2, 4), math.log(6) + 0.25, 1e-9)
ok("3b bornes", (2 * math.log(3) - math.log(6) - 0.5) - (0 - math.log(4) - 0.75), math.log(6) + 0.25, 1e-12)
ok("3b valeur 4", 2 * math.log(3) - math.log(6) - 1 / 2, 2 * math.log(3) - math.log(6) - 0.5)
ok("3b ln(9*4/6)", math.log(9 * 4 / 6), math.log(6))
ok("3c integrale", integrer(lambda x: (4 * x + 2) / (x * x + x + 1), 0, 1), 2 * math.log(3), 1e-9)
ok("3c derivee du denominateur", deriver(lambda x: x * x + x + 1, 0.7), 2 * 0.7 + 1, 1e-8)

# ---- Ex 4 ----
R4 = math.hypot(8, 15)
al4 = math.degrees(math.atan2(15, 8))
ok("4a R", R4, 17); ok("4a alpha", round(al4, 2), 61.93, 1e-9)
for th in (0.0, 20.0, 133.0, 250.0, 300.0):
    t = math.radians(th)
    ok("4a forme harmonique", 8 * math.sin(t) + 15 * math.cos(t), 17 * math.sin(t + math.radians(al4)), 1e-9)
ok("4a R cos alpha", R4 * math.cos(math.radians(al4)), 8); ok("4a R sin alpha", R4 * math.sin(math.radians(al4)), 15)
# 4b : balayage de theta pour 8 sin + 15 cos = 10 sur [0, 360]
g = lambda th: 8 * math.sin(math.radians(th)) + 15 * math.cos(math.radians(th)) - 10
sol4 = racines_reelles(g, 0, 360)
ok("4b nombre de solutions", len(sol4), 2)
ok("4b theta 1", round(sol4[0], 1), 82.0, 1e-9); ok("4b theta 2", round(sol4[1], 1), 334.1, 1e-9)
ok("4b asin", round(math.degrees(math.asin(10 / 17)), 2), 36.03, 1e-9)
ok("4b 143.97", round(180 - math.degrees(math.asin(10 / 17)), 2), 143.97, 1e-9)
ok("4b 396.03", round(360 + math.degrees(math.asin(10 / 17)), 2), 396.03, 1e-9)
ok("4b borne haute", round(360 + al4, 2), 421.93, 1e-9)
for th in (10.0, 55.0, 99.0, 171.0):
    t = math.radians(th)
    ok("4c identite", math.sin(2 * t) / (1 + math.cos(2 * t)), math.tan(t), 1e-9)
    ok("4c 1+cos2t", 1 + math.cos(2 * t), 2 * math.cos(t) ** 2, 1e-12)
sol4c = racines_reelles(lambda th: math.sin(math.radians(2 * th)) / (1 + math.cos(math.radians(2 * th))) - 3, 1, 89.9) + \
    racines_reelles(lambda th: math.sin(math.radians(2 * th)) / (1 + math.cos(math.radians(2 * th))) - 3, 90.1, 179.9)
ok("4c nombre de solutions", len(sol4c), 1); ok("4c theta", round(sol4c[0], 1), 71.6, 1e-9)
ok("4c atan 3", round(math.degrees(math.atan(3)), 1), 71.6, 1e-9)

# ---- Ex 5 ----
u5 = lambda n: 2.4 + 0.3 * (n - 1)
ok("5a jour 13", u5(13), 6.0, 1e-9)
jour = next(n for n in range(1, 100) if u5(n) > 6 + 1e-9)
ok("5a premier jour", jour, 14)
ok("5a u14", u5(14), 6.3, 1e-9)
ok("5a somme 14 (formule)", 7 * (2 * 2.4 + 13 * 0.3), 60.9, 1e-9)
ok("5a somme 14 (termes)", sum(u5(n) for n in range(1, 15)), 60.9, 1e-9)
r5 = 1 - 24 / 72
ok("5b r", r5, 2 / 3)
ok("5b somme a l'infini", sum(24 * r5 ** k for k in range(2000)), 72, 1e-9)
ok("5b S6 (termes)", sum(24 * r5 ** k for k in range(6)), 5320 / 81, 1e-9)
ok("5b S6 (72 x 665/729)", 72 * 665 / 729, 5320 / 81, 1e-9)
ok("5b 665", 729 - 64, 665)
ok("5b S6 decimal", round(5320 / 81, 1), 65.7, 1e-9)


def poly_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return r


p = [1]
for _ in range(5):
    p = poly_mul(p, [2, -3])  # coefficients par puissances croissantes de (2 - 3x)^5
ok("5c coefficient 0", p[0], 32); ok("5c coefficient 1", p[1], -240); ok("5c coefficient 2", p[2], 720)
ok("5c C(5,1)", math.comb(5, 1), 5); ok("5c C(5,2)", math.comb(5, 2), 10)
pp = poly_mul([1, 2], p)
ok("5c coefficient de x^2 du produit", pp[2], 240)
ok("5c 720 - 480", 720 - 480, 240)
# controle numerique par differences finies sur le polynome complet : coefficient de x^2 = f''(0)/2
fx = lambda x: (1 + 2 * x) * (2 - 3 * x) ** 5
h = 1e-3
ok("5c f''(0)/2", (fx(h) - 2 * fx(0) + fx(-h)) / h ** 2 / 2, 240, 1e-2)

# ---- Ex 6 ----
w = (5 + 5j) / (2 - 1j)
ok("6a w", w, 1 + 3j, 1e-12)
ok("6a numerateur", (5 + 5j) * (2 + 1j), 5 + 15j)
z = complex(-1, 1)
ok("6b module", abs(z), math.sqrt(2)); ok("6b argument", cmath.phase(z), 3 * math.pi / 4)
ok("6b z^6", z ** 6, 8j, 1e-12)
ok("6b De Moivre", (math.sqrt(2)) ** 6 * cmath.exp(1j * 6 * 3 * math.pi / 4), 8j, 1e-9)
ok("6b z^2", z ** 2, -2j, 1e-12); ok("6b (-2i)^3", (-2j) ** 3, 8j, 1e-12)
ok("6b 18pi/4", 18 * math.pi / 4, 9 * math.pi / 2)
racines = [2 * cmath.exp(1j * (math.pi + 2 * k * math.pi) / 4) for k in range(4)]
for r in racines:
    ok("6c puissance 4", r ** 4, -16, 1e-9)
attendues = [complex(math.sqrt(2), math.sqrt(2)), complex(-math.sqrt(2), math.sqrt(2)), complex(-math.sqrt(2), -math.sqrt(2)), complex(math.sqrt(2), -math.sqrt(2))]
for r, a in zip(racines, attendues):
    ok("6c racine", r, a, 1e-9)
ok("6c module", 16 ** 0.25, 2)
# unicite : on cherche les solutions de z^4 = -16 parmi une grille fine du plan et on retrouve exactement ces quatre
sol6 = [complex(x / 20, y / 20) for x in range(-60, 61) for y in range(-60, 61) if abs(complex(x / 20, y / 20) ** 4 + 16) < 0.7]
ok("6c grille proche des racines", 1 if all(min(abs(s - a) for a in attendues) < 0.3 for s in sol6) else 0, 1)

# ---- Ex 7 ----
def y7a(x):
    return 2 * math.sqrt(1 + math.log(x * x + 1))


ok("7a condition", y7a(0), 2)
for x in (0.3, 1.1, 2.6, 4.0):  # (x^2+1) y y' = 4x
    ok("7a equation", (x * x + 1) * y7a(x) * deriver(y7a, x), 4 * x, 1e-6)
ok("7a y^2", y7a(1.7) ** 2, 4 * math.log(1.7 ** 2 + 1) + 4, 1e-12)
ok("7a integrale du second membre", integrer(lambda x: 4 * x / (x * x + 1), 0, 2.5), 2 * math.log(2.5 ** 2 + 1), 1e-9)


def y7b(x):
    return (x + 2) * math.cos(x)


ok("7b condition", y7b(0), 2)
for x in (0.1, 0.6, 1.0, 1.4):  # cos x y' + y sin x = cos^2 x
    ok("7b equation", math.cos(x) * deriver(y7b, x) + y7b(x) * math.sin(x), math.cos(x) ** 2, 1e-6)
    ok("7b facteur integrant", integrer(math.tan, 0, x, 20000), math.log(1 / math.cos(x)), 1e-8)
    ok("7b d(y sec x)", deriver(lambda t: y7b(t) / math.cos(t), x), 1, 1e-6)

# ---- Ex 8 ----
b8 = (2.4 - 0.9) / (0.8 - 0.2)
ok("8a gradient", b8, 2.5)
lga = 0.9 - b8 * 0.2
ok("8a ordonnee a l'origine", lga, 0.4); ok("8a point 2", lga + b8 * 0.8, 2.4)
a8 = 10 ** lga
ok("8a a", round(a8, 2), 2.51, 1e-9)
ok("8a retour sur la loi de puissance", math.log10(a8 * (10 ** 0.2) ** b8), 0.9, 1e-12)
V = lambda t: 800 * 0.8 ** t
ok("8b V(1)", V(1), 640, 1e-9); ok("8b V(3)", V(3), 409.6, 1e-9)
ok("8b k^2", 409.6 / 640, 0.64, 1e-12); ok("8b A", 640 / 0.8, 800)
ok("8b log-lineaire", math.log10(V(3)) - math.log10(V(1)), 2 * math.log10(0.8), 1e-12)
t8 = math.log10(0.25) / math.log10(0.8)
ok("8b seuil", round(t8, 2), 6.21, 1e-9)
ok("8b annees", next(t for t in range(0, 50) if V(t) < 200), 7)
ok("8b V(6) >= 200", 1 if V(6) >= 200 else 0, 1); ok("8b V(7) < 200", 1 if V(7) < 200 else 0, 1)
ok("8b V(6)", round(V(6), 2), 209.72, 1e-9); ok("8b V(7)", round(V(7), 2), 167.77, 1e-9)

# ---- Ex 9 ----
def f9(x):
    return (x * x - 4) / (x * x - 1)


for x in (-3.3, -0.4, 0.8, 2.7, 6.0):
    ok("9a division", f9(x), 1 - 3 / (x * x - 1), 1e-12)
    ok("9d parite", f9(x), f9(-x), 1e-12)
ok("9a f grand x", f9(1e8), 1, 1e-6); ok("9a f tres negatif", f9(-1e8), 1, 1e-6)
ok("9a numerateur en 1", 1 - 4, -3)
for x0 in (1.0, -1.0):
    ok(f"9a vertical {x0} haut", 1 if abs(f9(x0 + 1e-9)) > 1e6 and abs(f9(x0 - 1e-9)) > 1e6 else 0, 1)
ok("9a sens a 1-", 1 if f9(1 - 1e-8) > 1e6 else 0, 1); ok("9a sens a 1+", 1 if f9(1 + 1e-8) < -1e6 else 0, 1)
ok("9a sens a -1+", 1 if f9(-1 + 1e-8) > 1e6 else 0, 1); ok("9a sens a -1-", 1 if f9(-1 - 1e-8) < -1e6 else 0, 1)
ok("9b f(-2)", f9(-2), 0); ok("9b f(2)", f9(2), 0); ok("9b f(0)", f9(0), 4)
zeros = racines_reelles(f9, -5, 5, 20001)
ok("9b nombre de zeros", len([z for z in zeros if abs(f9(z)) < 1e-6]), 2)
for x in (-5, -2.5, -0.7, 0.3, 0.9, 1.4, 3, 8):
    ok("9c derivee", deriver(f9, x), 6 * x / (x * x - 1) ** 2, 1e-5 * max(1, abs(deriver(f9, x))))
st = racines_reelles(lambda x: deriver(f9, x), -0.9, 0.9, 2000)
ok("9c points stationnaires", len(st), 1); ok("9c abscisse", st[0], 0, 1e-5); ok("9c ordonnee", f9(st[0]), 4, 1e-6)
ok("9c minimum local", 1 if all(f9(x) > 4 for x in (-0.9, -0.5, -0.1, 0.1, 0.5, 0.9)) else 0, 1)
ok("9c signe gauche", 1 if all(deriver(f9, x) < 0 for x in (-0.9, -0.5, -0.1)) else 0, 1)
ok("9c signe droite", 1 if all(deriver(f9, x) > 0 for x in (0.1, 0.5, 0.9)) else 0, 1)
ok("9d signe au centre", 1 if all(f9(x) > 0 for x in (-0.9, -0.3, 0.0, 0.5, 0.95)) else 0, 1)
ok("9d branche droite sous 1", 1 if all(f9(x) < 1 for x in (1.2, 2, 3, 10, 100)) else 0, 1)
ok("9d branche droite negative entre 1 et 2", 1 if all(f9(x) < 0 for x in (1.01, 1.5, 1.99)) else 0, 1)
ok("9d branche droite positive apres 2", 1 if all(f9(x) > 0 for x in (2.01, 3, 10)) else 0, 1)

# ---- Ex 10 ----
y10 = lambda x: math.log(x) / x ** 2
for x in (0.4, 1.0, 1.9, 3.5):
    ok("10a derivee", deriver(y10, x), (1 - 2 * math.log(x)) / x ** 3, 1e-6)
xs10 = racines_reelles(lambda x: deriver(y10, x), 0.5, 5, 40000)
ok("10a un seul point stationnaire", len(xs10), 1)
ok("10a abscisse", xs10[0], math.sqrt(math.e), 1e-5); ok("10a ordonnee", y10(math.sqrt(math.e)), 1 / (2 * math.e), 1e-9)
ok("10a ln(sqrt e)", math.log(math.sqrt(math.e)), 0.5)
ok("10b integrale", integrer(lambda x: x / math.sqrt(x + 1), 0, 3), 8 / 3, 1e-9)
ok("10b par u", integrer(lambda u: (u - 1) / math.sqrt(u), 1, 4), 8 / 3, 1e-9)
anti = lambda u: 2 / 3 * u ** 1.5 - 2 * math.sqrt(u)
ok("10b en u=4", anti(4), 4 / 3); ok("10b en u=1", anti(1), -4 / 3); ok("10b difference", anti(4) - anti(1), 8 / 3)
ok("10b derivee de l'antiderivee", deriver(anti, 2.3), (2.3 - 1) / math.sqrt(2.3), 1e-6)
ok("10c integrale", integrer(lambda x: x * math.exp(2 * x), 0, 1), (math.e ** 2 + 1) / 4, 1e-9)
F10 = lambda x: 0.5 * x * math.exp(2 * x) - 0.25 * math.exp(2 * x)
ok("10c antiderivee", F10(1) - F10(0), (math.e ** 2 + 1) / 4, 1e-12)
ok("10c derivee de l'antiderivee", deriver(F10, 0.6), 0.6 * math.exp(1.2), 1e-6)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
