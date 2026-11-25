"""Ce que voit un élève des Fiches EduKora, et le geste « Garder dans mes notes »."""

from django.conf import settings

from access.models import NoteLibre
from access.services import bulk_active_subscription_cursus_ids
from catalog.models import StatutContenu
from inedit.liens import themes_avec_cours, themes_avec_quiz

from .gratuites import sessions_de
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


def liens_des_fiches(memos, cursus):
    """
    {id de fiche: {"theme": …, "sources": […]}} : de quoi passer d'une fiche à son quiz, à son cours et aux épreuves dont
    elle est tirée. Les fiches n'avaient aucun de ces passages (audit du 2026-11-25). Un lien « quiz » ou « cours » n'est
    annoncé que si le thème a de quoi le remplir ; une source n'est citée que publiée et de cet examen.
    """
    ids_themes = [m.theme_id for m in memos if m.theme_id]
    avec_quiz = themes_avec_quiz(ids_themes, cursus) if ids_themes else set()
    avec_cours = themes_avec_cours(ids_themes, cursus) if ids_themes else set()
    sources = {}
    lignes = (
        Memo.sources.through.objects.filter(
            memo_id__in=[m.pk for m in memos], lesson__statut=StatutContenu.VALIDE, lesson__cursus=cursus,
        )
        .values_list("memo_id", "lesson__slug", "lesson__title", "lesson__year")
        .order_by("-lesson__year", "lesson__title")
    )
    for memo_id, slug, titre, annee in lignes:
        sources.setdefault(memo_id, []).append({"slug": slug, "titre": titre, "annee": annee})
    return {
        m.pk: {
            "theme": (
                {"id": m.theme_id, "nom": m.theme.name, "a_quiz": m.theme_id in avec_quiz, "a_cours": m.theme_id in avec_cours}
                if m.theme_id else None
            ),
            "sources": sources.get(m.pk, []),
        }
        for m in memos
    }


def entree(memo, *, lisible, gardee, cursus_id=None, liens=None):
    """Une fiche telle que l'API la rend. Verrouillée : le terme et les sessions restent visibles (c'est ce qui donne envie),
    jamais la définition."""
    return {
        "id": memo.pk,
        "terme": memo.terme,
        "definition": memo.definition if lisible else None,
        "exemple": memo.exemple if lisible else "",
        "piege": memo.piege if lisible else "",
        "exercice": memo.exercice if lisible else "",
        "reponse": memo.reponse if lisible else "",
        "rubrique": memo.rubrique,
        # Les années de CET examen seulement (voir memos.gratuites).
        "sessions": sessions_de(memo, cursus_id),
        "gratuit": memo.gratuit,
        "verrouillee": not lisible,
        "gardee": gardee,
        "a_relire": memo.statut != StatutMemo.PUBLIE,
        "matiere_id": memo.subject_id,
        **(liens or {"theme": None, "sources": []}),
    }


def garder_dans_les_notes(profil, memo):
    """
    Copie la fiche dans les notes de l'élève : (note, créée ?). Le terme devient le recto de la carte de révision (la
    citation), la définition son verso (la note) : réviser ses notes interroge alors « Scrutin ? » et montre la définition.
    L'exemple et le piège suivent ; l'exercice « À toi » reste sur la fiche, que la note permet de rouvrir.
    Un second appui ne crée pas de doublon.
    """
    existante = NoteLibre.objects.filter(profil=profil, origine=ORIGINE_FICHE, source=source_de(memo)).first()
    if existante is not None:
        return existante, False
    texte = memo.definition
    if memo.exemple:
        texte += f"\n\n{memo.exemple}"
    if memo.piege:
        texte += f"\n\n**Piège** : {memo.piege}"
    note = NoteLibre.objects.create(
        profil=profil, subject=memo.subject, note=texte[:2000], citation=memo.terme, origine=ORIGINE_FICHE,
        source=source_de(memo), theme=memo.theme,
    )
    return note, True
