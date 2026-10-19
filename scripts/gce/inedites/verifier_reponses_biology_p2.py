"""Verifie les valeurs chiffrees du Paper 2 Biology inedit (taux du potometre, croisement, energie) et leur presence dans les corriges.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\verifier_reponses_biology_p2.py [ep-....json]

Un paper de biologie est surtout factuel : les reponses modeles (listes, tableaux, descriptions) sont relues a la main contre le programme.
Ici, seuls les calculs sont recalcules independamment : rythme de montee de la bulle (2a), genotypes et proportions du croisement (3b),
energie a chaque niveau trophique (4c). Sortie 1 au moindre ecart.
"""
import itertools
import json
import os
import re
import sys

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-biology-p2-1-2026-s1.json")


def verifier(ep):
    erreurs = []
    qs = {(ex["numero_exercice"], q["numero"]): q for ex in ep["exercices"] for q in ex["questions"]}

    def corr(e, n):
        return qs[(e, n)]["corrige_markdown"]

    def ok(cond, msg):
        if not cond:
            erreurs.append(msg)

    def contient(e, n, *jetons):
        for j in jetons:
            ok(j in corr(e, n), f"{e}.{n}: valeur absente du corrige : {j!r}")

    # 2a : distance (mm) / duree (5 min), a partir des lignes du tableau de l'enonce
    texte2a = [ex for ex in ep["exercices"] if ex["numero_exercice"] == "2"][0]["enonce_intro_markdown"]
    distances = {m.group(1): int(m.group(2)) for m in re.finditer(r"\| ([A-D]) \|.*\| (\d+) \|\s*$", texte2a, re.M)}
    ok(set(distances) == set("ABCD"), f"2a : table du potometre illisible {distances}")
    taux = {k: v / 5 for k, v in distances.items()}
    ok(abs(taux["A"] - 2.4) < 1e-9 and abs(taux["C"] - 9.2) < 1e-9, f"2a : taux {taux}")
    contient("2", "a", "2.4", "9.2")
    ok(taux["C"] > taux["B"] > taux["A"] and taux["D"] > taux["B"], "2a : l'ordre des taux ne soutient plus les explications (vent, temperature)")
    # 3b : Pp x Pp
    enfants = ["".join(sorted(a + b)) for a, b in itertools.product("Pp", "Pp")]
    comptes = {g: enfants.count(g) for g in set(enfants)}
    ok(comptes == {"PP": 1, "Pp": 2, "pp": 1}, f"3b : genotypes {comptes}")
    jaunes = sum(1 for g in enfants if g == "pp") / len(enfants)
    ok(jaunes == 0.25 and 480 * jaunes == 120, "3b : proportion de grains jaunes")
    contient("3", "b", "$1\\,PP:2\\,Pp:1\\,pp$", "120", "$3$ purple : $1$ yellow")
    # F1 : PP x pp -> tous Pp
    ok({"".join(sorted(a + b)) for a, b in itertools.product("Pp"[:1], "p")} == {"Pp"}, "3b : F1")
    # 4c : 10 % a chaque niveau, trois fois
    e1 = 60000
    niveaux = [e1 * 0.1 ** k for k in range(1, 4)]
    ok([round(v) for v in niveaux] == [6000, 600, 60], f"4c : {niveaux}")
    contient("4", "c", "6\\,000", "600", "60")
    # 4a : coherence entre l'enonce (qui mange quoi) et la figure du corrige
    enonce = [ex for ex in ep["exercices"] if ex["numero_exercice"] == "4"][0]["enonce_intro_markdown"]
    liens = ["algae $\\rightarrow$ tadpoles", "water lilies $\\rightarrow$ snails", "tadpoles $\\rightarrow$ dragonfly larvae",
             "dragonfly larvae $\\rightarrow$ small fish", "snails $\\rightarrow$ small fish", "small fish $\\rightarrow$ heron"]
    contient("4", "a", *liens)
    for mot in ("tadpoles feed on algae", "snails feed on water lilies", "dragonfly larvae feed on tadpoles",
                "small fish feed on dragonfly larvae and on snails", "heron feeds on small fish"):
        ok(mot in enonce, f"4a : l'enonce ne dit plus « {mot} »")
    # chaque sous-question de 20 points par question : somme des criteres = points (deja garanti a la generation, relu ici)
    for ex in ep["exercices"]:
        ok(sum(float(q["points"]) for q in ex["questions"]) == float(ex["points"]) == 20, f"question {ex['numero_exercice']} : 20 points")
        for q in ex["questions"]:
            ok(sum(float(c["points"]) for c in q["criteres_notation"]) == float(q["points"]), f"{ex['numero_exercice']}.{q['numero']} : grille")
    return erreurs


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    n = sum(len(x["questions"]) for x in ep["exercices"])
    print(f"{n} sous-questions, calculs recalcules (2a, 3b, 4a, 4c), {len(erreurs)} ecart(s). Le reste est factuel : relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
