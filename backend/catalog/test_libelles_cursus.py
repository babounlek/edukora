from types import SimpleNamespace

from django.test import SimpleTestCase

from catalog.libelles import libelle_cursus, libelle_series, matiere_dans_titre, public_dans_titre


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


class DejaDansLeTitreTests(SimpleTestCase):
    def test_public_dit_par_le_titre(self):
        cursus = [_cursus("BAC", "C"), _cursus("BAC", "E")]
        self.assertTrue(public_dans_titre("Mathématiques BAC C et E 2002", cursus))
        self.assertTrue(public_dans_titre("Anglais BAC C, D, E et TI – Épreuve inédite n°2", [_cursus("BAC", c) for c in ("C", "D", "E", "TI")]))

    def test_public_absent_ou_incomplet_du_titre(self):
        cursus = [_cursus("BAC", "C"), _cursus("BAC", "E")]
        self.assertFalse(public_dans_titre("Mathématiques 2002", cursus))
        self.assertFalse(public_dans_titre("Mathématiques BAC C 2002", cursus))
        self.assertFalse(public_dans_titre("Mathématiques BAC", []))

    def test_cursus_sans_serie(self):
        self.assertTrue(public_dans_titre("Français BEPC – Épreuve inédite n°2", [_cursus("BEPC")]))

    def test_code_de_serie_cherche_comme_mot_entier(self):
        self.assertFalse(public_dans_titre("Physique BAC TI 2020", [_cursus("BAC", "T")]))

    def test_matiere_dans_titre(self):
        self.assertTrue(matiere_dans_titre("Mathématiques BAC C 2002", "Mathématiques"))
        self.assertFalse(matiere_dans_titre("BAC C 2002", "Mathématiques"))
        self.assertFalse(matiere_dans_titre("BAC C 2002", ""))
