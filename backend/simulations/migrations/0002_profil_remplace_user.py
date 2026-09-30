"""
`SimulationEpreuve` passe de `user` à `profil` - même vague, voir
`quiz.migrations.0016_profil_remplace_user`.
"""
import django.db.models.deletion
from django.db import migrations, models


def _backfill(apps, schema_editor):
    SimulationEpreuve = apps.get_model("simulations", "SimulationEpreuve")
    Profil = apps.get_model("users", "Profil")

    profil_par_compte = {p.compte_id: p.id for p in Profil.objects.all()}

    a_mettre_a_jour = []
    for row in SimulationEpreuve.objects.all().only("id", "user_id"):
        profil_id = profil_par_compte.get(row.user_id)
        if profil_id is None:
            profil_id = Profil.objects.get_or_create(compte_id=row.user_id)[0].id
            profil_par_compte[row.user_id] = profil_id
        row.profil_id = profil_id
        a_mettre_a_jour.append(row)
    SimulationEpreuve.objects.bulk_update(a_mettre_a_jour, ["profil_id"], batch_size=500)


def _reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_backfill_profil_depuis_user"),
        ("simulations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="simulationepreuve", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="simulations_epreuves", to="users.profil",
            ),
        ),
        migrations.RunPython(_backfill, _reverse_backfill),
        migrations.AlterField(
            model_name="simulationepreuve", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="simulations_epreuves", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="simulationepreuve", name="user"),
    ]
