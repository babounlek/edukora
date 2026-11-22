r"""Genere l'epreuve inedite GCE A Level ICT Paper 1 n.1 (50 QCM de 1 point, 90 min).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_ict_al_p1.py [dossier_de_sortie]

N'ecrit QUE l'epreuve ep-cm-gce-al-ict-p1-1-2026-s1 : le blueprint bp-cm-gce-al-ict-p1-1 existe deja (valide, ingere) et n'est pas touche.
50 questions a meilleure reponse, themes melanges comme les Paper 1 reels 2025-2026. Les cles sont placees par ce script (13/13/12/12, jamais trois cles
identiques de suite, graine fixe) ; chaque question porte un rappel de methode dont `competence` est le titre exact d'un Cours publie de la matiere quand
le theme en a un (releve en base le 2026-11-22), sinon le theme avec une majuscule.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_ict_al_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-ict-p1-1"
EP_ID = "ep-cm-gce-al-ict-p1-1-2026-s1"
TITRE = "ICT GCE A Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 (1 hour 30 minutes).** Multiple choice questions: answer ALL fifty questions. Each question carries 1 mark and the total is 50 marks. "
    "Each question has four suggested answers A, B, C and D: choose the one best answer. "
    "No marks are deducted for a wrong answer. Non-programmable electronic calculators are allowed. "
    "All the data needed to answer a question are given in the question itself."
)
# Cours publies (matiere GCE_ICT, statut VALIDE) releves en base : tag du theme -> titre exact du cours
COURS = {
    "computer hardware": "Computer Hardware: what the CPU, memory and storage do and how they limit speed",
    "input devices and data capture": "Input Devices and Data Capture: choosing the right device and checking what it reads",
    "data security and privacy": "Protecting Information: threats, security measures and the rights of data subjects",
    "information systems in organisations": "Information Systems at Work: components, types and the managers they serve",
    "ict system software": "System Software and Applications: what the operating system and utilities do for the user",
    "ict computer networks": "ICT Computer Networks: topologies, devices, media and what limits network speed",
    "ict number systems": "ICT Number Systems: binary, octal, hexadecimal, two's complement and units of time",
    "ict health and safety": "ICT Health and Safety: matching each health problem and hazard to the right preventive measure",
    "spreadsheet modelling": "Spreadsheet Modelling: writing formulas that stay correct when copied",
    "computer crime and malware": "Computer Crime and Malware: recognising the threat and defending a school network",
    "systems analysis and design": "Developing a New System: life cycle, fact finding, design and changeover",
    "e-commerce and e-services": "E-commerce and E-services: how online trade works and how to make it safe",
    "ict project management": "Managing an ICT Project: tasks, Gantt charts, PERT networks and the critical path",
}


def competence_du_rappel(themes):
    for t in themes:
        if t in COURS:
            return COURS[t]
    return themes[0].capitalize()


def placer_cles(n, graine=20261122):
    """Suite de n cles equilibree (13/13/12/12 pour 50), jamais trois cles identiques de suite."""
    rng = random.Random(graine)
    base = [l for l, k in zip(LETTRES, (13, 13, 12, 12)) for _ in range(k)] if n == 50 else None
    assert base and len(base) == n
    for _ in range(200000):
        cles = base[:]
        rng.shuffle(cles)
        if all(not (cles[i] == cles[i + 1] == cles[i + 2]) for i in range(n - 2)):
            return cles
    raise RuntimeError("aucune suite de cles valide")


def construire():
    qs = questions()
    assert len(qs) == 50, len(qs)
    cles = placer_cles(len(qs))
    rng = random.Random(7)
    questions_json = []
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        autres = [l for l in LETTRES if l != cle]
        dist = list(q["dist"])
        rng.shuffle(dist)
        options = [None] * 4
        options[LETTRES.index(cle)] = q["key"]
        reas = {}
        for l, (texte, raison) in zip(autres, dist):
            options[LETTRES.index(l)] = texte
            reas[l] = raison
        assert options[LETTRES.index(cle)] == q["key"], n
        assert len(set(options)) == 4, f"options en double (Q{n})"
        liste = "; ".join(f"option {l.upper()} {reas[l]}" for l in LETTRES if l in reas)
        corrige = (f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**\n\n"
                   f"### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {liste}.")
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(n), "ordre": n, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)], "reponse_correcte": cle, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{n}-0", "competence": competence_du_rappel(q["themes"]),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    return {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
            "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO, "questions": questions_json}]}


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    ep = construire()
    chemin = os.path.join(sortie, EP_ID + ".json")
    with open(chemin, "w", encoding="utf8", newline="\n") as fh:
        json.dump(ep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("ecrit", chemin)
    qj = ep["exercices"][0]["questions"]
    from collections import Counter
    print("questions", len(qj), "cles", dict(sorted(Counter(q["reponse_correcte"] for q in qj).items())),
          "difficultes", dict(Counter(q["difficulte_estimee"] for q in qj)))
    print("competences des rappels :", sorted({q["rappels_de_methode"][0]["competence"] for q in qj}))


if __name__ == "__main__":
    main()
