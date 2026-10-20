r"""Genere le blueprint et l'epreuve inedite GCE O Level Human Biology Paper 2 n.1 (Section A : 3 questions ; Section B : 2 questions ; 20 points chacune).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_humanbio_p2.py [dossier_de_sortie]

Jumeau du Paper 1 (generer_humanbio_p1.py). Le vrai sujet donne 5 questions en A et 4 en B et demande d'en traiter 3 puis 2 ; la plateforme ne code pas
ce choix : l'inedite ne contient que les questions A TRAITER (version « answer ALL », voir scripts/gce/INEDITES_GCE.md).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_humanbio_p2 import section_a, section_b  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-humanbio-p2-1"
EP_ID = "ep-cm-gce-ol-humanbio-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-humanbio-p1-1"
TITRE = "Human Biology GCE O Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    "**Paper 2 (2 hours 30 minutes).** This paper has two sections. Answer ALL five questions: the three questions of Section A and the two questions "
    "of Section B. All the questions carry equal marks (20 marks each) and the marks allocated to the parts of a question are indicated. In the "
    "examination itself, Section A offers five questions of which three are answered, and Section B offers four questions of which two are answered; "
    "this original paper contains only the questions to be answered. You are reminded of the necessity for good English and orderly presentation in "
    "your answers."
)
TITRES_EXERCICES = {
    "1": "The teeth and dental decay", "2": "Genetics and the ABO blood groups", "3": "Nutrition: vitamins and mineral salts",
    "4": "Refuse disposal", "5": "HIV and AIDS",
}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_human_biology_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_humanbio_p1 import questions
    out = []
    for q in questions():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    cours = titres_cours()
    exercices = section_a() + section_b()
    ex_json = []
    for e in exercices:
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            if s["conseil"]:
                corrige += f"\n\n### Conseil\n{s['conseil']}"
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
        if e["num"] == "1":
            sp["support"] = "schema d une dent molaire : forme « Draw OR Describe » du vrai sujet, corrige decrit ce que le dessin montre"
        elif e["num"] == "3":
            sp["support"] = "tableau a completer (6 nutriments)"
        sections_plan.append(sp)
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Human Biology", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2",
        },
        "format": {
            "section_a": "3 questions de 20 points (le vrai sujet en propose 5 et demande d'en traiter 3), chacune en trois parties a, b, c de 2 a 14 points imprimes",
            "section_b": "2 questions de 20 points (le vrai sujet en propose 4 et demande d'en traiter 2), sante publique et environnement",
            "reference": "Paper 2 reels 2019-2026 : 100 points a traiter (3 + 2 questions de 20), 2 h 30",
            "regle_de_choix": "version answer ALL limitee aux questions a traiter ; la regle reelle est rappelee dans l'introduction",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 0, "figures": "aucune : le dessin du vrai sujet (ici une dent molaire) est propose sous sa forme « Draw OR Describe » ; le corrige decrit ce que le dessin doit montrer",
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
