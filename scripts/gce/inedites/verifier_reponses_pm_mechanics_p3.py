r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Pure Mathematics with Mechanics Paper 3 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_pm_mechanics_p3.py

Chaque reponse finale et chaque valeur intermediaire citee dans le corrige est recalculee par une autre voie (integration numerique, derivation
numerique, simulation pas a pas, resolution de racines par bissection, substitution). Sortie 0 s'il n'y a aucun ecart.
"""
import math
import sys

ecarts = []
nverif = 0
g = 9.8


def ok(nom, valeur, attendu, tol=1e-6):
    global nverif
    nverif += 1
    if abs(valeur - attendu) > tol:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def bissection(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        fm = f(m)
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def d1(f, t, h=1e-5):
    return (f(t + h) - f(t - h)) / (2 * h)


def integrer(f, a, b, n=20000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


# ---- Ex 1 : cinematique vectorielle ----
rx = lambda t: t ** 3 - 6 * t
ry = lambda t: 4 * t - t * t
vx, vy = (lambda t: d1(rx, t)), (lambda t: d1(ry, t))
ax, ay = (lambda t: d1(vx, t, 1e-3)), (lambda t: d1(vy, t, 1e-3))
ok("1a vx(2)", vx(2), 6, 1e-6); ok("1a vy(2)", vy(2), 0, 1e-6)
ok("1a ax(2)", ax(2), 12, 1e-3); ok("1a ay(2)", ay(2), -2, 1e-3)
ok("1a vitesse", math.hypot(vx(2), vy(2)), 6, 1e-6)
ok("1a formule vx", vx(1.7), 3 * 1.7 ** 2 - 6, 1e-6); ok("1a formule vy", vy(1.7), 4 - 3.4, 1e-6)
tb = bissection(lambda t: vx(t), 0.1, 3)
ok("1b t", tb, math.sqrt(2), 1e-6); ok("1b t approx", tb, 1.41, 5e-3)
ok("1b vitesse", abs(vy(tb)), 4 - 2 * math.sqrt(2), 1e-6); ok("1b vitesse approx", abs(vy(tb)), 1.17, 5e-3)
# bateau : acceleration (2t, -3), v(0)=(3,6), r(0)=(0,10) : integration numerique pas a pas (Simpson sur l'acceleration puis la vitesse)
Bvx = lambda t: 3 + integrer(lambda s: 2 * s, 0, t, 200)
Bvy = lambda t: 6 + integrer(lambda s: -3, 0, t, 200)
ok("1c vx formule", Bvx(2.5), 2.5 ** 2 + 3, 1e-9); ok("1c vy formule", Bvy(2.5), 6 - 7.5, 1e-9)
Bx3 = 0 + integrer(lambda s: s * s + 3, 0, 3, 600)
By3 = 10 + integrer(lambda s: 6 - 3 * s, 0, 3, 600)
ok("1c x(3)", Bx3, 18, 1e-9); ok("1c y(3)", By3, 14.5, 1e-9)
ok("1c primitive x", 27 / 3 + 9, 18); ok("1c primitive y", 18 - 1.5 * 9 + 10, 14.5)
ok("1d vy(2)", 6 - 3 * 2, 0)
Bx2 = integrer(lambda s: s * s + 3, 0, 2, 600); By2 = 10 + integrer(lambda s: 6 - 3 * s, 0, 2, 600)
ok("1d x(2)", Bx2, 26 / 3, 1e-9); ok("1d y(2)", By2, 16, 1e-9)
ok("1d distance", math.hypot(Bx2, By2), math.sqrt(676 / 9 + 256), 1e-9); ok("1d distance approx", math.hypot(Bx2, By2), 18.2, 5e-2)

# ---- Ex 2 : acceleration constante ----
a2 = (22 ** 2 - 8 ** 2) / (2 * 150)
ok("2a a", a2, 1.4); ok("2a t", (22 - 8) / a2, 10)
ok("2a controle distance", 8 * 10 + 0.5 * a2 * 100, 150)
# autobus : simulation pas a pas
dt = 1e-3; t = 0.0; v = 0.0; x = 0.0; vmax = 0.0
while t < 85 - 1e-9:
    acc = 0.8 if t < 15 else (0 if t < 75 else -12 / 10)
    v += acc * dt; x += v * dt; t += dt; vmax = max(vmax, v)
ok("2b vitesse max", vmax, 12, 5e-3); ok("2b distance", x, 870, 1.0); ok("2b vitesse finale", v, 0, 5e-3)
ok("2b aires", 0.5 * 15 * 12 + 60 * 12 + 0.5 * 10 * 12, 870); ok("2b vitesse moyenne", 870 / 85, 10.235, 5e-4); ok("2b arrondi", 870 / 85, 10.2, 5e-2)
ok("2b decel", 12 / 10, 1.2)
# poursuite : simulation du camion et de la moto
dt = 1e-3; t = 0.0; xm = 0.0; vm = 0.0; trouve = None; t_atteint = None; x_atteint = None
while t < 100:
    if t >= 8:
        if vm < 30:
            vm = min(30.0, vm + 3 * dt)
        xm += vm * dt
        if t_atteint is None and vm >= 30 - 1e-9:
            t_atteint = t - 8; x_atteint = xm
    xl = 20 * t
    if t > 8 and xm >= xl:
        trouve = (t - 8, xm); break
    t += dt
ok("2c temps de la moto", trouve[0], 31, 5e-3); ok("2c distance", trouve[1], 780, 0.2)
ok("2c temps pour 30 m/s", t_atteint, 10, 5e-3); ok("2c distance d'acceleration", x_atteint, 150, 0.1)
ok("2c camion a 18 s", 20 * 18, 360); ok("2c equation", 20 * 31 + 160, 150 + 30 * 21); ok("2c 20*39", 20 * 39, 780)

# ---- Ex 3 : particules liees ----
mu, mA, mB = 0.2, 4.0, 3.0
F3 = mu * mA * g
ok("3a frottement", F3, 7.84)
a3 = (mB * g - F3) / (mA + mB)
ok("3a a", a3, 3.08)
T3 = mB * (g - a3)
ok("3a T", T3, 20.16); ok("3a T par A", F3 + mA * a3, 20.16)
# simulation : B tombe de 1,5 m
dt = 1e-5; t = 0.0; x = 0.0; v = 0.0
while x < 1.5:
    v += a3 * dt; x += v * dt; t += dt
ok("3b v", v, math.sqrt(9.24), 5e-3); ok("3b v2", v * v, 9.24, 5e-3); ok("3b v approx", v, 3.04, 5e-3)
dist2 = 0.0
while v > 0:
    v -= mu * g * dt; dist2 += max(v, 0) * dt
ok("3c distance de glissement", dist2, 9.24 / 3.92, 5e-3); ok("3c deceleration", F3 / mA, 1.96)
ok("3c 9.24/3.92", 9.24 / 3.92, 2.357, 5e-4); ok("3c total", 1.5 + 9.24 / 3.92, 3.857, 5e-4); ok("3c total arrondi", 1.5 + dist2, 3.86, 1e-2)

# ---- Ex 4 : projectiles ----
u, h0 = 20.0, 8.1
sinA, cosA = 0.6, 0.8
ok("4a tan", sinA / cosA, 0.75); ok("4a sin2+cos2", sinA ** 2 + cosA ** 2, 1)
ux, uy = u * cosA, u * sinA
ok("4a ux", ux, 16); ok("4a uy", uy, 12)
yh = lambda t: h0 + uy * t - 0.5 * g * t * t
tg = bissection(yh, 0.5, 6)
ok("4a t", tg, 3, 1e-9); ok("4a x", ux * tg, 48, 1e-8)
ok("4a discriminant", 144 + 4 * 4.9 * 8.1, 302.76, 1e-9); ok("4a racine", math.sqrt(302.76), 17.4, 1e-9)
vyg = uy - g * tg
ok("4b vy", vyg, -17.4, 1e-8); ok("4b vitesse", math.hypot(ux, vyg), math.sqrt(558.76), 1e-8); ok("4b vitesse approx", math.hypot(ux, vyg), 23.6, 5e-2)
ok("4b angle", math.degrees(math.atan(17.4 / 16)), 47.4, 5e-2)
# controle de la vitesse a l'arrivee par l'energie : v^2 = u^2 + 2 g h
ok("4b energie", math.sqrt(u * u + 2 * g * h0), math.hypot(ux, vyg), 1e-8)
tm = 32 / ux
ok("4c t", tm, 2); ok("4c hauteur", yh(tm), 12.5, 1e-9); ok("4c marge", yh(tm) - 12, 0.5, 1e-9)
tsommet = uy / g
ok("4c a la descente", tm - tsommet > 0, True)

# ---- Ex 5 : chocs ----
mA5, mB5, uA, uB, e5 = 3.0, 2.0, 6.0, 2.0, 0.5
# resolution par balayage : on cherche vA tel que les deux equations soient satisfaites
def residu(vA):
    vB = (mA5 * uA + mB5 * uB - mA5 * vA) / mB5
    return (vB - vA) - e5 * (uA - uB)
vA5 = bissection(residu, -50, 50)
vB5 = (mA5 * uA + mB5 * uB - mA5 * vA5) / mB5
ok("5a quantite de mouvement", mA5 * uA + mB5 * uB, 22); ok("5a vA", vA5, 3.6, 1e-9); ok("5a vB", vB5, 5.6, 1e-9)
ok("5a separation", vB5 - vA5, 2, 1e-9)
# controle par la formule du centre de masse : v = vG + e (vG - u)
vG = (mA5 * uA + mB5 * uB) / (mA5 + mB5)
ok("5a formule vA", vG - e5 * mB5 / (mA5 + mB5) * (uA - uB), 3.6, 1e-9); ok("5a formule vB", vG + e5 * mA5 / (mA5 + mB5) * (uA - uB), 5.6, 1e-9)
ec0 = 0.5 * mA5 * uA ** 2 + 0.5 * mB5 * uB ** 2
ec1A, ec1B = 0.5 * mA5 * vA5 ** 2, 0.5 * mB5 * vB5 ** 2
ok("5b EC avant", ec0, 58); ok("5b EC A", ec1A, 19.44, 1e-9); ok("5b EC B", ec1B, 31.36, 1e-9); ok("5b total apres", ec1A + ec1B, 50.8, 1e-9)
ok("5b perte", ec0 - ec1A - ec1B, 7.2, 1e-9)
ok("5b formule de la perte", 0.5 * (mA5 * mB5 / (mA5 + mB5)) * (1 - e5 ** 2) * (uA - uB) ** 2, 7.2, 1e-9)
ok("5c e", 2.8 / vB5, 0.5, 1e-9); ok("5c impulsion", mB5 * (vB5 + 2.8), 16.8, 1e-9)
ok("5c impulsion par difference", mB5 * 2.8 - mB5 * (-vB5), 16.8, 1e-9)

# ---- Ex 6 : travail, energie, puissance ----
M6, P6, R6 = 5000.0, 60000.0, 2000.0
ok("6a vmax", P6 / R6, 30)
# vitesse limite par simulation de v' = (P/v - R)/M
v = 5.0; dt = 1e-3
for _ in range(600000):
    v += (P6 / v - R6) / M6 * dt
ok("6a vmax simulee", v, 30, 5e-3)
ok("6a force a 15", P6 / 15, 4000); ok("6a a", (P6 / 15 - R6) / M6, 0.4)
s_t = 1 / 20
ok("6b composante du poids", M6 * g * s_t, 2450); F6 = R6 + M6 * g * s_t
ok("6b F", F6, 4450); ok("6b puissance", F6 * 12, 53400); ok("6b kW", F6 * 12 / 1000, 53.4)
ok("6b vmax", P6 / F6, 13.483, 5e-4); ok("6b vmax arrondi", P6 / F6, 13.5, 2e-2)
# simulation de la montee a pleine puissance : vitesse limite
v = 5.0
for _ in range(600000):
    v += (P6 / v - F6) / M6 * dt
ok("6b vmax simulee", v, P6 / F6, 5e-3)
ok("6c EC", 0.5 * M6 * 144, 360000); d6 = 0.5 * M6 * 144 / F6
ok("6c d", d6, 80.9, 5e-2)
# simulation : moteur coupe, deceleration constante (F6/M6)
v = 12.0; x = 0.0; t = 0.0; dt = 1e-5
while v > 0:
    v -= F6 / M6 * dt; x += max(v, 0) * dt; t += dt
ok("6c distance simulee", x, d6, 5e-3); ok("6d deceleration", F6 / M6, 0.89, 1e-12); ok("6d temps simule", t, 12 / 0.89, 1e-3); ok("6d t approx", 12 / 0.89, 13.5, 5e-2)
ok("6d controle (c)", 0.5 * 12 * (12 / 0.89), d6, 1e-6)

# ---- Ex 7 : centre de masse et equilibre ----
# lamina : on echantillonne les points du rectangle 12 x 8 prive de [6,12] x [4,8] (moyenne sur une grille fine)
nx, ny = 12 * 100, 8 * 100
sx = sy = n = 0
for i in range(nx):
    x = (i + 0.5) / 100
    for j in range(ny):
        y = (j + 0.5) / 100
        if x >= 6 and y >= 4:
            continue
        sx += x; sy += y; n += 1
xb, yb = sx / n, sy / n
ok("7a aire", n / 10000, 72, 1e-9); ok("7a x", xb, 5, 1e-6); ok("7a y", yb, 10 / 3, 1e-6)
ok("7a aires", 12 * 8, 96); ok("7a piece", 6 * 4, 24); ok("7a moment x", 96 * 6 - 24 * 9, 360); ok("7a moment y", 96 * 4 - 24 * 6, 240)
dx, dy = xb - 0, yb - 8  # vecteur de C vers G
ang = math.degrees(math.atan2(dx, -dy))
ok("7b angle", ang, 47.0, 5e-2); ok("7b tan", 5 / (14 / 3), 15 / 14, 1e-9); ok("7b exact", ang, math.degrees(math.atan(15 / 14)), 1e-4)
ok("7b distance verticale", 8 - 10 / 3, 14 / 3, 1e-9)
# echelle : on cherche S, R, F par resolution du systeme (moments autour de Q puis P : verification croisee)
mL, mP = 20.0, 70.0
cosT = 3 / 5; sinT = 4 / 5
ok("7c longueur", math.hypot(3, 4), 5)
R7 = (mL + mP) * g
S7 = (mL * g * 2.5 * cosT + mP * g * 2 * cosT) / (5 * sinT)
ok("7c R", R7, 882); ok("7c S", S7, 279.3, 1e-9); ok("7c moment gauche", 4 * S7, 1117.2, 1e-9); ok("7c moment droit", 196 * 1.5 + 686 * 1.2, 1117.2, 1e-9)
ok("7c distances", 2.5 * cosT, 1.5); ok("7c distance du peintre", 2 * cosT, 1.2)
# verification : moments autour de Q (sommet) avec F = S et R : doivent s'annuler
Fh = S7
# autour de Q (x=0 au mur, A = (3, 0), Q = (0, 4)) : R en (3,0) vers le haut, F en (3,0) vers le mur (direction -x), poids en (1.5, ...) et (1.2 de P...)
xP = 3.0
# moment autour de Q = rx*Fy - ry*Fx, avec r = position du point d'application relative a Q
M_R = (xP - 0) * R7 - (0 - 4) * 0
M_F = (xP - 0) * 0 - (0 - 4) * (-Fh)  # F en P vers -x : Fx = -F
M_Wl = (xP - 1.5 - 0) * (-mL * g)    # le poids de l'echelle est a 1.5 m horizontalement de P, donc x = 3 - 1.5
M_Wp = (xP - 1.2 - 0) * (-mP * g)
ok("7c equilibre des moments autour de Q", M_R + M_F + M_Wl + M_Wp, 0, 1e-8)
ok("7c mu", S7 / R7, 0.3167, 5e-4); ok("7c mu arrondi", S7 / R7, 0.317, 5e-4)

# ---- Ex 8 : mouvement circulaire et ficelles elastiques ----
m8, L8, cosA8 = 0.4, 1.0, 0.8
sinA8 = math.sqrt(1 - cosA8 ** 2)
ok("8a sin", sinA8, 0.6, 1e-12)
T8 = m8 * g / cosA8
ok("8a T", T8, 4.9, 1e-12)
r8 = L8 * sinA8
w8 = math.sqrt(T8 * sinA8 / (m8 * r8))
ok("8a omega", w8, 3.5, 1e-12); ok("8a omega2", w8 ** 2, 12.25, 1e-12); ok("8a rayon", r8, 0.6, 1e-12)
# autre voie : omega^2 = g tan(theta) / r
ok("8a autre voie", math.sqrt(g * sinA8 / cosA8 / r8), 3.5, 1e-12)
# simulation : particule dans un cone, on verifie l'equilibre des forces radiales dans le plan (ficelle tendue de longueur 1)
ok("8a equilibre vertical", T8 * cosA8, m8 * g, 1e-12)
L, u8 = 0.9, 8.0
v2 = u8 ** 2 - 4 * g * L
ok("8b v2", v2, 28.72, 1e-9)
T8b = m8 * v2 / L - m8 * g
ok("8b T", T8b, 8.8444, 5e-4); ok("8b arrondi", T8b, 8.84, 5e-3)
# simulation du cercle vertical (integration pas a pas de l'angle depuis le bas) : vitesse au sommet
th, om = 0.0, u8 / L; dt = 1e-6
while th < math.pi:
    om += -(g / L) * math.sin(th) * dt; th += om * dt
ok("8b vitesse au sommet simulee", (om * L) ** 2, v2, 5e-3)
ok("8b hauteur du sommet", 2 * L, 1.8)
ok("8b cercle complet (u^2 >= 5gL)", u8 ** 2 >= 5 * g * L, True)
lam, l8, m8b = 19.6, 0.5, 0.5
ok("8c mg", m8b * g, 4.9); ok("8c extension", m8b * g * l8 / lam, 0.125, 1e-12); ok("8c tension", lam * 0.125 / l8, 4.9, 1e-12)
f8 = lambda x: m8b * g * (l8 + x) - lam * x * x / (2 * l8)
x8 = bissection(f8, 0.01, 3)
ok("8d extension max", x8, 0.5, 1e-9); ok("8d quadratique", 8 * 0.25 - 2 * 0.5 - 1, 0); ok("8d factorisation", (4 * 0.5 + 1) * (2 * 0.5 - 1), 0)
# simulation : chute depuis O, corde elastique : vitesse nulle apres extension maximale
y = 0.0; v = 0.0; dt = 1e-6; ymax = 0.0
while True:
    ext = max(0.0, y - l8)
    acc = g - lam * ext / l8 / m8b
    v += acc * dt; y += v * dt
    ymax = max(ymax, y)
    if v < 0:
        break
ok("8d extension simulee", ymax - l8, 0.5, 5e-3)
ok("8d equation divisee", 19.6 / 2.45, 8); ok("8d 4.9/2.45", 4.9 / 2.45, 2)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e_ in ecarts:
        print("  -", e_)
    sys.exit(1)
print("0 ecart")
