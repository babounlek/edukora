"""Conversion des rythmes existants quand l'objectif du jour passe de 10 / 20 / 30 à 30 / 50 / 80 (migration users 0021)."""
from datetime import timedelta
from importlib import import_module

from django.apps import apps
from django.test import TestCase
from django.utils import timezone

from quiz.models import JourXP
from users.models import Profil, User

migration = import_module("users.migrations.0021_objectif_xp_releve")


class ConversionDesRythmesTests(TestCase):
    def _profil(self, numero, objectif):
        profil = User.objects.create_user(phone_number=f"67755000{numero}", password="x").profils.first()
        Profil.objects.filter(pk=profil.pk).update(objectif_xp_quotidien=objectif)
        return profil

    def _objectif(self, profil):
        return Profil.objects.get(pk=profil.pk).objectif_xp_quotidien

    def test_chaque_eleve_garde_son_rythme_avec_sa_nouvelle_valeur(self):
        tranquille, regulier, intense = self._profil(1, 10), self._profil(2, 20), self._profil(3, 30)

        migration.relever(apps, None)

        # 30 est l'ancien « intense » ET le nouveau « tranquille » : l'ordre de conversion ne doit pas les confondre.
        self.assertEqual([self._objectif(p) for p in (tranquille, regulier, intense)], [30, 50, 80])

    def test_le_retour_arriere_rend_les_anciennes_valeurs(self):
        profils = [self._profil(1, 10), self._profil(2, 20), self._profil(3, 30)]

        migration.relever(apps, None)
        migration.rabaisser(apps, None)

        self.assertEqual([self._objectif(p) for p in profils], [10, 20, 30])

    def test_la_journee_en_cours_suit_sauf_si_elle_est_deja_gagnee(self):
        aujourdhui = timezone.localdate()
        en_cours, gagnee = self._profil(1, 20), self._profil(2, 20)
        JourXP.objects.create(profil=en_cours, jour=aujourdhui, xp=10, objectif=20, atteint=False)
        JourXP.objects.create(profil=gagnee, jour=aujourdhui, xp=20, objectif=20, atteint=True)
        hier = JourXP.objects.create(profil=en_cours, jour=aujourdhui - timedelta(days=1), xp=5, objectif=20, atteint=False)

        migration.relever(apps, None)

        self.assertEqual(JourXP.objects.get(profil=en_cours, jour=aujourdhui).objectif, 50)
        self.assertEqual(JourXP.objects.get(profil=gagnee, jour=aujourdhui).objectif, 20)
        self.assertEqual(JourXP.objects.get(pk=hier.pk).objectif, 20)  # un jour passé garde l'objectif d'alors
