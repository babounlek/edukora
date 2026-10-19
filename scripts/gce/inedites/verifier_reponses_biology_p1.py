"""Recalcule INDEPENDAMMENT les reponses chiffrees ou lues sur donnees du Paper 1 Biology inedit, et controle la coherence des
donnees des figures. Les questions de pur rappel de cours (la majorite) n'ont rien a recalculer : elles sont relues a la main
(voir `faits_a_relire` ci-dessous) et le restent.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\verifier_reponses_biology_p1.py [ep-....json]

Pour chaque question recalculable : valeur attendue recalculee ici a partir des donnees, les quatre options lues, la cle doit etre
la SEULE egale. Sortie 1 au moindre ecart.
"""
import itertools
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_biology_p1 as F  # noqa: E402
from questions_biology_p1 import questions  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm",
                      "ep-cm-gce-ol-biology-p1-1-2026-s1.json")


def nombre(txt):
    t = txt.replace("\\,", "").replace(" ", "")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return float(m.group()) if m else None


def chaines_vers(aretes, cible):
    """Nombre de chaines alimentaires distinctes (producteur -> ... -> cible) dans un reseau d'aretes (proie, predateur)."""
    proies = {}
    for a, b in aretes:
        proies.setdefault(b, []).append(a)
    producteurs = {a for a, _ in aretes} - {b for _, b in aretes}

    def remonte(x):
        if x in producteurs:
            return 1
        return sum(remonte(p) for p in proies.get(x, []))
    return remonte(cible)


def offre_attendue():
    """id -> (fonction de lecture d'une option, valeur attendue)."""
    E = {}
    E["b03"] = (nombre, 45 / 0.03)
    # b08 : la solution dont la masse n'a pas change est de meme concentration que la seve
    masses = {"P": 11.4, "Q": 10.5, "R": 10.0, "S": 8.7}
    E["b08"] = (lambda t: t.strip(". "), [k for k, v in masses.items() if v == 10.0][0])
    # b10 : regles de lecture des trois tests
    tests = {"benedict": "bleu", "iode": "bleu-noir", "biuret": "bleu"}
    contenu = []
    if tests["iode"] == "bleu-noir":
        contenu.append("starch")
    if tests["benedict"] == "rouge brique":
        contenu.append("reducing sugar")
    if tests["biuret"] == "violet":
        contenu.append("protein")
    E["b10"] = (lambda t: t.lower(), "starch only." if contenu == ["starch"] else None)
    # b12 : l'activite est maximale a l'optimum et nulle (enzyme denaturee) a 60 degres
    assert F._act_enzyme(F.TEMP_OPTIMUM) == max(F._act_enzyme(t) for t in range(0, 71))
    assert F._act_enzyme(60) < 0.01 and F._act_enzyme(20) > 0.1
    E["b12"] = (lambda t: t.lower(), "is denatured and stops working.")
    # b18 : plateau a partir de P (intensite 6), pas avant
    assert min(5 * 8 / F.PLATEAU_LUMIERE, 8) < 8 and min(F.PLATEAU_LUMIERE * 8 / F.PLATEAU_LUMIERE, 8) == 8 and min(9 * 8 / F.PLATEAU_LUMIERE, 8) == 8
    E["b18"] = (lambda t: t.lower().startswith("another factor"), True)
    # b25 : le taux est maximal a 13 h et ne fait que decroitre apres 15 h
    pic = F.HEURES_TRANSPIRATION[F.TAUX_TRANSPIRATION.index(max(F.TAUX_TRANSPIRATION))]
    apres = [v for h, v in zip(F.HEURES_TRANSPIRATION, F.TAUX_TRANSPIRATION) if h >= 15]
    assert pic == 13 and all(a > b for a, b in zip(apres, apres[1:])), "donnees de transpiration"
    E["b25"] = (nombre, pic)
    # b37 : 4,00 / 0,04
    E["b37"] = (nombre, 4.00 / 0.04)
    # b41 : premiere minute ou le rythme atteint la valeur de repos
    E["b41"] = (nombre, next(m for m, v in zip(F.FC_MINUTES, F.FC_BATTEMENTS) if v <= F.FC_REPOS))
    # b52 : Tt x tt
    def part_recessive(p1, p2):
        enf = ["".join(sorted(a + b)) for a, b in itertools.product(p1, p2)]
        return 100 * sum(1 for e in enf if e == e.lower()) / len(enf)
    E["b52"] = (nombre, part_recessive("Tt", "tt"))
    # b54 : chaines qui finissent au faucon
    E["b54"] = (nombre, chaines_vers(F.RESEAU_ARETES, "hawk"))
    return E


def verifier(ep):
    erreurs = []
    qs = ep["exercices"][0]["questions"]
    source = {q["id"]: q for q in questions()}
    E = offre_attendue()
    trouvees = 0
    for qid, (lire, attendu) in E.items():
        src = source[qid]
        cible = [q for q in qs if src["sol"].replace("{FIG}", "") in q["corrige_markdown"] or src["sol"].split("{FIG}")[0] in q["corrige_markdown"]]
        if len(cible) != 1:
            erreurs.append(f"{qid}: question introuvable ou ambigue dans l'epreuve ({len(cible)})")
            continue
        q = cible[0]
        trouvees += 1
        egales = [c["lettre"] for c in q["choix"] if lire(c["texte"]) == attendu or (isinstance(attendu, float) and lire(c["texte"]) is not None and abs(lire(c["texte"]) - attendu) < 1e-9)]
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"{qid} (Q{q['numero']}): attendu {attendu!r}, cle {q['reponse_correcte']}, options egales {egales}")
    return erreurs, trouvees


FAITS_A_RELIRE = (
    "Les autres questions sont du rappel de cours : cle et distracteurs relus a la main (aucune option ne doit etre defendable) ; "
    "voir le compte rendu de generation."
)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    print(f"{n} questions recalculees sur {len(ep['exercices'][0]['questions'])}, {len(erreurs)} ecart(s). {FAITS_A_RELIRE}")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
