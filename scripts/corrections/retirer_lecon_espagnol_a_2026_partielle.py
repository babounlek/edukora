# Retrait LOCAL de la lecon « Espagnol Probatoire A 2026 » (Lesson 3107) : sujet PARTIEL (partie III seule, « Parte incompleta »),
# laisse de cote par l'utilisateur et jamais publie. Retrait demande le 2026-11-11 pour aligner le local sur la production.
# Les 4 cours crees pour elle seule (16579 a 16582) partent aussi ; le cours 12079, partage, reste.
# Le dossier d'ingestion est range dans backend/ingest/_retire/ : une reingestion recreera la lecon si un sujet complet arrive.
#   docker exec -i edukora-backend-1 python manage.py shell < scripts/corrections/retirer_lecon_espagnol_a_2026_partielle.py
import logging; logging.disable(logging.CRITICAL)
from django.db import transaction
from catalog.models import Lesson, Cours, Question
l = Lesson.objects.get(pk=3107)
assert l.title == "Espagnol Probatoire A 2026" and l.year == 2026 and l.subject.code == "ESPAGNOL", (l.title, l.year)
exclusifs = [c for c in Cours.objects.filter(rappels_source__exercise__lesson=l).distinct() if not c.rappels_source.exclude(exercise__lesson=l).exists()]
print("AVANT exercices", l.exercises.count(), "questions", Question.objects.filter(exercise__lesson=l).count(), "cours exclusifs", sorted(c.pk for c in exclusifs))
assert sorted(c.pk for c in exclusifs) == [16579, 16580, 16581, 16582], [c.pk for c in exclusifs]
with transaction.atomic():
    for e in list(l.exercises.all()):
        e.delete()  # Exercise.lesson est PROTECT : exercices d'abord
    l.delete()
    for c in exclusifs:
        c.delete()
print("APRES lecon existe", Lesson.objects.filter(pk=3107).exists(), "| cours restants", Cours.objects.filter(pk__in=[16579, 16580, 16581, 16582, 12079]).count())
print("fin")
