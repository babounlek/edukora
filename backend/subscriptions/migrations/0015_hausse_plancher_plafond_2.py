from django.db import migrations

# Deuxième hausse du plancher et du plafond de la grille Jusqu'à l'Examen, le même
# jour que la première (voir 0014_hausse_plancher_plafond) - décision utilisateur,
# toujours pré-lancement. Même mécanique que 0014 : le plancher est une constante
# Python (voir subscriptions.models.PLANCHER_JUSQUA_EXAMEN, relevée dans le même
# commit), rien à migrer côté données pour lui. Le plafond est le champ `price` de
# chaque Plan JUSQUA_EXAMEN - à relever explicitement ici pour les lignes déjà en
# base.

ANCIEN_PLAFOND = 15000
NOUVEAU_PLAFOND = 20000


def appliquer(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", price=ANCIEN_PLAFOND,
    ).update(price=NOUVEAU_PLAFOND)


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", price=NOUVEAU_PLAFOND,
    ).update(price=ANCIEN_PLAFOND)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0014_hausse_plancher_plafond"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
