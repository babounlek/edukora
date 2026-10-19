r"""Recalcule INDEPENDAMMENT les reponses chiffrees ou lues sur les donnees des figures du Paper 1 Chemistry inedit.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_chemistry_p1.py [ep-....json]

Les masses molaires sont recalculees a partir des formules (table des masses atomiques de la consigne), les moles et volumes sont recalcules ici,
les options sont lues, et la cle doit etre la SEULE egale. Les questions de pur rappel de cours sont relues a la main.
Sortie 1 au moindre ecart.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_chemistry_p1 as F  # noqa: E402
from questions_chemistry_p1 import questions  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-chemistry-p1-1-2026-s1.json")
AR = {"H": 1, "C": 12, "N": 14, "O": 16, "Mg": 24, "S": 32, "Ca": 40}
VM_CM3 = 24000


def masse_molaire(formule):
    """Masse molaire d'une formule du type H2SO4 ou CaCO3 (pas de parentheses ici)."""
    total = 0
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formule):
        total += AR[el] * (int(n) if n else 1)
    return total


def nombre(txt):
    t = txt.replace("$", "").replace("\\,", "").replace("\\ ", " ")
    t = re.sub(r"\\text\{[^}]*\}", "", t).replace("^{\\circ}", "").replace("\\%", "").replace("%", "")
    t = t.replace("\\mathrm{", "").replace("}", "")
    m = re.search(r"[-−+]?\d+(?:\.\d+)?", t.replace(" ", ""))
    return float(m.group().replace("−", "-")) if m else None


def formule_brute(txt):
    return re.sub(r"[\\$ {}_]|mathrm", "", txt)


def attendues():
    E = {}
    E["c06"] = (nombre, 4.9 / masse_molaire("H2SO4"))
    E["c07"] = (nombre, 10.0 / masse_molaire("CaCO3") * 1 * VM_CM3)
    E["c08"] = (nombre, 4.8 / AR["Mg"] * masse_molaire("MgO"))
    # 25,0 cm3 de NaOH 0,20 mol/dm3 neutralisent 20,0 cm3 de H2SO4 : rapport 2 NaOH pour 1 H2SO4
    E["c09"] = (nombre, (0.20 * 25.0 / 1000) / 2 / (20.0 / 1000))
    # formule empirique : 80 % C, 20 % H -> rapport en moles, simplifie par le plus petit
    nc, nh = 80 / AR["C"], 20 / AR["H"]
    petit = min(nc, nh)
    E["c10"] = (formule_brute, f"CH{round(nh / petit)}" if abs(nc / petit - 1) < 1e-9 else "?")
    E["c11"] = (nombre, round(200 * (127 + 273) / (27 + 273)))
    # solubilite : difference entre 60 et 20 degres, lue dans les constantes de la figure
    sol = dict(F.SOLUBILITE)
    E["c12"] = (nombre, sol[60] - sol[20])
    E["c32"] = (lambda t: re.sub(r"[^\d:]", "", t), "2:1")
    gaz = dict(F.GAZ)
    E["c34"] = (nombre, gaz[2] / 2)
    E["c39"] = (nombre, F.PROFIL["produits"] - F.PROFIL["reactifs"])
    E["c42"] = (nombre, 100 * 5)
    # c33 : etat d'oxydation de Mn dans KMnO4 : (+1) + x + 4(-2) = 0
    E["c33"] = (nombre, -(1 + 4 * -2))
    return E


def verifier(ep):
    erreurs = []
    qs = ep["exercices"][0]["questions"]
    source = {q["id"]: q for q in questions()}
    trouvees = 0

    def cible(qid):
        sol = source[qid]["sol"]
        return [q for q in qs if sol in q["corrige_markdown"]]

    for qid, (lire, attendu) in attendues().items():
        c = cible(qid)
        if len(c) != 1:
            erreurs.append(f"{qid}: question introuvable ou ambigue ({len(c)})")
            continue
        q = c[0]
        trouvees += 1
        egales = []
        for ch in q["choix"]:
            v = lire(ch["texte"])
            if v == attendu or (isinstance(attendu, float) and isinstance(v, float) and abs(v - attendu) < 1e-9):
                egales.append(ch["lettre"])
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"{qid} (Q{q['numero']}): attendu {attendu!r}, cle {q['reponse_correcte']}, options egales {egales}")

    # c27 : completion multiple, une equation est une OXYDATION quand les electrons sont a droite de la fleche
    c = cible("c27")
    if len(c) == 1:
        trouvees += 1
        q = c[0]
        lignes = re.findall(r"^(\d)\. \$(.+)\$$", q["enonce_markdown"], re.M)
        oxydees = [n for n, eq in lignes if "e^-" in eq.split("\\rightarrow")[1]]
        attendu = " and ".join([", ".join(oxydees[:-1]), oxydees[-1]]) if len(oxydees) > 2 else " and ".join(oxydees)
        texte = {ch["lettre"]: ch["texte"] for ch in q["choix"]}[q["reponse_correcte"]]
        if texte != attendu + " only":
            erreurs.append(f"c27: oxydations en {oxydees} -> '{attendu} only', cle '{texte}'")
    # c28 / c29 : completion multiple, jeux de verite ecrits ici (la verite chimique est relue a la main)
    verites = {"c28": {"1": True, "2": True, "3": True, "4": False}, "c29": {"1": False, "2": False, "3": False, "4": True}}
    for qid, tv in verites.items():
        c = cible(qid)
        if len(c) != 1:
            erreurs.append(f"{qid}: introuvable")
            continue
        trouvees += 1
        q = c[0]
        justes = [n for n, v in tv.items() if v]
        attendu = {"123": "1, 2 and 3 only", "13": "1 and 3 only", "24": "2 and 4 only", "4": "4 only"}.get("".join(justes))
        texte = {ch["lettre"]: ch["texte"] for ch in q["choix"]}[q["reponse_correcte"]]
        if texte != attendu:
            erreurs.append(f"{qid}: vrais {justes} -> {attendu}, cle '{texte}'")
    # c36 / c37 : assertion-raison, (premiere vraie, seconde vraie, seconde explique la premiere)
    ar = {"c36": (False, True, False), "c37": (True, True, False)}
    for qid, (v1, v2, expl) in ar.items():
        c = cible(qid)
        if len(c) != 1:
            erreurs.append(f"{qid}: introuvable")
            continue
        trouvees += 1
        q = c[0]
        if v1 and v2 and expl:
            lettre = "a"
        elif v1 and v2:
            lettre = "b"
        elif v1:
            lettre = "c"
        else:
            lettre = "d"
        if q["reponse_correcte"] != lettre:
            erreurs.append(f"{qid}: attendu {lettre}, cle {q['reponse_correcte']}")
    # constantes de figure
    if F.GAZ[2] != (2, 50) or F.PROFIL != {"reactifs": 150, "sommet": 240, "produits": 90} or dict(F.SOLUBILITE)[20] != 40 or dict(F.SOLUBILITE)[60] != 120:
        erreurs.append("constantes de figure modifiees")
    return erreurs, trouvees


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    print(f"{n} questions recalculees sur {len(ep['exercices'][0]['questions'])}, {len(erreurs)} ecart(s). Les autres sont du rappel de cours, relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
