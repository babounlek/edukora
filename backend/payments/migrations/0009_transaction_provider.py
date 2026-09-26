import payments.providers
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Abstraction du fournisseur de paiement : `campay_reference` devient
    `provider_reference` (RenameField, données conservées) et `provider` est ajouté.
    Toutes les transactions existantes viennent de CamPay : le défaut statique "campay"
    les rétro-remplit correctement, avant de basculer sur le défaut dynamique du modèle.
    """

    dependencies = [
        ("payments", "0008_transaction_credit_applique"),
    ]

    operations = [
        migrations.RenameField(
            model_name="transaction",
            old_name="campay_reference",
            new_name="provider_reference",
        ),
        migrations.AlterField(
            model_name="transaction",
            name="provider_reference",
            field=models.CharField(
                blank=True, max_length=100,
                help_text="Référence de la transaction chez l'agrégateur (`provider`).",
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="provider",
            field=models.CharField(
                default="campay", max_length=20,
                help_text="Agrégateur qui traite cette transaction (voir payments.providers), figé à la création.",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="provider",
            field=models.CharField(
                default=payments.providers.fournisseur_par_defaut, max_length=20,
                help_text="Agrégateur qui traite cette transaction (voir payments.providers), figé à la création.",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="amount",
            field=models.PositiveIntegerField(
                help_text=(
                    "Montant en FCFA réellement envoyé à l'agrégateur (déjà net du crédit "
                    "parrainage - voir credit_applique), capturé au moment du paiement "
                    "(indépendant d'un changement de prix ultérieur)."
                ),
            ),
        ),
    ]
