from types import SimpleNamespace

from django.test import SimpleTestCase

from catalog.libelles import libelle_cursus, libelle_series


def _cursus(examen, code=None):
    return SimpleNamespace(display_examen=lambda: examen, series=SimpleNamespace(code=code) if code else None)


class LibelleCursusTests(SimpleTestCase):
    def test_plusieurs_series_du_meme_examen_ne_repetent_pas_l_examen(self):
        cursus = [_cursus("BAC", c) for c in ("C", "D", "E", "TI")]
        self.assertEqual(libelle_cursus(cursus), "BAC - Séries C, D, E et TI")

    def test_deux_series_se_joignent_par_et(self):
        self.assertEqual(libelle_cursus([_cursus("BAC", "C"), _cursus("BAC", "E")]), "BAC - Séries C et E")

    def test_libelle_series_accorde_le_mot(self):
        self.assertEqual(libelle_series(["C"]), "Série C")
        self.assertEqual(libelle_series(["C", "D", "E"]), "Séries C, D et E")
        self.assertIsNone(libelle_series([]))

    def test_une_seule_serie_reste_au_singulier(self):
        self.assertEqual(libelle_cursus([_cursus("BAC", "C")]), "BAC - Série C")

    def test_cursus_sans_serie(self):
        self.assertEqual(libelle_cursus([_cursus("BEPC")]), "BEPC")

    def test_plusieurs_examens_sont_separes(self):
        cursus = [_cursus("Probatoire", "C"), _cursus("Probatoire", "D"), _cursus("BAC", "C")]
        self.assertEqual(libelle_cursus(cursus), "Probatoire - Séries C et D · BAC - Série C")

    def test_doublons_ecartes_et_vide(self):
        self.assertEqual(libelle_cursus([_cursus("BAC", "C"), _cursus("BAC", "C")]), "BAC - Série C")
        self.assertEqual(libelle_cursus([]), "")
