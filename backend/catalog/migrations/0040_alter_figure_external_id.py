from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0039_seed_physique_chimie_split"),
    ]

    operations = [
        migrations.AlterField(
            model_name="figure",
            name="external_id",
            field=models.CharField(
                max_length=255,
                help_text="Identifiant du placeholder dans le Markdown (ex: fig-1) - unique seulement au sein d'un exercice.",
            ),
        ),
    ]
