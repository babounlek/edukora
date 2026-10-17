from django.db import migrations

# Plan « Jusqu'à l'Examen » du GCE Advanced Level (Cameroun) - un abonnement PAR NIVEAU (un Cursus = un Plan), comme le
# GCE O Level (voir 0019) : même grille unique (15 000 FCFA par enfant, durée calculée jusqu'à la dernière épreuve de la
# session, voir Plan.effective_duration_days).
#
# SEMÉ DÉSACTIVÉ (is_active=False), pour la même raison qu'en 0019 : activer ce plan ouvre une vente réelle (Campay, paiement
# manuel), et l'A Level ne porte pour l'instant que des sujets corrigés (Chimie, Physique, Biologie), sans quiz ni cours. La
# mise en vente est un geste délibéré depuis l'admin (Plan > cocher « actif »).
#
# Seul le cursus GENERAL de l'Advanced Level est semé (pas de série, pas de branche technique : aucun contenu publié).
# `inclut_inedit` reste à False : le GCE n'a pas d'épreuves inédites.

NOM = "GCE A Level - Jusqu'à l'Examen"
PRIX = 15000


def appliquer(apps, schema_editor):
    Cursus = apps.get_model("catalog", "Cursus")
    Plan = apps.get_model("subscriptions", "Plan")
    cursus = Cursus.objects.filter(country__code="CM", examen="GCE_AL", series__isnull=True).first()
    if cursus is None:
        return
    Plan.objects.update_or_create(
        cursus=cursus, product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN",
        defaults={"name": NOM, "price": PRIX, "duration_days": 30, "is_active": False, "inclut_inedit": False},
    )


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    # Transaction/ManualPayment référencent Plan en PROTECT : l'annulation échoue si ce plan a déjà été acheté, voulu.
    Plan.objects.filter(
        cursus__country__code="CM", cursus__examen="GCE_AL", cursus__series__isnull=True,
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", name=NOM,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0063_seed_gce_referentiel"),
        ("subscriptions", "0020_plan_gce_ol_nom_o_level"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
