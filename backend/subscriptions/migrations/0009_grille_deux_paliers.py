from django.db import migrations

# Refonte de la grille tarifaire - décision utilisateur du 2026-08-19, en remplacement
# direct de la grille initiale (0002_seed_plans : Essentiel 500 FCFA/7j, Performance
# 1500 FCFA/30j, Max 15000 FCFA/365j). Deux paliers seulement désormais :
#
#   Mensuel           2 000 FCFA / 30 jours, jamais d'inédites - porte d'entrée à
#                      faible risque, et référence de prix pour Jusqu'à l'Examen
#                      (voir subscriptions.models.Plan.effective_price).
#   Jusqu'à l'Examen   prix dynamique (plafond 12 000 FCFA, jamais plus cher au jour
#                      que Mensuel, plancher 3 000 FCFA), inédites incluses, expire
#                      réellement au jour de la session (duration_mode=JUSQUA_EXAMEN,
#                      calculé depuis ExamSession - voir effective_duration_days).
#
# "Mensuel" reprend la ligne existante à 30 jours (l'ancien "Performance") plutôt que
# d'en créer une nouvelle : même durée, get_or_create créerait un doublon silencieux
# jamais désactivé par la boucle ci-dessous. Tout autre palier FIXE (7j, 90j, 365j -
# désactivation par exclusion plutôt que par liste : la base peut porter des paliers
# intermédiaires jamais reflétés dans une migration committée, voir la refonte du
# 2026-08-16 restée non committée) est simplement désactivé (is_active=False), jamais
# supprimé - Transaction/ManualPayment les référencent en PROTECT.

ANCIENNE_DUREE_REPRISE = 30

MENSUEL = {"price": 2000, "formule": "Mensuel", "duree_label": "30 jours"}
ANCIEN_PALIER_30J = {"price": 1500, "formule": "Performance", "duree_label": "1 mois"}

JUSQUA_EXAMEN = {"price": 12000, "formule": "Jusqu'à l'Examen"}

EXAMEN_LABELS = {
    "BEPC": "BEPC",
    "PROBATOIRE": "Probatoire",
    "BAC": "BAC",
    "AUTRE": "Devoir surveille / Autre",
}


def _libelle_cursus(cursus):
    """Même reconstruction manuelle que 0002_seed_plans : les modèles historiques
    d'une migration n'ont ni __str__ ni get_FOO_display."""
    examen_label = EXAMEN_LABELS.get(cursus.examen, cursus.examen)
    return f"{examen_label} Série {cursus.series.code}" if cursus.series_id else examen_label


def appliquer(apps, schema_editor):
    Cursus = apps.get_model("catalog", "Cursus")
    Plan = apps.get_model("subscriptions", "Plan")
    ExamSession = apps.get_model("catalog", "ExamSession")

    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="FIXE",
    ).exclude(duration_days=ANCIENNE_DUREE_REPRISE).update(is_active=False)

    # Cursus déjà commercialisés (au moins un Plan ABONNEMENT existant) : seuls eux
    # reçoivent la nouvelle grille, pour ne pas ouvrir à la vente un cursus qui n'en
    # avait jamais eu (même filtre que la seed initiale, portée par l'existence d'un
    # Plan plutôt que par is_active - un cursus dont l'unique Plan aurait été
    # désactivé après coup reste "déjà commercialisé").
    cursus_commercialises = set(
        Plan.objects.filter(product_type="ABONNEMENT").values_list("cursus_id", flat=True)
    )
    # (pays, examen) avec une date de session officielle saisie : sans elle, Jusqu'à
    # l'Examen retomberait silencieusement sur une durée de repli plutôt que d'expirer
    # au bon jour (voir Plan.effective_duration_days).
    avec_session = set(ExamSession.objects.values_list("country_id", "examen"))

    for cursus in Cursus.objects.filter(id__in=cursus_commercialises).select_related("series"):
        libelle = _libelle_cursus(cursus)

        Plan.objects.update_or_create(
            cursus=cursus, product_type="ABONNEMENT", duration_mode="FIXE", duration_days=ANCIENNE_DUREE_REPRISE,
            defaults={
                "name": f"{libelle} - {MENSUEL['formule']} ({MENSUEL['duree_label']})",
                "price": MENSUEL["price"], "is_active": True, "inclut_inedit": False,
            },
        )

        if (cursus.country_id, cursus.examen) not in avec_session:
            continue

        Plan.objects.update_or_create(
            cursus=cursus, product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN",
            defaults={
                "name": f"{libelle} - {JUSQUA_EXAMEN['formule']}",
                "price": JUSQUA_EXAMEN["price"], "duration_days": 30, "is_active": True, "inclut_inedit": True,
            },
        )


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")

    Plan.objects.filter(product_type="ABONNEMENT", duration_mode="JUSQUA_EXAMEN").delete()

    for plan in Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="FIXE", duration_days=ANCIENNE_DUREE_REPRISE,
    ).select_related("cursus", "cursus__series"):
        libelle = _libelle_cursus(plan.cursus)
        plan.name = f"{libelle} - {ANCIEN_PALIER_30J['formule']} ({ANCIEN_PALIER_30J['duree_label']})"
        plan.price = ANCIEN_PALIER_30J["price"]
        plan.inclut_inedit = False
        plan.save(update_fields=["name", "price", "inclut_inedit"])

    Plan.objects.filter(
        product_type="ABONNEMENT", duration_mode="FIXE",
    ).exclude(duration_days=ANCIENNE_DUREE_REPRISE).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0008_alter_plan_product_type_inscriptionrepetiteur"),
        ("catalog", "0044_seed_espagnol"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
