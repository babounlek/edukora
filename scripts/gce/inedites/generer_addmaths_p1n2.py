"""Genere le blueprint et l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.2 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_addmaths_p1.py [dossier_de_sortie]

Ordre du SYLLABUS (indices, logarithmes, polynomes, suites, denombrement, trigonometrie, geometrie analytique, inequations, fonctions,
matrices, groupes, vecteurs, derivation, integration), comme les sept vrais Paper 1 2019-2026. Les cles sont placees par le script
(12-13 par lettre, jamais 3 de suite), jamais tapees a la main.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_addmaths_s2  # noqa: E402
from questions_addmaths_p1n2_a import questions as qa  # noqa: E402
from questions_addmaths_p1n2_b import questions as qb  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-addmaths-p1-2"
EP_ID = "ep-cm-gce-ol-addmaths-p1-2-2026-s1"
BP_P2 = "bp-cm-gce-ol-addmaths-p2-2"
TITRE = "Additional Mathematics GCE O Level Paper 1 \u2013 Original Paper No. 2"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks (1 mark each). "
    "Each question has four suggested answers A, B, C and D: choose only one answer for each question. Non-programmable "
    "calculators are allowed, but formulae booklets are NOT allowed."
)
BLOCS = [  # (premiere, derniere, titre) : ordre du syllabus
    (1, 3, "Indices, surds and logarithms"),
    (4, 7, "Quadratics and polynomials"),
    (8, 11, "Arithmetic and geometric progressions"),
    (12, 15, "Binomial expansion, permutations and combinations"),
    (16, 23, "Trigonometry"),
    (24, 26, "Coordinate geometry"),
    (27, 31, "Inequalities, modulus and linear programming"),
    (32, 34, "Functions"),
    (35, 37, "Matrices and transformations"),
    (38, 40, "Binary operations and groups"),
    (41, 43, "Vectors"),
    (44, 46, "Differentiation"),
    (47, 50, "Integration"),
]


def cles_equilibrees(n, graine=2576):
    rng = random.Random(graine)
    base = [LETTRES[i % 4] for i in range(n)]
    while True:
        rng.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_add_maths_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire():
    figs = figs_addmaths_s2.toutes()
    cours = titres_cours()
    qs = qa() + qb()
    assert [q["n"] for q in qs] == list(range(1, 51)), "numerotation 1..50 continue"
    cles = cles_equilibrees(len(qs))
    rng = random.Random(12)
    questions_json = []
    nfig = 0
    for q, cle in zip(qs, cles):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3
        rng.shuffle(mauvaises)
        it = iter(mauvaises)
        options = [q["ok"] if lettre == cle else next(it) for lettre in LETTRES]
        # fractions des options et de l'enonce en style texte (\frac) : une dfrac empilee deborde de la ligne d'une option dans le PDF
        options = [o.replace(r"\dfrac", r"\frac") for o in options]
        assert len(set(options)) == 4, f"options en double a la question {q['n']}"
        enonce = q["stem"].replace(r"\dfrac", r"\frac")
        if q["fig"]:
            nfig += 1
            nom = f"Figure {nfig}"
            enonce = enonce.replace("{FIG}", nom) + "\n\n" + figs[q["fig"]].replace("{FIG}", nom) + "\n\n"
        assert "{FIG}" not in enonce
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**"
        if q["piege"]:
            corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{q['piege']}"
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(q["n"]), "ordre": q["n"], "enonce_markdown": enonce, "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)],
            "reponse_correcte": cle, "points": 1, "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{q['n']}-0", "competence": competence_du_rappel(q["themes"], cours),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
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
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Additional Mathematics",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix",
            "ordre": "ordre du syllabus 0575, comme les sept vrais Paper 1 2019-2026",
            "repartition": repartition, "repartition_difficulte": diffs, "figures_prevues": nfig,
            "figures": "3 figures calculees : triangle (regle des sinus), droite coupant les axes, region definie par trois droites",
            "calculs": "toutes les questions se recalculent (verifier_reponses_addmaths_p1n2.py)",
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 2,
                    "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2"},
    }
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
    print("cles", {l: cles.count(l) for l in LETTRES}, "difficultes", bp["sections_plan"][0]["repartition_difficulte"], "figures", bp["sections_plan"][0]["figures_prevues"])


if __name__ == "__main__":
    main()
