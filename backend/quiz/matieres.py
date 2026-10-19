"""
Matières que passe un profil - ce qui distingue, pour le coach, une matière « de l'élève » d'une
matière simplement présente dans le cursus.

Au BEPC, au Probatoire et au BAC, la série fixe les matières : tout le cursus est « à l'élève », et
`Profil.matieres_passees` reste vide. Le GCE n'a pas de séries : un élève choisit ses matières
parmi celles du Board (6 à 11 au O Level, 5 au plus à l'A Level : voir REGLES_INSCRIPTION_GCE). Le plan du jour, les priorités, la progression et le
diagnostic se limitent alors à ce choix, ainsi que les listes de la bibliothèque (épreuves, cours,
pastilles de matière, voir sujets_a_afficher) - tant que le profil garde actif « voir seulement mes
matières » (`Profil.voir_seulement_mes_matieres`, une préférence d'affichage séparée de l'inscription).
La recherche reste ouverte à tout le cursus : on y nomme ce qu'on cherche. Rien n'est un contrôle d'accès :
un lien direct vers une épreuve d'une autre matière s'ouvre toujours.

Règle de repli, partout la même : un choix qui ne recoupe AUCUNE matière du périmètre considéré
(il porte sur un autre cursus, ou sur des matières sans contenu) est ignoré plutôt que de laisser
l'élève devant un plan vide.
"""
from django.db.models import Exists, OuterRef

from catalog.models import Examen, Lesson, StatutContenu, Subject

from .models import CompetenceItem

# Règles d'inscription du GCE Board, par niveau (camgceb.org, pages « GCE Ordinary Level » et « GCE Advanced Level »,
# relevées le 2026-10-15). Le O Level exige English Language, French et Mathematics, au moins 6 matières pour un
# candidat complet et au plus 11, la onzième étant Religious Studies. L'A Level en permet au plus 5, sans minimum
# ni matière obligatoire publiés. La page du O Level se contredit sur le minimum (elle cite aussi 4, pour qui ajoute
# des matières à un acquis) : 6 est retenu, « candidat complet ». Ces règles ne bloquent jamais : un élève peut avoir
# une inscription arrêtée par son établissement, voir avertissements_inscription.
REGLES_INSCRIPTION_GCE = {
    Examen.GCE_OL: {
        "minimum": 6, "maximum": 11,
        "obligatoires": ("GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"),
        "derniere": "GCE_RELIGION",
    },
    Examen.GCE_AL: {"minimum": None, "maximum": 5, "obligatoires": (), "derniere": None},
}


def _choix(profil):
    """Les matières à ne montrer QUE : le choix du profil tant que « voir seulement mes matières » est actif,
    rien (donc tout le cursus) sinon. L'inscription elle-même (`matieres_passees`) n'est jamais touchée."""
    if profil is None or not profil.voir_seulement_mes_matieres:
        return frozenset()
    return frozenset(profil.matieres_passees.values_list("id", flat=True))


def sujets_a_afficher(profil, cursus_id):
    """
    Les identifiants de matières à garder dans une liste de la bibliothèque (épreuves, cours, pastilles de
    matière) de l'examen `cursus_id`, ou None quand rien ne se restreint : visiteur anonyme, interrupteur éteint,
    aucune matière choisie, examen autre que celui que prépare le profil, ou choix sans contenu sur cet examen
    (même règle de repli que restreindre_matieres : jamais une liste vide à cause d'un choix).
    """
    if profil is None or not cursus_id or not str(cursus_id).isdigit():
        return None
    # `User.cursus_prepare` est le champ lu partout (celui du profil n'en est que le point de départ, voir
    # users.views._realigner_cursus_prepare).
    cursus = profil.compte.cursus_prepare
    if cursus is None or cursus.id != int(cursus_id):
        return None
    choix = _choix(profil)
    if not choix:
        return None
    gardees = choix & {m.id for m in matieres_disponibles(cursus)}
    return frozenset(gardees) or None


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


def regles_inscription(cursus):
    """
    Les règles d'inscription du Board pour ce cursus (REGLES_INSCRIPTION_GCE), ou None. Seule la branche
    GÉNÉRALE du GCE en a : la branche technique relève d'un autre examen du Board (le TVE, aux règles propres).
    """
    if cursus is None or cursus.series_id is not None:
        return None
    regles = REGLES_INSCRIPTION_GCE.get(cursus.examen)
    return dict(regles) if regles else None


def matieres_officielles(cursus):
    """
    Les matières que le Board propose à ce niveau (Subject.codes_officiels), AVEC OU SANS contenu chez nous :
    c'est la liste de l'inscription, pas celle de l'étude. Vide hors branche générale du GCE.
    """
    if regles_inscription(cursus) is None:
        return []
    return list(
        Subject.objects.filter(country=cursus.country, codes_officiels__has_key=cursus.examen).order_by("label")
    )


def avertissements_inscription(cursus, subjects):
    """
    Ce qui, dans le choix `subjects`, s'écarte des règles du Board - jamais un refus, seulement de quoi prévenir
    l'élève. Un choix vide veut dire « pas encore déclaré » : aucun avertissement.

    Chaque avertissement : {"code": "minimum" | "maximum" | "obligatoire" | "derniere_matiere", ...}
    avec `attendu` et `actuel` pour les bornes, `matiere` (code Subject) pour les deux autres.
    """
    regles = regles_inscription(cursus)
    subjects = list(subjects)
    if regles is None or not subjects:
        return []
    codes = {s.code for s in subjects}
    n = len(codes)
    avertissements = []
    if regles["minimum"] is not None and n < regles["minimum"]:
        avertissements.append({"code": "minimum", "attendu": regles["minimum"], "actuel": n})
    if regles["maximum"] is not None and n > regles["maximum"]:
        avertissements.append({"code": "maximum", "attendu": regles["maximum"], "actuel": n})
    avertissements.extend(
        {"code": "obligatoire", "matiere": code} for code in regles["obligatoires"] if code not in codes
    )
    # Au O Level, la onzième matière doit être Religious Studies.
    if regles["derniere"] and n >= (regles["maximum"] or 0) and regles["derniere"] not in codes:
        avertissements.append({"code": "derniere_matiere", "matiere": regles["derniere"]})
    return avertissements
