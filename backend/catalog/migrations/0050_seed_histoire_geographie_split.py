from django.db import migrations


def seed_histoire_geographie_split(apps, schema_editor):
    # Même procédé que 0039_seed_physique_chimie_split : HISTOIRE_GEO reste le code
    # combiné (voir SUBJECT_FAMILIES dans catalog.models), HISTOIRE et GEOGRAPHIE sont
    # désormais aussi des Subject à part entière pour les épreuves qui n'examinent
    # qu'une seule des deux disciplines.
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="HISTOIRE", defaults={"label": "Histoire"})
        Subject.objects.get_or_create(country=country, code="GEOGRAPHIE", defaults={"label": "Géographie"})


def unseed_histoire_geographie_split(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code__in=["HISTOIRE", "GEOGRAPHIE"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0049_seed_dessin"),
    ]

    operations = [
        migrations.RunPython(seed_histoire_geographie_split, unseed_histoire_geographie_split),
    ]
