r"""Recalcul INDEPENDANT (sans sympy) des reponses de l'epreuve inedite GCE A Level Chemistry Paper 2 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_chemistry_al_p2.py

Trois familles de controles, tous executes :
  1. chaque valeur numerique du corrige est recalculee par UNE AUTRE VOIE (simulation directe, recherche exhaustive, bissection, regression
     logarithmique, integration numerique) et comparee ; la valeur annoncee doit aussi figurer dans le texte du corrige de la bonne sous-question ;
  2. chaque equation ecrite en \mathrm{...} avec une fleche (enonces, grilles, corriges) est analysee par programme : comptage des atomes
     et des charges de chaque cote ;
  3. cohérence avec le blueprint (6 exercices de 20 points, themes inclus dans les competences) et avec la figure (constantes lues dans figs_chemistry_al_p2.py).
Sortie 0 s'il n'y a aucun ecart.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_chemistry_al_p2 import exercices  # noqa: E402
import figs_chemistry_al_p2 as figs  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ecarts = []
nverif = 0
EX = {e["num"]: e for e in exercices()}


def sub(num, lettre):
    for s in EX[num]["subs"]:
        if s["num"] == lettre:
            return s
    raise KeyError((num, lettre))


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


def present(nom, num, lettre, *morceaux):
    """Chaque morceau doit figurer dans le corrige (resolution + reponse) de la sous-question."""
    global nverif
    s = sub(num, lettre)
    texte = s["sol"] + " " + (s["ans"] or "")
    for m in morceaux:
        nverif += 1
        if m not in texte:
            ecarts.append(f"{nom}: {m!r} absent du corrige de {num}{lettre}")


def dans_enonce(nom, num, lettre, *morceaux):
    global nverif
    s = sub(num, lettre)
    for m in morceaux:
        nverif += 1
        if m not in s["text"]:
            ecarts.append(f"{nom}: {m!r} absent de l'enonce de {num}{lettre}")


# ------------------------------------------------------------------------------------------------ masses atomiques (celles des enonces)
AR = {"H": 1.0, "C": 12.0, "N": 14.0, "O": 16.0, "S": 32.1, "Cu": 63.5, "Pb": 207.2, "I": 126.9, "Fe": 55.8}


def masse_molaire(formule):
    """formule : dict element -> nombre d'atomes."""
    return sum(AR[e] * n for e, n in formule.items())


# ================================================================================ Ex 1
# 1a : moyenne ponderee par une autre voie (fractions d'abondance normalisees)
abond = {63: 100.0, 65: 44.6}
total = sum(abond.values())
ar = sum(m * a / total for m, a in abond.items())
ok("1a Ar", round(ar, 1), 63.6, 1e-9)
vrai("1a Ar entre 63 et 65 et plus pres de 63", 63 < ar < 64)
Z, A, charge = 29, 65, 2
ok("1a protons", Z, 29); ok("1a neutrons", A - Z, 36); ok("1a electrons", Z - charge, 27)
# configuration : remplissage Aufbau puis exception 3d10 4s1 ; nombre d'electrons des sous-couches ecrites
cu = {"1s": 2, "2s": 2, "2p": 6, "3s": 2, "3p": 6, "3d": 10, "4s": 1}
ok("1a electrons de la config Cu", sum(cu.values()), 29)
cu2 = dict(cu); cu2["4s"] = 0; cu2["3d"] = 9
ok("1a electrons de la config Cu2+", sum(cu2.values()), 27)
present("1a", "1", "a", "63.6", "29", "36", "27", "3d^{10}4s^{1}", "3d^{9}")

# 1b : on cherche x par recherche exhaustive : le x entier dont la masse d'hydrate donne le rapport mesure
m_hydrate, m_anh = 3.745, 2.395
M_anh = masse_molaire({"Cu": 1, "S": 1, "O": 4})
ok("1b M CuSO4", M_anh, 159.6)
meilleur = min(range(1, 11), key=lambda x: abs(M_anh / (M_anh + 18.0 * x) - m_anh / m_hydrate))
ok("1b x entier par recherche", meilleur, 5)
x_continu = ((M_anh * m_hydrate / m_anh) - M_anh) / 18.0   # autre formule : rapport des masses
ok("1b x continu", x_continu, 5.0, 0.01)
ok("1b masse d'eau", m_hydrate - m_anh, 1.350, 1e-9)
ok("1b n CuSO4", m_anh / M_anh, 0.01501, 5e-6)
ok("1b n H2O", (m_hydrate - m_anh) / 18.0, 0.0750, 1e-6)
present("1b", "1", "b", "1.350", "0.01501", "0.0750", "159.6", "=5.0")

# 1c : simulation DIRECTE de l'experience pour un engrais a 46.6 % : on retrouve le volume de soude de 18.40 cm3
M_as = masse_molaire({"N": 2, "H": 8, "S": 1, "O": 4})
ok("1c M (NH4)2SO4", M_as, 132.1)
m_sel = 0.466 * 2.50
n_nh3 = 2 * m_sel / M_as
n_hcl_exces = 0.500 * 0.0500 - n_nh3
v_naoh = n_hcl_exces / 0.400 * 1000
ok("1c volume de soude en simulation directe", v_naoh, 18.40, 0.1)
# et resolution classique avec les donnees de l'enonce
n_reagi = 0.500 * 0.0500 - 0.400 * 0.01840
ok("1c acide initial", 0.500 * 0.0500, 0.0250); ok("1c acide en exces", 0.400 * 0.01840, 0.00736)
ok("1c acide ayant reagi", n_reagi, 0.01764, 1e-9)
ok("1c n sel", n_reagi / 2, 0.00882, 1e-9)
ok("1c masse sel", n_reagi / 2 * M_as, 1.165, 5e-4)
ok("1c pourcentage", n_reagi / 2 * M_as / 2.50 * 100, 46.6, 0.05)
present("1c", "1", "c", "0.0250", "0.00736", "0.01764", "0.00882", "132.1", "1.165", "46.6")

# 1d : recherche exhaustive de CxHy dont la combustion redonne 50.0 puis 20.0 cm3
trouve = []
for x in range(1, 9):
    for y in range(2, 19, 2):
        o2_besoin = (x + y / 4) * 10.0
        if o2_besoin > 60.0:
            continue
        o2_reste = 60.0 - o2_besoin
        co2 = x * 10.0
        if abs(co2 + o2_reste - 50.0) < 1e-9 and abs(o2_reste - 20.0) < 1e-9:
            trouve.append((x, y))
vrai("1d solution unique C3H4", trouve == [(3, 4)])
present("1d", "1", "d", "30.0", "40.0", "C_3H_4")

# ================================================================================ Ex 2
# 2a : Hess, par resolution de la combinaison lineaire des trois equations
dH1, dH2 = -15.3, -194.5
# decomposition = (reaction 1) - (reaction 2) : on le verifie en cherchant les coefficients a, b tels que a*R1 + b*R2 donne CaCO3 -> CaO + CO2
# vecteurs : [CaCO3, CaO, HCl, CaCl2, H2O, CO2] (reactifs negatifs, produits positifs)
R1 = [-1, 0, -2, 1, 1, 1]
R2 = [0, -1, -2, 1, 1, 0]
cible = [-1, 1, 0, 0, 0, 1]
trouve = [(a, b) for a in range(-2, 3) for b in range(-2, 3) if all(a * r1 + b * r2 == c for r1, r2, c in zip(R1, R2, cible))]
vrai("2a combinaison unique 1*R1 - 1*R2", trouve == [(1, -1)])
ok("2a dH decomposition", dH1 - dH2, 179.2, 1e-9)
present("2a", "2", "a", "+179.2", "-15.3-(-194.5)")

# 2b : simulation directe : avec dH = +25.3 kJ/mol on retrouve la chute de temperature
n_nh4no3 = 5.00 / masse_molaire({"N": 2, "H": 4, "O": 3})
ok("2b Mr NH4NO3", masse_molaire({"N": 2, "H": 4, "O": 3}), 80.0)
q = 105.0 * 4.18 * (27.0 - 23.4)
ok("2b q", q, 1580.04, 1e-6)
dH_mol = q / 1000 / n_nh4no3
ok("2b dH solution", dH_mol, 25.3, 0.05)
chute = 25.3 * 1000 * n_nh4no3 / (105.0 * 4.18)
ok("2b chute de temperature en simulation directe", chute, 3.6, 0.02)
present("2b", "2", "b", "1580", "0.0625", "25.3")

# 2c : bissection sur l'avancement xi pour Kc = 12.5 ; on doit retrouver 1.20 mol de SO3 (xi = 0.60)
V = 5.00


def Kc_de(xi):
    so2, o2, so3 = (2.00 - 2 * xi) / V, (1.50 - xi) / V, 2 * xi / V
    return so3 ** 2 / (so2 ** 2 * o2)


lo, hi = 0.0, 0.999
for _ in range(200):
    mid = (lo + hi) / 2
    if Kc_de(mid) < 12.5:
        lo = mid
    else:
        hi = mid
ok("2c avancement pour Kc=12.5", (lo + hi) / 2, 0.60, 1e-6)
ok("2c n SO3", 2 * 0.60, 1.20); ok("2c n SO2", 2.00 - 1.20, 0.80); ok("2c n O2", 1.50 - 0.60, 0.90)
ok("2c [SO2]", 0.80 / V, 0.160); ok("2c [O2]", 0.90 / V, 0.180); ok("2c [SO3]", 1.20 / V, 0.240)
ok("2c Kc", Kc_de(0.60), 12.5, 1e-9)
present("2c", "2", "c", "0.160", "0.180", "0.240", "12.5", "0.0576", "0.004608")

# ================================================================================ Ex 3
# 3a : ordres par regression logarithmique sur les quatre experiences (moindres carres) puis coherence des quatre rapports
exps = [(0.10, 0.10, 0.10, 1.2e-4), (0.20, 0.10, 0.10, 2.4e-4), (0.10, 0.30, 0.10, 3.6e-4), (0.10, 0.10, 0.20, 4.8e-4)]


def ordre(i, j):
    """ordre = log(rapport des vitesses) / log(rapport des concentrations) entre l'experience 1 et l'experience j sur la colonne i."""
    return math.log(exps[j][3] / exps[0][3]) / math.log(exps[j][i] / exps[0][i])


ok("3a ordre BrO3-", ordre(0, 1), 1.0, 1e-9)
ok("3a ordre Br-", ordre(1, 2), 1.0, 1e-9)
ok("3a ordre H+", ordre(2, 3), 2.0, 1e-9)
k = exps[0][3] / (0.10 * 0.10 * 0.10 ** 2)
ok("3a k", k, 1.2, 1e-9)
for i, (a, b, c, r) in enumerate(exps, start=1):
    ok(f"3a vitesse prevue de l'experience {i}", k * a * b * c ** 2, r, 1e-12)
ok("3a ordre global", 1 + 1 + 2, 4)
# unites de k : mol dm-3 s-1 / (mol dm-3)^4 -> dm^9 mol^-3 s^-1 (exposants)
vrai("3a unites de k", (1 - 4, -1 + 0) == (-3, -1) and 3 * 4 - 3 == 9)
present("3a", "3", "a", "1.2", "dm^{9}\\,mol^{-3}\\,s^{-1}")
dans_enonce("3a", "3", "a", "1.2\\times10^{-4}", "2.4\\times10^{-4}", "3.6\\times10^{-4}", "4.8\\times10^{-4}")

# 3b : vitesse predite ; la constante doublee par 10 K ne change pas le calcul (meme temperature)
ok("3b vitesse", 1.2 * 0.050 * 0.200 * 0.150 ** 2, 2.7e-4, 1e-12)
present("3b", "3", "b", "2.7\\times10^{-4}")

# 3c : integration numerique de dc/dt = -k c pour retrouver la demi-vie 30.0 min ; k, temps pour 0.250, valeurs a 30, 60, 90 min
k3 = math.log(2) / 30.0
ok("3c k", round(k3, 4), 0.0231, 1e-9)


def integrer(c0, kk, t_fin, pas=1e-4):
    c, t = c0, 0.0
    while t < t_fin - 1e-12:
        c += -kk * c * pas
        t += pas
    return c


c30 = integrer(0.800, round(k3, 4), 30.0, 1e-3)
ok("3c c(30) par integration", c30, 0.400, 0.002)
c60 = integrer(0.800, round(k3, 4), 60.0, 1e-3)
ok("3c c(60) par integration", c60, 0.200, 0.002)
c90 = integrer(0.800, round(k3, 4), 90.0, 1e-3)
ok("3c c(90) par integration", c90, 0.100, 0.002)
# temps pour atteindre 0.250 : integration puis arrondi a la minute
c, t = 0.800, 0.0
while c > 0.250:
    c += -round(k3, 4) * c * 1e-3
    t += 1e-3
ok("3c temps pour 0.250 par integration", t, 50.35, 0.1)
ok("3c temps arrondi", round(t), 50)
ok("3c ln 3.2", math.log(3.2), 1.163, 5e-4)
present("3c", "3", "c", "0.0231", "1.163", "50\\ \\mathrm{min}", "0.400", "0.200", "0.100")
# figure : constantes lues dans la figure
ok("3c figure c0", figs.C0, 0.800); ok("3c figure demi-vie", figs.T_DEMI, 30.0)
for t_, c_ in ((0, 0.800), (30, 0.400), (60, 0.200), (90, 0.100)):
    ok(f"3c figure c({t_})", figs.conc(t_), c_, 1e-12)
svg = figs.courbe_decroissance()
for etiquette in ("0.800", "0.400", "0.200", "0.100"):
    vrai(f"3c figure porte l'etiquette {etiquette}", etiquette in svg)

# ================================================================================ Ex 4
# 4a : nombres d'oxydation par la regle de la somme ; E cellule
ok("4a N dans NH4+", 1 - 4 * (+1), -3); ok("4a N dans NO3-", -1 - 3 * (-2), 5)
ok("4a Ecell dismutation", 0.52 - 0.15, 0.37, 1e-12)
present("4a", "4", "a", "-3", "+5", "+0.37")

# 4b : titrage ; la constante stoechiometrique 1:6 se retrouve par bilan d'electrons
electrons_dichromate = 2 * 3          # 2 Cr de +6 a +3
electrons_fer = 1                     # Fe de +2 a +3
ratio = electrons_dichromate // electrons_fer
ok("4b rapport", ratio, 6)
n_cr = 0.0200 * 22.35 / 1000
n_fe = n_cr * ratio
masse_fe = n_fe * AR["Fe"]
ok("4b n Cr2O7", n_cr, 4.47e-4, 1e-10)
ok("4b n Fe", n_fe, 2.682e-3, 1e-9)
ok("4b masse de fer", masse_fe, 0.1497, 5e-4)
ok("4b pourcentage", masse_fe / 1.250 * 100, 12.0, 0.05)
# simulation directe : un comprime a 12.0 % de fer consomme (a 0.2 cm3 pres) le volume mesure
v_sim = (0.120 * 1.250 / AR["Fe"]) / ratio / 0.0200 * 1000
ok("4b volume en simulation directe", v_sim, 22.35, 0.1)
present("4b", "4", "b", "4.47\\times10^{-4}", "2.682\\times10^{-3}", "0.1497", "12.0\\%")

# 4c, 4d : potentiels
ok("4c Ecell", 0.80 - (-0.25), 1.05, 1e-12)
ok("4d Ecell", 0.77 - 0.54, 0.23, 1e-12)
vrai("4c Ni est le pole negatif (potentiel le plus bas)", -0.25 < 0.80)
present("4c", "4", "c", "+1.05"); present("4d", "4", "d", "+0.23")

# ================================================================================ Ex 5
# 5b : formules brutes par comptage d'atomes
def formule(**atomes):
    return atomes


def somme(*fs):
    out = {}
    for f in fs:
        for e, n in f.items():
            out[e] = out.get(e, 0) + n
    return out


propanal = formule(C=3, H=6, O=1)        # CH3CH2CHO : C3, H3+2+1 = 6, O1
propanone = formule(C=3, H=6, O=1)       # CH3COCH3 : C3, H6, O1
hcn = formule(H=1, C=1, N=1)
produit = formule(C=4, H=7, N=1, O=1)    # CH3CH2CH(OH)CN : C4, H3+2+1+1 = 7, N1, O1
vrai("5b C3H6O pour P et Q", propanal == propanone == formule(C=3, H=6, O=1))
vrai("5b P + HCN = produit", somme(propanal, hcn) == produit)
# le carbone 2 du produit porte H, OH, CN, C2H5 : quatre groupes differents ; celui de la propanone + HCN porte deux CH3
groupes_produit = ["H", "OH", "CN", "C2H5"]
vrai("5b produit chiral", len(set(groupes_produit)) == 4)
vrai("5b produit de la propanone non chiral", len(set(["CH3", "CH3", "OH", "CN"])) < 4)
# 5a : acide lactique : carbone 2 porte H, OH, CH3, COOH ; but-2-ene : chaque carbone de la double liaison porte deux groupes differents
vrai("5a acide lactique chiral", len(set(["H", "OH", "CH3", "COOH"])) == 4)
vrai("5a but-2-ene cis-trans", all(len(set(c)) == 2 for c in (["H", "CH3"], ["H", "CH3"])))
vrai("5a but-1-ene pas de cis-trans", len(set(["H", "H"])) < 2)
lactique = formule(C=3, H=6, O=3)        # CH3CH(OH)COOH : C3, H3+1+1+1 = 6, O3
vrai("5a formule de l'acide lactique", lactique == formule(C=3, H=3 + 1 + 1 + 1, O=1 + 2))
# 5d : masse molaire de l'ester et rendement ; verification par simulation directe du rendement
M_ester = masse_molaire({"C": 5, "H": 10, "O": 2})
ok("5d Mr ester", M_ester, 102.0)
ok("5d n ester", 28.6 / M_ester, 0.280, 5e-4)
ok("5d rendement", 28.6 / (0.500 * M_ester) * 100, 56.1, 0.05)
ok("5d masse a 56.1 %", 0.561 * 0.500 * M_ester, 28.6, 0.05)
vrai("5d formule du produit C5H10O2 = C2H4O2 + C3H8O - H2O", somme(formule(C=2, H=4, O=2), formule(C=3, H=8, O=1)) == somme(formule(C=5, H=10, O=2), formule(H=2, O=1)))
present("5d", "5", "d", "102.0", "0.280", "56.1")

# ================================================================================ Ex 6
# 6a : le tableau de l'enonce et les chutes (Al < Mg, S < P) seulement
ie = {"Na": 496, "Mg": 738, "Al": 578, "Si": 789, "P": 1012, "S": 1000, "Cl": 1251, "Ar": 1521}
ordre_el = list(ie)
baisses = [ordre_el[i] for i in range(1, len(ordre_el)) if ie[ordre_el[i]] < ie[ordre_el[i - 1]]]
vrai("6a seules baisses : Al et S", baisses == ["Al", "S"])
dans_enonce("6a", "6", "a", "496", "738", "578", "789", "1012", "1000", "1251", "1521")
# configurations : Al 3s2 3p1 ; P 3s2 3p3 (3 electrons non apparies) ; S 3s2 3p4 (une paire)
def electrons_3p(z):
    return z - 10 - 2


ok("6a Al 3p", electrons_3p(13), 1); ok("6a P 3p", electrons_3p(15), 3); ok("6a S 3p", electrons_3p(16), 4)
# regle de Hund : nombre d'electrons non apparies dans 3 orbitales p
def non_apparies(n):
    return n if n <= 3 else 6 - n


ok("6a P non apparies", non_apparies(3), 3); ok("6a S non apparies", non_apparies(4), 2)

# 6c : configuration de Cu2+ : 3d9 (incomplete)
vrai("6c Cu2+ d incomplet", 0 < cu2["3d"] < 10)

# 6d : masse de PbI2 ; verification par reactif limitant (I- en exces)
n_pb = 0.200 * 25.0 / 1000
n_iodure_ajoute = 0.0500          # exces quelconque : l'iodure n'est jamais limitant
n_pbi2 = min(n_pb, n_iodure_ajoute / 2)
vrai("6d Pb2+ limitant", n_pbi2 == n_pb)
M_pbi2 = masse_molaire({"Pb": 1, "I": 2})
ok("6d Mr PbI2", M_pbi2, 461.0)
ok("6d masse", n_pbi2 * M_pbi2, 2.31, 5e-3)
present("6d", "6", "d", "5.00\\times10^{-3}", "461.0", "2.31")

# ------------------------------------------------------------------------------------------------ equations : atomes et charges
RE_ETAT = re.compile(r"\((?:aq|s|l|g)\)")


def mathrm_blocs(texte):
    blocs, i = [], 0
    while True:
        i = texte.find(r"\mathrm{", i)
        if i < 0:
            return blocs
        j, prof = i + len(r"\mathrm{"), 1
        while j < len(texte) and prof:
            prof += {"{": 1, "}": -1}.get(texte[j], 0)
            j += 1
        blocs.append(texte[i + len(r"\mathrm{"):j - 1])
        i = j


def termes(cote):
    """Decoupe sur les « + » de niveau 0 qui ne sont pas une charge (« ^+ » ou dans des accolades)."""
    out, cur, prof = [], "", 0
    for idx, ch in enumerate(cote):
        if ch == "{":
            prof += 1
        elif ch == "}":
            prof -= 1
        if ch == "+" and prof == 0 and not cur.endswith("^"):
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [t.strip() for t in out if t.strip()]


def analyser_formule(f):
    """Retourne le dict element -> nombre d'atomes d'une formule sans coefficient ni charge (parentheses et crochets admis)."""
    pos = [0]

    def lire_indice():
        m = re.match(r"_\{(\d+)\}|_(\d)", f[pos[0]:])
        if m:
            pos[0] += m.end()
            return int(m.group(1) or m.group(2))
        return 1

    def groupe(fermant):
        atomes = {}
        while pos[0] < len(f):
            c = f[pos[0]]
            if c in ")]":
                pos[0] += 1
                return atomes
            if c in "([":
                pos[0] += 1
                interne = groupe(")" if c == "(" else "]")
                mult = lire_indice()
                for e, n in interne.items():
                    atomes[e] = atomes.get(e, 0) + n * mult
                continue
            m = re.match(r"[A-Z][a-z]?", f[pos[0]:])
            if not m:
                raise ValueError(f"formule illisible : {f!r} a {pos[0]}")
            pos[0] += m.end()
            n = lire_indice()
            atomes[m.group(0)] = atomes.get(m.group(0), 0) + n
        return atomes

    return groupe(None)


def analyser_espece(t):
    """(coefficient, atomes, charge) d'une espece ecrite comme `2Cr^{3+}`, `Fe^{2+}(aq)`, `e^{-}`, `CuSO_4\\cdot5H_2O`."""
    t = RE_ETAT.sub("", t).strip()
    m = re.match(r"(\d+)(.*)", t)
    coef, reste = (int(m.group(1)), m.group(2)) if m else (1, t)
    charge = 0
    mc = re.search(r"\^\{?(\d*)([+-])\}?$", reste)
    if mc:
        charge = int(mc.group(1) or 1) * (1 if mc.group(2) == "+" else -1)
        reste = reste[:mc.start()]
    if reste == "e":
        return coef, {}, charge
    atomes = {}
    for morceau in reste.split(r"\cdot"):
        mm = re.match(r"(\d+)(.*)", morceau)
        mult, formule_ = (int(mm.group(1)), mm.group(2)) if mm else (1, morceau)
        for e, n in analyser_formule(formule_).items():
            atomes[e] = atomes.get(e, 0) + n * mult
    return coef, atomes, charge


def totaux(cote):
    atomes, charge = {}, 0
    for t in termes(cote):
        coef, a, q = analyser_espece(t)
        for e, n in a.items():
            atomes[e] = atomes.get(e, 0) + n * coef
        charge += q * coef
    return atomes, charge


def tous_les_textes():
    for e in EX.values():
        yield f"ex{e['num']} intro", e["intro"]
        for s in e["subs"]:
            yield f"{e['num']}{s['num']} enonce", s["text"]
            yield f"{e['num']}{s['num']} rappel", s["rappel"]
            yield f"{e['num']}{s['num']} corrige", s["sol"] + " " + (s["ans"] or "") + " " + (s["piege"] or "") + " " + (s["conseil"] or "")
            for lib, _ in s["crit"]:
                yield f"{e['num']}{s['num']} critere", lib


nequations = 0
vues = set()
for origine, texte in tous_les_textes():
    for bloc in mathrm_blocs(texte):
        if r"\rightleftharpoons" in bloc:
            gauche, droite = bloc.split(r"\rightleftharpoons")
        elif r"\rightarrow" in bloc:
            gauche, droite = bloc.split(r"\rightarrow")
        else:
            continue
        # equations a conditions ou a deux fleches : non utilisees ici
        if r"\rightarrow" in droite or r"\rightleftharpoons" in droite:
            ecarts.append(f"{origine}: equation a deux fleches non analysee : {bloc}")
            continue
        try:
            ag, qg = totaux(gauche)
            ad, qd = totaux(droite)
        except Exception as exc:  # noqa: BLE001
            ecarts.append(f"{origine}: equation illisible {bloc!r} ({exc})")
            continue
        nequations += 1
        nverif += 1
        if ag != ad or qg != qd:
            ecarts.append(f"{origine}: equation NON equilibree {bloc} : gauche {ag} charge {qg} ; droite {ad} charge {qd}")
        vues.add(RE_ETAT.sub("", bloc))
# equations attendues (si l'une disparaissait de l'epreuve, le controle le dirait)
attendues = [
    r"CuSO_4\cdot5H_2O\rightarrow CuSO_4+5H_2O",
    r"(NH_4)_2SO_4+2NaOH\rightarrow Na_2SO_4+2NH_3+2H_2O",
    r"C_3H_4+4O_2\rightarrow3CO_2+2H_2O",
    r"Cr_2O_7^{2-}+14H^{+}+6e^{-}\rightarrow2Cr^{3+}+7H_2O",
    r"Cr_2O_7^{2-}+14H^{+}+6Fe^{2+}\rightarrow2Cr^{3+}+6Fe^{3+}+7H_2O",
    r"Ni+2Ag^{+}\rightarrow Ni^{2+}+2Ag",
    r"CH_3COOH+CH_3CH_2CH_2OH\rightleftharpoons CH_3COOCH_2CH_2CH_3+H_2O",
    r"[Cu(H_2O)_6]^{2+}+4NH_3\rightarrow[Cu(NH_3)_4(H_2O)_2]^{2+}+4H_2O",
    r"PbO+2OH^{-}+H_2O\rightarrow[Pb(OH)_4]^{2-}",
    r"Pb^{2+}+2I^{-}\rightarrow PbI_2",
]
for eq in attendues:
    nverif += 1
    if eq not in vues:
        ecarts.append(f"equation attendue absente de l'epreuve : {eq}")
vrai("au moins 30 equations analysees", nequations >= 30)

# ------------------------------------------------------------------------------------------------ blueprint
with open(os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-chemistry-p2-1.json"), encoding="utf8") as fh:
    bp = json.load(fh)
plan = {p["exercice"]: p for p in bp["sections_plan"]}
ok("blueprint 6 exercices", len(EX), 6)
for num, e in EX.items():
    ok(f"ex{num} points", e["pts"], plan[num]["points"])
    ok(f"ex{num} somme des sous-questions", sum(s["pts"] for s in e["subs"]), 20)
    ok(f"ex{num} nombre de questions", len(e["subs"]), plan[num]["nombre_questions"])
    for s in e["subs"]:
        vrai(f"ex{num}{s['num']} themes inclus dans les competences du blueprint", set(s["themes"]) <= set(plan[num]["competences"]))
        ok(f"ex{num}{s['num']} somme des criteres", sum(p for _, p in s["crit"]), s["pts"], 1e-9)
    vues_themes = {t for s in e["subs"] for t in s["themes"]}
    vrai(f"ex{num} couvre tous les themes du blueprint", vues_themes == set(plan[num]["competences"]))
ok("total des points", sum(e["pts"] for e in EX.values()), bp["bareme_total"])

# ------------------------------------------------------------------------------------------------ bilan
if ecarts:
    print(f"{len(ecarts)} ecart(s) sur {nverif} verifications")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print(f"{nverif} verifications, {nequations} equations equilibrees (atomes et charges), 0 ecart")
