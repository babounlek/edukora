import os
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from catalog.models import Cursus, Examen
from payments.models import ManualPayment, ManualPaymentStatus
from subscriptions.models import DureeMode, InscriptionInedite, Plan, ProductType, Subscription
from users.models import User

BASE = "moi@gmail.com"


def lancer(*args, **kwargs):
    sortie = StringIO()
    call_command("seed_donnees_test", *args, stdout=sortie, **kwargs)
    return sortie.getvalue()


def creer_plan(cursus):
    return Plan.objects.create(
        name="Jusqu'à l'examen", cursus=cursus, price=15000, duration_days=30,
        duration_mode=DureeMode.JUSQUA_EXAMEN, product_type=ProductType.ABONNEMENT, inclut_inedit=True,
    )


@override_settings(DEBUG=True)
class SeedDonneesTestTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.plan = creer_plan(self.cursus)

    def _comptes(self):
        return User.objects.filter(email__contains="+edukora-test-")

    def test_cree_cinq_comptes_marques_sans_telephone_ni_relance(self):
        lancer("--email-base", BASE)
        comptes = self._comptes()
        self.assertEqual(comptes.count(), 5)
        for u in comptes:
            self.assertIsNone(u.phone_number)  # aucun SMS/WhatsApp possible
            self.assertFalse(u.email_verified)  # les relances exigent un e-mail confirmé
            self.assertFalse(u.rappels_actifs)
            self.assertTrue(u.full_name.startswith("[TEST] "))
            self.assertTrue(u.email.startswith("moi+edukora-test-"))
            self.assertFalse(u.has_usable_password())

    def test_etats_attendus(self):
        lancer("--email-base", BASE)
        abonne = User.objects.get(email="moi+edukora-test-eleve-abonne@gmail.com")
        self.assertTrue(Subscription.objects.get(user=abonne).is_active)
        self.assertTrue(InscriptionInedite.objects.filter(user=abonne).exists())  # via _activer_acces

        libre = User.objects.get(email="moi+edukora-test-eleve-libre@gmail.com")
        self.assertFalse(Subscription.objects.filter(user=libre).exists())

        expire = User.objects.get(email="moi+edukora-test-eleve-expire@gmail.com")
        self.assertFalse(Subscription.objects.get(user=expire).is_active)

        famille = User.objects.get(email="moi+edukora-test-parent-famille@gmail.com")
        self.assertEqual(famille.profils.count(), 2)
        self.assertEqual(Subscription.objects.filter(user=famille).count(), 1)

        attente = User.objects.get(email="moi+edukora-test-paiement-attente@gmail.com")
        self.assertEqual(ManualPayment.objects.get(user=attente).status, ManualPaymentStatus.PENDING)

    def test_idempotent_et_sans_prolongation(self):
        lancer("--email-base", BASE)
        abonne = User.objects.get(email="moi+edukora-test-eleve-abonne@gmail.com")
        expiration = Subscription.objects.get(user=abonne).expires_at
        lancer("--email-base", BASE)
        self.assertEqual(self._comptes().count(), 5)
        self.assertEqual(Subscription.objects.get(user=abonne).expires_at, expiration)
        self.assertEqual(ManualPayment.objects.count(), 1)
        famille = User.objects.get(email="moi+edukora-test-parent-famille@gmail.com")
        self.assertEqual(famille.profils.count(), 2)

    def test_aucun_sms_n_est_envoye(self):
        with mock.patch("users.sms_backends.get_sms_backend") as sms:
            lancer("--email-base", BASE)
        sms.assert_not_called()

    def test_purge_sans_oui_ne_supprime_rien(self):
        lancer("--email-base", BASE)
        sortie = lancer("--purge")
        self.assertEqual(self._comptes().count(), 5)
        self.assertIn("--oui", sortie)

    def test_purge_supprime_les_comptes_de_test_et_eux_seuls(self):
        vrai = User.objects.create_user(phone_number="677000001", email="vrai@gmail.com", full_name="Vrai Élève")
        # Piège : alias de la bonne forme mais nom sans la marque -> ne doit JAMAIS être supprimé.
        piege = User.objects.create_user(
            phone_number="677000002", email="x+edukora-test-eleve-abonne@gmail.com", full_name="Pas un compte de test",
        )
        lancer("--email-base", BASE)
        lancer("--purge", "--oui")
        self.assertEqual(self._comptes().exclude(pk=piege.pk).count(), 0)
        self.assertTrue(User.objects.filter(pk=vrai.pk).exists())
        self.assertTrue(User.objects.filter(pk=piege.pk).exists())
        self.assertEqual(ManualPayment.objects.count(), 0)

    def test_email_base_avec_plus_refuse(self):
        with self.assertRaises(CommandError):
            lancer("--email-base", "moi+deja@gmail.com")

    def test_sans_plan_jusqua_examen_message_clair(self):
        Plan.objects.all().delete()
        with self.assertRaises(CommandError):
            lancer("--email-base", BASE)


class GardeEnvironnementTests(TestCase):
    @override_settings(DEBUG=False)
    def test_refuse_en_prod_sans_drapeau(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("ALLOW_TEST_DATA", None)
            with self.assertRaises(CommandError):
                lancer("--email-base", BASE)

    @override_settings(DEBUG=False)
    def test_autorise_en_prod_avec_drapeau(self):
        creer_plan(Cursus.objects.get(examen=Examen.BAC, series__code="C"))
        with mock.patch.dict(os.environ, {"ALLOW_TEST_DATA": "1"}):
            lancer("--email-base", BASE)
        self.assertEqual(User.objects.filter(email__contains="+edukora-test-").count(), 5)
