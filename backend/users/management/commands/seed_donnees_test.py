"""
Données de test pour un environnement déjà en ligne (recette sur la prod avant le lancement).

    python manage.py seed_donnees_test --email-base vous@gmail.com          # crée / complète
    python manage.py seed_donnees_test --email-base vous@gmail.com --purge  # liste ce qui serait supprimé
    python manage.py seed_donnees_test --purge --oui                        # supprime les comptes de test

Principes, tous pensés pour qu'un compte de test ne puisse JAMAIS coûter de l'argent ni écrire à un
vrai destinataire :

- **Marqueur strict** : un compte de test a une adresse `local+edukora-test-<rôle>@domaine` ET un
  nom commençant par « [TEST] ». La purge ne touche que les comptes qui portent les DEUX marques ;
  un vrai utilisateur ne peut pas être supprimé par erreur.
- **Adresses en « plus-addressing »** (`vous+edukora-test-eleve-abonne@gmail.com`) : elles arrivent
  toutes dans VOTRE boîte, ce qui permet de recevoir le code de connexion par e-mail (le site n'a pas
  de mot de passe élève : téléphone-OTP, code e-mail, Google). Aucun numéro de téléphone n'est posé,
  donc aucun SMS LMT ni WhatsApp ne peut partir vers quelqu'un.
- **Aucun appel CamPay, aucun SMS** : l'accès est activé par le point de passage unique des paiements
  (`payments.models._activer_acces`, le même que la validation d'un paiement manuel), le paiement en
  attente est créé en base directement (jamais via `ManualPayment.objects.declare`, qui envoie un SMS).
- **Relances muettes** : `rappels_actifs=False` et `email_verified=False` — les relances (rappel
  quotidien, paiement non abouti, bilan parent) exigent un e-mail confirmé, elles ignorent ces comptes.
- **Idempotent** : relancer ne recrée rien et ne prolonge aucun abonnement.
- **Garde d'environnement** : refuse de tourner hors DEBUG sans `ALLOW_TEST_DATA=1`, à passer à la
  commande (`docker compose exec -e ALLOW_TEST_DATA=1 backend ...`) et non à écrire dans le .env.
"""
import os
import re
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Cursus
from payments.models import (
    ManualPayment,
    ManualPaymentStatus,
    MobileMoneyOperator,
    Transaction,
    _activer_acces,
)
from subscriptions.models import DureeMode, Plan, ProductType, Subscription
from users.models import AuthIdentity, AuthProvider, Profil, User

MARQUE_EMAIL = "+edukora-test-"
MARQUE_NOM = "[TEST] "
RE_EMAIL_TEST = re.compile(r"^[^@+]+\+edukora-test-[a-z0-9-]+@[^@]+$")

# (rôle, nom affiché, description pour la sortie)
COMPTES = [
    ("eleve-abonne", "Élève abonné", "accès Jusqu'à l'examen actif"),
    ("eleve-libre", "Élève sans abonnement", "cursus déclaré, aucun achat : voit les pages de vente"),
    ("eleve-expire", "Élève abonnement expiré", "abonnement échu depuis 3 jours : voit la relance de réabonnement"),
    ("parent-famille", "Parent de famille", "2 profils (un abonné, un non) : compte famille et sélecteur de profils"),
    ("paiement-attente", "Paiement en attente", "1 paiement manuel en attente : file de validation de l'admin"),
]


class Command(BaseCommand):
    help = (
        "Crée (ou complète) un jeu de comptes de test marqués et neutralisés, ou les supprime "
        "(--purge). Voir l'en-tête du module pour les garanties."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email-base",
            help="Votre adresse réelle (ex. vous@gmail.com) : les comptes de test en dérivent des "
                 "alias `vous+edukora-test-<rôle>@gmail.com` qui aboutissent tous dans votre boîte.",
        )
        parser.add_argument(
            "--cursus-id", type=int,
            help="Cursus sur lequel porter les abonnements (défaut : le premier qui a un Plan "
                 "Jusqu'à l'examen actif).",
        )
        parser.add_argument(
            "--purge", action="store_true",
            help="Supprime les comptes de test (sans --oui : liste seulement, ne supprime rien).",
        )
        parser.add_argument("--oui", action="store_true", help="Confirme la suppression demandée par --purge.")

    def handle(self, *args, **options):
        if not (settings.DEBUG or os.environ.get("ALLOW_TEST_DATA") == "1"):
            raise CommandError(
                "Refusé : ni DEBUG ni ALLOW_TEST_DATA=1. Pour une recette sur la prod, passez le "
                "drapeau à la commande : docker compose exec -e ALLOW_TEST_DATA=1 backend python "
                "manage.py seed_donnees_test ... (jamais dans le .env : rien ne doit rester activé)."
            )
        if options["purge"]:
            return self._purger(confirme=options["oui"])
        if not options["email_base"]:
            raise CommandError("--email-base est obligatoire (votre adresse réelle).")
        self._creer(options["email_base"], options["cursus_id"])

    # ------------------------------------------------------------------ création

    @staticmethod
    def _alias(email_base, role):
        local, _, domaine = email_base.strip().lower().partition("@")
        if not local or not domaine or "+" in local:
            raise CommandError("--email-base doit être une adresse simple, sans « + » (ex. vous@gmail.com).")
        return f"{local}{MARQUE_EMAIL}{role}@{domaine}"

    @staticmethod
    def _plan(cursus_id):
        plans = Plan.objects.filter(
            is_active=True, product_type=ProductType.ABONNEMENT, duration_mode=DureeMode.JUSQUA_EXAMEN,
        ).select_related("cursus")
        if cursus_id:
            plans = plans.filter(cursus_id=cursus_id)
            if not Cursus.objects.filter(pk=cursus_id).exists():
                raise CommandError(f"Cursus #{cursus_id} introuvable.")
        plan = plans.order_by("cursus_id", "price").first()
        if plan is None:
            raise CommandError(
                "Aucun Plan « Jusqu'à l'examen » actif trouvé"
                + (f" pour le cursus #{cursus_id}." if cursus_id else ".")
                + " Le catalogue (migrations de seed) est-il en place ?"
            )
        return plan

    def _utilisateur(self, email_base, role, nom):
        email = self._alias(email_base, role)
        user = User.objects.filter(email=email).first()
        cree = user is None
        if cree:
            user = User.objects.create_user(
                phone_number=None, email=email, full_name=f"{MARQUE_NOM}{nom}",
                is_active=True, rappels_actifs=False, email_verified=False,
            )
        # create_user ne pose pas l'identité `email` : sans elle, la connexion par code e-mail
        # (users.email_service.verify_email_code) répond « adresse déjà utilisée » (409) et le
        # compte de test est inutilisable. email_verified reste False : les relances l'ignorent.
        AuthIdentity.objects.get_or_create(
            user=user, provider=AuthProvider.EMAIL,
            defaults={"provider_uid": email, "email": email},
        )
        return user, cree

    @staticmethod
    def _activer_si_absent(plan, user, profil):
        if Subscription.objects.filter(user=user, cursus=plan.cursus, profil=profil).exists():
            return False
        _activer_acces(plan, user, profil=profil)
        return True

    @transaction.atomic
    def _creer(self, email_base, cursus_id):
        plan = self._plan(cursus_id)
        cursus = plan.cursus
        self.stdout.write(f"Cursus de test : {cursus} (plan « {plan.name} »)")

        for role, nom, description in COMPTES:
            user, cree = self._utilisateur(email_base, role, nom)
            profil = user.profils.first()
            if profil.cursus_prepare_id is None:
                profil.cursus_prepare = cursus
                profil.prenom = profil.prenom or "Test"
                profil.save(update_fields=["cursus_prepare", "prenom"])
            if user.cursus_prepare_id is None:
                user.cursus_prepare = cursus
                user.save(update_fields=["cursus_prepare"])

            if role == "eleve-abonne":
                self._activer_si_absent(plan, user, profil)
            elif role == "eleve-expire":
                if self._activer_si_absent(plan, user, profil):
                    Subscription.objects.filter(user=user, profil=profil).update(
                        expires_at=timezone.now() - timedelta(days=3),
                    )
            elif role == "parent-famille":
                self._activer_si_absent(plan, user, profil)
                if user.profils.count() < 2:
                    Profil.objects.create(compte=user, prenom="Cadet", cursus_prepare=cursus, ordre=1)
            elif role == "paiement-attente":
                if not ManualPayment.objects.filter(user=user).exists():
                    # create() et pas declare() : declare() envoie un SMS au titulaire.
                    ManualPayment.objects.create(
                        user=user, profil=profil, plan=plan, operator=MobileMoneyOperator.MTN,
                        amount_expected=plan.effective_price(user=user, profil=profil),
                        amount_declared=plan.effective_price(user=user, profil=profil),
                        payer_phone_number="600000000",
                        transaction_reference=f"TEST-{user.pk:06d}",
                        status=ManualPaymentStatus.PENDING,
                    )
            self.stdout.write(f"  {'+' if cree else '='} {user.email}  — {description}")

        self.stdout.write(self.style.SUCCESS(
            "\nTerminé. Connexion : page de connexion > « E-mail », saisir l'adresse ci-dessus, le code "
            "arrive dans votre boîte. Ne VALIDEZ PAS le paiement en attente (l'admin enverrait un SMS à "
            "un numéro vide) : rejetez-le, ou laissez-le en attente.\n"
            "Compte administrateur : non créé ici, voir `manage.py createsuperuser`."
        ))

    # ------------------------------------------------------------------ purge

    @staticmethod
    def _comptes_test():
        ids = [
            u.pk for u in User.objects.filter(email__contains=MARQUE_EMAIL, full_name__startswith=MARQUE_NOM)
            if RE_EMAIL_TEST.match(u.email or "")
        ]
        return User.objects.filter(pk__in=ids)

    def _purger(self, confirme):
        comptes = self._comptes_test()
        total = comptes.count()
        if total == 0:
            self.stdout.write("Aucun compte de test.")
            return
        for user in comptes:
            self.stdout.write(f"  - {user.email}  ({user.full_name})")
        if not confirme:
            self.stdout.write(self.style.WARNING(
                f"{total} compte(s) seraient supprimés. Relancez avec --oui pour confirmer."
            ))
            return
        with transaction.atomic():
            # PROTECT sur user : les paiements d'abord. Abonnements, profils, identités,
            # séances, quiz... partent en cascade ; les événements d'analytics restent,
            # anonymisés (SET_NULL).
            ManualPayment.objects.filter(user__in=comptes).delete()
            Transaction.objects.filter(user__in=comptes).delete()
            comptes.delete()
        self.stdout.write(self.style.SUCCESS(f"{total} compte(s) de test supprimé(s)."))
