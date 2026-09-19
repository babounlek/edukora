"""
Reprise du contenu DÉJÀ en base après la décision utilisateur du 2026-09-17 : en
Série TI (Probatoire et BAC), l'Informatique n'est jamais une seule épreuve
généraliste - elle se décompose en trois épreuves distinctes au sein d'une même
session (voir SUBJECT_FAMILIES dans catalog.models et MATIERE_MAP dans
catalog.ingestion) : Programmation, Systèmes d'Information (l'ancien intitulé
"Informatique Théorique" désigne cette même discipline) et Réseaux, Internet et
Sécurité Informatique. Le nouveau mapping ne vaut que pour les ingestions FUTURES,
ré-ingérer ne retouche jamais un Lesson déjà en base dont la Subject a changé (voir
la "promotion, jamais de retour en arrière" dans ingest_exercise).

10 Lesson de Série TI étaient rattachées à INFORMATIQUE au 2026-09-17 (toutes CM,
aucune autre série/pays concernée à cette date) : 9 reclassées d'après l'intitulé
donné par l'utilisateur lui-même (qui a précisé la discipline exacte de chacune),
la 10e (probatoire-blanc-ti-avril-2024-college-vogt-cameroun) d'après son contenu
réel relu (Algorithmique et Langage C + Programmation de sites web - aucun contenu
Systèmes d'Information ou Réseaux) - voir PROGRAMMATION/SYSTEMES_INFORMATION/
RESEAUX_SECURITE ci-dessous.

Non destructive - modifie Lesson.subject/Lesson.title en place (id, slug, Exercise/
Question/Savoir/Tag.savoir_officiel inchangés - voir la docstring de
build_lesson_title : jamais le slug, figé à la création), jamais un ré-import.
Aucun Module officiel de programme ne couvre encore ces trois disciplines pour la
Série TI (gap distinct, à traiter par une campagne rattachement-savoir séparée) :
savoir_officiel reste tel quel sur les sous-questions concernées.

Idempotente : relancer ne change plus rien une fois la reprise faite (recherche par
epreuve_source, pas par Subject.code actuel).

    python manage.py corriger_ti_informatique_split            # simulation
    python manage.py corriger_ti_informatique_split --apply
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import build_lesson_title
from catalog.models import Cours, Lesson, Subject

# epreuve_source -> nouveau code Subject, d'après la discipline réellement examinée
# (voir la docstring ci-dessus pour la source de chaque classification).
PROGRAMMATION = {
    "bac-ti-informatique-programmation-2021-officiel-cameroun.pdf",
    "bac-ti-epreuve-zero-dres-ouest-programmation-2022-cameroun",
    "bac-ti-epreuve-zero-programmation-2022-cameroun",
    "bac-blanc-t-informatique-college-la-retaite-2024-cameroun.pdf",
    # Contenu relu (pas signalé par l'utilisateur) : Algorithmique et Langage C
    # (Partie I) + Programmation de sites web statiques/dynamiques HTML/CSS/JS
    # (Partie II) - aucun contenu de Systèmes d'Information ni de Réseaux.
    "probatoire-blanc-ti-avril-2024-college-vogt-cameroun",
}
SYSTEMES_INFORMATION = {
    "bac-ti-informatique-etude-de-cas-2017-officiel-cameroun",
    "bac-ti-informatique-2018-officiel-cameroun",
    "bac-ti-informatique-etude-de-cas-2020-officiel-cameroun.pdf",
    # "Informatique Théorique" est l'ancien intitulé de cette discipline pour la
    # Série TI (voir la règle dédiée dans le SKILL.md de correction-experte).
    "bac-ti-informatique-theorique-2022-officiel-cameroun.pdf",
    # Blanc Probatoire TI 2023 : titre déjà "Systèmes d'Information", resté sous INFORMATIQUE.
    "probatoire-blanc-ti-SI-bayangam-2023.pdf",
}
RESEAUX_SECURITE = {
    "bac-ti-informatique-reseaux-2021-officiel-cameroun",
    # Ingérée le 2026-09-19 avec matiere="Informatique" (avant le garde-fou d'ingestion
    # `_refuser_informatique_generique_en_serie_ti`) : contenu 100 % réseaux/Internet/sécurité.
    "bac-blanc-ti-reseau-2021-nkongsamba-cameroun.pdf",
}


class Command(BaseCommand):
    help = "Applique au contenu déjà en base la décomposition de l'Informatique en Série TI."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Écrit réellement les corrections (sans cette option : simulation seule).",
        )

    def handle(self, *args, **options):
        appliquer = options["apply"]

        # Recherche par epreuve_source seul (pas par Subject.code actuel) : reste
        # correct que le Lesson soit encore sous INFORMATIQUE ou déjà reclassé par un
        # run précédent de cette commande.
        lessons_par_code = {}
        for epreuve_source, code in [
            *((s, "PROGRAMMATION") for s in PROGRAMMATION),
            *((s, "SYSTEMES_INFORMATION") for s in SYSTEMES_INFORMATION),
            *((s, "RESEAUX_SECURITE") for s in RESEAUX_SECURITE),
        ]:
            lesson = Lesson.objects.filter(epreuve_source=epreuve_source).select_related("subject__country").prefetch_related("cursus").first()
            if lesson is None:
                self.stdout.write(self.style.WARNING(f"Lesson introuvable pour epreuve_source={epreuve_source!r}"))
                continue
            lessons_par_code.setdefault(code, []).append(lesson)

        # Titre recalculé (jamais le slug, figé à la création) seulement si l'actuel
        # correspond exactement à ce que build_lesson_title aurait produit sous
        # l'ancienne Subject INFORMATIQUE - récupérée explicitement par (pays, code)
        # plutôt que via lesson.subject, qui peut déjà pointer vers la nouvelle
        # Subject si la commande a déjà tourné une première fois. Un titre retouché à
        # la main est laissé tel quel (même garde-fou que corriger_series_et_reperes).
        plan = []
        for code, lessons in lessons_par_code.items():
            for lesson in lessons:
                cursus_list = list(lesson.cursus.all())
                informatique = Subject.objects.get(country=lesson.subject.country, code="INFORMATIQUE")
                nouveau_subject = Subject.objects.get(country=lesson.subject.country, code=code)
                ancien_attendu = build_lesson_title(
                    informatique, cursus_list, lesson.year, lesson.origine, lesson.etablissement,
                    lesson.nature_epreuve, lesson.partie_epreuve_francais, lesson.variante_sujet,
                    lesson.filiere_serie_a,
                )
                nouveau_attendu = build_lesson_title(
                    nouveau_subject, cursus_list, lesson.year, lesson.origine, lesson.etablissement,
                    lesson.nature_epreuve, lesson.partie_epreuve_francais, lesson.variante_sujet,
                    lesson.filiere_serie_a,
                )
                # lesson.title == nouveau_attendu : déjà repris par un run précédent,
                # rien à re-signaler comme "retouché à la main".
                auto_genere = lesson.title in (ancien_attendu, nouveau_attendu)
                nouveau_titre = nouveau_attendu if auto_genere else None
                plan.append((lesson, nouveau_subject, nouveau_titre))
                if not auto_genere:
                    self.stdout.write(self.style.WARNING(
                        f"  {lesson.title!r} : titre retouché à la main, subject seul changé vers {code} "
                        f"(titre attendu si auto-généré : {ancien_attendu!r}).",
                    ))
                elif lesson.title != nouveau_attendu:
                    self.stdout.write(f"  {lesson.title!r} -> {nouveau_attendu!r} ({code})")
                else:
                    self.stdout.write(f"  {lesson.title!r} : déjà à jour ({code})")

        self.stdout.write(
            f"{len(lessons_par_code.get('PROGRAMMATION', []))} Lesson -> PROGRAMMATION, "
            f"{len(lessons_par_code.get('SYSTEMES_INFORMATION', []))} Lesson -> SYSTEMES_INFORMATION, "
            f"{len(lessons_par_code.get('RESEAUX_SECURITE', []))} Lesson -> RESEAUX_SECURITE.",
        )
        if not appliquer:
            self.stdout.write(self.style.WARNING("Simulation seule (--apply pour écrire)."))
            return

        with transaction.atomic():
            for lesson, nouveau_subject, nouveau_titre in plan:
                lesson.subject = nouveau_subject
                update_fields = ["subject", "updated_at"]
                if nouveau_titre is not None and nouveau_titre != lesson.title:
                    lesson.title = nouveau_titre
                    update_fields.append("title")
                lesson.save(update_fields=update_fields)
                # Les Cours dérivés des rappels de cette épreuve suivent sa discipline
                # (ils portent leur propre Subject) : sans ça ils resteraient sous INFORMATIQUE.
                cours_suivis = Cours.objects.filter(
                    rappels_source__exercise__lesson=lesson, subject__code="INFORMATIQUE",
                ).distinct()
                for cours in cours_suivis:
                    cours.subject = nouveau_subject
                    cours.save(update_fields=["subject", "updated_at"] if hasattr(cours, "updated_at") else ["subject"])

        self.stdout.write(self.style.SUCCESS("Décomposition de l'Informatique en Série TI appliquée."))
