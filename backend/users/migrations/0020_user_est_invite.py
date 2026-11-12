from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0019_chrono_quiz"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="est_invite",
            field=models.BooleanField(
                default=False,
                help_text="Compte invité : créé sans identité (ni numéro, ni e-mail, ni Google) pour essayer une épreuve inédite gratuite sans s'inscrire. Il n'ouvre que /inedit/ (voir users.authentication) et disparaît quand son porteur crée un vrai compte (voir users.invites.rattacher), qui hérite de sa copie, ou au bout de 60 jours (commande purger_invites).",
            ),
        ),
    ]
