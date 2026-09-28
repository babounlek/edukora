from django.db import migrations

# Ancrage historique 2026 (Cameroun) - premier jour de chaque session, calendrier
# officiel communiqué par l'utilisateur le 2026-09-28. Sert d'ancre à
# ExamSession.compte_a_rebours_pour / subscriptions.Plan._calculer_duree_jusqua_examen
# pour estimer 2027 (+1 an, "estimee=True") tant que le vrai calendrier 2027 n'est pas
# publié - voir ExamSession.compte_a_rebours_pour pour le mécanisme.
DATES_2026 = [
    ("BEPC", "2026-06-01"),
    ("PROBATOIRE", "2026-06-08"),
    ("BAC", "2026-05-25"),
    ("GCE", "2026-06-02"),
]

# Ces 3 lignes 2027 avaient été saisies à la main pendant les tests (BAC et
# PROBATOIRE tombant le même jour, 2027-05-24 - aucun calendrier officiel ne les
# confond) plutôt qu'à partir d'un vrai calendrier publié - décision utilisateur du
# 2026-09-28 : les retirer pour que 2027 retombe sur l'estimation automatique
# (2026 + 1 an) tant que le calendrier officiel 2027 n'existe pas.
EXAMENS_2027_A_RETIRER = ["BEPC", "PROBATOIRE", "BAC"]


def seed_exam_sessions_2026(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    for examen, date_debut in DATES_2026:
        ExamSession.objects.update_or_create(
            country=cm, examen=examen, annee=2026, defaults={"date_debut": date_debut}
        )
    ExamSession.objects.filter(country=cm, examen__in=EXAMENS_2027_A_RETIRER, annee=2027).delete()


def unseed_exam_sessions_2026(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    ExamSession.objects.filter(country=cm, examen__in=[e for e, _ in DATES_2026], annee=2026).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0055_alter_cursus_examen_alter_examenlabel_examen_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_exam_sessions_2026, unseed_exam_sessions_2026),
    ]
