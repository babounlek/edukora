from django.db import migrations, models


def _copy_fk_cursus_to_m2m(apps, schema_editor):
    """Préserve les valeurs existantes de l'ancien FK `cursus` (une valeur par ligne)
    dans le nouveau M2M temporaire, avant que RemoveField ne le supprime - no-op si la
    table est encore vide (voir la docstring de module de inedit.ingestion pour le
    contexte : ce champ passe de FK à M2M pour autoriser une épreuve commune à
    plusieurs séries, ex. Maths BAC C/E)."""
    Blueprint = apps.get_model("inedit", "Blueprint")
    EpreuveInedite = apps.get_model("inedit", "EpreuveInedite")
    for blueprint in Blueprint.objects.all():
        if blueprint.cursus_id is not None:
            blueprint.cursus_m2m.add(blueprint.cursus_id)
    for epreuve in EpreuveInedite.objects.all():
        if epreuve.cursus_id is not None:
            epreuve.cursus_m2m.add(epreuve.cursus_id)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0041_widen_question_numero"),
        ("inedit", "0009_remove_epreuveinedite_corrige_pdf_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="blueprint",
            name="cursus_m2m",
            field=models.ManyToManyField(related_name="blueprints_tmp", to="catalog.cursus"),
        ),
        migrations.AddField(
            model_name="epreuveinedite",
            name="cursus_m2m",
            field=models.ManyToManyField(related_name="epreuves_inedites_tmp", to="catalog.cursus"),
        ),
        migrations.RunPython(_copy_fk_cursus_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="blueprint",
            name="cursus",
        ),
        migrations.RemoveField(
            model_name="epreuveinedite",
            name="cursus",
        ),
        migrations.RenameField(
            model_name="blueprint",
            old_name="cursus_m2m",
            new_name="cursus",
        ),
        migrations.RenameField(
            model_name="epreuveinedite",
            old_name="cursus_m2m",
            new_name="cursus",
        ),
        migrations.AlterField(
            model_name="blueprint",
            name="cursus",
            field=models.ManyToManyField(
                help_text="Plusieurs cursus si l'épreuve est commune à plusieurs séries (ex: Maths BAC C/E).",
                related_name="blueprints",
                to="catalog.cursus",
            ),
        ),
        migrations.AlterField(
            model_name="epreuveinedite",
            name="cursus",
            field=models.ManyToManyField(
                help_text="Plusieurs cursus si l'épreuve est commune à plusieurs séries (ex: Maths BAC C/E) - hérité du Blueprint source à l'ingestion.",
                related_name="epreuves_inedites",
                to="catalog.cursus",
            ),
        ),
    ]
