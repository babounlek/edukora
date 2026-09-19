import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .ingestion import ingest_exercise
from .models import Tag
from .tunnel import ALERTE, BLOQUANT, gate_structure, gate_tags, parse_since, tag_key


def _payload(themes, numero="1"):
    return {
        "epreuve_source": "bac-maths-2024", "numero_exercice": numero, "matiere": "Mathématiques",
        "serie": "C", "examen": "BAC",
        "questions": [{"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": themes}],
    }


class ParseSinceTests(SimpleTestCase):
    def test_relative_and_iso_forms(self):
        self.assertLess(parse_since("2h"), timezone.now())
        self.assertLess(parse_since("90m"), parse_since("30m"))
        self.assertEqual(parse_since("2026-09-18T10:00").year, 2026)

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            parse_since("hier")


class TagKeyTests(SimpleTestCase):
    def test_accents_case_plural_and_hyphen_are_neutralised(self):
        self.assertEqual(tag_key("Héritage"), tag_key("heritage"))
        self.assertEqual(tag_key("Équations paramétrées"), tag_key("équation paramétrée"))
        self.assertEqual(tag_key("écart-type"), tag_key("écart type"))

    def test_code_tokens_never_collapse_onto_plain_words(self):
        self.assertNotEqual(tag_key("$_GET"), tag_key("get"))
        self.assertNotEqual(tag_key("gets()"), tag_key("gets"))


class TunnelGatesTests(TestCase):
    def _ingest(self, themes):
        return ingest_exercise(_payload(themes), source_dir=Path("ingest/cm/bac-maths-2024"))[0]

    def test_question_without_theme_is_blocking(self):
        self._ingest([])
        findings = gate_structure(timezone.now() - timezone.timedelta(hours=1))
        self.assertTrue(any(f.severity == BLOQUANT and "sans aucun thème" in f.message for f in findings))

    def test_question_with_theme_passes_structure_gate(self):
        self._ingest(["Dérivation"])
        findings = gate_structure(timezone.now() - timezone.timedelta(hours=1))
        self.assertFalse([f for f in findings if f.severity == BLOQUANT])

    def test_incoherent_qcm_is_blocking(self):
        exercise = self._ingest(["Dérivation"])
        question = exercise.questions.get()
        question.type_reponse = "QCM"
        question.choix = [{"lettre": "a", "texte": "1"}, {"lettre": "b", "texte": "2"}]
        question.reponse_correcte = "z"
        question.save()
        findings = gate_structure(timezone.now() - timezone.timedelta(hours=1))
        self.assertTrue(any(f.severity == BLOQUANT and "QCM incohérent" in f.message for f in findings))

    def test_accent_variant_of_an_existing_tag_is_flagged(self):
        Tag.objects.create(name="Héritage")
        self._ingest(["heritage"])
        findings = gate_tags(timezone.now() - timezone.timedelta(hours=1))
        self.assertTrue(any(f.severity == ALERTE and "quasi-doublon" in f.message for f in findings))


class ValiderIngestionCommandTests(TestCase):
    def _run(self, since="1h", **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            dump = str(Path(tmp) / "dump.json")
            out = StringIO()
            call_command("valider_ingestion", since=since, dump=dump, stdout=out, **kwargs)
            return out.getvalue(), json.loads(Path(dump).read_text(encoding="utf-8"))

    def test_clean_round_passes_and_writes_scoped_dump(self):
        ingest_exercise(_payload(["Dérivation"]), source_dir=Path("ingest/cm/bac-maths-2024"))
        out, records = self._run()
        self.assertIn("Portes base OK", out)
        self.assertTrue(any(r["model"] == "Question" for r in records))

    def test_blocking_finding_fails_the_command(self):
        ingest_exercise(_payload([]), source_dir=Path("ingest/cm/bac-maths-2024"))
        with self.assertRaises(CommandError):
            self._run()

    def test_empty_scope_fails_instead_of_passing_silently(self):
        with self.assertRaises(CommandError):
            self._run()


class AppliquerThemesQuestionsTests(TestCase):
    def _question(self):
        exercise = ingest_exercise(_payload([]), source_dir=Path("ingest/cm/bac-maths-2024"))[0]
        return exercise.questions.get()

    def _apply(self, mapping, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "themes.json"
            path.write_text(json.dumps(mapping), encoding="utf-8")
            call_command("appliquer_themes_questions", str(path), stdout=StringIO(), **kwargs)

    def test_adds_themes_and_reuses_the_existing_tag_form(self):
        Tag.objects.create(name="équation paramétrée")
        question = self._question()
        self._apply({str(question.pk): ["Équations paramétrées", "matrice inverse"]})
        self.assertEqual(sorted(question.themes.values_list("name", flat=True)), ["matrice inverse", "équation paramétrée"])
        self.assertEqual(Tag.objects.filter(name__icontains="paramétr").count(), 1)

    def test_never_touches_a_question_that_already_has_themes(self):
        question = self._question()
        question.themes.add(Tag.objects.create(name="existant"))
        self._apply({str(question.pk): ["autre"]})
        self.assertEqual(list(question.themes.values_list("name", flat=True)), ["existant"])

    def test_dry_run_writes_nothing(self):
        question = self._question()
        self._apply({str(question.pk): ["thème"]}, dry_run=True)
        self.assertFalse(question.themes.exists())
