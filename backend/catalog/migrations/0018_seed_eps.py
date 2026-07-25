from django.db import migrations


def seed_eps(apps, schema_editor):
    Subject = apps.get_model("catalog", "Subject")
    Subject.objects.get_or_create(code="EPS", defaults={"label": "Éducation physique et sportive"})


def unseed_eps(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="EPS").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0017_examsession"),
    ]

    operations = [
        migrations.RunPython(seed_eps, unseed_eps),
    ]
