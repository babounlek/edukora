r"""Genere le blueprint et l'epreuve inedite GCE O Level Additional Mathematics Paper 2 n.2 (Section A : 8 questions, 66 points ;
Section C : 2 questions de Statistiques et Probabilites, 34 points).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_addmaths_p2n2.py [dossier_de_sortie]

Jumeau du Paper 1 n.2 (generer_addmaths_p1n2.py). Le vrai sujet donne : « Answer ALL questions in SECTION A and ANY TWO questions from EITHER SECTION B
(Mechanics) OR SECTION C (Statistics and Probability) » ; la plateforme ne code pas ce choix : l'inedite contient la Section A en entier et deux
questions de la Section C (le n.1 avait deux questions de la Section B), voir scripts/gce/INEDITES_GCE.md.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_s2  # noqa: E402
from questions_addmaths_p2n2_a import numero_affiche, sans_prefixe, section_a  # noqa: E402
from questions_addmaths_p2n2_c import section_c  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-addmaths-p2-2"
EP_ID = "ep-cm-gce-ol-addmaths-p2-2-2026-s1"
BP_P1 = "bp-cm-gce-ol-addmaths-p1-2"
TITRE = "Additional Mathematics GCE O Level Paper 2 \u2013 Original Paper No. 2"
INTRO_PAPER = (
    r"**Paper 2 (2 hours 30 minutes).** This paper has two sections. Answer ALL ten questions: the eight questions of Section A (Pure Mathematics, "
    r"66 marks) and the two questions of Section C (Statistics and Probability, 17 marks each). In the examination itself, candidates answer all of Section A and any two "
    r"questions from EITHER Section B (Mechanics) OR Section C (Statistics and Probability), never a mixture of B and C; this original paper contains "
    r"only Section A and Section C. The total is 100 marks. For your guidance, the mark for each part of a question is indicated. All necessary working must "
    r"be shown: no marks are awarded for answers without brief statements showing how the answers have been obtained. Non-programmable electronic "
    r"calculators and the mathematical formulae booklets published by the GCE Board are allowed."
)
TITRES_EXERCICES = {
    "1": "A cubic and the roots of a quadratic", "2": "Counting numbers and a binomial estimate", "3": "A bouncing ball",
    "4": "A group table and a matrix inverse", "5": "A tailor, linear inequalities and profit", "6": "A trigonometric equation and an identity",
    "7": "A line through two points and perpendicular vectors", "8": "Stationary points and a curve from its gradient",
    "9": "Grouped data and a cumulative frequency curve", "10": "A probability distribution and a binomial model",
}
LEGENDES = {"region_a5": "Solution: the region R", "cf": "Solution: cumulative frequency curve"}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_add_maths_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_addmaths_p1n2_a import questions as qa
    from questions_addmaths_p1n2_b import questions as qb
    out = []
    for q in qa() + qb():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    figs = figs_addmaths_s2.toutes()
    cours = titres_cours()
    exercices = section_a() + section_c()
    ex_json = []
    for e in exercices:
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER + ("\n\n" + intro if intro else "")
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            numero, groupe_local = numero_affiche(e["num"], s["num"])
            assert not s["fig_enonce"], "aucune figure d'enonce dans ce paper"
            enonce = sans_prefixe(s["text"])
            assert "{FIG}" not in enonce, (e["num"], s["num"])
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
            if s["fig"]:
                corrige += "\n\n" + figs[s["fig"]].replace("{FIG}", LEGENDES[s["fig"]])
            if s["ans"]:
                corrige += f"\n\n**Answer: {s['ans']}.**"
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            if s["conseil"]:
                corrige += f"\n\n### Conseil\n{s['conseil']}"
            questions.append({
                "numero": numero, "ordre": ordre, "enonce_markdown": enonce, "corrige_markdown": corrige,
                "difficulte_estimee": s["diff"], "type_reponse": "ouverte", "points": s["pts"],
                "criteres_notation": [{"libelle": lib, "points": p} for lib, p in s["crit"]],
                "themes": s["themes"], **({"groupe_local": groupe_local} if groupe_local else {}),
                "rappels_de_methode": [{
                    "id": f"rdi-{EP_ID}-ex{e['num']}-q{numero}-0", "competence": competence_du_rappel(s["themes"], cours),
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
            sp["support"] = "table d'une operation a completer"
        elif e["num"] == "5":
            sp["support"] = "region attendue dans le corrige"
        elif e["num"] == "9":
            sp["support"] = "tableau de frequences en enonce, courbe des effectifs cumules attendue dans le corrige"
        sections_plan.append(sp)
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Additional Mathematics", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 2,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2",
        },
        "format": {
            "section_a": "8 questions obligatoires de 7 a 10 points (66 points au total), comme les 7 vrais Paper 2 2019-2026 : polynomes et racines, denombrement et binome, suites geometriques, groupes et matrices, programmation lineaire, trigonometrie, vecteurs, calcul differentiel et integral",
            "section_c": "2 questions de Statistiques et Probabilites de 17 points (donnees groupees et courbe des effectifs cumules ; loi de probabilite et loi binomiale)",
            "reference": "Paper 2 reels 2019-2026 : 14 questions, Section A 8 questions (62 a 68 points), Section B 3 questions de 17 (Mecanique), Section C 3 questions de 17 (Statistiques et Probabilites), 100 points a traiter, 2 h 30",
            "regle_de_choix": "reelle : tout A + deux questions de B OU de C ; version answer ALL : tout A + deux questions de C (Statistiques et Probabilites), la regle reelle est rappelee dans l'introduction",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 2, "figures": "region des contraintes (question 5) et courbe des effectifs cumules (question 9) dans le corrige seulement ; aucune figure d'enonce",
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
