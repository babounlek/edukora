from django.db import migrations

# La session BAC 2027 (Cameroun) avait été saisie à la main, du 15 au 25 juin 2027, et
# s'affichait comme une date exacte. Vérification du 2026-11-16 : aucune source ne la
# confirme, et elle contredit ce qu'on sait du calendrier - elle place le BAC après le
# Probatoire (7 au 11 juin 2027) alors qu'il le précède, lui donne 11 jours d'écrit
# contre 5 en 2026, et s'écarte de trois semaines du BAC technique annoncé du 24 au
# 28 mai 2027. Décision utilisateur du 2026-11-16 : la retirer, pour que le BAC 2027
# retombe sur l'estimation automatique (session 2026 + 1 an, affichée au mois) tant que
# la décision du MINESEC fixant le calendrier 2027 n'a pas été lue pour le BAC général.
#
# Seule cette ligne-là est visée (mêmes dates) : une session BAC 2027 ressaisie entre-temps
# à partir du texte officiel ne doit pas être emportée.
DATE_DEBUT_NON_CONFIRMEE = "2027-06-15"
DATE_FIN_NON_CONFIRMEE = "2027-06-25"


def retirer_bac_2027(apps, schema_editor):
    Country = apps.get_model("catalog", "Country")
    ExamSession = apps.get_model("catalog", "ExamSession")
    cm = Country.objects.filter(code="CM").first()
    if cm is None:
        return
    ExamSession.objects.filter(
        country=cm, examen="BAC", annee=2027,
        date_debut=DATE_DEBUT_NON_CONFIRMEE, date_fin=DATE_FIN_NON_CONFIRMEE,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0071_avis_dans_l_application"),
    ]

    operations = [
        # Pas de retour arrière : on ne réinscrit pas une date dont l'origine est inconnue.
        migrations.RunPython(retirer_bac_2027, migrations.RunPython.noop),
    ]
