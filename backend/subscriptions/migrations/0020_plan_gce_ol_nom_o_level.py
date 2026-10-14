from django.db import migrations

# « Ordinary Level » s'écrit « O Level » partout (décision utilisateur du 2026-10-14), comme le libellé d'examen
# `Examen.GCE_OL` ("GCE O Level"). Ne renomme que le plan encore sous son nom d'origine : un nom modifié à la main
# depuis l'admin n'est pas écrasé.
ANCIEN = "GCE Ordinary Level - Jusqu'à l'Examen"
NOUVEAU = "GCE O Level - Jusqu'à l'Examen"


def renommer(de, vers):
    def appliquer(apps, schema_editor):
        Plan = apps.get_model("subscriptions", "Plan")
        Plan.objects.filter(
            cursus__country__code="CM", cursus__examen="GCE_OL", cursus__series__isnull=True,
            product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", name=de,
        ).update(name=vers)
    return appliquer


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0019_seed_plan_gce_ol"),
    ]

    operations = [
        migrations.RunPython(renommer(ANCIEN, NOUVEAU), renommer(NOUVEAU, ANCIEN)),
    ]
