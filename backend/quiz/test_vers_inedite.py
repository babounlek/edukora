"""Fin de quiz : une inédite entière du même cursus est proposée, jamais une mini ni une épreuve déjà commencée."""
from catalog.models import StatutContenu
from inedit.models import Blueprint, EpreuveInedite, TentativeInedite

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .test_erreurs import ErreursFixture


class VersInediteTests(ErreursFixture):
    def _epreuve(self, titre, **kwargs):
        kwargs.setdefault("statut", StatutContenu.VALIDE)
        blueprint = Blueprint.objects.create(subject=self.item("bp").subject, titre=f"bp {titre}")
        blueprint.cursus.add(self.cursus)
        epreuve = EpreuveInedite.objects.create(blueprint=blueprint, subject=blueprint.subject, titre=titre, **kwargs)
        epreuve.cursus.add(self.cursus)
        return epreuve

    def _resultat(self):
        quiz = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        question = QuizQuestion.objects.create(session=quiz, competence_item=self.item("q1"), ordre=1)
        QuizAnswer.objects.create(quiz_question=question, resultat_declare="REUSSI")
        return self.client.post(f"/quiz/sessions/{quiz.pk}/completer/").data

    def test_sans_inedite_publiee_le_champ_est_vide(self):
        self._epreuve("Brouillon", statut=StatutContenu.BROUILLON)

        self.assertIsNone(self._resultat()["inedite_suggeree"])

    def test_une_mini_n_est_pas_proposee_mais_une_epreuve_entiere_oui(self):
        self._epreuve("Mini", est_mini=True)
        entiere = self._epreuve("Entière")

        suggeree = self._resultat()["inedite_suggeree"]

        self.assertEqual(suggeree["id"], entiere.id)
        self.assertTrue(suggeree["meme_matiere"])

    def test_une_epreuve_deja_commencee_n_est_plus_proposee(self):
        epreuve = self._epreuve("Déjà vue")
        TentativeInedite.objects.create(profil=self.profil, epreuve=epreuve)

        self.assertIsNone(self._resultat()["inedite_suggeree"])


class InediteOfferteEssaiTests(ErreursFixture):
    """Visiteur sans compte : seule l'inédite OFFERTE du cursus est proposée."""

    def _epreuve(self, titre, **kwargs):
        blueprint = Blueprint.objects.create(subject=self.item("bp").subject, titre=f"bp {titre}")
        blueprint.cursus.add(self.cursus)
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject, titre=titre, statut=StatutContenu.VALIDE, **kwargs,
        )
        epreuve.cursus.add(self.cursus)
        return epreuve

    def _get(self, cursus):
        from rest_framework.test import APIClient

        return APIClient().get(f"/quiz/essais/inedite/?cursus={cursus}").data

    def test_une_epreuve_payante_n_est_pas_proposee(self):
        self._epreuve("Payante")

        self.assertIsNone(self._get(self.cursus.pk))

    def test_l_epreuve_offerte_est_proposee_et_un_cursus_invalide_ne_casse_rien(self):
        offerte = self._epreuve("Offerte", est_gratuite=True)

        self.assertEqual(self._get(self.cursus.pk)["id"], offerte.id)
        self.assertIsNone(self._get("abc"))


class OfferteEnPremierTests(VersInediteTests):
    def test_l_epreuve_offerte_passe_avant_une_payante_plus_recente(self):
        offerte = self._epreuve("Offerte", est_gratuite=True)
        self._epreuve("Payante plus récente")

        self.assertEqual(self._resultat()["inedite_suggeree"]["id"], offerte.id)


class MiniSuggereeTests(VersInediteTests):
    """La mini est la marche avant l'épreuve entière : réservée aux abonnés du cursus, jamais déjà commencée."""

    def test_un_abonne_recoit_la_mini_du_cursus(self):
        self.abonner()
        mini = self._epreuve("Mini", est_mini=True)

        suggeree = self._resultat()["mini_suggeree"]

        self.assertEqual(suggeree["id"], mini.id)
        self.assertTrue(suggeree["meme_matiere"])

    def test_sans_abonnement_pas_de_mini(self):
        self._epreuve("Mini", est_mini=True)

        self.assertIsNone(self._resultat()["mini_suggeree"])

    def test_une_mini_deja_commencee_ou_une_epreuve_entiere_ne_comptent_pas(self):
        self.abonner()
        vue = self._epreuve("Mini vue", est_mini=True)
        TentativeInedite.objects.create(profil=self.profil, epreuve=vue)
        self._epreuve("Entière")

        self.assertIsNone(self._resultat()["mini_suggeree"])
