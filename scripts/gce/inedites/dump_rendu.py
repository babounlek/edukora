"""Ecrit le dump des champs Markdown d'une epreuve inedite pour le VRAI moteur de rendu (remark-math, remark-gfm, rehype-katex).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\dump_rendu.py ep-....json dump.json
    cd frontend && AUDIT_RENDU_DUMP=<dump.json> npx vitest run src/lib/audit-rendu.test.ts

Un champ sur deux est ecrit en pipeline « full » (enonces, corriges, supports) et les options de QCM et grilles en « bare ».
"""
import json
import sys


def main():
    ep = json.load(open(sys.argv[1], encoding="utf8"))
    recs = []
    for ex in ep["exercices"]:
        num = ex["numero_exercice"]
        if ex.get("enonce_intro_markdown"):
            recs.append(dict(model="ExerciceInedite", pk=1, ref=f"intro{num}", field="enonce_intro_markdown", pipeline="full", markdown=ex["enonce_intro_markdown"]))
        for q in ex["questions"]:
            ref = f"{num}.{q['numero']}"
            recs.append(dict(model="QuestionInedite", pk=1, ref=ref, field="enonce_markdown", pipeline="full", markdown=q["enonce_markdown"]))
            recs.append(dict(model="QuestionInedite", pk=1, ref=ref, field="corrige_markdown", pipeline="full", markdown=q["corrige_markdown"]))
            for c in q.get("choix") or []:
                recs.append(dict(model="QuestionInedite", pk=1, ref=ref + c["lettre"], field="choix", pipeline="bare", markdown=c["texte"]))
            for c in q.get("criteres_notation") or []:
                recs.append(dict(model="QuestionInedite", pk=1, ref=ref, field="critere", pipeline="bare", markdown=c["libelle"]))
    json.dump(recs, open(sys.argv[2], "w", encoding="utf8"), ensure_ascii=False)
    print(len(recs), "champs")


if __name__ == "__main__":
    main()
