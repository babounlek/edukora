from django.db import migrations

# Tarification unique Jusqu'à l'Examen (2026-10-02) : 15 000 F par enfant, fixe. La
# grille dégressive par tranches de 30 jours est supprimée (voir
# subscriptions.models.Plan.effective_price) ; `price` devient le prix réel, plus un
# plafond. Les Plan ABONNEMENT/JUSQUA_EXAMEN passent donc de 20 000 à 15 000.

ANCIEN_PRIX = 20000
NOUVEAU_PRIX = 15000


def appliquer(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", price=ANCIEN_PRIX,
    ).update(price=NOUVEAU_PRIX)


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", price=NOUVEAU_PRIX,
    ).update(price=ANCIEN_PRIX)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0017_unique_par_profil"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
