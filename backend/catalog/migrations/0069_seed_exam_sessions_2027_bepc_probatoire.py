from django.db import migrations

# Calendrier officiel 2027 (Cameroun) annoncé, communiqué par l'utilisateur le
# 2026-11-02 : BEPC du 31 mai au 4 juin, Probatoire général du 7 au 11 juin. Remplace
# l'estimation automatique (2026 + 1 an, "estimee=True") par la vraie session ; le BAC
# et le GCE restent estimés tant que leur calendrier n'est pas publié.
SESSIONS_2027 = [
    ("BEPC", "2027-05-31", "2027-06-04"),
    ("PROBATOIRE", "2027-06-07", "2027-06-11"),
]


def seed_sessions_2027(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    for examen, date_debut, date_fin in SESSIONS_2027:
        ExamSession.objects.update_or_create(
            country=cm, examen=examen, annee=2027,
            defaults={"date_debut": date_debut, "date_fin": date_fin},
        )


def unseed_sessions_2027(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    ExamSession.objects.filter(country=cm, examen__in=[e for e, _, _ in SESSIONS_2027], annee=2027).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0068_gce_cinematic_art"),
    ]

    operations = [
        migrations.RunPython(seed_sessions_2027, unseed_sessions_2027),
    ]
