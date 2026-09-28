from django.db import migrations

# Dernier jour de chaque session 2026 (Cameroun) - calendrier officiel communiqué par
# l'utilisateur le 2026-09-28, complète les date_debut saisies en 0056. Voir
# ExamSession.date_fin : sert de base à la durée d'accès facturée (jusqu'au dernier
# papier, pas le premier).
DATES_FIN_2026 = [
    ("BEPC", "2026-06-04"),
    ("PROBATOIRE", "2026-06-12"),
    ("BAC", "2026-05-30"),
    ("GCE", "2026-06-18"),
]


def seed_dates_fin(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    for examen, date_fin in DATES_FIN_2026:
        ExamSession.objects.filter(country=cm, examen=examen, annee=2026).update(date_fin=date_fin)


def unseed_dates_fin(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    ExamSession.objects.filter(country=cm, examen__in=[e for e, _ in DATES_FIN_2026], annee=2026).update(date_fin=None)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0057_examsession_date_fin"),
    ]

    operations = [
        migrations.RunPython(seed_dates_fin, unseed_dates_fin),
    ]
