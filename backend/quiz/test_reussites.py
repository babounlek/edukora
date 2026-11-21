"""« Mes réussites » (R12, voir quiz.reussites) : des jalons tirés de faits d'étude, et des rangs qui durent."""
from django.utils import timezone

from catalog.models import Lesson, LessonType, Origine, StatutContenu
from simulations.models import SimulationEpreuve

from . import xp
from .models import GainXP, SourceXP
from .reussites import reussites_du_profil
from .test_erreurs import ErreursFixture


class RangsTests(ErreursFixture):
    def test_quinze_rangs_etales_et_les_cinq_premiers_seuils_inchanges(self):
        self.assertEqual(len(xp.NIVEAUX), 15)
        self.assertEqual(xp.NIVEAUX[:5], (0, 60, 200, 500, 1000))
        self.assertEqual(list(xp.NIVEAUX), sorted(set(xp.NIVEAUX)))

    def test_mille_points_ne_sont_plus_le_sommet(self):
        GainXP.objects.create(profil=self.profil, jour=timezone.localdate(), source=SourceXP.SEANCE, points=1000)

        niveau = xp.niveau_du_profil(self.profil)

        self.assertEqual((niveau["rang"], niveau["seuil_suivant"]), (5, 1600))


class JalonsTests(ErreursFixture):
    def _jalon(self, code):
        return next(j for j in reussites_du_profil(self.profil)["jalons"] if j["code"] == code)

    def test_un_profil_neuf_n_a_rien_et_son_prochain_jalon_est_le_premier_quiz(self):
        donnees = reussites_du_profil(self.profil)

        self.assertFalse(any(j["obtenu"] for j in donnees["jalons"]))
        self.assertEqual(donnees["prochain"], "premier_quiz")

    def test_les_bonnes_reponses_comptent_mais_pas_un_rejeu(self):
        self.repondre(self.item("a"), "REUSSI")
        original = self.repondre(self.item("b"), "REUSSI")
        self.repondre(self.item("c"), "REUSSI", rejeu_de=original)

        self.assertTrue(self._jalon("premier_quiz")["obtenu"])
        self.assertEqual(self._jalon("bonnes_100")["valeur"], 2)

    def test_un_examen_blanc_rendu_ouvre_son_jalon_pas_une_copie_inachevee(self):
        lesson = Lesson.objects.create(
            title="Épreuve", subject=self.maths, year=2025, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        SimulationEpreuve.objects.create(profil=self.profil, lesson=lesson)
        self.assertFalse(self._jalon("premier_examen_blanc")["obtenu"])

        SimulationEpreuve.objects.create(profil=self.profil, lesson=lesson, submitted_at=timezone.now())
        self.assertTrue(self._jalon("premier_examen_blanc")["obtenu"])

    def test_dix_themes_solides(self):
        for n in range(10):
            from catalog.models import Tag

            theme = Tag.objects.create(name=f"solide-{n}")
            for i in range(3):
                self.repondre(self.item(f"s{n}-{i}", theme=theme), "REUSSI")

        self.assertTrue(self._jalon("themes_solides_10")["obtenu"])
        self.assertFalse(self._jalon("themes_solides_25")["obtenu"])

    def test_l_api_repond_a_un_profil_connecte(self):
        reponse = self.client.get("/quiz/reussites/")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["niveau"]["rang"], 1)
        self.assertEqual(len(reponse.data["jalons"]), 26)


class JalonsRapprochesTests(ErreursFixture):
    """Les jalons des débuts, le quiz sans faute, les cartes, et le choix du prochain jalon (le plus proche)."""

    def _donnees(self):
        return reussites_du_profil(self.profil)

    def _jalon(self, code):
        return next(j for j in self._donnees()["jalons"] if j["code"] == code)

    def _quiz(self, resultats, **session):
        """Un quiz d'autant de questions que de résultats ; None laisse la question sans réponse (passée)."""
        from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession

        quiz = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, **session)
        for ordre, resultat in enumerate(resultats, start=1):
            question = QuizQuestion.objects.create(
                session=quiz, competence_item=self.item(f"q{quiz.pk}-{ordre}"), ordre=ordre,
            )
            if resultat is not None:
                QuizAnswer.objects.create(quiz_question=question, resultat_declare=resultat)
        return quiz

    def test_dix_bonnes_reponses_ouvrent_le_premier_palier(self):
        self._quiz(["REUSSI"] * 9 + ["ECHEC"])
        self.assertFalse(self._jalon("bonnes_10")["obtenu"])
        self.assertEqual(self._jalon("bonnes_10")["valeur"], 9)

        self._quiz(["REUSSI"])
        self.assertTrue(self._jalon("bonnes_10")["obtenu"])
        self.assertFalse(self._jalon("bonnes_50")["obtenu"])

    def test_un_quiz_sans_faute_demande_toutes_les_questions_justes(self):
        self._quiz(["REUSSI"] * 4 + ["ECHEC"])  # une erreur
        self._quiz(["REUSSI"] * 4 + [None])  # une question passée
        self._quiz(["REUSSI"] * 4 + ["PARTIEL"])  # « en partie » n'est pas juste
        self.assertEqual(self._jalon("sans_faute_1")["valeur"], 0)

        self._quiz(["REUSSI"] * 5)
        self.assertTrue(self._jalon("sans_faute_1")["obtenu"])
        self.assertEqual(self._jalon("sans_faute_5")["valeur"], 1)

    def test_un_quiz_trop_court_un_rejeu_ou_un_quiz_chronometre_ne_comptent_pas_sans_faute(self):
        self._quiz(["REUSSI"] * 4)  # moins de 5 questions
        original = self._quiz(["REUSSI"] * 4 + ["ECHEC"])
        self._quiz(["REUSSI"] * 5, rejeu_de=original)
        self._quiz(["REUSSI"] * 5, chrono_actif=True)

        self.assertEqual(self._jalon("sans_faute_1")["valeur"], 0)

    def test_le_premier_theme_solide_a_son_jalon(self):
        self.assertFalse(self._jalon("themes_solides_1")["obtenu"])
        for i in range(3):
            self.repondre(self.item(f"s{i}"), "REUSSI")

        self.assertTrue(self._jalon("themes_solides_1")["obtenu"])
        self.assertFalse(self._jalon("themes_solides_3")["obtenu"])

    def test_les_cartes_travaillees_comptent_une_fois_chacune(self):
        from catalog.models import Cours

        from . import cartes

        sections = [{"type": "regle", "titre": "Règle", "contenu_markdown": "Texte."}]
        for n in range(10):
            cours = Cours.objects.create(
                external_id=f"carte-{n}", titre=f"Cours {n}", subject=self.maths, sections_raw=sections,
                statut=StatutContenu.VALIDE,
            )
            cartes.noter(self.profil, cours, "regle", n % 2 == 0)
            if n == 0:
                cartes.noter(self.profil, cours, "regle", False)  # la même carte, revue deux fois
        self.assertTrue(self._jalon("cartes_10")["obtenu"])
        self.assertEqual(self._jalon("cartes_50")["valeur"], 10)

    def test_le_prochain_jalon_est_le_plus_proche_pas_le_premier_de_la_liste(self):
        self._quiz(["REUSSI"] * 4 + ["ECHEC"])  # première réponse acquise ; 4 bonnes sur 10

        donnees = self._donnees()

        # 4/10 bonnes réponses bat 0/1 sans-faute, 0/1 thème solide et 0/3 jours de série.
        self.assertEqual(donnees["prochain"], "bonnes_10")
        codes = [j["code"] for j in donnees["jalons"]]
        self.assertLess(codes.index("bonnes_10"), codes.index("bonnes_100"))
        self.assertLess(codes.index("serie_3"), codes.index("serie_7"))


class JalonsErreursCorrigeesTests(ErreursFixture):
    def _jalon(self, code):
        return next(j for j in reussites_du_profil(self.profil)["jalons"] if j["code"] == code)

    def test_une_erreur_corrigee_reste_acquise_meme_apres_une_rechute(self):
        a = self.item("a")
        self.repondre(a, "ECHEC", il_y_a_jours=3)
        self.assertFalse(self._jalon("erreurs_1")["obtenu"])

        self.repondre(a, "REUSSI", il_y_a_jours=2)
        self.assertTrue(self._jalon("erreurs_1")["obtenu"])

        self.repondre(a, "ECHEC", il_y_a_jours=1)  # rechute : la question revient dans la banque, le jalon reste
        self.assertTrue(self._jalon("erreurs_1")["obtenu"])
        self.assertEqual(self._jalon("erreurs_10")["valeur"], 1)

    def test_une_question_reussie_du_premier_coup_n_est_pas_une_erreur_corrigee(self):
        self.repondre(self.item("a"), "REUSSI")

        self.assertEqual(self._jalon("erreurs_1")["valeur"], 0)


class EchelleQuizMiniEpreuveTests(ErreursFixture):
    """Les jalons de l'échelle : une mini terminée, une épreuve inédite entière terminée. Une copie commencée ne compte pas."""

    def _jalon(self, code):
        return next(j for j in reussites_du_profil(self.profil)["jalons"] if j["code"] == code)

    def _epreuve(self, titre, est_mini):
        from inedit.models import Blueprint, EpreuveInedite

        blueprint = Blueprint.objects.create(
            external_id=f"bp-{titre}", subject=self.maths, titre=titre, sections_plan=[], duree_minutes=30, statut=StatutContenu.VALIDE,
        )
        return EpreuveInedite.objects.create(
            blueprint=blueprint, external_id=f"ep-{titre}", subject=self.maths, titre=titre, statut=StatutContenu.VALIDE,
            est_mini=est_mini, published_at=timezone.now(),
        )

    def _rendre(self, epreuve, rendue=True):
        from inedit.models import TentativeInedite

        return TentativeInedite.objects.create(
            profil=self.profil, epreuve=epreuve, submitted_at=timezone.now() if rendue else None,
        )

    def test_une_mini_rendue_ouvre_son_jalon_pas_une_copie_commencee(self):
        mini = self._epreuve("Mini", est_mini=True)
        self._rendre(mini, rendue=False)
        self.assertFalse(self._jalon("premiere_mini")["obtenu"])

        self._rendre(mini)
        self.assertTrue(self._jalon("premiere_mini")["obtenu"])
        self.assertFalse(self._jalon("premiere_inedite")["obtenu"])

    def test_une_mini_ne_compte_pas_comme_epreuve_entiere_et_trois_epreuves_ouvrent_le_dernier_jalon(self):
        self._rendre(self._epreuve("Mini", est_mini=True))
        self.assertFalse(self._jalon("premiere_inedite")["obtenu"])

        for n in range(3):
            self._rendre(self._epreuve(f"Entière {n}", est_mini=False))
        self.assertTrue(self._jalon("premiere_inedite")["obtenu"])
        self.assertTrue(self._jalon("inedites_3")["obtenu"])

    def test_la_meme_epreuve_rendue_deux_fois_ne_compte_qu_une_fois(self):
        entiere = self._epreuve("Entière", est_mini=False)
        self._rendre(entiere)
        self._rendre(entiere)

        self.assertEqual(self._jalon("inedites_3")["valeur"], 1)
