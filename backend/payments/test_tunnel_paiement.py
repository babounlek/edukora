"""
Ce que le payeur vit quand le paiement automatique sort du chemin nominal (audit du tunnel de paiement,
2026-11-26) : une erreur de l'agrégateur dite en clair, une demande jamais doublée sans qu'il le sache,
une attente qui se reprend, un paiement confirmé qui se retrouve dans « Mes paiements ».
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from subscriptions.models import Plan
from users.models import User

from . import campay_client
from .campay_client import CampayError
from .models import StatutTransaction, Transaction
from .tests import _make_cursus


class _Base(TestCase):
    def setUp(self):
        self.cursus = _make_cursus()
        self.user = User.objects.create_user(phone_number="677000050", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _payer(self, **en_plus):
        return self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": "677000050", **en_plus}, format="json",
        )


class ErreursDitesAuPayeurTests(_Base):
    @patch("payments.campay_client.init_collect")
    def test_une_panne_de_l_agregateur_ne_montre_jamais_son_detail_technique(self, mock_init):
        mock_init.side_effect = CampayError('Échec d\'authentification CamPay : {"non_field_errors":["Unable to log in"]}')

        response = self._payer()

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["code"], "paiement_indisponible")
        self.assertNotIn("CamPay", response.data["error"])
        self.assertNotIn("non_field_errors", response.data["error"])

    @patch("payments.campay_client.init_collect")
    def test_un_numero_refuse_est_dit_comme_tel(self, mock_init):
        mock_init.side_effect = CampayError("Demande refusée (400) : Invalid phone number", code="numero_refuse")

        response = self._payer()

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["code"], "numero_refuse")
        self.assertIn("Orange ou MTN", response.data["error"])
        self.assertNotIn("Invalid phone number", response.data["error"])

    def test_un_numero_mal_forme_est_refuse_avant_tout_appel(self):
        with patch("payments.campay_client.init_collect") as mock_init:
            response = self.client.post(
                "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": "12"}, format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "numero_invalide")
        mock_init.assert_not_called()
        self.assertFalse(Transaction.objects.exists())

    @patch("payments.campay_client.init_collect")
    def test_le_numero_est_ramene_a_neuf_chiffres_meme_saisi_avec_l_indicatif(self, mock_init):
        mock_init.return_value = {"reference": "ref-1"}

        response = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": "+237 677 00 00 50"}, format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.get().phone_number, "677000050")

    @patch("payments.campay_client.get_transaction_status")
    def test_un_statut_illisible_ne_montre_pas_le_detail_technique(self, mock_status):
        mock_status.side_effect = CampayError("CamPay est injoignable (HTTPSConnectionPool...)")
        transaction = Transaction.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan, amount=2000,
            phone_number="677000050", provider_reference="ref-1",
        )

        response = self.client.get(f"/payments/status/{transaction.id}/")

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("HTTPSConnectionPool", response.data["error"])


class OperateurEtAttenteTests(_Base):
    @patch("payments.campay_client.init_collect")
    def test_la_reponse_dit_l_operateur_reconnu_pour_le_numero(self, mock_init):
        mock_init.return_value = {"reference": "ref-1", "operator": "mtn", "ussd_code": "*126#"}

        response = self._payer()

        self.assertEqual(response.data["operator"], "MTN")
        self.assertEqual(response.data["phone_number"], "677000050")

    @patch("payments.campay_client.init_collect")
    def test_un_operateur_inconnu_reste_vide(self, mock_init):
        mock_init.return_value = {"reference": "ref-1", "operator": "mtn or orange"}

        self.assertEqual(self._payer().data["operator"], "")

    @patch("payments.campay_client.init_collect")
    def test_la_demande_en_cours_se_retrouve_pour_reprendre_l_attente(self, mock_init):
        mock_init.return_value = {"reference": "ref-1", "operator": "ORANGE"}
        self.assertEqual(self.client.get("/payments/en-cours/").data, {"en_cours": False})

        transaction_id = self._payer().data["transaction_id"]

        en_cours = self.client.get(f"/payments/en-cours/?cursus={self.cursus.id}").data
        self.assertTrue(en_cours["en_cours"])
        self.assertEqual(en_cours["transaction_id"], transaction_id)
        self.assertEqual(en_cours["operator"], "ORANGE")
        self.assertEqual(en_cours["amount"], 2000)

    @patch("payments.campay_client.init_collect")
    def test_une_demande_de_plus_de_dix_minutes_n_est_plus_reprise(self, mock_init):
        mock_init.return_value = {"reference": "ref-1"}
        transaction_id = self._payer().data["transaction_id"]
        Transaction.objects.filter(pk=transaction_id).update(created_at=timezone.now() - timedelta(minutes=11))

        self.assertEqual(self.client.get("/payments/en-cours/").data, {"en_cours": False})

    @patch("payments.campay_client.init_collect")
    def test_la_demande_d_un_autre_compte_n_est_jamais_rendue(self, mock_init):
        mock_init.return_value = {"reference": "ref-1"}
        self._payer()
        autre = APIClient()
        autre.force_authenticate(user=User.objects.create_user(phone_number="677000051", password="x"))

        self.assertEqual(autre.get("/payments/en-cours/").data, {"en_cours": False})


class JamaisDeuxDemandesSansLeDireTests(_Base):
    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_reessayer_rend_la_demande_encore_en_attente_au_lieu_d_en_envoyer_une_deuxieme(self, mock_init, mock_status):
        mock_init.return_value = {"reference": "ref-1"}
        mock_status.return_value = {"status": "PENDING", "reference": "ref-1", "operator": "MTN"}
        premiere = self._payer().data

        seconde = self._payer().data

        self.assertEqual(seconde["transaction_id"], premiere["transaction_id"])
        self.assertTrue(seconde["deja_en_attente"])
        self.assertEqual(mock_init.call_count, 1)
        self.assertEqual(Transaction.objects.count(), 1)

    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_reessayer_apres_une_validation_tardive_ouvre_l_acces_sans_second_paiement(self, mock_init, mock_status):
        mock_init.return_value = {"reference": "ref-1"}
        mock_status.return_value = {"status": "SUCCESSFUL", "reference": "ref-1"}
        self._payer()

        seconde = self._payer().data

        self.assertEqual(seconde["status"], StatutTransaction.SUCCESSFUL)
        self.assertEqual(mock_init.call_count, 1)
        self.assertTrue(Transaction.objects.get().subscription.is_active)

    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_une_demande_echouee_laisse_en_envoyer_une_neuve(self, mock_init, mock_status):
        mock_init.side_effect = [{"reference": "ref-1"}, {"reference": "ref-2"}]
        mock_status.return_value = {"status": "FAILED", "reference": "ref-1"}
        premiere = self._payer().data

        seconde = self._payer().data

        self.assertNotEqual(seconde["transaction_id"], premiere["transaction_id"])
        self.assertNotIn("deja_en_attente", seconde)
        self.assertEqual(mock_init.call_count, 2)

    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_le_payeur_peut_demander_lui_meme_une_demande_neuve(self, mock_init, mock_status):
        mock_init.side_effect = [{"reference": "ref-1"}, {"reference": "ref-2"}]
        mock_status.return_value = {"status": "PENDING", "reference": "ref-1"}
        premiere = self._payer().data

        seconde = self._payer(nouvelle_demande=True).data

        self.assertNotEqual(seconde["transaction_id"], premiere["transaction_id"])
        self.assertEqual(mock_init.call_count, 2)
        mock_status.assert_not_called()

    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_un_autre_numero_n_est_pas_la_meme_demande(self, mock_init, mock_status):
        mock_init.side_effect = [{"reference": "ref-1"}, {"reference": "ref-2"}]
        self._payer()

        seconde = self.client.post(
            "/payments/initiate/", {"plan_id": self.plan.id, "phone_number": "699000001"}, format="json",
        ).data

        self.assertNotIn("deja_en_attente", seconde)
        self.assertEqual(Transaction.objects.count(), 2)
        mock_status.assert_not_called()

    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_un_statut_illisible_ne_fait_pas_doubler_la_demande(self, mock_init, mock_status):
        mock_init.return_value = {"reference": "ref-1"}
        mock_status.side_effect = CampayError("CamPay injoignable")
        self._payer()

        seconde = self._payer().data

        self.assertTrue(seconde["deja_en_attente"])
        self.assertEqual(mock_init.call_count, 1)


class MesPaiementsConfirmesTests(_Base):
    @patch("payments.models._prevenir_du_paiement")
    @patch("payments.campay_client.get_transaction_status")
    @patch("payments.campay_client.init_collect")
    def test_un_paiement_confirme_apparait_avec_son_recu(self, mock_init, mock_status, _mock_sms):
        mock_init.return_value = {"reference": "ref-1"}
        mock_status.return_value = {
            "status": "SUCCESSFUL", "reference": "ref-1", "operator": "MTN", "code": "CP201027T00005",
        }
        transaction_id = self._payer().data["transaction_id"]
        self.assertEqual(self.client.get("/payments/mine/").data, [])

        self.client.get(f"/payments/status/{transaction_id}/")

        paiements = self.client.get("/payments/mine/").data
        self.assertEqual(len(paiements), 1)
        self.assertEqual(paiements[0]["amount"], 2000)
        self.assertEqual(paiements[0]["operator"], "MTN")
        self.assertEqual(paiements[0]["reference"], "CP201027T00005")

    @patch("payments.campay_client.init_collect")
    def test_ni_les_demandes_en_attente_ni_celles_des_autres_n_y_figurent(self, mock_init):
        mock_init.return_value = {"reference": "ref-1"}
        self._payer()
        autre = User.objects.create_user(phone_number="677000052", password="x")
        Transaction.objects.create(
            user=autre, profil=autre.profils.first(), plan=self.plan, amount=2000, phone_number="677000052",
            status=StatutTransaction.SUCCESSFUL,
        )

        self.assertEqual(self.client.get("/payments/mine/").data, [])


def _reponse(status_code, corps):
    reponse = MagicMock()
    reponse.status_code = status_code
    reponse.json.return_value = corps
    reponse.text = str(corps)
    return reponse


class ClientCampayTests(TestCase):
    """Le client HTTP lui-même, `requests` simulé : jeton gardé, refus traduits, réponse sans référence."""

    def setUp(self):
        campay_client.oublier_jeton()
        self.addCleanup(campay_client.oublier_jeton)

    @patch("payments.campay_client.config", return_value="x")
    @patch("payments.campay_client.requests.request")
    def test_le_jeton_n_est_demande_qu_une_fois_pour_plusieurs_lectures(self, mock_request, _config):
        mock_request.side_effect = [
            _reponse(200, {"token": "jeton-1"}),
            _reponse(200, {"status": "PENDING"}),
            _reponse(200, {"status": "PENDING"}),
        ]

        campay_client.get_transaction_status("ref-1")
        campay_client.get_transaction_status("ref-1")

        urls = [appel.args[1] for appel in mock_request.call_args_list]
        self.assertEqual(sum(url.endswith("/api/token/") for url in urls), 1)
        self.assertEqual(len(urls), 3)

    @patch("payments.campay_client.config", return_value="x")
    @patch("payments.campay_client.requests.request")
    def test_un_jeton_refuse_est_redemande_une_fois(self, mock_request, _config):
        mock_request.side_effect = [
            _reponse(200, {"token": "jeton-perime"}),
            _reponse(401, {"detail": "Invalid token"}),
            _reponse(200, {"token": "jeton-neuf"}),
            _reponse(200, {"status": "SUCCESSFUL"}),
        ]

        self.assertEqual(campay_client.get_transaction_status("ref-1"), {"status": "SUCCESSFUL"})
        self.assertEqual(mock_request.call_args_list[-1].kwargs["headers"], {"Authorization": "Token jeton-neuf"})

    @patch("payments.campay_client.config", return_value="x")
    @patch("payments.campay_client.requests.request")
    def test_une_demande_refusee_pour_le_numero_porte_le_code_numero_refuse(self, mock_request, _config):
        mock_request.side_effect = [
            _reponse(200, {"token": "jeton-1"}),
            _reponse(400, {"message": "Invalid phone number"}),
        ]

        with self.assertRaises(CampayError) as contexte:
            campay_client.init_collect(2000, "677000050", "Abonnement", "ref-interne")

        self.assertEqual(contexte.exception.code, "numero_refuse")

    @patch("payments.campay_client.config", return_value="x")
    @patch("payments.campay_client.requests.request")
    def test_une_panne_garde_le_code_par_defaut(self, mock_request, _config):
        mock_request.side_effect = [_reponse(400, {"non_field_errors": ["Unable to log in"]})]

        with self.assertRaises(CampayError) as contexte:
            campay_client.init_collect(2000, "677000050", "Abonnement", "ref-interne")

        self.assertEqual(contexte.exception.code, "paiement_indisponible")

    @patch("payments.campay_client.config", return_value="x")
    @patch("payments.campay_client.requests.request")
    def test_une_reponse_sans_reference_est_une_erreur(self, mock_request, _config):
        mock_request.side_effect = [_reponse(200, {"token": "jeton-1"}), _reponse(200, {"operator": "MTN"})]

        with self.assertRaises(CampayError):
            campay_client.init_collect(2000, "677000050", "Abonnement", "ref-interne")
