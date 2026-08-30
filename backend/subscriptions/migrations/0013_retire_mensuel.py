from django.db import migrations

# Fusion en une seule offre - décision utilisateur du 2026-08-30 : Mensuel disparaît de
# la vente, Jusqu'à l'Examen (plancher redescendu à 2 000 FCFA le même jour, voir
# subscriptions.models.PLANCHER_JUSQUA_EXAMEN) devient l'unique formule proposée sur
# /tarifs. Même réflexe que 0009_grille_deux_paliers pour les anciens paliers :
# désactivé, jamais supprimé - Transaction/ManualPayment référencent ces Plan en
# PROTECT, et les abonnements Mensuel déjà vendus doivent rester lisibles tels quels
# (voir AccountPage.tsx, qui affiche encore "Mensuel" pour ces abonnements existants).

DUREE_MENSUEL = 30


def appliquer(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="FIXE", duration_days=DUREE_MENSUEL,
    ).update(is_active=False)


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="FIXE", duration_days=DUREE_MENSUEL,
    ).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0012_subscription_duration_mode"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
