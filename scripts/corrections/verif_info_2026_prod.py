from catalog.models import Lesson, Cours, Question, Tag
from quiz.models import CompetenceItem

ls = list(Lesson.objects.filter(subject__code="INFORMATIQUE", year=2026, cursus__series__code="A", cursus__examen__iexact="probatoire").distinct())
for l in ls:
    qs = Question.objects.filter(exercise__lesson=l)
    print("LECON", l.pk, l.title, l.epreuve_source, l.statut, "| exercices", l.exercises.count(), "| questions", qs.count(), "| pdf", bool(l.sujet_pdf))
    cs = Cours.objects.filter(rappels_source__exercise__lesson=l).distinct()
    print("  cours lies", cs.count(), "| rappels sans cours", l.exercises.filter(rappels_de_methode__cours__isnull=True).count())
print("Lecon 1681 presente :", Lesson.objects.filter(pk=1681).exists())
for n in ("gravure de disque optique", "compression de fichier"):
    t = Tag.objects.filter(name=n).first()
    print("quiz", n, t and CompetenceItem.objects.filter(theme=t, statut="VALIDE").count())
