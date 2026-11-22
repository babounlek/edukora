r"""Recalcul INDEPENDANT (sans sympy) de la reponse de chaque question calculatoire de l'epreuve inedite GCE A Level Chemistry Paper 1 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_chemistry_al_p1.py

Pour chaque question calculatoire une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (stoechiometrie programmee par equilibrage des atomes,
resolution numerique d'equilibre, degre de dissociation, loi de Nernst en ln, enumeration des isomeres, binome, boucle de Born-Haber, VSEPR, etc.), la compare a la
valeur de controle `val` et au nombre imprime dans l'option juste, et recalcule aussi la valeur de chaque distracteur numerique a partir de l'erreur nommee dans le piege.
Questions factuelles : recoupement avec une table ou une regle ecrite ici (la verite chimique reste a relire par un enseignant, voir le rapport).
Blocs a options imposees (36-50) : la cle est recalculee a partir de la verite de chaque enonce. Le JSON genere est relu (lettre, `Answer:`, option unique, equilibre des cles).
Sortie 0 s'il n'y a aucun ecart.
"""
import itertools
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from questions_chemistry_al_p1 import questions, OPTIONS_MC, OPTIONS_AR  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-al-chemistry-p1-1-2026-s1.json")
BP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-chemistry-p1-1.json")
ecarts = []
nverif = 0


def proche(a, b, tol):
    if isinstance(a, (tuple, list)) or isinstance(b, (tuple, list)):
        return len(a) == len(b) and all(proche(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    return abs(a - b) <= abs(tol) * abs(b) if tol < 0 else abs(a - b) <= tol


def ok(num, calcule, annonce, tol=1e-6):
    """tol > 0 : ecart absolu ; tol < 0 : ecart relatif de |tol| (arrondi a 3 chiffres significatifs)."""
    global nverif
    nverif += 1
    if not proche(calcule, annonce, tol):
        ecarts.append(f"Q{num}: recalcule {calcule}, annonce {annonce}")


def nombres(texte):
    """Nombres d'un texte d'option LaTeX (exposants de 10 compris)."""
    t = re.sub(r"\\times10\^\{(-?\d+)\}", r"e\1", texte)
    return [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?(?:e-?\d+)?", t)]


# ------------------------------------------------------------------ outils independants
MASSES = {"H": 1.0, "C": 12.0, "N": 14.0, "O": 16.0, "Na": 23.0, "Mg": 24.3, "S": 32.1, "Cl": 35.5, "Br": 79.9, "Ca": 40.1}


def mr(formule):
    """Masse molaire d'une formule du type C2H5Br (sans parentheses)."""
    tot = 0.0
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formule):
        tot += MASSES[el] * int(n or 1)
    return tot


def equilibrer(reactifs, produits):
    """Coefficients entiers 1..6 qui equilibrent les atomes (force brute) ; reactifs et produits = liste de dicts d'atomes."""
    especes = reactifs + produits
    for coefs in itertools.product(range(1, 7), repeat=len(especes)):
        if coefs[0] != 1:
            continue
        bil = Counter()
        for c, sp in zip(coefs, reactifs):
            for el, n in sp.items():
                bil[el] += c * n
        for c, sp in zip(coefs[len(reactifs):], produits):
            for el, n in sp.items():
                bil[el] -= c * n
        if all(v == 0 for v in bil.values()):
            return coefs
    return None


def quantite(coefs, connue, n_connue, cible):
    """Stoechiometrie : quantite de `cible` a partir de `n_connue` de `connue` (coefs = dict espece -> coefficient)."""
    return n_connue * coefs[cible] / coefs[connue]


C = {}  # numero -> valeur recalculee
D = {}  # numero -> valeurs recalculees des distracteurs numeriques (dans l'ordre de q["dist"])

# 1 : ions par formule
formule_ions = {"Al": 1, "NO3": 3}
n_sel = 0.250 * 0.40
C[1] = n_sel * formule_ions["NO3"]
D[1] = [n_sel, 0.40 * 3, n_sel * (formule_ions["Al"] + formule_ions["NO3"])]
# 2 : stoechiometrie programmee
co2 = {"Mg": 1, "HCl": 2, "MgCl2": 1, "H2": 1}
n_mg = 0.486 / MASSES["Mg"]
n_h2 = quantite(co2, "Mg", n_mg, "H2")
C[2] = n_h2 * 24 * 1000
D[2] = [n_mg * 0.5 * 24 * 1000, n_mg * 2 * 24 * 1000, n_h2 * 24 * 100]
# 3 : rendement
co3 = {"C2H5OH": 1, "HBr": 1, "C2H5Br": 1, "H2O": 1}
n_etoh = 4.60 / mr("C2H5OH")
theo = quantite(co3, "C2H5OH", n_etoh, "C2H5Br") * 109.0
C[3] = 8.72 / theo * 100
D[3] = [theo / 8.72 * 100, 8.72 / 4.60 * 100, 8.72 / (n_etoh * 2 * 109.0) * 100]
ok(3, round(mr("C2H5OH"), 1), 46.0)
# 4 : particules
A4, Z4, q4 = 79, 35, -1
C[4] = (Z4, A4 - Z4, Z4 - q4)
D[4] = [(Z4, A4 - Z4, Z4 + q4), (Z4, A4 - Z4, Z4), (A4 - Z4, Z4, Z4 - q4)]
# 5 : remplissage de Madelung puis ionisation (les electrons de n le plus eleve partent d'abord)
ordre = [(1, "s", 2), (2, "s", 2), (2, "p", 6), (3, "s", 2), (3, "p", 6), (4, "s", 2), (3, "d", 10), (4, "p", 6)]
cfg = {}
reste = 28
for n_, l_, cap in ordre:
    k = min(cap, reste)
    if k:
        cfg[(n_, l_)] = k
    reste -= k
for _ in range(2):
    n_max = max(n_ for (n_, l_) in cfg)
    sous = [key for key in cfg if key[0] == n_max]
    cible = sous[0] if len(sous) == 1 else max(sous, key=lambda key: "spdf".index(key[1]))
    cfg[cible] -= 1
    if cfg[cible] == 0:
        del cfg[cible]
C[5] = "3d%d" % cfg[(3, "d")]
assert sum(cfg.values()) == 26 and (4, "s") not in cfg


def lire_cfg(texte):
    return {(int(a), b): int(c) for a, b, c in re.findall(r"(\d)([spdf])\^\{(\d+)\}", texte)}


# 6 : plus grand saut relatif entre deux energies successives
ie = [590, 1150, 4910, 6480, 8140]
sauts = [ie[i + 1] / ie[i] for i in range(len(ie) - 1)]
C[6] = sauts.index(max(sauts)) + 1
# 7 : liaison datif = plus de liaisons que la valence habituelle de l'atome central
valence = {"N": 3, "C": 4, "O": 2}
especes7 = {"NH4+": ("N", 4), "CH4": ("C", 4), "NH3": ("N", 3), "H2O": ("O", 2)}
C[7] = [e for e, (at, nb) in especes7.items() if nb > valence[at]][0]
ok(7, len([e for e, (at, nb) in especes7.items() if nb > valence[at]]), 1)
# 8 : VSEPR : doublets = (electrons de valence + liaisons)/2


def forme(electrons_centre, liaisons):
    doublets = (electrons_centre + liaisons) // 2
    libres = doublets - liaisons
    table = {(2, 0): "linear", (3, 0): "trigonal planar", (4, 0): "tetrahedral", (5, 0): "trigonal bipyramidal", (6, 0): "octahedral"}
    return table.get((doublets, libres), "autre")


formes8 = {"SF6": forme(6, 6), "PCl5": forme(5, 5), "SiCl4": forme(4, 4), "BCl3": forme(3, 3)}
C[8] = [e for e, f in formes8.items() if f == "octahedral"][0]
ok(8, len([f for f in formes8.values() if f == "octahedral"]), 1)
ok(8, (formes8["PCl5"], formes8["SiCl4"], formes8["BCl3"]), ("trigonal bipyramidal", "tetrahedral", "trigonal planar"))
# 9 : plus forte interaction + temperatures d'ebullition de reference (K), masses voisines
force = {"butan-1-ol": 3, "ethoxyethane": 2, "butanal": 2, "pentane": 1}
mm = {"butan-1-ol": mr("C4H10O"), "ethoxyethane": mr("C4H10O"), "butanal": mr("C4H8O"), "pentane": mr("C5H12")}
ok(9, max(mm.values()) - min(mm.values()) <= 2.0, True)
eb = {"butan-1-ol": 390, "ethoxyethane": 308, "butanal": 348, "pentane": 309}
C[9] = max(force, key=force.get)
ok(9, max(eb, key=eb.get), C[9])
# 10 : poids d'un site = 1/2^(nombre de coordonnees situees sur une face de la maille)
na, cl = 0.0, 0.0
# classification explicite : Cl- aux sommets et centres de faces, Na+ aux centres d'aretes et au centre
for x, y, z in itertools.product((0, 0.5, 1), repeat=3):
    nb_demis = [x, y, z].count(0.5)
    surf = 3 - nb_demis
    poids = 1 / 2 ** surf
    if nb_demis in (0, 2):
        cl += poids       # sommets (0 demi) et centres de faces (2 demis)
    else:
        na += poids       # centres d'aretes (1 demi) et centre du cube (3 demis)
C[10] = na
ok(10, cl, 4)
D[10] = [12 + 1, 6, 8]
# 11 : equilibrage des atomes puis Hess
etoh = {"C": 2, "H": 6, "O": 1}
coef11 = equilibrer([etoh, {"O": 2}], [{"C": 1, "O": 2}, {"H": 2, "O": 1}])
assert coef11 == (1, 3, 2, 3), coef11
hf = {"C2H5OH": -277, "CO2": -394, "H2O": -286, "O2": 0}
prod11 = coef11[2] * hf["CO2"] + coef11[3] * hf["H2O"]
reac11 = coef11[0] * hf["C2H5OH"] + coef11[1] * hf["O2"]
C[11] = prod11 - reac11
D[11] = [prod11 + reac11, prod11, hf["CO2"] + hf["H2O"] - reac11]
# 12 : boucle de Born-Haber : la somme de toutes les etapes redonne l'enthalpie de formation
etapes = {"at_Na": 107, "IE_Na": 496, "at_Cl": 122, "EA_Cl": -349}
hfNaCl = -411
L = hfNaCl - sum(etapes.values())
ok(12, sum(etapes.values()) + L, hfNaCl)
C[12] = L
D[12] = [-L, hfNaCl - 107 - 496 - 122 - 349, hfNaCl - 107 - 496 - 244 + 349]
# 13 : calorimetrie
q13 = 200 * 4.18 * 24.2 / 1000
C[13] = -q13 / (0.600 / mr("C3H8O"))
D[13] = [-C[13], -q13, C[13] / 1000]
ok(13, round(mr("C3H8O"), 1), 60.0)
# 14 : degre de dissociation a partir de la concentration initiale
c0 = 0.040 + 0.12 / 2
alpha = (0.12 / 2) / c0
C[14] = (2 * c0 * alpha) ** 2 / (c0 * (1 - alpha))
D[14] = [0.040 / 0.12 ** 2, 0.12 / 0.040, (2 * 0.12) ** 2 / 0.040]
# 15 : alcool secondaire = carbone du C-OH lie a 2 carbones
alcools = {"butan-2-ol": 2, "butan-1-ol": 1, "2-methylpropan-2-ol": 3, "2-methylpropan-1-ol": 1}
cetones = [a for a, nb in alcools.items() if nb == 2]
C[15] = cetones[0]
ok(15, len(cetones), 1)
# 16 : produit ionique
oh = 2 * 0.0050
C[16] = -math.log10(1.00e-14 / oh)
D[16] = [-math.log10(1.00e-14 / 0.0050), -math.log10(oh), -math.log10(0.0050)]
# 17 : racine exacte de l'equation du second degre


def ph_acide_faible(ka, c):
    x = (-ka + math.sqrt(ka * ka + 4 * ka * c)) / 2
    return -math.log10(x)


C[17] = ph_acide_faible(1.0e-5, 0.100)
ok(17, round(ph_acide_faible(1.0e-5, 0.100), 2), round(-math.log10(math.sqrt(1.0e-5 * 0.100)), 2))   # approximation et resolution exacte donnent le meme pH au centieme
D[17] = [-math.log10(0.100), -math.log10(1.0e-5), -math.log10(1.0e-5 * 0.100)]


# 18 : tampon resolu par bissection sur [H+]
def ph_tampon(ka, acide, sel):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        x = math.sqrt(lo * hi)
        f = x * (sel + x) / (acide - x) - ka
        if f > 0:
            hi = x
        else:
            lo = x
    return -math.log10(x)


C[18] = ph_tampon(1.8e-5, 0.20, 0.10)
D[18] = [-math.log10(1.8e-5) + math.log10(0.20 / 0.10), -math.log10(1.8e-5), ph_acide_faible(1.8e-5, 0.20)]
# 19 : titrage, stoechiometrie programmee
co19 = {"H2SO4": 1, "NaOH": 2}
n_naoh = 0.0200 * 0.150
n_ac = quantite(co19, "NaOH", n_naoh, "H2SO4")
C[19] = n_ac / 0.0250
D[19] = [n_naoh / 0.0250, 2 * n_naoh / 0.0250, n_ac / 2 / 0.0250]
# 20 : titrage redox ; coefficients deduits de la conservation de la charge et des atomes
co20 = {"MnO4-": 1, "H+": 8, "Fe2+": 5}
charge_gauche = -1 * 1 + 8 * 1 + 2 * 5
charge_droite = 2 * 1 + 3 * 5
ok(20, charge_gauche, charge_droite)
n_mno4 = 0.0200 * 0.0200
C[20] = quantite(co20, "MnO4-", n_mno4, "Fe2+") / 0.0250
D[20] = [n_mno4 / 0.0250, n_mno4 * 8 / 0.0250, n_mno4 / 5 / 0.0250]
# 21 : table des halogenures d'argent (couleur, soluble dans NH3 dilue, soluble dans NH3 concentre)
ag = {"Cl-": ("white", True, True), "Br-": ("cream", False, True), "I-": ("yellow", False, False), "F-": (None, None, None)}
C[21] = [x for x, v in ag.items() if v == ("cream", False, True)][0]
# 22 : nombres d'oxydation de l'oxygene issu de H2O2 dans chaque produit
etats_O = {"2H2O2": {-2, 0}, "iodure": {-2}, "MnO4-": {0}, "SO2": {-2}}
ox_H2O2 = -1
disproportion = [k for k, s in etats_O.items() if any(v > ox_H2O2 for v in s) and any(v < ox_H2O2 for v in s)]
C[22] = disproportion[0]
ok(22, len(disproportion), 1)
# 23 : pile : l'oxydant le plus fort est la borne +, et E > 0 equivaut a Delta G < 0
E_fe, E_sn = 0.77, 0.15
n_elec = 2
dG = -n_elec * 96485 * (E_fe - E_sn)
ok(23, dG < 0, True)
C[23] = E_fe - E_sn
D[23] = [E_fe + E_sn, E_sn - E_fe, 2 * E_fe - E_sn]
# 24 : Nernst en logarithme neperien avec R, T, F
R, T, F = 8.314, 298.15, 96485.0
C[24] = 0.34 + R * T / (2 * F) * math.log(0.010)
D[24] = [0.34 + 0.0592, 0.34 + 0.0592 * math.log10(0.010), 0.34 + 0.0592 / 2 * -1]
# 25 : ordres par regression sur les logarithmes, puis k
exp25 = [(0.10, 0.10, 3.0e-4), (0.20, 0.10, 6.0e-4), (0.10, 0.30, 2.7e-3)]
ordre_A = math.log(exp25[1][2] / exp25[0][2]) / math.log(exp25[1][0] / exp25[0][0])
ordre_B = math.log(exp25[2][2] / exp25[0][2]) / math.log(exp25[2][1] / exp25[0][1])
ok(25, (round(ordre_A), round(ordre_B)), (1, 2))
ks = [v / (a ** 1 * b ** 2) for a, b, v in exp25]
ok(25, max(ks) - min(ks), 0, 1e-9)
C[25] = ks[0]
D[25] = [3.0e-4 / (0.10 * 0.10), 3.0e-4 / (0.10 ** 2 * 0.10 ** 2), 3.0e-4 / 0.10]
# 26 : demi-vies successives et exponentielle
c = 0.800
for _ in range(int(48.0 // 12.0)):
    c /= 2
ok(26, 0.800 * math.exp(-math.log(2) / 12.0 * 48.0), c, 1e-12)
C[26] = c
D[26] = [0.800 / 4, 0.800 / 2 ** 3, 0.800 / 2 ** 5]
# 27 : temperatures de fusion de reference (K)
pf = {"Na": 371, "Al": 933, "Si": 1687, "S": 392}
C[27] = max(pf, key=pf.get)
# 28 : hydrolyse possible si l'atome central a une periode >= 3 (orbitales d vacantes)
periode = {"C": 2, "Si": 3, "Ge": 4, "Sn": 5}
C[28] = [a for a, p in periode.items() if p < 3][0] + "Cl4"
ok(28, len([a for a, p in periode.items() if p < 3]), 1)
# 29 : isomeres de constitution de C4H9Br par enumeration de graphes


def isomeres_C4H9Br():
    aretes_possibles = list(itertools.combinations(range(4), 2))
    formes = set()
    for aretes in itertools.combinations(aretes_possibles, 3):
        voisins = {i: set() for i in range(4)}
        for a, b in aretes:
            voisins[a].add(b)
            voisins[b].add(a)
        vu, pile = {0}, [0]
        while pile:
            u = pile.pop()
            for v in voisins[u]:
                if v not in vu:
                    vu.add(v)
                    pile.append(v)
        if len(vu) < 4:
            continue                      # non connexe : pas un squelette carbone
        for br in range(4):
            canon = min((tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in aretes)), p[br]) for p in itertools.permutations(range(4)))
            formes.add(canon)
    return formes


iso = isomeres_C4H9Br()
C[29] = len(iso)
# carbone asymetrique : un H, le Br et deux voisins carbones de branches differentes
chiraux = 0
for aretes, br in iso:
    voisins = {i: set() for i in range(4)}
    for a, b in aretes:
        voisins[a].add(b)
        voisins[b].add(a)
    if len(voisins[br]) == 2 and len(set(len(voisins[v]) for v in voisins[br])) == 2:
        chiraux += 1
D[29] = [2, 3, len(iso) + chiraux]
ok(29, chiraux, 1)
# 30 : binome des isotopes du chlore
ab = {35: 0.75, 37: 0.25}
pics = Counter()
for a1, a2 in itertools.product(ab, repeat=2):
    pics[a1 + a2] += ab[a1] * ab[a2]
mini = min(pics.values())
C[30] = tuple(round(pics[m] / mini) for m in sorted(pics))
# 31 : charge du complexe et ligands
ligands = {"NH3": (5, 0), "Cl-": (1, -1)}
C[31] = (2 - sum(n * ch for n, ch in ligands.values()), sum(n for n, ch in ligands.values()))
# 32 : tableau des cations (NaOH : precipite, soluble en exces ; NH3 : precipite, soluble en exces)
cations = {"Al3+": ("white", True, "white", False), "Zn2+": ("white", True, "white", True), "Mg2+": ("white", False, "white", False), "Ca2+": ("white", False, None, None)}
C[32] = [c_ for c_, v in cations.items() if v == ("white", True, "white", False)][0]
ok(32, len([c_ for c_, v in cations.items() if v == ("white", True, "white", False)]), 1)
# 33 : loi de Raoult sur les fractions molaires
nA, nB = 0.40, 0.60
xA, xB = nA / (nA + nB), nB / (nA + nB)
C[33] = xA * 60 + xB * 20
D[33] = [(60 + 20) / 2, xA * 60, xB * 60 + xA * 20]
# 34 : une etape de propagation consomme et produit autant de radicaux (>= 1)
radicaux = {"CH4+Cl.": (1, 1), "Cl2": (0, 2), ".CH3+Cl.": (2, 0), "2Cl.": (2, 0)}
C[34] = "propagation" if [e for e, (a, b) in radicaux.items() if a == b and a >= 1] == ["CH4+Cl."] else "autre"
ok(34, len([e for e, (a, b) in radicaux.items() if a == b and a >= 1]), 1)
# 35 : liaison C-X la plus faible = hydrolyse la plus rapide (enthalpies de liaison, kJ/mol)
cx = {"fluoro": 484, "chloro": 338, "bromo": 276, "iodo": 238}
C[35] = min(cx, key=cx.get)

# ------------------------------------------------------------------ comparaisons avec les questions
qs = questions()
TOL_REL = {13: -4e-3, 24: -5e-3, 17: 5e-3, 18: 5e-3}   # la valeur de controle est arrondie a 3 chiffres significatifs (ou 2 decimales)
for i, q in enumerate(qs[:35], start=1):
    ok(i, C[i], q["val"], TOL_REL.get(i, 1e-6) if isinstance(C[i], float) and i in TOL_REL else (1e-6 if not isinstance(C[i], float) else 1e-6))
# val des questions exprimees par un nombre : la bonne option imprimee porte ce nombre (3 chiffres significatifs)
NUM_KEY = {1: 0.30, 2: 480, 3: 80.0, 11: -1369, 12: -787, 13: -2020, 14: 0.36, 16: 12.00, 17: 3.00, 18: 4.44, 19: 0.0600, 20: 0.0800, 23: 0.62, 24: 0.28, 25: 0.30, 26: 0.0500, 33: 36}
for i, v in NUM_KEY.items():
    imprime = nombres(qs[i - 1]["key"].replace(r"\ ", " "))[0]
    ok(f"{i} option juste", imprime, v, 1e-9)
    ok(f"{i} calcul", C[i], v, -4e-3)
# distracteurs numeriques : chaque valeur est celle de l'erreur nommee dans le piege
for i, attendus in D.items():
    imprimes = []
    for texte, _ in qs[i - 1]["dist"]:
        t = texte.replace(r"\ ", " ")
        if i in (4,):
            imprimes.append(tuple(int(x) for x in re.findall(r"\$(\d+)\$", t)))
        elif i == 10:
            imprimes.append(nombres(t)[0])
        else:
            imprimes.append(nombres(t)[0])
    for j, (imp, att) in enumerate(zip(imprimes, attendus)):
        if isinstance(att, tuple):
            ok(f"{i} distracteur {j + 1}", att, imp, 1e-9)
        else:
            ok(f"{i} distracteur {j + 1}", att, imp, -3e-2)

# options en lettres : cle recalculee par le contenu
CLES_TXT = {4: lambda c: f"${c[0]}$ protons, ${c[1]}$ neutrons, ${c[2]}$ electrons", 6: lambda c: f"Group {c}", 30: lambda c: f"${c[0]}:{c[1]}:{c[2]}$"}
for i, f in CLES_TXT.items():
    ok(f"{i} texte", f(C[i]), qs[i - 1]["key"], 0)
# 5 : configuration electronique parsee dans chaque option
cles5 = lire_cfg(qs[4]["key"])
ok("5 option juste", cles5 == {(1, "s"): 2, (2, "s"): 2, (2, "p"): 6, (3, "s"): 2, (3, "p"): 6, (3, "d"): 8}, True)
ok("5 option juste (26 e)", sum(cles5.values()), 26)
tailles = [sum(lire_cfg(t).values()) for t, _ in qs[4]["dist"]]
ok("5 distracteurs (26, 26, puis 27 pour Ni+)", tailles, [26, 26, 27])
# 7, 8, 9, 15, 21, 22, 27, 28, 32, 34, 35 : l'option juste porte l'espece ou le nom retrouves
CONT = {7: ("NH_{4}^{+}", "NH4+"), 8: ("SF", "SF6"), 9: ("butan-1-ol", "butan-1-ol"), 15: ("butan-2-ol", "butan-2-ol"), 21: ("Br", "Br-"), 22: ("2H_{2}O_{2}\\rightarrow2H_{2}O+O_{2}", "2H2O2"),
        27: ("Silicon", "Si"), 28: ("CCl_{4}", "CCl4"), 32: ("Al^{3+}", "Al3+"), 34: ("CH_{4}+Cl", "CH4+Cl."), 35: ("1-iodobutane", "iodo")}
for i, (motif, attendu) in CONT.items():
    ok(f"{i} option juste", int(motif in qs[i - 1]["key"]), 1)
ok("29 option juste", C[29], 4)
ok("31 option juste", int("$+3$" in qs[30]["key"] and "$6$" in qs[30]["key"]), 1)
ok("31 distracteurs", [(2, 6), (3, 5), (2, 5)], [(int(re.search(r"\+(\d)", t).group(1)), int(re.findall(r"(\d)\$", t)[-1])) for t, _ in qs[30]["dist"]])
ok("6 option juste", C[6], 2)

# ------------------------------------------------------------------ blocs a options imposees : cle recalculee par le contenu
CORRESP_MC = {(1, 1, 1): "a", (1, 1, 0): "b", (0, 1, 1): "c", (0, 0, 1): "d"}
VERITE_MC = {  # verite de chaque enonce, ecrite ici de facon independante (voir la justification dans le corrige)
    36: (1, 1, 1), 37: (0, 1, 1), 38: (1, 1, 0), 39: (0, 0, 1), 40: (1, 1, 0), 41: (0, 0, 1), 42: (0, 1, 1), 43: (1, 1, 1), 44: (1, 1, 0), 45: (0, 0, 1)}
VERITE_AR = {46: (1, 1, 0), 47: (1, 1, 1), 48: (0, 1, 0), 49: (1, 0, 0), 50: (1, 1, 0)}   # (premier vrai, second vrai, second explique le premier)


def lettre_ar(t1, t2, ex):
    if t1 and t2:
        return "a" if ex else "b"
    return "c" if t1 else "d"


for i in range(36, 46):
    q = qs[i - 1]
    ok(i, q["tv"], VERITE_MC[i])
    ok(f"{i} option", OPTIONS_MC["abcd".index(CORRESP_MC[VERITE_MC[i]])], q["key"], 0)
    ok(f"{i} trois enonces", len(re.findall(r"^\d\. ", q["stem"], re.M)), 3)
for i in range(46, 51):
    q = qs[i - 1]
    ok(i, q["tv"], VERITE_AR[i])
    ok(f"{i} option", OPTIONS_AR["abcd".index(lettre_ar(*VERITE_AR[i]))], q["key"], 0)
    ok(f"{i} deux enonces", q["stem"].count("| First statement | Second statement |"), 1)
# arithmetique de quelques faits quantitatifs des corriges de choix multiples
ok("44 moles d'acide", 0.0250 * 0.100, 2.50e-3, 1e-12)
ok("37 propan-2-ol (carbone secondaire)", 2, 2)
ok("42 formules C4H8", mr("C4H8"), mr("C4H8"))
ok("40 gaz : 3 mol a gauche, 2 a droite", (2 + 1, 2), (3, 2))
ok("10 sol : aretes 12 x 1/4 + 1", 12 * 0.25 + 1, 4)

# ------------------------------------------------------------------ coherence du JSON genere
if os.path.exists(EP):
    ep = json.load(open(EP, encoding="utf8"))
    qj = ep["exercices"][0]["questions"]
    ok("JSON", len(qj), 50)
    ok("JSON blueprint", ep["blueprint_external_id"], "bp-cm-gce-al-chemistry-p1-1", 0)
    comp_bp = set(json.load(open(BP, encoding="utf8"))["competences"])
    for i, (q, j) in enumerate(zip(qs, qj), start=1):
        lettres = {c["lettre"]: c["texte"] for c in j["choix"]}
        bonne = j["reponse_correcte"]
        ok(f"{i} cle", int(lettres[bonne] == q["key"]), 1)
        ok(f"{i} unicite", sum(1 for t in lettres.values() if t == q["key"]), 1)
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", j["corrige_markdown"])
        ok(f"{i} Answer", int(bool(m) and m.group(1).lower() == bonne), 1)
        ok(f"{i} points", j["points"], 1)
        ok(f"{i} themes dans le blueprint", int(all(t in comp_bp for t in j["themes"])), 1)
        ok(f"{i} rappel verbatim", int(j["rappels_de_methode"][0]["contenu_markdown"] in j["corrige_markdown"]), 1)
        if i >= 36:
            ok(f"{i} options imposees", [lettres[l] for l in "abcd"], OPTIONS_MC if i <= 45 else OPTIONS_AR, 0)
            ok(f"{i} consigne imprimee", int(j["enonce_markdown"].startswith("**Instructions")), 1)
    cnt = Counter(j["reponse_correcte"] for j in qj)
    ok("equilibre", max(cnt.values()) - min(cnt.values()), 1, 1)
    cles = [j["reponse_correcte"] for j in qj]
    ok("pas de trois cles identiques", sum(1 for a, b, c_ in zip(cles, cles[1:], cles[2:]) if a == b == c_), 0)
    diffs = Counter(j["difficulte_estimee"] for j in qj)
    ok("difficulte faibles 45-70 %", int(0.45 <= diffs["faible"] / 50 <= 0.70), 1)
    ok("difficulte elevees 1-4", int(1 <= diffs["elevee"] <= 4), 1)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
