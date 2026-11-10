from catalog.models import Lesson, Cours

l = Lesson.objects.get(pk=2071)
print(l.title, [c.series.code for c in l.cursus.all()])
cs = Cours.objects.filter(rappels_source__exercise__lesson=l).distinct()
print(cs.count(), sorted(set(tuple(sorted(x.series.code for x in c.cursus.all())) for c in cs)))
