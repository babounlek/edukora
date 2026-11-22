r"""Genere l'epreuve inedite GCE A Level Chemistry Paper 1 n.1 (50 QCM de 1 point, 90 min).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_chemistry_al_p1.py [dossier_de_sortie]

N'ecrit QUE l'epreuve ep-cm-gce-al-chemistry-p1-1-2026-s1 : le blueprint bp-cm-gce-al-chemistry-p1-1 existe deja (valide, ingere) et n'est pas touche.
Ordre : 35 questions a meilleure reponse (themes melanges), puis 10 questions de completion multiple (36-45) et 5 d'assertion-raison (46-50), comme les Paper 1 reels
2024-2026. Les options des 15 questions des blocs speciaux sont a ordre IMPOSE : leur cle decoule du contenu ; le script place les 35 autres cles autour
(13/13/12/12 au total, jamais trois cles identiques de suite, graine fixe).
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_chemistry_al_p1 import questions, raisons, OPTIONS_MC, OPTIONS_AR, MC_PLAGE, AR_PLAGE  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-chemistry-p1-1"
EP_ID = "ep-cm-gce-al-chemistry-p1-1-2026-s1"
TITRE = "Chemistry GCE A Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    f"**Paper 1 (1 hour 30 minutes).** Multiple choice questions: answer ALL fifty questions. Each question carries 1 mark and the total is 50 marks. "
    f"Questions 1 to 35 have four suggested answers A, B, C and D: choose the one best answer. Questions {MC_PLAGE} and {AR_PLAGE} have their own instructions, printed with each question. "
    "No marks are deducted for a wrong answer. Non-programmable electronic calculators are allowed. "
    "The relative atomic masses and the other data needed are given in the questions themselves."
)
ALIAS = {"hess's law": "enthalpy changes"}


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_chemistry_al.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    """Titre exact d'un Cours publie de la matiere : A Level d'abord, sinon le cours O Level de meme etiquette ; sinon le theme."""
    for t in themes:
        t = ALIAS.get(t, t)
        if t in cours["al"]:
            return cours["al"][t]
    for t in themes:
        if t in cours["ol"]:
            return cours["ol"][t]
    return themes[0].capitalize()


def placer_cles(qs, graine=20261122):
    """Cles fixees par les blocs speciaux, puis suite equilibree (13/13/12/12 au total, jamais 3 de suite)."""
    rng = random.Random(graine)
    n = len(qs)
    cible = {"a": 13, "b": 13, "c": 12, "d": 12}
    for _ in range(200000):
        cles = [None] * n
        pool = dict(cible)
        for i, q in enumerate(qs):
            if q["kind"] == "mc":
                cles[i] = "abcd"[OPTIONS_MC.index(q["key"])]
            elif q["kind"] == "ar":
                cles[i] = "abcd"[OPTIONS_AR.index(q["key"])]
            if cles[i]:
                pool[cles[i]] -= 1
        if min(pool.values()) < 0:
            raise ValueError("equilibrage impossible : trop de cles fixees pour une lettre")
        libres = [i for i in range(n) if cles[i] is None]
        lettres = [l for l in LETTRES for _ in range(pool[l])]
        if len(lettres) != len(libres):
            raise ValueError("equilibrage impossible")
        rng.shuffle(lettres)
        for i, l in zip(libres, lettres):
            cles[i] = l
        if all(not (cles[i] == cles[i + 1] == cles[i + 2]) for i in range(n - 2)):
            return cles
    raise RuntimeError("aucune suite de cles valide")


def construire():
    cours = titres_cours()
    qs = questions()
    assert len(qs) == 50, len(qs)
    mc = [i + 1 for i, q in enumerate(qs) if q["kind"] == "mc"]
    ar = [i + 1 for i, q in enumerate(qs) if q["kind"] == "ar"]
    assert f"{mc[0]}-{mc[-1]}" == MC_PLAGE and len(mc) == 10, mc
    assert f"{ar[0]}-{ar[-1]}" == AR_PLAGE and len(ar) == 5, ar
    cles = placer_cles(qs)
    rng = random.Random(7)
    questions_json = []
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        if q["kind"] == "mc":
            options = list(OPTIONS_MC)
            reas = raisons(q)
        elif q["kind"] == "ar":
            options = list(OPTIONS_AR)
            reas = raisons(q)
        else:
            autres = [l for l in LETTRES if l != cle]
            dist = list(q["dist"])
            rng.shuffle(dist)
            options = [None] * 4
            options[LETTRES.index(cle)] = q["key"]
            reas = {}
            for l, (texte, raison) in zip(autres, dist):
                options[LETTRES.index(l)] = texte
                reas[l] = raison
        assert options[LETTRES.index(cle)] == q["key"], n
        assert len(set(options)) == 4, f"options en double (Q{n})"
        liste = "; ".join(f"option {l.upper()} {reas[l]}" for l in LETTRES if l in reas)
        corrige = (f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**\n\n"
                   f"### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {liste}.")
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        questions_json.append({
            "numero": str(n), "ordre": n, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)], "reponse_correcte": cle, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{n}-0", "competence": competence_du_rappel(q["themes"], cours),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    epreuve = {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
               "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO, "questions": questions_json}]}
    return epreuve


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    ep = construire()
    chemin = os.path.join(sortie, EP_ID + ".json")
    with open(chemin, "w", encoding="utf8", newline="\n") as fh:
        json.dump(ep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("ecrit", chemin)
    qj = ep["exercices"][0]["questions"]
    from collections import Counter
    print("questions", len(qj), "cles", dict(sorted(Counter(q["reponse_correcte"] for q in qj).items())),
          "difficultes", dict(Counter(q["difficulte_estimee"] for q in qj)))
    print("competences des rappels :", sorted({q["rappels_de_methode"][0]["competence"] for q in qj}))


if __name__ == "__main__":
    main()
