from django.db import migrations

# Référentiel GCE (Cameroun) - décision utilisateur du 2026-10-13. POINT DE DÉPART : la liste
# des matières est celle du tronc commun du GCE camerounais, à valider/compléter avec les
# syllabus du Cameroon GCE Board (matières O/L et A/L à distinguer) et à ajuster ensuite
# depuis l'admin. Codes préfixés GCE_ : ils ne doivent jamais entrer en collision avec les
# matières francophones (Subject est unique par (pays, code) et "MATHS" y est déjà pris),
# et gardent thèmes, programmes et quiz du GCE séparés de ceux du BEPC/Probatoire/BAC.
# Subject.code est limité à 20 caractères.
SUBJECTS_GCE = [
    ("GCE_ENGLISH", "English Language"),
    ("GCE_LITERATURE", "Literature in English"),
    ("GCE_FRENCH", "French"),
    ("GCE_MATHS", "Mathematics"),
    ("GCE_ADD_MATHS", "Additional Mathematics"),
    ("GCE_PURE_MATHS", "Pure Mathematics"),
    ("GCE_FURTHER_MATHS", "Further Mathematics"),
    ("GCE_PHYSICS", "Physics"),
    ("GCE_CHEMISTRY", "Chemistry"),
    ("GCE_BIOLOGY", "Biology"),
    ("GCE_GEOGRAPHY", "Geography"),
    ("GCE_HISTORY", "History"),
    ("GCE_ECONOMICS", "Economics"),
    ("GCE_COMPUTER_SCI", "Computer Science"),
    ("GCE_ICT", "ICT"),
    ("GCE_PHILOSOPHY", "Philosophy"),
    ("GCE_LOGIC", "Logic"),
    ("GCE_RELIGION", "Religious Studies"),
    ("GCE_CITIZENSHIP", "Citizenship Education"),
    ("GCE_FOOD_NUTRITION", "Food and Nutrition"),
    ("GCE_ACCOUNTING", "Accounting"),
    ("GCE_COMMERCE", "Commerce"),
    ("GCE_TECH_DRAWING", "Technical Drawing"),
]

NIVEAUX = ["GCE_OL", "GCE_AL"]
# Libellé court : il s'affiche derrière le nom de l'examen (« GCE Advanced Level Technical »).
SERIE_TECHNIQUE = ("GCE_TECHNICAL", "Technical")


def seed_gce(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    Series = apps.get_model("catalog", "Series")
    Cursus = apps.get_model("catalog", "Cursus")
    ExamSession = apps.get_model("catalog", "ExamSession")

    # Le code unique « GCE » n'existe plus : un Cursus qui l'utiliserait encore ne peut pas
    # être rattaché à un niveau sans deviner (Ordinary ou Advanced ?). Aucun n'existait au
    # 2026-10-13 ; s'il en apparaît un, arrêter plutôt que mal le classer.
    if Cursus.objects.filter(examen="GCE").exists():
        raise RuntimeError("Des Cursus avec l'ancien examen « GCE » existent : les rattacher à GCE_OL ou GCE_AL à la main avant de migrer.")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return

    # Les sessions 2026 saisies sous l'ancien code unique valent pour les deux niveaux : le
    # calendrier officiel les réunit (session écrite unique). Dupliquées telles quelles ; une
    # date propre à un niveau se corrige ensuite depuis l'admin.
    for ancienne in ExamSession.objects.filter(country=cm, examen="GCE"):
        for niveau in NIVEAUX:
            ExamSession.objects.update_or_create(
                country=cm, examen=niveau, annee=ancienne.annee,
                defaults={"date_debut": ancienne.date_debut, "date_fin": ancienne.date_fin},
            )
        ancienne.delete()

    for code, label in SUBJECTS_GCE:
        Subject.objects.get_or_create(country=cm, code=code, defaults={"label": label, "langue": "en"})

    serie, _ = Series.objects.get_or_create(
        country=cm, code=SERIE_TECHNIQUE[0], defaults={"label": SERIE_TECHNIQUE[1], "groupe": "TECHNIQUE"},
    )

    for niveau in NIVEAUX:
        Cursus.objects.get_or_create(country=cm, examen=niveau, series=None)
        Cursus.objects.get_or_create(country=cm, examen=niveau, series=serie)


def unseed_gce(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    Subject = apps.get_model("catalog", "Subject")
    Series = apps.get_model("catalog", "Series")
    Cursus = apps.get_model("catalog", "Cursus")
    ExamSession = apps.get_model("catalog", "ExamSession")

    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return

    # Retour à l'ancien code unique : la session de l'Advanced Level reprend le rôle de l'ancienne.
    for session in ExamSession.objects.filter(country=cm, examen="GCE_AL"):
        ExamSession.objects.update_or_create(
            country=cm, examen="GCE", annee=session.annee,
            defaults={"date_debut": session.date_debut, "date_fin": session.date_fin},
        )
    ExamSession.objects.filter(country=cm, examen__in=NIVEAUX).delete()

    # Les PROTECT (Lesson, Plan...) font échouer l'annulation si du contenu GCE existe déjà : voulu.
    Cursus.objects.filter(country=cm, examen__in=NIVEAUX).delete()
    Series.objects.filter(country=cm, code=SERIE_TECHNIQUE[0]).delete()
    Subject.objects.filter(country=cm, code__in=[c for c, _ in SUBJECTS_GCE]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0062_gce_deux_niveaux_subject_langue"),
    ]

    operations = [
        migrations.RunPython(seed_gce, unseed_gce),
    ]
