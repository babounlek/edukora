"""Habitudes de retour (voir analytics.retention)."""

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from catalog.models import Cursus, Subject
from quiz.models import (
    ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, SeanceJournaliere, StatutSeance,
)
from quiz.tests import _make_competence_item
from users.models import User

from .models import AnalyticsEvent, EventName
from .retention import jours_actifs_par_profil, retention


class RetentionTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.first()
        self.maintenant = timezone.now()
        self.aujourdhui = timezone.localtime(self.maintenant).date()
        self._n = 0

    def eleve(self):
        self._n += 1
        return User.objects.create_user(phone_number=f"6772000{self._n:02d}", password="x").profils.first()

    def seance_terminee(self, profil, *, il_y_a, ordre=1):
        quand = self.maintenant - timedelta(days=il_y_a)
        return SeanceJournaliere.objects.create(
            profil=profil, cursus=self.cursus, date=timezone.localtime(quand).date(),
            origine=OrigineSeance.DIAGNOSTIC, ordre=ordre, statut=StatutSeance.TERMINEE, termine_at=quand,
        )

    def test_retour_a_j1_et_j7_se_lit_depuis_le_premier_jour_actif(self):
        revient_j1 = self.eleve()
        ne_revient_pas = self.eleve()
        for il_y_a in (20, 19, 13):
            self.seance_terminee(revient_j1, il_y_a=il_y_a)
        self.seance_terminee(ne_revient_pas, il_y_a=20)

        rapport = retention(30, maintenant=self.maintenant)

        self.assertEqual(rapport["nouveaux_profils_actifs"], 2)
        self.assertEqual(rapport["retour"]["j1"], {"eligibles": 2, "revenus": 1, "part": 50.0})
        # J+7 exact : 20 jours - 13 jours = 7 jours après le premier jour.
        self.assertEqual(rapport["retour"]["j7"]["revenus"], 1)
        self.assertEqual(rapport["retour"]["semaine_suivante"]["revenus"], 1)

    def test_un_profil_trop_recent_n_est_pas_juge(self):
        recent = self.eleve()
        self.seance_terminee(recent, il_y_a=2)
        rapport = retention(30, maintenant=self.maintenant)
        self.assertEqual(rapport["retour"]["j1"]["eligibles"], 1)
        self.assertEqual(rapport["retour"]["j7"]["eligibles"], 0)
        self.assertIsNone(rapport["retour"]["j7"]["part"])

    def test_un_eleve_actif_depuis_longtemps_n_est_pas_un_nouveau(self):
        ancien = self.eleve()
        self.seance_terminee(ancien, il_y_a=90, ordre=1)
        self.seance_terminee(ancien, il_y_a=5, ordre=2)
        rapport = retention(30, maintenant=self.maintenant)
        self.assertEqual(rapport["nouveaux_profils_actifs"], 0)

    def test_une_seance_seulement_proposee_n_est_pas_une_activite(self):
        profil = self.eleve()
        SeanceJournaliere.objects.create(
            profil=profil, cursus=self.cursus, date=self.aujourdhui, origine=OrigineSeance.DIAGNOSTIC,
            ordre=1, statut=StatutSeance.PROPOSEE,
        )
        self.assertEqual(jours_actifs_par_profil(), {})

    def test_une_reponse_de_quiz_compte_comme_jour_actif(self):
        profil = self.eleve()
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        item = _make_competence_item(subject, self.cursus)
        session = QuizSession.objects.create(profil=profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        qq = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        reponse = QuizAnswer.objects.create(quiz_question=qq)
        QuizAnswer.objects.filter(pk=reponse.pk).update(answered_at=self.maintenant - timedelta(days=3))

        jours = jours_actifs_par_profil()
        self.assertEqual(jours[profil.id], {timezone.localtime(self.maintenant - timedelta(days=3)).date()})

    def test_quiz_termines_et_abandons(self):
        profil = self.eleve()
        QuizSession.objects.create(profil=profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, completed_at=self.maintenant)
        QuizSession.objects.create(profil=profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        AnalyticsEvent.objects.create(name=EventName.QUIZ_ABANDONNE, user=profil.compte)

        quiz = retention(30)["quiz"]
        self.assertEqual((quiz["commences"], quiz["termines"], quiz["part_terminee"]), (2, 1, 50.0))
        self.assertEqual(quiz["abandons_declares"], 1)

    def test_frequence_sans_activite_ne_divise_pas_par_zero(self):
        rapport = retention(30, maintenant=self.maintenant)
        self.assertIsNone(rapport["frequence"]["jours_actifs_par_profil"])
        self.assertIsNone(rapport["quiz"]["part_terminee"])

    def test_la_commande_s_execute(self):
        sortie = StringIO()
        call_command("rapport_retention", stdout=sortie)
        self.assertIn("Habitudes de retour", sortie.getvalue())
        sortie = StringIO()
        call_command("rapport_retention", "--json", stdout=sortie)
        self.assertIn('"retour"', sortie.getvalue())
