r"""Genere les DEUX epreuves inedites GCE A Level Pure Mathematics Paper 1 n.1 (50 QCM de 1 point, 90 min) : option Mechanics et option Statistics.

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_pm_p1.py [dossier_de_sortie]

Les vrais Paper 1 des deux options sont identiques : les 50 questions, leurs options et leurs cles (lettres placees ICI : 13/13/12/12, jamais trois de suite,
graine fixe) sont les memes ; seuls changent l'external_id, le titre, le blueprint et les ids de rappels. Les blueprints bp-cm-gce-al-pmmechanics-p1-1 et
bp-cm-gce-al-pmstatistics-p1-1 existent deja (valides, ingeres en local) : ce script n'ecrit que les deux epreuves.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_pm_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
LETTRES = "abcd"
INTRO_PAPER = (
    r"**Paper 1 (1 hour 30 minutes).** Multiple choice questions: choose the one correct answer, A, B, C or D, for each of the fifty questions. Each question carries 1 mark "
    r"and the total is 50 marks. No marks are deducted for a wrong answer. Non-programmable electronic calculators and the mathematical formulae booklets published by the GCE Board are allowed."
)
EPREUVES = [
    {"ep": "ep-cm-gce-al-pmmechanics-p1-1-2026-s1", "bp": "bp-cm-gce-al-pmmechanics-p1-1", "matiere": "Pure Mathematics with Mechanics", "cours": "GCE_PM_MECHANICS"},
    {"ep": "ep-cm-gce-al-pmstatistics-p1-1-2026-s1", "bp": "bp-cm-gce-al-pmstatistics-p1-1", "matiere": "Pure Mathematics with Statistics", "cours": "GCE_PM_STATISTICS"},
]

# tag -> titre exact du Cours VALIDE de la matiere (releve en base le 2026-11-21 ; un seul cours par tag)
COURS = {
    "GCE_PM_MECHANICS": {
        "asymptotes of rational functions": "Asymptotes of Rational Functions: vertical, horizontal, oblique and holes",
        "coefficient of restitution": "Coefficient of Restitution: impacts with walls and between spheres",
        "complex numbers": "Complex Numbers: Cartesian, polar and exponential form",
        "curve sketching": "Curve Sketching: building a sketch from intercepts, asymptotes and turning points",
        "de moivre theorem": "De Moivre's Theorem: powers, multiple angles and roots",
        "definite integrals": "Definite Integrals: areas between curves and volumes of revolution",
        "determinants and inverses": "Determinants and Inverses: cofactors, the adjugate and solving systems",
        "first order differential equations": "First Order Differential Equations: separating variables and using conditions",
        "inequalities and modulus": "Inequalities and Modulus: critical values, sign tables and distances",
        "integration of rational functions": "Integration of Rational Functions: partial fractions and logarithms",
        "limits and continuity": "Limits and Continuity: Evaluating Limits and Matching Pieces",
        "linear transformations": "Linear Transformations: matrices acting on points and lines",
        "lines and planes": "Lines and Planes in Three Dimensions: direction, normal and intersection",
        "matrix algebra": "Matrix Algebra: products, transposes, 3 by 3 inverses and linear systems",
        "parametric equations": "Parametric Equations: from parameter to Cartesian curve, and tangents",
        "partial fractions": "Partial Fractions: setting up the form and using it in integration",
        "properties of functions": "Properties of Functions: Parity, Composition and Bijections",
        "propositional logic": "Propositional Logic: implication, contrapositive and truth tables",
        "resultant and couple": "Resultant and Couple: Reducing a System of Coplanar Forces",
        "scalar and vector products": "Scalar and Vector Products: angles, lengths, normals and areas",
        "series summation": "Series Summation: Standard Sums, Induction and Geometric Series",
        "systems of forces": "Systems of Forces: resultant, moments and equilibrium",
        "vector geometry in three dimensions": "Vector Geometry in Three Dimensions: intersecting lines, normals and angles with planes",
        "vector moment of a force": "Vector Moment of a Force: Using the Vector Product in Two Dimensions",
        "work done by a force": "Work Done by a Force: scalar product, slopes and the work-energy principle",
    },
    "GCE_PM_STATISTICS": {
        "asymptotes of rational functions": "Rational Curves: finding vertical, horizontal and oblique asymptotes",
        "complex numbers": "Complex Numbers: Argand Diagram, Polar Form and Conjugate Roots",
        "curve sketching": "Curve Sketching: Rational Curves from Intercepts, Asymptotes and Gradient",
        "de moivre theorem": "De Moivre's Theorem: Powers, Multiple Angles and Roots of Complex Numbers",
        "definite integrals": "Definite Integrals: area, signed area and volumes of revolution",
        "determinants and inverses": "Determinants and Inverse Matrices: Cofactors, Adjugates and Linear Systems",
        "first order differential equations": "First Order Equations in One Pass: separating, integrating and fixing the constant",
        "inequalities and modulus": "Solving Inequalities and Modulus Problems: sign tables, squaring and checking",
        "integration of rational functions": "Rational Integrands: partial fractions turned into logarithms",
        "limits and continuity": "Limits and Continuity: Indeterminate Forms, Standard Limits and Piecewise Joins",
        "linear transformations": "Linear Transformations: Matrices, Images of Lines and Area Scale Factors",
        "lines and planes": "Lines and Planes in Space: Vector Equations, Intersections and Angles",
        "matrix algebra": "Matrix Algebra: Determinants, Cofactors and Solving Systems with an Inverse",
        "normal distribution": "Normal Distribution: Standardising, Tables and Unknown Parameters",
        "numerical integration": "Numerical Integration: the Trapezium Rule from Tables and Functions",
        "numerical methods": "Numerical Methods: Locating Roots, Newton-Raphson and Convergent Iterations",
        "parametric equations": "Curves from a Parameter: eliminating t, the range of the curve and the gradient",
        "partial fractions": "Partial Fractions: splitting a rational function into simple pieces",
        "probability density functions": "Probability Density Functions: Constants, Areas, Median, Mode and Expectation",
        "properties of functions": "Properties of Functions: Proving Injective, Surjective and Bijective",
        "propositional logic": "Logic of Statements: connectives, truth tables and the contrapositive",
        "scalar and vector products": "Scalar and Vector Products: angles, lengths, areas and normals",
        "series convergence": "Series Convergence: Geometric Series, Sums to Infinity and Ranges of Validity",
        "series summation": "Series Summation: Standard Sums, Changing Limits and Proof by Induction",
        "vector geometry in three dimensions": "Vector Geometry in Three Dimensions: lines, intersections and planes",
    },
}


def competence_du_rappel(themes, code):
    for t in themes:
        if t in COURS[code]:
            return COURS[code][t]
    return themes[0].capitalize()


def cles(n, graine=20261121):
    rnd = random.Random(graine)
    base = list("a" * 13 + "b" * 13 + "c" * 12 + "d" * 12)
    while True:
        rnd.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def construire(cfg):
    qs = questions()
    ks = cles(len(qs))
    ep_id = cfg["ep"]
    titre = f"{cfg['matiere']} GCE A Level Paper 1 \u2013 Original Paper No. 1"
    questions_json = []
    for i, (q, k) in enumerate(zip(qs, ks), start=1):
        autres = [c for c in LETTRES if c != k]
        options = {k: q["key"]}
        for c, (texte, _) in zip(autres, q["dist"]):
            options[c] = texte
        raisons = "; ".join(f"option {c.upper()} {r}" for c, (_, r) in zip(autres, q["dist"]))
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {k.upper()}.**\n\n### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {raisons}."
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(i), "ordre": i, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": c, "texte": options[c]} for c in LETTRES], "reponse_correcte": k, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{ep_id}-ex1-q{i}-0", "competence": competence_du_rappel(q["themes"], cfg["cours"]),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    return {
        "type": "epreuve", "external_id": ep_id, "titre": titre, "blueprint_external_id": cfg["bp"],
        "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO_PAPER, "questions": questions_json}],
    }


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    from collections import Counter
    for cfg in EPREUVES:
        ep = construire(cfg)
        chemin = os.path.join(sortie, cfg["ep"] + ".json")
        with open(chemin, "w", encoding="utf8", newline="\n") as fh:
            json.dump(ep, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        qs = ep["exercices"][0]["questions"]
        print("ecrit", chemin)
        print("questions", len(qs), "cles", dict(sorted(Counter(q["reponse_correcte"] for q in qs).items())))


if __name__ == "__main__":
    main()
