"""PIN des profils, PIN parent (mode parent) et session enfant - voir users.pin / users.parent."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from . import pin as pin_module
from .models import Profil, User


def _client_pour(user, profil=None, restreint=False):
    """Client authentifié par un VRAI token (claims `profil_id`/`restreint` incluses)."""
    refresh = RefreshToken.for_user(user)
    if profil is not None:
        refresh["profil_id"] = profil.id
    if restreint:
        refresh["restreint"] = True
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


class FamilleTestCase(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user(phone_number="677400001", password="x")
        self.aine = self.parent.profils.first()
        self.cadet = Profil.objects.create(compte=self.parent, prenom="Cadet", ordre=1)
        self.client_parent = _client_pour(self.parent, self.aine)

    def definir_pin_cadet(self, pin="1234"):
        pin_module.definir(self.cadet, pin_module.PROFIL, pin)


class PinProfilTests(FamilleTestCase):
    def test_profile_without_pin_stays_open(self):
        response = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/")

        self.assertEqual(response.status_code, 200)

    def test_pin_is_stored_hashed_and_required_to_open_the_profile(self):
        response = self.client_parent.post(f"/auth/profils/{self.cadet.id}/pin/", {"pin": "1234"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["pin_actif"])
        self.cadet.refresh_from_db()
        self.assertNotIn("1234", self.cadet.pin_hash)

        sans_pin = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/")
        self.assertEqual(sans_pin.status_code, 403)
        self.assertEqual(sans_pin.data["code"], "pin_requis")

        faux = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/", {"pin": "0000"}, format="json")
        self.assertEqual(faux.status_code, 403)
        self.assertEqual(faux.data["code"], "pin_incorrect")

        bon = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/", {"pin": "1234"}, format="json")
        self.assertEqual(bon.status_code, 200)
        self.assertEqual(bon.data["user"]["profil_actif"]["id"], self.cadet.id)

    def test_pin_must_be_four_digits(self):
        for invalide in ("123", "12345", "abcd", ""):
            response = self.client_parent.post(
                f"/auth/profils/{self.cadet.id}/pin/", {"pin": invalide}, format="json",
            )
            self.assertEqual(response.status_code, 400, invalide)

    def test_already_active_profile_is_not_asked_again(self):
        self.definir_pin_cadet()
        client_cadet = _client_pour(self.parent, self.cadet)

        response = client_cadet.post(f"/auth/profils/{self.cadet.id}/activer/")

        self.assertEqual(response.status_code, 200)

    def test_too_many_wrong_pins_lock_the_profile_even_for_the_right_pin(self):
        self.definir_pin_cadet()
        for _ in range(pin_module.MAX_ECHECS):
            self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/", {"pin": "0000"}, format="json")

        response = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/", {"pin": "1234"}, format="json")

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.data["code"], "pin_bloque")

    def test_pin_can_be_removed(self):
        self.definir_pin_cadet()

        response = self.client_parent.delete(f"/auth/profils/{self.cadet.id}/pin/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["pin_actif"])
        self.assertEqual(self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/").status_code, 200)

    def test_parent_pin_also_opens_a_child_profile(self):
        self.definir_pin_cadet()
        pin_module.definir(self.parent, pin_module.PARENT, "9999")

        response = self.client_parent.post(f"/auth/profils/{self.cadet.id}/activer/", {"pin": "9999"}, format="json")

        self.assertEqual(response.status_code, 200)


class ModeParentTests(FamilleTestCase):
    def definir_pin_parent(self, pin="4321"):
        response = self.client_parent.post("/auth/parent/pin/", {"pin": pin}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["pin_parent_actif"])

    def jeton(self, pin="4321"):
        response = self.client_parent.post("/auth/parent/verifier/", {"pin": pin}, format="json")
        self.assertEqual(response.status_code, 200)
        return response.data["jeton"]

    def test_without_parent_pin_account_actions_stay_open(self):
        response = self.client_parent.post("/auth/profils/", {"prenom": "Benjamin"}, format="json")

        self.assertEqual(response.status_code, 201)

    def test_account_actions_require_the_parent_token_once_a_pin_is_set(self):
        self.definir_pin_parent()

        sans_jeton = self.client_parent.post("/auth/profils/", {"prenom": "Benjamin"}, format="json")
        self.assertEqual(sans_jeton.status_code, 403)
        self.assertEqual(sans_jeton.data["code"], "parent_requis")

        paiement = self.client_parent.post("/payments/initiate/", {"plan_id": 1, "phone_number": "677400001"})
        self.assertEqual(paiement.status_code, 403)
        self.assertEqual(paiement.data["code"], "parent_requis")

        avec_jeton = self.client_parent.post(
            "/auth/profils/", {"prenom": "Benjamin"}, format="json", HTTP_X_PARENT_TOKEN=self.jeton(),
        )
        self.assertEqual(avec_jeton.status_code, 201)

    def test_wrong_parent_pin_gives_no_token_and_locks_after_repeated_errors(self):
        self.definir_pin_parent()
        for _ in range(pin_module.MAX_ECHECS):
            self.client_parent.post("/auth/parent/verifier/", {"pin": "0000"}, format="json")
        faux = self.client_parent.post("/auth/parent/verifier/", {"pin": "0000"}, format="json")
        self.assertEqual(faux.status_code, 429)

        bon = self.client_parent.post("/auth/parent/verifier/", {"pin": "4321"}, format="json")
        self.assertEqual(bon.status_code, 429)

    def test_parent_token_of_another_account_is_rejected(self):
        self.definir_pin_parent()
        autre = User.objects.create_user(phone_number="677400002", password="x")
        pin_module.definir(autre, pin_module.PARENT, "1111")
        jeton_autre = _client_pour(autre).post("/auth/parent/verifier/", {"pin": "1111"}, format="json").data["jeton"]

        response = self.client_parent.post(
            "/auth/profils/", {"prenom": "X"}, format="json", HTTP_X_PARENT_TOKEN=jeton_autre,
        )

        self.assertEqual(response.status_code, 403)

    def test_changing_or_removing_the_parent_pin_needs_the_current_one(self):
        self.definir_pin_parent()

        sans_actuel = self.client_parent.post("/auth/parent/pin/", {"pin": "5555"}, format="json")
        self.assertEqual(sans_actuel.status_code, 403)

        change = self.client_parent.post("/auth/parent/pin/", {"pin": "5555", "pin_actuel": "4321"}, format="json")
        self.assertEqual(change.status_code, 200)

        retire = self.client_parent.delete("/auth/parent/pin/", {"pin_actuel": "5555"}, format="json")
        self.assertEqual(retire.status_code, 200)
        self.assertFalse(retire.data["pin_parent_actif"])

    @patch("users.views.consume_otp")
    @patch("users.views.request_otp")
    def test_forgotten_parent_pin_is_reset_through_a_code(self, mock_request, mock_consume):
        self.definir_pin_parent()

        demande = self.client_parent.post("/auth/parent/reinitialiser/demander/")
        self.assertEqual(demande.status_code, 200)
        mock_request.assert_called_once()

        confirmation = self.client_parent.post("/auth/parent/reinitialiser/confirmer/", {"code": "123456"}, format="json")
        self.assertEqual(confirmation.status_code, 200)
        self.assertFalse(confirmation.data["pin_parent_actif"])


class SessionEnfantTests(FamilleTestCase):
    NUMERO_ENFANT = "+237677400099"

    def test_parent_links_a_phone_to_a_child_profile(self):
        with patch("users.views.request_otp") as mock_request, patch("users.views.consume_otp"):
            demande = self.client_parent.post(
                f"/auth/profils/{self.cadet.id}/connexion/demander/", {"phone_number": "677400099"}, format="json",
            )
            self.assertEqual(demande.status_code, 200)
            mock_request.assert_called_once()

            confirmation = self.client_parent.post(
                f"/auth/profils/{self.cadet.id}/connexion/confirmer/",
                {"phone_number": "677400099", "code": "123456"}, format="json",
            )

        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(confirmation.data["connexion_active"])
        self.cadet.refresh_from_db()
        self.assertEqual(self.cadet.connexion_phone, self.NUMERO_ENFANT)

    def test_a_number_already_used_by_an_account_cannot_be_linked(self):
        response = self.client_parent.post(
            f"/auth/profils/{self.cadet.id}/connexion/demander/", {"phone_number": "677400001"}, format="json",
        )

        self.assertEqual(response.status_code, 409)

    def test_child_logs_in_with_own_number_into_a_restricted_session(self):
        self.cadet.connexion_phone = self.NUMERO_ENFANT
        self.cadet.save(update_fields=["connexion_phone"])

        with patch("users.views.consume_otp", return_value=self.NUMERO_ENFANT):
            response = APIClient().post(
                "/auth/otp/verify/", {"phone_number": "677400099", "code": "123456"}, format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["profil_actif"]["id"], self.cadet.id)
        self.assertTrue(response.data["user"]["session_restreinte"])
        self.assertEqual(User.objects.filter(phone_number=self.NUMERO_ENFANT).count(), 0)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        me = client.get("/auth/me/")
        self.assertEqual(me.data["profil_actif"]["id"], self.cadet.id)
        self.assertTrue(me.data["session_restreinte"])

    def test_restricted_session_cannot_switch_profile_pay_or_manage_children(self):
        client = _client_pour(self.parent, self.cadet, restreint=True)

        self.assertEqual(client.post(f"/auth/profils/{self.aine.id}/activer/").status_code, 403)
        self.assertEqual(client.post("/payments/initiate/", {"plan_id": 1, "phone_number": "677400001"}).status_code, 403)
        self.assertEqual(client.post("/auth/profils/", {"prenom": "X"}, format="json").status_code, 403)
        self.assertEqual(client.post(f"/auth/profils/{self.aine.id}/pin/", {"pin": "1234"}, format="json").status_code, 403)
        self.assertEqual(client.post("/auth/parent/pin/", {"pin": "1234"}, format="json").status_code, 403)

    def test_restricted_session_survives_a_token_refresh(self):
        refresh = RefreshToken.for_user(self.parent)
        refresh["profil_id"] = self.cadet.id
        refresh["restreint"] = True
        client = APIClient()
        client.cookies["edukamer_refresh"] = str(refresh)

        response = client.post("/auth/token/refresh/")

        self.assertEqual(response.status_code, 200)
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(api.post(f"/auth/profils/{self.aine.id}/activer/").status_code, 403)

    def test_unlinking_removes_the_child_login(self):
        self.cadet.connexion_phone = self.NUMERO_ENFANT
        self.cadet.save(update_fields=["connexion_phone"])

        response = self.client_parent.delete(f"/auth/profils/{self.cadet.id}/connexion/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["connexion_active"])


class VerrouInactiviteTests(FamilleTestCase):
    def test_active_profile_pin_can_be_rechecked_on_demand(self):
        self.definir_pin_cadet()
        client_cadet = _client_pour(self.parent, self.cadet)

        sans = client_cadet.post(f"/auth/profils/{self.cadet.id}/activer/", {"reverifier": True}, format="json")
        self.assertEqual(sans.status_code, 403)
        self.assertEqual(sans.data["code"], "pin_requis")

        faux = client_cadet.post(
            f"/auth/profils/{self.cadet.id}/activer/", {"reverifier": True, "pin": "0000"}, format="json",
        )
        self.assertEqual(faux.status_code, 403)

        bon = client_cadet.post(
            f"/auth/profils/{self.cadet.id}/activer/", {"reverifier": True, "pin": "1234"}, format="json",
        )
        self.assertEqual(bon.status_code, 200)

    def test_recheck_on_a_profile_without_pin_just_succeeds(self):
        client_aine = _client_pour(self.parent, self.aine)

        response = client_aine.post(f"/auth/profils/{self.aine.id}/activer/", {"reverifier": True}, format="json")

        self.assertEqual(response.status_code, 200)
