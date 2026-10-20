r"""Recalcule INDEPENDAMMENT les 5 questions chiffrees du Paper 1 Human Biology inedit (debit ventilatoire, pouls, croisements, probabilite
conditionnelle) et controle la structure des 44 autres (une cle, quatre options distinctes, lettre du corrige = cle).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_humanbio_p1.py [ep-....json]

Les croisements sont recalcules en ENUMERANT les gametes ; la probabilite conditionnelle de la question 40 est recalculee en enumerant les
genotypes possibles des enfants de deux parents sains dont un premier enfant est atteint. Les autres questions sont du rappel de cours,
relu a la main : une cle fausse n'y est detectable que par relecture.
"""
import itertools
import json
import os
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
import figs_humanbio_p1 as F  # noqa: E402
from questions_humanbio_p1 import questions  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-humanbio-p1-1-2026-s1.json")


def nombre(txt):
    t = txt.replace("$", "").replace("\\,", "").replace("\\ ", " ").replace("\\%", "").replace("%", "")
    t = re.sub(r"\\text\{[^}]*\}", "", t)
    m = re.fullmatch(r"\s*\\d?frac\{(\d+)\}\{(\d+)\}\s*", t)
    if m:
        return Fr(int(m.group(1)), int(m.group(2)))
    return Fr(re.search(r"-?\d+(?:\.\d+)?", t.replace(" ", "")).group())


def croisement(p1, p2, recessif_lie_x=False):
    """Descendance d'un croisement d'un seul gene : liste de genotypes (tuples tries) equiprobables."""
    return [tuple(sorted((a, b))) for a, b in itertools.product(p1, p2)]


def attendues():
    E = {}
    s = F.SPIRO
    volume_courant = s["max"] - s["min"]
    E["h21"] = (nombre, volume_courant * (60 // (s["duree"] // s["respirations"])))
    E["h27"] = (nombre, dict(F.POULS)[0] - dict(F.POULS)[3])
    enfants = croisement("Bb", "Bb")
    E["h38"] = (nombre, Fr(sum(1 for g in enfants if g == ("B", "B")), len(enfants)) * 100)
    # filles du croisement X^c Y (pere) x X^C X^c (mere) : le pere donne X^c, la mere X^C ou X^c
    filles = [tuple(sorted((pere, mere))) for pere in ("Xc",) for mere in ("XC", "Xc")]
    E["h39"] = (nombre, Fr(sum(1 for g in filles if g == ("Xc", "Xc")), len(filles)) * 100)
    # parents sains avec un premier enfant atteint (hh) : ils sont tous deux heterozygotes ; parmi les enfants sains, part des porteurs
    assert F.ARBRE["parents"] == ("sain", "sain") and F.ARBRE["enfant1"] == "atteint" and F.ARBRE["enfant2"] == "sain"
    parents_possibles = [(a, b) for a in ("AA", "AS", "SS") for b in ("AA", "AS", "SS") if "SS" not in (a, b)]
    consistent = [p for p in parents_possibles if any(g == ("S", "S") for g in croisement(p[0], p[1]))]
    assert consistent == [("AS", "AS")], consistent  # seuls deux porteurs peuvent avoir un enfant atteint
    enf = croisement("AS", "AS")
    sains = [g for g in enf if g != ("S", "S")]
    porteurs = [g for g in sains if g == ("A", "S")]
    E["h40"] = (nombre, Fr(len(porteurs), len(sains)))
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
        egales = [ch["lettre"] for ch in q["choix"] if lire(ch["texte"]) == attendu]
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"{qid} (Q{q['numero']}): attendu {attendu!r}, cle {q['reponse_correcte']}, options egales {egales}")
    # structure de toutes les questions
    for q in qs:
        lettres = [c["lettre"] for c in q["choix"]]
        textes = [c["texte"] for c in q["choix"]]
        if lettres != list("abcd") or len(set(textes)) != 4:
            erreurs.append(f"Q{q['numero']}: options mal formees")
        m = re.search(r"\*\*Answer: ([A-D])\.\*\*", q["corrige_markdown"])
        if not m or m.group(1).lower() != q["reponse_correcte"]:
            erreurs.append(f"Q{q['numero']}: la lettre du corrige ne correspond pas a la cle")
    return erreurs, trouvees


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    print(f"{n} questions chiffrees recalculees sur {len(ep['exercices'][0]['questions'])}, {len(erreurs)} ecart(s). Les autres sont du rappel de cours, relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
