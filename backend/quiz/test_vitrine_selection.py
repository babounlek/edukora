"""Garde-fous sur la sélection des quiz gratuits (quiz.management.commands.definir_quiz_vitrine.SELECTION)."""
from collections import Counter

from django.test import SimpleTestCase

from .management.commands.definir_quiz_vitrine import SELECTION


class SelectionVitrineTests(SimpleTestCase):
    def test_une_seule_entree_par_cursus_et_par_matiere(self):
        # Un seul quiz est joué par (cursus, matière) - voir quiz.gratuits : une 2e entrée serait élaguée
        # sans bruit, et la sélection mentirait sur ce qui est offert.
        doublons = [cle for cle, n in Counter(c[:4] for c in SELECTION).items() if n > 1]
        self.assertEqual(doublons, [])

    def test_physique_est_offerte_en_bac_c_et_d(self):
        # La Physique manquait en série C alors que c'est une matière majeure (test élève F5, 2026-10-19).
        offertes = {(c[2], c[3]) for c in SELECTION if c[1] == "BAC"}
        self.assertIn(("C", "PHYSIQUE"), offertes)
        self.assertIn(("D", "PHYSIQUE"), offertes)
