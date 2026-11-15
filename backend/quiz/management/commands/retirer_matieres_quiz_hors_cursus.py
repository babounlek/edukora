import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.models import Cours, Cursus, Lesson
from programme.models import Module
from quiz.models import CompetenceItem

# Matières de la filière informatique, rattachées à toutes les séries du BAC par l'ingestion alors que seule
# la série TI les enseigne (épreuves, cours et programme officiel n'existent que là).
MATIERES_PAR_DEFAUT = ["PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE"]


class Command(BaseCommand):
    help = (
        "Détache les quiz d'une matière des examens où elle n'existe pas : aucune épreuve, aucun cours et aucun "
        "module de programme officiel pour ce cursus. Ne supprime AUCUN item (seul le lien item-cursus est retiré), "
        "écrit la liste des liens retirés dans un fichier JSON pour pouvoir les rétablir, et laisse tel quel un "
        "item qui n'aurait plus aucun cursus. Sans --appliquer : simple compte. Idempotente."
    )

    def add_arguments(self, parser):
        parser.add_argument("--matieres", nargs="*", default=MATIERES_PAR_DEFAUT, help="Codes de matière.")
        parser.add_argument("--appliquer", action="store_true", help="Retire réellement les liens.")
        parser.add_argument("--sauvegarde", default="", help="Chemin du JSON des liens retirés.")

    def handle(self, *args, **options):
        liens = []
        for code in options["matieres"]:
            cursus_concernes = Cursus.objects.filter(
                competence_items__subject__code=code, competence_items__statut="VALIDE"
            ).distinct()
            sans_contenu = []
            for cursus in cursus_concernes:
                existe = (
                    Lesson.objects.filter(subject__code=code, cursus=cursus).exists()
                    or Cours.objects.filter(subject__code=code, cursus=cursus).exists()
                    or Module.objects.filter(subject__code=code, cursus=cursus).exists()
                )
                if not existe:
                    sans_contenu.append(cursus.pk)
            for cursus_pk in sans_contenu:
                items = CompetenceItem.objects.filter(subject__code=code, cursus__pk=cursus_pk)
                # Un item n'est détaché que s'il reste rattaché à au moins un cursus où la matière existe.
                a_retirer = items.filter(cursus__in=Cursus.objects.exclude(pk__in=sans_contenu)).distinct()
                orphelins = items.count() - a_retirer.count()
                self.stdout.write(
                    f"{code} / cursus {cursus_pk} : {a_retirer.count()} lien(s) à retirer, {orphelins} item(s) laissé(s)."
                )
                liens += [{"item": pk, "cursus": cursus_pk, "matiere": code} for pk in a_retirer.values_list("pk", flat=True)]

        if not options["appliquer"]:
            self.stdout.write(f"{len(liens)} lien(s) seraient retirés (rien n'est écrit sans --appliquer).")
            return
        if not liens:
            self.stdout.write("Rien à faire.")
            return

        chemin = Path(options["sauvegarde"] or f"liens_quiz_retires_{datetime.now():%Y%m%d-%H%M%S}.json")
        chemin.write_text(json.dumps(liens, indent=1), encoding="utf-8")
        par_cursus = {}
        for lien in liens:
            par_cursus.setdefault(lien["cursus"], []).append(lien["item"])
        Through = CompetenceItem.cursus.through
        for cursus_pk, pks in par_cursus.items():
            Through.objects.filter(cursus_id=cursus_pk, competenceitem_id__in=pks).delete()
        self.stdout.write(self.style.SUCCESS(f"{len(liens)} lien(s) retiré(s). Sauvegarde : {chemin}"))
