from django.db import migrations


def seed_litterature(apps, schema_editor):
    Subject = apps.get_model("catalog", "Subject")
    Subject.objects.get_or_create(code="LITTERATURE", defaults={"label": "Littérature"})


def unseed_litterature(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code="LITTERATURE").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0010_cours_rappeldemethode"),
    ]

    operations = [
        migrations.RunPython(seed_litterature, unseed_litterature),
    ]
