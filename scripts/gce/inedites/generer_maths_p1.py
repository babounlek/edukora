"""Genere le blueprint et l'epreuve inedite GCE O Level Mathematics Paper 1 n.1 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_maths_p1.py [dossier_de_sortie]

Sortie par defaut : backend/ingest/_inedit/cm/ (bp-cm-gce-ol-maths-p1-1.json, ep-cm-gce-ol-maths-p1-1-2026-s1.json).
Les cles des QCM ne sont PAS tapees a la main : la bonne option est placee a la lettre voulue par une suite
equilibree et deterministe, et la lettre citee dans le corrige est recalculee a chaque generation.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_maths_p1  # noqa: E402
from questions_maths_p1_a import questions as qa  # noqa: E402
from questions_maths_p1_b import questions as qb  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-maths-p1-1"
EP_ID = "ep-cm-gce-ol-maths-p1-1-2026-s1"
TITRE = "Mathematics GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"

INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks "
    "(1 mark each). Each question has four suggested answers A, B, C and D: choose only one answer for each "
    "question. Non-programmable calculators are allowed."
)

BLOCS = [  # (premiere, derniere, titre du bloc) : ordre du syllabus, comme les huit vrais Paper 1 2019-2026
    (1, 9, "Number, ratio and consumer arithmetic"),
    (10, 13, "Sets and logic"),
    (14, 16, "Functions and mappings"),
    (17, 24, "Geometry and mensuration"),
    (25, 27, "Coordinate geometry and graphs"),
    (28, 37, "Algebra"),
    (38, 38, "Graph theory"),
    (39, 41, "Trigonometry and bearings"),
    (42, 43, "Vectors"),
    (44, 46, "Matrices and transformations"),
    (47, 50, "Statistics and probability"),
]


def cles_equilibrees(n, graine=2026):
    """n lettres a peu pres egales en nombre, jamais trois fois la meme de suite."""
    rng = random.Random(graine)
    base = [LETTRES[i % 4] for i in range(n)]
    while True:
        rng.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_maths_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    """Titre EXACT du cours existant du premier theme qui en a un : le rattachement est une egalite de chaines."""
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire():
    figs = figs_maths_p1.toutes()
    cours = titres_cours()
    qs = qa() + qb()
    assert [q["n"] for q in qs] == list(range(1, 51)), "numerotation 1..50 continue"
    cles = cles_equilibrees(len(qs))
    rng = random.Random(7)
    questions_json = []
    for q, cle in zip(qs, cles):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3
        rng.shuffle(mauvaises)
        options = []
        it = iter(mauvaises)
        for lettre in LETTRES:
            options.append(q["ok"] if lettre == cle else next(it))
        assert len(set(options)) == 4, f"options en double a la question {q['n']}"
        enonce = q["stem"]
        if q["fig"]:
            enonce += "\n\n" + figs[q["fig"]] + "\n\n"
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**"
        if q["piege"]:
            corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{q['piege']}"
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(q["n"]), "ordre": q["n"],
            "enonce_markdown": enonce,
            "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"],
            "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)],
            "reponse_correcte": cle,
            "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{q['n']}-0",
                "competence": competence_du_rappel(q["themes"], cours),
                "contenu_markdown": q["rappel"],
                "cours_genere": False, "cours_id": None,
            }],
        })
    competences = []
    for q in qs:
        for t in q["themes"]:
            if t not in competences:
                competences.append(t)
    repartition = []
    for debut, fin, titre in BLOCS:
        themes = []
        for q in qs[debut - 1:fin]:
            for t in q["themes"]:
                if t not in themes:
                    themes.append(t)
        repartition.append({"questions": f"{debut}-{fin}", "bloc": titre, "nombre": fin - debut + 1, "competences": themes})
    assert sum(b["nombre"] for b in repartition) == 50
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint",
        "external_id": BP_ID,
        "titre": TITRE,
        "matiere": "Mathematics",
        "cursus": [{"examen": "gce_ol", "serie": ""}],
        "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50,
            "difficulte": "faible a moyenne", "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix",
            "ordre": "ordre du syllabus 0570, comme les vrais Paper 1 2019-2026",
            "repartition": repartition,
            "repartition_difficulte": diffs,
            "figures_prevues": sum(1 for q in qs if q["fig"]),
        }],
        "duree_minutes": 90,
        "bareme_total": 50,
    }
    epreuve = {
        "type": "epreuve",
        "external_id": EP_ID,
        "titre": TITRE,
        "blueprint_external_id": BP_ID,
        "exercices": [{
            "numero_exercice": "1", "points": "50", "enonce_intro_markdown": INTRO,
            "questions": questions_json,
        }],
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
    cles = [q["reponse_correcte"] for q in ep["exercices"][0]["questions"]]
    print("cles", {l: cles.count(l) for l in LETTRES}, "difficultes", bp["sections_plan"][0]["repartition_difficulte"])


if __name__ == "__main__":
    main()
