"""
Couvre les deux risques principaux du module : la sélection de questions (voir
quiz.services.generer_session) et la fuite de la bonne réponse avant que l'élève n'ait
répondu (voir quiz.views._question_payload) - un test de niveau ou un quiz dont la
réponse est visible dans l'onglet réseau avant d'être tentée ne vaut rien.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import (
    Cursus, Difficulte, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject, Tag, TypeReponse,
)
from subscriptions.models import Subscription
from users.models import User

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare
from .services import generer_session


def _make_question(lesson, numero, difficulte=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, **kwargs):
    exercise = Exercise.objects.create(lesson=lesson, numero_exercice=numero, statut=StatutContenu.VALIDE)
    question = Question.objects.create(
        exercise=exercise, numero="1", ordre=1,
        enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        difficulte_estimee=difficulte, type_reponse=type_reponse, **kwargs,
    )
    exercise.compile_from_questions()
    return question


class GenererSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.other_subject = Subject.objects.get(country__code="CM", code="FRANCAIS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")

        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)

    def test_only_questions_from_matching_cursus_are_eligible(self):
        _make_question(self.lesson, "1")
        other_lesson = Lesson.objects.create(
            title="Maths BAC D", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        other_lesson.cursus.add(self.other_cursus)
        _make_question(other_lesson, "1")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

        questions = [qq.question for qq in session.quiz_questions.all()]
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].exercise.lesson, self.lesson)

    def test_filters_by_subject(self):
        _make_question(self.lesson, "1")
        other_lesson = Lesson.objects.create(
            title="Français BAC C", subject=self.other_subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        other_lesson.cursus.add(self.cursus)
        _make_question(other_lesson, "1")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, subject=self.subject, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().question.exercise.lesson.subject, self.subject)

    def test_filters_by_theme(self):
        theme = Tag.objects.create(name="dérivation")
        matching = _make_question(self.lesson, "1")
        matching.themes.add(theme)
        _make_question(self.lesson, "2")  # sans thème

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, theme=theme, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().question, matching)

    def test_raises_when_no_question_eligible(self):
        with self.assertRaises(ValueError):
            generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

    def test_diagnostic_mode_covers_a_range_of_difficulties(self):
        for i in range(5):
            _make_question(self.lesson, f"faible-{i}", difficulte=Difficulte.FAIBLE)
        for i in range(5):
            _make_question(self.lesson, f"moyenne-{i}", difficulte=Difficulte.MOYENNE)
        for i in range(5):
            _make_question(self.lesson, f"elevee-{i}", difficulte=Difficulte.ELEVEE)

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=10)

        difficultes = {qq.question.difficulte_estimee for qq in session.quiz_questions.all()}
        self.assertEqual(session.quiz_questions.count(), 10)
        self.assertEqual(difficultes, {Difficulte.FAIBLE, Difficulte.MOYENNE, Difficulte.ELEVEE})


class QuizAnswerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200002", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        self.qcm = _make_question(
            lesson, "1", type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}], reponse_correcte="a",
        )
        self.ouverte = _make_question(lesson, "2", type_reponse=TypeReponse.OUVERTE)
        session = QuizSession.objects.create(user=self.user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        self.qcm_qq = QuizQuestion.objects.create(session=session, question=self.qcm, ordre=1)
        self.ouverte_qq = QuizQuestion.objects.create(session=session, question=self.ouverte, ordre=2)

    def test_qcm_correct_choice_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="a")
        self.assertTrue(answer.est_correcte)

    def test_qcm_wrong_choice_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="b")
        self.assertFalse(answer.est_correcte)

    def test_open_question_reussi_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.REUSSI)
        self.assertTrue(answer.est_correcte)

    def test_open_question_echec_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.ECHEC)
        self.assertFalse(answer.est_correcte)


class QuizApiTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.theme = Tag.objects.create(name="dérivation")
        self.question = _make_question(self.lesson, "1")
        self.question.themes.add(self.theme)

        self.user = User.objects.create_user(phone_number="677200003", password="x")
        self.client = APIClient()

    def _subscribe(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )

    def test_start_session_requires_authentication(self):
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_start_session_denied_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_start_session_creates_session_with_questions(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/quiz/sessions/", {"cursus": self.cursus.id, "mode": ModeQuiz.PRATIQUE}, format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_questions"], 1)
        self.assertTrue(QuizSession.objects.filter(user=self.user, cursus=self.cursus).exists())

    def test_question_payload_never_leaks_answer_before_responding(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]

        detail = self.client.get(f"/quiz/sessions/{start.data['id']}/")

        payload = detail.data["questions"][0]
        self.assertNotIn("corrige_markdown", payload)
        self.assertNotIn("reponse_correcte", payload)
        self.assertNotIn("reponse", payload)
        self.assertEqual(payload["id"], quiz_question_id)

    def test_answering_reveals_corrige_and_computes_est_correcte(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("corrige_markdown", response.data)
        self.assertTrue(response.data["reponse"]["est_correcte"])

        # Une fois répondu, la question révèle aussi le corrigé dans le détail de session.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_returns_content_without_recording_answer(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["corrige_markdown"], self.question.corrige_markdown)
        self.assertFalse(QuizAnswer.objects.filter(quiz_question_id=quiz_question_id).exists())

        # Toujours pas répondu : le détail de session ne fuite pas encore le corrigé.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertNotIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_denied_for_another_users_session(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        other_user = User.objects.create_user(phone_number="677200004", password="x")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 404)

    def test_complete_session_computes_score_by_theme(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]
        self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        response = self.client.post(f"/quiz/sessions/{session_id}/completer/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score"], 1)
        self.assertEqual(response.data["questions_repondues"], 1)
        self.assertEqual(response.data["par_theme"], [{"theme": "dérivation", "total": 1, "reussies": 1}])
        self.assertIsNotNone(QuizSession.objects.get(pk=session_id).completed_at)
