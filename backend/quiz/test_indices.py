"""Difficulté visible et coup de pouce « rappel de méthode » (R19, voir quiz.views.indice_question)."""
from django.test import SimpleTestCase

from . import instantane
from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .test_erreurs import ErreursFixture

CORRIGE = "### Rappel de méthode\n\nDérive puis étudie le signe.\n\n### Corrigé\n\n**Réponse : B.** Car f' > 0."


class IndiceDuCorrigeTests(SimpleTestCase):
    def test_seule_la_section_rappel_de_methode_est_extraite(self):
        self.assertEqual(instantane.indice_du_corrige(CORRIGE), "Dérive puis étudie le signe.")

    def test_sans_rappel_de_methode_pas_d_indice(self):
        self.assertEqual(instantane.indice_du_corrige("### Corrigé\n\n**Réponse : B.**"), "")
        self.assertEqual(instantane.indice_du_corrige(""), "")

    def test_un_rappel_en_derniere_section_va_jusqu_a_la_fin(self):
        self.assertEqual(instantane.indice_du_corrige("### Rappel de méthode\nFais ceci."), "Fais ceci.")


class IndiceQuestionTests(ErreursFixture):
    def _question(self, corrige=CORRIGE, **item):
        it = self.item("i1", type_reponse="QCM", reponse_correcte="b", choix=[{"lettre": "a", "texte": "x"}, {"lettre": "b", "texte": "y"}], **item)
        it.corrige_markdown = corrige
        it.save(update_fields=["corrige_markdown"])
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        question = QuizQuestion.objects.create(
            session=session, competence_item=it, ordre=1,
            snapshot=instantane.figer_item(type(it).objects.select_related("theme", "subject").get(pk=it.pk)),
        )
        return session, question

    def _url(self, session, question):
        return f"/quiz/sessions/{session.pk}/questions/{question.pk}/indice/"

    def test_le_coup_de_pouce_donne_la_methode_et_se_retient(self):
        session, question = self._question()

        reponse = self.client.get(self._url(session, question))

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["indice_markdown"], "Dérive puis étudie le signe.")
        self.assertNotIn("Réponse", reponse.data["indice_markdown"])
        question.refresh_from_db()
        self.assertTrue(question.indice_vu)

    def test_le_payload_annonce_la_difficulte_et_l_indice_sans_le_livrer(self):
        session, question = self._question()

        donnees = self.client.get(f"/quiz/sessions/{session.pk}/").data["questions"][0]

        self.assertEqual(donnees["difficulte"], "MOYENNE")
        self.assertTrue(donnees["indice_disponible"])
        self.assertFalse(donnees["indice_vu"])
        self.assertNotIn("Dérive puis", str(donnees))
        self.assertNotIn("corrige_markdown", donnees)

    def test_apres_la_reponse_le_coup_de_pouce_est_refuse(self):
        session, question = self._question()
        QuizAnswer.objects.create(quiz_question=question, reponse_choisie="b")

        self.assertEqual(self.client.get(self._url(session, question)).status_code, 409)

    def test_sans_rappel_de_methode_rien_a_donner(self):
        session, question = self._question(corrige="### Corrigé\n\n**Réponse : B.**")

        self.assertEqual(self.client.get(self._url(session, question)).status_code, 404)
        donnees = self.client.get(f"/quiz/sessions/{session.pk}/").data["questions"][0]
        self.assertFalse(donnees["indice_disponible"])

    def test_la_question_d_un_autre_profil_est_introuvable(self):
        from users.models import User

        session, question = self._question()
        autre = User.objects.create_user(phone_number="677610009", password="x")
        self.client.force_authenticate(user=autre)

        self.assertEqual(self.client.get(self._url(session, question)).status_code, 404)
