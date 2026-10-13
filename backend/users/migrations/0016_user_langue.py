from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_bilan_parent_actif'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='langue',
            field=models.CharField(
                choices=[('fr', 'Français'), ('en', 'English')], default='fr', max_length=2,
                help_text=(
                    "Langue de l'interface et des messages envoyés (e-mail, SMS, WhatsApp). Choisie par "
                    "l'élève avec le sélecteur de langue ; français par défaut. Les contenus (épreuves, "
                    "cours, quiz) ont leur propre langue - voir catalog.models.Subject.langue."
                ),
            ),
        ),
    ]
