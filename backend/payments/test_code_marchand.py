"""
Comptes marchands Orange Money et MoMo Pay (2026-11-26) : l'élève paie un code marchand au lieu d'envoyer un
transfert à un numéro. Le compte se configure dans l'admin (code + séquence USSD recopiée du kit de l'opérateur),
l'écran de paiement le lit par /payments/manual/methods/ et la déclaration reste la même.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from catalog.models import Cursus, Examen
from subscriptions.models import Plan
from users.models import User

from .models import ManualPayment, MobileMoneyAccount, MobileMoneyOperator, sequence_ussd_validator


class ValidationCompteMarchandTests(TestCase):
    def test_un_compte_sans_numero_ni_code_est_refuse(self):
        compte = MobileMoneyAccount(operator=MobileMoneyOperator.ORANGE, account_name="EduKora")
        with self.assertRaises(ValidationError):
            compte.full_clean()

    def test_la_base_refuse_aussi_un_compte_sans_numero_ni_code(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MobileMoneyAccount.objects.create(operator=MobileMoneyOperator.ORANGE, account_name="EduKora")

    def test_un_compte_marchand_sans_numero_est_accepte(self):
        compte = MobileMoneyAccount(
            operator=MobileMoneyOperator.MTN, merchant_code="123456",
            ussd_template="*126*4*{code}*{montant}#", account_name="EduKora",
        )
        compte.full_clean()

    def test_une_sequence_sans_code_marchand_est_refusee(self):
        compte = MobileMoneyAccount(
            operator=MobileMoneyOperator.ORANGE, phone_number="699000000",
            ussd_template="#150*47*{code}*{montant}#", account_name="EduKora",
        )
        with self.assertRaises(ValidationError) as erreur:
            compte.full_clean()
        self.assertIn("ussd_template", erreur.exception.message_dict)

    def test_le_code_marchand_ne_contient_que_des_chiffres(self):
        compte = MobileMoneyAccount(operator=MobileMoneyOperator.ORANGE, merchant_code="EDU-12", account_name="EduKora")
        with self.assertRaises(ValidationError) as erreur:
            compte.full_clean()
        self.assertIn("merchant_code", erreur.exception.message_dict)

    def test_sequences_acceptees(self):
        for sequence in ["#150*47*{code}*{montant}#", "*126*4*{code}*{montant}#", "#150*47*{code}#"]:
            with self.subTest(sequence=sequence):
                sequence_ussd_validator(sequence)

    def test_sequences_refusees(self):
        # Repère inconnu (affiché tel quel à l'élève), pas de # final, lettres, début sans * ni #.
        for sequence in ["#150*47*{code}*{prix}#", "#150*47*{code}*{montant}", "#150*47*EDU#", "150*47*{code}#"]:
            with self.subTest(sequence=sequence), self.assertRaises(ValidationError):
                sequence_ussd_validator(sequence)


@override_settings(MANUAL_PAYMENT_ACTIVE=True)
class PaiementParCodeMarchandTests(TestCase):
    def setUp(self):
        cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.plan = Plan.objects.create(name="Mois", cursus=cursus, price=2000, duration_days=30)
        MobileMoneyAccount.objects.create(
            operator=MobileMoneyOperator.ORANGE, merchant_code="654321",
            ussd_template="#150*47*{code}*{montant}#", account_name="EduKora SARL",
        )
        self.user = User.objects.create_user(phone_number="677100090", password="x")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.user)}")

    def test_l_ecran_de_paiement_recoit_le_code_et_la_sequence(self):
        comptes = self.client.get("/payments/manual/methods/").json()

        self.assertEqual(comptes, [{
            "operator": "ORANGE", "operator_display": "Orange Money", "phone_number": "",
            "merchant_code": "654321", "ussd_template": "#150*47*{code}*{montant}#", "account_name": "EduKora SARL",
        }])

    def test_les_tarifs_ne_publient_pas_le_code(self):
        config = APIClient().get("/payments/config/").json()

        self.assertEqual(config["beneficiaires"], [
            {"operator": "ORANGE", "operator_display": "Orange Money", "account_name": "EduKora SARL"},
        ])

    def test_un_paiement_par_code_marchand_se_declare_comme_un_transfert(self):
        reponse = self.client.post("/payments/manual/declare/", {
            "plan": self.plan.pk, "operator": MobileMoneyOperator.ORANGE,
            "payer_phone_number": "677100090", "transaction_reference": "MP261126.1530.A12345",
        })

        self.assertEqual(reponse.status_code, 201)
        self.assertTrue(ManualPayment.objects.filter(user=self.user, operator=MobileMoneyOperator.ORANGE).exists())
