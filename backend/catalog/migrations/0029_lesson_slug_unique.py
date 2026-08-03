# Dernière étape : toutes les lignes ont désormais un slug non vide (voir
# 0028_backfill_lesson_slug) - la contrainte d'unicité peut être posée en toute
# sécurité, sans risque d'échouer sur un slug encore vide ou en doublon.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0028_backfill_lesson_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lesson",
            name="slug",
            field=models.SlugField(
                blank=True, max_length=255, unique=True,
                help_text="Généré automatiquement depuis le titre à la création - ne pas modifier après publication.",
            ),
        ),
    ]
