"""Rejet, à l'ingestion réelle, des questions sans thème (prévention plutôt que détection par le tunnel)."""

from pathlib import Path

from django.test import TestCase

from .ingestion import IngestionError, ingest_exercise
from .models import Exercise, Question


def _payload(themes):
    question = {"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé."}
    if themes is not None:
        question["themes"] = themes
    return {
        "epreuve_source": "bac-maths-2024",
        "numero_exercice": "1",
        "matiere": "Mathématiques",
        "serie": "C",
        "examen": "BAC",
        "questions": [question],
    }


SOURCE = Path("ingest/cm/bac-maths-2024")


class ExigerThemesTests(TestCase):
    def test_question_sans_theme_rejetee_et_rien_persiste(self):
        with self.assertRaises(IngestionError) as ctx:
            ingest_exercise(_payload(None), source_dir=SOURCE, exiger_themes=True)
        self.assertIn("aucun thème", str(ctx.exception))
        self.assertEqual(Exercise.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)

    def test_liste_de_themes_vide_ou_blanche_rejetee(self):
        for themes in ([], ["  "]):
            with self.assertRaises(IngestionError):
                ingest_exercise(_payload(themes), source_dir=SOURCE, exiger_themes=True)

    def test_question_avec_theme_acceptee(self):
        exercise, created = ingest_exercise(_payload(["Dérivation"]), source_dir=SOURCE, exiger_themes=True)
        self.assertTrue(created)
        self.assertEqual(list(exercise.questions.get().themes.values_list("name", flat=True)), ["Dérivation"])

    def test_appel_direct_sans_exigence_reste_permissif(self):
        _, created = ingest_exercise(_payload(None), source_dir=SOURCE)
        self.assertTrue(created)
