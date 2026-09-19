from django.db import migrations


def seed_ti_informatique_split(apps, schema_editor):
    # Même procédé que 0050_seed_histoire_geographie_split : INFORMATIQUE reste le code
    # combiné (voir SUBJECT_FAMILIES dans catalog.models), PROGRAMMATION/
    # SYSTEMES_INFORMATION/RESEAUX_SECURITE sont désormais aussi des Subject à
    # part entière pour les épreuves de Série TI qui n'examinent qu'une seule discipline.
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        Subject.objects.get_or_create(country=country, code="PROGRAMMATION", defaults={"label": "Programmation"})
        Subject.objects.get_or_create(
            country=country, code="SYSTEMES_INFORMATION", defaults={"label": "Systèmes d'Information"},
        )
        Subject.objects.get_or_create(
            country=country,
            code="RESEAUX_SECURITE",
            defaults={"label": "Réseaux, Internet et Sécurité Informatique"},
        )


def unseed_ti_informatique_split(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(
        code__in=["PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0052_alter_lesson_coefficient"),
    ]

    operations = [
        migrations.RunPython(seed_ti_informatique_split, unseed_ti_informatique_split),
    ]
