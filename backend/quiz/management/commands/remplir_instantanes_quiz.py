from django.core.management.base import BaseCommand

from quiz import instantane
from quiz.models import QuizQuestion


class Command(BaseCommand):
    help = (
        "Remplit l'instantané (QuizQuestion.snapshot) des questions de quiz créées avant son "
        "introduction, depuis le contenu vivant d'AUJOURD'HUI, et les marque snapshot_retroactif : "
        "l'historique peut alors différer de ce que l'élève a réellement vu (l'interface le "
        "signale). Idempotente : ne touche que les questions sans instantané, n'écrase jamais "
        "un instantané existant, ne modifie ni réponse, ni score, ni contenu."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Compte sans rien écrire.")
        parser.add_argument("--batch", type=int, default=500, help="Taille des lots (défaut 500).")

    def handle(self, *args, **options):
        sans_instantane = QuizQuestion.objects.filter(snapshot__isnull=True)
        total = sans_instantane.count()
        if options["dry_run"]:
            self.stdout.write(f"{total} question(s) sans instantané (dry-run : rien n'est écrit).")
            return

        remplies = orphelines = 0
        dernier_pk = 0
        while True:
            lot = list(
                sans_instantane.filter(pk__gt=dernier_pk)
                .select_related("competence_item__theme", "competence_item__subject", "question__exercise__lesson__subject")
                .prefetch_related("question__themes")
                .order_by("pk")[: options["batch"]]
            )
            if not lot:
                break
            dernier_pk = lot[-1].pk
            a_ecrire = []
            for quiz_question in lot:
                figee = instantane.figer(quiz_question)
                if figee is None:
                    # Aucune source vivante ni instantané : impossible depuis la contrainte
                    # d'origine, signalé plutôt que de planter au milieu du lot.
                    orphelines += 1
                    continue
                quiz_question.snapshot = figee
                quiz_question.snapshot_retroactif = True
                a_ecrire.append(quiz_question)
            QuizQuestion.objects.bulk_update(a_ecrire, ["snapshot", "snapshot_retroactif"])
            remplies += len(a_ecrire)

        self.stdout.write(self.style.SUCCESS(f"{remplies} instantané(s) rempli(s) sur {total}."))
        if orphelines:
            self.stdout.write(self.style.WARNING(f"{orphelines} question(s) sans source vivante : ignorées."))
