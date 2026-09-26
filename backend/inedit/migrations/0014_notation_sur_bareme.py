from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inedit", "0013_questioninedite_groupe_local"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tentativeinedite",
            name="score_obtenu",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                help_text=(
                    "Note en pourcentage du barème COMPLET (0-100, même échelle que "
                    "EpreuveInedite.score_originalite/score_qualite) : une question non traitée "
                    "compte zéro, voir inedit.notation. La note en points est `note_obtenue`. Null "
                    "tant que la tentative n'est pas soumise."
                ),
            ),
        ),
        migrations.AddField(
            model_name="questioninedite",
            name="points",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True,
                help_text=(
                    "Barème exact de la question. Null tant qu'il n'est pas renseigné : la note "
                    "répartit alors les points de l'exercice à parts égales entre ses questions "
                    "(voir inedit.notation.points_par_question), présenté à l'élève comme un barème "
                    "estimé."
                ),
            ),
        ),
        migrations.AddField(
            model_name="questioninedite",
            name="criteres_notation",
            field=models.JSONField(
                blank=True, default=list,
                help_text=(
                    "[{\"libelle\": \"Formule correcte\", \"points\": 1}] - critères de la grille "
                    "de notation, à cocher par l'élève après le corrigé. Leur somme doit égaler "
                    "`points`. Vide : repli sur l'auto-évaluation en trois niveaux."
                ),
            ),
        ),
        migrations.AddField(
            model_name="tentativeinedite",
            name="note_obtenue",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True,
                help_text=(
                    "Note en points sur `bareme_snapshot`, recalculée à chaque notation d'une "
                    "question tant que la tentative est soumise (voir inedit.notation). Les "
                    "questions non traitées comptent zéro. Null avant la soumission."
                ),
            ),
        ),
        migrations.AddField(
            model_name="tentativeinedite",
            name="bareme_snapshot",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True,
                help_text=(
                    "Total des points de l'épreuve au moment de la soumission, copié ici pour "
                    "qu'une correction ultérieure du barème ne réécrive pas d'anciennes notes."
                ),
            ),
        ),
        migrations.AddField(
            model_name="tentativereponse",
            name="traitee_at",
            field=models.DateTimeField(
                blank=True, null=True,
                help_text=(
                    "Posé quand l'élève déclare avoir traité une question ouverte - possible "
                    "pendant le mode examen, où le corrigé (donc la notation) est encore masqué. "
                    "Une question ouverte jamais traitée vaut zéro sans que l'élève ait à agir."
                ),
            ),
        ),
        migrations.AddField(
            model_name="tentativereponse",
            name="points_obtenus",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True,
                help_text=(
                    "Points obtenus sur une question ouverte, une fois notée par l'élève. Null "
                    "tant que la question n'est pas notée : une réponse ancienne qui porte "
                    "seulement resultat_declare est convertie à la volée (voir inedit.notation)."
                ),
            ),
        ),
        migrations.AddField(
            model_name="tentativereponse",
            name="criteres_valides",
            field=models.JSONField(
                blank=True, default=list,
                help_text="Indices des critères de QuestionInedite.criteres_notation cochés par l'élève.",
            ),
        ),
    ]
