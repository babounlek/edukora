"""completer_points_gce : écrit le total des points d'un exercice GCE quand toutes ses questions en ont, et rien d'autre."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Country, Cursus, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject


class CompleterPointsGceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cm = Country.objects.get_or_create(code="CM", defaults={"label": "Cameroun"})[0]
        cursus = Cursus.objects.get_or_create(country=cm, examen=Examen.GCE_AL, series=None)[0]
        matiere = Subject.objects.create(country=cm, code="GCE_ECON_T", label="Economics", langue="en")
        cls.paper2 = cls._epreuve(matiere, cursus, "Economics GCE A Level 2026 - Paper 2", 2)
        cls.paper1 = cls._epreuve(matiere, cursus, "Economics GCE A Level 2026 - Paper 1", 1)

        cls.complet = cls._exercice(cls.paper2, "1", "", [(3, "a (3 marks)"), (2, "b *[2 marks]*")])
        cls.incomplet = cls._exercice(cls.paper2, "2", "", [(5, "a (5 marks)"), (None, "b")])
        cls.deja_saisi = cls._exercice(cls.paper2, "3", "10", [(4, "a (4 marks)")])
        cls.decimal = cls._exercice(cls.paper2, "4", "", [(2, "a (2 marks)")])
        cls.divergent = cls._exercice(cls.paper2, "5", "", [(4, "a (6 marks)")])
        cls.qcm = cls._exercice(cls.paper1, "1", "", [(1, "Q1"), (1, "Q2")])

    @staticmethod
    def _epreuve(matiere, cursus, titre, paper):
        lesson = Lesson.objects.create(
            title=titre, subject=matiere, lesson_type=LessonType.CORR, year=2026, statut=StatutContenu.VALIDE,
            numero_paper=paper,
        )
        lesson.cursus.add(cursus)
        return lesson

    @staticmethod
    def _exercice(lesson, numero, points, questions):
        exercice = Exercise.objects.create(
            lesson=lesson, numero_exercice=numero, points=points, statut=StatutContenu.VALIDE,
        )
        for ordre, (pts, texte) in enumerate(questions, start=1):
            Question.objects.create(exercise=exercice, numero=str(ordre), ordre=ordre, enonce_markdown=texte, points=pts)
        return exercice

    def _lancer(self, *args):
        sortie = StringIO()
        call_command("completer_points_gce", *args, stdout=sortie)
        return sortie.getvalue()

    def _points(self, exercice):
        exercice.refresh_from_db()
        return exercice.points

    def test_la_simulation_n_ecrit_rien_et_le_dit(self):
        sortie = self._lancer()
        self.assertIn("simulation", sortie)
        self.assertEqual(self._points(self.complet), "")

    def test_appliquer_ecrit_la_somme_des_points_des_questions(self):
        self._lancer("--appliquer")
        self.assertEqual(self._points(self.complet), "5")
        self.assertEqual(self._points(self.divergent), "4")

    def test_un_exercice_dont_une_question_n_a_pas_de_points_reste_vide(self):
        sortie = self._lancer("--appliquer")
        self.assertEqual(self._points(self.incomplet), "")
        self.assertIn("exercices 2", sortie)
        self.assertIn("INCOMPLET", sortie)

    def test_un_total_deja_saisi_n_est_jamais_touche(self):
        self._lancer("--appliquer")
        self.assertEqual(self._points(self.deja_saisi), "10")

    def test_le_paper_1_n_est_pas_concerne(self):
        self._lancer("--appliquer")
        self.assertEqual(self._points(self.qcm), "")

    def test_le_rapport_donne_le_total_de_l_epreuve_et_signale_les_ecarts_de_lecture(self):
        sortie = self._lancer()
        # 5 (exercice 1) + 10 (saisi) + 2 + 4, l'exercice 2 incomplet n'est pas compté.
        self.assertIn("Economics GCE A Level 2026 - Paper 2 : total 21, 3 complété(s)", sortie)
        self.assertIn("à relire : 5 (4 points, 6 lus)", sortie)
        self.assertNotIn("Paper 1", sortie)

    def test_rejouer_ne_change_rien(self):
        self._lancer("--appliquer")
        sortie = self._lancer("--appliquer")
        self.assertEqual(self._points(self.complet), "5")
        self.assertTrue(sortie.splitlines()[-1].startswith("0 exercice(s) complété(s)"))
