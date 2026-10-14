from django.db import migrations, models

# Voir catalog.models.EQUIVALENTS_GCE (copie figée : une migration ne dépend jamais du code courant).
EQUIVALENTS_GCE = {
    "GCE_MATHS": "MATHS", "GCE_ADD_MATHS": "MATHS", "GCE_PURE_MATHS": "MATHS", "GCE_FURTHER_MATHS": "MATHS",
    "GCE_PHYSICS": "PHYSIQUE", "GCE_CHEMISTRY": "CHIMIE", "GCE_BIOLOGY": "SVT",
    "GCE_HISTORY": "HISTOIRE", "GCE_GEOGRAPHY": "GEOGRAPHIE", "GCE_ECONOMICS": "ECONOMIE",
    "GCE_PHILOSOPHY": "PHILOSOPHIE", "GCE_LOGIC": "PHILOSOPHIE", "GCE_LITERATURE": "LITTERATURE",
    "GCE_ENGLISH": "ANGLAIS", "GCE_FRENCH": "FRANCAIS",
    "GCE_COMPUTER_SCI": "INFORMATIQUE", "GCE_ICT": "INFORMATIQUE",
    "GCE_CITIZENSHIP": "EDUCATION_CIVIQUE", "GCE_ACCOUNTING": "ECONOMIE", "GCE_COMMERCE": "ECONOMIE",
    "GCE_TECH_DRAWING": "DESSIN",
}


def remplir(apps, schema_editor):
    Subject = apps.get_model("catalog", "Subject")
    for code, equivalent in EQUIVALENTS_GCE.items():
        Subject.objects.filter(code=code).update(equivalent_code=equivalent)


def vider(apps, schema_editor):
    apps.get_model("catalog", "Subject").objects.filter(code__in=EQUIVALENTS_GCE).update(equivalent_code="")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0064_gce_paper_code_regles_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="equivalent_code",
            field=models.CharField(
                blank=True, max_length=20,
                help_text=(
                    "Code de la matière qui lui correspond dans l'autre sous-système (ex. GCE_MATHS -> MATHS, "
                    "GCE_PHYSICS -> PHYSIQUE). Sert à l'AFFICHAGE seulement : icône, couleur et libellé court "
                    "partagés, repérage des matières jumelles. Ce n'est PAS une équivalence de programme, de "
                    "thèmes ni de quiz : ils restent distincts (voir EQUIVALENTS_GCE). Vide = aucune jumelle."
                ),
            ),
        ),
        migrations.RunPython(remplir, vider),
    ]
