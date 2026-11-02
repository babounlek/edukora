"""Papers gratuits francophones (voir catalog.management.commands.definir_papers_vitrine_francophone)."""
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .management.commands.definir_papers_vitrine_francophone import SELECTION
from .models import Country, Cursus, Lesson, LessonType, StatutContenu, Subject


class PapersVitrineFrancophoneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pays = {}
        cls.matiere = {}
        cls.papiers = {}
        for code, examen, titre in SELECTION:
            if code not in cls.pays:
                pays = Country.objects.get_or_create(code=code, defaults={"label": code})[0]
                cls.pays[code] = pays
                cls.matiere[code] = Subject.objects.create(country=pays, code="T_MATIERE", label="Matière")
            cursus = Cursus.objects.get_or_create(country=cls.pays[code], examen=examen, series=None)[0]
            lesson = Lesson.objects.create(
                title=titre, subject=cls.matiere[code], lesson_type=LessonType.CORR, year=2023,
                statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(cursus)
            cls.papiers[(code, examen, titre)] = lesson

    def _lancer(self, *args):
        sortie = StringIO()
        call_command("definir_papers_vitrine_francophone", *args, stdout=sortie)
        return sortie.getvalue()

    def _vitrine(self, lesson):
        lesson.refresh_from_db()
        return lesson.est_vitrine

    def test_la_selection_n_a_pas_de_doublon_et_reste_francophone(self):
        self.assertEqual(len(SELECTION), len(set(SELECTION)))
        self.assertTrue(all(examen in {"BEPC", "PROBATOIRE", "BAC"} for _, examen, _ in SELECTION))

    def test_simulation_n_ecrit_rien(self):
        self.assertIn("simulation", self._lancer())
        self.assertFalse(any(self._vitrine(l) for l in self.papiers.values()))

    def test_appliquer_puis_retirer(self):
        self._lancer("--appliquer")
        self.assertTrue(all(self._vitrine(l) for l in self.papiers.values()))
        self._lancer("--retirer")
        self.assertFalse(any(self._vitrine(l) for l in self.papiers.values()))

    def test_selection_perimee_est_refusee(self):
        Lesson.objects.filter(title=SELECTION[0][2]).update(statut=StatutContenu.BROUILLON)
        with self.assertRaises(CommandError):
            self._lancer("--appliquer")
