from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .bilan import PERIODE_JOURS, bilan_de_periode
from .models import ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, SeanceJournaliere, StatutSeance
from .tests import _make_competence_item


class BilanDePeriodeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="b1")
        self.session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.ordre = 0

    def _abonner(self, expire_dans_jours=10, cree_il_y_a_jours=100):
        sub = Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=expire_dans_jours),
        )
        # created_at est auto_now_add : on le recule pour simuler un abonnement ancien.
        Subscription.objects.filter(pk=sub.pk).update(created_at=timezone.now() - timedelta(days=cree_il_y_a_jours))
        return sub

    def _repondre(self, correcte, il_y_a_jours=0, item=None):
        self.ordre += 1
        item = item or self.item
        quiz_question = QuizQuestion.objects.create(session=self.session, competence_item=item, ordre=self.ordre)
        answer = QuizAnswer.objects.create(
            quiz_question=quiz_question, resultat_declare="REUSSI" if correcte else "ECHEC",
        )
        QuizAnswer.objects.filter(pk=answer.pk).update(answered_at=timezone.now() - timedelta(days=il_y_a_jours))

    def _seance(self, il_y_a_jours, statut=StatutSeance.TERMINEE):
        return SeanceJournaliere.objects.create(
            user=self.user, cursus=self.cursus, date=timezone.localdate() - timedelta(days=il_y_a_jours),
            origine=OrigineSeance.DIAGNOSTIC, statut=statut, etapes=[],
        )

    def test_returns_none_without_any_subscription(self):
        self.assertIsNone(bilan_de_periode(self.user, self.cursus))

    def test_counts_only_finished_sessions_inside_the_window(self):
        self._abonner()
        self._seance(il_y_a_jours=2)
        self._seance(il_y_a_jours=3, statut=StatutSeance.PROPOSEE)
        self._seance(il_y_a_jours=PERIODE_JOURS + 5)

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertEqual(bilan["seances"], 1)
        self.assertEqual(bilan["jours_actifs"], 1)
        self.assertTrue(bilan["a_de_l_activite"])

    def test_no_activity_is_flagged_so_the_front_can_stay_silent(self):
        self._abonner()

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertFalse(bilan["a_de_l_activite"])
        self.assertIsNone(bilan["taux_reussite"])

    def test_success_rate_compares_the_window_with_what_came_before(self):
        self._abonner()
        for _ in range(4):  # avant : 1 sur 4
            self._repondre(False, il_y_a_jours=60)
        self._repondre(True, il_y_a_jours=60)
        for _ in range(3):  # période : 3 sur 4
            self._repondre(True, il_y_a_jours=5)
        self._repondre(False, il_y_a_jours=5)

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertEqual(bilan["questions"], 4)
        self.assertEqual(bilan["taux_reussite"], 75)
        self.assertEqual(bilan["taux_avant"], 20)
        self.assertEqual(bilan["matieres"][0]["taux_avant"], 20)
        self.assertEqual(bilan["matieres"][0]["taux_periode"], 75)

    def test_best_streak_is_counted_inside_the_window_only(self):
        self._abonner()
        for _ in range(5):  # série d'avant la période : ne compte pas
            self._repondre(True, il_y_a_jours=60)
        for correcte in (True, True, False, True):
            self._repondre(correcte, il_y_a_jours=3)

        self.assertEqual(bilan_de_periode(self.user, self.cursus)["meilleure_serie"], 2)

    def test_theme_crossing_the_mastery_threshold_is_consolidated(self):
        self._abonner()
        self._repondre(False, il_y_a_jours=60)
        for _ in range(4):
            self._repondre(True, il_y_a_jours=4)

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertEqual(bilan["themes_consolides_total"], 1)
        self.assertEqual(bilan["themes_consolides"][0]["theme"], "dérivation")

    def test_theme_already_mastered_before_the_window_is_not_credited_again(self):
        self._abonner()
        for _ in range(4):
            self._repondre(True, il_y_a_jours=60)
        self._repondre(True, il_y_a_jours=3)

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertEqual(bilan["themes_consolides_total"], 0)
        self.assertEqual(bilan["themes_travailles"], 1)

    def test_one_lucky_answer_is_not_enough_to_consolidate_a_theme(self):
        self._abonner()
        self._repondre(True, il_y_a_jours=1)

        self.assertEqual(bilan_de_periode(self.user, self.cursus)["themes_consolides_total"], 0)

    def test_window_stops_at_expiry_and_ignores_later_answers(self):
        self._abonner(expire_dans_jours=-10)
        self._repondre(True, il_y_a_jours=15)  # pendant l'abonnement
        self._repondre(False, il_y_a_jours=2)  # après l'expiration : sans accès légitime

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertFalse(bilan["abonnement_actif"])
        self.assertEqual(bilan["questions"], 1)
        self.assertEqual(bilan["taux_reussite"], 100)

    def test_window_never_starts_before_the_subscription_was_created(self):
        self._abonner(cree_il_y_a_jours=5)
        self._repondre(True, il_y_a_jours=20)  # d'avant l'abonnement : compte comme "avant"

        bilan = bilan_de_periode(self.user, self.cursus)

        self.assertEqual(bilan["questions"], 0)
        self.assertEqual(bilan["debut"], timezone.localdate() - timedelta(days=5))

    def test_other_users_activity_is_never_counted(self):
        self._abonner()
        autre = User.objects.create_user(phone_number="677300002", password="x")
        session = QuizSession.objects.create(user=autre, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=self.item, ordre=1)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare="REUSSI")

        self.assertEqual(bilan_de_periode(self.user, self.cursus)["questions"], 0)


class BilanPeriodeApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300003", password="x")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.get("/quiz/bilan-periode/", {"cursus": self.cursus.id})
        self.assertIn(response.status_code, (401, 403))

    def test_404_when_never_subscribed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/quiz/bilan-periode/", {"cursus": self.cursus.id})
        self.assertEqual(response.status_code, 404)

    def test_400_without_cursus_nor_declared_exam(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/quiz/bilan-periode/").status_code, 400)

    def test_returns_the_bilan_for_an_expired_subscription(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() - timedelta(days=3),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/quiz/bilan-periode/", {"cursus": self.cursus.id})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["abonnement_actif"])
        self.assertFalse(response.data["a_de_l_activite"])


class BilanHebdomadaireEtJalonsTests(BilanDePeriodeTests):
    """Même fixtures que le bilan mensuel : la fenêtre de 7 jours et les compteurs de jalons."""

    def test_weekly_window_only_counts_the_last_seven_days(self):
        self._abonner()
        self._seance(il_y_a_jours=2)
        self._seance(il_y_a_jours=12)

        bilan = bilan_de_periode(self.user, self.cursus, jours=7)

        self.assertEqual(bilan["seances"], 1)
        self.assertEqual(bilan["jalons"]["seances_total"], 2)
        self.assertEqual(bilan["jalons"]["seances_avant"], 1)

    def test_milestone_counters_split_before_and_after_the_window(self):
        self._abonner()
        for _ in range(3):
            self._repondre(True, il_y_a_jours=40)
        for _ in range(2):
            self._repondre(True, il_y_a_jours=2)

        jalons = bilan_de_periode(self.user, self.cursus, jours=7)["jalons"]

        self.assertEqual((jalons["questions_avant"], jalons["questions_total"]), (3, 5))
        self.assertEqual((jalons["solides_avant"], jalons["solides_total"]), (1, 1))

    def test_a_theme_becoming_solid_inside_the_window_shows_in_the_counters(self):
        self._abonner()
        self._repondre(False, il_y_a_jours=40)
        for _ in range(4):
            self._repondre(True, il_y_a_jours=2)

        jalons = bilan_de_periode(self.user, self.cursus, jours=7)["jalons"]

        self.assertEqual((jalons["solides_avant"], jalons["solides_total"]), (0, 1))
