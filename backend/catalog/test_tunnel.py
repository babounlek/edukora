import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .ingestion import ingest_exercise
from .models import RappelDeMethode, Tag
from .tunnel import (
    ALERTE, BLOQUANT, _VARIANT_INDEX, blocked_lessons, find_tag_variant, gate_structure, gate_tags, parse_since,
    rappel_est_reponse_deguisee, register_tag, tag_key,
)


def _payload(themes, numero="1"):
    return {
        "epreuve_source": "bac-maths-2024", "numero_exercice": numero, "matiere": "Mathématiques",
        "serie": "C", "examen": "BAC",
        "questions": [{"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": themes}],
    }


class RappelReponseDeguiseeTests(SimpleTestCase):
    ENONCE = "**1.** Qu'appelle-t-on capacité d'un accumulateur ?"

    def test_declarative_rappel_answering_the_question_is_flagged(self):
        corrige = "### Rappel de méthode\nLa capacité d'un accumulateur est la quantité d'électricité qu'il fournit.\n\nSuite."
        self.assertTrue(rappel_est_reponse_deguisee(self.ENONCE, corrige))

    def test_method_formula_rappel_passes(self):
        corrige = "### Rappel de méthode\nPour définir une grandeur, on dit ce qu'elle représente.\n\nLa capacité est..."
        self.assertFalse(rappel_est_reponse_deguisee(self.ENONCE, corrige))

    def test_calculation_question_is_never_flagged(self):
        corrige = "### Rappel de méthode\nLa loi d'Ohm relie U et I.\n\nOn calcule."
        self.assertFalse(rappel_est_reponse_deguisee("**2.** Calculer la tension.", corrige))


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
        question = self._ingest(["Dérivation"]).questions.get()
        question.themes.add(Tag.objects.create(name="heritage"))
        findings = gate_tags(timezone.now() - timezone.timedelta(hours=1))
        self.assertTrue(any(f.severity == ALERTE and "quasi-doublon" in f.message for f in findings))


class BlockedLessonsTests(TestCase):
    """Périmètre = l'ensemble des Lesson listées, pas une fenêtre temporelle - voir
    catalog.ingestion._appliquer_gate_publication, qui garde un Lesson en BROUILLON
    tant que blocked_lessons() le désigne."""

    def _ingest(self, themes, numero="1"):
        return ingest_exercise(_payload(themes, numero), source_dir=Path("ingest/cm/bac-maths-2024"))[0]

    def test_clean_lesson_is_not_blocked(self):
        exercise = self._ingest(["Dérivation"])
        self.assertEqual(blocked_lessons([exercise.lesson_id]), {})

    def test_empty_input_returns_empty_without_querying(self):
        self.assertEqual(blocked_lessons([]), {})

    def test_question_without_theme_blocks_its_lesson(self):
        exercise = self._ingest([])
        raisons = blocked_lessons([exercise.lesson_id])
        self.assertIn(exercise.lesson_id, raisons)
        self.assertTrue(any("sans thème" in r for r in raisons[exercise.lesson_id]))

    def test_incoherent_qcm_blocks_its_lesson(self):
        exercise = self._ingest(["Dérivation"])
        question = exercise.questions.get()
        question.type_reponse = "QCM"
        question.choix = [{"lettre": "a", "texte": "1"}, {"lettre": "b", "texte": "2"}]
        question.reponse_correcte = "z"
        question.save()
        raisons = blocked_lessons([exercise.lesson_id])
        self.assertIn(exercise.lesson_id, raisons)
        self.assertTrue(any("QCM incohérent" in r for r in raisons[exercise.lesson_id]))

    def test_rappel_never_shown_blocks_its_lesson(self):
        exercise = self._ingest(["Dérivation"])
        exercise.corrige_markdown = "Corrigé, sans le titre du rappel."
        exercise.save()
        RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-test", competence="Test",
            contenu_markdown="Contenu du rappel.",
        )
        raisons = blocked_lessons([exercise.lesson_id])
        self.assertIn(exercise.lesson_id, raisons)
        self.assertTrue(any("jamais affiché" in r for r in raisons[exercise.lesson_id]))

    def test_a_lesson_outside_the_given_ids_is_never_touched(self):
        exercise = self._ingest([])
        self.assertEqual(blocked_lessons([exercise.lesson_id + 1]), {})

    def test_untouched_faulty_exercise_still_blocks_its_lesson(self):
        # Contrairement à gate_structure(since), le périmètre est le Lesson entier :
        # un exercice fautif mais non retouché par le run en cours doit quand même
        # empêcher la promotion du Lesson auquel il appartient.
        fautif = self._ingest([])
        propre = self._ingest(["Dérivation"], numero="2")
        self.assertEqual(fautif.lesson_id, propre.lesson_id)
        raisons = blocked_lessons([propre.lesson_id])
        self.assertIn(propre.lesson_id, raisons)


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


class TagKeyNonLatinTests(SimpleTestCase):
    def test_phonetic_symbols_are_not_erased(self):
        self.assertNotEqual(tag_key("diphtongue /aɪ/"), tag_key("diphtongue /aʊ/"))
        self.assertEqual(tag_key("Énergie cinétique"), tag_key("energie cinetique"))


class IngestionReusesTagVariantTests(TestCase):
    def setUp(self):
        _VARIANT_INDEX["built_at"] = None

    def test_ingestion_reuses_an_accent_or_plural_variant_instead_of_creating_a_tag(self):
        Tag.objects.create(name="élimination de paramètre")
        ingest_exercise(_payload(["Elimination de parametres"]), source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(Tag.objects.filter(name__icontains="limination").count(), 1)

    def test_ambiguous_variants_are_never_guessed(self):
        Tag.objects.create(name="limite")
        Tag.objects.create(name="Limites")
        _VARIANT_INDEX["built_at"] = None
        self.assertIsNone(find_tag_variant("limites"))

    def test_two_new_variants_created_within_the_same_run_still_collapse_to_one_tag(self):
        # Reproduit le bug corrigé le 2026-09-22 : l'index de find_tag_variant n'était
        # mis à jour qu'au TTL (60s) - un round de quiz qui invente "ADN polymérase" puis
        # "ADN-polymérase" quelques instants plus tard, sans qu'aucun des deux n'existait
        # avant le run, ne se voyait pas lui-même et créait deux Tag quasi-doublons.
        payload = {
            "epreuve_source": "bac-maths-2024", "numero_exercice": "1", "matiere": "Mathématiques",
            "serie": "C", "examen": "BAC",
            "questions": [
                {"numero": "1", "enonce_markdown": "Énoncé 1.", "corrige_markdown": "Corrigé 1.", "themes": ["ADN polymérase"]},
                {"numero": "2", "enonce_markdown": "Énoncé 2.", "corrige_markdown": "Corrigé 2.", "themes": ["ADN-polymérase"]},
            ],
        }
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(Tag.objects.filter(name__icontains="polymérase").count(), 1)

    def test_register_tag_extends_the_live_index_without_a_rebuild(self):
        _VARIANT_INDEX["built_at"] = None
        self.assertIsNone(find_tag_variant("nouveau theme"))  # construit l'index une première fois
        nouveau = Tag.objects.create(name="Nouveau Theme")
        register_tag(nouveau)
        self.assertEqual(find_tag_variant("nouveau theme"), nouveau)


class FusionQuasiDoublonsSavoirsTests(TestCase):
    def _tag_avec_savoir(self, nom, numero_module, intitule):
        from catalog.models import Subject
        from programme.models import Module, Savoir

        subject = Subject.objects.filter(country__code="CM").first()
        module = Module.objects.create(subject=subject, classe="Tle", serie_label="C", numero=numero_module, titre="M")
        savoir = Savoir.objects.create(module=module, intitule=intitule)
        return Tag.objects.create(name=nom, savoir_officiel=savoir)

    def _groupe(self, intitule_a, intitule_b):
        self._tag_avec_savoir("suite numérique", "1", intitule_a)
        self._tag_avec_savoir("Suites numériques", "2", intitule_b)

    def test_conflicting_savoirs_are_left_alone_by_default(self):
        self._groupe("SUITES NUMERIQUES", "Suites numériques")
        call_command("fusionner_tags_quasi_doublons", "--apply", stdout=StringIO())
        self.assertEqual(Tag.objects.filter(name__icontains="suite").count(), 2)

    def test_equivalent_savoirs_are_merged_on_request(self):
        self._groupe("SUITES NUMERIQUES", "Suites numériques")
        call_command("fusionner_tags_quasi_doublons", "--savoirs-equivalents", "--apply", stdout=StringIO())
        self.assertEqual(Tag.objects.filter(name__icontains="suite").count(), 1)

    def test_different_savoirs_stay_separate_even_on_request(self):
        self._groupe("Suites numériques", "Statistiques descriptives")
        call_command("fusionner_tags_quasi_doublons", "--savoirs-equivalents", "--apply", stdout=StringIO())
        self.assertEqual(Tag.objects.filter(name__icontains="suite").count(), 2)
