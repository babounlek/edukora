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
import random
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

from access.models import LectureProgress
from catalog.ingestion import IngestionError
from catalog.models import (
    Cours, Country, Cursus, Difficulte, Examen, Exercise, Lesson, LessonType, Origine, Question, RappelDeMethode,
    Series, StatutContenu, Subject, Tag, TypeReponse,
)
from programme.models import Module, Savoir
from subscriptions.models import Subscription
from users.models import User

from .ingestion import ingest_competence_item, run_ingestion, select_quiz_batch
from .models import (
    CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare, RevisionSchedule, StatutFichePdf,
)
from .services import (
    LEITNER_INTERVALS_JOURS, PARCOURS_COURS_PAR_SAVOIR_MAX, PARCOURS_FREQUENCE_OCCURRENCES_MIN,
    SEUIL_MINIMUM_THEMES_PARCOURS, SUBJECTS_PARCOURS_PAR_FREQUENCE, TAGS_ALIAS_PARCOURS_FREQUENCE,
    TAGS_BLOCKLIST_PARCOURS_FREQUENCE, _poids_par_theme, construire_parcours, construire_parcours_par_frequence,
    enregistrer_resultat_pour_revision, generer_session, maitrise_par_savoir, maitrise_par_theme, resume_parcours,
    revisions_dues,
)
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


def _make_cours(subject, cursus=None, tags=(), titre="Cours", external_id="cours-x", **kwargs):
    """Fixture Cours minimale - sert uniquement à vérifier que la file de révision
    (quiz.views.list_revisions_dues) sait retrouver les cours déjà publiés pour un
    thème donné."""
    kwargs.setdefault("statut", StatutContenu.VALIDE)
    cours = Cours.objects.create(external_id=external_id, titre=titre, subject=subject, **kwargs)
    if cursus:
        cours.cursus.add(*(cursus if isinstance(cursus, (list, tuple)) else [cursus]))
    if tags:
        cours.tags.add(*tags)
    return cours


def _make_lesson_avec_themes(subject, cursus, title, themes_par_question):
    """Fixture Lesson OFFICIEL/VALIDE avec un Exercise et une Question par groupe de
    tags de `themes_par_question` (une liste de listes de Tag) - sert à peupler le
    corpus qu'interroge construire_parcours_par_frequence (agrégation par ÉPREUVE,
    voir sa docstring)."""
    lesson = Lesson.objects.create(
        title=title, subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        origine=Origine.OFFICIEL,
    )
    lesson.cursus.add(cursus)
    for numero, tags in enumerate(themes_par_question, start=1):
        question = _make_question(lesson, str(numero))
        question.themes.add(*tags)
    return lesson


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


class IngestCompetenceItemSavoirOfficielTests(TestCase):
    """`savoir_officiel` (optionnel) lie le Tag `theme` résolu à son Savoir officiel -
    voir catalog.ingestion._resolve_savoir_officiel/_link_tags_to_savoir, réutilisés
    tels quels par quiz.ingestion.ingest_competence_item."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.tag = Tag.objects.create(name="dérivation")
        maths = Subject.objects.get(country=self.country, code="MATHS")
        module = Module.objects.create(subject=maths, classe="Tle", serie_label="C-E", numero="25", titre="Module test")
        self.savoir = Savoir.objects.create(module=module, numero="III", intitule="Dérivation")

    def test_links_theme_to_savoir(self):
        payload = _item_payload(savoir_officiel={
            "classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III",
        })
        ingest_competence_item(payload, self.country)

        self.tag.refresh_from_db()
        self.assertEqual(self.tag.savoir_officiel_id, self.savoir.pk)

    def test_absent_field_is_a_no_op(self):
        ingest_competence_item(_item_payload(), self.country)

        self.tag.refresh_from_db()
        self.assertIsNone(self.tag.savoir_officiel_id)

    def test_savoir_officiel_allows_inventing_a_brand_new_theme(self):
        # Un savoir tout juste ajouté au référentiel n'a par construction encore aucun
        # Tag - ce pipeline doit pouvoir le créer, mais seulement parce qu'il est ancré
        # à une entrée réelle du programme officiel (voir _resolve_theme, allow_create).
        payload = _item_payload(theme="Notion neuve jamais encore taguée", savoir_officiel={
            "classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III",
        })

        item, created = ingest_competence_item(payload, self.country)

        self.assertTrue(created)
        self.assertEqual(item.theme.name, "Notion neuve jamais encore taguée")
        self.assertEqual(item.theme.savoir_officiel_id, self.savoir.pk)

    def test_without_savoir_officiel_still_rejects_an_unknown_theme(self):
        payload = _item_payload(theme="Notion neuve jamais encore taguée")
        with self.assertRaises(IngestionError):
            ingest_competence_item(payload, self.country)


class SelectQuizBatchSavoirAwareTests(TestCase):
    """select_quiz_batch rend visibles les savoirs officiels sans aucun contenu
    existant - _find_undercovered_competencies seule ne peut jamais les voir (rien à
    grouper) - voir quiz.ingestion._find_undercovered_savoirs_officiels."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        self.subject = Subject.objects.get(country=self.cm, code="MATHS")
        self.cursus_c = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="90", titre="Module test")
        module.cursus.set([self.cursus_c])
        self.savoir = Savoir.objects.create(module=module, numero="I", intitule="Notion jamais couverte")

    def test_zero_coverage_savoir_surfaces_in_batch(self):
        requests = select_quiz_batch(self.cm)

        self.assertEqual(len(requests), 1)
        req = requests[0]
        self.assertIn("Notion jamais couverte", req["competence"])
        self.assertEqual(req["savoir_officiel"], {
            "classe": "Tle", "serie_label": "C", "module_numero": "90", "savoir_numero": "I",
        })
        self.assertEqual(req["materiel_reference"], [])

    def test_tag_already_linked_to_a_surfaced_savoir_is_not_duplicated(self):
        tag = Tag.objects.create(name="notion existante", savoir_officiel=self.savoir)
        lesson = Lesson.objects.create(
            title="x", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus_c)
        q = _make_question(lesson, "1")
        q.themes.add(tag)

        requests = select_quiz_batch(self.cm)

        # Un seul objet pour ce savoir, pas deux (un via le Tag historique, un via le
        # Savoir référentiel) - le signal savoir prime, voir select_quiz_batch.
        self.assertEqual(len(requests), 1)


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

    def _questions_taguees(self, theme, combien=2, prefixe="q"):
        """Crée `combien` Question portant `theme`, chacune dans son propre Exercise.

        Le minimum par défaut est deux : un couple (thème, matière) adossé à un unique
        exercice n'est plus proposé par la sélection (voir
        quiz.ingestion.SELECTION_MIN_QUESTIONS). Ces tests portent sur autre chose - la
        forme de la requête, la limite, le fichier de sortie - donc ils se contentent de
        franchir ce seuil.
        """
        questions = []
        for i in range(combien):
            question = _make_question(self.lesson, f"{prefixe}{i}")
            question.themes.add(theme)
            questions.append(question)
        return questions

    def test_selects_undercovered_competency_with_reference_material(self):
        questions = self._questions_taguees(self.theme)

        requests = self._run()

        self.assertEqual(len(requests), 1)
        req = requests[0]
        self.assertEqual(req["competence"], "dérivation")
        self.assertEqual(req["pays"], "cm")
        self.assertEqual(req["matiere"], self.subject.label)
        self.assertEqual(req["cursus"], [{"examen": "bac", "serie": "C"}])
        self.assertEqual(req["cible"]["nombre_items"], 6)
        exercise_ids = {m["exercise_id"] for m in req["materiel_reference"]}
        self.assertEqual(exercise_ids, {q.exercise_id for q in questions})

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
            self._questions_taguees(theme, prefixe=f"t{i}q")

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
        self._questions_taguees(self.theme)

        requests = self._run()

        series_codes = sorted(c["serie"] for c in requests[0]["cursus"])
        self.assertEqual(series_codes, ["C", "E"])

    # --- Gardes de qualité de la sélection (2026-08-17) ---
    #
    # Deux familles de requêtes revenaient à chaque sélection sans pouvoir être
    # traitées : les tags qui nomment la forme d'une question plutôt qu'une notion, et
    # les couples adossés à un unique exercice, dont le nom du tag ne suffit pas à
    # savoir ce qu'ils recouvrent.

    def test_structural_tags_are_never_proposed(self):
        # « situation-problème » est le nom d'une section d'épreuve du format
        # camerounais par compétences ; « QCM » et « vrai ou faux » nomment un format
        # de réponse ; « schéma » un support que le quiz ne peut pas afficher.
        noms = ("situation-problème", "QCM", "QCM d'inférence", "vrai ou faux", "schéma", "définitions")
        for rang, nom in enumerate(noms):
            self._questions_taguees(Tag.objects.create(name=nom), prefixe=f"s{rang}-")

        self.assertEqual(self._run(), [])

    def test_a_notion_whose_name_starts_like_a_structural_tag_is_kept(self):
        # Le filtrage est une égalité exacte, jamais un préfixe : ces trois intitulés
        # sont de vraies notions qu'un motif large emporterait à tort.
        noms = ("définition de Brönsted", "figures de style", "définition par foyer et directrice")
        for rang, nom in enumerate(noms):
            self._questions_taguees(Tag.objects.create(name=nom), prefixe=f"n{rang}-")

        competences = {r["competence"] for r in self._run()}

        self.assertEqual(
            competences,
            {"définition de Brönsted", "figures de style", "définition par foyer et directrice"},
        )

    def test_competency_backed_by_a_single_exercise_is_not_proposed(self):
        question = _make_question(self.lesson, "unique")
        question.themes.add(self.theme)

        self.assertEqual(self._run(), [])

    def test_min_questions_can_be_lowered_to_restore_the_old_behaviour(self):
        question = _make_question(self.lesson, "unique")
        question.themes.add(self.theme)

        requests = self._run(min_questions=1)

        self.assertEqual([r["competence"] for r in requests], ["dérivation"])

    def test_unknown_pays_raises_command_error(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command("select_quiz_batch", pays="zz", stdout=out)

    def test_output_file_option_writes_json_to_disk(self):
        self._questions_taguees(self.theme)

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
        # Deux exercices, pas un : le bouton admin partage la sélection de
        # select_quiz_batch, donc son seuil minimal (voir SELECTION_MIN_QUESTIONS).
        for i in range(2):
            question = _make_question(self.lesson, f"q{i}")
            question.themes.add(self.theme)

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

    def test_filters_by_savoir_across_several_tags(self):
        # Un Savoir peut porter plusieurs Tags (cas réel documenté dans
        # quiz.services._items_eligibles) : les deux doivent être couverts, pas
        # seulement l'un des deux comme le ferait un filtre par theme= unique.
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="1", titre="M")
        savoir = Savoir.objects.create(module=module, numero="I", intitule="Dérivation")
        theme_a = Tag.objects.create(name="dérivation - approche graphique", savoir_officiel=savoir)
        theme_b = Tag.objects.create(name="dérivation - calcul formel", savoir_officiel=savoir)
        item_a = _make_competence_item(self.subject, self.cursus, theme=theme_a, numero="1")
        item_b = _make_competence_item(self.subject, self.cursus, theme=theme_b, numero="2")
        _make_competence_item(self.subject, self.cursus, numero="3")  # savoir différent

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, savoir=savoir, n=10)

        self.assertEqual(
            {qq.competence_item_id for qq in session.quiz_questions.all()}, {item_a.id, item_b.id},
        )

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


class PoidsParThemeTests(TestCase):
    """quiz.services._poids_par_theme - traduit l'historique QuizAnswer d'un
    utilisateur en poids par thème, base du tirage pondéré du mode PRATIQUE (voir
    GenererSessionPratiqueWeightingTests plus bas pour l'effet bout en bout)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200010", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.theme = Tag.objects.create(name="theme")

    def _repondre(self, cursus, theme, correcte):
        item = _make_competence_item(self.subject, cursus, theme=theme, numero="x")
        session = QuizSession.objects.create(user=self.user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        resultat = ResultatDeclare.REUSSI if correcte else ResultatDeclare.ECHEC
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=resultat)

    def test_no_history_returns_empty_dict(self):
        self.assertEqual(_poids_par_theme(self.user, self.cursus), {})

    def test_all_failures_give_maximum_weight(self):
        self._repondre(self.cursus, self.theme, correcte=False)
        self._repondre(self.cursus, self.theme, correcte=False)

        self.assertAlmostEqual(_poids_par_theme(self.user, self.cursus)[self.theme.id], 1.7)

    def test_all_successes_give_minimum_weight(self):
        self._repondre(self.cursus, self.theme, correcte=True)
        self._repondre(self.cursus, self.theme, correcte=True)

        self.assertAlmostEqual(_poids_par_theme(self.user, self.cursus)[self.theme.id], 0.3)

    def test_mixed_results_give_intermediate_weight(self):
        self._repondre(self.cursus, self.theme, correcte=True)
        self._repondre(self.cursus, self.theme, correcte=False)

        self.assertAlmostEqual(_poids_par_theme(self.user, self.cursus)[self.theme.id], 1.0)

    def test_history_on_a_different_cursus_is_ignored(self):
        # Même thème (partagé entre cursus), mais l'échec a eu lieu en Série D - ne
        # doit jamais repondérer une pratique libre en Série C.
        self._repondre(self.other_cursus, self.theme, correcte=False)

        self.assertEqual(_poids_par_theme(self.user, self.cursus), {})


class GenererSessionPratiqueWeightingTests(TestCase):
    """mode=PRATIQUE pondère désormais la sélection par thème selon le taux d'échec de
    l'utilisateur sur ce cursus (voir quiz.services._poids_par_theme et
    _selection_ponderee_par_theme) - remplace l'ancien tirage uniforme, documenté dans
    le code comme un raccourci temporaire en attendant de vraies données QuizAnswer."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200012", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme_faible = Tag.objects.create(name="theme-faible")
        self.theme_fort = Tag.objects.create(name="theme-fort")

    def _repondre(self, item, correcte):
        session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        resultat = ResultatDeclare.REUSSI if correcte else ResultatDeclare.ECHEC
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=resultat)

    def test_no_history_behaves_like_the_former_uniform_draw(self):
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme_faible, numero="1")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

        self.assertEqual(list(session.quiz_questions.values_list("competence_item_id", flat=True)), [item.id])

    def test_selection_is_biased_toward_the_theme_with_more_failures(self):
        for i in range(20):
            item = _make_competence_item(self.subject, self.cursus, theme=self.theme_faible, numero=f"faible-{i}")
            self._repondre(item, correcte=False)
        for i in range(20):
            item = _make_competence_item(self.subject, self.cursus, theme=self.theme_fort, numero=f"fort-{i}")
            self._repondre(item, correcte=True)

        random.seed(20260807)  # tirage pondéré, probabiliste par nature - déterministe pour ce test
        tirages_faible = 0
        tirages_fort = 0
        for _ in range(100):
            session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)
            theme_ids = list(session.quiz_questions.values_list("competence_item__theme_id", flat=True))
            tirages_faible += theme_ids.count(self.theme_faible.id)
            tirages_fort += theme_ids.count(self.theme_fort.id)

        # 1000 tirages au total (100 sessions x 10). Sans pondération, ~500/500 - avec
        # elle (poids ~1.7 contre ~0.3, ratio ~5,7x), le thème en échec doit nettement
        # dominer sans pour autant faire disparaître l'autre (voir le plancher à 0.3
        # dans _poids_par_theme, jamais 0).
        self.assertGreater(tirages_faible, tirages_fort * 2)
        self.assertGreater(tirages_fort, 0)


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

    def test_reveal_corrige_injects_cours_link_after_rappel_block_when_a_cours_matches(self):
        # Le lien n'est jamais écrit par le skill de génération (qui n'a aucun moyen
        # fiable de connaître un slug de Cours) - recalculé à la lecture, voir
        # quiz.views._competence_item_corrige.
        self.item.corrige_markdown = (
            "### Rappel de méthode\n\nOn dérive terme à terme.\n\n### Corrigé\n\nf'(x) = 2x."
        )
        self.item.save(update_fields=["corrige_markdown"])
        cours = _make_cours(self.subject, cursus=self.cursus, tags=[self.theme], external_id="cours-derivation")
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 200)
        corrige = response.data["corrige_markdown"]
        self.assertIn(f"[COURS_LINK:{cours.slug}]", corrige)
        # Le marqueur suit le bloc "Rappel de méthode", pas juste ajouté n'importe où.
        self.assertLess(corrige.index("[COURS_LINK:"), corrige.index("### Corrigé"))

    def test_answer_question_also_injects_cours_link_when_a_cours_matches(self):
        self.item.corrige_markdown = (
            "### Rappel de méthode\n\nOn dérive terme à terme.\n\n### Corrigé\n\nf'(x) = 2x."
        )
        self.item.save(update_fields=["corrige_markdown"])
        cours = _make_cours(self.subject, cursus=self.cursus, tags=[self.theme], external_id="cours-derivation")
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        self.assertIn(f"[COURS_LINK:{cours.slug}]", response.data["corrige_markdown"])

    def test_reveal_corrige_omits_cours_link_when_no_cours_matches(self):
        # self.item n'a par défaut aucun Cours correspondant (aucun créé dans setUp) -
        # le corrigé doit rester strictement inchangé, jamais de lien inventé/cassé.
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.data["corrige_markdown"], self.item.corrige_markdown)
        self.assertNotIn("COURS_LINK", response.data["corrige_markdown"])

    # --- Cascade de rapprochement quiz -> cours (voir quiz.views._cours_pour_competence) ---
    #
    # Deux vocabulaires de tags coexistent à deux granularités : correction-experte pose
    # des tags de technique sur les cours, le quiz porte des tags de chapitre alignés sur
    # les savoirs officiels et suffixés par série. L'égalité stricte ne reliait que 108
    # items sur 336 alors que les cours existaient - d'où les deux passes de repli.

    def _corrige_via_api(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        response = self.client.get(
            f"/quiz/sessions/{start.data['id']}/questions/{start.data['questions'][0]['id']}/corrige/",
        )
        return response.data["corrige_markdown"]

    def _savoir(self, intitule="Dérivation"):
        module = Module.objects.create(
            subject=self.subject, classe="Tle", serie_label="C", numero="90", titre="Module test",
        )
        return Savoir.objects.create(module=module, numero="I", intitule=intitule)

    def test_cours_found_through_a_shared_savoir_when_tags_differ(self):
        # Le cas réel : le cours est tagué « algorithme d'Euclide », l'item « Arithmétique
        # (Tle C) ». Aucun tag commun, mais les deux pointent le même savoir officiel.
        savoir = self._savoir()
        self.theme.savoir_officiel = savoir
        self.theme.save(update_fields=["savoir_officiel"])
        autre_tag = Tag.objects.create(name="algorithme d'Euclide", savoir_officiel=savoir)
        cours = _make_cours(
            self.subject, cursus=self.cursus, tags=[autre_tag], external_id="cours-par-savoir",
        )

        self.assertIn(f"[COURS_LINK:{cours.slug}]", self._corrige_via_api())

    def test_cours_found_through_the_chapter_label_when_nothing_else_matches(self):
        # Ni tag commun ni savoir : reste le libellé du chapitre, suffixe de série retiré.
        cours = _make_cours(
            self.subject, cursus=self.cursus, external_id="cours-par-libelle",
            titre="Dériver une fonction polynôme", sous_theme="Dérivation et variations",
        )

        self.assertIn(f"[COURS_LINK:{cours.slug}]", self._corrige_via_api())

    def test_short_labels_never_trigger_the_approximate_match(self):
        # « Suites » matcherait des dizaines de cours sans rapport : en dessous du seuil,
        # aucun lien vaut mieux qu'un lien douteux.
        self.item.theme = Tag.objects.create(name="Suites (Tle C)")
        self.item.save(update_fields=["theme"])
        _make_cours(
            self.subject, cursus=self.cursus, external_id="cours-trop-vague",
            titre="Suites numériques", sous_theme="Suites",
        )

        self.assertNotIn("COURS_LINK", self._corrige_via_api())

    def test_exact_tag_wins_over_the_fallbacks(self):
        # L'ordre des passes compte : le cours explicitement rattaché à la compétence
        # prime sur celui que le libellé rapprocherait.
        _make_cours(
            self.subject, cursus=self.cursus, external_id="cours-approximatif",
            titre="Dérivation approchée", sous_theme="Dérivation",
        )
        exact = _make_cours(
            self.subject, cursus=self.cursus, tags=[self.theme], external_id="cours-exact",
        )

        self.assertIn(f"[COURS_LINK:{exact.slug}]", self._corrige_via_api())

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

    def _completed_session_id(self):
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        self.client.post(f"/quiz/sessions/{session_id}/completer/")
        return session_id

    @patch("quiz.views.queue_quiz_fiche_pdf_generation")
    def test_fiche_pdf_works_for_a_session_still_in_progress(self, mock_queue):
        # Le tirage des QuizQuestion est figé à la création (voir QuizQuestion, "jamais
        # modifiée après création") - le contenu des deux PDF ne dépend donc pas de
        # l'avancement de l'élève, voir la docstring de quiz.views.quiz_fiche_pdf.
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")

        response = self.client.post(f"/quiz/sessions/{start.data['id']}/fiche-pdf/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["statut"], StatutFichePdf.EN_COURS)
        mock_queue.assert_called_once_with(start.data["id"])

    @patch("quiz.views.queue_quiz_fiche_pdf_generation")
    def test_fiche_pdf_denied_without_active_subscription(self, mock_queue):
        # Revérifié à chaque appel (pas seulement au moment du quiz) : l'abonnement a pu
        # expirer depuis - voir _has_active_subscription.
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        session_id = self._completed_session_id()
        Subscription.objects.filter(user=self.user, cursus=self.cursus).delete()

        response = self.client.post(f"/quiz/sessions/{session_id}/fiche-pdf/")

        self.assertEqual(response.status_code, 403)
        mock_queue.assert_not_called()

    @patch("quiz.views.queue_quiz_fiche_pdf_generation")
    def test_fiche_pdf_post_queues_generation_once(self, mock_queue):
        # Un deuxième POST pendant que la génération tourne déjà ne doit pas relancer un
        # second processus détaché - voir la docstring de quiz_fiche_pdf.
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        session_id = self._completed_session_id()

        first = self.client.post(f"/quiz/sessions/{session_id}/fiche-pdf/")
        second = self.client.post(f"/quiz/sessions/{session_id}/fiche-pdf/")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(
            first.data, {"statut": StatutFichePdf.EN_COURS, "sujet_pdf_disponible": False, "corrige_pdf_disponible": False},
        )
        self.assertEqual(second.data["statut"], StatutFichePdf.EN_COURS)
        mock_queue.assert_called_once_with(session_id)

    def test_fiche_pdf_get_polls_without_triggering_generation(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        session_id = self._completed_session_id()

        response = self.client.get(f"/quiz/sessions/{session_id}/fiche-pdf/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {"statut": "", "sujet_pdf_disponible": False, "corrige_pdf_disponible": False},
        )
        self.assertEqual(QuizSession.objects.get(pk=session_id).fiche_pdf_statut, "")

    def test_download_sujet_and_corrige_pdf_not_yet_generated(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        session_id = self._completed_session_id()

        self.assertEqual(self.client.get(f"/quiz/sessions/{session_id}/sujet.pdf").status_code, 404)
        self.assertEqual(self.client.get(f"/quiz/sessions/{session_id}/corrige.pdf").status_code, 404)

    def test_fiche_pdf_endpoints_denied_for_another_users_session(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        session_id = self._completed_session_id()

        other_user = User.objects.create_user(phone_number="677200005", password="x")
        self.client.force_authenticate(user=other_user)

        self.assertEqual(self.client.get(f"/quiz/sessions/{session_id}/fiche-pdf/").status_code, 404)
        self.assertEqual(self.client.get(f"/quiz/sessions/{session_id}/sujet.pdf").status_code, 404)
        self.assertEqual(self.client.get(f"/quiz/sessions/{session_id}/corrige.pdf").status_code, 404)


class EnregistrerResultatPourRevisionTests(TestCase):
    """quiz.services.enregistrer_resultat_pour_revision - moteur de la file de révision
    espacée (RevisionSchedule) : un échec (ré)ouvre un thème au palier 0 (J+1), une
    réussite fait avancer un thème déjà suivi, jamais un thème qui n'a jamais posé
    problème - voir la docstring de la fonction pour la justification pédagogique."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200013", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")

    def test_failure_opens_a_schedule_at_the_first_palier(self):
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=False)

        schedule = RevisionSchedule.objects.get(user=self.user, cursus=self.cursus, theme=self.theme)
        self.assertEqual(schedule.palier, 0)
        self.assertEqual(schedule.due_at, timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[0]))

    def test_success_without_an_existing_schedule_creates_nothing(self):
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=True)

        self.assertFalse(RevisionSchedule.objects.filter(user=self.user, theme=self.theme).exists())

    def test_success_advances_an_existing_schedule_to_the_next_palier(self):
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=False)

        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=True)

        schedule = RevisionSchedule.objects.get(user=self.user, cursus=self.cursus, theme=self.theme)
        self.assertEqual(schedule.palier, 1)
        self.assertEqual(schedule.due_at, timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[1]))

    def test_success_at_the_last_palier_graduates_the_theme_out_of_the_queue(self):
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=False)
        for _ in range(len(LEITNER_INTERVALS_JOURS) - 1):
            enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=True)

        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=True)

        self.assertFalse(RevisionSchedule.objects.filter(user=self.user, theme=self.theme).exists())

    def test_a_relapse_resets_an_advanced_schedule_back_to_the_first_palier(self):
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=False)
        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=True)

        enregistrer_resultat_pour_revision(self.user, self.cursus, self.subject, self.theme, correcte=False)

        schedule = RevisionSchedule.objects.get(user=self.user, cursus=self.cursus, theme=self.theme)
        self.assertEqual(schedule.palier, 0)
        self.assertEqual(schedule.due_at, timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[0]))


class RevisionsDuesServiceTests(TestCase):
    """quiz.services.revisions_dues - ne renvoie que les échéances déjà atteintes,
    triées de la plus en retard à la moins en retard (voir RevisionSchedule.Meta.ordering)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200014", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")

    def _make_schedule(self, theme_name, due_at, cursus=None):
        theme = Tag.objects.create(name=theme_name)
        return RevisionSchedule.objects.create(
            user=self.user, cursus=cursus or self.cursus, subject=self.subject, theme=theme, due_at=due_at,
        )

    def test_future_schedules_are_excluded(self):
        self._make_schedule("pas-encore-du", timezone.localdate() + timedelta(days=3))

        self.assertEqual(list(revisions_dues(self.user)), [])

    def test_due_today_and_overdue_are_included_most_overdue_first(self):
        du_aujourdhui = self._make_schedule("aujourdhui", timezone.localdate())
        tres_en_retard = self._make_schedule("tres-en-retard", timezone.localdate() - timedelta(days=5))

        self.assertEqual(list(revisions_dues(self.user)), [tres_en_retard, du_aujourdhui])

    def test_scoped_to_the_requested_user(self):
        other_user = User.objects.create_user(phone_number="677200015", password="x")
        RevisionSchedule.objects.create(
            user=other_user, cursus=self.cursus, subject=self.subject,
            theme=Tag.objects.create(name="pas-le-mien"), due_at=timezone.localdate(),
        )

        self.assertEqual(list(revisions_dues(self.user)), [])


class RevisionsDuesApiTests(TestCase):
    """GET /quiz/revisions/ (quiz.views.list_revisions_dues) et son déclenchement via
    POST .../answer/ (voir quiz.views.answer_question, seul appelant réel de
    enregistrer_resultat_pour_revision côté production)."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.user = User.objects.create_user(phone_number="677200016", password="x")
        self.client = APIClient()
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

    def test_answering_incorrectly_schedules_the_theme_for_tomorrow_not_today(self):
        # J+1 : une notion ratée aujourd'hui ne doit pas encombrer la file "à réviser"
        # du jour même - elle n'y entre qu'à partir de demain (voir revisions_dues,
        # due_at__lte=aujourd'hui).
        _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero="1",
            type_reponse=TypeReponse.QCM, choix=[{"lettre": "a", "texte": "x"}], reponse_correcte="b",
        )
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]

        self.client.post(
            f"/quiz/sessions/{start.data['id']}/questions/{quiz_question_id}/answer/",
            {"reponse_choisie": "a"}, format="json",  # "a" != reponse_correcte ("b") : réponse fausse
        )

        schedule = RevisionSchedule.objects.get(user=self.user, theme=self.theme)
        self.assertEqual(schedule.palier, 0)
        self.assertEqual(schedule.due_at, timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[0]))
        self.assertEqual(self.client.get("/quiz/revisions/").data, [])

    def test_theme_appears_in_the_queue_once_its_due_date_is_reached(self):
        _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero="1",
            type_reponse=TypeReponse.QCM, choix=[{"lettre": "a", "texte": "x"}], reponse_correcte="b",
        )
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]
        self.client.post(
            f"/quiz/sessions/{start.data['id']}/questions/{quiz_question_id}/answer/",
            {"reponse_choisie": "a"}, format="json",
        )
        # Simule le passage du temps : la fenêtre J+1 posée par la réponse ci-dessus
        # est désormais atteinte.
        RevisionSchedule.objects.filter(user=self.user, theme=self.theme).update(
            due_at=timezone.localdate() - timedelta(days=1),
        )

        response = self.client.get("/quiz/revisions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        due = response.data[0]
        self.assertEqual(due["theme"], "dérivation")
        self.assertEqual(due["theme_id"], self.theme.id)
        self.assertEqual(due["subject_label"], self.subject.label)
        self.assertEqual(due["jours_retard"], 1)
        self.assertEqual(due["cours"], [])

    def test_answering_correctly_never_creates_an_entry(self):
        _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero="1",
            type_reponse=TypeReponse.QCM, choix=[{"lettre": "a", "texte": "x"}], reponse_correcte="a",
        )
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]

        self.client.post(
            f"/quiz/sessions/{start.data['id']}/questions/{quiz_question_id}/answer/",
            {"reponse_choisie": "a"}, format="json",
        )

        self.assertFalse(RevisionSchedule.objects.filter(user=self.user, theme=self.theme).exists())

    def test_includes_published_cours_covering_the_same_theme(self):
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=self.theme,
            due_at=timezone.localdate(),
        )
        cours = _make_cours(self.subject, cursus=self.cursus, tags=[self.theme], titre="Dérivées : la méthode")

        response = self.client.get("/quiz/revisions/")

        self.assertEqual(
            response.data[0]["cours"],
            [{
                "id": cours.id, "slug": cours.slug, "titre": cours.titre, "has_access": True,
                "apercu_contenu": {"has_exemple_resolu": False, "exercices_count": 0},
            }],
        )

    def test_excludes_cours_for_a_different_theme(self):
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=self.theme,
            due_at=timezone.localdate(),
        )
        autre_theme = Tag.objects.create(name="autre-notion")
        _make_cours(self.subject, cursus=self.cursus, tags=[autre_theme], titre="Sans rapport")

        response = self.client.get("/quiz/revisions/")

        self.assertEqual(response.data[0]["cours"], [])

    def test_a_cours_common_to_all_series_is_still_included(self):
        # cursus vide sur le Cours = "toutes séries" (voir Cours.cursus, blank=True) -
        # doit rester rattaché à la file de révision d'une série précise malgré tout.
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=self.theme,
            due_at=timezone.localdate(),
        )
        cours = _make_cours(self.subject, cursus=None, tags=[self.theme], titre="Notion commune")

        response = self.client.get("/quiz/revisions/")

        self.assertEqual(
            response.data[0]["cours"],
            [{
                "id": cours.id, "slug": cours.slug, "titre": cours.titre, "has_access": True,
                "apercu_contenu": {"has_exemple_resolu": False, "exercices_count": 0},
            }],
        )

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/quiz/revisions/")

        self.assertIn(response.status_code, (401, 403))


class MaitriseParThemeTests(TestCase):
    """quiz.services.maitrise_par_theme - contrairement à RevisionSchedule (qui
    disparaît une fois un thème gradué, voir enregistrer_resultat_pour_revision), cette
    vue agrège la TOTALITÉ de l'historique de réponses d'un utilisateur : elle doit
    aussi montrer ce qui est déjà maîtrisé, pas seulement les lacunes."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200017", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.theme = Tag.objects.create(name="dérivation")

    def _repondre(self, item, correcte, cursus=None):
        session = QuizSession.objects.create(user=self.user, cursus=cursus or self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        resultat = ResultatDeclare.REUSSI if correcte else ResultatDeclare.ECHEC
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=resultat)

    def test_aggregates_across_several_sessions_and_rounds_the_rate(self):
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        self._repondre(item, correcte=True)
        self._repondre(item, correcte=True)
        self._repondre(item, correcte=False)  # 2/3 -> 67% (arrondi, pas tronqué à 66%)

        maitrise = maitrise_par_theme(self.user)

        self.assertEqual(len(maitrise), 1)
        entry = maitrise[0]
        self.assertEqual(entry["theme"], "dérivation")
        self.assertEqual(entry["subject_label"], self.subject.label)
        self.assertEqual(entry["total"], 3)
        self.assertEqual(entry["reussies"], 2)
        self.assertEqual(entry["taux"], 67)

    def test_theme_currently_in_the_revision_queue_is_flagged(self):
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        self._repondre(item, correcte=False)
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=self.theme,
            due_at=timezone.localdate() + timedelta(days=1),
        )

        entry = maitrise_par_theme(self.user)[0]

        self.assertTrue(entry["en_revision"])

    def test_theme_never_flagged_for_revision_is_not_marked(self):
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        self._repondre(item, correcte=True)

        entry = maitrise_par_theme(self.user)[0]

        self.assertFalse(entry["en_revision"])

    def test_sorted_from_weakest_to_strongest(self):
        theme_fort = Tag.objects.create(name="fort")
        item_faible = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        item_fort = _make_competence_item(self.subject, self.cursus, theme=theme_fort, numero="2")
        self._repondre(item_faible, correcte=False)
        self._repondre(item_fort, correcte=True)

        maitrise = maitrise_par_theme(self.user)

        self.assertEqual([entry["theme"] for entry in maitrise], ["dérivation", "fort"])

    def test_scoped_to_a_cursus_when_provided(self):
        item_ici = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        item_ailleurs = _make_competence_item(self.subject, self.other_cursus, theme=self.theme, numero="2")
        self._repondre(item_ici, correcte=True, cursus=self.cursus)
        self._repondre(item_ailleurs, correcte=False, cursus=self.other_cursus)

        maitrise = maitrise_par_theme(self.user, cursus=self.cursus)

        self.assertEqual(len(maitrise), 1)
        self.assertEqual(maitrise[0]["total"], 1)
        self.assertEqual(maitrise[0]["reussies"], 1)

    def test_scoped_to_the_requesting_user(self):
        other_user = User.objects.create_user(phone_number="677200018", password="x")
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        session = QuizSession.objects.create(user=other_user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=ResultatDeclare.REUSSI)

        self.assertEqual(maitrise_par_theme(self.user), [])

    def test_legacy_catalog_question_answers_are_excluded(self):
        # Historique pré-bascule : plusieurs thèmes possibles par question (M2M), donc
        # aucune agrégation fiable par thème unique - jamais inclus ici (même
        # restriction que _poids_par_theme/enregistrer_resultat_pour_revision).
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus)
        question = _make_question(lesson, "1")
        question.themes.add(self.theme)
        session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, question=question, ordre=1)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=ResultatDeclare.REUSSI)

        self.assertEqual(maitrise_par_theme(self.user), [])


class MaitriseApiTests(TestCase):
    """GET /quiz/maitrise/ (quiz.views.maitrise)."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.user = User.objects.create_user(phone_number="677200019", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")
        session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=ResultatDeclare.REUSSI)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/quiz/maitrise/")

        self.assertIn(response.status_code, (401, 403))

    def test_returns_aggregated_payload(self):
        response = self.client.get("/quiz/maitrise/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["theme"], "dérivation")
        self.assertEqual(response.data[0]["taux"], 100)

    def test_cursus_query_param_filters_the_result(self):
        other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")

        response = self.client.get(f"/quiz/maitrise/?cursus={other_cursus.id}")

        self.assertEqual(response.data, [])


class ConstruireParcoursTests(TestCase):
    """quiz.services.construire_parcours - vue séquencée du programme officiel,
    enrichie de la progression réelle de l'utilisateur savoir par savoir."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200021", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")

        self.module_2 = Module.objects.create(
            subject=self.subject, classe="Tle", serie_label="C", numero="2", titre="Second module", ordre=2,
        )
        self.module_2.cursus.add(self.cursus)
        self.module_1 = Module.objects.create(
            subject=self.subject, classe="Tle", serie_label="C", numero="1", titre="Premier module", ordre=1,
        )
        self.module_1.cursus.add(self.cursus)
        self.savoir_1b = Savoir.objects.create(module=self.module_1, numero="II", intitule="Second savoir", ordre=2)
        self.savoir_1a = Savoir.objects.create(module=self.module_1, numero="I", intitule="Premier savoir", ordre=1)

    def _repondre(self, item, correcte):
        session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)
        resultat = ResultatDeclare.REUSSI if correcte else ResultatDeclare.ECHEC
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=resultat)

    def test_orders_modules_and_savoirs_by_ordre_not_creation(self):
        parcours = construire_parcours(self.user, self.cursus, self.subject)

        self.assertEqual([m["titre"] for m in parcours], ["Premier module", "Second module"])
        self.assertEqual(
            [s["intitule"] for s in parcours[0]["savoirs"]], ["Premier savoir", "Second savoir"],
        )

    def test_savoir_without_any_content_still_appears(self):
        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertEqual(savoir_payload["taux"], None)
        self.assertFalse(savoir_payload["has_quiz"])
        self.assertEqual(savoir_payload["cours"], [])

    def test_taux_reflects_real_answers(self):
        theme = Tag.objects.create(name="premier-savoir-theme", savoir_officiel=self.savoir_1a)
        item = _make_competence_item(self.subject, self.cursus, theme=theme, numero="1")
        self._repondre(item, correcte=True)
        self._repondre(item, correcte=False)

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertEqual(savoir_payload["taux"], 50)
        self.assertTrue(savoir_payload["has_quiz"])

    def test_en_revision_flag_from_revision_schedule(self):
        theme = Tag.objects.create(name="theme-en-echec", savoir_officiel=self.savoir_1a)
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.subject, theme=theme,
            due_at=timezone.localdate() + timedelta(days=1),
        )

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        self.assertTrue(parcours[0]["savoirs"][0]["en_revision"])

    def test_a_lu_le_cours_flag_from_lecture_progress(self):
        theme = Tag.objects.create(name="theme-cours", savoir_officiel=self.savoir_1a)
        cours = _make_cours(self.subject, cursus=self.cursus, tags=[theme], titre="Le cours")
        LectureProgress.objects.create(user=self.user, cours=cours)

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertTrue(savoir_payload["a_lu_le_cours"])
        self.assertEqual(
            savoir_payload["cours"], [{"slug": cours.slug, "titre": cours.titre, "sous_theme": cours.sous_theme}],
        )

    def test_cours_found_through_a_different_tag_sharing_the_savoir(self):
        # Même situation réelle que quiz.views._cours_pour_competence (niveau 2) :
        # le cours est tagué différemment du quiz, les deux partagent le savoir.
        theme_quiz = Tag.objects.create(name="theme-quiz", savoir_officiel=self.savoir_1a)
        theme_cours = Tag.objects.create(name="theme-cours-distinct", savoir_officiel=self.savoir_1a)
        _make_competence_item(self.subject, self.cursus, theme=theme_quiz, numero="1")
        cours = _make_cours(self.subject, cursus=self.cursus, tags=[theme_cours], titre="Cours indirect")

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertEqual(
            savoir_payload["cours"], [{"slug": cours.slug, "titre": cours.titre, "sous_theme": cours.sous_theme}],
        )

    def test_returns_several_distinct_cours_for_the_same_savoir(self):
        # L'assimilation d'un savoir peut demander plus d'une leçon (voir sa
        # docstring) - contrairement à l'ancien comportement qui n'exposait que le
        # premier Cours trouvé, .first() sur un queryset par ailleurs souvent
        # multi-résultats (un Tag est partagé par plusieurs Cours).
        theme = Tag.objects.create(name="theme-plusieurs-cours", savoir_officiel=self.savoir_1a)
        cours_a = _make_cours(
            self.subject, cursus=self.cursus, tags=[theme], titre="Cours A", external_id="cours-a",
        )
        cours_b = _make_cours(
            self.subject, cursus=self.cursus, tags=[theme], titre="Cours B", external_id="cours-b",
        )

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertEqual([c["slug"] for c in savoir_payload["cours"]], [cours_a.slug, cours_b.slug])

    def test_caps_cours_at_parcours_cours_par_savoir_max(self):
        theme = Tag.objects.create(name="theme-beaucoup-de-cours", savoir_officiel=self.savoir_1a)
        for i in range(PARCOURS_COURS_PAR_SAVOIR_MAX + 2):
            _make_cours(
                self.subject, cursus=self.cursus, tags=[theme], titre=f"Cours {i}", external_id=f"cours-cap-{i}",
            )

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        self.assertEqual(len(savoir_payload["cours"]), PARCOURS_COURS_PAR_SAVOIR_MAX)

    def test_deduplicates_cours_sharing_the_same_sous_theme(self):
        # Deux Cours distincts peuvent légitimement partager le même sous_theme (ex.
        # deux exercices différents sur "Nombres complexes - similitudes") - les
        # afficher tous les deux produirait deux boutons visuellement identiques
        # mais menant à des pages différentes, plutôt qu'un choix utile.
        theme = Tag.objects.create(name="theme-sous-themes-partages", savoir_officiel=self.savoir_1a)
        doublon_1 = _make_cours(
            self.subject, cursus=self.cursus, tags=[theme], titre="Doublon 1", external_id="cours-doublon-1",
            sous_theme="Même sous-thème",
        )
        _make_cours(
            self.subject, cursus=self.cursus, tags=[theme], titre="Doublon 2", external_id="cours-doublon-2",
            sous_theme="Même sous-thème",
        )
        autre = _make_cours(
            self.subject, cursus=self.cursus, tags=[theme], titre="Autre", external_id="cours-autre",
            sous_theme="Sous-thème distinct",
        )

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        savoir_payload = parcours[0]["savoirs"][0]
        # Le premier des deux doublons (ordre par id) est gardé, le second exclu -
        # l'espace libéré profite à "autre", pas gaspillé sur un libellé répété.
        self.assertEqual([c["slug"] for c in savoir_payload["cours"]], [doublon_1.slug, autre.slug])


class ConstruireParcoursParFrequenceTests(TestCase):
    """quiz.services.construire_parcours_par_frequence - classement des thèmes réels
    par fréquence d'examen, qui remplace le Module→Savoir pour
    SUBJECTS_PARCOURS_PAR_FREQUENCE (voir
    project_parcours_par_frequence_conception_2026_09_14)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200023", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")

    def test_below_reliability_floor_returns_none(self):
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS - 1):
            tag = Tag.objects.create(name=f"theme-{i}")
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])

        self.assertIsNone(construire_parcours_par_frequence(self.user, self.cursus, self.subject))

    def test_ranks_themes_by_number_of_distinct_lessons(self):
        frequent = Tag.objects.create(name="frequent")
        rare = Tag.objects.create(name="rare")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            themes = [frequent, rare] if i < 2 else [frequent]
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [themes])

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertEqual(themes[0]["intitule"], "frequent")
        self.assertEqual(themes[0]["nb_epreuves"], SEUIL_MINIMUM_THEMES_PARCOURS)
        self.assertEqual(themes[0]["frequence_pct"], 100)
        self.assertEqual(themes[1]["intitule"], "rare")
        self.assertEqual(themes[1]["nb_epreuves"], 2)

    def test_merges_known_alias_variants_into_a_single_theme(self):
        variante, canonique = next(iter(TAGS_ALIAS_PARCOURS_FREQUENCE.items()))
        tag_canonique = Tag.objects.create(name=canonique)
        tag_variante = Tag.objects.create(name=variante)
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            tag = tag_canonique if i % 2 == 0 else tag_variante
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        noms = [t["intitule"] for t in themes]
        self.assertEqual(noms.count(canonique), 1)
        self.assertNotIn(variante, noms)
        self.assertEqual(themes[0]["nb_epreuves"], SEUIL_MINIMUM_THEMES_PARCOURS)

    def test_a_lesson_mobilizing_both_alias_variants_counts_once(self):
        variante, canonique = next(iter(TAGS_ALIAS_PARCOURS_FREQUENCE.items()))
        tag_canonique = Tag.objects.create(name=canonique)
        tag_variante = Tag.objects.create(name=variante)
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag_canonique, tag_variante]])

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        # Union, jamais la somme (voir la docstring) : sinon la fréquence dépasserait
        # nb_sessions_disponibles, un non-sens pour un frequence_pct.
        self.assertEqual(themes[0]["nb_epreuves"], SEUIL_MINIMUM_THEMES_PARCOURS)
        self.assertEqual(themes[0]["frequence_pct"], 100)

    def test_excludes_blocklisted_junk_tags(self):
        junk_name = next(iter(TAGS_BLOCKLIST_PARCOURS_FREQUENCE))
        junk = Tag.objects.create(name=junk_name)
        real = Tag.objects.create(name="notion-reelle")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[junk, real]])

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertNotIn(junk_name, [t["intitule"] for t in themes])

    def test_excludes_themes_below_occurrences_min(self):
        singleton = Tag.objects.create(name="une-seule-fois")
        recurrent = Tag.objects.create(name="recurrent")
        _make_lesson_avec_themes(self.subject, self.cursus, "Lesson 0", [[singleton, recurrent]])
        for i in range(1, SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[recurrent]])
        self.assertEqual(PARCOURS_FREQUENCE_OCCURRENCES_MIN, 2)

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertNotIn("une-seule-fois", [t["intitule"] for t in themes])
        self.assertIn("recurrent", [t["intitule"] for t in themes])

    def test_savoir_label_is_the_dominant_savoir_officiel_among_its_questions(self):
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="1", titre="M")
        savoir_majoritaire = Savoir.objects.create(module=module, numero="I", intitule="Savoir majoritaire")
        savoir_minoritaire = Savoir.objects.create(module=module, numero="II", intitule="Savoir minoritaire")
        tag = Tag.objects.create(name="theme-avec-savoir")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            lesson = _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])
            question = lesson.exercises.get().questions.get()
            question.savoir_officiel = savoir_majoritaire if i < 6 else savoir_minoritaire
            question.save()

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertEqual(themes[0]["savoir_label"], "Savoir majoritaire")

    def test_theme_without_any_savoir_officiel_still_appears_unlabelled(self):
        # Le point même de cette conception (voir sa docstring) : un thème hors
        # référentiel (ex. calorimétrie) reste affiché sans étiquette plutôt que
        # d'être exclu.
        tag = Tag.objects.create(name="theme-hors-referentiel")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertEqual(themes[0]["intitule"], "theme-hors-referentiel")
        self.assertIsNone(themes[0]["savoir_label"])

    def test_theme_to_quiz_is_direct_via_competence_item(self):
        tag = Tag.objects.create(name="theme-avec-quiz")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])
        _make_competence_item(self.subject, self.cursus, theme=tag, numero="1")

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertTrue(themes[0]["has_quiz"])

    def test_theme_to_cours_follows_rappel_de_methode_lineage_not_cours_cursus(self):
        # Cours.cursus est vide en pratique (voir la conception) - le vrai signal est
        # la lignée Cours←RappelDeMethode←Exercise←Lesson.cursus.
        tag = Tag.objects.create(name="theme-avec-cours")
        lesson = None
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            lesson = _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])
        cours = _make_cours(self.subject, tags=[tag], titre="Le cours du thème")
        exercise = lesson.exercises.get()
        RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-theme-avec-cours", competence="x", contenu_markdown="x", cours=cours,
        )

        themes = construire_parcours_par_frequence(self.user, self.cursus, self.subject)

        self.assertEqual(
            themes[0]["cours"], [{"slug": cours.slug, "titre": cours.titre, "sous_theme": cours.sous_theme}],
        )

    def test_other_subjects_are_untouched(self):
        self.assertNotIn("FRANCAIS", SUBJECTS_PARCOURS_PAR_FREQUENCE)


class ConstruireParcoursBranchesToFrequenceForStemSubjectsTests(TestCase):
    """construire_parcours doit basculer en mode fréquence pour
    SUBJECTS_PARCOURS_PAR_FREQUENCE quand le corpus est assez fourni, tout en restant
    consommable par resume_parcours sans changement (voir sa docstring)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200024", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="1", titre="M")
        module.cursus.add(self.cursus)
        Savoir.objects.create(module=module, numero="I", intitule="Un savoir du programme")

    def test_falls_back_to_module_savoir_below_the_reliability_floor(self):
        parcours = construire_parcours(self.user, self.cursus, self.subject)

        self.assertEqual(parcours[0]["titre"], "M")

    def test_switches_to_frequence_mode_once_reliable(self):
        tag = Tag.objects.create(name="theme-frequent")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])

        parcours = construire_parcours(self.user, self.cursus, self.subject)

        self.assertEqual(len(parcours), 1)
        self.assertEqual(parcours[0]["savoirs"][0]["intitule"], "theme-frequent")

    def test_resume_parcours_still_works_in_frequence_mode(self):
        tag = Tag.objects.create(name="theme-frequent")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson {i}", [[tag]])

        resume = resume_parcours(self.user, self.cursus)

        matiere = next(r for r in resume if r["subject_id"] == self.subject.id)
        self.assertEqual(matiere["total"], 1)


class ParcoursApiTests(TestCase):
    """GET /quiz/parcours/ (quiz.views.parcours)."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="1", titre="M")
        module.cursus.add(self.cursus)
        Savoir.objects.create(module=module, numero="I", intitule="Un savoir")
        self.user = User.objects.create_user(phone_number="677200022", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(f"/quiz/parcours/?cursus={self.cursus.id}&subject={self.subject.id}")

        self.assertIn(response.status_code, (401, 403))

    def test_returns_modules_with_their_savoirs(self):
        response = self.client.get(f"/quiz/parcours/?cursus={self.cursus.id}&subject={self.subject.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titre"], "M")
        self.assertEqual(response.data[0]["savoirs"][0]["intitule"], "Un savoir")


class ResumeParcoursTests(TestCase):
    """quiz.services.resume_parcours - tableau de bord toutes matières, un
    histogramme de statuts par savoir réduit depuis construire_parcours."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200023", password="x")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        self.francais = Subject.objects.get(country__code="CM", code="FRANCAIS")

    def _module_savoir(self, subject, numero="1", intitule="Un savoir"):
        module = Module.objects.create(subject=subject, classe="Tle", serie_label="C", numero=numero, titre="M")
        module.cursus.add(self.cursus)
        return Savoir.objects.create(module=module, numero="I", intitule=intitule)

    def test_lists_only_subjects_with_programme_officiel_for_the_cursus(self):
        self._module_savoir(self.maths)
        # self.francais n'a aucun Module pour ce cursus - ne doit pas apparaître.

        resume = resume_parcours(self.user, self.cursus)

        self.assertEqual([r["subject_label"] for r in resume], [self.maths.label])

    def test_subject_without_any_content_is_entirely_sans_contenu(self):
        self._module_savoir(self.maths)

        resume = resume_parcours(self.user, self.cursus)

        entry = resume[0]
        self.assertEqual(entry["total"], 1)
        self.assertEqual(entry["sans_contenu"], 1)
        self.assertEqual(entry["maitrises"], 0)
        self.assertEqual(entry["en_revision"], 0)
        self.assertEqual(entry["a_decouvrir"], 0)

    def test_each_savoir_counts_in_exactly_one_bucket(self):
        savoir_maitrise = self._module_savoir(self.maths, numero="1", intitule="Maitrise")
        savoir_en_revision = self._module_savoir(self.maths, numero="2", intitule="En revision")
        savoir_a_decouvrir = self._module_savoir(self.maths, numero="3", intitule="A decouvrir")
        # savoir_sans_contenu : aucun CompetenceItem ni Cours, laissé tel quel.
        self._module_savoir(self.maths, numero="4", intitule="Sans contenu")

        theme_maitrise = Tag.objects.create(name="theme-maitrise", savoir_officiel=savoir_maitrise)
        item_maitrise = _make_competence_item(self.maths, self.cursus, theme=theme_maitrise, numero="1")
        session = QuizSession.objects.create(user=self.user, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item_maitrise, ordre=1)
        QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare=ResultatDeclare.REUSSI)

        theme_en_revision = Tag.objects.create(name="theme-en-revision", savoir_officiel=savoir_en_revision)
        _make_competence_item(self.maths, self.cursus, theme=theme_en_revision, numero="2")
        RevisionSchedule.objects.create(
            user=self.user, cursus=self.cursus, subject=self.maths, theme=theme_en_revision,
            due_at=timezone.localdate() + timedelta(days=1),
        )

        theme_a_decouvrir = Tag.objects.create(name="theme-a-decouvrir", savoir_officiel=savoir_a_decouvrir)
        _make_competence_item(self.maths, self.cursus, theme=theme_a_decouvrir, numero="3")

        resume = resume_parcours(self.user, self.cursus)

        entry = resume[0]
        self.assertEqual(entry["total"], 4)
        self.assertEqual(entry["maitrises"], 1)
        self.assertEqual(entry["en_revision"], 1)
        self.assertEqual(entry["a_decouvrir"], 1)
        self.assertEqual(entry["sans_contenu"], 1)


class ResumeParcoursApiTests(TestCase):
    """GET /quiz/parcours/resume/ (quiz.views.parcours_resume)."""

    def setUp(self):
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C", numero="1", titre="M")
        module.cursus.add(self.cursus)
        Savoir.objects.create(module=module, numero="I", intitule="Un savoir")
        self.user = User.objects.create_user(phone_number="677200024", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(f"/quiz/parcours/resume/?cursus={self.cursus.id}")

        self.assertIn(response.status_code, (401, 403))

    def test_returns_one_entry_per_subject(self):
        response = self.client.get(f"/quiz/parcours/resume/?cursus={self.cursus.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["subject_label"], self.maths.label)
        self.assertEqual(response.data[0]["total"], 1)


class QuizSubjectsApiTests(TestCase):
    """GET /quiz/subjects/ (quiz.views.list_quiz_subjects) - ne doit proposer que les
    matières ayant déjà une banque de quiz pour le cursus demandé, contrairement à
    catalog.SubjectListView (tout le référentiel du pays, sans lien avec le Quiz)."""

    def setUp(self):
        self.subject_avec_quiz = Subject.objects.get(country__code="CM", code="MATHS")
        self.subject_sans_quiz = Subject.objects.get(country__code="CM", code="PHYSIQUE_CHIMIE")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.user = User.objects.create_user(phone_number="677200020", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        _make_competence_item(self.subject_avec_quiz, self.cursus, numero="1")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(f"/quiz/subjects/?cursus={self.cursus.id}")

        self.assertIn(response.status_code, (401, 403))

    def test_only_returns_subjects_with_an_eligible_item_for_this_cursus(self):
        response = self.client.get(f"/quiz/subjects/?cursus={self.cursus.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([s["id"] for s in response.data], [self.subject_avec_quiz.id])

    def test_scoped_to_the_requested_cursus(self):
        response = self.client.get(f"/quiz/subjects/?cursus={self.other_cursus.id}")

        self.assertEqual(response.data, [])

    def test_draft_items_do_not_make_a_subject_eligible(self):
        subject_brouillon_seulement = Subject.objects.get(country__code="CM", code="FRANCAIS")
        _make_competence_item(subject_brouillon_seulement, self.cursus, numero="2", statut=StatutContenu.BROUILLON)

        response = self.client.get(f"/quiz/subjects/?cursus={self.cursus.id}")

        self.assertEqual([s["id"] for s in response.data], [self.subject_avec_quiz.id])
