# Correction ponctuelle (2026-11-10) : l EPS Probatoire 2024 (Lesson 2071, 18 cours propres) n etait rattachee qu aux series C, D, E.
# Elle est commune a A, C, D, E, TI comme les autres EPS du Probatoire. Deja appliquee en LOCAL ; a rejouer en PROD :
#   ssh deploy@157.245.140.254 "docker exec -i edukora-backend-1 python manage.py shell" < scripts/corrections/eps_probatoire_2024_toutes_series.py
# puis (titre change) : docker exec edukora-backend-1 python manage.py indexer_recherche ; ... calculer_frequences_cours
# Etat d avant, pour retour arriere : titre "Éducation physique et sportive Probatoire C, D et E 2024", cursus C, D, E (lecon et 18 cours).
import logging; logging.disable(logging.CRITICAL)
from django.db import transaction
from catalog.models import Lesson, Cursus, Cours
from catalog.ingestion import build_lesson_title
tous = list(Cursus.objects.filter(country__code__iexact="cm", examen__iexact="probatoire", series__code__in=["A","C","D","E","TI"]).select_related("series"))
assert len(tous) == 5
with transaction.atomic():
    l = Lesson.objects.get(pk=2071)
    avant = (l.title, sorted(c.series.code for c in l.cursus.all()))
    l.cursus.set(tous)
    l.title = build_lesson_title(l.subject, list(l.cursus.all().order_by("examen","series__code")), l.year, l.origine, l.etablissement, nature_epreuve=l.nature_epreuve or "", partie_epreuve_francais=l.partie_epreuve_francais or "", variante_sujet=l.variante_sujet or "", filiere_serie_a=l.filiere_serie_a or "", numero_paper=l.numero_paper)
    l.save(update_fields=["title"])
    n = 0
    for c in Cours.objects.filter(rappels_source__exercise__lesson=l).distinct():
        if not c.rappels_source.exclude(exercise__lesson=l).exists():
            c.cursus.set(tous); n += 1
print("AVANT", avant); print("APRES", l.title, sorted(c.series.code for c in l.cursus.all()), "| cours mis à jour", n)
