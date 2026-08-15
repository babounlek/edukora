"""
Couvre la logique de durée d'accès (Plan.effective_duration_days, Subscription.extend,
SubscriptionManager.activate_or_extend) et les deux endpoints publics de l'app. Le
flux de paiement/parrainage qui s'appuie sur ces mêmes points d'entrée est déjà bien
couvert côté payments (voir payments.tests.TransactionSyncStatusTests et
ParrainageIdempotenceTests) - ici on teste ces points d'entrée directement, en
particulier le mode JUSQUA_EXAMEN, jamais exercé ailleurs.
"""

from datetime import timedelta

from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, ExamSession
from users.models import User

from .models import DureeMode, InscriptionInedite, ParrainageRecompense, Plan, ProductType, Subscription, recompenser_parrainage


def _cursus():
    # Référentiel (Country/Series/Cursus) déjà seedé par les migrations catalog (voir
    # 0003_seed_referentiel.py) - présent dans la base de test après migration, donc
    # on le récupère plutôt que d'en recréer un en double.
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


class PlanEffectiveDurationDaysTests(TestCase):
    def test_fixe_mode_returns_duration_days_as_is(self):
        plan = Plan.objects.create(
            name="Trimestre", cursus=_cursus(), price=2000,
            duration_mode=DureeMode.FIXE, duration_days=90,
        )
        self.assertEqual(plan.effective_duration_days(), 90)

    def test_jusqua_examen_computes_days_until_next_exam_session(self):
        cursus = _cursus()
        ExamSession.objects.create(
            country=cursus.country, examen=cursus.examen, annee=timezone.now().year,
            date_debut=(timezone.now() + timedelta(days=45)).date(),
        )
        plan = Plan.objects.create(
            name="Jusqu'à l'examen", cursus=cursus, price=5000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        # Tolérance d'un jour : la date "aujourd'hui" utilisée par le calcul peut
        # différer de celle de ce test si l'exécution chevauche minuit.
        self.assertIn(plan.effective_duration_days(), (44, 45))

    def test_jusqua_examen_never_returns_less_than_one_day_even_if_exam_is_today(self):
        cursus = _cursus()
        ExamSession.objects.create(
            country=cursus.country, examen=cursus.examen, annee=timezone.now().year,
            date_debut=timezone.now().date(),
        )
        plan = Plan.objects.create(
            name="Jusqu'à l'examen", cursus=cursus, price=5000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        self.assertGreaterEqual(plan.effective_duration_days(), 1)

    def test_jusqua_examen_falls_back_to_duration_days_without_an_exam_session(self):
        cursus = _cursus()
        self.assertFalse(ExamSession.objects.filter(country=cursus.country, examen=cursus.examen).exists())
        plan = Plan.objects.create(
            name="Jusqu'à l'examen", cursus=cursus, price=5000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        self.assertEqual(plan.effective_duration_days(), 30)


class SubscriptionExtendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000010", password="x")
        self.cursus = _cursus()

    def test_extend_stacks_on_top_of_a_still_active_expiry(self):
        subscription = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )

        subscription.extend(30)

        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=40), delta=timedelta(seconds=5),
        )

    def test_extend_restarts_from_now_when_already_expired(self):
        subscription = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() - timedelta(days=10),
        )

        subscription.extend(30)

        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )

    def test_is_active_reflects_expiry(self):
        subscription = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(subscription.is_active)

        subscription.expires_at = timezone.now() - timedelta(days=1)
        self.assertFalse(subscription.is_active)


class SubscriptionManagerActivateOrExtendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000011", password="x")
        self.cursus = _cursus()

    def test_creates_a_new_subscription_when_none_exists(self):
        subscription = Subscription.objects.activate_or_extend(self.user, self.cursus, 30)

        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )
        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 1)

    def test_extends_the_existing_subscription_instead_of_duplicating(self):
        Subscription.objects.activate_or_extend(self.user, self.cursus, 30)
        Subscription.objects.activate_or_extend(self.user, self.cursus, 15)

        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 1)
        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=45), delta=timedelta(seconds=5),
        )


class InscriptionInediteExtendTests(TestCase):
    """Miroir de SubscriptionExtendTests - même comportement, modèle séparé (décision "C2")."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000030", password="x")
        self.cursus = _cursus()

    def test_extend_stacks_on_top_of_a_still_active_expiry(self):
        inscription = InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )
        inscription.extend(30)
        self.assertAlmostEqual(
            inscription.expires_at, timezone.now() + timedelta(days=40), delta=timedelta(seconds=5),
        )

    def test_is_active_reflects_expiry(self):
        inscription = InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(inscription.is_active)
        inscription.expires_at = timezone.now() - timedelta(days=1)
        self.assertFalse(inscription.is_active)


class InscriptionInediteConstraintTests(TestCase):
    def test_duplicate_user_cursus_pair_is_rejected(self):
        user = User.objects.create_user(phone_number="677000031", password="x")
        cursus = _cursus()
        InscriptionInedite.objects.create(user=user, cursus=cursus, expires_at=timezone.now() + timedelta(days=1))

        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                InscriptionInedite.objects.create(
                    user=user, cursus=cursus, expires_at=timezone.now() + timedelta(days=1),
                )


class InscriptionInediteManagerActivateOrExtendTests(TestCase):
    """Miroir de SubscriptionManagerActivateOrExtendTests, plus la garantie
    d'indépendance entre les deux modèles qui justifie la décision "C2"."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000032", password="x")
        self.cursus = _cursus()

    def test_creates_a_new_inscription_when_none_exists(self):
        inscription = InscriptionInedite.objects.activate_or_extend(self.user, self.cursus, 30)

        self.assertAlmostEqual(
            inscription.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )
        self.assertEqual(InscriptionInedite.objects.filter(user=self.user, cursus=self.cursus).count(), 1)

    def test_extends_the_existing_inscription_instead_of_duplicating(self):
        InscriptionInedite.objects.activate_or_extend(self.user, self.cursus, 30)
        InscriptionInedite.objects.activate_or_extend(self.user, self.cursus, 15)

        self.assertEqual(InscriptionInedite.objects.filter(user=self.user, cursus=self.cursus).count(), 1)
        inscription = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual(
            inscription.expires_at, timezone.now() + timedelta(days=45), delta=timedelta(seconds=5),
        )

    def test_activating_the_addon_never_touches_an_existing_base_subscription(self):
        Subscription.objects.activate_or_extend(self.user, self.cursus, 30)

        InscriptionInedite.objects.activate_or_extend(self.user, self.cursus, 7)

        subscription = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )


class ParrainageSkippedForAddonInediteTests(TestCase):
    """recompenser_parrainage() ne s'applique jamais à un achat d'add-on (voir sa
    docstring dans models.py) - portée volontairement limitée à l'abonnement de base."""

    def setUp(self):
        self.cursus = _cursus()
        self.admin = User.objects.create_user(phone_number="677000042", password="x", is_staff=True)
        self.parrain = User.objects.create_user(phone_number="677000040", password="x")
        self.filleul = User.objects.create_user(
            phone_number="677000041", password="x", referred_by=self.parrain,
        )
        self.addon_plan = Plan.objects.create(
            name="Épreuves Inédites", cursus=self.cursus, price=1000, product_type=ProductType.ADDON_INEDIT,
        )

    def test_addon_purchase_activates_the_addon_but_never_rewards_the_parrain(self):
        from payments.models import ManualPayment, MobileMoneyOperator

        payment = ManualPayment.objects.create(
            user=self.filleul, plan=self.addon_plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.addon_plan.price, amount_declared=self.addon_plan.price,
            payer_phone_number=self.filleul.phone_number, transaction_reference="ref-addon-1",
        )

        payment.approve(admin_user=self.admin)

        self.assertTrue(
            InscriptionInedite.objects.filter(
                user=self.filleul, cursus=self.cursus, expires_at__gt=timezone.now(),
            ).exists(),
        )
        self.assertFalse(ParrainageRecompense.objects.filter(manual_payment=payment).exists())
        self.assertFalse(Subscription.objects.filter(user=self.parrain, cursus=self.cursus).exists())
        self.assertFalse(InscriptionInedite.objects.filter(user=self.parrain, cursus=self.cursus).exists())


class PlanListViewTests(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.other_cursus = Cursus.objects.exclude(pk=self.cursus.pk).first()
        self.client = APIClient()

    def test_endpoint_is_public(self):
        response = self.client.get("/subscriptions/plans/")
        self.assertEqual(response.status_code, 200)

    def test_only_active_plans_are_listed(self):
        Plan.objects.create(name="Actif", cursus=self.cursus, price=1000, is_active=True)
        Plan.objects.create(name="Retiré", cursus=self.cursus, price=1000, is_active=False)

        response = self.client.get("/subscriptions/plans/")

        names = [p["name"] for p in response.data]
        self.assertIn("Actif", names)
        self.assertNotIn("Retiré", names)

    def test_filters_by_cursus_query_param(self):
        Plan.objects.create(name="Pour ce cursus", cursus=self.cursus, price=1000)
        Plan.objects.create(name="Pour un autre cursus", cursus=self.other_cursus, price=1000)

        response = self.client.get("/subscriptions/plans/", {"cursus": self.cursus.pk})

        names = [p["name"] for p in response.data]
        self.assertIn("Pour ce cursus", names)
        self.assertNotIn("Pour un autre cursus", names)


class MySubscriptionsViewTests(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.user = User.objects.create_user(phone_number="677000012", password="x")
        self.other_user = User.objects.create_user(phone_number="677000013", password="x")
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.get("/subscriptions/mine/")
        self.assertEqual(response.status_code, 401)

    def test_returns_only_the_authenticated_user_subscriptions(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )
        Subscription.objects.create(
            user=self.other_user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/subscriptions/mine/")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["cursus"]["id"], self.cursus.pk)
        self.assertTrue(response.data[0]["is_active"])


class MySubscriptionsViewPlanNameTests(TestCase):
    """plan_name est dérivé du dernier paiement réussi ayant activé/prolongé la
    Subscription (Transaction Campay ou ManualPayment, voir SubscriptionSerializer.
    get_plan_name) - jamais stocké sur Subscription elle-même."""

    def setUp(self):
        self.cursus = _cursus()
        self.user = User.objects.create_user(phone_number="677000014", password="x")
        self.plan = Plan.objects.create(name="BAC Série C - Max (1 an)", cursus=self.cursus, price=15000, duration_days=365)
        self.subscription = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=365),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_plan_name_is_none_without_any_matching_payment(self):
        response = self.client.get("/subscriptions/mine/")
        self.assertIsNone(response.data[0]["plan_name"])

    def test_plan_name_reflects_the_latest_successful_transaction(self):
        from payments.models import StatutTransaction, Transaction

        Transaction.objects.create(
            user=self.user, plan=self.plan, subscription=self.subscription,
            amount=self.plan.price, phone_number=self.user.phone_number,
            status=StatutTransaction.SUCCESSFUL,
        )

        response = self.client.get("/subscriptions/mine/")

        self.assertEqual(response.data[0]["plan_name"], self.plan.name)

    def test_plan_name_reflects_the_more_recent_of_transaction_and_manual_payment(self):
        from payments.models import ManualPayment, ManualPaymentStatus, MobileMoneyOperator, StatutTransaction, Transaction

        older_plan = Plan.objects.create(name="Ancien forfait", cursus=self.cursus, price=1500, duration_days=30)
        Transaction.objects.create(
            user=self.user, plan=older_plan, subscription=self.subscription,
            amount=older_plan.price, phone_number=self.user.phone_number,
            status=StatutTransaction.SUCCESSFUL,
        )
        ManualPayment.objects.create(
            user=self.user, plan=self.plan, subscription=self.subscription,
            operator=MobileMoneyOperator.ORANGE, amount_expected=self.plan.price,
            amount_declared=self.plan.price, payer_phone_number=self.user.phone_number,
            transaction_reference="REF123", status=ManualPaymentStatus.APPROVED,
        )

        response = self.client.get("/subscriptions/mine/")

        self.assertEqual(response.data[0]["plan_name"], self.plan.name)


class ParrainageAcrossPaymentChannelsTests(TestCase):
    """
    recompenser_parrainage() généralisé pour accepter Campay ET le paiement manuel
    (voir payments.tests.ParrainageIdempotenceTests pour le cas Campay seul, déjà
    couvert) - ici on vérifie que la "première conversion" est évaluée sur les deux
    canaux à la fois, jamais un seul en isolation.
    """

    def setUp(self):
        self.cursus = _cursus()
        self.admin = User.objects.create_user(phone_number="677000022", password="x", is_staff=True)
        self.parrain = User.objects.create_user(phone_number="677000020", password="x")
        self.filleul = User.objects.create_user(
            phone_number="677000021", password="x", referred_by=self.parrain,
        )
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)

    def _manual_payment(self, reference):
        from payments.models import ManualPayment, MobileMoneyOperator

        return ManualPayment.objects.create(
            user=self.filleul, plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.filleul.phone_number, transaction_reference=reference,
        )

    def test_first_manual_payment_approval_rewards_parrain(self):
        payment = self._manual_payment("ref-manual-1")

        payment.approve(admin_user=self.admin)

        self.assertTrue(ParrainageRecompense.objects.filter(manual_payment=payment).exists())
        self.assertTrue(Subscription.objects.filter(user=self.parrain, cursus=self.cursus).exists())

    def test_second_manual_payment_does_not_reward_parrain_again(self):
        first = self._manual_payment("ref-manual-1")
        first.approve(admin_user=self.admin)
        parrain_sub = Subscription.objects.get(user=self.parrain, cursus=self.cursus)
        expires_after_first = parrain_sub.expires_at

        second = self._manual_payment("ref-manual-2")
        second.approve(admin_user=self.admin)

        self.assertEqual(ParrainageRecompense.objects.filter(parrain=self.parrain).count(), 1)
        parrain_sub.refresh_from_db()
        self.assertEqual(parrain_sub.expires_at, expires_after_first)

    def test_campay_then_manual_only_rewards_once_on_true_first_conversion(self):
        from payments.models import StatutTransaction, Transaction

        transaction = Transaction.objects.create(
            user=self.filleul, plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, campay_reference="ref-campay-1",
            status=StatutTransaction.SUCCESSFUL,
        )
        # Simule l'activation déjà effectuée par Transaction.sync_status() (sans
        # repasser par lui, qui appellerait campay_client) : même point de
        # convergence + même récompense qu'un vrai paiement Campay réussi.
        Subscription.objects.activate_or_extend(
            user=self.filleul, cursus=self.cursus, duration_days=self.plan.effective_duration_days(),
        )
        recompenser_parrainage(transaction)

        manual = self._manual_payment("ref-manual-1")
        manual.approve(admin_user=self.admin)

        self.assertEqual(ParrainageRecompense.objects.filter(parrain=self.parrain).count(), 1)
        self.assertTrue(ParrainageRecompense.objects.filter(transaction=transaction).exists())
        self.assertFalse(ParrainageRecompense.objects.filter(manual_payment=manual).exists())
