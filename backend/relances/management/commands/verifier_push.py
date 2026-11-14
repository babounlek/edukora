from django.core.management.base import BaseCommand, CommandError

from relances.models import AbonnementPush
from relances.push import envoyer_a_l_appareil, push_configure
from users.models import User

CHARGE_TEST = {
    "title": "Test des notifications EduKora",
    "body": "Si tu lis ceci, les rappels push arrivent bien sur cet appareil.",
    "url": "/",
    "tag": "test-push",
}


class Command(BaseCommand):
    help = (
        "Vérifie les notifications push : clés VAPID présentes, appareils abonnés, et - avec --envoyer - un message "
        "de test aux appareils d'un compte. À lancer sur le serveur après avoir posé les clés (voir generer_cles_vapid) : "
        "sans elles, l'application n'affiche même pas l'interrupteur, et rien ne dit pourquoi."
    )

    def add_arguments(self, parser):
        parser.add_argument("--email", help="Le compte dont on teste les appareils (avec --envoyer).")
        parser.add_argument("--envoyer", action="store_true", help="Envoie un message de test aux appareils du compte.")

    def handle(self, *args, **options):
        from django.conf import settings

        self.stdout.write(f"Clé publique VAPID : {'présente' if settings.VAPID_PUBLIC_KEY else 'ABSENTE'}")
        self.stdout.write(f"Clé privée VAPID   : {'présente' if settings.VAPID_PRIVATE_KEY else 'ABSENTE'}")
        self.stdout.write(f"Adresse de contact : {'présente' if settings.VAPID_CLAIM_EMAIL else 'ABSENTE'}")
        if not push_configure():
            raise CommandError(
                "Push non configuré : aucun rappel ne part et l'interrupteur n'est pas proposé. "
                "Lance generer_cles_vapid, pose les trois lignes dans le .env du serveur, puis redéploie.",
            )
        total = AbonnementPush.objects.count()
        comptes = AbonnementPush.objects.values("user_id").distinct().count()
        self.stdout.write(self.style.SUCCESS(f"Push configuré. {total} appareil(s) abonné(s), {comptes} compte(s)."))

        if not options["envoyer"]:
            return
        if not options["email"]:
            raise CommandError("--envoyer demande --email <compte>.")
        user = User.objects.filter(email__iexact=options["email"]).first()
        if user is None:
            raise CommandError("Aucun compte avec cette adresse.")
        appareils = list(user.abonnements_push.all())
        if not appareils:
            raise CommandError("Ce compte n'a aucun appareil abonné : active les notifications depuis « Mon compte ».")
        partis = 0
        for appareil in appareils:
            ok = envoyer_a_l_appareil(appareil, CHARGE_TEST)
            partis += ok
            hote = appareil.endpoint.split("/")[2] if "//" in appareil.endpoint else "?"
            self.stdout.write(f"  appareil {appareil.pk} ({hote}) : {'envoyé' if ok else 'ÉCHEC (voir les journaux relances)'}")
        if partis == 0:
            raise CommandError("Aucun message n'est parti.")
        self.stdout.write(self.style.SUCCESS(f"{partis}/{len(appareils)} message(s) de test envoyé(s)."))
