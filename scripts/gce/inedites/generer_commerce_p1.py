r"""Genere le blueprint et l'epreuve inedite GCE O Level Commerce Paper 1 n.1 (50 QCM).

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\generer_commerce_p1.py [dossier_de_sortie]

Les vrais Paper 1 de Commerce (2019-2026) melangent les themes d'une question a l'autre (pas d'ordre de syllabus) : l'ordre est donc celui de
questions_commerce_p1.py, sans deux questions de meme theme cote a cote. Les cles sont placees par le script (12-13 par lettre, jamais 3 de suite).
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_commerce_p1 import questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-commerce-p1-1"
EP_ID = "ep-cm-gce-ol-commerce-p1-1-2026-s1"
BP_P2 = "bp-cm-gce-ol-commerce-p2-1"
TITRE = "Commerce GCE O Level Paper 1 \u2013 Original Paper No. 1"
LETTRES = "abcd"
INTRO = (
    "**Paper 1 - Multiple choice (1 hour 30 minutes).** Answer ALL 50 questions. All questions carry equal marks (1 mark each). "
    "Each question has four suggested answers A, B, C and D: choose only one answer for each question."
)
FAMILLES = {  # theme -> famille du plan (le sujet reel ne range pas ses questions par famille, le plan oui)
    "commercial banking services": "Banking and means of payment", "methods of payment": "Banking and means of payment", "central and commercial banks": "Banking and means of payment",
    "transport in commerce": "Transport, warehousing and communication", "warehousing": "Transport, warehousing and communication", "communication services": "Transport, warehousing and communication",
    "retail trade": "Retail, wholesale and distribution", "commercial channels of distribution": "Retail, wholesale and distribution", "commercial agents": "Retail, wholesale and distribution",
    "advertising and sales promotion": "Advertising and consumers",
    "types of insurance": "Insurance", "insurance principles": "Insurance", "insurance documents": "Insurance",
    "co-operative societies": "Business ownership and finance", "business ownership types": "Business ownership and finance", "limited liability companies": "Business ownership and finance",
    "company formation documents": "Business ownership and finance", "company securities and investors": "Business ownership and finance", "business funding sources": "Business ownership and finance",
    "hire purchase": "Business ownership and finance",
    "business documents": "Documents and terms of sale", "quotations and delivery terms": "Documents and terms of sale", "incoterms": "Documents and terms of sale",
    "foreign trade concepts": "Foreign trade and customs", "foreign trade documents": "Foreign trade and customs", "customs administration": "Foreign trade and customs",
    "profit and mark-up calculations": "Commercial calculations", "stock turnover": "Commercial calculations", "trade discounts and cash discounts": "Commercial calculations", "vat calculations": "Commercial calculations",
    "scope of commerce": "The scope of commerce", "division of labour and specialisation": "The scope of commerce", "social responsibility of business": "The scope of commerce",
}


def cles_equilibrees(n, graine=520):
    rng = random.Random(graine)
    base = [LETTRES[i % 4] for i in range(n)]
    while True:
        rng.shuffle(base)
        if all(not (base[i] == base[i + 1] == base[i + 2]) for i in range(n - 2)):
            return base


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_commerce_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence_du_rappel(themes, cours):
    for t in themes:
        if t in cours:
            return cours[t]
    return themes[0].capitalize()


def construire():
    cours = titres_cours()
    qs = questions()
    assert [q["n"] for q in qs] == list(range(1, 51)), "numerotation 1..50 continue"
    for q1, q2 in zip(qs, qs[1:]):
        assert q1["themes"][0] != q2["themes"][0], f"meme theme cote a cote : {q1['n']} et {q2['n']}"
    cles = cles_equilibrees(len(qs))
    rng = random.Random(21)
    questions_json = []
    for q, cle in zip(qs, cles):
        mauvaises = list(q["bad"])
        assert len(mauvaises) == 3
        rng.shuffle(mauvaises)
        it = iter(mauvaises)
        options = [q["ok"] if lettre == cle else next(it) for lettre in LETTRES]
        assert len(set(options)) == 4, f"options en double a la question {q['n']}"
        enonce = q["stem"]
        corrige = f"### Rappel de m\u00e9thode\n{q['rappel']}\n\n{q['sol']}\n\n**Answer: {cle.upper()}.**"
        if q["piege"]:
            corrige += f"\n\n### Pi\u00e8ge \u00e0 \u00e9viter\n{q['piege']}"
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
    repartition = {}
    for q in qs:
        fam = FAMILLES[q["themes"][0]]
        r = repartition.setdefault(fam, {"bloc": fam, "nombre": 0, "questions": [], "competences": []})
        r["nombre"] += 1
        r["questions"].append(q["n"])
        for t in q["themes"]:
            if t not in r["competences"]:
                r["competences"].append(t)
    repartition = [dict(v, questions=",".join(str(n) for n in v["questions"])) for v in repartition.values()]
    assert sum(b["nombre"] for b in repartition) == 50
    diffs = {d: sum(1 for q in qs if q["diff"] == d) for d in ("faible", "moyenne", "elevee")}
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "Commerce",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [{
            "exercice": "1", "titre": "Paper 1 - Multiple choice questions", "points": 50, "difficulte": "faible a moyenne",
            "nombre_questions": 50, "competences": competences,
            "format": "50 QCM a 4 choix (a-d), une seule bonne reponse, 1 point chacun, aucune regle de choix, options courtes terminees par un point",
            "ordre": "themes melanges d'une question a l'autre, comme les huit vrais Paper 1 2019-2026 (pas d'ordre de syllabus), jamais deux questions de meme theme cote a cote",
            "repartition": repartition, "repartition_difficulte": diffs, "figures_prevues": 0,
            "figures": "aucune (le corpus reel n'en contient pas)",
            "calculs": "4 calculs commerciaux (marge et majoration, rotation du stock, remise commerciale, TVA) et 1 remise en cascade, recalcules par verifier_reponses_commerce_p1.py",
            "formes": "5 questions « EXCEPT / NOT » (11 % dans le corpus reel)",
        }],
        "duree_minutes": 90, "bareme_total": 50,
        "session": {"papier_jumeau": BP_P2, "numero_session": 1,
                    "regle": "aucune donnee, aucun contexte ni aucun fait partages entre les deux papers de la session ; un QCM du Paper 1 ne donne jamais la reponse d'une question du Paper 2 (assurance : principes, avantages, risques non assurables ; services des banques ; ordre permanent et virement ; interet simple ; restrictions a l'importation ; balance commerciale ; conteneurisation ; promotion des ventes ; inconvenients de la publicite ; protection des consommateurs)"},
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


if __name__ == "__main__":
    main()
