"""Genere le blueprint et l'epreuve inedite GCE O Level Biology Paper 2 n.1 (5 questions de 20 points).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_biology_p2.py [dossier_de_sortie]

Jumeau du Paper 1 (generer_biology_p1.py). Section A : 3 questions obligatoires. Section B : 2 questions (le vrai sujet en propose 4 et en demande
2 ; version « answer ALL » limitee aux questions a traiter, la plateforme ne codant pas le choix : voir scripts/gce/INEDITES_GCE.md).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_biology_p2  # noqa: E402
from questions_biology_p2 import section_a, section_b  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-biology-p2-1"
EP_ID = "ep-cm-gce-ol-biology-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-biology-p1-1"
TITRE = "Biology GCE O Level Paper 2 \u2013 Original Paper No. 1"
INTRO_PAPER = (
    "**Paper 2 (2 hours 30 minutes).** Answer FIVE questions: ALL THREE questions of Section A and BOTH questions of Section B. All questions "
    "carry 20 marks each. For your guidance, the approximate mark for each part of a question is indicated. Begin each question on a new page. "
    "Give labelled diagrams where these will make the answers clearer. You are reminded of the necessity for good English and orderly "
    "presentation in your answers. In calculations, show all the steps in your working."
)
TITRES_EXERCICES = {"1": "Food tests, absorption and digestion", "2": "Transpiration, water transport and photosynthesis",
                    "3": "Genetics and variation", "4": "Food webs, pollution and energy flow", "5": "The human eye"}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_biology_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def themes_p1():
    from questions_biology_p1 import questions
    out = []
    for q in questions():
        for t in q["themes"]:
            if t not in out:
                out.append(t)
    return out


def construire():
    figs = figs_biology_p2.toutes()
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
            if s["fig"]:
                corrige += "\n\n" + figs[s["fig"]]
            if s["piege"]:
                corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{s['piege']}"
            if s["conseil"]:
                corrige += f"\n\n### Conseil\n{s['conseil']}"
            q = {
                "numero": s["num"], "ordre": ordre, "enonce_markdown": s["text"], "corrige_markdown": corrige,
                "difficulte_estimee": s["diff"], "type_reponse": "ouverte", "points": s["pts"],
                "criteres_notation": [{"libelle": lib, "points": p} for lib, p in s["crit"]],
                "themes": s["themes"],
                "rappels_de_methode": [{
                    "id": f"rdi-{EP_ID}-ex{e['num']}-q{s['num']}-0", "competence": competence_du_rappel(s["themes"], cours),
                    "contenu_markdown": s["rappel"], "cours_genere": False, "cours_id": None,
                }],
            }
            # pas de repere de sous-partie : les vrais Paper 2 de Biology n'en portent pas, et « (a) Food tests » au-dessus de « a. » est un doublon
            # (les reperes `groupe_local` des donnees servent seulement de memo de conception)
            questions.append(q)
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
            "support": "tableau de resultats" if e["num"] in ("1", "2") else ("situation ecologique decrite" if e["num"] == "4" else None),
        })
    sections_plan = [{k: v for k, v in sp.items() if v is not None} for sp in sections_plan]
    p1 = themes_p1()
    tous = [s["diff"] for e in exercices for s in e["subs"]]
    total = sum(e["pts"] for e in exercices)
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Biology", "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences, "sections_plan": sections_plan, "duree_minutes": 150, "bareme_total": total,
        "session": {
            "papier_jumeau": BP_P1, "numero_session": 1,
            "themes_communs_aux_deux_papers": [t for t in competences if t in p1],
            "themes_propres_au_paper_2": [t for t in competences if t not in p1],
            "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session",
        },
        "format": {
            "section_a": "3 questions de 20 points, toutes obligatoires (60)",
            "section_b": "2 questions de 20 points (40) : le vrai sujet en propose 4 et demande d'en traiter 2",
            "reference": "Paper 2 reels 2019-2026 : 7 questions de 20 points en trois parties (a)(b)(c) a points imprimes, reponse 'ALL THREE of Section A and any TWO of Section B'",
            "regle_de_choix": "version answer ALL limitee aux questions a traiter (la plateforme ne code pas le choix des inedites)",
        },
        "repartition_difficulte": {d: tous.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 1, "schemas": "un dessin a faire (oeil), decrit en texte dans le corrige ; aucun schema anatomique produit",
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
