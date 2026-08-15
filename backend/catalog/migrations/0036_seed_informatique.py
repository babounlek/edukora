from django.db import migrations


def seed_informatique(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="INFORMATIQUE", defaults={"label": "Informatique"})


def unseed_informatique(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="INFORMATIQUE").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0035_cours_slug_unique"),
    ]

    operations = [
        migrations.RunPython(seed_informatique, unseed_informatique),
    ]
