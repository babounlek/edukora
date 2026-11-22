r"""Recalcul INDEPENDANT de la reponse de chaque question de l'epreuve inedite GCE A Level Computer Science Paper 1 n.1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_cs_al_p1.py

Pour chaque question calculatoire, une fonction recalcule la bonne reponse par une AUTRE voie que le corrige (conversion de bases par programme, table de verite exhaustive,
recherche exhaustive d'un reseau de portes NAND, simulation d'ordonnancement et de remplacement de pages, algorithme du banquier par permutations, sqlite3 pour les requetes,
execution Python des algorithmes, calcul d'adresses avec le module ipaddress), la compare a la valeur de controle `val`, au texte de l'option juste, et recalcule aussi
chaque distracteur numerique a partir de l'erreur nommee dans le piege. Questions factuelles (definitions, ordre des phases, choix d'un type de systeme) : coherence logique
(une seule option vraie) seulement ; la verite du fait reste a relire par un enseignant (voir le rapport). Le JSON genere est relu (lettre, `Answer:`, option unique,
equilibre des cles, themes du blueprint). Sortie 0 s'il n'y a aucun ecart.
"""
import ipaddress
import itertools
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter, deque

sys.path.insert(0, os.path.dirname(__file__))
from questions_cs_al_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-al-computerscience-p1-1-2026-s1.json")
BP = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "bp-cm-gce-al-computerscience-p1-1.json")
ecarts = []
nverif = 0
QS = {q["id"]: q for q in questions()}


def ok(nom, calcule, annonce, tol=0.0):
    global nverif
    nverif += 1
    if isinstance(calcule, float) or isinstance(annonce, float):
        bon = abs(calcule - annonce) <= max(tol, 1e-9)
    else:
        bon = calcule == annonce
    if not bon:
        ecarts.append(f"{nom}: recalcule {calcule!r}, annonce {annonce!r}")


def opts(qid):
    q = QS[qid]
    return q["key"], [d[0] for d in q["dist"]]


def num(texte):
    t = texte.replace("\u202f", "").replace(" ", "").replace("`", "")
    m = re.match(r"-?\d+(?:\.\d+)?", t)
    return float(m.group(0)) if m else None


def bits(texte):
    return texte.replace("`", "")


# ------------------------------------------------------------------ numeration
def t_hex2dec():
    k, d = opts("hex2dec")
    v = int("2F5", 16)
    ok("hex2dec valeur", v, 757)
    ok("hex2dec cle", num(k), float(v))
    ok("hex2dec F=16", 2 * 256 + 16 * 16 + 5, num(d[0]))
    ok("hex2dec puissances de 10", 2 * 100 + 15 * 10 + 5, num(d[1]))
    ok("hex2dec puissances de 8", 2 * 64 + 15 * 8 + 5, num(d[2]))
    ok("hex2dec val", QS["hex2dec"]["val"], v)


def t_hex_octal():
    k, d = opts("hex_octal")
    n = int("1100110", 2)
    ok("hex_octal cle", oct(n)[2:], k)
    ok("hex_octal gauche", str(int("110", 2)) + str(int("011", 2)) + str(int("0", 2)), d[0])  # 110 011 0
    ok("hex_octal decimal", str(n), d[1])
    ok("hex_octal hexa", format(n, "X"), d[2])
    ok("hex_octal val", QS["hex_octal"]["val"], k)


def t_bits_colours():
    k, d = opts("bits_colours")
    n = 1
    while 2 ** n < 300:
        n += 1
    ok("bits cle", float(n), num(k))
    ok("bits 8 insuffisant", int(2 ** 8 >= 300), 0)
    ok("bits 8", 8, num(d[0]))
    ok("bits 10", n + 1, num(d[1]))
    ok("bits 38", math.ceil(300 / 8), num(d[2]))
    ok("bits val", QS["bits_colours"]["val"], n)


# ------------------------------------------------------------------ arithmetique binaire
def add_sans_retenue(a, b):
    return format(a ^ b, "08b")


def add_111_en_10(a, b):
    A, B = format(a, "08b"), format(b, "08b")
    c, out = 0, ""
    for i in range(7, -1, -1):
        s = int(A[i]) + int(B[i]) + c
        if s == 3:
            out, c = "0" + out, 1
        else:
            out, c = str(s % 2) + out, s // 2
    return out


def t_bin_add():
    k, d = opts("bin_add")
    a, b = int("01101101", 2), int("00111011", 2)
    ok("bin_add cle", format((a + b) % 256, "08b"), bits(k))
    ok("bin_add pas de depassement", int(a + b < 256), 1)
    ok("bin_add sans retenue", add_sans_retenue(a, b), bits(d[0]))
    ok("bin_add 1+1+1", add_111_en_10(a, b), bits(d[1]))
    ok("bin_add retenue parasite", format(a + b + 1, "08b"), bits(d[2]))
    ok("bin_add val", QS["bin_add"]["val"], a + b)


def t_twos_neg():
    k, d = opts("twos_neg")
    inv = "".join("1" if c == "0" else "0" for c in format(45, "08b"))
    ok("twos_neg cle", format((-45) % 256, "08b"), bits(k))
    ok("twos_neg par inversion", format(int(inv, 2) + 1, "08b"), bits(k))
    ok("twos_neg sans +1", inv, bits(d[0]))
    ok("twos_neg signe-valeur", "1" + format(45, "07b"), bits(d[1]))
    ok("twos_neg 128-45", format(128 - 45, "08b"), bits(d[2]))
    ok("twos_neg val", QS["twos_neg"]["val"], (-45) % 256)


def lire_c2(s):
    n = int(s, 2)
    return n - 256 if s[0] == "1" else n


def t_twos_sub():
    k, d = opts("twos_sub")
    a, b = int("00101110", 2), int("00110100", 2)
    ok("twos_sub cle", format((a - b) % 256, "08b"), bits(k))
    c2b = format((-b) % 256, "08b")
    ok("twos_sub a + c2(b)", format((a + int(c2b, 2)) % 256, "08b"), bits(k))
    ok("twos_sub valeur", lire_c2(bits(k)), -6)
    ok("twos_sub magnitude", format(abs(a - b), "08b"), bits(d[0]))
    ok("twos_sub complement a 1", format(255 - 6, "08b"), bits(d[1]))
    ok("twos_sub signe-valeur", "1" + format(6, "07b"), bits(d[2]))
    ok("twos_sub val", QS["twos_sub"]["val"], (a - b) % 256)


def t_overflow():
    k, d = opts("overflow")
    a, b = int("01100100", 2), int("00110010", 2)
    r = format((a + b) % 256, "08b")
    ok("overflow somme depasse 127", int(a + b > 127), 1)
    ok("overflow cle", float(lire_c2(r)), num(k))
    ok("overflow non signe", int(r, 2), int(num(d[0])))
    ok("overflow signe-valeur", -int(r[1:], 2), int(num(d[1])))
    ok("overflow sans signe", abs(lire_c2(r)), int(num(d[2])))
    ok("overflow val", QS["overflow"]["val"], lire_c2(r))


# ------------------------------------------------------------------ algebre de Boole et portes
def tt(f):
    return tuple(int(f(*v)) for v in itertools.product((0, 1), repeat=f.__code__.co_argcount))


def t_bool_simpl():
    k, d = opts("bool_simpl")
    orig = lambda A, B, C: (A and B) or (A and (not B) and C)
    ok("bool_simpl cle", tt(orig), tt(lambda A, B, C: A and (B or C)))
    ok("bool_simpl dist A.B", int(tt(orig) == tt(lambda A, B, C: A and B)), 0)
    ok("bool_simpl dist (AB)+C", int(tt(orig) == tt(lambda A, B, C: (A and B) or C)), 0)
    ok("bool_simpl dist A+B+C", int(tt(orig) == tt(lambda A, B, C: A or B or C)), 0)
    ok("bool_simpl texte cle", k, "`A AND (B OR C)`")
    ok("bool_simpl ligne de la resolution", int(orig(1, 0, 1)), 1)
    ok("bool_simpl A.B vaut 0 sur cette ligne", int(1 and 0), 0)


def t_demorgan():
    k, d = opts("demorgan")
    orig = lambda X, Y: not (X and (not Y))
    ok("demorgan cle", tt(orig), tt(lambda X, Y: (not X) or Y))
    for nom, f in (("NOT X AND Y", lambda X, Y: (not X) and Y), ("X OR NOT Y", lambda X, Y: X or (not Y)),
                   ("NOT X OR NOT Y", lambda X, Y: (not X) or (not Y))):
        ok("demorgan distracteur " + nom, int(tt(orig) == tt(f)), 0)
    ok("demorgan faux seulement pour X=1,Y=0", [v for v, o in zip(itertools.product((0, 1), repeat=2), tt(orig)) if o == 0], [(1, 0)])


def t_xor_circuit():
    k, d = opts("xor_circuit")
    circ = lambda A, B: (not (A and B)) and (A or B)
    ref = tt(circ)
    ok("xor cle", ref, tt(lambda A, B: A != B))
    ok("xor XNOR", int(ref == tt(lambda A, B: A == B)), 0)
    ok("xor AND", int(ref == tt(lambda A, B: A and B)), 0)
    ok("xor NOR", int(ref == tt(lambda A, B: not (A or B))), 0)
    ok("xor colonne annoncee", ref, QS["xor_circuit"]["val"])
    ok("xor NAND(0,0)=1 (piege NOR)", int(not (0 and 0)), 1)


def t_full_adder():
    k, d = opts("full_adder")
    A = B = Cin = 1
    s = A ^ B ^ Cin
    c = (A & B) | (Cin & (A ^ B))
    ok("full_adder somme binaire", format(A + B + Cin, "02b"), f"{c}{s}")
    ok("full_adder cle", f"sum {s}, carry {c}", k)
    ok("full_adder sans Cin", f"sum {(A ^ B)}, carry {(A & B)}", d[0])  # 1+1 = 10 -> sum 0, carry 1
    ok("full_adder retenue perdue", f"sum {s}, carry 0", d[1])
    ok("full_adder rien reporte", "sum 0, carry 0", d[2])
    ok("full_adder val", QS["full_adder"]["val"], (s, c))


def t_nand_or():
    k, d = opts("nand_or")
    # recherche exhaustive : plus petit reseau de portes NAND a 2 entrees (entrees A, B) donnant la table de OR
    def table(f):
        return tuple(int(f(a, b)) for a in (0, 1) for b in (0, 1))
    A, B = table(lambda a, b: a), table(lambda a, b: b)
    cible = {"OR": table(lambda a, b: a or b), "NOR": table(lambda a, b: not (a or b)),
             "AND": table(lambda a, b: a and b), "XOR": table(lambda a, b: a != b)}
    nand = lambda x, y: tuple(1 - (p & q) for p, q in zip(x, y))

    def minimal(cible_t, maxg=6):
        # profondeur croissante : le premier nombre de portes qui reussit est le minimum
        for lim in range(0, maxg + 1):
            if existe([A, B], cible_t, lim):
                return lim
        return None

    def existe(signaux, cible_t, restant):
        if cible_t in signaux:
            return True
        if restant == 0:
            return False
        for x, y in itertools.combinations_with_replacement(range(len(signaux)), 2):
            n = nand(signaux[x], signaux[y])
            if n in signaux:
                continue
            if existe(signaux + [n], cible_t, restant - 1):
                return True
        return False

    mins = {nom: minimal(t) for nom, t in cible.items()}
    ok("nand OR minimum", float(mins["OR"]), num(k))
    ok("nand NOR (distracteur 4)", float(mins["NOR"]), num(d[1]))
    ok("nand AND = 2 (partage d'un inverseur impossible pour OR)", mins["AND"], 2)
    ok("nand OR sans partage : 2 portes ne suffisent pas", int(existe([A, B], cible["OR"], 2)), 0)
    ok("nand 1 porte ne suffit pas", int(existe([A, B], cible["OR"], 1)), 0)
    ok("nand val", QS["nand_or"]["val"], mins["OR"])


# ------------------------------------------------------------------ memoire, architecture
def t_addr_capacity():
    k, d = opts("addr_capacity")
    lieux = 2 ** 14
    octets = lieux * 16 // 8
    ok("addr cle", float(octets), num(k))
    ok("addr 14 bits = 16384 lieux", lieux, 16384)
    ok("addr octets par lieu", float(lieux), num(d[0]))
    ok("addr 16 octets par lieu", float(lieux * 16), num(d[1]))
    ok("addr 14 x 16", float(14 * 16), num(d[2]))
    ok("addr val", QS["addr_capacity"]["val"], octets)


def t_download_time():
    k, d = opts("download_time")
    bits_ = 90 * 1048576 * 8
    t = bits_ / 6e6
    ok("download cle", round(t), int(num(k)))
    ok("download bits", bits_, 754974720)
    ok("download sans x8", round(90 * 1048576 / 6e6), int(num(d[0])))
    ok("download MiB decimal", round(90e6 * 8 / 6e6), int(num(d[1])))
    ok("download x8 deux fois", round(90 * 1048576 * 64 / 6e6), int(num(d[2])))
    ok("download val", QS["download_time"]["val"], round(t, 1), 0.05)


def t_pc_fetch():
    k, d = opts("pc_fetch")
    pc = 40
    longueur = 2
    ok("pc cle", float(pc + longueur), num(k))
    ok("pc 40", float(pc), num(d[0]))
    ok("pc +1", float(pc + 1), num(d[1]))
    ok("pc x2", float(pc * 2), num(d[2]))
    ok("pc val", QS["pc_fetch"]["val"], 42)


def t_fetch_regs():
    """Chaque option est codee comme une suite de transferts ; une seule respecte les roles (PC adresse, MAR adresse, MDR donnee lue, IR instruction, PC+1)."""
    k, d = opts("fetch_regs")
    ROLES_OK = [("PC", "MAR"), ("MEM", "MDR"), ("MDR", "IR"), ("PC", "PC+1")]

    def code(texte):
        t = texte
        seq = []
        for m in re.finditer(r"The (PC|MDR|accumulator) is copied to the (MAR|MDR|PC|IR)|the memory location addressed is read into the (MDR|MAR|accumulator)|the (MAR|MDR|accumulator) is copied to the (IR|PC)|the (PC|IR) is incremented", t):
            g = m.group(0)
            if g.startswith("The "):
                seq.append(("PC" if m.group(1) == "PC" else m.group(1).upper(), m.group(2)))
            elif g.startswith("the memory"):
                seq.append(("MEM", {"accumulator": "ACC"}.get(m.group(3), m.group(3))))
            elif g.endswith("incremented"):
                seq.append((m.group(6), m.group(6) + "+1"))
            else:
                src = {"accumulator": "ACC"}.get(m.group(4), m.group(4))
                seq.append((src, m.group(5)))
        return seq
    ok("fetch cle", code(k), ROLES_OK)
    for i, t in enumerate(d):
        ok(f"fetch distracteur {i + 1} diffère", int(code(t) == ROLES_OK), 0)
    ok("fetch val", QS["fetch_regs"]["val"], "fetch")


def t_acc_trace():
    k, d = opts("acc_trace")
    mem = {4: 9, 10: 7, 11: 3, 12: 0}

    def run(prog, mode):
        acc = 0
        for op, arg in prog:
            imm = arg.startswith("#")
            n = int(arg.lstrip("#"))
            if mode.get(op + arg) == "force_imm":
                imm = True
            if mode.get(op + arg) == "force_dir":
                imm = False
            v = n if imm else mem[n]
            if op == "LDA":
                acc = v
            elif op == "ADD":
                acc += v
            elif op == "STA":
                mem[n] = acc
        return acc
    prog = [("LDA", "10"), ("ADD", "#4"), ("ADD", "11"), ("STA", "12")]
    ok("acc cle", float(run(prog, {})), num(k))
    ok("acc #4 lu comme adresse", float(run(prog, {"ADD#4": "force_dir"})), num(d[0]))
    ok("acc ADD 11 immediat", float(run(prog, {"ADD11": "force_imm"})), num(d[1]))
    ok("acc LDA 10 immediat", float(run(prog, {"LDA10": "force_imm"})), num(d[2]))
    ok("acc val", QS["acc_trace"]["val"], 14)


# ------------------------------------------------------------------ systemes d'exploitation
def t_process_state():
    """Machine a etats : seule la transition running -> blocked decoule d'une demande d'E/S."""
    k, d = opts("process_state")
    transitions_io = {("running", "blocked")}
    options = [k] + d
    cod = {"running state to the blocked": ("running", "blocked"), "running state to the ready": ("running", "ready"),
           "running state to the terminated": ("running", "terminated"), "ready state to the running": ("ready", "running")}
    lus = []
    for t in options:
        for cle, v in cod.items():
            if cle in t:
                lus.append(v)
    ok("etats options lues", len(lus), 4)
    ok("etats une seule option sur demande d'E/S", sum(1 for v in lus if v in transitions_io), 1)
    ok("etats cle", lus[0], ("running", "blocked"))


def fautes(ref, k, politique):
    cadres, f = [], 0
    for i, p in enumerate(ref):
        if p in cadres:
            if politique == "lru":
                cadres.remove(p)
                cadres.append(p)
            continue
        f += 1
        if len(cadres) == k:
            if politique == "opt":
                futur = ref[i + 1:]
                v = max(cadres, key=lambda x: futur.index(x) if x in futur else 10 ** 6)
                cadres.remove(v)
            else:
                cadres.pop(0)
        cadres.append(p)
    return f


def t_fifo_faults():
    k, d = opts("fifo_faults")
    ref = [3, 1, 2, 3, 4, 1, 5, 3, 2, 1, 4]
    ok("fifo cle", float(fautes(ref, 3, "fifo")), num(k))
    ok("fifo lru", float(fautes(ref, 3, "lru")), num(d[0]))
    ok("fifo optimal", float(fautes(ref, 3, "opt")), num(d[1]))
    ok("fifo pages distinctes", float(len(set(ref))), num(d[2]))
    ok("fifo val", QS["fifo_faults"]["val"], 9)


def t_paging_addr():
    k, d = opts("paging_addr")
    taille, adr, cadre = 2048, 9000, 11
    page, off = divmod(adr, taille)
    ok("paging page", page, 4)
    ok("paging offset", off, 808)
    ok("paging cle", float(cadre * taille + off), num(k))
    ok("paging sans offset", float(cadre * taille), num(d[0]))
    ok("paging adr entiere", float(cadre * taille + adr), num(d[1]))
    ok("paging sans traduction", float(adr), num(d[2]))
    ok("paging val", QS["paging_addr"]["val"], cadre * taille + off)


# ------------------------------------------------------------------ ordonnancement
def attentes_fcfs(P):
    t, w = 0, {}
    for n, a, b in sorted(P, key=lambda p: p[1]):
        t = max(t, a)
        w[n] = t - a
        t += b
    return w


def sjf_np(P):
    t, fait, w, ta = 0, set(), {}, {}
    while len(fait) < len(P):
        dispo = [p for p in P if p[1] <= t and p[0] not in fait]
        if not dispo:
            t = min(p[1] for p in P if p[0] not in fait)
            continue
        n, a, b = min(dispo, key=lambda p: (p[2], p[1]))
        w[n] = t - a
        t += b
        ta[n] = t - a
        fait.add(n)
    return w, ta


def srtf(P):
    rest = {n: b for n, a, b in P}
    arr = {n: a for n, a, b in P}
    t, fin = 0, {}
    while rest:
        dispo = [n for n in rest if arr[n] <= t]
        if not dispo:
            t += 1
            continue
        n = min(dispo, key=lambda x: (rest[x], arr[x]))
        rest[n] -= 1
        t += 1
        if rest[n] == 0:
            del rest[n]
            fin[n] = t
    return fin


def round_robin(P, q):
    P = sorted(P, key=lambda p: p[1])
    rest = {n: b for n, a, b in P}
    i, t, file_, fin = 0, 0, deque(), {}
    while len(fin) < len(P):
        while i < len(P) and P[i][1] <= t:
            file_.append(P[i][0])
            i += 1
        if not file_:
            t = P[i][1]
            continue
        n = file_.popleft()
        r = min(q, rest[n])
        t += r
        rest[n] -= r
        while i < len(P) and P[i][1] <= t:
            file_.append(P[i][0])
            i += 1
        if rest[n] > 0:
            file_.append(n)
        else:
            fin[n] = t
    return fin


def t_fcfs():
    k, d = opts("fcfs")
    P = [("A", 0, 6), ("B", 1, 2), ("C", 2, 7), ("D", 4, 3)]
    w = attentes_fcfs(P)
    moy = sum(w.values()) / 4
    ok("fcfs attentes", w, {"A": 0, "B": 5, "C": 6, "D": 11})
    ok("fcfs cle", moy, num(k), 1e-9)
    fin, t = {}, 0
    for n, a, b in sorted(P, key=lambda p: p[1]):
        t = max(t, a) + b
        fin[n] = t
    ok("fcfs rotation (retour)", sum(fin[n] - a for n, a, b in P) / 4, num(d[0]), 1e-9)
    ok("fcfs SJF", sum(sjf_np(P)[0].values()) / 4, num(d[1]), 1e-9)
    t, starts = 0, []
    for n, a, b in sorted(P, key=lambda p: p[1]):
        t = max(t, a)
        starts.append(t)
        t += b
    ok("fcfs sans arrivee", sum(starts) / 4, num(d[2]), 1e-9)
    ok("fcfs val", QS["fcfs"]["val"], moy, 1e-9)


def t_sjf():
    k, d = opts("sjf")
    P = [("P1", 0, 5), ("P2", 1, 3), ("P3", 2, 1), ("P4", 3, 4)]
    w, ta = sjf_np(P)
    moy = sum(w.values()) / 4
    ok("sjf attentes", w, {"P1": 0, "P3": 3, "P2": 5, "P4": 6})
    ok("sjf cle", moy, num(k), 1e-9)
    ok("sjf FCFS", sum(attentes_fcfs(P).values()) / 4, num(d[0]), 1e-9)
    fin = srtf(P)
    ok("sjf SRTF", sum(fin[n] - a - b for n, a, b in P) / 4, num(d[1]), 1e-9)
    ok("sjf rotation", sum(ta.values()) / 4, num(d[2]), 1e-9)
    ok("sjf val", QS["sjf"]["val"], moy, 1e-9)


def t_rr():
    k, d = opts("rr")
    P = [("P1", 0, 7), ("P2", 1, 4), ("P3", 2, 2)]
    f3, f2 = round_robin(P, 3), round_robin(P, 2)
    ok("rr cle", float(f3["P2"]), num(k))
    ok("rr quantum 2", float(f2["P2"]), num(d[0]))
    ok("rr P3", float(f3["P3"]), num(d[1]))
    ok("rr P1", float(f3["P1"]), num(d[2]))
    ok("rr tout le calendrier", f3, {"P3": 8, "P2": 12, "P1": 13})
    ok("rr val", QS["rr"]["val"], 12)


def t_deadlock_safe():
    k, d = opts("deadlock_safe")
    total = 12
    alloc = {"P1": 5, "P2": 2, "P3": 3}
    mx = {"P1": 9, "P2": 4, "P3": 8}
    libre0 = total - sum(alloc.values())
    sures = []
    for perm in itertools.permutations(alloc):
        libre, bon = libre0, True
        for p in perm:
            if mx[p] - alloc[p] > libre:
                bon = False
                break
            libre += alloc[p]
        if bon:
            sures.append(", ".join(perm))
    ok("banquier libres", libre0, 2)
    ok("banquier une seule sequence sure", sures, [k])
    for i, t in enumerate(d):
        ok(f"banquier distracteur {i + 1} non sur", int(t in sures), 0)
    ok("banquier val", QS["deadlock_safe"]["val"], "P2,P1,P3")


# ------------------------------------------------------------------ reseaux, securite
def t_subnet_net():
    k, d = opts("subnet_net")
    ip = ipaddress.ip_address("172.16.37.200")
    reseau = ipaddress.ip_network("172.16.37.200/255.255.255.192", strict=False).network_address
    ok("subnet cle", str(reseau), k)
    ok("subnet ET bit a bit", ".".join(str(a & m) for a, m in zip(map(int, "172.16.37.200".split(".")), (255, 255, 255, 192))), k)
    ok("subnet masque 128", str(ipaddress.ip_network("172.16.37.200/255.255.255.128", strict=False).network_address), d[0])
    ok("subnet masque /24", str(ipaddress.ip_network("172.16.37.200/255.255.255.0", strict=False).network_address), d[1])
    ok("subnet masque /16", str(ipaddress.ip_network("172.16.37.200/255.255.0.0", strict=False).network_address), d[2])
    ok("subnet val", QS["subnet_net"]["val"], str(reseau))


def t_parity():
    k, d = opts("parity")
    octets = [bits(k)] + [bits(x) for x in d]
    impairs = [o for o in octets if o.count("1") % 2 == 1]
    ok("parite un seul octet impair", impairs, [bits(k)])
    ok("parite compte 5", bits(k).count("1"), 5)
    for o in octets[1:]:
        ok("parite quatre 1 " + o, o.count("1"), 4)
    ok("parite val", QS["parity"]["val"], bits(k))


def t_switch_mac():
    k, d = opts("switch_mac")
    # une seule option decrit le transfert selectif selon l'adresse MAC apprise
    roles = {"A switch": "selectif", "A hub": "diffusion", "A repeater": "regeneration", "A modem": "conversion"}
    ok("switch roles couverts", sorted(roles), sorted([k] + d))
    ok("switch un seul selectif", [t for t in [k] + d if roles[t] == "selectif"], [k])


def t_caesar():
    k, d = opts("caesar")
    def dec(s, n):
        return "".join(chr((ord(c) - 65 - n) % 26 + 65) for c in s)
    ok("caesar cle", dec("WIVZIV", 4), bits(k))
    ok("caesar aller-retour", dec(bits(k), -4), "WIVZIV")
    ok("caesar decalage avant", dec("WIVZIV", -4), bits(d[0]))
    ok("caesar recul de 3", dec("WIVZIV", 3), bits(d[1]))
    ok("caesar recul de 5", dec("WIVZIV", 5), bits(d[2]))
    ok("caesar val", QS["caesar"]["val"], dec("WIVZIV", 4))


def t_trojan():
    k, d = opts("trojan")
    defs = {"Trojan horse": {"deguise", "charge cachee"}, "worm": {"copie"}, "logic bomb": {"condition"}, "keylogger": {"frappes"}}
    scenario = {"deguise", "charge cachee"}  # programme utile en apparence + port ouvert en secret, sans copie ni condition ni simple enregistrement
    ok("trojan options couvertes", sorted(defs), sorted([k] + d))
    ok("trojan une seule definition recouvre le scenario", [n for n, s in defs.items() if scenario <= s], [k])


# ------------------------------------------------------------------ bases de donnees
def base():
    db = sqlite3.connect(":memory:")
    db.executescript("""
    create table Pupil(pid int, name text, town text, mark int);
    insert into Pupil values (1,'Ada','Buea',62),(2,'Bih','Limbe',48),(3,'Che','Buea',55),(4,'Dul','Kumba',71),(5,'Eno','Limbe',66),(6,'Fon','Buea',43),(7,'Gwen','Limbe',59);
    create table Customer(cid int, cname text);
    insert into Customer values (1,'Mba'),(2,'Nji'),(3,'Oben'),(4,'Pa');
    create table Orders(oid int, cid int, amount int);
    insert into Orders values (10,1,200),(11,1,150),(12,3,400),(13,3,50),(14,5,90);
    create table Staff(name text, salary int);
    insert into Staff values ('Aba',320),('Bessem',450),('Chi',280),('Dione',510),('Epie',300),('Fru',390),('Gah',380);
    """)
    return db


def fmt_groupes(lignes, nd=1):
    parts = [f"{t} {v:.{nd}f}" if isinstance(v, float) else f"{t} {v}" for t, v in lignes]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def t_sql_group():
    k, d = opts("sql_group")
    db = base()
    # le texte de l'enonce doit etre la requete executee
    stem = QS["sql_group"]["stem"]
    ok("sql_group requete presente", int("WHERE mark >= 50\nGROUP BY town\nHAVING COUNT(*) >= 2\nORDER BY town" in stem), 1)
    r = db.execute("SELECT town, AVG(mark) FROM Pupil WHERE mark >= 50 GROUP BY town HAVING COUNT(*) >= 2 ORDER BY town").fetchall()
    ok("sql_group cle", fmt_groupes(r), k)
    r1 = db.execute("SELECT town, AVG(mark) FROM Pupil GROUP BY town HAVING COUNT(*) >= 2 ORDER BY town").fetchall()
    ok("sql_group sans WHERE", fmt_groupes(r1), d[0])
    r2 = db.execute("SELECT town, AVG(mark) FROM Pupil WHERE mark >= 50 GROUP BY town ORDER BY town").fetchall()
    ok("sql_group sans HAVING", fmt_groupes(r2), d[1])
    r3 = db.execute("SELECT town, COUNT(*) FROM Pupil WHERE mark >= 50 GROUP BY town HAVING COUNT(*) >= 2 ORDER BY town").fetchall()
    ok("sql_group COUNT", fmt_groupes(r3), d[2])
    ok("sql_group val", QS["sql_group"]["val"], "sql_group")


def t_sql_join():
    k, d = opts("sql_join")
    db = base()
    n = lambda q: float(db.execute(q).fetchone()[0])
    ok("sql_join cle", n("SELECT COUNT(*) FROM (SELECT c.cname, o.amount FROM Customer c LEFT JOIN Orders o ON c.cid = o.cid)"), num(k))
    ok("sql_join interne", n("SELECT COUNT(*) FROM (SELECT c.cname, o.amount FROM Customer c JOIN Orders o ON c.cid = o.cid)"), num(d[0]))
    ok("sql_join commandes", n("SELECT COUNT(*) FROM Orders"), num(d[1]))
    ok("sql_join croisee", n("SELECT COUNT(*) FROM (SELECT * FROM Customer CROSS JOIN Orders)"), num(d[2]))
    ok("sql_join commande orpheline", n("SELECT COUNT(*) FROM Orders WHERE cid NOT IN (SELECT cid FROM Customer)"), 1.0)
    ok("sql_join val", QS["sql_join"]["val"], 6)


def liste_noms(noms):
    return ", ".join(noms[:-1]) + " and " + noms[-1] if len(noms) > 1 else noms[0]


def t_sql_subq():
    k, d = opts("sql_subq")
    db = base()
    noms = lambda q: [r[0] for r in db.execute(q).fetchall()]
    ok("sql_subq cle", liste_noms(noms("SELECT name FROM Staff WHERE salary > (SELECT AVG(salary) FROM Staff) ORDER BY name")), k)
    sal = sorted(r[0] for r in db.execute("select salary from Staff"))
    med = sal[len(sal) // 2]
    ok("sql_subq mediane", med, 380)
    ok("sql_subq mediane distracteur", liste_noms(noms(f"SELECT name FROM Staff WHERE salary > {med} ORDER BY name")), d[0])
    ok("sql_subq inferieur", liste_noms(noms("SELECT name FROM Staff WHERE salary < (SELECT AVG(salary) FROM Staff) ORDER BY name")), d[1])
    ok("sql_subq minimum", liste_noms(noms("SELECT name FROM Staff WHERE salary > (SELECT MIN(salary) FROM Staff) ORDER BY name")), d[2])
    ok("sql_subq moyenne", round(db.execute("select avg(salary) from Staff").fetchone()[0], 1), 375.7)
    ok("sql_subq val", QS["sql_subq"]["val"], "sql_subq")


def t_normal_form():
    """Dependances fonctionnelles : calcul de la plus haute forme normale a partir des DF et de la cle."""
    k, d = opts("normal_form")
    attrs = {"OrderID", "ProductID", "ProductName", "Quantity"}
    cle = {"OrderID", "ProductID"}
    DF = [({"ProductID"}, {"ProductName"}), ({"OrderID", "ProductID"}, {"Quantity", "ProductName"})]
    def fermeture(x):
        x = set(x)
        ch = True
        while ch:
            ch = False
            for g, dr in DF:
                if g <= x and not dr <= x:
                    x |= dr
                    ch = True
        return x
    ok("nf cle candidate", int(fermeture(cle) == attrs and all(fermeture(cle - {a}) != attrs for a in cle)), 1)
    non_cle = attrs - cle
    partielle = any(g < cle and dr & non_cle for g, dr in DF)
    ok("nf dependance partielle", int(partielle), 1)
    haute = "First normal form" if partielle else "Second normal form"
    ok("nf cle", haute, k)
    ok("nf distracteurs plus hauts", [d[0], d[1], d[2]], ["Second normal form", "Third normal form", "Boyce-Codd normal form"])


# ------------------------------------------------------------------ algorithmes
def t_trace_loop():
    k, d = opts("trace_loop")
    total = 0
    for i in range(1, 9):
        total = total + i if i % 3 == 0 else total - 1
    ok("trace cle", float(total), num(k))
    t2 = 0
    for i in range(1, 8):
        t2 = t2 + i if i % 3 == 0 else t2 - 1
    ok("trace i jusqu'a 7", float(t2), num(d[0]))
    ok("trace sans soustractions", float(sum(i for i in range(1, 9) if i % 3 == 0)), num(d[1]))
    ok("trace sans additions", float(-8), num(d[2]))
    ok("trace val", QS["trace_loop"]["val"], total)


def t_bubble():
    k, d = opts("bubble")
    L = [9, 4, 7, 1, 8, 3]
    def bulles(L, passes):
        L = L[:]
        for p in range(passes):
            for i in range(len(L) - 1 - p):
                if L[i] > L[i + 1]:
                    L[i], L[i + 1] = L[i + 1], L[i]
        return L
    def selection(L, passes):
        L = L[:]
        for p in range(passes):
            m = min(range(p, len(L)), key=lambda i: L[i])
            L[p], L[m] = L[m], L[p]
        return L
    s = lambda L: "`" + " ".join(map(str, L)) + "`"
    ok("bubble cle", s(bulles(L, 2)), k)
    ok("bubble 1 passe", s(bulles(L, 1)), d[0])
    ok("bubble 3 passes", s(bulles(L, 3)), d[1])
    ok("bubble selection", s(selection(L, 2)), d[2])
    ok("bubble val", QS["bubble"]["val"], " ".join(map(str, bulles(L, 2))))


def t_insertion():
    k, d = opts("insertion")
    L = [5, 2, 9, 1, 7, 3]
    A = L[:]
    dec = cmp_ = 0
    for i in range(1, len(A)):
        x, j = A[i], i - 1
        while j >= 0:
            cmp_ += 1
            if A[j] > x:
                A[j + 1] = A[j]
                dec += 1
                j -= 1
            else:
                break
        A[j + 1] = x
    inversions = sum(1 for i in range(len(L)) for j in range(i + 1, len(L)) if L[i] > L[j])
    ok("insertion decalages", float(dec), num(k))
    ok("insertion = inversions", inversions, dec)
    ok("insertion comparaisons", float(cmp_), num(d[0]))
    ok("insertion passes", float(len(L) - 1), num(d[1]))
    ok("insertion pire cas", float(len(L) * (len(L) - 1) // 2), num(d[2]))
    ok("insertion trie", A, sorted(L))
    ok("insertion val", QS["insertion"]["val"], dec)


def t_binsearch():
    k, d = opts("binsearch")
    A = [4, 9, 13, 18, 22, 27, 31, 36, 40, 45, 51, 58, 63]
    lo, hi, c, trouve = 0, len(A) - 1, 0, None
    while lo <= hi:
        m = (lo + hi) // 2
        c += 1
        if A[m] == 40:
            trouve = m
            break
        if A[m] < 40:
            lo = m + 1
        else:
            hi = m - 1
    ok("binsearch trouve en 8", trouve, 8)
    ok("binsearch cle", float(c), num(k))
    ok("binsearch sans la derniere", float(c - 1), num(d[0]))
    ok("binsearch +1", float(c + 1), num(d[1]))
    ok("binsearch lineaire", float(A.index(40) + 1), num(d[2]))
    ok("binsearch liste triee", A, sorted(A))
    ok("binsearch val", QS["binsearch"]["val"], c)


def t_stack_pops():
    k, d = opts("stack_pops")
    ops = [("push", 4), ("push", 9), ("pop",), ("push", 2), ("push", 7), ("pop",), ("pop",)]
    def run(ops, fifo=False):
        s, sortie = [], []
        for o in ops:
            if o[0] == "push":
                s.append(o[1])
            else:
                sortie.append(s.pop(0) if fifo else s.pop())
        return sortie
    fmt = lambda L: ", ".join(map(str, L))
    pile = run(ops)
    ok("stack cle", fmt(pile), k)
    ok("stack file", fmt(run(ops, True)), d[0])
    ok("stack inverse", fmt(pile[::-1]), d[1])
    ok("stack sans push 2", fmt(run([o for o in ops if o != ("push", 2)])), d[2])
    ok("stack val", QS["stack_pops"]["val"], tuple(pile))


def t_bst_post():
    k, d = opts("bst_post")
    ordre = [40, 25, 60, 10, 30, 50, 70, 28, 35]
    def inserer(arbre, v):
        if arbre is None:
            return [v, None, None]
        if v < arbre[0]:
            arbre[1] = inserer(arbre[1], v)
        else:
            arbre[2] = inserer(arbre[2], v)
        return arbre
    t = None
    for v in ordre:
        t = inserer(t, v)
    post = lambda a: post(a[1]) + post(a[2]) + [a[0]] if a else []
    pre = lambda a: [a[0]] + pre(a[1]) + pre(a[2]) if a else []
    ino = lambda a: ino(a[1]) + [a[0]] + ino(a[2]) if a else []
    fmt = lambda L: ", ".join(map(str, L))
    ok("bst post", fmt(post(t)), k)
    ok("bst pre", fmt(pre(t)), d[0])
    ok("bst in", fmt(ino(t)), d[1])
    ok("bst niveaux = insertion", fmt(ordre), d[2])
    # parcours par niveaux reel
    niv, file_ = [], deque([t])
    while file_:
        a = file_.popleft()
        if a:
            niv.append(a[0])
            file_ += [a[1], a[2]]
    ok("bst niveaux reel", fmt(niv), d[2])
    ok("bst val", QS["bst_post"]["val"], tuple(post(t)))


def t_postfix():
    k, d = opts("postfix")
    def evaluer(expr, inverse=False, arret=None, plus_final=False):
        pile = []
        jetons = expr.split()
        for i, j in enumerate(jetons):
            if j in "+-*/":
                if arret is not None and i == arret:
                    break
                b, a = pile.pop(), pile.pop()
                if inverse and i == len(jetons) - 1:
                    a, b = b, a
                if plus_final and i == len(jetons) - 1:
                    j = "+"
                pile.append({"+": a + b, "-": a - b, "*": a * b, "/": a / b}[j])
            else:
                pile.append(int(j))
        return pile[-1]
    e = "15 4 3 + 2 * -"
    ok("postfix cle", float(evaluer(e)), num(k))
    ok("postfix operandes inverses", float(evaluer(e, inverse=True)), num(d[0]))
    ok("postfix avant le dernier operateur", float(evaluer(e, arret=len(e.split()) - 1)), num(d[1]))
    ok("postfix plus au lieu de moins", float(evaluer(e, plus_final=True)), num(d[2]))
    ok("postfix equivalent infixe", 15 - (4 + 3) * 2, 1)
    ok("postfix val", QS["postfix"]["val"], 1)


def t_byval_byref():
    k, d = opts("byval_byref")
    def mix(mode_a, mode_b):
        env = {"x": 3, "y": 4}
        loc = {"a": env["x"], "b": env["y"]}
        def lire(n):
            return env[{"a": "x", "b": "y"}[n]] if {"a": mode_a, "b": mode_b}[n] == "ref" else loc[n]
        def ecrire(n, v):
            if {"a": mode_a, "b": mode_b}[n] == "ref":
                env[{"a": "x", "b": "y"}[n]] = v
            else:
                loc[n] = v
        ecrire("a", lire("a") + 5)
        ecrire("b", lire("b") * 2)
        ecrire("a", lire("a") + lire("b"))
        return f"{env['x']} {env['y']}"
    ok("byval cle", mix("val", "ref"), k)
    ok("byval les deux par reference", mix("ref", "ref"), d[0])
    ok("byval les deux par valeur", mix("val", "val"), d[1])
    ok("byval modes inverses", mix("ref", "val"), d[2])
    ok("byval val", QS["byval_byref"]["val"], (3, 8))


def t_recursion_g():
    k, d = opts("recursion_g")
    def g(n):
        return 2 if n == 0 else g(n - 1) * 2 + 1
    def g_faux(n):
        return 2 if n == 0 else (g_faux(n - 1) + 1) * 2
    def g_sans_1(n):
        return 2 if n == 0 else g_sans_1(n - 1) * 2
    ok("recursion cle", float(g(4)), num(k))
    ok("recursion +1 avant x2", float(g_faux(4)), num(d[0]))
    ok("recursion sans +1", float(g_sans_1(4)), num(d[1]))
    ok("recursion niveau en moins", float(g(3)), num(d[2]))
    ok("recursion chaine", [g(i) for i in range(5)], [2, 5, 11, 23, 47])
    ok("recursion val", QS["recursion_g"]["val"], 47)


def t_scaling():
    k, d = opts("scaling")
    r = 1500 / 500
    ok("scaling cle", 3 * r ** 2, num(k))
    ok("scaling lineaire", 3 * r, num(d[0]))
    ok("scaling cubique", 3 * r ** 3, num(d[1]))
    ok("scaling addition", 3 + r, num(d[2]))
    ok("scaling val", QS["scaling"]["val"], 27)


def t_dvd_backup():
    k, d = opts("dvd_backup")
    ok("dvd cle", float(math.ceil(120000 / 4700)), num(k))
    ok("dvd quotient", round(120000 / 4700, 2), 25.53, 1e-9)
    ok("dvd arrondi bas", float(120000 // 4700), num(d[0]))
    ok("dvd 1024", float(math.ceil(120 * 1024 / 4700)), num(d[1]))
    ok("dvd 5 Go", float(math.ceil(120 / 5)), num(d[2]))
    ok("dvd 25 disques ne suffisent pas", int(25 * 4.7 >= 120), 0)
    ok("dvd val", QS["dvd_backup"]["val"], 26)


def t_amdahl():
    k, d = opts("amdahl")
    s, p, N = 0.3, 0.7, 4
    ok("amdahl cle", round(1 / (s + p / N), 1), num(k), 1e-9)
    ok("amdahl 1/0.475", round(1 / 0.475, 3), 2.105, 1e-9)
    ok("amdahl p x N", round(p * N, 1), num(d[0]), 1e-9)
    ok("amdahl limite", round(1 / s, 1), num(d[1]), 1e-9)
    ok("amdahl ideal", float(N), num(d[2]))
    ok("amdahl val", QS["amdahl"]["val"], round(1 / (s + p / N), 3), 1e-9)


# ------------------------------------------------------------------ questions factuelles : coherence logique
def t_logic_paradigm():
    k, d = opts("logic_paradigm")
    ok("paradigme options distinctes", len({k, *[x[0] for x in QS['logic_paradigm']['dist']]}), 4)
    ok("paradigme une seule option 'logic'", sum(1 for t in [k] + d if "logic" in t), 1)


def t_compiler_phases():
    k, d = opts("compiler_phases")
    ordre = ["Lexical analysis", "Syntax analysis", "Semantic analysis", "Code generation"]
    lire = lambda t: [x.strip().capitalize() for x in t.split(",")]
    ok("compilateur cle", lire(k), ordre)
    for i, t in enumerate(d):
        ok(f"compilateur distracteur {i + 1} permute", int(lire(t) != ordre and sorted(lire(t)) == sorted(ordre)), 1)


def t_boundary_tests():
    k, d = opts("boundary_tests")
    lo, hi = 18, 60
    frontiere = sorted({lo - 1, lo, hi, hi + 1})
    lire = lambda t: sorted(int(x) for x in t.split(","))
    ok("limites cle", lire(k), frontiere)
    for i, t in enumerate(d):
        ok(f"limites distracteur {i + 1} different", int(lire(t) == frontiere), 0)
    ok("limites val", list(QS["boundary_tests"]["val"]), frontiere)


def t_parallel_running():
    k, d = opts("parallel_running")
    ok("changement options distinctes", len({k, *d}), 4)
    ok("changement une seule 'parallel'", sum(1 for t in [k] + d if "parallel" in t), 1)


def t_tps():
    k, d = opts("tps")
    ok("SI options distinctes", len({k, *d}), 4)
    ok("SI une seule 'transaction'", sum(1 for t in [k] + d if "transaction" in t), 1)


TESTS = [t_hex2dec, t_hex_octal, t_bits_colours, t_bin_add, t_twos_neg, t_twos_sub, t_overflow, t_bool_simpl, t_demorgan, t_xor_circuit, t_full_adder,
         t_nand_or, t_addr_capacity, t_download_time, t_pc_fetch, t_fetch_regs, t_acc_trace, t_process_state, t_fifo_faults, t_paging_addr, t_fcfs, t_sjf,
         t_rr, t_deadlock_safe, t_subnet_net, t_parity, t_switch_mac, t_caesar, t_trojan, t_sql_group, t_sql_join, t_sql_subq, t_normal_form, t_trace_loop,
         t_bubble, t_insertion, t_binsearch, t_stack_pops, t_bst_post, t_postfix, t_byval_byref, t_recursion_g, t_scaling, t_dvd_backup, t_amdahl,
         t_logic_paradigm, t_compiler_phases, t_boundary_tests, t_parallel_running, t_tps]
couverts = {t.__name__[2:] for t in TESTS}
ok("couverture : chaque question a son test", sorted(set(QS) - couverts), [])
for t in TESTS:
    t()

# ------------------------------------------------------------------ coherence du JSON genere
if os.path.exists(EP):
    ep = json.load(open(EP, encoding="utf8"))
    qj = ep["exercices"][0]["questions"]
    ok("JSON nombre de questions", len(qj), 50)
    ok("JSON blueprint", ep["blueprint_external_id"], "bp-cm-gce-al-computerscience-p1-1")
    comp_bp = set(json.load(open(BP, encoding="utf8"))["competences"])
    par_enonce = {q["stem"]: q for q in questions()}
    for i, j in enumerate(qj, start=1):
        q = par_enonce[j["enonce_markdown"]]
        lettres = {c["lettre"]: c["texte"] for c in j["choix"]}
        bonne = j["reponse_correcte"]
        ok(f"{i} cle", int(lettres[bonne] == q["key"]), 1)
        ok(f"{i} unicite", sum(1 for t in lettres.values() if t == q["key"]), 1)
        ok(f"{i} quatre options distinctes", len(set(lettres.values())), 4)
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", j["corrige_markdown"])
        ok(f"{i} Answer", int(bool(m) and m.group(1).lower() == bonne), 1)
        ok(f"{i} points", j["points"], 1)
        ok(f"{i} themes dans le blueprint", int(all(t in comp_bp for t in j["themes"])), 1)
        ok(f"{i} rappel verbatim", int(j["rappels_de_methode"][0]["contenu_markdown"] in j["corrige_markdown"]), 1)
        ok(f"{i} pas de tout/aucun des precedents", int(not re.search(r"all of the above|none of the above", " ".join(lettres.values()), re.I)), 1)
        ok(f"{i} pas de tiret cadratin", int("\u2014" not in json.dumps(j, ensure_ascii=False)), 1)
        ok(f"{i} pas de dollar", int("$" not in j["enonce_markdown"] + "".join(lettres.values())), 1)
        blocs = re.findall(r"```.*?```", j["enonce_markdown"], re.S)
        ok(f"{i} pas de guillemets droits dans un bloc de code", int(all('"' not in b for b in blocs)), 1)
    cnt = Counter(j["reponse_correcte"] for j in qj)
    ok("equilibre", max(cnt.values()) - min(cnt.values()) <= 1, True)
    cles = [j["reponse_correcte"] for j in qj]
    ok("pas de trois cles identiques", sum(1 for a, b, c_ in zip(cles, cles[1:], cles[2:]) if a == b == c_), 0)
    diffs = Counter(j["difficulte_estimee"] for j in qj)
    ok("difficulte faibles 45-70 %", 0.45 <= diffs["faible"] / 50 <= 0.70, True)
    ok("difficulte elevees 1-4", 1 <= diffs["elevee"] <= 4, True)
    ok("themes voisins distincts", sum(1 for a, b in zip(qj, qj[1:]) if a["themes"][0] == b["themes"][0]), 0)
    ok("tous les themes du blueprint couverts", sorted(comp_bp - {t for j in qj for t in j["themes"]}), [])

print(f"{nverif} verifications")
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
    sys.exit(1)
print("0 ecart")
