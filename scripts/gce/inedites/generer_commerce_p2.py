r"""Genere le blueprint et l'epreuve inedite GCE O Level Commerce Paper 2 n.1 (4 questions de 20 points = 80 points).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_commerce_p2.py [dossier_de_sortie]

Jumeau du Paper 1 (generer_commerce_p1.py). Le vrai sujet donne : « Answer FOUR questions. All questions carry equal marks » parmi SIX questions de 20 points
(parties a, b, c) ; la plateforme ne code pas ce choix : l'inedite contient QUATRE questions (version « answer ALL », voir scripts/gce/INEDITES_GCE.md).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_commerce_p2 import section  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-commerce-p2-1"
EP_ID = "ep-cm-gce-ol-commerce-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-commerce-p1-1"
TITRE = "Commerce GCE O Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    "**Paper 2 (2 hours 30 minutes).** In the examination itself, candidates answer FOUR questions out of the six printed; all questions carry equal marks. "
    "This original paper contains four questions: answer ALL of them. Each question is worth 20 marks, so the total is 80 marks. "
    "You are reminded of the necessity for good English and orderly presentation in your answers. The use of SIMPLE electronic calculators is allowed. "
    "Show clearly all working in your answer booklet where necessary. For your guidance, the mark for each part of a question is indicated."
)
TITRES_EXERCICES = {
    "1": "Insurance: principles, advantages and uninsurable risks", "2": "Commercial banks: services, payment instructions and a loan",
    "3": "Foreign trade: import restrictions, balance of payments and containers", "4": "Sales promotion, advertising and consumer protection",
}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_commerce_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_commerce_p1 import questions
    out = []
    for q in questions():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    cours = titres_cours()
    exercices = section()
    ex_json = []
    for e in exercices:
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
            if s["ans"]:
                corrige += f"\n\n**Answer: {s['ans']}.**"
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            questions.append({
                "numero": s["num"], "ordre": ordre, "enonce_markdown": s["text"], "corrige_markdown": corrige,
                "difficulte_estimee": s["diff"], "type_reponse": "ouverte", "points": s["pts"],
                "criteres_notation": [{"libelle": lib, "points": p} for lib, p in s["crit"]],
                "themes": s["themes"],
                "rappels_de_methode": [{
                    "id": f"rdi-{EP_ID}-ex{e['num']}-q{s['num']}-0", "competence": competence_du_rappel(s["themes"], cours),
                    "contenu_markdown": s["rappel"], "cours_genere": False, "cours_id": None,
                }],
            })
        ex_json.append({"numero_exercice": e["num"], "points": f"{e['pts']:g}", "groupes": [e["groupe"]],
                        "enonce_intro_markdown": intro, "questions": questions})
    competences, sections_plan = [], []
    for e in exercices:
        comp = []
        for s in e["subs"]:
            for t in s["themes"]:
                if t not in comp:
                    comp.append(t)
                if t not in competences:
                    competences.append(t)
        sp = {"exercice": e["num"], "titre": TITRES_EXERCICES[e["num"]], "points": e["pts"], "groupes": [e["groupe"]],
              "nombre_questions": len(e["subs"]), "competences": comp, "difficulte": "moyenne"}
        if e["num"] == "2":
            sp["support"] = "calcul d'interet simple en quatre temps"
        elif e["num"] == "3":
            sp["support"] = "tableau du commerce exterieur d'un pays (balance commerciale et balance des paiements courants)"
        sections_plan.append(sp)
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Commerce", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte ni aucun fait partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2",
        },
        "format": {
            "structure": "4 questions de 20 points, chacune en trois parties a, b, c de 4 a 8 points (« State and explain any FOUR... », « Outline THREE... », « Distinguish between... », un calcul commercial), comme les 48 questions des 8 vrais Paper 2 2019-2026",
            "reference": "Paper 2 reels 2019-2026 : 6 questions de 20 points, parties de 4 a 12 points, « Answer FOUR questions. All questions carry equal marks », 2 h 30, calculatrice simple permise",
            "regle_de_choix": "reelle : 4 questions sur 6 ; version answer ALL : 4 questions (80 points), la regle reelle est rappelee dans l'introduction",
            "corrige": "reponse modele complete : introduction, points numerotes en gras avec explication, exemples, remarque entre parentheses pour les reponses equivalentes",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 0, "figures": "aucune ; un tableau Markdown dans l'enonce de la question 3(b)",
    }
    epreuve = {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID, "exercices": ex_json}
    return blueprint, epreuve


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    bp, ep = construire()
    for nom, obj in ((BP_ID, bp), (EP_ID, ep)):
        chemin = os.path.join(sortie, nom + ".json")
        with open(chemin, "w", encoding="utf8", newline="\n") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("ecrit", chemin)
    nq = sum(len(e["questions"]) for e in ep["exercices"])
    print("exercices", len(ep["exercices"]), "sous-questions", nq, "points", bp["bareme_total"], "difficultes", bp["repartition_difficulte"])
    print("themes communs avec P1:", bp["session"]["themes_communs_aux_deux_papers"])
    print("themes propres au P2:", bp["session"]["themes_propres_au_paper_2"])


if __name__ == "__main__":
    main()
