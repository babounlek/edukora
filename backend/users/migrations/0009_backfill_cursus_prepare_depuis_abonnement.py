from django.db import migrations
from django.db.models import Count
from django.utils import timezone


def backfill(apps, schema_editor):
    """
    Reprend le cursus des abonnés existants qui n'ont rien déclaré - même règle que
    SubscriptionManager.activate_or_extend, appliquée une fois aux abonnements déjà
    en cours au moment de la migration (eux n'ont jamais eu l'occasion de passer par
    ce chemin).

    Seulement quand l'abonnement actif est UNIQUE : deux abonnements actifs ne disent
    pas lequel l'élève prépare, et deviner ici lui collerait un compte à rebours vers
    le mauvais examen - alors qu'il suffit de ne rien faire pour qu'on le lui demande.
    """
    User = apps.get_model("users", "User")
    Subscription = apps.get_model("subscriptions", "Subscription")

    actifs = (
        Subscription.objects.filter(expires_at__gt=timezone.now(), user__cursus_prepare__isnull=True)
        .values("user_id")
        .annotate(n=Count("id"))
        .filter(n=1)
    )
    for ligne in actifs:
        abonnement = Subscription.objects.filter(
            user_id=ligne["user_id"], expires_at__gt=timezone.now()
        ).first()
        if abonnement is not None:
            User.objects.filter(pk=ligne["user_id"]).update(cursus_prepare=abonnement.cursus_id)


def noop(apps, schema_editor):
    """
    Irréversible volontairement : on ne sait pas distinguer, au retour, un cursus posé
    par cette migration d'un cursus que l'utilisateur a déclaré lui-même depuis. Tout
    effacer détruirait ses déclarations réelles, ne rien faire est sans danger (le
    champ redevient simplement un champ comme un autre).
    """


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_user_cursus_prepare"),
        ("subscriptions", "0015_hausse_plancher_plafond_2"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
