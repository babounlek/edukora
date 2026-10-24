"""
Historique, consultation et rejeu des quiz - voir quiz.historique et quiz.instantane.

Les invariants testés : une tentative terminée est figée (contenu, clé, note), elle ne
survit pas qu'au parcours habituel mais aussi à une correction ou une suppression du contenu,
elle n'est visible que de son propriétaire, et un rejeu est une session neuve, identique, neutre
pour la progression.
"""

from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse
from subscriptions.models import Subscription
from users.models import User

from . import instantane
from .models import GainXP, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, RevisionSchedule
from .services import creer_questions, maitrise_par_theme
from .tests import _make_competence_item

CHOIX = [{"lettre": "a", "texte": "faux"}, {"lettre": "b", "texte": "juste"}, {"lettre": "c", "texte": "autre"}]


class _Base(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677700001", password="x")
        self.profil = self.user.profils.first()
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.items = [
            _make_competence_item(
                self.subject, self.cursus, theme=Tag.objects.create(name=f"hist-{i}"), numero=f"h{i}",
                type_reponse=TypeReponse.QCM, choix=CHOIX, reponse_correcte="b",
            )
            for i in range(3)
        ]
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _abonner(self, user=None, profil=None):
        Subscription.objects.create(
            user=user or self.user, profil=profil or self.profil, cursus=self.cursus,
            expires_at=timezone.now() + timedelta(days=3),
        )

    def _session(self, profil=None, reponses=("b", "a", "b"), terminee=True, items=None):
        """Session créée par le service (donc avec instantané), répondue puis éventuellement close."""
        session = QuizSession.objects.create(
            profil=profil or self.profil, cursus=self.cursus, subject=self.subject, mode=ModeQuiz.PRATIQUE,
        )
        creer_questions(session, items or self.items)
        for quiz_question, lettre in zip(session.quiz_questions.order_by("ordre"), reponses):
            if lettre:
                QuizAnswer.objects.create(quiz_question=quiz_question, reponse_choisie=lettre, temps_secondes=10)
        if terminee:
            session.completed_at = timezone.now()
            session.save(update_fields=["completed_at"])
        return session

    def _repondre(self, session, quiz_question, lettre):
        return self.client.post(
            f"/quiz/sessions/{session.pk}/questions/{quiz_question.pk}/answer/", {"reponse_choisie": lettre},
            format="json",
        )


class InstantaneTests(_Base):
    def test_session_questions_carry_a_snapshot_of_the_content_they_were_given(self):
        session = self._session(terminee=False, reponses=())
        figee = session.quiz_questions.order_by("ordre").first().snapshot

        self.assertEqual(figee["enonce_markdown"], "Énoncé h0.")
        self.assertEqual(figee["reponse_correcte"], "b")
        self.assertEqual(figee["choix"], CHOIX)
        self.assertEqual(figee["theme"]["name"], "hist-0")
        self.assertEqual(figee["subject"]["code"], "MATHS")

    def test_correcting_an_item_afterwards_changes_neither_the_attempt_nor_its_score(self):
        session = self._session(reponses=("b", "a", "b"))
        self.items[0].enonce_markdown = "Énoncé réécrit."
        self.items[0].corrige_markdown = "Nouveau corrigé."
        self.items[0].reponse_correcte = "c"
        self.items[0].save()

        detail = self.client.get(f"/quiz/historique/{session.pk}/").json()
        premiere = detail["questions"][0]

        self.assertEqual(premiere["enonce_markdown"], "Énoncé h0.")
        self.assertEqual(premiere["corrige_markdown"], "Corrigé h0.")
        self.assertEqual(premiere["reponse_correcte"], "b")
        self.assertTrue(premiere["reponse"]["est_correcte"])
        self.assertEqual(detail["score"], 2)
        # La clé actuelle a changé : on le signale, sans recalculer la note.
        self.assertTrue(premiere["cle_modifiee"])
        self.assertFalse(detail["questions"][1]["cle_modifiee"])

    def test_deleting_an_item_keeps_the_attempt_readable(self):
        session = self._session()
        self.items[1].delete()

        detail = self.client.get(f"/quiz/historique/{session.pk}/").json()
        deuxieme = detail["questions"][1]

        self.assertEqual(QuizQuestion.objects.filter(session=session).count(), 3)
        self.assertEqual(deuxieme["enonce_markdown"], "Énoncé h1.")
        self.assertFalse(deuxieme["contenu_disponible"])
        self.assertFalse(deuxieme["reponse"]["est_correcte"])  # « a » ≠ clé « b », toujours jugé sur la clé figée
        self.assertEqual(detail["score"], 2)

    def test_deleting_content_never_fails_on_a_session_created_before_snapshots_existed(self):
        # Ligne créée directement, comme avant l'introduction de l'instantané : pas de snapshot.
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        ancienne = QuizQuestion.objects.create(session=session, competence_item=self.items[0], ordre=1)
        self.assertIsNone(ancienne.snapshot)

        self.items[0].delete()

        ancienne.refresh_from_db()
        self.assertIsNone(ancienne.competence_item_id)
        self.assertEqual(ancienne.snapshot["enonce_markdown"], "Énoncé h0.")
        self.assertTrue(ancienne.snapshot_retroactif)

    def test_playing_a_session_in_progress_uses_the_snapshot_not_the_live_item(self):
        session = self._session(terminee=False, reponses=())
        self.items[0].reponse_correcte = "c"
        self.items[0].save()
        premiere = session.quiz_questions.order_by("ordre").first()

        reponse = self._repondre(session, premiere, "b").json()

        self.assertTrue(reponse["reponse"]["est_correcte"])
        self.assertEqual(reponse["reponse_correcte"], "b")

    def test_legacy_rows_without_snapshot_still_play_from_the_live_content(self):
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=self.items[0], ordre=1)

        reponse = self._repondre(session, quiz_question, "b").json()

        self.assertTrue(reponse["reponse"]["est_correcte"])
        self.assertEqual(instantane.donnees(quiz_question)["enonce_markdown"], "Énoncé h0.")


class RemplirInstantanesTests(_Base):
    def test_backfill_fills_missing_snapshots_flags_them_and_is_idempotent(self):
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        ancienne = QuizQuestion.objects.create(session=session, competence_item=self.items[0], ordre=1)
        recente = self._session(terminee=False, reponses=()).quiz_questions.first()
        figee_avant = recente.snapshot

        call_command("remplir_instantanes_quiz", stdout=_Sortie())
        ancienne.refresh_from_db()
        recente.refresh_from_db()

        self.assertEqual(ancienne.snapshot["enonce_markdown"], "Énoncé h0.")
        self.assertTrue(ancienne.snapshot_retroactif)
        self.assertEqual(recente.snapshot, figee_avant)  # jamais écrasé
        self.assertFalse(recente.snapshot_retroactif)

        self.items[0].enonce_markdown = "Changé après le remplissage."
        self.items[0].save()
        call_command("remplir_instantanes_quiz", stdout=_Sortie())
        ancienne.refresh_from_db()
        self.assertEqual(ancienne.snapshot["enonce_markdown"], "Énoncé h0.")  # deuxième passage : rien ne bouge

    def test_dry_run_writes_nothing(self):
        session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        ancienne = QuizQuestion.objects.create(session=session, competence_item=self.items[0], ordre=1)

        call_command("remplir_instantanes_quiz", "--dry-run", stdout=_Sortie())

        ancienne.refresh_from_db()
        self.assertIsNone(ancienne.snapshot)


class _Sortie:
    def write(self, *args, **kwargs):
        pass

    def flush(self):
        pass


class HistoriqueListeTests(_Base):
    def test_requires_authentication(self):
        self.assertEqual(APIClient().get("/quiz/historique/").status_code, 401)

    def test_empty_history(self):
        reponse = self.client.get("/quiz/historique/").json()
        self.assertEqual(reponse["count"], 0)
        self.assertEqual(reponse["results"], [])

    def test_lists_only_finished_attempts_of_the_authenticated_profile_most_recent_first(self):
        autre = User.objects.create_user(phone_number="677700002", password="x")
        self._session(profil=autre.profils.first())
        ancienne = self._session()
        ancienne.completed_at = timezone.now() - timedelta(days=2)
        ancienne.save(update_fields=["completed_at"])
        recente = self._session()
        self._session(terminee=False)  # en cours : pas dans l'historique

        resultats = self.client.get("/quiz/historique/").json()["results"]

        self.assertEqual([r["id"] for r in resultats], [recente.pk, ancienne.pk])

    def test_each_row_carries_score_percentage_and_duration(self):
        self._session(reponses=("b", "a", "b"))

        ligne = self.client.get("/quiz/historique/").json()["results"][0]

        self.assertEqual((ligne["score"], ligne["total_questions"], ligne["pourcentage"]), (2, 3, 67))
        self.assertEqual(ligne["duree_secondes"], 30)
        self.assertEqual(ligne["subject_label"], self.subject.label)

    def test_duration_is_omitted_when_a_time_is_missing(self):
        session = self._session()
        QuizAnswer.objects.filter(quiz_question__session=session).first().delete()

        ligne = self.client.get("/quiz/historique/").json()["results"][0]

        self.assertIsNone(ligne["duree_secondes"])

    def test_history_is_paginated(self):
        for _ in range(21):
            self._session(reponses=("b", "b", "b"))

        page1 = self.client.get("/quiz/historique/").json()
        page2 = self.client.get("/quiz/historique/?page=2").json()

        self.assertEqual((page1["count"], len(page1["results"]), len(page2["results"])), (21, 20, 1))
        self.assertIsNotNone(page1["next"])

    def test_the_history_query_count_does_not_grow_with_the_number_of_attempts(self):
        self._session()
        un = self._nombre_de_requetes()
        for _ in range(8):
            self._session()

        self.assertEqual(self._nombre_de_requetes(), un)

    def _nombre_de_requetes(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as capture:
            self.client.get("/quiz/historique/")
        return len(capture)


class HistoriqueDetailTests(_Base):
    def test_returns_questions_answers_corrections_and_score(self):
        session = self._session(reponses=("b", "a", None))

        detail = self.client.get(f"/quiz/historique/{session.pk}/").json()

        self.assertEqual((detail["score"], detail["total_questions"]), (1, 3))
        premiere, deuxieme, troisieme = detail["questions"]
        self.assertEqual(premiere["reponse"]["reponse_choisie"], "b")
        self.assertEqual(premiere["reponse_correcte"], "b")
        self.assertEqual(premiere["corrige_markdown"], "Corrigé h0.")
        self.assertEqual(deuxieme["reponse"]["reponse_choisie"], "a")
        self.assertFalse(deuxieme["reponse"]["est_correcte"])
        self.assertIsNone(troisieme["reponse"])  # question sans réponse : consultable, sans réponse
        self.assertFalse(detail["snapshot_retroactif"])

    def test_another_profile_cannot_read_an_attempt_by_guessing_its_id(self):
        session = self._session()
        autre = User.objects.create_user(phone_number="677700003", password="x")
        client = APIClient()
        client.force_authenticate(user=autre)

        self.assertEqual(client.get(f"/quiz/historique/{session.pk}/").status_code, 404)
        self.assertEqual(client.post(f"/quiz/historique/{session.pk}/rejouer/").status_code, 404)

    def test_an_attempt_in_progress_is_not_consultable(self):
        session = self._session(terminee=False)
        self.assertEqual(self.client.get(f"/quiz/historique/{session.pk}/").status_code, 404)

    def test_retroactive_snapshot_is_flagged(self):
        session = QuizSession.objects.create(
            profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, completed_at=timezone.now(),
        )
        QuizQuestion.objects.create(session=session, competence_item=self.items[0], ordre=1)
        call_command("remplir_instantanes_quiz", stdout=_Sortie())

        detail = self.client.get(f"/quiz/historique/{session.pk}/").json()

        self.assertTrue(detail["snapshot_retroactif"])
        self.assertTrue(detail["questions"][0]["snapshot_retroactif"])


class RejeuTests(_Base):
    def test_requires_an_active_subscription_unless_every_item_is_a_showcase_item(self):
        session = self._session()
        self.assertEqual(self.client.post(f"/quiz/historique/{session.pk}/rejouer/").status_code, 403)
        self.assertEqual(QuizSession.objects.filter(rejeu_de=session).count(), 0)

        for item in self.items:
            item.est_vitrine = True
            item.save()
        self.assertEqual(self.client.post(f"/quiz/historique/{session.pk}/rejouer/").status_code, 201)

    def test_replay_creates_a_new_independent_session_with_the_same_questions_in_the_same_order(self):
        self._abonner()
        session = self._session(reponses=("b", "a", "b"))
        avant = (session.completed_at, session.quiz_questions.count(), QuizAnswer.objects.filter(quiz_question__session=session).count())

        reponse = self.client.post(f"/quiz/historique/{session.pk}/rejouer/")
        rejeu = QuizSession.objects.get(pk=reponse.json()["id"])

        self.assertEqual(reponse.status_code, 201)
        self.assertNotEqual(rejeu.pk, session.pk)
        self.assertEqual(rejeu.rejeu_de_id, session.pk)
        self.assertEqual(rejeu.mode, ModeQuiz.PRATIQUE)
        self.assertIsNone(rejeu.completed_at)
        self.assertEqual(
            [qq.snapshot for qq in rejeu.quiz_questions.order_by("ordre")],
            [qq.snapshot for qq in session.quiz_questions.order_by("ordre")],
        )
        self.assertEqual(QuizAnswer.objects.filter(quiz_question__session=rejeu).count(), 0)  # rien de prérempli
        session.refresh_from_db()
        apres = (session.completed_at, session.quiz_questions.count(), QuizAnswer.objects.filter(quiz_question__session=session).count())
        self.assertEqual(avant, apres)  # l'ancienne tentative n'a pas bougé

    def test_replay_serves_the_snapshot_even_when_the_item_was_corrected_or_deleted(self):
        self._abonner()
        session = self._session()
        self.items[0].enonce_markdown = "Réécrit."
        self.items[0].reponse_correcte = "c"
        self.items[0].save()
        self.items[1].delete()

        rejeu_id = self.client.post(f"/quiz/historique/{session.pk}/rejouer/").json()["id"]
        questions = self.client.get(f"/quiz/sessions/{rejeu_id}/").json()["questions"]

        self.assertEqual([q["enonce_markdown"] for q in questions], ["Énoncé h0.", "Énoncé h1.", "Énoncé h2."])
        rejeu = QuizSession.objects.get(pk=rejeu_id)
        premiere = rejeu.quiz_questions.order_by("ordre").first()
        self.assertTrue(self._repondre(rejeu, premiere, "b").json()["reponse"]["est_correcte"])  # clé figée « b »

    def test_a_double_click_does_not_create_two_replays(self):
        self._abonner()
        session = self._session()

        premier = self.client.post(f"/quiz/historique/{session.pk}/rejouer/")
        second = self.client.post(f"/quiz/historique/{session.pk}/rejouer/")

        self.assertEqual((premier.status_code, second.status_code), (201, 200))
        self.assertEqual(premier.json()["id"], second.json()["id"])
        self.assertEqual(QuizSession.objects.filter(rejeu_de=session).count(), 1)

    def test_several_attempts_of_the_same_quiz_coexist_in_the_history(self):
        self._abonner()
        session = self._session()
        premier = self.client.post(f"/quiz/historique/{session.pk}/rejouer/").json()["id"]
        rejeu = QuizSession.objects.get(pk=premier)
        for quiz_question in rejeu.quiz_questions.all():
            QuizAnswer.objects.create(quiz_question=quiz_question, reponse_choisie="b", temps_secondes=5)
        rejeu.completed_at = timezone.now()
        rejeu.save(update_fields=["completed_at"])

        # Rejouer le rejeu : la chaîne pointe toujours vers l'origine, une troisième tentative naît.
        troisieme = self.client.post(f"/quiz/historique/{rejeu.pk}/rejouer/").json()["id"]

        self.assertEqual(QuizSession.objects.get(pk=troisieme).rejeu_de_id, session.pk)
        lignes = self.client.get("/quiz/historique/").json()["results"]
        self.assertEqual({l["id"]: l["numero_tentative"] for l in lignes}, {session.pk: 1, rejeu.pk: 2})
        self.assertEqual({l["nb_tentatives"] for l in lignes}, {3})
        self.assertEqual(self.client.get("/quiz/historique/").json()["count"], 2)  # la 3e est en cours

    def test_a_session_still_in_progress_cannot_be_replayed(self):
        self._abonner()
        session = self._session(terminee=False)
        self.assertEqual(self.client.post(f"/quiz/historique/{session.pk}/rejouer/").status_code, 409)


class RejeuNeutreTests(_Base):
    def _rejouer(self, session):
        self._abonner()
        return QuizSession.objects.get(pk=self.client.post(f"/quiz/historique/{session.pk}/rejouer/").json()["id"])

    def test_a_correct_answer_in_a_normal_session_earns_xp_and_advances_the_revision(self):
        schedule = RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.subject, theme=self.items[0].theme,
            palier=0, due_at=timezone.localdate() - timedelta(days=1),
        )
        session = self._session(terminee=False, reponses=())

        self._repondre(session, session.quiz_questions.order_by("ordre").first(), "b")

        schedule.refresh_from_db()
        self.assertEqual(GainXP.objects.filter(profil=self.profil).count(), 1)
        self.assertEqual(schedule.palier, 1)

    def test_a_correct_answer_in_a_replay_earns_no_xp_and_does_not_advance_the_revision(self):
        schedule = RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.subject, theme=self.items[0].theme,
            palier=0, due_at=timezone.localdate() - timedelta(days=1),
        )
        rejeu = self._rejouer(self._session(reponses=("a", "a", "a")))

        reponse = self._repondre(rejeu, rejeu.quiz_questions.order_by("ordre").first(), "b").json()

        schedule.refresh_from_db()
        self.assertEqual(GainXP.objects.filter(profil=self.profil).count(), 0)
        self.assertEqual(reponse["reponse"]["xp_gagne"], 0)
        self.assertEqual(schedule.palier, 0)
        self.assertEqual(schedule.due_at, timezone.localdate() - timedelta(days=1))

    def test_a_wrong_answer_in_a_replay_still_reopens_the_revision_of_the_theme(self):
        rejeu = self._rejouer(self._session(reponses=("b", "b", "b")))
        self.assertFalse(RevisionSchedule.objects.filter(profil=self.profil).exists())

        self._repondre(rejeu, rejeu.quiz_questions.order_by("ordre").first(), "a")

        planning = RevisionSchedule.objects.get(profil=self.profil, theme=self.items[0].theme)
        self.assertEqual(planning.palier, 0)

    def test_replay_answers_are_left_out_of_the_mastery_statistics(self):
        rejeu = self._rejouer(self._session(reponses=()))
        for quiz_question in rejeu.quiz_questions.all():
            QuizAnswer.objects.create(quiz_question=quiz_question, reponse_choisie="b")

        self.assertEqual(maitrise_par_theme(self.profil, self.cursus), [])

    def test_the_replay_does_not_count_as_a_new_diagnostic(self):
        session = self._session()
        session.mode = ModeQuiz.DIAGNOSTIC
        session.save(update_fields=["mode"])

        self.assertEqual(self._rejouer(session).mode, ModeQuiz.PRATIQUE)


class ClotureTests(_Base):
    def test_answering_after_the_attempt_is_finished_is_refused_and_changes_nothing(self):
        session = self._session(reponses=("b", "a", "b"))
        deuxieme = session.quiz_questions.order_by("ordre")[1]

        reponse = self._repondre(session, deuxieme, "b")

        self.assertEqual(reponse.status_code, 409)
        self.assertEqual(QuizAnswer.objects.get(quiz_question=deuxieme).reponse_choisie, "a")
        detail = self.client.get(f"/quiz/historique/{session.pk}/").json()
        self.assertEqual(detail["score"], 2)

    def test_completing_twice_keeps_a_single_closing_and_the_same_result(self):
        session = self._session(terminee=False)

        premiere = self.client.post(f"/quiz/sessions/{session.pk}/completer/")
        session.refresh_from_db()
        cloture = session.completed_at
        seconde = self.client.post(f"/quiz/sessions/{session.pk}/completer/")
        session.refresh_from_db()

        self.assertEqual((premiere.status_code, seconde.status_code), (200, 200))
        self.assertEqual(session.completed_at, cloture)
        self.assertEqual(premiere.json()["score"], seconde.json()["score"])

    def test_the_score_comes_from_the_backend_even_if_the_client_sends_one(self):
        session = self._session(terminee=False, reponses=("a", "a", "a"))

        resultat = self.client.post(
            f"/quiz/sessions/{session.pk}/completer/", {"score": 3, "total": 3}, format="json",
        ).json()

        self.assertEqual(resultat["score"], 0)
