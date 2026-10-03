"""Classement hebdomadaire anonyme (voir quiz.classement) : ce qui le rendrait faux ou indiscret."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from catalog.models import Cursus, Examen
from subscriptions.models import Subscription
from users.models import User

from .classement import SEUIL_COHORTE, classement_hebdo
from .models import JourXP


class ClassementTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.autre_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.aujourdhui = timezone.localdate()
        self._n = 0

    def eleve(self, xp, *, cursus=None, jours_avant=0, staff=False):
        self._n += 1
        # Sans mot de passe : une cohorte de trente élèves ne doit pas payer trente hachages.
        user = User.objects.create_user(phone_number=f"6776{self._n:05d}", password=None, is_staff=staff)
        profil = user.profils.first()
        Subscription.objects.create(
            user=user, profil=profil, cursus=cursus or self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )
        if xp:
            JourXP.objects.create(profil=profil, jour=self.aujourdhui - timedelta(days=jours_avant), xp=xp, objectif=20)
        return profil

    def cohorte(self, n=SEUIL_COHORTE, xp=10):
        return [self.eleve(xp + i) for i in range(n)]

    def test_sous_le_seuil_de_cohorte_aucun_classement(self):
        profils = self.cohorte(SEUIL_COHORTE - 1)
        self.assertEqual(classement_hebdo(profils[-1], self.cursus), {"disponible": False, "bande": None})

    def test_le_meilleur_est_dans_le_quart_superieur(self):
        profils = self.cohorte()
        self.assertEqual(classement_hebdo(profils[-1], self.cursus), {"disponible": True, "bande": "quart"})

    def test_le_milieu_haut_est_dans_la_moitie_superieure(self):
        profils = self.cohorte(40)
        # 60 % des autres ont moins : au-dessus de la médiane, pas dans le quart supérieur.
        self.assertEqual(classement_hebdo(profils[24], self.cursus)["bande"], "moitie")

    def test_la_moitie_basse_se_tait(self):
        profils = self.cohorte(40)
        self.assertEqual(classement_hebdo(profils[5], self.cursus), {"disponible": True, "bande": None})

    def test_sans_xp_cette_semaine_aucune_bande(self):
        self.cohorte()
        inactif = self.eleve(0)
        self.assertEqual(classement_hebdo(inactif, self.cursus), {"disponible": True, "bande": None})

    def test_seule_la_semaine_en_cours_compte(self):
        self.cohorte()
        ancien = self.eleve(500, jours_avant=10)
        self.assertEqual(classement_hebdo(ancien, self.cursus)["bande"], None)

    def test_les_autres_cursus_et_le_personnel_ne_comptent_pas(self):
        for _ in range(SEUIL_COHORTE):
            self.eleve(10, cursus=self.autre_cursus)
        for _ in range(SEUIL_COHORTE):
            self.eleve(10, staff=True)
        moi = self.eleve(10)
        self.assertEqual(classement_hebdo(moi, self.cursus)["disponible"], False)

    def test_la_reponse_ne_contient_aucune_donnee_individuelle(self):
        profils = self.cohorte()
        self.assertEqual(set(classement_hebdo(profils[-1], self.cursus)), {"disponible", "bande"})
