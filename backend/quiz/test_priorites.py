from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Difficulte, Examen, Lesson, LessonType, Origine, StatutContenu, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .priorites import priorites_examen
from .services import DIAGNOSTIC_QUESTIONS_PAR_MATIERE, generer_session
from .tests import _make_competence_item


class _Base(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        self.user = User.objects.create_user(phone_number="677400001", password="x")
        self.compteur = 0

    def _matiere(self, code, coefficient, nb_items=4):
        subject = Subject.objects.create(code=code, label=code.title(), country=self.cursus.country)
        lesson = Lesson.objects.create(
            title=f"Épreuve {code}", subject=subject, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL, coefficient=str(coefficient),
        )
        lesson.cursus.add(self.cursus)
        items = []
        for _ in range(nb_items):
            self.compteur += 1
            items.append(_make_competence_item(
                subject, self.cursus, theme=Tag.objects.create(name=f"theme-{code}-{self.compteur}"),
                difficulte=Difficulte.MOYENNE, numero=str(self.compteur),
            ))
        return subject, items

    def _repondre(self, item, correcte, session=None):
        session = session or QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        ordre = session.quiz_questions.count() + 1
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=ordre)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare="REUSSI" if correcte else "ECHEC")
        return session


class DiagnosticParMatiereTests(_Base):
    def test_probes_the_heaviest_subjects_with_three_questions_each(self):
        fort, _ = self._matiere("fort", 5)
        moyen, _ = self._matiere("moyen", 3)
        faible, _ = self._matiere("faible", 1)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=6)

        matieres = [qq.competence_item.subject_id for qq in session.quiz_questions.order_by("ordre")]
        self.assertEqual(len(matieres), 6)
        self.assertEqual(set(matieres), {fort.id, moyen.id})
        self.assertEqual(matieres.count(fort.id), DIAGNOSTIC_QUESTIONS_PAR_MATIERE)
        self.assertNotIn(faible.id, matieres)

    def test_questions_alternate_between_subjects(self):
        self._matiere("fort", 5)
        self._matiere("moyen", 3)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=6)

        matieres = [qq.competence_item.subject_id for qq in session.quiz_questions.order_by("ordre")]
        self.assertTrue(all(a != b for a, b in zip(matieres, matieres[1:])))

    def test_a_thin_subject_gives_what_it_has_and_the_next_one_fills_the_gap(self):
        fort, _ = self._matiere("fort", 5, nb_items=1)
        self._matiere("moyen", 3, nb_items=4)
        self._matiere("faible", 1, nb_items=4)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=6)

        matieres = [qq.competence_item.subject_id for qq in session.quiz_questions.all()]
        self.assertEqual(len(matieres), 6)
        self.assertEqual(matieres.count(fort.id), 1)

    def test_a_single_subject_falls_back_to_the_global_draw(self):
        self._matiere("seul", 4, nb_items=5)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=4)

        self.assertEqual(session.quiz_questions.count(), 4)

    def test_an_explicit_subject_keeps_the_old_behaviour(self):
        fort, _ = self._matiere("fort", 5, nb_items=6)
        self._matiere("moyen", 3)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, subject=fort, n=6)

        self.assertEqual({qq.competence_item.subject_id for qq in session.quiz_questions.all()}, {fort.id})


class PrioritesExamenTests(_Base):
    def test_coefficient_drives_the_ranking_without_any_answer(self):
        self._matiere("faible", 1)
        self._matiere("fort", 5)

        resultat = priorites_examen(self.user, self.cursus)

        self.assertEqual([m["subject_label"] for m in resultat["matieres"]], ["Fort", "Faible"])
        self.assertEqual(resultat["matieres"][0]["urgence"], 100)
        self.assertFalse(resultat["a_deja_repondu"])
        self.assertTrue(all(m["niveau"] == "a_situer" for m in resultat["matieres"]))

    def test_answers_break_a_tie_between_equal_coefficients(self):
        a, items_a = self._matiere("alpha", 4)
        b, items_b = self._matiere("beta", 4)
        for item in items_a[:3]:
            self._repondre(item, True)
        for item in items_b[:3]:
            self._repondre(item, False)

        resultat = priorites_examen(self.user, self.cursus)

        self.assertEqual(resultat["matieres"][0]["subject_id"], b.id)
        self.assertEqual(resultat["matieres"][0]["niveau"], "fragile")
        self.assertEqual(resultat["matieres"][1]["niveau"], "solide")
        self.assertTrue(resultat["a_deja_repondu"])

    def test_three_answers_do_not_overturn_a_much_heavier_coefficient(self):
        fort, items_fort = self._matiere("fort", 5)
        self._matiere("faible", 1)
        for item in items_fort[:3]:
            self._repondre(item, True)  # 3/3 dans la matière lourde

        resultat = priorites_examen(self.user, self.cursus)

        self.assertEqual(resultat["matieres"][0]["subject_id"], fort.id)

    def test_only_the_top_three_are_flagged_as_priorities(self):
        for i, coef in enumerate((5, 4, 3, 2, 1)):
            self._matiere(f"m{i}", coef)

        resultat = priorites_examen(self.user, self.cursus)

        self.assertEqual([m["prioritaire"] for m in resultat["matieres"]], [True, True, True, False, False])

    def test_topics_to_work_on_are_the_ones_missed_in_the_diagnostic(self):
        _, items = self._matiere("fort", 5)
        session = QuizSession.objects.create(
            user=self.user, cursus=self.cursus, mode=ModeQuiz.DIAGNOSTIC, completed_at=timezone.now(),
        )
        self._repondre(items[0], True, session)
        self._repondre(items[1], False, session)
        self._repondre(items[2], False, session)

        resultat = priorites_examen(self.user, self.cursus)

        self.assertTrue(resultat["diagnostic_fait"])
        self.assertEqual(
            [t["theme"] for t in resultat["themes_a_travailler"]], [items[1].theme.name, items[2].theme.name],
        )

    def test_no_topics_without_a_finished_diagnostic(self):
        _, items = self._matiere("fort", 5)
        self._repondre(items[0], False)

        resultat = priorites_examen(self.user, self.cursus)

        self.assertFalse(resultat["diagnostic_fait"])
        self.assertEqual(resultat["themes_a_travailler"], [])


class PrioritesApiTests(_Base):
    def test_requires_authentication(self):
        response = APIClient().get("/quiz/priorites/", {"cursus": self.cursus.id})
        self.assertIn(response.status_code, (401, 403))

    def test_404_without_any_subscription(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        self.assertEqual(client.get("/quiz/priorites/", {"cursus": self.cursus.id}).status_code, 404)

    def test_returns_the_ranking_for_a_subscriber(self):
        self._matiere("fort", 5)
        Subscription.objects.create(user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=5))
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get("/quiz/priorites/", {"cursus": self.cursus.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["matieres"][0]["subject_label"], "Fort")
