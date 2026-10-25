from django.db import migrations

# Cinematic Art (0736) : nouvelle matière de l'A Level, syllabus publié par le GCE Board le 2025-10-13 (camgceb.org).
CODE = "GCE_CINEMATIC_ART"


def appliquer(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    Subject.objects.get_or_create(
        country=cm, code=CODE,
        defaults={"label": "Cinematic Art", "langue": "en", "equivalent_code": "DESSIN",
                  "codes_officiels": {"GCE_AL": "0736"}},
    )


def annuler(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    # Une matière déjà utilisée par du contenu ne se supprime pas : l'annulation échoue (PROTECT), voulu.
    Subject.objects.filter(country=cm, code=CODE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0067_gce_matieres_codes_officiels"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
