from django.db import migrations

# Add-on Fiches (répétiteurs/enseignants) mis en veille : le public répétiteur n'est pas
# prioritaire (onglet de /tarifs retiré le 2026-09-15, accès à /fiches retiré le
# 2026-10-20). On décoche is_active plutôt que de supprimer les Plans : le catalogue
# (subscriptions.views) et le paiement (payments.views) filtrent déjà sur is_active, donc
# plus aucun achat possible, et les InscriptionRepetiteur existantes restent valides.
# Pour réveiller l'offre : recocher is_active dans l'admin (ou relancer cette migration à
# l'envers).


def mettre_en_veille(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(product_type="ADDON_REPETITEUR").update(is_active=False)


def reveiller(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(product_type="ADDON_REPETITEUR").update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0022_jusqua_examen_inclut_inedit_gce"),
    ]

    operations = [
        migrations.RunPython(mettre_en_veille, reveiller),
    ]
