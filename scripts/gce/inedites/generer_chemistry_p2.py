r"""Genere le blueprint et l'epreuve inedite GCE O Level Chemistry Paper 2 n.1 (Section A : 4 questions, 40 points ; Section B : 2 questions, 40 points ;
Section C : 2 questions, 40 points).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_chemistry_p2.py [dossier_de_sortie]

Jumeau du Paper 1 (generer_chemistry_p1.py). Le vrai sujet donne 5 questions en A (les 4 meilleures sont notees), 2 en B (obligatoires) et 3 en C
(deux a traiter) ; la plateforme ne code pas ces choix : l'inedite ne contient que les questions A TRAITER (version « answer ALL », voir
scripts/gce/INEDITES_GCE.md).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_chemistry_p2  # noqa: E402
from questions_chemistry_p2 import section_a, section_b, section_c  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-chemistry-p2-1"
EP_ID = "ep-cm-gce-ol-chemistry-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-chemistry-p1-1"
TITRE = "Chemistry GCE O Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    r"**Paper 2 (2 hours 30 minutes).** This paper has three sections. Answer ALL eight questions: the four questions of Section A (10 marks each), "
    r"the two questions of Section B (20 marks each) and the two questions of Section C (20 marks each). The total is 120 marks. In the examination "
    r"itself, Section A offers five questions of which the best four are graded, and Section C offers three questions of which two are answered; this "
    r"original paper contains only the questions to be answered. "
    r"Show all the steps in your calculations. Useful data: molar volume of a gas at r.t.p. $=24000\ \text{cm}^3$; $1$ mole of electrons carries "
    r"$96000\ \text{C}$. The relative atomic masses needed are given in the questions."
)
TITRES_EXERCICES = {
    "1": "Isotopes, relative atomic mass and the Periodic Table", "2": "The Haber process", "3": "Purification of copper by electrolysis",
    "4": "Bonding and structure", "5": "Titration, preparation of a salt and pH curve", "6": "Qualitative analysis of two solids and a gas",
    "7": "Rate of reaction of marble with acid", "8": "Ethene: reactions, polymerisation and combustion",
}
FIGS_PAR_EXERCICE = {"5": "ph", "7": "gaz2"}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_chemistry_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_chemistry_p1 import questions
    out = []
    for q in questions():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    figs = figs_chemistry_p2.toutes()
    cours = titres_cours()
    exercices = section_a() + section_b() + section_c()
    ex_json = []
    nfig = 0
    for e in exercices:
        nom_fig = None
        if any(s["fig_enonce"] for s in e["subs"]):
            nfig += 1
            nom_fig = f"Figure {nfig}"
        intro = e["intro"].replace("{FIG}", nom_fig or "{FIG}")
        if e["num"] == "1":
            intro = INTRO_PAPER + "\n\n" + intro
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            enonce = s["text"].replace("{FIG}", nom_fig or "{FIG}")
            if s["fig_enonce"]:
                enonce += "\n\n" + figs[s["fig_enonce"]].replace("{FIG}", nom_fig) + "\n\n"
            assert "{FIG}" not in enonce, (e["num"], s["num"])
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol'].replace('{FIG}', nom_fig or '{FIG}')}"
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
        sp = {"exercice": e["num"], "titre": TITRES_EXERCICES[e["num"]], "points": e["pts"], "groupes": [e["groupe"]],
              "nombre_questions": len(e["subs"]), "competences": comp, "difficulte": "moyenne"}
        if e["num"] == "4":
            sp["support"] = "tableau de proprietes de trois substances"
        elif e["num"] == "5":
            sp["support"] = "tableau de lectures de burette et courbe de pH (figure 1)"
        elif e["num"] == "6":
            sp["support"] = "tableau de tests et d'observations"
        elif e["num"] == "7":
            sp["support"] = "deux courbes de volume de gaz (figure 2)"
        sections_plan.append(sp)
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Chemistry", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2",
        },
        "format": {
            "section_a": "4 questions de 10 points (le vrai sujet en propose 5 et note les 4 meilleures), toutes a traiter ici",
            "section_b": "2 questions de 20 points, obligatoires comme dans le vrai sujet : une de manipulation (titrage) et une d'analyse qualitative",
            "section_c": "2 questions de 20 points (le vrai sujet en propose 3 et demande d'en traiter 2)",
            "reference": "Paper 2 reels 2019-2026 : 120 points a traiter (4 x 10 + 2 x 20 + 2 x 20), 2 h 30",
            "regle_de_choix": "version answer ALL limitee aux questions a traiter ; la regle reelle est rappelee dans l'introduction",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 2, "figures": "courbe de pH d'un titrage (question 5) et deux courbes de volume de gaz (question 7), toutes deux en enonce",
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
