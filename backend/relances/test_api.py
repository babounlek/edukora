"""Endpoint de reprise de paiement (bannière de l'application)."""

from datetime import timedelta

from rest_framework.test import APIClient

from payments.models import StatutTransaction

from .tests import RelancesTestCase


class PaiementAReprendreApiTests(RelancesTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_reserve_aux_eleves_connectes(self):
        self.assertIn(self.client.get("/relances/paiement-a-reprendre/").status_code, (401, 403))

    def test_rien_a_reprendre_sans_tentative(self):
        self.client.force_authenticate(user=self.eleve(abonne=False))
        self.assertEqual(self.client.get("/relances/paiement-a-reprendre/").data, {"a_reprendre": False})

    def test_une_tentative_echouee_est_proposee_a_la_reprise(self):
        user = self.eleve(abonne=False)
        self.transaction(user, StatutTransaction.FAILED, timedelta(hours=1))
        self.client.force_authenticate(user=user)

        data = self.client.get("/relances/paiement-a-reprendre/").data

        self.assertTrue(data["a_reprendre"])
        self.assertEqual(data["montant"], 5000)
        self.assertEqual(data["cursus_id"], self.plan.cursus_id)

    def test_plus_rien_a_reprendre_une_fois_abonne(self):
        user = self.eleve(abonne=True)
        self.transaction(user, StatutTransaction.FAILED, timedelta(hours=1))
        self.client.force_authenticate(user=user)
        self.assertFalse(self.client.get("/relances/paiement-a-reprendre/").data["a_reprendre"])
