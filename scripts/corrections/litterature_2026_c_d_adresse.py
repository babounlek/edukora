# Correction ponctuelle (2026-11-10) : l'adresse de la Lesson « Litterature Probatoire C et D 2026 » (ex « A, C et D ») suit le titre.
# litterature-probatoire-a-c-et-d-2026 -> litterature-probatoire-c-et-d-2026. L'ancienne adresse reste valable une fois
# catalog/slugs_renommes.json deploye (entree "lesson" ajoutee dans le depot). Local :
#   docker exec -i edukora-backend-1 python manage.py shell < scripts/corrections/litterature_2026_c_d_adresse.py
# Prod : ssh deploy@157.245.140.254 "docker exec -i edukora-backend-1 python manage.py shell" < ce fichier ; puis indexer_recherche.
import logging; logging.disable(logging.CRITICAL)
from django.db import transaction
from catalog.models import Lesson, generate_unique_slug
ANCIEN = "litterature-probatoire-a-c-et-d-2026"
with transaction.atomic():
    l = Lesson.objects.get(slug=ANCIEN)
    assert l.title == "Littérature Probatoire C et D 2026", l.title
    nouveau = generate_unique_slug(Lesson, l.title, existing_pk=l.pk)
    print("SLUG", ANCIEN, "->", nouveau)
    Lesson.objects.filter(pk=l.pk).update(slug=nouveau)
print("fin")
