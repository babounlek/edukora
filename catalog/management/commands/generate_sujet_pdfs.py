from django.core.management.base import BaseCommand

from catalog.models import Lesson, StatutContenu
from catalog.sujet_pdf import save_sujet_pdf


class Command(BaseCommand):
    help = (
        "Génère (hors ligne) le PDF du sujet - énoncés uniquement, jamais le corrigé - "
        "pour les leçons publiées qui n'en ont pas encore. Ne tourne jamais dans le "
        "cycle d'une requête HTTP : à exécuter manuellement ou via une tâche planifiée."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--lesson", type=int, nargs="+", default=None,
            help="Ne traiter que ces leçons (un ou plusieurs id), sinon toutes les leçons éligibles.",
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Régénérer même les leçons qui ont déjà un PDF de sujet.",
        )

    def handle(self, *args, **options):
        qs = Lesson.objects.filter(statut=StatutContenu.VALIDE)
        if options["lesson"]:
            qs = qs.filter(pk__in=options["lesson"])
        if not options["force"]:
            qs = qs.filter(sujet_pdf="")

        lessons = list(qs)
        if not lessons:
            self.stdout.write(self.style.WARNING("Aucune leçon à traiter."))
            return

        succes, echecs = 0, []
        for lesson in lessons:
            try:
                save_sujet_pdf(lesson)
                succes += 1
                self.stdout.write(f"  - {lesson} : OK")
            except Exception as exc:
                echecs.append(f"{lesson} : {exc}")

        self.stdout.write(self.style.SUCCESS(f"{succes} PDF de sujet généré(s)."))
        if echecs:
            self.stdout.write(self.style.ERROR(f"{len(echecs)} échec(s) :"))
            for echec in echecs:
                self.stdout.write(self.style.ERROR(f"  - {echec}"))
