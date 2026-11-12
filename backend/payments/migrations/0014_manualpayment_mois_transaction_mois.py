from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_campagne_promotionnelle'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualpayment',
            name='mois',
            field=models.PositiveSmallIntegerField(default=1, help_text="Nombre de mois d'accès achetés (plan au mois, 30 jours chacun), figé à la déclaration. 1 pour tout autre plan."),
        ),
        migrations.AddField(
            model_name='transaction',
            name='mois',
            field=models.PositiveSmallIntegerField(default=1, help_text="Nombre de mois d'accès achetés (plan au mois, 30 jours chacun), figé à l'initiation. 1 pour tout autre plan."),
        ),
    ]
