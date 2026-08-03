# Generated manually - ajout en 3 étapes (champ non contraint -> backfill -> contrainte
# unique) car la table Lesson contient déjà des lignes : impossible d'ajouter
# directement un champ unique sans valeur par défaut exploitable pour l'existant.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0026_country_actif"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="slug",
            field=models.SlugField(blank=True, default="", max_length=255),
        ),
    ]
