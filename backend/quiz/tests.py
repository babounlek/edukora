"""
Couvre les deux risques principaux du module : la sélection d'items (voir
quiz.services.generer_session) et la fuite de la bonne réponse avant que l'élève n'ait
répondu (voir quiz.views._question_payload) - un test de niveau ou un quiz dont la
réponse est visible dans l'onglet réseau avant d'être tentée ne vaut rien.

generer_session pioche exclusivement dans CompetenceItem depuis la bascule (voir
quiz.services._items_eligibles) : un item est rédigé dès l'origine pour se suffire
seul, contrairement à une catalog.Question qui reste un extrait fidèle d'une épreuve
réelle, pensé pour être lu dans le récit complet de son Exercise. catalog.Question
n'est donc plus jamais tirée pour une nouvelle session - _make_question et les
fixtures qui en dépendent (QuizQuestionDeletionTests, LegacyQuestionPayloadTests) ne
couvrent plus que la lecture d'un historique de sessions créées avant la bascule.
"""

import json
import tempfile
from datetime import timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.ingestion import IngestionError
from catalog.models import (
    Country, Cursus, Difficulte, Examen, Exercise, Lesson, LessonType, Question, Series, StatutContenu, Subject, Tag,
    TypeReponse,
)
from subscriptions.models import Subscription
from users.models import User

from .ingestion import ingest_competence_item, run_ingestion
from .models import CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare
from .services import generer_session
from .views import _clean_quiz_markdown, _question_payload


def _make_question(lesson, numero, difficulte=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, **kwargs):
    """Fixture catalog.Question - ne sert plus qu'à couvrir la lecture de l'historique
    pré-bascule (QuizQuestion.question), plus jamais peuplé par generer_session."""
    exercise = Exercise.objects.create(lesson=lesson, numero_exercice=numero, statut=StatutContenu.VALIDE)
    question = Question.objects.create(
        exercise=exercise, numero="1", ordre=1,
        enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        difficulte_estimee=difficulte, type_reponse=type_reponse, **kwargs,
    )
    exercise.compile_from_questions()
    return question


def _make_competence_item(
    subject, cursus, theme=None, difficulte=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, numero="1",
    **kwargs,
):
    """Fixture CompetenceItem - source réelle du Mode Quiz depuis la bascule. `statut`
    par défaut à VALIDE (le seul éligible en Quiz, voir _questions_eligibles) mais
    surchageable via kwargs pour tester le verrou de qualité lui-même."""
    theme = theme or Tag.objects.create(name=f"theme-{numero}")
    kwargs.setdefault("statut", StatutContenu.VALIDE)
    item = CompetenceItem.objects.create(
        theme=theme, subject=subject,
        enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        difficulte_estimee=difficulte, type_reponse=type_reponse, **kwargs,
    )
    item.cursus.add(*(cursus if isinstance(cursus, (list, tuple)) else [cursus]))
    return item


def _item_payload(theme="dérivation", **overrides):
    payload = {
        "external_id": "cqc-test-1",
        "theme": theme,
        "matiere": "Mathematiques",
        "cursus": [{"examen": "BAC", "serie": "C"}],
        "enonce_markdown": "Calculer la dérivée de f(x) = x^2.",
        "corrige_markdown": "f'(x) = 2x.",
        "difficulte_estimee": "MOYENNE",
        "type_reponse": "OUVERTE",
        "choix": [],
        "reponse_correcte": "",
        "source_exercises": [],
    }
    payload.update(overrides)
    return payload


class IngestCompetenceItemTests(TestCase):
    """quiz.ingestion.ingest_competence_item - traduit le JSON du skill
    concepteur-quiz-competence vers CompetenceItem, en réutilisant les résolveurs de
    catalog.ingestion (voir la docstring du module)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.tag = Tag.objects.create(name="dérivation")

    def test_creates_item_with_resolved_references_and_valide_statut(self):
        item, created = ingest_competence_item(_item_payload(statut="BROUILLON"), self.country)

        self.assertTrue(created)
        self.assertEqual(item.theme, self.tag)
        self.assertEqual(item.subject, Subject.objects.get(country=self.country, code="MATHS"))
        self.assertEqual(
            list(item.cursus.all()), [Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")],
        )
        # Toujours VALIDE à l'ingestion, même si le JSON tente d'en dire autrement (voir
        # _item_payload(statut="BROUILLON") ci-dessus, ignoré par ingest_competence_item
        # - le champ n'est même pas lu depuis data) : publié et servable en Quiz
        # immédiatement, sans revue humaine préalable - voir la docstring de
        # ingest_competence_item pour la justification.
        self.assertEqual(item.statut, StatutContenu.VALIDE)

    def test_idempotent_via_external_id(self):
        first, first_created = ingest_competence_item(_item_payload(), self.country)
        second, second_created = ingest_competence_item(_item_payload(), self.country)

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(CompetenceItem.objects.count(), 1)

    def test_without_external_id_always_creates(self):
        ingest_competence_item(_item_payload(external_id=""), self.country)
        ingest_competence_item(_item_payload(external_id=""), self.country)

        self.assertEqual(CompetenceItem.objects.count(), 2)

    def test_unknown_theme_raises(self):
        with self.assertRaises(IngestionError):
            ingest_competence_item(_item_payload(theme="notion inexistante"), self.country)

    def test_theme_matched_case_insensitively_as_fallback(self):
        self.tag.delete()
        Tag.objects.create(name="Dérivation")

        item, _ = ingest_competence_item(_item_payload(theme="dérivation"), self.country)

        self.assertEqual(item.theme.name, "Dérivation")

    def test_ambiguous_theme_case_raises(self):
        # ASCII pur (pas d'accent) : le repli insensible à la casse (iexact) doit
        # rester ambigu de façon fiable quel que soit le moteur de base de données -
        # le pliage de casse Unicode de SQLite ne gère pas les caractères accentués
        # (voir "é"/"É") de la même façon que Postgres en production, contrairement à
        # la casse ASCII simple, portable entre les deux.
        self.tag.delete()
        Tag.objects.create(name="Limites")
        Tag.objects.create(name="LIMITES")

        with self.assertRaises(IngestionError):
            ingest_competence_item(_item_payload(theme="limites"), self.country)

    def test_missing_required_field_raises(self):
        payload = _item_payload()
        del payload["corrige_markdown"]
        with self.assertRaises(IngestionError):
            ingest_competence_item(payload, self.country)

    def test_qcm_choix_normalized_via_shared_resolver(self):
        # reponse_correcte donné comme texte complet plutôt que lettre - même repli
        # que catalog.ingestion._normalize_qcm_choix (réutilisé tel quel ici).
        payload = _item_payload(
            type_reponse="QCM",
            choix=[{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}],
            reponse_correcte="2x",
        )
        item, _ = ingest_competence_item(payload, self.country)

        self.assertEqual(item.reponse_correcte, "a")

    def test_source_exercises_best_effort_ignores_unknown_ids(self):
        item, _ = ingest_competence_item(_item_payload(source_exercises=[999999]), self.country)

        self.assertEqual(item.source_exercises.count(), 0)

    def test_multiple_cursus_entries_are_deduplicated(self):
        # "C-E" se scinde en deux séries (voir catalog.ingestion._split_series) - vérifie
        # qu'on obtient bien 2 Cursus distincts, sans doublon si redemandé séparément.
        payload = _item_payload(cursus=[{"examen": "BAC", "serie": "C-E"}, {"examen": "BAC", "serie": "C"}])
        item, _ = ingest_competence_item(payload, self.country)

        series_codes = sorted(c.series.code for c in item.cursus.all())
        self.assertEqual(series_codes, ["C", "E"])


class RunQuizIngestionTests(TestCase):
    """quiz.ingestion.run_ingestion - scan de dossier ingest/_quiz/<code_pays>/...
    (sous-dossier de l'arbre ingest/ déjà monté dans le conteneur, voir
    quiz.ingestion._country_code_from_quiz_ingest_path)."""

    def setUp(self):
        Tag.objects.create(name="dérivation")

    def test_resolves_country_from_ingest_quiz_folder_and_creates_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "_quiz" / "cm" / "derivation"
            source_dir.mkdir(parents=True)
            (source_dir / "batch.json").write_text(
                json.dumps([
                    _item_payload(external_id="cqc-a"),
                    _item_payload(external_id="cqc-b"),
                ]),
                encoding="utf-8",
            )

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["files_found"], 1)
        self.assertEqual(report["created"], 2)
        self.assertEqual(report["errors"], [])
        self.assertEqual(CompetenceItem.objects.count(), 2)

    def test_unknown_country_folder_is_captured_as_error_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest_quiz" / "zz" / "derivation"
            source_dir.mkdir(parents=True)
            (source_dir / "batch.json").write_text(json.dumps([_item_payload()]), encoding="utf-8")

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["created"], 0)
        self.assertEqual(len(report["errors"]), 1)

    def test_rerun_on_same_folder_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "_quiz" / "cm" / "derivation"
            source_dir.mkdir(parents=True)
            (source_dir / "batch.json").write_text(json.dumps([_item_payload(external_id="cqc-a")]), encoding="utf-8")

            first = run_ingestion(Path(tmp))
            second = run_ingestion(Path(tmp))

        self.assertEqual(first["created"], 1)
        self.assertEqual(second["created"], 0)
        self.assertEqual(second["skipped"], 1)

    def test_unexpected_exception_on_one_item_does_not_abort_the_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "_quiz" / "cm" / "derivation"
            source_dir.mkdir(parents=True)
            (source_dir / "batch.json").write_text(
                json.dumps([_item_payload(external_id="cqc-a"), _item_payload(external_id="cqc-b")]),
                encoding="utf-8",
            )

            with patch("quiz.ingestion.ingest_competence_item", side_effect=ValueError("boom")):
                report = run_ingestion(Path(tmp))

        self.assertEqual(report["created"], 0)
        self.assertEqual(len(report["errors"]), 2)
        self.assertIn("boom", report["errors"][0])

    def test_selection_request_file_directly_under_quiz_root_is_skipped(self):
        # select_quiz_batch écrit sa requête de sélection en _quiz/_batch_<pays>.json
        # (pas encore rattachée à un pays au sens ingestible) - ne doit jamais être
        # scanné comme un lot CompetenceItem lors d'un passage sur tout l'arbre _quiz/.
        with tempfile.TemporaryDirectory() as tmp:
            quiz_root = Path(tmp) / "ingest" / "_quiz"
            country_dir = quiz_root / "cm"
            country_dir.mkdir(parents=True)
            (quiz_root / "_batch_cm.json").write_text(
                json.dumps([{"competence": "dérivation", "pays": "cm"}]), encoding="utf-8",
            )
            (country_dir / "batch.json").write_text(
                json.dumps([_item_payload(external_id="cqc-a")]), encoding="utf-8",
            )

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["files_found"], 1)
        self.assertEqual(report["created"], 1)
        self.assertEqual(report["errors"], [])


class SelectQuizBatchTests(TestCase):
    """quiz.management.commands.select_quiz_batch - sélection déterministe des
    compétences sous-couvertes et de leur matériel de référence, en amont du skill
    concepteur-quiz-competence (qui invente le contenu, jamais cette commande - voir
    sa docstring de module)."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        self.subject = Subject.objects.get(country=self.cm, code="MATHS")
        self.cursus_c = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus_c)
        self.theme = Tag.objects.create(name="dérivation")

    def _run(self, **kwargs):
        out = StringIO()
        call_command("select_quiz_batch", pays="cm", stdout=out, **kwargs)
        return json.loads(out.getvalue())

    def test_selects_undercovered_competency_with_reference_material(self):
        q1 = _make_question(self.lesson, "1")
        q1.themes.add(self.theme)

        requests = self._run()

        self.assertEqual(len(requests), 1)
        req = requests[0]
        self.assertEqual(req["competence"], "dérivation")
        self.assertEqual(req["pays"], "cm")
        self.assertEqual(req["matiere"], self.subject.label)
        self.assertEqual(req["cursus"], [{"examen": "bac", "serie": "C"}])
        self.assertEqual(req["cible"]["nombre_items"], 6)
        self.assertEqual(len(req["materiel_reference"]), 1)
        self.assertEqual(req["materiel_reference"][0]["exercise_id"], q1.exercise_id)

    def test_excludes_competency_at_or_above_floor(self):
        q1 = _make_question(self.lesson, "1")
        q1.themes.add(self.theme)
        for i in range(6):
            _make_competence_item(self.subject, self.cursus_c, theme=self.theme, numero=f"cov-{i}")

        requests = self._run()

        self.assertEqual(requests, [])

    def test_respects_limit(self):
        for i in range(3):
            theme = Tag.objects.create(name=f"theme-{i}")
            q = _make_question(self.lesson, f"q{i}")
            q.themes.add(theme)

        requests = self._run(limit=2)

        self.assertEqual(len(requests), 2)

    def test_country_scoping_excludes_other_countries(self):
        bj = Country.objects.create(code="BJ", label="Bénin")
        bj_subject = Subject.objects.create(country=bj, code="MATHS", label="Mathématiques")
        bj_series = Series.objects.create(country=bj, code="C", label="Maths")
        bj_cursus = Cursus.objects.create(country=bj, examen=Examen.BAC, series=bj_series)
        bj_lesson = Lesson.objects.create(
            title="BJ", subject=bj_subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        bj_lesson.cursus.add(bj_cursus)
        bj_question = _make_question(bj_lesson, "1")
        bj_question.themes.add(self.theme)  # même Tag, mais pays différent

        requests = self._run()  # pays=cm

        self.assertEqual(requests, [])

    def test_materiel_reference_capped_at_four_distinct_exercises(self):
        for i in range(6):
            q = _make_question(self.lesson, f"q{i}")
            q.themes.add(self.theme)

        requests = self._run()

        exercise_ids = [m["exercise_id"] for m in requests[0]["materiel_reference"]]
        self.assertEqual(len(exercise_ids), 4)
        self.assertEqual(len(exercise_ids), len(set(exercise_ids)))

    def test_cursus_entries_include_all_series_for_the_competency(self):
        cursus_e = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="E")
        self.lesson.cursus.add(cursus_e)
        q1 = _make_question(self.lesson, "1")
        q1.themes.add(self.theme)

        requests = self._run()

        series_codes = sorted(c["serie"] for c in requests[0]["cursus"])
        self.assertEqual(series_codes, ["C", "E"])

    def test_unknown_pays_raises_command_error(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command("select_quiz_batch", pays="zz", stdout=out)

    def test_output_file_option_writes_json_to_disk(self):
        q1 = _make_question(self.lesson, "1")
        q1.themes.add(self.theme)

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "batch.json"
            out = StringIO()
            call_command("select_quiz_batch", pays="cm", output=str(output_path), stdout=out)
            data = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(len(data), 1)


class CompetenceItemAdminViewsTests(TestCase):
    """quiz.admin.CompetenceItemAdmin.select_batch_view/ingestion_view - pendants
    admin de select_quiz_batch/ingest_quiz_content (voir la discussion "implémenter
    dans l'admin Django") - mêmes fonctions partagées, jamais une réimplémentation."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200099", password="x")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

        self.cm = Country.objects.get(code="CM")
        self.subject = Subject.objects.get(country=self.cm, code="MATHS")
        self.cursus = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.theme = Tag.objects.create(name="dérivation")

    def test_select_batch_view_get_renders_form(self):
        response = self.client.get(reverse("admin:quiz_competenceitem_select_batch"))
        self.assertEqual(response.status_code, 200)

    def test_select_batch_view_post_writes_file_and_shows_requests(self):
        q = _make_question(self.lesson, "1")
        q.themes.add(self.theme)

        with tempfile.TemporaryDirectory() as tmp:
            quiz_dir = Path(tmp) / "_quiz"
            with patch("quiz.admin.QUIZ_INGEST_DIR", quiz_dir):
                response = self.client.post(
                    reverse("admin:quiz_competenceitem_select_batch"),
                    {"pays": "CM", "limit": "5", "floor": "6"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "dérivation")
                self.assertTrue((quiz_dir / "_batch_cm.json").exists())

    def test_select_batch_view_unknown_pays_shows_error_without_crashing(self):
        response = self.client.post(
            reverse("admin:quiz_competenceitem_select_batch"), {"pays": "ZZ"},
        )
        self.assertEqual(response.status_code, 200)
        messages_text = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("inconnu" in m for m in messages_text))

    def test_ingestion_view_get_lists_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            quiz_dir = Path(tmp) / "_quiz"
            (quiz_dir / "cm").mkdir(parents=True)
            (quiz_dir / "cm" / "batch.json").write_text(json.dumps([_item_payload()]), encoding="utf-8")

            with patch("quiz.admin.QUIZ_INGEST_DIR", quiz_dir):
                response = self.client.get(reverse("admin:quiz_competenceitem_ingestion"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cm/batch.json")

    def test_ingestion_view_post_ingests_and_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            quiz_dir = Path(tmp) / "_quiz"
            (quiz_dir / "cm").mkdir(parents=True)
            (quiz_dir / "cm" / "batch.json").write_text(
                json.dumps([_item_payload(external_id="cqc-x")]), encoding="utf-8",
            )

            with patch("quiz.admin.QUIZ_INGEST_DIR", quiz_dir):
                response = self.client.post(reverse("admin:quiz_competenceitem_ingestion"))

        self.assertEqual(response.status_code, 200)
        item = CompetenceItem.objects.get(external_id="cqc-x")
        self.assertEqual(item.statut, StatutContenu.VALIDE)


class GenererSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.other_subject = Subject.objects.get(country__code="CM", code="FRANCAIS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")

    def test_only_items_from_matching_cursus_are_eligible(self):
        _make_competence_item(self.subject, self.cursus, numero="1")
        _make_competence_item(self.subject, self.other_cursus, numero="2")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)

    def test_filters_by_subject(self):
        _make_competence_item(self.subject, self.cursus, numero="1")
        _make_competence_item(self.other_subject, self.cursus, numero="2")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, subject=self.subject, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().competence_item.subject, self.subject)

    def test_filters_by_theme(self):
        theme = Tag.objects.create(name="dérivation")
        matching = _make_competence_item(self.subject, self.cursus, theme=theme, numero="1")
        _make_competence_item(self.subject, self.cursus, numero="2")  # thème différent

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, theme=theme, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().competence_item, matching)

    def test_brouillon_items_are_not_eligible(self):
        # Le verrou de qualité est désormais explicite (statut=VALIDE), pas une
        # heuristique de texte appliquée après coup - voir CompetenceItem.statut.
        _make_competence_item(self.subject, self.cursus, numero="1", statut=StatutContenu.BROUILLON)

        with self.assertRaises(ValueError):
            generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

    def test_raises_when_no_item_eligible(self):
        with self.assertRaises(ValueError):
            generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

    def test_diagnostic_mode_covers_a_range_of_difficulties(self):
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.FAIBLE, numero=f"faible-{i}")
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.MOYENNE, numero=f"moyenne-{i}")
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.ELEVEE, numero=f"elevee-{i}")

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=10)

        difficultes = {qq.competence_item.difficulte_estimee for qq in session.quiz_questions.all()}
        self.assertEqual(session.quiz_questions.count(), 10)
        self.assertEqual(difficultes, {Difficulte.FAIBLE, Difficulte.MOYENNE, Difficulte.ELEVEE})


class QuizQuestionDeletionTests(TestCase):
    """QuizQuestion.question et QuizQuestion.competence_item doivent être CASCADE, pas
    PROTECT : la purge admin (voir catalog.admin.LessonAdmin.purge_view) supprime tout
    le contenu en bloc (Exercise -> Question en cascade) et ne doit jamais être bloquée
    parce qu'un item a été pioché dans un quiz - régression sur ce point précis, côté
    historique (question) comme côté source actuelle (competence_item)."""

    def test_deleting_exercise_cascades_through_quiz_question_without_protected_error(self):
        user = User.objects.create_user(phone_number="677200005", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        question = _make_question(lesson, "1")
        exercise = question.exercise
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, question=question, ordre=1)

        exercise.delete()

        self.assertFalse(QuizQuestion.objects.filter(pk=quiz_question.pk).exists())

    def test_deleting_competence_item_cascades_through_quiz_question_without_protected_error(self):
        user = User.objects.create_user(phone_number="677200007", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        item = _make_competence_item(subject, cursus, numero="1")
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)

        item.delete()

        self.assertFalse(QuizQuestion.objects.filter(pk=quiz_question.pk).exists())


class QuizAnswerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200002", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.qcm = _make_competence_item(
            subject, cursus, numero="1", type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}], reponse_correcte="a",
        )
        self.ouverte = _make_competence_item(subject, cursus, numero="2", type_reponse=TypeReponse.OUVERTE)
        session = QuizSession.objects.create(user=self.user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        self.qcm_qq = QuizQuestion.objects.create(session=session, competence_item=self.qcm, ordre=1)
        self.ouverte_qq = QuizQuestion.objects.create(session=session, competence_item=self.ouverte, ordre=2)

    def test_qcm_correct_choice_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="a")
        self.assertTrue(answer.est_correcte)

    def test_qcm_wrong_choice_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="b")
        self.assertFalse(answer.est_correcte)

    def test_open_question_reussi_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.REUSSI)
        self.assertTrue(answer.est_correcte)

    def test_open_question_echec_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.ECHEC)
        self.assertFalse(answer.est_correcte)


class CleanQuizMarkdownTests(TestCase):
    """Le cadre "épreuve papier" (en-tête Exercice/Problème, consigne de copie,
    barème) n'a jamais sa place dans le payload d'un item de quiz - toujours vrai pour
    un CompetenceItem (jamais rédigé avec ce cadre en premier lieu) et encore appliqué
    par _question_payload à la branche historique (catalog.Question), légitime tel
    quel dans la Lesson d'origine mais pas hors contexte. Cas réels rencontrés en
    production, avant la bascule."""

    def test_strips_heading_baked_into_first_question_enonce(self):
        text = "### Exercice 1 (5 points)\n\nRésoudre dans $\\mathbb R^2$ le système suivant : ..."
        self.assertEqual(
            _clean_quiz_markdown(text),
            "Résoudre dans $\\mathbb R^2$ le système suivant : ...",
        )

    def test_strips_probleme_heading(self):
        text = "### Problème (10 points)\n\nLe problème comporte deux parties indépendantes A et B."
        self.assertEqual(
            _clean_quiz_markdown(text),
            "Le problème comporte deux parties indépendantes A et B.",
        )

    def test_strips_exam_paper_instruction_and_bareme_from_intro(self):
        text = (
            "### Exercice 2 (5 points)\n\n"
            "Pour chacune des questions suivantes, 4 réponses vous sont proposées, mais une seule est juste ; "
            "écrivez-la sur votre feuille sans aucune autre justification. (Barème : 1,25 pt par réponse juste)"
        )
        cleaned = _clean_quiz_markdown(text)
        self.assertNotIn("Exercice", cleaned)
        self.assertNotIn("écrivez", cleaned)
        self.assertNotIn("Barème", cleaned)
        self.assertIn("Pour chacune des questions suivantes", cleaned)

    def test_leaves_text_without_exam_framing_untouched(self):
        text = "Calculer la dérivée de f."
        self.assertEqual(_clean_quiz_markdown(text), text)

    def test_handles_empty_string(self):
        self.assertEqual(_clean_quiz_markdown(""), "")


class LegacyQuestionPayloadTests(TestCase):
    """Couvre la branche historique de _question_payload (QuizQuestion.question) en
    isolation : plus jamais empruntée par generer_session depuis la bascule vers
    CompetenceItem, mais encore lue pour restituer les sessions déjà en base au moment
    de la bascule - une régression ici casserait silencieusement l'historique de quiz
    des élèves plutôt que les nouvelles sessions."""

    def test_legacy_question_payload_still_renders_lesson_link_and_numero(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        question = _make_question(lesson, "1")
        user = User.objects.create_user(phone_number="677200006", password="x")
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, question=question, ordre=1)

        payload = _question_payload(quiz_question)

        self.assertEqual(payload["lesson_id"], lesson.id)
        self.assertEqual(payload["numero"], question.numero)
        self.assertEqual(payload["subject_label"], subject.label)


class QuizApiTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")

        self.user = User.objects.create_user(phone_number="677200003", password="x")
        self.client = APIClient()

    def _subscribe(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )

    def test_start_session_requires_authentication(self):
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_start_session_denied_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_start_session_rejects_cursus_from_an_inactive_country(self):
        # Un pays désactivé doit rester invisible même pour un cursus auquel
        # l'utilisateur serait déjà abonné - voir catalog.models.VisibleQuerySet et
        # le même principe appliqué ici à quiz.views.start_session.
        inactive = Country.objects.create(code="TG", label="Togo", actif=False)
        series = Series.objects.create(country=inactive, code="C", label="Maths")
        inactive_cursus = Cursus.objects.create(country=inactive, examen=Examen.BAC, series=series)
        Subscription.objects.create(
            user=self.user, cursus=inactive_cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": inactive_cursus.id}, format="json")

        self.assertEqual(response.status_code, 404)

    def test_start_session_creates_session_with_questions(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/quiz/sessions/", {"cursus": self.cursus.id, "mode": ModeQuiz.PRATIQUE}, format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_questions"], 1)
        self.assertTrue(QuizSession.objects.filter(user=self.user, cursus=self.cursus).exists())

    def test_question_payload_exposes_theme_and_subject_without_exam_metadata(self):
        # Contrairement à l'ancien payload (source catalog.Question), un CompetenceItem
        # n'a ni lesson_id ni enonce_intro_markdown : il n'appartient à aucun Exercise,
        # donc rien de ce genre ne peut lui manquer une fois servi seul.
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")

        payload = response.data["questions"][0]
        self.assertEqual(payload["theme"], self.theme.name)
        self.assertEqual(payload["subject_label"], self.subject.label)
        self.assertNotIn("lesson_id", payload)
        self.assertNotIn("enonce_intro_markdown", payload)

    def test_session_payload_exposes_cursus_display(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")

        self.assertEqual(response.data["cursus_display"], "BAC - Série C")

    def test_question_payload_never_leaks_answer_before_responding(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]

        detail = self.client.get(f"/quiz/sessions/{start.data['id']}/")

        payload = detail.data["questions"][0]
        self.assertNotIn("corrige_markdown", payload)
        self.assertNotIn("reponse_correcte", payload)
        self.assertNotIn("reponse", payload)
        self.assertEqual(payload["id"], quiz_question_id)

    def test_answering_reveals_corrige_and_computes_est_correcte(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("corrige_markdown", response.data)
        self.assertTrue(response.data["reponse"]["est_correcte"])

        # Une fois répondu, la question révèle aussi le corrigé dans le détail de session.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_returns_content_without_recording_answer(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["corrige_markdown"], self.item.corrige_markdown)
        self.assertFalse(QuizAnswer.objects.filter(quiz_question_id=quiz_question_id).exists())

        # Toujours pas répondu : le détail de session ne fuite pas encore le corrigé.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertNotIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_denied_for_another_users_session(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        other_user = User.objects.create_user(phone_number="677200004", password="x")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 404)

    def test_complete_session_computes_score_by_theme(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]
        self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        response = self.client.post(f"/quiz/sessions/{session_id}/completer/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score"], 1)
        self.assertEqual(response.data["questions_repondues"], 1)
        self.assertEqual(response.data["par_theme"], [{"theme": "dérivation", "total": 1, "reussies": 1}])
        self.assertIsNotNone(QuizSession.objects.get(pk=session_id).completed_at)
