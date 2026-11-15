"""La jauge d'un thème à quatre crans (R6, voir quiz.services.niveau_theme) et sa progression dans un quiz."""
from django.test import SimpleTestCase

from .models import QuizAnswer, QuizQuestion, QuizSession, ModeQuiz
from .services import niveau_theme, niveaux_avant_apres
from .test_erreurs import ErreursFixture


class NiveauThemeTests(SimpleTestCase):
    def test_les_quatre_crans(self):
        self.assertIsNone(niveau_theme(None, 0))
        self.assertEqual(niveau_theme(100, 2), "decouvert")  # deux bonnes réponses ne prouvent rien
        self.assertEqual(niveau_theme(50, 5), "en_cours")
        self.assertEqual(niveau_theme(70, 3), "solide")  # exactement est_maitrise
        self.assertEqual(niveau_theme(80, 10), "solide")
        self.assertEqual(niveau_theme(85, 6), "maitrise")
        self.assertEqual(niveau_theme(100, 5), "solide")  # le plein demande 6 réponses


class AvantApresTests(ErreursFixture):
    def _quiz_de(self, resultats, **session):
        quiz = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, **session)
        for ordre, resultat in enumerate(resultats, start=1):
            question = QuizQuestion.objects.create(session=quiz, competence_item=self.item(f"n{quiz.pk}-{ordre}"), ordre=ordre)
            QuizAnswer.objects.create(quiz_question=question, resultat_declare=resultat)
        return quiz

    def test_un_quiz_fait_passer_un_theme_de_en_cours_a_solide(self):
        self._quiz_de(["ECHEC", "ECHEC", "REUSSI"])  # 1/3 : en cours
        quiz = self._quiz_de(["REUSSI"] * 5)  # 6/8 = 75 %

        avant, apres = niveaux_avant_apres(quiz)[self.derivation.id]

        self.assertEqual((avant, apres), ("en_cours", "solide"))

    def test_un_premier_quiz_part_de_rien(self):
        quiz = self._quiz_de(["REUSSI", "REUSSI"])

        self.assertEqual(niveaux_avant_apres(quiz)[self.derivation.id], (None, "decouvert"))

    def test_un_rejeu_ou_un_quiz_chronometre_ne_fait_rien_avancer(self):
        original = self._quiz_de(["REUSSI"] * 3)
        rejeu = self._quiz_de(["REUSSI"], rejeu_de=original)
        chrono = self._quiz_de(["REUSSI"], chrono_actif=True)

        self.assertEqual(niveaux_avant_apres(rejeu), {})
        self.assertEqual(niveaux_avant_apres(chrono), {})

    def test_le_resultat_de_l_api_porte_les_deux_niveaux(self):
        self._quiz_de(["ECHEC", "ECHEC", "REUSSI"])
        quiz = self._quiz_de(["REUSSI"] * 5)

        theme = self.client.post(f"/quiz/sessions/{quiz.pk}/completer/").data["par_theme"][0]

        self.assertEqual((theme["niveau_avant"], theme["niveau_apres"]), ("en_cours", "solide"))


class RafraichissementTests(ErreursFixture):
    """R13 : un thème solide non revu depuis 30 jours repasse en file ; les paliers vont jusqu'à J+35."""

    def _maitriser(self, il_y_a_jours):
        for i in range(4):
            self.repondre(self.item(f"r{i}"), "REUSSI", il_y_a_jours=il_y_a_jours)

    def test_les_paliers_vont_jusqu_a_35_jours(self):
        from .services import LEITNER_INTERVALS_JOURS

        self.assertEqual(LEITNER_INTERVALS_JOURS, [1, 3, 7, 16, 35])

    def test_un_theme_solide_ancien_repasse_en_file(self):
        from .models import RevisionSchedule
        from .services import PALIER_DE_RAFRAICHISSEMENT, rafraichir_themes_anciens

        self._maitriser(il_y_a_jours=40)

        remis = rafraichir_themes_anciens(self.profil, self.cursus)

        self.assertEqual(remis, [self.derivation.id])
        suivi = RevisionSchedule.objects.get(profil=self.profil, theme=self.derivation)
        self.assertEqual(suivi.palier, PALIER_DE_RAFRAICHISSEMENT)
        self.assertEqual(suivi.due_at, timezone_localdate())

    def test_un_theme_revu_recemment_ou_pas_solide_reste_tranquille(self):
        from .services import rafraichir_themes_anciens

        self._maitriser(il_y_a_jours=5)  # solide mais récent
        for i in range(4):  # ancien mais raté
            self.repondre(self.item(f"l{i}", theme=self.limites), "ECHEC", il_y_a_jours=40)

        self.assertEqual(rafraichir_themes_anciens(self.profil, self.cursus), [])

    def test_pas_plus_de_deux_par_jour_et_pas_deux_fois(self):
        from .services import rafraichir_themes_anciens

        for nom, theme in (("a", self.derivation), ("b", self.limites), ("c", self.optique)):
            for i in range(4):
                self.repondre(self.item(f"{nom}{i}", theme=theme), "REUSSI", il_y_a_jours=40)

        premier = rafraichir_themes_anciens(self.profil, self.cursus)
        second = rafraichir_themes_anciens(self.profil, self.cursus)

        self.assertEqual(len(premier), 2)
        self.assertEqual(len(second), 1)  # les deux premiers sont déjà suivis : seul le troisième manque


def timezone_localdate():
    from django.utils import timezone

    return timezone.localdate()


class MaitriseDesThemesTests(ErreursFixture):
    """R20 : où en est le profil sur chaque thème d'un classement (voir quiz.progression.maitrise_des_themes)."""

    def test_le_niveau_de_chaque_theme_du_classement(self):
        from .progression import maitrise_des_themes

        for i in range(4):
            self.repondre(self.item(f"m{i}"), "REUSSI")
        self.repondre(self.item("l0", theme=self.limites), "ECHEC")

        maitrise = maitrise_des_themes(self.profil, self.cursus, [self.derivation, self.limites])

        self.assertEqual(maitrise[self.derivation.id], {"taux": 100, "nb_reponses": 4, "niveau": "solide"})
        self.assertEqual(maitrise[self.limites.id]["niveau"], "decouvert")

    def test_un_theme_jamais_tente_n_a_pas_d_entree(self):
        from .progression import maitrise_des_themes

        self.assertEqual(maitrise_des_themes(self.profil, self.cursus, [self.derivation]), {})
