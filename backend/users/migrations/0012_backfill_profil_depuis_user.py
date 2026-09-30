"""
Un `Profil` par `User` existant, pour que l'introduction des profils multiples
(compte famille) soit invisible à tout compte qui n'en ajoute pas volontairement un
second - voir la docstring de `users.models.Profil`.

Déterministe et sûr : à l'instant précis où cette migration tourne, `Profil` vient
d'être créé (migration précédente) et ne peut donc contenir aucune ligne préexistante
- chaque `User` reçoit exactement un profil, avec son `cursus_prepare` et ses réglages
de rappel d'alors copiés tels quels. `prenom` part du premier mot de `full_name` (le
prénom, ce que le coach quotidien doit dire, jamais le nom de famille), à défaut vide.

Même patron que 0006_compte_unique_e164_authidentity.py : la logique de découpage du
prénom est dupliquée ICI plutôt qu'importée d'un module applicatif qui évoluera - une
migration doit rester figée dans le temps.

Contrairement à 0009_backfill_cursus_prepare_depuis_abonnement (reverse en noop, qui
ne peut pas distinguer après coup ce qu'elle a posé de ce que l'utilisateur a déclaré
ensuite), le sens inverse ICI est réel et sûr : à ce point du graphe de migrations,
aucun Profil ne peut exister que ceux créés ici, donc les supprimer tous les annule
proprement.
"""
from django.db import migrations


def _prenom_depuis(full_name):
    if not full_name:
        return ""
    return full_name.strip().split(" ")[0]


def creer_profil_par_defaut(apps, schema_editor):
    User = apps.get_model("users", "User")
    Profil = apps.get_model("users", "Profil")

    profils = [
        Profil(
            compte_id=user.id,
            prenom=_prenom_depuis(user.full_name),
            cursus_prepare_id=user.cursus_prepare_id,
            rappels_actifs=user.rappels_actifs,
            rappels_invite_refusee_at=user.rappels_invite_refusee_at,
        )
        for user in User.objects.all().only(
            "id", "full_name", "cursus_prepare_id", "rappels_actifs", "rappels_invite_refusee_at",
        )
    ]
    Profil.objects.bulk_create(profils, batch_size=500)


def supprimer_profils_par_defaut(apps, schema_editor):
    Profil = apps.get_model("users", "Profil")
    Profil.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0011_profil"),
    ]

    operations = [
        migrations.RunPython(creer_profil_par_defaut, supprimer_profils_par_defaut),
    ]
