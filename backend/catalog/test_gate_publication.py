"""
_appliquer_gate_publication (voir catalog.ingestion) : un Lesson dont le tunnel
signale un point BLOQUANT (catalog.tunnel.blocked_lessons) reste/redevient BROUILLON
au lieu d'être publié directement - voir project-ingestion-prevention-niveau1-2 dans
la mémoire du projet pour le contexte produit.
"""
import json
import tempfile
from pathlib import Path

from django.test import TestCase

from .ingestion import ingest_exercise, run_ingestion
from .models import Lesson, StatutContenu


def _ecrire(tmp, questions, numero_exercice="1", **extra):
    source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
    source_dir.mkdir(parents=True, exist_ok=True)
    fichier = source_dir / f"bac-maths-2024_exercice_{numero_exercice}.json"
    payload = {
        "epreuve_source": "bac-maths-2024.pdf", "numero_exercice": numero_exercice, "matiere": "Mathematiques",
        "serie": "C", "examen": "BAC", "questions": questions, **extra,
    }
    fichier.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return fichier


def _question_qcm_incoherente(numero="1"):
    return {
        "numero": numero, "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": ["Dérivation"],
        "type_reponse": "qcm", "choix": [{"lettre": "a", "texte": "Seule option"}], "reponse_correcte": "a",
    }


def _question_propre(numero="1"):
    return {"numero": numero, "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": ["Dérivation"]}


class GatePublicationTests(TestCase):
    def test_clean_lesson_is_published_immediately(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire(tmp, [_question_propre()])
            report = run_ingestion(Path(tmp) / "ingest")

        self.assertEqual(report["errors"], [])
        self.assertEqual(report["demoted_lessons"], {})
        lesson = Lesson.objects.get(id=report["lesson_ids"][0])
        self.assertEqual(lesson.statut, StatutContenu.VALIDE)

    def test_lesson_with_an_incoherent_qcm_stays_brouillon(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire(tmp, [_question_qcm_incoherente()])
            report = run_ingestion(Path(tmp) / "ingest")

        self.assertEqual(report["errors"], [])
        lesson_id = report["lesson_ids"][0]
        self.assertIn(str(lesson_id), report["demoted_lessons"])
        lesson = Lesson.objects.get(id=lesson_id)
        self.assertEqual(lesson.statut, StatutContenu.BROUILLON)
        self.assertIsNone(lesson.published_at)

    def test_lesson_is_republished_once_the_faulty_exercise_is_fixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = _ecrire(tmp, [_question_qcm_incoherente()])
            report = run_ingestion(Path(tmp) / "ingest")
            lesson_id = report["lesson_ids"][0]
            self.assertEqual(Lesson.objects.get(id=lesson_id).statut, StatutContenu.BROUILLON)

            fichier.write_text(
                json.dumps({
                    "epreuve_source": "bac-maths-2024.pdf", "numero_exercice": "1", "matiere": "Mathematiques",
                    "serie": "C", "examen": "BAC", "questions": [_question_propre()],
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            ingest_exercise(json.loads(fichier.read_text(encoding="utf-8")), source_dir=fichier.parent, force=True, exiger_themes=True)
            report2 = run_ingestion(Path(tmp) / "ingest")

        self.assertEqual(report2["demoted_lessons"], {})
        self.assertEqual(Lesson.objects.get(id=lesson_id).statut, StatutContenu.VALIDE)

    def test_one_faulty_exercise_does_not_block_a_different_lesson(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire(tmp, [_question_qcm_incoherente()], numero_exercice="1")
            (Path(tmp) / "ingest" / "cm" / "bac-maths-2024-autre").mkdir(parents=True)
            (Path(tmp) / "ingest" / "cm" / "bac-maths-2024-autre" / "bac-maths-2024-autre_exercice_1.json").write_text(
                json.dumps({
                    "epreuve_source": "bac-maths-2024-autre.pdf", "numero_exercice": "1", "matiere": "Mathematiques",
                    "serie": "C", "examen": "BAC", "questions": [_question_propre()],
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            report = run_ingestion(Path(tmp) / "ingest")

        self.assertEqual(len(report["demoted_lessons"]), 1)
        lessons = list(Lesson.objects.filter(id__in=report["lesson_ids"]).order_by("epreuve_source"))
        statuts = {lesson.epreuve_source: lesson.statut for lesson in lessons}
        self.assertEqual(statuts["bac-maths-2024-autre.pdf"], StatutContenu.VALIDE)
        self.assertEqual(statuts["bac-maths-2024.pdf"], StatutContenu.BROUILLON)
