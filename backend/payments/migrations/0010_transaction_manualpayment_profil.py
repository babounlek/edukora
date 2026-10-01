"""
`Transaction` et `ManualPayment` gagnent un champ `profil` - l'enfant pour qui
l'achat est fait (voir users.models.Profil), à côté de `user` qui reste le compte
payeur, jamais remis en cause. Nécessaire pour que payments.views.initiate_payment/
declare_manual_payment puissent activer l'abonnement du bon enfant (voir
_activer_acces) plutôt que de toujours retomber sur `user.profils.first()`.

Même rétro-remplissage déterministe que subscriptions.migrations.0016_profil_additif :
`profil = user.profils.first()`, valable pour toute ligne existante (aucun compte
n'a encore payé explicitement pour un profil précis avant cette migration).
"""
import django.db.models.deletion
from django.db import migrations, models


def _backfill(apps, schema_editor):
    Transaction = apps.get_model("payments", "Transaction")
    ManualPayment = apps.get_model("payments", "ManualPayment")
    Profil = apps.get_model("users", "Profil")

    profil_par_compte = {p.compte_id: p.id for p in Profil.objects.all()}

    for Model in (Transaction, ManualPayment):
        a_mettre_a_jour = []
        for row in Model.objects.all().only("id", "user_id"):
            profil_id = profil_par_compte.get(row.user_id)
            if profil_id is None:
                profil_id = Profil.objects.get_or_create(compte_id=row.user_id)[0].id
                profil_par_compte[row.user_id] = profil_id
            row.profil_id = profil_id
            a_mettre_a_jour.append(row)
        Model.objects.bulk_update(a_mettre_a_jour, ["profil_id"], batch_size=500)


def _reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_backfill_profil_depuis_user"),
        ("payments", "0009_transaction_provider"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="manualpayment", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, related_name="manual_payments", to="users.profil",
            ),
        ),

        migrations.RunPython(_backfill, _reverse_backfill),

        migrations.AlterField(
            model_name="transaction", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="users.profil",
                help_text="L'enfant pour qui cet achat est fait - voir payments.views.initiate_payment.",
            ),
        ),
        migrations.AlterField(
            model_name="manualpayment", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="manual_payments", to="users.profil",
                help_text="L'enfant pour qui cet achat est fait - voir payments.views.declare_manual_payment.",
            ),
        ),
    ]
