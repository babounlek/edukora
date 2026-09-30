"""
Les 5 modèles qui décrivent une progression d'apprentissage (QuizSession,
RevisionSchedule, SeanceJournaliere, ObjectifMatiere, VisiteAccueil) passent de
`user` (le compte) à `profil` (la personne qui étudie sous ce compte) - voir la
docstring de `users.models.Profil` : fusionner l'activité de deux enfants sous un
même compte casserait leur série de jours et leur coaching respectifs.

Même patron que `users.migrations.0012_backfill_profil_depuis_user` (elle-même
calquée sur `users.migrations.0006_compte_unique_e164_authidentity`) : schéma et
données dans le même fichier, `profil` ajouté nullable, rempli depuis `user`, puis
`user` retiré - jamais de fenêtre où les deux se contrediraient.

Le rétro-remplissage est déterministe et sûr : à ce stade, chaque compte n'a par
construction qu'un seul profil (`users.migrations.0012...` a tourné avant celle-ci,
et aucune vue ne permet encore d'en ajouter un second - voir le plan de chantier),
donc `row.user.profils.first()` désigne sans ambiguïté LE profil de ce compte.
"""
import django.db.models.deletion
from django.db import migrations, models


def _backfill(apps, schema_editor):
    QuizSession = apps.get_model("quiz", "QuizSession")
    RevisionSchedule = apps.get_model("quiz", "RevisionSchedule")
    SeanceJournaliere = apps.get_model("quiz", "SeanceJournaliere")
    ObjectifMatiere = apps.get_model("quiz", "ObjectifMatiere")
    VisiteAccueil = apps.get_model("quiz", "VisiteAccueil")
    Profil = apps.get_model("users", "Profil")

    profil_par_compte = {p.compte_id: p.id for p in Profil.objects.all()}

    for Model in (QuizSession, RevisionSchedule, SeanceJournaliere, ObjectifMatiere, VisiteAccueil):
        a_mettre_a_jour = []
        for row in Model.objects.all().only("id", "user_id"):
            profil_id = profil_par_compte.get(row.user_id)
            if profil_id is None:
                # Aucun profil pour ce compte (ne devrait pas arriver, voir la
                # docstring) - le premier profil créé pour ce compte, faute de mieux,
                # plutôt que de laisser une ligne orpheline qu'AlterField(null=False)
                # refuserait ensuite.
                profil_id = Profil.objects.get_or_create(compte_id=row.user_id)[0].id
                profil_par_compte[row.user_id] = profil_id
            row.profil_id = profil_id
            a_mettre_a_jour.append(row)
        Model.objects.bulk_update(a_mettre_a_jour, ["profil_id"], batch_size=500)


def _reverse_backfill(apps, schema_editor):
    # Rien à défaire : `user_id` n'a jamais été touché par `_backfill`, la valeur
    # renseignée par le forward reste donc disponible telle quelle pour toute
    # migration ultérieure qui rétablirait le champ `user`.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_backfill_profil_depuis_user"),
        ("quiz", "0015_visiteaccueil"),
    ]

    operations = [
        # --- 1. `profil` nullable, en plus de `user` (encore présent) -----------
        migrations.AddField(
            model_name="quizsession", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="quiz_sessions", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="revisionschedule", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="revision_schedules", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="seancejournaliere", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="seances_journalieres", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="objectifmatiere", name="profil",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="objectifs_matiere", to="users.profil",
            ),
        ),
        migrations.AddField(
            model_name="visiteaccueil", name="profil",
            field=models.OneToOneField(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="visite_accueil", to="users.profil",
            ),
        ),

        # --- 2. Rétro-remplissage -------------------------------------------------
        migrations.RunPython(_backfill, _reverse_backfill),

        # --- 3. Contraintes d'unicité : `user` -> `profil` -------------------------
        migrations.RemoveConstraint(model_name="revisionschedule", name="unique_revision_schedule"),
        migrations.AddConstraint(
            model_name="revisionschedule",
            constraint=models.UniqueConstraint(fields=["profil", "cursus", "theme"], name="unique_revision_schedule"),
        ),
        migrations.RemoveConstraint(model_name="seancejournaliere", name="unique_seance_par_rang_du_jour"),
        migrations.AddConstraint(
            model_name="seancejournaliere",
            constraint=models.UniqueConstraint(
                fields=["profil", "cursus", "date", "ordre"], name="unique_seance_par_rang_du_jour",
            ),
        ),
        migrations.RemoveConstraint(model_name="objectifmatiere", name="uniq_objectif_matiere_user_cursus"),
        migrations.AddConstraint(
            model_name="objectifmatiere",
            constraint=models.UniqueConstraint(fields=["profil", "cursus"], name="uniq_objectif_matiere_user_cursus"),
        ),

        # --- 4. `profil` non-nul, `user` retiré -------------------------------------
        migrations.AlterField(
            model_name="quizsession", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="quiz_sessions", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="quizsession", name="user"),

        migrations.AlterField(
            model_name="revisionschedule", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="revision_schedules", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="revisionschedule", name="user"),

        migrations.AlterField(
            model_name="seancejournaliere", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="seances_journalieres", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="seancejournaliere", name="user"),

        migrations.AlterField(
            model_name="objectifmatiere", name="profil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="objectifs_matiere", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="objectifmatiere", name="user"),

        migrations.AlterField(
            model_name="visiteaccueil", name="profil",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="visite_accueil", to="users.profil",
            ),
        ),
        migrations.RemoveField(model_name="visiteaccueil", name="user"),
    ]
