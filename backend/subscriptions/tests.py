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
from users.models import Profil, User

from .models import (
    DureeMode,
    InscriptionInedite,
    InscriptionRepetiteur,
    ParrainageRecompense,
    Plan,
    ProductType,
    Subscription,
    recompenser_parrainage,
    solde_credit_parrainage,
)


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
        # Le référentiel seedé (migration catalog 0056) porte désormais une vraie
        # ExamSession BAC 2026 pour ce cursus - à effacer pour tester un état propre,
        # sinon la création ci-dessous violerait unique_exam_session.
        ExamSession.objects.filter(country=cursus.country, examen=cursus.examen).delete()
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
        # Voir le commentaire du test précédent - même effacement nécessaire.
        ExamSession.objects.filter(country=cursus.country, examen=cursus.examen).delete()
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
        # Le référentiel seedé (migration catalog 0056) porte une vraie ExamSession
        # BAC 2026 pour ce cursus - à effacer pour tester le cas "aucune session".
        ExamSession.objects.filter(country=cursus.country, examen=cursus.examen).delete()
        plan = Plan.objects.create(
            name="Jusqu'à l'examen", cursus=cursus, price=5000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

        self.assertEqual(plan.effective_duration_days(), 30)


class PlanEffectivePriceTests(TestCase):
    """
    Tarification unique du 2026-10-02 : Jusqu'à l'Examen = `price` (15 000 F) par enfant,
    quelle que soit la date d'achat ; chaque enfant supplémentaire de la même famille
    paie 12 000 F (remise fixe de 20 %, jamais cumulative).
    """

    def _plan(self, cursus=None):
        return Plan.objects.create(
            name="Jusqu'à l'Examen", cursus=cursus or _cursus(), price=15000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=30,
        )

    def _payer(self, user, profil, cursus, jours=200):
        Subscription.objects.create(
            user=user, profil=profil, cursus=cursus,
            expires_at=timezone.now() + timedelta(days=jours), duration_mode=DureeMode.JUSQUA_EXAMEN,
        )

    def test_fixe_mode_returns_price_as_is(self):
        plan = Plan.objects.create(
            name="Mensuel", cursus=_cursus(), price=2000,
            duration_mode=DureeMode.FIXE, duration_days=30,
        )
        self.assertEqual(plan.effective_price(), 2000)
        self.assertEqual(plan.prix_enfant_supplementaire(), 2000)

    def test_jusqua_examen_price_does_not_depend_on_the_date(self):
        cursus = _cursus()
        ExamSession.objects.filter(country=cursus.country, examen=cursus.examen).delete()
        ExamSession.objects.create(
            country=cursus.country, examen=cursus.examen, annee=timezone.now().year,
            date_debut=(timezone.now() + timedelta(days=5)).date(),
        )
        self.assertEqual(self._plan(cursus).effective_price(), 15000)

    def test_additional_child_price_is_a_fixed_20_percent_discount(self):
        self.assertEqual(self._plan().prix_enfant_supplementaire(), 12000)

    def test_first_child_pays_full_price_then_each_other_child_pays_12000(self):
        user = User.objects.create_user(phone_number="677000091", password="x")
        cursus = _cursus()
        plan = self._plan(cursus)
        enfants = [user.profils.first()]
        enfants += [Profil.objects.create(compte=user, prenom=f"Enfant{i}", ordre=i + 1) for i in range(3)]

        totaux = []
        for profil in enfants:
            totaux.append(plan.effective_price(user=user, profil=profil))
            self._payer(user, profil, cursus)

        self.assertEqual(totaux, [15000, 12000, 12000, 12000])
        self.assertEqual(sum(totaux[:2]), 27000)
        self.assertEqual(sum(totaux[:3]), 39000)
        self.assertEqual(sum(totaux), 51000)

    def test_renewing_an_already_active_child_is_not_discounted(self):
        user = User.objects.create_user(phone_number="677000092", password="x")
        cursus = _cursus()
        plan = self._plan(cursus)
        premier = user.profils.first()
        second = Profil.objects.create(compte=user, prenom="Second", ordre=1)
        self._payer(user, premier, cursus)
        self._payer(user, second, cursus)

        self.assertEqual(plan.effective_price(user=user, profil=premier), 15000)

    def test_another_family_does_not_get_the_discount(self):
        cursus = _cursus()
        plan = self._plan(cursus)
        autre = User.objects.create_user(phone_number="677000093", password="x")
        self._payer(autre, autre.profils.first(), cursus)
        user = User.objects.create_user(phone_number="677000094", password="x")

        self.assertEqual(plan.effective_price(user=user, profil=user.profils.first()), 15000)


class SubscriptionExtendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000010", password="x")
        self.cursus = _cursus()

    def test_extend_stacks_on_top_of_a_still_active_expiry(self):
        subscription = Subscription.objects.create(
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )

        subscription.extend(30)

        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=40), delta=timedelta(seconds=5),
        )

    def test_extend_restarts_from_now_when_already_expired(self):
        subscription = Subscription.objects.create(
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() - timedelta(days=10),
        )

        subscription.extend(30)

        self.assertAlmostEqual(
            subscription.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )

    def test_is_active_reflects_expiry(self):
        subscription = Subscription.objects.create(
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
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

    def test_new_subscription_defaults_to_fixe(self):
        subscription = Subscription.objects.activate_or_extend(self.user, self.cursus, 30)
        self.assertEqual(subscription.duration_mode, DureeMode.FIXE)

    def test_new_subscription_records_jusqua_examen_when_purchased_directly(self):
        subscription = Subscription.objects.activate_or_extend(
            self.user, self.cursus, 30, duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertEqual(subscription.duration_mode, DureeMode.JUSQUA_EXAMEN)

    def test_jusqua_examen_purchase_upgrades_an_existing_fixe_subscription(self):
        Subscription.objects.activate_or_extend(self.user, self.cursus, 30, duration_mode=DureeMode.FIXE)
        subscription = Subscription.objects.activate_or_extend(
            self.user, self.cursus, 30, duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertEqual(subscription.duration_mode, DureeMode.JUSQUA_EXAMEN)

    def test_fixe_topup_never_downgrades_an_existing_jusqua_examen_subscription(self):
        """Un réabonnement Mensuel moins cher, après un achat Jusqu'à l'Examen, ne doit
        pas faire perdre l'accès aux fonctionnalités exclusives à ce palier pour le
        reste de la période déjà payée - voir Subscription.extend."""
        Subscription.objects.activate_or_extend(self.user, self.cursus, 30, duration_mode=DureeMode.JUSQUA_EXAMEN)
        subscription = Subscription.objects.activate_or_extend(
            self.user, self.cursus, 30, duration_mode=DureeMode.FIXE,
        )
        self.assertEqual(subscription.duration_mode, DureeMode.JUSQUA_EXAMEN)

    def test_two_profils_of_the_same_account_get_independent_subscriptions_on_the_same_cursus(self):
        """Le cas que la contrainte élargie (user, cursus, profil) débloque : deux
        enfants du même compte préparant le même examen, chacun son abonnement, chacun
        sa propre échéance - voir unique_subscription_per_cursus_profil."""
        aine = self.user.profils.first()
        cadet = Profil.objects.create(compte=self.user, prenom="Junior")

        sub_aine = Subscription.objects.activate_or_extend(self.user, self.cursus, 30, profil=aine)
        sub_cadet = Subscription.objects.activate_or_extend(self.user, self.cursus, 90, profil=cadet)

        self.assertNotEqual(sub_aine.id, sub_cadet.id)
        self.assertEqual(Subscription.objects.filter(user=self.user, cursus=self.cursus).count(), 2)
        self.assertAlmostEqual(
            sub_aine.expires_at, timezone.now() + timedelta(days=30), delta=timedelta(seconds=5),
        )
        self.assertAlmostEqual(
            sub_cadet.expires_at, timezone.now() + timedelta(days=90), delta=timedelta(seconds=5),
        )

        # Prolonger l'un ne doit jamais toucher l'autre.
        Subscription.objects.activate_or_extend(self.user, self.cursus, 10, profil=aine)
        sub_cadet.refresh_from_db()
        self.assertAlmostEqual(
            sub_cadet.expires_at, timezone.now() + timedelta(days=90), delta=timedelta(seconds=5),
        )

    def test_profil_defaults_to_the_account_s_first_profil_when_not_given(self):
        """Comportement inchangé pour l'immense majorité des appels (aucun profil
        précisé) - voir la docstring de activate_or_extend."""
        subscription = Subscription.objects.activate_or_extend(self.user, self.cursus, 30)
        self.assertEqual(subscription.profil_id, self.user.profils.first().id)


class InscriptionInediteExtendTests(TestCase):
    """Miroir de SubscriptionExtendTests - même comportement, modèle séparé (décision "C2")."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677000030", password="x")
        self.cursus = _cursus()

    def test_extend_stacks_on_top_of_a_still_active_expiry(self):
        inscription = InscriptionInedite.objects.create(
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )
        inscription.extend(30)
        self.assertAlmostEqual(
            inscription.expires_at, timezone.now() + timedelta(days=40), delta=timedelta(seconds=5),
        )

    def test_is_active_reflects_expiry(self):
        inscription = InscriptionInedite.objects.create(
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(inscription.is_active)
        inscription.expires_at = timezone.now() - timedelta(days=1)
        self.assertFalse(inscription.is_active)


class InscriptionInediteConstraintTests(TestCase):
    def test_duplicate_user_cursus_pair_is_rejected(self):
        user = User.objects.create_user(phone_number="677000031", password="x")
        profil = user.profils.first()
        cursus = _cursus()
        InscriptionInedite.objects.create(
            user=user, profil=profil, cursus=cursus, expires_at=timezone.now() + timedelta(days=1),
        )

        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                InscriptionInedite.objects.create(
                    user=user, profil=profil, cursus=cursus, expires_at=timezone.now() + timedelta(days=1),
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


class ParrainageSkippedForAddonRepetiteurTests(TestCase):
    """recompenser_parrainage() ne s'applique jamais à un achat d'add-on (voir sa
    docstring dans models.py) - portée volontairement limitée à l'abonnement de base.
    ADDON_REPETITEUR sert d'exemple depuis le retrait de l'achat séparé de l'add-on
    Épreuves Inédites (2026-09-30) - même add-on, même règle."""

    def setUp(self):
        self.cursus = _cursus()
        self.admin = User.objects.create_user(phone_number="677000042", password="x", is_staff=True)
        self.parrain = User.objects.create_user(phone_number="677000040", password="x")
        self.filleul = User.objects.create_user(
            phone_number="677000041", password="x", referred_by=self.parrain,
        )
        self.addon_plan = Plan.objects.create(
            name="Add-on Fiches", cursus=self.cursus, price=1000, product_type=ProductType.ADDON_REPETITEUR,
        )

    def test_addon_purchase_activates_the_addon_but_never_rewards_the_parrain(self):
        from payments.models import ManualPayment, MobileMoneyOperator

        payment = ManualPayment.objects.create(
            user=self.filleul, profil=self.filleul.profils.first(), plan=self.addon_plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.addon_plan.price, amount_declared=self.addon_plan.price,
            payer_phone_number=self.filleul.phone_number, transaction_reference="ref-addon-1",
        )

        payment.approve(admin_user=self.admin)

        self.assertTrue(
            InscriptionRepetiteur.objects.filter(
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

    def test_pack_examen_est_liste_meme_loin_de_l_examen(self):
        """Plus de fenêtre d'urgence (Plan.est_achetable retiré le 2026-08-19) : le
        pack reste au catalogue toute l'année scolaire, seul son prix (voir
        PlanEffectivePriceTests) reflète la proximité de l'examen."""
        ExamSession.objects.create(
            country=self.cursus.country, examen=self.cursus.examen, annee=timezone.now().year + 1,
            date_debut=(timezone.now() + timedelta(days=280)).date(),
        )
        Plan.objects.create(
            name="Pack Examen", cursus=self.cursus, price=12000,
            duration_mode=DureeMode.JUSQUA_EXAMEN, duration_days=60,
        )

        response = self.client.get("/subscriptions/plans/", {"cursus": self.cursus.pk})

        self.assertIn("Pack Examen", [p["name"] for p in response.data])

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
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
        )
        Subscription.objects.create(
            user=self.other_user, profil=self.other_user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=10),
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
            user=self.user, profil=self.user.profils.first(),
            cursus=self.cursus, expires_at=timezone.now() + timedelta(days=365),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_plan_name_is_none_without_any_matching_payment(self):
        response = self.client.get("/subscriptions/mine/")
        self.assertIsNone(response.data[0]["plan_name"])

    def test_plan_name_reflects_the_latest_successful_transaction(self):
        from payments.models import StatutTransaction, Transaction

        Transaction.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan, subscription=self.subscription,
            amount=self.plan.price, phone_number=self.user.phone_number,
            status=StatutTransaction.SUCCESSFUL,
        )

        response = self.client.get("/subscriptions/mine/")

        self.assertEqual(response.data[0]["plan_name"], self.plan.name)

    def test_plan_name_reflects_the_more_recent_of_transaction_and_manual_payment(self):
        from payments.models import ManualPayment, ManualPaymentStatus, MobileMoneyOperator, StatutTransaction, Transaction

        older_plan = Plan.objects.create(name="Ancien forfait", cursus=self.cursus, price=1500, duration_days=30)
        Transaction.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=older_plan, subscription=self.subscription,
            amount=older_plan.price, phone_number=self.user.phone_number,
            status=StatutTransaction.SUCCESSFUL,
        )
        ManualPayment.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan, subscription=self.subscription,
            operator=MobileMoneyOperator.ORANGE, amount_expected=self.plan.price,
            amount_declared=self.plan.price, payer_phone_number=self.user.phone_number,
            transaction_reference="REF123", status=ManualPaymentStatus.APPROVED,
        )

        response = self.client.get("/subscriptions/mine/")

        self.assertEqual(response.data[0]["plan_name"], self.plan.name)


class ParrainageAcrossPaymentChannelsTests(TestCase):
    """
    Décision du 2026-09-28 (voir project_parrainage_eleve_recalibrage) : le parrain ne
    reçoit plus rien, quel que soit le canal de paiement du filleul (Campay ou manuel) -
    recompenser_parrainage n'est plus appelée par ManualPayment.approve() ni par
    Transaction._confirmer_succes. La fonction elle-même reste intacte (voir sa
    docstring) : test_recompenser_parrainage_frozen_function_still_works_if_called_directly
    documente qu'un appel direct détecterait toujours correctement la première
    conversion sur les deux canaux à la fois - utile si les crédits déjà accordés avant
    cette date doivent un jour être audités.
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
            user=self.filleul, profil=self.filleul.profils.first(), plan=self.plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=self.plan.price, amount_declared=self.plan.price,
            payer_phone_number=self.filleul.phone_number, transaction_reference=reference,
        )

    def test_manual_payment_approval_no_longer_rewards_parrain(self):
        payment = self._manual_payment("ref-manual-1")

        payment.approve(admin_user=self.admin)

        self.assertFalse(ParrainageRecompense.objects.filter(manual_payment=payment).exists())
        self.assertEqual(solde_credit_parrainage(self.parrain), 0)
        self.assertFalse(Subscription.objects.filter(user=self.parrain, cursus=self.cursus).exists())

    def test_recompenser_parrainage_frozen_function_still_works_if_called_directly(self):
        from payments.models import StatutTransaction, Transaction

        transaction = Transaction.objects.create(
            user=self.filleul, profil=self.filleul.profils.first(), plan=self.plan, amount=self.plan.price,
            phone_number=self.filleul.phone_number, provider_reference="ref-campay-1",
            status=StatutTransaction.SUCCESSFUL,
        )
        # Simule l'activation déjà effectuée par Transaction.sync_status() (sans
        # repasser par lui, qui appellerait campay_client) : même point de
        # convergence qu'un vrai paiement Campay réussi. Appel direct de la fonction
        # gelée (plus aucun call site en production, voir subscriptions.models) pour
        # documenter qu'elle détecte toujours correctement la première conversion.
        Subscription.objects.activate_or_extend(
            user=self.filleul, cursus=self.cursus, duration_days=self.plan.effective_duration_days(),
        )
        recompenser_parrainage(transaction)

        manual = self._manual_payment("ref-manual-1")
        manual.approve(admin_user=self.admin)

        # L'appel direct a bien créé la récompense sur la Transaction Campay...
        self.assertEqual(ParrainageRecompense.objects.filter(parrain=self.parrain).count(), 1)
        self.assertTrue(ParrainageRecompense.objects.filter(transaction=transaction).exists())
        # ...mais l'approbation du paiement manuel, elle, n'appelle plus la fonction du
        # tout : aucune seconde récompense, même si on avait pu croire (avant le
        # 2026-09-28) que le manuel serait la "première conversion" sur son propre canal.
        self.assertFalse(ParrainageRecompense.objects.filter(manual_payment=manual).exists())


class CursusPrepareDeduitDeLAbonnementTests(TestCase):
    """
    Payer pour un cursus est la déclaration la plus forte de ce qu'on prépare : elle
    est reprise telle quelle pour le compte à rebours, mais jamais par-dessus ce que
    l'élève a lui-même déclaré.
    """

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900202", password="x")
        self.cursus = _cursus()

    def test_un_premier_abonnement_declare_le_cursus(self):
        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=30)

        self.user.refresh_from_db()
        self.assertEqual(self.user.cursus_prepare_id, self.cursus.id)

    def test_une_declaration_existante_nest_jamais_ecrasee(self):
        autre = Cursus.objects.exclude(pk=self.cursus.pk).first()
        self.user.cursus_prepare = autre
        self.user.save(update_fields=["cursus_prepare"])

        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=30)

        self.user.refresh_from_db()
        # Un parent qui achète un second cursus, ou un rattrapage sur une ancienne
        # série, ne doit pas réécrire le choix de l'élève.
        self.assertEqual(self.user.cursus_prepare_id, autre.id)

    def test_une_prolongation_ne_change_rien_non_plus(self):
        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=30)
        autre = Cursus.objects.exclude(pk=self.cursus.pk).first()
        self.user.cursus_prepare = autre
        self.user.save(update_fields=["cursus_prepare"])

        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=30)

        self.user.refresh_from_db()
        self.assertEqual(self.user.cursus_prepare_id, autre.id)
