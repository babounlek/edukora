"""
La recherche de cours ne tient pas compte des accents (passe élève Guyguy 2026-11-07) : « electricite » donnait
« Aucun cours ne correspond » alors que « électricité » en trouvait 46. Sur Android, on écrit presque toujours sans
accents. La recherche d'épreuves le faisait déjà (voir catalog.recherche_titre) ; celle des cours s'y aligne.
"""
from django.test import TestCase
from django.urls import reverse

from .models import Cours, StatutContenu, Subject


class CoursRechercheSansAccentTests(TestCase):
    def setUp(self):
        maths = Subject.objects.get(country__code="CM", code="MATHS")
        for titre in ("Électricité : le courant continu", "Les fractions"):
            Cours.objects.create(external_id=f"ext-{titre}", titre=titre, subject=maths, statut=StatutContenu.VALIDE)

    def _titres(self, terme):
        reponse = self.client.get(reverse("catalog:cours-list"), {"country": "cm", "search": terme})
        self.assertEqual(reponse.status_code, 200)
        return {c["titre"] for c in reponse.json()["results"]}

    def test_avec_ou_sans_accents_ou_en_majuscules_on_trouve_le_meme_cours(self):
        for terme in ("électricité", "electricite", "ELECTRICITE", "Électricité", "electricité"):
            self.assertEqual(self._titres(terme), {"Électricité : le courant continu"}, terme)

    def test_un_terme_absent_ne_renvoie_rien(self):
        self.assertEqual(self._titres("thermodynamique"), set())
