"""
Couvre le risque principal du module : argent réel encaissé via CamPay, et paiement
qui ne doit jamais activer/prolonger un abonnement ni récompenser un parrainage plus
d'une fois pour une même transaction. CamPay lui-même n'est jamais appelé en vrai
(voir campay_client, mocké partout ici) - seule la logique applicative est testée.
"""

import threading
from datetime import timedelta
from unittest import skipUnless
from unittest.mock import patch

from django.db import IntegrityError, connection, connections
from django.db import transaction as db_transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, ExamSession
from subscriptions.models import (
    PARRAINAGE_CREDIT_MONTANT,
    DureeMode,
    InscriptionInedite,
    ParrainageRecompense,
    Plan,
    ProductType,
    Subscription,
    solde_credit_parrainage,
)
from users.models import User

from .campay_client import CampayError
from .models import (
    ManualPayment,
    ManualPaymentAlreadyReviewed,
    ManualPaymentRejectReason,
    ManualPaymentStatus,
    MobileMoneyAccount,
    MobileMoneyOperator,
    StatutTransaction,
    Transaction,
)


def _make_cursus():
    # Le référentiel (Country/Series/Cursus) est seedé par les migrations catalog
    # (voir 0003_seed_referentiel.py / 0015_country.py) - déjà présent dans la base
    # de test après migration, donc on le récupère plutôt que d'en recréer un en
    # double (Country.code est unique, une deuxième "CM" ferait échouer le test).
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


def _octroyer_credit(parrain, montant, cursus):
    """
    Crée directement un crédit parrainage disponible pour `parrain`, sans passer par
    le parcours complet filleul -> première conversion (déjà couvert par
    ParrainageIdempotenceTests) - utile pour tester sa consommation côté paiement de
    manière isolée. `transaction`/`filleul` bidons uniquement pour satisfaire les FK
    obligatoires de ParrainageRecompense.
    """
    filleul_bidon = User.objects.create_user(phone_number=f"679{User.objects.count():06d}", password="x")
    plan_bidon = Plan.objects.create(name="Bidon", cursus=cursus, price=1, duration_days=1)
    transaction_bidon = Transaction.objects.create(
        user=filleul_bidon, plan=plan_bidon, amount=1,
        phone_number=filleul_bidon.phone_number, status=StatutTransaction.SUCCESSFUL,
    )
    return ParrainageRecompense.objects.create(
        parrain=parrain, filleul=filleul_bidon, transaction=transaction_bidon, cursus=cursus,
        montant_offert=montant, montant_restant=montant,
        expires_at=timezone.now() + timezone.timedelta(days=365),
    )


class TransactionSyncStatusTests(TestCase):
    """sync_status() est le seul chemin qui active un abonnement - c'est lui qui doit être idempotent."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000001", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-1",
        )

    @patch("payments.campay_client.get_transaction_status")
    def test_successful_status_activates_subscription(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, StatutTransaction.SUCCESSFUL)
        self.assertIsNotNone(self.transaction.subscription_id)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertTrue(subscription.is_active)

    @patch("payments.campay_client.get_transaction_status")
    def test_sync_status_is_idempotent_on_repeated_call(self, mock_status):
        """Rejouer sync_status() sur la même instance (ex. polling qui chevauche un
        webhook) ne doit ni re-prolonger l'abonnement ni rappeler CamPay une deuxième fois."""
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}

        self.transaction.sync_status()
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        expires_after_first = subscription.expires_at

        self.transaction.sync_status()

        subscription.refresh_from_db()
        self.assertEqual(subscription.expires_at, expires_after_first)
        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 1)
        mock_status.assert_called_once()

    @patch("payments.campay_client.get_transaction_status")
    def test_sync_status_idempotent_across_separate_instances(self, mock_status):
        """Même garantie en relisant la transaction depuis la base plutôt qu'en
        réutilisant l'objet Python déjà en mémoire - un webhook et un polling client
        n'opèrent jamais sur la même instance."""
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        self.transaction.sync_status()

        reloaded = Transaction.objects.get(pk=self.transaction.pk)
        reloaded.sync_status()

        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 1)
        self.assertEqual(mock_status.call_count, 1)

    @patch("payments.campay_client.get_transaction_status")
    def test_failed_status_does_not_activate_subscription(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.FAILED, "reference": "ref-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, StatutTransaction.FAILED)
        self.assertIsNone(self.transaction.subscription_id)
        self.assertFalse(Subscription.objects.filter(user=self.user, cursus=self.cursus).exists())

    @patch("payments.campay_client.get_transaction_status")
    def test_renewal_extends_existing_subscription_instead_of_duplicating(self, mock_status):
        """Un renouvellement (transaction distincte, même user/cursus) doit prolonger
        l'abonnement existant, jamais en créer un second - la contrainte unique le
        garantirait de toute façon en base, mais la logique applicative doit aussi
        prendre ce chemin (extend), pas tenter un create qui échouerait."""
        existing = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=5),
        )
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}

        self.transaction.sync_status()

        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 1)
        existing.refresh_from_db()
        self.assertGreater(existing.expires_at, timezone.now() + timezone.timedelta(days=90))


class TransactionSyncStatusAddonInediteTests(TestCase):
    """_activer_acces route un Plan ADDON_INEDIT vers InscriptionInedite, jamais
    Subscription - même garanties d'idempotence que TransactionSyncStatusTests, sur
    l'autre branche du branchement (voir payments.models._activer_acces)."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000050", password="x")
        self.plan = Plan.objects.create(
            name="Épreuves Inédites", cursus=self.cursus, price=1000, duration_days=30,
            product_type=ProductType.ADDON_INEDIT,
        )
        self.transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-addon-1",
        )

    @patch("payments.campay_client.get_transaction_status")
    def test_successful_status_activates_inscription_inedite_not_subscription(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-addon-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, StatutTransaction.SUCCESSFUL)
        self.assertIsNotNone(self.transaction.inscription_inedite_id)
        self.assertIsNone(self.transaction.subscription_id)
        inscription = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        self.assertTrue(inscription.is_active)
        self.assertFalse(Subscription.objects.filter(user=self.user, cursus=self.cursus).exists())

    @patch("payments.campay_client.get_transaction_status")
    def test_sync_status_is_idempotent_on_repeated_call(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-addon-1"}

        self.transaction.sync_status()
        inscription = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        expires_after_first = inscription.expires_at

        self.transaction.sync_status()

        inscription.refresh_from_db()
        self.assertEqual(inscription.expires_at, expires_after_first)
        mock_status.assert_called_once()


class TransactionSyncStatusPlanInclutInediteTests(TestCase):
    """Un Plan ABONNEMENT avec inclut_inedit=True (ex. la formule Max) doit activer
    Subscription ET InscriptionInedite pour le même paiement - voir
    payments.models._activer_acces. Un Plan ABONNEMENT ordinaire (inclut_inedit=False,
    déjà couvert par TransactionSyncStatusTests) ne doit toucher qu'à Subscription."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000060", password="x")
        self.plan = Plan.objects.create(
            name="BAC Série C - Max (1 an)", cursus=self.cursus, price=15000, duration_days=365,
            inclut_inedit=True,
        )
        self.transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-max-1",
        )

    @patch("payments.campay_client.get_transaction_status")
    def test_successful_status_activates_both_subscription_and_inscription_inedite(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-max-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertIsNotNone(self.transaction.subscription_id)
        self.assertIsNotNone(self.transaction.inscription_inedite_id)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        inscription = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        self.assertTrue(subscription.is_active)
        self.assertTrue(inscription.is_active)

    @patch("payments.campay_client.get_transaction_status")
    def test_sync_status_is_idempotent_on_repeated_call(self, mock_status):
        """Même garantie que les deux autres branches : un deuxième appel ne doit ni
        re-prolonger les deux accès, ni rappeler CamPay."""
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-max-1"}

        self.transaction.sync_status()
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        inscription = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        sub_expires_after_first = subscription.expires_at
        insc_expires_after_first = inscription.expires_at

        self.transaction.sync_status()

        subscription.refresh_from_db()
        inscription.refresh_from_db()
        self.assertEqual(subscription.expires_at, sub_expires_after_first)
        self.assertEqual(inscription.expires_at, insc_expires_after_first)
        mock_status.assert_called_once()


class TransactionSyncStatusPlanWithoutInclutInediteTests(TestCase):
    """Contrôle négatif : un Plan ABONNEMENT ordinaire (inclut_inedit=False, la valeur
    par défaut) n'active jamais InscriptionInedite - la formule Max n'est pas censée
    devenir le comportement par défaut de tout Plan ABONNEMENT."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000061", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-no-inedit-1",
        )

    @patch("payments.campay_client.get_transaction_status")
    def test_successful_status_does_not_activate_inscription_inedite(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-no-inedit-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertIsNotNone(self.transaction.subscription_id)
        self.assertIsNone(self.transaction.inscription_inedite_id)
        self.assertFalse(InscriptionInedite.objects.filter(user=self.user, cursus=self.cursus).exists())


class ParrainageIdempotenceTests(TestCase):
    """recompenser_parrainage() : seule la toute première conversion du filleul
    récompense le parrain, jamais un réabonnement - et jamais deux fois pour la même transaction."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.parrain = User.objects.create_user(phone_number="677000002", password="x")
        self.filleul = User.objects.create_user(phone_number="677000003", password="x", referred_by=self.parrain)
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)

    @patch("payments.campay_client.get_transaction_status")
    def test_first_conversion_rewards_parrain(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-1",
        )

        transaction.sync_status()

        self.assertTrue(ParrainageRecompense.objects.filter(transaction=transaction).exists())
        # Crédit FCFA dépensable sur n'importe quel achat futur - plus une extension
        # d'abonnement sur le cursus du filleul (voir subscriptions.models, décision
        # du 2026-08-22).
        self.assertEqual(solde_credit_parrainage(self.parrain), PARRAINAGE_CREDIT_MONTANT)
        self.assertFalse(Subscription.objects.filter(user=self.parrain, cursus=self.cursus).exists())

    @patch("payments.campay_client.get_transaction_status")
    def test_renewal_does_not_reward_parrain_again(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}

        first = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-1",
        )
        first.sync_status()

        second = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-2",
        )
        second.sync_status()

        self.assertEqual(ParrainageRecompense.objects.filter(parrain=self.parrain).count(), 1)
        self.assertEqual(solde_credit_parrainage(self.parrain), PARRAINAGE_CREDIT_MONTANT)

    @patch("payments.campay_client.get_transaction_status")
    def test_replaying_sync_status_does_not_reward_parrain_twice(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-1",
        )

        transaction.sync_status()
        Transaction.objects.get(pk=transaction.pk).sync_status()

        self.assertEqual(ParrainageRecompense.objects.filter(transaction=transaction).count(), 1)

    @patch("payments.campay_client.get_transaction_status")
    def test_no_referrer_no_reward_attempt(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        solo_user = User.objects.create_user(phone_number="677000004", password="x")
        transaction = Transaction.objects.create(
            user=solo_user, plan=self.plan, amount=self.plan.price,
            phone_number=solo_user.phone_number, provider_reference="ref-solo",
        )

        transaction.sync_status()

        self.assertFalse(ParrainageRecompense.objects.filter(transaction=transaction).exists())


class PaymentFlowAPITests(TestCase):
    """Parcours complet côté API : initiation -> vérification de statut -> abonnement actif."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000005", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_creates_pending_transaction(self, mock_init):
        mock_init.return_value = {"reference": "campay-ref-123", "status": "PENDING"}

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 200)
        transaction = Transaction.objects.get(pk=response.data["transaction_id"])
        self.assertEqual(transaction.status, StatutTransaction.PENDING)
        self.assertEqual(transaction.provider_reference, "campay-ref-123")
        self.assertEqual(transaction.user, self.user)

    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_charges_the_effective_price_for_a_jusqua_examen_plan(self, mock_init):
        # Le montant encaissé doit suivre Plan.effective_price(), jamais le plafond
        # `price` brut - sinon un candidat proche de son examen se voit facturer le
        # tarif plein plutôt que le prix réellement affiché (voir mission tarification
        # 2026-08-19).
        mock_init.return_value = {"reference": "campay-ref-jusqua", "status": "PENDING"}
        ExamSession.objects.create(
            country=self.cursus.country, examen=self.cursus.examen, annee=timezone.now().year,
            date_debut=(timezone.now() + timedelta(days=5)).date(),
        )
        plan = Plan.objects.create(
            name="Jusqu'à l'Examen", cursus=self.cursus, price=12000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        response = self.client.post(
            "/payments/initiate/", {"plan_id": plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 200)
        transaction = Transaction.objects.get(pk=response.data["transaction_id"])
        self.assertEqual(transaction.amount, 4000)

    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_applies_available_credit_as_a_discount(self, mock_init):
        mock_init.return_value = {"reference": "campay-ref-credit", "status": "PENDING"}
        _octroyer_credit(self.user, 500, self.cursus)

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 200)
        transaction = Transaction.objects.get(pk=response.data["transaction_id"])
        self.assertEqual(transaction.credit_applique, 500)
        self.assertEqual(transaction.amount, self.plan.price - 500)
        # CamPay ne doit jamais voir le prix plein : c'est bien le montant net qui
        # part en collecte, pas seulement celui stocké côté Transaction.
        self.assertEqual(mock_init.call_args.kwargs["amount"], self.plan.price - 500)

    @patch("payments.campay_client.get_transaction_status")
    def test_credit_is_consumed_only_on_confirmation_not_on_initiation(self, mock_status):
        # Le solde affiché à l'initiation n'est qu'une cotation - voir
        # consommer_credit_parrainage. Le solde réel ne doit bouger qu'à la
        # confirmation (sync_status), jamais avant, sinon un paiement qui échoue
        # aurait quand même consommé le crédit du parrain.
        _octroyer_credit(self.user, 500, self.cursus)
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price - 500,
            credit_applique=500, phone_number=self.user.phone_number, provider_reference="ref-credit-confirm",
        )
        self.assertEqual(solde_credit_parrainage(self.user), 500)

        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-credit-confirm"}
        transaction.sync_status()

        self.assertEqual(solde_credit_parrainage(self.user), 0)

    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_skips_campay_when_credit_fully_covers_the_price(self, mock_init):
        _octroyer_credit(self.user, self.plan.price, self.cursus)

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 200)
        mock_init.assert_not_called()
        transaction = Transaction.objects.get(pk=response.data["transaction_id"])
        self.assertEqual(transaction.status, StatutTransaction.SUCCESSFUL)
        self.assertEqual(transaction.amount, 0)
        self.assertEqual(transaction.credit_applique, self.plan.price)
        self.assertTrue(Subscription.objects.get(user=self.user, cursus=self.cursus).is_active)
        self.assertEqual(solde_credit_parrainage(self.user), 0)

    def test_initiate_payment_requires_plan_id_and_phone(self):
        response = self.client.post("/payments/initiate/", {})
        self.assertEqual(response.status_code, 400)

    def test_initiate_payment_rejects_inactive_plan(self):
        self.plan.is_active = False
        self.plan.save()

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 404)

    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_marks_transaction_failed_on_campay_error(self, mock_init):
        mock_init.side_effect = CampayError("CamPay injoignable")

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 502)
        transaction = Transaction.objects.get(user=self.user)
        self.assertEqual(transaction.status, StatutTransaction.FAILED)

    @patch("payments.views.sentry_sdk.capture_exception")
    @patch("payments.campay_client.init_collect")
    def test_initiate_payment_reports_campay_error_to_sentry_tagged_as_critical_path(self, mock_init, mock_capture):
        # Voir l'audit UX, reco 5.1 : une CampayError est déjà gérée gracieusement
        # (réponse 502 propre) donc jamais remontée automatiquement par l'intégration
        # Django de Sentry - _report_campay_error doit la capturer explicitement.
        mock_init.side_effect = CampayError("CamPay injoignable")

        self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        mock_capture.assert_called_once()
        self.assertIsInstance(mock_capture.call_args[0][0], CampayError)

    @patch("payments.campay_client.get_transaction_status")
    def test_check_status_full_happy_path(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-1",
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], StatutTransaction.SUCCESSFUL)
        self.assertTrue(response.data["subscription_active"])

    @patch("payments.campay_client.get_transaction_status")
    def test_check_status_does_not_repoll_already_successful_transaction(self, mock_status):
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-1",
            status=StatutTransaction.SUCCESSFUL,
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 200)
        mock_status.assert_not_called()

    @patch("payments.views.sentry_sdk.capture_exception")
    @patch("payments.campay_client.get_transaction_status")
    def test_check_status_reports_campay_error_to_sentry(self, mock_status, mock_capture):
        mock_status.side_effect = CampayError("CamPay injoignable")
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, provider_reference="ref-1",
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 502)
        mock_capture.assert_called_once()

    def test_check_status_rejects_other_users_transaction(self):
        other_user = User.objects.create_user(phone_number="677000006", password="x")
        transaction = Transaction.objects.create(
            user=other_user, plan=self.plan, amount=self.plan.price, phone_number=other_user.phone_number,
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 404)


@skipUnless(
    connection.vendor == "postgresql",
    "Verrou de ligne réel (select_for_update) nécessaire - sans effet sur SQLite, "
    "utilisé pour manage.py test faute de CREATEDB sur le rôle applicatif Postgres "
    "(voir settings.py) : ce test-ci resterait silencieusement non-diagnostique là-bas.",
)
class TransactionConcurrencyTests(TransactionTestCase):
    """
    Reproduit une vraie course (deux threads, deux connexions séparées, jamais la
    même instance Python) plutôt qu'un simple double appel séquentiel - c'est le
    scénario webhook + polling client qui se chevauchent. TransactionTestCase (pas
    TestCase) : il faut de vraies transactions/connexions concurrentes, incompatibles
    avec le wrapping savepoint-only de TestCase.
    """

    def setUp(self):
        self.cursus = _make_cursus()
        self.parrain = User.objects.create_user(phone_number="677100010", password="x")
        self.filleul = User.objects.create_user(
            phone_number="677100011", password="x", referred_by=self.parrain,
        )
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=30)
        self.transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-race",
        )

    def tearDown(self):
        connections.close_all()

    def test_concurrent_sync_status_does_not_double_extend_subscriptions(self):
        start_barrier = threading.Barrier(2)
        errors = []

        def worker():
            try:
                with patch("payments.campay_client.get_transaction_status") as mock_status:
                    mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-race"}
                    # Instance rechargée séparément par thread : un webhook et un
                    # polling client ne partagent jamais le même objet Python.
                    reloaded = Transaction.objects.get(pk=self.transaction.pk)
                    start_barrier.wait(timeout=5)
                    reloaded.sync_status()
            except Exception as exc:  # noqa: BLE001 - remonté explicitement plus bas
                errors.append(exc)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])

        filleul_sub = Subscription.objects.get(user=self.filleul, cursus=self.cursus)

        # 25-30j (pas ~60) : marge pour le temps d'exécution du test, mais large
        # marge de sécurité avant de pouvoir confondre avec un double crédit (qui
        # doublerait carrément cette valeur).
        filleul_days_left = (filleul_sub.expires_at - timezone.now()).days
        self.assertTrue(25 <= filleul_days_left <= 30, f"abonnement filleul prolongé en double : {filleul_days_left}j")
        self.assertEqual(ParrainageRecompense.objects.filter(transaction=self.transaction).count(), 1)
        # Même garde-fou côté crédit parrainage : un double appel concurrent ne doit
        # jamais créditer le parrain deux fois (500 FCFA, pas 1000).
        self.assertEqual(solde_credit_parrainage(self.parrain), PARRAINAGE_CREDIT_MONTANT)


class ManualPaymentDeclareAPITests(TestCase):
    """
    POST /payments/manual/declare/ : couvre le risque principal du second mode de
    paiement - le serveur ne doit jamais faire confiance au montant envoyé par le
    client (voir mission, section 8), toujours le recalculer depuis plan.price.
    """

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000030", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        MobileMoneyAccount.objects.create(
            operator=MobileMoneyOperator.ORANGE, phone_number="677000099", account_name="Edukora",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _payload(self, **overrides):
        payload = {
            "plan": self.plan.id, "operator": MobileMoneyOperator.ORANGE,
            "amount_declared": 2000, "payer_phone_number": self.user.phone_number,
            "transaction_reference": "OM123456",
        }
        payload.update(overrides)
        return payload

    def test_declare_creates_pending_manual_payment(self):
        response = self.client.post("/payments/manual/declare/", self._payload())

        self.assertEqual(response.status_code, 201)
        payment = ManualPayment.objects.get(pk=response.data["id"])
        self.assertEqual(payment.status, ManualPaymentStatus.PENDING)
        self.assertEqual(payment.user, self.user)

    def test_amount_expected_is_never_taken_from_the_client(self):
        # amount_declared (2500) dépasse le prix de l'offre (2000) - autorisé (rien
        # n'empêche un utilisateur d'arrondir/surpayer) - et amount_expected vient
        # toujours de plan.price, jamais du client : l'écart doit rester visible pour
        # l'admin, jamais aligné silencieusement sur ce que le client a déclaré.
        response = self.client.post("/payments/manual/declare/", self._payload(amount_declared=2500))

        self.assertEqual(response.status_code, 201)
        payment = ManualPayment.objects.get(pk=response.data["id"])
        self.assertEqual(payment.amount_expected, 2000)
        self.assertEqual(payment.amount_declared, 2500)

    def test_amount_expected_uses_effective_price_for_a_jusqua_examen_plan(self):
        # Même règle que côté Campay (voir PaymentFlowAPITests.
        # test_initiate_payment_charges_the_effective_price_for_a_jusqua_examen_plan) :
        # amount_expected et la validation de amount_declared doivent suivre
        # Plan.effective_price(), jamais le plafond `price` brut, sinon une déclaration
        # légitime au prix réellement affiché serait rejetée à tort.
        ExamSession.objects.create(
            country=self.cursus.country, examen=self.cursus.examen, annee=timezone.now().year,
            date_debut=(timezone.now() + timedelta(days=5)).date(),
        )
        plan = Plan.objects.create(
            name="Jusqu'à l'Examen", cursus=self.cursus, price=12000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        response = self.client.post(
            "/payments/manual/declare/", self._payload(plan=plan.id, amount_declared=4000),
        )

        self.assertEqual(response.status_code, 201)
        payment = ManualPayment.objects.get(pk=response.data["id"])
        self.assertEqual(payment.amount_expected, 4000)

    def test_rejects_amount_declared_below_plan_price(self):
        # Constaté en production : un montant déclaré inférieur au prix de l'offre ne
        # doit jamais être accepté, même pour revue admin - rejeté dès la déclaration.
        response = self.client.post("/payments/manual/declare/", self._payload(amount_declared=100))

        self.assertEqual(response.status_code, 400)
        self.assertIn("amount_declared", response.data)
        self.assertFalse(ManualPayment.objects.exists())

    def test_rejects_inactive_plan(self):
        self.plan.is_active = False
        self.plan.save()

        response = self.client.post("/payments/manual/declare/", self._payload())

        self.assertEqual(response.status_code, 400)

    def test_rejects_operator_without_active_account(self):
        response = self.client.post("/payments/manual/declare/", self._payload(operator=MobileMoneyOperator.MTN))

        self.assertEqual(response.status_code, 400)

    def test_rejects_blank_transaction_reference(self):
        response = self.client.post("/payments/manual/declare/", self._payload(transaction_reference=""))

        self.assertEqual(response.status_code, 400)

    def test_normalizes_transaction_reference(self):
        response = self.client.post("/payments/manual/declare/", self._payload(transaction_reference="  om-abc123  "))

        self.assertEqual(response.status_code, 201)
        payment = ManualPayment.objects.get(pk=response.data["id"])
        self.assertEqual(payment.transaction_reference, "OM-ABC123")

    def test_declare_sends_sms_confirmation(self):
        with patch("payments.models._notifier_utilisateur") as mock_notify:
            response = self.client.post("/payments/manual/declare/", self._payload())

        self.assertEqual(response.status_code, 201)
        mock_notify.assert_called_once()


class ManualPaymentDuplicateReferenceTests(TestCase):
    """
    Anti-réutilisation de transaction (voir mission, section 6) : une même référence
    ne peut jamais financer deux abonnements, ni être déclarée deux fois tant qu'une
    déclaration est active - mais un rejet la libère pour corriger une déclaration.
    """

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000031", password="x")
        self.other_user = User.objects.create_user(phone_number="677000032", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.other_plan = Plan.objects.create(name="Annuel", cursus=self.cursus, price=5000, duration_days=365)
        MobileMoneyAccount.objects.create(
            operator=MobileMoneyOperator.ORANGE, phone_number="677000099", account_name="Edukora",
        )

    def _declare(self, user, plan, reference):
        return ManualPayment.objects.declare(
            user=user, plan=plan, operator=MobileMoneyOperator.ORANGE, amount_declared=plan.price,
            payer_phone_number=user.phone_number, transaction_reference=reference,
        )

    def test_same_reference_twice_while_pending_is_rejected(self):
        self._declare(self.user, self.plan, "OM-DUP-1")

        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                self._declare(self.user, self.plan, "OM-DUP-1")

    def test_reference_frees_up_after_rejection(self):
        first = self._declare(self.user, self.plan, "OM-DUP-2")
        first.reject(admin_user=self.user, reason=ManualPaymentRejectReason.TRANSACTION_INTROUVABLE)

        second = self._declare(self.user, self.plan, "OM-DUP-2")  # ne doit pas lever

        self.assertEqual(second.transaction_reference, "OM-DUP-2")

    def test_approved_reference_blocked_for_another_user_and_cursus(self):
        first = self._declare(self.user, self.plan, "OM-DUP-3")
        first.approve(admin_user=self.user)

        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                self._declare(self.other_user, self.other_plan, "OM-DUP-3")


class ManualPaymentApproveRejectTests(TestCase):
    """approve()/reject() : mêmes garanties d'idempotence que Transaction.sync_status
    (voir TransactionSyncStatusTests), sur le point de convergence partagé."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000040", password="x")
        self.admin = User.objects.create_user(phone_number="677000041", password="x", is_staff=True)
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.payment = ManualPayment.objects.create(
            user=self.user, plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.user.phone_number, transaction_reference="OM-APR-1",
        )

    def test_approve_activates_subscription(self):
        self.payment.approve(admin_user=self.admin)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, ManualPaymentStatus.APPROVED)
        self.assertEqual(self.payment.reviewed_by, self.admin)
        self.assertIsNotNone(self.payment.reviewed_at)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertTrue(subscription.is_active)

    def test_approve_twice_raises_and_does_not_double_extend(self):
        self.payment.approve(admin_user=self.admin)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        expires_after_first = subscription.expires_at

        with self.assertRaises(ManualPaymentAlreadyReviewed):
            ManualPayment.objects.get(pk=self.payment.pk).approve(admin_user=self.admin)

        subscription.refresh_from_db()
        self.assertEqual(subscription.expires_at, expires_after_first)

    def test_reject_does_not_activate_subscription(self):
        self.payment.reject(admin_user=self.admin, reason=ManualPaymentRejectReason.MONTANT_INCORRECT)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, ManualPaymentStatus.REJECTED)
        self.assertIsNone(self.payment.subscription)
        self.assertFalse(Subscription.objects.filter(user=self.user, cursus=self.cursus).exists())

    def test_reject_twice_raises_already_reviewed(self):
        self.payment.reject(admin_user=self.admin, reason=ManualPaymentRejectReason.MONTANT_INCORRECT)

        with self.assertRaises(ManualPaymentAlreadyReviewed):
            ManualPayment.objects.get(pk=self.payment.pk).reject(
                admin_user=self.admin, reason=ManualPaymentRejectReason.AUTRE,
            )

    def test_approve_sends_sms(self):
        with patch("payments.models._notifier_utilisateur") as mock_notify:
            self.payment.approve(admin_user=self.admin)
        mock_notify.assert_called_once()

    def test_reject_sends_sms(self):
        with patch("payments.models._notifier_utilisateur") as mock_notify:
            self.payment.reject(admin_user=self.admin, reason=ManualPaymentRejectReason.PAIEMENT_NON_RECU)
        mock_notify.assert_called_once()


class ManualPaymentMineAPITests(TestCase):
    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000050", password="x")
        self.other_user = User.objects.create_user(phone_number="677000051", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.get("/payments/manual/mine/")
        self.assertEqual(response.status_code, 401)

    def test_returns_only_the_authenticated_user_payments(self):
        ManualPayment.objects.create(
            user=self.user, plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.user.phone_number, transaction_reference="OM-MINE-1",
        )
        ManualPayment.objects.create(
            user=self.other_user, plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.other_user.phone_number, transaction_reference="OM-MINE-2",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/payments/manual/mine/")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["transaction_reference"], "OM-MINE-1")


@skipUnless(
    connection.vendor == "postgresql",
    "Verrou de ligne réel (select_for_update) nécessaire - voir la même remarque sur TransactionConcurrencyTests.",
)
class ManualPaymentConcurrencyTests(TransactionTestCase):
    """Même scénario que TransactionConcurrencyTests, pour le double-clic admin /
    deux administrateurs validant la même ligne en même temps (voir mission, section 15)."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677100020", password="x")
        self.admin = User.objects.create_user(phone_number="677100021", password="x", is_staff=True)
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=30)
        self.payment = ManualPayment.objects.create(
            user=self.user, plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.user.phone_number, transaction_reference="OM-RACE-1",
        )

    def tearDown(self):
        connections.close_all()

    def test_concurrent_approve_does_not_double_extend_subscription(self):
        start_barrier = threading.Barrier(2)
        errors = []
        already_reviewed_count = [0]

        def worker():
            try:
                reloaded = ManualPayment.objects.get(pk=self.payment.pk)
                start_barrier.wait(timeout=5)
                try:
                    reloaded.approve(admin_user=self.admin)
                except ManualPaymentAlreadyReviewed:
                    already_reviewed_count[0] += 1
            except Exception as exc:  # noqa: BLE001 - remonté explicitement plus bas
                errors.append(exc)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(already_reviewed_count[0], 1)

        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        days_left = (subscription.expires_at - timezone.now()).days
        self.assertTrue(25 <= days_left <= 30, f"abonnement prolongé en double : {days_left}j")


class PaymentProviderAbstractionTests(TestCase):
    """Le domaine ne dépend que du port PaymentProvider : statuts normalisés, fournisseur choisi par transaction."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000091", password="x")
        cursus = _make_cursus()
        self.plan = Plan.objects.create(name="Essentiel", cursus=cursus, price=3000, duration_days=30)

    def _transaction(self, **kwargs):
        return Transaction.objects.create(
            user=self.user, plan=self.plan, amount=3000, phone_number="677000091",
            provider_reference="ref-prov", **kwargs,
        )

    @patch("payments.campay_client.get_transaction_status")
    def test_unknown_provider_status_is_treated_as_pending_and_never_activates(self, mock_status):
        mock_status.return_value = {"status": "SOMETHING_NEW"}
        transaction = self._transaction()
        transaction.sync_status()
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, StatutTransaction.PENDING)
        self.assertIsNone(transaction.subscription)

    def test_transaction_defaults_to_configured_provider(self):
        self.assertEqual(self._transaction().provider, "campay")

    def test_unknown_provider_name_raises_provider_error(self):
        from .providers import PaiementFournisseurError, get_provider
        with self.assertRaises(PaiementFournisseurError):
            get_provider("inconnu")

    def test_campay_error_is_a_provider_error(self):
        from .providers import PaiementFournisseurError
        self.assertTrue(issubclass(CampayError, PaiementFournisseurError))
