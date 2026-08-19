"""
Couvre le risque principal du module : OTP = seule porte d'authentification (pas de
mot de passe côté utilisateur final). Un code rejouable, un brute-force sans limite,
ou un parrainage attribué après coup à un compte existant sont chacun une faille
d'authentification ou d'intégrité, pas un simple bug fonctionnel.
"""

import time
from datetime import timedelta
from types import SimpleNamespace
from io import StringIO
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core import mail
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .management.commands.purge_otp_codes import MIN_RETENTION_DAYS
from .models import AuthIdentity, AuthProvider, CodeCanal, OTPCode, User
from .email_service import (
    EmailAlreadyTaken,
    EmailCapReached,
    EmailInvalid,
    EmailSendFailed,
    EmailThrottled,
    request_email_code,
    verify_email_code,
)
from .google import GoogleAuthError, GoogleNotConfigured, verify_google_id_token
from .phone import to_e164, to_msisdn
from .otp_service import (
    OTP_MAX_ATTEMPTS,
    OTP_MIN_INTERVAL_SECONDS,
    OTPCapReached,
    OTPInvalid,
    OTPThrottled,
    request_otp,
    verify_otp,
)
from .views import REFRESH_COOKIE_NAME, _client_ip


class RequestOTPTests(TestCase):
    @patch("users.otp_service.get_sms_backend")
    def test_creates_otp_code_and_sends_sms(self, mock_get_backend):
        request_otp("677200001")

        otp = OTPCode.objects.get(destination="+237677200001")
        self.assertFalse(otp.is_used)
        self.assertEqual(otp.attempts, 0)
        mock_get_backend.return_value.send.assert_called_once()

    @patch("users.otp_service.get_sms_backend")
    def test_throttles_repeated_requests_within_interval(self, mock_get_backend):
        request_otp("677200002")
        with self.assertRaises(OTPThrottled):
            request_otp("677200002")

        self.assertEqual(OTPCode.objects.filter(destination="+237677200002").count(), 1)

    @patch("users.otp_service.get_sms_backend")
    def test_allows_new_request_once_interval_has_elapsed(self, mock_get_backend):
        request_otp("677200003")
        OTPCode.objects.filter(destination="+237677200003").update(
            created_at=timezone.now() - timedelta(seconds=OTP_MIN_INTERVAL_SECONDS + 1),
        )

        request_otp("677200003")  # ne doit pas lever OTPThrottled

        self.assertEqual(OTPCode.objects.filter(destination="+237677200003").count(), 2)


class VerifyOTPTests(TestCase):
    def _create_otp(self, phone_number, code="123456", **overrides):
        # Normalisé comme le ferait request_otp : ces tests court-circuitent l'envoi
        # du SMS mais doivent écrire la ligne au format réellement stocké, sans quoi
        # ils valideraient un chemin qui n'existe pas en production.
        defaults = {
            "destination": to_e164(phone_number),
            "code": code,
            "expires_at": timezone.now() + timedelta(minutes=5),
        }
        defaults.update(overrides)
        return OTPCode.objects.create(**defaults)

    def test_valid_code_creates_new_user(self):
        self._create_otp("677200010", code="111111")

        user = verify_otp("677200010", "111111")

        # Saisi au format local, stocké en E.164 : c'est tout l'objet de la
        # normalisation, et le seul format qui existe désormais en base.
        self.assertEqual(user.phone_number, "+237677200010")
        self.assertTrue(User.objects.filter(phone_number="+237677200010").exists())

    def test_local_and_international_input_reach_the_same_account(self):
        """
        Le compte est la personne, pas la façon dont elle a tapé son numéro : les deux
        saisies doivent ouvrir le même compte, jamais en créer un second.
        """
        self._create_otp("677200050", code="121212")
        premier = verify_otp("677200050", "121212")

        self._create_otp("+237677200050", code="343434")
        second = verify_otp("+237677200050", "343434")

        self.assertEqual(premier.pk, second.pk)
        self.assertEqual(User.objects.filter(phone_number="+237677200050").count(), 1)

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

        otp = OTPCode.objects.get(destination="+237677200020")
        response = self.client.post("/auth/otp/verify/", {"phone_number": "677200020", "code": otp.code})

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        # Le refresh token voyage en cookie httpOnly, jamais en JSON - voir
        # users.views._set_refresh_cookie.
        self.assertIn(REFRESH_COOKIE_NAME, response.cookies)
        self.assertTrue(response.cookies[REFRESH_COOKIE_NAME]["httponly"])

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
            destination="677200022", code="123456", expires_at=timezone.now() + timedelta(minutes=5),
        )

        response = self.client.post("/auth/otp/verify/", {"phone_number": "677200022", "code": "999999"})

        self.assertEqual(response.status_code, 400)

    def test_me_requires_authentication(self):
        response = self.client.get("/auth/me/")
        self.assertIn(response.status_code, (401, 403))


class MeUpdateAPITests(TestCase):
    """PATCH /auth/me/ : seul point d'entrée qui permet à un utilisateur de renseigner
    lui-même full_name/pseudo (les deux ne sont jamais fixés à l'inscription, voir
    otp_service.verify_otp)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677200040", password="x")
        access = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_updates_full_name_and_pseudo(self):
        response = self.client.patch("/auth/me/", {"full_name": "Awa Ndiaye", "pseudo": "awa_237"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Awa Ndiaye")
        self.assertEqual(response.data["pseudo"], "awa_237")
        self.user.refresh_from_db()
        self.assertEqual(self.user.pseudo, "awa_237")

    def test_partial_update_leaves_other_field_untouched(self):
        self.user.full_name = "Nom initial"
        self.user.save(update_fields=["full_name"])

        response = self.client.patch("/auth/me/", {"pseudo": "solo_field"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Nom initial")

    def test_rejects_pseudo_with_invalid_characters(self):
        response = self.client.patch("/auth/me/", {"pseudo": "a b!"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_rejects_pseudo_already_taken_by_another_user(self):
        User.objects.create_user(phone_number="677200041", password="x", pseudo="deja_pris")

        response = self.client.patch("/auth/me/", {"pseudo": "deja_pris"})

        self.assertEqual(response.status_code, 400)

    def test_clearing_pseudo_with_empty_string_stores_null_not_empty_string(self):
        """Une chaîne vide en base romprait l'unicité au deuxième utilisateur qui
        efface aussi son pseudo - voir UserProfileUpdateSerializer.validate_pseudo."""
        self.user.pseudo = "avant"
        self.user.save(update_fields=["pseudo"])

        response = self.client.patch("/auth/me/", {"pseudo": ""})

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.pseudo)

    def test_two_users_can_both_clear_their_pseudo(self):
        other = User.objects.create_user(phone_number="677200042", password="x")
        self.client.patch("/auth/me/", {"pseudo": ""})

        other_access = RefreshToken.for_user(other).access_token
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_access}")
        response = other_client.patch("/auth/me/", {"pseudo": ""})

        self.assertEqual(response.status_code, 200)

    def test_requires_authentication(self):
        response = APIClient().patch("/auth/me/", {"pseudo": "anonyme"})
        self.assertIn(response.status_code, (401, 403))


class TokenRefreshCookieTests(TestCase):
    """token_refresh_view lit le refresh token depuis le cookie httpOnly, jamais
    depuis le corps de la requête - voir users.views."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677200030", password="x")

    def test_valid_refresh_cookie_returns_new_access_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post("/auth/token/refresh/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_missing_cookie_returns_401(self):
        response = self.client.post("/auth/token/refresh/")
        self.assertEqual(response.status_code, 401)

    def test_garbage_cookie_returns_401_rather_than_500(self):
        """Un cookie corrompu/expiré doit être traité comme une session absente, pas
        planter le endpoint - voir le except TokenError de token_refresh_view."""
        self.client.cookies[REFRESH_COOKIE_NAME] = "pas-un-vrai-jeton"

        response = self.client.post("/auth/token/refresh/")

        self.assertEqual(response.status_code, 401)

    # Pas de test "avec un Authorization: Bearer expiré/invalide en plus du cookie" :
    # DRF authentifie la requête (JWTAuthentication, DEFAULT_AUTHENTICATION_CLASSES)
    # avant même de regarder AllowAny - un Bearer mal formé y échoue toujours en 401,
    # peu importe la vue. Non pertinent ici de toute façon : le frontend n'envoie
    # jamais d'en-tête Authorization sur cet appel (voir api/client.ts,
    # refreshAccessToken), seulement le cookie - déjà couvert par le test ci-dessus.


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_logout_clears_refresh_cookie(self):
        self.client.cookies[REFRESH_COOKIE_NAME] = "peu-importe-la-valeur"

        response = self.client.post("/auth/logout/")

        self.assertEqual(response.status_code, 200)
        # delete_cookie() fixe un cookie déjà expiré (valeur vide, max-age=0) dans la
        # réponse - c'est ce qui indique au navigateur de le supprimer immédiatement.
        self.assertEqual(response.cookies[REFRESH_COOKIE_NAME].value, "")
        self.assertEqual(response.cookies[REFRESH_COOKIE_NAME]["max-age"], 0)

    def test_logout_succeeds_even_without_a_cookie(self):
        response = self.client.post("/auth/logout/")
        self.assertEqual(response.status_code, 200)


@patch("users.otp_service.get_sms_backend")
class OTPSpendingCapsTests(TestCase):
    """
    Les deux plafonds ajoutés au-dessus du throttle par numéro (voir
    users.otp_service.request_otp). L'enjeu n'est pas la même chose que le reste du
    module : ici chaque envoi qui passe est un SMS facturé, donc un garde-fou absent
    est une perte d'argent directe, pas seulement une faille d'authentification.

    Chaque appel utilise un numéro différent : le throttle par numéro (60 s) masquerait
    sinon le plafond qu'on cherche à tester.
    """

    def _request_many(self, count, ip_address, first=677300000):
        for i in range(count):
            request_otp(f"{first + i}", ip_address=ip_address)

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=3)
    def test_blocks_once_ip_hourly_cap_is_reached(self, mock_get_backend):
        self._request_many(3, ip_address="41.202.1.1")

        with self.assertRaises(OTPThrottled):
            request_otp("677399999", ip_address="41.202.1.1")

        self.assertEqual(OTPCode.objects.count(), 3)
        self.assertEqual(mock_get_backend.return_value.send.call_count, 3)

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=3)
    def test_rotating_phone_numbers_does_not_defeat_the_ip_cap(self, mock_get_backend):
        """Le scénario d'attaque exact : le throttle par numéro seul ne coûte rien à contourner."""
        with self.assertRaises(OTPThrottled):
            self._request_many(10, ip_address="41.202.1.2")

        self.assertEqual(OTPCode.objects.count(), 3)

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=3)
    def test_ip_cap_only_counts_the_last_hour(self, mock_get_backend):
        self._request_many(3, ip_address="41.202.1.3")
        OTPCode.objects.all().update(created_at=timezone.now() - timedelta(hours=1, minutes=1))

        request_otp("677399998", ip_address="41.202.1.3")  # ne doit pas lever

        self.assertEqual(OTPCode.objects.count(), 4)

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=3)
    def test_ip_cap_is_per_ip_not_global(self, mock_get_backend):
        self._request_many(3, ip_address="41.202.1.4")

        request_otp("677399997", ip_address="41.202.1.5")  # autre source, ne doit pas lever

        self.assertEqual(OTPCode.objects.filter(ip_address="41.202.1.5").count(), 1)

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=1)
    def test_unknown_ip_skips_the_ip_cap_rather_than_blocking(self, mock_get_backend):
        """Ne pas savoir d'où vient la demande ne doit jamais refuser un utilisateur légitime."""
        self._request_many(5, ip_address=None)

        self.assertEqual(OTPCode.objects.count(), 5)
        self.assertIsNone(OTPCode.objects.first().ip_address)

    @override_settings(OTP_DAILY_GLOBAL_CAP=3, OTP_MAX_PER_IP_PER_HOUR=1000)
    def test_global_cap_blocks_even_across_many_distinct_ips(self, mock_get_backend):
        """Cas botnet : le plafond par IP ne mord jamais, seul le plafond global borne la facture."""
        for i in range(3):
            request_otp(f"67740000{i}", ip_address=f"41.202.2.{i}")

        with self.assertRaises(OTPCapReached):
            request_otp("677499999", ip_address="41.202.3.99")

        self.assertEqual(OTPCode.objects.count(), 3)
        self.assertEqual(mock_get_backend.return_value.send.call_count, 3)

    @override_settings(OTP_DAILY_GLOBAL_CAP=3)
    def test_global_cap_only_counts_the_last_24h(self, mock_get_backend):
        self._request_many(3, ip_address=None)
        OTPCode.objects.all().update(created_at=timezone.now() - timedelta(hours=24, minutes=1))

        request_otp("677499998", ip_address=None)  # ne doit pas lever

        self.assertEqual(OTPCode.objects.count(), 4)

    def test_records_the_requesting_ip(self, mock_get_backend):
        request_otp("677400010", ip_address="41.202.9.9")
        self.assertEqual(OTPCode.objects.get(destination="+237677400010").ip_address, "41.202.9.9")


class ClientIPTests(TestCase):
    """
    users.views._client_ip. Une erreur ici ne se voit pas : elle rend simplement le
    plafond par IP inopérant (toutes les demandes attribuées à la même adresse, ou à
    aucune) sans qu'aucun test fonctionnel ne casse.
    """

    def _request(self, **meta):
        request = type("FakeRequest", (), {})()
        request.META = meta
        return request

    def test_uses_the_rightmost_forwarded_entry_added_by_caddy(self):
        # Valeur falsifiée par le client à gauche, IP réelle ajoutée par Caddy à droite.
        request = self._request(
            HTTP_X_FORWARDED_FOR="1.2.3.4, 41.202.5.5", REMOTE_ADDR="172.18.0.3",
        )
        self.assertEqual(_client_ip(request), "41.202.5.5")

    def test_falls_back_to_remote_addr_without_proxy_header(self):
        self.assertEqual(_client_ip(self._request(REMOTE_ADDR="41.202.6.6")), "41.202.6.6")

    def test_supports_ipv6(self):
        self.assertEqual(_client_ip(self._request(REMOTE_ADDR="2001:db8::1")), "2001:db8::1")

    def test_malformed_header_yields_none_rather_than_an_unusable_value(self):
        # GenericIPAddressField = type `inet` côté PostgreSQL : une chaîne arbitraire
        # écrite telle quelle ferait échouer l'INSERT, donc une 500 déclenchable par
        # un simple en-tête.
        self.assertIsNone(_client_ip(self._request(HTTP_X_FORWARDED_FOR="pas-une-ip")))

    def test_no_information_at_all_yields_none(self):
        self.assertIsNone(_client_ip(self._request()))


class OTPCapsAPITests(TestCase):
    """Les deux plafonds n'ont pas le même sens côté client, donc pas le même code HTTP."""

    def setUp(self):
        self.client = APIClient()

    @override_settings(OTP_MAX_PER_IP_PER_HOUR=1)
    @patch("users.otp_service.get_sms_backend")
    def test_ip_cap_returns_429(self, mock_get_backend):
        self.client.post("/auth/otp/request/", {"phone_number": "677500001"}, REMOTE_ADDR="41.202.7.7")
        response = self.client.post(
            "/auth/otp/request/", {"phone_number": "677500002"}, REMOTE_ADDR="41.202.7.7",
        )

        self.assertEqual(response.status_code, 429)

    @override_settings(OTP_DAILY_GLOBAL_CAP=1)
    @patch("users.otp_service.get_sms_backend")
    def test_global_cap_returns_503_not_429(self, mock_get_backend):
        self.client.post("/auth/otp/request/", {"phone_number": "677500003"}, REMOTE_ADDR="41.202.8.1")
        response = self.client.post(
            "/auth/otp/request/", {"phone_number": "677500004"}, REMOTE_ADDR="41.202.8.2",
        )

        # 429 dirait à ce demandeur, qui n'a fait qu'une seule tentative, de ralentir.
        self.assertEqual(response.status_code, 503)
        self.assertEqual(OTPCode.objects.count(), 1)


class PurgeOTPCodesCommandTests(TestCase):
    """
    users.management.commands.purge_otp_codes. La table n'était jamais vidée : numéros
    et IP y restaient indéfiniment alors qu'un code ne vaut que 5 minutes.
    """

    def _create_otp(self, phone_number, age_days=0):
        otp = OTPCode.objects.create(
            destination=to_e164(phone_number), code="123456", expires_at=timezone.now() + timedelta(minutes=5),
        )
        if age_days:
            OTPCode.objects.filter(pk=otp.pk).update(created_at=timezone.now() - timedelta(days=age_days))
        return otp

    def test_deletes_old_codes_and_keeps_recent_ones(self):
        self._create_otp("677600001", age_days=30)
        self._create_otp("677600002", age_days=8)
        self._create_otp("677600003")

        call_command("purge_otp_codes", stdout=StringIO())

        self.assertEqual(
            list(OTPCode.objects.values_list("destination", flat=True)), ["+237677600003"],
        )

    def test_purge_les_codes_e_mail_aussi(self):
        """
        Le help_text d'OTPCode.ip_address promet que l'adresse du demandeur est purgée
        avec la ligne : sans ce test, la promesse tiendrait au seul fait que personne
        n'a restreint la commande au seul canal SMS.
        """
        ancien = OTPCode.objects.create(
            canal=CodeCanal.EMAIL, destination="vieux@example.com", code="123456",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        OTPCode.objects.filter(pk=ancien.pk).update(
            created_at=timezone.now() - timedelta(days=30),
        )
        OTPCode.objects.create(
            canal=CodeCanal.EMAIL, destination="recent@example.com", code="123456",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        call_command("purge_otp_codes", stdout=StringIO())

        self.assertEqual(
            list(
                OTPCode.objects.filter(canal=CodeCanal.EMAIL)
                .values_list("destination", flat=True)
            ),
            ["recent@example.com"],
        )

    def test_dry_run_reports_without_deleting(self):
        self._create_otp("677600004", age_days=30)
        out = StringIO()

        call_command("purge_otp_codes", "--dry-run", stdout=out)

        self.assertIn("1 code", out.getvalue())
        self.assertEqual(OTPCode.objects.count(), 1)

    def test_refuses_a_retention_shorter_than_the_cap_windows(self):
        """Purger dans la fenêtre des plafonds effacerait les envois qu'ils comptent encore."""
        with self.assertRaises(CommandError):
            call_command("purge_otp_codes", "--days", str(MIN_RETENTION_DAYS - 1), stdout=StringIO())


class PhoneNormalizationTests(TestCase):
    """
    users.phone : frontière unique de conversion. Une erreur ici ne se voit pas en
    développement (ConsoleSMSBackend accepte n'importe quoi) mais se paie en SMS
    jamais reçus, donc en comptes inaccessibles, dès qu'un vrai fournisseur est branché.
    """

    def test_accepts_the_three_formats_that_circulate_in_the_project(self):
        for saisie in ["677123456", "237677123456", "+237677123456", "+237 677 123 456", "677-123-456"]:
            with self.subTest(saisie=saisie):
                self.assertEqual(to_e164(saisie), "+237677123456")

    def test_rejects_a_number_that_is_not_structurally_valid(self):
        # Validation structurelle seulement (voir le module) : la longueur nationale
        # réelle est du ressort du sérialiseur, testé séparément ci-dessous.
        for saisie in ["abcdef", "+0123456789", "+237"]:
            with self.subTest(saisie=saisie):
                with self.assertRaises(ValidationError):
                    to_e164(saisie)

    def test_a_too_short_number_is_rejected_at_the_api_boundary(self):
        """
        to_e164 accepte "12345" (structurellement valide une fois préfixé) : c'est le
        sérialiseur qui porte la règle nationale, et il doit donc mordre ici.
        """
        response = APIClient().post("/auth/otp/request/", {"phone_number": "12345"})

        self.assertEqual(response.status_code, 400)

    def test_msisdn_strips_the_plus_for_providers_that_refuse_it(self):
        """Format exigé par CamPay et l'API Graph WhatsApp."""
        self.assertEqual(to_msisdn("+237677123456"), "237677123456")

    def test_msisdn_is_idempotent_on_a_local_number(self):
        """
        Garde-fou contre la régression exacte que la refonte a créé le risque de
        commettre : concaténer l'indicatif à un numéro qui le porte déjà produisait
        "237+237..." et faisait échouer silencieusement la collecte Mobile Money.
        """
        self.assertEqual(to_msisdn("677123456"), to_msisdn("+237677123456"))


class AuthIdentityTests(TestCase):
    """
    Le passage de "le numéro EST le compte" à "le numéro PROUVE le compte". Ces
    invariants sont ce qui permettra de rattacher Google ou de changer de numéro sans
    créer de doublon ni perdre l'abonnement.
    """

    def test_every_account_with_a_phone_gets_its_identity(self):
        user = User.objects.create_user(phone_number="677900001", password="x")

        identity = user.identities.get()
        self.assertEqual(identity.provider, AuthProvider.PHONE)
        self.assertEqual(identity.provider_uid, "+237677900001")

    def test_an_account_can_exist_without_any_phone_number(self):
        """Prérequis de toute méthode tierce : un compte Google-first n'a pas de numéro."""
        user = User.objects.create_user(phone_number=None, password="x")

        self.assertIsNone(user.phone_number)
        self.assertFalse(user.identities.exists())

    def test_several_accounts_without_a_phone_coexist(self):
        """
        `unique` sur une colonne nullable : deux NULL ne se heurtent jamais en SQL.
        Sans cette propriété, le deuxième compte sans numéro serait rejeté en base.
        """
        User.objects.create_user(phone_number=None, password="x")
        User.objects.create_user(phone_number=None, password="x")

        self.assertEqual(User.objects.filter(phone_number=None).count(), 2)

    def test_a_provider_identity_can_only_designate_one_account(self):
        """C'est la contrainte de base, pas du code applicatif, qui interdit le doublon."""
        premier = User.objects.create_user(phone_number="677900002", password="x")
        autre = User.objects.create_user(phone_number="677900003", password="x")
        AuthIdentity.objects.create(user=premier, provider=AuthProvider.GOOGLE, provider_uid="sub-123")

        with self.assertRaises(IntegrityError):
            AuthIdentity.objects.create(user=autre, provider=AuthProvider.GOOGLE, provider_uid="sub-123")

    def test_superuser_still_requires_a_phone_number(self):
        """USERNAME_FIELD reste le numéro : un superuser sans numéro ne pourrait pas se connecter."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(phone_number=None, password="x")

    def test_login_updates_last_used_at(self):
        OTPCode.objects.create(
            destination="+237677900004", code="151515", expires_at=timezone.now() + timedelta(minutes=5),
        )
        user = verify_otp("677900004", "151515")

        self.assertIsNotNone(user.identities.get().last_used_at)


class JWTSubjectTests(TestCase):
    """
    Le sujet du token doit être la clé primaire, jamais le numéro : un numéro se
    change et se réattribue, un token qui le porterait désignerait alors quelqu'un
    d'autre. Régression silencieuse et non détectable côté utilisateur - d'où ce test.
    """

    def test_token_carries_the_primary_key_not_the_phone_number(self):
        user = User.objects.create_user(phone_number="677900010", password="x")

        token = RefreshToken.for_user(user)

        # simplejwt sérialise la claim en chaîne, d'où le str() - ce qui compte est
        # qu'elle désigne la clé primaire et que l'ancienne claim ait disparu.
        self.assertEqual(token["user_id"], str(user.pk))
        self.assertNotIn("phone_number", token.payload)

    def test_a_token_still_authenticates_after_the_phone_number_changed(self):
        user = User.objects.create_user(phone_number="677900011", password="x")
        access = str(RefreshToken.for_user(user).access_token)

        user.phone_number = "+237677900012"
        user.save(update_fields=["phone_number"])

        response = APIClient().get("/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], user.pk)


class UserSerializerContractTests(TestCase):
    """
    Le format de stockage ne doit pas fuir dans le contrat d'API : le frontend affiche
    ce champ et s'en sert pour préremplir le champ Mobile Money de SubscribePage, que
    payments valide au format local.
    """

    def test_phone_number_is_exposed_in_local_format(self):
        user = User.objects.create_user(phone_number="677900020", password="x")
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/auth/me/")

        self.assertEqual(response.data["phone_number"], "677900020")
        self.assertEqual(response.data["auth_methods"], ["phone"])

    def test_an_account_without_a_phone_serializes_without_crashing(self):
        user = User.objects.create_user(phone_number=None, password="x")
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/auth/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["phone_number"], "")
        self.assertEqual(response.data["auth_methods"], [])


@override_settings(GOOGLE_CLIENT_ID="edukora-test.apps.googleusercontent.com")
class GoogleSignInTests(TestCase):
    """
    La politique de rattachement est le point sensible de cette fonctionnalité : mal
    écrite, elle offre un compte existant à qui contrôle une adresse e-mail. La
    vérification cryptographique est mockée (elle appelle Google), pas la politique -
    qui est justement ce qu'il faut tester.
    """

    def setUp(self):
        self.client = APIClient()

    def _claims(self, sub="google-sub-1", email="eleve@gmail.com", verified=True, **extra):
        claims = {
            "iss": "https://accounts.google.com",
            "sub": sub,
            "email": email,
            "email_verified": verified,
            "name": "Awa N.",
        }
        claims.update(extra)
        return claims

    def _signin(self, claims, **payload):
        with patch("users.views.verify_google_id_token", return_value=claims):
            return self.client.post("/auth/google/", {"credential": "jeton", **payload})

    def test_first_sign_in_creates_an_account_without_a_phone_number(self):
        response = self._signin(self._claims())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["created"])
        user = User.objects.get(email="eleve@gmail.com")
        self.assertIsNone(user.phone_number)
        self.assertTrue(user.email_verified)
        self.assertEqual(user.identities.get().provider, AuthProvider.GOOGLE)

    def test_second_sign_in_reuses_the_same_account(self):
        premier = self._signin(self._claims())
        second = self._signin(self._claims())

        self.assertFalse(second.data["created"])
        self.assertEqual(premier.data["user"]["id"], second.data["user"]["id"])
        self.assertEqual(User.objects.count(), 1)

    def test_identity_follows_the_google_sub_not_the_email(self):
        """Changer l'adresse de son compte Google ne doit pas créer un second compte."""
        premier = self._signin(self._claims(email="ancienne@gmail.com"))
        second = self._signin(self._claims(email="nouvelle@gmail.com"))

        self.assertEqual(premier.data["user"]["id"], second.data["user"]["id"])
        self.assertEqual(User.objects.count(), 1)

    def test_unverified_google_email_never_links_and_is_not_stored(self):
        response = self._signin(self._claims(verified=False))

        self.assertEqual(response.status_code, 200)
        user = User.objects.get()
        self.assertIsNone(user.email)
        self.assertFalse(user.email_verified)

    def test_refuses_to_take_over_an_existing_account_by_email_alone(self):
        """
        Le scénario d'attaque : un compte déclare l'adresse de la victime sans l'avoir
        attestée. Se connecter avec Google ne doit jamais en hériter.
        """
        victime = User.objects.create_user(
            phone_number="677800001", password="x", email="victime@gmail.com", email_verified=False,
        )

        response = self._signin(self._claims(email="victime@gmail.com"))

        self.assertEqual(response.status_code, 409)
        victime.refresh_from_db()
        self.assertFalse(victime.identities.filter(provider=AuthProvider.GOOGLE).exists())

    def test_links_when_the_address_is_attested_on_both_sides(self):
        existant = User.objects.create_user(
            phone_number="677800002", password="x", email="ok@gmail.com", email_verified=True,
        )

        response = self._signin(self._claims(email="ok@gmail.com"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["id"], existant.pk)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            sorted(existant.identities.values_list("provider", flat=True)), ["google", "phone"],
        )

    def test_referral_code_is_applied_on_account_creation(self):
        parrain = User.objects.create_user(phone_number="677800003", password="x")

        self._signin(self._claims(), referral_code=parrain.referral_code)

        self.assertEqual(User.objects.get(email="eleve@gmail.com").referred_by, parrain)

    def test_a_rejected_token_never_creates_an_account(self):
        with patch("users.views.verify_google_id_token", side_effect=GoogleAuthError("nope")):
            response = self.client.post("/auth/google/", {"credential": "faux"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(User.objects.count(), 0)

    @override_settings(GOOGLE_CLIENT_ID="")
    def test_endpoint_is_unavailable_rather_than_permissive_when_unconfigured(self):
        """Sans client_id, aucune claim `aud` n'est vérifiable : refuser, jamais accepter."""
        response = self.client.post("/auth/google/", {"credential": "jeton"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(User.objects.count(), 0)


@override_settings(GOOGLE_CLIENT_ID="edukora-test.apps.googleusercontent.com")
class GoogleLinkTests(TestCase):
    """Rattachement depuis un compte déjà connecté - le chemin sûr de fusion."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677810001", password="x")
        self.client.force_authenticate(user=self.user)

    def _link(self, claims):
        with patch("users.views.verify_google_id_token", return_value=claims):
            return self.client.post("/auth/google/link/", {"credential": "jeton"})

    def _claims(self, sub="google-sub-9", email="moi@gmail.com"):
        return {"iss": "https://accounts.google.com", "sub": sub, "email": email, "email_verified": True}

    def test_links_google_to_the_phone_account(self):
        response = self._link(self._claims())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(response.data["auth_methods"]), ["google", "phone"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "moi@gmail.com")

    def test_refuses_a_google_account_already_used_elsewhere(self):
        autre = User.objects.create_user(phone_number="677810002", password="x")
        AuthIdentity.objects.create(user=autre, provider=AuthProvider.GOOGLE, provider_uid="google-sub-9")

        response = self._link(self._claims())

        self.assertEqual(response.status_code, 409)
        self.assertFalse(self.user.identities.filter(provider=AuthProvider.GOOGLE).exists())

    def test_does_not_overwrite_an_email_already_set_on_the_account(self):
        self.user.email = "choisie@edukora.cm"
        self.user.save(update_fields=["email"])

        self._link(self._claims())

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "choisie@edukora.cm")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post("/auth/google/link/", {"credential": "jeton"})

        self.assertEqual(response.status_code, 401)


class GoogleTokenVerificationTests(TestCase):
    """
    Contrôles cryptographiques. `aud` est le seul qui, absent, transformerait
    l'endpoint en porte ouverte : un ID token émis par Google pour n'importe quelle
    autre application ouvrirait alors n'importe quel compte Edukora.
    """

    @override_settings(GOOGLE_CLIENT_ID="edukora-test.apps.googleusercontent.com")
    def test_audience_is_passed_to_the_decoder(self):
        with patch("users.google._jwk_client"), patch("users.google.jwt.decode") as mock_decode:
            mock_decode.return_value = {"iss": "https://accounts.google.com", "sub": "s"}
            verify_google_id_token("jeton")

        self.assertEqual(
            mock_decode.call_args.kwargs["audience"], "edukora-test.apps.googleusercontent.com",
        )
        self.assertEqual(mock_decode.call_args.kwargs["algorithms"], ["RS256"])

    @override_settings(GOOGLE_CLIENT_ID="edukora-test.apps.googleusercontent.com")
    def test_rejects_a_token_from_an_unexpected_issuer(self):
        with patch("users.google._jwk_client"), patch("users.google.jwt.decode") as mock_decode:
            mock_decode.return_value = {"iss": "https://evil.example", "sub": "s"}
            with self.assertRaises(GoogleAuthError):
                verify_google_id_token("jeton")

    @override_settings(GOOGLE_CLIENT_ID="")
    def test_raises_when_not_configured(self):
        with self.assertRaises(GoogleNotConfigured):
            verify_google_id_token("jeton")


class PhoneChangeTests(TestCase):
    """
    Changer de numéro sans perdre son compte : le motif de perte le plus fréquent sur
    ce marché est la rotation de puce, pas l'oubli d'un identifiant. Ce qui est vérifié
    ici est surtout ce que le changement ne doit JAMAIS faire - créer un doublon,
    marcher sur le compte d'autrui, ou laisser le compte sans identité.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677700001", password="x")
        self.client.force_authenticate(user=self.user)

    def _demander(self, numero):
        with patch("users.otp_service.get_sms_backend"):
            return self.client.post("/auth/phone/change/request/", {"phone_number": numero})

    def _confirmer(self, numero, code):
        with patch("users.account.get_sms_backend"):
            return self.client.post(
                "/auth/phone/change/confirm/", {"phone_number": numero, "code": code},
            )

    def _code(self, numero):
        return OTPCode.objects.get(destination=to_e164(numero), is_used=False).code

    def test_full_change_moves_the_account_to_the_new_number(self):
        self._demander("677700002")
        response = self._confirmer("677700002", self._code("677700002"))

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+237677700002")
        # L'identité suit le compte : c'est elle qui décide quelle connexion l'ouvre.
        self.assertEqual(
            self.user.identities.get(provider=AuthProvider.PHONE).provider_uid, "+237677700002",
        )
        self.assertEqual(self.user.identities.count(), 1)

    def test_the_old_number_can_then_open_a_brand_new_account(self):
        """Un numéro libéré redevient disponible - sans jamais rouvrir l'ancien compte."""
        self._demander("677700003")
        self._confirmer("677700003", self._code("677700003"))

        OTPCode.objects.create(
            destination="+237677700001", code="424242",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        repreneur = verify_otp("677700001", "424242")

        self.assertNotEqual(repreneur.pk, self.user.pk)

    def test_after_the_change_the_new_number_opens_the_same_account(self):
        self._demander("677700004")
        self._confirmer("677700004", self._code("677700004"))

        OTPCode.objects.create(
            destination="+237677700004", code="434343",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        reconnecte = verify_otp("677700004", "434343")

        self.assertEqual(reconnecte.pk, self.user.pk)

    def test_refuses_a_number_already_used_by_another_account(self):
        User.objects.create_user(phone_number="677700010", password="x")

        response = self._demander("677700010")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(OTPCode.objects.count(), 0)

    def test_refuses_the_number_the_account_already_has(self):
        """Sans ce garde-fou, l'utilisateur paierait un SMS pour ne rien changer."""
        response = self._demander("677700001")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(OTPCode.objects.count(), 0)

    def test_a_wrong_code_changes_nothing(self):
        self._demander("677700005")

        response = self._confirmer("677700005", "000000")

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+237677700001")

    def test_confirmation_never_creates_a_second_account(self):
        """
        La régression que consume_otp existe pour empêcher : verify_otp aurait créé un
        compte sur le numéro visé au lieu d'y déplacer celui-ci.
        """
        self._demander("677700006")
        self._confirmer("677700006", self._code("677700006"))

        self.assertEqual(User.objects.count(), 1)

    def test_notifies_the_old_number_after_the_change(self):
        self._demander("677700007")
        # captureOnCommitCallbacks : la notification part volontairement via
        # transaction.on_commit (voir users.account), qui ne se déclenche jamais dans
        # une TestCase - dont la transaction est toujours annulée. Sans ce capture, le
        # test vérifierait l'absence d'un envoi qui a bien lieu en production.
        with patch("users.account.get_sms_backend") as mock_backend:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(
                    "/auth/phone/change/confirm/",
                    {"phone_number": "677700007", "code": self._code("677700007")},
                )

        numero, message = mock_backend.return_value.send.call_args[0]
        self.assertEqual(numero, "+237677700001")
        self.assertNotIn("677700007", message)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post("/auth/phone/change/request/", {"phone_number": "677700008"})

        self.assertEqual(response.status_code, 401)

    def test_a_google_only_account_can_attach_a_first_phone_number(self):
        sans_numero = User.objects.create_user(phone_number=None, password="x")
        AuthIdentity.objects.create(
            user=sans_numero, provider=AuthProvider.GOOGLE, provider_uid="sub-abc",
        )
        self.client.force_authenticate(user=sans_numero)

        self._demander("677700009")
        response = self._confirmer("677700009", self._code("677700009"))

        self.assertEqual(response.status_code, 200)
        sans_numero.refresh_from_db()
        self.assertEqual(sans_numero.phone_number, "+237677700009")
        self.assertEqual(sorted(sans_numero.identities.values_list("provider", flat=True)),
                         ["google", "phone"])


class UnlinkIdentityTests(TestCase):
    """
    Détacher une méthode ne doit jamais pouvoir enfermer l'utilisateur dehors - c'est
    le seul geste de cette API qui peut rendre un compte définitivement inaccessible.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677710001", password="x")
        self.client.force_authenticate(user=self.user)

    def test_refuses_to_unlink_the_last_identity(self):
        response = self.client.delete("/auth/identities/phone/")

        self.assertEqual(response.status_code, 409)
        self.assertTrue(self.user.identities.exists())

    def test_unlinks_google_when_a_phone_remains(self):
        AuthIdentity.objects.create(
            user=self.user, provider=AuthProvider.GOOGLE, provider_uid="sub-xyz",
        )

        response = self.client.delete("/auth/identities/google/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["auth_methods"], ["phone"])

    def test_unlinking_the_phone_also_frees_the_number(self):
        """
        Sinon User.phone_number désignerait un numéro que plus aucune identité ne
        prouve, tout en le bloquant pour les autres comptes par unicité.
        """
        AuthIdentity.objects.create(
            user=self.user, provider=AuthProvider.GOOGLE, provider_uid="sub-libre",
        )

        self.client.delete("/auth/identities/phone/")

        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone_number)

    def test_a_staff_account_can_never_unlink_its_phone(self):
        """C'est USERNAME_FIELD, donc le seul identifiant de connexion à l'admin Django."""
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        AuthIdentity.objects.create(
            user=self.user, provider=AuthProvider.GOOGLE, provider_uid="sub-staff",
        )

        response = self.client.delete("/auth/identities/phone/")

        self.assertEqual(response.status_code, 409)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+237677710001")

    def test_unknown_provider_is_a_404(self):
        response = self.client.delete("/auth/identities/apple/")

        self.assertEqual(response.status_code, 404)


@override_settings(GOOGLE_CLIENT_ID="edukora-test.apps.googleusercontent.com")
class GoogleRealSignatureTests(TestCase):
    """
    Vérification RS256 RÉELLE, sans mocker jwt.decode.

    Existe à cause d'une panne constatée en local : les tests de
    GoogleTokenVerificationTests mockent le décodeur pour contrôler les claims, si
    bien qu'aucun n'exerçait la cryptographie. PyJWT sans le paquet `cryptography`
    ne gère que HMAC et lève « RS256 requires 'cryptography' to be installed » -
    toute connexion Google répondait 401, suite verte comprise.

    Seul le client JWKS est remplacé ici (il appellerait Google) : la signature, elle,
    est bel et bien produite puis vérifiée.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 2048 bits, généré une fois pour toute la classe : c'est la taille des clés
        # de signature de Google, et la génération est trop lente pour chaque test.
        cls.cle_privee = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def _jeton(self, **remplacements):
        maintenant = int(time.time())
        claims = {
            "iss": "https://accounts.google.com",
            "sub": "google-sub-signe",
            "aud": "edukora-test.apps.googleusercontent.com",
            "email": "eleve@gmail.com",
            "email_verified": True,
            "iat": maintenant,
            "exp": maintenant + 300,
        }
        claims.update(remplacements)
        return jwt.encode(claims, self.cle_privee, algorithm="RS256")

    def _verifier(self, jeton):
        with patch("users.google._jwk_client") as mock_client:
            mock_client.get_signing_key_from_jwt.return_value = SimpleNamespace(
                key=self.cle_privee.public_key(),
            )
            return verify_google_id_token(jeton)

    def test_accepts_a_genuinely_signed_token(self):
        """Échoue si `cryptography` disparaît des dépendances - c'est tout l'objet du test."""
        claims = self._verifier(self._jeton())

        self.assertEqual(claims["sub"], "google-sub-signe")
        self.assertEqual(claims["email"], "eleve@gmail.com")

    def test_rejects_a_token_issued_for_another_application(self):
        """
        Le contrôle décisif : sans lui, un ID token émis par Google pour n'importe
        quelle autre application ouvrirait n'importe quel compte Edukora.
        """
        with self.assertRaises(GoogleAuthError):
            self._verifier(self._jeton(aud="une-autre-app.apps.googleusercontent.com"))

    def test_rejects_an_expired_token(self):
        maintenant = int(time.time())
        with self.assertRaises(GoogleAuthError):
            self._verifier(self._jeton(iat=maintenant - 3600, exp=maintenant - 3000))

    def test_rejects_a_token_signed_by_another_key(self):
        """Signature valide en apparence, mais pas par la clé annoncée par le JWKS."""
        autre_cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        maintenant = int(time.time())
        jeton = jwt.encode(
            {
                "iss": "https://accounts.google.com", "sub": "s",
                "aud": "edukora-test.apps.googleusercontent.com",
                "iat": maintenant, "exp": maintenant + 300,
            },
            autre_cle,
            algorithm="RS256",
        )

        with self.assertRaises(GoogleAuthError):
            self._verifier(jeton)


LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


@override_settings(EMAIL_BACKEND=LOCMEM)
class EmailCodeSendingTests(TestCase):
    def test_envoi_cree_une_ligne_et_un_message(self):
        request_email_code("Eleve@Example.COM")

        entry = OTPCode.objects.get(canal=CodeCanal.EMAIL)
        self.assertEqual(entry.destination, "eleve@example.com")
        self.assertEqual(len(mail.outbox), 1)
        # Le code doit figurer dans l'objet : c'est ce qui le rend lisible depuis la
        # notification du téléphone, sans ouvrir le message.
        self.assertIn(entry.code, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["eleve@example.com"])

    def test_deuxieme_demande_immediate_refusee(self):
        request_email_code("eleve@example.com")
        with self.assertRaises(EmailThrottled):
            request_email_code("eleve@example.com")
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_CODE_MAX_PER_IP_PER_HOUR=2)
    def test_plafond_par_ip(self):
        for i in range(2):
            request_email_code(f"eleve{i}@example.com", ip_address="41.202.1.1")
        with self.assertRaises(EmailThrottled):
            request_email_code("autre@example.com", ip_address="41.202.1.1")
        # Une autre source n'est pas affectée par le plafond de celle-ci.
        request_email_code("autre@example.com", ip_address="41.202.9.9")

    @override_settings(EMAIL_CODE_DAILY_GLOBAL_CAP=1)
    def test_plafond_global(self):
        request_email_code("un@example.com")
        with self.assertRaises(EmailCapReached):
            request_email_code("deux@example.com")

    def test_echec_smtp_remonte_en_exception_dediee(self):
        with patch("users.email_service.send_mail", side_effect=OSError("smtp down")):
            with self.assertRaises(EmailSendFailed):
                request_email_code("eleve@example.com")
        # La ligne est conservée volontairement : elle fait courir le délai anti-renvoi.
        self.assertEqual(OTPCode.objects.filter(canal=CodeCanal.EMAIL).count(), 1)


@override_settings(EMAIL_BACKEND="users.email_backends.ConsoleEmailBackend")
class ConsoleEmailBackendTests(TestCase):
    """
    Le backend de développement doit rendre le code aussi facile à relever que celui du
    canal SMS. Sans ce test, le jour où quelqu'un revient au backend console de Django,
    la régression est invisible : les messages continuent de « partir », simplement le
    code se perd au milieu des en-têtes MIME.
    """

    def test_le_code_est_affiche_en_une_ligne_lisible(self):
        sortie = StringIO()
        with patch("sys.stdout", sortie):
            request_email_code("eleve@example.com")

        affiche = sortie.getvalue()
        code = OTPCode.objects.get(canal=CodeCanal.EMAIL).code
        self.assertIn("[E-MAIL -> eleve@example.com]", affiche)
        self.assertIn(code, affiche)

    def test_send_mail_retourne_bien_un_envoi(self):
        # BaseEmailBackend doit retourner le nombre de messages envoyés : un 0 ferait
        # croire à un échec chez tout appelant qui teste la valeur de retour.
        from django.core.mail import send_mail

        with patch("sys.stdout", StringIO()):
            envoyes = send_mail("Objet", "Corps", None, ["eleve@example.com"])
        self.assertEqual(envoyes, 1)


@override_settings(EMAIL_BACKEND=LOCMEM)
class EmailAndSMSBudgetsAreSeparateTests(TestCase):
    """
    Le point de conception le plus facile à casser par mégarde : les deux canaux ont des
    coûts sans rapport, leurs compteurs ne doivent jamais se croiser. Si un jour quelqu'un
    fusionne les deux tables, ces deux tests tombent.
    """

    @override_settings(OTP_DAILY_GLOBAL_CAP=1)
    def test_plafond_sms_atteint_nempeche_pas_les_e_mails(self):
        request_otp("+237677100001")
        with self.assertRaises(OTPCapReached):
            request_otp("+237677100002")

        request_email_code("eleve@example.com")
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(OTP_DAILY_GLOBAL_CAP=2)
    def test_les_e_mails_ne_consomment_pas_le_budget_sms(self):
        for i in range(5):
            request_email_code(f"eleve{i}@example.com")
        # Le budget SMS est intact malgré les cinq e-mails envoyés. Le filtre sur le
        # canal EST l'assertion : depuis que les deux canaux partagent la table, compter
        # les lignes sans lui compterait aussi les e-mails, et ce test ne prouverait
        # plus rien de ce pour quoi il a été écrit.
        request_otp("+237677100001")
        self.assertEqual(OTPCode.objects.filter(canal=CodeCanal.SMS).count(), 1)
        self.assertEqual(OTPCode.objects.filter(canal=CodeCanal.EMAIL).count(), 5)


@override_settings(EMAIL_BACKEND=LOCMEM)
class VerifyEmailCodeTests(TestCase):
    def _code_pour(self, email):
        request_email_code(email)
        return OTPCode.objects.filter(
            canal=CodeCanal.EMAIL, destination=email.strip().lower(),
        ).latest("created_at").code

    def test_cree_un_compte_verifie_avec_son_identite(self):
        code = self._code_pour("eleve@example.com")
        user, cree = verify_email_code("eleve@example.com", code)

        self.assertTrue(cree)
        self.assertEqual(user.email, "eleve@example.com")
        self.assertTrue(user.email_verified)
        self.assertIsNone(user.phone_number)
        self.assertEqual(
            list(user.identities.values_list("provider", flat=True)), [AuthProvider.EMAIL],
        )

    def test_deuxieme_connexion_rouvre_le_meme_compte(self):
        code = self._code_pour("eleve@example.com")
        premier, _ = verify_email_code("eleve@example.com", code)

        OTPCode.objects.filter(canal=CodeCanal.EMAIL).delete()
        code = self._code_pour("eleve@example.com")
        second, cree = verify_email_code("eleve@example.com", code)

        self.assertFalse(cree)
        self.assertEqual(premier.pk, second.pk)
        self.assertEqual(User.objects.count(), 1)

    def test_la_casse_ne_cree_pas_deux_comptes(self):
        code = self._code_pour("Eleve@Example.com")
        premier, _ = verify_email_code("ELEVE@example.COM", code)

        OTPCode.objects.filter(canal=CodeCanal.EMAIL).delete()
        code = self._code_pour("eleve@example.com")
        second, cree = verify_email_code("eleve@example.com", code)

        self.assertFalse(cree)
        self.assertEqual(premier.pk, second.pk)
        self.assertEqual(AuthIdentity.objects.filter(provider=AuthProvider.EMAIL).count(), 1)

    def test_adresse_attestee_par_google_ouvre_le_compte_existant(self):
        google_user = User.objects.create_user(
            phone_number=None, email="eleve@example.com", email_verified=True,
        )
        AuthIdentity.objects.create(
            user=google_user, provider=AuthProvider.GOOGLE, provider_uid="sub-123",
        )

        code = self._code_pour("eleve@example.com")
        user, cree = verify_email_code("eleve@example.com", code)

        self.assertFalse(cree)
        self.assertEqual(user.pk, google_user.pk)
        self.assertEqual(User.objects.count(), 1)
        # L'identité e-mail est rattachée au passage : la méthode devient utilisable seule.
        self.assertTrue(user.identities.filter(provider=AuthProvider.EMAIL).exists())

    def test_adresse_non_attestee_dun_autre_compte_refusee(self):
        autre = User.objects.create_user(phone_number="677100001")
        User.objects.filter(pk=autre.pk).update(email="eleve@example.com", email_verified=False)

        code = self._code_pour("eleve@example.com")
        with self.assertRaises(EmailAlreadyTaken):
            verify_email_code("eleve@example.com", code)
        self.assertEqual(User.objects.count(), 1)

    def test_code_faux_puis_epuisement_des_tentatives(self):
        self._code_pour("eleve@example.com")
        for _ in range(5):
            with self.assertRaises(EmailInvalid):
                verify_email_code("eleve@example.com", "000000")
        # Au-delà du plafond, redemander un code est la seule issue.
        with self.assertRaises(EmailInvalid):
            verify_email_code("eleve@example.com", "000000")
        self.assertEqual(User.objects.count(), 0)

    def test_code_expire_refuse(self):
        code = self._code_pour("eleve@example.com")
        OTPCode.objects.filter(canal=CodeCanal.EMAIL).update(
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        with self.assertRaises(EmailInvalid):
            verify_email_code("eleve@example.com", code)

    def test_parrainage_pris_en_compte_a_la_creation(self):
        parrain = User.objects.create_user(phone_number="677100001")
        code = self._code_pour("eleve@example.com")
        user, _ = verify_email_code("eleve@example.com", code, referral_code=parrain.referral_code)
        self.assertEqual(user.referred_by_id, parrain.pk)


@override_settings(EMAIL_BACKEND=LOCMEM)
class EmailAuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _code(self, email):
        return OTPCode.objects.filter(
            canal=CodeCanal.EMAIL, destination=email,
        ).latest("created_at").code

    def test_flux_complet_connexion(self):
        reponse = self.client.post("/auth/email/request/", {"email": "Eleve@example.com"})
        self.assertEqual(reponse.status_code, 200)

        reponse = self.client.post("/auth/email/verify/", {
            "email": "eleve@example.com", "code": self._code("eleve@example.com"),
        })
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("access", reponse.data)
        self.assertTrue(reponse.data["created"])
        self.assertEqual(reponse.data["user"]["email"], "eleve@example.com")
        self.assertIn(REFRESH_COOKIE_NAME, reponse.cookies)
        self.assertIn(AuthProvider.EMAIL, reponse.data["user"]["auth_methods"])

    def test_adresse_invalide_rejetee_avant_tout_envoi(self):
        reponse = self.client.post("/auth/email/request/", {"email": "pas-une-adresse"})
        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_code_faux_renvoie_400(self):
        self.client.post("/auth/email/request/", {"email": "eleve@example.com"})
        reponse = self.client.post("/auth/email/verify/", {
            "email": "eleve@example.com", "code": "000000",
        })
        self.assertEqual(reponse.status_code, 400)

    @override_settings(EMAIL_CODE_DAILY_GLOBAL_CAP=0)
    def test_plafond_global_renvoie_503(self):
        reponse = self.client.post("/auth/email/request/", {"email": "eleve@example.com"})
        self.assertEqual(reponse.status_code, 503)

    def test_panne_smtp_renvoie_503_et_pas_500(self):
        with patch("users.email_service.send_mail", side_effect=OSError("smtp down")):
            reponse = self.client.post("/auth/email/request/", {"email": "eleve@example.com"})
        self.assertEqual(reponse.status_code, 503)


@override_settings(EMAIL_BACKEND=LOCMEM)
class EmailLinkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677100001")
        self.client.force_authenticate(user=self.user)

    def _code(self, email):
        return OTPCode.objects.filter(
            canal=CodeCanal.EMAIL, destination=email,
        ).latest("created_at").code

    def test_rattachement_complet(self):
        reponse = self.client.post("/auth/email/link/request/", {"email": "eleve@example.com"})
        self.assertEqual(reponse.status_code, 200)

        reponse = self.client.post("/auth/email/link/confirm/", {
            "email": "eleve@example.com", "code": self._code("eleve@example.com"),
        })
        self.assertEqual(reponse.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "eleve@example.com")
        self.assertTrue(self.user.email_verified)
        self.assertTrue(self.user.identities.filter(provider=AuthProvider.EMAIL).exists())
        self.assertEqual(
            sorted(reponse.data["auth_methods"]), [AuthProvider.EMAIL, AuthProvider.PHONE],
        )

    def test_adresse_dun_autre_compte_refusee_avant_envoi(self):
        autre = User.objects.create_user(phone_number="677100002")
        AuthIdentity.objects.create(
            user=autre, provider=AuthProvider.EMAIL, provider_uid="pris@example.com",
        )

        reponse = self.client.post("/auth/email/link/request/", {"email": "pris@example.com"})
        self.assertEqual(reponse.status_code, 409)
        self.assertEqual(len(mail.outbox), 0)

    def test_rattachement_anonyme_refuse(self):
        client = APIClient()
        reponse = client.post("/auth/email/link/request/", {"email": "eleve@example.com"})
        self.assertEqual(reponse.status_code, 401)

    def test_detacher_libere_ladresse(self):
        self.client.post("/auth/email/link/request/", {"email": "eleve@example.com"})
        self.client.post("/auth/email/link/confirm/", {
            "email": "eleve@example.com", "code": self._code("eleve@example.com"),
        })

        reponse = self.client.delete(f"/auth/identities/{AuthProvider.EMAIL}/")
        self.assertEqual(reponse.status_code, 200)

        self.user.refresh_from_db()
        # L'adresse est libérée, sinon elle resterait réservée par unicité sans qu'aucune
        # identité ne la prouve - et son titulaire réel ne pourrait plus s'en servir.
        self.assertIsNone(self.user.email)
        self.assertFalse(self.user.email_verified)
