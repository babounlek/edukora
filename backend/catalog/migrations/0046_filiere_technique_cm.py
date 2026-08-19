# Reprise de données pour Cameroun (CM), seedé avant l'introduction de Filiere/CAP -
# les pays seedés depuis via `manage.py seed_country` reçoivent déjà tout ceci à la
# création (voir SUBJECTS/SERIES/FILIERES/SPECIALITES dans cette commande, dont ce
# fichier reprend délibérément les mêmes données plutôt que d'appeler la commande
# elle-même : une migration ne doit dépendre que de `apps.get_model`, jamais des
# modèles réels qui peuvent diverger de l'état historique qu'elle représente).
#
# Trois volets, tous décisions utilisateur du 2026-08-19 :
#   1. Filiere (5 familles techniques) + leurs spécialités (Series technique
#      rattachées) + Cursus Probatoire/BAC/CAP associés - CM n'avait, avant Filiere,
#      aucune notion de spécialité technique.
#   2. Correction du libellé TI : hérité à tort de "Techniques Industrielles" alors
#      que TI = Technologie de l'Information, une dominante du général.
#   3. Suppression de COM et SES, deux codes de base hérités d'avant Filiere : COM
#      recoupait Commerce/Comptabilité/Gestion (désormais des spécialités STT) sans y
#      être rattaché et sans aucun contenu ; SES portait 1 Lesson VALIDE (épreuve
#      commune A/C/D/E/SES), qui survit rattachée aux 4 autres séries - seul le Cursus
#      (SES) et la Series elle-même disparaissent, jamais le Lesson.
from django.db import migrations

FILIERES = [
    ("STT", "Sciences et Technologies du Tertiaire"),
    ("STI", "Sciences et Technologies Industrielles"),
    ("ESF_SMS", "Économie Sociale et Familiale / Sciences Médico-Sociales"),
    ("HOTELLERIE_TOURISME", "Hôtellerie et Tourisme"),
    ("AGRICULTURE", "Agriculture et domaines connexes"),
]

SPECIALITES = [
    ("STT", "COMPTABILITE_GESTION", "Comptabilité et Gestion"),
    ("STT", "SECRETARIAT_BUREAUTIQUE", "Secrétariat / Bureautique"),
    ("STT", "COMMERCE", "Commerce"),
    ("STT", "BANQUE", "Banque"),
    ("STI", "ELECTRICITE", "Électricité"),
    ("STI", "ELECTROTECHNIQUE", "Électrotechnique"),
    ("STI", "ELECTRONIQUE", "Électronique"),
    ("STI", "MECANIQUE", "Mécanique"),
    ("STI", "GENIE_CIVIL", "Génie Civil"),
    ("STI", "CONSTRUCTION", "Construction"),
    ("STI", "FABRICATION_MECANIQUE", "Fabrication Mécanique"),
    ("HOTELLERIE_TOURISME", "RESTAURATION", "Restauration"),
    ("HOTELLERIE_TOURISME", "HEBERGEMENT", "Hébergement"),
    ("HOTELLERIE_TOURISME", "TOURISME", "Tourisme"),
]

GENERAL = "GENERAL"
TECHNIQUE = "TECHNIQUE"


def seeder_filieres_et_specialites(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Series = apps.get_model("catalog", "Series")
    Filiere = apps.get_model("catalog", "Filiere")
    Cursus = apps.get_model("catalog", "Cursus")

    try:
        cm = Country.objects.get(code="CM")
    except Country.DoesNotExist:
        return

    filiere_objs = {}
    for code, label in FILIERES:
        filiere, _ = Filiere.objects.get_or_create(country=cm, code=code, defaults={"label": label})
        filiere_objs[code] = filiere

    specialite_series = []
    for filiere_code, series_code, series_label in SPECIALITES:
        series, _ = Series.objects.get_or_create(
            country=cm, code=series_code,
            defaults={"label": series_label, "groupe": TECHNIQUE, "filiere": filiere_objs[filiere_code]},
        )
        specialite_series.append(series)

    for series in specialite_series:
        Cursus.objects.get_or_create(country=cm, examen="PROBATOIRE", series=series)
        Cursus.objects.get_or_create(country=cm, examen="BAC", series=series)
        Cursus.objects.get_or_create(country=cm, examen="CAP", series=series)


def corriger_libelle_ti(apps, schema_editor):
    Series = apps.get_model("catalog", "Series")
    Series.objects.filter(code="TI").update(label="Technologie de l'Information", groupe=GENERAL)


def supprimer_com_et_ses(apps, schema_editor):
    Series = apps.get_model("catalog", "Series")
    Cursus = apps.get_model("catalog", "Cursus")

    # PROTECT sur Cursus.series : le Cursus doit disparaître avant la Series. Le
    # Lesson lui-même n'est jamais touché (relation M2M via Lesson.cursus) - il perd
    # seulement cette entrée-là, pas les autres cursus auxquels il reste rattaché.
    Cursus.objects.filter(series__code__in=["COM", "SES"]).delete()
    Series.objects.filter(code__in=["COM", "SES"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0045_lesson_filiere_serie_a_lesson_institution_and_more"),
    ]

    operations = [
        migrations.RunPython(seeder_filieres_et_specialites, migrations.RunPython.noop),
        migrations.RunPython(corriger_libelle_ti, migrations.RunPython.noop),
        migrations.RunPython(supprimer_com_et_ses, migrations.RunPython.noop),
    ]
