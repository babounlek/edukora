r"""Genere l'epreuve inedite GCE A Level Computer Science Paper 1 n.1 (50 QCM de 1 point, 90 min).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_cs_al_p1.py [dossier_de_sortie]

N'ecrit QUE l'epreuve ep-cm-gce-al-computerscience-p1-1-2026-s1 : le blueprint bp-cm-gce-al-computerscience-p1-1 existe deja (valide, ingere) et n'est pas touche.
50 questions a meilleure reponse (comme les Paper 1 reels 2025 et 2026), themes melanges ; l'ordre est fixe par ORDRE (aucune paire de themes voisins).
Les cles sont placees par le script (13/13/12/12, jamais trois cles identiques de suite, graine fixe) ; les distracteurs sont melanges (graine fixe).
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_cs_al_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-al-computerscience-p1-1"
EP_ID = "ep-cm-gce-al-computerscience-p1-1-2026-s1"
TITRE = "Computer Science GCE A Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 (1 hour 30 minutes).** Multiple choice questions: answer ALL fifty questions. Each question has four suggested answers A, B, C and D: "
    "choose the one best answer. Each question carries 1 mark and the total is 50 marks. No marks are deducted for a wrong answer. "
    "Non-programmable electronic calculators are allowed. All the data needed are given in the questions themselves."
)
ORDRE = ["hex2dec", "process_state", "bool_simpl", "trace_loop", "switch_mac", "twos_neg", "sjf", "stack_pops", "pc_fetch", "normal_form",
         "bubble", "subnet_net", "logic_paradigm", "bin_add", "fcfs", "tps", "bst_post", "addr_capacity", "xor_circuit", "caesar",
         "fifo_faults", "compiler_phases", "sql_join", "hex_octal", "parity", "acc_trace", "boundary_tests", "insertion", "full_adder", "paging_addr",
         "trojan", "recursion_g", "dvd_backup", "twos_sub", "rr", "binsearch", "demorgan", "download_time", "parallel_running", "postfix",
         "sql_subq", "overflow", "fetch_regs", "nand_or", "scaling", "deadlock_safe", "bits_colours", "amdahl", "byval_byref", "sql_group"]


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_cs_al.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(q, cours):
    """Titre exact d'un Cours publie de la matiere : `cours` explicite, sinon premier theme qui a un cours, sinon le theme."""
    if q.get("cours"):
        return cours[q["cours"]]
    for t in q["themes"]:
        if t in cours:
            return cours[t]
    return q["themes"][0].capitalize()


def placer_cles(n, graine=20261122):
    """Suite de cles equilibree (13/13/12/12), jamais trois cles identiques de suite."""
    rng = random.Random(graine)
    lettres = list("a" * 13 + "b" * 13 + "c" * 12 + "d" * 12)
    assert len(lettres) == n
    for _ in range(100000):
        rng.shuffle(lettres)
        if all(not (lettres[i] == lettres[i + 1] == lettres[i + 2]) for i in range(n - 2)):
            return lettres[:]
    raise RuntimeError("aucune suite de cles valide")


def construire():
    cours = titres_cours()
    par_id = {q["id"]: q for q in questions()}
    assert len(par_id) == len(questions()) == 50 and sorted(par_id) == sorted(ORDRE) and len(set(ORDRE)) == 50, "ORDRE incomplet"
    qs = [par_id[i] for i in ORDRE]
    for a, b in zip(qs, qs[1:]):
        assert a["themes"][0] != b["themes"][0], ("themes voisins", a["id"], b["id"])
    cles = placer_cles(50)
    rng = random.Random(7)
    sortie = []
    for n, (q, cle) in enumerate(zip(qs, cles), start=1):
        autres = [l for l in LETTRES if l != cle]
        dist = list(q["dist"])
        rng.shuffle(dist)
        options = [None] * 4
        options[LETTRES.index(cle)] = q["key"]
        reas = {}
        for l, (texte, raison) in zip(autres, dist):
            options[LETTRES.index(l)] = texte
            reas[l] = raison
        assert len(set(options)) == 4, f"options en double (Q{n})"
        liste = "; ".join(f"option {l.upper()} {reas[l]}" for l in LETTRES if l in reas)
        corrige = (f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**\n\n"
                   f"### Pi\u00e8ge \u00e0 \u00e9viter\nEach wrong option comes from a precise slip: {liste}.")
        if q["conseil"]:
            corrige += f"\n\n### Conseil\n{q['conseil']}"
        sortie.append({
            "numero": str(n), "ordre": n, "enonce_markdown": q["stem"], "corrige_markdown": corrige,
            "difficulte_estimee": q["diff"], "type_reponse": "qcm",
            "choix": [{"lettre": l, "texte": t} for l, t in zip(LETTRES, options)], "reponse_correcte": cle, "points": 1,
            "themes": q["themes"],
            "rappels_de_methode": [{
                "id": f"rdi-{EP_ID}-ex1-q{n}-0", "competence": competence_du_rappel(q, cours),
                "contenu_markdown": q["rappel"], "cours_genere": False, "cours_id": None,
            }],
        })
    return {"type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
            "exercices": [{"numero_exercice": "1", "points": "50", "groupes": [], "enonce_intro_markdown": INTRO, "questions": sortie}]}


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
