from catalog.models import Lesson

l = Lesson.objects.get(pk=1475)
print("ETAT 1475", repr(l.title), l.year)
