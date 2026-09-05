from django.db import migrations

# Hausse du plancher et du plafond de la grille Jusqu'à l'Examen - décision
# utilisateur du 2026-09-05 (voir subscriptions.models.{PLANCHER_JUSQUA_EXAMEN,
# INCREMENT_PAR_TRANCHE}, relevés dans le même commit). Le plancher est une constante
# Python lue à chaque calcul, rien à migrer côté données pour lui. Le plafond, lui,
# est le champ `price` de chaque Plan JUSQUA_EXAMEN, seedé une fois par
# 0009_grille_deux_paliers - il faut le relever explicitement ici pour les lignes déjà
# en base, sans quoi elles resteraient plafonnées à l'ancien montant.

ANCIEN_PLAFOND = 12000
NOUVEAU_PLAFOND = 15000


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
        ("subscriptions", "0013_retire_mensuel"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
