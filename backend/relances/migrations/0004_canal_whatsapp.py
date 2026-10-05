from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relances', '0003_bilan_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relanceenvoyee',
            name='canal',
            field=models.CharField(choices=[('email', 'E-mail'), ('push', 'Notification du navigateur'), ('whatsapp', 'WhatsApp')], default='email', max_length=10),
        ),
    ]
