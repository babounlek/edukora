from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import TestCase

from .models import User


class LangueDuCompteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone_number="677200090", password="x")
        access = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_francais_par_defaut_et_exposee_par_me(self):
        self.assertEqual(self.user.langue, "fr")
        self.assertEqual(self.client.get("/auth/me/").data["langue"], "fr")

    def test_l_eleve_choisit_l_anglais(self):
        reponse = self.client.patch("/auth/me/", {"langue": "en"}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["langue"], "en")
        self.user.refresh_from_db()
        self.assertEqual(self.user.langue, "en")

    def test_langue_inconnue_refusee(self):
        reponse = self.client.patch("/auth/me/", {"langue": "de"}, format="json")
        self.assertEqual(reponse.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.langue, "fr")

    def test_changer_la_langue_ne_touche_pas_au_reste(self):
        self.user.full_name = "Awa Ndiaye"
        self.user.save(update_fields=["full_name"])
        self.client.patch("/auth/me/", {"langue": "en"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Awa Ndiaye")
