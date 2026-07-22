from django.db import migrations

SUBJECTS = [
    ("MATHS", "Mathématiques"),
    ("PHYSIQUE_CHIMIE", "Physique-Chimie"),
    ("SVT", "Sciences de la Vie et de la Terre"),
    ("FRANCAIS", "Français"),
    ("PHILOSOPHIE", "Philosophie"),
    ("HISTOIRE_GEO", "Histoire-Géographie"),
    ("ANGLAIS", "Anglais"),
    ("ECONOMIE", "Économie"),
    ("DROIT", "Droit"),
]

SERIES = [
    ("A", "Lettres-Philo"),
    ("SES", "Sciences Économiques et Sociales"),
    ("C", "Maths"),
    ("D", "Sciences"),
    ("E", "Mathématiques et Techniques"),
    ("TI", "Techniques Industrielles"),
    ("COM", "Techniques Commerciales et de Gestion"),
]


def seed_referentiel(apps, schema_editor):
    Subject = apps.get_model("catalog", "Subject")
    Series = apps.get_model("catalog", "Series")
    Cursus = apps.get_model("catalog", "Cursus")

    Subject.objects.bulk_create([Subject(code=code, label=label) for code, label in SUBJECTS])
    series_objs = Series.objects.bulk_create([Series(code=code, label=label) for code, label in SERIES])

    Cursus.objects.create(examen="BEPC", series=None)
    for series in series_objs:
        Cursus.objects.create(examen="PROBATOIRE", series=series)
        Cursus.objects.create(examen="BAC", series=series)


def unseed_referentiel(apps, schema_editor):
    apps.get_model("catalog", "Cursus").objects.all().delete()
    apps.get_model("catalog", "Series").objects.all().delete()
    apps.get_model("catalog", "Subject").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_series_code"),
    ]

    operations = [
        migrations.RunPython(seed_referentiel, unseed_referentiel),
    ]
