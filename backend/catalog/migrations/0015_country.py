from django.db import migrations, models
import django.db.models.deletion


def seed_and_backfill(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Cursus = apps.get_model("catalog", "Cursus")
    cameroun, _ = Country.objects.get_or_create(code="CM", defaults={"label": "Cameroun"})
    Cursus.objects.filter(country__isnull=True).update(country=cameroun)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0014_lesson_etablissement_lesson_origine"),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=10, unique=True)),
                ("label", models.CharField(max_length=100)),
            ],
            options={
                "ordering": ["label"],
                "verbose_name_plural": "countries",
            },
        ),
        migrations.AddField(
            model_name="cursus",
            name="country",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="cursus_set", to="catalog.country",
            ),
        ),
        migrations.RunPython(seed_and_backfill, noop),
        migrations.AlterField(
            model_name="cursus",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cursus_set", to="catalog.country",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="cursus",
            name="unique_cursus_combo",
        ),
        migrations.AddConstraint(
            model_name="cursus",
            constraint=models.UniqueConstraint(fields=["country", "examen", "series"], name="unique_cursus_combo"),
        ),
        migrations.AlterModelOptions(
            name="cursus",
            options={"ordering": ["country", "examen", "series"], "verbose_name_plural": "cursus"},
        ),
    ]
