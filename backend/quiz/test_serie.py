"""Série de jours de travail (voir quiz.serie) : règles de pardon et fonction pure."""

from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from catalog.models import Cursus
from users.models import User

from .models import OrigineSeance, SeanceJournaliere, StatutSeance
from .serie import calculer_serie, serie_de_jours

AUJOURDHUI = date(2026, 9, 26)


def jours(*decalages):
    """Jours travaillés, en nombre de jours AVANT aujourd'hui (0 = aujourd'hui)."""
    return {AUJOURDHUI - timedelta(days=d) for d in decalages}


class CalculerSerieTests(SimpleTestCase):
    def test_aucun_jour_travaille(self):
        self.assertEqual(
            calculer_serie(set(), AUJOURDHUI),
            {"jours": 0, "record": 0, "actif_aujourdhui": False, "repos_pris": False},
        )

    def test_jours_consecutifs_dont_aujourd_hui(self):
        serie = calculer_serie(jours(0, 1, 2, 3), AUJOURDHUI)
        self.assertEqual(serie["jours"], 4)
        self.assertTrue(serie["actif_aujourdhui"])

    def test_aujourd_hui_pas_encore_fait_ne_coupe_pas_la_serie(self):
        serie = calculer_serie(jours(1, 2, 3), AUJOURDHUI)
        self.assertEqual(serie["jours"], 3)
        self.assertFalse(serie["actif_aujourdhui"])

    def test_un_jour_de_repos_est_pardonne_et_ne_compte_pas(self):
        serie = calculer_serie(jours(0, 1, 3, 4), AUJOURDHUI)  # le jour -2 est manqué
        self.assertEqual(serie["jours"], 4)
        self.assertTrue(serie["repos_pris"])

    def test_deux_jours_manques_cassent_la_serie(self):
        serie = calculer_serie(jours(0, 1, 4, 5), AUJOURDHUI)  # -2 et -3 manqués
        self.assertEqual(serie["jours"], 2)

    def test_un_second_repos_dans_les_sept_jours_casse_la_serie(self):
        # manqués : -2 et -5, séparés de 3 jours seulement
        serie = calculer_serie(jours(0, 1, 3, 4, 6, 7), AUJOURDHUI)
        self.assertEqual(serie["jours"], 4)

    def test_deux_repos_espaces_de_sept_jours_ou_plus_sont_permis(self):
        # manqués : -2 et -9 (sept jours d'écart)
        serie = calculer_serie(jours(0, 1, 3, 4, 5, 6, 7, 8, 10), AUJOURDHUI)
        self.assertEqual(serie["jours"], 9)

    def test_hier_repos_et_aujourd_hui_pas_encore_fait_la_serie_reste_vivante(self):
        serie = calculer_serie(jours(2, 3, 4), AUJOURDHUI)  # hier manqué, avant-hier travaillé
        self.assertEqual(serie["jours"], 3)
        self.assertFalse(serie["actif_aujourdhui"])

    def test_deux_jours_sans_seance_la_serie_est_rompue(self):
        serie = calculer_serie(jours(3, 4, 5), AUJOURDHUI)
        self.assertEqual(serie["jours"], 0)
        self.assertEqual(serie["record"], 3)

    def test_le_record_survit_a_une_rupture(self):
        serie = calculer_serie(jours(0, 10, 11, 12, 13, 14), AUJOURDHUI)
        self.assertEqual(serie["jours"], 1)
        self.assertEqual(serie["record"], 5)


class SerieDeJoursTests(TestCase):
    def test_lue_depuis_les_seances_terminees_seulement(self):
        user = User.objects.create_user(phone_number="677300001", password="x")
        profil = user.profils.first()
        cursus = Cursus.objects.first()
        aujourdhui = timezone.localdate()
        for decalage, statut in ((0, StatutSeance.TERMINEE), (1, StatutSeance.TERMINEE), (2, StatutSeance.PROPOSEE)):
            SeanceJournaliere.objects.create(
                profil=profil, cursus=cursus, date=aujourdhui - timedelta(days=decalage),
                origine=OrigineSeance.DIAGNOSTIC, statut=statut,
            )

        serie = serie_de_jours(profil)

        self.assertEqual(serie["jours"], 2)
        self.assertTrue(serie["actif_aujourdhui"])
