from django.db import migrations

# Matières examinées au Probatoire A camerounais (Musique, Travail manuel) - demande utilisateur du
# 2026-11-09. Même procédé que 0049_seed_dessin : une Subject par pays déjà en base ; les pays créés
# plus tard l'obtiennent par seed_country.SUBJECTS.
MATIERES = (("MUSIQUE", "Musique"), ("TRAVAIL_MANUEL", "Travail manuel"))


def seed(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    for country in Country.objects.all():
        for code, label in MATIERES:
            Subject.objects.get_or_create(country=country, code=code, defaults={"label": label})


def unseed(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code__in=[c for c, _ in MATIERES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0069_seed_exam_sessions_2027_bepc_probatoire"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
