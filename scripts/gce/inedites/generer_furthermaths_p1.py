r"""Genere le blueprint et l'epreuve inedite GCE A Level Further Mathematics Paper 1 n.1 (50 QCM de 1 point, 90 min).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_furthermaths_p1.py [dossier_de_sortie]

Les lettres des cles sont placees ICI (equilibre 13/13/12/12, jamais trois cles identiques de suite, graine fixe), jamais tapees dans les questions.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generer_furthermaths_p2 import competence_du_rappel  # noqa: E402  (meme table tag -> cours publie)
from questions_furthermaths_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-furthermaths-p1-1"
EP_ID = "ep-cm-gce-al-furthermaths-p1-1-2026-s1"
TITRE = "Further Mathematics GCE A Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO_PAPER = (
    r"**Paper 1 (1 hour 30 minutes).** Multiple choice questions: choose the one correct answer, A, B, C or D, for each of the fifty questions. Each question carries 1 mark "
    r"and the total is 50 marks. No marks are deducted for a wrong answer. Non-programmable electronic calculators and the mathematical formulae booklets published by the GCE Board are allowed."
)


def cles(n, graine=20261121):
    rnd = random.Random(graine)
    base = list("a" * 13 + "b" * 13 + "c" * 12 + "d" * 12)
    while True:
        rnd.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def construire():
    qs = questions()
    ks = cles(len(qs))
    questions_json = []
    themes_tous = []
    for i, (q, k) in enumerate(zip(qs, ks), start=1):
        autres = [c for c in LETTRES if c != k]
        options = {k: q["key"]}
        for c, (texte, _) in zip(autres, q["dist"]):
            options[c] = texte
        raisons = "; ".join(f"option {c.upper()} {r}" for c, (_, r) in zip(autres, q["dist"]))
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {k.upper()}.**\n\n### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {raisons}."
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        for t in q["themes"]:
            if t not in themes_tous:
                themes_tous.append(t)
        questions_json.append({
            "numero": str(i), "ordre": i, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": c, "texte": options[c]} for c in LETTRES], "reponse_correcte": k, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{i}-0", "competence": competence_du_rappel(q["themes"]),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    diffs = [q["diff"] for q in qs]
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Further Mathematics", "cursus": [{"examen": "gce_al", "serie": ""}],
        "competences": themes_tous,
        "sections_plan": [{
            "exercice": "1", "titre": "Multiple choice questions", "points": 50, "difficulte": "moyenne", "nombre_questions": 50, "competences": themes_tous,
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {
            "papier_jumeau": "bp-cm-gce-al-furthermaths-p2-1", "papiers_de_la_session": ["bp-cm-gce-al-furthermaths-p2-1", "bp-cm-gce-al-furthermaths-p3-1"], "numero_session": 1,
            "regle": "aucune donnee, aucun contexte, aucune figure partages avec les Paper 2 et 3 de la session ; aucune option ne donne la reponse d'une question des deux autres papers",
        },
        "format": {
            "structure": "50 QCM de 1 point, 4 options a-d, un seul exercice, themes melanges comme dans les Paper 1 reels 2025 et 2026 (mathematiques pures, mecanique, statistiques, logique)",
            "cles": "13 a, 13 b, 12 c, 12 d, placees par le generateur, jamais trois cles identiques de suite",
            "reference": "Paper 1 reels 2025 et 2026 de Further Mathematics (50 questions, 4 options, 21 a 25 faibles)",
        },
        "repartition_difficulte": {d: diffs.count(d) for d in ("faible", "moyenne", "elevee")},
        "figures_prevues": 0,
    }
    epreuve = {
        "type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
        "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO_PAPER, "questions": questions_json}],
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
    qs = ep["exercices"][0]["questions"]
    from collections import Counter
    print("questions", len(qs), "cles", dict(sorted(Counter(q["reponse_correcte"] for q in qs).items())), "difficultes", bp["repartition_difficulte"])


if __name__ == "__main__":
    main()
