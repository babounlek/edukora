"""« Signaler cette question » (R22, voir quiz.views.signaler_question)."""
from users.models import User

from . import views
from .models import ModeQuiz, QuizQuestion, QuizSession, SignalementQuestion
from .test_erreurs import ErreursFixture


class SignalerQuestionTests(ErreursFixture):
    def setUp(self):
        super().setUp()
        self.session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.question = QuizQuestion.objects.create(session=self.session, competence_item=self.item("s1"), ordre=1)

    def _url(self, question=None):
        question = question or self.question
        return f"/quiz/sessions/{self.session.pk}/questions/{question.pk}/signaler/"

    def test_un_signalement_garde_le_motif_et_l_item(self):
        reponse = self.client.post(self._url(), {"motif": "REPONSE_FAUSSE", "commentaire": " la clé est B "}, format="json")

        self.assertEqual(reponse.status_code, 201)
        s = SignalementQuestion.objects.get()
        self.assertEqual((s.motif, s.commentaire, s.competence_item_id_garde), ("REPONSE_FAUSSE", "la clé est B", self.question.competence_item_id))
        self.assertEqual(s.statut, "NOUVEAU")

    def test_signaler_deux_fois_la_meme_question_met_a_jour(self):
        self.client.post(self._url(), {"motif": "FIGURE"}, format="json")
        reponse = self.client.post(self._url(), {"motif": "AUTRE", "commentaire": "finalement"}, format="json")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(SignalementQuestion.objects.count(), 1)
        self.assertEqual(SignalementQuestion.objects.get().motif, "AUTRE")

    def test_un_motif_inconnu_est_refuse(self):
        self.assertEqual(self.client.post(self._url(), {"motif": "BOF"}, format="json").status_code, 400)
        self.assertEqual(self.client.post(self._url(), {}, format="json").status_code, 400)
        self.assertFalse(SignalementQuestion.objects.exists())

    def test_la_question_d_un_autre_profil_est_introuvable(self):
        autre_profil = User.objects.create_user(phone_number="677610002", password="x").profils.first()
        autre = QuizSession.objects.create(profil=autre_profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        q = QuizQuestion.objects.create(session=autre, competence_item=self.item("s2"), ordre=1)

        reponse = self.client.post(f"/quiz/sessions/{autre.pk}/questions/{q.pk}/signaler/", {"motif": "AUTRE"}, format="json")

        self.assertEqual(reponse.status_code, 404)

    def test_un_plafond_par_jour(self):
        for i in range(views.SIGNALEMENTS_MAX_PAR_JOUR):
            q = QuizQuestion.objects.create(session=self.session, competence_item=self.item(f"p{i}"), ordre=10 + i)
            self.assertEqual(self.client.post(self._url(q), {"motif": "AUTRE"}, format="json").status_code, 201)

        self.assertEqual(self.client.post(self._url(), {"motif": "AUTRE"}, format="json").status_code, 429)

    def test_le_signalement_ne_change_ni_les_points_ni_la_maitrise(self):
        from .services import maitrise_par_theme

        self.client.post(self._url(), {"motif": "REPONSE_FAUSSE"}, format="json")

        self.assertEqual(maitrise_par_theme(self.profil, self.cursus), [])
