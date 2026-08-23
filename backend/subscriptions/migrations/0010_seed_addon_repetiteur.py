from django.db import migrations

# Add-on Fiches (répétiteurs/enseignants, voir app "fiches") - décision utilisateur du
# 2026-08-22 : reprend telle quelle la grille déjà présente en base (créée à la main
# pendant le développement, ids 58/59, cursus_id=20 = BAC Série C Cameroun) et la
# propage à tous les cursus déjà commercialisés pour l'abonnement classique. Jusqu'ici
# l'onglet "Répétiteur ou enseignant" de /tarifs n'affichait une offre que sur ce seul
# cursus (11 commercialisés au total pour ABONNEMENT à la date de cette migration) -
# le parcours technique (paiement, activation, génération de fiches) était déjà
# fonctionnel de bout en bout, seule la grille commerciale manquait.

PALIER_30J = {"price": 3000, "duration_days": 30, "duree_label": "30 jours"}
PALIER_1AN = {"price": 20000, "duration_days": 365, "duree_label": "1 an"}

EXAMEN_LABELS = {
    "BEPC": "BEPC",
    "PROBATOIRE": "Probatoire",
    "BAC": "BAC",
    "AUTRE": "Devoir surveille / Autre",
}


def _libelle_cursus(cursus):
    """Même reconstruction manuelle que 0002_seed_plans/0009_grille_deux_paliers : les
    modèles historiques d'une migration n'ont ni __str__ ni get_FOO_display."""
    examen_label = EXAMEN_LABELS.get(cursus.examen, cursus.examen)
    return f"{examen_label} Série {cursus.series.code}" if cursus.series_id else examen_label


def appliquer(apps, schema_editor):
    Cursus = apps.get_model("catalog", "Cursus")
    Plan = apps.get_model("subscriptions", "Plan")

    # Mêmes cursus que l'abonnement classique (au moins un Plan ABONNEMENT existant,
    # même filtre que 0009_grille_deux_paliers) - l'add-on Fiches s'appuie sur le même
    # contenu (CompetenceItem), pas de raison de le vendre là où l'abonnement de base
    # ne l'est pas.
    cursus_commercialises = set(
        Plan.objects.filter(product_type="ABONNEMENT").values_list("cursus_id", flat=True)
    )

    for cursus in Cursus.objects.filter(id__in=cursus_commercialises).select_related("series"):
        libelle = _libelle_cursus(cursus)

        for palier in (PALIER_30J, PALIER_1AN):
            Plan.objects.update_or_create(
                cursus=cursus, product_type="ADDON_REPETITEUR", duration_mode="FIXE",
                duration_days=palier["duration_days"],
                defaults={
                    "name": f"{libelle} - Add-on Fiches ({palier['duree_label']})",
                    "price": palier["price"], "is_active": True,
                },
            )


def annuler(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(
        product_type="ADDON_REPETITEUR", duration_mode="FIXE", duration_days__in=[30, 365],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0009_grille_deux_paliers"),
    ]

    operations = [
        migrations.RunPython(appliquer, annuler),
    ]
