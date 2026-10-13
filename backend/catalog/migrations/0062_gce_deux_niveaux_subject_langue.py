from django.db import migrations, models

EXAMEN_CHOICES = [
    ('BEPC', 'BEPC'), ('PROBATOIRE', 'Probatoire'), ('BAC', 'BAC'), ('CAP', 'CAP'),
    ('GCE_OL', 'GCE Ordinary Level'), ('GCE_AL', 'GCE Advanced Level'),
    ('AUTRE', 'Devoir surveillé / Autre'),
]


class Migration(migrations.Migration):
    """Schéma seul : le code unique « GCE » devient GCE_OL / GCE_AL et Subject porte une langue.
    Les données (sessions, matières, cursus) sont migrées dans 0063 - schéma et données
    dans deux migrations distinctes, pour ne pas mélanger ALTER TABLE et écritures dans
    une même transaction PostgreSQL."""

    dependencies = [
        ('catalog', '0061_frequencecours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cursus',
            name='examen',
            field=models.CharField(choices=EXAMEN_CHOICES, max_length=20),
        ),
        migrations.AlterField(
            model_name='examenlabel',
            name='examen',
            field=models.CharField(choices=EXAMEN_CHOICES, max_length=20),
        ),
        migrations.AlterField(
            model_name='examsession',
            name='examen',
            field=models.CharField(choices=EXAMEN_CHOICES, max_length=20),
        ),
        migrations.AddField(
            model_name='subject',
            name='langue',
            field=models.CharField(
                choices=[('fr', 'Français'), ('en', 'English')], default='fr', max_length=2,
                help_text=(
                    "Langue d'enseignement. Les matières du GCE (anglophone) portent un code "
                    "distinct de leur équivalent francophone (préfixe GCE_) pour ne pas partager "
                    "leurs thèmes, programmes et quiz avec lui - la langue sert aux filtres et à "
                    "l'affichage."
                ),
            ),
        ),
    ]
