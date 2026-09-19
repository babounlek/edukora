"""Suite de fix_rendu_dollars.py : reporte l'échappement des `$` des 3 corrigés de Question dans les JSON
sources, puis recompile uniquement les Exercise/Lesson concernés (jamais tout le corpus)."""
import json
from pathlib import Path

from catalog.models import Question

INGEST = Path("/app/ingest")
src = open("/app/ingest/_audit/fix_rendu_dollars.py", encoding="utf-8").read().split("_SOURCES = {}")[0]
exec(src.split("bilan = []")[0])

for pk in (54684, 56093, 56640):
    q = Question.objects.select_related("exercise__lesson").get(pk=pk)
    lesson, exercise = q.exercise.lesson, q.exercise
    stem = lesson.epreuve_source.removesuffix(".pdf")
    fichier = None
    for d in INGEST.glob(f"*/{stem}"):
        for f in d.glob("*_exercice_*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if str(data.get("numero_exercice")) == str(exercise.numero_exercice):
                fichier = (f, data)
    if not fichier:
        print(pk, "source introuvable", stem)
    else:
        f, data = fichier
        cible = next((x for x in data["questions"] if str(x.get("numero")) == str(q.numero)), None)
        if cible is None:
            print(pk, "question absente de la source")
        else:
            nouveau = escape_dollars(cible["corrige_markdown"])
            if nouveau != cible["corrige_markdown"]:
                cible["corrige_markdown"] = nouveau
                f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(pk, "source patchée", f.name)
            else:
                print(pk, "source déjà à jour")
    exercise.compile_from_questions()
    lesson.compile_from_exercises()
    print(pk, "recompilé", lesson.slug)
