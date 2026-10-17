"""
GET /catalog/cours/titres/?slugs=a,b,c : les titres de plusieurs cours en une requête.

Sert au lecteur d'épreuve : les marqueurs `[COURS_LINK:<slug>]` du corrigé ne portent que le slug, donc
deux boutons « Voir le cours complet » côte à côte étaient indiscernables. Le frontend demande les titres
des slugs présents dans la page, en un seul appel.
"""
from django.test import TestCase
from django.urls import reverse

from .models import Cours, Subject


class CoursTitresTests(TestCase):
    def setUp(self):
        self.matiere = Subject.objects.get(code="GCE_MATHS")
        self.url = reverse("catalog:cours-titres")

    def _cours(self, titre, statut="VALIDE"):
        return Cours.objects.create(
            external_id=f"cours-test-{titre}", titre=titre, subject=self.matiere, statut=statut,
            content_markdown="Contenu.",
        )

    def test_renvoie_le_titre_de_chaque_slug_demande_sans_connexion(self):
        a, b = self._cours("Statistics: mean and median"), self._cours("Vectors: sums and ratios")

        reponse = self.client.get(self.url, {"slugs": f"{a.slug},{b.slug}"})

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json(), {"titres": {a.slug: a.titre, b.slug: b.titre}})

    def test_slug_inconnu_ou_cours_non_publie_absent_de_la_reponse(self):
        publie = self._cours("Publie")
        brouillon = self._cours("Brouillon", statut="BROUILLON")

        reponse = self.client.get(self.url, {"slugs": f"{publie.slug},{brouillon.slug},n-existe-pas"})

        self.assertEqual(reponse.json(), {"titres": {publie.slug: publie.titre}})

    def test_aucun_slug_donne_une_reponse_vide(self):
        reponse = self.client.get(self.url)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json(), {"titres": {}})

    def test_nombre_de_slugs_borne(self):
        cours = [self._cours(f"Cours {i}") for i in range(61)]

        reponse = self.client.get(self.url, {"slugs": ",".join(c.slug for c in cours)})

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(len(reponse.json()["titres"]), 60)  # les 60 premiers slugs seulement
