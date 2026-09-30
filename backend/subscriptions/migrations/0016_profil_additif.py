"""
`Subscription`, `InscriptionInedite`, `InscriptionRepetiteur` gagnent un champ
`profil` - PUREMENT ADDITIF, `user` reste inchangé et continue de porter la
facturation (voir payments.models.Transaction/ManualPayment, qui pointent sur `user`,
jamais remis en cause). Décision confirmée avec le user : un abonnement payé est
assigné au profil (l'enfant) actif au moment de l'achat, jamais partagé entre les
profils d'un même compte - voir la docstring de `Subscription`.

Contrairement aux vagues précédentes (quiz, access, inedit, simulations), rien n'est
retiré ici : la contrainte d'unicité `(user, cursus)` reste en place pour l'instant
(voir le commentaire dans `SubscriptionManager.activate_or_extend` - le grain exact
sera resserré une fois l'achat pour un profil précis branché de bout en bout, pas
avant). Même rétro-remplissage déterministe que les vagues précédentes :
`profil = user.profils.first()`, valable tant que chaque compte n'a qu'un seul profil.
"""
import django.db.models.deletion
from django.db import migrations, models


def _backfill(apps, schema_editor):
    Subscription = apps.get_model("subscriptions", "Subscription")
    InscriptionInedite = apps.get_model("subscriptions", "InscriptionInedite")
    InscriptionRepetiteur = apps.get_model("subscriptions", "InscriptionRepetiteur")
    Profil = apps.get_model("users", "Profil")

    profil_par_compte = {p.compte_id: p.id for p in Profil.objects.all()}

    for Model in (Subscription, InscriptionInedite, InscriptionRepetiteur):
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
        ("subscriptions", "0015_hausse_plancher_plafond_2"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="inscriptioninedite", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="inscriptions_inedites", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="inscriptionrepetiteur", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="inscriptions_repetiteur", to="users.profil",
            ),
        ),

        migrations.RunPython(_backfill, _reverse_backfill),

        migrations.AlterField(
            model_name="subscription", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to="users.profil",
                help_text="L'enfant pour qui cet accès a été payé - voir la docstring de la classe.",
            ),
        ),
        migrations.AlterField(
            model_name="inscriptioninedite", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="inscriptions_inedites", to="users.profil",
            ),
        ),
        migrations.AlterField(
            model_name="inscriptionrepetiteur", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="inscriptions_repetiteur", to="users.profil",
            ),
        ),
    ]
