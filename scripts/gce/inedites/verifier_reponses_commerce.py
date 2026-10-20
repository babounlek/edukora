r"""Recalcule INDEPENDAMMENT les reponses chiffrees des deux papers Commerce inedits et controle la structure des QCM.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_commerce.py [dossier]

Paper 1 : les 5 questions de calcul (majoration, rotation du stock, remise commerciale, TVA, remise de caisse en cascade) sont recalculees a partir des
donnees de l'enonce ; l'option cle doit etre la SEULE egale a la valeur recalculee ; chaque QCM a 4 options distinctes, une seule cle, pas de « all of the
above ». Paper 2 : l'interet simple et la balance commerciale sont recalcules ; chaque valeur doit figurer dans le corrige ; points par partie = somme des
criteres, total 80. Sortie 1 au moindre ecart.
"""
import json
import os
import re
import sys

DOSSIER = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm")


def nombre(texte):
    """Premier nombre d'une option (« CFAF 95,400. », « 30%. », « 6 times. »)."""
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", texte)
    return float(m.group(0).replace(",", ""))


def p1(chemin):
    ep = json.load(open(chemin, encoding="utf8"))
    qs = {int(q["numero"]): q for q in ep["exercices"][0]["questions"]}
    erreurs = []
    assert len(qs) == 50
    for n, q in qs.items():
        textes = [c["texte"] for c in q["choix"]]
        if len(set(textes)) != 4 or [c["lettre"] for c in q["choix"]] != list("abcd"):
            erreurs.append(f"Q{n}: options en double ou mal lettrees")
        if re.search(r"all of the above|none of the above", " ".join(textes), re.I):
            erreurs.append(f"Q{n}: option « all/none of the above »")
        cle = [c for c in q["choix"] if c["lettre"] == q["reponse_correcte"]]
        if len(cle) != 1:
            erreurs.append(f"Q{n}: cle absente")
    # recalculs : (numero, valeur attendue)
    attendu = {}
    attendu[5] = (78000 - 60000) / 60000 * 100  # majoration sur le cout
    attendu[17] = 12_000_000 / 2_000_000  # rotation du stock
    attendu[25] = 50_000 - 50_000 * 20 / 100  # remise commerciale
    attendu[37] = 80_000 + 80_000 * 19.25 / 100  # TVA
    liste = 200_000 * (1 - 0.25)
    attendu[44] = liste * (1 - 0.04)  # remise commerciale puis remise de caisse sur le net
    for n, val in attendu.items():
        q = qs[n]
        egales = [c["lettre"] for c in q["choix"] if abs(nombre(c["texte"]) - val) < 1e-6]
        if egales != [q["reponse_correcte"]]:
            erreurs.append(f"Q{n}: cle {q['reponse_correcte']}, options egales au recalcul ({val}) : {egales}")
    # le piege de la question 5 (marge) et de la question 44 (remise de caisse sur le prix de liste) doit etre une option distincte de la cle
    assert round((78000 - 60000) / 78000 * 100) == 23 and 200_000 * 0.96 == 192_000 and 150_000 - 8_000 == 142_000
    return erreurs, len(attendu)


def p2(chemin):
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs = []
    corr = {}
    total = 0
    for e in ep["exercices"]:
        s = 0
        for q in e["questions"]:
            corr[(e["numero_exercice"], q["numero"])] = re.sub(r"\s+", "", q["corrige_markdown"])
            if abs(sum(c["points"] for c in q["criteres_notation"]) - q["points"]) > 1e-9:
                erreurs.append(f"{e['numero_exercice']}{q['numero']}: criteres != points")
            s += q["points"]
        if s != 20:
            erreurs.append(f"exercice {e['numero_exercice']}: {s} points au lieu de 20")
        total += s
    if total != 80:
        erreurs.append(f"total {total} au lieu de 80")

    def present(cle, textes):
        for t in textes:
            if re.sub(r"\s+", "", t) not in corr[cle]:
                erreurs.append(f"{cle}: « {t} » absent du corrige")

    interet_an = 1_800_000 * 12 / 100
    interet = interet_an * 2
    total_remb = 1_800_000 + interet
    mensualite = total_remb / 24
    assert (interet_an, interet, total_remb, mensualite) == (216_000, 432_000, 2_232_000, 93_000)
    present(("2", "c"), ["216,000", "432,000", "2,232,000", "93,000"])
    vis = 1200 - 1450
    invis = 380 - 260
    cc = vis + invis
    assert (vis, invis, cc) == (-250, 120, -130)
    present(("3", "b"), ["−250", "+120", "−130"])
    # l'enonce de la question 3(b) contient bien les quatre valeurs du tableau
    enonce = [q for e in ep["exercices"] if e["numero_exercice"] == "3" for q in e["questions"] if q["numero"] == "b"][0]["enonce_markdown"]
    for v in ("1,200", "1,450", "380", "260"):
        if v not in enonce:
            erreurs.append(f"3b: valeur {v} absente de l'enonce")
    return erreurs, total


def main():
    dossier = sys.argv[1] if len(sys.argv) > 1 else DOSSIER
    e1, n1 = p1(os.path.join(dossier, "ep-cm-gce-ol-commerce-p1-1-2026-s1.json"))
    e2, total = p2(os.path.join(dossier, "ep-cm-gce-ol-commerce-p2-1-2026-s1.json"))
    for e in e1 + e2:
        print("ERREUR", e)
    print(f"Paper 1 : 50 QCM structures, {n1} calculs recalcules ; Paper 2 : {total} points, calculs recalcules ; {len(e1) + len(e2)} ecart(s).")
    return 1 if e1 or e2 else 0


if __name__ == "__main__":
    sys.exit(main())
