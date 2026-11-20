from django.db import migrations, models


class Migration(migrations.Migration):
    """Deux nouveaux types de message : les relances d'absence (voir relances.absence). Aucun changement de table."""

    dependencies = [
        ('relances', '0004_canal_whatsapp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relanceenvoyee',
            name='type',
            field=models.CharField(
                choices=[
                    ('rappel_seance', 'Rappel de la séance du jour'),
                    ('paiement_abandonne_1', 'Paiement non abouti - premier message'),
                    ('paiement_abandonne_2', 'Paiement non abouti - dernier message'),
                    ('bilan_parent', 'Bilan de la semaine au parent'),
                    ('absence_1', "Absence - deux jours sans séance"),
                    ('absence_2', "Absence - une semaine sans séance, dernier message"),
                ],
                max_length=30,
            ),
        ),
    ]
