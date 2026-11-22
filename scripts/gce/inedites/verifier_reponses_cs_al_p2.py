r"""Recalcul INDEPENDANT (sans sympy) des reponses de l'epreuve inedite GCE A Level Computer Science Paper 2 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_cs_al_p2.py

Chaque valeur numerique ou de trace du corrige est recalculee par une autre voie : conversions de base par programme, complement a deux par
recherche exhaustive, virgule flottante par enumeration des 4096 motifs, simulation du cycle fetch-execute et de l'ordonnancement, detection de
cycle dans un graphe, pagination, traduction du pseudocode en Python execute, base SQLite en memoire pour les requetes SQL, recursion comptee,
passage de parametres simule. La valeur annoncee doit aussi figurer dans le texte du corrige de la bonne sous-question. Controles de structure :
blueprint (8 exercices de 17 points, themes inclus dans les competences, tous couverts), grilles, absence de signe dollar, de tiret cadratin.
Sortie 0 s'il n'y a aucun ecart.
"""
import itertools
import json
import math
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_cs_al_p2 import exercices  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ecarts = []
nverif = 0
EX = {e["num"]: e for e in exercices()}


def sub(num, lettre):
    for s in EX[num]["subs"]:
        if s["num"] == lettre:
            return s
    raise KeyError((num, lettre))


def ok(nom, valeur, attendu, tol=1e-9):
    global nverif
    nverif += 1
    if abs(valeur - attendu) > tol:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def egal(nom, valeur, attendu):
    global nverif
    nverif += 1
    if valeur != attendu:
        ecarts.append(f"{nom}: calcule {valeur!r}, annonce {attendu!r}")


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


def complement_a_deux(valeur, bits):
    """Motif de `bits` bits (chaine) de l'entier `valeur`, par construction directe (modulo 2^bits)."""
    return format(valeur % (1 << bits), f"0{bits}b")


def lire_complement_a_deux(motif):
    n = int(motif, 2)
    return n - (1 << len(motif)) if motif[0] == "1" else n


# ================================================================================ Ex 1
# 1a : instruction de 18 bits, op-code de 7 bits
ok("1a op-codes", 2 ** 7, 128)
ok("1a bits d'operande", 18 - 7, 11)
ok("1a adresse la plus haute (toutes les valeurs d'operande, par enumeration)", max(range(2 ** 11)), 2047)
memoire = {40: 73, 73: 19}
operande = 40
immediat = operande
direct = memoire[operande]
indirect = memoire[memoire[operande]]
ok("1a immediat", immediat, 40); ok("1a direct", direct, 73); ok("1a indirect", indirect, 19)
present("1a", "1", "a", "128", "2047", "40", "73", "19")

# 1b : simulation du cycle fetch-execute, registres nommes
mem = {200: ("ADD", 30), 30: 12}
reg = {"PC": 200, "MAR": None, "MDR": None, "CIR": None, "ACC": 50}
journal = []
reg["MAR"] = reg["PC"]; journal.append("MAR<-PC")
reg["MDR"] = mem[reg["MAR"]]; reg["PC"] += 1; journal.append("MDR<-[MAR]; PC<-PC+1")
reg["CIR"] = reg["MDR"]; journal.append("CIR<-MDR")
egal("1b PC apres fetch", reg["PC"], 201)
op, adr = reg["CIR"]
reg["MAR"] = adr; reg["MDR"] = mem[reg["MAR"]]
if op == "ADD":
    reg["ACC"] = reg["ACC"] + reg["MDR"]
ok("1b ACC", reg["ACC"], 62)
egal("1b nombre d'etapes de fetch", len(journal), 3)
present("1b", "1", "b", "201", "62", "MAR ← PC", "CIR ← MDR")

# 1c : memoire
puces_par_puce = 4096
lignes_puce = math.ceil(math.log2(puces_par_puce))
ok("1c lignes d'une puce", lignes_puce, 12)
octets = 32 * 1024
nb_puces = octets // puces_par_puce
lignes_total = math.ceil(math.log2(octets))
ok("1c puces", nb_puces, 8); ok("1c lignes totales", lignes_total, 15)
ok("1c lignes de selection", lignes_total - lignes_puce, 3)
ok("1c 2^3 puces selectionnables", 2 ** (lignes_total - lignes_puce), nb_puces)
present("1c", "1", "c", "32768", "4096", "12", "15", "8")

# ================================================================================ Ex 2
# 2a
ok("2a hex -> decimal", int("2D7", 16), 727)
egal("2a hex -> binaire chiffre par chiffre", "".join(format(int(c, 16), "04b") for c in "2D7"), "001011010111")
egal("2a binaire sans zeros de tete", format(727, "b"), "1011010111")
egal("2a octal", format(301, "o"), "455")
ok("2a octal recompose", 4 * 64 + 5 * 8 + 5, 301)
ok("2a 727 par poids", 2 * 16 ** 2 + 13 * 16 + 7, 727)
table = [(a, b, a ^ b, a & b) for a in (0, 1) for b in (0, 1)]
egal("2a table du demi-additionneur", table, [(0, 0, 0, 0), (0, 1, 1, 0), (1, 0, 1, 0), (1, 1, 0, 1)])
# le demi-additionneur reproduit l'addition arithmetique de deux bits
for a, b, s, c in table:
    vrai(f"2a demi-additionneur {a}+{b}", 2 * c + s == a + b)
present("2a", "2", "a", "727", "455", "001011010111", "XOR", "AND")
texte = sub("2", "a")["sol"]
for ligne in ("| 0 | 0 | 0 | 0 |", "| 0 | 1 | 1 | 0 |", "| 1 | 0 | 1 | 0 |", "| 1 | 1 | 0 | 1 |"):
    nverif += 1
    if ligne not in texte:
        ecarts.append(f"2a ligne de table absente : {ligne}")

# 2b : complement a deux sur 8 bits, par recherche exhaustive des 256 motifs
tous = {format(i, "08b"): lire_complement_a_deux(format(i, "08b")) for i in range(256)}
motif_m58 = [m for m, v in tous.items() if v == -58]
egal("2b -58 unique", motif_m58, ["11000110"])
egal("2b 58 en binaire", format(58, "08b"), "00111010")
egal("2b inversion", "".join("1" if c == "0" else "0" for c in "00111010"), "11000101")
somme = (int("00101101", 2) + int("11000110", 2)) & 0xFF
egal("2b 45 + (-58) en binaire", format(somme, "08b"), "11110011")
ok("2b valeur", lire_complement_a_deux("11110011"), -13)
ok("2b 45 - 58", 45 - 58, -13)
ok("2b inversion de 11110011", int("00001100", 2) + 1, 13)
vrai("2b plage", min(tous.values()) == -128 and max(tous.values()) == 127)
s150 = (100 + 50) & 0xFF
egal("2b 100 + 50 en binaire", format(s150, "08b"), "10010110")
ok("2b 100 + 50 lu sur 8 bits", lire_complement_a_deux(format(s150, "08b")), -106)
egal("2b 100 binaire", format(100, "08b"), "01100100"); egal("2b 50 binaire", format(50, "08b"), "00110010")
vrai("2b 150 hors plage", 150 > 127)
present("2b", "2", "b", "11000110", "11110011", "-13", "10010110", "-106", "127")

# 2c : virgule flottante, mantisse 8 bits (point apres le 1er bit), exposant 4 bits, par enumeration de tous les motifs


def valeur_flottante(mant, expo):
    m = lire_complement_a_deux(mant) / 2 ** 7          # 8 bits : poids du premier bit = -1, dernier = 2^-7
    return m * 2 ** lire_complement_a_deux(expo)


def normalise(mant):
    return mant[0] != mant[1]


candidats = [(m, e) for m in (format(i, "08b") for i in range(256)) for e in (format(j, "04b") for j in range(16))
             if normalise(m) and abs(valeur_flottante(m, e) - 10.75) < 1e-12]
egal("2c representation normalisee de 10.75 (unique par enumeration)", candidats, [("01010110", "0100")])
ok("2c valeur de 10110000 / 0011", valeur_flottante("10110000", "0011"), -5.0)
ok("2c mantisse seule", lire_complement_a_deux("10110000") / 2 ** 7, -0.625)
vrai("2c mantisse 10110000 normalisee", normalise("10110000"))
egal("2c 10.75 binaire", format(10, "b") + "." + "11", "1010.11")
ok("2c 0.101011 x 2^4", int("101011", 2) / 2 ** 6 * 2 ** 4, 10.75)
# precision et etendue : on deplace un bit de la mantisse vers l'exposant (7 bits / 5 bits)
plus_grand_avant = max(valeur_flottante(format(i, "08b"), "0111") for i in range(256))
vrai("2c plus grand reel avec exposant 4 bits : 127/128 x 2^7", abs(plus_grand_avant - 127 / 128 * 2 ** 7) < 1e-12)
plus_grand_apres = (63 / 64) * 2 ** 15
vrai("2c etendue plus grande apres le deplacement", plus_grand_apres > plus_grand_avant)
vrai("2c pas plus fin avant (2^-7) que apres (2^-6)", 2 ** -7 < 2 ** -6)
present("2c", "2", "c", "01010110", "0100", "-0.625", "-5")

# ================================================================================ Ex 3
# 3a : simulation d'ordonnancement non preemptif
procs = {"A": (0, 6), "B": (1, 3), "C": (2, 8), "D": (4, 2)}


def ordonnancer(choix):
    t, restants, gantt, attente = 0, dict(procs), [], {}
    while restants:
        prets = [p for p, (a, _) in restants.items() if a <= t]
        if not prets:
            t = min(a for a, _ in restants.values())
            continue
        p = choix(prets, restants)
        a, b = restants.pop(p)
        gantt.append((p, t, t + b))
        attente[p] = t - a
        t += b
    return gantt, attente


gantt_sjf, att_sjf = ordonnancer(lambda prets, r: min(prets, key=lambda p: (r[p][1], r[p][0])))
gantt_fcfs, att_fcfs = ordonnancer(lambda prets, r: min(prets, key=lambda p: (r[p][0], p)))
egal("3a Gantt SJF", gantt_sjf, [("A", 0, 6), ("D", 6, 8), ("B", 8, 11), ("C", 11, 19)])
egal("3a attentes SJF", att_sjf, {"A": 0, "D": 2, "B": 7, "C": 9})
ok("3a moyenne SJF", sum(att_sjf.values()) / 4, 4.5)
egal("3a Gantt FCFS", gantt_fcfs, [("A", 0, 6), ("B", 6, 9), ("C", 9, 17), ("D", 17, 19)])
egal("3a attentes FCFS", att_fcfs, {"A": 0, "B": 5, "C": 7, "D": 13})
ok("3a moyenne FCFS", sum(att_fcfs.values()) / 4, 6.25)
vrai("3a SJF meilleur", sum(att_sjf.values()) < sum(att_fcfs.values()))
vrai("3a D est arrive a 4 pendant l'execution de A (0 a 6)", procs["D"][0] < 6)
present("3a", "3", "a", "A 0-6 | D 6-8 | B 8-11 | C 11-19", "4.5", "6.25", "0 - 0 = 0", "6 - 4 = 2", "8 - 1 = 7", "11 - 2 = 9", "17 - 4 = 13")

# 3b : cycle dans le graphe d'attente des trois processus
detient = {"imprimante": "P1", "scanner": "P2", "traceur": "P3"}
demande = {"P1": "scanner", "P2": "traceur", "P3": "imprimante"}
attend_de = {p: detient[r] for p, r in demande.items()}     # P -> processus qui detient ce qu'il demande


def a_un_cycle(g):
    for depart in g:
        vus, p = [], depart
        while p in g and p not in vus:
            vus.append(p)
            p = g[p]
        if p == depart:
            return vus
    return None


cycle = a_un_cycle(attend_de)
egal("3b cycle dans le graphe d'attente", sorted(cycle or []), ["P1", "P2", "P3"])
egal("3b ordre du cycle P1 -> P2 -> P3", cycle, ["P1", "P2", "P3"])
# sans le dernier arc, plus de cycle (la dependance circulaire est bien necessaire)
sans = dict(attend_de); del sans["P3"]
vrai("3b pas de cycle sans l'arc P3 -> P1", a_un_cycle(sans) is None)
present("3b", "3", "b", "P1 → scanner → P2 → plotter → P3 → printer → P1", "Mutual exclusion", "circular wait")

# 3c : pagination
taille = 2048
adresse = 5000
page, decal = divmod(adresse, taille)
egal("3c page et decalage", (page, decal), (2, 904))
table_pages = {0: 4, 1: 9, 2: 7, 3: 2}
physique = table_pages[page] * taille + decal
ok("3c adresse physique", physique, 15240)
ok("3c reconstitution : meme page/decalage", divmod(physique, taille)[1], decal)
ok("3c 2 x 2048", 2 * 2048, 4096); ok("3c 7 x 2048", 7 * 2048, 14336)
present("3c", "3", "c", "5000 - 4096 = 904", "7 × 2048 + 904 = 14336 + 904 = 15240", "15240")

# ================================================================================ Ex 4
# 4a
bits = 36 * 8
ok("4a megabits", bits, 288)
ok("4a temps", bits / 12, 24)
debit_eff = 0.75 * 12
ok("4a debit effectif", debit_eff, 9)
ok("4a temps effectif", bits / debit_eff, 32)


def bit_parite_paire(code7):
    return str(code7.count("1") % 2)


egal("4a nombre de 1 dans 1000011", "1000011".count("1"), 3)
octet = bit_parite_paire("1000011") + "1000011"   # bit de parite en tete (bit le plus a gauche)
egal("4a octet envoye", "1" + "1000011", octet)
egal("4a le motif 1000011 est bien C (ASCII 67)", format(ord("C"), "07b"), "1000011")
egal("4a octet", octet, "11000011")
egal("4a nombre de 1 de l'octet envoye pair", octet.count("1") % 2, 0)
egal("4a nombre de 1 recu", "10110110".count("1"), 5)
vrai("4a erreur detectee (nombre impair)", "10110110".count("1") % 2 == 1)
present("4a", "4", "a", "288", "24", "9", "32", "11000011", "10110110")

# 4c : paquets
taille_fichier, charge, entete = 2_400_000, 1200, 100
paquets = math.ceil(taille_fichier / charge)
ok("4c paquets", paquets, 2000)
total = paquets * (charge + entete)
ok("4c total", total, 2_600_000)
ok("4c total = fichier + en-tetes", taille_fichier + paquets * entete, total)
ok("4c pourcentage", round(100 * paquets * entete / total, 1), 7.7)
ok("4c pourcentage par paquet", round(100 * entete / (charge + entete), 1), 7.7)
ok("4c en-tetes", paquets * entete, 200_000)
present("4c", "4", "c", "2000", "2 600 000", "7.7", "200 000")

# ================================================================================ Ex 5
# 5a : chiffre de controle modulo 11
code = "438215"
poids = [7, 6, 5, 4, 3, 2]
produits = [int(c) * p for c, p in zip(code, poids)]
egal("5a produits", produits, [28, 18, 40, 8, 3, 10])
ok("5a somme", sum(produits), 107)
reste = sum(produits) % 11
ok("5a reste", reste, 8)
cle = 11 - reste
ok("5a chiffre de controle", cle, 3)
# le code complet est coherent : somme ponderee des 7 chiffres avec le poids 1 pour la cle = multiple de 11
ok("5a code complet 4382153 : somme + cle = multiple de 11", (sum(produits) + cle) % 11, 0)
present("5a", "5", "a", "107", "28", "18", "40", "3", "4382153")

# 5b : base SQLite en memoire, memes donnees que l'enonce
bd = sqlite3.connect(":memory:")
bd.executescript("""
CREATE TABLE CLASSROOM (ClassID TEXT PRIMARY KEY, Room TEXT, Teacher TEXT);
CREATE TABLE STUDENT (StudentID INTEGER PRIMARY KEY, FirstName TEXT, ClassID TEXT REFERENCES CLASSROOM(ClassID));
INSERT INTO CLASSROOM VALUES ('1A','B12','Mr Nkou'),('1B','B14','Mrs Tabi'),('2A','C03','Mr Eto');
INSERT INTO STUDENT VALUES (101,'Aline','1A'),(102,'Brice','1B'),(103,'Carine','1A'),(104,'Didier','2A'),(105,'Esther','1A'),(106,'Fabrice','1B');
""")
res_b = [r[0] for r in bd.execute("SELECT FirstName FROM STUDENT WHERE ClassID = '1A' ORDER BY FirstName;")]
egal("5b requete (ii)", res_b, ["Aline", "Carine", "Esther"])
res_c = list(bd.execute("SELECT ClassID, COUNT(*) FROM STUDENT GROUP BY ClassID;"))
egal("5b requete (iii)", sorted(res_c), [("1A", 3), ("1B", 2), ("2A", 1)])
sub_b = sub("5", "b")
dans_enonce("5b", "5", "b", "| 101 | Aline | 1A |", "| 106 | Fabrice | 1B |", "| 2A | C03 | Mr Eto |")
present("5b", "5", "b", "SELECT FirstName FROM STUDENT WHERE ClassID = '1A' ORDER BY FirstName;", "Aline, Carine, Esther",
        "SELECT ClassID, COUNT(*) FROM STUDENT GROUP BY ClassID;", "1A with 3, 1B with 2 and 2A with 1")


# 5c : chiffre de Cesar
def cesar(texte, k):
    return "".join(chr((ord(c) - 65 + k) % 26 + 65) for c in texte)


egal("5c chiffrement", cesar("DOUALA", 3), "GRXDOD")
egal("5c dechiffrement", cesar("HGHD", -3), "EDEA")
egal("5c aller-retour", cesar(cesar("DOUALA", 3), -3), "DOUALA")
present("5c", "5", "c", "GRXDOD", "EDEA", "`H → E`", "`G → D`", "`D → A`")

# ================================================================================ Ex 6
# 6a : le pseudocode est traduit en Python et execute avec trace
def algo_6a(n):
    total = 0
    lignes = []
    while n > 0:
        avant = n
        d = n % 10
        if d % 2 == 0:
            total = total + d
        n = n // 10
        lignes.append((avant, d, total, n))
    return total, lignes


sortie, lignes = algo_6a(48263)
ok("6a sortie", sortie, 20)
egal("6a trace", lignes, [(48263, 3, 0, 4826), (4826, 6, 6, 482), (482, 2, 8, 48), (48, 8, 16, 4), (4, 4, 20, 0)])
ok("6a somme des chiffres pairs (autre voie)", sum(int(c) for c in "48263" if int(c) % 2 == 0), 20)
egal("6a chiffres d", [l[1] for l in lignes], [3, 6, 2, 8, 4])
egal("6a total", [l[2] for l in lignes], [0, 6, 8, 16, 20])
egal("6a n apres DIV", [l[3] for l in lignes], [4826, 482, 48, 4, 0])
texte = sub("6", "a")["sol"]
for l in lignes:
    nverif += 1
    ligne = f"| {lignes.index(l) + 1} | {l[0]} | {l[1]} | {l[2]} | {l[3]} |"
    if ligne not in texte:
        ecarts.append(f"6a ligne de trace absente : {ligne}")
present("6a", "6", "a", "20", "6 + 2 + 8 + 4 = 20")


# 6b : tri a bulles traduit mot a mot
def tri_bulles(tab):
    a = [None] + list(tab)           # indices 1 a 6
    etats, echanges = [], []
    for passe in range(1, 6):
        n = 0
        for i in range(1, 6 - passe + 1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                n += 1
        etats.append(a[1:]); echanges.append(n)
    return etats, echanges


etats, echanges = tri_bulles([31, 12, 45, 8, 27, 19])
egal("6b apres la passe 1", etats[0], [12, 31, 8, 27, 19, 45])
egal("6b apres la passe 2", etats[1], [12, 8, 27, 19, 31, 45])
egal("6b echanges par passe", echanges, [4, 3, 2, 0, 0])
ok("6b total des echanges", sum(echanges), 9)
inversions = sum(1 for i, j in itertools.combinations(range(6), 2) if [31, 12, 45, 8, 27, 19][i] > [31, 12, 45, 8, 27, 19][j])
ok("6b inversions (autre voie)", inversions, 9)
egal("6b tableau final trie", etats[-1], sorted([31, 12, 45, 8, 27, 19]))
egal("6b apres la passe 3", etats[2], [8, 12, 19, 27, 31, 45])
present("6b", "6", "b", "[12, 31, 8, 27, 19, 45]", "[12, 8, 27, 19, 31, 45]", "[8, 12, 27, 19, 31, 45]", "[8, 12, 19, 27, 31, 45]", "9")

# 6c : recherche dichotomique
L = [3, 8, 12, 17, 21, 26, 30, 35, 41, 47, 52, 58, 63, 69, 74]
dans_enonce("6c", "6", "c", "3, 8, 12, 17, 21, 26, 30, 35, 41, 47, 52, 58, 63, 69, 74")
egal("6c liste triee", L, sorted(L)); ok("6c longueur", len(L), 15)


def dichotomie(cible):
    bas, haut, vus = 1, 15, []
    while bas <= haut:
        mil = (bas + haut) // 2
        vus.append((mil, L[mil - 1], bas, haut))
        if L[mil - 1] == cible:
            return vus
        if L[mil - 1] < cible:
            bas = mil + 1
        else:
            haut = mil - 1
    return vus


vus = dichotomie(30)
egal("6c positions examinees", [v[0] for v in vus], [8, 4, 6, 7])
egal("6c valeurs examinees", [v[1] for v in vus], [35, 17, 26, 30])
egal("6c limites avant chaque pas", [(v[2], v[3]) for v in vus], [(1, 15), (1, 7), (5, 7), (7, 7)])
pire = max(len(dichotomie(x)) for x in range(0, 80))
ok("6c pire cas par essai de toutes les cibles", pire, 4)
ok("6c 2^4 > 15 et 2^3 < 15", int(2 ** 4 > 15 and 2 ** 3 < 15), 1)
present("6c", "6", "c", "`mid = 8`", "`L[8] = 35 > 30`", "`high = 7`", "`mid = (1 + 7) DIV 2 = 4`", "`L[4] = 17 < 30`", "`low = 5`", "`L[6] = 26 < 30`", "`low = 7`", "`L[7] = 30`")

# ================================================================================ Ex 7
# 7b : le programme de saisie du mark est ecrit et execute sur les jeux d'essai
def accepte(saisie):
    try:
        v = int(saisie)
    except ValueError:
        return False
    if isinstance(saisie, float):
        return False
    return 0 <= v <= 100


jeux = [("64", True), ("0", True), ("100", True), ("-1", False), ("101", False), ("abc", False), ("6.5", False)]
for saisie, attendu in jeux:
    egal(f"7b entree {saisie}", accepte(saisie), attendu)
# test de mutation : une comparaison stricte est detectee par les extremes seulement
def accepte_faux(saisie):
    try:
        v = int(saisie)
    except ValueError:
        return False
    return 0 < v < 100


detectes = [s for s, att in jeux if accepte_faux(s) != att]
egal("7b les valeurs extremes decouvrent la comparaison stricte", detectes, ["0", "100"])
present("7b", "7", "b", "64", "0", "100", "-1", "101", "abc")
dans_enonce("7b", "7", "b", "0 to 100 inclusive")

# 7c : classification des erreurs executee
# instruction 2 : syntaxe valide, resultat faux ; instruction 3 : exception a l'execution
total_m, nb = 450, 9
egal("7c instruction 2 s'execute sans erreur et donne un resultat faux", total_m * nb != total_m / nb, True)
ok("7c moyenne correcte", total_m / nb, 50.0)
try:
    total_m / 0
    levee = False
except ZeroDivisionError:
    levee = True
egal("7c instruction 3 : division par zero a l'execution", levee, True)
try:
    compile('print("Average:" average)', "<7c>", "exec")
    syntaxe = False
except SyntaxError:
    syntaxe = True
egal("7c instruction 1 : refusee a la traduction", syntaxe, True)
present("7c", "7", "c", "syntax error", "logic error", "run-time error")

# ================================================================================ Ex 8
# 8c : recursion traduite et comptee
appels = []


def power(b, e):
    appels.append(e)
    if e == 0:
        return 1
    return b * power(b, e - 1)


ok("8c power(2,5)", power(2, 5), 32)
egal("8c appels", appels, [5, 4, 3, 2, 1, 0])
ok("8c nombre d'appels", len(appels), 6)
ok("8c 2^5 autre voie", 2 ** 5, 32)


def add_bonus_valeur(pay):
    pay = pay + 5000
    return pay


salaire = 80000
add_bonus_valeur(salaire)
ok("8c par valeur", salaire, 80000)
ref = {"salary": 80000}          # passage par reference : le parametre designe la meme case
def add_bonus_ref(cell):
    cell["salary"] = cell["salary"] + 5000
add_bonus_ref(ref)
ok("8c par reference", ref["salary"], 85000)
present("8c", "8", "c", "32", "6 calls", "80000", "85000")

# ================================================================================ textes : style et structure
nverif += 1
TEXTES = []
for e in EX.values():
    TEXTES.append((f"ex{e['num']} intro", e["intro"]))
    for s in e["subs"]:
        for nom, t in (("enonce", s["text"]), ("rappel", s["rappel"]), ("sol", s["sol"]), ("ans", s["ans"] or ""),
                       ("piege", s["piege"] or ""), ("conseil", s["conseil"] or "")):
            TEXTES.append((f"{e['num']}{s['num']} {nom}", t))
        for lib, _ in s["crit"]:
            TEXTES.append((f"{e['num']}{s['num']} critere", lib))
for nom, t in TEXTES:
    nverif += 3
    if "\u2014" in t:
        ecarts.append(f"{nom}: tiret cadratin")
    if "$" in t:
        ecarts.append(f"{nom}: signe dollar (le code est entre apostrophes inverses)")
    if t.count("`") % 2 and "```" not in t:
        ecarts.append(f"{nom}: apostrophes inverses non appariees")
    elif "```" in t and t.count("```") % 2:
        ecarts.append(f"{nom}: bloc de code non ferme")
# paragraphe de rappel unique et sans la reponse finale
for e in EX.values():
    for s in e["subs"]:
        nverif += 1
        if "\n\n" in s["rappel"]:
            ecarts.append(f"{e['num']}{s['num']}: rappel sur plusieurs paragraphes")
        nverif += 1
        if not (s["ans"] or "").strip() and s["num"] != "":
            if e["num"] in ("1", "2", "3", "4", "5", "6", "7", "8"):
                ecarts.append(f"{e['num']}{s['num']}: pas de reponse finale")

# ------------------------------------------------------------------------------------------------ blueprint
with open(os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-computerscience-p2-1.json"), encoding="utf8") as fh:
    bp = json.load(fh)
plan = {p["exercice"]: p for p in bp["sections_plan"]}
ok("blueprint 8 exercices", len(EX), 8)
for num, e in EX.items():
    ok(f"ex{num} points", e["pts"], plan[num]["points"])
    ok(f"ex{num} somme des sous-questions", sum(s["pts"] for s in e["subs"]), 17)
    ok(f"ex{num} nombre de questions", len(e["subs"]), plan[num]["nombre_questions"])
    vrai(f"ex{num} lettres a, b, c", [s["num"] for s in e["subs"]] == ["a", "b", "c"])
    for s in e["subs"]:
        vrai(f"ex{num}{s['num']} themes inclus dans les competences du blueprint", set(s["themes"]) <= set(plan[num]["competences"]))
        ok(f"ex{num}{s['num']} somme des criteres", sum(p for _, p in s["crit"]), s["pts"], 1e-9)
        vrai(f"ex{num}{s['num']} 2 a 5 criteres", 2 <= len(s["crit"]) <= 5)
    vues_themes = {t for s in e["subs"] for t in s["themes"]}
    vrai(f"ex{num} couvre tous les themes du blueprint", vues_themes == set(plan[num]["competences"]))
ok("total des points", sum(e["pts"] for e in EX.values()), bp["bareme_total"])
ok("total 136", sum(e["pts"] for e in EX.values()), 136)

# ------------------------------------------------------------------------------------------------ bilan
if ecarts:
    print(f"{len(ecarts)} ecart(s) sur {nverif} verifications")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print(f"{nverif} verifications, 0 ecart")
