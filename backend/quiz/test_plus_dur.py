"""« Même thème, plus dur » (quiz.services.generer_session, plus_dur=True) : jamais une question faible."""
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Difficulte, Examen, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .models import QuizQuestion
from .tests import _make_competence_item


class PlusDurTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900888", password="x")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.subject = Subject.objects.create(code="MATHS_PLUS_DUR", label="Maths (plus dur)", country=self.cursus.country)
        self.theme = Tag.objects.create(name="thème plus dur")
        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=30)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def item(self, numero, difficulte):
        return _make_competence_item(self.subject, self.cursus, theme=self.theme, numero=numero, difficulte=difficulte)

    def demarrer(self, **extra):
        return self.client.post(
            "/quiz/sessions/", {"cursus": self.cursus.id, "theme": self.theme.id, "n": 3, "plus_dur": True, **extra}, format="json",
        )

    def difficultes(self, reponse):
        ids = [q["id"] for q in reponse.json()["questions"]]
        return sorted(QuizQuestion.objects.filter(id__in=ids).values_list("competence_item__difficulte_estimee", flat=True))

    def test_sert_les_elevees_d_abord_et_jamais_une_faible(self):
        for n in range(3):
            self.item(f"e{n}", Difficulte.ELEVEE)
        for n in range(3):
            self.item(f"f{n}", Difficulte.FAIBLE)

        reponse = self.demarrer()

        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(self.difficultes(reponse), [Difficulte.ELEVEE] * 3)

    def test_complete_par_des_moyennes_quand_les_elevees_manquent(self):
        self.item("e0", Difficulte.ELEVEE)
        for n in range(3):
            self.item(f"m{n}", Difficulte.MOYENNE)
        self.item("f0", Difficulte.FAIBLE)

        reponse = self.demarrer()

        self.assertEqual(reponse.status_code, 201)
        self.assertNotIn(Difficulte.FAIBLE, self.difficultes(reponse))
        self.assertIn(Difficulte.ELEVEE, self.difficultes(reponse))

    def test_un_theme_sans_question_plus_dure_repond_une_phrase_claire(self):
        for n in range(3):
            self.item(f"f{n}", Difficulte.FAIBLE)

        reponse = self.demarrer()

        self.assertEqual(reponse.status_code, 404)
        self.assertIn("plus difficile", reponse.json()["error"])

    def test_sans_plus_dur_le_tirage_est_inchange(self):
        for n in range(3):
            self.item(f"f{n}", Difficulte.FAIBLE)

        reponse = self.demarrer(plus_dur=False)

        self.assertEqual(reponse.status_code, 201)
