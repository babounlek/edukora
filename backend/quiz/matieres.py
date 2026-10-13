"""
Matières que passe un profil - ce qui distingue, pour le coach, une matière « de l'élève » d'une
matière simplement présente dans le cursus.

Au BEPC, au Probatoire et au BAC, la série fixe les matières : tout le cursus est « à l'élève », et
`Profil.matieres_passees` reste vide. Le GCE n'a pas de séries : un élève passe 5 à 8 matières
qu'il choisit, parmi plusieurs dizaines. Le plan du jour, les priorités, la progression et le
diagnostic se limitent alors à ce choix ; la bibliothèque (épreuves, cours, recherche) reste ouverte
à toutes les matières du cursus.

Règle de repli, partout la même : un choix qui ne recoupe AUCUNE matière du périmètre considéré
(il porte sur un autre cursus, ou sur des matières sans contenu) est ignoré plutôt que de laisser
l'élève devant un plan vide.
"""
from django.db.models import Exists, OuterRef

from catalog.models import Lesson, StatutContenu, Subject

from .models import CompetenceItem


def _choix(profil):
    if profil is None:
        return frozenset()
    return frozenset(profil.matieres_passees.values_list("id", flat=True))


def restreindre_matieres(profil, subjects):
    """Les `subjects` (instances de Subject) que le profil passe ; tous si rien n'est choisi
    ou si le choix ne recoupe pas cette liste. L'ordre reçu est conservé."""
    subjects = list(subjects)
    choix = _choix(profil)
    if not choix:
        return subjects
    gardees = [s for s in subjects if s.id in choix]
    return gardees or subjects


def restreindre_items(profil, items):
    """Même règle pour des éléments portant `subject_id` (CompetenceItem du diagnostic)."""
    items = list(items)
    choix = _choix(profil)
    if not choix:
        return items
    gardes = [i for i in items if i.subject_id in choix]
    return gardes or items


def matieres_disponibles(cursus):
    """Matières qu'un élève de ce cursus peut déclarer passer : celles qui ont du contenu publié
    (une épreuve, ou une banque de quiz) - proposer une matière vide ne mènerait nulle part."""
    avec_epreuve = Exists(
        Lesson.objects.filter(subject=OuterRef("pk"), statut=StatutContenu.VALIDE, cursus=cursus),
    )
    avec_quiz = Exists(
        CompetenceItem.objects.filter(subject=OuterRef("pk"), statut=StatutContenu.VALIDE, cursus=cursus),
    )
    return list(Subject.objects.filter(country=cursus.country).filter(avec_epreuve | avec_quiz).order_by("label"))
