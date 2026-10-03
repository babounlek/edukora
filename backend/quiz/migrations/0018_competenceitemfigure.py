import django.db.models.deletion
import quiz.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0017_gain_xp_jour_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompetenceItemFigure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.CharField(help_text="Identifiant du placeholder dans le Markdown (ex: fig-1) - unique seulement au sein d'un item.", max_length=255)),
                ("image", models.FileField(upload_to=quiz.models._competence_item_figure_upload_to)),
                ("type_figure", models.CharField(blank=True, help_text="Ex : courbe, figure geometrique, schema, graphique, circuit (valeur libre, non contrainte).", max_length=30)),
                ("legende", models.TextField(blank=True)),
                ("origine", models.CharField(choices=[("ENONCE", "Énoncé"), ("CORRIGE", "Corrigé")], default="CORRIGE", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="figures", to="quiz.competenceitem")),
            ],
            options={
                "ordering": ["item", "external_id"],
                "constraints": [models.UniqueConstraint(fields=("item", "external_id"), name="unique_competenceitemfigure_par_item")],
            },
        ),
    ]
