"""
Couvre le risque principal du module : argent réel encaissé via CamPay, et paiement
qui ne doit jamais activer/prolonger un abonnement ni récompenser un parrainage plus
d'une fois pour une même transaction. CamPay lui-même n'est jamais appelé en vrai
(voir campay_client, mocké partout ici) - seule la logique applicative est testée.
"""

import threading
from unittest import skipUnless
from unittest.mock import patch

from django.db import connection, connections
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen
from subscriptions.models import ParrainageRecompense, Plan, Subscription
from users.models import User

from .campay_client import CampayError
from .models import StatutTransaction, Transaction


def _make_cursus():
    # Le référentiel (Country/Series/Cursus) est seedé par les migrations catalog
    # (voir 0003_seed_referentiel.py / 0015_country.py) - déjà présent dans la base
    # de test après migration, donc on le récupère plutôt que d'en recréer un en
    # double (Country.code est unique, une deuxième "CM" ferait échouer le test).
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


class TransactionSyncStatusTests(TestCase):
    """sync_status() est le seul chemin qui active un abonnement - c'est lui qui doit être idempotent."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000001", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, campay_reference="ref-1",
        )

    @patch("payments.models.campay_client.get_transaction_status")
    def test_successful_status_activates_subscription(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, StatutTransaction.SUCCESSFUL)
        self.assertIsNotNone(self.transaction.subscription_id)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertTrue(subscription.is_active)

    @patch("payments.models.campay_client.get_transaction_status")
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

    @patch("payments.models.campay_client.get_transaction_status")
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

    @patch("payments.models.campay_client.get_transaction_status")
    def test_failed_status_does_not_activate_subscription(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.FAILED, "reference": "ref-1"}

        self.transaction.sync_status()

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, StatutTransaction.FAILED)
        self.assertIsNone(self.transaction.subscription_id)
        self.assertFalse(Subscription.objects.filter(user=self.user, cursus=self.cursus).exists())

    @patch("payments.models.campay_client.get_transaction_status")
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


class ParrainageIdempotenceTests(TestCase):
    """recompenser_parrainage() : seule la toute première conversion du filleul
    récompense le parrain, jamais un réabonnement - et jamais deux fois pour la même transaction."""

    def setUp(self):
        self.cursus = _make_cursus()
        self.parrain = User.objects.create_user(phone_number="677000002", password="x")
        self.filleul = User.objects.create_user(phone_number="677000003", password="x", referred_by=self.parrain)
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)

    @patch("payments.models.campay_client.get_transaction_status")
    def test_first_conversion_rewards_parrain(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, campay_reference="ref-1",
        )

        transaction.sync_status()

        self.assertTrue(ParrainageRecompense.objects.filter(transaction=transaction).exists())
        self.assertTrue(Subscription.objects.filter(user=self.parrain, cursus=self.cursus).exists())

    @patch("payments.models.campay_client.get_transaction_status")
    def test_renewal_does_not_reward_parrain_again(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}

        first = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, campay_reference="ref-1",
        )
        first.sync_status()
        parrain_subscription = Subscription.objects.get(user=self.parrain, cursus=self.cursus)
        expires_after_first_reward = parrain_subscription.expires_at

        second = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, campay_reference="ref-2",
        )
        second.sync_status()

        self.assertEqual(ParrainageRecompense.objects.filter(parrain=self.parrain).count(), 1)
        parrain_subscription.refresh_from_db()
        self.assertEqual(parrain_subscription.expires_at, expires_after_first_reward)

    @patch("payments.models.campay_client.get_transaction_status")
    def test_replaying_sync_status_does_not_reward_parrain_twice(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, campay_reference="ref-1",
        )

        transaction.sync_status()
        Transaction.objects.get(pk=transaction.pk).sync_status()

        self.assertEqual(ParrainageRecompense.objects.filter(transaction=transaction).count(), 1)

    @patch("payments.models.campay_client.get_transaction_status")
    def test_no_referrer_no_reward_attempt(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL}
        solo_user = User.objects.create_user(phone_number="677000004", password="x")
        transaction = Transaction.objects.create(
            user=solo_user, plan=self.plan, amount=self.plan.price,
            phone_number=solo_user.phone_number, campay_reference="ref-solo",
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

    @patch("payments.models.campay_client.init_collect")
    def test_initiate_payment_creates_pending_transaction(self, mock_init):
        mock_init.return_value = {"reference": "campay-ref-123", "status": "PENDING"}

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 200)
        transaction = Transaction.objects.get(pk=response.data["transaction_id"])
        self.assertEqual(transaction.status, StatutTransaction.PENDING)
        self.assertEqual(transaction.campay_reference, "campay-ref-123")
        self.assertEqual(transaction.user, self.user)

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

    @patch("payments.models.campay_client.init_collect")
    def test_initiate_payment_marks_transaction_failed_on_campay_error(self, mock_init):
        mock_init.side_effect = CampayError("CamPay injoignable")

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number},
        )

        self.assertEqual(response.status_code, 502)
        transaction = Transaction.objects.get(user=self.user)
        self.assertEqual(transaction.status, StatutTransaction.FAILED)

    @patch("payments.models.campay_client.get_transaction_status")
    def test_check_status_full_happy_path(self, mock_status):
        mock_status.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, campay_reference="ref-1",
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], StatutTransaction.SUCCESSFUL)
        self.assertTrue(response.data["subscription_active"])

    @patch("payments.models.campay_client.get_transaction_status")
    def test_check_status_does_not_repoll_already_successful_transaction(self, mock_status):
        transaction = Transaction.objects.create(
            user=self.user, plan=self.plan, amount=self.plan.price,
            phone_number=self.user.phone_number, campay_reference="ref-1",
            status=StatutTransaction.SUCCESSFUL,
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 200)
        mock_status.assert_not_called()

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
            phone_number=self.filleul.phone_number, campay_reference="ref-race",
        )

    def tearDown(self):
        connections.close_all()

    def test_concurrent_sync_status_does_not_double_extend_subscriptions(self):
        start_barrier = threading.Barrier(2)
        errors = []

        def worker():
            try:
                with patch("payments.models.campay_client.get_transaction_status") as mock_status:
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
        parrain_sub = Subscription.objects.get(user=self.parrain, cursus=self.cursus)

        # 25-30j (pas ~60) et 5-7j (pas ~14) : marge pour le temps d'exécution du
        # test, mais large marge de sécurité avant de pouvoir confondre avec un
        # double crédit (qui doublerait carrément ces valeurs).
        filleul_days_left = (filleul_sub.expires_at - timezone.now()).days
        parrain_days_left = (parrain_sub.expires_at - timezone.now()).days
        self.assertTrue(25 <= filleul_days_left <= 30, f"abonnement filleul prolongé en double : {filleul_days_left}j")
        self.assertTrue(5 <= parrain_days_left <= 7, f"abonnement parrain prolongé en double : {parrain_days_left}j")
        self.assertEqual(ParrainageRecompense.objects.filter(transaction=self.transaction).count(), 1)
