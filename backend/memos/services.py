"""Ce que voit un élève des Fiches EduKora, et le geste « Garder dans mes notes »."""

from django.conf import settings

from access.models import NoteLibre
from access.services import bulk_active_subscription_cursus_ids

from .models import Memo, StatutMemo

ORIGINE_FICHE = "fiche"


def visibles():
    """
    Les fiches montrées aux élèves : les publiées. En développement (MEMOS_MONTRER_BROUILLONS), les brouillons s'affichent
    aussi, marqués « à relire » : c'est ce qui permet de voir un pilote avant la relecture, jamais en production.
    """
    if getattr(settings, "MEMOS_MONTRER_BROUILLONS", False):
        return Memo.objects.all()
    return Memo.objects.filter(statut=StatutMemo.PUBLIE)


def a_l_abonnement(user, profil, cursus_id):
    return cursus_id in bulk_active_subscription_cursus_ids(user, profil)


def source_de(memo):
    return f"/fiches-edukora?fiche={memo.pk}"


def gardees(profil, memos):
    """Les ids des fiches déjà gardées dans les notes de ce profil."""
    if profil is None:
        return set()
    sources = {source_de(m): m.pk for m in memos}
    trouvees = NoteLibre.objects.filter(profil=profil, origine=ORIGINE_FICHE, source__in=sources).values_list("source", flat=True)
    return {sources[s] for s in trouvees}


def entree(memo, *, lisible, gardee):
    """Une fiche telle que l'API la rend. Verrouillée : le terme et les sessions restent visibles (c'est ce qui donne envie),
    jamais la définition."""
    return {
        "id": memo.pk,
        "terme": memo.terme,
        "definition": memo.definition if lisible else None,
        "exemple": memo.exemple if lisible else "",
        "sessions": memo.sessions,
        "gratuit": memo.gratuit,
        "verrouillee": not lisible,
        "gardee": gardee,
        "a_relire": memo.statut != StatutMemo.PUBLIE,
        "matiere_id": memo.subject_id,
    }


def garder_dans_les_notes(profil, memo):
    """
    Copie la fiche dans les notes de l'élève : (note, créée ?). Le terme devient le recto de la carte de révision (la
    citation), la définition son verso (la note) : réviser ses notes interroge alors « Scrutin ? » et montre la définition.
    Un second appui ne crée pas de doublon.
    """
    existante = NoteLibre.objects.filter(profil=profil, origine=ORIGINE_FICHE, source=source_de(memo)).first()
    if existante is not None:
        return existante, False
    texte = memo.definition
    if memo.exemple:
        texte += f"\n\n{memo.exemple}"
    note = NoteLibre.objects.create(
        profil=profil, subject=memo.subject, note=texte[:2000], citation=memo.terme, origine=ORIGINE_FICHE,
        source=source_de(memo), theme=memo.theme,
    )
    return note, True
