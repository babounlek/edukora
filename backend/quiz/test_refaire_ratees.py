from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .services import items_rates, session_des_ratees
from .tests import _make_competence_item


class RefaireRateesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677600001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.items = [
            _make_competence_item(self.subject, self.cursus, theme=Tag.objects.create(name=f"t{i}"), numero=f"r{i}")
            for i in range(4)
        ]
        self.session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        # r0 juste, r1 raté, r2 raté, r3 jamais répondu
        for ordre, (item, resultat) in enumerate(zip(self.items, ("REUSSI", "ECHEC", "ECHEC", None)), start=1):
            quiz_question = QuizQuestion.objects.create(session=self.session, competence_item=item, ordre=ordre)
            if resultat:
                QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=resultat)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _abonner(self):
        Subscription.objects.create(user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=3))

    def test_only_answered_and_missed_items_are_returned_in_order(self):
        self.assertEqual(items_rates(self.session), [self.items[1], self.items[2]])

    def test_the_new_session_reuses_exactly_those_items(self):
        refaite = session_des_ratees(self.user, self.session)

        self.assertEqual(refaite.mode, ModeQuiz.PRATIQUE)
        self.assertNotEqual(refaite.pk, self.session.pk)
        self.assertEqual(
            [qq.competence_item_id for qq in refaite.quiz_questions.order_by("ordre")],
            [self.items[1].id, self.items[2].id],
        )

    def test_nothing_to_redo_raises(self):
        propre = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        with self.assertRaises(ValueError):
            session_des_ratees(self.user, propre)

    def test_api_requires_an_active_subscription(self):
        response = self.client.post(f"/quiz/sessions/{self.session.id}/refaire-ratees/")
        self.assertEqual(response.status_code, 403)

    def test_api_creates_the_session(self):
        self._abonner()
        response = self.client.post(f"/quiz/sessions/{self.session.id}/refaire-ratees/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_questions"], 2)

    def test_api_is_private_to_the_owner(self):
        self._abonner()
        autre = User.objects.create_user(phone_number="677600002", password="x")
        client = APIClient()
        client.force_authenticate(user=autre)
        self.assertEqual(client.post(f"/quiz/sessions/{self.session.id}/refaire-ratees/").status_code, 404)

    def test_result_payload_announces_how_many_can_be_redone(self):
        self._abonner()
        response = self.client.post(f"/quiz/sessions/{self.session.id}/completer/")
        self.assertEqual(response.data["nb_ratees"], 2)
