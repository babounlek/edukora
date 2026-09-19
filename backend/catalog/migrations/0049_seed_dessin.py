from django.db import migrations


def seed_dessin(apps, schema_editor):
    # Même procédé que 0044_seed_espagnol : une Subject par pays (Subject est rattaché
    # à Country depuis 0015_country), pour tous les pays déjà en base. Les pays créés
    # après cette migration l'obtiennent par seed_country.SUBJECTS.
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="DESSIN", defaults={"label": "Dessin"})


def unseed_dessin(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="DESSIN").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0048_alter_figure_legende"),
    ]

    operations = [
        migrations.RunPython(seed_dessin, unseed_dessin),
    ]
