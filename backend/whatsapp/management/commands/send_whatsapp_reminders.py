from django.core.management.base import BaseCommand

from whatsapp.services import envoyer_rappels_du_jour


class Command(BaseCommand):
    help = (
        "Envoie le rappel de révision WhatsApp du jour à tous les utilisateurs opt-in "
        "ayant au moins une notion due (voir whatsapp.services.utilisateurs_a_relancer). "
        "Déjà exécutée automatiquement chaque jour en fin d'après-midi par le service "
        "`relances` (commande planifier_relances) - cette commande ne sert qu'à un envoi "
        "manuel. Idempotente : un utilisateur déjà relancé aujourd'hui n'est pas relancé."
    )

    def handle(self, *args, **options):
        envoyes = envoyer_rappels_du_jour()
        self.stdout.write(self.style.SUCCESS(f"{envoyes} rappel(s) WhatsApp envoyé(s)."))
