r"""Genere les DEUX epreuves inedites GCE A Level Pure Mathematics Paper 2 n.1 (10 exercices obligatoires, 100 marks, 3 h) a partir des memes questions :

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_pm_p2.py [dossier_de_sortie]

  - ep-cm-gce-al-pmmechanics-p2-1-2026-s1  (blueprint bp-cm-gce-al-pmmechanics-p2-1)  : Pure Mathematics with Mechanics ;
  - ep-cm-gce-al-pmstatistics-p2-1-2026-s1 (blueprint bp-cm-gce-al-pmstatistics-p2-1) : Pure Mathematics with Statistics.

Les vrais Paper 2 des deux options sont identiques ; une epreuve n'ayant qu'une matiere, le contenu est ingere deux fois sous deux external_id
(ids de rappels propres a chaque epreuve). Les blueprints existent deja (valides, ingeres en local) : ce script n'ecrit que les epreuves.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_pm_p2  # noqa: E402
from questions_pm_p2 import exercices  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
INTRO_PAPER = (
    r"**Paper 2 (3 hours).** Answer ALL ten questions. The total is 100 marks. For your guidance, the mark for each part of a question is indicated. "
    r"All necessary working must be shown: no marks are awarded for answers without brief statements showing how the answers have been obtained. "
    r"Non-programmable electronic calculators and the mathematical formulae booklets published by the GCE Board are allowed."
)

# tag -> titre exact du Cours VALIDE de la matiere (releve en base locale le 2026-11-21)
GCE_PM_MECHANICS_COURS = {
    'asymptotes of rational functions': 'Asymptotes of Rational Functions: vertical, horizontal, oblique and holes',
    'coefficient of restitution': 'Coefficient of Restitution: impacts with walls and between spheres',
    'complex numbers': 'Complex Numbers: Cartesian, polar and exponential form',
    'curve sketching': 'Curve Sketching: building a sketch from intercepts, asymptotes and turning points',
    'de moivre theorem': "De Moivre's Theorem: powers, multiple angles and roots",
    'definite integrals': 'Definite Integrals: areas between curves and volumes of revolution',
    'determinants and inverses': 'Determinants and Inverses: cofactors, the adjugate and solving systems',
    'first order differential equations': 'First Order Differential Equations: separating variables and using conditions',
    'inequalities and modulus': 'Inequalities and Modulus: critical values, sign tables and distances',
    'integration of rational functions': 'Integration of Rational Functions: partial fractions and logarithms',
    'limits and continuity': 'Limits and Continuity: Evaluating Limits and Matching Pieces',
    'linear transformations': 'Linear Transformations: matrices acting on points and lines',
    'lines and planes': 'Lines and Planes in Three Dimensions: direction, normal and intersection',
    'matrix algebra': 'Matrix Algebra: products, transposes, 3 by 3 inverses and linear systems',
    'parametric equations': 'Parametric Equations: from parameter to Cartesian curve, and tangents',
    'partial fractions': 'Partial Fractions: setting up the form and using it in integration',
    'properties of functions': 'Properties of Functions: Parity, Composition and Bijections',
    'propositional logic': 'Propositional Logic: implication, contrapositive and truth tables',
    'resultant and couple': 'Resultant and Couple: Reducing a System of Coplanar Forces',
    'scalar and vector products': 'Scalar and Vector Products: angles, lengths, normals and areas',
    'series summation': 'Series Summation: Standard Sums, Induction and Geometric Series',
    'systems of forces': 'Systems of Forces: resultant, moments and equilibrium',
    'vector geometry in three dimensions': 'Vector Geometry in Three Dimensions: intersecting lines, normals and angles with planes',
    'vector moment of a force': 'Vector Moment of a Force: Using the Vector Product in Two Dimensions',
    'work done by a force': 'Work Done by a Force: scalar product, slopes and the work-energy principle',
}
GCE_PM_STATISTICS_COURS = {
    'asymptotes of rational functions': 'Rational Curves: finding vertical, horizontal and oblique asymptotes',
    'complex numbers': 'Complex Numbers: Argand Diagram, Polar Form and Conjugate Roots',
    'curve sketching': 'Curve Sketching: Rational Curves from Intercepts, Asymptotes and Gradient',
    'de moivre theorem': "De Moivre's Theorem: Powers, Multiple Angles and Roots of Complex Numbers",
    'definite integrals': 'Definite Integrals: area, signed area and volumes of revolution',
    'determinants and inverses': 'Determinants and Inverse Matrices: Cofactors, Adjugates and Linear Systems',
    'first order differential equations': 'First Order Equations in One Pass: separating, integrating and fixing the constant',
    'inequalities and modulus': 'Solving Inequalities and Modulus Problems: sign tables, squaring and checking',
    'integration of rational functions': 'Rational Integrands: partial fractions turned into logarithms',
    'limits and continuity': 'Limits and Continuity: Indeterminate Forms, Standard Limits and Piecewise Joins',
    'linear transformations': 'Linear Transformations: Matrices, Images of Lines and Area Scale Factors',
    'lines and planes': 'Lines and Planes in Space: Vector Equations, Intersections and Angles',
    'matrix algebra': 'Matrix Algebra: Determinants, Cofactors and Solving Systems with an Inverse',
    'normal distribution': 'Normal Distribution: Standardising, Tables and Unknown Parameters',
    'numerical integration': 'Numerical Integration: the Trapezium Rule from Tables and Functions',
    'numerical methods': 'Numerical Methods: Locating Roots, Newton-Raphson and Convergent Iterations',
    'parametric equations': 'Curves from a Parameter: eliminating t, the range of the curve and the gradient',
    'partial fractions': 'Partial Fractions: splitting a rational function into simple pieces',
    'probability density functions': 'Probability Density Functions: Constants, Areas, Median, Mode and Expectation',
    'properties of functions': 'Properties of Functions: Proving Injective, Surjective and Bijective',
    'propositional logic': 'Logic of Statements: connectives, truth tables and the contrapositive',
    'scalar and vector products': 'Scalar and Vector Products: angles, lengths, areas and normals',
    'series convergence': 'Series Convergence: Geometric Series, Sums to Infinity and Ranges of Validity',
    'series summation': 'Series Summation: Standard Sums, Changing Limits and Proof by Induction',
    'vector geometry in three dimensions': 'Vector Geometry in Three Dimensions: lines, intersections and planes',
}

EPREUVES = [
    dict(ep_id="ep-cm-gce-al-pmmechanics-p2-1-2026-s1", bp_id="bp-cm-gce-al-pmmechanics-p2-1",
         titre="Pure Mathematics with Mechanics GCE A Level Paper 2 \u2013 Original Paper No. 1", cours=GCE_PM_MECHANICS_COURS),
    dict(ep_id="ep-cm-gce-al-pmstatistics-p2-1-2026-s1", bp_id="bp-cm-gce-al-pmstatistics-p2-1",
         titre="Pure Mathematics with Statistics GCE A Level Paper 2 \u2013 Original Paper No. 1", cours=GCE_PM_STATISTICS_COURS),
]


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire(cfg):
    figs = figs_pm_p2.toutes()
    ep_id = cfg["ep_id"]
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
                    "id": f"rdi-{ep_id}-ex{e['num']}-q{numero}-0", "competence": competence_du_rappel(s["themes"], cfg["cours"]),
                    "contenu_markdown": s["rappel"], "cours_genere": False, "cours_id": None,
                }],
            })
        ex_json.append({"numero_exercice": e["num"], "points": f"{e['pts']:g}", "groupes": [],
                        "enonce_intro_markdown": intro, "questions": questions})
    return {"type": "epreuve", "external_id": ep_id, "titre": cfg["titre"], "blueprint_external_id": cfg["bp_id"], "exercices": ex_json}


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    for cfg in EPREUVES:
        ep = construire(cfg)
        chemin = os.path.join(sortie, cfg["ep_id"] + ".json")
        with open(chemin, "w", encoding="utf8", newline="\n") as fh:
            json.dump(ep, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        nq = sum(len(e["questions"]) for e in ep["exercices"])
        total = sum(float(e["points"]) for e in ep["exercices"])
        print("ecrit", chemin)
        print("exercices", len(ep["exercices"]), "sous-questions", nq, "points", total)


if __name__ == "__main__":
    main()
