"""
Coche CompetenceItem.est_vitrine pour la sélection de quiz gratuits (un thème par cursus et
matière jouable en entier sans abonnement - voir quiz.services.perimetre_est_vitrine).

La sélection vit ici, en clair, plutôt que dans l'admin : elle se rejoue à l'identique en
production (les ids de Cursus/Tag y diffèrent) et se relit d'un coup d'œil. Chaque entrée est
identifiée par des clés stables (pays, examen, série, code matière, nom du tag), jamais par un id.

    python manage.py definir_quiz_vitrine                 # simulation, n'écrit rien
    python manage.py definir_quiz_vitrine --appliquer     # coche les items de la sélection
    python manage.py definir_quiz_vitrine --retirer       # décoche exactement la sélection
    python manage.py definir_quiz_vitrine --ids           # ids des items, pour l'audit de rendu

Choix (2026-10-12) : les thèmes les plus fréquents aux épreuves officielles du cursus, 5 à 9 items,
sans figure, dont les items sont propres à ce cursus. « tableau de variation » et « tracé de
courbe », pourtant très fréquents, sont écartés (items partagés entre cursus ou à figures).
Le périmètre d'un thème est tout ou rien : un thème offert l'est avec tous ses items VALIDE du
cursus, sans quoi perimetre_est_vitrine refuserait la session.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Cursus, Tag
from quiz.models import CompetenceItem

# (pays, examen, série ou None, code matière, nom exact du Tag)
SELECTION = [
    ("CM", "BEPC", None, "MATHS", "identité remarquable"),
    ("CM", "BEPC", None, "FRANCAIS", "transformation de phrase"),
    ("CM", "BEPC", None, "HISTOIRE", "Seconde Guerre mondiale"),
    ("CM", "BEPC", None, "GEOGRAPHIE", "sous-développement"),
    ("CM", "BEPC", None, "INFORMATIQUE", "codage binaire"),
    ("CM", "BEPC", None, "PHYSIQUE_CHIMIE_TECH", "masse molaire"),
    ("CM", "BEPC", None, "EDUCATION_CIVIQUE", "symboles nationaux"),
    ("CM", "BEPC", None, "ANGLAIS", "present perfect"),
    ("CM", "BEPC", None, "ESPAGNOL", "versión"),
    ("CM", "PROBATOIRE", "A", "MATHS", "dénombrement"),
    ("CM", "PROBATOIRE", "C", "MATHS", "limites"),
    ("CM", "PROBATOIRE", "D", "MATHS", "cercle"),
    ("CM", "PROBATOIRE", "E", "MATHS", "limites"),
    ("CM", "BAC", "A", "MATHS", "limites"),
    ("CM", "BAC", "C", "MATHS", "étude de fonction"),
    ("CM", "BAC", "D", "MATHS", "limites"),
    ("CM", "BAC", "E", "MATHS", "intégrale"),
    ("CM", "BAC", "TI", "MATHS", "dérivée"),
]


def _items_de(pays, examen, serie, code_matiere, nom_tag):
    cursus = Cursus.objects.filter(country__code=pays, examen=examen)
    cursus = cursus.filter(series__code=serie) if serie else cursus.filter(series__isnull=True)
    cursus = cursus.first()
    if cursus is None:
        raise CommandError(f"Cursus introuvable : {pays} {examen} {serie or ''}".strip())
    try:
        theme = Tag.objects.get(name=nom_tag)
    except Tag.DoesNotExist:
        raise CommandError(f"Tag introuvable : {nom_tag!r}") from None
    items = CompetenceItem.objects.filter(
        statut="VALIDE", cursus=cursus, subject__code=code_matiere, theme=theme,
    )
    return cursus, items


class Command(BaseCommand):
    help = "Coche (ou décoche) les quiz gratuits de la sélection - voir la docstring du module."

    def add_arguments(self, parser):
        groupe = parser.add_mutually_exclusive_group()
        groupe.add_argument("--appliquer", action="store_true", help="Cocher est_vitrine sur la sélection.")
        groupe.add_argument("--retirer", action="store_true", help="Décocher est_vitrine sur la sélection.")
        groupe.add_argument("--ids", action="store_true", help="Afficher les ids des items de la sélection.")

    @transaction.atomic
    def handle(self, *args, **options):
        valeur = not options["retirer"]
        ecrire = options["appliquer"] or options["retirer"]
        tous_ids = []
        total = 0
        for cle in SELECTION:
            cursus, items = _items_de(*cle)
            ids = list(items.values_list("id", flat=True))
            if not ids:
                raise CommandError(f"Aucun item VALIDE pour {cle} - sélection périmée ?")
            tous_ids += ids
            deja = items.filter(est_vitrine=valeur).count()
            self.stdout.write(f"{cursus} | {cle[3]} | {cle[4]} : {len(ids)} items ({deja} déjà à {valeur})")
            if ecrire:
                total += items.update(est_vitrine=valeur)
        if options["ids"]:
            self.stdout.write("IDS " + ",".join(str(i) for i in tous_ids))
        verbe = "mis à jour" if ecrire else "concernés (simulation, rien écrit)"
        self.stdout.write(self.style.SUCCESS(f"{len(SELECTION)} thèmes, {len(tous_ids)} items {verbe}."))
