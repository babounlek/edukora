from django.core.management.base import BaseCommand

from catalog.ingestion import _strip_em_dash
from catalog.models import Cours, Exercise, Lesson, Question, RappelDeMethode


class Command(BaseCommand):
    help = (
        "Filet de sécurité rétroactif : remplace le tiret cadratin (—) par un tiret "
        "simple (-) dans tout le contenu déjà en base - au cas où il aurait été "
        "ingéré avant que catalog.ingestion.run_ingestion applique ce nettoyage "
        "automatiquement à la source (voir _strip_em_dash)."
    )

    def handle(self, *args, **options):
        # Question porte désormais le contenu source (Exercise.enonce_markdown/
        # corrige_markdown est compilé depuis les Question, voir
        # Exercise.compile_from_questions) - on nettoie donc Question, puis on
        # recompile Exercise pour propager la correction.
        question_fixed = 0
        exercises_a_recompiler = set()
        for question in Question.objects.all():
            enonce = _strip_em_dash(question.enonce_markdown)
            corrige = _strip_em_dash(question.corrige_markdown)
            if enonce != question.enonce_markdown or corrige != question.corrige_markdown:
                question.enonce_markdown = enonce
                question.corrige_markdown = corrige
                question.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])
                question_fixed += 1
                exercises_a_recompiler.add(question.exercise_id)

        exercise_fixed = 0
        for exercise in Exercise.objects.filter(pk__in=exercises_a_recompiler):
            exercise.compile_from_questions()
            exercise_fixed += 1

        rappel_fixed = 0
        for rappel in RappelDeMethode.objects.all():
            competence = _strip_em_dash(rappel.competence)
            contenu = _strip_em_dash(rappel.contenu_markdown)
            if competence != rappel.competence or contenu != rappel.contenu_markdown:
                rappel.competence = competence
                rappel.contenu_markdown = contenu
                rappel.save(update_fields=["competence", "contenu_markdown"])
                rappel_fixed += 1

        cours_fixed = 0
        for cours in Cours.objects.all():
            titre = _strip_em_dash(cours.titre)
            sous_theme = _strip_em_dash(cours.sous_theme)
            sections = _strip_em_dash(cours.sections_raw)
            if titre != cours.titre or sous_theme != cours.sous_theme or sections != cours.sections_raw:
                cours.titre = titre
                cours.sous_theme = sous_theme
                cours.sections_raw = sections
                cours.save(update_fields=["titre", "sous_theme", "sections_raw", "updated_at"])
                cours_fixed += 1

        # Recompile pour propager les corrections aux content_markdown dérivés
        # (compile_from_exercices/compile_from_sections lisent les champs sources
        # qu'on vient de corriger, donc un simple recalcul suffit, pas de duplication).
        for lesson in Lesson.objects.filter(exercises__isnull=False).distinct():
            lesson.compile_from_exercises()
        for cours in Cours.objects.all():
            cours.compile_from_sections()

        self.stdout.write(self.style.SUCCESS(
            f"{question_fixed} question(s) ({exercise_fixed} exercice(s) recompilé(s)), "
            f"{rappel_fixed} rappel(s) de méthode, {cours_fixed} cours corrigé(s). "
            "Contenus compilés recalculés.",
        ))
