"""
Comptes invités et quiz gratuit : un visiteur joue un thème gratuit avec une vraie séance (historique, reprise, XP), sans
compte, et la garde en s'inscrivant. Le jeton d'invité n'ouvre que les routes d'une séance (voir users.authentication).
"""
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag
from quiz.models import GainXP, JourXP, QuizAnswer, QuizSession, RevisionSchedule
from quiz.tests import _make_competence_item
from users import invites
from users.authentication import chemin_ouvert_aux_invites
from users.models import OTPCode, User


def _jeton(client):
    reponse = client.post("/auth/invite/")
    assert reponse.status_code == 201, reponse.data
    return reponse.data["access"]


class _Base(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme_gratuit = Tag.objects.create(name="theme-gratuit")
        for i in range(3):
            _make_competence_item(self.subject, self.cursus, theme=self.theme_gratuit, numero=f"g{i}", est_vitrine=True)
        self.theme_payant = Tag.objects.create(name="theme-payant")
        _make_competence_item(self.subject, self.cursus, theme=self.theme_payant, numero="p1")
        self.client = APIClient()
        self.jeton = _jeton(self.client)

    def auth(self, jeton=None):
        return {"HTTP_AUTHORIZATION": f"Bearer {jeton or self.jeton}"}

    def demarrer(self, theme=None):
        corps = {"cursus": self.cursus.id, "theme": (theme or self.theme_gratuit).id, "mode": "PRATIQUE", "n": 5}
        return self.client.post("/quiz/sessions/", corps, format="json", **self.auth())

    def repondre(self, session_id, question):
        return self.client.post(
            f"/quiz/sessions/{session_id}/questions/{question['id']}/answer/",
            {"resultat_declare": "REUSSI"}, format="json", **self.auth(),
        )


class RoutesOuvertesAuxInvitesTests(TestCase):
    def test_les_routes_d_une_seance_sont_ouvertes(self):
        for chemin in (
            "/inedit/tentatives/",
            "/quiz/sessions/",
            "/quiz/sessions/12/",
            "/quiz/sessions/12/questions/34/answer/",
            "/quiz/sessions/12/questions/34/corrige/",
            "/quiz/sessions/12/completer/",
            "/quiz/sessions/12/refaire-ratees/",
            "/quiz/en-cours/",
            "/quiz/historique/12/",
            "/quiz/historique/12/rejouer/",
        ):
            self.assertTrue(chemin_ouvert_aux_invites(chemin), chemin)

    def test_tout_le_reste_du_quiz_et_du_site_reste_ferme(self):
        for chemin in (
            "/auth/me/",
            "/quiz/parcours/",
            "/quiz/parcours/resume/",
            "/quiz/plan-du-jour/",
            "/quiz/plan-du-jour/terminer/",
            "/quiz/accueil/",
            "/quiz/bilan-periode/",
            "/quiz/maitrise/",
            "/quiz/revisions/",
            "/quiz/priorites/",
            "/quiz/xp/objectif/",
            "/quiz/chrono/",
            "/quiz/historique/",  # la LISTE, pas une séance
            "/quiz/sessions/12/fiche-pdf/",
            "/quiz/sessions/12/sujet.pdf",
            "/quiz/sessions/12/questions/34/answer/extra/",
            "/quiz/sessions/abc/",
            "/access/progression/",
            "/subscriptions/plans/",
        ):
            self.assertFalse(chemin_ouvert_aux_invites(chemin), chemin)


class QuizGratuitInviteTests(_Base):
    def test_joue_un_quiz_gratuit_du_debut_a_la_fin_avec_de_l_xp_reel(self):
        creation = self.demarrer()
        self.assertEqual(creation.status_code, 201, creation.data)
        session_id = creation.data["id"]
        questions = creation.data["questions"]
        self.assertEqual(len(questions), 3)

        for question in questions:
            self.assertEqual(self.repondre(session_id, question).status_code, 200)

        fin = self.client.post(f"/quiz/sessions/{session_id}/completer/", **self.auth())
        self.assertEqual(fin.status_code, 200, fin.data)
        self.assertEqual(fin.data["questions_repondues"], 3)

        invite = User.objects.get(est_invite=True)
        profil = invite.profils.get()
        self.assertTrue(GainXP.objects.filter(profil=profil).exists())  # de vrais points, pas des points simulés
        self.assertEqual(QuizSession.objects.get(pk=session_id).profil_id, profil.pk)

    def test_un_theme_payant_reste_ferme(self):
        self.assertEqual(self.demarrer(self.theme_payant).status_code, 403)
        self.assertFalse(QuizSession.objects.exists())

    def test_refaire_les_ratees_et_l_historique_d_une_seance_marchent(self):
        session_id = self.demarrer().data["id"]
        question = self.client.get(f"/quiz/sessions/{session_id}/", **self.auth()).data["questions"][0]
        self.client.post(
            f"/quiz/sessions/{session_id}/questions/{question['id']}/answer/",
            {"resultat_declare": "ECHEC"}, format="json", **self.auth(),
        )
        self.client.post(f"/quiz/sessions/{session_id}/completer/", **self.auth())

        self.assertEqual(self.client.get(f"/quiz/historique/{session_id}/", **self.auth()).status_code, 200)
        self.assertEqual(self.client.get("/quiz/en-cours/", **self.auth()).status_code, 200)
        ratees = self.client.post(f"/quiz/sessions/{session_id}/refaire-ratees/", **self.auth())
        self.assertEqual(ratees.status_code, 201, ratees.data)

    def test_les_routes_hors_seance_sont_refusees_a_l_invite(self):
        for chemin in ("/quiz/parcours/", "/quiz/plan-du-jour/", "/quiz/accueil/", "/auth/me/", "/quiz/historique/"):
            self.assertEqual(self.client.get(chemin, **self.auth()).status_code, 403, chemin)

    def test_un_invite_ne_voit_pas_la_seance_d_un_autre(self):
        session_id = self.demarrer().data["id"]
        autre = _jeton(APIClient())
        reponse = self.client.get(f"/quiz/sessions/{session_id}/", **self.auth(autre))
        self.assertEqual(reponse.status_code, 404)

    def test_les_fiches_pdf_restent_reservees_aux_abonnes(self):
        session_id = self.demarrer().data["id"]
        reponse = self.client.get(f"/quiz/sessions/{session_id}/fiche-pdf/", **self.auth())
        self.assertEqual(reponse.status_code, 403)


class RattachementQuizTests(_Base):
    def _jouer_une_seance(self):
        session_id = self.demarrer().data["id"]
        for question in self.client.get(f"/quiz/sessions/{session_id}/", **self.auth()).data["questions"]:
            self.repondre(session_id, question)
        self.client.post(f"/quiz/sessions/{session_id}/completer/", **self.auth())
        return session_id

    def _inscrire(self, numero):
        with patch("users.otp_service.get_sms_backend"):
            self.client.post("/auth/otp/request/", {"phone_number": numero})
        code = OTPCode.objects.get(destination=f"+237{numero}").code
        return self.client.post(
            "/auth/otp/verify/", {"phone_number": numero, "code": code}, HTTP_X_INVITE_TOKEN=self.jeton,
        )

    def test_un_compte_neuf_garde_sa_seance_et_ses_points(self):
        session_id = self._jouer_une_seance()
        invite = User.objects.get(est_invite=True)
        xp_avant = sum(GainXP.objects.filter(profil=invite.profils.get()).values_list("points", flat=True))
        self.assertGreater(xp_avant, 0)

        reponse = self._inscrire("677900110")
        self.assertEqual(reponse.status_code, 200)

        user = User.objects.get(phone_number="+237677900110")
        session = QuizSession.objects.get(pk=session_id)
        self.assertEqual(session.profil.compte_id, user.pk)
        self.assertEqual(sum(GainXP.objects.filter(profil=session.profil).values_list("points", flat=True)), xp_avant)
        # Et le vrai jeton relit la séance, comme n'importe quel compte.
        relue = self.client.get(f"/quiz/historique/{session_id}/", HTTP_AUTHORIZATION=f"Bearer {reponse.data['access']}")
        self.assertEqual(relue.status_code, 200)

    def test_un_compte_deja_utilise_recoit_les_seances_et_l_xp(self):
        existant = User.objects.create_user(phone_number="677900120", password="x")
        profil = existant.profils.get()
        # Une activité d'élève : ce profil n'est plus « vierge ». Un total du jour existe déjà, qu'il faudra additionner.
        JourXP.objects.create(profil=profil, jour=invites.timezone.localdate(), xp=10, objectif=30)
        session_id = self._jouer_une_seance()
        profil_invite = User.objects.get(est_invite=True).profils.get()
        xp_invite = sum(GainXP.objects.filter(profil=profil_invite).values_list("points", flat=True))
        jours_invite = JourXP.objects.filter(profil=profil_invite).count()
        self.assertGreater(xp_invite, 0)
        self.assertEqual(jours_invite, 1)

        reponse = self._inscrire("677900120")
        self.assertEqual(reponse.status_code, 200)

        self.assertEqual(QuizSession.objects.get(pk=session_id).profil_id, profil.pk)
        self.assertEqual(sum(GainXP.objects.filter(profil=profil).values_list("points", flat=True)), xp_invite)
        # Le total du jour s'additionne (une seule ligne par jour), l'objectif reste celui du compte.
        jour = JourXP.objects.get(profil=profil)
        self.assertEqual(jour.xp, 10 + xp_invite)
        self.assertEqual(jour.objectif, 30)

    def test_une_revision_deja_programmee_sur_le_compte_n_est_pas_ecrasee(self):
        existant = User.objects.create_user(phone_number="677900130", password="x")
        profil = existant.profils.get()
        RevisionSchedule.objects.create(
            profil=profil, cursus=self.cursus, subject=self.subject, theme=self.theme_gratuit,
            palier=2, due_at=invites.timezone.localdate(),
        )
        # Une réponse ratée de l'invité programme une révision du même thème.
        session_id = self.demarrer().data["id"]
        question = self.client.get(f"/quiz/sessions/{session_id}/", **self.auth()).data["questions"][0]
        self.client.post(
            f"/quiz/sessions/{session_id}/questions/{question['id']}/answer/",
            {"resultat_declare": "ECHEC"}, format="json", **self.auth(),
        )
        profil_invite = User.objects.get(est_invite=True).profils.get()
        self.assertTrue(RevisionSchedule.objects.filter(profil=profil_invite).exists())

        self.assertEqual(self._inscrire("677900130").status_code, 200)

        self.assertEqual(RevisionSchedule.objects.filter(profil=profil).count(), 1)
        self.assertEqual(RevisionSchedule.objects.get(profil=profil).palier, 2)
        self.assertEqual(QuizAnswer.objects.count(), 1)  # la réponse de l'invité n'a pas disparu avec lui
