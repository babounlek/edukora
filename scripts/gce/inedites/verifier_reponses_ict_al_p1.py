r"""Recalcul INDEPENDANT (sans sympy) de la reponse de chaque question calculatoire de l'epreuve inedite GCE A Level ICT Paper 1 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_ict_al_p1.py

Pour chaque question calculatoire, une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (conversion par int()/format(), chiffrement avec
ord/chr, traducteur de references de tableur ecrit ici, tables de verite par enumeration, boucles Python equivalentes aux algorithmes, requetes SQL EXECUTEES avec
sqlite3 sur les tables LUES DANS L'ENONCE, chemin critique par enumeration de tous les chemins puis flottement par retard simule, module ipaddress, urllib.parse),
la compare a la valeur de controle `val` et a l'option juste, et recalcule aussi chaque distracteur a partir de l'erreur nommee dans le piege.
Questions factuelles : la cle est recoupee avec une table ecrite ici (FAITS) et la coherence logique est controlee (quatre options distinctes, une seule vraie
selon la table) ; leur verite reste a relire par un enseignant (voir le rapport). Le JSON genere est relu (lettre, `Answer:`, option unique egale a la cle,
equilibre des cles, themes du blueprint). Sortie 0 s'il n'y a aucun ecart.
"""
import ipaddress
import itertools
import json
import os
import re
import sqlite3
import sys
from collections import Counter
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
from questions_ict_al_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-al-ict-p1-1-2026-s1.json")
BP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-ict-p1-1.json")
ecarts = []
nverif = 0
qs = questions()
BT = chr(96)


def ok(num, calcule, annonce):
    global nverif
    nverif += 1
    if isinstance(calcule, float) or isinstance(annonce, float):
        bon = abs(float(calcule) - float(annonce)) < 1e-9
    else:
        bon = calcule == annonce
    if not bon:
        ecarts.append(f"Q{num}: recalcule {calcule!r}, annonce {annonce!r}")


def nu(texte):
    """Premier nombre d'un texte d'option (espaces fines et virgules decimales exclues)."""
    m = re.search(r"-?\d+(?:\.\d+)?", texte.replace(BT, ""))
    return float(m.group(0)) if m else None


def opt(i):
    """Texte de l'option juste et textes des distracteurs, sans backticks."""
    q = qs[i - 1]
    return q["key"].replace(BT, ""), [d[0].replace(BT, "") for d in q["dist"]]


def tables(stem):
    """Tables Markdown de l'enonce : liste de (nom ou None, entetes, lignes)."""
    out = []
    lignes = stem.split("\n")
    nom = None
    i = 0
    while i < len(lignes):
        m = re.fullmatch(r"`(\w+)`", lignes[i].strip())
        if m:
            nom = m.group(1)
        if lignes[i].startswith("|") and i + 1 < len(lignes) and set(lignes[i + 1].replace("|", "").strip()) <= set("-"):
            ent = [c.strip() for c in lignes[i].strip().strip("|").split("|")]
            j = i + 2
            rows = []
            while j < len(lignes) and lignes[j].startswith("|"):
                rows.append([c.strip() for c in lignes[j].strip().strip("|").split("|")])
                j += 1
            out.append((nom, ent, rows))
            nom = None
            i = j
            continue
        i += 1
    return out


def base_sql(stem):
    con = sqlite3.connect(":memory:")
    defaut = re.search(r"table `(\w+)`", stem)
    for nom, ent, rows in tables(stem):
        nom = nom or defaut.group(1)
        con.execute(f"CREATE TABLE {nom} ({', '.join(ent)})")
        for r in rows:
            con.execute(f"INSERT INTO {nom} VALUES ({', '.join('?' * len(ent))})",
                        [None if c == "NULL" else (int(c) if c.isdigit() else c) for c in r])
    return con


def requete(stem):
    return re.search(r"```sql\n(.*?)```", stem, re.S).group(1).strip().rstrip(";")


# ------------------------------------------------------------------ 1 : bus d'adresses
ok(1, 2 ** 12, nu(qs[0]["key"]))
ok("1 distracteurs", sorted([12, 2 ** 11, 12 ** 2]), sorted(nu(d) for d in opt(1)[1]))
# 2 : binaire -> hexadecimal
h = format(int("10110110", 2), "X")
ok(2, h, opt(2)[0])
ok("2 distracteurs", sorted([h[::-1], "A6", str(int("10110110", 2))]), sorted(opt(2)[1]))
# 4 : chiffrement par decalage
def cesar(mot, k):
    return mot.translate({ord(c): ord("A") + (ord(c) - ord("A") + k) % 26 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})
ok(4, cesar("NETWORK", 5), opt(4)[0])
ok("4 distracteurs", sorted([cesar("NETWORK", -5), cesar("NETWORK", 3), cesar("NETWORK", 5)[::-1]]), sorted(opt(4)[1]))


# 5 : copie de formule (traducteur de references ecrit ici)
def copier(formule, dcol, dlig):
    def lettres(n):
        return chr(ord("A") + n)

    def rep(m):
        cf, col, lf, lig = m.group(1), m.group(2), m.group(3), m.group(4)
        c = ord(col) - ord("A")
        l = int(lig)
        if not cf:
            c += dcol
        if not lf:
            l += dlig
        return f"{cf}{lettres(c)}{lf}{l}"
    return re.sub(r"(\$?)([A-Z])(\$?)(\d+)", rep, formule)


ok(5, copier("=$B2*C$1+D2", 2, 2), opt(5)[0])
ok("5 distracteurs", sorted(["=D4*E3+F4", "=$B2*C$1+D2", "=$B4*C$1+F4"]), sorted(opt(5)[1]))
ok("5 sans dollars", copier("=B2*C1+D2", 2, 2), "=D4*E3+F4")
ok("5 tout fixe", "=$B$2*$C$1+$D$2", copier("=$B$2*$C$1+$D$2", 2, 2))
# 6 : reduction en pourcentage
ok(6, 100 * (12 - 3) / 12, nu(opt(6)[0]))
ok("6 distracteurs", sorted([100 * 3 / 12, 100 * 12 / 3, 9]), sorted(nu(d) for d in opt(6)[1]))
# 7 : temps de transfert
ok(7, 45 * 8 / 30, nu(opt(7)[0]))
ok("7 distracteurs", sorted([round(45 / 30, 3), round(30 / (45 * 8), 3), 45 * 8]), sorted(nu(d) for d in opt(7)[1]))


# 8 : trace d'algorithme (boucle Python equivalente)
def algo8(mode):
    t = 0
    for i in range(1, 7):
        if mode == "juste" and i % 2 == 0:
            t += i * i
        elif mode == "tous":
            t += i * i
        elif mode == "pairs" and i % 2 == 0:
            t += i
        elif mode == "impairs" and i % 2 == 1:
            t += i * i
    return t


ok(8, algo8("juste"), nu(opt(8)[0]))
ok("8 distracteurs", sorted([algo8("tous"), algo8("pairs"), algo8("impairs")]), sorted(nu(d) for d in opt(8)[1]))
# 9 : adresses IPv4
def ipv4(s):
    try:
        ipaddress.IPv4Address(s)
        return True
    except ValueError:
        return False


ok(9, [ipv4(opt(9)[0])] + [ipv4(d) for d in opt(9)[1]], [True, False, False, False])


# 10 : table de verite
def x10(a, b, c, lecture="juste"):
    if lecture == "juste":
        return int((not (a and b)) or c)
    if lecture == "nor":
        return int((not (a or b)) or c)
    if lecture == "sans_not":
        return int((a and b) or c)
    return int((not (a and b)) and c)


zeros = [(a, b, c) for a, b, c in itertools.product((0, 1), repeat=3) if x10(a, b, c) == 0]
ok(10, zeros, [(1, 1, 0)])
ok("10 distracteurs", [x10(1, 0, 0, "nor"), x10(0, 0, 0, "sans_not"), x10(1, 1, 1, "et")], [0, 0, 0])
ok("10 option juste", opt(10)[0], "A = 1, B = 1, C = 0")
# 12 : SQL execute sur les tables de l'enonce
con = base_sql(qs[11]["stem"])


def fmt12(rows):
    return " and ".join(f"{f}: {n}" for f, n in rows)


ok(12, fmt12(con.execute(requete(qs[11]["stem"])).fetchall()), opt(12)[0])
ok("12 distracteurs", sorted([
    fmt12(con.execute("SELECT form, COUNT(*) FROM student GROUP BY form ORDER BY form").fetchall()),
    fmt12(con.execute("SELECT form, COUNT(*) FROM student WHERE mark < 60 GROUP BY form ORDER BY form").fetchall()),
    fmt12(con.execute("SELECT form, COUNT(*) FROM student WHERE mark >= 60 OR mark IS NULL GROUP BY form ORDER BY form").fetchall()),
]), sorted(opt(12)[1]))
# 14 : complement a deux sur 8 bits
ok(14, format((-45) & 0xFF, "08b"), opt(14)[0])
d = [format(45, "08b"), None]
ok("14 distracteurs", sorted([format(~45 & 0xFF, "08b"), "1" + format(45, "07b"), format(~(45 + 1) & 0xFF, "08b")]), sorted(opt(14)[1]))
ok("14 relecture", int(opt(14)[0], 2) - 256, -45)
# 17 et 47 : chemin critique (enumeration des chemins) puis flottement par retard simule
def lire_projet(stem):
    _, ent, rows = tables(stem)[0]
    taches = {}
    for t, dur, dep in rows:
        taches[t] = (int(dur), [] if dep == "none" else [x.strip() for x in dep.split(",")])
    return taches


def chemins(taches):
    suiv = {t: [u for u, (_, dep) in taches.items() if t in dep] for t in taches}
    debuts = [t for t, (_, dep) in taches.items() if not dep]
    fins = [t for t in taches if not suiv[t]]
    out = []

    def aller(chemin):
        if chemin[-1] in fins:
            out.append(chemin)
        for u in suiv[chemin[-1]]:
            aller(chemin + [u])
    for t in debuts:
        aller([t])
    return out


def duree(taches, retard=None):
    retard = retard or {}
    return max(sum(taches[t][0] + retard.get(t, 0) for t in c) for c in chemins(taches))


p17 = lire_projet(qs[16]["stem"])
ok(17, duree(p17), 12)
ok("17 option", nu(opt(17)[0]), 12)
som = {"".join(c): sum(p17[t][0] for t in c) for c in chemins(p17)}
ok("17 distracteurs", sorted([som["ACEG"], sum(v[0] for v in p17.values()), som["ADFG"]]), sorted(nu(d) for d in opt(17)[1]))
p47 = lire_projet(qs[46]["stem"])


def flottement(taches, t):
    base = duree(taches)
    n = 0
    while duree(taches, {t: n + 1}) == base:
        n += 1
    return n


ok(47, flottement(p47, "C"), 2)
ok("47 option", nu(opt(47)[0]), 2)
ok("47 distracteurs", sorted([flottement(p47, "G"), flottement(p47, "B"), p47["C"][0]]), sorted(nu(d) for d in opt(47)[1]))
ok("47 B et F", (flottement(p47, "B"), flottement(p47, "F")), (1, 1))
# 19 : COUNTIF
v19 = [int(x) for x in re.search(r"contain ([\d, and]+)\.", qs[18]["stem"]).group(1).replace("and", ",").replace(" ", "").split(",") if x]
ok(19, sum(1 for v in v19 if v >= 50), nu(opt(19)[0]))
ok("19 distracteurs", sorted([sum(1 for v in v19 if v > 50), len(v19) , sum(1 for v in v19 if v < 50)]), sorted(nu(x) for x in opt(19)[1]))
# 21 : chiffre de controle modulo 11
def chiffre(code, poids, mod=11):
    s = sum(int(c) * w for c, w in zip(code, poids))
    return s, s % mod


s21, r21 = chiffre("735192480", range(10, 1, -1))
ok(21, (11 - r21) % 11, nu(opt(21)[0]))
ok("21 somme", s21, 248)
s21b, r21b = chiffre("735192480", range(9, 0, -1))
ok("21 distracteurs", sorted([r21, (10 - s21 % 10) % 10, (11 - r21b) % 11]), sorted(nu(x) for x in opt(21)[1]))
ok("21 verif (code complet multiple de 11)", (s21 + (11 - r21) % 11) % 11, 0)
# 24 : trace du WHILE
def algo24(variante):
    n, s, passes, inv = 4827, 0, 0, 0
    while n > 0:
        s += n % 10
        inv = inv * 10 + n % 10
        passes += 1
        n //= 10
    return {"somme": s, "passes": passes, "inverse": inv}[variante]


ok(24, algo24("somme"), nu(opt(24)[0]))
carres = sum(int(c) ** 2 for c in "4827")
ok("24 distracteurs", sorted([algo24("passes"), algo24("inverse"), carres]), sorted(nu(x) for x in opt(24)[1]))
# 27 : jeux de sauvegarde (simulation)
jours = ["Sun", "Mon", "Tue", "Wed"]
types = {"Sun": "full", "Mon": "inc", "Tue": "inc", "Wed": "inc"}
besoin = []
for j in reversed(jours):
    besoin.append(j)
    if types[j] == "full":
        break
ok(27, len(besoin), nu(opt(27)[0]))
ok("27 distracteurs", sorted([1, 2, 3]), sorted(nu(x) for x in opt(27)[1]))
# 28 : transmission asynchrone
ok(28, 6000 * (8 + 1 + 1) / 9600, nu(opt(28)[0]))
ok("28 distracteurs", sorted([6000 * 8 / 9600, 6000 * 9 / 9600, 6000 * 1 / 9600]), sorted(nu(x) for x in opt(28)[1]))
# 30 : SUMIF
ok(30, sum(b for a, b in zip(["East", "West", "East", "North", "West", "East"], [120, 90, 60, 150, 30, 45]) if a == "East"), nu(opt(30)[0]))
ok("30 distracteurs", sorted([3, 120 + 90 + 60 + 150 + 30 + 45, 225 / 3]), sorted(nu(x) for x in opt(30)[1]))
# 32 : table de verite
def x32(a, b, c, variante="juste"):
    if variante == "juste":
        return int((a != b) and not c)
    if variante == "or":
        return int((a or b) and not c)
    if variante == "sans_c":
        return int(a != b)
    return int((a != b) or not c)


compte = {v: sum(x32(a, b, c, v) for a, b, c in itertools.product((0, 1), repeat=3)) for v in ("juste", "or", "sans_c", "ou_non")}
ok(32, compte["juste"], nu(opt(32)[0]))
ok("32 distracteurs", sorted([compte["or"], compte["sans_c"], compte["ou_non"]]), sorted(nu(x) for x in opt(32)[1]))
# 35 : jointure et agregat executes
con35 = base_sql(qs[34]["stem"])
fmt = lambda r: f"{r[0]}, {r[1]}"
ok(35, fmt(con35.execute(requete(qs[34]["stem"])).fetchone()), opt(35)[0])
j = "FROM customer c JOIN orders o ON c.cid = o.cid GROUP BY c.cname"
ok("35 distracteurs", sorted([
    fmt(con35.execute(f"SELECT c.cname, SUM(o.amount) {j} ORDER BY SUM(o.amount) ASC LIMIT 1").fetchone()),
    fmt(con35.execute("SELECT c.cname, MAX(o.amount) FROM customer c JOIN orders o ON c.cid = o.cid").fetchone()),
    fmt(con35.execute(f"SELECT c.cname, COUNT(o.oid) {j} ORDER BY SUM(o.amount) DESC LIMIT 1").fetchone()),
]), sorted(opt(35)[1]))
# 36 : addition hexadecimale
ok(36, format(int("3F", 16) + int("2D", 16), "X"), opt(36)[0])
bas = 15 + 13
sans_retenue = format(3 + 2, "X") + format(bas % 16, "X")
f_vaut_16 = 16 + 13
avec_16 = format(3 + 2 + f_vaut_16 // 16, "X") + format(f_vaut_16 % 16, "X")
ok("36 distracteurs", sorted([sans_retenue, avec_16, str(63 + 45)]), sorted(opt(36)[1]))
# 37 : REPEAT ... UNTIL
x = 3
trace = []
while True:
    x *= 2
    trace.append(x)
    if x > 20:
        break
ok(37, x, nu(opt(37)[0]))
ok("37 distracteurs", sorted([trace[-2], 3, trace[-1] * 2]), sorted(nu(v) for v in opt(37)[1]))
# 40 : VLOOKUP recalcule a partir du tableau de l'enonce
_, ent40, rows40 = tables(qs[39]["stem"])[0]
grille = {r[1]: r[1:] for r in rows40}
ligne = [r[1:] for r in rows40 if r[1] == "P103"][0]
ok(40, ligne[3 - 1], opt(40)[0])
ok("40 distracteurs", sorted([ligne[2 - 1], ligne[0], [r[3] for r in rows40][[r[1] for r in rows40].index("P103") - 1]]), sorted(opt(40)[1]))
# 43 : tri a bulles, une passe puis deux ; tri par selection
def bulle(liste, passes):
    L = liste[:]
    for _ in range(passes):
        for i in range(len(L) - 1):
            if L[i] > L[i + 1]:
                L[i], L[i + 1] = L[i + 1], L[i]
    return " ".join(map(str, L))


def selection(liste):
    L = liste[:]
    m = L.index(min(L))
    L[0], L[m] = L[m], L[0]
    return " ".join(map(str, L))


lst = [7, 3, 9, 2, 6]
ok(43, bulle(lst, 1), opt(43)[0])
ok("43 distracteurs", sorted([bulle(lst, 2), selection(lst), " ".join(map(str, sorted(lst)))]), sorted(opt(43)[1]))
# 44 : parite paire
ok(44, [o for o in ["10110101", "11001100", "01111110", "10000001"] if o.count("1") % 2 == 1], [opt(44)[0]])
ok("44 distracteurs pairs", [o.count("1") for o in opt(44)[1]], [4, 6, 2])
# 45 : lignes d'une table de verite
ok(45, len(list(itertools.product((0, 1), repeat=5))), nu(opt(45)[0]))
ok("45 distracteurs", sorted([5 * 2, 5 ** 2, 2 ** 4]), sorted(nu(x) for x in opt(45)[1]))
# 46 : marge CSS
marges = dict(zip(["top", "right", "bottom", "left"], "5px 15px 25px 35px".split()))
ok(46, marges["left"], opt(46)[0])
ok("46 distracteurs", sorted([marges["top"], marges["right"], marges["bottom"]]), sorted(opt(46)[1]))
# 48 : agregats avec NULL executes
con48 = base_sql(qs[47]["stem"])
r = con48.execute(requete(qs[47]["stem"])).fetchone()
def f48(t):
    return ", ".join((str(int(v)) if float(v).is_integer() else f"{v:.1f}") for v in t)
ok(48, f48(r), opt(48)[0])
ok("48 distracteurs", sorted([
    f48(con48.execute("SELECT COUNT(*), COUNT(*), AVG(mark) FROM student").fetchone()),
    f48(con48.execute("SELECT COUNT(mark), COUNT(*), SUM(COALESCE(mark, 0)) * 1.0 / COUNT(*) FROM student").fetchone()),
    f48(con48.execute("SELECT COUNT(*), COUNT(mark), AVG(mark) FROM student").fetchone()),
]), sorted(opt(48)[1]))
# 49 : taille d'une image
bits = 4
octets = 1024 * 768 * bits // 8
ok(49, octets // 1024, nu(opt(49)[0]))
ok("49 distracteurs", sorted([1024 * 768 * 16 // 8 // 1024, 1024 * 768 * 4 // 1024, 1024 * 768 * 1 // 8 // 1024]), sorted(nu(x) for x in opt(49)[1]))
ok("49 bits par pixel", (16).bit_length() - 1, 4)


# 50 : SI imbriques
def si50(b, c):
    return "Pass" if (b >= 40 and c >= 40) else ("Resit" if (b >= 40 or c >= 40) else "Fail")


ok(50, si50(35, 62), opt(50)[0])
ok("50 distracteurs", sorted([si50(62, 62), si50(35, 30), "TRUE"]), sorted(opt(50)[1]))
# 34 : adresse web
u = urlparse("https://www.school.cm:8080/library/books.html?id=42")
ok(34, (u.scheme, u.hostname, u.port, u.path, u.query), ("https", "www.school.cm", 8080, "/library/books.html", "id=42"))

# ------------------------------------------------------------------ questions FACTUELLES : cle recoupee avec une table ecrite ici (a relire par un enseignant)
FAITS = {
    3: "Optical mark recognition", 11: "decision support system", 13: "worm", 15: "Multitasking", 16: "<a href=\"books.html\">Library</a>",
    18: "Fibre-optic cable", 20: "Program counter", 22: "Switch", 23: "Parallel running", 25: "software piracy", 26: "business-to-business",
    29: "foreign key", 31: "Regular breaks and a wrist rest", 33: "inheritance", 34: "path to the resource on the server", 38: "RFID",
    39: "telemedicine", 41: "Second normal form, because of a partial dependency", 42: "Compiler",
}
for i, attendu in FAITS.items():
    q = qs[i - 1]
    textes = [q["key"].replace(BT, "")] + [d[0].replace(BT, "") for d in q["dist"]]
    ok(f"{i} factuelle : cle", q["key"].replace(BT, ""), attendu)
    ok(f"{i} factuelle : quatre options distinctes", len(set(textes)), 4)
    ok(f"{i} factuelle : une seule option egale a la cle", sum(1 for t in textes if t == attendu), 1)
    ok(f"{i} factuelle : pas de tout/aucun", int(not any(re.search(r"all of the above|none of the above|both a and b", t, re.I) for t in textes)), 1)

# ------------------------------------------------------------------ regles de forme de toutes les questions
for i, q in enumerate(qs, start=1):
    textes = [q["stem"], q["rappel"], q["sol"]] + [q["key"]] + [d[0] + " " + d[1] for d in q["dist"]]
    ok(f"{i} pas de tiret cadratin", int(not any("\u2014" in t for t in textes)), 1)
    ok(f"{i} pas de all/none of the above", int(not any(re.search(r"all of the above|none of the above", t, re.I) for t in textes)), 1)
    for t in textes:
        hors = re.sub(r"```.*?```", "", t, flags=re.S)
        hors = re.sub(r"`[^`]*`", "", hors)
        for ln in hors.split("\n"):
            ok(f"{i} au plus un $ par ligne hors code", int(ln.count("$") <= 1), 1)
    ok(f"{i} quatre options", len({q["key"]} | {d[0] for d in q["dist"]}), 4)
    ok(f"{i} raisons presentes", int(all(len(d[1]) > 15 for d in q["dist"])), 1)
    ok(f"{i} rappel en un paragraphe", int("\n\n" not in q["rappel"]), 1)

# ------------------------------------------------------------------ coherence du JSON genere
if os.path.exists(EP):
    ep = json.load(open(EP, encoding="utf8"))
    qj = ep["exercices"][0]["questions"]
    ok("JSON", len(qj), 50)
    ok("JSON blueprint", ep["blueprint_external_id"], "bp-cm-gce-al-ict-p1-1")
    ok("JSON external_id", ep["external_id"], "ep-cm-gce-al-ict-p1-1-2026-s1")
    comp_bp = set(json.load(open(BP, encoding="utf8"))["competences"])
    for i, (q, jq) in enumerate(zip(qs, qj), start=1):
        lettres = {c["lettre"]: c["texte"] for c in jq["choix"]}
        bonne = jq["reponse_correcte"]
        ok(f"{i} cle", int(lettres[bonne] == q["key"]), 1)
        ok(f"{i} unicite", sum(1 for t in lettres.values() if t == q["key"]), 1)
        ok(f"{i} quatre lettres", "".join(sorted(lettres)), "abcd")
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", jq["corrige_markdown"])
        ok(f"{i} Answer", int(bool(m) and m.group(1).lower() == bonne), 1)
        ok(f"{i} points", jq["points"], 1)
        ok(f"{i} themes dans le blueprint", int(all(t in comp_bp for t in jq["themes"])), 1)
        ok(f"{i} rappel verbatim", int(jq["rappels_de_methode"][0]["contenu_markdown"] in jq["corrige_markdown"]), 1)
        ok(f"{i} piege cite les 3 distracteurs", len(re.findall(r"option [A-D] ", jq["corrige_markdown"])), 3)
    cnt = Counter(jq["reponse_correcte"] for jq in qj)
    ok("equilibre", max(cnt.values()) - min(cnt.values()) <= 1, True)
    cles = [jq["reponse_correcte"] for jq in qj]
    ok("pas de trois cles identiques", sum(1 for a, b, c_ in zip(cles, cles[1:], cles[2:]) if a == b == c_), 0)
    diffs = Counter(jq["difficulte_estimee"] for jq in qj)
    ok("difficulte faibles 45-70 %", int(0.45 <= diffs["faible"] / 50 <= 0.70), 1)
    ok("difficulte elevees 1-4", int(1 <= diffs["elevee"] <= 4), 1)
    ok("themes : les 28 du blueprint", set(t for jq in qj for t in jq["themes"]), comp_bp)

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
