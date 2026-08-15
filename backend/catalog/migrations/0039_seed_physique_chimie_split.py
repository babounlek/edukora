from django.db import migrations


def seed_physique_chimie_split(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="PHYSIQUE", defaults={"label": "Physique"})
        Subject.objects.get_or_create(country=country, code="CHIMIE", defaults={"label": "Chimie"})


def unseed_physique_chimie_split(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code__in=["PHYSIQUE", "CHIMIE"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0038_add_nature_epreuve"),
    ]

    operations = [
        migrations.RunPython(seed_physique_chimie_split, unseed_physique_chimie_split),
    ]
