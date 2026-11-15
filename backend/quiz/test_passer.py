"""Passer une question (R22, voir quiz.views.passer_question) : ni réponse, ni échec, ni effet sur la maîtrise."""
from datetime import timedelta

from django.utils import timezone

from . import instantane
from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, RevisionSchedule
from .test_erreurs import ErreursFixture


class PasserQuestionTests(ErreursFixture):
    def _session(self, nb=2):
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        questions = []
        for i in range(nb):
            it = self.item(
                f"p{i}", type_reponse="QCM", reponse_correcte="b",
                choix=[{"lettre": "a", "texte": "x"}, {"lettre": "b", "texte": "y"}],
            )
            questions.append(QuizQuestion.objects.create(
                session=session, competence_item=it, ordre=i + 1,
                snapshot=instantane.figer_item(type(it).objects.select_related("theme", "subject").get(pk=it.pk)),
            ))
        return session, questions

    def _passer(self, session, question):
        return self.client.post(f"/quiz/sessions/{session.pk}/questions/{question.pk}/passer/")

    def test_passer_ne_cree_ni_reponse_ni_effet_sur_la_maitrise(self):
        session, (q1, _) = self._session()

        reponse = self._passer(session, q1)

        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.data["passee"])
        self.assertNotIn("corrige_markdown", reponse.data)  # passer ne dévoile rien
        self.assertFalse(QuizAnswer.objects.exists())
        self.assertFalse(RevisionSchedule.objects.exists())

    def test_le_payload_de_la_session_dit_quelles_questions_sont_passees(self):
        session, (q1, q2) = self._session()
        self._passer(session, q1)

        questions = self.client.get(f"/quiz/sessions/{session.pk}/").data["questions"]

        self.assertEqual([q["passee"] for q in questions], [True, False])

    def test_une_question_passee_reste_repondable_et_n_est_plus_passee(self):
        session, (q1, _) = self._session()
        self._passer(session, q1)

        reponse = self.client.post(
            f"/quiz/sessions/{session.pk}/questions/{q1.pk}/answer/", {"reponse_choisie": "b"}, format="json",
        )

        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(reponse.data["passee"])
        self.assertTrue(reponse.data["reponse"]["est_correcte"])

    def test_on_ne_passe_pas_une_question_deja_repondue(self):
        session, (q1, _) = self._session()
        self.client.post(f"/quiz/sessions/{session.pk}/questions/{q1.pk}/answer/", {"reponse_choisie": "a"}, format="json")

        self.assertEqual(self._passer(session, q1).status_code, 409)

    def test_session_terminee_refusee(self):
        session, (q1, _) = self._session()
        QuizSession.objects.filter(pk=session.pk).update(completed_at=timezone.now())

        self.assertEqual(self._passer(session, q1).status_code, 409)

    def test_la_session_d_un_autre_profil_est_introuvable(self):
        from users.models import User

        session, (q1, _) = self._session()
        self.client.force_authenticate(user=User.objects.create_user(phone_number="677610099", password="x"))

        self.assertEqual(self._passer(session, q1).status_code, 404)

    def test_le_resultat_compte_les_passees_a_part_sans_les_compter_comme_ratees(self):
        session, (q1, q2) = self._session()
        self._passer(session, q1)
        self.client.post(f"/quiz/sessions/{session.pk}/questions/{q2.pk}/answer/", {"reponse_choisie": "b"}, format="json")

        resultat = self.client.post(f"/quiz/sessions/{session.pk}/completer/").data

        self.assertEqual(resultat["questions_repondues"], 1)
        self.assertEqual(resultat["questions_passees"], 1)
        self.assertEqual(resultat["score"], 1)

    def test_un_quiz_entierement_passe_ne_valide_pas_la_seance_du_jour(self):
        from unittest import mock

        session, (q1, q2) = self._session()
        self._passer(session, q1)
        self._passer(session, q2)

        with mock.patch("quiz.views.cloturer_seance_si_quiz_termine") as cloturer:
            reponse = self.client.post(f"/quiz/sessions/{session.pk}/completer/")

        self.assertEqual(reponse.status_code, 200)
        cloturer.assert_not_called()
        self.assertEqual(reponse.data["questions_repondues"], 0)

    def test_un_quiz_ou_l_on_a_repondu_valide_toujours_la_seance(self):
        from unittest import mock

        session, (q1, q2) = self._session()
        self._passer(session, q1)
        self.client.post(f"/quiz/sessions/{session.pk}/questions/{q2.pk}/answer/", {"reponse_choisie": "b"}, format="json")

        with mock.patch("quiz.views.cloturer_seance_si_quiz_termine") as cloturer:
            self.client.post(f"/quiz/sessions/{session.pk}/completer/")

        cloturer.assert_called_once()
