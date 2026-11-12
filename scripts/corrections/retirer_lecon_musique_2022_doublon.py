# Retrait LOCAL de la lecon « Musique Probatoire C, D, E et TI 2022 » (Lesson 3137) : sujet mot pour mot identique a Musique 2026
# (Lesson 3104). Jamais publiee. Retrait demande par l'utilisateur le 2026-11-11 pour aligner le local sur la production.
# Les cours crees pour elle seule partent aussi ; les cours partages restent. Le dossier d'ingestion est range dans backend/ingest/_retire/.
#   docker exec -i edukora-backend-1 python manage.py shell < scripts/corrections/retirer_lecon_musique_2022_doublon.py
import logging; logging.disable(logging.CRITICAL)
from django.db import transaction
from catalog.models import Lesson, Cours, Question
l = Lesson.objects.get(pk=3137)
assert l.title == "Musique Probatoire C, D, E et TI 2022" and l.year == 2022 and l.subject.code == "MUSIQUE", (l.title, l.year)
exclusifs = [c for c in Cours.objects.filter(rappels_source__exercise__lesson=l).distinct() if not c.rappels_source.exclude(exercise__lesson=l).exists()]
print("AVANT exercices", l.exercises.count(), "questions", Question.objects.filter(exercise__lesson=l).count(), "cours exclusifs", sorted(c.pk for c in exclusifs))
with transaction.atomic():
    for e in list(l.exercises.all()):
        e.delete()  # Exercise.lesson est PROTECT : exercices d'abord
    l.delete()
    for c in exclusifs:
        c.delete()
print("APRES lecon existe", Lesson.objects.filter(pk=3137).exists(), "| lecons totales", Lesson.objects.count())
print("fin")
