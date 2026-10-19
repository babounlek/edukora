r"""Genere le blueprint et l'epreuve inedite GCE O Level Physics Paper 2 n.1 (Section I : 6 questions, 40 points ; Section II : 3 questions, 60 points).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_physics_p2.py [dossier_de_sortie]

Jumeau du Paper 1 (generer_physics_p1.py). Le vrai sujet donne, en Section II, « EITHER a, b and c OR d, e and f » pour chaque question ; la plateforme
ne code pas ce choix : une seule des deux branches par question (version « answer ALL », voir scripts/gce/INEDITES_GCE.md).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_p2  # noqa: E402
from questions_physics_p2 import section_1, section_2  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-physics-p2-1"
EP_ID = "ep-cm-gce-ol-physics-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-physics-p1-1"
TITRE = "Physics GCE O Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    r"**Paper 2 (2 hours 30 minutes).** Answer ALL nine questions: the six questions of Section I and the three questions of Section II. "
    r"Section I carries 40 marks and Section II carries 60 marks. For your guidance, the approximate mark for each part of a question is "
    r"indicated. You are reminded of the necessity for good English and orderly presentation in your answers. In calculations, show all "
    r"the steps in your working, giving your answer at each stage. Where it is needed, take $g=10\ \text{m/s}^{2}$."
)
TITRES_EXERCICES = {
    "1": "Machines and efficiency", "2": "Moments and equilibrium", "3": "Static electricity and a circuit", "4": "Half-life",
    "5": "Refraction and critical angle", "6": "Echoes", "7": "Hooke's law, pressure and density",
    "8": "Specific heat capacity, heat transfer and latent heat", "9": "Transformers, induction and domestic electricity",
}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_physics_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_physics_p1 import questions
    out = []
    for q in questions():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    figs = figs_physics_p2.toutes()
    cours = titres_cours()
    exercices = section_1() + section_2()
    ex_json = []
    for e in exercices:
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            enonce = s["text"]
            if s["fig_enonce"]:
                enonce += "\n\n" + figs[s["fig_enonce"]] + "\n\n"
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
                "numero": s["num"], "ordre": ordre, "enonce_markdown": enonce, "corrige_markdown": corrige,
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
        sections_plan.append({
            "exercice": e["num"], "titre": TITRES_EXERCICES[e["num"]], "points": e["pts"], "groupes": [e["groupe"]],
            "nombre_questions": len(e["subs"]), "competences": comp, "difficulte": "moyenne",
            "support": "tableau de mesures" if e["num"] == "7" else ("circuit (figure 1)" if e["num"] == "3" else None),
        })
    sections_plan = [{k: v for k, v in sp.items() if v is not None} for sp in sections_plan]
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Physics", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2",
        },
        "format": {
            "section_1": "6 questions courtes (8, 7, 9, 5, 6, 5 points = 40), toutes obligatoires",
            "section_2": "3 questions de 20 points (60) : le vrai sujet donne EITHER a-b-c OR d-e-f ; une seule branche ici",
            "reference": "Paper 2 reels 2019-2026 : 100 points, 2 h 30, Section I a 6 questions, Section II a 3 questions",
            "regle_de_choix": "version answer ALL limitee a une branche par question de la Section II",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 2, "figures": "un circuit en enonce (question 3) ; le graphique de Hooke, trace attendu, dans le corrige (question 7)",
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
