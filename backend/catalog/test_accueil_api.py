"""La route unique de l'accueil (voir catalog.accueil_api) : ses chiffres sont ceux des listes, par construction."""
from django.test import TestCase

from .models import Country, Cours, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject, Temoignage


class AccueilApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pays, _ = Country.objects.get_or_create(
            code="CM", defaults={"label": "Cameroun", "dial_code": "+237", "currency": "XAF"},
        )
        bepc, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.BEPC, series=None)
        gce, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.GCE_OL, series=None)
        maths = Subject.objects.create(country=pays, code="ACC_MATHS", label="Mathématiques", langue="fr")
        anglais = Subject.objects.create(country=pays, code="ACC_GCE", label="Mathematics", langue="en")
        for titre, sujet, annee, cursus in (
            ("Maths BEPC 2026", maths, 2026, bepc), ("Maths BEPC 2025", maths, 2025, bepc),
            ("Mathematics GCE O Level 2019", anglais, 2019, gce),
        ):
            lesson = Lesson.objects.create(
                title=titre, subject=sujet, lesson_type=LessonType.CORR, year=annee, statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(cursus)
        # Un brouillon ne compte pas, ni ici ni dans la liste.
        Lesson.objects.create(title="Brouillon", subject=maths, lesson_type=LessonType.CORR, year=2023).cursus.add(bepc)

    def _accueil(self, langue):
        return self.client.get(f"/catalog/accueil/?country=cm&langue={langue}").json()

    def test_les_chiffres_sont_ceux_des_listes(self):
        for langue in ("fr", "en"):
            accueil = self._accueil(langue)
            epreuves = self.client.get(f"/catalog/lessons/?country=cm&langue={langue}").json()
            cours = self.client.get(f"/catalog/cours/?country=cm&langue={langue}").json()
            matieres = self.client.get(f"/catalog/subjects/?country=cm&langue={langue}").json()
            self.assertEqual(accueil["epreuves"], epreuves["count"], langue)
            self.assertEqual(accueil["cours"], cours["count"], langue)
            self.assertEqual(accueil["matieres"], len(matieres), langue)

    def test_chaque_langue_a_ses_epreuves(self):
        self.assertEqual(self._accueil("fr")["epreuves"], 2)
        self.assertEqual(self._accueil("en")["epreuves"], 1)

    def test_les_temoignages_sont_ceux_de_la_route_publique(self):
        self.assertEqual(self._accueil("fr")["temoignages"], self.client.get("/catalog/temoignages/").json())

    def test_ouverte_sans_connexion(self):
        self.assertEqual(self.client.get("/catalog/accueil/?country=cm&langue=fr").status_code, 200)

    def test_modeles_utilises_par_la_route_existent(self):
        # Garde-fou d'import : la route s'appuie sur ces modèles à travers les vues des listes.
        self.assertTrue(all(m is not None for m in (Cours, Temoignage)))
