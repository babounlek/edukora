"""Cours qui « tombent souvent » : catalog.frequences_cours, la commande qui reconstruit
catalog.FrequenceCours, et sa lecture par /catalog/cours/ (champ tombe_souvent, filtre, tri)."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from quiz.services import SEUIL_MINIMUM_THEMES_PARCOURS

from .frequences_cours import PLANCHER_OR, recalculer_cursus, seuil_or
from .models import (
    Cours, Cursus, Examen, Exercise, FrequenceCours, Lesson, LessonType, Origine, Question, RappelDeMethode,
    StatutContenu, Subject, Tag,
)


def _epreuve(subject, cursus, titre, tags):
    """Une annale officielle VALIDE dont une question porte les `tags` ; renvoie son Exercise."""
    lesson = Lesson.objects.create(
        title=titre, subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
    )
    lesson.cursus.add(cursus)
    exercise = Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
    question = Question.objects.create(
        exercise=exercise, numero="1", ordre=1, enonce_markdown="Énoncé.", corrige_markdown="Corrigé.",
    )
    question.themes.add(*tags)
    return exercise


def _cours(subject, exercise, titre, tags):
    """Un cours VALIDE issu d'un rappel de méthode de `exercise` (la lignée qui le rattache au cursus)."""
    cours = Cours.objects.create(external_id=f"cours-{titre}", titre=titre, subject=subject, statut=StatutContenu.VALIDE)
    cours.tags.add(*tags)
    RappelDeMethode.objects.create(
        exercise=exercise, external_id=f"rappel-{titre}", competence=titre, contenu_markdown="x", cours=cours,
    )
    return cours


class SeuilOrTests(TestCase):
    def test_moins_de_quatre_frequences_ne_dore_rien(self):
        self.assertIsNone(seuil_or([90, 80, 70]))
        self.assertIsNone(seuil_or([None, None, None, None, None]))

    def test_retient_le_quart_superieur(self):
        self.assertEqual(seuil_or([90, 80, 70, 60, 50, 40, 35, 31]), 80)

    def test_ne_descend_pas_sous_le_plancher(self):
        self.assertEqual(seuil_or([20, 15, 10, 5, 4, 3, 2, 1]), PLANCHER_OR)


class RecalculTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.frequent = Tag.objects.create(name="theme-frequent")
        # Quatre thèmes classables (il en faut quatre pour qu'un quart supérieur existe), un seul très fréquent.
        self.autres = [Tag.objects.create(name=f"theme-moyen-{i}") for i in range(3)]
        self.exercices = []
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            tags = [self.frequent, *self.autres] if i < 2 else [self.frequent]
            self.exercices.append(_epreuve(self.subject, self.cursus, f"Annale {i}", tags))

    def test_un_cours_du_theme_frequent_est_retenu_avec_sa_frequence(self):
        cours = _cours(self.subject, self.exercices[0], "frequent", [self.frequent])

        par_matiere = recalculer_cursus(self.cursus)

        ligne = FrequenceCours.objects.get(cursus=self.cursus, cours=cours)
        self.assertEqual(ligne.frequence_pct, 100)
        self.assertEqual(ligne.nb_epreuves, SEUIL_MINIMUM_THEMES_PARCOURS)
        self.assertEqual(ligne.nb_sessions, SEUIL_MINIMUM_THEMES_PARCOURS)
        self.assertEqual(ligne.theme, "theme-frequent")
        self.assertEqual(par_matiere, {"MATHS": 1})

    def test_un_cours_d_un_theme_rare_n_a_pas_de_ligne(self):
        _cours(self.subject, self.exercices[0], "rare", [self.autres[0]])

        recalculer_cursus(self.cursus)

        self.assertFalse(FrequenceCours.objects.exists())

    def test_un_cours_sans_epreuve_source_dans_le_cursus_est_ecarte(self):
        # Ses tags correspondent au thème fréquent, mais rien ne le relie à une annale de ce cursus.
        cours = Cours.objects.create(external_id="cours-orphelin", titre="orphelin", subject=self.subject, statut=StatutContenu.VALIDE)
        cours.tags.add(self.frequent)

        recalculer_cursus(self.cursus)

        self.assertFalse(FrequenceCours.objects.filter(cours=cours).exists())

    def test_un_cours_brouillon_est_ecarte(self):
        cours = _cours(self.subject, self.exercices[0], "brouillon", [self.frequent])
        Cours.objects.filter(pk=cours.pk).update(statut=StatutContenu.BROUILLON)

        recalculer_cursus(self.cursus)

        self.assertFalse(FrequenceCours.objects.exists())

    def test_le_recalcul_remplace_les_lignes_au_lieu_de_les_accumuler(self):
        cours = _cours(self.subject, self.exercices[0], "frequent", [self.frequent])
        recalculer_cursus(self.cursus)
        Cours.objects.filter(pk=cours.pk).update(statut=StatutContenu.BROUILLON)

        recalculer_cursus(self.cursus)

        self.assertFalse(FrequenceCours.objects.exists())

    def test_la_commande_ecrit_la_table_et_un_cursus_peut_etre_cible(self):
        _cours(self.subject, self.exercices[0], "frequent", [self.frequent])
        sortie = StringIO()

        call_command("calculer_frequences_cours", "--cursus", str(self.cursus.pk), stdout=sortie)

        self.assertEqual(FrequenceCours.objects.count(), 1)
        self.assertIn("1 cours fréquents", sortie.getvalue())


class ApiCoursTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.autre_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.frequent = Cours.objects.create(external_id="c-freq", titre="Cours fréquent", subject=self.subject, statut=StatutContenu.VALIDE)
        self.banal = Cours.objects.create(external_id="c-banal", titre="Cours banal", subject=self.subject, statut=StatutContenu.VALIDE)
        FrequenceCours.objects.create(
            cursus=self.cursus, cours=self.frequent, theme="dérivation", nb_epreuves=8, nb_sessions=10, frequence_pct=80,
        )
        self.client = APIClient()

    def _liste(self, **params):
        reponse = self.client.get("/catalog/cours/", params)
        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()
        return donnees["results"] if isinstance(donnees, dict) else donnees

    def test_le_champ_tombe_souvent_porte_le_chiffre_reel(self):
        par_titre = {c["titre"]: c for c in self._liste()}

        self.assertEqual(
            par_titre["Cours fréquent"]["tombe_souvent"],
            {"frequence_pct": 80, "nb_epreuves": 8, "nb_sessions": 10, "theme": "dérivation"},
        )
        self.assertIsNone(par_titre["Cours banal"]["tombe_souvent"])

    def test_le_filtre_ne_garde_que_les_cours_frequents(self):
        titres = [c["titre"] for c in self._liste(tombe_souvent="true")]

        self.assertEqual(titres, ["Cours fréquent"])

    def test_le_filtre_respecte_le_cursus_demande(self):
        self.assertEqual(len(self._liste(tombe_souvent="true", cursus=self.cursus.pk)), 1)
        self.assertEqual(self._liste(tombe_souvent="true", cursus=self.autre_cursus.pk), [])

    def test_le_tri_frequent_place_les_cours_frequents_en_premier(self):
        titres = [c["titre"] for c in self._liste(ordering="frequent")]

        self.assertEqual(titres[0], "Cours fréquent")
        self.assertIn("Cours banal", titres)

    def test_le_detail_d_un_cours_porte_aussi_la_frequence(self):
        reponse = self.client.get(f"/catalog/cours/{self.frequent.slug}/")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json()["tombe_souvent"]["frequence_pct"], 80)
