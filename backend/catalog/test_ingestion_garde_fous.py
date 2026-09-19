from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .ingestion import IngestionError, ingest_exercise
from .models import Question, Tag

SRC = Path("ingest/cm/bac-test-2026")


def _payload(matiere="Mathématiques", serie="C", themes=None, epreuve="bac-test-2026"):
    return {
        "epreuve_source": epreuve, "numero_exercice": "1", "matiere": matiere, "serie": serie, "examen": "BAC",
        "questions": [{"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": themes or []}],
    }


class SerieTiInformatiqueGeneriqueTests(TestCase):
    def test_generic_informatique_is_refused_in_serie_ti(self):
        with self.assertRaises(IngestionError):
            ingest_exercise(_payload(matiere="Informatique", serie="TI"), source_dir=SRC)

    def test_other_matiere_is_accepted_in_serie_ti(self):
        exercise, created = ingest_exercise(_payload(matiere="Mathématiques", serie="TI"), source_dir=SRC)
        self.assertTrue(created)
        self.assertEqual(exercise.lesson.subject.code, "MATHS")

    def test_generic_informatique_stays_valid_outside_serie_ti(self):
        _, created = ingest_exercise(_payload(matiere="Informatique", serie="C"), source_dir=SRC)
        self.assertTrue(created)


class ForceReingestionKeepsThemesTests(TestCase):
    def test_themes_attributed_after_the_fact_survive_a_force_reingestion(self):
        exercise, _ = ingest_exercise(_payload(themes=[]), source_dir=SRC)
        question = exercise.questions.get()
        question.themes.add(Tag.objects.create(name="dérivation"))

        recreated, _ = ingest_exercise(_payload(themes=[]), source_dir=SRC, force=True)

        self.assertEqual(list(recreated.questions.get().themes.values_list("name", flat=True)), ["dérivation"])

    def test_themes_from_the_source_json_take_precedence(self):
        exercise, _ = ingest_exercise(_payload(themes=[]), source_dir=SRC)
        exercise.questions.get().themes.add(Tag.objects.create(name="ancien"))

        recreated, _ = ingest_exercise(_payload(themes=["nouveau"]), source_dir=SRC, force=True)

        self.assertEqual(list(recreated.questions.get().themes.values_list("name", flat=True)), ["nouveau"])


class AppliquerThemesTouchesUpdatedAtTests(TestCase):
    def test_applying_themes_bumps_updated_at_so_the_tunnel_sees_the_question(self):
        import json
        import tempfile

        exercise, _ = ingest_exercise(_payload(themes=[]), source_dir=SRC)
        question = exercise.questions.get()
        Question.objects.filter(pk=question.pk).update(updated_at=timezone.now() - timezone.timedelta(days=3))
        avant = Question.objects.get(pk=question.pk).updated_at

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.json"
            path.write_text(json.dumps({str(question.pk): ["un thème"]}), encoding="utf-8")
            call_command("appliquer_themes_questions", str(path), stdout=StringIO())

        self.assertGreater(Question.objects.get(pk=question.pk).updated_at, avant)


class FusionTousSavoirsTests(TestCase):
    def _tag(self, nom, numero_module, intitule):
        from catalog.models import Subject
        from programme.models import Module, Savoir

        subject = Subject.objects.filter(country__code="CM").first()
        module = Module.objects.create(subject=subject, classe="Tle", serie_label="C", numero=numero_module, titre="M")
        return Tag.objects.create(name=nom, savoir_officiel=Savoir.objects.create(module=module, intitule=intitule))

    def test_distinct_savoirs_are_merged_on_request_but_homonyms_can_be_excluded(self):
        self._tag("limite", "1", "LIMITES")
        self._tag("Limites", "2", "SUITES")
        self._tag("registre", "3", "STYLISTIQUE")
        self._tag("registres", "4", "PROCESSEUR")

        call_command("fusionner_tags_quasi_doublons", "--tous-savoirs", "--exclure", "registre", "--apply", stdout=StringIO())

        self.assertEqual(Tag.objects.filter(name__icontains="limite").count(), 1)
        self.assertEqual(Tag.objects.filter(name__icontains="registre").count(), 2)
