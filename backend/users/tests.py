"""
Couvre le risque principal du module : OTP = seule porte d'authentification (pas de
mot de passe côté utilisateur final). Un code rejouable, un brute-force sans limite,
ou un parrainage attribué après coup à un compte existant sont chacun une faille
d'authentification ou d'intégrité, pas un simple bug fonctionnel.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import OTPCode, User
from .otp_service import (
    OTP_MAX_ATTEMPTS,
    OTP_MIN_INTERVAL_SECONDS,
    OTPInvalid,
    OTPThrottled,
    request_otp,
    verify_otp,
)


class RequestOTPTests(TestCase):
    @patch("users.otp_service.get_sms_backend")
    def test_creates_otp_code_and_sends_sms(self, mock_get_backend):
        request_otp("677200001")

        otp = OTPCode.objects.get(phone_number="677200001")
        self.assertFalse(otp.is_used)
        self.assertEqual(otp.attempts, 0)
        mock_get_backend.return_value.send.assert_called_once()

    @patch("users.otp_service.get_sms_backend")
    def test_throttles_repeated_requests_within_interval(self, mock_get_backend):
        request_otp("677200002")
        with self.assertRaises(OTPThrottled):
            request_otp("677200002")

        self.assertEqual(OTPCode.objects.filter(phone_number="677200002").count(), 1)

    @patch("users.otp_service.get_sms_backend")
    def test_allows_new_request_once_interval_has_elapsed(self, mock_get_backend):
        request_otp("677200003")
        OTPCode.objects.filter(phone_number="677200003").update(
            created_at=timezone.now() - timedelta(seconds=OTP_MIN_INTERVAL_SECONDS + 1),
        )

        request_otp("677200003")  # ne doit pas lever OTPThrottled

        self.assertEqual(OTPCode.objects.filter(phone_number="677200003").count(), 2)


class VerifyOTPTests(TestCase):
    def _create_otp(self, phone_number, code="123456", **overrides):
        defaults = {"phone_number": phone_number, "code": code, "expires_at": timezone.now() + timedelta(minutes=5)}
        defaults.update(overrides)
        return OTPCode.objects.create(**defaults)

    def test_valid_code_creates_new_user(self):
        self._create_otp("677200010", code="111111")

        user = verify_otp("677200010", "111111")

        self.assertEqual(user.phone_number, "677200010")
        self.assertTrue(User.objects.filter(phone_number="677200010").exists())

    def test_valid_code_marks_otp_used_and_rejects_replay(self):
        """Un code déjà consommé ne doit jamais pouvoir être rejoué, même correct."""
        self._create_otp("677200011", code="222222")
        verify_otp("677200011", "222222")

        with self.assertRaises(OTPInvalid):
            verify_otp("677200011", "222222")

    def test_wrong_code_raises_and_increments_attempts(self):
        otp = self._create_otp("677200012", code="333333")

        with self.assertRaises(OTPInvalid):
            verify_otp("677200012", "000000")

        otp.refresh_from_db()
        self.assertEqual(otp.attempts, 1)
        self.assertFalse(otp.is_used)

    def test_max_attempts_locks_out_even_with_correct_code(self):
        """Le garde-fou anti brute-force doit bloquer avant même de comparer le code."""
        otp = self._create_otp("677200013", code="444444")
        OTPCode.objects.filter(pk=otp.pk).update(attempts=OTP_MAX_ATTEMPTS)

        with self.assertRaises(OTPInvalid):
            verify_otp("677200013", "444444")

    def test_expired_code_rejected(self):
        self._create_otp("677200014", code="555555", expires_at=timezone.now() - timedelta(seconds=1))

        with self.assertRaises(OTPInvalid):
            verify_otp("677200014", "555555")

    def test_no_otp_at_all_rejected(self):
        with self.assertRaises(OTPInvalid):
            verify_otp("677299999", "123456")

    def test_referral_code_applied_only_on_first_account_creation(self):
        parrain = User.objects.create_user(phone_number="677200015", password="x")
        self._create_otp("677200016", code="666666")

        filleul = verify_otp("677200016", "666666", referral_code=parrain.referral_code)

        self.assertEqual(filleul.referred_by, parrain)

    def test_referral_code_ignored_on_existing_user_relogin(self):
        """Un compte déjà créé ne doit jamais se voir attribuer un parrain après coup."""
        parrain = User.objects.create_user(phone_number="677200017", password="x")
        existing_user = User.objects.create_user(phone_number="677200018", password="x")
        self._create_otp("677200018", code="777777")

        verify_otp("677200018", "777777", referral_code=parrain.referral_code)

        existing_user.refresh_from_db()
        self.assertIsNone(existing_user.referred_by)

    def test_unknown_referral_code_silently_ignored(self):
        self._create_otp("677200019", code="888888")

        user = verify_otp("677200019", "888888", referral_code="ZZZZZZ")

        self.assertIsNone(user.referred_by)


class OTPFlowAPITests(TestCase):
    """Parcours complet côté API : demande -> vérification -> JWT -> endpoint authentifié."""

    def setUp(self):
        self.client = APIClient()

    @patch("users.otp_service.get_sms_backend")
    def test_full_signup_and_authentication_flow(self, mock_get_backend):
        response = self.client.post("/auth/otp/request/", {"phone_number": "677200020"})
        self.assertEqual(response.status_code, 200)

        otp = OTPCode.objects.get(phone_number="677200020")
        response = self.client.post("/auth/otp/verify/", {"phone_number": "677200020", "code": otp.code})

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        access_token = response.data["access"]
        me_response = self.client.get("/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["phone_number"], "677200020")

    def test_request_rejects_invalid_phone_format(self):
        response = self.client.post("/auth/otp/request/", {"phone_number": "12345"})
        self.assertEqual(response.status_code, 400)

    @patch("users.otp_service.get_sms_backend")
    def test_request_throttled_returns_429(self, mock_get_backend):
        self.client.post("/auth/otp/request/", {"phone_number": "677200021"})
        response = self.client.post("/auth/otp/request/", {"phone_number": "677200021"})
        self.assertEqual(response.status_code, 429)

    def test_verify_rejects_wrong_code(self):
        OTPCode.objects.create(
            phone_number="677200022", code="123456", expires_at=timezone.now() + timedelta(minutes=5),
        )

        response = self.client.post("/auth/otp/verify/", {"phone_number": "677200022", "code": "999999"})

        self.assertEqual(response.status_code, 400)

    def test_me_requires_authentication(self):
        response = self.client.get("/auth/me/")
        self.assertIn(response.status_code, (401, 403))
