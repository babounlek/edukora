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
        self.assertEqual(len(reponse.data["jalons"]), 9)
