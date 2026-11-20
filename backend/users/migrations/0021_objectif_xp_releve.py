from django.db import migrations, models
from django.utils import timezone

# L'objectif du jour passe de 10 / 20 / 30 à 30 / 50 / 80 points (voir quiz.xp) : chaque élève garde le RYTHME qu'il avait
# choisi (tranquille, régulier, intense), avec sa nouvelle valeur. L'ordre compte : 30 est à la fois l'ancien « intense »
# et le nouveau « tranquille », il faut donc convertir du plus grand au plus petit (et l'inverse au retour).
ANCIEN_VERS_NOUVEAU = ((30, 80), (20, 50), (10, 30))


def _convertir(apps, paires):
    Profil = apps.get_model("users", "Profil")
    JourXP = apps.get_model("quiz", "JourXP")
    aujourdhui = timezone.localdate()
    for avant, apres in paires:
        Profil.objects.filter(objectif_xp_quotidien=avant).update(objectif_xp_quotidien=apres)
        # La journée en cours suit, tant que son objectif n'est pas déjà atteint : un jour acquis au rythme d'alors le
        # reste, comme les jours passés (voir JourXP, l'objectif est figé sur la ligne).
        JourXP.objects.filter(jour=aujourdhui, atteint=False, objectif=avant).update(objectif=apres)


def relever(apps, schema_editor):
    _convertir(apps, ANCIEN_VERS_NOUVEAU)


def rabaisser(apps, schema_editor):
    _convertir(apps, [(apres, avant) for avant, apres in reversed(ANCIEN_VERS_NOUVEAU)])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0020_user_est_invite"),
        ("quiz", "0017_gain_xp_jour_xp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profil",
            name="objectif_xp_quotidien",
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text="Rythme que ce profil se fixe, en points d'XP par jour (voir quiz.xp : 30, 50 ou 80). "
                          "Un jour où il est atteint compte pour la série, comme une séance du jour terminée.",
            ),
        ),
        migrations.RunPython(relever, rabaisser),
    ]
