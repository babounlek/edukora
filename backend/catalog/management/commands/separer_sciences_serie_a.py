from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Cours, Cursus, Lesson, Subject
from inedit.models import Blueprint, EpreuveInedite
from quiz.models import CompetenceItem, CompetenceItemFigure, ObjectifMatiere, RevisionSchedule

SUFFIXE_COPIE = "-sciences-a"


class Command(BaseCommand):
    help = (
        "Sépare la série A de la SVT : crée la matière « Sciences » (code SCIENCES) et y range ce qui est propre à la "
        "série A (Probatoire A, BAC A) - sujets, cours, épreuves inédites, plans, items de quiz. Les items de quiz "
        "PARTAGÉS avec d'autres séries sont DUPLIQUÉS : une copie réservée à la série A passe en Sciences, l'original "
        "garde les autres séries. Aucune suppression ; idempotent ; SIMULATION par défaut (rien n'est écrit sans "
        "--appliquer)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", default="CM")
        parser.add_argument("--appliquer", action="store_true")

    def handle(self, *args, **options):
        pays = options["pays"].upper()
        try:
            svt = Subject.objects.get(country__code__iexact=pays, code="SVT")
        except Subject.DoesNotExist:
            raise CommandError(f"Matière SVT introuvable pour le pays {pays}.")
        cursus_a = list(Cursus.objects.filter(country=svt.country, series__code__iexact="A"))
        if not cursus_a:
            raise CommandError("Aucun cursus de série A.")
        ids_a = {c.id for c in cursus_a}
        ecrire = options["appliquer"]
        self.stdout.write(f"Cursus de série A : {sorted(ids_a)} ; mode {'ÉCRITURE' if ecrire else 'simulation'}")

        with transaction.atomic():
            sciences = Subject.objects.filter(country=svt.country, code="SCIENCES").first()
            if sciences is None:
                self.stdout.write("Matière Sciences : à créer.")
                if ecrire:
                    sciences = Subject.objects.create(
                        country=svt.country, code="SCIENCES", label="Sciences", equivalent_code="SVT", langue=svt.langue,
                    )
            else:
                self.stdout.write(f"Matière Sciences : existe (id {sciences.id}).")
            cible = sciences or svt  # en simulation, on compte sans écrire

            def propres_a(qs):
                """Éléments de SVT dont TOUS les cursus sont de série A (et au moins un)."""
                retenus = []
                for obj in qs.prefetch_related("cursus"):
                    ids = {c.id for c in obj.cursus.all()}
                    if ids and ids <= ids_a:
                        retenus.append(obj.id)
                return retenus

            maintenant = timezone.now()
            for nom, modele in (("Sujets (Lesson)", Lesson), ("Cours", Cours),
                                ("Plans d'épreuve inédite", Blueprint), ("Épreuves inédites", EpreuveInedite)):
                ids = propres_a(modele.objects.filter(subject=svt))
                self.stdout.write(f"{nom} propres à la série A : {len(ids)}")
                if ecrire and ids:
                    champs = {"subject": cible}
                    if any(f.name == "updated_at" for f in modele._meta.get_fields()):
                        champs["updated_at"] = maintenant
                    modele.objects.filter(id__in=ids).update(**champs)

            # Items de quiz : propres à la série A -> déplacés ; partagés -> copie réservée à A + retrait de A de l'original.
            items = CompetenceItem.objects.filter(subject=svt, cursus__in=cursus_a).distinct().prefetch_related("cursus", "figures")
            deplaces = copies = deja = 0
            for item in items:
                ids = {c.id for c in item.cursus.all()}
                if ids <= ids_a:
                    deplaces += 1
                    if ecrire:
                        CompetenceItem.objects.filter(pk=item.pk).update(subject=cible)
                    continue
                ext_copie = f"{item.external_id}{SUFFIXE_COPIE}" if item.external_id else ""
                if ext_copie and CompetenceItem.objects.filter(external_id=ext_copie).exists():
                    deja += 1
                    continue
                copies += 1
                if not ecrire:
                    continue
                copie = CompetenceItem.objects.get(pk=item.pk)
                sources = list(copie.source_exercises.all())
                copie.pk = None
                copie.external_id = ext_copie
                copie.subject = cible
                copie.save()
                copie.cursus.set([c for c in item.cursus.all() if c.id in ids_a])
                copie.source_exercises.set(sources)
                for fig in item.figures.all():
                    CompetenceItemFigure.objects.create(
                        item=copie, external_id=fig.external_id, image=fig.image.name, type_figure=fig.type_figure,
                        legende=fig.legende, origine=fig.origine,
                    )
                item.cursus.remove(*[c for c in item.cursus.all() if c.id in ids_a])
            self.stdout.write(f"Items de quiz propres à la série A déplacés : {deplaces}")
            self.stdout.write(f"Items de quiz partagés dupliqués : {copies} (déjà dupliqués : {deja})")

            # Données d'élèves liées à un cursus de série A (plans de révision, objectifs).
            for nom, modele in (("Plans de révision", RevisionSchedule), ("Objectifs de matière", ObjectifMatiere)):
                qs = modele.objects.filter(subject=svt, cursus__in=cursus_a)
                self.stdout.write(f"{nom} d'élèves de série A : {qs.count()}")
                if ecrire:
                    qs.update(subject=cible)

            if not ecrire:
                transaction.set_rollback(True)

        if ecrire:
            self.stdout.write(self.style.SUCCESS(
                "Terminé. À faire ensuite : `python manage.py indexer_recherche` (recherche globale)."))
        else:
            self.stdout.write("Simulation terminée : relancer avec --appliquer pour écrire.")
