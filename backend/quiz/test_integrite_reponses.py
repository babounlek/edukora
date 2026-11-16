"""
Audit du 2026-11-16 (section 4.3) : ce que l'interface empêchait déjà, le serveur le refuse aussi.

- la bonne lettre d'un QCM ne se lit pas avant d'avoir répondu ;
- une réponse ne se réécrit pas après la correction ;
- un quiz clos sans une seule réponse, ou « J'ai fini » sur une séance à quiz, ne valide pas la séance du jour.
"""

from unittest import mock

from django.utils import timezone

from . import instantane
from .models import (
    ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, SeanceJournaliere, StatutSeance,
)
from .test_erreurs import ErreursFixture


class IntegriteFixture(ErreursFixture):
    def _session(self, nb=2, type_reponse="QCM"):
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        questions = []
        for i in range(nb):
            options = (
                {"type_reponse": "QCM", "reponse_correcte": "b",
                 "choix": [{"lettre": "a", "texte": "x"}, {"lettre": "b", "texte": "y"}]}
                if type_reponse == "QCM" else {}
            )
            it = self.item(f"i{type_reponse}{i}", **options)
            questions.append(QuizQuestion.objects.create(
                session=session, competence_item=it, ordre=i + 1,
                snapshot=instantane.figer_item(type(it).objects.select_related("theme", "subject").get(pk=it.pk)),
            ))
        return session, questions

    def _repondre(self, session, question, **corps):
        return self.client.post(f"/quiz/sessions/{session.pk}/questions/{question.pk}/answer/", corps, format="json")

    def _corrige(self, session, question):
        return self.client.get(f"/quiz/sessions/{session.pk}/questions/{question.pk}/corrige/")


class CleDuQcmTests(IntegriteFixture):
    def test_la_bonne_lettre_ne_se_lit_pas_avant_de_repondre(self):
        session, (q1, _) = self._session()

        reponse = self._corrige(session, q1)

        self.assertEqual(reponse.status_code, 409)
        self.assertEqual(reponse.data["code"], "reponse_requise")
        self.assertNotIn("reponse_correcte", reponse.data)

    def test_elle_se_lit_une_fois_la_reponse_donnee(self):
        session, (q1, _) = self._session()
        self._repondre(session, q1, reponse_choisie="a")

        reponse = self._corrige(session, q1)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["reponse_correcte"], "b")

    def test_une_question_ouverte_se_revele_toujours_avant_de_se_noter(self):
        session, (q1, _) = self._session(type_reponse="OUVERTE")

        self.assertEqual(self._corrige(session, q1).status_code, 200)


class ReponseUniqueTests(IntegriteFixture):
    def test_un_qcm_ne_se_reecrit_pas_apres_la_correction(self):
        session, (q1, _) = self._session()
        self.assertFalse(self._repondre(session, q1, reponse_choisie="a").data["reponse"]["est_correcte"])

        seconde = self._repondre(session, q1, reponse_choisie="b")

        self.assertEqual(seconde.status_code, 409)
        self.assertEqual(seconde.data["code"], "deja_repondue")
        self.assertEqual(QuizAnswer.objects.get(quiz_question=q1).reponse_choisie, "a")

    def test_une_auto_notation_ne_se_reecrit_pas(self):
        session, (q1, _) = self._session(type_reponse="OUVERTE")
        self._repondre(session, q1, resultat_declare="ECHEC")

        seconde = self._repondre(session, q1, resultat_declare="REUSSI")

        self.assertEqual(seconde.status_code, 409)
        self.assertEqual(QuizAnswer.objects.get(quiz_question=q1).resultat_declare, "ECHEC")

    def test_la_meme_reponse_rejouee_est_acceptee_sans_rien_refaire(self):
        session, (q1, _) = self._session()
        premiere = self._repondre(session, q1, reponse_choisie="b")

        with mock.patch("quiz.views.xp.crediter_reponse") as crediter, \
                mock.patch("quiz.views.enregistrer_resultat_pour_revision") as revision:
            rejouee = self._repondre(session, q1, reponse_choisie="b")

        self.assertEqual(rejouee.status_code, 200)
        self.assertEqual(rejouee.data["reponse"], premiere.data["reponse"])
        self.assertEqual(QuizAnswer.objects.filter(quiz_question=q1).count(), 1)
        crediter.assert_not_called()
        revision.assert_not_called()


class SeanceSansTravailTests(IntegriteFixture):
    def test_un_quiz_clos_sans_y_toucher_ne_valide_pas_la_seance(self):
        session, _ = self._session()

        with mock.patch("quiz.views.cloturer_seance_si_quiz_termine") as cloturer:
            reponse = self.client.post(f"/quiz/sessions/{session.pk}/completer/")

        self.assertEqual(reponse.status_code, 200)
        cloturer.assert_not_called()

    def _seance(self, etapes):
        return SeanceJournaliere.objects.create(
            profil=self.profil, cursus=self.cursus, date=timezone.localdate(), etapes=etapes,
            origine=OrigineSeance.DIAGNOSTIC, ordre=1, subject=self.maths, theme=self.derivation,
        )

    def test_j_ai_fini_est_refuse_quand_la_seance_a_un_quiz(self):
        self.abonner()
        seance = self._seance([{"type": "cours", "slug": "derivation"}, {"type": "quiz"}])

        reponse = self.client.post("/quiz/plan-du-jour/terminer/")

        self.assertEqual(reponse.status_code, 409)
        self.assertEqual(reponse.data["code"], "quiz_requis")
        seance.refresh_from_db()
        self.assertNotEqual(seance.statut, StatutSeance.TERMINEE)

    def test_j_ai_fini_reste_possible_pour_une_seance_sans_quiz(self):
        self.abonner()
        seance = self._seance([{"type": "cours", "slug": "derivation"}])

        reponse = self.client.post("/quiz/plan-du-jour/terminer/")

        self.assertEqual(reponse.status_code, 200)
        seance.refresh_from_db()
        self.assertEqual(seance.statut, StatutSeance.TERMINEE)
