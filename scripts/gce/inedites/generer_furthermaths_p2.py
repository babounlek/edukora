r"""Genere l'epreuve inedite GCE A Level Further Mathematics Paper 2 n.1 (10 exercices obligatoires, 100 marks, 3 h).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_furthermaths_p2.py [dossier_de_sortie]

Le blueprint bp-cm-gce-al-furthermaths-p2-1 existe deja (valide par l'utilisateur, ingere en local) : ce script n'ecrit que l'epreuve.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_furthermaths_p2  # noqa: E402
from questions_furthermaths_p2 import exercices  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-furthermaths-p2-1"
EP_ID = "ep-cm-gce-al-furthermaths-p2-1-2026-s1"
TITRE = "Further Mathematics GCE A Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    r"**Paper 2 (3 hours).** Answer ALL ten questions. The total is 100 marks. For your guidance, the mark for each part of a question is indicated. "
    r"All necessary working must be shown: no marks are awarded for answers without brief statements showing how the answers have been obtained. "
    r"Non-programmable electronic calculators and the mathematical formulae booklets published by the GCE Board are allowed."
)

# tag -> titre exact du Cours GCE A Level Further Mathematics deja publie (25 cours valides)
COURS = {
    "coefficient of restitution": "Coefficient of Restitution: impact laws for particles and walls",
    "complex numbers": "Complex Numbers: polar form, De Moivre and loci",
    "complex transformations": "Complex Transformations: Invariant points, inverses and images of loci",
    "compound pendulum": "Compound Pendulum: oscillations of a rigid body about a fixed axis",
    "conic sections": "Conic Sections: tangents, normals and polar forms",
    "curve sketching": "Curve Sketching: asymptotes, turning points and range",
    "definite integrals": "Definite Integrals: limits, symmetry, substitution and mean values",
    "first order differential equations": "First Order Differential Equations: Separating, Integrating Factors and Series Solutions",
    "group theory": "Group Theory: proving the axioms, reading tables and applying Lagrange",
    "hyperbolic functions": "Hyperbolic Functions: Identities, Inverses and Integrals",
    "limits and continuity": "Limits and Continuity: evaluating limits and repairing discontinuities",
    "modular arithmetic": "Modular Arithmetic: Remainders, power cycles and unit digits",
    "moments of inertia": "Moments of Inertia: integration, parallel axes and swinging bodies",
    "motion in a resisting medium": "Motion in a Resisting Medium: terminal speed and equations of motion",
    "numerical solution of differential equations": "Numerical Solution of Differential Equations: Euler, improved Euler and central differences",
    "oblique impact of smooth spheres": "Oblique Impact of Smooth Spheres: Line of centres, restitution and deflection",
    "partial fractions": "Partial Fractions: splitting rational functions for integration and series",
    "polar coordinates": "Polar Coordinates: Curves, Areas and Motion in Radial and Transverse Components",
    "probability distributions": "Probability Distributions: mass functions, expectation, binomial, Poisson and density models",
    "radial and transverse acceleration": "Radial and Transverse Acceleration: Components of motion in polar coordinates",
    "recurrence relations": "Recurrence Relations: from the rule to the closed form",
    "scalar and vector products": "Scalar and Vector Products: Angles, Components and Areas in Three Dimensions",
    "second order differential equations": "Second Order Differential Equations: Complementary Functions, Particular Integrals and Oscillations",
    "simple harmonic motion of a particle": "Simple Harmonic Motion of a Particle: From the equation to period, speed and timing",
    "systems of forces": "Systems of Forces: resultants, couples and equivalent systems",
}


def competence_du_rappel(themes):
    for t in themes:
        if t in COURS:
            return COURS[t]
    return themes[0].capitalize()


def construire():
    figs = figs_furthermaths_p2.toutes()
    ex_json = []
    for e in exercices():
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            numero = s["num"]
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
            if s["fig"]:
                corrige += "\n\n" + figs[s["fig"]]
            if s["ans"]:
                corrige += f"\n\n**Answer: {s['ans']}.**"
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            if s["conseil"]:
                corrige += f"\n\n### Conseil\n{s['conseil']}"
            questions.append({
                "numero": numero, "ordre": ordre, "enonce_markdown": s["text"], "corrige_markdown": corrige,
                "difficulte_estimee": s["diff"], "type_reponse": "ouverte", "points": s["pts"],
                "criteres_notation": [{"libelle": lib, "points": p} for lib, p in s["crit"]],
                "themes": s["themes"],
                "rappels_de_methode": [{
                    "id": f"rdi-{EP_ID}-ex{e['num']}-q{numero}-0", "competence": competence_du_rappel(s["themes"]),
                    "contenu_markdown": s["rappel"], "cours_genere": False, "cours_id": None,
                }],
            })
        ex_json.append({"numero_exercice": e["num"], "points": f"{e['pts']:g}", "groupes": [],
                        "enonce_intro_markdown": intro, "questions": questions})
    return {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID, "exercices": ex_json}


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    ep = construire()
    chemin = os.path.join(sortie, EP_ID + ".json")
    with open(chemin, "w", encoding="utf8", newline="\n") as fh:
        json.dump(ep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    nq = sum(len(e["questions"]) for e in ep["exercices"])
    total = sum(float(e["points"]) for e in ep["exercices"])
    print("ecrit", chemin)
    print("exercices", len(ep["exercices"]), "sous-questions", nq, "points", total)


if __name__ == "__main__":
    main()
