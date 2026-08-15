from django.db import migrations


def seed_espagnol(apps, schema_editor):
    # Même procédé que 0042_seed_education_civique : une Subject par pays (Subject est
    # rattaché à Country depuis 0015_country), pour tous les pays déjà en base. Les pays
    # créés après cette migration l'obtiennent par seed_country.SUBJECTS.
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="ESPAGNOL", defaults={"label": "Espagnol"})


def unseed_espagnol(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="ESPAGNOL").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0043_tag_savoir_officiel"),
    ]

    operations = [
        migrations.RunPython(seed_espagnol, unseed_espagnol),
    ]
