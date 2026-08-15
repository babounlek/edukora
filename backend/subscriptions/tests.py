"""
Couvre la logique de durée d'accès (Plan.effective_duration_days, Subscription.extend,
SubscriptionManager.activate_or_extend) et les deux endpoints publics de l'app. Le
flux de paiement/parrainage qui s'appuie sur ces mêmes points d'entrée est déjà bien
couvert côté payments (voir payments.tests.TransactionSyncStatusTests et
ParrainageIdempotenceTests) - ici on teste ces points d'entrée directement, en
particulier le mode JUSQUA_EXAMEN, jamais exercé ailleurs.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, ExamSession
from users.models import User

from .models import DureeMode, Plan, Subscription


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
