r"""Recalcule INDEPENDAMMENT les resultats chiffres et logiques du Paper 2 Human Biology inedit (croisement ABO, probabilite, groupes possibles
du pere) par enumeration des genotypes, verifie que le corrige les cite, et que le total des points des criteres vaut le bareme de chaque
sous-question et celui de chaque question.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_humanbio_p2.py [ep-....json]

Le reste du Paper 2 est du rappel de cours : relu a la main, grille par grille.
"""
import itertools
import json
import os
import sys
from fractions import Fraction as Fr

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-humanbio-p2-1-2026-s1.json")


def phenotype(g):
    a, b = sorted(g)
    if "IA" in g and "IB" in g:
        return "AB"
    if "IA" in g:
        return "A"
    if "IB" in g:
        return "B"
    return "O"


def sous_question(ep, ex, num):
    for e in ep["exercices"]:
        if e["numero_exercice"] == ex:
            for q in e["questions"]:
                if q["numero"] == num:
                    return q
    raise KeyError((ex, num))


def verifier(ep):
    erreurs = []
    # --- 2b : mere IA i (groupe A), pere IB i (groupe B)
    mere, pere = ("IA", "i"), ("IB", "i")
    assert phenotype(mere) == "A" and phenotype(pere) == "B"
    enfants = [tuple(sorted(c)) for c in itertools.product(mere, pere)]
    phenos = sorted(phenotype(g) for g in enfants)
    assert phenos == ["A", "AB", "B", "O"], phenos
    p_o = Fr(phenos.count("O"), len(phenos))
    assert p_o == Fr(1, 4)
    corr = sous_question(ep, "2", "b")["corrige_markdown"].replace(" ", "")
    for attendu in ("I^{A}I^{B}", "I^{A}i", "I^{B}i", "ii", "AB", "\\dfrac{1}{4}", "25\\%"):
        if attendu.replace(" ", "") not in corr:
            erreurs.append(f"2b: '{attendu}' absent du corrige")
    # --- 2c : enfant AB, mere de groupe A ; peres possibles
    genotypes = {"A": [("IA", "IA"), ("IA", "i")], "B": [("IB", "IB"), ("IB", "i")], "AB": [("IA", "IB")], "O": [("i", "i")]}
    possibles = set()
    for groupe, gens in genotypes.items():
        for pere in gens:
            for mere in genotypes["A"]:
                if any(phenotype(c) == "AB" for c in itertools.product(mere, pere)):
                    possibles.add(groupe)
    assert possibles == {"B", "AB"}, possibles
    corr = sous_question(ep, "2", "c")["corrige_markdown"]
    if "cannot be the father" not in corr or "blood group B" not in corr or "blood group AB" not in corr:
        erreurs.append("2c: le corrige ne cite pas les groupes possibles du pere ou le refus du pere de groupe O")
    # --- baremes : somme des criteres = points de la sous-question, somme des sous-questions = 20, total = 100
    total = 0
    for e in ep["exercices"]:
        s = 0
        for q in e["questions"]:
            somme = sum(c["points"] for c in q["criteres_notation"])
            if abs(somme - float(q["points"])) > 1e-9:
                erreurs.append(f"{e['numero_exercice']}{q['numero']}: criteres {somme} != points {q['points']}")
            s += float(q["points"])
        if abs(s - 20) > 1e-9:
            erreurs.append(f"question {e['numero_exercice']}: {s} points au lieu de 20")
        total += s
    if abs(total - 100) > 1e-9:
        erreurs.append(f"total {total} au lieu de 100")
    return erreurs


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    nq = sum(len(e["questions"]) for e in ep["exercices"])
    print(f"2 sous-questions recalculees (croisement ABO, groupes possibles du pere) et {nq} baremes verifies, {len(erreurs)} ecart(s). Le reste est du rappel de cours, relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
