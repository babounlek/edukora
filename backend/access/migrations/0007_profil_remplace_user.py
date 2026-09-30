"""
`LectureProgress`, `ExerciceFait`, `MarqueEtude` passent de `user` à `profil` - même
vague et même raison que `quiz.migrations.0016_profil_remplace_user` (voir sa
docstring) : ce sont des données de progression d'apprentissage, per-enfant.

Même patron : `profil` ajouté nullable, rempli depuis `user.profils.first()` (chaque
compte n'a par construction qu'un seul profil à ce stade), puis `user` retiré.
"""
import django.db.models.deletion
from django.db import migrations, models


def _backfill(apps, schema_editor):
    LectureProgress = apps.get_model("access", "LectureProgress")
    ExerciceFait = apps.get_model("access", "ExerciceFait")
    MarqueEtude = apps.get_model("access", "MarqueEtude")
    Profil = apps.get_model("users", "Profil")

    profil_par_compte = {p.compte_id: p.id for p in Profil.objects.all()}

    for Model in (LectureProgress, ExerciceFait, MarqueEtude):
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
        ("access", "0006_marqueetude"),
    ]

    operations = [
        migrations.AddField(
            model_name="lectureprogress", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="lectures", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="exercicefait", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="exercices_faits", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="marqueetude", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="marques_etude", to="users.profil",
            ),
        ),

        migrations.RunPython(_backfill, _reverse_backfill),

        migrations.RemoveConstraint(model_name="lectureprogress", name="unique_lecture_lesson"),
        migrations.RemoveConstraint(model_name="lectureprogress", name="unique_lecture_cours"),
        migrations.AddConstraint(
            model_name="lectureprogress",
            constraint=models.UniqueConstraint(
                fields=["profil", "lesson"], name="unique_lecture_lesson", condition=models.Q(lesson__isnull=False),
            ),
        ),
        migrations.AddConstraint(
            model_name="lectureprogress",
            constraint=models.UniqueConstraint(
                fields=["profil", "cours"], name="unique_lecture_cours", condition=models.Q(cours__isnull=False),
            ),
        ),

        migrations.RemoveConstraint(model_name="exercicefait", name="unique_exercice_fait"),
        migrations.AddConstraint(
            model_name="exercicefait",
            constraint=models.UniqueConstraint(fields=["profil", "exercise"], name="unique_exercice_fait"),
        ),

        migrations.RemoveConstraint(model_name="marqueetude", name="unique_marque_lesson"),
        migrations.RemoveConstraint(model_name="marqueetude", name="unique_marque_cours"),
        migrations.AddConstraint(
            model_name="marqueetude",
            constraint=models.UniqueConstraint(
                fields=["profil", "lesson", "cle"], name="unique_marque_lesson", condition=models.Q(lesson__isnull=False),
            ),
        ),
        migrations.AddConstraint(
            model_name="marqueetude",
            constraint=models.UniqueConstraint(
                fields=["profil", "cours", "cle"], name="unique_marque_cours", condition=models.Q(cours__isnull=False),
            ),
        ),

        migrations.AlterField(
            model_name="lectureprogress", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="lectures", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="lectureprogress", name="user"),

        migrations.AlterField(
            model_name="exercicefait", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="exercices_faits", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="exercicefait", name="user"),

        migrations.AlterField(
            model_name="marqueetude", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="marques_etude", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="marqueetude", name="user"),
    ]
