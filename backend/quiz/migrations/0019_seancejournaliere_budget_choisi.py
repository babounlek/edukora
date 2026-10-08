from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0018_competenceitemfigure'),
    ]

    operations = [
        migrations.AddField(
            model_name='seancejournaliere',
            name='budget_choisi',
            field=models.BooleanField(default=False, help_text="Vrai quand ce budget vient d'un choix de l'élève (ou de la reconduite d'un choix), faux quand le système l'a imposé - le retour en douceur après une absence. Seul un budget choisi est reconduit à la séance du lendemain : un budget imposé ne doit jamais devenir une habitude."),
        ),
    ]
