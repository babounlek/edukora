"""Genere le blueprint et l'epreuve inedite GCE O Level Mathematics Paper 2 n.1 (Section A 10 questions, Section B 4 questions).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_maths_p2.py [dossier_de_sortie]

Sortie par defaut : backend/ingest/_inedit/cm/ (bp-cm-gce-ol-maths-p2-1.json, ep-cm-gce-ol-maths-p2-1-2026-s1.json).
Jumeau du Paper 1 (generer_maths_p1.py) : meme matiere, meme cursus, meme numero de session (« Original Paper No. 1 »).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_maths_p2  # noqa: E402
from questions_maths_p2_a import section_a  # noqa: E402
from questions_maths_p2_b import section_b  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-maths-p2-1"
EP_ID = "ep-cm-gce-ol-maths-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-maths-p1-1"
TITRE = "Mathematics GCE O Level Paper 2 \u2013 Original Paper No. 1"

INTRO_PAPER = (
    "**Paper 2 (2 hours 30 minutes).** This paper is arranged in two sections, A and B. Section A: answer ALL ten "
    "questions; the marks for each question are shown. Section B: answer ALL FOUR questions; each question in "
    "Section B carries 15 marks. You are reminded of the necessity for good English and orderly presentation in your "
    "answers. In calculations, show all the steps in your working. Calculators are allowed."
)

TITRES_EXERCICES = {
    "1": "Fractions", "2": "Indices", "3": "Change of subject", "4": "Sets", "5": "Matrices", "6": "Networks",
    "7": "Vectors", "8": "Simultaneous equations", "9": "Inequalities", "10": "Probability",
    "B1": "Consumer arithmetic, percentages and ratio", "B2": "Statistics, sets and probability",
    "B3": "Functions, sequences and construction", "B4": "Quadratic graph and quadratic equation",
}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_maths_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    """Themes de l'epreuve jumelle (Paper 1) : sert au plan de session du blueprint."""
    from questions_maths_p1_a import questions as qa
    from questions_maths_p1_b import questions as qb
    out = []
    for q in qa() + qb():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def num_ex(n):
    """« 1 » devient « 01 » : la plateforme trie les exercices par numero_exercice en TEXTE (inedit/views.py, models.py),
    donc « 10 » viendrait avant « 2 » dans le lecteur et le PDF. Le zero initial garde l'ordre tant que ce tri n'est pas
    naturel (DEFAUT de plateforme releve le 2026-10-19, voir scripts/gce/INEDITES_GCE.md)."""
    return f"{int(n):02d}" if n.isdigit() else n


def figure_markdown(svg):
    return "\n\n" + svg + "\n\n"


def construire():
    figs = figs_maths_p2.toutes()
    cours = titres_cours()
    exercices = section_a() + section_b()
    ex_json = []
    for e in exercices:
        intro = e["intro"]
        if e["num"] == "1":
            intro = INTRO_PAPER
        if e["fig_intro"]:
            intro = intro + figure_markdown(figs[e["fig_intro"]])
        questions = []
        for ordre, s in enumerate(e["subs"], start=1):
            corrige = f"### Rappel de m\u00e9thode\n{s['rappel']}\n\n{s['sol']}"
            if s["fig"]:
                corrige += figure_markdown(figs[s["fig"]]).rstrip("\n")
            ans = s["ans"]
            corrige += f"\n\n**Answer: {ans}.**"
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            if s["conseil"]:
                corrige += f"\n\n### Conseil\n{s['conseil']}"
            q = {
                "numero": s["num"], "ordre": ordre,
                "enonce_markdown": s["text"],
                "corrige_markdown": corrige,
                "difficulte_estimee": s["diff"],
                "type_reponse": "ouverte",
                "points": s["pts"],
                "criteres_notation": [{"libelle": lib, "points": p} for lib, p in s["crit"]],
                "themes": s["themes"],
                "rappels_de_methode": [{
                    "id": f"rdi-{EP_ID}-ex{num_ex(e['num'])}-q{s['num']}-0",
                    "competence": competence_du_rappel(s["themes"], cours),
                    "contenu_markdown": s["rappel"],
                    "cours_genere": False, "cours_id": None,
                }],
            }
            if s["groupe_local"]:
                q["groupe_local"] = s["groupe_local"]
            questions.append(q)
        ex_json.append({
            "numero_exercice": num_ex(e["num"]), "points": f"{e['pts']:g}", "groupes": [e["groupe"]],
            "enonce_intro_markdown": intro, "questions": questions,
        })
    competences, sections_plan = [], []
    for e in exercices:
        comp = []
        for s in e["subs"]:
            for t in s["themes"]:
                if t not in comp:
                    comp.append(t)
                if t not in competences:
                    competences.append(t)
        diffs = [s["diff"] for s in e["subs"]]
        sections_plan.append({
            "exercice": num_ex(e["num"]), "titre": TITRES_EXERCICES[e["num"]], "points": e["pts"], "groupes": [e["groupe"]],
            "nombre_questions": len(e["subs"]), "competences": comp,
            "difficulte": "faible" if diffs.count("faible") > len(diffs) / 2 else "moyenne",
            "support": ("figure 1 (reseau)" if e["fig_intro"] else ("tableau de frequences" if e["num"] == "B2" else None)),
        })
    sections_plan = [{k: v for k, v in sp.items() if v is not None} for sp in sections_plan]
    p1 = themes_p1()
    tous_diffs = [s["diff"] for e in exercices for s in e["subs"]]
    total_a = sum(e["pts"] for e in exercices if e["groupe"] == "SECTION A")
    total_b = sum(e["pts"] for e in exercices if e["groupe"] == "SECTION B")
    blueprint = {
        "type": "blueprint",
        "external_id": BP_ID,
        "titre": TITRE,
        "matiere": "Mathematics",
        "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences,
        "sections_plan": sections_plan,
        "duree_minutes": 150,
        "bareme_total": total_a + total_b,
        "session": {
            "papier_jumeau": BP_P1,
            "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "themes_propres_au_paper_1": [t for t in p1 if t not in competences],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session",
        },
        "format": {
            "section_a": f"10 questions courtes (4 a 5 points, total {total_a}), toutes obligatoires",
            "section_b": f"4 questions de 15 points (total {total_b}), toutes obligatoires",
            "reference": "Paper 2 reels 2023, 2025 et 2026 (A 45 / 45 / 43 points, B 60)",
            "regle_de_choix": "aucune : Answer ALL",
        },
        "repartition_difficulte": {d: tous_diffs.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 1 + sum(1 for e in exercices for s in e["subs"] if s["fig"]),
    }
    epreuve = {
        "type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
        "exercices": ex_json,
    }
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
    print("exercices", len(ep["exercices"]), "sous-questions", nq, "points", bp["bareme_total"],
          "difficultes", bp["repartition_difficulte"], "figures", bp["figures_prevues"])
    print("themes communs avec P1:", bp["session"]["themes_communs_aux_deux_papers"])
    print("themes propres au P2:", bp["session"]["themes_propres_au_paper_2"])


if __name__ == "__main__":
    main()
