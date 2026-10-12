import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0060_trigram_index_recherche_textuelle'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrequenceCours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(help_text='Nom du thème dont le cours hérite sa fréquence.', max_length=100)),
                ('nb_epreuves', models.PositiveSmallIntegerField(help_text='Épreuves de référence où le thème est tombé.')),
                ('nb_sessions', models.PositiveSmallIntegerField(help_text='Épreuves de référence de la matière sur ce cursus.')),
                ('frequence_pct', models.PositiveSmallIntegerField()),
                ('calcule_le', models.DateTimeField(auto_now=True)),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frequences', to='catalog.cours')),
                ('cursus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frequences_cours', to='catalog.cursus')),
            ],
            options={
                'verbose_name': "fréquence d'un cours",
                'verbose_name_plural': 'fréquences des cours',
                'indexes': [models.Index(fields=['cursus', '-frequence_pct'], name='catalog_fre_cursus__25b000_idx')],
                'constraints': [models.UniqueConstraint(fields=('cursus', 'cours'), name='unique_frequence_cours_par_cursus')],
            },
        ),
    ]
