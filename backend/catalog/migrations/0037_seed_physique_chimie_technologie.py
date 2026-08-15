from django.db import migrations


def seed_physique_chimie_technologie(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(
            country=country, code="PHYSIQUE_CHIMIE_TECH",
            defaults={"label": "Physique-Chimie-Technologie"},
        )


def unseed_physique_chimie_technologie(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="PHYSIQUE_CHIMIE_TECH").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0036_seed_informatique"),
    ]

    operations = [
        migrations.RunPython(seed_physique_chimie_technologie, unseed_physique_chimie_technologie),
    ]
