"""Genere le blueprint et l'epreuve inedite GCE O Level Biology Paper 1 n.1 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_biology_p1.py [dossier_de_sortie]

Sortie par defaut : backend/ingest/_inedit/cm/ (bp-cm-gce-ol-biology-p1-1.json, ep-cm-gce-ol-biology-p1-1-2026-s1.json).
Comme les vrais Paper 1 de Biology, l'ordre des questions est MELANGE (aucun bloc par chapitre) : suite deterministe (graine fixe).
Les cles sont placees par le script (suite equilibree) et la lettre citee dans le corrige est recalculee a chaque generation.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_biology_p1  # noqa: E402
from questions_biology_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-biology-p1-1"
EP_ID = "ep-cm-gce-ol-biology-p1-1-2026-s1"
BP_P2 = "bp-cm-gce-ol-biology-p2-1"
TITRE = "Biology GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks "
    "(1 mark each). Each question has four suggested answers A, B, C and D: choose only one answer for each "
    "question. Non-programmable calculators are allowed."
)
# regroupement des themes en grands domaines du syllabus 0510, pour le plan chiffre du blueprint (l'ordre des questions, lui, est melange)
DOMAINES = {
    "Cells, organisms and transport": ["plant cell structure", "cell structure", "practical biology", "unicellular organisms", "structure of algae",
                                        "bread mould", "osmosis in cells", "transport in plants", "transpiration"],
    "Nutrition and enzymes": ["biochemical food tests", "enzyme action", "digestive secretions", "mineral salts and deficiency diseases",
                              "photosynthesis process"],
    "Respiration and gaseous exchange": ["gas tests and absorbents", "cell respiration", "gaseous exchange in humans"],
    "Circulation, excretion and homeostasis": ["blood circulation", "mammalian heart", "excretory system", "kidney and nephron",
                                               "body temperature control", "mammalian skin"],
    "Coordination, support and plant responses": ["the human eye", "endocrine system", "nervous system", "plant tropisms", "human skeleton and joints"],
    "Reproduction and genetics": ["flower structure", "pollination and fertilization in plants", "seed germination", "human reproductive system",
                                  "human embryo and gestation", "monohybrid inheritance", "dominant and recessive alleles", "genetic engineering"],
    "Ecology and environment": ["food chains and food webs", "energy flow in ecosystems", "nitrogen cycle", "carbon cycle", "water pollution",
                                "air pollution", "malaria and disease vectors"],
}


def cles_equilibrees(n, graine=510):
    rng = random.Random(graine)
    base = [LETTRES[i % 4] for i in range(n)]
    while True:
        rng.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_biology_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire():
    figs = figs_biology_p1.toutes()
    cours = titres_cours()
    qs = questions()
    assert len(qs) == 50, len(qs)
    ordre = list(range(len(qs)))
    random.Random(2026).shuffle(ordre)
    qs = [qs[i] for i in ordre]
    cles = cles_equilibrees(len(qs))
    rng = random.Random(11)
    questions_json = []
    nfig = 0
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3
        rng.shuffle(mauvaises)
        it = iter(mauvaises)
        options = [q["ok"] if l == cle else next(it) for l in LETTRES]
        assert len(set(options)) == 4, f"options en double ({q['id']})"
        enonce = q["stem"]
        if q["fig"]:
            nfig += 1
            nom = f"Figure {nfig}"
            enonce = enonce.replace("{FIG}", nom) + "\n\n" + figs[q["fig"]].replace("{FIG}", nom) + "\n\n"
        assert "{FIG}" not in enonce
        sol = q["sol"].replace("{FIG}", f"Figure {nfig}")
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{sol}\n\n**Answer: {cle.upper()}.**"
        if q["piege"]:
            corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{q['piege']}"
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(n), "ordre": n, "enonce_markdown": enonce, "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)],
            "reponse_correcte": cle, "points": 1, "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{n}-0", "competence": competence_du_rappel(q["themes"], cours),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
            "_id": q["id"],
        })
    competences = []
    for q in qs:
        for t in q["themes"]:
            if t not in competences:
                competences.append(t)
    domaines = {}
    for d, themes in DOMAINES.items():
        nb = sum(1 for q in qs if q["themes"][0] in themes)
        domaines[d] = nb
    assert sum(domaines.values()) == 50, domaines
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Biology",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix",
            "ordre": "melange, comme les vrais Paper 1 de Biology 2019-2026 (aucun bloc par chapitre)",
            "repartition_par_domaine": domaines,
            "repartition_difficulte": diffs,
            "figures_prevues": nfig,
            "figures": "5 figures de DONNEES calculees (courbes de resultats, reseau trophique) ; aucun schema anatomique ou cellulaire",
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 1,
                    "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session"},
    }
    for q in questions_json:
        q.pop("_id")
    epreuve = {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
               "exercices": [{"numero_exercice": "1", "points": "50", "enonce_intro_markdown": INTRO, "questions": questions_json}]}
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
    cles = [q["reponse_correcte"] for q in ep["exercices"][0]["questions"]]
    print("cles", {l: cles.count(l) for l in LETTRES}, "difficultes", bp["sections_plan"][0]["repartition_difficulte"],
          "figures", bp["sections_plan"][0]["figures_prevues"], "domaines", bp["sections_plan"][0]["repartition_par_domaine"])


if __name__ == "__main__":
    main()
