# Peuple le slug de chaque Cours existant depuis son titre, avec suffixe -2/-3... en
# cas de collision. Logique dupliquée ici plutôt qu'importée de catalog.models : une
# migration de données doit rester valide même si le modèle change ensuite (voir
# apps.get_model, qui donne la version HISTORIQUE du modèle, sans ses méthodes custom).

from django.db import migrations
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    Cours = apps.get_model("catalog", "cours")
    existing_slugs = set()
    for cours in Cours.objects.all().order_by("pk"):
        base = slugify(cours.titre) or "cours"
        slug = base
        counter = 2
        while slug in existing_slugs:
            slug = f"{base}-{counter}"
            counter += 1
        existing_slugs.add(slug)
        cours.slug = slug
        cours.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0033_cours_slug"),
    ]

    operations = [
        migrations.RunPython(backfill_slugs, noop_reverse),
    ]
