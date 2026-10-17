from django.db import migrations, models

# Copies figées (une migration ne dépend jamais du code courant) de catalog.models.CODES_OFFICIELS_GCE et
# EQUIVALENTS_GCE, relevées sur camgceb.org (pages GCE Ordinary Level / GCE Advanced Level) le 2026-10-15.
CODES_OFFICIELS_GCE = {
    "GCE_ACCOUNTING": {"GCE_OL": "0505", "GCE_AL": "0705"},
    "GCE_BIOLOGY": {"GCE_OL": "0510", "GCE_AL": "0710"},
    "GCE_CHEMISTRY": {"GCE_OL": "0515", "GCE_AL": "0715"},
    "GCE_COMMERCE": {"GCE_OL": "0520"},
    "GCE_ECONOMICS": {"GCE_OL": "0525", "GCE_AL": "0725"},
    "GCE_ENGLISH": {"GCE_OL": "0530", "GCE_AL": "0730"},
    "GCE_LITERATURE": {"GCE_OL": "0535", "GCE_AL": "0735"},
    "GCE_FOOD_NUTRITION": {"GCE_OL": "0540", "GCE_AL": "0740"},
    "GCE_FRENCH": {"GCE_OL": "0545", "GCE_AL": "0745"},
    "GCE_SBE_FRENCH": {"GCE_OL": "0546", "GCE_AL": "0746"},
    "GCE_GEOGRAPHY": {"GCE_OL": "0550", "GCE_AL": "0750"},
    "GCE_GEOLOGY": {"GCE_OL": "0555", "GCE_AL": "0755"},
    "GCE_HISTORY": {"GCE_OL": "0560", "GCE_AL": "0760"},
    "GCE_CITIZENSHIP": {"GCE_OL": "0562"},
    "GCE_HUMAN_BIOLOGY": {"GCE_OL": "0565"},
    "GCE_MATHS": {"GCE_OL": "0570"},
    "GCE_ADD_MATHS": {"GCE_OL": "0575"},
    "GCE_PHYSICS": {"GCE_OL": "0580", "GCE_AL": "0780"},
    "GCE_RELIGION": {"GCE_OL": "0585", "GCE_AL": "0785"},
    "GCE_LOGIC": {"GCE_OL": "0590"},
    "GCE_COMPUTER_SCI": {"GCE_OL": "0595", "GCE_AL": "0795"},
    "GCE_PM_MECHANICS": {"GCE_AL": "0765"},
    "GCE_PM_STATISTICS": {"GCE_AL": "0770"},
    "GCE_FURTHER_MATHS": {"GCE_AL": "0775"},
    "GCE_PHILOSOPHY": {"GCE_AL": "0790"},
    "GCE_ICT": {"GCE_AL": "0796"},
}

# (code, libellé, jumelle d'affichage) des matières qui manquaient au référentiel de 0063.
NOUVELLES_MATIERES = [
    ("GCE_PM_MECHANICS", "Pure Mathematics with Mechanics", "MATHS"),
    ("GCE_PM_STATISTICS", "Pure Mathematics with Statistics", "MATHS"),
    ("GCE_HUMAN_BIOLOGY", "Human Biology", "SVT"),
    ("GCE_GEOLOGY", "Geology", "SVT"),
    ("GCE_SBE_FRENCH", "Special Bilingual Education French", "FRANCAIS"),
]

# « Pure Mathematics » seule n'est pas une matière du Board : elle est remplacée par les deux ci-dessus.
ANCIENNE_PURE_MATHS = "GCE_PURE_MATHS"


def _est_utilisee(Subject, matiere):
    """Vrai si un objet quelconque (épreuve, cours, quiz, plan...) référence encore cette matière."""
    for relation in Subject._meta.related_objects:
        if relation.related_model.objects.filter(**{relation.field.name: matiere}).exists():
            return True
    return False


def appliquer(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return

    for code, libelle, jumelle in NOUVELLES_MATIERES:
        Subject.objects.get_or_create(
            country=cm, code=code,
            defaults={"label": libelle, "langue": "en", "equivalent_code": jumelle},
        )

    for code, codes in CODES_OFFICIELS_GCE.items():
        Subject.objects.filter(country=cm, code=code).update(codes_officiels=codes)

    # Supprimée seulement si rien ne s'y rattache : sinon elle reste (migrer son contenu vers Mechanics ou
    # Statistics demande de savoir de laquelle des deux il relève, ce qu'une migration ne peut pas deviner).
    ancienne = Subject.objects.filter(country=cm, code=ANCIENNE_PURE_MATHS).first()
    if ancienne is not None and not _est_utilisee(Subject, ancienne):
        ancienne.delete()


def annuler(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return

    Subject.objects.get_or_create(
        country=cm, code=ANCIENNE_PURE_MATHS,
        defaults={"label": "Pure Mathematics", "langue": "en", "equivalent_code": "MATHS"},
    )
    # Une matière nouvelle déjà utilisée par du contenu ne se supprime pas : l'annulation échoue (PROTECT), voulu.
    Subject.objects.filter(country=cm, code__in=[code for code, _, _ in NOUVELLES_MATIERES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0066_examen_gce_libelles_o_level_a_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="codes_officiels",
            field=models.JSONField(
                blank=True, default=dict,
                help_text=(
                    "Codes de matière du GCE Board par niveau, ex. {\"GCE_OL\": \"0510\", \"GCE_AL\": \"0710\"}. "
                    "Une clé présente = la matière est offerte à ce niveau. Vide pour les matières francophones "
                    "et pour une matière que le Board ne propose pas (voir CODES_OFFICIELS_GCE)."
                ),
            ),
        ),
        migrations.RunPython(appliquer, annuler),
    ]
