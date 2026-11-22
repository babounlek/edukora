r"""Recalcul INDEPENDANT de tout le code du corrige de l'epreuve inedite GCE A Level Computer Science Paper 3 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_cs_al_p3.py

Le verificateur relit le JSON ECRIT (backend/ingest/_inedit/cm/ep-cm-gce-al-computerscience-p3-1-2026-s1.json), pas le module de questions :
  1. SQL : les tables sont reconstruites depuis les tableaux Markdown de l'enonce (et le DDL de l'enonce), chaque requete du corrige est
     executee avec sqlite3 (cles etrangeres actives) et son resultat est compare au tableau imprime dans le corrige ; les contraintes de
     la table Booking sont eprouvees (cle primaire, UNIQUE, CHECK, cle etrangere) ;
  2. pseudocode : les blocs ```pseudo de l'enonce et du corrige sont traduits en Python par un mini-transpileur (FOR, WHILE, REPEAT,
     IF, FUNCTION, DECLARE, DIV...) puis executes ; les tables de trace et les exemples du corrige sont compares ;
  3. C : le code donne et les fonctions du corrige sont assembles et compiles par gcc (ANSI, -pedantic -Wall -Wextra : aucun avertissement
     toléré), executes, et les sorties imprimees dans le corrige sont comparees aux sorties reelles. gcc tourne dans Docker : image
     `edukora-cs-gcc` si elle existe, sinon `alpine` avec `apk add gcc musl-dev` (lent). Les sorties sont mises en cache dans
     %TEMP%/cs_al_p3_cache.json (cle = empreinte du source, des options et de l'entree standard) ;
  4. baremes, themes et structure contre le blueprint (7 exercices, points par exercice, themes inclus dans les competences).
Sortie 0 s'il n'y a aucun ecart.
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DOSSIER = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
EP_PATH = os.path.join(DOSSIER, "ep-cm-gce-al-computerscience-p3-1-2026-s1.json")
BP_PATH = os.path.join(DOSSIER, "bp-cm-gce-al-computerscience-p3-1.json")
CACHE_PATH = os.environ.get("CS_P3_CACHE") or os.path.join(tempfile.gettempdir(), "cs_al_p3_cache.json")
IMAGE_GCC = "edukora-cs-gcc"
OPTIONS_C = "-ansi -pedantic -Wall -Wextra"

ecarts = []
stats = {"verif": 0, "sql": 0, "c": 0, "pseudo": 0}


def ok(nom, valeur, attendu, tol=1e-6):
    stats["verif"] += 1
    if abs(valeur - attendu) > tol:
        ecarts.append(f"{nom}: calcule {valeur}, annonce {attendu}")


def vrai(nom, condition, detail=""):
    stats["verif"] += 1
    if not condition:
        ecarts.append(f"{nom}: condition fausse {detail}")


def egal(nom, obtenu, attendu):
    stats["verif"] += 1
    if obtenu != attendu:
        ecarts.append(f"{nom}: obtenu {obtenu!r} != attendu {attendu!r}")


with open(EP_PATH, encoding="utf8") as fh:
    EP = json.load(fh)
with open(BP_PATH, encoding="utf8") as fh:
    BP = json.load(fh)
EX = {e["numero_exercice"]: e for e in EP["exercices"]}


def Q(num, lettre):
    for q in EX[num]["questions"]:
        if q["numero"] == lettre:
            return q
    raise KeyError((num, lettre))


# ------------------------------------------------------------------------------------------------ analyse du Markdown
RE_FENCE = re.compile(r"```(\w*)\n(.*?)\n```", re.S)


def blocs(texte, langue=None):
    return [(l, c) for l, c in RE_FENCE.findall(texte) if langue is None or l == langue]


def parse_tables(texte):
    """Tableaux Markdown (hors blocs de code) : liste de (entetes, lignes) dans l'ordre du texte."""
    sans = RE_FENCE.sub("\x00", texte)
    res = []
    cur = []
    for l in sans.split("\n") + [""]:
        if l.strip().startswith("|"):
            cur.append(l.strip())
        else:
            if cur:
                cells = [[c.strip() for c in ln.strip("|").split("|")] for ln in cur]
                res.append((cells[0], cells[2:]))
            cur = []
    return res


def jetons(texte):
    """Blocs de code et tableaux dans l'ordre du texte : ('bloc', langue, code) ou ('table', entetes, lignes)."""
    res = []
    pos = 0
    for m in RE_FENCE.finditer(texte):
        for h, r in parse_tables(texte[pos:m.start()]):
            res.append(("table", h, r))
        res.append(("bloc", m.group(1), m.group(2)))
        pos = m.end()
    for h, r in parse_tables(texte[pos:]):
        res.append(("table", h, r))
    return res


def tables_nommees(texte):
    """Tableaux precedes de leur nom en gras (« **Passenger** »)."""
    res = {}
    for m in re.finditer(r"\*\*(\w+)\*\*\n\n((?:\|[^\n]*\n?)+)", texte):
        h, r = parse_tables(m.group(2))[0]
        res[m.group(1)] = (h, r)
    return res


def norm_sortie(s):
    return "\n".join(l.rstrip() for l in s.strip("\n").split("\n"))


# ------------------------------------------------------------------------------------------------ controles de forme du JSON
for ex in EP["exercices"]:
    for q in ex["questions"]:
        for champ in ("enonce_markdown", "corrige_markdown"):
            t = q[champ]
            vrai(f"{ex['numero_exercice']}{q['numero']} {champ} : blocs de code fermes", t.count("```") % 2 == 0)
            for l, c in RE_FENCE.findall(t):
                vrai(f"{ex['numero_exercice']}{q['numero']} {champ} : pas de $ dans un bloc de code", "$" not in c)
        vrai(f"{ex['numero_exercice']}{q['numero']} pas de tiret cadratin", "\u2014" not in q["corrige_markdown"] + q["enonce_markdown"] and "\u2013" not in q["corrige_markdown"] + q["enonce_markdown"])

# ================================================================================ SQL
RE_SELECT = re.compile(r"^\s*SELECT\b", re.I)


def executer_bloc_sql(db, code, nom, attendu=None):
    """Execute un bloc ```sql. Un SELECT est compare au tableau `attendu` ; sinon le script est execute."""
    if RE_SELECT.match(code):
        stats["sql"] += 1
        cur = db.execute(code)
        entetes = [d[0] for d in cur.description]
        lignes = [tuple(str(v) for v in r) for r in cur.fetchall()]
        if attendu is None:
            ecarts.append(f"{nom}: aucun tableau de resultat apres la requete")
            return
        egal(f"{nom} entetes", entetes, attendu[0])
        egal(f"{nom} lignes", lignes, [tuple(r) for r in attendu[1]])
    else:
        stats["sql"] += code.count(";")
        db.executescript(code)


def charger(db, nom, tab):
    entetes, lignes = tab
    db.executemany(f"INSERT INTO {nom} ({', '.join(entetes)}) VALUES ({', '.join('?' * len(entetes))})", lignes)


def executer_corrige_sql(db, q, prefixe):
    jet = jetons(q["corrige_markdown"])
    n = 0
    for i, j in enumerate(jet):
        if j[0] == "bloc" and j[1] == "sql":
            n += 1
            suivant = jet[i + 1] if i + 1 < len(jet) and jet[i + 1][0] == "table" else None
            executer_bloc_sql(db, j[2], f"{prefixe} bloc {n}", (suivant[1], suivant[2]) if suivant else None)
    return n


intro2, intro3 = EX["2"]["enonce_intro_markdown"], EX["3"]["enonce_intro_markdown"]
ddl_trois = blocs(intro2, "sql")[0][1]
t2, t3 = tables_nommees(intro2), tables_nommees(intro3)
egal("tables de l'exercice 3 identiques a celles de l'exercice 2", t3, t2)
vrai("quatre tableaux de donnees", set(t2) == {"Passenger", "Route", "Trip", "Booking"})

# --- exercice 2 : cumulatif a, b, c
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript(ddl_trois)
for nom in ("Passenger", "Route", "Trip"):
    charger(db, nom, t2[nom])
q2a = Q("2", "a")
ddl_booking = blocs(q2a["corrige_markdown"], "sql")[0][1]
db.executescript(ddl_booking)
stats["sql"] += 1
charger(db, "Booking", t2["Booking"])
ok("12 reservations chargees", db.execute("SELECT COUNT(*) FROM Booking").fetchone()[0], 12)
# contraintes de la table Booking eprouvees
for nom, instr in [
    ("cle primaire composite", "INSERT INTO Booking VALUES ('P01', 'T101', 20)"),
    ("UNIQUE (TripCode, SeatNo)", "INSERT INTO Booking VALUES ('P07', 'T101', 3)"),
    ("CHECK SeatNo > 70", "INSERT INTO Booking VALUES ('P07', 'T101', 71)"),
    ("CHECK SeatNo < 1", "INSERT INTO Booking VALUES ('P07', 'T101', 0)"),
    ("cle etrangere TripCode", "INSERT INTO Booking VALUES ('P07', 'T999', 10)"),
    ("cle etrangere PassengerID", "INSERT INTO Booking VALUES ('P99', 'T101', 10)"),
]:
    stats["sql"] += 1
    try:
        db.execute(instr)
        ecarts.append(f"2a {nom}: la contrainte n'a pas rejete {instr}")
    except sqlite3.IntegrityError:
        stats["verif"] += 1
# le meme siege sur deux voyages differents est permis (UNIQUE sur le couple)
stats["sql"] += 1
db.execute("INSERT INTO Booking VALUES ('P07', 'T108', 3)")
db.execute("DELETE FROM Booking WHERE PassengerID = 'P07'")
stats["verif"] += 1
egal("2a le blueprint du corrige : CREATE TABLE Booking", "CREATE TABLE Booking" in ddl_booking, True)
executer_corrige_sql(db, Q("2", "b"), "2b")
fares = dict(db.execute("SELECT RouteCode, Fare FROM Route").fetchall())
egal("2b tarifs R2, R5", (fares["R2"], fares["R5"]), (4800, 2300))
egal("2b tarifs inchanges", (fares["R1"], fares["R3"], fares["R4"]), (2500, 3000, 5000))
ok("2b P08 ajoute", db.execute("SELECT COUNT(*) FROM Passenger WHERE PassengerID = 'P08'").fetchone()[0], 1)
ok("2b reservation P06/T106 supprimee", db.execute("SELECT COUNT(*) FROM Booking WHERE PassengerID='P06' AND TripCode='T106'").fetchone()[0], 0)
ok("2b une seule reservation supprimee", db.execute("SELECT COUNT(*) FROM Booking").fetchone()[0], 11)
vrai("2b texte : 4800 et 2300", "4800" in Q("2", "b")["corrige_markdown"] and "2300" in Q("2", "b")["corrige_markdown"])
executer_corrige_sql(db, Q("2", "c"), "2c")

# --- exercice 3 : base neuve, donnees de l'exercice 3
db3 = sqlite3.connect(":memory:")
db3.execute("PRAGMA foreign_keys = ON")
db3.executescript(ddl_trois)
for nom in ("Passenger", "Route", "Trip"):
    charger(db3, nom, t3[nom])
db3.executescript(ddl_booking)
charger(db3, "Booking", t3["Booking"])
executer_corrige_sql(db3, Q("3", "a"), "3a")
executer_corrige_sql(db3, Q("3", "b"), "3b")
executer_corrige_sql(db3, Q("3", "c"), "3c")
# 3c(ii) : l'insertion de l'enonce doit etre refusee par la cle etrangere
m = re.search(r"`(INSERT INTO Booking VALUES \('P07', 'T999', 10\);)`", Q("3", "c")["enonce_markdown"])
vrai("3c(ii) insertion lisible dans l'enonce", m is not None)
if m:
    stats["sql"] += 1
    try:
        db3.execute(m.group(1))
        ecarts.append("3c(ii): l'insertion n'est pas refusee")
    except sqlite3.IntegrityError as exc:
        egal("3c(ii) message", str(exc), "FOREIGN KEY constraint failed")
        vrai("3c(ii) corrige cite le message", "FOREIGN KEY constraint failed" in Q("3", "c")["corrige_markdown"])
# 3b : recalcul par une autre voie (python)
rows_b = db3.execute("SELECT t.RouteCode, r.Fare FROM Booking b JOIN Trip t ON b.TripCode = t.TripCode JOIN Route r ON t.RouteCode = r.RouteCode").fetchall()
agg = {}
for rc, fare in rows_b:
    n, s = agg.get(rc, (0, 0))
    agg[rc] = (n + 1, s + fare)
attendu_b = sorted(((rc, n, s) for rc, (n, s) in agg.items() if n >= 2), key=lambda x: -x[2])
egal("3b recalcul python", attendu_b, [("R2", 4, 18000), ("R1", 5, 12500)])
stats["sql"] += 0

# ================================================================================ pseudocode : mini-transpileur
def traduire_expr(e):
    parts = re.split(r'("[^"]*")', e)
    out = []
    for p in parts:
        if p.startswith('"'):
            out.append(p)
            continue
        p = p.replace("<>", "!=")
        p = re.sub(r"(?<![<>!=])=(?!=)", "==", p)
        p = re.sub(r"\bAND\b", "and", p)
        p = re.sub(r"\bOR\b", "or", p)
        p = re.sub(r"\bNOT\b", "not", p)
        p = re.sub(r"\bDIV\b", "//", p)
        p = re.sub(r"\bMOD\b", "%", p)
        p = re.sub(r"\bTRUE\b", "True", p)
        p = re.sub(r"\bFALSE\b", "False", p)
        out.append(p)
    return "".join(out)


def traduire(src, trace=None):
    """Pseudocode -> source Python. `trace` : expressions notees a la fin de chaque tour de boucle (FOR ou WHILE)."""
    out, ind = [], 0

    def emit(s):
        out.append("    " * ind + s)

    for raw in src.strip().split("\n"):
        l = raw.strip()
        if not l:
            continue
        mot = l.split()[0]
        if mot == "DECLARE":
            m = re.match(r"DECLARE (\w+) : ARRAY\[1\.\.(\d+)\] OF \w+", l)
            emit(f"{m.group(1)} = [0] * ({m.group(2)} + 1)")
        elif mot == "FUNCTION":
            m = re.match(r"FUNCTION (\w+)\((.*?)\)( RETURNS \w+)?$", l)
            emit(f"def {m.group(1)}({m.group(2)}):")
            ind += 1
        elif mot == "ENDFUNCTION":
            ind -= 1
        elif mot == "FOR":
            m = re.match(r"FOR (\w+) ← (.+) TO (.+)$", l)
            emit(f"for {m.group(1)} in range({traduire_expr(m.group(2))}, ({traduire_expr(m.group(3))}) + 1):")
            ind += 1
        elif mot in ("NEXT", "ENDWHILE"):
            if trace:
                emit("TR.append([FMT(v) for v in (" + ", ".join(trace) + ",)])")
            ind -= 1
        elif mot == "WHILE":
            emit(f"while {traduire_expr(l[len('WHILE '):])}:")
            ind += 1
        elif mot == "REPEAT":
            emit("while True:")
            ind += 1
        elif mot == "UNTIL":
            emit(f"if {traduire_expr(l[len('UNTIL '):])}:")
            emit("    break")
            ind -= 1
        elif mot == "IF":
            emit(f"if {traduire_expr(re.sub(r' THEN$', '', l[len('IF '):]))}:")
            ind += 1
        elif mot == "ELSEIF":
            ind -= 1
            emit(f"elif {traduire_expr(re.sub(r' THEN$', '', l[len('ELSEIF '):]))}:")
            ind += 1
        elif mot == "ELSE":
            ind -= 1
            emit("else:")
            ind += 1
        elif mot == "ENDIF":
            ind -= 1
        elif mot == "RETURN":
            emit(f"return {traduire_expr(l[len('RETURN '):])}")
        elif mot == "OUTPUT":
            emit(f"OUT({traduire_expr(l[len('OUTPUT '):])})")
        elif mot == "INPUT":
            emit(f"{l.split()[1]} = INP()")
        elif "←" in l:
            g, d = l.split("←", 1)
            d = d.strip()
            d = ("[None] + " + d) if d.startswith("[") else traduire_expr(d)
            emit(f"{g.strip()} = {d}")
        else:
            raise ValueError("ligne de pseudocode non reconnue : " + l)
    assert ind == 0, "blocs mal fermes : " + src[:60]
    return "\n".join(out)


def fmt(v):
    if v is True:
        return "TRUE"
    if v is False:
        return "FALSE"
    return str(v)


def executer_pseudo(src, entrees=(), trace=None, preambule=""):
    """Execute le pseudocode ; retourne (espace de noms, sorties, trace). `preambule` : source Python a executer avant."""
    stats["pseudo"] += 1
    sorties, file_entrees, tr = [], list(entrees), []

    def OUT(*a):
        sorties.append(" ".join(fmt(x) for x in a))

    def INP():
        return file_entrees.pop(0)

    ns = {"OUT": OUT, "INP": INP, "ROUND": lambda x, n: round(x, n), "TR": tr, "FMT": fmt}
    exec(preambule + "\n" + traduire(src, trace), ns)
    return ns, sorties, tr


def table_de(texte, cles):
    for h, r in parse_tables(texte):
        if h == cles:
            return r
    return None


# --- exercice 4
i4 = EX["4"]["enonce_intro_markdown"]
algo1 = blocs(i4, "pseudo")[0][1]
_, sortie1, tr1 = executer_pseudo(algo1, trace=["i", "rain[i]", "wet", "run", "best"])
q4a = Q("4", "a")
attendu_tr1 = table_de(q4a["corrige_markdown"], ["i", "rain[i]", "wet", "run", "best"])
egal("4a table de trace du corrige", [list(r) for r in attendu_tr1], tr1)
egal("4a sortie", sortie1, ["6 3"])
vrai("4a sortie dans le corrige", "`6 3`" in q4a["corrige_markdown"])
vrai("4a l'enonce a 9 lignes vides a remplir", len(table_de(q4a["enonce_markdown"], ["i", "rain[i]", "wet", "run", "best"]) or []) == 9)
# 4b(ii) : neuf releves egaux a 10
algo1_dix = algo1.replace("[4, 12, 15, 0, 11, 22, 30, 3, 14]", "[10, 10, 10, 10, 10, 10, 10, 10, 10]")
vrai("4b donnees remplacees", algo1_dix != algo1)
_, sortie_dix, _ = executer_pseudo(algo1_dix)
egal("4b sortie pour dix partout", sortie_dix, ["0 0"])
vrai("4b corrige : 0 0", "`0 0`" in Q("4", "b")["corrige_markdown"])
q4c = Q("4", "c")
algo2 = blocs(q4c["enonce_markdown"], "pseudo")[0][1]
_, sortie2, tr2 = executer_pseudo(algo2, trace=["mid", "alt[mid]", "low", "high", "found"])
attendu_tr2 = table_de(q4c["corrige_markdown"], ["Pass", "mid", "alt[mid]", "low", "high", "found"])
egal("4c table de trace du corrige", [r[1:] for r in attendu_tr2], tr2)
egal("4c numeros de passe", [r[0] for r in attendu_tr2], ["1", "2", "3"])
egal("4c sortie", sortie2, ["Not found"])
vrai("4c corrige : Not found", "`Not found`" in q4c["corrige_markdown"])
# la recherche trouve bien les altitudes presentes (le pseudocode est une vraie recherche dichotomique)
for cible, pos in ((150, 1), (980, 4), (1620, 6), (2800, 8)):
    _, s, _ = executer_pseudo(algo2.replace("target ← 1000", f"target ← {cible}"))
    egal(f"4c recherche de {cible}", s, [f"Found at position {pos}"])

# --- exercice 5
q5a, q5b, q5c = Q("5", "a"), Q("5", "b"), Q("5", "c")
f_read = blocs(q5a["corrige_markdown"], "pseudo")[0][1]
f_count = blocs(q5b["corrige_markdown"], "pseudo")[0][1]
main5 = blocs(q5c["corrige_markdown"], "pseudo")[0][1]
for entrees, attendu_val, nb_invalides in (([-5, 620, 35], 35, 2), ([0], 0, 0), ([500], 500, 0), ([501, 500], 500, 1), ([-1, 0], 0, 1)):
    ns, s, _ = executer_pseudo(f_read + "\nRESULT ← ReadRainfall()", entrees)
    egal(f"5a ReadRainfall{entrees}", ns["RESULT"], attendu_val)
    egal(f"5a messages invalides {entrees}", s.count("Invalid rainfall"), nb_invalides)
vrai("5a corrige : exemple -5, 620, 35 donne 35", "35" in q5a["corrige_markdown"] and "twice" in q5a["corrige_markdown"])
jeu = [0, 20, 35, 0, 48, 10, 52, 5]
for limite, attendu_val in ((10, 4), (20, 3), (52, 0), (-1, 7)):
    ns, _, _ = executer_pseudo(f_count + f"\nRESULT ← CountAbove({jeu!r}, 7, {limite})")
    egal(f"5b CountAbove limite {limite}", ns["RESULT"], attendu_val)
vrai("5b corrige : l'exemple retourne 4", "returns 4" in q5b["corrige_markdown"])
ns, s, _ = executer_pseudo(f_read + "\n" + f_count + "\n" + main5, [7, 20, 35, 0, 48, 10, 52, 5])
egal("5c sorties", s[-2:], ["Average rainfall: 24.3", "Days above 20 mm: 3"])
egal("5c total", ns["total"], 170)
sortie_5c = [l for l in blocs(q5c["corrige_markdown"], "text")[0][1].split("\n")]
egal("5c bloc de sortie du corrige", sortie_5c, ["Average rainfall: 24.3", "Days above 20 mm: 3"])
vrai("5c corrige : total 170", "170" in q5c["corrige_markdown"])

# ================================================================================ C
def empreinte(src, stdin):
    return hashlib.sha256((OPTIONS_C + "\0" + src + "\0" + stdin).encode("utf8")).hexdigest()


def charger_cache():
    try:
        with open(CACHE_PATH, encoding="utf8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {}


def image_disponible():
    try:
        return subprocess.run(["docker", "image", "inspect", IMAGE_GCC], capture_output=True).returncode == 0
    except OSError:
        return False


def compiler_et_executer(jobs):
    """jobs : {nom: (source, stdin)} -> {nom: {'cc': sortie du compilateur, 'out': sortie du programme, 'rc': code}}."""
    cache = charger_cache()
    resultats, manquants = {}, {}
    for nom, (src, stdin) in jobs.items():
        cle = empreinte(src, stdin)
        if cle in cache:
            resultats[nom] = cache[cle]
        else:
            manquants[nom] = (src, stdin, cle)
    if manquants:
        dossier = os.path.realpath(tempfile.mkdtemp(prefix="cs_al_p3_"))
        for nom, (src, stdin, _) in manquants.items():
            with open(os.path.join(dossier, nom + ".c"), "w", encoding="utf8", newline="\n") as fh:
                fh.write(src)
            with open(os.path.join(dossier, nom + ".in"), "w", encoding="utf8", newline="\n") as fh:
                fh.write(stdin)
        script = (f"for f in *.c; do n=${{f%.c}}; gcc {OPTIONS_C} -o $n.bin $n.c 2> $n.cc; "
                  "if [ -x $n.bin ]; then ./$n.bin < $n.in > $n.out 2> $n.err; echo $? > $n.rc; fi; done\n")
        with open(os.path.join(dossier, "run.sh"), "w", encoding="utf8", newline="\n") as fh:
            fh.write(script)
        if image_disponible():
            commande = f"cd /w && sh run.sh"
            image = IMAGE_GCC
        else:
            commande = "apk add --no-cache gcc musl-dev >/dev/null && cd /w && sh run.sh"
            image = "alpine"
        cp = subprocess.run(["docker", "run", "--rm", "-v", dossier.replace("\\", "/") + ":/w", image, "sh", "-c", commande],
                            capture_output=True, text=True, timeout=1500)
        if cp.returncode != 0:
            ecarts.append(f"docker : code {cp.returncode} {cp.stderr[-300:]}")
        for nom, (src, stdin, cle) in manquants.items():
            def lire(ext):
                p = os.path.join(dossier, nom + ext)
                if os.path.exists(p):
                    with open(p, encoding="utf8", newline="") as fh:
                        return fh.read()
                return None
            r = {"cc": lire(".cc") or "", "out": lire(".out"), "rc": (lire(".rc") or "").strip()}
            resultats[nom] = r
            if r["out"] is not None:
                cache[cle] = r
        try:
            with open(CACHE_PATH, "w", encoding="utf8") as fh:
                json.dump(cache, fh)
        except OSError:
            pass
    return resultats


if os.environ.get("CS_P3_SKIP_C"):  # mise au point seulement : saute la partie C (jamais pour le « 0 ecart » final)
    print("PARTIE C SAUTEE ; ecarts :", ecarts, "; verifications", stats)
    sys.exit(2)

intro6 = EX["6"]["enonce_intro_markdown"]
HEADER = blocs(intro6, "c")[0][1]
q6a, q6b, q6c = Q("6", "a"), Q("6", "b"), Q("6", "c")
code6a = blocs(q6a["corrige_markdown"], "c")[0][1]
code6b = blocs(q6b["corrige_markdown"], "c")[0][1]
read_c, main_c = [c for _, c in blocs(q6c["corrige_markdown"], "c")]
vrai("6a trois fonctions dans le corrige", all(f in code6a for f in ("int station_total(int r[][MONTHS], int s)", "int wettest_month(int r[][MONTHS], int s)",
                                                                  "int stations_above(int r[][MONTHS], int m, int limit)")))
q7a, q7b, q7c = Q("7", "a"), Q("7", "b"), Q("7", "c")
faulty = blocs(q7b["enonce_markdown"], "c")[0][1]
wet_ok = re.search(r"int wettest_month\(.*?\n}", code6a, re.S).group(0)
vrai("7b la fonction fautive differe de la bonne par >= seulement", faulty.replace(">=", ">") == wet_ok)
corrected_7b_ok = "`>`" in q7b["corrige_markdown"]
faulty_renamed = faulty.replace("wettest_month", "wettest_faulty")
ok_renamed = wet_ok.replace("wettest_month", "wettest_ok")

jobs = {}
jobs["p6a"] = (HEADER + "\n\n" + code6a + r'''

int main(void)
{
    int s;

    printf("total %d\n", station_total(rain, 2));
    printf("wettest %d\n", wettest_month(rain, 2));
    printf("above %d\n", stations_above(rain, 2, 100));
    for (s = 0; s < STATIONS; s++)
        printf("s%d %d %d\n", s, station_total(rain, s), wettest_month(rain, s));
    return 0;
}
''', "")
jobs["p6b"] = (HEADER + "\n\n" + code6a + "\n\n" + code6b + "\n\nint main(void)\n{\n    print_report(rain);\n    return 0;\n}\n", "")
programme_complet = HEADER + "\n\n" + code6a + "\n\n" + code6b + "\n\n" + read_c + "\n\n" + main_c + "\n"
STDIN_6C = "7\n0\n3\n3\n100\n"
jobs["p6c"] = (programme_complet, STDIN_6C)
jobs["p6c_bis"] = (programme_complet, "1\n6\n300\n")
jobs["p7a"] = (HEADER + "\n\n" + code6a + r'''

int main(void)
{
    printf("limit 100: %d\n", stations_above(rain, 2, 100));
    printf("limit 130: %d\n", stations_above(rain, 2, 130));
    printf("limit 1000: %d\n", stations_above(rain, 2, 1000));
    return 0;
}
''', "")
jobs["p7b"] = (HEADER + "\n\n" + faulty_renamed + "\n\n" + ok_renamed + r'''

int main(void)
{
    int t[1][MONTHS] = {{50, 90, 90, 10, 20, 30}};
    int s;

    printf("faulty: %d\n", wettest_faulty(t, 0));
    printf("corrected: %d\n", wettest_ok(t, 0));
    printf("--\n");
    for (s = 0; s < STATIONS; s++)
        printf("%d %d\n", wettest_faulty(rain, s), wettest_ok(rain, s));
    return 0;
}
''', "")
jobs["p7b_fautif_seul"] = (HEADER + "\n\n" + faulty + "\n\nint main(void) { return wettest_month(rain, 0) == 5 ? 0 : 1; }\n", "")

res = compiler_et_executer(jobs)
for nom, r in res.items():
    stats["c"] += 1
    egal(f"{nom} : aucun avertissement ni erreur de compilation ({OPTIONS_C})", r["cc"], "")
    egal(f"{nom} : code de retour", r["rc"], "0")


def sortie_c(nom):
    return norm_sortie(res[nom]["out"] or "")


# 6a : valeurs citees dans le corrige
s6a = sortie_c("p6a").split("\n")
egal("6a station_total Buea", s6a[0], "total 1075")
egal("6a wettest_month Buea", s6a[1], "wettest 5")
egal("6a stations_above mars 100", s6a[2], "above 3")
vrai("6a corrige cite 1075, 5 et 3", all(x in q6a["corrige_markdown"] for x in ("1075", "returns 5", "returns 3")))
# recalcul des memes valeurs en Python a partir du tableau donne dans l'enonce
vals = [int(x) for x in re.findall(r"\d+", re.search(r"int rain\[STATIONS\]\[MONTHS\] = \{(.*?)\};", HEADER, re.S).group(1))]
rain = [vals[i * 6:(i + 1) * 6] for i in range(4)]
egal("6a tableau 4 x 6", len(vals), 24)
egal("6a totaux python", [sum(r) for r in rain], [3045, 1855, 1075, 843])
egal("6a total C = total python", [tuple(int(v) for v in l.split()[1:]) for l in s6a[3:]], [(sum(r), r.index(max(r))) for r in rain])
egal("6a stations_above python", sum(1 for r in rain if r[2] > 100), 3)
# 6b : la sortie de print_report = le modele de l'enonce = la sortie du corrige
modele_6b = blocs(q6b["enonce_markdown"], "text")[0][1]
sortie_corrige_6b = blocs(q6b["corrige_markdown"], "text")[0][1]
egal("6b sortie reelle = modele de l'enonce", sortie_c("p6b"), norm_sortie(modele_6b))
egal("6b sortie reelle = sortie du corrige", sortie_c("p6b"), norm_sortie(sortie_corrige_6b))
lignes_6b = sortie_c("p6b").split("\n")
egal("6b sommes de la derniere ligne", [int(x) for x in lignes_6b[-1].split()[2:]], [sum(r[m] for r in rain) for m in range(6)] + [sum(map(sum, rain))])
# 6c : programme complet
egal("6c sortie reelle = sortie du corrige", sortie_c("p6c"), norm_sortie(blocs(q6c["corrige_markdown"], "text")[0][1]))
vrai("6c format demande : ligne de la station", "Buea: total 1075 mm, wettest month Jun (350 mm)" in sortie_c("p6c"))
vrai("6c format demande : ligne des stations", "Stations above 100 mm in Mar: 3" in sortie_c("p6c"))
vrai("6c exemple de l'enonce identique au format de l'enonce", "`Buea: total 1075 mm, wettest month Jun (350 mm)`" in q6c["enonce_markdown"] and "`Stations above 100 mm in Mar: 3`" in q6c["enonce_markdown"])
bis = sortie_c("p6c_bis").split("\n")
vrai("6c second essai : station 1", "Debundscha: total 3045 mm, wettest month Jun (840 mm)" in sortie_c("p6c_bis"))
vrai("6c second essai : juin au-dessus de 300", bis[-1].endswith("Stations above 300 mm in Jun: 4"))
# 7a
egal("7a sortie reelle = bloc du corrige", sortie_c("p7a"), norm_sortie(blocs(q7a["corrige_markdown"], "text")[0][1]))
egal("7a colonne de mars", [r[2] for r in rain], [405, 210, 130, 90])
# 7b
s7b = sortie_c("p7b").split("\n--\n")
egal("7b sortie reelle = bloc du corrige", s7b[0], norm_sortie(blocs(q7b["corrige_markdown"], "text")[0][1]))
egal("7b sur les donnees de l'exercice 6 les deux versions donnent le meme mois", [l.split()[0] == l.split()[1] for l in s7b[1].split("\n")], [True] * 4)
egal("7c aucune egalite de maximum dans le tableau", [sorted(r)[-1] != sorted(r)[-2] for r in rain], [True] * 4)
vrai("7b la ligne d'essai du corrige est celle du harnais", "{50, 90, 90, 10, 20, 30}" in q7b["corrige_markdown"])

# ================================================================================ bareme, themes, blueprint
plan = {p["exercice"]: p for p in BP["sections_plan"]}
ok("blueprint : 7 exercices", len(EX), 7)
for num, e in EX.items():
    ok(f"ex{num} points", float(e["points"]), plan[num]["points"])
    ok(f"ex{num} somme des sous-questions", sum(q["points"] for q in e["questions"]), plan[num]["points"])
    ok(f"ex{num} nombre de questions", len(e["questions"]), plan[num]["nombre_questions"])
    lettres = [q["numero"] for q in e["questions"]]
    egal(f"ex{num} numeros uniques a, b, c", lettres, list("abcdef")[:len(lettres)])
    themes_vus = set()
    for q in e["questions"]:
        vrai(f"ex{num}{q['numero']} themes inclus dans les competences du blueprint", set(q["themes"]) <= set(plan[num]["competences"]), str(q["themes"]))
        ok(f"ex{num}{q['numero']} somme des criteres", sum(c["points"] for c in q["criteres_notation"]), q["points"], 1e-9)
        vrai(f"ex{num}{q['numero']} 2 a 5 criteres", 2 <= len(q["criteres_notation"]) <= 5)
        themes_vus |= set(q["themes"])
        vrai(f"ex{num}{q['numero']} un rappel, un paragraphe", len(q["rappels_de_methode"]) == 1 and "\n\n" not in q["rappels_de_methode"][0]["contenu_markdown"])
        vrai(f"ex{num}{q['numero']} le rappel figure dans le corrige", q["rappels_de_methode"][0]["contenu_markdown"] in q["corrige_markdown"])
    vrai(f"ex{num} couvre tous les themes du blueprint", themes_vus == set(plan[num]["competences"]), str(set(plan[num]["competences"]) ^ themes_vus))
ok("total des points", sum(float(e["points"]) for e in EX.values()), BP["bareme_total"])
egal("blueprint de l'epreuve", EP["blueprint_external_id"], BP["external_id"])

# ------------------------------------------------------------------------------------------------ bilan
if ecarts:
    print(f"{len(ecarts)} ecart(s) sur {stats['verif']} verifications")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print(f"{stats['verif']} verifications, {stats['sql']} requetes SQL executees (sqlite3), {stats['c']} programmes C compiles et executes (gcc {OPTIONS_C}), "
      f"{stats['pseudo']} executions de pseudocode, 0 ecart")
