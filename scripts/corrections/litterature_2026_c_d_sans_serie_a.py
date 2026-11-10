# Correction ponctuelle (2026-11-10) : la Lesson « Litterature Probatoire A, C et D 2026 » (lot 20261110-210733-01d0a376,
# Ndolomath page A, C et D mais en-tete du sujet « PREMIERE C ») ne doit PAS etre rattachee a la serie A : l'epreuve A 2026
# a sa propre Lesson (3123). On retire la serie A de la lecon, de ses cours propres et des 30 QCM pc26 de Litterature.
# Applique en LOCAL ; a rejouer en PROD :
#   cmd /c "ssh deploy@157.245.140.254 docker exec -i edukora-backend-1 python manage.py shell < scripts/corrections/litterature_2026_c_d_sans_serie_a.py"
# puis : docker exec edukora-backend-1 python manage.py indexer_recherche ; ... calculer_frequences_cours
# Etat d'avant, pour retour arriere : titre « Littérature Probatoire A, C et D 2026 », cursus A, C, D (lecon, cours propres, QCM).
import logging; logging.disable(logging.CRITICAL)
from django.db import transaction
from catalog.models import Lesson, Cursus, Cours
from catalog.ingestion import build_lesson_title
from quiz.models import CompetenceItem
cd = list(Cursus.objects.filter(country__code__iexact="cm", examen__iexact="probatoire", series__code__in=["C", "D"]).select_related("series"))
assert len(cd) == 2, cd
with transaction.atomic():
    l = Lesson.objects.get(slug="litterature-probatoire-a-c-et-d-2026")
    assert l.year == 2026 and l.subject.code == "LITTERATURE", (l.year, l.subject.code)
    avant = (l.title, sorted(c.series.code for c in l.cursus.all()))
    l.cursus.set(cd)
    l.title = build_lesson_title(l.subject, list(l.cursus.all().order_by("examen", "series__code")), l.year, l.origine, l.etablissement, nature_epreuve=l.nature_epreuve or "", partie_epreuve_francais=l.partie_epreuve_francais or "", variante_sujet=l.variante_sujet or "", filiere_serie_a=l.filiere_serie_a or "", numero_paper=l.numero_paper)
    l.save(update_fields=["title"])
    nc = 0
    for c in Cours.objects.filter(rappels_source__exercise__lesson=l).distinct():
        if not c.rappels_source.exclude(exercise__lesson=l).exists() and "A" in {x.series.code for x in c.cursus.all()}:
            c.cursus.set(cd); nc += 1
    qs = CompetenceItem.objects.filter(external_id__contains="-litterature-pc26-")
    ni = 0
    for it in qs:
        if "A" in {x.series.code for x in it.cursus.all()}:
            it.cursus.set(cd); ni += 1
print("AVANT", avant)
print("APRES", l.title, sorted(c.series.code for c in l.cursus.all()), "| cours mis a jour", nc, "| QCM mis a jour", ni, "sur", qs.count())
print('fin')
