"""Genere le blueprint et l'epreuve inedite GCE O Level Physics Paper 1 n.1 (50 QCM).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_physics_p1.py [dossier_de_sortie]

Ordre MELANGE (les vrais Paper 1 de Physics 2023-2026 enchainent des grappes de 1 a 3 questions d'un meme chapitre sans suivre le syllabus).
Les cles sont placees par le script ; une question dont les options designent les panneaux A a D d'une figure a sa cle FIXEE par la figure.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figs_physics_p1  # noqa: E402
from questions_physics_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-physics-p1-1"
EP_ID = "ep-cm-gce-ol-physics-p1-1-2026-s1"
BP_P2 = "bp-cm-gce-ol-physics-p2-1"
TITRE = "Physics GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks "
    "(1 mark each). Each question has four suggested answers A, B, C and D: choose only one answer for each "
    "question. Non-programmable calculators are allowed. Where it is needed, the question itself gives the value of $g$."
)
DOMAINES = {
    "Mechanics, pressure and energy": ["measurement", "density", "motion", "velocity-time graphs", "forces and Newton's laws", "mass and weight",
                                       "linear momentum", "forces and their effects", "moments and equilibrium", "elasticity and Hooke's law",
                                       "pressure", "pressure in fluids", "simple machines", "work energy and power", "energy conversions",
                                       "practical physics", "graph plotting"],
    "Thermal physics": ["thermal physics", "change of state", "thermometers and temperature scales", "heat transfer"],
    "Waves, sound and light": ["waves", "sound", "electromagnetic spectrum", "light and reflection", "refraction and lenses", "refraction of light",
                               "total internal reflection"],
    "Electricity and magnetism": ["electrostatics", "current electricity", "electric circuits", "electrical energy and power", "domestic electricity",
                                  "electromagnetism", "transformers", "magnetism", "electronics and semiconductors"],
    "Atomic and nuclear physics": ["radioactive decay", "atomic and nuclear physics"],
}


def placer_cles(qs, graine=580):
    """Une lettre par question : les cles fixees d'abord, puis une suite equilibree (12-13 par lettre, jamais 3 de suite)."""
    rng = random.Random(graine)
    n = len(qs)
    for _ in range(100000):
        fixees = {i: q["cle_fixee"] for i, q in enumerate(qs) if q["cle_fixee"]}
        reste = [i for i in range(n) if i not in fixees]
        cible = {l: n // 4 + (1 if k < n % 4 else 0) for k, l in enumerate(LETTRES)}
        for l in fixees.values():
            cible[l] -= 1
        pool = [l for l in LETTRES for _ in range(max(0, cible[l]))]
        if len(pool) != len(reste):
            raise ValueError("equilibrage impossible")
        rng.shuffle(pool)
        cles = [None] * n
        for i, l in fixees.items():
            cles[i] = l
        for i, l in zip(reste, pool):
            cles[i] = l
        if all(not (cles[i] == cles[i + 1] == cles[i + 2]) for i in range(n - 2)):
            return cles
    raise RuntimeError("aucune suite de cles valide")


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_physics_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire():
    figs = figs_physics_p1.toutes()
    cours = titres_cours()
    qs = questions()
    assert len(qs) == 50, len(qs)
    ordre = list(range(len(qs)))
    random.Random(2026).shuffle(ordre)
    qs = [qs[i] for i in ordre]
    cles = placer_cles(qs)
    rng = random.Random(13)
    questions_json = []
    nfig = 0
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3
        if q["cle_fixee"]:  # options « A. », « B. »... : l'ordre suit la figure
            options = [q["ok"] if l == cle else None for l in LETTRES]
            restantes = iter(sorted(mauvaises))
            options = [o if o is not None else next(restantes) for o in options]
        else:
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
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**"
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
        })
    competences = []
    for q in qs:
        for t in q["themes"]:
            if t not in competences:
                competences.append(t)
    domaines = {d: sum(1 for q in qs if q["themes"][0] in themes) for d, themes in DOMAINES.items()}
    assert sum(domaines.values()) == 50, domaines
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Physics",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix",
            "ordre": "melange par petites grappes d'un meme chapitre, comme les vrais Paper 1 de Physics 2023-2026",
            "repartition_par_domaine": domaines, "repartition_difficulte": diffs, "figures_prevues": nfig,
            "figures": "6 figures calculees : graphique vitesse-temps, regle en equilibre, courbe de chauffe, reflexion sur un miroir, circuit, quatre graphiques en options",
            "calculs": "une trentaine de questions chiffrees, toutes recalculees par verifier_reponses_physics_p1.py",
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 1,
                    "regle": "aucune donnee, aucun contexte, aucune figure partages entre les deux papers de la session"},
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
          "figures", bp["sections_plan"][0]["figures_prevues"], "domaines", bp["sections_plan"][0]["repartition_par_domaine"])


if __name__ == "__main__":
    main()
