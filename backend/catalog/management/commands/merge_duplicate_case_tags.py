from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Cours, Exercise, Lesson, Question, Tag
from fiches.models import FicheGeneree
from inedit.models import Blueprint, QuestionInedite
from quiz.models import CompetenceItem, QuizSession, RevisionSchedule

# Chaque (modèle, champ) porte une relation M2M vers Tag - toutes doivent être
# redirigées du doublon vers le canonique avant suppression, sinon tout contenu qui
# ne portait QUE la variante supprimée perdrait purement et simplement ce thème.
M2M_RELATIONS = [
    (Lesson, "themes"),
    (Lesson, "mots_cles_recherche"),
    (Exercise, "themes"),
    (Exercise, "mots_cles_recherche"),
    (Question, "themes"),
    (Cours, "tags"),
    (FicheGeneree, "themes"),
    (Blueprint, "competences"),
    (QuestionInedite, "themes"),
]

# FK simples vers Tag, sans contrainte d'unicité impliquant ce champ - une simple
# réaffectation en masse suffit, aucun conflit possible. CompetenceItem.theme est
# PROTECT (empêche `doublon.delete()` tant qu'il reste référencé - découvert en
# pratique, pas en lisant le modèle) ; QuizSession.theme est SET_NULL (la suppression
# seule ne casserait rien mais effacerait silencieusement quel thème une session
# passée ciblait - autant le préserver comme pour toute autre relation).
FK_RELATIONS = [
    (CompetenceItem, "theme"),
    (QuizSession, "theme"),
]


class Command(BaseCommand):
    help = (
        "Fusionne les Tag qui ne diffèrent que par la casse (ex: \"Activité\" / "
        "\"activité\") - doublon mécanique introduit par des générations successives "
        "de correction-experte, jamais une distinction voulue. Un seul Tag canonique "
        "conservé par groupe : celui déjà rattaché à un programme.Savoir s'il y en a "
        "exactement un (jamais choisi au hasard si les deux variantes pointent vers "
        "des savoirs différents - groupe alors laissé de côté pour revue manuelle), "
        "sinon celui qui porte le plus de liens existants. Toutes les relations M2M "
        "vers Tag (Lesson/Exercise/Question.themes, *.mots_cles_recherche, Cours.tags, "
        "FicheGeneree.themes, inedit.Blueprint.competences, "
        "inedit.QuestionInedite.themes) sont redirigées vers le canonique avant "
        "suppression du doublon - jamais un simple delete, qui perdrait le thème sur "
        "tout contenu qui ne portait QUE la variante supprimée. Idem pour les FK "
        "simples quiz.CompetenceItem.theme (PROTECT - bloquerait la suppression du "
        "doublon sinon) et quiz.QuizSession.theme (SET_NULL - se contenterait "
        "d'effacer silencieusement le thème d'une session passée). "
        "quiz.RevisionSchedule.theme (FK CASCADE, unique par user+cursus+theme) est "
        "traité à part : en cas de conflit (l'élève a déjà une échéance sur le "
        "canonique), la ligne la plus urgente (due_at le plus proche) est gardée, "
        "l'autre supprimée plutôt que de violer la contrainte d'unicité. "
        "Toujours par --dry-run d'abord."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="N'écrit rien en base, affiche seulement le rapport.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        groups = defaultdict(list)
        for tag in Tag.objects.all():
            groups[tag.name.lower()].append(tag)
        dupe_groups = [tags for tags in groups.values() if len(tags) > 1]

        merged_groups = 0
        deleted_tags = 0
        skipped_conflict = 0
        revision_conflicts_resolved = 0

        for tags in dupe_groups:
            savoir_ids = {t.savoir_officiel_id for t in tags if t.savoir_officiel_id is not None}
            if len(savoir_ids) > 1:
                self.stdout.write(self.style.WARNING(
                    f"IGNORÉ (savoirs officiels différents) : {[t.name for t in tags]}",
                ))
                skipped_conflict += 1
                continue

            def nb_liens(t):
                return (
                    t.lessons_as_theme.count() + t.lessons_as_keyword.count()
                    + t.exercises_as_theme.count() + t.exercises_as_keyword.count()
                    + t.questions_as_theme.count() + t.cours.count()
                )

            # Canonique : priorité au savoir officiel déjà rattaché (ne jamais le
            # perdre), puis au plus de liens (minimise le travail de réassignation),
            # puis au pk le plus petit (le plus ancien) à égalité.
            tags_sorted = sorted(
                tags, key=lambda t: (t.savoir_officiel_id is not None, nb_liens(t), -t.pk), reverse=True,
            )
            canonical = tags_sorted[0]
            doublons = tags_sorted[1:]

            self.stdout.write(
                f"{'[dry-run] ' if dry_run else ''}Fusion -> {canonical.name!r} (garde) "
                f"<- {[t.name for t in doublons]}",
            )

            if dry_run:
                merged_groups += 1
                deleted_tags += len(doublons)
                continue

            with transaction.atomic():
                for doublon in doublons:
                    for model, field in M2M_RELATIONS:
                        for obj in model.objects.filter(**{field: doublon}):
                            getattr(obj, field).add(canonical)

                    for model, field in FK_RELATIONS:
                        model.objects.filter(**{field: doublon}).update(**{field: canonical})

                    for schedule in RevisionSchedule.objects.filter(theme=doublon):
                        conflit = RevisionSchedule.objects.filter(
                            user=schedule.user, cursus=schedule.cursus, theme=canonical,
                        ).first()
                        if conflit is None:
                            schedule.theme = canonical
                            schedule.save(update_fields=["theme"])
                        else:
                            revision_conflicts_resolved += 1
                            if schedule.due_at < conflit.due_at:
                                conflit.delete()
                                schedule.theme = canonical
                                schedule.save(update_fields=["theme"])
                            else:
                                schedule.delete()

                    doublon.delete()

            merged_groups += 1
            deleted_tags += len(doublons)

        self.stdout.write(self.style.SUCCESS(
            f"\n{merged_groups} groupe(s) fusionné(s), {deleted_tags} Tag(s) doublon(s) supprimé(s), "
            f"{revision_conflicts_resolved} conflit(s) de révision résolu(s)"
            + (f", {skipped_conflict} groupe(s) ignoré(s) (savoirs différents)" if skipped_conflict else "")
            + (" (dry-run, rien n'a été écrit)" if dry_run else "") + ".",
        ))
