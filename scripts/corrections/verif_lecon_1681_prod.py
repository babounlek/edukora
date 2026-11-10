from catalog.models import Lesson, Cours, Exercise, Question

l = Lesson.objects.filter(pk=1681).first()
print("LECON", l and (l.title, l.year, l.epreuve_source, l.statut))
if l:
    qs = Question.objects.filter(exercise__lesson=l)
    print("exercices", l.exercises.count(), "questions", qs.count())
    cs = Cours.objects.filter(rappels_source__exercise__lesson=l).distinct()
    print("cours lies", cs.count())
    # reperage des donnees utilisateur rattachees aux questions / exercices (relations inverses)
    for model in (Question, Exercise):
        for rel in model._meta.related_objects:
            try:
                n = rel.related_model.objects.filter(**{rel.field.name + "__in": (qs if model is Question else l.exercises.all())}).count()
            except Exception as e:  # noqa
                n = "?"
            if n:
                print("  relation", model.__name__, "<-", rel.related_model.__name__, rel.field.name, n)
print("AUTRES lecons Informatique 2026 serie A", list(Lesson.objects.filter(subject__code="INFORMATIQUE", year=2026, cursus__series__code="A", cursus__examen__iexact="probatoire").values_list("pk", "title")))
