from django.db import migrations

# (duration_days, price, label)
DURATIONS = [
    (7, 500, "7 jours"),
    (30, 1500, "1 mois"),
    (365, 9000, "1 an"),
]

EXAMEN_LABELS = {
    "BEPC": "BEPC",
    "PROBATOIRE": "Probatoire",
    "BAC": "BAC",
    "AUTRE": "Devoir surveille / Autre",
}


def seed_plans(apps, schema_editor):
    Cursus = apps.get_model("catalog", "Cursus")
    Plan = apps.get_model("subscriptions", "Plan")

    # Modèles historiques : pas de __str__/get_FOO_display, on reconstruit le libellé à la main.
    for cursus in Cursus.objects.select_related("series").all():
        examen_label = EXAMEN_LABELS.get(cursus.examen, cursus.examen)
        cursus_label = f"{examen_label} Série {cursus.series.code}" if cursus.series_id else examen_label

        for duration_days, price, label in DURATIONS:
            Plan.objects.get_or_create(
                cursus=cursus,
                duration_days=duration_days,
                defaults={"name": f"{cursus_label} - {label}", "price": price, "is_active": True},
            )


def unseed_plans(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(duration_days__in=[7, 30, 365]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0001_initial"),
        ("catalog", "0006_remove_lesson_cursus_lesson_cursus"),
    ]

    operations = [
        migrations.RunPython(seed_plans, unseed_plans),
    ]
