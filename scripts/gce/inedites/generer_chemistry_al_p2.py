r"""Genere l'epreuve inedite GCE A Level Chemistry Paper 2 n.1 (6 exercices obligatoires de 20 marks, 120 marks, 3 h).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_chemistry_al_p2.py [dossier_de_sortie]

Le blueprint bp-cm-gce-al-chemistry-p2-1 existe deja (valide par l'utilisateur, ingere en local) : ce script n'ecrit que l'epreuve.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_chemistry_al_p2  # noqa: E402
from questions_chemistry_al_p2 import exercices  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-chemistry-p2-1"
EP_ID = "ep-cm-gce-al-chemistry-p2-1-2026-s1"
TITRE = "Chemistry GCE A Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    r"**Paper 2 (3 hours).** Answer ALL six questions. The total is 120 marks. For your guidance, the mark for each part of a question is indicated. "
    r"All necessary working must be shown: no marks are awarded for answers without brief statements showing how the answers have been obtained. "
    r"The relative atomic masses and the other data needed are given in each question. Non-programmable electronic calculators are allowed."
)

# tag -> titre exact du Cours GCE Chemistry deja publie (statut VALIDE, interroge dans la base locale le 2026-11-21)
COURS = {
    "atomic structure": "Atomic structure: particles, electron shells, ions and isotopes",
    "mole concept": "Mole Concept: from grams to moles, volumes and concentrations",
    "stoichiometry": "Stoichiometry: moles, reacting masses and gas volumes",
    "enthalpy changes": "Enthalpy Changes: Definitions, Hess's Law and Born-Haber Cycles",
    "chemical equilibrium": "Chemical equilibrium: reversible reactions, Le Chatelier and industrial conditions",
    "chemical kinetics": "Chemical Kinetics: Rate Equations, Half-Lives and Catalysts",
    "rate equations": "Rate Equations: Orders, Rate Constants and Initial-Rate Analysis",
    "redox reactions": "Redox Reactions: electron transfer, half-equations and electrolysis",
    "oxidation states": "Oxidation States: Assigning, Balancing and Disproportionation",
    "electrode potentials": "Electrode Potentials: standard hydrogen electrode, cell emf and feasibility",
    "reaction mechanisms": "Reaction Mechanisms: Radicals, Electrophiles and Nucleophiles",
    "alcohols and carboxylic acids": "Alcohols and carboxylic acids: ethanol, ethanoic acid and esters",
    "aldehydes and ketones": "Aldehydes and Ketones: Carbonyl Reactions and Tests",
    "periodicity": "Periodicity: Trends Across Period 3 and Down Group 2",
    "Group IV elements": "Group IV Elements: Carbon to Lead, Oxides and Chlorides",
    "transition elements": "Transition Elements: Electrons, Complexes and Colour",
    "qualitative analysis": "Qualitative Analysis: flame tests and tests for ions and gases",
}


def competence_du_rappel(themes):
    for t in themes:
        if t in COURS:
            return COURS[t]
    return themes[0].capitalize()


def construire():
    figs = figs_chemistry_al_p2.toutes()
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
