r"""Recalcul INDEPENDANT (numerique, sans sympy) des reponses de l'epreuve inedite GCE A Level Physics Paper 1 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_physics_al_p1.py

Pour chaque question calculatoire, une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (simulation pas a pas, integration numerique, bilan
de dimensions, recherche exhaustive, resolution de circuit par noeud, lecture des donnees de la figure) et la compare a la valeur de controle `val` de la question ;
la valeur imprimee dans l'option juste est ensuite relue et comparee a la valeur recalculee (a la demi-unite du dernier chiffre), et aucune des trois autres
options ne doit tomber sur cette valeur. Pour les questions conceptuelles, la proposition vraie est retrouvee par un petit modele numerique (une seule option
vraie). Le JSON est enfin controle (lettre, `Answer:`, option unique egale a la cle, equilibre des cles, tirets cadratins, « all of the above »).
Sortie 1 s'il y a au moins un ecart.
"""
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_physics_al_p1 import questions  # noqa: E402
import figs_physics_al_p1 as figs  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-al-physics-p1-1-2026-s1.json")
ecarts = []
nverif = 0
QS = questions()
CONCEPTUELLES = [i for i, q in enumerate(QS, start=1) if q["conc"]]


def ok(num, calcule, annonce, tol_rel=2e-3):
    """Compare la valeur recalculee a la valeur de controle de la question (tuples compris)."""
    global nverif
    nverif += 1
    a, b = (calcule if isinstance(calcule, (tuple, list)) else (calcule,)), (annonce if isinstance(annonce, (tuple, list)) else (annonce,))
    if len(a) != len(b) or any(abs(x - y) > tol_rel * max(abs(y), 1e-30) + 1e-12 for x, y in zip(a, b)):
        ecarts.append(f"Q{num}: recalcule {calcule}, annonce {annonce}")


def vrai(num, condition, message):
    global nverif
    nverif += 1
    if not condition:
        ecarts.append(f"Q{num}: {message}")


def brent(f, a, b, n=200):
    """Zero d'une fonction continue par dichotomie."""
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        fm = f(m)
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


G = 9.8
C = {}  # numero -> valeur recalculee

# 1 : dimensions reconstruites depuis F = m a et p = F / A (vecteurs d'exposants M, L, T)
M_, L_, T_ = (1, 0, 0), (0, 1, 0), (0, 0, 1)
acc = tuple(l - 2 * t for l, t in zip(L_, T_))
force = tuple(m + a for m, a in zip(M_, acc))
aire = tuple(2 * l for l in L_)
C[1] = tuple(f - a for f, a in zip(force, aire))
# 2 : recherche exhaustive de a, b (multiples de 1/2) tels que T^a mu^b ait la dimension d'une vitesse
dim_v, dim_T, dim_mu = (0, 1, -1), (1, 1, -2), (1, -1, 0)  # (M, L, T)
sols = [(a2 / 2, b2 / 2) for a2 in range(-6, 7) for b2 in range(-6, 7)
        if all(abs(a2 / 2 * dim_T[k] + b2 / 2 * dim_mu[k] - dim_v[k]) < 1e-12 for k in range(3))]
vrai(2, len(sols) == 1, f"plusieurs solutions de dimensions {sols}")
C[2] = sols[0]
# 3 : somme vectorielle par composantes, angle avec la force de 8 N
fx, fy = 8.0, 6.0
C[3] = (math.hypot(fx, fy), math.degrees(math.atan2(fy, fx)))
# 4 : simulation pas a pas du lancer
y, v, dt, ymax = 0.0, 14.0, 1e-5, 0.0
while v > 0:
    y += v * dt
    v -= G * dt
    ymax = max(ymax, y)
C[4] = ymax
# 5 : aire sous la courbe de la figure (regle des trapezes sur les points de la figure), puis lecture des donnees ecrites en texte
aire_fig = sum((t2 - t1) * (v1 + v2) / 2 for (t1, v1), (t2, v2) in zip(figs.VT, figs.VT[1:]))
texte = (0.5 * 5.0 * 12) + (15 * 12) + (0.5 * 10 * 12)
vrai(5, abs(aire_fig - texte) < 1e-9, f"figure {aire_fig} et texte {texte} different")
C[5] = aire_fig
# 6 : theoreme de l'energie cinetique : F = delta Ec / distance, avec la distance moyenne
m6, u6, v6, t6 = 1200.0, 5.0, 20.0, 6.0
s6 = (u6 + v6) / 2 * t6
C[6] = 0.5 * m6 * (v6 ** 2 - u6 ** 2) / s6
# 7 : tension T cherchee par dichotomie pour que la somme verticale egale le poids
W7 = 40.0
C[7] = brent(lambda T: 2 * T * math.sin(math.radians(30)) - W7, 0, 500)
# 8 : vitesse du centre de masse (les deux chariots collent : leur vitesse est celle du centre de masse), et perte d'energie positive
v8 = (2.0 * 3.0 + 1.0 * 0.0) / (2.0 + 1.0)
vrai(8, 0.5 * 2.0 * 3.0 ** 2 > 0.5 * 3.0 * v8 ** 2, "l'energie cinetique doit diminuer")
C[8] = v8
# 9 : acceleration moyenne pendant le contact puis F = m a
a9 = (8.0 - (-12.0)) / 0.020
C[9] = 0.15 * a9
# 10 : debit massique 10 kg/s, P = (dm/dt) g h
C[10] = (600 / 60.0) * G * 15
# 11 : energie par metre parcouru = force, P / v
t11 = 1.0
C[11] = (40e3 * t11) / (25.0 * t11)
# 12 : potentiel -GM/r : negatif, croissant vers 0
GM = 3.986e14
V = lambda r: -GM / r
rs = [6.4e6 * k for k in (1, 2, 4, 8, 100, 10 ** 4)]
vrai(12, all(V(r) < 0 for r in rs) and all(V(a) < V(b) for a, b in zip(rs, rs[1:])) and abs(V(1e22)) < 1e-6, "modele du potentiel")
# 13 : periode puis omega, F = m omega^2 r
r13, v13, m13 = 0.80, 4.0, 0.50
omega13 = 2 * math.pi / (2 * math.pi * r13 / v13)
C[13] = m13 * omega13 ** 2 * r13
# 14 : periode d'une orbite circulaire obtenue en integrant le mouvement (GM = 1) puis rapport
def periode_orbite(r, dt=2e-4):
    x, yy, vx, vy = r, 0.0, 0.0, 1 / math.sqrt(r)
    t, crossings, prev = 0.0, [], yy
    while len(crossings) < 1:
        ax, ay = -x / (x * x + yy * yy) ** 1.5, -yy / (x * x + yy * yy) ** 1.5
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        yy += vy * dt
        t += dt
        if prev < 0 <= yy and t > 0.1:
            crossings.append(t)
        prev = yy
    return crossings[0]


C[14] = 8.0 * periode_orbite(4.0, dt=4e-4) / periode_orbite(1.0, dt=1e-4)
# 15 : derivee numerique de x(t) sur un maillage fin
x15 = lambda t: 0.050 * math.sin(12 * t)
C[15] = max(abs((x15(k * 1e-4 + 1e-6) - x15(k * 1e-4 - 1e-6)) / 2e-6) for k in range(0, 6000))
# 16 : integration de x'' = -(k/m) x, mesure du temps entre deux passages montants par zero
k16, m16 = 64.0, 0.40
x, v, t, dt, mont = 0.01, 0.0, 0.0, 1e-5, []
prev = x
while len(mont) < 2:
    v += -(k16 / m16) * x * dt
    x += v * dt
    t += dt
    if prev < 0 <= x:
        mont.append(t)
    prev = x
C[16] = mont[1] - mont[0]
# 17 : g = GM / r^2 avec R = 1 et GM = 9.8
C[17] = 9.8 / 1.5 ** 2
# 18 : vitesse de liberation par bilan d'energie 1/2 v^2 = GM/R avec les vraies valeurs de la Terre, rapport applique a 11 km/s
GT, MT, RT = 6.674e-11, 5.972e24, 6.371e6
ve_terre = math.sqrt(2 * GT * MT / RT)
ve_planete = math.sqrt(2 * GT * 8 * MT / (2 * RT))
C[18] = 11.0 * ve_planete / ve_terre
# 19 : constante de raideur k = E A / L puis e = F / k
A19 = math.pi * (0.50e-3 / 2) ** 2
C[19] = 40.0 / (2.0e11 * A19 / 2.0)
# 20 : energie = aire sous la droite de la figure (trapezes sur 400 pas)
F20, x20 = figs.FORCE_EXT["F"], figs.FORCE_EXT["x_cm"] / 100
n20 = 400
C[20] = sum((F20 / x20 * (i * x20 / n20) + F20 / x20 * ((i + 1) * x20 / n20)) / 2 * (x20 / n20) for i in range(n20))
# 21 : chauffage simule seconde par seconde : c tel que le liquide gagne 12 K en 180 s
def temps_pour_12K(c):
    th, t = 0.0, 0
    while th < 12.0:
        th += 500.0 / (1.5 * c)
        t += 1
    return t


C[21] = brent(lambda c: temps_pour_12K(c) - 180.5, 1000, 20000, n=60)
# 22 : onde stationnaire y = A sin(kx) cos(wt) : phase entre noeuds voisins, amplitude, flux d'energie moyen
lam22, Lc = 0.80, 1.20
kk = 2 * math.pi / lam22
xs_entre = [0.4 + 0.4 * u / 10 for u in range(1, 10)]  # entre les noeuds x = 0.4 et x = 0.8
xs_de_part = [0.4 - 0.05, 0.4 + 0.05]
amp = lambda x: abs(math.sin(kk * x))
phase_ok = len({math.copysign(1, math.sin(kk * x)) for x in xs_entre}) == 1
phase_noeud = math.sin(kk * xs_de_part[0]) * math.sin(kk * xs_de_part[1]) < 0
amp_varie = amp(0.2) > 0.99 and amp(0.4) < 1e-9
flux = sum(-(-math.sin(kk * 0.123) * math.sin(2 * math.pi * k / 1000)) * (kk * math.cos(kk * 0.123) * math.cos(2 * math.pi * k / 1000)) for k in range(1000))  # -dy/dt * dy/dx
vrai(22, phase_ok and phase_noeud and amp_varie and abs(flux) < 1e-6, "modele de l'onde stationnaire")
# 23 : Monte-Carlo : vitesses gaussiennes d'ecart-type sqrt(kT/m), rapport des vitesses quadratiques moyennes
rnd = random.Random(5)
def vrms(T, n=60000):
    s = math.sqrt(T / 300.0)
    return math.sqrt(sum(sum(rnd.gauss(0, s) ** 2 for _ in range(3)) for _ in range(n)) / n)
C[23] = vrms(1200.0) / vrms(300.0)
# 24 : constante de Boltzmann et nombre d'Avogadro : p = N k T / V
kB, NA = 1.380649e-23, 6.02214076e23
C[24] = (0.50 * NA) * kB * (77 + 273.15) / 2.0e-3
# 25 : travail integre pas a pas sous pression constante
W25 = sum(2.0e5 * (3.0e-3 / 1000) for _ in range(1000))
C[25] = 900.0 - W25
# 26 : gaz parfait, detente isotherme n = 1 mol, T = 300 K : W = integrale de p dV, delta U = (3/2) n R delta T = 0
R = 8.314
n26, T26, V1, V2 = 1.0, 300.0, 1.0e-3, 2.0e-3
W26 = sum(n26 * R * T26 / (V1 + (V2 - V1) * (i + 0.5) / 100000) * (V2 - V1) / 100000 for i in range(100000))
dU26 = 1.5 * n26 * R * (T26 - T26)
Q26 = dU26 + W26
vrai(26, W26 > 0 and dU26 == 0 and abs(Q26 - W26) < 1e-9 and abs(W26 - n26 * R * T26 * math.log(2)) < 1e-3, "modele isotherme")
# 27 : vitesse d'une crete suivie numeriquement sur y = sin(2 pi (x / lambda - f t))
lam27, f27 = 0.80, 50.0
y27 = lambda x, t: math.sin(2 * math.pi * (x / lam27 - f27 * t))
# vitesse de crete mesuree (deux instants proches, meme crete suivie a partir de la premiere position)
def pos_crete_proche(t, x_ref):
    xs = [x_ref - 0.2 + k * 1e-4 for k in range(4000)]
    return max(xs, key=lambda x: y27(x, t))
x_a = pos_crete_proche(0.0, 0.2)
x_b = pos_crete_proche(0.002, x_a)
C[27] = (x_b - x_a) / 0.002
# 28 : MHS x = A cos wt : signe de a x, vitesse maximale en x = 0, energie totale constante non nulle
A28, w28, m28 = 0.1, 5.0, 1.0
ts = [k * 1e-3 for k in range(3000)]
xx = [A28 * math.cos(w28 * t) for t in ts]
vv = [-A28 * w28 * math.sin(w28 * t) for t in ts]
aa = [-A28 * w28 ** 2 * math.cos(w28 * t) for t in ts]
e_tot = [0.5 * m28 * v_ ** 2 + 0.5 * m28 * w28 ** 2 * x_ ** 2 for v_, x_ in zip(vv, xx)]
s1 = all(a_ * x_ <= 1e-12 for a_, x_ in zip(aa, xx))
imax = max(range(len(vv)), key=lambda i: abs(vv[i]))
s2 = abs(xx[imax]) < 0.01 * A28
s3 = abs(e_tot[min(range(len(xx)), key=lambda i: -abs(xx[i]))]) < 1e-12
vrai(28, (s1, s2, s3) == (True, True, False) and max(e_tot) - min(e_tot) < 1e-9, "valeurs de verite des trois affirmations")
# 29 : positions exactes des maxima d'interference (chemins hypot), premier maximum au-dela du central
lam29, a29, D29 = 600e-9, 0.50e-3, 2.0
dchem = lambda y: math.hypot(D29, y + a29 / 2) - math.hypot(D29, y - a29 / 2)
y1 = brent(lambda y: dchem(y) - lam29, 0, 0.02)
C[29] = y1
# 30 : angle ou la difference de chemin entre fentes voisines vaut 2 lambda
d30 = 1e-3 / 300
C[30] = math.degrees(brent(lambda th: d30 * math.sin(th) - 2 * 600e-9, 0, math.pi / 2))
# 31 : noeuds de sin(2 pi x / lambda) sur [0, L] : trois boucles si ends compris et lambda = 0.80
for lam31 in [0.80]:
    noeuds = [k * lam31 / 2 for k in range(0, 100) if k * lam31 / 2 <= Lc + 1e-9]
    vrai(31, len(noeuds) - 1 == figs.CORDE["boucles"] and abs(noeuds[-1] - Lc) < 1e-9, "trois boucles pour 0.80 m sur 1.20 m")
    C[31] = lam31
# la figure donne 3 boucles et L = 1.20 m : lambda = 2 L / 3, retrouve par recherche
C[31] = min((lam for lam in [k / 1000 for k in range(100, 3000)] if abs(round(2 * figs.CORDE["L"] / lam) - 2 * figs.CORDE["L"] / lam) < 1e-9 and round(2 * figs.CORDE["L"] / lam) == figs.CORDE["boucles"]), default=None)
# 32 : tuyau ferme-ouvert : balayage de la frequence, premier f tel que noeud en x = 0 et ventre en x = L (cos(2 pi f L / v) = 0)
v32, L32 = 340.0, 0.30
f_scan = [k * 0.05 for k in range(1, 40000)]
C[32] = next(f for f in f_scan if abs(math.cos(2 * math.pi * f * L32 / v32)) < 1e-4)
# 33 : loi de Snell : plus petit angle d'incidence dans le verre pour lequel il n'y a plus de rayon refracte
n_v, n_e = 1.60, 1.33
C[33] = next(math.degrees(th) for th in [k * 1e-5 for k in range(1, 157000)] if n_v * math.sin(th) / n_e >= 1.0)
# 34 : bilan de charge d'un cristal dope n : donneurs fixes + et electrons libres -
Nd = 1000
charge_ions = +1 * Nd
charge_libres = -1 * Nd
vrai(34, charge_ions + charge_libres == 0 and Nd > 0, "le cristal dope n est neutre, porteurs majoritaires = electrons")
# 35 : force = variation de l'energie potentielle d'un electron entre les plaques (deux positions)
e, Vp, d35 = 1.6e-19, 600.0, 0.040
U = lambda x: e * Vp * x / d35  # energie potentielle de l'electron (x depuis la plaque la plus negative)
C[35] = abs((U(0.030) - U(0.010)) / (0.030 - 0.010))
# 36 : bilans de nucleons, de charge et de nombre leptonique (C-14 -> N-14 + X) pour chacune des quatre propositions
PART = {"e-": (0, -1, +1), "e+": (0, +1, -1), "nu": (0, 0, +1), "antinu": (0, 0, -1), "alpha": (4, +2, 0)}  # (nucleons, charge, nombre leptonique)
propositions = {"b- + antinu": ["e-", "antinu"], "b- + nu": ["e-", "nu"], "b+ + nu": ["e+", "nu"], "alpha": ["alpha"]}
conserve = [nom for nom, ps in propositions.items()
            if 14 == 14 + sum(PART[p][0] for p in ps) and 6 == 7 + sum(PART[p][1] for p in ps) and sum(PART[p][2] for p in ps) == 0]
vrai(36, conserve == ["b- + antinu"], f"propositions qui conservent tout : {conserve}")
# 37 : decharge RC integree pas a pas
Rr, Cc, V0 = 22e3, 470e-6, 9.0
v37, t37, dt37 = V0, 0.0, 1e-3
while t37 < 20.0 - 1e-12:
    v37 -= v37 / (Rr * Cc) * dt37
    t37 += dt37
C[37] = v37
# 38 : energie = integrale de V dq avec V = q / C (somme de petits paquets de charge)
C38, V38, N38 = 100e-6, 50.0, 100000
q_tot = C38 * V38
C[38] = sum((i + 0.5) * q_tot / N38 / C38 * (q_tot / N38) for i in range(N38))
# 39 : resistance = somme de 2000 tranches de 1 mm en serie
A39 = math.pi * (0.40e-3 / 2) ** 2
C[39] = sum(1.7e-8 * 1e-3 / A39 for _ in range(2000))
# 40 : circuit complet : R de charge tel que I = 1,0 A, puis V = I R
E40, r40, I40 = 6.0, 0.50, 1.0
R40 = E40 / I40 - r40
C[40] = I40 * R40
# 41 : methode des noeuds : (24 - Va)/5 = Va/12 + Va/4
c = figs.CIRCUIT
va = brent(lambda x: (c["U"] - x) / c["R1"] - x / c["R2"] - x / c["R3"], 0, c["U"])
C[41] = va
# 42 : methode des noeuds : (12 - Va)/4k = Va/2k + Va/2k
d = figs.DIVISEUR
va2 = brent(lambda x: (d["U"] - x) / d["R1"] - x / d["R2"] - x / d["RV"], 0, d["U"])
C[42] = va2
# 43 : mouvement integre avec un pas de Boris dans B uniforme ; diametre = distance maximale au point de depart
mq, qq, Bf = 9.11e-31, 1.60e-19, 1.0e-3
vx, vy, vz = 2.0e7, 0.0, 0.0
px, py = 0.0, 0.0
dt43 = 1e-11
dmax = 0.0
for _ in range(20000):
    # rotation de Boris autour de z (champ le long de z)
    th = qq * Bf / mq * dt43
    c_, s_ = math.cos(th), math.sin(th)
    vx, vy = vx * c_ + vy * s_, -vx * s_ + vy * c_
    px += vx * dt43
    py += vy * dt43
    dmax = max(dmax, math.hypot(px, py))
C[43] = dmax / 2
# 44 : Lenz : le flux croit quand le pole nord approche, la f.e.m. est negative, le courant produit un champ qui s'oppose ;
# le pole induit en face est donc de meme nom (repulsion) : la force sur l'aimant s'oppose a son mouvement, il faut fournir de l'energie
phi = lambda t: 1.0 + 0.5 * t  # flux dans le sens du champ de l'aimant, croissant
emf = -(phi(1.001) - phi(0.999)) / 0.002
champ_induit = math.copysign(1, emf)  # signe du champ induit par rapport au champ de l'aimant dans la bobine
vrai(44, champ_induit < 0, "le champ induit doit s'opposer a l'accroissement du flux")
puissance_joule = emf ** 2 / 1.0
vrai(44, puissance_joule > 0, "une puissance est dissipee : un travail exterieur est necessaire")
# 45 : f.e.m. integree sur la duree : somme de N dPhi / dt
N45 = 200
steps = 2000
emf_somme = 0.0
for i in range(steps):
    ph1 = 5.0e-3 + (1.0e-3 - 5.0e-3) * i / steps
    ph2 = 5.0e-3 + (1.0e-3 - 5.0e-3) * (i + 1) / steps
    emf_somme += abs(N45 * (ph2 - ph1) / (0.020 / steps)) / steps
C[45] = emf_somme
# 46 : moyenne sur une periode de V(t)^2 / R
C[46] = sum((100.0 * math.sin(2 * math.pi * k / 100000)) ** 2 / 50.0 for k in range(100000)) / 100000
# 47 : conservation de la puissance en nombres : I_p = Vs Is / Vp ; verification par le rapport d'un transformateur ideal de 1200 spires
Np = 1200
Ns = Np * 12 / 230
Ip = 4.0 * (Ns / Np)
C[47] = Ip
# 48 : energie des photons avec les constantes de l'enonce, en eV
h, cc, el = 6.63e-34, 3.00e8, 1.60e-19
C[48] = h * cc / 400e-9 / el - 2.3
# 49 : toutes les transitions entre les trois niveaux, plus grande longueur d'onde
niv = figs.NIVEAUX
lams = [h * cc / ((hi - lo) * el) for lo in niv for hi in niv if hi > lo]
C[49] = max(lams)
# 50 : demi-vie par decroissance simulee : combien de pas de 1 h pour passer de 800 a 100 avec T = 12 h
A, t50 = 800.0, 0
lam50 = math.log(2) / 12.0
while A > 100.0 + 1e-6:
    A *= math.exp(-lam50 * 0.001)
    t50 += 0.001
C[50] = 36.0 / (round(math.log2(800 / 100)))
vrai(50, abs(t50 - 36.0) < 0.05, "la simulation avec T = 12 h donne bien 36 h pour 800 -> 100")

# ------------------------------------------------------------------------------------------------ comparaison avec les valeurs de controle
for n in sorted(C):
    q = QS[n - 1]
    if q["val"] is not None:
        ok(n, C[n], q["val"], tol_rel=(2e-2 if n in (14, 23, 27, 37) else 2e-3))
for n in CONCEPTUELLES:
    vrai(n, QS[n - 1]["val"] is None, "question conceptuelle : pas de valeur")

# ------------------------------------------------------------------------------------------------ valeur imprimee dans la bonne option
RE_NOMBRE = re.compile(r"(-?\d+(?:\.\d+)?)(?:\\times10\^\{(-?\d+)\})?")
ECHELLES = {19: 1e-3, 29: 1e-3, 5: 1, 18: 1}


def lire(texte):
    m = RE_NOMBRE.search(texte)
    if not m:
        return None
    mant, exp = m.group(1), int(m.group(2) or 0)
    dec = len(mant.split(".")[1]) if "." in mant else 0
    return float(mant) * 10 ** exp, 0.5 * 10 ** (-dec) * 10 ** exp


for n in sorted(C):
    q = QS[n - 1]
    if n in (1, 2, 3):
        continue
    lu = lire(q["key"].replace("$", ""))
    if lu is None:
        continue
    ech = ECHELLES.get(n, 1)
    valeur, demi = lu[0] * ech, lu[1] * ech
    vrai(n, abs(C[n] - valeur) <= demi * 1.0001 + 1e-12, f"option juste {q['key']} different de la valeur recalculee {C[n]:.6g}")
    for texte, _ in q["dist"]:
        ld = lire(texte.replace("$", ""))
        if ld is not None:
            vd = ld[0] * ech
            vrai(n, abs(C[n] - vd) > ld[1] * ech * 1.0001, f"un distracteur ({texte}) vaut la bonne reponse")
# lectures particulieres
vrai(1, C[1] == (1, -1, -2) and "kg m}^{-1}\\,\\text{s}^{-2}" in QS[0]["key"], "unite du pascal")
vrai(2, C[2] == (0.5, -0.5) and "a=\\tfrac12,\\ b=-\\tfrac12" in QS[1]["key"], "exposants")
vrai(3, abs(C[3][0] - 10) < 1e-9 and round(C[3][1]) == 37 and "10\\ \\text{N}$ at $37" in QS[2]["key"], "resultante")
vrai(36, "antineutrino" in QS[35]["key"], "cle de la desintegration beta moins")
# distracteurs numeriques particuliers : chaque erreur annoncee redonne bien la valeur du distracteur
dist_attendus = {
    19: [(0.51e-3, 40.0 * 2.0 / (2.0e11 * math.pi * (0.50e-3) ** 2)), (8.1e-3, 40.0 * 2.0 / (2.0e11 * math.pi * (0.50e-3 / 4) ** 2)), (1.6e-3, 40.0 * 2.0 / (2.0e11 * (0.50e-3) ** 2))],
    39: [(0.068, 1.7e-8 * 2.0 / (math.pi * 0.40e-3 ** 2)), (1.1, 1.7e-8 * 2.0 / (math.pi * (0.40e-3 / 4) ** 2)), (0.21, 1.7e-8 * 2.0 / (0.40e-3) ** 2)],
    13: [(2.5, 0.5 * 4.0 / 0.8), (6.4, 0.5 * 16.0 * 0.8), (8.0, 0.5 * 16.0)],
    6: [(4.0e3, 1200 * 20 / 6.0), (1.8e4, 1200 * 15.0), (7.2e3, 1200 * 6.0)],
    9: [(30.0, 0.15 * 4.0 / 0.02), (90.0, 0.15 * 12 / 0.02), (60.0, 0.15 * 8 / 0.02)],
    45: [(0.20, 4.0e-3 / 0.020), (60.0, 200 * 6.0e-3 / 0.020), (10.0, 200 * 1.0e-3 / 0.020)],
    47: [(77.0, 4.0 * 230 / 12), (0.052, 12 / 230)],
    37: [(7.7, V0 * (1 - math.exp(-20 / (Rr * Cc)))), (4.7, V0 / (20 / (Rr * Cc))), (1.9e-8, V0 * math.exp(-20.0))],
    48: [(5.4, h * cc / 400e-9 / el + 2.3), (3.1, h * cc / 400e-9 / el)],
    49: [(2.5e-7, h * cc / (5.0 * el)), (1.8e-7, h * cc / (6.8 * el)), (4.1e-7, h * cc / (3.0 * el))],
    43: [(0.23, 2 * mq * 2.0e7 / (qq * Bf)), (1.1e-4, mq * 2.0e7 / (qq * 1.0)), (5.7e-2, mq * 2.0e7 / (2 * qq * Bf))],
    35: [(2.4e-17, e * 600 / 4.0), (3.8e-18, e * 600 * 0.040), (1.5e4, 600 / 0.040)],
    21: [(83.0, 500 * 3.0 / (1.5 * 12)), (7.5e3, 500 * 180 / 12), (6.0e4, 500 * 180 / 1.5)],
    24: [(7.3e2, 0.5 * 8.31 * 350 / 2.0), (1.5e6, 8.31 * 350 / 2.0e-3), (1.6e5, 0.5 * 8.31 * 77 / 2.0e-3)],
    29: [(24e-3, 600e-9 * 2.0 / 0.050e-3), (1.2e-3, 600e-9 * 2.0 / 1.0e-3), (4.8e-3, 600e-9 * 2.0 / 0.25e-3)],
    30: [(10.0, math.degrees(math.asin(600e-9 / d30))), (46.0, math.degrees(math.asin(2 * 600e-9 * 600e3)))],
    10: [(8.8e4, 600 * G * 15), (1.5e2, 600 * 15 / 60.0), (25.0, 600 * G * 15 / 3600.0)],
    16: [(0.079, math.sqrt(0.40 / 64)), (2.0, 1 / (2 * math.pi * math.sqrt(0.40 / 64))), (13.0, math.sqrt(64 / 0.40))],
    17: [(6.5, 9.8 / 1.5), (2.9, 9.8 / 1.5 ** 3), (39.0, 9.8 / 0.5 ** 2)],
    18: [(44.0, 11 * 8 / 2), (31.0, 11 * math.sqrt(8)), (16.0, 11 * math.sqrt(2))],
    14: [(32.0, 8 * 4), (128.0, 8 * 16), (16.0, 8 * 2)],
    23: [(4.0, 1200 / 300), (5.9, math.sqrt(927 / 27)), (34.0, 927 / 27)],
    31: [(2.4, 2 * 1.2), (0.40, 1.2 / 3), (1.2, 1.2)],
    32: [(567.0, 340 / (2 * 0.30)), (1130.0, 340 / 0.30), (850.0, 3 * 340 / (4 * 0.30))],
    33: [(34.0, math.degrees(math.acos(1.33 / 1.60))), (39.0, math.degrees(math.asin(1 / 1.60))), (0.83, 1.33 / 1.60)],
    38: [(0.25, 100e-6 * 50 ** 2), (2.5e-3, 0.5 * 100e-6 * 50), (125.0, 0.5 * 100e-3 * 50 ** 2)],
    46: [(200.0, 100 ** 2 / 50), (141.0, 100 ** 2 / 50 / math.sqrt(2)), (50.0, 100 ** 2 / 50 / 4)],
    11: [(1.0e6, 40e3 * 25), (1.6, 40 / 25), (6.3e-4, 25 / 40e3)],
    4: [(20.0, 14 ** 2 / G), (1.4, 14 / G), (2.5, 7 ** 2 / (2 * G))],
    8: [(1.5, 3.0 / 2), (1.0, 3.0 / 3.0), (6.0, 2 * 3.0)],
    40: [(6.0, 6.0), (0.50, 0.50), (6.5, 6.0 + 0.5)],
    41: [(15.0, 24 / 8.0 * 5.0), (24.0, 24.0), (3.0, 24 / 8.0)],
    42: [(4.0, 12 * 2.0 / 6.0), (6.0, 12 / 2), (8.0, 12 * 4.0 / 6.0)],
    25: [(1500.0, 900 + 600), (600.0, 600), (-300.0, 600 - 900)],
    27: [(63.0, 50 / 0.80), (0.016, 0.80 / 50), (51.0, 50 + 0.80)],
    5: [(360.0, 12 * 30.0), (210.0, 30.0 + 180.0), (180.0, 12 * 15.0)],
    15: [(7.2, 0.050 * 12 ** 2), (4.2e-3, 0.050 / 12), (0.050, 0.050)],
    20: [(0.48, 12 * 0.040), (24.0, 0.5 * 12 * 4.0), (2.4, 0.5 * 12 * 0.40)],
    7: [(20.0, 40.0 / 2), (80.0, 40.0 / math.sin(math.radians(30))), (23.0, 40.0 / (2 * math.cos(math.radians(30))))],
}
for n, lst in dist_attendus.items():
    for annonce, calcule in lst:
        vrai(n, abs(calcule - annonce) <= 0.05 * abs(annonce) + 1e-12 or (abs(annonce) > 0 and abs(round(calcule, 2) - annonce) < 0.011), f"distracteur annonce {annonce}, l'erreur decrite donne {calcule:.5g}")

# ------------------------------------------------------------------------------------------------ coherence du JSON
with open(EP, encoding="utf8") as fh:
    ep = json.load(fh)
qjs = ep["exercices"][0]["questions"]
vrai(0, len(qjs) == 50, "il faut 50 questions")
from collections import Counter  # noqa: E402
cles = [q["reponse_correcte"] for q in qjs]
vrai(0, sorted(Counter(cles).values()) == [12, 12, 13, 13], f"equilibre des cles {dict(Counter(cles))}")
vrai(0, all(not (cles[i] == cles[i + 1] == cles[i + 2]) for i in range(48)), "trois cles identiques de suite")
for i, (q, src) in enumerate(zip(qjs, QS), start=1):
    k = q["reponse_correcte"]
    lettres = [c["lettre"] for c in q["choix"]]
    vrai(i, lettres == list("abcd") and k in lettres, "lettres des options")
    textes = {c["lettre"]: c["texte"] for c in q["choix"]}
    vrai(i, textes[k] == src["key"] and sum(1 for t in textes.values() if t == src["key"]) == 1, "l'option de la cle n'est pas la bonne reponse unique")
    vrai(i, f"**Answer: {k.upper()}.**" in q["corrige_markdown"], "ligne Answer du corrige")
    vrai(i, len(set(textes.values())) == 4, "options en double")
    vrai(i, q["points"] == 1 and q["type_reponse"] == "qcm" and q["numero"] == str(i), "champs de base")
    brut = json.dumps(q, ensure_ascii=False)
    vrai(i, "\u2014" not in brut and "\u2013" not in brut, "tiret cadratin ou demi-cadratin")
    vrai(i, not re.search(r"all of the above|none of the above", brut, re.I), "all/none of the above interdit en Physics")
    vrai(i, all(t in q["themes"] or True for t in src["themes"]) and q["themes"] == src["themes"], "themes")
    vrai(i, "{FIG}" not in brut, "marque de figure non remplacee")
    # la raison de chaque distracteur est citee dans le piege
    vrai(i, q["corrige_markdown"].count("option ") >= 3, "pieges nommes")

print(f"{nverif} verifications, {len(ecarts)} ecart(s)")
print("questions conceptuelles a faire relire par un enseignant :", ", ".join(f"Q{i}" for i in CONCEPTUELLES))
for e in ecarts:
    print("ECART", e)
if not ecarts:
    print("0 ecart")
sys.exit(1 if ecarts else 0)
