# Lecon 1475 (Espagnol Probatoire A) : la meme epreuve que le PDF Ndolomath 2025, mais sans annee en base.
# Mode lecture par defaut ; APPLIQUER = True pour ecrire.
from django.db import transaction
from catalog.models import Lesson
from catalog.ingestion import build_lesson_title

APPLIQUER = True

l = Lesson.objects.get(pk=1475)
print("AVANT", l.pk, repr(l.title), l.year, l.subject.code, l.origine, l.etablissement, l.statut, [str(c) for c in l.cursus.all()], l.epreuve_source)
print("exercices", l.exercises.count(), "| autres lecons Espagnol Probatoire A 2025 :",
      list(Lesson.objects.filter(subject=l.subject, year=2025, cursus__series__code="A", cursus__examen__iexact="probatoire").values_list("pk", "title")))
titre = build_lesson_title(l.subject, list(l.cursus.all().order_by("examen", "series__code")), 2025, l.origine, l.etablissement,
                           nature_epreuve=l.nature_epreuve or "", partie_epreuve_francais=l.partie_epreuve_francais or "",
                           variante_sujet=l.variante_sujet or "", filiere_serie_a=l.filiere_serie_a or "", numero_paper=l.numero_paper)
print("TITRE PROPOSE", repr(titre))
if APPLIQUER:
    with transaction.atomic():
        l.year = 2025
        l.title = titre
        l.save(update_fields=["year", "title"])
    l.refresh_from_db()
    print("APRES", l.pk, repr(l.title), l.year)

print("fin")
