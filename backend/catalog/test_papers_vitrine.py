"""Papers gratuits de l'A Level (voir catalog.management.commands.definir_papers_vitrine) : la commande ne touche
que sa sélection, ne casse jamais un paper gratuit posé à la main, et refuse une sélection périmée."""
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .management.commands.definir_papers_vitrine import SELECTION
from .models import Country, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject


class PapersVitrineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cm = Country.objects.get_or_create(code="CM", defaults={"label": "Cameroun"})[0]
        cls.cursus_al = Cursus.objects.get_or_create(country=cm, examen=Examen.GCE_AL, series=None)[0]
        cls.cursus_ol = Cursus.objects.get_or_create(country=cm, examen=Examen.GCE_OL, series=None)[0]
        cls.matiere = Subject.objects.create(country=cm, code="GCE_PHYSICS_T", label="Physics", langue="en")
        cls.papiers = {}
        for _, _, titre in SELECTION:
            lesson = Lesson.objects.create(
                title=titre, subject=cls.matiere, lesson_type=LessonType.CORR, year=2023, statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(cls.cursus_al)
            cls.papiers[titre] = lesson
        # Un paper gratuit posé à la main (O Level), et un paper A Level hors sélection.
        cls.gratuit_a_la_main = Lesson.objects.create(
            title="Physics GCE O Level 2023 - Paper 1", subject=cls.matiere, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, est_vitrine=True,
        )
        cls.gratuit_a_la_main.cursus.add(cls.cursus_ol)
        cls.hors_selection = Lesson.objects.create(
            title="Physics GCE A Level 2023 - Paper 1", subject=cls.matiere, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )
        cls.hors_selection.cursus.add(cls.cursus_al)

    def _vitrine(self, lesson):
        lesson.refresh_from_db()
        return lesson.est_vitrine

    def _lancer(self, *args):
        sortie = StringIO()
        call_command("definir_papers_vitrine", *args, stdout=sortie)
        return sortie.getvalue()

    def test_la_selection_a_un_paper_par_matiere_a_level(self):
        self.assertEqual(len(SELECTION), 4)
        self.assertEqual({examen for _, examen, _ in SELECTION}, {"GCE_AL"})
        self.assertEqual({titre.split(" GCE")[0] for _, _, titre in SELECTION},
                         {"Biology", "Chemistry", "Further Mathematics", "Physics"})

    def test_simulation_n_ecrit_rien(self):
        sortie = self._lancer()
        self.assertIn("simulation", sortie)
        self.assertFalse(any(self._vitrine(p) for p in self.papiers.values()))

    def test_appliquer_ne_coche_que_la_selection(self):
        self._lancer("--appliquer")
        self.assertTrue(all(self._vitrine(p) for p in self.papiers.values()))
        self.assertFalse(self._vitrine(self.hors_selection))
        self.assertTrue(self._vitrine(self.gratuit_a_la_main))

    def test_appliquer_deux_fois_est_idempotent(self):
        self._lancer("--appliquer")
        sortie = self._lancer("--appliquer")
        self.assertEqual(sortie.count("déjà gratuit"), len(SELECTION))

    def test_retirer_ne_decoche_que_la_selection(self):
        self._lancer("--appliquer")
        self._lancer("--retirer")
        self.assertFalse(any(self._vitrine(p) for p in self.papiers.values()))
        self.assertTrue(self._vitrine(self.gratuit_a_la_main))

    def test_un_paper_non_publie_ou_absent_fait_echouer_sans_rien_ecrire(self):
        titre = SELECTION[-1][2]
        brouillon = self.papiers[titre]
        brouillon.statut = StatutContenu.BROUILLON
        brouillon.save(update_fields=["statut"])
        with self.assertRaises(CommandError):
            self._lancer("--appliquer")
        self.assertFalse(any(self._vitrine(p) for p in self.papiers.values()))
