"""
Couvre les trois risques du chantier "Rappels WhatsApp" : le consentement explicite
(jamais présumé depuis un numéro déjà en base, voir OptIn - docstring de modèle), la
sélection des destinataires du jour (whatsapp.services.utilisateurs_a_relancer, qui
réutilise quiz.services.revisions_dues plutôt qu'un second calcul de retard), et
l'authentification du webhook entrant (whatsapp.webhook - URL publique dont
l'acceptation d'une notification non signée offrirait un désabonnement de masse).
"""

import hashlib
import hmac
import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag
from quiz.models import RevisionSchedule
from users.models import User

from .backends import ConsoleWhatsAppBackend, MetaCloudAPIBackend, get_whatsapp_backend
from .models import OptIn
from .services import (
    envoyer_rappels_du_jour,
    est_demande_arret,
    is_opted_in,
    opt_in,
    opt_out,
    traiter_payload_entrant,
    utilisateurs_a_relancer,
)


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


class WhatsAppBackendTests(TestCase):
    """
    Chaque cas force WHATSAPP_BACKEND plutôt que de lire la valeur ambiante : dès que
    le .env branche réellement Meta (le cas normal une fois l'intégration en service),
    un test qui affirmait « le backend est le backend console » échouait sur une
    configuration pourtant correcte. Le contrat testé ici est la RÉSOLUTION du chemin,
    pas la valeur du jour ; le repli sûr, lui, est fixé par le `default=` de settings.py.
    """

    @override_settings(WHATSAPP_BACKEND="whatsapp.backends.ConsoleWhatsAppBackend")
    def test_resolves_console_backend(self):
        self.assertIsInstance(get_whatsapp_backend(), ConsoleWhatsAppBackend)

    @override_settings(WHATSAPP_BACKEND="whatsapp.backends.MetaCloudAPIBackend")
    def test_resolves_meta_backend(self):
        self.assertIsInstance(get_whatsapp_backend(), MetaCloudAPIBackend)

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


VERIFY_TOKEN = "jeton-de-verification-de-test"
APP_SECRET = "secret-application-de-test"


def _config_de_test(valeurs):
    """Remplace decouple.config dans whatsapp.webhook : les vraies valeurs vivent dans
    .env, absent de l'environnement de test."""
    def _config(cle, default=None):
        return valeurs.get(cle, default)
    return _config


def _payload_message(numero, texte):
    """Forme réelle d'une notification « message entrant » de l'API Cloud (le `from`
    arrive en chiffres seuls, indicatif compris, jamais en E.164)."""
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "1827002815377625",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "messages": [{
                        "from": numero,
                        "id": "wamid.TEST",
                        "type": "text",
                        "text": {"body": texte},
                    }],
                },
            }],
        }],
    }


class DemandeArretTests(TestCase):
    def test_reconnait_les_variantes_reellement_tapees(self):
        for texte in ["STOP", "stop", "Arrêt", "ARRÊT !", "stop rappels", "arreter", "Unsubscribe"]:
            with self.subTest(texte=texte):
                self.assertTrue(est_demande_arret(texte))

    def test_ignore_un_message_ordinaire(self):
        for texte in ["bonjour", "merci pour le rappel", "", "je veux arrêter demain"]:
            with self.subTest(texte=texte):
                self.assertFalse(est_demande_arret(texte))


class TraiterPayloadEntrantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677400050", password="x")
        opt_in(self.user)

    def test_stop_desabonne_l_utilisateur(self):
        self.assertEqual(traiter_payload_entrant(_payload_message("237677400050", "STOP")), 1)
        self.assertFalse(is_opted_in(self.user))

    def test_message_ordinaire_ne_desabonne_pas(self):
        self.assertEqual(traiter_payload_entrant(_payload_message("237677400050", "bonjour")), 0)
        self.assertTrue(is_opted_in(self.user))

    def test_numero_inconnu_est_ignore_sans_lever(self):
        self.assertEqual(traiter_payload_entrant(_payload_message("237699999999", "STOP")), 0)
        self.assertTrue(is_opted_in(self.user))

    def test_numero_stocke_au_format_local_historique_est_retrouve(self):
        """Les comptes créés avant la migration E.164 doivent aussi pouvoir se
        désabonner (voir services.utilisateur_par_numero)."""
        User.objects.filter(pk=self.user.pk).update(phone_number="677400050")

        self.assertEqual(traiter_payload_entrant(_payload_message("237677400050", "STOP")), 1)
        self.assertFalse(is_opted_in(self.user))

    def test_accuse_de_reception_est_ignore_sans_lever(self):
        payload = {"entry": [{"changes": [{"value": {"statuses": [{"status": "delivered"}]}}]}]}
        self.assertEqual(traiter_payload_entrant(payload), 0)

    def test_payload_de_forme_inattendue_ne_leve_pas(self):
        """Lever ferait retenter Meta en boucle (voir la docstring de la fonction)."""
        for payload in [{}, {"entry": None}, {"entry": [{}]}, {"entry": [{"changes": [{}]}]}]:
            with self.subTest(payload=payload):
                self.assertEqual(traiter_payload_entrant(payload), 0)


class WebhookVerificationTests(TestCase):
    """GET /whatsapp/webhook/ - l'échange unique que Meta fait à l'enregistrement."""

    def _get(self, params):
        return self.client.get("/whatsapp/webhook/", params)

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_VERIFY_TOKEN": VERIFY_TOKEN}))
    def test_bon_jeton_renvoie_le_challenge_en_texte_brut(self):
        response = self._get({
            "hub.mode": "subscribe", "hub.verify_token": VERIFY_TOKEN, "hub.challenge": "1158201444",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"1158201444")
        self.assertTrue(response["Content-Type"].startswith("text/plain"))

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_VERIFY_TOKEN": VERIFY_TOKEN}))
    def test_mauvais_jeton_est_refuse(self):
        response = self._get({
            "hub.mode": "subscribe", "hub.verify_token": "pas-le-bon", "hub.challenge": "1158201444",
        })

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(b"1158201444", response.content)

    @patch("whatsapp.webhook.config", _config_de_test({}))
    def test_jeton_non_configure_refuse_au_lieu_de_tout_accepter(self):
        response = self._get({"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "x"})

        self.assertEqual(response.status_code, 403)


class WebhookNotificationTests(TestCase):
    """POST /whatsapp/webhook/ - la signature du corps est la SEULE authentification."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677400060", password="x")
        opt_in(self.user)
        self.corps = json.dumps(_payload_message("237677400060", "STOP")).encode()

    def _post(self, corps, signature=None):
        entetes = {"HTTP_X_HUB_SIGNATURE_256": signature} if signature is not None else {}
        return self.client.post(
            "/whatsapp/webhook/", data=corps, content_type="application/json", **entetes,
        )

    def _signer(self, corps, secret=APP_SECRET):
        return "sha256=" + hmac.new(secret.encode(), corps, hashlib.sha256).hexdigest()

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_APP_SECRET": APP_SECRET}))
    def test_notification_signee_applique_le_desabonnement(self):
        response = self._post(self.corps, self._signer(self.corps))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["desabonnements"], 1)
        self.assertFalse(is_opted_in(self.user))

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_APP_SECRET": APP_SECRET}))
    def test_notification_sans_signature_est_refusee(self):
        response = self._post(self.corps)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(is_opted_in(self.user))

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_APP_SECRET": APP_SECRET}))
    def test_signature_d_un_autre_secret_est_refusee(self):
        response = self._post(self.corps, self._signer(self.corps, secret="secret-de-l-attaquant"))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(is_opted_in(self.user))

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_APP_SECRET": APP_SECRET}))
    def test_corps_altere_apres_signature_est_refuse(self):
        signature = self._signer(self.corps)
        autre = json.dumps(_payload_message("237677400060", "STOP MAINTENANT")).encode()

        response = self._post(autre, signature)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(is_opted_in(self.user))

    @patch("whatsapp.webhook.config", _config_de_test({}))
    def test_secret_non_configure_refuse_meme_une_notification_bien_formee(self):
        """Défaut fermé : sans secret, rien ne distingue Meta d'un tiers."""
        response = self._post(self.corps, self._signer(self.corps))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(is_opted_in(self.user))

    @patch("whatsapp.webhook.config", _config_de_test({"WHATSAPP_APP_SECRET": APP_SECRET}))
    def test_corps_illisible_repond_200_pour_ne_pas_faire_retenter_meta(self):
        corps = b"{ pas du json"

        response = self._post(corps, self._signer(corps))

        self.assertEqual(response.status_code, 200)
