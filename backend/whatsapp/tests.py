"""
Couvre les deux risques du chantier "Rappels WhatsApp" : le consentement explicite
(jamais présumé depuis un numéro déjà en base, voir OptIn - docstring de modèle) et la
sélection des destinataires du jour (whatsapp.services.utilisateurs_a_relancer, qui
réutilise quiz.services.revisions_dues plutôt qu'un second calcul de retard).
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag
from quiz.models import RevisionSchedule
from users.models import User

from .backends import ConsoleWhatsAppBackend, get_whatsapp_backend
from .models import OptIn
from .services import envoyer_rappels_du_jour, is_opted_in, opt_in, opt_out, utilisateurs_a_relancer


class OptInServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677400001", password="x")

    def test_opt_in_creates_an_active_row(self):
        opt_in(self.user)
        self.assertTrue(is_opted_in(self.user))
        self.assertEqual(OptIn.objects.filter(user=self.user).count(), 1)

    def test_opt_in_is_idempotent(self):
        opt_in(self.user)
        opt_in(self.user)
        self.assertEqual(OptIn.objects.filter(user=self.user).count(), 1)

    def test_opt_out_deactivates(self):
        opt_in(self.user)
        opt_out(self.user)
        self.assertFalse(is_opted_in(self.user))

    def test_opt_in_after_opt_out_creates_a_new_row(self):
        opt_in(self.user)
        opt_out(self.user)
        opt_in(self.user)
        self.assertTrue(is_opted_in(self.user))
        self.assertEqual(OptIn.objects.filter(user=self.user).count(), 2)


class UtilisateursARelancerTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")

    def _make_schedule(self, user, due_at):
        theme = Tag.objects.create(name=f"theme-{user.id}-{due_at}")
        return RevisionSchedule.objects.create(
            user=user, cursus=self.cursus, subject=self.subject, theme=theme, due_at=due_at,
        )

    def test_excludes_users_not_opted_in(self):
        user = User.objects.create_user(phone_number="677400010", password="x")
        self._make_schedule(user, timezone.localdate())

        self.assertEqual(list(utilisateurs_a_relancer()), [])

    def test_excludes_opted_out_users(self):
        user = User.objects.create_user(phone_number="677400011", password="x")
        opt_in(user)
        opt_out(user)
        self._make_schedule(user, timezone.localdate())

        self.assertEqual(list(utilisateurs_a_relancer()), [])

    def test_excludes_opted_in_users_with_nothing_due(self):
        user = User.objects.create_user(phone_number="677400012", password="x")
        opt_in(user)
        self._make_schedule(user, timezone.localdate() + timedelta(days=3))

        self.assertEqual(list(utilisateurs_a_relancer()), [])

    def test_includes_opted_in_users_with_something_due(self):
        user = User.objects.create_user(phone_number="677400013", password="x")
        opt_in(user)
        schedule = self._make_schedule(user, timezone.localdate())

        result = list(utilisateurs_a_relancer())

        self.assertEqual(len(result), 1)
        got_user, schedules = result[0]
        self.assertEqual(got_user, user)
        self.assertEqual(schedules, [schedule])


class EnvoyerRappelsDuJourTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.user = User.objects.create_user(phone_number="677400020", password="x")
        opt_in(self.user)
        theme = Tag.objects.create(name="dérivation")
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=theme, due_at=timezone.localdate(),
        )

    @patch("whatsapp.services.get_whatsapp_backend")
    def test_sends_one_template_per_eligible_user(self, mock_get_backend):
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend

        envoyes = envoyer_rappels_du_jour()

        self.assertEqual(envoyes, 1)
        mock_backend.send_template.assert_called_once()
        phone_number, template_name, params = mock_backend.send_template.call_args[0]
        self.assertEqual(phone_number, self.user.phone_number)
        self.assertEqual(params[0], 1)  # nombre de notions dues
        self.assertIn("dérivation", params[1])

    @patch("whatsapp.services.get_whatsapp_backend")
    def test_returns_zero_when_nobody_is_eligible(self, mock_get_backend):
        opt_out(self.user)

        envoyes = envoyer_rappels_du_jour()

        self.assertEqual(envoyes, 0)
        mock_get_backend.return_value.send_template.assert_not_called()


class ConsoleWhatsAppBackendTests(TestCase):
    def test_default_backend_is_console(self):
        self.assertIsInstance(get_whatsapp_backend(), ConsoleWhatsAppBackend)

    def test_send_template_does_not_raise(self):
        ConsoleWhatsAppBackend().send_template("677400030", "rappel_revision_quotidien", [1, "dérivation"])


class WhatsAppApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677400040", password="x")
        self.client = APIClient()

    def test_statut_requires_authentication(self):
        response = self.client.get("/whatsapp/statut/")
        self.assertIn(response.status_code, (401, 403))

    def test_statut_defaults_to_not_opted_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/whatsapp/statut/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["opted_in"], False)

    def test_opt_in_then_opt_out_roundtrip(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/whatsapp/opt-in/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["opted_in"])
        self.assertTrue(is_opted_in(self.user))

        response = self.client.post("/whatsapp/opt-out/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["opted_in"])
        self.assertFalse(is_opted_in(self.user))
