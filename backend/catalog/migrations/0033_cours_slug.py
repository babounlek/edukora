# Même procédé en 3 étapes que 0027/0028/0029 pour Lesson.slug (champ non contraint ->
# backfill -> contrainte unique) : la table Cours contient déjà des lignes, impossible
# d'ajouter directement un champ unique sans valeur par défaut exploitable pour l'existant.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0032_temoignage"),
    ]

    operations = [
        migrations.AddField(
            model_name="cours",
            name="slug",
            field=models.SlugField(blank=True, default="", max_length=255),
        ),
    ]
