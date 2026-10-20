"""Genere le blueprint et l'epreuve inedite GCE O Level English Language Paper 1 n.1 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_english_p1.py [dossier_de_sortie]

Structure des 5 vrais Paper 1 (2021, 2023-2026) : A ecoute 1-10 (un texte lu une fois, en trois parties), B lecture 11-25 (un texte), C grammaire 26-40,
D vocabulaire 41-50. Les textes sont inseres dans l'enonce de la premiere question de chaque section de texte, comme dans les vrais sujets. Cles
equilibrees PLACEES ICI (12-13 par lettre, jamais 3 de suite), jamais tapees dans les questions.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_english_p1 import PREFIXE, questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-english-p1-1"
EP_ID = "ep-cm-gce-ol-english-p1-1-2026-s1"
BP_P2 = "bp-cm-gce-ol-english-p2-1"
TITRE = "English Language GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
SECTIONS = {"A": (1, 10), "B": (11, 25), "C": (26, 40), "D": (41, 50)}
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks (1 mark each). Each question has "
    "four suggested answers A, B, C and D: choose only one answer for each question. The paper has four sections: A listening comprehension "
    "(questions 1 to 10), B reading comprehension (questions 11 to 25), C grammar (questions 26 to 40) and D vocabulary (questions 41 to 50)."
)


def placer_cles(n, graine=5301):
    """Une lettre par question : suite equilibree (12-13 par lettre), jamais 3 identiques de suite."""
    rng = random.Random(graine)
    for _ in range(100000):
        cible = {l: n // 4 + (1 if k < n % 4 else 0) for k, l in enumerate(LETTRES)}
        pool = [l for l in LETTRES for _ in range(cible[l])]
        rng.shuffle(pool)
        if all(not (pool[i] == pool[i + 1] == pool[i + 2]) for i in range(n - 2)):
            return pool
    raise RuntimeError("aucune suite de cles valide")


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_english_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def sans_prefixe(theme):
    return theme[len(PREFIXE):] if theme.startswith(PREFIXE) else theme


def competence_du_rappel(themes, cours):
    """Titre EXACT d'un Cours O Level existant pour le theme ; a defaut le theme lui-meme (rappel non rattache : voir le compte rendu)."""
    for t in themes:
        if sans_prefixe(t) in cours:
            return cours[sans_prefixe(t)]
    return sans_prefixe(themes[0]).capitalize()


def section_de(n):
    for s, (a, b) in SECTIONS.items():
        if a <= n <= b:
            return s
    raise ValueError(n)


def construire():
    cours = titres_cours()
    qs = questions()
    assert len(qs) == 50, len(qs)
    cles = placer_cles(len(qs))
    rng = random.Random(29)
    questions_json = []
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3, q["id"]
        rng.shuffle(mauvaises)
        it = iter(mauvaises)
        options = [q["ok"] if l == cle else next(it) for l in LETTRES]
        assert len(set(options)) == 4, f"options en double ({q['id']})"
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}"
        if q["preuve"]:
            corrige += f"\n\n**In the passage:** \"{q['preuve']}\""
        corrige += f"\n\n**Answer: {cle.upper()}.**"
        if q["piege"]:
            corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{q['piege']}"
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(n), "ordre": n, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)],
            "reponse_correcte": cle, "points": 1, "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{n}-0", "competence": competence_du_rappel(q["themes"], cours),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    competences = []
    for q in qs:
        for t in q["themes"]:
            if t not in competences:
                competences.append(t)
    par_section = {}
    for n, q in enumerate(qs, start=1):
        par_section[section_de(n)] = par_section.get(section_de(n), 0) + 1
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "English Language",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix ; textes inseres dans l'enonce de Q1 (ecoute) et Q11 (lecture)",
            "ordre": "ordre fixe des vrais Paper 1 2021-2026 : A ecoute 1-10 (trois parties), B lecture 11-25, C grammaire 26-40, D vocabulaire 41-50",
            "repartition_par_section": {
                "A listening comprehension (1-10)": par_section["A"], "B reading comprehension (11-25)": par_section["B"],
                "C grammar (26-40)": par_section["C"], "D vocabulary (41-50)": par_section["D"],
            },
            "textes": "deux textes originaux : une causerie suivie d'un recit lus une seule fois (environ 435 mots, Section One-Three) et un recit de lecture (environ 600 mots, six paragraphes numerotes)",
            "repartition_difficulte": diffs, "figures_prevues": 0,
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 1,
                    "regle": "aucun texte, personnage, theme de composition ni phrase partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais le sujet ni la reponse du Paper 2"},
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
    print("cles", {l: cles.count(l) for l in LETTRES}, "difficultes", bp["sections_plan"][0]["repartition_difficulte"],
          "sections", bp["sections_plan"][0]["repartition_par_section"])


if __name__ == "__main__":
    main()
