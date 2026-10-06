import re

from django.db import migrations

_EPREUVE_BLANCHE = re.compile(r"[ÉéEe]preuve blanche", re.IGNORECASE)


def renommer(apps, schema_editor):
    """« Épreuve blanche n°1 » -> « Épreuve inédite n°1 » : « blanc » désigne déjà, dans le
    catalogue, les vrais examens blancs d'établissement. Le slug (URL publique) n'est
    volontairement pas touché : un lien partagé ne doit jamais casser pour un mot. Idempotent."""
    for nom in ("Blueprint", "EpreuveInedite"):
        modele = apps.get_model("inedit", nom)
        for objet in modele.objects.filter(titre__icontains="preuve blanche"):
            nouveau = _EPREUVE_BLANCHE.sub("Épreuve inédite", objet.titre)
            if nouveau != objet.titre:
                modele.objects.filter(pk=objet.pk).update(titre=nouveau)


class Migration(migrations.Migration):

    dependencies = [
        ("inedit", "0017_profil_remplace_user"),
    ]

    operations = [
        migrations.RunPython(renommer, migrations.RunPython.noop),
    ]
