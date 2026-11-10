# Retrait de la lecon 1681 (Informatique Probatoire A 2026, ancienne transcription)
# remplacee par la transcription Ndolomath (dossier probatoire-a-informatique-2026-officiel-cameroun).
# Seule la lecon est supprimee (ses exercices, questions, rappels et figures partent en cascade) ;
# les cours restent : ils servent aussi aux quiz et peuvent etre reutilises par la nouvelle epreuve.
from django.db import transaction
from catalog.models import Lesson, Cours, Exercise, Question

l = Lesson.objects.get(pk=1681)
assert l.title == "Informatique Probatoire A 2026", l.title
assert l.year == 2026 and l.subject.code == "INFORMATIQUE", (l.year, l.subject.code)
cours_ids = list(Cours.objects.filter(rappels_source__exercise__lesson=l).distinct().values_list("id", flat=True))
print("AVANT exercices", l.exercises.count(), "questions", Question.objects.filter(exercise__lesson=l).count(), "cours lies", len(cours_ids))
with transaction.atomic():
    for e in list(l.exercises.all()):
        e.delete()  # Exercise.lesson est PROTECT : on supprime les exercices d'abord
    l.delete()
print("APRES lecon existe", Lesson.objects.filter(pk=1681).exists(), "| cours conserves", Cours.objects.filter(pk__in=cours_ids).count(), "/", len(cours_ids))
