"""
Révision espacée après une rechute (voir quiz.services.enregistrer_resultat_pour_revision) : un thème raté revient demain,
mais ne recule que d'un palier, une fois par jour - plus de retour au palier 0 pour une seule erreur (audit 14, M1).
"""
from datetime import timedelta
from unittest import mock

from django.utils import timezone

from .models import RevisionSchedule
from .services import LEITNER_INTERVALS_JOURS, enregistrer_resultat_pour_revision
from .test_erreurs import ErreursFixture


class ReculDUnPalierTests(ErreursFixture):
    def setUp(self):
        super().setUp()
        self.aujourdhui = timezone.localdate()

    def _suivi(self, palier, due_dans=0):
        return RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.maths, theme=self.derivation,
            palier=palier, due_at=self.aujourdhui + timedelta(days=due_dans),
        )

    def _repondre(self, correcte):
        enregistrer_resultat_pour_revision(self.profil, self.cursus, self.maths, self.derivation, correcte)

    def _etat(self):
        suivi = RevisionSchedule.objects.get(profil=self.profil, theme=self.derivation)
        return suivi.palier, suivi.due_at

    def test_une_premiere_erreur_ouvre_le_suivi_au_palier_zero_pour_demain(self):
        self._repondre(False)

        self.assertEqual(self._etat(), (0, self.aujourdhui + timedelta(days=1)))

    def test_une_rechute_revient_demain_mais_ne_recule_que_d_un_palier(self):
        self._suivi(palier=4, due_dans=20)  # arrivé à J+35

        self._repondre(False)

        self.assertEqual(self._etat(), (3, self.aujourdhui + timedelta(days=1)))

    def test_deux_erreurs_le_meme_jour_ne_font_pas_reculer_de_deux_paliers(self):
        self._suivi(palier=4, due_dans=20)

        self._repondre(False)
        self._repondre(False)

        self.assertEqual(self._etat()[0], 3)

    def test_reussi_le_lendemain_le_theme_retrouve_son_palier(self):
        self._suivi(palier=4, due_dans=20)
        self._repondre(False)

        demain = self.aujourdhui + timedelta(days=1)
        with mock.patch("django.utils.timezone.localdate", return_value=demain):
            self._repondre(True)

        self.assertEqual(self._etat(), (4, demain + timedelta(days=LEITNER_INTERVALS_JOURS[4])))

    def test_rate_jour_apres_jour_le_theme_redescend_jusqu_en_bas(self):
        self._suivi(palier=2, due_dans=5)

        for jours in range(4):
            jour = self.aujourdhui + timedelta(days=jours)
            # `updated_at` suit l'horloge réelle : on le recale sur le jour simulé, comme le ferait une vraie journée.
            RevisionSchedule.objects.filter(theme=self.derivation).update(updated_at=timezone.now() - timedelta(days=1))
            with mock.patch("django.utils.timezone.localdate", return_value=jour):
                self._repondre(False)

        self.assertEqual(self._etat()[0], 0)

    def test_une_reussite_juste_apres_l_erreur_ne_rattrape_rien_le_jour_meme(self):
        self._suivi(palier=3, due_dans=10)

        self._repondre(False)
        self._repondre(True)

        self.assertEqual(self._etat(), (2, self.aujourdhui + timedelta(days=1)))
