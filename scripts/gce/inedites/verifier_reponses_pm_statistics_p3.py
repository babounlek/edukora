r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Pure Mathematics with Statistics Paper 3 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_pm_statistics_p3.py

Chaque reponse finale et chaque valeur intermediaire citee dans le corrige est recalculee par une autre voie (enumeration, integration numerique,
sommes directes, simulation, math.erf, math.comb). Les valeurs de table de la loi normale sont recalculees par math.erf et comparees a 4 decimales.
Sortie 0 s'il n'y a aucun ecart.
"""
import itertools
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_pm_statistics_p3 import exercices  # noqa: E402

ecarts = []
nverif = 0


def ok(nom, valeur, attendu, tol=1e-6):
    global nverif
    nverif += 1
    if abs(valeur - attendu) > tol:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def vrai(nom, condition):
    global nverif
    nverif += 1
    if not condition:
        ecarts.append(f"{nom}: condition fausse")


def integrer(f, a, b, n=200000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
poisson = lambda lam, r: math.exp(-lam) * lam ** r / math.factorial(r)

# ---- Structure : points par exercice (blueprint 12, 12, 12, 13, 13, 12, 13, 13) ----
ex = exercices()
for e, attendu in zip(ex, (12, 12, 12, 13, 13, 12, 13, 13)):
    ok(f"points exercice {e['num']}", sum(s["pts"] for s in e["subs"]), attendu, 1e-9)
    for s in e["subs"]:
        ok(f"bareme {e['num']}{s['num']}", sum(p for _, p in s["crit"]), s["pts"], 1e-9)
ok("total", sum(e["pts"] for e in ex), 100, 1e-9)
vrai("8 exercices", len(ex) == 8)

# ---- Ex 1 : probabilites. Verification par denombrement d'une population de 10 000 eleves ----
N = 10000
G_, E_, GE = 4000, 3500, 1500
ok("1a union", (G_ + E_ - GE) / N, 0.60); ok("1a ni l'un ni l'autre", (N - (G_ + E_ - GE)) / N, 0.40)
ok("1b produit", (G_ / N) * (E_ / N), 0.14); vrai("1b non independants", abs((G_ / N) * (E_ / N) - GE / N) > 1e-9)
ok("1b conditionnelle", GE / E_, 3 / 7); ok("1b arrondi", round(GE / E_, 4), 0.4286, 1e-9)
# boulangerie : population de 100 000 pains
four_a, four_b = 55000, 45000
mal_a, mal_b = four_a * 4 // 100, four_b * 7 // 100
ok("1c branche A", mal_a / 100000, 0.022); ok("1c branche B", mal_b / 100000, 0.0315)
ok("1c total", (mal_a + mal_b) / 100000, 0.0535)
ok("1d Bayes", mal_b / (mal_a + mal_b), 63 / 107); ok("1d arrondi", round(mal_b / (mal_a + mal_b), 4), 0.5888, 1e-9)
# simulation de la boulangerie
random.seed(11)
tot = mal = malB = 0
for _ in range(400000):
    four = "B" if random.random() < 0.45 else "A"
    m = random.random() < (0.07 if four == "B" else 0.04)
    tot += 1
    if m:
        mal += 1
        malB += four == "B"
ok("1c simulation", mal / tot, 0.0535, 2e-3); ok("1d simulation", malB / mal, 63 / 107, 1.5e-2)

# ---- Ex 2 : denombrement et binomiale ----
arr = set(itertools.permutations("BAMENDA"))
ok("2a total par enumeration", len(arr), 2520, 0)
ok("2a A cote a cote", sum(1 for w in arr if "AA" in "".join(w)), 720, 0)
ok("2a A separes", sum(1 for w in arr if "AA" not in "".join(w)), 1800, 0)
ok("2a 7!/2!", math.factorial(7) // 2, 2520, 0); ok("2a 6!", math.factorial(6), 720, 0)
b15 = lambda r: math.comb(15, r) * 0.2 ** r * 0.8 ** (15 - r)
ok("2b C(15,3)", math.comb(15, 3), 455, 0); ok("2b 0.8^12", 0.8 ** 12, 0.068719, 1e-6)
ok("2b P(X=3)", round(b15(3), 4), 0.2501, 1e-9)
ok("2b P(X=0)", round(b15(0), 4), 0.0352, 1e-9); ok("2b P(X=1)", round(b15(1), 4), 0.1319, 1e-9)
ok("2b P(X>=2)", round(sum(b15(r) for r in range(2, 16)), 4), 0.8329, 1e-9); ok("2b 1-0.0352-0.1319", 1 - 0.0352 - 0.1319, 0.8329)
ok("2b somme des probabilites", sum(b15(r) for r in range(16)), 1.0, 1e-12)
random.seed(5)
cnt3 = ge2 = 0
for _ in range(200000):
    x = sum(random.random() < 0.2 for _ in range(15))
    cnt3 += x == 3
    ge2 += x >= 2
ok("2b simulation P(X=3)", cnt3 / 200000, 0.2501, 4e-3); ok("2b simulation P(X>=2)", ge2 / 200000, 0.8329, 4e-3)
m15 = sum(r * b15(r) for r in range(16)); v15 = sum(r * r * b15(r) for r in range(16)) - m15 ** 2
ok("2c esperance", m15, 3, 1e-9); ok("2c variance", v15, 2.4, 1e-9)
n_min = next(n for n in range(1, 200) if 1 - 0.8 ** n > 0.99)
ok("2d n minimal", n_min, 21, 0); ok("2d seuil", math.log(0.01) / math.log(0.8), 20.64, 5e-3)
ok("2d 0.8^20", 0.8 ** 20, 0.0115, 5e-5); ok("2d 0.8^21", 0.8 ** 21, 0.0092, 5e-5)
ok("2d ln 0.01", math.log(0.01), -4.6052, 5e-5); ok("2d ln 0.8", math.log(0.8), -0.2231, 5e-5)

# ---- Ex 3 : donnees groupees. Reconstitution des 80 valeurs, une par rang (hypothese de repartition uniforme dans une classe) ----
classes = [(0, 5, 6), (5, 10, 15), (10, 15, 25), (15, 20, 18), (20, 30, 12), (30, 40, 4)]
n = sum(c[2] for c in classes)
ok("3 effectif", n, 80, 0)
mil = [(lo + hi) / 2 for lo, hi, _ in classes]
sfx = sum(f * m for (lo, hi, f), m in zip(classes, mil)); sfx2 = sum(f * m * m for (lo, hi, f), m in zip(classes, mil))
ok("3a sum fx", sfx, 1195); ok("3a moyenne", sfx / n, 14.9375); ok("3a moyenne arrondie", round(sfx / n, 2), 14.94, 1e-9)
ok("3a sum fx2", sfx2, 22700); var = sfx2 / n - (sfx / n) ** 2
ok("3a variance", var, 60.6211, 5e-5); ok("3a ecart-type", math.sqrt(var), 7.79, 5e-3)
ok("3a variance par ecarts", sum(f * (m - sfx / n) ** 2 for (lo, hi, f), m in zip(classes, mil)) / n, var, 1e-9)


def quantile_interpole(p):
    """Position p*n dans la distribution des effectifs cumules (interpolation lineaire dans la classe)."""
    cible = p * n
    cum = 0
    for lo, hi, f in classes:
        if cum + f >= cible:
            return lo + (cible - cum) / f * (hi - lo)
        cum += f


def effectif_cumule(x):
    cum = 0
    for lo, hi, f in classes:
        if x >= hi:
            cum += f
        elif x > lo:
            cum += (x - lo) / (hi - lo) * f
    return cum


ok("3b cumules", [sum(c[2] for c in classes[: i + 1]) for i in range(6)] == [6, 21, 46, 64, 76, 80], True, 0)
ok("3b mediane", quantile_interpole(0.5), 13.8, 1e-9); ok("3b Q1", quantile_interpole(0.25), 9.6667, 5e-5)
ok("3b Q3", quantile_interpole(0.75), 18.8889, 5e-5); ok("3b IQR", quantile_interpole(0.75) - quantile_interpole(0.25), 9.2222, 5e-5)
ok("3b Q1 arrondi", round(quantile_interpole(0.25), 2), 9.67, 1e-9); ok("3b Q3 arrondi", round(quantile_interpole(0.75), 2), 18.89, 1e-9)
ok("3b IQR des arrondis", 18.89 - 9.67, 9.22, 1e-9)
ok("3c F(12)", effectif_cumule(12), 31); ok("3c F(25)", effectif_cumule(25), 70)
ok("3c entre 12 et 25", effectif_cumule(25) - effectif_cumule(12), 39); ok("3c pourcentage", (effectif_cumule(25) - effectif_cumule(12)) / n * 100, 48.75)
ok("3d moyenne", 0.8 * sfx / n, 11.95, 1e-9); ok("3d ecart-type", 0.8 * math.sqrt(var), 6.23, 5e-3)
var_nv = sum(f * (0.8 * m - 0.8 * sfx / n) ** 2 for (lo, hi, f), m in zip(classes, mil)) / n
ok("3d ecart-type recalcule", math.sqrt(var_nv), 0.8 * math.sqrt(var), 1e-9)

# ---- Ex 4 : variable discrete ----
p4, q4 = 0.275, 0.175
loi = {0: 0.10, 1: p4, 2: 0.30, 3: q4, 4: 0.15}
ok("4a somme", sum(loi.values()), 1.0, 1e-12); ok("4a E(X)", sum(x * pr for x, pr in loi.items()), 2.0, 1e-12)
# resolution du systeme par force brute sur une grille fine : une seule solution
sol = [(p / 1000, q / 1000) for p in range(0, 451) for q in range(0, 451)
       if abs(p / 1000 + q / 1000 - 0.45) < 1e-9 and abs(p / 1000 + 3 * q / 1000 - 0.8) < 1e-9]
vrai("4a solution unique", sol == [(0.275, 0.175)])
EX2 = sum(x * x * pr for x, pr in loi.items())
ok("4b E(X2)", EX2, 5.45, 1e-12); var4 = EX2 - 4
ok("4b Var", var4, 1.45, 1e-12); ok("4b Var par ecarts", sum((x - 2) ** 2 * pr for x, pr in loi.items()), 1.45, 1e-12)
ok("4b ecart-type", math.sqrt(var4), 1.20, 5e-3)
EY = sum((1.5 * x - 2) * pr for x, pr in loi.items())
ok("4c E(Y)", EY, 1.0, 1e-12); ok("4c Var(Y)", sum(((1.5 * x - 2) - EY) ** 2 * pr for x, pr in loi.items()), 3.2625, 1e-12)
ok("4c 2.25 x 1.45", 2.25 * 1.45, 3.2625, 1e-12)
ok("4d P(Y>0)", sum(pr for x, pr in loi.items() if 1.5 * x - 2 > 0), 0.625, 1e-12)
vrai("4d Y>0 equivaut a X>=2", all((1.5 * x - 2 > 0) == (x >= 2) for x in loi))
ok("4d conditionnelle", sum(pr for x, pr in loi.items() if x >= 2) / sum(pr for x, pr in loi.items() if x >= 1), 25 / 36, 1e-12)
ok("4d arrondi", round(25 / 36, 4), 0.6944, 1e-9); ok("4d P(X>=1)", 1 - 0.10, 0.90)

# ---- Ex 5 : variable continue, integration numerique ----
k5 = 3 / 64
f5 = lambda x: k5 * x * x * (4 - x)
ok("5a integrale totale", integrer(f5, 0, 4), 1.0, 1e-9)
ok("5a 64/3", 256 / 3 - 64, 64 / 3, 1e-12); ok("5a k", 1 / (64 / 3), 3 / 64, 1e-12)
vrai("5a densite positive", all(f5(i / 100) >= 0 for i in range(401)))
E5 = integrer(lambda x: x * f5(x), 0, 4); E52 = integrer(lambda x: x * x * f5(x), 0, 4)
ok("5b E(X)", E5, 2.4, 1e-8); ok("5b E(X2)", E52, 6.4, 1e-8); ok("5b Var", E52 - E5 ** 2, 0.64, 1e-8)
ok("5b 4^4 - 4^5/5", 256 - 1024 / 5, 51.2, 1e-9); ok("5b E(X) exact", 3 / 64 * 51.2, 2.4, 1e-12)
ok("5b 819.2 - 682.67", 4 * 1024 / 5 - 4096 / 6, 136.5333, 5e-5); ok("5b E(X2) exact", 3 / 64 * (4 * 1024 / 5 - 4096 / 6), 6.4, 1e-9)
ok("5c P(X>3)", integrer(f5, 3, 4), 67 / 256, 1e-9); ok("5c arrondi", round(67 / 256, 4), 0.2617, 1e-9)
ok("5c borne x=3", 36 - 81 / 4, 63 / 4, 1e-12); ok("5c produit", 3 / 64 * (64 / 3 - 63 / 4), 67 / 256, 1e-12)
g5 = lambda m: 3 * m ** 4 - 16 * m ** 3 + 128
ok("5d F(m) = m^3/16 - 3m^4/256", integrer(f5, 0, 2.7), 2.7 ** 3 / 16 - 3 * 2.7 ** 4 / 256, 1e-9)
ok("5d g(2.4)", g5(2.4), 6.3488, 1e-9); ok("5d g(2.5)", g5(2.5), -4.8125, 1e-9)
ok("5d 3(33.1776)", 3 * 33.1776, 99.5328, 1e-9); ok("5d 16(13.824)", 16 * 13.824, 221.184, 1e-9)
lo, hi = 2.4, 2.5
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (lo, mid) if g5(lo) * g5(mid) <= 0 else (mid, hi)
ok("5d racine", lo, 2.457, 5e-4); ok("5d F(m)=1/2 a la racine", integrer(f5, 0, lo), 0.5, 1e-9)
ok("5d equation equivalente", (2.5 ** 3 / 16 - 3 * 2.5 ** 4 / 256 - 0.5) * 256, -g5(2.5), 1e-9)

# ---- Ex 6 : loi normale ; tables par math.erf, simulation ----
for z, att in ((1.5, 0.9332), (1.25, 0.8944), (1.0, 0.8413), (1.58, 0.9429), (1.2816, 0.9000)):
    ok(f"6 table Phi({z})", round(Phi(z), 4), att, 1e-9)
ok("6a z", (31 - 25) / 4, 1.5); ok("6a P(T>31)", round(1 - round(Phi(1.5), 4), 4), 0.0668, 1e-9); ok("6a P(T>31) exact", 1 - Phi(1.5), 0.0668, 5e-5)
ok("6a z bornes", ((21 - 25) / 4, (30 - 25) / 4) == (-1.0, 1.25), True, 0)
ok("6a P(21<T<30)", Phi(1.25) - Phi(-1), 0.7357, 5e-5); ok("6a par tables", round(0.8944 - (1 - 0.8413), 4), 0.7357, 1e-9)
ok("6a integration", integrer(lambda t: math.exp(-0.5 * ((t - 25) / 4) ** 2) / (4 * math.sqrt(2 * math.pi)), 21, 30), 0.7357, 5e-5)
random.seed(8)
sim = [random.gauss(25, 4) for _ in range(300000)]
ok("6a simulation (i)", sum(t > 31 for t in sim) / len(sim), 0.0668, 3e-3); ok("6a simulation (ii)", sum(21 < t < 30 for t in sim) / len(sim), 0.7357, 5e-3)
# 6b : le quantile 0.90 par bissection sur Phi
lo, hi = 0.0, 4.0
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if Phi(mid) < 0.90 else (lo, mid)
ok("6b z de 0.90", lo, 1.2816, 5e-5); ok("6b t", 25 + 4 * 1.2816, 30.1264, 1e-9); ok("6b t arrondi", round(25 + 4 * 1.2816, 2), 30.13, 1e-9)
ok("6b controle P(T>t)", 1 - Phi((30.1264 - 25) / 4), 0.10, 1e-5)
ok("6c E(X)", 150 * 0.4, 60, 1e-9); ok("6c Var(X)", 150 * 0.4 * 0.6, 36, 1e-9); ok("6c nq", 150 * 0.6, 90, 1e-9)
ok("6c Var par somme", sum((k - 60) ** 2 * math.comb(150, k) * 0.4 ** k * 0.6 ** (150 - k) for k in range(151)), 36, 1e-6)
ok("6d z", (69.5 - 60) / 6, 1.5833, 5e-5); ok("6d z arrondi", round((69.5 - 60) / 6, 2), 1.58, 1e-9)
ok("6d P par tables", round(1 - 0.9429, 4), 0.0571, 1e-9); ok("6d P exact normal", 1 - Phi(9.5 / 6), 0.0567, 1e-3)
exact6 = sum(math.comb(150, k) * 0.4 ** k * 0.6 ** (150 - k) for k in range(70, 151))
ok("6d binomiale exacte proche", exact6, 0.0571, 2e-3)
ok("6d sans correction", 1 - Phi((70 - 60) / 6), 0.0478, 5e-4); vrai("6d sans correction plus petit", 1 - Phi(10 / 6) < exact6)

# ---- Ex 7 : Poisson et binomiale ----
ok("7a e^-2.5", math.exp(-2.5), 0.082085, 1e-6); ok("7a P(4)", round(poisson(2.5, 4), 4), 0.1336, 1e-9)
ok("7a P(4) calcul", math.exp(-2.5) * 39.0625 / 24, 0.1336, 5e-5)
ok("7a P(<=2)", round(sum(poisson(2.5, r) for r in range(3)), 4), 0.5438, 1e-9); ok("7a 1+2.5+3.125", 1 + 2.5 + 6.25 / 2, 6.625, 1e-12)
ok("7a somme complete", sum(poisson(2.5, r) for r in range(80)), 1.0, 1e-12)
random.seed(21)


def tirage_poisson(lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= random.random()
        if p <= L:
            return k
        k += 1


s7 = [tirage_poisson(2.5) for _ in range(200000)]
ok("7a simulation P(4)", sum(x == 4 for x in s7) / len(s7), 0.1336, 3e-3); ok("7a simulation P(<=2)", sum(x <= 2 for x in s7) / len(s7), 0.5438, 4e-3)
ok("7b e^-5", math.exp(-5), 0.006738, 1e-6); ok("7b P(0)", round(poisson(5, 0), 4), 0.0067, 1e-9)
ok("7b P(>=2)", round(1 - poisson(5, 0) - poisson(5, 1), 4), 0.9596, 1e-9); ok("7b 6e^-5", 6 * math.exp(-5), 0.0404, 5e-5)
s7b = [tirage_poisson(5.0) for _ in range(200000)]
ok("7b simulation P(0)", sum(x == 0 for x in s7b) / len(s7b), 0.0067, 1.5e-3); ok("7b simulation P(>=2)", sum(x >= 2 for x in s7b) / len(s7b), 0.9596, 4e-3)
ok("7c np", 200 * 0.015, 3, 1e-12); ok("7c P(2) Poisson", round(poisson(3, 2), 4), 0.2240, 1e-9)
ok("7c e^-3", math.exp(-3), 0.049787, 1e-6); ok("7c e^-3 x 4.5", math.exp(-3) * 4.5, 0.2240, 5e-5)
exact7 = math.comb(200, 2) * 0.015 ** 2 * 0.985 ** 198
ok("7d P(2) binomiale", round(exact7, 4), 0.2246, 1e-9); ok("7d C(200,2)", math.comb(200, 2), 19900, 0)
ok("7d 0.985^198", 0.985 ** 198, 0.050162, 5e-7); ok("7d produit", 19900 * 0.000225 * 0.050162, 0.2246, 5e-5)
ok("7d difference", round(exact7, 4) - round(poisson(3, 2), 4), 0.0006, 1e-9)
random.seed(33)
c2 = sum(sum(random.random() < 0.015 for _ in range(200)) == 2 for _ in range(60000))
ok("7d simulation P(Y=2)", c2 / 60000, 0.2246, 6e-3)

# ---- Ex 8 : correlation et regression, par deux voies (sommes brutes puis ecarts a la moyenne) ----
xs = [12, 15, 19, 22, 26, 30, 33, 38]; ys = [34, 36, 44, 41, 55, 52, 63, 60]
n8 = len(xs)
ok("8a sum x", sum(xs), 195, 0); ok("8a sum y", sum(ys), 385, 0); ok("8a sum x2", sum(a * a for a in xs), 5323, 0)
ok("8a sum y2", sum(b * b for b in ys), 19367, 0); ok("8a sum xy", sum(a * b for a, b in zip(xs, ys)), 10035, 0)
mx, my = sum(xs) / n8, sum(ys) / n8
Sxx = sum(a * a for a in xs) - sum(xs) ** 2 / n8; Syy = sum(b * b for b in ys) - sum(ys) ** 2 / n8; Sxy = sum(a * b for a, b in zip(xs, ys)) - sum(xs) * sum(ys) / n8
ok("8a Sxx", Sxx, 569.875); ok("8a Syy", Syy, 838.875); ok("8a Sxy", Sxy, 650.625)
ok("8a Sxx par ecarts", sum((a - mx) ** 2 for a in xs), Sxx, 1e-9); ok("8a Syy par ecarts", sum((b - my) ** 2 for b in ys), Syy, 1e-9)
ok("8a Sxy par ecarts", sum((a - mx) * (b - my) for a, b in zip(xs, ys)), Sxy, 1e-9)
r8 = Sxy / math.sqrt(Sxx * Syy)
ok("8a r", round(r8, 4), 0.9410, 1e-9); ok("8a racine", math.sqrt(Sxx * Syy), 691.41, 5e-3)
ok("8a r par covariance", (sum(a * b for a, b in zip(xs, ys)) / n8 - mx * my) / (math.sqrt(sum(a * a for a in xs) / n8 - mx ** 2) * math.sqrt(sum(b * b for b in ys) / n8 - my ** 2)), r8, 1e-12)
b8 = Sxy / Sxx; a8 = my - b8 * mx
ok("8b gradient", b8, 1.1417, 5e-5); ok("8b x moyen", mx, 24.375); ok("8b y moyen", my, 48.125)
ok("8b ordonnee", a8, 20.296, 5e-4); ok("8b ordonnee arrondie", round(a8, 2), 20.30, 1e-9); ok("8b b arrondi", round(b8, 3), 1.142, 1e-9)
ok("8b 1.1417 x 24.375", 1.1417 * 24.375, 27.829, 5e-4)
# moindres carres : aucune droite voisine ne fait mieux (balayage de la somme des carres des residus)
sse = lambda a, b: sum((y - a - b * x) ** 2 for x, y in zip(xs, ys))
vrai("8b minimum de la somme des carres", all(sse(a8, b8) <= sse(a8 + da, b8 + db) + 1e-9 for da in (-0.5, 0, 0.5) for db in (-0.05, 0, 0.05)))
ok("8c estimation", 20.30 + 1.142 * 28, 52.276, 1e-9); ok("8c estimation exacte", a8 + b8 * 28, 52.26, 5e-2)
ok("8c 1.142 x 28", 1.142 * 28, 31.976, 1e-9); ok("8c entier", round(a8 + b8 * 28), 52, 0)
vrai("8c 60 hors de l'etendue", not (min(xs) <= 60 <= max(xs)) and min(xs) == 12 and max(xs) == 38)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e_ in ecarts:
        print("  -", e_)
    sys.exit(1)
print("0 ecart")
