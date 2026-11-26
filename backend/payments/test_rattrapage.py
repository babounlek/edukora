"""
Audit du 2026-11-16 (section 4.1) : un paiement CamPay validé après la fermeture de la page d'abonnement
doit donner son accès, prévenir le payeur, et ne jamais faire échouer la déclaration ou la validation
d'un paiement parce qu'un message n'a pas pu partir.
"""

from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from catalog.models import Cursus, Examen
from subscriptions.models import Plan, Subscription
from users.models import User

from .campay_client import CampayError
from .models import ManualPayment, MobileMoneyAccount, MobileMoneyOperator, StatutTransaction, Transaction
from .rattrapage import rattraper_paiements_en_attente


def _cursus():
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


class RattrapageTests(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.user = User.objects.create_user(phone_number="677100001", password="x")
        self.plan = Plan.objects.create(name="Mois", cursus=self.cursus, price=2000, duration_days=30)

    def _transaction(self, age=timedelta(minutes=10), **champs):
        transaction = Transaction.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan, amount=2000,
            phone_number="677100001", provider_reference=champs.pop("provider_reference", "ref-1"), **champs,
        )
        # created_at / updated_at sont posés par la base : on les recule à la main.
        Transaction.objects.filter(pk=transaction.pk).update(
            created_at=timezone.now() - age, updated_at=timezone.now() - age,
        )
        return transaction

    @patch("payments.campay_client.get_transaction_status")
    def test_un_paiement_valide_apres_coup_active_l_acces(self, statut):
        statut.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        transaction = self._transaction()

        self.assertEqual(rattraper_paiements_en_attente(), 1)

        transaction.refresh_from_db()
        self.assertEqual(transaction.status, StatutTransaction.SUCCESSFUL)
        self.assertTrue(Subscription.objects.get(user=self.user, cursus=self.cursus).is_active)

    @patch("payments.campay_client.get_transaction_status")
    def test_la_page_d_abonnement_sonde_seule_les_deux_premieres_minutes(self, statut):
        self._transaction(age=timedelta(minutes=1))

        self.assertEqual(rattraper_paiements_en_attente(), 0)
        statut.assert_not_called()

    @patch("payments.campay_client.get_transaction_status")
    def test_au_dela_de_48_heures_on_n_interroge_plus(self, statut):
        self._transaction(age=timedelta(hours=49))

        self.assertEqual(rattraper_paiements_en_attente(), 0)
        statut.assert_not_called()

    @patch("payments.campay_client.get_transaction_status")
    def test_sans_reference_chez_l_agregateur_rien_a_relire(self, statut):
        self._transaction(provider_reference="")

        self.assertEqual(rattraper_paiements_en_attente(), 0)
        statut.assert_not_called()

    @patch("payments.campay_client.get_transaction_status")
    def test_un_agregateur_injoignable_ne_fait_rien_echouer(self, statut):
        statut.side_effect = CampayError("injoignable")
        transaction = self._transaction()

        self.assertEqual(rattraper_paiements_en_attente(), 0)

        transaction.refresh_from_db()
        self.assertEqual(transaction.status, StatutTransaction.PENDING)

    @patch("payments.campay_client.get_transaction_status")
    def test_a_l_ouverture_de_l_application_une_lecture_par_minute(self, statut):
        statut.return_value = {"status": StatutTransaction.PENDING, "reference": "ref-1"}
        self._transaction()

        rattraper_paiements_en_attente(user=self.user)
        # La première lecture vient de réécrire `updated_at` : la seconde attend une minute.
        rattraper_paiements_en_attente(user=self.user)

        self.assertEqual(statut.call_count, 1)

    @patch("payments.campay_client.get_transaction_status")
    def test_la_banniere_reprendre_relit_d_abord_le_paiement(self, statut):
        statut.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        self._transaction()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.user)}")

        reponse = client.get("/relances/paiement-a-reprendre/")

        # Proposer de « reprendre » un paiement qui vient d'aboutir, ce serait le faire payer deux fois. Et
        # l'application, chargée avant ce rattrapage, doit apprendre que l'accès est ouvert (voir lib/accesActive.ts).
        self.assertEqual(reponse.data, {"a_reprendre": False, "acces_active": True})
        self.assertTrue(Subscription.objects.get(user=self.user, cursus=self.cursus).is_active)

        # À la lecture suivante, plus rien à rattraper : l'application ne relit pas le compte en boucle.
        self.assertEqual(client.get("/relances/paiement-a-reprendre/").data, {"a_reprendre": False, "acces_active": False})


class RecuTests(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.plan = Plan.objects.create(name="Mois", cursus=self.cursus, price=2000, duration_days=30)

    @patch("payments.models._notifier_utilisateur")
    @patch("payments.campay_client.get_transaction_status")
    def test_un_succes_campay_previent_le_numero_qui_a_paye(self, statut, sms):
        statut.return_value = {"status": StatutTransaction.SUCCESSFUL, "reference": "ref-1"}
        # Compte ouvert par e-mail : aucun numéro sur le compte, c'est le numéro payeur qui reçoit le SMS.
        user = User.objects.create_user(None, email="parent@example.com", password="x")
        User.objects.filter(pk=user.pk).update(email_verified=True)
        user.refresh_from_db()
        transaction = Transaction.objects.create(
            user=user, profil=user.profils.first(), plan=self.plan, amount=2000,
            phone_number="677100002", provider_reference="ref-1",
        )

        transaction.sync_status()
        # Rejouer la confirmation ne renvoie pas un second reçu.
        Transaction.objects.get(pk=transaction.pk).sync_status()

        sms.assert_called_once()
        self.assertEqual(sms.call_args.args[0], "677100002")
        self.assertIn("2000 FCFA", sms.call_args.args[1])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["parent@example.com"])

    @patch("payments.models._notifier_utilisateur", side_effect=RuntimeError("fournisseur SMS en panne"))
    def test_une_panne_de_sms_ne_fait_pas_echouer_la_declaration(self, _sms):
        MobileMoneyAccount.objects.create(
            operator=MobileMoneyOperator.ORANGE, phone_number="699000000", account_name="EduKora",
        )
        user = User.objects.create_user(phone_number="677100003", password="x")

        paiement = ManualPayment.objects.declare(
            user=user, plan=self.plan, operator=MobileMoneyOperator.ORANGE, amount_declared=2000,
            payer_phone_number="677100003", transaction_reference="OM-1",
        )

        self.assertEqual(ManualPayment.objects.filter(pk=paiement.pk).count(), 1)


class DeclarationTests(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.plan = Plan.objects.create(name="Mois", cursus=self.cursus, price=2000, duration_days=30)
        MobileMoneyAccount.objects.create(
            operator=MobileMoneyOperator.ORANGE, phone_number="699000000", account_name="EduKora",
        )
        self.user = User.objects.create_user(phone_number="677100004", password="x")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.user)}")

    def _donnees(self, **plus):
        return {
            "plan": self.plan.pk, "operator": MobileMoneyOperator.ORANGE,
            "payer_phone_number": "677100004", "transaction_reference": "OM-REF-1", **plus,
        }

    def test_l_adresse_retenue_est_celle_du_client_pas_celle_du_proxy(self):
        reponse = self.client.post(
            "/payments/manual/declare/", self._donnees(),
            HTTP_X_CLIENT_IP="41.202.10.10", REMOTE_ADDR="172.18.0.3",
        )

        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(ManualPayment.objects.get(pk=reponse.data["id"]).declared_ip, "41.202.10.10")

    def test_une_preuve_qui_n_est_ni_image_ni_pdf_est_refusee(self):
        programme = SimpleUploadedFile("preuve.exe", b"MZ\x90\x00binaire", content_type="application/octet-stream")
        reponse = self.client.post("/payments/manual/declare/", self._donnees(proof=programme), format="multipart")
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("proof", reponse.data)

    def test_une_image_deguisee_est_refusee(self):
        fausse = SimpleUploadedFile("preuve.png", b"<html>pas une image</html>", content_type="image/png")
        reponse = self.client.post("/payments/manual/declare/", self._donnees(proof=fausse), format="multipart")
        self.assertEqual(reponse.status_code, 400)

    def test_une_vraie_capture_est_acceptee_sous_un_nom_neutre(self):
        capture = SimpleUploadedFile(
            "../../Capture d'écran 2026.PNG", b"\x89PNG\r\n\x1a\n" + b"\x00" * 32, content_type="image/png",
        )
        reponse = self.client.post("/payments/manual/declare/", self._donnees(proof=capture), format="multipart")

        self.assertEqual(reponse.status_code, 201)
        nom = ManualPayment.objects.get(pk=reponse.data["id"]).proof.name
        self.assertTrue(nom.endswith("_preuve.png"), nom)
