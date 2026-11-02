"""
Quiz chronométrés, au choix de l'élève - voir quiz.chrono.

Invariants testés : le chrono est facultatif (désactivé par défaut) ; sa durée est figée à la création et
l'échéance vient du serveur ; passé l'échéance les réponses données restent mais une nouvelle réponse est
refusée ; une session chronométrée est NEUTRE pour la progression (XP, révision, maîtrise) ; le chrono ne
s'applique ni au test de niveau ni à l'étape quiz d'une séance du jour.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse
from subscriptions.models import Subscription
from users.models import User

from . import chrono
from .historique import rejouer_session
from .models import GainXP, ModeQuiz, QuizAnswer, QuizSession, RevisionSchedule
from .services import creer_questions, maitrise_par_theme
from .tests import _make_competence_item

CHOIX = [{"lettre": "a", "texte": "faux"}, {"lettre": "b", "texte": "juste"}, {"lettre": "c", "texte": "autre"}]


class _Base(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677700011", password="x")
        self.profil = self.user.profils.first()
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.items = [
            _make_competence_item(
                self.subject, self.cursus, theme=Tag.objects.create(name=f"chrono-{i}"), numero=f"c{i}",
                type_reponse=TypeReponse.QCM, choix=CHOIX, reponse_correcte="b",
            )
            for i in range(4)
        ]
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=3),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _demarrer(self, **corps):
        corps = {"cursus": self.cursus.pk, "subject": self.subject.pk, "mode": "PRATIQUE", "n": 4, **corps}
        return self.client.post("/quiz/sessions/", corps, format="json")

    def _repondre(self, session_id, quiz_question_id, lettre="b"):
        return self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/", {"reponse_choisie": lettre},
            format="json",
        )

    def _vieillir(self, session, secondes):
        """Recule le début de la session : l'échéance est started_at + durée, pas une horloge du client."""
        QuizSession.objects.filter(pk=session.pk).update(started_at=timezone.now() - timedelta(seconds=secondes))
        session.refresh_from_db()


class DemarrageTests(_Base):
    def test_a_quiz_has_no_chrono_unless_asked(self):
        reponse = self._demarrer()

        self.assertEqual(reponse.status_code, 201)
        corps = reponse.json()
        self.assertFalse(corps["chrono_actif"])
        self.assertIsNone(corps["echeance"])
        self.assertIsNone(corps["duree_limite_secondes"])
        self.assertFalse(corps["chrono_ecoule"])

    def test_chrono_duration_is_generous_and_fixed_at_creation(self):
        corps = self._demarrer(chrono=True).json()

        self.assertTrue(corps["chrono_actif"])
        self.assertEqual(corps["duree_limite_secondes"], 4 * chrono.SECONDES_PAR_QCM)
        self.assertEqual(corps["temps_additionnel_pct"], 0)
        self.assertIsNotNone(corps["echeance"])

    def test_additional_time_lengthens_the_chrono(self):
        corps = self._demarrer(chrono=True, temps_additionnel=50).json()

        self.assertEqual(corps["duree_limite_secondes"], 4 * chrono.SECONDES_PAR_QCM * 3 // 2)
        self.assertEqual(corps["temps_additionnel_pct"], 50)

    def test_unknown_additional_time_is_refused_before_any_session_is_created(self):
        reponse = self._demarrer(chrono=True, temps_additionnel=33)

        self.assertEqual(reponse.status_code, 400)
        self.assertFalse(QuizSession.objects.exists())

    def test_the_level_test_is_never_timed(self):
        corps = self._demarrer(chrono=True, mode="DIAGNOSTIC").json()

        self.assertFalse(corps["chrono_actif"])

    def test_the_quiz_step_of_a_daily_session_is_never_timed(self):
        corps = self._demarrer(chrono=True, seance=1).json()

        self.assertFalse(corps["chrono_actif"])

    def test_the_deadline_is_the_server_start_plus_the_duration(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])

        self.assertEqual(chrono.echeance(session), session.started_at + timedelta(seconds=session.duree_limite_secondes))

    def test_resuming_after_closing_the_tab_does_not_stop_the_clock(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        self._vieillir(session, session.duree_limite_secondes + 60)

        corps = self.client.get(f"/quiz/sessions/{session.pk}/").json()

        self.assertTrue(corps["chrono_actif"])
        self.assertTrue(corps["chrono_ecoule"])


class EcheanceTests(_Base):
    def setUp(self):
        super().setUp()
        self.session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        self.qs = list(self.session.quiz_questions.order_by("ordre"))

    def test_answers_are_accepted_while_time_remains(self):
        self.assertEqual(self._repondre(self.session.pk, self.qs[0].pk).status_code, 200)

    def test_a_new_answer_after_the_deadline_is_refused_but_earlier_answers_stay(self):
        self._repondre(self.session.pk, self.qs[0].pk)
        self._vieillir(self.session, self.session.duree_limite_secondes + 60)

        refus = self._repondre(self.session.pk, self.qs[1].pk)

        self.assertEqual(refus.status_code, 409)
        self.assertTrue(refus.json()["chrono_ecoule"])
        self.assertTrue(QuizAnswer.objects.filter(quiz_question=self.qs[0]).exists())
        self.assertFalse(QuizAnswer.objects.filter(quiz_question=self.qs[1]).exists())

    def test_a_late_arrival_within_the_network_margin_is_still_accepted(self):
        self._vieillir(self.session, self.session.duree_limite_secondes + chrono.TOLERANCE_RESEAU_SECONDES - 3)

        self.assertEqual(self._repondre(self.session.pk, self.qs[0].pk).status_code, 200)

    def test_the_paper_can_still_be_handed_in_after_the_deadline(self):
        self._repondre(self.session.pk, self.qs[0].pk)
        self._vieillir(self.session, self.session.duree_limite_secondes + 600)

        resultat = self.client.post(f"/quiz/sessions/{self.session.pk}/completer/")

        self.assertEqual(resultat.status_code, 200)
        corps = resultat.json()
        self.assertEqual(corps["questions_repondues"], 1)
        self.assertTrue(corps["chrono_actif"])
        self.assertTrue(corps["neutre_progression"])

    def test_an_untimed_quiz_never_expires(self):
        libre = QuizSession.objects.get(pk=self._demarrer().json()["id"])
        self._vieillir(libre, 10 * 24 * 3600)

        premiere = libre.quiz_questions.order_by("ordre").first()

        self.assertEqual(self._repondre(libre.pk, premiere.pk).status_code, 200)


class NeutraliteTests(_Base):
    def _jouer_tout(self, **corps):
        session = QuizSession.objects.get(pk=self._demarrer(**corps).json()["id"])
        for quiz_question in session.quiz_questions.order_by("ordre"):
            self._repondre(session.pk, quiz_question.pk, "b")
        return session

    def test_a_timed_quiz_earns_no_xp_and_leaves_no_trace_in_revision_or_mastery(self):
        session = self._jouer_tout(chrono=True)

        self.assertEqual(QuizAnswer.objects.filter(quiz_question__session=session).count(), 4)
        self.assertFalse(GainXP.objects.filter(quiz_answer__quiz_question__session=session).exists())
        self.assertFalse(RevisionSchedule.objects.filter(profil=self.profil).exists())
        self.assertEqual(maitrise_par_theme(self.profil, self.cursus), [])

    def test_a_timed_wrong_answer_does_not_open_a_revision_either(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        premiere = session.quiz_questions.order_by("ordre").first()

        self._repondre(session.pk, premiere.pk, "a")

        self.assertFalse(RevisionSchedule.objects.filter(profil=self.profil).exists())

    def test_the_same_quiz_untimed_does_count(self):
        self._jouer_tout()

        self.assertTrue(GainXP.objects.exists())
        self.assertNotEqual(maitrise_par_theme(self.profil, self.cursus), [])

    def test_the_result_says_why_nothing_moved(self):
        session = self._jouer_tout(chrono=True)

        corps = self.client.post(f"/quiz/sessions/{session.pk}/completer/").json()

        self.assertTrue(corps["neutre_progression"])
        self.assertEqual(corps["xp"]["session"]["total"], 0)
        self.assertEqual(corps["score"], 4)
        self.assertIsNotNone(corps["temps_utilise_secondes"])

    def test_an_untimed_result_carries_no_chrono_block(self):
        session = self._jouer_tout()

        corps = self.client.post(f"/quiz/sessions/{session.pk}/completer/").json()

        self.assertFalse(corps["chrono_actif"])
        self.assertNotIn("neutre_progression", corps)


class RecordTests(_Base):
    def _session_terminee(self, secondes, repondre_tout=True):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        qs = list(session.quiz_questions.order_by("ordre"))
        for quiz_question in qs if repondre_tout else qs[:2]:
            self._repondre(session.pk, quiz_question.pk)
        debut = timezone.now() - timedelta(seconds=secondes)
        QuizSession.objects.filter(pk=session.pk).update(started_at=debut)
        # Dernier clic de réponse à `secondes` après le début.
        QuizAnswer.objects.filter(quiz_question__session=session).update(answered_at=debut + timedelta(seconds=secondes))
        session.refresh_from_db()
        return session, self.client.post(f"/quiz/sessions/{session.pk}/completer/").json()

    def test_the_first_time_is_a_record_but_not_a_beaten_one(self):
        _, corps = self._session_terminee(100)

        self.assertEqual(corps["record_secondes"], 100)
        self.assertFalse(corps["nouveau_record"])

    def test_a_faster_run_beats_the_record(self):
        self._session_terminee(100)

        _, corps = self._session_terminee(80)

        self.assertEqual(corps["record_secondes"], 80)
        self.assertTrue(corps["nouveau_record"])

    def test_a_slower_run_keeps_the_previous_record(self):
        self._session_terminee(80)

        _, corps = self._session_terminee(120)

        self.assertEqual(corps["record_secondes"], 80)
        self.assertFalse(corps["nouveau_record"])

    def test_a_half_empty_paper_is_not_a_time_to_beat(self):
        _, corps = self._session_terminee(20, repondre_tout=False)

        self.assertIsNone(corps["record_secondes"])
        self.assertFalse(corps["nouveau_record"])

    def test_the_time_used_never_exceeds_the_allowance(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        self._vieillir(session, 10 * 3600)
        self.client.post(f"/quiz/sessions/{session.pk}/completer/")
        session.refresh_from_db()

        self.assertEqual(chrono.temps_utilise_secondes(session), session.duree_limite_secondes)


class ReglageEtRejeuTests(_Base):
    def test_the_profile_preference_is_off_by_default_and_can_be_switched(self):
        self.assertFalse(self.client.get("/quiz/chrono/").json()["quiz_chronometres"])

        corps = self.client.put("/quiz/chrono/", {"quiz_chronometres": True}, format="json").json()

        self.assertTrue(corps["quiz_chronometres"])
        self.profil.refresh_from_db()
        self.assertTrue(self.profil.quiz_chronometres)
        self.assertEqual(corps["temps_additionnel_possibles"], list(chrono.TEMPS_ADDITIONNEL_POSSIBLES))

    def test_the_preference_must_be_a_boolean(self):
        reponse = self.client.put("/quiz/chrono/", {"quiz_chronometres": "oui"}, format="json")

        self.assertEqual(reponse.status_code, 400)

    def test_the_preference_does_not_time_a_quiz_by_itself(self):
        self.client.put("/quiz/chrono/", {"quiz_chronometres": True}, format="json")

        self.assertFalse(self._demarrer().json()["chrono_actif"])

    def test_a_replay_inherits_the_chrono_of_the_replayed_attempt_unless_told_otherwise(self):
        origine = QuizSession.objects.get(pk=self._demarrer(chrono=True, temps_additionnel=25).json()["id"])
        origine.completed_at = timezone.now()
        origine.save(update_fields=["completed_at"])

        herite = self.client.post(f"/quiz/historique/{origine.pk}/rejouer/", {}, format="json").json()
        libre = self.client.post(f"/quiz/historique/{origine.pk}/rejouer/", {"chrono": False}, format="json").json()

        self.assertTrue(herite["chrono_actif"])
        self.assertEqual(herite["temps_additionnel_pct"], 25)
        self.assertFalse(libre["chrono_actif"])
        self.assertNotEqual(herite["id"], libre["id"])

    def test_a_blank_timed_replay_that_has_expired_is_not_reused(self):
        origine = QuizSession.objects.get(pk=self._demarrer().json()["id"])
        origine.completed_at = timezone.now()
        origine.save(update_fields=["completed_at"])
        ancien, _ = rejouer_session(self.profil, origine, chronometre=True)
        self._vieillir(ancien, ancien.duree_limite_secondes + 60)

        neuf, cree = rejouer_session(self.profil, origine, chronometre=True)

        self.assertTrue(cree)
        self.assertNotEqual(neuf.pk, ancien.pk)

    def test_the_history_shows_the_chrono_and_the_time_used(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        for quiz_question in session.quiz_questions.order_by("ordre"):
            self._repondre(session.pk, quiz_question.pk)
        self.client.post(f"/quiz/sessions/{session.pk}/completer/")

        ligne = self.client.get("/quiz/historique/").json()["results"][0]

        self.assertTrue(ligne["chrono_actif"])
        self.assertEqual(ligne["duree_limite_secondes"], 4 * chrono.SECONDES_PAR_QCM)
        self.assertIsNotNone(ligne["temps_utilise_secondes"])

    def test_an_expired_session_is_listed_as_to_hand_in(self):
        session = QuizSession.objects.get(pk=self._demarrer(chrono=True).json()["id"])
        self._repondre(session.pk, session.quiz_questions.order_by("ordre").first().pk)
        self._vieillir(session, session.duree_limite_secondes + 60)

        en_cours = self.client.get("/quiz/en-cours/").json()

        self.assertEqual(len(en_cours), 1)
        self.assertTrue(en_cours[0]["a_terminer"])
        self.assertTrue(en_cours[0]["chrono_ecoule"])
