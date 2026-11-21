from django.db import migrations, models


class Migration(migrations.Migration):
    """Deux nouveaux types de message : la fin d'abonnement (voir relances.fin_abonnement). Aucun changement de table."""

    dependencies = [
        ('relances', '0005_relances_absence'),
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
                    ('fin_abonnement_1', "Fin d'abonnement - trois jours avant"),
                    ('fin_abonnement_2', "Fin d'abonnement - le jour même, dernier message"),
                ],
                max_length=30,
            ),
        ),
    ]
