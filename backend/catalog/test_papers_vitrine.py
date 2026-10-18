"""Papers gratuits du GCE (voir catalog.management.commands.definir_papers_vitrine) : la commande ne touche
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
        for _, examen, titre in SELECTION:
            lesson = Lesson.objects.create(
                title=titre, subject=cls.matiere, lesson_type=LessonType.CORR, year=2023, statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(cls.cursus_al if examen == "GCE_AL" else cls.cursus_ol)
            cls.papiers[titre] = lesson
        # Un paper gratuit posé à la main (hors sélection), et un paper A Level hors sélection.
        cls.gratuit_a_la_main = Lesson.objects.create(
            title="Physics GCE O Level 2021 - Paper 1", subject=cls.matiere, lesson_type=LessonType.CORR,
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

    def test_la_selection_couvre_toutes_les_matieres_du_gce_une_fois(self):
        a_level = [titre for _, examen, titre in SELECTION if examen == "GCE_AL"]
        o_level = [titre for _, examen, titre in SELECTION if examen == "GCE_OL"]
        self.assertEqual(len(SELECTION), len({titre for _, _, titre in SELECTION}))
        matieres_al = [t.split(" GCE")[0] for t in a_level]
        matieres_ol = [t.split(" GCE")[0] for t in o_level]
        # Une seule fois par matière et par niveau : le paper gratuit est un échantillon, pas un lot.
        self.assertEqual(len(matieres_al), len(set(matieres_al)))
        self.assertEqual(len(matieres_ol), len(set(matieres_ol)))
        # Aucune matière du GCE sans paper gratuit : sinon elle paraît vide au visiteur qui la choisit.
        self.assertEqual(set(matieres_al), {
            "Biology", "Chemistry", "Computer Science", "Economics", "English Language", "Further Mathematics",
            "Geography", "Geology", "History", "ICT", "Philosophy", "Physics", "Pure Mathematics with Mechanics",
            "Pure Mathematics with Statistics", "Religious Studies", "Special Bilingual Education French",
        })
        self.assertEqual(set(matieres_ol), {
            "Additional Mathematics", "Biology", "Chemistry", "Citizenship Education", "Commerce", "Computer Science",
            "Economics", "English Language", "Food and Nutrition", "French", "Geography", "History", "Human Biology",
            "Mathematics", "Physics",
        })

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
