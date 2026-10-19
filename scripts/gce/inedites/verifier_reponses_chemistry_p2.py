r"""Recalcule INDEPENDAMMENT les reponses chiffrees du Paper 2 Chemistry inedit et verifie qu'elles figurent dans le corrige ecrit.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_chemistry_p2.py [ep-....json]

Les valeurs sont recalculees ici a partir des donnees de l'enonce (masses atomiques, lectures de burette, constantes des figures) ; chaque
valeur attendue doit apparaitre dans le corrige de la sous-question. Les barèmes sont deja verifies a la generation (somme exacte).
Sortie 1 au moindre ecart.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_chemistry_p2 as F  # noqa: E402

DEFAUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-chemistry-p2-1-2026-s1.json")
AR = {"H": 1, "B": 10.8, "C": 12, "O": 16, "Zn": 65, "Ca": 40, "Cu": 64}
VM = 24000.0
FARADAY = 96000.0


def sous_question(ep, ex, num):
    for e in ep["exercices"]:
        if e["numero_exercice"] == ex:
            for q in e["questions"]:
                if q["numero"] == num:
                    return q
    raise KeyError((ex, num))


def attendues():
    A = []  # (exercice, sous-question, [chaines attendues dans le corrige], description)
    # 1b : masse atomique relative du bore
    A.append(("1", "b", [f"{(20 * 10 + 80 * 11) / 100:g}"], "RAM du bore"))
    # 2d : 600 cm3 de H2 -> NH3 (rapport 3:2)
    A.append(("2", "d", [f"{600 * 2 / 3:g}"], "volume de NH3"))
    # 3c : electrolyse du cuivre, 2,0 A pendant 30 minutes
    q = 2.0 * 30 * 60
    mol_e = q / FARADAY
    m_cu = mol_e / 2 * AR["Cu"]
    A.append(("3", "c", [f"{q:g}", f"{mol_e:g}", f"{m_cu:g}"], "masse de cuivre"))
    # 5b/5c : titrage
    lectures = {"Rough": (0.00, 25.20), "1": (0.50, 25.10), "2": (0.20, 24.70), "3": (1.00, 25.70)}
    titres = {k: round(f - i, 2) for k, (i, f) in lectures.items()}
    concordants = [titres["1"], titres["2"], titres["3"]]
    assert max(concordants) - min(concordants) <= 0.20 + 1e-9, "titres non concordants"
    assert titres["Rough"] - max(concordants) > 0.20, "le titre approximatif doit s'ecarter des autres"
    moyenne = round(sum(concordants) / 3, 2)
    n = 0.100 * moyenne / 1000
    c = n / (25.0 / 1000)
    A.append(("5", "b", [f"{titres['Rough']:.2f}", f"{titres['1']:.2f}", f"{titres['2']:.2f}", f"{titres['3']:.2f}", f"{moyenne:.2f}"], "titres et moyenne"))
    A.append(("5", "c", ["2.46\\times10^{-3}", f"{c:.4f}".rstrip("0")], "concentration de KOH"))
    # 5e : le saut de pH de la figure doit encadrer la moyenne des titres
    pts = sorted(F.PH)
    saut = max(zip(pts, pts[1:]), key=lambda p: abs(p[1][1] - p[0][1]))
    assert saut[0][0] <= moyenne <= saut[1][0], f"le saut de pH {saut} n'encadre pas le titre moyen {moyenne}"
    assert dict(F.PH)[0] == 13.0
    p_fin = [p for v, p in F.PH if abs(v - moyenne) < 0.05]
    assert p_fin == [7.0], f"pH au point d'equivalence {p_fin}"
    A.append(("5", "e", ["13", "7", "24.6"], "lectures de la courbe de pH"))
    # 6d : carbonate de zinc
    m_zn_co3 = AR["Zn"] + AR["C"] + 3 * AR["O"]
    n_q = 6.25 / m_zn_co3
    m_zno = n_q * (AR["Zn"] + AR["O"])
    v_co2 = n_q * VM
    A.append(("6", "d", [f"{m_zn_co3:g}", f"{n_q:.3f}", f"{m_zno:.2f}", f"{v_co2:g}"], "decomposition de ZnCO3"))
    # 7b/7e : marbre et acide
    e1, e2 = dict(F.EXP1), dict(F.EXP2)
    final = e1[max(e1)]
    arret = min(t for t, v in e1.items() if v == final)
    taux = e1[40] / 40
    assert e2[max(e2)] == final, "les deux experiences doivent finir au meme volume"
    assert min(t for t, v in e2.items() if v == final) < arret, "la poudre doit finir avant les morceaux"
    assert all(e2[t] > e1[t] for t in (20, 40, 60)), "la poudre doit etre au-dessus des morceaux au debut"
    A.append(("7", "b", [f"{arret:g}", f"{taux:g}"], "arret et vitesse moyenne"))
    n_co2 = final / VM
    m_caco3 = n_co2 * (AR["Ca"] + AR["C"] + 3 * AR["O"])
    assert abs(m_caco3 - 0.50) < 1e-9, f"masse de marbre incoherente: {m_caco3}"
    n_hcl = 0.50 * 25.0 / 1000
    assert n_hcl > 2 * n_co2, "l'acide doit etre en exces"
    A.append(("7", "e", [f"{n_co2:.4f}", f"{m_caco3:.2f}", f"{n_hcl:.4f}", f"{2 * n_co2:.4f}"], "moles, masse, exces d'acide"))
    # 8d : combustion de l'ethene
    m_c2h4 = 2 * AR["C"] + 4 * AR["H"]
    n_e = 2.8 / m_c2h4
    A.append(("8", "d", [f"{n_e:.2f}", f"{3 * n_e * VM:g}", f"{2 * n_e * (AR['C'] + 2 * AR['O']):.1f}"], "combustion de l'ethene"))
    return A


def verifier(ep):
    erreurs = []
    n = 0
    for ex, num, textes, desc in attendues():
        q = sous_question(ep, ex, num)
        corr = q["corrige_markdown"]
        n += 1
        for t in textes:
            if t not in corr:
                erreurs.append(f"{ex}{num} ({desc}): la valeur recalculee '{t}' ne figure pas dans le corrige")
    return erreurs, n


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf8"))
    erreurs, n = verifier(ep)
    for e in erreurs:
        print("ERREUR", e)
    nq = sum(len(e["questions"]) for e in ep["exercices"])
    print(f"{n} sous-questions chiffrees recalculees sur {nq}, {len(erreurs)} ecart(s). Les autres sont du rappel de cours, relu a la main.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
