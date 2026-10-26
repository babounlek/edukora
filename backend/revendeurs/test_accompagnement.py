"""Accompagnement : le revendeur guide le parent et avance la somme depuis son propre numéro."""
from payments.models import ManualPayment, MobileMoneyAccount, MobileMoneyOperator
from rest_framework.test import APIClient

from .models import AttributionRevendeur, Revendeur
from .services import enregistrer_commission
from .tests import _Base

NUMERO_REVENDEUR = "699111222"


class AccompagnementTests(_Base):
    def setUp(self):
        super().setUp()
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement=NUMERO_REVENDEUR)
        self.revendeur.refresh_from_db()

    def _avance(self, client, ref, payeur=NUMERO_REVENDEUR, declare=True):
        paiement = self._manuel(client, ref, payeur=payeur)
        ManualPayment.objects.filter(pk=paiement.pk).update(paye_par_revendeur=declare)
        return ManualPayment.objects.get(pk=paiement.pk)

    def test_le_numero_du_revendeur_comme_payeur_donne_une_commission_normale(self):
        commission = enregistrer_commission(self._avance(self._client(tel="677900801"), "REF-AV1"))

        self.assertIsNotNone(commission)
        self.assertEqual(commission.montant_fcfa, 2100)
        self.assertFalse(commission.a_verifier)

    def test_sans_la_declaration_le_meme_paiement_reste_un_auto_achat(self):
        paiement = self._avance(self._client(tel="677900811"), "REF-AV2", declare=False)
        self.assertIsNone(enregistrer_commission(paiement))

    def test_numero_payeur_different_du_sien_retient_la_commission(self):
        commission = enregistrer_commission(self._avance(self._client(tel="677900821"), "REF-AV3", payeur="699555000"))

        self.assertTrue(commission.a_verifier)
        self.assertIn("autre numéro", commission.motif_a_verifier)

    def test_avancer_pour_plusieurs_parents_depuis_le_meme_numero_n_est_pas_signale(self):
        derniere = None
        for i, tel in enumerate(("677900831", "677900841", "677900851", "677900861")):
            derniere = enregistrer_commission(self._avance(self._client(tel=tel), f"REF-AVM{i}"))

        self.assertFalse(derniere.a_verifier)

    def test_le_meme_schema_sans_declaration_reste_signale(self):
        # Même payeur pour quatre comptes, mais un numéro qui n'est pas celui du revendeur et pas déclaré.
        derniere = None
        for i, tel in enumerate(("677900871", "677900881", "677900891", "677900901")):
            derniere = enregistrer_commission(self._avance(self._client(tel=tel), f"REF-AVN{i}", payeur="699555333", declare=False))

        self.assertTrue(derniere.a_verifier)
        self.assertIn("même numéro", derniere.motif_a_verifier)

    def test_le_revendeur_reste_exclu_comme_client_meme_avec_la_declaration(self):
        AttributionRevendeur.objects.create(client=self.revendeur.user, revendeur=self.revendeur)
        paiement = self._avance(self.revendeur.user, "REF-AV4")
        self.assertIsNone(enregistrer_commission(paiement))


class DeclarationAPITests(_Base):
    def setUp(self):
        super().setUp()
        MobileMoneyAccount.objects.create(operator=MobileMoneyOperator.ORANGE, phone_number="699000000", account_name="Edukora")
        self.api = APIClient()

    def _declarer(self, client, ref, **extra):
        self.api.force_authenticate(client)
        return self.api.post("/payments/manual/declare/", {
            "plan": self.plan.pk, "operator": "ORANGE", "payer_phone_number": "699111222",
            "transaction_reference": ref, **extra,
        }, format="multipart")

    def test_la_declaration_est_enregistree_pour_un_client_rattache(self):
        reponse = self._declarer(self._client(tel="677900911"), "REF-D1", paye_par_revendeur=True)

        self.assertEqual(reponse.status_code, 201)
        self.assertTrue(reponse.json()["paye_par_revendeur"])
        self.assertTrue(ManualPayment.objects.get().paye_par_revendeur)

    def test_ignoree_sans_revendeur_rattache(self):
        reponse = self._declarer(self._client(tel="677900921", attribue=False), "REF-D2", paye_par_revendeur=True)

        self.assertEqual(reponse.status_code, 201)
        self.assertFalse(reponse.json()["paye_par_revendeur"])

    def test_absente_elle_vaut_faux(self):
        reponse = self._declarer(self._client(tel="677900931"), "REF-D3")

        self.assertEqual(reponse.status_code, 201)
        self.assertFalse(reponse.json()["paye_par_revendeur"])
