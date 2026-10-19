from django.db import migrations

# « Jusqu'à l'Examen » donne droit aux épreuves inédites quel que soit le cursus (décision produit du 2026-09-30,
# voir Plan.inclut_inedit). Les plans GCE O Level / A Level (0019, 0021) avaient été semés avec inclut_inedit=False
# (« le GCE n'a pas d'épreuves inédites ») : leur paiement n'activait donc jamais l'InscriptionInedite, et /mes-acces
# n'affichait pas « Épreuves inédites incluses » pour ces abonnés. Le GCE a désormais des inédites publiées.
#
# Deux gestes : (1) aligner les plans, (2) rattraper les abonnements « Jusqu'à l'Examen » déjà actifs sans
# InscriptionInedite, avec la même échéance que l'abonnement (même durée, comme _activer_acces).


def appliquer(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Subscription = apps.get_model("subscriptions", "Subscription")
    InscriptionInedite = apps.get_model("subscriptions", "InscriptionInedite")

    Plan.objects.filter(product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", inclut_inedit=False).update(
        inclut_inedit=True,
    )

    for sub in Subscription.objects.filter(duration_mode="JUSQUA_EXAMEN"):
        InscriptionInedite.objects.get_or_create(
            user_id=sub.user_id, cursus_id=sub.cursus_id, profil_id=sub.profil_id,
            defaults={"expires_at": sub.expires_at},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0021_seed_plan_gce_al"),
    ]

    operations = [
        # Pas d'inverse utile : on ne sait plus quelles lignes étaient à False avant.
        migrations.RunPython(appliquer, migrations.RunPython.noop),
    ]
