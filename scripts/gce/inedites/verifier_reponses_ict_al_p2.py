r"""Recalcul INDEPENDANT (sans sympy) des reponses de l'epreuve inedite GCE A Level ICT Paper 2 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_ict_al_p2.py

Chaque valeur numerique ou de trace du corrige est recalculee par UNE AUTRE VOIE que celle du corrige :
  - ordonnancement : simulation d'une horloge (et non la somme des durees precedentes) ;
  - conversions : format binaire, module ipaddress, decalage de bits ; trames de transmission construites octet par octet ;
  - normalisation : donnees d'exemple, fermeture des dependances fonctionnelles, jointure sans perte dans sqlite3 ;
  - trace d'algorithme : execution Python du pseudo-code ; tables de verite : enumeration exhaustive ;
  - SQL : les requetes ecrites dans le corrige sont EXECUTEES dans sqlite3 sur les donnees de l'enonce ;
  - reseau : comptage des aretes d'un graphe, recherche du plus petit nombre de commutateurs par construction.
Puis coherence avec le blueprint (8 exercices, points, themes), avec les figures et absence de tiret cadratin.
Sortie 0 s'il n'y a aucun ecart.
"""
import ipaddress
import itertools
import json
import math
import os
import re
import sqlite3
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from questions_ict_al_p2 import exercices, PSEUDO_5A, PSEUDO_5A_BIS, SQL_8B_I, SQL_8B_II, SQL_8B_III  # noqa: E402
import figs_ict_al_p2 as figs  # noqa: E402

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
    if abs(float(valeur) - float(attendu)) > tol:
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


# ================================================================================ Ex 1b : ordonnancement par simulation d'horloge
BURST = {"P1": 7, "P2": 3, "P3": 5, "P4": 1}


def simuler(ordre):
    """Horloge : chaque processus attend dans la file jusqu'a son lancement (tous arrivent a t = 0)."""
    t, attentes = 0, {}
    for p in ordre:
        attentes[p] = t - 0
        t += BURST[p]
    return attentes


fcfs = simuler(["P1", "P2", "P3", "P4"])
sjf = simuler(sorted(BURST, key=lambda p: (BURST[p], p)))
vrai("1b ordre SJF", sorted(BURST, key=lambda p: (BURST[p], p)) == ["P4", "P2", "P3", "P1"])
vrai("1b attentes FCFS", [fcfs[p] for p in ("P1", "P2", "P3", "P4")] == [0, 7, 10, 15])
ok("1b moyenne FCFS", Fraction(sum(fcfs.values()), 4), 8.0)
vrai("1b attentes SJF", [sjf[p] for p in ("P4", "P2", "P3", "P1")] == [0, 1, 4, 9])
ok("1b moyenne SJF", Fraction(sum(sjf.values()), 4), 3.5)
# deuxieme voie : temps d'attente = fin - arrivee - burst, avec les temps de fin lus sur la ligne du temps
for ordre, att in ((["P1", "P2", "P3", "P4"], fcfs), (["P4", "P2", "P3", "P1"], sjf)):
    fin, t = {}, 0
    for p in ordre:
        t += BURST[p]
        fin[p] = t
    vrai("1b attente = fin - burst", all(att[p] == fin[p] - BURST[p] for p in ordre))
present("1b", "1", "b", "8.0", "3.5", "7+3=10", "10+5=15", "1+3=4", "4+5=9")

# ================================================================================ Ex 1c : flux de video
flux = 0
while Fraction(3, 2) * (flux + 1) <= 10:
    flux += 1
ok("1c nombre de flux", flux, 6)
vrai("1c 7 flux depassent le lien", Fraction(3, 2) * 7 > 10 and Fraction(3, 2) * 6 <= 10)
ok("1c rapport", 10 / 1.5, 6.67, 0.005)
present("1c", "1", "c", "6.67", "$6$")

# ================================================================================ Ex 2a : trames de transmission construites octet par octet
trames = []
for _ in range(4500):
    trames.append("0" + "1" * 8 + "1" + "1")   # start + 8 bits de donnees + parite + stop
nbits = sum(len(t) for t in trames)
ok("2a bits par octet", len(trames[0]), 11)
ok("2a bits totaux", nbits, 49500)
duree = Fraction(nbits, 9600)
ok("2a duree", float(duree), 5.15625, 1e-9)
ok("2a duree arrondie", round(float(duree), 2), 5.16)
ok("2a erreur sans bits de controle", 4500 * 8 / 9600, 3.75)
present("2a", "2", "a", "49\\,500", "5.16", "11")

# ================================================================================ Ex 2b : normalisation (donnees d'exemple, fermeture, jointure sans perte)
ATTRS = ["DeliveryNo", "DeliveryDate", "FarmerID", "FarmerName", "Village", "ProductCode", "ProductName", "PricePerKg", "KgDelivered"]
FDS = [
    ({"DeliveryNo"}, {"DeliveryDate", "FarmerID"}),
    ({"FarmerID"}, {"FarmerName", "Village"}),
    ({"ProductCode"}, {"ProductName", "PricePerKg"}),
    ({"DeliveryNo", "ProductCode"}, {"KgDelivered"}),
]


def fermeture(x, fds):
    c = set(x)
    change = True
    while change:
        change = False
        for g, d in fds:
            if g <= c and not d <= c:
                c |= d
                change = True
    return c


tous = set(ATTRS)
vrai("2b (DeliveryNo, ProductCode) est une cle", fermeture({"DeliveryNo", "ProductCode"}, FDS) == tous)
vrai("2b DeliveryNo seul n'est pas une cle", fermeture({"DeliveryNo"}, FDS) != tous)
vrai("2b ProductCode seul n'est pas une cle", fermeture({"ProductCode"}, FDS) != tous)
# dependances partielles : un attribut non cle determine par une partie de la cle
non_cle = tous - {"DeliveryNo", "ProductCode"}
partielles = {a for a in non_cle if a in fermeture({"DeliveryNo"}, FDS) or a in fermeture({"ProductCode"}, FDS)}
vrai("2b attributs a dependance partielle", partielles == {"DeliveryDate", "FarmerID", "FarmerName", "Village", "ProductName", "PricePerKg"})
vrai("2b KgDelivered depend de la cle entiere seulement", "KgDelivered" not in partielles)
# dependance transitive : FarmerID (non cle) determine FarmerName et Village
vrai("2b dependance transitive", {"FarmerName", "Village"} <= fermeture({"FarmerID"}, FDS) and "FarmerID" in fermeture({"DeliveryNo"}, FDS)
     and "FarmerID" not in {"DeliveryNo", "ProductCode"})
RELATIONS = {
    "DELIVERY": (["DeliveryNo", "DeliveryDate", "FarmerID"], ["DeliveryNo"]),
    "FARMER": (["FarmerID", "FarmerName", "Village"], ["FarmerID"]),
    "PRODUCT": (["ProductCode", "ProductName", "PricePerKg"], ["ProductCode"]),
    "DELIVERY_LINE": (["DeliveryNo", "ProductCode", "KgDelivered"], ["DeliveryNo", "ProductCode"]),
}
for nom, (att, cle) in RELATIONS.items():
    vrai(f"2b {nom}: la cle determine tous les attributs", fermeture(set(cle), FDS) >= set(att))
    # 3FN : aucun attribut non cle ne depend d'un autre attribut non cle ni d'une partie de la cle
    nc = set(att) - set(cle)
    sous_ens = [set(c) for r in range(1, len(cle) + 1) for c in itertools.combinations(cle, r) if set(c) != set(cle)]
    partiel = any(a in fermeture(s, FDS) for s in sous_ens for a in nc)
    trans = any(a in fermeture({b}, FDS) for b in nc for a in nc if a != b)
    vrai(f"2b {nom}: ni partielle ni transitive", not partiel and not trans)
flat = [
    ("D1", "2026-03-02", "F1", "Tchinda", "Bafang", "C1", "Cocoa", 1200, 80),
    ("D1", "2026-03-02", "F1", "Tchinda", "Bafang", "C2", "Coffee", 1500, 30),
    ("D2", "2026-03-05", "F2", "Nkeng", "Mbouda", "C1", "Cocoa", 1200, 120),
    ("D3", "2026-03-09", "F1", "Tchinda", "Bafang", "C1", "Cocoa", 1200, 65),
    ("D4", "2026-03-11", "F3", "Fotso", "Bafang", "C2", "Coffee", 1500, 45),
]
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE FLAT (" + ", ".join(ATTRS) + ")")
db.executemany("INSERT INTO FLAT VALUES (?,?,?,?,?,?,?,?,?)", flat)
db.execute("CREATE TABLE DELIVERY AS SELECT DISTINCT DeliveryNo, DeliveryDate, FarmerID FROM FLAT")
db.execute("CREATE TABLE FARMER AS SELECT DISTINCT FarmerID, FarmerName, Village FROM FLAT")
db.execute("CREATE TABLE PRODUCT AS SELECT DISTINCT ProductCode, ProductName, PricePerKg FROM FLAT")
db.execute("CREATE TABLE DELIVERY_LINE AS SELECT DeliveryNo, ProductCode, KgDelivered FROM FLAT")
joint = db.execute("SELECT DeliveryNo, DeliveryDate, FarmerID, FarmerName, Village, ProductCode, ProductName, PricePerKg, KgDelivered "
                   "FROM DELIVERY_LINE JOIN DELIVERY USING (DeliveryNo) JOIN FARMER USING (FarmerID) JOIN PRODUCT USING (ProductCode)").fetchall()
vrai("2b jointure sans perte ni ajout", sorted(joint) == sorted(flat))
ok("2b lignes FARMER", db.execute("SELECT COUNT(*) FROM FARMER").fetchone()[0], 3)
ok("2b cle de FARMER unique", db.execute("SELECT COUNT(DISTINCT FarmerID) FROM FARMER").fetchone()[0], 3)
ok("2b cle de DELIVERY_LINE unique", db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT DeliveryNo, ProductCode FROM DELIVERY_LINE)").fetchone()[0], len(flat))
# les relations ecrites dans le corrige sont bien les quatre calculees
sol2b = sub("2", "b")["sol"]
for nom, (att, cle) in RELATIONS.items():
    vrai(f"2b corrige ecrit {nom}", f"`{nom}({', '.join(att)})`" in sol2b)

# ================================================================================ Ex 3
# 3a : temps moyen d'acces simule sur 1000 requetes (900 dans le cache)
requetes = [4] * 900 + [50] * 100
ok("3a temps moyen", Fraction(sum(requetes), len(requetes)), 8.6, 1e-9)
ok("3a moyenne simple erronee", (4 + 50) / 2, 27.0)
present("3a", "3", "a", "8.6", "3.6", "5.0")
# 3b : graphe complet et etoile
n = figs.N_ORDINATEURS
ok("3b ordinateurs", n, 12)
ok("3b aretes du graphe complet", len(list(itertools.combinations(range(n), 2))), 66)
ok("3b cables de l'etoile", len([(0, i) for i in range(1, n + 1)]), 12)
ok("3b cables en plus", 66 - 12, 54)
ok("3b produit erronee", n * (n - 1), 132)
svg_etoile = figs.etoile()
vrai("3b la figure a au moins un trait par poste", svg_etoile.count("<line") >= n)
vrai("3b la figure compte douze postes", svg_etoile.count("stroke-linecap='round'") >= n)
present("3b", "3", "b", "66", "12")
# 3c : temps de transfert en fractions exactes
taille_bits = 450 * 1_000_000 * 8
debit = Fraction(80, 100) * 100 * 1_000_000
ok("3c taille en Mbit", taille_bits / 1e6, 3600)
ok("3c debit utile Mbit/s", float(debit) / 1e6, 80)
ok("3c temps", Fraction(taille_bits) / debit, 45)
ok("3c erreur sans facteur 8", 450 / 100, 4.5)
present("3c", "3", "c", "3600", "80", "45")

# ================================================================================ Ex 4
# 4a : adresse IPv4
adresse = "172.16.5.200"
binaire = ".".join(format(int(o), "08b") for o in adresse.split("."))
vrai("4a binaire", binaire == "10101100.00010000.00000101.11001000")
vrai("4a ipaddress", ipaddress.IPv4Address(adresse) == ipaddress.IPv4Address(int(binaire.replace(".", ""), 2)))
ok("4a nombre d'adresses", 1 << 32, 4294967296)
vrai("4a decomposition 172", 128 + 32 + 8 + 4 == 172 and 128 + 64 + 8 == 200)
vrai("4a erreur sans zeros de tete", format(5, "b") == "101" and format(5, "08b") == "00000101")
present("4a", "4", "a", "10101100.00010000.00000101.11001000", "4\\,294\\,967\\,296", "00000101", "11001000")
# 4b : licences
prix_copie, prix_site = 12500, 400000
ok("4b cout copie par copie", prix_copie * 40, 500000)
ok("4b economie", prix_copie * 40 - prix_site, 100000)
seuil = next(k for k in range(1, 100) if k * prix_copie > prix_site)
ok("4b plus petit nombre de copies (site moins cher)", seuil, 33)
ok("4b egalite a 32", 32 * prix_copie, prix_site)
ok("4b cout a 33", 33 * prix_copie, 412500)
vrai("4b le site couvre 40 postes", 40 <= 60)
present("4b", "4", "b", "500\\,000", "100\\,000", "33", "412\\,500")
# 4c : photographies
capacite_mo = 8 * 1024
ok("4c capacite en MB", capacite_mo, 8192)
ok("4c nombre de photos", math.floor(Fraction(capacite_mo) / Fraction(5, 2)), 3276)
ok("4c rapport", capacite_mo / 2.5, 3276.8, 1e-9)
vrai("4c 3277 photos depasseraient", Fraction(5, 2) * 3277 > capacite_mo)
ok("4c depassement", float(Fraction(5, 2) * 3277), 8192.5)
present("4c", "4", "c", "8192", "3276.8", "3276")

# ================================================================================ Ex 5a : execution du pseudo-code
def executer_5a(donnees):
    """Traduction directe du pseudo-code de PSEUDO_5A (la trace est enregistree a chaque tour)."""
    it = iter(donnees)
    total, heavy = 0, 0
    w = next(it)
    trace = []
    while w != 0:
        total = total + w
        if w >= 50:
            heavy = heavy + 1
        trace.append((w, total, heavy))
        w = next(it)
    return total, heavy, trace


DONNEES = [42, 65, 50, 18, 73, 0]
t5, h5, trace5 = executer_5a(DONNEES)
vrai("5a trace", trace5 == [(42, 42, 0), (65, 107, 1), (50, 157, 2), (18, 175, 2), (73, 248, 3)])
ok("5a total", t5, 248)
ok("5a heavy", h5, 3)
ok("5a total par somme directe", sum(x for x in DONNEES if x != 0), 248)
ok("5a heavy par comptage direct", sum(1 for x in DONNEES if x >= 50), 3)
for w, total, heavy in trace5:
    vrai(f"5a ligne {w} dans le tableau du corrige", f"| {w} | {total} | {heavy} |" in sub("5", "a")["sol"])
vrai("5a pseudo-code de l'enonce identique a celui execute", "total ← total + w" in PSEUDO_5A and "IF w >= 50 THEN" in PSEUDO_5A and "WHILE w <> 0 DO" in PSEUDO_5A)


def executer_5a_bis(donnees):
    it = iter(donnees)
    total = heavy = count = 0
    w = next(it)
    while w != 0:
        total += w
        count += 1
        if w >= 50:
            heavy += 1
        w = next(it)
    return (total, heavy, total / count) if count > 0 else "No delivery"


ok("5a moyenne", executer_5a_bis(DONNEES)[2], 49.6)
vrai("5a donnee vide", executer_5a_bis([0]) == "No delivery")
vrai("5a pseudo-code modifie", "count ← count + 1" in PSEUDO_5A_BIS and "IF count > 0 THEN" in PSEUDO_5A_BIS)

# ================================================================================ Ex 6
# 6b : plus petit nombre de commutateurs de 8 ports en chaine pour 30 postes (construction explicite)
def postes_libres(n_commutateurs, ports=8):
    libres = [ports] * n_commutateurs
    for i in range(n_commutateurs - 1):      # un cable entre i et i+1 : un port de chacun
        libres[i] -= 1
        libres[i + 1] -= 1
    return sum(libres)


plus_petit = next(n_ for n_ in range(1, 20) if postes_libres(n_) >= 30)
ok("6b plus petit nombre de commutateurs", plus_petit, 5)
ok("6b postes avec 4", postes_libres(4), 26)
ok("6b postes avec 5", postes_libres(5), 32)
vrai("6b formule 6n+2", all(postes_libres(n_) == 6 * n_ + 2 for n_ in range(1, 12)))
ok("6b n minimal non entier", 28 / 6, 4.67, 0.005)
present("6b", "6", "b", "6n+2", "26", "32")
# 6c : temps d'execution
cycles = 1_500_000_000 * 4
ok("6c cycles", cycles, 6_000_000_000)
ok("6c temps", Fraction(cycles) / Fraction(25, 10) / 1_000_000_000, 2.4, 1e-12)
ok("6c instructions par seconde", 2.5e9 / 4, 625e6)
present("6c", "6", "c", "2.4", "6\\,000\\,000\\,000")

# ================================================================================ Ex 7
# 7a
pixels = 1280 * 720
ok("7a pixels", pixels, 921600)
ok("7a octets", pixels * 24 // 8, 2764800)
ok("7a MB", round(pixels * 24 / 8 / 1e6, 2), 2.76)
ok("7a laser par page", Fraction(35000, 2500), 14)
ok("7a encre par page", Fraction(15000, 500), 30)
ok("7a laser 1200 pages", 1200 * Fraction(35000, 2500), 16800)
ok("7a encre 1200 pages", 1200 * Fraction(15000, 500), 36000)
# par cartouches entieres : meme resultat (1200 pages = 0.48 cartouche de toner, 2.4 cartouches d'encre, au prorata)
ok("7a toner au prorata", Fraction(1200, 2500) * 35000, 16800)
ok("7a encre au prorata", Fraction(1200, 500) * 15000, 36000)
present("7a", "7", "a", "921\\,600", "2\\,764\\,800", "2.76", "16\\,800", "36\\,000", "14", "30")
# 7b
total_mo = Fraction(12) * Fraction(7, 2)
ok("7b total MB", total_mo, 42)
ok("7b total Mbit", total_mo * 8, 336)
ok("7b duree", total_mo * 8 / 2, 168)
ok("7b minutes et secondes", divmod(168, 60)[0] * 100 + divmod(168, 60)[1], 248)
present("7b", "7", "b", "42", "336", "168")

# ================================================================================ Ex 8a : table de verite par enumeration
lignes = []
for s_, d_, w_ in itertools.product((0, 1), repeat=3):
    x_ = int(bool(s_) and (bool(d_) or bool(w_)))
    lignes.append((s_, d_, w_, x_))
vrai("8a colonne de sortie", [l[3] for l in lignes] == [0, 0, 0, 0, 0, 1, 1, 1])
ok("8a nombre de lignes a 1", sum(l[3] for l in lignes), 3)
for s_, d_, w_, x_ in lignes:
    vrai(f"8a ligne {s_}{d_}{w_} dans le corrige", f"| {s_} | {d_} | {w_} | {x_} |" in sub("8", "a")["sol"])
# De Morgan : verification exhaustive de la forme donnee
for s_, d_, w_ in itertools.product((0, 1), repeat=3):
    x_ = int(bool(s_) and (bool(d_) or bool(w_)))
    rhs = int((not s_) or ((not d_) and (not w_)))
    vrai(f"8a De Morgan {s_}{d_}{w_}", int(not x_) == rhs)
# erreur classique : NOT D OR NOT W n'est pas equivalent
vrai("8a la mauvaise forme est fausse", any(int(not (d_ or w_)) != int((not d_) or (not w_)) for d_, w_ in itertools.product((0, 1), repeat=2)))
# cas verifie dans le corrige : S=1, D=0, W=0
vrai("8a cas S=1 D=0 W=0", int(1 and (0 or 0)) == 0 and int(not 0) == 1 and int((not 1) or ((not 0) and (not 0))) == 1)
# circuit de la figure : meme fonction que l'expression
for s_, d_, w_ in itertools.product((0, 1), repeat=3):
    vrai(f"8a circuit {s_}{d_}{w_}", figs.evaluer(figs.CIRCUIT, {"S": s_, "D": d_, "W": w_}) == int(bool(s_) and (bool(d_) or bool(w_))))

# ================================================================================ Ex 8b : SQL execute dans sqlite3
bd = sqlite3.connect(":memory:")
bd.executescript("""
CREATE TABLE FARMER (FarmerID TEXT PRIMARY KEY, FarmerName TEXT, Village TEXT);
CREATE TABLE DELIVERY (DeliveryID TEXT PRIMARY KEY, FarmerID TEXT REFERENCES FARMER(FarmerID), Kg INTEGER, DeliveryMonth TEXT);
INSERT INTO FARMER VALUES ('F01','Tchamba Paul','Bafang'),('F02','Nkeng Ruth','Mbouda'),('F03','Fotso Jean','Bafang'),('F04','Mbarga Alice','Mbouda');
INSERT INTO DELIVERY VALUES ('D1','F01',120,'Oct'),('D2','F02',80,'Oct'),('D3','F01',150,'Nov'),('D4','F03',60,'Nov'),('D5','F02',90,'Nov'),('D6','F04',200,'Nov');
""")
# les donnees de l'enonce sont celles de la base
texte_8b = sub("8", "b")["text"]
for ligne in ("| F01 | Tchamba Paul | Bafang |", "| F02 | Nkeng Ruth | Mbouda |", "| F03 | Fotso Jean | Bafang |", "| F04 | Mbarga Alice | Mbouda |",
              "| D1 | F01 | 120 | Oct |", "| D2 | F02 | 80 | Oct |", "| D3 | F01 | 150 | Nov |", "| D4 | F03 | 60 | Nov |", "| D5 | F02 | 90 | Nov |", "| D6 | F04 | 200 | Nov |"):
    vrai(f"8b donnee de l'enonce {ligne}", ligne in texte_8b)
r1 = [r[0] for r in bd.execute(SQL_8B_I.rstrip(";")).fetchall()]
vrai("8b requete (i)", r1 == ["Fotso Jean", "Tchamba Paul"])
r2 = bd.execute(SQL_8B_II.rstrip(";")).fetchall()
vrai("8b requete (ii)", r2 == [("Bafang", 210), ("Mbouda", 290)])
r3 = [r[0] for r in bd.execute(SQL_8B_III.rstrip(";")).fetchall()]
vrai("8b requete (iii)", r3 == ["Mbarga Alice", "Tchamba Paul"])
sans_distinct = [r[0] for r in bd.execute(SQL_8B_III.rstrip(";").replace("DISTINCT ", "")).fetchall()]
vrai("8b sans DISTINCT Tchamba apparait deux fois", sans_distinct.count("Tchamba Paul") == 2)
# erreur annoncee : sans le filtre de mois, Bafang ferait 330
ok("8b Bafang sans filtre de mois", bd.execute("SELECT SUM(Kg) FROM FARMER JOIN DELIVERY USING (FarmerID) WHERE Village='Bafang'").fetchone()[0], 330)
sol8b = sub("8", "b")["sol"]
for requete in (SQL_8B_I, SQL_8B_III):
    vrai("8b requete ecrite dans le corrige", requete in sol8b)
vrai("8b requete (ii) dans l'enonce", SQL_8B_II in texte_8b)
vrai("8b resultat (ii) dans le corrige", "| Bafang | 210 |" in sol8b and "| Mbouda | 290 |" in sol8b)
present("8b", "8", "b", "Fotso Jean, Tchamba Paul", "Mbarga Alice, Tchamba Paul", "150+60=210", "90+200=290")
# 8c : table de liaison executable avec integrite referentielle
bd2 = sqlite3.connect(":memory:")
bd2.execute("PRAGMA foreign_keys = ON")
bd2.executescript("""
CREATE TABLE STUDENT (StudentID TEXT PRIMARY KEY, StudentName TEXT);
CREATE TABLE BOOK (BookID TEXT PRIMARY KEY, Title TEXT);
CREATE TABLE LOAN (StudentID TEXT REFERENCES STUDENT(StudentID), BookID TEXT REFERENCES BOOK(BookID), LoanDate TEXT, PRIMARY KEY (StudentID, BookID, LoanDate));
INSERT INTO STUDENT VALUES ('S1','A'),('S2','B'); INSERT INTO BOOK VALUES ('B1','X'),('B2','Y');
INSERT INTO LOAN VALUES ('S1','B1','2026-01-10'),('S1','B2','2026-01-12'),('S2','B1','2026-02-01'),('S1','B1','2026-03-05');
""")
ok("8c prets enregistres (meme eleve, meme livre, dates differentes)", bd2.execute("SELECT COUNT(*) FROM LOAN").fetchone()[0], 4)
try:
    bd2.execute("INSERT INTO LOAN VALUES ('S9','B1','2026-04-01')")
    refuse = False
except sqlite3.IntegrityError:
    refuse = True
vrai("8c l'integrite referentielle refuse un eleve inexistant", refuse)
try:
    bd2.execute("INSERT INTO LOAN VALUES ('S1','B1','2026-01-10')")
    doublon = False
except sqlite3.IntegrityError:
    doublon = True
vrai("8c la cle composee refuse un pret identique", doublon)

# ================================================================================ coherence avec le blueprint et le texte
with open(os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-ict-p2-1.json"), encoding="utf8") as fh:
    bp = json.load(fh)
plan = {p["exercice"]: p for p in bp["sections_plan"]}
ok("blueprint 8 exercices", len(EX), 8)
for num, e in EX.items():
    ok(f"ex{num} points", e["pts"], plan[num]["points"])
    ok(f"ex{num} somme des sous-questions", sum(s["pts"] for s in e["subs"]), plan[num]["points"])
    ok(f"ex{num} nombre de questions", len(e["subs"]), plan[num]["nombre_questions"])
    for s in e["subs"]:
        vrai(f"ex{num}{s['num']} themes inclus dans les competences du blueprint", set(s["themes"]) <= set(plan[num]["competences"]))
        ok(f"ex{num}{s['num']} somme des criteres", sum(p for _, p in s["crit"]), s["pts"])
        vrai(f"ex{num}{s['num']} rappel en un paragraphe", "\n\n" not in s["rappel"])
        vrai(f"ex{num}{s['num']} grille de 2 a 6 criteres", 2 <= len(s["crit"]) <= 6)
    vues = {t for s in e["subs"] for t in s["themes"]}
    vrai(f"ex{num} couvre tous les themes du blueprint", vues == set(plan[num]["competences"]))
ok("total des points", sum(e["pts"] for e in EX.values()), bp["bareme_total"])
ok("duree", bp["duree_minutes"], 150)

# aucun tiret cadratin, aucun tiret demi-cadratin, pas de dollar impair
for e in EX.values():
    for s in e["subs"]:
        for nom in ("text", "rappel", "sol", "ans", "piege", "conseil"):
            t = s[nom] or ""
            nverif += 1
            if "\u2014" in t or "\u2013" in t:
                ecarts.append(f"{e['num']}{s['num']} {nom}: tiret cadratin")
            if t.count("$") % 2:
                ecarts.append(f"{e['num']}{s['num']} {nom}: nombre impair de signes dollar")
        for lib, _ in s["crit"]:
            nverif += 1
            if lib.count("$") % 2 or "\u2014" in lib:
                ecarts.append(f"{e['num']}{s['num']} critere: dollar impair ou tiret cadratin")

# les figures sont celles des sous-questions annoncees et se rendent sans exception
vrai("figures de 3b et 8a", sub("3", "b")["fig"] == "etoile" and sub("8", "a")["fig"] == "circuit")
for nom, svg in figs.toutes().items():
    vrai(f"figure {nom} sans guillemet ni retour a la ligne", "\n" not in svg and '"' not in svg)

# ------------------------------------------------------------------------------------------------ bilan
if ecarts:
    print(f"{len(ecarts)} ecart(s) sur {nverif} verifications")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print(f"{nverif} verifications, 0 ecart")
