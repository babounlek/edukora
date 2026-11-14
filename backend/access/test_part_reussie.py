"""« Qu'as-tu réussi ? » : la part d'un exercice que l'élève déclare avoir réussie (voir ExerciceFait.part_reussie)."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Lesson, LessonType, StatutContenu, Subject, Tag
from quiz.tests import _make_question
from subscriptions.models import Subscription
from users.models import User

from .models import ExerciceFait


class PartReussieTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900888", password="x")
        self.profil = self.user.profils.first()
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2023", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.question = _make_question(self.lesson, "1")
        self.exercice = self.question.exercise
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def marquer(self, **corps):
        return self.client.post(f"/access/exercices/{self.exercice.pk}/fait/", corps, format="json")

    def test_dire_l_avoir_fait_ne_note_rien(self):
        reponse = self.marquer()

        self.assertEqual(reponse.status_code, 200)
        self.assertIsNone(reponse.data["part_reussie"])
        self.assertIsNone(ExerciceFait.objects.get().part_reussie)

    def test_la_part_declaree_s_enregistre_et_se_corrige(self):
        self.assertEqual(self.marquer(part_reussie=50).data["part_reussie"], 50)
        self.assertEqual(self.marquer(part_reussie=100).data["part_reussie"], 100)

        trace = ExerciceFait.objects.get()
        self.assertEqual(trace.part_reussie, 100)

    def test_se_noter_vaut_declaration_et_ne_rapporte_les_points_qu_une_fois(self):
        premiere = self.marquer(part_reussie=75)
        seconde = self.marquer(part_reussie=0)

        self.assertTrue(premiere.data["fait"])
        self.assertGreater(premiere.data["xp_gagne"], 0)
        self.assertEqual(seconde.data["xp_gagne"], 0)
        self.assertEqual(ExerciceFait.objects.count(), 1)

    def test_redire_l_avoir_fait_garde_la_part_deja_declaree(self):
        self.marquer(part_reussie=75)

        self.assertEqual(self.marquer().data["part_reussie"], 75)

    def test_revenir_sur_sa_declaration_efface_aussi_la_part(self):
        self.marquer(part_reussie=75)

        reponse = self.marquer(fait=False)

        self.assertFalse(reponse.data["fait"])
        self.assertIsNone(reponse.data["part_reussie"])
        self.assertFalse(ExerciceFait.objects.exists())

    def test_une_part_hors_echelle_est_refusee(self):
        for valeur in (30, -1, 101, "tout", True):
            self.assertEqual(self.marquer(part_reussie=valeur).status_code, 400, valeur)
        self.assertFalse(ExerciceFait.objects.exists())

    def test_le_lecteur_d_epreuve_rend_la_part_de_chaque_exercice(self):
        autre = _make_question(self.lesson, "2").exercise
        self.marquer(part_reussie=50)

        exercices = {e["id"]: e for e in self.client.get(f"/access/read/{self.lesson.slug}/").data["exercises"]}

        self.assertTrue(exercices[self.exercice.pk]["fait"])
        self.assertEqual(exercices[self.exercice.pk]["part_reussie"], 50)
        self.assertFalse(exercices[autre.pk]["fait"])
        self.assertIsNone(exercices[autre.pk]["part_reussie"])

    def test_le_lecteur_par_theme_rend_la_part(self):
        theme = Tag.objects.create(name="dérivation (part réussie)")
        self.question.themes.add(theme)
        self.marquer(part_reussie=100)

        reponse = self.client.get(f"/catalog/themes/{theme.pk}/exercices/{self.exercice.pk}/lecture/")

        self.assertEqual(reponse.status_code, 200, reponse.data)
        self.assertTrue(reponse.data["exercise"]["fait"])
        self.assertEqual(reponse.data["exercise"]["part_reussie"], 100)
