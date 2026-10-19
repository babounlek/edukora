from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0017_profil_matieres_passees"),
    ]

    operations = [
        migrations.AddField(
            model_name="profil",
            name="voir_seulement_mes_matieres",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Préférence d'affichage, distincte de `matieres_passees` (la donnée : ce que l'élève passe "
                    "vraiment). Activée, les listes (épreuves, cours, matières, quiz, parcours, plan du jour) se "
                    "limitent aux matières choisies ; désactivée, tout le catalogue du cursus reste visible sans "
                    "toucher à l'inscription. Sans effet tant qu'aucune matière n'est choisie. Voir quiz.matieres."
                ),
            ),
        ),
    ]
