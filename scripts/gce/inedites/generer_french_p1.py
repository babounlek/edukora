"""Genere le blueprint et l'epreuve inedite GCE O Level French Paper 1 n.1 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_french_p1.py [dossier_de_sortie]

Structure des 6 vrais Paper 1 (2020-2023, 2025, 2026 ; code 0545) : 45 questions isolees puis un texte a trous de 5 questions (46-50). Cles equilibrees PLACEES ICI
(12-13 par lettre, jamais 3 de suite). Le piege du corrige est compose des RAISONS ecrites pour chaque distracteur.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_french_p1 import PREFIXE, questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-french-p1-1"
EP_ID = "ep-cm-gce-ol-french-p1-1-2026-s1"
BP_P2 = "bp-cm-gce-ol-french-p2-1"
TITRE = "French GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks (1 mark each). Each question has "
    "four suggested answers A, B, C and D: choose only one answer for each question. Questions 1 to 45 are independent; questions 46 to 50 are based on one passage."
)


def placer_cles(n, graine=5451):
    rng = random.Random(graine)
    for _ in range(100000):
        cible = {l: n // 4 + (1 if k < n % 4 else 0) for k, l in enumerate(LETTRES)}
        pool = [l for l in LETTRES for _ in range(cible[l])]
        rng.shuffle(pool)
        if all(not (pool[i] == pool[i + 1] == pool[i + 2]) for i in range(n - 2)):
            return pool
    raise RuntimeError("aucune suite de cles valide")


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_french_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def sans_prefixe(theme):
    return theme[len(PREFIXE):] if theme.startswith(PREFIXE) else theme


def competence_du_rappel(themes, cours):
    for t in themes:
        if sans_prefixe(t) in cours:
            return cours[sans_prefixe(t)]
    return sans_prefixe(themes[0]).capitalize()


def construire():
    cours = titres_cours()
    qs = questions()
    assert len(qs) == 50, len(qs)
    cles = placer_cles(50)
    rng = random.Random(31)
    questions_json = []
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        paires = list(zip(q["bad"], q["raisons"]))
        rng.shuffle(paires)
        it = iter(paires)
        options = [q["ok"] if l == cle else next(it)[0] for l in LETTRES]
        assert len({o.strip().lower() for o in options}) == 4, f"options en double ({q['id']})"
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**"
        corrige += "\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n" + " ".join(f"*{b}* {r}." for b, r in paires)
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
    premiers = {}
    for q in qs:
        t = sans_prefixe(q["themes"][0])
        premiers[t] = premiers.get(t, 0) + 1
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "French",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun ; 45 questions isolees puis un texte a trous de 5 questions (46-50)",
            "ordre": "ordre melange des vrais Paper 1 2020-2026 : aucune section par theme ; le texte a trous termine le paper",
            "repartition_par_theme": premiers, "repartition_difficulte": diffs, "figures_prevues": 0,
            "texte": "un texte original de 5 trous (infinitif, accord, connecteur, superlatif, pronom relatif)",
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 1,
                    "regle": "aucun texte, nom, lieu ni phrase partages entre les deux papers de la session (Ngoumou, Limbe, Bamenda et les phrases du Paper 1 ne reparaissent pas au Paper 2)"},
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
    print("cles", {l: cles.count(l) for l in LETTRES}, "difficultes", bp["sections_plan"][0]["repartition_difficulte"])
    print("themes (premier theme)", bp["sections_plan"][0]["repartition_par_theme"])


if __name__ == "__main__":
    main()
