"""Une épreuve inédite rendue nourrit la séance du jour : thèmes ratés ou laissés de côté."""

from datetime import timedelta
from unittest import mock

from django.utils import timezone

from quiz.models import RevisionSchedule

from .models import TentativeInedite
from .test_notation import NotationAPITestCase


class RevisionsApresEpreuveTests(NotationAPITestCase):
    def rendre(self):
        return self.client.post(self.url("completer"))

    def test_une_question_laissee_de_cote_planifie_la_revision_de_son_theme(self):
        # Ni la QCM ni l'ouverte ne sont traitées : le thème commun revient demain.
        reponse = self.rendre()

        planification = RevisionSchedule.objects.get(user=self.user, cursus=self.cursus)
        self.assertEqual(planification.theme.name, "Suites numériques")
        self.assertEqual(planification.due_at, timezone.localdate() + timedelta(days=1))
        self.assertEqual(
            reponse.data["themes_a_reviser"],
            [{"theme": "Suites numériques", "echeance": planification.due_at.isoformat()}],
        )

    def test_rendre_deux_fois_ne_replanifie_pas(self):
        self.rendre()
        with mock.patch("inedit.views.enregistrer_resultat_pour_revision") as enregistrer:
            self.rendre()
        enregistrer.assert_not_called()

    def test_un_theme_reussi_partout_ne_revient_pas(self):
        self.ouverte.criteres_notation = []
        self.ouverte.save(update_fields=["criteres_notation"])
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 4}, format="json")

        reponse = self.rendre()

        self.assertEqual(reponse.data["themes_a_reviser"], [])
        self.assertFalse(RevisionSchedule.objects.filter(user=self.user).exists())

    def test_un_theme_partiellement_reussi_est_a_reviser(self):
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 1}, format="json")

        reponse = self.rendre()

        self.assertEqual([t["theme"] for t in reponse.data["themes_a_reviser"]], ["Suites numériques"])

    def test_la_planification_n_est_faite_que_pour_l_eleve_qui_rend(self):
        autre = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        self.rendre()
        self.assertEqual(RevisionSchedule.objects.filter(user=self.user).count(), 1)
        self.assertIsNone(autre.submitted_at)
