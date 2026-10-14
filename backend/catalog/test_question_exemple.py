"""
Question d'exemple de /quiz (voir catalog.views.question_exemple_gratuite) : une vraie question QCM d'une épreuve
en accès libre, dans la langue demandée - jamais d'une épreuve payante, jamais un texte qui ne se lirait pas brut.
"""
from django.test import TestCase
from django.urls import reverse

from .models import (
    Cursus,
    Examen,
    Exercise,
    Lesson,
    LessonType,
    Origine,
    Question,
    StatutContenu,
    Subject,
    TypeReponse,
)

CHOIX = [{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}, {"lettre": "c", "texte": "Trois"}, {"lettre": "d", "texte": "Quatre"}]


class QuestionExempleTests(TestCase):
    def setUp(self):
        self.gce = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        self.bac = Cursus.objects.filter(country__code="CM", examen=Examen.BAC).first()
        self.maths_gce = Subject.objects.get(country__code="CM", code="GCE_MATHS")
        self.maths_fr = Subject.objects.get(country__code="CM", code="MATHS")

    def _epreuve(self, subject, cursus, titre, vitrine=True, statut=StatutContenu.VALIDE):
        lesson = Lesson.objects.create(
            title=titre, subject=subject, year=2024, lesson_type=LessonType.CORR,
            statut=statut, origine=Origine.OFFICIEL, est_vitrine=vitrine,
        )
        lesson.cursus.add(cursus)
        return Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)

    def _question(self, exercice, numero, enonce, choix=CHOIX, reponse="b", type_reponse=TypeReponse.QCM):
        return Question.objects.create(
            exercise=exercice, numero=str(numero), ordre=numero, enonce_markdown=enonce, corrige_markdown="c",
            type_reponse=type_reponse, choix=choix, reponse_correcte=reponse,
        )

    def _appeler(self, **params):
        return self.client.get(reverse("catalog:question-exemple"), params)

    def test_renvoie_la_question_d_une_epreuve_gratuite_dans_la_langue(self):
        exercice = self._epreuve(self.maths_gce, self.gce, "Mathematics GCE gratuite")
        self._question(exercice, 1, "What is two plus two?")

        reponse = self._appeler(langue="en")

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()
        self.assertEqual(donnees["question"], "What is two plus two?")
        self.assertEqual(donnees["reponse_correcte"], "b")
        self.assertEqual([c["lettre"] for c in donnees["choix"]], ["a", "b", "c", "d"])
        self.assertEqual(donnees["epreuve"]["title"], "Mathematics GCE gratuite")
        self.assertEqual(donnees["epreuve"]["slug"], Lesson.objects.get(title="Mathematics GCE gratuite").slug)
        self.assertEqual(donnees["numero"], "1")

    def test_jamais_une_epreuve_payante_ni_non_publiee_ni_d_une_autre_langue(self):
        self._question(self._epreuve(self.maths_gce, self.gce, "Payante", vitrine=False), 1, "Paid question?")
        self._question(
            self._epreuve(self.maths_gce, self.gce, "Brouillon", statut=StatutContenu.BROUILLON), 1, "Draft question?",
        )
        self._question(self._epreuve(self.maths_fr, self.bac, "Gratuite française"), 1, "Question française ?")

        self.assertEqual(self._appeler(langue="en").status_code, 404)
        self.assertEqual(self._appeler(langue="fr").json()["question"], "Question française ?")

    def test_ecarte_ce_qui_ne_se_lirait_pas_brut_ou_n_est_pas_un_qcm_complet(self):
        exercice = self._epreuve(self.maths_gce, self.gce, "Gratuite")
        self._question(exercice, 1, "Compute $x^2$ now?")  # LaTeX
        self._question(exercice, 2, "Not a question")  # ne se termine pas par « ? »
        self._question(exercice, 3, "Only three choices?", choix=CHOIX[:3])
        self._question(exercice, 4, "Open question?", type_reponse=TypeReponse.OUVERTE)
        self._question(exercice, 5, "No known answer?", reponse="")
        self._question(exercice, 6, "x" * 250 + "?")  # trop long
        self.assertEqual(self._appeler(langue="en").status_code, 404)

        self._question(exercice, 7, "Is this readable?")
        self.assertEqual(self._appeler(langue="en").json()["question"], "Is this readable?")

    def test_le_choix_est_stable_et_suit_l_ordre_des_questions(self):
        exercice = self._epreuve(self.maths_gce, self.gce, "Gratuite")
        self._question(exercice, 2, "Second question?")
        self._question(exercice, 1, "First question?")

        premiers = {self._appeler(langue="en").json()["question"] for _ in range(3)}

        self.assertEqual(premiers, {"First question?"})

    def test_un_pays_sans_epreuve_gratuite_donne_404(self):
        self._question(self._epreuve(self.maths_gce, self.gce, "Gratuite"), 1, "Any question?")
        self.assertEqual(self._appeler(langue="en", country="sn").status_code, 404)
        self.assertEqual(self._appeler(langue="en", country="cm").status_code, 200)
