r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Further Mathematics Paper 3 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_furthermaths_p3.py

Chaque reponse finale et chaque valeur intermediaire citee dans le corrige est recalculee par une autre voie (simulation, integration numerique,
derivation numerique, substitution). Sortie 0 s'il n'y a aucun ecart.
"""
import math
import sys

ecarts = []
nverif = 0


def ok(nom, valeur, attendu, tol=1e-6):
    global nverif
    nverif += 1
    if abs(valeur - attendu) > tol:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def sub(u, v):
    return tuple(a - b for a, b in zip(u, v))


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def integrer(f, a, b, n=200000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


# ---- Ex 1 ----
F1, F2, F3 = (3, -2, 1), (-1, 4, 2), (2, 1, -5)
R = tuple(a + b + c for a, b, c in zip(F1, F2, F3))
assert R == (4, 3, -2), R
ok("1a module", math.sqrt(dot(R, R)), math.sqrt(29)); ok("1a module approx", math.sqrt(29), 5.39, 5e-3)
F = (2, -3, 1); A = (1, 2, -1); B = (4, 0, 2); P = (0, 1, 1)
M = cross(A, F)
assert M == (-1, -3, -7), M
ok("1b premiere composante", 2 * 1 - (-1) * (-3), -1)
d = sub(B, A)
assert d == (3, -2, 3), d
ok("1c travail", dot(F, d), 15)
MP = cross(sub(A, P), F)
assert sub(A, P) == (1, 1, -2) and MP == (-5, -5, -5), MP
ok("1d perpendiculaire", dot(MP, F), 0)
ok("1b perpendiculaire", dot(M, F), 0)

# ---- Ex 2 ----
def f2(x, y):
    return x + y * y


y1 = 1 + 0.1 * f2(0, 1)
ok("2a y1", y1, 1.1); ok("2a f(0.1,1.1)", f2(0.1, 1.1), 1.31)
y2 = y1 + 0.1 * f2(0.1, y1)
ok("2a y2", y2, 1.231)
ok("2b predicteur", y1, 1.1)
ok("2b correcteur", 1 + 0.05 * (f2(0, 1) + f2(0.1, 1.1)), 1.1155)
g = lambda x: 1 / (1 + x * x)
xs = [0, 0.25, 0.5, 0.75, 1]
ok("2c f(0.25)", g(0.25), 0.941176, 1e-6); ok("2c f(0.5)", g(0.5), 0.8); ok("2c f(0.75)", g(0.75), 0.64)
S4 = 0.25 / 3 * (g(0) + g(1) + 4 * (g(0.25) + g(0.75)) + 2 * g(0.5))
ok("2c Simpson", S4, 0.78539, 5e-6); ok("2c arrondi", round(S4, 4), 0.7854, 1e-9)
ok("2c somme", 1 + 0.5 + 4 * (g(0.25) + g(0.75)) + 2 * g(0.5), 9.424706, 1e-6)
ok("2c pi", round(4 * S4, 4), 3.1416, 1e-9)
ok("2c valeur exacte", integrer(g, 0, 1), math.pi / 4, 1e-9)

# ---- Ex 3 ----
A3, w = 0.4, 3.0
ok("3a vmax", A3 * w, 1.2); ok("3a amax", A3 * w * w, 3.6)
ok("3a v(0.2)", w * math.sqrt(A3 ** 2 - 0.2 ** 2), math.sqrt(1.08)); ok("3a v approx", math.sqrt(1.08), 1.04, 5e-3)
t = math.asin(0.5) / w
ok("3b t", t, math.pi / 18); ok("3b t approx", t, 0.175, 5e-4)
ok("3b x(t)", A3 * math.sin(w * t), 0.2)


def x3(t):
    return math.exp(-2 * t) * (2 * math.cos(3 * t) + 4 / 3 * math.sin(3 * t))


ok("3c x(0)", x3(0), 2)
h = 1e-6
ok("3c x'(0)", (x3(h) - x3(-h)) / (2 * h), 0, 1e-5)
for tt in (0.3, 0.9, 2.0):
    x1 = (x3(tt + h) - x3(tt - h)) / (2 * h)
    x2 = (x3(tt + h) - 2 * x3(tt) + x3(tt - h)) / (h * h)
    ok("3c equation", x2 + 4 * x1 + 13 * x3(tt), 0, 1e-3)
ok("3c discriminant", 16 - 52, -36)
ok("3c periode", 2 * math.pi / 3, 2.09, 5e-3)

# ---- Ex 4 ----
g_, k = 9.8, 0.4
ok("4a k", 0.08 / 0.2, 0.4)
v4 = lambda t: 24.5 * (1 - math.exp(-0.4 * t))
for tt in (0.5, 1.7, 4.0):  # dv/dt = 9.8 - 0.4 v
    ok("4a equation", (v4(tt + 1e-6) - v4(tt - 1e-6)) / 2e-6, 9.8 - 0.4 * v4(tt), 1e-5)
ok("4a v(0)", v4(0), 0)
ok("4b terminale", g_ / k, 24.5); ok("4b grand t", v4(60), 24.5, 1e-8)
tb = math.log(2) / 0.4
ok("4b v(t)", v4(tb), 12.25); ok("4b t approx", tb, 1.73, 5e-3)
dist = integrer(v4, 0, tb)
ok("4c distance", dist, 24.5 * (tb + (math.exp(-0.4 * tb) - 1) / 0.4), 1e-6)
ok("4c valeur", dist, 11.83, 5e-3); ok("4c facteur", tb - 1.25, 0.4829, 1e-4)

# ---- Ex 5 ----
par, nor = 10 * math.cos(math.radians(60)), 10 * math.sin(math.radians(60))
ok("5a parallele", par, 5); ok("5a normale", nor, 5 * math.sqrt(3))
nor2 = 0.6 * nor
ok("5a rebond", nor2, 3 * math.sqrt(3))
ok("5a vitesse", math.hypot(par, nor2), math.sqrt(52)); ok("5a vitesse approx", math.sqrt(52), 7.21, 5e-3)
ok("5a angle", math.degrees(math.atan2(nor2, par)), 46.1, 5e-2)
u = 8 * math.cos(math.radians(30)); p = 8 * math.sin(math.radians(30))
ok("5b u", u, 4 * math.sqrt(3)); ok("5b p", p, 4)
e = 0.5
vB = u * (1 + e) / 2
vA = u * (1 - e) / 2
ok("5b somme", vA + vB, u); ok("5b restitution", vB - vA, e * u)
ok("5b vB", vB, 3 * math.sqrt(3)); ok("5b vA", vA, math.sqrt(3)); ok("5b vB approx", vB, 5.20, 5e-3)
ok("5b vitesse de A", math.hypot(vA, p), math.sqrt(19)); ok("5b vitesse de A approx", math.sqrt(19), 4.36, 5e-3)
m = 0.5
ec0 = 0.5 * m * 64
ec1A = 0.5 * m * (vA ** 2 + p ** 2); ec1B = 0.5 * m * vB ** 2
ok("5c EC initiale", ec0, 16); ok("5c EC A", ec1A, 4.75); ok("5c EC B", ec1B, 6.75); ok("5c perte", ec0 - ec1A - ec1B, 4.5)

# ---- Ex 6 ----
r6 = lambda t: 4 * t
th6 = lambda t: t * t
h = 1e-5
d = lambda f, t: (f(t + h) - f(t - h)) / (2 * h)
d2 = lambda f, t: (f(t + h) - 2 * f(t) + f(t - h)) / (h * h)
t = 1.0
rd, thd = d(r6, t), d(th6, t)
ok("6a vr", rd, 4, 1e-6); ok("6a vtheta", r6(t) * thd, 8, 1e-5)
ok("6a vitesse", math.hypot(rd, r6(t) * thd), 4 * math.sqrt(5), 1e-5); ok("6a vitesse approx", 4 * math.sqrt(5), 8.94, 5e-3)
rdd, thdd = d2(r6, t), d2(th6, t)
ar = rdd - r6(t) * thd ** 2
at = r6(t) * thdd + 2 * rd * thd
ok("6b ar", ar, -16, 1e-3); ok("6b atheta", at, 24, 1e-3)
ok("6b module", math.hypot(ar, at), math.sqrt(832), 1e-3); ok("6b module approx", math.sqrt(832), 28.8, 5e-2)
at2 = (1 / r6(t)) * (d(lambda s: r6(s) ** 2 * d(th6, s), t))  # forme equivalente (1/r) d(r^2 theta')/dt
ok("6b forme equivalente", at2, 24, 1e-2)
ok("6c angle", math.degrees(math.atan(8 / 4)), 63.4, 5e-2)

# ---- Ex 7 ----
M7, L = 0.9, 1.0
IG = M7 * L * L / 12
ok("7a IG", IG, 0.075); ok("7a IA", IG + M7 * 0.5 ** 2, 0.3)
ok("7a IA direct M L^2/3", M7 * L * L / 3, 0.3)
w2 = M7 * 9.8 * 0.5 / 0.3
ok("7b omega2", w2, 14.7); T7 = 2 * math.pi / math.sqrt(w2)
ok("7b periode", T7, 1.64, 5e-3)
I2 = 0.3 + 0.3 * 1 ** 2
h2 = (0.9 * 0.5 + 0.3 * 1) / 1.2
ok("7c I", I2, 0.6); ok("7c masse", 0.9 + 0.3, 1.2); ok("7c h", h2, 0.625)
w2b = 1.2 * 9.8 * h2 / I2
ok("7c omega2", w2b, 12.25); ok("7c omega", math.sqrt(w2b), 3.5)
T7b = 2 * math.pi / 3.5
ok("7c periode", T7b, 4 * math.pi / 7); ok("7c periode approx", T7b, 1.80, 5e-3)
# simulation numerique du pendule compose (petites oscillations) : la periode simulee doit etre proche de la formule
def periode_simulee(I, Mtot, hh, theta0=0.01):
    dt, th, om, t, croisements = 1e-4, theta0, 0.0, 0.0, []
    prev = th
    while len(croisements) < 3 and t < 20:
        om += -(Mtot * 9.8 * hh / I) * math.sin(th) * dt
        th += om * dt
        t += dt
        if prev > 0 >= th:
            croisements.append(t)
        prev = th
    return croisements[2] - croisements[1]


ok("7b simulation", periode_simulee(0.3, 0.9, 0.5), T7, 5e-3)
ok("7c simulation", periode_simulee(0.6, 1.2, 0.625), T7b, 5e-3)

# ---- Ex 8 ----
k8 = 1 / sum(x + 1 for x in range(5))
ok("8a k", k8, 1 / 15)
EX = sum(x * k8 * (x + 1) for x in range(5)); EX2 = sum(x * x * k8 * (x + 1) for x in range(5))
ok("8b E(X)", EX, 8 / 3); ok("8c E(X2)", EX2, 26 / 3); ok("8c Var", EX2 - EX ** 2, 14 / 9)
ok("8c Var formule", sum((x - EX) ** 2 * k8 * (x + 1) for x in range(5)), 14 / 9)
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
ok("8d z", (49 - 50) / 0.8, -1.25)
ok("8d Phi(1.25) table", round(Phi(1.25), 4), 0.8944, 1e-9)
ok("8d probabilite", round(Phi(-1.25), 4), 0.1056, 1e-9); ok("8d 1-0.8944", 1 - 0.8944, 0.1056)
ok("8e 0.9^10", round(0.9 ** 10, 4), 0.3487, 1e-9); ok("8e P(X=1)", round(10 * 0.1 * 0.9 ** 9, 4), 0.3874, 1e-9)
p2 = 1 - sum(math.comb(10, r) * 0.1 ** r * 0.9 ** (10 - r) for r in (0, 1))
ok("8e P(X>=2)", round(p2, 4), 0.2639, 1e-9)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e_ in ecarts:
        print("  -", e_)
    sys.exit(1)
print("0 ecart")
