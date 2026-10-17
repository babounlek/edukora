"""
Simulation à la question pour les Paper 1 du GCE (50 QCM corrigés automatiquement) : une réponse
peut désormais viser une QUESTION précise (`sous_question`) et porter la lettre choisie ; une
question peut être marquée « à revoir ». Les simulations existantes (à l'exercice) sont inchangées.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0067_gce_matieres_codes_officiels"),
        ("simulations", "0002_profil_remplace_user"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="simulationreponse", name="unique_reponse_par_exercice_et_simulation",
        ),
        migrations.AddField(
            model_name="simulationreponse", name="sous_question",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="+",
                to="catalog.question",
            ),
        ),
        migrations.AddField(
            model_name="simulationreponse", name="reponse_choisie",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AddField(
            model_name="simulationepreuve", name="questions_marquees_qcm",
            field=models.ManyToManyField(
                blank=True, help_text="Questions marquées « à revoir » (simulation à la question).",
                related_name="+", to="catalog.question",
            ),
        ),
        migrations.AddConstraint(
            model_name="simulationreponse",
            constraint=models.UniqueConstraint(
                condition=models.Q(sous_question__isnull=True), fields=("simulation", "exercise"),
                name="unique_reponse_par_exercice_et_simulation",
            ),
        ),
        migrations.AddConstraint(
            model_name="simulationreponse",
            constraint=models.UniqueConstraint(
                condition=models.Q(sous_question__isnull=False), fields=("simulation", "sous_question"),
                name="unique_reponse_par_question_et_simulation",
            ),
        ),
    ]
