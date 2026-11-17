"""
Passes élève du 2026-11-17 : l'ordre dans lequel un élève rencontre les questions (à choix d'abord, les plus simples en
tête) et les points d'une copie d'inédite rendue en conditions réelles.
"""
from datetime import timedelta
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from catalog.models import Difficulte, TypeReponse
from users.models import User

from . import xp
from .models import GainXP, SourceXP
from .services import ordonner_pour_jouer


def _item(type_reponse, difficulte):
    return SimpleNamespace(type_reponse=type_reponse, difficulte_estimee=difficulte)


class OrdonnerPourJouerTests(SimpleTestCase):
    def test_les_questions_a_choix_passent_avant_celles_a_rediger(self):
        ouverte = _item(TypeReponse.OUVERTE, Difficulte.FAIBLE)
        qcm = _item(TypeReponse.QCM, Difficulte.ELEVEE)
        self.assertEqual(ordonner_pour_jouer([ouverte, qcm]), [qcm, ouverte])

    def test_les_plus_simples_d_abord_dans_chaque_groupe(self):
        dur, moyen, facile = (_item(TypeReponse.QCM, d) for d in (Difficulte.ELEVEE, Difficulte.MOYENNE, Difficulte.FAIBLE))
        self.assertEqual(ordonner_pour_jouer([dur, moyen, facile]), [facile, moyen, dur])

    def test_le_tri_est_stable_et_ne_perd_aucune_question(self):
        a, b = _item(TypeReponse.QCM, Difficulte.MOYENNE), _item(TypeReponse.QCM, Difficulte.MOYENNE)
        sans_difficulte = _item(TypeReponse.QCM, "")
        resultat = ordonner_pour_jouer([a, b, sans_difficulte])
        # À rang égal le tirage reste tel quel ; la question sans difficulté compte comme moyenne (ni en tête, ni en queue).
        self.assertEqual([id(i) for i in resultat], [id(a), id(b), id(sans_difficulte)])


class CrediterInediteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900888", password="x")
        self.profil = self.user.profils.first()

    def test_une_copie_rapporte_les_points_d_un_examen_blanc_une_fois(self):
        gain = xp.crediter_inedite(self.profil, 11)
        self.assertEqual(gain.points, xp.XP_SIMULATION)
        self.assertEqual(xp.gain_inedite(self.profil, 11), xp.XP_SIMULATION)
        self.assertIsNone(xp.crediter_inedite(self.profil, 11))

    def test_une_seule_copie_par_jour(self):
        xp.crediter_inedite(self.profil, 11)
        self.assertIsNone(xp.crediter_inedite(self.profil, 12))
        self.assertEqual(xp.gain_inedite(self.profil, 12), 0)

    def test_ne_bloque_pas_un_examen_blanc_sur_annale_du_meme_jour(self):
        xp.crediter_simulation(self.profil, 5)
        self.assertIsNotNone(xp.crediter_inedite(self.profil, 11))
        self.assertEqual(GainXP.objects.filter(profil=self.profil, source=SourceXP.SIMULATION).count(), 2)

    def test_la_veille_ne_compte_pas(self):
        xp.crediter_inedite(self.profil, 11)
        GainXP.objects.filter(profil=self.profil).update(jour=timezone.localdate() - timedelta(days=1))
        self.assertIsNotNone(xp.crediter_inedite(self.profil, 12))
