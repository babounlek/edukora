r"""Genere l'epreuve inedite GCE A Level Physics Paper 1 n.1 (50 QCM de 1 point, 90 min), compatible avec le blueprint DEJA VALIDE bp-cm-gce-al-physics-p1-1.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_physics_al_p1.py [dossier_de_sortie]

N'ecrit QUE l'epreuve : le blueprint existant n'est ni regenere ni ecrase (il est seulement relu pour verifier que chaque theme des questions en fait partie).
Les lettres des cles sont placees ICI (equilibre 13/13/12/12, jamais trois cles identiques de suite, graine fixe), jamais tapees dans les questions.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_al_p1  # noqa: E402
from questions_physics_al_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-physics-p1-1"
EP_ID = "ep-cm-gce-al-physics-p1-1-2026-s1"
TITRE = "Physics GCE A Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO_PAPER = (
    r"**Paper 1 (1 hour 30 minutes).** Multiple choice questions: choose the one best answer, A, B, C or D, for each of the fifty questions. Each question carries 1 mark "
    r"and the total is 50 marks. No marks are deducted for a wrong answer. Non-programmable electronic calculators are allowed. Where a question needs a physical constant "
    r"or the value of $g$, the question itself gives it."
)

# theme (nom de Tag du blueprint) -> titre EXACT du Cours GCE_PHYSICS VALIDE qui porte ce tag (releve en base locale le 2026-11-21)
COURS = {
    "physical quantities and units": "Physical Quantities and Units: Base Units, Homogeneity and Its Limits",
    "dimensional analysis": "Dimensional analysis: homogeneity, units and deriving formulae",
    "motion": "Motion: velocity, acceleration and the equations of motion",
    "newton's laws of motion": "Newton's Laws of Motion: Force, Momentum and Impulse",
    "work energy and power": "Work, energy and power: calculations, efficiency and energy sources",
    "circular motion": "Circular Motion: Centripetal Force, Banked Tracks and Orbits",
    "simple harmonic motion": "Simple harmonic motion: equations, energy and resonance",
    "gravitational fields": "Gravitational Fields: Field Strength, Potential, Orbits and Escape Speed",
    "thermal physics": "Thermal physics: heat, specific heat capacity and changes of state",
    "kinetic theory of gases": "Kinetic theory of gases: from molecules to pressure and temperature",
    "specific heat capacity": "Specific heat capacity: Q = mc(delta theta), heaters and mixtures",
    "waves": "Waves: properties, wave types and the wave equation",
    "interference of waves": "Interference of Waves: Coherence, Path Difference and Gratings",
    "electric fields": "Electric Fields: Forces, Field Strength, Potential and Charged Particles",
    "capacitors": "Capacitors: charge, energy and exponential discharge",
    "current electricity": "Current electricity: charge, current, potential difference and resistance",
    "electric circuits": "Electric circuits: series, parallel and combined resistors",
    "electromagnetic induction": "Electromagnetic induction: from moving magnets to transformers",
    "alternating current": "Alternating Current: R.M.S. Values, Reactance and Impedance",
    "transformers": "Transformers: turns ratio, efficiency and power transmission",
    "photoelectric effect": "Photoelectric effect: photons, work function and stopping potential",
    "radioactive decay": "Radioactive decay: radiations, balanced equations and half-life",
    "electronics and semiconductors": "Semiconductors and electronics: doping, diodes and sensors",
}


def competence_du_rappel(themes):
    for t in themes:
        if t in COURS:
            return COURS[t]
    return themes[0].capitalize()


def cles(n, graine=20261121):
    rnd = random.Random(graine)
    base = list("a" * 13 + "b" * 13 + "c" * 12 + "d" * 12)
    while True:
        rnd.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def construire():
    qs = questions()
    assert len(qs) == 50, len(qs)
    with open(os.path.join(SORTIE, BP_ID + ".json"), encoding="utf8") as fh:
        bp = json.load(fh)
    permis = set(bp["competences"])
    figs = figs_physics_al_p1.toutes()
    ks = cles(len(qs))
    rng = random.Random(11)
    questions_json = []
    nfig = 0
    for i, (q, k) in enumerate(zip(qs, ks), start=1):
        for t in q["themes"]:
            assert t in permis, f"theme hors blueprint : {t}"
        autres = [c for c in LETTRES if c != k]
        dist = list(q["dist"])
        rng.shuffle(dist)  # l'ordre des distracteurs ne suit pas celui du fichier
        options = {k: q["key"]}
        for c, (texte, _) in zip(autres, dist):
            options[c] = texte
        raisons = "; ".join(f"option {c.upper()} {r}" for c, (_, r) in zip(autres, dist))
        enonce = q["stem"]
        if q["fig"]:
            nfig += 1
            nom = f"Figure {nfig}"
            enonce = enonce.replace("{FIG}", nom) + "\n\n" + figs[q["fig"]].replace("{FIG}", nom) + "\n\n"
        assert "{FIG}" not in enonce
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {k.upper()}.**\n\n### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {raisons}."
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(i), "ordre": i, "enonce_markdown": enonce, "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": c, "texte": options[c]} for c in LETTRES], "reponse_correcte": k, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{i}-0", "competence": competence_du_rappel(q["themes"]),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    epreuve = {
        "type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
        "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO_PAPER, "questions": questions_json}],
    }
    return epreuve, nfig


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    ep, nfig = construire()
    chemin = os.path.join(sortie, EP_ID + ".json")
    with open(chemin, "w", encoding="utf8", newline="\n") as fh:
        json.dump(ep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("ecrit", chemin)
    from collections import Counter
    qs = ep["exercices"][0]["questions"]
    print("questions", len(qs), "cles", dict(sorted(Counter(q["reponse_correcte"] for q in qs).items())),
          "difficultes", dict(Counter(q["difficulte_estimee"] for q in qs)), "figures", nfig)
    print("enonces en point d'interrogation", sum(1 for q in qs if q["enonce_markdown"].split("\n\n")[0].rstrip().endswith("?")))


if __name__ == "__main__":
    main()
