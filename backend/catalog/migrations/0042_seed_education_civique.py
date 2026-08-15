from django.db import migrations


def seed_education_civique(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(
            country=country, code="EDUCATION_CIVIQUE", defaults={"label": "Éducation Civique"},
        )


def unseed_education_civique(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="EDUCATION_CIVIQUE").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0041_widen_question_numero"),
    ]

    operations = [
        migrations.RunPython(seed_education_civique, unseed_education_civique),
    ]
