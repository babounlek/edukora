from django.core.management.base import BaseCommand

from whatsapp.services import envoyer_rappels_du_jour


class Command(BaseCommand):
    help = (
        "Envoie le rappel de révision WhatsApp du jour à tous les utilisateurs opt-in "
        "ayant au moins une notion due (voir whatsapp.services.utilisateurs_a_relancer). "
        "Ne tourne jamais automatiquement - à planifier une fois par jour via une tâche "
        "externe (cron/scheduler), même principe que les commandes de génération PDF "
        "(catalog.generate_sujet_pdfs, fiches.generate_fiche_pdfs) : aucune de ces "
        "commandes ne se déclenche elle-même."
    )

    def handle(self, *args, **options):
        envoyes = envoyer_rappels_du_jour()
        self.stdout.write(self.style.SUCCESS(f"{envoyes} rappel(s) WhatsApp envoyé(s)."))
