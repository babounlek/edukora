"""Tests de synchro.empreintes (bibliothèque standard seule). `python -I -m unittest` depuis backend/synchro."""
import importlib.util
import os
import unittest

_spec = importlib.util.spec_from_file_location("emp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "empreintes.py"))
emp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emp)


class CanonisationTests(unittest.TestCase):
    def test_ordre_des_cles_indifferent(self):
        self.assertEqual(emp.canoniser({"b": 1, "a": [1, {"y": 1, "x": 2}]}),
                         emp.canoniser({"a": [1, {"x": 2, "y": 1}], "b": 1}))

    def test_statut_exclu_au_premier_niveau_seulement(self):
        a = {"epreuve_source": "x", "statut": "brouillon", "q": {"statut": "garde"}}
        b = {"epreuve_source": "x", "statut": "valide", "q": {"statut": "garde"}}
        self.assertEqual(emp.canoniser(a), emp.canoniser(b))
        c = {"epreuve_source": "x", "q": {"statut": "autre"}}
        self.assertNotEqual(emp.canoniser(a), emp.canoniser(c))

    def test_unicode_nfc_et_fins_de_ligne(self):
        self.assertEqual(emp.canoniser({"t": "é"}), emp.canoniser({"t": "é"}))
        self.assertEqual(emp.canoniser({"t": "a\r\nb"}), emp.canoniser({"t": "a\nb"}))

    def test_les_accents_ne_sont_pas_echappes(self):
        self.assertIn("é", emp.canoniser({"t": "é"}))

    def test_empreinte_depend_du_contenu_et_des_fichiers(self):
        base = emp.empreinte_source({"a": 1}, ["aa", "bb"])
        self.assertEqual(base, emp.empreinte_source({"a": 1}, ["bb", "aa"]))
        self.assertNotEqual(base, emp.empreinte_source({"a": 2}, ["aa", "bb"]))
        self.assertNotEqual(base, emp.empreinte_source({"a": 1}, ["aa", "cc"]))
        self.assertNotEqual(base, emp.empreinte_source({"a": 1}, ["aa"]))

    def test_empreinte_stable_valeur_connue(self):
        # Garde-fou contre un changement involontaire de canonisation (voir VERSION_EMPREINTE).
        self.assertEqual(emp.canoniser({"b": "é", "a": [1, 2]}), '{"a":[1,2],"b":"é"}')
        self.assertEqual(emp.empreinte_source({"a": 1}), emp.sha256_octets(b'{"a":1}'))


class IdentitesTests(unittest.TestCase):
    def test_identifiant_chemin(self):
        self.assertEqual(emp.identifiant_chemin("cm/dos/dos_exercice_1.json"), "cm/dos/dos_exercice_1")
        self.assertEqual(emp.identifiant_chemin("cm\\dos\\f.JSON"), "cm/dos/f")

    def test_chemins_ingerables(self):
        ok = ["cm/dos/f.json", "cm/dos/sous/f.json", "_quiz/cm/f.json"]
        ko = ["_audit/x.json", "_inedit/cm/bp.json", "_gce_staging/d/f.json", "cm/_x/f.json",
              "_quiz/_audit/f.json", "_quiz/cm/_batch.json", "_quiz/f.json", "cm/f.json", "cm/dos/f.png"]
        for c in ok:
            self.assertTrue(emp.est_chemin_ingerable(c), c)
        for c in ko:
            self.assertFalse(emp.est_chemin_ingerable(c), c)

    def test_unite(self):
        self.assertEqual(emp.unite_de("cm/dos/sous/f.json"), "cm/dos")
        self.assertEqual(emp.unite_de("_quiz/cm/f.json"), "_quiz/cm/f.json")

    def test_types(self):
        ex = {"epreuve_source": "s", "numero_exercice": "1", "questions": []}
        self.assertEqual(emp.type_de_contenu("cm/d/f.json", ex), emp.TYPE_EXERCICE)
        self.assertEqual(emp.type_de_contenu("cm/d/f.json", {"cours_id": "c", "sections": []}), emp.TYPE_COURS)
        self.assertEqual(emp.type_de_contenu("_inedit/cm/bp.json", {"type": "blueprint"}), emp.TYPE_INEDITE)
        item = {"external_id": "e", "theme": "t", "enonce_markdown": "q"}
        self.assertEqual(emp.type_de_contenu("_quiz/cm/f.json", [item]), emp.TYPE_QUIZ)
        self.assertEqual(emp.type_de_contenu("cm/d/f.json", {"x": 1}), emp.TYPE_INCONNU)

    def test_elements_quiz_par_external_id_et_non_par_position(self):
        items = [{"external_id": "b"}, {"external_id": "a"}, {"theme": "sans id"}]
        ids = [i for i, _ in emp.elements("_quiz/cm/f.json", items, emp.TYPE_QUIZ)]
        self.assertEqual(ids, ["b", "a", ""])

    def test_cle_naturelle_exercice(self):
        cle = emp.cle_naturelle(emp.TYPE_EXERCICE, "cm/dos/f.json",
                                {"epreuve_source": "s.pdf", "numero_exercice": 1, "matiere": "Maths", "annee": 2019})
        self.assertEqual(cle["pays"], "cm")
        self.assertEqual(cle["numero_exercice"], "1")
        self.assertEqual(cle["variante_sujet"], "")

    def test_fichiers_declares(self):
        el = {"figures": [{"fichier": "a.png"}, {"nom_fichier": "b.png"}, {"id": "x"}, "pas un objet"]}
        self.assertEqual(emp.noms_fichiers_declares(el), ["a.png", "b.png"])
        self.assertEqual(emp.noms_fichiers_declares({}), [])


if __name__ == "__main__":
    unittest.main()
