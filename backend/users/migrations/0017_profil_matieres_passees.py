from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0063_seed_gce_referentiel'),
        ('users', '0016_user_langue'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='matieres_passees',
            field=models.ManyToManyField(
                blank=True, related_name='profils_eleves', to='catalog.subject',
                help_text=(
                    "Matières que CE profil passe à l'examen. Vide = toutes celles du cursus (le "
                    "cas des séries du BEPC, Probatoire et BAC, où la série fixe déjà les matières). "
                    "Sert au GCE, qui n'a pas de séries : on y choisit ses matières, et le coach, le "
                    "plan du jour, les priorités et la progression se limitent à elles. Voir "
                    "quiz.matieres."
                ),
            ),
        ),
    ]
