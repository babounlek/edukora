from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Cursus, Examen, ExamSession


class CursusCompteAReboursPublicTests(TestCase):
    """Le décompte jusqu'à l'examen est offert à un visiteur qui a choisi son examen sans compte : même calcul que /auth/me/."""

    def setUp(self):
        # Référentiel déjà seedé par les migrations catalog - récupéré, jamais recréé (voir users.tests).
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.client = APIClient()  # anonyme

    def _url(self, cursus=None):
        return f"/catalog/cursus/{(cursus or self.cursus).pk}/compte-a-rebours/"

    def _sessions(self, *, date_debut):
        ExamSession.objects.filter(country=self.cursus.country, examen=self.cursus.examen).delete()
        ExamSession.objects.create(
            country=self.cursus.country, examen=self.cursus.examen, annee=date_debut.year, date_debut=date_debut,
        )

    def test_un_visiteur_recoit_le_decompte_de_la_prochaine_session(self):
        self._sessions(date_debut=(timezone.now() + timedelta(days=60)).date())

        reponse = self.client.get(self._url())

        self.assertEqual(reponse.status_code, 200)
        self.assertIn(reponse.data["jours_restants"], (59, 60))
        self.assertFalse(reponse.data["estimee"])

    def test_la_date_de_fin_reste_interne(self):
        self._sessions(date_debut=(timezone.now() + timedelta(days=60)).date())

        reponse = self.client.get(self._url())

        self.assertEqual(set(reponse.data), {"date_examen", "jours_restants", "session_label", "estimee"})

    def test_une_session_passee_donne_une_date_estimee(self):
        self._sessions(date_debut=(timezone.now() - timedelta(days=30)).date())

        reponse = self.client.get(self._url())

        self.assertTrue(reponse.data["estimee"])
        self.assertGreater(reponse.data["jours_restants"], 0)

    def test_aucune_session_saisie_donne_null(self):
        ExamSession.objects.filter(country=self.cursus.country, examen=self.cursus.examen).delete()

        reponse = self.client.get(self._url())

        self.assertEqual(reponse.status_code, 200)
        self.assertIsNone(reponse.data)

    def test_un_cursus_inconnu_ou_dun_pays_desactive_est_introuvable(self):
        self.assertEqual(self.client.get("/catalog/cursus/999999/compte-a-rebours/").status_code, 404)

        pays = self.cursus.country
        pays.actif = False
        pays.save(update_fields=["actif"])
        self.assertEqual(self.client.get(self._url()).status_code, 404)
