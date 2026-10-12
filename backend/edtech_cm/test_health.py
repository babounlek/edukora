import os
from unittest import mock

from django.db.utils import OperationalError
from django.test import TestCase, override_settings


@override_settings(SECURE_SSL_REDIRECT=False)
class HealthzTests(TestCase):
    def test_ok_avec_version(self):
        with mock.patch.dict(os.environ, {"APP_VERSION": "abc1234"}):
            reponse = self.client.get("/healthz")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json(), {"status": "ok", "version": "abc1234"})

    def test_version_par_defaut(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("APP_VERSION", None)
            reponse = self.client.get("/healthz")
        self.assertEqual(reponse.json()["version"], "dev")

    def test_503_si_la_base_ne_repond_pas(self):
        connexion = mock.Mock()
        connexion.cursor.side_effect = OperationalError("down")
        with mock.patch("edtech_cm.health.connection", connexion):
            reponse = self.client.get("/healthz")
        self.assertEqual(reponse.status_code, 503)
        self.assertEqual(reponse.json()["status"], "db_indisponible")
