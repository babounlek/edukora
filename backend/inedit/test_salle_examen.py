"""Salle d'examen : mode papier, choisi au lancement du chrono."""

from .models import EpreuveInedite
from .test_notation import NotationAPITestCase


class ModePapierTests(NotationAPITestCase):
    def lancer(self, **corps):
        return self.client.post(self.url("mode-examen"), corps, format="json")

    def donner_un_sujet_pdf(self):
        EpreuveInedite.objects.filter(pk=self.epreuve.pk).update(sujet_pdf="cm/sujet-test.pdf")

    def test_par_defaut_le_mode_examen_n_est_pas_un_mode_papier(self):
        reponse = self.lancer()

        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(reponse.data["mode_papier"])
        self.assertIsNotNone(reponse.data["exam_mode_started_at"])

    def test_le_mode_papier_exige_un_sujet_pdf(self):
        reponse = self.lancer(papier=True)

        self.assertEqual(reponse.status_code, 400)
        self.tentative.refresh_from_db()
        self.assertIsNone(self.tentative.exam_mode_started_at)

    def test_le_mode_papier_est_enregistre_et_expose(self):
        self.donner_un_sujet_pdf()

        reponse = self.lancer(papier=True)

        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.data["mode_papier"])
        self.tentative.refresh_from_db()
        self.assertTrue(self.tentative.mode_papier)
        self.assertTrue(self.client.get(self.detail_url).data["mode_papier"])

    def test_le_choix_ne_change_plus_une_fois_le_chrono_lance(self):
        self.donner_un_sujet_pdf()
        self.lancer()

        reponse = self.lancer(papier=True)

        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(reponse.data["mode_papier"])

    def test_le_corrige_reste_masque_en_mode_papier(self):
        self.donner_un_sujet_pdf()
        self.lancer(papier=True)

        data = self.client.get(self.detail_url).data

        self.assertFalse(data["correction_disponible"])
        for question in data["exercices"][0]["questions"]:
            self.assertNotIn("corrige_markdown", question)


class ModeDansLeResultatTests(NotationAPITestCase):
    def rendre(self):
        return self.client.post(self.url("completer")).data

    def test_une_epreuve_libre(self):
        self.assertEqual(self.rendre()["mode"], "libre")

    def test_une_epreuve_en_conditions_reelles(self):
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.assertEqual(self.rendre()["mode"], "examen")

    def test_une_epreuve_sur_papier(self):
        EpreuveInedite.objects.filter(pk=self.epreuve.pk).update(sujet_pdf="cm/sujet-test.pdf")
        self.client.post(self.url("mode-examen"), {"papier": True}, format="json")
        self.assertEqual(self.rendre()["mode"], "papier")
