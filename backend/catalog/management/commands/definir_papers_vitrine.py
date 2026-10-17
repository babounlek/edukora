"""
Coche Lesson.est_vitrine pour une sélection de papers en accès libre (voir access.services.has_access :
une Lesson « vitrine » est lisible par n'importe qui, y compris un visiteur anonyme).

La sélection vit ici, en clair, plutôt que dans l'admin : elle se rejoue à l'identique en production (les
ids de Lesson y diffèrent) et se relit d'un coup d'œil. Chaque entrée est identifiée par des clés stables
(pays, examen, titre exact), jamais par un id ni par un slug (suffixé en cas de doublon).

    python manage.py definir_papers_vitrine                 # simulation (annulée), affiche le résultat
    python manage.py definir_papers_vitrine --appliquer     # coche les papers de la sélection
    python manage.py definir_papers_vitrine --retirer       # décoche UNIQUEMENT les papers de la sélection

Contrairement à definir_quiz_vitrine, ce n'est PAS un alignement : seuls les papers listés ici sont
touchés. Les autres papers gratuits (BAC, BEPC, GCE O Level...) ont été posés à la main et restent tels
quels - ne jamais décocher ce qui n'est pas dans SELECTION.

Choix (2026-10-15) - GCE Advanced Level : un paper par matière, le Paper 2 de 2023 (structuré, il montre
le mieux la qualité des corrigés ; 2023 est l'année du lot pilote, présente pour les 4 matières). Même
règle que le O Level : un paper gratuit par matière.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Lesson, StatutContenu

# (pays, examen, titre exact)
SELECTION = [
    ("CM", "GCE_AL", "Biology GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Chemistry GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Computer Science GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Economics GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Further Mathematics GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Geography GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "History GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "ICT GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Physics GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Pure Mathematics with Mechanics GCE A Level 2023 - Paper 2"),
    ("CM", "GCE_AL", "Pure Mathematics with Statistics GCE A Level 2023 - Paper 2"),
    # O Level : les quatre échantillons posés à la main en base locale le 2026-10-14, ajoutés ici le
    # 2026-10-17 pour qu'ils existent aussi en production.
    ("CM", "GCE_OL", "Biology GCE O Level 2019 - Paper 2"),
    ("CM", "GCE_OL", "Chemistry GCE O Level 2020 - Paper 1"),
    ("CM", "GCE_OL", "Mathematics GCE O Level 2019 - Paper 2"),
    ("CM", "GCE_OL", "Physics GCE O Level 2023 - Paper 1"),
]


def _lesson_de(pays, examen, titre):
    lessons = list(
        Lesson.objects.filter(
            statut=StatutContenu.VALIDE, cursus__country__code=pays, cursus__examen=examen, title=titre,
        ).distinct(),
    )
    if len(lessons) != 1:
        raise CommandError(
            f"{len(lessons)} paper(s) VALIDE pour {pays} {examen} {titre!r} (1 attendu) - sélection périmée ?",
        )
    return lessons[0]


class Command(BaseCommand):
    help = "Coche (ou décoche) est_vitrine sur la sélection de papers gratuits - voir la docstring du module."

    def add_arguments(self, parser):
        groupe = parser.add_mutually_exclusive_group()
        groupe.add_argument("--appliquer", action="store_true", help="Cocher est_vitrine sur la sélection.")
        groupe.add_argument("--retirer", action="store_true", help="Décocher est_vitrine sur la sélection (seulement elle).")

    @transaction.atomic
    def handle(self, *args, **options):
        retirer = options["retirer"]
        for cle in SELECTION:
            lesson = _lesson_de(*cle)
            if lesson.est_vitrine == (not retirer):
                self.stdout.write(f"{lesson.title} : déjà {'gratuit' if not retirer else 'payant'}")
                continue
            lesson.est_vitrine = not retirer
            lesson.save(update_fields=["est_vitrine"])
            self.stdout.write(f"{lesson.title} : {'gratuit' if not retirer else 'décoché'}")
        self.stdout.write(self.style.SUCCESS(
            f"{len(SELECTION)} papers {'décochés' if retirer else 'en accès libre'}.",
        ))
        if not (options["appliquer"] or retirer):
            transaction.set_rollback(True)
            self.stdout.write("(simulation : rien n'a été écrit)")
