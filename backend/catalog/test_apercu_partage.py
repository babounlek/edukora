"""Aperçu des liens partagés (voir catalog.apercu_partage) : balises propres au contenu pour les
robots de WhatsApp & co., repli générique sinon, et image PNG à la demande."""
from django.test import TestCase

from .apercu_partage import LARGEUR, HAUTEUR, infos_page
from .models import Cours, Country, Lesson, LessonType, StatutContenu, Subject


class ApercuPartageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pays = Country.objects.create(code="cm", label="Cameroun", dial_code="+237", currency="XAF")
        cls.matiere = Subject.objects.create(country=pays, code="MATHS", label="Mathématiques")
        cls.lesson = Lesson.objects.create(
            title="Maths BAC C 2023", subject=cls.matiere, lesson_type=LessonType.CORR, year=2023, statut=StatutContenu.VALIDE,
        )
        cls.brouillon = Lesson.objects.create(
            title="Maths secrètes", subject=cls.matiere, lesson_type=LessonType.CORR, statut=StatutContenu.BROUILLON,
        )
        cls.cours = Cours.objects.create(
            external_id="cours-derivation", titre="Dériver une fonction", subject=cls.matiere,
            sous_theme="Dérivation", statut=StatutContenu.VALIDE,
        )

    def test_page_d_epreuve_porte_titre_et_image_du_contenu(self):
        html = self.client.get(f"/partage-apercu/cm/epreuves/{self.lesson.slug}").content.decode()
        self.assertIn('og:title" content="Maths BAC C 2023 |', html)
        self.assertIn(f"/partage-image/epreuves/{self.lesson.slug}.png", html)
        self.assertIn('twitter:card" content="summary_large_image"', html)
        self.assertIn(f"/cm/epreuves/{self.lesson.slug}", html)

    def test_le_lecteur_pointe_vers_la_fiche_publique(self):
        infos = infos_page(f"cours/{self.cours.slug}/lire")
        self.assertEqual(infos["chemin"], f"cours/{self.cours.slug}")

    def test_page_de_cours(self):
        html = self.client.get(f"/partage-apercu/cours/{self.cours.slug}").content.decode()
        self.assertIn("Dériver une fonction", html)
        self.assertIn("Dérivation", html)

    def test_contenu_non_publie_ou_inconnu_retombe_sur_l_aperçu_generique(self):
        for chemin in (f"cm/epreuves/{self.brouillon.slug}", "cm/epreuves/n-existe-pas", "cm/epreuves"):
            html = self.client.get(f"/partage-apercu/{chemin}").content.decode()
            self.assertNotIn("Maths secrètes", html)
            self.assertIn("/partage-image/defaut.png", html)

    def test_le_titre_est_echappe(self):
        piege = Lesson.objects.create(
            title='<script>alert("x")</script>', subject=self.matiere, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        html = self.client.get(f"/partage-apercu/cm/epreuves/{piege.slug}").content.decode()
        self.assertNotIn("<script>", html)

    def test_image_png_aux_dimensions_attendues(self):
        from io import BytesIO

        from PIL import Image

        for url in (f"/partage-image/epreuves/{self.lesson.slug}.png", f"/partage-image/cours/{self.cours.slug}.png", "/partage-image/defaut.png"):
            reponse = self.client.get(url)
            self.assertEqual(reponse.status_code, 200, url)
            self.assertEqual(reponse["Content-Type"], "image/png")
            self.assertEqual(Image.open(BytesIO(reponse.content)).size, (LARGEUR, HAUTEUR))

    def test_image_d_un_contenu_non_publie_ou_inconnu_est_404(self):
        self.assertEqual(self.client.get(f"/partage-image/epreuves/{self.brouillon.slug}.png").status_code, 404)
        self.assertEqual(self.client.get("/partage-image/epreuves/n-existe-pas.png").status_code, 404)
        self.assertEqual(self.client.get("/partage-image/inconnu/x.png").status_code, 404)
