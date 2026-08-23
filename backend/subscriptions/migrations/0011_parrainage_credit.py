import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0010_seed_addon_repetiteur"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="parrainagerecompense",
            name="jours_offerts",
        ),
        migrations.AlterField(
            model_name="parrainagerecompense",
            name="cursus",
            field=models.ForeignKey(
                help_text=(
                    "Cursus dont l'achat du filleul a déclenché la récompense - "
                    "purement informatif, le crédit lui-même est dépensable sur "
                    "n'importe quel cursus."
                ),
                on_delete=django.db.models.deletion.PROTECT,
                to="catalog.cursus",
            ),
        ),
        migrations.AddField(
            model_name="parrainagerecompense",
            name="montant_offert",
            field=models.PositiveIntegerField(
                default=500, help_text="Montant FCFA accordé au parrain, figé à l'octroi.",
            ),
        ),
        migrations.AddField(
            model_name="parrainagerecompense",
            name="montant_restant",
            field=models.PositiveIntegerField(
                default=500,
                help_text="Solde encore dépensable de ce crédit - voir consommer_credit_parrainage.",
            ),
        ),
        migrations.AddField(
            model_name="parrainagerecompense",
            name="expires_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Au-delà, ce crédit n'est plus comptabilisé dans le solde même si montant_restant > 0.",
            ),
            preserve_default=False,
        ),
    ]
