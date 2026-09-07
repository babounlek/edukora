from django.db import migrations


def seed_allemand(apps, schema_editor):
    # Même procédé que 0044_seed_espagnol : une Subject par pays, pour tous les pays
    # déjà en base. Les pays créés après cette migration l'obtiennent par
    # seed_country.SUBJECTS.
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="ALLEMAND", defaults={"label": "Allemand"})


def unseed_allemand(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="ALLEMAND").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0050_seed_histoire_geographie_split"),
    ]

    operations = [
        migrations.RunPython(seed_allemand, unseed_allemand),
    ]
