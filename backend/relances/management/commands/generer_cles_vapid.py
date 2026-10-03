import base64

from cryptography.hazmat.primitives import serialization
from django.core.management.base import BaseCommand
from py_vapid import Vapid


def _b64url(octets):
    return base64.urlsafe_b64encode(octets).rstrip(b"=").decode()


class Command(BaseCommand):
    help = (
        "Génère la paire de clés VAPID des notifications push (voir relances.push). À lancer UNE seule "
        "fois : changer les clés plus tard invalide tous les abonnements déjà enregistrés."
    )

    def handle(self, *args, **options):
        vapid = Vapid()
        vapid.generate_keys()
        publique = vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        privee = vapid.private_key.private_bytes(
            serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
        )
        self.stdout.write("Ajoute ces trois lignes au .env du serveur (jamais dans le dépôt), puis redéploie :\n")
        self.stdout.write(f"VAPID_PUBLIC_KEY={_b64url(publique)}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={_b64url(privee)}")
        self.stdout.write("VAPID_CLAIM_EMAIL=<une adresse e-mail de contact, sans « mailto: »>")
        self.stdout.write(
            "\nLa clé privée est un secret : ne la partage pas et ne la committe jamais. "
            "La clé publique, elle, est servie au navigateur.",
        )
