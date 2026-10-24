"""
Reprendre une tentative en cours - voir quiz.historique.en_cours.

Trois gestes distincts : reprendre (rouvrir la MÊME session, encore en cours), rejouer (une nouvelle
session) et consulter (une session terminée, en lecture seule). Ici, seul le premier.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APIClient

from users.models import User

from .models import QuizAnswer, QuizSession
from .test_historique import _Base


class EnCoursTests(_Base):
    def _lister(self, client=None):
        reponse = (client or self.client).get("/quiz/en-cours/")
        self.assertEqual(reponse.status_code, 200)
        return reponse.json()

    def test_requires_authentication(self):
        self.assertEqual(APIClient().get("/quiz/en-cours/").status_code, 401)

    def test_lists_started_unfinished_sessions_with_their_progress(self):
        self._abonner()
        session = self._session(terminee=False, reponses=("b", "a", None))

        ligne = self._lister()[0]

        self.assertEqual(ligne["id"], session.pk)
        self.assertEqual((ligne["nb_repondues"], ligne["total_questions"]), (2, 3))
        self.assertFalse(ligne["a_terminer"])
        self.assertEqual(ligne["subject_label"], self.subject.label)

    def test_flags_a_session_whose_questions_are_all_answered_but_not_closed(self):
        self._abonner()
        self._session(terminee=False, reponses=("b", "a", "b"))

        self.assertTrue(self._lister()[0]["a_terminer"])

    def test_leaves_out_finished_sessions_untouched_sessions_and_other_profiles(self):
        self._abonner()
        self._session(terminee=True)
        self._session(terminee=False, reponses=())  # ouverte sans jamais répondre : pas une tentative interrompue
        autre = User.objects.create_user(phone_number="677700009", password="x")
        self._session(profil=autre.profils.first(), terminee=False, reponses=("b", None, None))

        self.assertEqual(self._lister(), [])
        self.assertEqual(self._lister(_client_de(autre)), [])  # il n'a lui non plus aucune session à lui

    def test_most_recent_answer_first_and_capped(self):
        self._abonner()
        sessions = [self._session(terminee=False, reponses=("b", None, None)) for _ in range(7)]
        # La plus ancienne par numéro reçoit la réponse la plus récente.
        QuizAnswer.objects.filter(quiz_question__session=sessions[0]).update(answered_at=timezone.now() + timedelta(minutes=1))

        liste = self._lister()

        self.assertEqual(len(liste), 5)
        self.assertEqual(liste[0]["id"], sessions[0].pk)

    def test_a_session_abandoned_for_days_is_no_longer_offered_but_remains_openable(self):
        self._abonner()
        session = self._session(terminee=False, reponses=("b", None, None))
        QuizAnswer.objects.filter(quiz_question__session=session).update(answered_at=timezone.now() - timedelta(days=4))

        self.assertEqual(self._lister(), [])
        self.assertEqual(self.client.get(f"/quiz/sessions/{session.pk}/").status_code, 200)

    def test_without_a_subscription_only_showcase_sessions_can_be_resumed(self):
        payante = self._session(terminee=False, reponses=("b", None, None))
        self.assertEqual(self._lister(), [])  # abonnement absent ou expiré : pas de reprise d'un quiz payant

        for item in self.items:
            item.est_vitrine = True
            item.save()
        self.assertEqual([l["id"] for l in self._lister()], [payante.pk])

    def test_a_session_with_deleted_content_is_not_resumable_without_a_subscription(self):
        self._session(terminee=False, reponses=("b", None, None))
        for item in self.items:
            item.est_vitrine = True
            item.save()
        self.items[2].delete()  # une clé nulle n'est pas vitrine

        self.assertEqual(self._lister(), [])

    def test_the_query_count_does_not_grow_with_the_number_of_sessions(self):
        self._abonner()
        self._session(terminee=False, reponses=("b", None, None))
        un = self._nombre_de_requetes()
        for _ in range(4):
            self._session(terminee=False, reponses=("b", None, None))

        self.assertEqual(self._nombre_de_requetes(), un)

    def _nombre_de_requetes(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as capture:
            self.client.get("/quiz/en-cours/")
        return len(capture)


class ReprendreTests(_Base):
    def test_resuming_reopens_the_same_session_with_its_answers_and_finishes_it_without_loss(self):
        self._abonner()
        session = self._session(terminee=False, reponses=("b", "a", None))
        avant = QuizSession.objects.count()

        rouverte = self.client.get(f"/quiz/sessions/{session.pk}/").json()
        questions = rouverte["questions"]

        self.assertEqual(rouverte["id"], session.pk)
        self.assertEqual([bool(q.get("reponse")) for q in questions], [True, True, False])
        self.assertEqual(questions[0]["reponse"]["reponse_choisie"], "b")

        derniere = session.quiz_questions.order_by("ordre")[2]
        self.assertEqual(self._repondre(session, derniere, "b").status_code, 200)
        resultat = self.client.post(f"/quiz/sessions/{session.pk}/completer/").json()

        self.assertEqual(QuizSession.objects.count(), avant)  # reprendre ne crée jamais de session
        self.assertEqual((resultat["score"], resultat["questions_repondues"]), (2, 3))
        self.assertEqual(self._lister_en_cours(), [])  # une fois terminée, plus à reprendre
        self.assertEqual(self.client.get("/quiz/historique/").json()["count"], 1)  # ... mais dans l'historique

    def test_another_profile_cannot_resume_a_session_by_its_id(self):
        session = self._session(terminee=False, reponses=("b", None, None))
        autre = User.objects.create_user(phone_number="677700010", password="x")
        client = _client_de(autre)

        self.assertEqual(client.get(f"/quiz/sessions/{session.pk}/").status_code, 404)

    def _lister_en_cours(self):
        return self.client.get("/quiz/en-cours/").json()


def _client_de(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client
