from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0008_telechargements_pdf_quotas'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercicefait',
            name='part_reussie',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                help_text="Part de l'exercice que l'élève déclare avoir réussie, en % (0, 50, 75 ou 100). "
                          "Vide : il a dit l'avoir fait sans se noter.",
            ),
        ),
    ]
