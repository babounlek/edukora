r"""Genere l'epreuve inedite GCE A Level Computer Science Paper 2 n.1 (8 exercices obligatoires de 17 marks, 136 marks, 2 h 30).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_cs_al_p2.py [dossier_de_sortie]

Le blueprint bp-cm-gce-al-computerscience-p2-1 existe deja (valide par l'utilisateur, ingere en local) : ce script n'ecrit que l'epreuve.
Aucune figure : les questions chiffrees portent leurs donnees en tableaux ou en blocs de code.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_cs_al_p2 import exercices  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-computerscience-p2-1"
EP_ID = "ep-cm-gce-al-computerscience-p2-1-2026-s1"
TITRE = "Computer Science GCE A Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    r"**Paper 2 (2 hours 30 minutes).** Answer ALL eight questions. The total is 136 marks. All questions carry 17 marks each. For your guidance, the approximate mark for each part of a question is indicated. "
    r"You are reminded of the necessity for good English and orderly presentation in your answers. In calculations, you are advised to show all the steps in your working, giving your answer at each stage."
)

# tag -> titre exact du Cours GCE Computer Science deja publie (statut VALIDE, interroge dans la base locale le 2026-11-22)
COURS = {
    "binary number representation": "Binary Number Representation: integers, fixed point and floating point",
    "processor instruction sets": "Processor Instruction Sets: instruction formats, addressing modes and RISC versus CISC",
    "deadlock": "Deadlock: conditions, graphs, prevention, avoidance and recovery",
    "memory management": "Memory Management: addresses, paging, segmentation and virtual memory",
    "process scheduling": "Process Scheduling: FCFS, SJF, priority and round robin on a CPU",
    "software engineering": "Software Engineering: life cycle, design tools and program errors",
}


def competence_du_rappel(themes):
    for t in themes:
        if t in COURS:
            return COURS[t]
    return themes[0].capitalize()


def construire():
    ex_json = []
    for e in exercices():
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            numero = s["num"]
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
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
