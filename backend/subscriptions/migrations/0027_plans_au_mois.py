from django.db import migrations

# Tarification au mois (décision utilisateur du 2026-11-11) : 2 000 FCFA par mois, l'élève
# choisit le nombre de mois. Un plan au mois par cursus qui avait un plan Jusqu'à l'Examen actif ;
# les plans Jusqu'à l'Examen sont DÉSACTIVÉS, jamais supprimés (Transaction/ManualPayment les
# référencent en PROTECT, et les accès déjà vendus gardent leur date de fin). Même réflexe que
# 0013_retire_mensuel. Les anciens plans « Mensuel (30 jours) » restent eux aussi inactifs : ils ont
# des abonnés et un autre sens (pas de remise famille, pas d'inédites), on en crée de nouveaux.
#
# Idempotent : relancée, elle ne recrée aucun plan et ne réactive rien d'autre.

PRIX_MOIS = 2000
JOURS_PAR_MOIS = 30


def _prefixe(plan_jusqua):
    """« BEPC - Jusqu'à l'Examen » -> « BEPC » ; sans séparateur, le nom du cursus."""
    if " - " in plan_jusqua.name:
        return plan_jusqua.name.rsplit(" - ", 1)[0]
    return str(plan_jusqua.cursus)


def appliquer(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    jusqua = Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", is_active=True,
    ).select_related("cursus")
    for plan_jusqua in jusqua:
        existe = Plan.objects.filter(
            product_type="ABONNEMENT", duration_mode="MENSUEL", cursus_id=plan_jusqua.cursus_id,
        ).exists()
        if not existe:
            Plan.objects.create(
                name=f"{_prefixe(plan_jusqua)} - Au mois", cursus_id=plan_jusqua.cursus_id,
                product_type="ABONNEMENT", price=PRIX_MOIS, duration_mode="MENSUEL",
                duration_days=JOURS_PAR_MOIS, is_active=True, inclut_inedit=True,
            )
    jusqua.update(is_active=False)


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    cursus_au_mois = Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="MENSUEL",
    ).values_list("cursus_id", flat=True)
    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN", cursus_id__in=list(cursus_au_mois),
    ).update(is_active=True)
    Plan.objects.filter(product_type="ABONNEMENT", duration_mode="MENSUEL").update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0026_tarif_au_mois"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
