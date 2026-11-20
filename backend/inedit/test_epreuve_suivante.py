"""Après une mini, le résultat propose l'épreuve entière du même cursus (l'offerte d'abord, jamais déjà commencée)."""
from .models import EpreuveInedite, TentativeInedite
from .test_notation import NotationAPITestCase
from .tests import _make_published_epreuve


class EpreuveSuivanteTests(NotationAPITestCase):
    def _resultat(self):
        return self.client.post(self.url("completer")).data["epreuve_suivante"]

    def _faire_une_mini(self):
        EpreuveInedite.objects.filter(pk=self.epreuve.pk).update(est_mini=True)

    def _autre_epreuve(self, **champs):
        autre = _make_published_epreuve(self.country)
        EpreuveInedite.objects.filter(pk=autre.pk).update(**champs)
        return autre

    def test_apres_une_epreuve_entiere_rien_n_est_propose(self):
        self._autre_epreuve()

        self.assertIsNone(self._resultat())

    def test_apres_une_mini_l_epreuve_entiere_du_cursus_est_proposee(self):
        self._faire_une_mini()
        entiere = self._autre_epreuve()

        suivante = self._resultat()

        self.assertEqual(suivante["id"], entiere.id)
        self.assertEqual(suivante["country"], "cm")

    def test_l_offerte_passe_avant_une_payante_plus_recente(self):
        self._faire_une_mini()
        offerte = self._autre_epreuve(est_gratuite=True)
        self._autre_epreuve()

        self.assertEqual(self._resultat()["id"], offerte.id)

    def test_une_epreuve_deja_commencee_ou_une_autre_mini_ne_sont_pas_proposees(self):
        self._faire_une_mini()
        vue = self._autre_epreuve()
        TentativeInedite.objects.create(profil=self.profil, epreuve=vue)
        self._autre_epreuve(est_mini=True)

        self.assertIsNone(self._resultat())
