from django.db import migrations

# Plan « Jusqu'à l'Examen » du GCE Ordinary Level (Cameroun) - décision utilisateur du 2026-10-13 : un abonnement PAR
# NIVEAU (un Cursus = un Plan), sur le modèle des autres cursus commercialisés (voir 0018 : 15 000 FCFA par enfant,
# durée calculée jusqu'à la dernière épreuve de la session, voir Plan.effective_duration_days).
#
# SEMÉ DÉSACTIVÉ (is_active=False) : activer ce plan ouvre une vente réelle (Campay, paiement manuel), alors que le GCE
# n'a pas encore ses quiz ni ses cours. Une migration qui se déploie ne doit pas décider seule de la mise en vente ;
# l'activation est un geste délibéré depuis l'admin (Plan > cocher « actif »), une fois le contenu jugé prêt.
#
# Seul le cursus GENERAL de l'Ordinary Level est semé : l'Advanced Level et la branche technique n'ont encore aucun
# contenu publié (ils n'apparaissent pas au catalogue), leur ouvrir un plan vendrait du vide.
# `inclut_inedit` reste à False : le GCE n'a pas d'épreuves inédites ; le cocher promettrait un add-on inexistant.

NOM = "GCE Ordinary Level - Jusqu'à l'Examen"
PRIX = 15000


def appliquer(apps, schema_editor):
    Cursus = apps.get_model("catalog", "Cursus")
    Plan = apps.get_model("subscriptions", "Plan")
    cursus = Cursus.objects.filter(country__code="CM", examen="GCE_OL", series__isnull=True).first()
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
        cursus__country__code="CM", cursus__examen="GCE_OL", cursus__series__isnull=True,
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", name=NOM,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0063_seed_gce_referentiel"),
        ("subscriptions", "0018_tarif_unique_jusqua_examen"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
