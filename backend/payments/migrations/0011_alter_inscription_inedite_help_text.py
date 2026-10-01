"""
Aide en ligne de `ManualPayment.inscription_inedite`/`Transaction.inscription_inedite`
actualisée (retrait de l'achat séparé de l'add-on Épreuves Inédites, 2026-09-30, voir
subscriptions.models.ProductType) - restait en attente depuis ce retrait.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_transaction_manualpayment_profil'),
        ('subscriptions', '0017_unique_par_profil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualpayment',
            name='inscription_inedite',
            field=models.ForeignKey(blank=True, help_text='Renseigné avec `subscription` une fois un paiement de Plan ABONNEMENT inclut_inedit=True approuvé.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manual_payments', to='subscriptions.inscriptioninedite'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='inscription_inedite',
            field=models.ForeignKey(blank=True, help_text="Renseigné avec `subscription` une fois le paiement d'un Plan ABONNEMENT inclut_inedit=True confirmé (voir _activer_acces).", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='subscriptions.inscriptioninedite'),
        ),
    ]
