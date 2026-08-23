from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0007_manualpayment_inscription_repetiteur_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="credit_applique",
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    "Crédit parrainage appliqué en remise sur le prix du plan (voir "
                    "subscriptions.models.solde_credit_parrainage), figé à l'initiation. "
                    "Consommé pour de vrai (montant_restant décrémenté) seulement à la "
                    "confirmation du paiement - voir _confirmer_succes - jamais à "
                    "l'initiation, qui peut encore échouer."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="amount",
            field=models.PositiveIntegerField(
                help_text=(
                    "Montant en FCFA réellement envoyé à CamPay (déjà net du crédit "
                    "parrainage - voir credit_applique), capturé au moment du paiement "
                    "(indépendant d'un changement de prix ultérieur)."
                ),
            ),
        ),
    ]
