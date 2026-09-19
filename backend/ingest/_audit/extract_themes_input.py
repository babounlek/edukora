import json, sys
from collections import Counter
from catalog.models import Question, Lesson, Tag
slugs = sys.argv[1].split(",") if len(sys.argv) > 1 else []
for slug in slugs:
    lesson = Lesson.objects.select_related("subject").get(slug=slug)
    qs = Question.objects.filter(exercise__lesson=lesson, themes__isnull=True).select_related("exercise").order_by("exercise__numero_exercice", "ordre")
    usage = Counter()
    for name in Question.themes.through.objects.filter(question__exercise__lesson__subject=lesson.subject, question__exercise__lesson__year__gte=2000).values_list("tag__name", flat=True):
        usage[name] += 1
    out = {
        "lesson": slug, "matiere": lesson.subject.label, "epreuve_source": lesson.epreuve_source,
        "questions": [{"pk": q.pk, "exercice": q.exercise.numero_exercice, "numero": q.numero,
                       "enonce": (q.enonce_markdown or "")[:700], "corrige": (q.corrige_markdown or "")[:350]} for q in qs],
        "vocabulaire_existant": [n for n, _ in usage.most_common(250)],
    }
    path = f"/app/ingest/_audit/themes_in_{slug}.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(slug, len(out["questions"]), "questions,", len(out["vocabulaire_existant"]), "tags de vocabulaire")
