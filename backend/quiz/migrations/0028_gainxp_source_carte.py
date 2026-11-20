from django.db import migrations, models


class Migration(migrations.Migration):
    """Une carte de révision revue à son échéance rapporte des points (voir quiz.xp.crediter_carte) : nouvelle source."""

    dependencies = [
        ('quiz', '0027_question_passee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gainxp',
            name='source',
            field=models.CharField(
                choices=[
                    ('REPONSE', 'Réponse à une question'),
                    ('SEANCE', 'Séance du jour terminée'),
                    ('COURS', 'Section de cours comprise'),
                    ('EXERCICE', 'Exercice déclaré fait'),
                    ('SIMULATION', 'Examen blanc terminé'),
                    ('CARTE', 'Carte de révision revue'),
                ],
                max_length=10,
            ),
        ),
    ]
