from django.db import migrations, models


class Migration(migrations.Migration):
    """Schéma de la tarification au mois (2026-11-11) : le palier MENSUEL. Les plans eux-mêmes sont créés
    par 0027_plans_au_mois."""

    dependencies = [
        ('subscriptions', '0025_campagne_nom_en'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='duration_days',
            field=models.PositiveSmallIntegerField(default=30, help_text="Utilisé tel quel si duration_mode=FIXE. Ignoré (valeur de repli seulement, voir effective_duration_days) si duration_mode=JUSQUA_EXAMEN ; ignoré aussi si duration_mode=MENSUEL (30 jours par mois choisi à l'achat)."),
        ),
        migrations.AlterField(
            model_name='plan',
            name='duration_mode',
            field=models.CharField(choices=[('FIXE', 'Durée fixe'), ('JUSQUA_EXAMEN', "Jusqu'à l'examen"), ('MENSUEL', 'Au mois')], default='FIXE', max_length=20),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='duration_mode',
            field=models.CharField(choices=[('FIXE', 'Durée fixe'), ('JUSQUA_EXAMEN', "Jusqu'à l'examen"), ('MENSUEL', 'Au mois')], default='FIXE', help_text="Palier du Plan qui a (au moins une fois) financé cette ligne - copié depuis Plan.duration_mode à l'activation (voir SubscriptionManager.activate_or_extend), jamais déduit après coup. Distinct de has_access (qui ignore ce champ, n'importe quel palier donne accès au contenu de base) : sert uniquement à gater les fonctionnalités pensées comme argument de vente propre à Jusqu'à l'Examen (voir access.services.has_access_jusqua_examen).", max_length=20),
        ),
    ]
