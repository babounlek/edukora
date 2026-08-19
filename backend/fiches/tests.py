"""
Couvre les deux risques principaux du chantier "Outil Fiches pour répétiteurs" :
- la sélection (fiches.services.generer_fiche/themes_eligibles), garde-fou anti-fiche-
  vide et respect des filtres (thème/difficulté) ;
- le gating (create_fiche exige has_access_fiches, les sous-endpoints n'exigent que
  l'ownership, même compromis que inedit/quiz - voir leurs docstrings de module).

queue_fiche_pdf_generation (Popen d'un vrai processus détaché lançant Chromium) est
systématiquement mocké dans les tests d'API : jamais de génération PDF réelle ici, ce
n'est pas ce que ces tests couvrent (voir fiches.pdf, hors ligne par construction).
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Difficulte, Examen, StatutContenu, Subject, Tag, TypeReponse
from quiz.models import CompetenceItem
from subscriptions.models import InscriptionRepetiteur
from users.models import User

from .models import FicheGeneree, FicheItem, StatutGeneration
from .pdf import _combined_markdown
from .services import generer_fiche, themes_eligibles


def _make_competence_item(subject, cursus, theme, difficulte=Difficulte.MOYENNE, numero="1", **kwargs):
    """Même fixture que quiz.tests._make_competence_item - dupliquée plutôt qu'importée
    pour ne pas coupler ce module de tests à l'organisation interne de quiz.tests."""
    kwargs.setdefault("statut", StatutContenu.VALIDE)
    kwargs.setdefault("enonce_markdown", f"Énoncé {numero}.")
    kwargs.setdefault("corrige_markdown", f"Corrigé {numero}.")
    item = CompetenceItem.objects.create(
        theme=theme, subject=subject,
        difficulte_estimee=difficulte, type_reponse=TypeReponse.OUVERTE, **kwargs,
    )
    item.cursus.add(cursus)
    return item


class ThemesEligiblesTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")

    def test_counts_only_valide_items_for_this_theme(self):
        _make_competence_item(self.subject, self.cursus, self.theme, numero="1")
        _make_competence_item(self.subject, self.cursus, self.theme, numero="2", difficulte=Difficulte.ELEVEE)
        _make_competence_item(self.subject, self.cursus, self.theme, numero="3", statut=StatutContenu.BROUILLON)

        result = themes_eligibles(self.cursus, self.subject)

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry["theme_id"], self.theme.id)
        self.assertEqual(entry["total"], 2)
        self.assertEqual(entry["par_difficulte"], {Difficulte.MOYENNE: 1, Difficulte.ELEVEE: 1})

    def test_theme_without_any_valide_item_is_absent(self):
        _make_competence_item(self.subject, self.cursus, self.theme, statut=StatutContenu.BROUILLON)

        self.assertEqual(themes_eligibles(self.cursus, self.subject), [])

    def test_ignores_items_from_another_cursus(self):
        autre_series = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        _make_competence_item(self.subject, autre_series, self.theme)

        self.assertEqual(themes_eligibles(self.cursus, self.subject), [])


class GenererFicheTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.user = User.objects.create_user(phone_number="677300001", password="x")

    def test_raises_when_pool_is_empty(self):
        with self.assertRaises(ValueError):
            generer_fiche(
                user=self.user, cursus=self.cursus, subject=self.subject, themes=[self.theme],
                difficulte="", n=5, titre="Fiche vide",
            )

    def test_creates_fiche_with_requested_items_in_order(self):
        for i in range(3):
            _make_competence_item(self.subject, self.cursus, self.theme, numero=str(i))

        fiche = generer_fiche(
            user=self.user, cursus=self.cursus, subject=self.subject, themes=[self.theme],
            difficulte="", n=2, titre="Ma fiche",
        )

        self.assertEqual(fiche.owner, self.user)
        self.assertEqual(fiche.statut, StatutGeneration.EN_COURS)
        self.assertEqual(fiche.nombre_questions, 2)
        self.assertEqual(list(fiche.themes.all()), [self.theme])
        items = list(FicheItem.objects.filter(fiche=fiche).order_by("ordre"))
        self.assertEqual(len(items), 2)
        self.assertEqual([fi.ordre for fi in items], [1, 2])

    def test_filters_by_difficulte(self):
        _make_competence_item(self.subject, self.cursus, self.theme, numero="1", difficulte=Difficulte.FAIBLE)
        _make_competence_item(self.subject, self.cursus, self.theme, numero="2", difficulte=Difficulte.ELEVEE)

        fiche = generer_fiche(
            user=self.user, cursus=self.cursus, subject=self.subject, themes=[self.theme],
            difficulte=Difficulte.ELEVEE, n=5, titre="Fiche difficile",
        )

        self.assertEqual(fiche.nombre_questions, 1)
        item = FicheItem.objects.get(fiche=fiche).competence_item
        self.assertEqual(item.difficulte_estimee, Difficulte.ELEVEE)


class CombinedMarkdownTests(TestCase):
    """
    Contenu des deux PDF avant rendu (fiches.pdf._combined_markdown) - le rendu
    Playwright lui-même reste hors tests, voir la docstring de module.
    """

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.user = User.objects.create_user(phone_number="677300010", password="x")
        self.fiche = FicheGeneree.objects.create(
            owner=self.user, cursus=self.cursus, subject=self.subject, titre="Ma fiche", nombre_questions=1,
        )

    def _ajouter_item(self, *, ordre=1, **kwargs):
        item = _make_competence_item(self.subject, self.cursus, self.theme, numero=str(ordre), **kwargs)
        return FicheItem.objects.create(fiche=self.fiche, competence_item=item, ordre=ordre)

    def test_sujet_ne_contient_que_les_enonces(self):
        self._ajouter_item()

        markdown_text = _combined_markdown(self.fiche, avec_corrige=False)

        self.assertIn("## Question 1", markdown_text)
        self.assertIn("Énoncé 1.", markdown_text)
        self.assertNotIn("Corrigé 1.", markdown_text)

    def test_corrige_rappelle_lenonce_avant_la_solution(self):
        self._ajouter_item(
            corrige_markdown="### Rappel de méthode\n\nOn dérive.\n\n### Corrigé\n\nRésultat.",
        )

        markdown_text = _combined_markdown(self.fiche, avec_corrige=True)

        self.assertLess(markdown_text.index("## Question 1"), markdown_text.index("Énoncé 1."))
        self.assertLess(markdown_text.index("Énoncé 1."), markdown_text.index("### Rappel de méthode"))
        self.assertLess(markdown_text.index("### Rappel de méthode"), markdown_text.index("### Corrigé"))

    def test_corrige_sans_titre_recoit_un_titre_de_section(self):
        self._ajouter_item()

        markdown_text = _combined_markdown(self.fiche, avec_corrige=True)

        self.assertLess(markdown_text.index("Énoncé 1."), markdown_text.index("### Corrigé"))
        self.assertLess(markdown_text.index("### Corrigé"), markdown_text.index("Corrigé 1."))

    def test_les_questions_suivent_lordre_de_la_fiche(self):
        self._ajouter_item(ordre=2)
        self._ajouter_item(ordre=1)

        markdown_text = _combined_markdown(self.fiche, avec_corrige=True)

        self.assertLess(markdown_text.index("## Question 1"), markdown_text.index("## Question 2"))


class FichesApiTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        _make_competence_item(self.subject, self.cursus, self.theme, numero="1")

        self.user = User.objects.create_user(phone_number="677300002", password="x")
        self.client = APIClient()

    def _grant_access(self):
        InscriptionRepetiteur.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )

    def test_create_fiche_requires_authentication(self):
        response = self.client.post("/fiches/", {"cursus": self.cursus.id}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_create_fiche_denied_without_inscription_repetiteur(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/fiches/",
            {"cursus": self.cursus.id, "subject": self.subject.id, "themes": [self.theme.id], "n": 1, "titre": "X"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    @patch("fiches.views.queue_fiche_pdf_generation")
    def test_create_fiche_succeeds_with_active_access(self, mock_queue):
        self._grant_access()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/fiches/",
            {"cursus": self.cursus.id, "subject": self.subject.id, "themes": [self.theme.id], "n": 1, "titre": "X"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["statut"], StatutGeneration.EN_COURS)
        self.assertEqual(response.data["nombre_questions"], 1)
        mock_queue.assert_called_once()

    @patch("fiches.views.queue_fiche_pdf_generation")
    def test_create_fiche_rejects_empty_pool(self, mock_queue):
        self._grant_access()
        self.client.force_authenticate(user=self.user)
        autre_theme = Tag.objects.create(name="sans-item")

        response = self.client.post(
            "/fiches/",
            {"cursus": self.cursus.id, "subject": self.subject.id, "themes": [autre_theme.id], "n": 1, "titre": "X"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        mock_queue.assert_not_called()

    def test_eligibilite_returns_theme_counts(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/fiches/eligibilite/?cursus={self.cursus.id}&subject={self.subject.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["theme_id"], self.theme.id)
        self.assertEqual(response.data[0]["total"], 1)

    def test_fiche_detail_is_scoped_to_owner(self):
        self._grant_access()
        fiche = generer_fiche(
            user=self.user, cursus=self.cursus, subject=self.subject, themes=[self.theme],
            difficulte="", n=1, titre="X",
        )
        autre_user = User.objects.create_user(phone_number="677300003", password="x")
        self.client.force_authenticate(user=autre_user)

        response = self.client.get(f"/fiches/{fiche.id}/")

        self.assertEqual(response.status_code, 404)

    def test_download_returns_404_before_pdf_is_generated(self):
        self._grant_access()
        fiche = generer_fiche(
            user=self.user, cursus=self.cursus, subject=self.subject, themes=[self.theme],
            difficulte="", n=1, titre="X",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/fiches/{fiche.id}/sujet.pdf")

        self.assertEqual(response.status_code, 404)
