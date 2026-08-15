import json
import tempfile
from io import BytesIO, StringIO
from pathlib import Path

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from unittest.mock import patch

from rest_framework.test import APIClient

from access.models import LectureProgress
from inedit.models import Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite, RappelDeMethodeInedite, TentativeInedite
from users.models import User

from .admin import ExerciseAdmin
from .ingestion import (
    IngestionError, _compress_figure_image, _country_code_from_path, ingest_cours, ingest_exercise,
    queue_ingestion, read_ingestion_report, run_ingestion, write_ingestion_report,
)
from .ingestion_repairs import _dedupe_question_enonce
from .management.commands.seed_country import SUBJECTS as SEED_SUBJECTS
from .models import Cours, Country, Cursus, Difficulte, Examen, ExamenLabel, Exercise, Figure, Lesson, LessonType, NatureEpreuve, Origine, Question, RappelDeMethode, Series, StatutContenu, Subject, Tag, Temoignage, TypeReponse, figure_upload_to, resolve_examen_label
from programme.models import Module, Savoir
from .rendering import _exercise_titre_et_points, _render_question_enonce, cours_sections_breakdown
from .sujet_pdf import _render_html, save_sujet_pdf, sujet_pdf_filename


def _exercise_payload(epreuve_source, numero="1"):
    return {
        "epreuve_source": epreuve_source,
        "numero_exercice": numero,
        "matiere": "Mathématiques",
        "serie": "C",
        "examen": "BAC",
        "questions": [
            {"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé."},
        ],
    }


class CountryCodeFromPathTests(TestCase):
    def test_extracts_two_letter_code_after_ingest_segment(self):
        path = Path("/app/ingest/cm/bac-maths-2010/bac-maths-2010_exercice_1.json")
        self.assertEqual(_country_code_from_path(path), "cm")

    def test_works_with_country_folder_passed_directly(self):
        # `manage.py ingest_corrections ingest/bj/` : le code pays reste dans le
        # chemin absolu résolu même si l'argument transmis ne contient pas "ingest".
        path = Path("ingest/bj/epreuve-x")
        self.assertEqual(_country_code_from_path(path), "bj")

    def test_returns_none_without_an_ingest_segment(self):
        path = Path("/tmp/some-other-dir/exercice.json")
        self.assertIsNone(_country_code_from_path(path))


class IngestExerciseCountryScopingTests(TestCase):
    """
    Reproduit le bug corrigé : avant, _resolve_cursus_list ignorait le pays et
    Cursus.objects.get(examen=.., series=..) levait MultipleObjectsReturned dès que
    deux pays partageaient le même (examen, série) - voir catalog.ingestion.
    """

    def setUp(self):
        # Référentiel CM déjà seedé par les migrations (0003/0015) - voir le même
        # commentaire dans payments/tests.py::_make_cursus.
        self.cm = Country.objects.get(code="CM")
        self.bj = Country.objects.create(code="BJ", label="Bénin")
        # Subject/Series sont maintenant propres à chaque pays (voir catalog.models) :
        # le Bénin a besoin de ses propres lignes, pas de celles du Cameroun.
        Subject.objects.create(country=self.bj, code="MATHS", label="Mathématiques")
        series_c_bj = Series.objects.create(country=self.bj, code="C", label="Maths")
        self.bj_cursus = Cursus.objects.create(country=self.bj, examen=Examen.BAC, series=series_c_bj)

    def test_same_examen_serie_resolves_to_each_countrys_own_cursus(self):
        cm_exercise, _ = ingest_exercise(
            _exercise_payload("bac-maths-2024"),
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )
        bj_exercise, _ = ingest_exercise(
            _exercise_payload("bac-maths-2024"),
            source_dir=Path("ingest/bj/bac-maths-2024"),
        )

        self.assertEqual(list(cm_exercise.lesson.cursus.all()), [Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")])
        self.assertEqual(list(bj_exercise.lesson.cursus.all()), [self.bj_cursus])

    def test_identical_epreuve_source_in_two_countries_does_not_merge_lessons(self):
        cm_exercise, _ = ingest_exercise(
            _exercise_payload("bac-blanc-maths-2024"),
            source_dir=Path("ingest/cm/bac-blanc-maths-2024"),
        )
        bj_exercise, _ = ingest_exercise(
            _exercise_payload("bac-blanc-maths-2024"),
            source_dir=Path("ingest/bj/bac-blanc-maths-2024"),
        )

        self.assertNotEqual(cm_exercise.lesson_id, bj_exercise.lesson_id)
        self.assertEqual(Lesson.objects.filter(epreuve_source="bac-blanc-maths-2024").count(), 2)

    def test_missing_source_dir_raises(self):
        with self.assertRaises(IngestionError):
            ingest_exercise(_exercise_payload("bac-maths-2024"), source_dir=None)

    def test_unknown_country_folder_raises(self):
        with self.assertRaises(IngestionError):
            ingest_exercise(
                _exercise_payload("bac-maths-2024"),
                source_dir=Path("ingest/zz/bac-maths-2024"),
            )

    def test_subject_not_seeded_for_country_raises(self):
        # "LITTERATURE" existe pour CM (migration 0011) mais jamais créé pour BJ
        # dans ce setUp - _resolve_subject doit refuser de retomber sur celui du CM.
        payload = {**_exercise_payload("bac-lit-2024"), "matiere": "Littérature"}
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/bj/bac-lit-2024"))


class SavoirOfficielLinkingTests(TestCase):
    """`savoir_officiel` (optionnel, sur une Question ou un Cours) lie le Tag résolu à
    son Savoir officiel - voir catalog.ingestion._resolve_savoir_officiel et
    _link_tags_to_savoir. Branché depuis correction-experte (ce test), et de la même
    façon depuis concepteur-quiz-competence/concepteur-epreuve-inedite (voir leurs
    propres tests)."""

    def setUp(self):
        maths = Subject.objects.get(country__code="CM", code="MATHS")
        module = Module.objects.create(subject=maths, classe="1ere", serie_label="C", numero="99", titre="Module test")
        self.savoir = Savoir.objects.create(module=module, numero="I", intitule="Notion test")
        self.savoir_ref = {"classe": "1ere", "serie_label": "C", "module_numero": "99", "savoir_numero": "I"}

    def test_links_new_tag_to_savoir(self):
        payload = _exercise_payload("bac-maths-savoir-1")
        payload["questions"][0]["themes"] = ["Notion test tag"]
        payload["questions"][0]["savoir_officiel"] = self.savoir_ref
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoir-1"))

        tag = Tag.objects.get(name="Notion test tag")
        self.assertEqual(tag.savoir_officiel_id, self.savoir.pk)

    def test_never_overwrites_an_already_linked_tag(self):
        other_savoir = Savoir.objects.create(module=self.savoir.module, numero="II", intitule="Autre notion")
        tag = Tag.objects.create(name="Deja lie", savoir_officiel=other_savoir)

        payload = _exercise_payload("bac-maths-savoir-2")
        payload["questions"][0]["themes"] = ["Deja lie"]
        payload["questions"][0]["savoir_officiel"] = self.savoir_ref
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoir-2"))

        tag.refresh_from_db()
        self.assertEqual(tag.savoir_officiel_id, other_savoir.pk)

    def test_absent_field_is_a_no_op(self):
        payload = _exercise_payload("bac-maths-savoir-3")
        payload["questions"][0]["themes"] = ["Sans savoir"]
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoir-3"))

        tag = Tag.objects.get(name="Sans savoir")
        self.assertIsNone(tag.savoir_officiel_id)

    def test_unresolvable_reference_raises(self):
        payload = _exercise_payload("bac-maths-savoir-4")
        payload["questions"][0]["themes"] = ["Peu importe"]
        payload["questions"][0]["savoir_officiel"] = {**self.savoir_ref, "module_numero": "999"}
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoir-4"))

    def test_duplicate_savoir_numero_in_module_raises_cleanly(self):
        # Régression du 2026-08-12 : un doublon de numérotation dans le fixture source
        # (deux savoirs "III" sous le même module, voir programme_officiel_cm_maths.json)
        # faisait remonter un Savoir.MultipleObjectsReturned brut jusqu'à l'appelant -
        # doit échouer proprement via IngestionError à la place.
        Savoir.objects.create(module=self.savoir.module, numero="I", intitule="Doublon du même numéro")

        payload = _exercise_payload("bac-maths-savoir-5")
        payload["questions"][0]["themes"] = ["Peu importe"]
        payload["questions"][0]["savoir_officiel"] = self.savoir_ref
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoir-5"))


class BepcWithoutSerieIngestionTests(TestCase):
    """Le BEPC (fin de collège au Cameroun) n'a pas de série, contrairement au
    Probatoire/BAC - REQUIRED_KEYS exigeait pourtant `serie` sans condition, rejetant
    toute épreuve BEPC avant même d'atteindre _resolve_cursus_list qui, lui, sait déjà
    ignorer `serie` pour ce diplôme (Cursus.series__isnull=True, voir seed_country)."""

    def _bepc_payload(self, epreuve_source="bepc-physique-2023", **overrides):
        payload = {**_exercise_payload(epreuve_source), "matiere": "Physique-Chimie", "examen": "BEPC"}
        del payload["serie"]
        payload.update(overrides)
        return payload

    def test_bepc_exercise_without_serie_key_ingests_successfully(self):
        exercise, created = ingest_exercise(self._bepc_payload(), source_dir=Path("ingest/cm/bepc-physique-2023"))

        self.assertTrue(created)
        self.assertEqual(
            list(exercise.lesson.cursus.all()),
            [Cursus.objects.get(country__code="CM", examen=Examen.BEPC, series__isnull=True)],
        )

    def test_bepc_exercise_with_null_serie_still_ingests_successfully(self):
        exercise, created = ingest_exercise(
            self._bepc_payload(serie=None), source_dir=Path("ingest/cm/bepc-physique-2023"),
        )

        self.assertTrue(created)

    def test_bac_still_requires_a_serie(self):
        payload = {**_exercise_payload("bac-maths-2024")}
        del payload["serie"]
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))


class PaysFieldToleranceTests(TestCase):
    """SKILL.md ajoute un champ `pays` (code ISO alpha-2 minuscule) au schéma JSON,
    censé reproduire le pays déjà déduit du dossier ingest/<code_pays>/ - voir
    catalog.ingestion._validate_pays_matches_country. Le pays continue d'être résolu
    uniquement depuis le dossier, jamais depuis ce champ : `pays` ne sert que de
    signal de contrôle redondant."""

    def test_ingest_exercise_accepts_a_pays_matching_the_folder(self):
        payload = {**_exercise_payload("bac-maths-2024"), "pays": "cm"}
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(exercise.lesson.cursus.first().country.code, "CM")

    def test_ingest_exercise_still_works_when_pays_is_absent(self):
        # Corpus existant intégral au moment où ce champ a été ajouté à la compétence :
        # aucun fichier ne le porte encore - absence != erreur.
        exercise, _ = ingest_exercise(_exercise_payload("bac-maths-2024"), source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(exercise.lesson.cursus.first().country.code, "CM")

    def test_ingest_exercise_rejects_a_pays_contradicting_the_folder(self):
        # Contenu déposé dans le mauvais dossier (ou dérive analogue à celle déjà
        # rencontrée sur `origine`) : signalé plutôt que silencieusement ignoré.
        payload = {**_exercise_payload("bac-maths-2024"), "pays": "sn"}
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))


class CountryFilteringApiTests(TestCase):
    """`?country=` sur les vues de liste catalog - voir catalog.views."""

    def setUp(self):
        self.cm_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.cm_subject = Subject.objects.get(country__code="CM", code="MATHS")

        self.bj = Country.objects.create(code="BJ", label="Bénin")
        # Subject/Series sont propres à chaque pays (voir catalog.models) : on ne
        # réutilise pas les lignes du Cameroun pour le Cursus/Lesson/Cours du Bénin.
        bj_series_c = Series.objects.create(country=self.bj, code="C", label="Maths")
        self.bj_cursus = Cursus.objects.create(country=self.bj, examen=Examen.BAC, series=bj_series_c)
        self.bj_subject = Subject.objects.create(country=self.bj, code="MATHS", label="Mathématiques")

        self.cm_lesson = Lesson.objects.create(
            title="CM", subject=self.cm_subject, lesson_type=LessonType.CORR,
            epreuve_source="cm-src", statut=StatutContenu.VALIDE,
        )
        self.cm_lesson.cursus.add(self.cm_cursus)

        self.bj_lesson = Lesson.objects.create(
            title="BJ", subject=self.bj_subject, lesson_type=LessonType.CORR,
            epreuve_source="bj-src", statut=StatutContenu.VALIDE,
        )
        self.bj_lesson.cursus.add(self.bj_cursus)

        # Cours "toutes séries" (cursus vide) : doit rester visible quel que soit
        # le pays filtré - voir Cours.cursus (blank=True) et le commentaire dans
        # CoursListView.get_queryset.
        self.universal_cours = Cours.objects.create(
            external_id="universal", titre="Universel", subject=self.cm_subject, statut=StatutContenu.VALIDE,
        )
        self.bj_cours = Cours.objects.create(
            external_id="bj-only", titre="BJ seulement", subject=self.bj_subject, statut=StatutContenu.VALIDE,
        )
        self.bj_cours.cursus.add(self.bj_cursus)

    def test_lesson_list_filters_by_country(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"country": "bj"})
        titles = [item["title"] for item in response.json()["results"]] if "results" in response.json() else [item["title"] for item in response.json()]
        self.assertIn("BJ", titles)
        self.assertNotIn("CM", titles)

    def test_cursus_list_filters_by_country_and_exposes_country_field(self):
        # Le référentiel CM compte 15 Cursus déjà seedés (migrations) - seul "bj" est
        # sans ambiguïté ici puisqu'on n'en crée qu'un seul dans setUp.
        response = self.client.get(reverse("catalog:cursus-list"), {"country": "bj"})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["country"]["code"], "BJ")

    def test_cours_list_country_filter_keeps_universal_cours(self):
        response = self.client.get(reverse("catalog:cours-list"), {"country": "cm"})
        payload = response.json()
        titles = [item["titre"] for item in payload["results"]] if "results" in payload else [item["titre"] for item in payload]
        self.assertIn("Universel", titles)
        self.assertNotIn("BJ seulement", titles)

    def test_country_list_exposes_dial_code_and_currency(self):
        response = self.client.get(reverse("catalog:country-list"))
        by_code = {item["code"]: item for item in response.json()}
        self.assertEqual(by_code["CM"]["dial_code"], "237")
        self.assertEqual(by_code["CM"]["currency"], "XAF")
        self.assertEqual(by_code["BJ"]["dial_code"], "")
        self.assertEqual(by_code["BJ"]["currency"], "")

    def test_country_list_flags_has_lessons_correctly(self):
        # Pays présent en base (référentiel Subject/Series/Cursus déjà créé, voir
        # seed_country) mais sans aucune Lesson VALIDE encore ingérée - doit rester
        # listé (le sélecteur d'inscription en a besoin) mais avec has_lessons=false.
        empty_country = Country.objects.create(code="TD", label="Tchad")
        Subject.objects.create(country=empty_country, code="MATHS", label="Mathématiques")

        response = self.client.get(reverse("catalog:country-list"))
        by_code = {item["code"]: item for item in response.json()}

        self.assertTrue(by_code["CM"]["has_lessons"])
        self.assertTrue(by_code["BJ"]["has_lessons"])
        self.assertFalse(by_code["TD"]["has_lessons"])


class ExcludeReadFilterApiTests(TestCase):
    """`?exclude_read=true` sur /catalog/lessons/ - alimente la section "Autres
    épreuves" (EpreuveDetailPage) pour ne pousser que du contenu neuf. Doit se
    dégrader proprement pour un visiteur anonyme (aucun LectureProgress à exclure),
    voir LessonListView.get_queryset."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.lesson_read = Lesson.objects.create(
            title="Lu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson_unread = Lesson.objects.create(
            title="Non lu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.user = User.objects.create_user(phone_number="677100002", password="x")
        LectureProgress.objects.create(user=self.user, lesson=self.lesson_read)

    def test_excludes_already_read_lesson_for_authenticated_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(reverse("catalog:lesson-list"), {"exclude_read": "true"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Non lu", titles)
        self.assertNotIn("Lu", titles)

    def test_is_a_no_op_for_anonymous_user(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"exclude_read": "true"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Lu", titles)
        self.assertIn("Non lu", titles)


class OrderingFilterApiTests(TestCase):
    """`?ordering=year` sur /catalog/lessons/ - tri du catalogue par année croissante,
    à l'inverse du défaut (Lesson.Meta.ordering = -year, plus récent d'abord)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.old = Lesson.objects.create(
            title="Ancien", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, year=2001,
        )
        self.recent = Lesson.objects.create(
            title="Recent", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, year=2023,
        )

    def test_default_ordering_is_most_recent_first(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertLess(titles.index("Recent"), titles.index("Ancien"))

    def test_ordering_year_sorts_oldest_first(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "year"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertLess(titles.index("Ancien"), titles.index("Recent"))

    def test_ordering_recent_sorts_by_created_at_not_year(self):
        # Un vieux sujet (year=2001) tout juste corrigé doit ressortir avant un sujet
        # plus récent (year=2023) ajouté plus tôt à la plateforme - created_at, jamais
        # year (voir le rail "Derniers ajouts", audit UX). .update() plutôt que
        # created_at= au create() : auto_now_add ignore toute valeur passée à l'INSERT.
        Lesson.objects.filter(pk=self.old.pk).update(created_at=timezone.now())
        Lesson.objects.filter(pk=self.recent.pk).update(created_at=timezone.now() - timezone.timedelta(days=10))
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "recent"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertLess(titles.index("Ancien"), titles.index("Recent"))


class PopularOrderingApiTests(TestCase):
    """`?ordering=popular` sur /catalog/lessons/ - classe par nombre de lecteurs
    distincts (access.LectureProgress), avec un seuil minimum (voir
    catalog.views.MIN_POPULAR_READERS) pour ne jamais qualifier de "populaire" un
    contenu qui n'a que 1-2 lectures de test."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.popular = Lesson.objects.create(
            title="Tres lu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, year=2020,
        )
        self.below_threshold = Lesson.objects.create(
            title="Peu lu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, year=2021,
        )
        self.unread = Lesson.objects.create(
            title="Jamais lu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE, year=2022,
        )
        for i in range(3):
            reader = User.objects.create_user(phone_number=f"67710010{i}", password="x")
            LectureProgress.objects.create(user=reader, lesson=self.popular)
        below_reader = User.objects.create_user(phone_number="677100109", password="x")
        LectureProgress.objects.create(user=below_reader, lesson=self.below_threshold)

    def test_excludes_lessons_below_minimum_reader_threshold(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "popular"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Tres lu", titles)
        self.assertNotIn("Peu lu", titles)
        self.assertNotIn("Jamais lu", titles)

    def test_never_exposes_raw_reader_count(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "popular"})
        item = response.json()["results"][0]
        self.assertNotIn("_lectures_count", item)
        self.assertNotIn("lectures_count", item)


class InediteCatalogueMergeApiTests(TestCase):
    """/catalog/lessons/ fusionne désormais Lesson et EpreuveInedite - voir
    catalog.views.LessonListView.list / catalog.inedit_bridge. Une EpreuveInedite n'a
    pas d'année (sort toujours après une Lesson datée sous ordering=year/défaut -
    décision produit actée, voir le plan de fusion du catalogue)."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Classique", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, year=2020,
        )
        self.lesson.cursus.add(self.cursus)

        self.blueprint = Blueprint.objects.create(
            subject=self.subject, titre="Blueprint fusion",
            sections_plan=[{"section": "Exercice 1", "points": 20}], duree_minutes=120, bareme_total=20,
            statut=StatutContenu.VALIDE,
        )
        self.blueprint.cursus.set([self.cursus])
        self.epreuve = EpreuveInedite.objects.create(
            blueprint=self.blueprint, subject=self.subject,
            titre="Inedite fusion", statut=StatutContenu.VALIDE,
        )
        self.epreuve.cursus.set([self.cursus])

    def test_inedite_appears_in_merged_list_with_kind(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS"})
        by_title = {item["title"]: item for item in response.json()["results"]}
        self.assertIn("Inedite fusion", by_title)
        self.assertEqual(by_title["Inedite fusion"]["kind"], "inedite")
        self.assertEqual(by_title["Classique"]["kind"], "classique")

    def test_epreuve_common_to_multiple_series_appears_only_once(self):
        """Régression : cursus__country__actif (build_inedit_queryset) traverse le M2M
        EpreuveInedite.cursus - sans distinct(), une épreuve commune à 2 séries
        apparaissait 2 fois dans la liste fusionnée."""
        other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.epreuve.cursus.add(other_cursus)

        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS"})

        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles.count("Inedite fusion"), 1)

    def test_inedite_exposes_its_own_slug_through_the_merged_list(self):
        # Contrairement au reste des champs classique-only (voir Epreuve côté frontend),
        # slug est désormais renseigné aussi côté inédit (voir EpreuveInedite.slug) - un
        # id numérique dans l'URL ne dit rien du contenu (motif SEO, voir
        # generate_unique_slug côté catalog, réutilisé tel quel).
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "origine": "INEDITE"})
        item = response.json()["results"][0]
        self.assertEqual(item["slug"], self.epreuve.slug)
        self.assertNotEqual(item["slug"], None)

    def test_origine_inedite_filter_returns_only_inedites(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "origine": "INEDITE"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["Inedite fusion"])

    def test_lesson_type_filter_excludes_inedites(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "lesson_type": "CORR"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Classique", titles)
        self.assertNotIn("Inedite fusion", titles)

    def test_nature_filter_excludes_inedites(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "nature": "pratique"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertNotIn("Inedite fusion", titles)

    def test_est_vitrine_filter_excludes_inedites(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "est_vitrine": "true"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertNotIn("Inedite fusion", titles)

    def test_default_and_year_ordering_puts_inedite_after_dated_lessons(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertLess(titles.index("Classique"), titles.index("Inedite fusion"))

        response_year = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "year"})
        titles_year = [item["title"] for item in response_year.json()["results"]]
        self.assertLess(titles_year.index("Classique"), titles_year.index("Inedite fusion"))

    def test_popular_ordering_respects_threshold_for_inedites(self):
        for i in range(3):
            reader = User.objects.create_user(phone_number=f"67710020{i}", password="x")
            TentativeInedite.objects.create(user=reader, epreuve=self.epreuve)

        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "ordering": "popular"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Inedite fusion", titles)

    def test_anonymous_request_sees_inedite_with_has_access_false(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "origine": "INEDITE"})
        item = response.json()["results"][0]
        self.assertFalse(item["has_access"])

    def test_pagination_across_merged_set_larger_than_page_size(self):
        for i in range(30):
            extra = Lesson.objects.create(
                title=f"Page {i}", subject=self.subject, lesson_type=LessonType.CORR,
                statut=StatutContenu.VALIDE, year=1990 + i,
            )
            extra.cursus.add(self.cursus)

        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS"})
        payload = response.json()
        self.assertEqual(len(payload["results"]), 24)
        self.assertIsNotNone(payload["next"])
        self.assertEqual(payload["count"], 32)  # 30 + self.lesson + self.epreuve

        page2 = self.client.get(payload["next"])
        self.assertEqual(len(page2.json()["results"]), 8)

    def test_related_cours_surfaces_through_the_merged_list_too(self):
        """Même fonction (catalog.inedit_bridge.epreuve_inedite_catalogue_payload) que
        pour la fiche détail - second consommateur, même garantie."""
        exercice = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="1")
        rappel = RappelDeMethodeInedite.objects.create(
            exercice=exercice, external_id="rdi-merge-test", competence="C",
        )
        cours = Cours.objects.create(
            external_id="cours-merge-test", titre="Cours fusion", subject=self.subject, statut=StatutContenu.VALIDE,
        )
        rappel.cours = cours
        rappel.save(update_fields=["cours"])

        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "origine": "INEDITE"})

        item = response.json()["results"][0]
        self.assertEqual([c["titre"] for c in item["related_cours"]], ["Cours fusion"])

    def test_apercu_enonce_markdown_stays_none_in_the_merged_list(self):
        # include_apercu=False dans le catalogue fusionné (voir
        # catalog.inedit_bridge.epreuve_inedite_catalogue_payload) - même si l'épreuve a
        # bien une question, la clé reste None ici : coûterait 2 requêtes de plus par
        # carte pour un aperçu jamais affiché dans la liste (seul EpreuveInediteDetailAPITests
        # couvre la valeur réellement renseignée, sur la fiche détail).
        exercice = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="1")
        QuestionInedite.objects.create(
            exercice=exercice, numero="1", ordre=1, enonce_markdown="Un énoncé.",
            corrige_markdown="Un corrigé.", type_reponse=TypeReponse.OUVERTE,
        )

        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "MATHS", "origine": "INEDITE"})

        item = response.json()["results"][0]
        self.assertIsNone(item["apercu_enonce_markdown"])


class CountryActiveFilteringTests(TestCase):
    """`Country.actif=False` doit rendre tout le contenu de ce pays invisible côté
    frontend (catalogue, cours, quiz, sitemap) sans jamais bloquer l'ingestion - voir
    catalog.models.VisibleQuerySet, que l'ingestion ne consulte jamais."""

    def setUp(self):
        self.inactive = Country.objects.create(code="TG", label="Togo", actif=False)
        series = Series.objects.create(country=self.inactive, code="C", label="Maths")
        self.inactive_cursus = Cursus.objects.create(country=self.inactive, examen=Examen.BAC, series=series)
        self.inactive_subject = Subject.objects.create(country=self.inactive, code="MATHS", label="Mathématiques")
        self.inactive_lesson = Lesson.objects.create(
            title="Togo", subject=self.inactive_subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )
        self.inactive_lesson.cursus.add(self.inactive_cursus)
        self.inactive_cours = Cours.objects.create(
            external_id="tg-cours", titre="Cours Togo", subject=self.inactive_subject, statut=StatutContenu.VALIDE,
        )
        inactive_blueprint = Blueprint.objects.create(
            subject=self.inactive_subject, titre="BP Togo",
            statut=StatutContenu.VALIDE,
        )
        inactive_blueprint.cursus.set([self.inactive_cursus])
        self.inactive_epreuve_inedite = EpreuveInedite.objects.create(
            blueprint=inactive_blueprint, subject=self.inactive_subject,
            titre="Inédite Togo", statut=StatutContenu.VALIDE,
        )
        self.inactive_epreuve_inedite.cursus.set([self.inactive_cursus])

    def _titles(self, payload, key):
        return [item[key] for item in payload["results"]] if "results" in payload else [item[key] for item in payload]

    def test_country_list_excludes_inactive_country(self):
        response = self.client.get(reverse("catalog:country-list"))
        codes = [item["code"] for item in response.json()]
        self.assertNotIn("TG", codes)

    def test_subject_list_excludes_inactive_country(self):
        response = self.client.get(reverse("catalog:subject-list"), {"country": "tg"})
        self.assertEqual(response.json(), [])

    def test_cursus_list_excludes_inactive_country(self):
        response = self.client.get(reverse("catalog:cursus-list"), {"country": "tg"})
        self.assertEqual(response.json(), [])

    def test_lesson_list_excludes_inactive_country(self):
        response = self.client.get(reverse("catalog:lesson-list"))
        self.assertNotIn("Togo", self._titles(response.json(), "title"))

    def test_lesson_detail_404_for_inactive_country(self):
        response = self.client.get(reverse("catalog:lesson-detail", args=[self.inactive_lesson.id]))
        self.assertEqual(response.status_code, 404)

    def test_cours_list_excludes_inactive_country(self):
        response = self.client.get(reverse("catalog:cours-list"))
        self.assertNotIn("Cours Togo", self._titles(response.json(), "titre"))

    def test_cours_detail_404_for_inactive_country(self):
        response = self.client.get(reverse("catalog:cours-detail", args=[self.inactive_cours.id]))
        self.assertEqual(response.status_code, 404)

    def test_preview_lesson_404_for_inactive_country(self):
        response = self.client.get(reverse("access:preview", args=[self.inactive_lesson.id]))
        self.assertEqual(response.status_code, 404)

    def test_preview_cours_404_for_inactive_country(self):
        response = self.client.get(reverse("access:cours-preview", args=[self.inactive_cours.id]))
        self.assertEqual(response.status_code, 404)

    def test_sitemap_excludes_inactive_country(self):
        from django.conf import settings

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        base = settings.FRONTEND_URL
        self.assertNotIn(f"<loc>{base}/tg</loc>", xml)
        self.assertNotIn(f"/epreuves/{self.inactive_lesson.slug}", xml)
        self.assertNotIn(f"/epreuves-inedites/{self.inactive_epreuve_inedite.slug}", xml)

    def test_ingestion_still_accepts_content_for_an_inactive_country(self):
        # L'ingestion ne consulte jamais Country.actif - un pays désactivé doit rester
        # ingérable (préparation avant lancement, ou retrait temporaire sans perdre le
        # contenu déjà traité).
        payload = _exercise_payload("tg-src")
        payload["matiere"] = "Mathématiques"
        payload["serie"] = "C"
        exercise, created = ingest_exercise(payload, source_dir=Path("ingest/tg/tg-src"))
        self.assertTrue(created)
        self.assertEqual(exercise.lesson.subject.country.code, "TG")


class CoursDetailSlugLookupTests(TestCase):
    """`/catalog/cours/<slug-ou-id>/` - voir CoursDetailView.get_object et
    catalog.models.Cours.save (slug auto-généré), reco d'audit UX (URLs cours en slug)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(
            external_id="slug-lookup-test", titre="Cours de test slug", subject=subject, statut=StatutContenu.VALIDE,
        )

    def test_generates_a_slug_from_titre_on_creation(self):
        self.assertEqual(self.cours.slug, "cours-de-test-slug")

    def test_detail_view_resolves_by_slug(self):
        response = self.client.get(reverse("catalog:cours-detail", args=[self.cours.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["titre"], "Cours de test slug")

    def test_detail_view_still_resolves_by_numeric_id(self):
        # Compat historique (voir VisibleQuerySet.par_slug_ou_id) - liens déjà en
        # circulation construits avec l'id avant l'introduction du slug.
        response = self.client.get(reverse("catalog:cours-detail", args=[self.cours.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["titre"], "Cours de test slug")


class SubjectSeriesCountryScopingTests(TestCase):
    """Subject/Series sont rattachés à Country (voir catalog.models) - un même code
    ("MATHS", "C") doit pouvoir exister une fois par pays sans collision."""

    def setUp(self):
        self.bj = Country.objects.create(code="BJ", label="Bénin")

    def test_same_subject_code_allowed_in_two_countries(self):
        cm_maths = Subject.objects.get(country__code="CM", code="MATHS")
        bj_maths = Subject.objects.create(country=self.bj, code="MATHS", label="Mathématiques")
        self.assertNotEqual(cm_maths.pk, bj_maths.pk)

    def test_subject_list_filters_by_country(self):
        bj_subject = Subject.objects.create(country=self.bj, code="MATHS", label="Mathématiques")
        # SubjectListView ne propose désormais que les matières ayant déjà du contenu
        # publié (voir SubjectCursusContentFilterTests) - sans cette Lesson, "MATHS"
        # n'apparaîtrait plus du tout, et ce test ne vérifierait plus le scoping pays.
        Lesson.objects.create(
            title="BJ Maths", subject=bj_subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        response = self.client.get(reverse("catalog:subject-list"), {"country": "bj"})
        codes = [item["code"] for item in response.json()]
        self.assertEqual(codes, ["MATHS"])

    def test_cursus_clean_rejects_series_from_another_country(self):
        cm_series_c = Series.objects.get(country__code="CM", code="C")
        cursus = Cursus(country=self.bj, examen=Examen.BAC, series=cm_series_c)
        with self.assertRaises(ValidationError):
            cursus.full_clean()


class SplitSeriesTests(TestCase):
    """Reproduit un blocage d'ingestion réel (bac-blanc-d-ti-physique-2025-cameroun,
    4 fichiers) : "D et TI" (conjonction française, pas un séparateur symbolique comme
    "," ou "-") était splitté par _split_series en trois tokens ["D", "et", "TI"],
    "et" étant ensuite rejeté comme code de série inconnu - voir
    catalog.ingestion._split_series."""

    def test_treats_et_as_a_separator_not_a_series_code(self):
        from .ingestion import _split_series

        self.assertEqual(_split_series("D et TI"), ["D", "TI"])

    def test_still_handles_the_existing_separator_forms(self):
        from .ingestion import _split_series

        self.assertEqual(_split_series("C-E"), ["C", "E"])
        self.assertEqual(_split_series("C, E"), ["C", "E"])
        self.assertEqual(_split_series("C"), ["C"])
        self.assertEqual(_split_series("A-ABI"), ["A"])

    def test_ingest_exercise_resolves_both_cursus_for_a_et_b_series(self):
        payload = _exercise_payload("bac-blanc-d-ti-physique-2025-cameroun")
        payload["matiere"] = "Physique-Chimie"
        payload["serie"] = "D et TI"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-blanc-d-ti-physique-2025-cameroun"))

        series_codes = sorted(c.series.code for c in exercise.lesson.cursus.all())
        self.assertEqual(series_codes, ["D", "TI"])


class SubjectCursusContentFilterTests(TestCase):
    """SubjectListView/CursusListView ne proposent que les matières/cursus ayant déjà
    du contenu publié (Épreuve ou Cours, statut VALIDE) - décision utilisateur du
    2026-08-03 : le référentiel Subject/Series/Cursus (seedé par pays, voir
    seed_country) est bien plus large que le contenu réellement ingéré à date, les
    selects du catalogue étaient donc très majoritairement vides. Même principe que
    CountrySerializer.get_has_lessons, étendu à Cours."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        # Série dédiée (code inédit) plutôt qu'une des séries déjà seedées par
        # migration : évite toute collision avec un Cursus (country, examen, series)
        # déjà existant, la combinaison étant contrainte unique (voir Cursus.Meta).
        self.series = Series.objects.create(country=self.country, code="TESTX", label="Test")
        self.empty_subject = Subject.objects.create(
            country=self.country, code="PHYSIQUE_CHIMIE_2", label="Physique-Chimie (vide)",
        )
        self.empty_cursus = Cursus.objects.create(
            country=self.country, examen=Examen.PROBATOIRE, series=self.series,
        )

    def test_subject_list_excludes_a_subject_with_no_content(self):
        response = self.client.get(reverse("catalog:subject-list"), {"country": "cm"})
        codes = [item["code"] for item in response.json()]
        self.assertNotIn("PHYSIQUE_CHIMIE_2", codes)

    def test_subject_list_includes_a_subject_with_only_a_valid_lesson(self):
        Lesson.objects.create(
            title="A du contenu", subject=self.empty_subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )
        response = self.client.get(reverse("catalog:subject-list"), {"country": "cm"})
        codes = [item["code"] for item in response.json()]
        self.assertIn("PHYSIQUE_CHIMIE_2", codes)

    def test_subject_list_includes_a_subject_with_only_a_valid_cours(self):
        Cours.objects.create(
            external_id="a-du-contenu", titre="A du contenu", subject=self.empty_subject,
            statut=StatutContenu.VALIDE,
        )
        response = self.client.get(reverse("catalog:subject-list"), {"country": "cm"})
        codes = [item["code"] for item in response.json()]
        self.assertIn("PHYSIQUE_CHIMIE_2", codes)

    def test_subject_list_excludes_a_subject_whose_only_lesson_is_a_draft(self):
        Lesson.objects.create(
            title="Brouillon", subject=self.empty_subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.BROUILLON,
        )
        response = self.client.get(reverse("catalog:subject-list"), {"country": "cm"})
        codes = [item["code"] for item in response.json()]
        self.assertNotIn("PHYSIQUE_CHIMIE_2", codes)

    def test_cursus_list_excludes_a_cursus_with_no_content(self):
        response = self.client.get(reverse("catalog:cursus-list"), {"country": "cm"})
        ids = [item["id"] for item in response.json()]
        self.assertNotIn(self.empty_cursus.id, ids)

    def test_cursus_list_includes_a_cursus_with_only_a_valid_lesson(self):
        subject = Subject.objects.get(country=self.country, code="MATHS")
        lesson = Lesson.objects.create(
            title="A du contenu", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.empty_cursus)

        response = self.client.get(reverse("catalog:cursus-list"), {"country": "cm"})
        ids = [item["id"] for item in response.json()]
        self.assertIn(self.empty_cursus.id, ids)

    def test_cursus_list_includes_a_cursus_with_only_a_valid_cours(self):
        subject = Subject.objects.get(country=self.country, code="MATHS")
        cours = Cours.objects.create(
            external_id="a-du-contenu-2", titre="A du contenu", subject=subject, statut=StatutContenu.VALIDE,
        )
        cours.cursus.add(self.empty_cursus)

        response = self.client.get(reverse("catalog:cursus-list"), {"country": "cm"})
        ids = [item["id"] for item in response.json()]
        self.assertIn(self.empty_cursus.id, ids)


class SeedCountryCommandTests(TestCase):
    """`manage.py seed_country` - voir catalog.management.commands.seed_country."""

    def _run(self, *args, **kwargs):
        call_command("seed_country", *args, stdout=StringIO(), **kwargs)

    def test_seeds_full_referentiel_for_a_new_country(self):
        self._run("bj", "Bénin", dial_code="229", currency="XOF")

        bj = Country.objects.get(code="BJ")
        self.assertEqual(bj.label, "Bénin")
        self.assertEqual(bj.dial_code, "229")
        self.assertEqual(bj.currency, "XOF")
        # Comparé à SUBJECTS plutôt qu'à un nombre en dur : ce qui est testé est que la
        # commande crée bien *toute* la liste déclarée, et un compte figé fait échouer ces
        # tests à chaque matière ajoutée au référentiel pour une raison qui n'en est pas
        # une (constaté : bloqués à 15 alors que la liste en comptait 16).
        self.assertEqual(Subject.objects.filter(country=bj).count(), len(SEED_SUBJECTS))
        self.assertEqual(Series.objects.filter(country=bj).count(), 7)
        # 1 BEPC (sans série) + 7 séries x (PROBATOIRE + BAC).
        self.assertEqual(Cursus.objects.filter(country=bj).count(), 15)

        # Chaque Cursus créé doit passer la validation cross-pays (voir Cursus.clean) -
        # le référentiel de ce pays ne doit jamais mélanger la Series d'un autre pays.
        for cursus in Cursus.objects.filter(country=bj):
            cursus.full_clean()

    def test_is_idempotent(self):
        self._run("bj", "Bénin")
        self._run("bj", "Bénin")

        self.assertEqual(Country.objects.filter(code="BJ").count(), 1)
        bj = Country.objects.get(code="BJ")
        self.assertEqual(Subject.objects.filter(country=bj).count(), len(SEED_SUBJECTS))
        self.assertEqual(Cursus.objects.filter(country=bj).count(), 15)

    def test_rejects_code_that_is_not_two_letters(self):
        with self.assertRaises(CommandError):
            self._run("ben", "Bénin")

    def test_does_not_touch_other_countries_referentiel(self):
        cm_subject_count = Subject.objects.filter(country__code="CM").count()
        self._run("bj", "Bénin")
        self.assertEqual(Subject.objects.filter(country__code="CM").count(), cm_subject_count)

    def test_new_country_defaults_to_inactive(self):
        # Un référentiel cloné depuis le Cameroun n'est pas une localisation réelle - voir
        # l'audit UX, reco 8.2. Le pays doit rester invisible du catalogue public
        # (VisibleQuerySet.visibles()) tant qu'un admin ne l'a pas vérifié et activé.
        self._run("bj", "Bénin")

        self.assertFalse(Country.objects.get(code="BJ").actif)

    def test_rerun_does_not_reset_an_already_activated_country(self):
        # Idempotence : compléter le référentiel d'un pays déjà activé par un admin ne
        # doit jamais le repasser inactif (get_or_create ne touche pas defaults sur un
        # objet déjà existant, mais on le vérifie explicitement ici).
        self._run("bj", "Bénin")
        bj = Country.objects.get(code="BJ")
        bj.actif = True
        bj.save(update_fields=["actif"])

        self._run("bj", "Bénin")

        self.assertTrue(Country.objects.get(code="BJ").actif)


class ExamenLabelTests(TestCase):
    """Le nom affiché d'un examen peut différer du code interne selon le pays (ex :
    le Sénégal appelle son BEPC "BFEM") - voir catalog.models.ExamenLabel."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        self.sn = Country.objects.create(code="SN", label="Sénégal")
        ExamenLabel.objects.create(country=self.sn, examen=Examen.BEPC, label="BFEM")

    def test_resolve_examen_label_returns_override_when_present(self):
        self.assertEqual(resolve_examen_label(self.sn, Examen.BEPC), "BFEM")

    def test_resolve_examen_label_falls_back_to_generic_choice(self):
        # Pas d'override pour BAC au Sénégal, ni pour le Cameroun du tout.
        self.assertEqual(resolve_examen_label(self.sn, Examen.BAC), "BAC")
        self.assertEqual(resolve_examen_label(self.cm, Examen.BEPC), "BEPC")

    def test_cursus_str_uses_country_override(self):
        cursus = Cursus.objects.create(country=self.sn, examen=Examen.BEPC, series=None)
        self.assertEqual(str(cursus), "BFEM")

    def test_lesson_header_info_uses_country_override(self):
        subject = Subject.objects.get(country=self.cm, code="MATHS")
        cursus = Cursus.objects.create(country=self.sn, examen=Examen.BEPC, series=None)
        lesson = Lesson.objects.create(
            title="Test BFEM", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        self.assertEqual(lesson.header_info()["examen"], "BFEM")

    def test_ingestion_accepts_bfem_alias_and_uses_it_in_lesson_title(self):
        Subject.objects.create(country=self.sn, code="MATHS", label="Mathématiques")
        Cursus.objects.create(country=self.sn, examen=Examen.BEPC, series=None)

        payload = {
            "epreuve_source": "bfem-maths-2024", "numero_exercice": "1",
            "matiere": "Mathématiques", "serie": "-", "examen": "BFEM",
            "questions": [{"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé."}],
        }
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/sn/bfem-maths-2024"))
        self.assertIn("BFEM", exercise.lesson.title)

    def test_examen_map_tolerates_bfem_for_college_level(self):
        from .ingestion import EXAMEN_MAP

        self.assertEqual(EXAMEN_MAP["bfem"], Examen.BEPC)

    def test_api_exposes_country_specific_examen_display(self):
        cursus = Cursus.objects.create(country=self.sn, examen=Examen.BEPC, series=None)
        # CursusListView ne propose désormais que les cursus ayant déjà du contenu
        # publié (voir SubjectCursusContentFilterTests) - sans cette Lesson, ce cursus
        # n'apparaîtrait plus du tout, et ce test ne vérifierait plus examen_display.
        subject = Subject.objects.create(country=self.sn, code="MATHS", label="Mathématiques")
        lesson = Lesson.objects.create(
            title="SN BFEM", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)

        response = self.client.get(reverse("catalog:cursus-list"), {"country": "sn"})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], cursus.id)
        self.assertEqual(data[0]["examen_display"], "BFEM")


class OrigineMapToleranceTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 18 fichiers (bac-d-maths-1994 à 1997,
    bac-c-maths-2015-cameroun) portaient "origine": "officielle" (variante d'accord
    grammatical) ou "compilation" (sujet officiel réel transcrit depuis un ouvrage de
    compilation plutôt que le sujet de l'année seule - décision utilisateur du
    2026-08-03 : traiter comme un sujet officiel classique) - voir
    catalog.ingestion.ORIGINE_MAP. Ni l'une ni l'autre n'était reconnue, faisant lever
    IngestionError sur les 18 fichiers."""

    def test_origine_map_tolerates_the_feminine_grammatical_agreement(self):
        from .ingestion import ORIGINE_MAP

        self.assertEqual(ORIGINE_MAP["officielle"], Origine.OFFICIEL)

    def test_origine_map_treats_compilation_as_officiel(self):
        from .ingestion import ORIGINE_MAP

        self.assertEqual(ORIGINE_MAP["compilation"], Origine.OFFICIEL)

    def test_ingest_exercise_accepts_officielle_and_compilation(self):
        for origine_raw in ["officielle", "compilation"]:
            # numero distinct par itération : sinon le 2e appel retomberait sur le
            # même (lesson, numero_exercice) déjà ingéré et serait ignoré (idempotent
            # par défaut, voir ingest_exercise), sans jamais exercer "compilation".
            payload = _exercise_payload("bac-maths-2024", numero=origine_raw)
            payload["origine"] = origine_raw
            exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))
            self.assertEqual(exercise.lesson.origine, Origine.OFFICIEL)


class OrigineCountryNameToleranceTests(TestCase):
    """Reproduit un blocage d'ingestion réel, rencontré à deux reprises (8 fichiers
    bac-c-e-physique-2014/2015-cameroun, puis 28 fichiers bac-c(-e)-physique-2017 à
    2022-cameroun) : "origine" portait le nom du pays ("Cameroun") au lieu d'une
    catégorie valide - IngestionError sur les 36 fichiers au total. Voir
    catalog.ingestion._resolve_origine."""

    def test_ingest_exercise_treats_country_label_as_officiel(self):
        payload = _exercise_payload("bac-physique-2017")
        payload["origine"] = "Cameroun"
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-physique-2017"))
        self.assertEqual(exercise.lesson.origine, Origine.OFFICIEL)

    def test_ingest_exercise_still_rejects_an_unrelated_unknown_origine(self):
        payload = _exercise_payload("bac-physique-2018")
        payload["origine"] = "Nigeria"
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-physique-2018"))


class ExamenMapToleranceTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 60 fichiers (bac-d-physique-chimie
    1995-1997, bac-d-ti-physique 1999-2016-cameroun) portaient "examen":
    "baccalaureat" (nom complet en toutes lettres) plutôt que le code court "bac"
    documenté dans le schéma JSON de la compétence - voir catalog.ingestion.EXAMEN_MAP.
    IngestionError sur les 60 fichiers ("Examen inconnu : 'baccalaureat'")."""

    def test_examen_map_tolerates_the_full_word_form(self):
        from .ingestion import EXAMEN_MAP

        self.assertEqual(EXAMEN_MAP["baccalaureat"], Examen.BAC)

    def test_ingest_exercise_accepts_baccalaureat(self):
        payload = _exercise_payload("bac-physique-chimie-1995")
        payload["examen"] = "baccalaureat"
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-physique-chimie-1995"))
        self.assertEqual(exercise.lesson.cursus.first().examen, Examen.BAC)


class ExamenMapBlancEtHarmoniseToleranceTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 5 fichiers (bac-d-ti-maths-2026-cameroun)
    portaient "examen": "bac_blanc" et 4 fichiers (terminale-c-maths-jean-tabi-2025-2026)
    "examen": "devoir_harmonise" - ni l'un ni l'autre n'est un niveau d'examen à part
    entière (voir Examen.choices) : le premier confond le niveau (BAC) avec le caractère
    non-officiel de l'épreuve (déjà porté par `origine`) ; le second désigne un devoir
    interne d'établissement dont le niveau réel, ici, est bien le BAC visé (coefficient/
    durée identiques, série renseignée) - voir catalog.ingestion.EXAMEN_MAP. Un premier
    essai avait mappé "devoir_harmonise" vers Examen.AUTRE comme "devoir surveille" (déjà
    présent dans EXAMEN_MAP), ce qui échoue systématiquement la résolution de Cursus :
    aucun Cursus n'est jamais seedé pour Examen.AUTRE (voir seed_country.py), quelle que
    soit la série."""

    def test_examen_map_tolerates_bac_blanc(self):
        from .ingestion import EXAMEN_MAP

        self.assertEqual(EXAMEN_MAP["bac_blanc"], Examen.BAC)
        self.assertEqual(EXAMEN_MAP["bac blanc"], Examen.BAC)

    def test_examen_map_resolves_devoir_harmonise_to_bac_not_autre(self):
        from .ingestion import EXAMEN_MAP

        self.assertEqual(EXAMEN_MAP["devoir_harmonise"], Examen.BAC)
        self.assertEqual(EXAMEN_MAP["devoir harmonise"], Examen.BAC)

    def test_ingest_exercise_accepts_bac_blanc(self):
        payload = _exercise_payload("bac-d-ti-maths-2026")
        payload["examen"] = "bac_blanc"
        payload["origine"] = "etablissement"
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-d-ti-maths-2026"))
        self.assertEqual(exercise.lesson.cursus.first().examen, Examen.BAC)

    def test_ingest_exercise_accepts_devoir_harmonise_and_resolves_a_cursus(self):
        payload = _exercise_payload("terminale-c-maths-jean-tabi-2025-2026")
        payload["examen"] = "devoir_harmonise"
        payload["origine"] = "etablissement"
        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/terminale-c-maths-jean-tabi-2025-2026"),
        )
        self.assertEqual(exercise.lesson.cursus.first().examen, Examen.BAC)


class QuestionNumeroWidthTests(TestCase):
    """Reproduit un blocage d'ingestion réel : "numero": "Présentation" (12 caractères,
    un item de barème récurrent - clarté/soin de la copie - sans rapport avec une
    sous-question numérotée) est apparu identique sur 3 lots d'épreuves de maths
    distincts (bac-c-maths-2026, bac-d-maths-2023, bepc-maths-2024-cameroun), ce qui
    dépassait Question.numero (CharField max_length=10 à l'époque) et levait un
    DataError Postgres ("value too long for type character varying(10)")."""

    def test_ingest_exercise_accepts_presentation_as_numero(self):
        payload = _exercise_payload("bac-maths-2026")
        payload["questions"] = [
            {"numero": "Présentation", "enonce_markdown": "Présentation.", "corrige_markdown": "Corrigé."},
        ]
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2026"))
        self.assertEqual(exercise.questions.get().numero, "Présentation")


class ContentPageCountryTests(TestCase):
    """Le visiteur d'une page de contenu doit voir le pays de CE contenu, pas celui
    qu'il navigue par ailleurs (voir Lesson/Cours.header_info) - dérivé de
    Subject.country, seule source toujours renseignée (contrairement à Cursus, vide
    pour un Cours "toutes séries")."""

    def setUp(self):
        self.sn = Country.objects.create(code="SN", label="Sénégal")
        self.subject = Subject.objects.create(country=self.sn, code="MATHS", label="Mathématiques")

    def test_lesson_header_info_exposes_subject_country(self):
        lesson = Lesson.objects.create(
            title="Test", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.assertEqual(lesson.header_info()["pays"], {"code": "SN", "label": "Sénégal"})

    def test_cours_header_info_exposes_subject_country_even_without_cursus(self):
        cours = Cours.objects.create(
            external_id="test-cours", titre="Test", subject=self.subject, statut=StatutContenu.VALIDE,
        )
        self.assertEqual(cours.cursus.count(), 0)
        self.assertEqual(cours.header_info()["pays"], {"code": "SN", "label": "Sénégal"})


class CoursPrerequisSectionTests(TestCase):
    """Section "prerequis" (mode cours) : chaque item dont le titre matche un Cours
    déjà validé devient un lien "(COURS_REF:<slug>)" - voir _render_cours_section."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.autre_cours = Cours.objects.create(
            external_id="autre-cours", titre="Calcul littéral", subject=subject, statut=StatutContenu.VALIDE,
        )
        self.cours = Cours.objects.create(external_id="test-prerequis", titre="Test", subject=subject)

    def test_matching_item_links_to_the_cours_slug_not_its_numeric_id(self):
        self.cours.sections_raw = [{"type": "prerequis", "items": ["Calcul littéral"]}]
        rendered = self.cours._render_section(self.cours.sections_raw[0])

        self.assertIn(f"(COURS_REF:{self.autre_cours.slug})", rendered)
        self.assertNotIn(f"(COURS_REF:{self.autre_cours.id})", rendered)

    def test_items_markdown_key_is_accepted_as_a_fallback_for_items(self):
        # Constaté sur 638 Cours du corpus : la compétence utilise parfois le nom de
        # champ de la section synthese ("items_markdown") au lieu de "items" pour
        # prerequis - sans ce repli, la section reste vide (voir aussi
        # CoursSectionsBreakdownTests.test_prerequis_accepts_items_markdown_fallback
        # pour la version structurée).
        self.cours.sections_raw = [{"type": "prerequis", "items_markdown": ["Calcul littéral"]}]
        rendered = self.cours._render_section(self.cours.sections_raw[0])

        self.assertIn(f"(COURS_REF:{self.autre_cours.slug})", rendered)


class CoursExercicesApplicationSectionTests(TestCase):
    """Section 6 (mode cours) : correction-experte peut produire soit un exercice à
    bloc unique (`enonce_markdown`/`solution_markdown`), soit - pour un exercice à
    sous-questions - `enonce_intro_markdown` + `questions[]`, même convention que la
    Question du corrigé d'épreuve (voir Exercise.compile_from_questions)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(external_id="test-section-6", titre="Test", subject=subject)

    def _render(self, item):
        self.cours.sections_raw = [{"type": "exercices_application", "items": [item]}]
        return self.cours._render_section(self.cours.sections_raw[0])

    def test_flat_item_still_renders_as_before(self):
        rendered = self._render({
            "numero": 1, "difficulte": "facile",
            "enonce_markdown": "Résoudre l'équation.", "solution_markdown": "x = 2.",
        })
        self.assertIn("Résoudre l'équation.", rendered)
        self.assertIn("x = 2.", rendered)

    def test_item_with_sub_questions_renders_intro_and_each_question(self):
        rendered = self._render({
            "numero": 2, "difficulte": "moyen",
            "enonce_intro_markdown": "Soit f(x) = x^2.",
            "questions": [
                {"numero": "a", "enonce_markdown": "Calculer f'(x).", "solution_markdown": "f'(x) = 2x."},
                {"numero": "b", "enonce_markdown": "Résoudre f'(x) = 0.", "solution_markdown": "x = 0."},
            ],
        })
        self.assertIn("Soit f(x) = x^2.", rendered)
        self.assertIn("Calculer f'(x).", rendered)
        self.assertIn("Résoudre f'(x) = 0.", rendered)
        self.assertIn("f'(x) = 2x.", rendered)
        self.assertIn("x = 0.", rendered)

    def test_sub_question_accepts_corrige_markdown_as_alias_for_solution(self):
        rendered = self._render({
            "numero": 3, "difficulte": "approfondissement",
            "questions": [{"numero": "a", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé via alias."}],
        })
        self.assertIn("Corrigé via alias.", rendered)

    def test_bare_string_item_renders_without_crashing(self):
        # Reproduit bac-c-d-chimie-1999/2000/2001/2002-cameroun (et une centaine
        # d'autres Cours du corpus) : "items" est une liste de chaînes nues (l'énoncé
        # seul, sans numero/difficulte/solution) plutôt que d'objets structurés -
        # `item.get(...)` levait AttributeError: 'str' object has no attribute 'get'.
        rendered = self._render("Comparer, dans un tableau, deux méthodes de calcul.")
        self.assertIn("Comparer, dans un tableau, deux méthodes de calcul.", rendered)
        # Pas de solution fournie pour cette forme : pas de toggle vide.
        self.assertNotIn("### Solution", rendered)


class CoursExempleResoluSectionTests(TestCase):
    """Section "exemple_resolu" (mode cours) : "etapes" est parfois une liste de
    chaînes nues plutôt que d'objets {numero, action, justification,
    resultat_markdown}, constaté sur bac-c-d-chimie-1999-cameroun - même tolérance
    texte-brut que pour les autres sections (voir CoursErreursClassiquesSectionTests)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(external_id="test-exemple-resolu", titre="Test", subject=subject)

    def _render(self, etapes):
        section = {"type": "exemple_resolu", "enonce_markdown": "Énoncé.", "etapes": etapes}
        return self.cours._render_section(section)

    def test_structured_etape_still_renders_as_before(self):
        rendered = self._render([{"numero": 1, "action": "Identifier", "justification": "Car X."}])
        self.assertIn("**Étape 1 - Identifier**", rendered)
        self.assertIn("Car X.", rendered)

    def test_bare_string_etape_renders_without_crashing(self):
        rendered = self._render(["Identifier le caractère amphotère de l'aluminium."])
        self.assertIn("Identifier le caractère amphotère de l'aluminium.", rendered)


class CoursErreursClassiquesSectionTests(TestCase):
    """Section "erreurs_classiques" (mode cours) : même tolérance texte-brut que
    "exercices_application" (voir CoursExercicesApplicationSectionTests) - un item peut
    être un objet {erreur_markdown, pourquoi_faux, correction_markdown} ou une simple
    chaîne, constaté sur bac-c-d-chimie-1999/2000/2001/2002-cameroun."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(external_id="test-erreurs-classiques", titre="Test", subject=subject)

    def _render(self, item):
        section = {"type": "erreurs_classiques", "items": [item]}
        return self.cours._render_section(section)

    def test_structured_item_still_renders_as_before(self):
        rendered = self._render({
            "erreur_markdown": "Confondre A et B.",
            "pourquoi_faux": "Ce sont deux notions distinctes.",
            "correction_markdown": "Bien distinguer A de B.",
        })
        self.assertIn("Confondre A et B.", rendered)
        self.assertIn("Ce sont deux notions distinctes.", rendered)
        self.assertIn("Bien distinguer A de B.", rendered)

    def test_bare_string_item_renders_without_crashing(self):
        rendered = self._render("Confondre saponification et hydrolyse acide d'un ester.")
        self.assertIn("Confondre saponification et hydrolyse acide d'un ester.", rendered)


class CoursSectionsBreakdownTests(TestCase):
    """cours_sections_breakdown() - version structurée (dicts) des sections, pour la
    lecture en ligne (voir CoursReaderPage) - même tolérance str-vs-objet que
    _render_cours_section, testée séparément ci-dessus, mais des dicts en sortie plutôt
    que du Markdown concaténé."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(external_id="test-breakdown", titre="Test", subject=subject)

    def _breakdown(self, section, allowed_types=None):
        self.cours.sections_raw = [section]
        return cours_sections_breakdown(self.cours, allowed_types=allowed_types)

    def test_accroche_returns_body(self):
        result = self._breakdown({"type": "accroche", "contenu_markdown": "Une accroche."})
        self.assertEqual(result, [{"type": "accroche", "body_markdown": "Une accroche."}])

    def test_empty_accroche_is_excluded(self):
        result = self._breakdown({"type": "accroche", "contenu_markdown": ""})
        self.assertEqual(result, [])

    def test_prerequis_links_matching_cours_by_slug(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        autre = Cours.objects.create(
            external_id="test-breakdown-autre", titre="Calcul littéral", subject=subject,
            statut=StatutContenu.VALIDE,
        )
        result = self._breakdown({"type": "prerequis", "items": ["Calcul littéral", "Notion inconnue"]})
        self.assertEqual(result, [{
            "type": "prerequis",
            "items": [
                {"label": "Calcul littéral", "cours_slug": autre.slug},
                {"label": "Notion inconnue", "cours_slug": None},
            ],
        }])

    def test_prerequis_accepts_items_markdown_fallback(self):
        # Voir CoursPrerequisSectionTests.test_items_markdown_key_is_accepted_as_a_fallback_for_items -
        # même repli côté rendu structuré.
        result = self._breakdown({"type": "prerequis", "items_markdown": ["Notion X"]})
        self.assertEqual(result, [{"type": "prerequis", "items": [{"label": "Notion X", "cours_slug": None}]}])

    def test_regle_structures_formule_and_variantes(self):
        result = self._breakdown({
            "type": "regle", "titre": "La règle des signes", "contenu_markdown": "Corps.",
            "formule_principale": "a \\times b", "variantes": [
                {"nom": "Cas positif", "quand_utiliser": "a>0", "contenu_markdown": "Reste positif."},
                "x < 0",
            ],
        })
        self.assertEqual(result, [{
            "type": "regle",
            "titre": "La règle des signes",
            "body_markdown": "Corps.",
            "formule_markdown": "$$a \\times b$$",
            "variantes": [
                {"nom": "Cas positif", "quand_utiliser": "a>0", "body_markdown": "Reste positif."},
                {"nom": None, "quand_utiliser": None, "body_markdown": "$$x < 0$$"},
            ],
        }])

    def test_regle_without_formula_keeps_formule_markdown_none(self):
        result = self._breakdown({"type": "regle", "contenu_markdown": "Corps seul."})
        self.assertIsNone(result[0]["formule_markdown"])
        self.assertEqual(result[0]["titre"], "La règle")

    def test_exemple_resolu_structures_steps_and_tolerates_bare_strings(self):
        result = self._breakdown({
            "type": "exemple_resolu", "enonce_markdown": "Énoncé.",
            "etapes": [
                {"numero": 1, "action": "Identifier", "justification": "Car X.", "resultat_markdown": "y=1."},
                "Étape en texte libre.",
            ],
            "conclusion_markdown": "Donc voilà.",
        })
        self.assertEqual(result, [{
            "type": "exemple_resolu",
            "enonce_markdown": "Énoncé.",
            "etapes": [
                {"numero": 1, "action": "Identifier", "justification": "Car X.", "resultat_markdown": "y=1.", "body_markdown": None},
                {"numero": None, "action": None, "justification": None, "resultat_markdown": None, "body_markdown": "Étape en texte libre."},
            ],
            "conclusion_markdown": "Donc voilà.",
        }])

    def test_erreurs_classiques_structures_items_and_tolerates_bare_strings(self):
        result = self._breakdown({
            "type": "erreurs_classiques", "items": [
                {"erreur_markdown": "Confondre A et B.", "pourquoi_faux": "Distincts.", "correction_markdown": "Corriger."},
                "Erreur en texte libre.",
            ],
        })
        self.assertEqual(result, [{
            "type": "erreurs_classiques",
            "items": [
                {"erreur_markdown": "Confondre A et B.", "pourquoi_faux": "Distincts.", "correction_markdown": "Corriger."},
                {"erreur_markdown": "Erreur en texte libre.", "pourquoi_faux": None, "correction_markdown": None},
            ],
        }])

    def test_exercices_application_structures_items_with_sub_questions(self):
        result = self._breakdown({
            "type": "exercices_application", "items": [
                {
                    "numero": 1, "difficulte": "moyen", "enonce_intro_markdown": "Soit f(x) = x^2.",
                    "questions": [
                        {"numero": "a", "enonce_markdown": "Calculer f'(x).", "solution_markdown": "f'(x) = 2x."},
                    ],
                },
                "Énoncé nu, sans solution fournie.",
            ],
        })
        self.assertEqual(result[0]["type"], "exercices_application")
        first, second = result[0]["items"]
        self.assertEqual(first["numero"], 1)
        self.assertEqual(first["difficulte"], "moyen")
        self.assertIn("Soit f(x) = x^2.", first["enonce_markdown"])
        self.assertIn("Calculer f'(x).", first["enonce_markdown"])
        self.assertEqual(first["solution_markdown"], "f'(x) = 2x.")
        self.assertEqual(second, {
            "numero": None, "difficulte": None,
            "enonce_markdown": "Énoncé nu, sans solution fournie.", "solution_markdown": None,
        })

    def test_synthese_joins_bullet_list(self):
        result = self._breakdown({"type": "synthese", "items_markdown": ["Point A.", "Point B."]})
        self.assertEqual(result, [{"type": "synthese", "body_markdown": "- Point A.\n- Point B."}])

    def test_synthese_keeps_prose_string_as_is(self):
        result = self._breakdown({"type": "synthese", "items_markdown": "Déjà rédigé en prose."})
        self.assertEqual(result, [{"type": "synthese", "body_markdown": "Déjà rédigé en prose."}])

    def test_empty_synthese_is_excluded(self):
        result = self._breakdown({"type": "synthese", "items_markdown": []})
        self.assertEqual(result, [])

    def test_allowed_types_filters_before_building(self):
        self.cours.sections_raw = [
            {"type": "accroche", "contenu_markdown": "Accroche."},
            {"type": "regle", "contenu_markdown": "Règle."},
            {"type": "synthese", "items_markdown": "Retenir."},
        ]
        result = cours_sections_breakdown(self.cours, allowed_types={"accroche", "regle"})
        self.assertEqual([s["type"] for s in result], ["accroche", "regle"])


class IngestCoursRappelsLiesTests(TestCase):
    """`source.rappels_lies` (mode cours, SKILL.md) : d'autres rappels déjà ingérés,
    de la même épreuve, que ce même cours couvre aussi - cas du mode interactif où
    plusieurs blocs "### Rappel de méthode" fournis ensemble donnent lieu à un seul
    cours (le mode automatisation produit toujours un rappel par fichier cours, donc
    une liste vide). Voir catalog.ingestion._link_rappels_lies."""

    def setUp(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-a", "competence": "Notion A", "contenu_markdown": "Contenu A."},
            {"id": "rdm-b", "competence": "Notion B", "contenu_markdown": "Contenu B."},
        ]
        self.exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def _cours_payload(self, cours_id="cours-test", rappel_id="rdm-a", rappels_lies=None):
        return {
            "cours_id": cours_id,
            "meta": {"titre": "Cours de test", "matiere": "Mathematiques"},
            "source": {"rappel_id": rappel_id, "rappels_lies": rappels_lies or []},
            "sections": [],
        }

    def test_links_the_primary_rappel(self):
        cours, created = ingest_cours(self._cours_payload())
        self.assertTrue(created)
        rappel_a = self.exercise.rappels_de_methode.get(external_id="rdm-a")
        self.assertEqual(rappel_a.cours_id, cours.id)

    def test_also_links_rappels_lies(self):
        cours, _ = ingest_cours(self._cours_payload(rappels_lies=["rdm-b"]))
        rappel_b = self.exercise.rappels_de_methode.get(external_id="rdm-b")
        self.assertEqual(rappel_b.cours_id, cours.id)

    def test_does_not_fail_on_an_unknown_linked_rappel(self):
        cours, created = ingest_cours(self._cours_payload(rappels_lies=["rdm-does-not-exist"]))
        self.assertTrue(created)

    def test_links_rappels_lies_on_the_duplicate_title_path_too(self):
        ingest_cours(self._cours_payload())

        payload = _exercise_payload("bac-maths-2025")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-c", "competence": "Notion A bis", "contenu_markdown": "Contenu C."},
            {"id": "rdm-d", "competence": "Notion D", "contenu_markdown": "Contenu D."},
        ]
        other_exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2025"))

        # Même titre que le premier cours ("Cours de test") : dédoublonnage attendu -
        # rappels_lies doit quand même être rattaché au Cours existant.
        cours, created = ingest_cours(
            self._cours_payload(cours_id="cours-test-doublon", rappel_id="rdm-c", rappels_lies=["rdm-d"]),
        )
        self.assertFalse(created)
        rappel_d = other_exercise.rappels_de_methode.get(external_id="rdm-d")
        self.assertEqual(rappel_d.cours_id, cours.id)


class RepairDictShapedCoursSectionsTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 124 fichiers cours (bac-c-maths-1985/
    1986/1991/1992/blanc-2003-cameroun) portaient `sections` comme un DICT à clés
    fixes ("accroche", "regle", ...) plutôt que la forme LISTE de blocs {"type": ...}
    attendue partout ailleurs dans le corpus - `for section in cours.sections_raw:
    section.get("type")` itère alors les CLÉS du dict (des chaînes), levant
    `AttributeError: 'str' object has no attribute 'get'` sur les 124 fichiers. Voir
    catalog.ingestion_repairs._repair_dict_shaped_cours_sections."""

    def _cours_payload(self, sections_dict):
        return {
            "cours_id": "cours-dict-shape-test",
            "meta": {"titre": "Cours dict-shape", "matiere": "Mathematiques"},
            "source": {"rappel_id": "rdm-dict-shape"},
            "sections": sections_dict,
        }

    def setUp(self):
        payload = _exercise_payload("bac-maths-1985")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-dict-shape", "competence": "Notion", "contenu_markdown": "Contenu."},
        ]
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-1985"))

    def test_ingest_cours_accepts_dict_shaped_sections_without_crashing(self):
        cours, created = ingest_cours(self._cours_payload({
            "accroche": "Phrase d'accroche.",
            "prerequis": ["Prérequis 1", "Prérequis 2"],
            "regle": {"titre": "La règle", "contenu_markdown": "Contenu de la règle."},
            "exemple_resolu": {"enonce_markdown": "Énoncé.", "etapes": [], "conclusion_markdown": "Conclusion."},
            "erreurs_classiques": [{"erreur_markdown": "Une erreur.", "pourquoi_faux": "Car.", "correction_markdown": "Corrigé."}],
            "exercices_application": [{"numero": 1, "difficulte": "facile", "enonce_markdown": "Énoncé.", "solution_markdown": "Solution."}],
            "synthese": "Une phrase de synthèse.",
        }))
        self.assertTrue(created)
        self.assertIn("Phrase d'accroche.", cours.content_markdown)
        self.assertIn("Prérequis 1", cours.content_markdown)
        self.assertIn("Contenu de la règle.", cours.content_markdown)
        self.assertIn("Une phrase de synthèse.", cours.content_markdown)

    def test_list_shaped_sections_are_left_untouched(self):
        list_sections = [{"type": "accroche", "contenu_markdown": "Déjà la bonne forme."}]
        cours, created = ingest_cours(self._cours_payload(list_sections))
        self.assertTrue(created)
        self.assertIn("Déjà la bonne forme.", cours.content_markdown)


class CoursSiblingRappelIdMapFilenameToleranceTests(TestCase):
    """`_cours_sibling_rappel_id_map` (filet de secours id manquant + cours_id, voir
    IngestCoursRappelsLiesTests) ne doit dépendre d'aucune convention de nommage -
    repéré sur bac-c-maths-1985/1986/1991/1992/blanc-2003-cameroun (124 fichiers) qui
    utilisent `<epreuve>_cours-<slug>.json` (tiret) plutôt que `<epreuve>_cours_<slug>.json`
    (underscore, la convention majoritaire) - l'ancien glob `*_cours_*.json` manquait
    ces fichiers entièrement."""

    def test_recovers_id_from_a_hyphen_named_cours_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-1985"
            source_dir.mkdir(parents=True)
            (source_dir / "bac-maths-1985_cours-slug-with-hyphen.json").write_text(
                json.dumps({
                    "cours_id": "cours-slug-with-hyphen",
                    "source": {"rappel_id": "rdm-recovered-via-hyphen-filename"},
                }),
                encoding="utf-8",
            )

            payload = _exercise_payload("bac-maths-1985")
            payload["questions"][0]["rappels_de_methode"] = [
                {"cours_id": "cours-slug-with-hyphen", "texte": "Contenu du rappel."},
            ]
            exercise, _ = ingest_exercise(payload, source_dir=source_dir)
            rappel = exercise.rappels_de_methode.get()
            self.assertEqual(rappel.external_id, "rdm-recovered-via-hyphen-filename")

    def test_falls_back_to_texte_when_contenu_markdown_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-1986"
            source_dir.mkdir(parents=True)
            payload = _exercise_payload("bac-maths-1986")
            payload["questions"][0]["rappels_de_methode"] = [
                {"id": "rdm-texte-shape", "cours_id": None, "texte": "Contenu porté par 'texte', pas 'contenu_markdown'."},
            ]
            exercise, _ = ingest_exercise(payload, source_dir=source_dir)
            rappel = exercise.rappels_de_methode.get(external_id="rdm-texte-shape")
            self.assertEqual(rappel.contenu_markdown, "Contenu porté par 'texte', pas 'contenu_markdown'.")


class IngestCoursSameExternalIdAcrossEpreuvesTests(TestCase):
    """`cours_id` est déterministe, dérivé de la seule compétence/niveau (voir
    SKILL.md) - jamais de l'épreuve source. Deux épreuves distinctes couvrant la
    même compétence produisent donc légitimement le même `cours_id` : ce n'est pas
    seulement une ré-ingestion du même fichier. Constaté en production sur deux
    épreuves d'Informatique BAC C 2022/2023 partageant plusieurs compétences avec
    une épreuve 2024 déjà ingérée - le fast-path `external_id` existant retournait
    le Cours déjà en base sans jamais rattacher le NOUVEAU rappel, le laissant
    orphelin (cours_genere jamais mis à true) malgré 0 erreur d'ingestion."""

    def setUp(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-a", "competence": "Notion A", "contenu_markdown": "Contenu A."},
        ]
        self.exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def _cours_payload(self, rappel_id):
        return {
            "cours_id": "cours-meme-id-partout",
            "meta": {"titre": "Cours de test", "matiere": "Mathematiques"},
            "source": {"rappel_id": rappel_id},
            "sections": [],
        }

    def test_second_epreuve_reusing_the_same_cours_id_still_links_its_rappel(self):
        first_cours, first_created = ingest_cours(self._cours_payload("rdm-a"))
        self.assertTrue(first_created)

        payload = _exercise_payload("bac-maths-2025")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-b", "competence": "Notion A", "contenu_markdown": "Contenu A."},
        ]
        other_exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2025"))

        second_cours, second_created = ingest_cours(self._cours_payload("rdm-b"))

        self.assertFalse(second_created)
        self.assertEqual(second_cours.id, first_cours.id)
        rappel_b = other_exercise.rappels_de_methode.get(external_id="rdm-b")
        self.assertEqual(rappel_b.cours_id, first_cours.id)

    def test_tolerates_a_missing_or_already_stale_rappel_id(self):
        ingest_cours(self._cours_payload("rdm-a"))

        cours, created = ingest_cours(self._cours_payload("rdm-does-not-exist"))

        self.assertFalse(created)
        self.assertEqual(cours.titre, "Cours de test")


class CoursPaysFieldToleranceTests(TestCase):
    """Même champ `pays` que côté exercice (voir PaysFieldToleranceTests), mais dans
    `meta` pour un cours - voir catalog.ingestion._validate_pays_matches_country. Le
    pays d'un cours est toujours hérité de l'épreuve source (rappel.exercise.lesson),
    jamais lu depuis meta.pays lui-même - ce champ ne sert qu'au contrôle."""

    def setUp(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-a", "competence": "Notion A", "contenu_markdown": "Contenu A."},
        ]
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def _cours_payload(self, pays=None):
        meta = {"titre": "Cours de test", "matiere": "Mathematiques"}
        if pays is not None:
            meta["pays"] = pays
        return {
            "cours_id": "cours-test",
            "meta": meta,
            "source": {"rappel_id": "rdm-a", "rappels_lies": []},
            "sections": [],
        }

    def test_accepts_a_pays_matching_the_source_exercises_country(self):
        cours, created = ingest_cours(self._cours_payload(pays="cm"))
        self.assertTrue(created)

    def test_still_works_when_pays_is_absent(self):
        cours, created = ingest_cours(self._cours_payload())
        self.assertTrue(created)

    def test_rejects_a_pays_contradicting_the_source_exercises_country(self):
        with self.assertRaises(IngestionError):
            ingest_cours(self._cours_payload(pays="sn"))


class RappelIdRecoveryFromCoursSiblingTests(TestCase):
    """Reproduit un blocage d'ingestion réel, rencontré à deux reprises (8 fichiers
    bac-c-e-physique-2014/2015-cameroun, puis 28 fichiers bac-c(-e)-physique-2017 à
    2022-cameroun) : une entrée `rappels_de_methode` perdait son `id` requis et ne
    portait plus que `cours_id` (bookkeeping interne à la compétence, jamais lu par
    ailleurs) - `KeyError` puis, en cascade, `RappelDeMethode introuvable` sur chaque
    cours dérivé de cet exercice. Voir catalog.ingestion._cours_sibling_rappel_id_map."""

    def test_recovers_id_from_a_sibling_cours_file_with_matching_cours_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-physique-2019"
            source_dir.mkdir(parents=True)
            (source_dir / "bac-physique-2019_cours_test.json").write_text(
                json.dumps({
                    "cours_id": "cours-test",
                    "meta": {"titre": "Cours de test", "matiere": "Physique"},
                    "source": {"rappel_id": "rdm-recovered-1", "rappels_lies": []},
                    "sections": [],
                }),
                encoding="utf-8",
            )

            payload = _exercise_payload("bac-physique-2019")
            payload["questions"][0]["rappels_de_methode"] = [
                {"cours_id": "cours-test", "contenu_markdown": "Contenu."},
            ]
            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        rappel = exercise.rappels_de_methode.get(external_id="rdm-recovered-1")
        self.assertEqual(rappel.contenu_markdown, "Contenu.")

    def test_raises_a_clear_error_when_cours_id_has_no_matching_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-physique-2019"
            source_dir.mkdir(parents=True)

            payload = _exercise_payload("bac-physique-2019")
            payload["questions"][0]["rappels_de_methode"] = [
                {"cours_id": "cours-does-not-exist", "contenu_markdown": "Contenu."},
            ]
            with self.assertRaises(IngestionError):
                ingest_exercise(payload, source_dir=source_dir)


class SitemapCountryFanOutTests(TestCase):
    """`/{code}` et `/{code}/cours` doivent apparaître une fois par pays - voir
    catalog.sitemap._PER_COUNTRY_PAGES."""

    def setUp(self):
        Country.objects.create(code="BJ", label="Bénin")

    def test_sitemap_lists_catalogue_and_cours_pages_for_every_country(self):
        from django.conf import settings

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        base = settings.FRONTEND_URL
        for code in ["cm", "bj"]:
            self.assertIn(f"<loc>{base}/{code}</loc>", xml)
            self.assertIn(f"<loc>{base}/{code}/cours</loc>", xml)

    def test_sitemap_prefixes_lesson_urls_with_their_country(self):
        # Reco d'audit UX : une fiche Lesson doit être indexée sous /{pays}/epreuves/...,
        # pas à une URL plate - voir catalog.sitemap._all_entries.
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Sitemap CM", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)

        from django.conf import settings

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        base = settings.FRONTEND_URL
        self.assertIn(f"<loc>{base}/cm/epreuves/{lesson.slug}</loc>", xml)

    def test_sitemap_prefixes_epreuve_inedite_urls_with_their_country(self):
        # Même reco que pour Lesson ci-dessus, désormais possible depuis qu'EpreuveInedite
        # a un slug (voir EpreuveInedite.slug) - voir catalog.sitemap._all_entries.
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        blueprint = Blueprint.objects.create(subject=subject, titre="BP Sitemap", statut=StatutContenu.VALIDE)
        blueprint.cursus.set([cursus])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=subject, titre="Sitemap Inédite CM", statut=StatutContenu.VALIDE,
        )
        epreuve.cursus.set([cursus])

        from django.conf import settings

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        base = settings.FRONTEND_URL
        self.assertIn(f"<loc>{base}/cm/epreuves-inedites/{epreuve.slug}</loc>", xml)

    def test_sitemap_lists_epreuve_common_to_multiple_series_only_once(self):
        """Régression : cursus__country__actif traverse le M2M EpreuveInedite.cursus -
        sans distinct(), une épreuve commune à 2 séries produisait 2 <url> identiques."""
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus_c = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        cursus_d = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        blueprint = Blueprint.objects.create(subject=subject, titre="BP Sitemap Multi", statut=StatutContenu.VALIDE)
        blueprint.cursus.set([cursus_c, cursus_d])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=subject, titre="Sitemap Inédite Multi", statut=StatutContenu.VALIDE,
        )
        epreuve.cursus.set([cursus_c, cursus_d])

        from django.conf import settings

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        base = settings.FRONTEND_URL
        self.assertEqual(xml.count(f"<loc>{base}/cm/epreuves-inedites/{epreuve.slug}</loc>"), 1)

    def test_sitemap_excludes_brouillon_epreuve_inedite(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        blueprint = Blueprint.objects.create(subject=subject, titre="BP Brouillon", statut=StatutContenu.VALIDE)
        blueprint.cursus.set([cursus])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=subject, titre="Brouillon Inédite CM", statut=StatutContenu.BROUILLON,
        )
        epreuve.cursus.set([cursus])

        response = self.client.get(reverse("sitemap-chunk", args=[1]))
        xml = response.content.decode()
        self.assertNotIn(f"/epreuves-inedites/{epreuve.slug}", xml)


class SujetPdfTemplateTests(TestCase):
    """
    `_render_html` (l'étape Django avant que Playwright ne transforme le HTML en PDF)
    doit au moins parser sans lever de TemplateSyntaxError - régression : un
    `{{ Edukora Africa }}` corrompu (un `{{ site_name }}` cassé par un renommage du
    site, probablement un remplacement automatique malheureux) a fait échouer toute
    génération de PDF en silence pour l'utilisateur (l'erreur n'apparaissait que dans
    logs/sujet_pdf_generation.log) - voir catalog/templates/catalog/sujet_pdf_template.html.
    Ne nécessite pas Chromium/Playwright : seul le rendu Django est vérifié ici.
    """

    def test_render_html_does_not_raise_template_syntax_error(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Sujet de test", subject=subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="Contenu de test.",
        )
        lesson.cursus.add(cursus)

        html = _render_html(lesson)

        self.assertIn("Sujet de test", html)
        self.assertIn("Contenu de test.", html)


class SujetPdfFilenamePrefixTests(TestCase):
    """sujet_pdf_filename() préfixe le nom de fichier par le code pays (même
    convention que ingest/<code_pays>/...) - décision utilisateur du 2026-08-03 :
    sans lui, deux pays partageant le même titre d'épreuve (ex. "Mathématiques BAC A
    2016") produiraient le même nom de fichier dans le dossier plat sujets_pdf/, le
    second écrasant silencieusement le PDF du premier."""

    def test_filename_is_prefixed_by_lowercase_country_code(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        lesson = Lesson.objects.create(
            title="Mathématiques BAC A 2016", subject=subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )

        self.assertEqual(sujet_pdf_filename(lesson), "cm/mathematiques-bac-a-2016-sujet.pdf")

    def test_two_countries_sharing_a_title_get_distinct_filenames(self):
        bj = Country.objects.create(code="BJ", label="Bénin")
        bj_subject = Subject.objects.create(country=bj, code="MATHS", label="Mathématiques")
        cm_subject = Subject.objects.get(country__code="CM", code="MATHS")

        cm_lesson = Lesson.objects.create(
            title="Mathématiques BAC A 2016", subject=cm_subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )
        bj_lesson = Lesson.objects.create(
            title="Mathématiques BAC A 2016", subject=bj_subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )

        self.assertNotEqual(sujet_pdf_filename(cm_lesson), sujet_pdf_filename(bj_lesson))


class SaveSujetPdfOverwriteTests(TestCase):
    """save_sujet_pdf() régénère un PDF sur le même nom de fichier déterministe
    (voir sujet_pdf_filename) - sans suppression explicite de l'ancien fichier au
    préalable, FieldFile.save() ne l'écrase jamais : le storage lui trouve un nom
    disponible différent (suffixe aléatoire) et l'ancien PDF reste orphelin à chaque
    régénération (ex. après correction du contenu, action admin "Générer le PDF du
    sujet" relancée sur une leçon déjà pourvue)."""

    def test_regenerating_overwrites_the_same_path_without_orphaning_the_old_file(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Sujet de test", subject=subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="Contenu de test.",
        )
        lesson.cursus.add(cursus)

        with tempfile.TemporaryDirectory() as tmp, override_settings(MEDIA_ROOT=tmp):
            with patch("catalog.sujet_pdf.generate_sujet_pdf", return_value=b"pdf-v1"):
                save_sujet_pdf(lesson)
            first_path = lesson.sujet_pdf.name
            self.assertTrue(default_storage.exists(first_path))

            with patch("catalog.sujet_pdf.generate_sujet_pdf", return_value=b"pdf-v2"):
                save_sujet_pdf(lesson)
            second_path = lesson.sujet_pdf.name

            self.assertEqual(first_path, second_path, "Un nom différent signale que l'ancien fichier n'a pas été supprimé avant la réécriture.")
            with default_storage.open(second_path, "rb") as f:
                self.assertEqual(f.read(), b"pdf-v2")


class FigureUploadToPrefixTests(TestCase):
    """figure_upload_to() préfixe le nom de fichier par le code pays, même convention
    et même raison que SujetPdfFilenamePrefixTests ci-dessus : le nom de fichier
    original d'une figure (souvent générique, ex. "figure1.png", livré tel quel par
    correction-experte) peut coïncider entre deux pays sans rapport, le second
    écrasant alors silencieusement l'image du premier dans le dossier plat figures/."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.exercise = Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)

    def test_path_is_prefixed_by_lowercase_country_code(self):
        figure = Figure(exercise=self.exercise, external_id="fig-1")
        self.assertEqual(figure_upload_to(figure, "figure1.png"), "figures/cm/figure1.png")

    def test_two_countries_sharing_a_filename_get_distinct_paths(self):
        bj = Country.objects.create(code="BJ", label="Bénin")
        bj_subject = Subject.objects.create(country=bj, code="MATHS", label="Mathématiques")
        bj_lesson = Lesson.objects.create(
            title="Test BJ", subject=bj_subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        bj_exercise = Exercise.objects.create(lesson=bj_lesson, numero_exercice="1", statut=StatutContenu.VALIDE)

        cm_figure = Figure(exercise=self.exercise, external_id="fig-1")
        bj_figure = Figure(exercise=bj_exercise, external_id="fig-1")

        self.assertNotEqual(
            figure_upload_to(cm_figure, "figure1.png"), figure_upload_to(bj_figure, "figure1.png"),
        )


class QuestionModelTests(TestCase):
    """Question est l'unité atomique de correction (voir catalog.models.Question) -
    un Exercise peut en avoir plusieurs, chacune notée/thématisée indépendamment."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Test", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.exercise = Exercise.objects.create(lesson=self.lesson, numero_exercice="1", statut=StatutContenu.VALIDE)

    def test_unique_numero_per_exercise(self):
        Question.objects.create(exercise=self.exercise, numero="1", ordre=1, enonce_markdown="a", corrige_markdown="b")
        with self.assertRaises(Exception):
            Question.objects.create(exercise=self.exercise, numero="1", ordre=2, enonce_markdown="c", corrige_markdown="d")

    def test_compile_from_questions_concatenates_in_order_and_rolls_up_themes(self):
        derivation = Question.objects.create(
            exercise=self.exercise, numero="2", ordre=2,
            enonce_markdown="Calculer la derivee.", corrige_markdown="f'(x) = 2x.",
        )
        limite = Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="Calculer la limite.", corrige_markdown="La limite vaut 0.",
        )
        theme_deriv = Tag.objects.create(name="derivation")
        theme_limite = Tag.objects.create(name="limites")
        derivation.themes.add(theme_deriv)
        limite.themes.add(theme_limite)
        self.exercise.enonce_intro_markdown = "Etudier la fonction f."

        self.exercise.compile_from_questions()

        self.assertTrue(self.exercise.enonce_markdown.startswith("Etudier la fonction f."))
        # ordre=1 (limite) doit preceder ordre=2 (derivation), pas l'ordre de creation.
        self.assertLess(
            self.exercise.enonce_markdown.index("Calculer la limite."),
            self.exercise.enonce_markdown.index("Calculer la derivee."),
        )
        self.assertIn("f'(x) = 2x.", self.exercise.corrige_markdown)
        self.assertEqual(set(self.exercise.themes.values_list("name", flat=True)), {"derivation", "limites"})

    def test_compile_from_questions_renders_numero_and_choix_for_qcm(self):
        """La lecture d'épreuve (hors Quiz) ne dispose que du texte compilé - le
        numéro et les options d'un QCM doivent donc y être réinjectés depuis les
        champs structurés (Question.numero, Question.choix), sinon un lecteur ne
        voit jamais quelles options existaient avant que le corrigé ne révèle la
        bonne réponse (voir bac-a-maths-2008-cameroun_exercice_2, cas réel signalé)."""
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="Calculer la limite.", corrige_markdown="0.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="2", ordre=2,
            enonce_markdown="2x est la derivee de :", corrige_markdown="La bonne reponse est b) x^2.",
            type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "x"}, {"lettre": "b", "texte": "x^2"}],
            reponse_correcte="b",
        )

        self.exercise.compile_from_questions()

        self.assertIn("**1.** Calculer la limite.", self.exercise.enonce_markdown)
        self.assertIn("**2.** 2x est la derivee de :", self.exercise.enonce_markdown)
        self.assertIn("a) x", self.exercise.enonce_markdown)
        self.assertIn("b) x^2", self.exercise.enonce_markdown)

    def test_compile_from_questions_omits_numero_for_single_question_exercise(self):
        """Un exercice à une seule sous-question (le cas le plus courant) n'a rien à
        distinguer d'un autre - lui ajouter un numéro serait un bruit visuel inutile."""
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="Calculer f'(x).", corrige_markdown="2x.",
        )

        self.exercise.compile_from_questions()

        self.assertEqual(self.exercise.enonce_markdown, "Calculer f'(x).")

    def test_compile_from_questions_skips_numero_prefix_when_already_labeled(self):
        """Une sous-question qui transcrit déjà son propre repère (numérotation
        d'origine, lettre, titre de Partie...) ne doit pas en recevoir un second par
        dessus - sinon un exercice à Parties nommées afficherait "**A.1.** **Partie
        A**" ou "**A.2.** 2. Déduire..." (cas réel signalé sur
        bac-a-maths-2015-cameroun_exercice_1)."""
        Question.objects.create(
            exercise=self.exercise, numero="A.1", ordre=1,
            enonce_markdown="**Partie A**\n\n1. Résoudre le système.", corrige_markdown="S = {...}.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="A.2", ordre=2,
            enonce_markdown="2. Déduire de la question précédente.", corrige_markdown="S = {...}.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="B.1", ordre=3,
            enonce_markdown="**Partie B.** Une urne contient...\n\nA : « obtenir deux boules rouges ».",
            corrige_markdown="P(A) = ...",
        )

        self.exercise.compile_from_questions()

        self.assertIn("**Partie A**\n\n1. Résoudre le système.", self.exercise.enonce_markdown)
        self.assertIn("2. Déduire de la question précédente.", self.exercise.enonce_markdown)
        self.assertNotIn("**A.1.**", self.exercise.enonce_markdown)
        self.assertNotIn("**A.2.**", self.exercise.enonce_markdown)
        self.assertNotIn("**B.1.**", self.exercise.enonce_markdown)

    def test_skips_numero_prefix_for_a_compound_numero_already_labeled(self):
        """Régression réelle (378 questions sur tout le corpus, surtout en
        physique-chimie) : une sous-question numérotée "1.2"/"2.4.1" (numérotation
        composée à plusieurs niveaux) qui transcrit déjà ce même repère dans son
        propre texte recevait quand même un second préfixe par-dessus - voir
        physique-chimie-bac-c-2015_exercice_1, question 1.2 ("**1.2.** 1.2. Une
        amine primaire...")."""
        Question.objects.create(
            exercise=self.exercise, numero="1.1", ordre=1,
            enonce_markdown="1.1. La réaction est :", corrige_markdown="Réponse.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="2.4.1", ordre=2,
            enonce_markdown="2.4.1. Écrire l'équation-bilan.", corrige_markdown="Réponse.",
        )

        self.exercise.compile_from_questions()

        self.assertIn("1.1. La réaction est :", self.exercise.enonce_markdown)
        self.assertIn("2.4.1. Écrire l'équation-bilan.", self.exercise.enonce_markdown)
        self.assertNotIn("**1.1.**", self.exercise.enonce_markdown)
        self.assertNotIn("**2.4.1.**", self.exercise.enonce_markdown)

    def test_skips_numero_prefix_for_a_compound_numero_without_trailing_punctuation(self):
        # Variante réelle du cas ci-dessus (physique-chimie-bac-d-2017) : le repère
        # composé est parfois transcrit sans point final ("1.3.2 l'expression...").
        Question.objects.create(
            exercise=self.exercise, numero="1.3.1", ordre=1,
            enonce_markdown="1.3.1 la période T.", corrige_markdown="Réponse.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="1.3.2", ordre=2,
            enonce_markdown="1.3.2 l'expression de la tension u(t).", corrige_markdown="Réponse.",
        )

        self.exercise.compile_from_questions()

        self.assertIn("1.3.2 l'expression de la tension u(t).", self.exercise.enonce_markdown)
        self.assertNotIn("**1.3.2.**", self.exercise.enonce_markdown)

    def test_skips_numero_prefix_for_other_real_world_labeling_conventions(self):
        """Autres conventions de numérotation réelles rencontrées sur tout le corpus
        (voir le commentaire de _ENONCE_ALREADY_LABELED_RE) : composé à séparateur
        tiret ("1-2"), composé avec niveau lettre ("2.c"), lettre collée sans
        séparateur ("5a"), ordinal à l'ancienne ("1°-")."""
        cases = [
            ("1-2", "1-2. Citer quatre verreries."),
            ("2.c", "2.c. Avec quelle vitesse."),
            ("1.a", "1.a) Vérifier que pour tout x."),
            ("5", "5a. What is a century?"),
            ("1", "1°- Combien y a-t-il de tirages ?"),
            ("1", "1- What have scientists tried ?"),
        ]
        for index, (numero, enonce) in enumerate(cases):
            exercise = Exercise.objects.create(
                lesson=self.lesson, numero_exercice=f"conv-{index}", statut=StatutContenu.VALIDE,
            )
            Question.objects.create(exercise=exercise, numero=numero, ordre=1, enonce_markdown=enonce, corrige_markdown="R.")
            Question.objects.create(exercise=exercise, numero=f"{numero}-bis", ordre=2, enonce_markdown="Autre question.", corrige_markdown="R.")

            exercise.compile_from_questions()

            self.assertIn(enonce, exercise.enonce_markdown, msg=f"case: {enonce!r}")
            self.assertNotIn(f"**{numero}.**", exercise.enonce_markdown, msg=f"case: {enonce!r}")

    def test_still_prefixes_a_bare_number_followed_by_a_word_with_no_punctuation(self):
        # Garde-fou : un chiffre nu suivi directement d'un mot ("2 pommes...") n'est
        # JAMAIS un repère - la ponctuation finale reste obligatoire dans ce cas,
        # sinon toute sous-question qui commence par une quantité perdrait son
        # numéro affiché.
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1, enonce_markdown="Premher.", corrige_markdown="R.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="2", ordre=2,
            enonce_markdown="2 pommes sont posées sur la table.", corrige_markdown="R.",
        )

        self.exercise.compile_from_questions()

        self.assertIn("**2.** 2 pommes sont posées sur la table.", self.exercise.enonce_markdown)

    def test_still_prefixes_a_question_starting_with_an_algebraic_term(self):
        # Garde-fou dédié : "2x", "3n"... (chiffre collé à une lettre de variable)
        # a exactement la même forme qu'un repère lettre collée ("5a") mais n'en est
        # pas un - régression détectée sur test_compile_from_questions_renders_
        # numero_and_choix_for_qcm lors de l'ajout de ce dernier.
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1, enonce_markdown="Premier.", corrige_markdown="R.",
        )
        Question.objects.create(
            exercise=self.exercise, numero="2", ordre=2,
            enonce_markdown="2x est la derivee de :", corrige_markdown="R.",
        )

        self.exercise.compile_from_questions()

        self.assertIn("**2.** 2x est la derivee de :", self.exercise.enonce_markdown)

    def test_qcm_options_already_embedded_in_prose_are_not_duplicated(self):
        """Régression réelle (14 questions sur 5 épreuves) : correction-experte
        recopie parfois les options d'un QCM en prose dans enonce_markdown EN PLUS
        de les fournir via `choix` (déjà contraire à la règle documentée), et le
        rendu les affichait alors deux fois de suite - voir
        physique-chimie-bac-c-2015_exercice_1, question 1.1."""
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="La réaction est :\n\na) athermique\nb) limitée\nc) rapide.",
            corrige_markdown="c) rapide.",
            type_reponse=TypeReponse.QCM,
            choix=[
                {"lettre": "a", "texte": "athermique"},
                {"lettre": "b", "texte": "limitée"},
                {"lettre": "c", "texte": "rapide"},
            ],
            reponse_correcte="c",
        )

        self.exercise.compile_from_questions()

        self.assertEqual(self.exercise.enonce_markdown.count("a) athermique"), 1)
        self.assertEqual(self.exercise.enonce_markdown.count("b) limitée"), 1)
        self.assertEqual(self.exercise.enonce_markdown.count("c) rapide"), 1)
        self.assertIn("La réaction est :", self.exercise.enonce_markdown)

    def test_qcm_options_embedded_inline_in_one_sentence_are_not_duplicated(self):
        """Variante réelle de la même régression (physique-chimie-bac-d-et-ti-2025,
        physique-chimie-bac-c-d-et-e-2021/2022) : les options recopiées à tort
        n'apparaissent pas toujours une par ligne - parfois toutes dans la même
        phrase, séparées par un espace ou un point-virgule, avec ou sans
        parenthèses autour de la lettre."""
        cas = [
            (
                "Question à choix multiples. La loi est : (a) attraction (b) Laplace (c) Coulomb.",
                [{"lettre": "a", "texte": "attraction"}, {"lettre": "b", "texte": "Laplace"}, {"lettre": "c", "texte": "Coulomb"}],
            ),
            (
                "La vitesse d'une réaction : a) reste la même ; b) augmente ; c) diminue.",
                [{"lettre": "a", "texte": "reste la même"}, {"lettre": "b", "texte": "augmente"}, {"lettre": "c", "texte": "diminue"}],
            ),
        ]
        for index, (enonce, choix) in enumerate(cas):
            exercise = Exercise.objects.create(
                lesson=self.lesson, numero_exercice=f"inline-{index}", statut=StatutContenu.VALIDE,
            )
            Question.objects.create(
                exercise=exercise, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown="R.",
                type_reponse=TypeReponse.QCM, choix=choix, reponse_correcte="a",
            )

            exercise.compile_from_questions()

            for option in choix:
                needle = f"{option['lettre']}) {option['texte']}"
                self.assertEqual(exercise.enonce_markdown.count(needle), 1, msg=f"case: {enonce!r}, needle: {needle!r}")

    def test_qcm_options_embedded_across_blank_lines_are_not_duplicated(self):
        # Variante réelle (physique-chimie-bac-c-2020) : chaque option déjà
        # recopiée sur son propre paragraphe (ligne vide entre chacune), pas juste
        # des lignes consécutives.
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="Le composé est :\n\na) Isomère 1\n\nb) Isomère 2\n\nc) Isomère 3",
            corrige_markdown="b.",
            type_reponse=TypeReponse.QCM,
            choix=[
                {"lettre": "a", "texte": "Isomère 1"},
                {"lettre": "b", "texte": "Isomère 2"},
                {"lettre": "c", "texte": "Isomère 3"},
            ],
            reponse_correcte="b",
        )

        self.exercise.compile_from_questions()

        self.assertEqual(self.exercise.enonce_markdown.count("a) Isomère 1"), 1)
        self.assertEqual(self.exercise.enonce_markdown.count("b) Isomère 2"), 1)
        self.assertEqual(self.exercise.enonce_markdown.count("c) Isomère 3"), 1)

    def test_qcm_options_render_normally_when_not_duplicated_in_prose(self):
        # Non-régression : le cas propre (majoritaire) - options fournies
        # uniquement via `choix` - continue de fonctionner normalement.
        question = Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="2x est la derivee de :", corrige_markdown="b.",
            type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "x"}, {"lettre": "b", "texte": "x^2"}],
            reponse_correcte="b",
        )

        rendered = _render_question_enonce(question, numbered=False)

        self.assertEqual(rendered, "2x est la derivee de :\n\na) x\nb) x^2")


class LessonExercisesBreakdownTests(TestCase):
    """`Lesson.exercises_breakdown()` - énoncé/corrigé exposés séparément par exercice
    (voir catalog.rendering.lesson_exercises_breakdown), utilisé par
    access.views.read_lesson pour replier l'énoncé côté lecture (audit UX)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(cursus)

    def _exercise(self, numero, statut=StatutContenu.VALIDE, enonce="Énoncé.", corrige="Corrigé.", intro="", points=""):
        exercise = Exercise.objects.create(
            lesson=self.lesson, numero_exercice=numero, statut=statut, enonce_intro_markdown=intro, points=points,
        )
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown=corrige,
        )
        exercise.compile_from_questions()
        return exercise

    def test_returns_one_entry_per_validated_exercise_in_order(self):
        self._exercise("2", enonce="Deuxieme.", corrige="Corrige 2.")
        self._exercise("1", enonce="Premier.", corrige="Corrige 1.")

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual([b["numero_exercice"] for b in breakdown], ["1", "2"])
        self.assertEqual(breakdown[0]["enonce_markdown"], "Premier.")
        self.assertEqual(breakdown[0]["corrige_markdown"], "Corrige 1.")

    def test_intro_is_exposed_separately_and_stripped_from_enonce(self):
        # La référence de l'exercice + le préambule partagé doivent rester visibles
        # même quand l'élève ne déplie pas l'énoncé complet (voir EpreuveReaderPage,
        # qui affiche enonce_intro_markdown hors du toggle, juste avant le corrigé) -
        # sans quoi un lecteur du corrigé seul n'a aucun repère sur l'exercice qu'il
        # lit ni sur le contexte auquel le corrigé fait implicitement référence.
        self._exercise("1", intro="**Exercice 1 (6 points)**\n\nDonnées communes.", enonce="Question posée.")

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual(breakdown[0]["enonce_intro_markdown"], "**Exercice 1 (6 points)**\n\nDonnées communes.")
        # Pas de doublon : le préambule ne doit plus apparaître dans enonce_markdown
        # une fois sorti dans son propre champ.
        self.assertEqual(breakdown[0]["enonce_markdown"], "Question posée.")

    def test_enonce_markdown_unchanged_when_no_intro(self):
        self._exercise("1", enonce="Question posée.")

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual(breakdown[0]["enonce_intro_markdown"], "")
        self.assertEqual(breakdown[0]["enonce_markdown"], "Question posée.")

    def test_excludes_draft_and_rejected_exercises(self):
        self._exercise("1", statut=StatutContenu.VALIDE)
        self._exercise("2", statut=StatutContenu.BROUILLON)
        self._exercise("3", statut=StatutContenu.REJETE)

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual([b["numero_exercice"] for b in breakdown], ["1"])

    def test_corrige_is_cleaned_like_the_flattened_content_markdown(self):
        # Même nettoyage que _render_exercise_block (fiche d'identité retirée) -
        # voir _clean_exercise_corrige, partagé par les deux chemins.
        self._exercise("1", corrige="```\nMatière : Maths\n```\nCorrigé réel.")

        breakdown = self.lesson.exercises_breakdown()

        self.assertNotIn("Matière : Maths", breakdown[0]["corrige_markdown"])
        self.assertIn("Corrigé réel.", breakdown[0]["corrige_markdown"])

    def test_empty_for_a_lesson_without_exercises(self):
        fiche = Lesson.objects.create(
            title="Fiche", subject=self.lesson.subject, lesson_type=LessonType.FICHE, statut=StatutContenu.VALIDE,
        )
        self.assertEqual(fiche.exercises_breakdown(), [])

    def test_cours_link_marker_uses_the_cours_slug_not_its_numeric_id(self):
        # Le frontend route vers "/cours/<slug>" (EpreuveMarkdown.tsx) : le marqueur
        # injecté ici doit donc porter le slug, pas l'id numérique - sinon "Voir le
        # cours complet" pointe vers une URL non-slug côté lecture.
        cours = Cours.objects.create(
            external_id="cours-test", titre="Résolution d'équations du second degré",
            subject=self.lesson.subject,
        )
        exercise = self._exercise("1", corrige="Corrigé.\n\n### Rappel de méthode\n\nContenu du rappel.")
        RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-test", competence="Test",
            contenu_markdown="Contenu du rappel.", cours=cours,
        )

        breakdown = self.lesson.exercises_breakdown()

        self.assertIn(f"[COURS_LINK:{cours.slug}]", breakdown[0]["corrige_markdown"])
        self.assertNotIn(f"[COURS_LINK:{cours.id}]", breakdown[0]["corrige_markdown"])

    def test_exposes_titre_and_points_for_the_navigation_sommaire(self):
        self._exercise("1", intro="**Exercice 1 : Chimie organique (5 points)**\n\nDonnées.")

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual(breakdown[0]["titre"], "Exercice 1 : Chimie organique")
        self.assertEqual(breakdown[0]["points"], "5")


class LessonPreviewExercisesTests(TestCase):
    """`Lesson.preview_exercises()` - le sujet public découpé par exercice, servi par
    access.views.preview_lesson (AllowAny) pour que la fiche renvoie vers le corrigé de
    l'exercice consulté. Aucun champ de corrigé ne doit en sortir."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C"))

    def _exercise(self, numero, statut=StatutContenu.VALIDE, intro="", enonce="Énoncé.", corrige="Corrigé secret."):
        exercise = Exercise.objects.create(
            lesson=self.lesson, numero_exercice=numero, statut=statut, enonce_intro_markdown=intro,
        )
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown=corrige,
        )
        exercise.compile_from_questions()
        return exercise

    def test_never_exposes_any_corrige(self):
        # Le vrai risque de cette sortie : elle est publique. Un champ de corrigé qui s'y
        # glisserait donnerait le contenu payant à n'importe quel visiteur.
        self._exercise("1", corrige="Corrigé secret.")

        preview = self.lesson.preview_exercises()

        self.assertNotIn("corrige_markdown", preview[0])
        self.assertNotIn("Corrigé secret.", str(preview))

    def test_keeps_the_preamble_inside_the_enonce(self):
        # Contrairement à exercises_breakdown (qui sort l'intro à part pour la garder
        # visible hors du toggle), rien n'est replié dans le sujet : tout est déjà là.
        self._exercise("1", intro="**Exercice 1 (6 points)**\n\nDonnées communes.", enonce="Question posée.")

        preview = self.lesson.preview_exercises()

        self.assertIn("Données communes.", preview[0]["enonce_markdown"])
        self.assertIn("Question posée.", preview[0]["enonce_markdown"])

    def test_exposes_the_same_labels_and_order_as_the_reader(self):
        for numero in ["10", "2", "1"]:
            self._exercise(numero, intro=f"**Exercice {numero} (5 points)**")

        preview = self.lesson.preview_exercises()

        self.assertEqual([e["numero_exercice"] for e in preview], ["1", "2", "10"])
        self.assertEqual([e["titre"] for e in preview], ["Exercice 1", "Exercice 2", "Exercice 10"])
        self.assertEqual(preview[0]["points"], "5")

    def test_excludes_draft_and_rejected_exercises(self):
        self._exercise("1", statut=StatutContenu.VALIDE)
        self._exercise("2", statut=StatutContenu.BROUILLON)

        self.assertEqual([e["numero_exercice"] for e in self.lesson.preview_exercises()], ["1"])

    def test_empty_for_a_lesson_without_exercises(self):
        fiche = Lesson.objects.create(
            title="Fiche", subject=self.lesson.subject, lesson_type=LessonType.FICHE, statut=StatutContenu.VALIDE,
        )
        self.assertEqual(fiche.preview_exercises(), [])


class ExerciseSortKeyTests(TestCase):
    """`numero_exercice` est un CharField : un ORDER BY SQL trie "10"/"11" avant "2".
    Constaté sur bac-c-svt-2015-cameroun (11 exercices), affichée dans le désordre à la
    fois en lecture, dans le sujet public et dans content_markdown compilé."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C"))

    def _exercise(self, numero):
        exercise = Exercise.objects.create(
            lesson=self.lesson, numero_exercice=numero, statut=StatutContenu.VALIDE,
        )
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1,
            enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        )
        exercise.compile_from_questions()
        return exercise

    def test_orders_numerically_beyond_nine(self):
        for numero in ["1", "2", "10", "11", "3"]:
            self._exercise(numero)

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual([b["numero_exercice"] for b in breakdown], ["1", "2", "3", "10", "11"])

    def test_groups_letter_suffixes_behind_their_number(self):
        for numero in ["3b", "10", "3a", "2"]:
            self._exercise(numero)

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual([b["numero_exercice"] for b in breakdown], ["2", "3a", "3b", "10"])

    def test_non_numeric_markers_come_after_the_numbered_exercises(self):
        # "Problème"/"Section III" n'ont pas de rang déductible - en pratique ce sont
        # les parties finales d'une épreuve, jamais un repère à insérer au milieu.
        for numero in ["Probleme", "2", "Section III", "1"]:
            self._exercise(numero)

        breakdown = self.lesson.exercises_breakdown()

        self.assertEqual(
            [b["numero_exercice"] for b in breakdown], ["1", "2", "Probleme", "Section III"],
        )

    def test_preview_and_compiled_content_follow_the_same_order(self):
        # Les trois sorties visibles par l'élève (lecture, sujet public, content_markdown
        # compilé) doivent s'accorder - sinon l'exercice 10 du sommaire ne tombe pas au
        # même endroit que dans le PDF ou dans le sujet.
        for numero in ["10", "2", "1"]:
            self._exercise(numero)

        preview = self.lesson.preview_markdown()
        self.assertLess(preview.index("Énoncé 1."), preview.index("Énoncé 2."))
        self.assertLess(preview.index("Énoncé 2."), preview.index("Énoncé 10."))

        self.lesson.compile_from_exercises()
        compiled = self.lesson.content_markdown
        self.assertLess(compiled.index("Énoncé 1."), compiled.index("Énoncé 2."))
        self.assertLess(compiled.index("Énoncé 2."), compiled.index("Énoncé 10."))


class ExerciseTitreEtPointsTests(TestCase):
    """`_exercise_titre_et_points` - le libellé d'un exercice n'a pas de champ dédié en
    base, il vit dans la première ligne de enonce_intro_markdown. Alimente le sommaire
    de navigation du lecteur (voir EpreuveSommaire côté frontend)."""

    def _titre_et_points(self, intro, points="", enonce=""):
        return _exercise_titre_et_points(
            Exercise(enonce_intro_markdown=intro, enonce_markdown=enonce, points=points),
        )

    def test_markdown_heading(self):
        self.assertEqual(self._titre_et_points("### Exercice 1 (5 points)"), ("Exercice 1", "5"))

    def test_bold_heading_with_a_descriptive_title(self):
        self.assertEqual(
            self._titre_et_points("**Exercice 2 : Acides et bases (5 points)**\n\nPréambule."),
            ("Exercice 2 : Acides et bases", "5"),
        )

    def test_bold_heading_followed_by_preamble_on_the_same_line(self):
        # Forme réelle des épreuves d'anglais (bac-a-anglais-2000-cameroun) : seul le
        # premier segment en gras est le titre, la suite de la ligne est du préambule.
        self.assertEqual(
            self._titre_et_points("**Section D: Essay (10 marks).** Write an essay of 300 words."),
            ("Section D: Essay", "10"),
        )

    def test_structured_points_field_wins_over_the_title(self):
        self.assertEqual(self._titre_et_points("### Problème (10 points)", points="12"), ("Problème", "12"))

    def test_no_title_when_the_intro_is_plain_preamble(self):
        # Une première phrase d'énoncé n'est pas un repère : mieux vaut un titre vide
        # (le frontend retombe sur "Exercice {numero}") qu'une étiquette tronquée.
        self.assertEqual(self._titre_et_points("Une urne contient 12 billes."), ("", ""))

    def test_no_title_when_the_intro_is_empty(self):
        self.assertEqual(self._titre_et_points(""), ("", ""))

    def test_falls_back_to_the_enonce_when_there_is_no_shared_preamble(self):
        # Cas réel de chimie-bac-c-1999 : aucun de ses 4 exercices n'a de préambule
        # partagé, la référence vit en tête de la première sous-question.
        self.assertEqual(
            self._titre_et_points("", enonce="**Exercice 1 : Chimie organique (5 points)**\n\n1. Donner..."),
            ("Exercice 1 : Chimie organique", "5"),
        )

    def test_a_leading_question_number_is_never_taken_for_a_title(self):
        # Sans garde-fou, un exercice sans préambule dont l'énoncé ouvre sur "**1.**"
        # se retrouvait étiqueté "1." dans le sommaire.
        self.assertEqual(
            self._titre_et_points("", enonce="**1.** Écris le nombre $A$ sous forme irréductible."),
            ("", ""),
        )


class ReferencesMissingFigureTests(TestCase):
    """Une question qui renvoie explicitement à une figure ("ci-contre"...) sans
    qu'aucune image ne soit attachée nulle part est insoluble - voir
    Question.references_missing_figure et son usage dans quiz.services."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(cursus)
        self._numero_exercice = 0

    def _question(self, enonce_markdown, enonce_intro_markdown=""):
        self._numero_exercice += 1
        exercise = Exercise.objects.create(
            lesson=self.lesson, numero_exercice=str(self._numero_exercice), statut=StatutContenu.VALIDE,
            enonce_intro_markdown=enonce_intro_markdown,
        )
        return Question.objects.create(
            exercise=exercise, numero="1", ordre=1, enonce_markdown=enonce_markdown, corrige_markdown="Corrigé.",
        )

    def test_true_when_ci_contre_reference_has_no_image_anywhere(self):
        question = self._question("La courbe ci-contre représente une fonction f. Pour tout x, f(x)>0.")
        self.assertTrue(question.references_missing_figure)

    def test_false_when_image_is_in_the_question_itself(self):
        question = self._question("La courbe ci-contre.\n\n![fig-1](/media/figures/x.png)")
        self.assertFalse(question.references_missing_figure)

    def test_false_when_image_is_in_the_shared_exercise_intro(self):
        question = self._question(
            "La courbe ci-contre représente f.", enonce_intro_markdown="![fig-1](/media/figures/x.png)",
        )
        self.assertFalse(question.references_missing_figure)

    def test_false_when_no_deictic_reference_at_all(self):
        question = self._question("Calculer la dérivée de f.")
        self.assertFalse(question.references_missing_figure)

    def test_detects_ci_dessous_and_ci_apres_variants(self):
        self.assertTrue(self._question("Le tableau ci-dessous donne les résultats.").references_missing_figure)
        self.assertTrue(self._question("Voir le schéma ci-après.").references_missing_figure)


class QuestionIngestionTests(TestCase):
    """L'ingestion doit decomposer un exercice en Question atomiques plutot que de
    tout aplatir dans un seul enonce_markdown/corrige_markdown - voir
    catalog.ingestion.ingest_exercise et le plan de ce chantier."""

    def _payload(self, **overrides):
        payload = {
            "epreuve_source": "bac-maths-2024", "numero_exercice": "1",
            "matiere": "Mathematiques", "serie": "C", "examen": "BAC",
            "enonce_intro_markdown": "Pour chacune des questions, une seule reponse est exacte.",
            "questions": [
                {
                    "numero": "1", "enonce_markdown": "Question 1 : 2+2 = ?", "corrige_markdown": "### Corrige\n\n4.",
                    "difficulte_estimee": "faible", "themes": ["arithmetique"],
                },
                {
                    "numero": "2", "enonce_markdown": "Question 2 : derivee de x^2 ?",
                    "corrige_markdown": "### Corrige\n\n2x.", "difficulte_estimee": "moyenne",
                    "themes": ["derivation"], "type_reponse": "qcm",
                    "choix": [{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}],
                    "reponse_correcte": "a",
                },
            ],
        }
        payload.update(overrides)
        return payload

    def test_creates_one_question_per_entry_with_correct_order_and_fields(self):
        exercise, created = ingest_exercise(self._payload(), source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertTrue(created)
        questions = list(exercise.questions.order_by("ordre"))
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].numero, "1")
        self.assertEqual(questions[0].difficulte_estimee, Difficulte.FAIBLE)
        self.assertEqual(questions[0].type_reponse, TypeReponse.OUVERTE)
        self.assertEqual(questions[1].numero, "2")
        self.assertEqual(questions[1].type_reponse, TypeReponse.QCM)
        self.assertEqual(questions[1].reponse_correcte, "a")
        self.assertEqual(questions[1].choix, [{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}])

    def test_qcm_choix_as_prefixed_strings_is_normalized_to_lettre_texte_objects(self):
        # Constaté en production : correction-experte peut produire "choix" comme une
        # liste de chaînes "x) texte" plutôt que des objets {lettre, texte}, et
        # "reponse_correcte" comme le texte complet du bon choix plutôt que sa seule
        # lettre - reponse_correcte dépassait alors max_length=10 (DataError Postgres)
        # et la comparaison de correction aurait de toute façon été fausse (une lettre
        # seule ne peut jamais égaler une phrase complète).
        payload = self._payload()
        payload["questions"][1]["choix"] = ["a) $2x$", "b) $x$"]
        payload["questions"][1]["reponse_correcte"] = "a) $2x$"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.get(numero="2")
        self.assertEqual(question.choix, [{"lettre": "a", "texte": "$2x$"}, {"lettre": "b", "texte": "$x$"}])
        self.assertEqual(question.reponse_correcte, "a")
        self.assertEqual(len(question.reponse_correcte), 1)

    def test_qcm_reponse_correcte_as_bare_letter_still_works(self):
        payload = self._payload()
        payload["questions"][1]["choix"] = ["a) $2x$", "b) $x$"]
        payload["questions"][1]["reponse_correcte"] = "b"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get(numero="2").reponse_correcte, "b")

    def test_qcm_reponse_correcte_matched_by_text_when_prefix_missing(self):
        payload = self._payload()
        payload["questions"][1]["choix"] = ["a) $2x$", "b) $x$"]
        payload["questions"][1]["reponse_correcte"] = "$x$"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get(numero="2").reponse_correcte, "b")

    def test_qcm_choix_without_any_letter_gets_letters_synthesized_by_position(self):
        # Constaté en production : un QCM vrai/faux peut arriver comme "choix":
        # ["Vrai", "Faux"] - aucune lettre du tout, ni objet ni préfixe "x) ". Rejeter
        # ce contenu par ailleurs valide serait pire que de lui assigner une lettre
        # par position ; reponse_correcte se raccroche alors par texte (voir plus bas).
        payload = self._payload()
        payload["questions"][1]["choix"] = ["Vrai", "Faux"]
        payload["questions"][1]["reponse_correcte"] = "Vrai"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.get(numero="2")
        self.assertEqual(question.choix, [{"lettre": "a", "texte": "Vrai"}, {"lettre": "b", "texte": "Faux"}])
        self.assertEqual(question.reponse_correcte, "a")

    def test_qcm_choix_with_compound_lettre_codes_for_matching_exercises(self):
        # Constaté en production : un QCM d'appariement (colonne A / colonne B) utilise
        # des lettres composées ("b1", "b2", "b3"...), pas seulement a/b/c/d - la
        # comparaison reponse_correcte doit reconnaître ces codes directement, pas
        # seulement les lettres à un caractère.
        payload = self._payload()
        payload["questions"][1]["choix"] = [
            {"lettre": "b1", "texte": "E0 = 0,17 V"},
            {"lettre": "b2", "texte": "E0 = mc^2"},
            {"lettre": "b3", "texte": "E = 13,6 eV"},
        ]
        payload["questions"][1]["reponse_correcte"] = "b3"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get(numero="2").reponse_correcte, "b3")

    def test_rejects_qcm_reponse_correcte_matching_nothing(self):
        payload = self._payload()
        payload["questions"][1]["choix"] = ["a) $2x$", "b) $x$"]
        payload["questions"][1]["reponse_correcte"] = "une reponse qui ne correspond a aucun choix"
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def test_ingest_strips_shared_intro_echoed_at_start_of_question_enonce(self):
        # Constaté en production : correction-experte recopie la phrase de contexte
        # partagée (déjà dans enonce_intro_markdown) au début de CHAQUE sous-question,
        # au lieu de ne la mettre qu'une fois - elle apparaît alors deux fois de suite
        # dans le corrigé compilé et dans le Quiz.
        payload = self._payload(enonce_intro_markdown="Soit f(x) = x^2.")
        payload["questions"][0]["enonce_markdown"] = "Soit f(x) = x^2.\n\nCalculer f'(x)."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.get(numero="1")
        self.assertEqual(question.enonce_markdown, "Calculer f'(x).")

    def test_ingest_strips_doubled_sub_question_label(self):
        payload = self._payload()
        payload["questions"][0]["enonce_markdown"] = "(a) (a) Calculer f'(x)."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get(numero="1").enonce_markdown, "(a) Calculer f'(x).")

    def test_matiere_aliases_physique_chimie_and_langue_francaise_resolve(self):
        # Constaté en production : certaines épreuves (Congo) traitent Physique et
        # Chimie comme deux matières distinctes - chacune sa propre Subject depuis le
        # 2026-08-08 (voir SUBJECT_FAMILIES) - et "Langue française" est un synonyme
        # de FRANCAIS - voir MATIERE_MAP.
        for i, (matiere, expected_code) in enumerate([("Physique", "PHYSIQUE"), ("Chimie", "CHIMIE"), ("Physique-Chimie", "PHYSIQUE_CHIMIE"), ("Langue française", "FRANCAIS"), ("Informatique", "INFORMATIQUE"), ("Physique-Chimie-Technologie", "PHYSIQUE_CHIMIE_TECH")]):
            # epreuve_source distinct par cas : Physique/Chimie/Physique-Chimie partagent
            # désormais une famille (voir SUBJECT_FAMILIES) - les réutiliser sur le même
            # epreuve_source les fusionnerait/promouvrait en un seul Lesson, alors que ce
            # test vérifie une résolution indépendante par matière.
            payload = self._payload(matiere=matiere, epreuve_source=f"bac-matiere-test-{i}")
            exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))
            self.assertEqual(exercise.lesson.subject.code, expected_code)

    def test_rappel_de_methode_with_null_competence_does_not_crash(self):
        # Constaté en production : correction-experte émet parfois "competence": null
        # au lieu d'omettre la clé - `.get("competence", "")` ne retourne son défaut
        # que si la clé est absente, jamais si sa valeur JSON est déjà null, donc le
        # None traversait jusqu'à la colonne NOT NULL (DataError Postgres).
        payload = self._payload()
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-test-1", "competence": None, "contenu_markdown": "Contenu du rappel."},
        ]

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        rappel = exercise.rappels_de_methode.get(external_id="rdm-test-1")
        self.assertEqual(rappel.competence, "")
        self.assertEqual(rappel.contenu_markdown, "Contenu du rappel.")

    def test_exercise_fields_are_compiled_from_questions(self):
        exercise, _ = ingest_exercise(self._payload(), source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertIn("Pour chacune des questions", exercise.enonce_markdown)
        self.assertIn("Question 1 : 2+2 = ?", exercise.enonce_markdown)
        self.assertIn("Question 2 : derivee de x^2 ?", exercise.enonce_markdown)
        self.assertIn("4.", exercise.corrige_markdown)
        self.assertIn("2x.", exercise.corrige_markdown)
        self.assertEqual(
            set(exercise.themes.values_list("name", flat=True)), {"arithmetique", "derivation"},
        )

    def test_lesson_still_compiles_correctly_from_the_compiled_exercise(self):
        exercise, _ = ingest_exercise(self._payload(), source_dir=Path("ingest/cm/bac-maths-2024"))
        exercise.lesson.refresh_from_db()
        self.assertIn("Question 1 : 2+2 = ?", exercise.lesson.content_markdown)

    def test_corrige_markdown_prefixes_question_numero_and_enonce_when_several_sub_questions(self):
        # Bug réel constaté en production (épreuves bac-c-e-maths-2005 à 2013) :
        # corrige_markdown ne préfixait jamais le numero de la sous-question, contrairement
        # à enonce_markdown (voir _render_question_enonce) - un exercice à plusieurs
        # sous-questions affichait donc une série de "### Rappel de méthode" à la suite
        # sans aucun moyen de savoir à quelle question chacun répond. Un premier correctif
        # n'a réinjecté que le numero nu ("**1.**") ; l'élève devait encore remonter au
        # sujet pour retrouver l'énoncé correspondant - _render_question_corrige réutilise
        # maintenant _render_question_enonce en entier (numero + texte de la question).
        exercise, _ = ingest_exercise(self._payload(), source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertIn("**1.** Question 1 : 2+2 = ?\n\n### Corrige\n\n4.", exercise.corrige_markdown)
        self.assertIn("**2.** Question 2 : derivee de x^2 ?", exercise.corrige_markdown)
        self.assertIn("### Corrige\n\n2x.", exercise.corrige_markdown)

    def test_corrige_markdown_has_no_numero_prefix_for_a_single_question_exercise(self):
        payload = _exercise_payload("bac-maths-2024")
        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertNotIn("**1.**", exercise.corrige_markdown)

    def test_rejects_payload_without_questions(self):
        payload = self._payload()
        payload["questions"] = []
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def test_rejects_question_missing_corrige(self):
        payload = self._payload()
        del payload["questions"][0]["corrige_markdown"]
        with self.assertRaises(IngestionError):
            ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

    def test_shared_figure_placeholder_replaced_across_multiple_questions(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "graphique.png").write_bytes(b"fake-png-bytes")

            payload = self._payload(
                figures=[{
                    "id": "fig-1", "fichier": "graphique.png", "page_source": 1,
                    "type": "courbe", "legende": "Courbe de f", "indispensable": True, "lisibilite": "bonne",
                }],
            )
            payload["questions"][0]["enonce_markdown"] = "Lire fig-1 (graphique.png) et calculer f(0)."
            payload["questions"][1]["corrige_markdown"] = "### Corrige\n\nOn relit fig-1 (graphique.png) : 2x."

            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        questions = list(exercise.questions.order_by("ordre"))
        # Le placeholder markdown "(graphique.png)" doit avoir disparu, remplacé par une
        # vraie URL servable - qui contient légitimement "graphique.png" en fin de chemin
        # (ex. /media/figures/graphique.png), donc on vérifie le motif de lien markdown
        # d'origine plutôt que la simple présence du nom de fichier.
        self.assertNotIn("(graphique.png)", questions[0].enonce_markdown)
        self.assertIn("/media/figures/", questions[0].enonce_markdown)
        self.assertNotIn("(graphique.png)", questions[1].corrige_markdown)
        self.assertIn("/media/figures/", questions[1].corrige_markdown)

    def test_a_real_figure_is_stored_compressed_as_webp(self):
        # Contrairement aux autres tests de ce fichier (b"fake-png-bytes", volontairement
        # illisible par Pillow pour rester rapides) : une vraie image ici, pour vérifier
        # que la compression (voir _compress_figure_image, reco 5.2 de l'audit UX) est
        # bien câblée bout en bout, jusqu'à l'URL finalement stockée dans le Markdown.
        buffer = BytesIO()
        Image.new("RGB", (50, 50), "red").save(buffer, format="PNG")

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "graphique.png").write_bytes(buffer.getvalue())

            payload = self._payload(
                figures=[{
                    "id": "fig-1", "fichier": "graphique.png", "page_source": 1,
                    "type": "courbe", "legende": "Courbe de f", "indispensable": True, "lisibilite": "bonne",
                }],
            )
            payload["questions"][0]["enonce_markdown"] = "Lire fig-1 (graphique.png)."

            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        figure = exercise.figures.get(external_id="fig-1")
        self.assertTrue(figure.image.name.endswith(".webp"))
        self.assertIn(".webp", exercise.questions.first().enonce_markdown)

    def test_figure_placeholder_alt_text_uses_the_legende_when_present(self):
        # Convention réelle de correction-experte (vérifiée en base de production) :
        # "![fig-1](nom_original.png)", jamais du texte libre - voir l'audit UX, reco
        # 6.1 : "fig-1" seul ne dit rien à un lecteur d'écran.
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "graphique.png").write_bytes(b"fake-png-bytes")

            payload = self._payload(
                figures=[{
                    "id": "fig-1", "fichier": "graphique.png",
                    "type": "courbe", "legende": "Courbe de f(x)", "indispensable": True, "lisibilite": "bonne",
                }],
            )
            payload["questions"][0]["enonce_markdown"] = "Voir ![fig-1](graphique.png) ci-dessus."

            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        enonce = exercise.questions.first().enonce_markdown
        self.assertIn("![Courbe de f(x)](", enonce)
        self.assertNotIn("![fig-1]", enonce)

    def test_figure_placeholder_alt_text_falls_back_to_type_figure_without_legende(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "graphique.png").write_bytes(b"fake-png-bytes")

            payload = self._payload(
                figures=[{"id": "fig-1", "fichier": "graphique.png", "type": "courbe", "indispensable": True}],
            )
            payload["questions"][0]["enonce_markdown"] = "Voir ![fig-1](graphique.png) ci-dessus."

            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        self.assertIn("![courbe](", exercise.questions.first().enonce_markdown)

    def test_figure_placeholder_alt_text_falls_back_to_a_generic_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "graphique.png").write_bytes(b"fake-png-bytes")

            payload = self._payload(figures=[{"id": "fig-1", "fichier": "graphique.png", "indispensable": True}])
            payload["questions"][0]["enonce_markdown"] = "Voir ![fig-1](graphique.png) ci-dessus."

            exercise, _ = ingest_exercise(payload, source_dir=source_dir)

        self.assertIn("![Figure du corrigé](", exercise.questions.first().enonce_markdown)

    def test_figure_without_fichier_is_dropped_with_incertitude_note(self):
        # Constaté en production (probatoire-c-d-chimie 2008/2011/2013-cameroun) : la
        # compétence décrit une figure qu'elle sait avoir existé sur le sujet source
        # (id + description) mais n'a pas pu en extraire une image exploitable (scan
        # trop ancien/dégradé) - ne doit jamais faire échouer l'ingestion de tout
        # l'exercice pour ça, juste être ignorée avec une trace dans incertitudes
        # (voir _attach_figures) : aucune de ces figures n'est référencée par un
        # placeholder dans enonce/corrige_markdown, donc rien n'est perdu à l'ignorer.
        payload = self._payload(
            figures=[{"id": "fig-1", "type": "schema", "description": "Schéma non capturé lors de l'extraction."}],
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.figures.count(), 0)
        self.assertTrue(any("fig-1" in note for note in exercise.incertitudes))

    def test_figure_entry_as_bare_string_is_dropped_with_incertitude_note(self):
        # Constaté en production (bac-c-physique-2024, bac-d-physique-2019/2022-
        # cameroun, 9 fichiers) : la compétence a émis l'id de la figure comme simple
        # chaîne au lieu de l'objet {"id", "fichier", ...} attendu - même traitement
        # que le cas "sans fichier" ci-dessus (voir _attach_figures), pas un AttributeError.
        payload = self._payload(figures=["fig-orpheline"])

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.figures.count(), 0)
        self.assertTrue(any("fig-orpheline" in note for note in exercise.incertitudes))


class PhysiqueChimieClassificationTests(TestCase):
    """Physique et Chimie sont désormais des Subject distinctes (voir MATIERE_MAP),
    mais une épreuve qui mélange les deux disciplines au sein d'un même epreuve_source
    (constaté en production sur bac-d-physique-chimie-1995-cameroun et
    bac-c-physique-chimie-2016-congo, où le champ matiere varie déjà par exercice) ne
    doit jamais être fragmentée en plusieurs Lesson - voir SUBJECT_FAMILIES et la
    promotion dans ingest_exercise."""

    def _payload(self, numero_exercice, matiere, **overrides):
        payload = {
            "epreuve_source": "bac-d-physique-chimie-1995-cameroun", "numero_exercice": numero_exercice,
            "matiere": matiere, "serie": "D", "examen": "BAC", "annee": 1995,
            "questions": [
                {"numero": "1", "enonce_markdown": f"Question {numero_exercice}.", "corrige_markdown": "### Corrige\n\nOK."},
            ],
        }
        payload.update(overrides)
        return payload

    def test_matiere_physique_and_chimie_resolve_to_distinct_subjects(self):
        # epreuve_source distincts (deux vraies épreuves séparées, pas un mélange) :
        # deux Lesson indépendantes, chacune sous sa propre discipline - le cas
        # courant, non combiné.
        physique, _ = ingest_exercise(
            self._payload("1", "Physique", epreuve_source="bac-c-physique-2017-cameroun"),
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )
        chimie, _ = ingest_exercise(
            self._payload("1", "Chimie", epreuve_source="bac-c-d-chimie-2017-cameroun"),
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )

        self.assertNotEqual(physique.lesson_id, chimie.lesson_id)
        self.assertEqual(physique.lesson.subject.code, "PHYSIQUE")
        self.assertEqual(chimie.lesson.subject.code, "CHIMIE")

    def test_mixed_disciplines_same_epreuve_source_promote_to_combined_subject(self):
        # Rejoue exactement le motif constaté sur bac-d-physique-chimie-1995-cameroun :
        # exercices 1-2 déclarés "Physique", exercices 3-4 déclarés "Chimie".
        ex1, created1 = ingest_exercise(self._payload("1", "Physique"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        ex2, created2 = ingest_exercise(self._payload("2", "Physique"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        ex3, created3 = ingest_exercise(self._payload("3", "Chimie"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        ex4, created4 = ingest_exercise(self._payload("4", "Chimie"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))

        self.assertTrue(created1 and created2 and created3 and created4)
        # Un seul Lesson pour les 4 exercices - jamais fragmenté en Lesson "Physique"
        # + Lesson "Chimie" séparées.
        lesson_ids = {ex1.lesson_id, ex2.lesson_id, ex3.lesson_id, ex4.lesson_id}
        self.assertEqual(len(lesson_ids), 1)
        # Relu depuis la base (pas ex1.lesson, mis en cache au moment de la création
        # de ex1 - avant la promotion déclenchée par ex3/ex4) : Django ne rafraîchit
        # jamais tout seul un objet lié déjà chargé.
        lesson = Lesson.objects.get(pk=ex1.lesson_id)
        self.assertEqual(lesson.subject.code, "PHYSIQUE_CHIMIE")
        self.assertEqual(lesson.exercises.count(), 4)

    def test_promotion_is_monotonic_never_narrows_back(self):
        # Une épreuve déjà promue en Physique-Chimie doit le rester, même si un
        # exercice ultérieur redéclare une seule discipline.
        ex1, _ = ingest_exercise(self._payload("1", "Physique"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        ex2, _ = ingest_exercise(self._payload("2", "Chimie"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        # ex2.lesson (pas ex1.lesson, stale) : l'objet Lesson lié à ex2 vient d'être
        # rechargé/promu par ingest_exercise lui-même, donc déjà à jour.
        self.assertEqual(ex2.lesson.subject.code, "PHYSIQUE_CHIMIE")

        ex3, _ = ingest_exercise(self._payload("3", "Physique"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))

        self.assertEqual(ex3.lesson_id, ex1.lesson_id)
        self.assertEqual(ex3.lesson.subject.code, "PHYSIQUE_CHIMIE")

    def test_explicit_physique_chimie_matiere_joins_and_promotes_existing_lesson(self):
        # Un premier exercice déclaré "Physique", puis un deuxième déclaré littéralement
        # "Physique-Chimie" (cas d'incertitude assumée par la compétence, voir §12) -
        # doit rejoindre le même Lesson et le promouvoir, pas en créer un troisième.
        ex1, _ = ingest_exercise(self._payload("1", "Physique"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))
        ex2, _ = ingest_exercise(self._payload("2", "Physique-Chimie"), source_dir=Path("ingest/cm/bac-d-physique-chimie-1995-cameroun"))

        self.assertEqual(ex1.lesson_id, ex2.lesson_id)
        self.assertEqual(ex2.lesson.subject.code, "PHYSIQUE_CHIMIE")

    def test_congo_mixed_order_reversed_still_promotes_correctly(self):
        # Même motif que bac-c-physique-chimie-2016-congo, mais Chimie déclarée avant
        # Physique cette fois (l'ordre de dépôt des fichiers ne doit rien changer).
        ex1, _ = ingest_exercise(self._payload("1", "Chimie"), source_dir=Path("ingest/cm/bac-c-physique-chimie-2016-congo"))
        ex2, _ = ingest_exercise(self._payload("2", "Physique"), source_dir=Path("ingest/cm/bac-c-physique-chimie-2016-congo"))

        self.assertEqual(ex1.lesson_id, ex2.lesson_id)
        self.assertEqual(ex2.lesson.subject.code, "PHYSIQUE_CHIMIE")

    def test_unrelated_subject_is_never_affected_by_family_lookup(self):
        # Garde-fou : deux exercices de Maths sur un même epreuve_source ne doivent
        # jamais être affectés par la logique de famille (Maths hors SUBJECT_FAMILIES).
        ex1, _ = ingest_exercise(
            {**self._payload("1", "Mathematiques"), "epreuve_source": "bac-maths-2024"},
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )
        ex2, _ = ingest_exercise(
            {**self._payload("2", "Mathematiques"), "epreuve_source": "bac-maths-2024"},
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )
        self.assertEqual(ex1.lesson_id, ex2.lesson_id)
        self.assertEqual(ex1.lesson.subject.code, "MATHS")


class NatureEpreuveIngestionTests(TestCase):
    """Champ optionnel (contrairement à examen/origine) : jamais deviné, jamais
    bloquant en son absence - voir _resolve_nature_epreuve."""

    def _payload(self, **overrides):
        payload = {
            "epreuve_source": "bac-c-physique-theorique-2022-cameroun", "numero_exercice": "1",
            "matiere": "Physique", "serie": "C", "examen": "BAC", "annee": 2022,
            "questions": [
                {"numero": "1", "enonce_markdown": "Question.", "corrige_markdown": "### Corrige\n\nOK."},
            ],
        }
        payload.update(overrides)
        return payload

    def test_theorique_and_pratique_resolve_on_lesson(self):
        theorique, _ = ingest_exercise(self._payload(nature_epreuve="theorique"), source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(theorique.lesson.nature_epreuve, NatureEpreuve.THEORIQUE)

        pratique, _ = ingest_exercise(
            self._payload(epreuve_source="bac-c-physique-pratique-2022-cameroun", nature_epreuve="pratique"),
            source_dir=Path("ingest/cm/bac-maths-2024"),
        )
        self.assertEqual(pratique.lesson.nature_epreuve, NatureEpreuve.PRATIQUE)

    def test_absent_nature_epreuve_stays_blank(self):
        exercise, _ = ingest_exercise(self._payload(), source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(exercise.lesson.nature_epreuve, "")

    def test_invalid_nature_epreuve_raises(self):
        with self.assertRaises(IngestionError):
            ingest_exercise(self._payload(nature_epreuve="mixte"), source_dir=Path("ingest/cm/bac-maths-2024"))

    def test_nature_epreuve_filled_by_later_exercise_when_first_omits_it(self):
        ex1, _ = ingest_exercise(self._payload(numero_exercice="1"), source_dir=Path("ingest/cm/bac-maths-2024"))
        self.assertEqual(ex1.lesson.nature_epreuve, "")

        ex2, _ = ingest_exercise(
            self._payload(numero_exercice="2", nature_epreuve="theorique"), source_dir=Path("ingest/cm/bac-maths-2024"),
        )

        self.assertEqual(ex1.lesson_id, ex2.lesson_id)
        ex1.lesson.refresh_from_db()
        self.assertEqual(ex1.lesson.nature_epreuve, NatureEpreuve.THEORIQUE)


class DisciplineAndNatureFilterApiTests(TestCase):
    """`?discipline=` (recherche "contient cette discipline", inclut Physique-Chimie)
    et `?nature=` sur /catalog/lessons/ - à distinguer de `?subject=` qui reste une
    correspondance exacte (voir catalog.views.LessonListView)."""

    def setUp(self):
        country = Country.objects.get(code="CM")
        self.physique = Subject.objects.get(country=country, code="PHYSIQUE")
        self.chimie = Subject.objects.get(country=country, code="CHIMIE")
        self.physique_chimie = Subject.objects.get(country=country, code="PHYSIQUE_CHIMIE")

        self.lesson_physique = Lesson.objects.create(
            title="Physique seule", subject=self.physique, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, nature_epreuve=NatureEpreuve.PRATIQUE,
        )
        self.lesson_chimie = Lesson.objects.create(
            title="Chimie seule", subject=self.chimie, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson_combinee = Lesson.objects.create(
            title="Physique-Chimie combinée", subject=self.physique_chimie, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )

    def test_subject_exact_match_excludes_physique_chimie(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"subject": "PHYSIQUE"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Physique seule", titles)
        self.assertNotIn("Physique-Chimie combinée", titles)

    def test_discipline_filter_includes_physique_chimie(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"discipline": "PHYSIQUE"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertIn("Physique seule", titles)
        self.assertIn("Physique-Chimie combinée", titles)
        self.assertNotIn("Chimie seule", titles)

    def test_discipline_filter_on_unrelated_subject_behaves_like_exact_match(self):
        maths = Subject.objects.get(country__code="CM", code="MATHS")
        Lesson.objects.create(title="Maths", subject=maths, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE)

        response = self.client.get(reverse("catalog:lesson-list"), {"discipline": "MATHS"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["Maths"])

    def test_nature_filter(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"nature": "pratique"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["Physique seule"])


class EstVitrineFilterApiTests(TestCase):
    """`?est_vitrine=true` sur /catalog/lessons/ - alimente le CTA "Essayer un
    corrigé gratuit" du hero (CataloguePage), qui a besoin de trouver une épreuve en
    accès libre pour le pays courant sans connaître son slug à l'avance."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.vitrine = Lesson.objects.create(
            title="Vitrine", subject=subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, est_vitrine=True,
        )
        Lesson.objects.create(
            title="Non vitrine", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )

    def test_returns_only_vitrine_lessons(self):
        response = self.client.get(reverse("catalog:lesson-list"), {"est_vitrine": "true"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["Vitrine"])

    def test_absent_returns_all(self):
        titles = [item["title"] for item in self.client.get(reverse("catalog:lesson-list")).json()["results"]]
        self.assertIn("Vitrine", titles)
        self.assertIn("Non vitrine", titles)


class LessonSearchApiTests(TestCase):
    """`?search=` sur /catalog/lessons/ - couvre les 4 canaux (titre, contenu compilé,
    thèmes, mots-clés) et le bug de fan-out déjà rencontré en production : joindre
    themes ET mots_cles_recherche dans le même filtre multiplie chaque Lesson par
    (nb thèmes × nb mots-clés) avant le WHERE - une épreuve à 65 thèmes et 43 mots-
    clés produisait 2795 lignes fantômes, rendant une recherche par année (ex.
    "2022") catastrophiquement lente (107s mesurés sur ~225 épreuves) alors que le
    filtre lui-même était fonctionnellement correct. Voir catalog.views.LessonListView,
    qui utilise désormais Exists() plutôt qu'un JOIN pour ces deux relations."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.lesson = Lesson.objects.create(
            title="Mathématiques BAC C 2022", subject=subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="Contenu sur les suites numériques.",
        )
        self.lesson.themes.set([Tag.objects.create(name="Suites arithmétiques")])
        self.lesson.mots_cles_recherche.set([Tag.objects.create(name="raison")])

    def _search(self, term):
        response = self.client.get(reverse("catalog:lesson-list"), {"search": term})
        return [item["title"] for item in response.json()["results"]]

    def test_matches_on_title(self):
        self.assertIn(self.lesson.title, self._search("2022"))

    def test_matches_on_content_markdown(self):
        self.assertIn(self.lesson.title, self._search("suites numériques"))

    def test_matches_on_theme(self):
        self.assertIn(self.lesson.title, self._search("arithmétiques"))

    def test_matches_on_mot_cle_recherche(self):
        self.assertIn(self.lesson.title, self._search("raison"))

    def test_no_duplicate_results_when_theme_and_keyword_both_match(self):
        # Un même terme présent à la fois dans un thème et un mot-clé ne doit renvoyer
        # la Lesson qu'une seule fois (voir Exists() + distinct() dans la vue) - c'est
        # précisément le cas qui, avec un JOIN, produisait des doublons avant DISTINCT.
        self.lesson.themes.add(Tag.objects.create(name="algèbre"))
        self.lesson.mots_cles_recherche.add(Tag.objects.create(name="algèbre avancée"))

        titles = self._search("algèbre")

        self.assertEqual(titles.count(self.lesson.title), 1)

    def test_many_themes_and_keywords_do_not_multiply_results(self):
        # Reproduit le motif de fan-out constaté en production (65 thèmes × 43 mots-
        # clés = 2795 lignes fantômes sur une seule Lesson) à plus petite échelle -
        # garde-fou contre une régression vers un JOIN qui recréerait le problème.
        self.lesson.themes.add(*(Tag.objects.create(name=f"theme-{i}") for i in range(15)))
        self.lesson.mots_cles_recherche.add(*(Tag.objects.create(name=f"motcle-{i}") for i in range(15)))

        titles = self._search("2022")

        self.assertEqual(titles, [self.lesson.title])


class CoursSearchApiTests(TestCase):
    """`?search=` sur /catalog/cours/ - même correction que LessonSearchApiTests
    (Exists() plutôt qu'un JOIN sur tags, voir catalog.views.CoursListView)."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cours = Cours.objects.create(
            titre="Résoudre une équation du second degré", subject=subject, statut=StatutContenu.VALIDE,
            content_markdown="Discriminant et racines.",
        )
        self.cours.tags.set([Tag.objects.create(name="discriminant")])

    def _search(self, term):
        response = self.client.get(reverse("catalog:cours-list"), {"search": term})
        return [item["titre"] for item in response.json()["results"]]

    def test_matches_on_titre(self):
        self.assertIn(self.cours.titre, self._search("second degré"))

    def test_matches_on_content_markdown(self):
        self.assertIn(self.cours.titre, self._search("Discriminant"))

    def test_matches_on_tag(self):
        self.assertIn(self.cours.titre, self._search("discriminant"))

    def test_no_duplicate_when_title_and_tag_both_match(self):
        titles = self._search("discriminant")
        self.assertEqual(titles.count(self.cours.titre), 1)


class DoubleJsonEscapingRepairTests(TestCase):
    """Filet de sécurité mécanique pour un bug récurrent de double échappement JSON
    observé sur une bonne partie du corpus ingest/ (fichiers régénérés hors de ce
    process en cours de session, potentiellement à nouveau doublement échappés à
    chaque régénération - voir catalog.ingestion._repair_double_json_escaping) :
    "\\n" littéral au lieu d'un vrai saut de ligne, backslashes de commandes LaTeX
    doublés. La correction doit se faire à l'ingestion (pas seulement sur les
    fichiers source, qui peuvent être défaits par la régénération externe)."""

    def test_repairs_double_escaped_newlines_and_latex(self):
        payload = _exercise_payload("bac-maths-2024")
        # Simule l'etat de `data` tel que recu par ingest_exercise (deja passe une
        # fois par json.loads du fichier source doublement echappe) : un saut de
        # ligne y apparait comme 1 seul backslash litteral + "n" (2 caracteres,
        # jamais un vrai octet de saut de ligne a ce stade), une commande LaTeX comme
        # "\\mathbb" y apparait avec 2 backslashes litteraux (json.loads a deja
        # reduit les 4 backslashes bruts du fichier a 2) - profondeurs differentes,
        # voir _repair_double_json_escaping.
        one_backslash = "\\"
        two_backslashes = one_backslash * 2
        payload["questions"][0]["corrige_markdown"] = (
            f"### Rappel de methode{one_backslash}nOn utilise "
            f"${two_backslashes}mathbb{{R}}$.{one_backslash}n{one_backslash}n### Corrige{one_backslash}n4."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertIn("\n", question.corrige_markdown)
        self.assertNotIn("\\n", question.corrige_markdown)
        self.assertIn("$\\mathbb{R}$", question.corrige_markdown)
        self.assertNotIn("\\\\mathbb", question.corrige_markdown)
        self.assertTrue(any("doublement échappé" in note for note in exercise.incertitudes))

    def test_never_touches_already_correct_content_with_reserved_json_letters(self):
        # \bar, \tan, \theta, \forall, \rightarrow, \underline commencent tous par une
        # lettre que JSON reserve a un caractere d'echappement (b/t/n/f/r/u) - mais la
        # correction ne passe plus par json.loads, donc ces lettres reservees ne
        # jouent plus aucun role : aucun de ces backslashes n'est double, et aucun
        # n'est un "\n" litteral, donc le filet ne se declenche meme pas.
        payload = _exercise_payload("bac-maths-2024")
        # Titre déjà présent : évite de déclencher _repair_missing_exercise_heading
        # (hors-sujet ici, testerait un 2e filet de sécurité en même temps que celui-ci).
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        latex_content = (
            "Soit $\\bar z$, $\\tan\\theta$, $\\forall x$, $f:\\mathbb R\\rightarrow\\mathbb R$ "
            "et $\\underline{u_n}$."
        )
        payload["questions"][0]["corrige_markdown"] = latex_content

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(question.corrige_markdown, latex_content)
        self.assertEqual(exercise.incertitudes, [])

    def test_repairs_a_newline_even_when_the_same_field_has_a_straight_quote_citation(self):
        # Un guillemet droit de citation en prose ("...", voir markdown.ts
        # STRAIGHT_QUOTE_RE - une convention légitime, pas une corruption) ne doit pas
        # empêcher de corriger le vrai saut de ligne présent plus loin dans le même
        # champ - la substitution directe (pas de ré-encapsulage JSON) ignore
        # totalement les guillemets, donc ce cas ne peut plus jamais échouer.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        payload["questions"][0]["corrige_markdown"] = (
            f'### Rappel de methode{one_backslash}nOn utilise le théorème "des valeurs intermédiaires".'
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertIn("\n", question.corrige_markdown)
        self.assertNotIn("\\n", question.corrige_markdown)
        self.assertIn('"des valeurs intermédiaires"', question.corrige_markdown)

    def test_never_mangles_commands_starting_with_lowercase_n(self):
        # Reproduit bac-c-maths-2017-cameroun (leçon 719) : un vrai saut de ligne (qui
        # declenche legitimement la correction) cohabite dans le meme champ avec
        # \neq/\nabla/\notin, qui partagent leur premiere lettre apres le backslash
        # avec ce meme signal. Sans la negative lookahead sur la minuscule suivante,
        # une correction a 2 couches (frequente sur ce fichier) finit, apres avoir
        # correctement reduit "\\neq" a "\neq", par relire CE "\neq" comme "\n" (saut
        # de ligne) suivi de "eq" au tour suivant de la boucle - une commande deja
        # correcte se retrouve coupee en deux par un vrai octet de saut de ligne.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        two_backslashes = one_backslash * 2
        payload["questions"][0]["corrige_markdown"] = (
            f"### Rappel de methode{one_backslash}nOn calcule le produit vectoriel.{one_backslash}n{one_backslash}n"
            f"### Corrige{one_backslash}nComme ${two_backslashes}vec n_1{two_backslashes}wedge{two_backslashes}vec n_2"
            f"{two_backslashes}neq{two_backslashes}vec0$, les vecteurs ne sont pas colinéaires."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertIn("\\neq\\vec0", question.corrige_markdown)
        self.assertIn("### Corrige\nComme", question.corrige_markdown)

    def test_repairs_two_layers_of_escaping_on_the_same_field(self):
        # Reproduit bac-c-maths-2017/2019-cameroun (lecons 719/720) : certains champs
        # ont ete echappes DEUX fois de trop, pas une seule - un vrai saut de ligne y
        # apparait comme 2 backslashes litteraux + "n", pas 1. Une seule passe y
        # laisserait "\n" litteral residuel (encore 1 couche en trop), a tort detecte
        # comme "toujours casse" si la correction ne boucle pas.
        payload = _exercise_payload("bac-maths-2024")
        two_backslashes = "\\" * 2
        payload["questions"][0]["corrige_markdown"] = f"### Rappel de methode{two_backslashes}nOn calcule."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertIn("\n", question.corrige_markdown)
        self.assertNotIn("\\n", question.corrige_markdown)

    def test_repairs_newline_around_a_latex_matrix_without_breaking_row_separators(self):
        # Reproduit bac-c-e-maths-2025-cameroun (leçon 724, exercice 1, question 1) :
        # un champ avec un vrai saut de ligne corrompu ET une matrice pmatrix dont les
        # séparateurs de ligne ("\\" - 2 backslashes, contenu déjà correct) et les
        # commandes \begin/\end (1 backslash, contenu déjà correct) doivent rester
        # intacts. \end{...} commence par "e", qui n'est pas un échappement JSON
        # valide (" \ / b f n r t u) : l'ancienne version (ré-encapsulage + json.loads)
        # échouait avec JSONDecodeError dès la 1ère itération sur tout champ contenant
        # une matrice, laissant le saut de ligne non corrigé.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        two_backslashes = one_backslash * 2
        payload["questions"][0]["corrige_markdown"] = (
            f"### Corrige{one_backslash}n$$A={one_backslash}begin{{pmatrix}}1&2&0"
            f"{two_backslashes}-1&0&2{two_backslashes}2&-1&-5{one_backslash}end{{pmatrix}}$${one_backslash}n"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertTrue(question.corrige_markdown.startswith("### Corrige\n$$A="))
        self.assertIn(
            r"\begin{pmatrix}1&2&0\\-1&0&2\\2&-1&-5\end{pmatrix}$$",
            question.corrige_markdown,
        )
        self.assertTrue(question.corrige_markdown.endswith("\n"))

    def test_never_mangles_nearrow_inside_a_display_math_block(self):
        # Reproduit bac-d-maths-1985/1989/1991-cameroun (et d'autres épreuves du
        # corpus) : "\nearrow" (commande légitime d'un tableau de variations) à
        # l'intérieur d'un "$$...$$" (maths "display") était mutilé en un saut de
        # ligne réel suivi de "earrow" en texte brut - voir _is_inside_math_zone.
        # L'ancienne version comptait chaque caractère "$" séparément : juste après
        # l'ouverture "$$", 2 "$" déjà vus (compte PAIR) faisait croire à tort qu'on
        # était HORS zone de maths, où "\n" est toujours traité comme un vrai saut de
        # ligne quelle que soit la lettre suivante.
        payload = _exercise_payload("bac-maths-2024")
        # Titre déjà présent : évite de déclencher _repair_missing_exercise_heading.
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["corrige_markdown"] = (
            r"$$\begin{array}{|c|c|c|}\hline x&-\infty\nearrow&+\infty\\\hline\end{array}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"$$\begin{array}{|c|c|c|}\hline x&-\infty\nearrow&+\infty\\\hline\end{array}$$",
        )
        self.assertEqual(exercise.incertitudes, [])

    def test_repairs_a_newline_followed_by_a_lowercase_word_outside_math(self):
        # Reproduit bac-c-e-maths-2025-cameroun (leçon 724, exercice 1, question 4b) :
        # un titre "### Rappel de methode" suivi d'une phrase commençant par une
        # variable en minuscule ("e1 appartient..."), donc HORS de toute zone de maths
        # ($...$). Le "\n" y reste à tort littéral si on se fie uniquement à la casse
        # de la lettre suivante (comme pour \neq/\nabla) : aucune commande LaTeX ne
        # s'utilise en dehors d'une zone de maths dans ce corpus, donc "\n" y est
        # toujours un vrai saut de ligne, quelle que soit la lettre suivante.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        payload["questions"][0]["corrige_markdown"] = (
            f"### Rappel de methode{one_backslash}ne1 appartient a ker f si f(e1)=0."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown, "### Rappel de methode\ne1 appartient a ker f si f(e1)=0."
        )

    def test_preserves_a_matrix_row_separator_followed_by_a_single_letter_variable(self):
        # Reproduit bac-c-e-maths-2025-cameroun (leçon 724, exercice 1, question 4c) :
        # un système d'équations dont la 3e ligne commence par la variable isolée "a"
        # juste après le séparateur de ligne LaTeX ("\\", contenu déjà correct). Une
        # seule lettre après la paire de backslashes ne suffit pas à la faire
        # ressembler à une commande LaTeX doublée (aucune commande standard ne fait 1
        # lettre) - elle doit rester intacte, pas être réduite à "\a" (rendu cassé
        # constaté en direct sur /epreuves/724/lire).
        payload = _exercise_payload("bac-maths-2024")
        two_backslashes = "\\" * 2
        payload["questions"][0]["corrige_markdown"] = (
            f"Soit ${two_backslashes}begin{{cases}}2a-b+4c=1{two_backslashes}"
            f"-a+b=-3{two_backslashes}a-2b-2c=7{two_backslashes}end{{cases}}$."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"Soit $\begin{cases}2a-b+4c=1\\-a+b=-3\\a-2b-2c=7\end{cases}$.",
        )

    def test_preserves_a_matrix_row_separator_immediately_followed_by_a_command(self):
        # Reproduit Proposition-Corrigé-Maths-BACC-C-E-2021 (leçons 634 et,
        # similairement, 697/716/685) : un séparateur de ligne LaTeX (2 backslashes,
        # déjà correct) directement suivi d'une commande à backslash simple (ici
        # \sqrt3, sans espace) forme une suite de 3 backslashes consécutifs, déjà
        # correcte, jamais corrompue - une longueur impaire est la preuve
        # mathématique qu'aucune couche d'échappement en trop n'a pu s'appliquer ici
        # (une corruption double TOUJOURS, donc produit une longueur paire). Une
        # version précédente réduisait à tort les 2 derniers des 3 backslashes,
        # produisant "\\sqrt3" au lieu du "\\\sqrt3" correct (rendu cassé constaté en
        # direct sur /epreuves/723/lire).
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        three_backslashes = one_backslash * 3
        payload["questions"][0]["corrige_markdown"] = (
            f"Sommets : $B_1{one_backslash}begin{{pmatrix}}1{three_backslashes}"
            f"sqrt3{one_backslash}end{{pmatrix}}$."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"Sommets : $B_1\begin{pmatrix}1\\\sqrt3\end{pmatrix}$.",
        )

    def test_repairs_the_affected_field_without_touching_a_sibling_reserved_letter_field(self):
        # Un exercice avec un vrai "\n" litteral (question 1, a corriger) ET du LaTeX
        # deja correct a lettre reservee JSON (question 2, jamais a toucher) dans le
        # meme JSON : le garde-fou est par champ (voir _unescape_one_json_layer), pas
        # par document entier - la question 1 doit etre corrigee, la question 2
        # laissee bit pour bit identique. Cas realiste : un document melange souvent
        # un champ a corriger et un champ deja correct du meme genre.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        payload["questions"][0]["corrige_markdown"] = f"### Rappel de methode{one_backslash}nOn calcule."
        payload["questions"].append({
            "numero": "2", "enonce_markdown": "Énoncé 2.",
            "corrige_markdown": "Soit $\\theta$ un angle.",
        })

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        questions = list(exercise.questions.order_by("ordre"))
        self.assertIn("\n", questions[0].corrige_markdown)
        self.assertNotIn("\\n", questions[0].corrige_markdown)
        self.assertEqual(questions[1].corrige_markdown, "Soit $\\theta$ un angle.")
        self.assertTrue(any("doublement échappé" in note for note in exercise.incertitudes))

    def test_repairs_a_newline_glued_to_a_single_letter_row_label_inside_math(self):
        # Reproduit bac-c-maths-1987 à 1992/bac-d-maths-2007/bac-c-maths-probatoire-2014
        # (tableaux de variations) : contrairement à \neq/\nabla/\nearrow/\notin/\nu (une
        # suite de minuscules PRÉCISE, jamais juste "commence par une minuscule"), un vrai
        # saut de ligne collé à l'étiquette d'une seule lettre de la ligne suivante
        # ("\nf" pour f(x), "\nx" pour la ligne x, "\ng", "\na") restait à tort protégé par
        # l'ancienne version (qui ne regardait que LA lettre suivante, pas le mot entier).
        payload = _exercise_payload("bac-maths-2024")
        b1 = "\\"
        b2 = b1 * 2
        payload["questions"][0]["corrige_markdown"] = (
            f"$${b1}begin{{array}}{{c|ccc}}x & 0 & & +{b1}infty{b2}"
            f"{b1}hline{b1}nf'(x) & & + &{b2}"
            f"{b1}hline{b1}nf(x) & -{b1}infty & {b1}nearrow & "
            f"{b1}end{{array}}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertIn(f"{b1}hline\nf'(x)", question.corrige_markdown)
        self.assertIn(f"{b1}hline\nf(x)", question.corrige_markdown)
        # \nearrow (commande légitime, mot entier "earrow") doit rester intact à côté.
        self.assertIn(f"{b1}nearrow", question.corrige_markdown)
        self.assertNotIn(f"{b1}nf", question.corrige_markdown)

    def test_never_mangles_nu_the_greek_letter(self):
        # \nu (fréquence en physique, voir "conditions-de-l-emission-photoelectrique")
        # est le seul cas légitime où le mot entier après le backslash+n ne fait qu'UNE
        # lettre - doit rester protégé même sous la nouvelle règle "mot EXACT, pas préfixe".
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        payload["questions"][0]["corrige_markdown"] = f"$E={one_backslash}nu h$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(question.corrige_markdown, r"$E=\nu h$.")

    def test_repairs_a_newline_followed_by_a_french_word_starting_with_u_inside_math(self):
        # "mot EXACT, pas préfixe" (voir _REAL_LOWERCASE_N_LATEX_WORDS) : un vrai saut de
        # ligne suivi du mot français "utilise" ne doit PAS être confondu avec "\nu" (la
        # lettre grecque) suivi de "tilise" - KaTeX lui-même lirait "nutilise" comme un
        # unique nom de commande indéfini, jamais "nu"+"tilise" séparément, donc seule la
        # correspondance sur le mot ENTIER (pas un préfixe) donne le bon résultat ici.
        payload = _exercise_payload("bac-maths-2024")
        one_backslash = "\\"
        payload["questions"][0]["corrige_markdown"] = f"$x=1{one_backslash}nutilise le théorème.$"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(question.corrige_markdown, "$x=1\nutilise le théorème.$")


class MissingMatrixRowSeparatorRepairTests(TestCase):
    """Filet de sécurité mécanique pour une erreur d'AUTEUR distincte du double
    échappement JSON (voir DoubleJsonEscapingRepairTests ci-dessus) : un séparateur de
    ligne LaTeX ("\\\\", 2 backslashes) écrit avec un seul backslash à l'intérieur d'un
    environnement matriciel (cases/pmatrix/...). Aucune commande LaTeX standard ne
    commence par un chiffre ou un signe moins juste après le backslash - voir
    catalog.ingestion._repair_missing_matrix_row_separators. Reproduit
    bac-c-e-maths-2024-cameroun (leçon 723, exercice 2, question 1) : rendu affichant
    "\\2a+b+3c=0" et "\\-a+b-3c=0" en toutes lettres au lieu d'un saut de ligne."""

    def test_doubles_a_single_backslash_before_a_digit_inside_a_cases_block(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["corrige_markdown"] = (
            r"Le système : $\begin{cases}a+2b=0&(L_1)\2a+b+3c=0&(L_2)\-a+b-3c=0&(L_3)\end{cases}$."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"Le système : $\begin{cases}a+2b=0&(L_1)\\2a+b+3c=0&(L_2)\\-a+b-3c=0&(L_3)\end{cases}$.",
        )
        self.assertTrue(any("Séparateur de ligne LaTeX manquant" in note for note in exercise.incertitudes))

    def test_doubles_a_single_backslash_before_a_bare_digit_inside_a_pmatrix(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["corrige_markdown"] = r"Vérification : $\begin{pmatrix}0\0\0\end{pmatrix}$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(question.corrige_markdown, r"Vérification : $\begin{pmatrix}0\\0\\0\end{pmatrix}$.")

    def test_never_touches_a_legitimate_single_backslash_command_inside_a_matrix(self):
        # \sqrt, \times commencent par une lettre, jamais par un chiffre ou un signe
        # moins - ne doivent jamais être touchés par ce filet.
        payload = _exercise_payload("bac-maths-2024")
        # Titre déjà présent : évite de déclencher _repair_missing_exercise_heading.
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["corrige_markdown"] = (
            r"$\begin{pmatrix}\sqrt2\\3\times4\end{pmatrix}$ déjà correct."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown, r"$\begin{pmatrix}\sqrt2\\3\times4\end{pmatrix}$ déjà correct."
        )
        self.assertEqual(exercise.incertitudes, [])

    def test_never_touches_content_outside_a_recognized_matrix_environment(self):
        # Un backslash isolé suivi d'un chiffre en dehors de tout environnement
        # matriciel n'est pas touché (portée volontairement restreinte aux blocs
        # cases/pmatrix/... reconnus, pour ne jamais risquer un "\-" de prose - voir
        # docstring de _repair_missing_matrix_row_separators).
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["corrige_markdown"] = r"Texte isolé : a\2b sans environnement."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(question.corrige_markdown, r"Texte isolé : a\2b sans environnement.")


class GluedHlineRepairTests(TestCase):
    """Filet de sécurité mécanique pour une erreur d'AUTEUR distincte des deux
    précédentes : "\\hline" collé sans espace au token qui suit dans un tableau de
    variations - voir catalog.ingestion._repair_glued_hline. Reproduit
    bac-d-maths-1985/1989-cameroun : rendu KaTeX en échec ("Undefined control
    sequence") sur "\\hlinex" / "\\hlineV_1V_2" au lieu de "\\hline x" / "\\hline
    V_1V_2"."""

    def test_inserts_a_space_between_hline_and_a_glued_letter(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["corrige_markdown"] = (
            r"$$\begin{array}{|c|c|}\hlinex & 1\\\hline\end{array}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"$$\begin{array}{|c|c|}\hline x & 1\\\hline\end{array}$$",
        )
        self.assertTrue(any(r"\hline collé" in note for note in exercise.incertitudes))

    def test_never_touches_a_correctly_spaced_hline(self):
        payload = _exercise_payload("bac-maths-2024")
        # Titre déjà présent : évite de déclencher _repair_missing_exercise_heading.
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["corrige_markdown"] = (
            r"$$\begin{array}{|c|c|}\hline x & 1\\\hline\end{array}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"$$\begin{array}{|c|c|}\hline x & 1\\\hline\end{array}$$",
        )
        self.assertEqual(exercise.incertitudes, [])


class NarrowArrayColumnsRepairTests(TestCase):
    """Filet de sécurité mécanique pour une erreur d'AUTEUR récurrente sur les tableaux
    de variations à plusieurs points de rupture : le spécificateur de colonnes d'un
    \\begin{array} sous-compte les colonnes réellement utilisées par les lignes - voir
    catalog.ingestion._repair_narrow_array_columns. Reproduit bac-d-maths-1991-cameroun
    (KaTeX : "Extra alignment tab has been changed to \\cr")."""

    def test_widens_the_column_spec_to_match_the_longest_row(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["corrige_markdown"] = (
            r"$$\begin{array}{|c|ccc|}\hline x&-\infty&&0&&+\infty\\\hline\end{array}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"$$\begin{array}{|c|ccccc|}\hline x&-\infty&&0&&+\infty\\\hline\end{array}$$",
        )
        self.assertTrue(any("Spécificateur de colonnes" in note for note in exercise.incertitudes))

    def test_never_narrows_or_touches_an_already_matching_spec(self):
        payload = _exercise_payload("bac-maths-2024")
        # Titre déjà présent : évite de déclencher _repair_missing_exercise_heading.
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["corrige_markdown"] = (
            r"$$\begin{array}{|c|c|}\hline x_i & 0\\\hline\end{array}$$"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        question = exercise.questions.first()
        self.assertEqual(
            question.corrige_markdown,
            r"$$\begin{array}{|c|c|}\hline x_i & 0\\\hline\end{array}$$",
        )
        self.assertEqual(exercise.incertitudes, [])


class MissingExerciseHeadingRepairTests(TestCase):
    """Filet de sécurité mécanique pour une erreur d'AUTEUR massive et récurrente (280
    des 491 exercices du corpus au 2026-08-03, pas un incident isolé) : le titre
    "**Exercice N**"/"**Problème**" absent en tête de l'énoncé - voir
    catalog.ingestion._repair_missing_exercise_heading. Lesson._render_exercise_block()
    n'injecte jamais ce titre lui-même (décision volontaire, voir sa docstring), donc
    sans ce filet l'épreuve entière perd ses repères "Exercice 1"/"Problème" côté
    lecture. Reproduit bac-d-maths-1994 à 1997, 1998, 2000, 2001, 2002, 2004-cameroun."""

    def test_injects_a_heading_with_points_for_a_numeric_exercice_without_one(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["points"] = 4

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Exercice 1 (4 points)**")
        self.assertTrue(exercise.enonce_markdown.startswith("**Exercice 1 (4 points)**"))
        self.assertTrue(any("Titre" in note for note in exercise.incertitudes))

    def test_injects_a_heading_without_points_when_points_is_absent(self):
        payload = _exercise_payload("bac-maths-2024")

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Exercice 1**")

    def test_injects_probleme_heading_for_numero_exercice_probleme(self):
        payload = _exercise_payload("bac-maths-2024", numero="Probleme")
        payload["points"] = 12

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Problème (12 points)**")

    def test_preserves_existing_intro_after_the_injected_heading(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "Une urne contient 12 billes."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Exercice 1**\n\nUne urne contient 12 billes.")

    def test_never_touches_an_intro_that_already_has_a_heading(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1 (4 points)**\n\nUne urne contient 12 billes."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Exercice 1 (4 points)**\n\nUne urne contient 12 billes.")
        self.assertEqual(exercise.incertitudes, [])

    def test_never_touches_when_the_heading_is_on_the_first_question_and_intro_is_empty(self):
        # enonce_intro_markdown vide (pas de préambule partagé) : le titre peut être
        # porté directement par la première Question - voir bac-c-maths-2015-cameroun.
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["enonce_markdown"] = "**Exercice 1 (4 points)**\n\nCalculer f'(x)."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "")
        self.assertEqual(exercise.incertitudes, [])

    def test_never_guesses_for_an_ambiguous_numero_exercice(self):
        # "Probleme-IIA" (ou "Section I", "B" seul...) : plusieurs Exercise de ce type
        # peuvent coexister sur la même épreuve (voir bac-c-maths-1985-cameroun) - leur
        # injecter à tous le même titre générique créerait des repères dupliqués/faux,
        # pires que l'absence de titre. Le filet doit rester silencieux dans ce cas.
        payload = _exercise_payload("bac-maths-2024", numero="Probleme-IIA")

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "")
        self.assertEqual(exercise.incertitudes, [])

    def test_never_injects_a_heading_in_front_of_a_part_marker(self):
        # Reproduit bac-c-maths-2017-cameroun : le Problème d'une épreuve scindé en deux
        # fichiers/Exercise ("exercice_4" = Partie A, "exercice_5" = Partie B,
        # numero_exercice="5" purement numérique). Injecter "**Exercice 5**" devant
        # "**Partie B**" ferait croire à tort à un 5e exercice indépendant plutôt qu'à
        # la suite du Problème précédent, cassant la numérotation visible (1, 2, 3,
        # Problème, Exercice 5).
        payload = _exercise_payload("bac-maths-2024", numero="5")
        payload["enonce_intro_markdown"] = "**Partie B**\n\nSoit $f$ une fonction."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Partie B**\n\nSoit $f$ une fonction.")
        # _flag_part_headers_in_intro se déclenche bien (à part entière, voir
        # PartHeaderInIntroSafetyNetTests) - seul le titre "Exercice N" ne doit pas
        # avoir été injecté par _repair_missing_exercise_heading.
        self.assertFalse(any("Titre" in note for note in exercise.incertitudes))

    def test_recognizes_an_unmarked_heading_and_injects_nothing(self):
        # Reproduit probatoire-c-d-chimie-2003-cameroun : le repère existe bien dans
        # l'intro, simplement en texte nu (ni "#" ni gras). L'ancienne détection, ancrée
        # sur "**", le manquait et injectait un SECOND repère juste au-dessus.
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "Exercice 1 (5 points) - hydrocarbures et isomérie"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "Exercice 1 (5 points) - hydrocarbures et isomérie")
        self.assertEqual(exercise.incertitudes, [])


class DuplicateExerciseHeadingDedupeTests(TestCase):
    """Même repère porté à la fois par l'intro et par la tête d'une question - doublon
    visible en lecture, puisque compile_exercise_from_questions concatène l'intro puis
    chaque enonce_markdown (201 questions sur 53 épreuves au scan du 2026-08-15). Voir
    catalog.ingestion_repairs._dedupe_exercise_heading."""

    def test_removes_the_heading_repeated_at_the_top_of_a_question(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "Exercice 1 (5 points) - hydrocarbures et isomérie"
        payload["questions"][0]["enonce_markdown"] = "**Exercice 1 (5 points)**\n\n1. Nommer le composé $A$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get().enonce_markdown, "1. Nommer le composé $A$.")
        self.assertEqual(exercise.enonce_intro_markdown, "Exercice 1 (5 points) - hydrocarbures et isomérie")
        self.assertEqual(exercise.enonce_markdown.count("Exercice 1"), 1)
        self.assertTrue(any("dédupliqué" in note for note in exercise.incertitudes))

    def test_matches_a_roman_numbered_heading_with_an_arabic_one(self):
        # L'intro numérote en arabe, la question en romain (constaté sur les épreuves
        # de chimie) : c'est le même exercice, donc le même doublon.
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["enonce_markdown"] = "**Exercice I : Chimie organique (5 pts)**\n\n1. Nommer $A$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.questions.get().enonce_markdown, "1. Nommer $A$.")

    def test_promotes_the_richer_heading_into_the_intro_without_losing_it(self):
        # Le sous-titre ("Chimie organique") n'existe que côté question : dédupliquer ne
        # doit pas le perdre, et le repère survivant reste dans l'intro (le sommaire du
        # lecteur s'y alimente - voir rendering.exercise_display_title).
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["enonce_markdown"] = "**Exercice I : Chimie organique (5 pts)**\n\n1. Nommer $A$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.enonce_intro_markdown, "**Exercice I : Chimie organique (5 pts)**")

    def test_keeps_the_intro_body_after_the_heading(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1 (5 points)**\n\nOn donne $M = 56\\,g/mol$."
        payload["questions"][0]["enonce_markdown"] = "**Exercice 1 (5 points)**\n\n1. Nommer $A$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.enonce_intro_markdown,
            "**Exercice 1 (5 points)**\n\nOn donne $M = 56\\,g/mol$.",
        )
        self.assertEqual(exercise.questions.get().enonce_markdown, "1. Nommer $A$.")

    def test_never_touches_a_question_whose_first_line_carries_real_content(self):
        # "**Section D: Essay (10 marks).** Write an essay..." : le repère et le début de
        # l'énoncé partagent la même ligne - la supprimer effacerait l'énoncé. Ici avec
        # un repère "Exercice" pour rester sur le cas que ce filet vise.
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["enonce_markdown"] = "**Exercice 1 (5 points).** Nommer le composé $A$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.questions.get().enonce_markdown,
            "**Exercice 1 (5 points).** Nommer le composé $A$.",
        )

    def test_never_touches_a_different_exercise_number(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**Exercice 1**"
        payload["questions"][0]["enonce_markdown"] = "**Exercice 2**\n\nÉnoncé de la partie suivante."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.questions.get().enonce_markdown,
            "**Exercice 2**\n\nÉnoncé de la partie suivante.",
        )

    def test_collapses_two_stacked_headings_inside_the_intro(self):
        # État hérité : l'ancien _repair_missing_exercise_heading injectait un repère
        # au-dessus d'un repère non balisé qu'il ne savait pas reconnaître. Les deux
        # fusionnent, en gardant le gras (seul lisible par le sommaire) et le texte le
        # plus informatif des deux.
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = (
            "**Exercice 1 (5 points)**\n\nExercice 1 (5 points) - hydrocarbures et isomérie"
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.enonce_intro_markdown,
            "**Exercice 1 (5 points) - hydrocarbures et isomérie**",
        )

    def test_never_collapses_a_real_sentence_starting_with_the_same_word(self):
        # "Exercice 2 étudie..." est une phrase d'énoncé, pas un second repère : la
        # supprimer effacerait du contenu.
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = (
            "**Exercice 2 (5 points)**\n\nExercice 2 étudie la réaction d'estérification."
        )

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.enonce_intro_markdown,
            "**Exercice 2 (5 points)**\n\nExercice 2 étudie la réaction d'estérification.",
        )

    def test_never_empties_the_intro_when_only_the_question_carries_the_heading(self):
        # Intro sans repère : celui de la question est alors le seul du lot (repli
        # documenté d'exercise_display_title) - le retirer viderait le sommaire.
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["enonce_markdown"] = "**Exercice 1 (4 points)**\n\nCalculer $f'(x)$."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(
            exercise.questions.get().enonce_markdown,
            "**Exercice 1 (4 points)**\n\nCalculer $f'(x)$.",
        )
        self.assertEqual(exercise.incertitudes, [])


class SeriesFromFolderNameMergeTests(TestCase):
    """Séries annoncées par le nom du dossier mais absentes du champ `serie` du JSON
    (62 dossiers / 244 fichiers au scan du 2026-08-15) - voir
    catalog.ingestion_repairs._merge_series_from_folder_name. Reproduit
    bac-c-d-chimie-2003-cameroun, rattachée à la seule Série C alors que l'épreuve est
    commune aux séries C et D, donc introuvable pour un candidat de Série D."""

    def _series_codes(self, exercise):
        return sorted(c.series.code for c in exercise.lesson.cursus.all() if c.series)

    def test_adds_the_series_the_json_omitted(self):
        payload = _exercise_payload("bac-c-d-chimie-2003-cameroun")
        payload["serie"] = "C"

        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/bac-c-d-chimie-2003-cameroun"),
        )

        self.assertEqual(self._series_codes(exercise), ["C", "D"])
        self.assertTrue(any("nom du dossier" in note for note in exercise.incertitudes))

    def test_never_removes_a_series_only_the_json_knows(self):
        # bac-c-maths-2019-cameroun : le JSON porte C et E quand le nom ne dit que "c" -
        # c'est le NOM qui est incomplet, la fusion doit rester purement additive.
        payload = _exercise_payload("bac-c-maths-2019-cameroun")
        payload["serie"] = "C, E"

        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/bac-c-maths-2019-cameroun"),
        )

        self.assertEqual(self._series_codes(exercise), ["C", "E"])
        self.assertFalse(any("nom du dossier" in note for note in exercise.incertitudes))

    def test_stays_silent_when_folder_and_json_already_agree(self):
        payload = _exercise_payload("bac-c-d-chimie-2003-cameroun")
        payload["serie"] = "C, D"

        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/bac-c-d-chimie-2003-cameroun"),
        )

        self.assertEqual(self._series_codes(exercise), ["C", "D"])
        self.assertFalse(any("nom du dossier" in note for note in exercise.incertitudes))

    def test_ignores_a_folder_token_that_is_not_a_known_series(self):
        # "abi" n'est pas un code de série (voir _SERIE_NOISE_SUFFIX_RE) : le filet doit
        # l'ignorer, jamais faire échouer une ingestion qui passait avant lui.
        payload = _exercise_payload("bac-a-abi-maths-2024-cameroun")
        payload["serie"] = "A"

        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/bac-a-abi-maths-2024-cameroun"),
        )

        self.assertEqual(self._series_codes(exercise), ["A"])

    def test_ignores_a_bepc_folder_without_series(self):
        payload = _exercise_payload("bepc-maths-2019-cameroun")
        payload["examen"] = "BEPC"
        payload.pop("serie")

        exercise, _ = ingest_exercise(
            payload, source_dir=Path("ingest/cm/bepc-maths-2019-cameroun"),
        )

        self.assertEqual(self._series_codes(exercise), [])


class PartHeaderInIntroSafetyNetTests(TestCase):
    """Filet de sécurité mécanique pour l'erreur de composition documentée dans
    SKILL.md ("Erreur déjà rencontrée") : un repère de partie ("Partie A", "II."...)
    casé dans enonce_intro_markdown plutôt que sur la première Question de cette
    partie - voir catalog.ingestion._flag_part_headers_in_intro. Reproduit le bug
    réel rencontré sur bac-c-e-maths-2000 (exercice 4) : le frontend n'affiche jamais
    le numero d'une Question dont le texte commence déjà par un nombre/une lettre
    isolés (voir Exercise._render_question_enonce), donc "Partie A" disparaissait
    purement et simplement pour le lecteur."""

    def test_flags_partie_header_left_in_intro(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "Contexte partagé.\n\n**Partie A : Étude (2 points).**"

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertTrue(any("repère de partie" in note for note in exercise.incertitudes))

    def test_flags_roman_numeral_header_left_in_intro(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "Contexte partagé.\n\n**II.** La suite de l'énoncé."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertTrue(any("repère de partie" in note for note in exercise.incertitudes))

    def test_does_not_flag_a_normal_intro(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["enonce_intro_markdown"] = "**PROBLÈME (11 points)**\n\nContexte partagé par tout l'exercice."

        exercise, _ = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024"))

        self.assertEqual(exercise.incertitudes, [])


class ForceReingestionTests(TestCase):
    """`ingest_exercise(..., force=True)` - le ré-import délibéré déclenché depuis
    l'admin quand une épreuve a été corrigée après sa première ingestion (voir
    ExerciseAdmin.reingerer_depuis_fichier)."""

    def setUp(self):
        self.source_dir = Path("ingest/cm/bac-maths-2024")

    def test_default_behavior_is_still_idempotent_skip(self):
        payload = _exercise_payload("bac-maths-2024")
        exercise, created = ingest_exercise(payload, source_dir=self.source_dir)
        self.assertTrue(created)

        payload["questions"][0]["enonce_markdown"] = "Texte modifié."
        same_exercise, created_again = ingest_exercise(payload, source_dir=self.source_dir)

        self.assertFalse(created_again)
        self.assertEqual(same_exercise.pk, exercise.pk)
        self.assertNotIn("Texte modifié.", same_exercise.questions.first().enonce_markdown)

    def test_force_replaces_existing_exercise_content(self):
        payload = _exercise_payload("bac-maths-2024")
        exercise, _ = ingest_exercise(payload, source_dir=self.source_dir)
        old_question_pk = exercise.questions.first().pk

        corrected = _exercise_payload("bac-maths-2024")
        corrected["questions"][0]["enonce_markdown"] = "Énoncé corrigé."
        corrected["questions"][0]["corrige_markdown"] = "Corrigé corrigé."

        new_exercise, created = ingest_exercise(corrected, source_dir=self.source_dir, force=True)

        self.assertTrue(created)
        self.assertEqual(new_exercise.lesson_id, exercise.lesson_id)
        # L'ancienne Question ne doit plus porter l'ancien texte, qu'elle ait été
        # recréée avec un nouveau pk ou (SQLite peut réutiliser un rowid libéré)
        # récupéré le même - seul le contenu final fait foi, pas l'identité du pk.
        self.assertFalse(Question.objects.filter(pk=old_question_pk, enonce_markdown="Énoncé.").exists())
        self.assertEqual(new_exercise.questions.count(), 1)
        self.assertEqual(new_exercise.questions.first().enonce_markdown, "Énoncé corrigé.")
        self.assertIn("Corrigé corrigé.", new_exercise.lesson.content_markdown)

    def test_force_preserves_cours_already_generated_from_a_rappel(self):
        payload = _exercise_payload("bac-maths-2024")
        payload["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-bac-maths-2024-ex1-q1-0", "competence": "Test", "contenu_markdown": "Contenu."},
        ]
        exercise, _ = ingest_exercise(payload, source_dir=self.source_dir)
        rappel = exercise.rappels_de_methode.get(external_id="rdm-bac-maths-2024-ex1-q1-0")
        cours = Cours.objects.create(external_id="cours-test", titre="Cours généré", subject=exercise.lesson.subject)
        rappel.cours = cours
        rappel.save(update_fields=["cours"])

        corrected = _exercise_payload("bac-maths-2024")
        corrected["questions"][0]["enonce_markdown"] = "Énoncé corrigé."
        corrected["questions"][0]["rappels_de_methode"] = [
            {"id": "rdm-bac-maths-2024-ex1-q1-0", "competence": "Test", "contenu_markdown": "Contenu."},
        ]
        new_exercise, _ = ingest_exercise(corrected, source_dir=self.source_dir, force=True)

        new_rappel = new_exercise.rappels_de_methode.get(external_id="rdm-bac-maths-2024-ex1-q1-0")
        self.assertEqual(new_rappel.cours_id, cours.id)
        self.assertTrue(new_rappel.cours_genere)

    def test_force_on_an_exercise_that_does_not_exist_yet_still_creates_it(self):
        payload = _exercise_payload("bac-maths-2024-nouveau")
        exercise, created = ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-2024-nouveau"), force=True)
        self.assertTrue(created)

    def test_force_deletes_old_figure_file_from_storage(self):
        """Une réingestion force doit retirer du storage le fichier de l'ancienne
        Figure, pas seulement sa ligne en base - sinon chaque correction relance via
        l'admin ("Réingérer depuis le fichier JSON source") laisse une image orpheline
        sur le disque/Spaces (voir _attach_figures/figure_upload_to)."""
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "figure1.png").write_bytes(b"fake-png-bytes")

            payload = _exercise_payload("bac-maths-2024")
            payload["figures"] = [{
                "id": "fig-1", "fichier": "figure1.png", "page_source": 1,
                "type": "courbe", "legende": "Courbe", "indispensable": True, "lisibilite": "bonne",
            }]
            payload["questions"][0]["enonce_markdown"] = "Lire fig-1 (figure1.png)."

            with override_settings(MEDIA_ROOT=tmp):
                exercise, _ = ingest_exercise(payload, source_dir=source_dir)
                old_path = exercise.figures.get(external_id="fig-1").image.name
                self.assertTrue(default_storage.exists(old_path))

                # La version corrigée n'a plus de figure : l'ancienne image doit
                # disparaître du storage, pas rester orpheline après le force.
                corrected = _exercise_payload("bac-maths-2024")
                new_exercise, _ = ingest_exercise(corrected, source_dir=source_dir, force=True)

                self.assertFalse(default_storage.exists(old_path))
            self.assertEqual(new_exercise.figures.count(), 0)


class CompressFigureImageTests(TestCase):
    """catalog.ingestion._compress_figure_image - voir l'audit UX, reco 5.2 : chaque
    figure est reconvertie en WebP et plafonnée en largeur au moment de la
    correction, jamais à la volée."""

    def _make_png_bytes(self, width, height, mode="RGB", color="red"):
        buffer = BytesIO()
        Image.new(mode, (width, height), color).save(buffer, format="PNG")
        return buffer.getvalue()

    def test_converts_to_webp(self):
        raw = self._make_png_bytes(100, 100)

        compressed, filename = _compress_figure_image(raw, "figure1.png")

        self.assertEqual(filename, "figure1.webp")
        self.assertEqual(Image.open(BytesIO(compressed)).format, "WEBP")

    def test_resizes_an_image_wider_than_the_maximum_preserving_aspect_ratio(self):
        raw = self._make_png_bytes(2400, 1200)

        compressed, _ = _compress_figure_image(raw, "figure1.png")

        result = Image.open(BytesIO(compressed))
        self.assertEqual((result.width, result.height), (1200, 600))

    def test_never_upscales_an_image_already_smaller_than_the_maximum(self):
        raw = self._make_png_bytes(300, 200)

        compressed, _ = _compress_figure_image(raw, "figure1.png")

        result = Image.open(BytesIO(compressed))
        self.assertEqual((result.width, result.height), (300, 200))

    def test_flattens_transparency_onto_a_white_background(self):
        buffer = BytesIO()
        Image.new("RGBA", (50, 50), (255, 0, 0, 0)).save(buffer, format="PNG")  # entièrement transparent

        compressed, _ = _compress_figure_image(buffer.getvalue(), "figure1.png")

        result = Image.open(BytesIO(compressed)).convert("RGB")
        self.assertEqual(result.getpixel((25, 25)), (255, 255, 255))

    def test_falls_back_to_the_original_bytes_and_filename_on_an_unreadable_file(self):
        # Un fichier corrompu ne doit jamais faire échouer l'ingestion de tout
        # l'exercice pour une seule figure - voir la docstring de la fonction.
        raw = b"pas-une-vraie-image"

        compressed, filename = _compress_figure_image(raw, "figure1.png")

        self.assertEqual(compressed, raw)
        self.assertEqual(filename, "figure1.png")


class ReingererDepuisFichierActionTests(TestCase):
    """L'action admin ExerciseAdmin.reingerer_depuis_fichier - reconstruit le chemin
    du fichier JSON source depuis epreuve_source + le pays, puis appelle
    ingest_exercise(force=True) dessus. Teste la méthode d'action directement
    (pattern standard pour tester une admin action Django) plutôt qu'en passant par
    le client HTTP, qui n'ajouterait que du bruit d'authentification/CSRF sans mieux
    couvrir la logique."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Test", subject=self.subject, lesson_type=LessonType.CORR,
            epreuve_source="bac-maths-2024.pdf", statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.exercise = Exercise.objects.create(lesson=self.lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        Question.objects.create(
            exercise=self.exercise, numero="1", ordre=1,
            enonce_markdown="Ancien énoncé.", corrige_markdown="Ancien corrigé.",
        )
        self.exercise.compile_from_questions()
        self.admin = ExerciseAdmin(Exercise, AdminSite())

    def _request(self):
        from django.contrib.sessions.middleware import SessionMiddleware

        request = RequestFactory().post("/admin/catalog/exercise/")
        SessionMiddleware(lambda r: None).process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        return request

    def _write_source_json(self, tmp, enonce_markdown="Nouvel énoncé.", corrige_markdown="Nouveau corrigé."):
        # Le sous-dossier doit s'appeler littéralement "ingest" : _country_code_from_path
        # (voir ingestion.py) dérive le pays du premier segment sous un dossier "ingest"
        # dans le chemin résolu - un tmpdir nu (sans ce repère) fait échouer la résolution
        # du pays en silence (IngestionError avalée par reingerer_depuis_fichier), ce qui
        # a fait échouer ce test malgré une implémentation correcte.
        source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
        source_dir.mkdir(parents=True)
        (source_dir / "bac-maths-2024_exercice_1.json").write_text(
            json.dumps({
                "epreuve_source": "bac-maths-2024.pdf", "numero_exercice": "1",
                "matiere": "Mathematiques", "serie": "C", "examen": "BAC",
                "questions": [{"numero": "1", "enonce_markdown": enonce_markdown, "corrige_markdown": corrige_markdown}],
            }),
            encoding="utf-8",
        )

    def test_reingests_and_replaces_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_source_json(tmp)
            with patch("catalog.admin.INGEST_DIR", Path(tmp) / "ingest"):
                self.admin.reingerer_depuis_fichier(self._request(), Exercise.objects.filter(pk=self.exercise.pk))

        new_exercise = Exercise.objects.get(lesson=self.lesson, numero_exercice="1")
        self.assertEqual(new_exercise.questions.first().enonce_markdown, "Nouvel énoncé.")
        self.assertIn("Nouveau corrigé.", new_exercise.lesson.content_markdown)

    def test_reports_error_when_source_file_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("catalog.admin.INGEST_DIR", Path(tmp)):
                request = self._request()
                self.admin.reingerer_depuis_fichier(request, Exercise.objects.filter(pk=self.exercise.pk))

        messages_text = [str(m) for m in get_messages(request)]
        self.assertTrue(any("introuvable" in m for m in messages_text))
        # L'exercice existant ne doit pas avoir été touché par une tentative échouée.
        self.assertTrue(Exercise.objects.filter(pk=self.exercise.pk).exists())

    def test_reports_error_when_epreuve_source_is_blank(self):
        self.lesson.epreuve_source = ""
        self.lesson.save(update_fields=["epreuve_source"])

        with tempfile.TemporaryDirectory() as tmp:
            with patch("catalog.admin.INGEST_DIR", Path(tmp)):
                request = self._request()
                self.admin.reingerer_depuis_fichier(request, Exercise.objects.filter(pk=self.exercise.pk))

        messages_text = [str(m) for m in get_messages(request)]
        self.assertTrue(any("epreuve_source vide" in m for m in messages_text))


class RunIngestionResilienceTests(TestCase):
    """Une erreur inattendue (pas seulement IngestionError) sur un fichier ne doit pas
    empêcher les fichiers suivants du lot d'être traités - régression : un DataError
    Postgres sur un exercice mal formé avait fait planter tout run_ingestion en cours
    de route (voir la normalisation QCM ci-dessus pour la cause initiale)."""

    def test_unexpected_exception_on_one_file_does_not_abort_the_batch(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        exercise = Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "exercice_1.json").write_text('{"numero_exercice": "1"}', encoding="utf-8")
            (source_dir / "exercice_2.json").write_text('{"numero_exercice": "2"}', encoding="utf-8")

            with patch("catalog.ingestion.ingest_exercise", side_effect=[ValueError("boom"), (exercise, True)]):
                report = run_ingestion(Path(tmp))

        self.assertEqual(report["created"], 1)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("boom", report["errors"][0])


class RunIngestionSkipsObsoleteFilesTests(TestCase):
    """Reproduit bac-c-e-maths-2015-cameroun_exercice_5.json : un fichier neutralisé
    intentionnellement (contenu dupliqué déjà fusionné ailleurs, suppression physique
    refusée par l'utilisateur - "questions": [] et "statut": "obsolete_fusionne")
    doit être ignoré silencieusement, jamais compté en erreur - voir run_ingestion."""

    def test_obsolete_statut_is_skipped_not_errored(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "exercice_5.json").write_text(
                json.dumps({
                    "epreuve_source": "bac-maths-2024.pdf", "numero_exercice": "5",
                    "matiere": "Mathematiques", "serie": "C", "examen": "BAC",
                    "questions": [], "statut": "obsolete_fusionne",
                }),
                encoding="utf-8",
            )

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["errors"], [])
        self.assertEqual(report["skipped"], 1)
        self.assertEqual(report["created"], 0)


class RunIngestionSkipsUnderscorePrefixedPathsTests(TestCase):
    """Tout composant de chemin préfixé par "_" (dossier ou fichier) est du tooling/état
    interne, jamais du contenu - voir catalog.ingestion.run_ingestion. "_quiz" (lots
    CompetenceItem du skill concepteur-quiz-competence, voir quiz.ingestion.run_ingestion)
    en est le cas d'origine ; généralisé après un cas réel : bac-blanc-d-ti-
    physique-2025-cameroun contenait un `_registry_dump.json` et un `_tmp_pages/` laissés
    par erreur dans l'arbre publié, faisant échouer ingest_exercise sur "Champs
    obligatoires manquants" à chaque ingestion pour une erreur qui n'en est pas une."""

    def test_quiz_batch_subfolder_is_never_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            quiz_dir = Path(tmp) / "ingest" / "_quiz" / "cm"
            quiz_dir.mkdir(parents=True)
            (quiz_dir / "derivation.json").write_text(
                json.dumps([{"theme": "dérivation", "matiere": "Mathematiques"}]), encoding="utf-8",
            )

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["files_found"], 0)
        self.assertEqual(report["errors"], [])

    def test_a_leading_underscore_file_is_never_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            exam_dir = Path(tmp) / "ingest" / "cm" / "bac-blanc-d-ti-physique-2025-cameroun"
            exam_dir.mkdir(parents=True)
            (exam_dir / "_registry_dump.json").write_text(
                json.dumps({"some": "internal state"}), encoding="utf-8",
            )

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["files_found"], 0)
        self.assertEqual(report["errors"], [])

    def test_a_leading_underscore_subfolder_is_never_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pages_dir = Path(tmp) / "ingest" / "cm" / "bac-blanc-d-ti-physique-2025-cameroun" / "_tmp_pages"
            tmp_pages_dir.mkdir(parents=True)
            (tmp_pages_dir / "stray.json").write_text(json.dumps({"not": "content"}), encoding="utf-8")

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["files_found"], 0)
        self.assertEqual(report["errors"], [])


class CleanEmDashQuestionTests(TestCase):
    """clean_em_dash doit nettoyer Question (nouvelle source du contenu) et recompiler
    Exercise, pas l'inverse - voir catalog.management.commands.clean_em_dash."""

    def test_cleans_question_and_recompiles_exercise(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        exercise = Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        dash = "—"
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1,
            enonce_markdown=f"Texte avec un tiret cadratin {dash} ici.", corrige_markdown=f"Corrige {dash} aussi.",
        )
        exercise.compile_from_questions()
        self.assertIn(dash, exercise.enonce_markdown)

        call_command("clean_em_dash", stdout=StringIO())

        exercise.refresh_from_db()
        question = exercise.questions.first()
        self.assertNotIn(dash, question.enonce_markdown)
        self.assertNotIn(dash, exercise.enonce_markdown)
        self.assertIn("-", exercise.enonce_markdown)


class DedupeQuestionEnonceTests(TestCase):
    """Unitaires sur _dedupe_question_enonce - voir catalog.ingestion."""

    def test_strips_shared_intro_prefix(self):
        result = _dedupe_question_enonce("Soit f(x) = x^2.\n\nCalculer f'(x).", "Soit f(x) = x^2.")
        self.assertEqual(result, "Calculer f'(x).")

    def test_strips_intro_prefix_even_with_heading(self):
        result = _dedupe_question_enonce(
            "Soit f(x) = x^2.\n\nCalculer f'(x).", "## Exercice 2 (5 points)\n\nSoit f(x) = x^2.",
        )
        self.assertEqual(result, "Calculer f'(x).")

    def test_leaves_enonce_untouched_when_no_prefix_match(self):
        result = _dedupe_question_enonce("Calculer f'(x).", "Soit g(x) = x^3.")
        self.assertEqual(result, "Calculer f'(x).")

    def test_leaves_enonce_untouched_when_no_intro(self):
        result = _dedupe_question_enonce("Calculer f'(x).", "")
        self.assertEqual(result, "Calculer f'(x).")

    def test_collapses_doubled_sub_question_label(self):
        self.assertEqual(_dedupe_question_enonce("(a) (a) Calculer f'(x).", ""), "(a) Calculer f'(x).")
        self.assertEqual(_dedupe_question_enonce("(3) (3) Calculer f'(x).", ""), "(3) Calculer f'(x).")

    def test_collapses_doubled_numbered_label(self):
        # Constaté en production : "1. 1. Calculer P(3)..." - même famille de doublon
        # que "(a) (a)" mais sans parenthèses, style liste numérotée.
        result = _dedupe_question_enonce("1. 1. Calculer $P(3)$. Que traduit ce résultat ?", "")
        self.assertEqual(result, "1. Calculer $P(3)$. Que traduit ce résultat ?")
        self.assertEqual(_dedupe_question_enonce("12. 12. Texte.", ""), "12. Texte.")


class CleanDuplicateQuestionTextCommandTests(TestCase):
    """clean_duplicate_question_text doit nettoyer Question déjà en base et
    recompiler Exercise/Lesson - voir catalog.management.commands.clean_duplicate_question_text."""

    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Test", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(cursus)

    def test_cleans_echoed_intro_and_doubled_label_then_recompiles(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, numero_exercice="1", statut=StatutContenu.VALIDE,
            enonce_intro_markdown="Soit f(x) = x^2.",
        )
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1,
            enonce_markdown="Soit f(x) = x^2.\n\n(a) (a) Calculer f'(x).", corrige_markdown="f'(x) = 2x.",
        )
        exercise.compile_from_questions()
        self.assertEqual(exercise.enonce_markdown.count("Soit f(x) = x^2."), 2)

        call_command("clean_duplicate_question_text", stdout=StringIO())

        exercise.refresh_from_db()
        question = exercise.questions.first()
        self.assertEqual(question.enonce_markdown, "(a) Calculer f'(x).")
        self.assertEqual(exercise.enonce_markdown.count("Soit f(x) = x^2."), 1)

    def test_does_not_touch_questions_without_duplication(self):
        exercise = Exercise.objects.create(lesson=self.lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1, enonce_markdown="Calculer f'(x).", corrige_markdown="f'(x) = 2x.",
        )

        call_command("clean_duplicate_question_text", stdout=StringIO())

        self.assertEqual(exercise.questions.get(numero="1").enonce_markdown, "Calculer f'(x).")


class TemoignageModelTests(TestCase):
    """Voir catalog.models.Temoignage - reco 8.3 de l'audit UX."""

    def test_publies_excludes_unpublished(self):
        Temoignage.objects.create(auteur_nom="Awa", contenu="Très utile.", est_publie=True)
        Temoignage.objects.create(auteur_nom="Marc", contenu="Brouillon pas encore relu.", est_publie=False)

        publies = list(Temoignage.objects.publies())

        self.assertEqual(len(publies), 1)
        self.assertEqual(publies[0].auteur_nom, "Awa")

    def test_defaults_to_unpublished(self):
        temoignage = Temoignage.objects.create(auteur_nom="Awa", contenu="Très utile.")
        self.assertFalse(temoignage.est_publie)

    def test_note_out_of_range_is_rejected(self):
        temoignage = Temoignage(auteur_nom="Awa", contenu="Très utile.", note=6)
        with self.assertRaises(ValidationError):
            temoignage.full_clean()


class TemoignageListApiTests(TestCase):
    """`GET /catalog/temoignages/` - ne doit jamais exposer un témoignage non publié."""

    def test_only_published_testimonials_are_returned(self):
        Temoignage.objects.create(auteur_nom="Awa", auteur_description="Terminale D", contenu="Top.", note=5, est_publie=True)
        Temoignage.objects.create(auteur_nom="Marc", contenu="Pas prêt.", est_publie=False)

        response = self.client.get(reverse("catalog:temoignage-list"))
        payload = response.json()

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["auteur_nom"], "Awa")
        self.assertEqual(payload[0]["auteur_description"], "Terminale D")
        self.assertEqual(payload[0]["note"], 5)

    def test_empty_when_nothing_published(self):
        response = self.client.get(reverse("catalog:temoignage-list"))
        self.assertEqual(response.json(), [])


class PlatformStatsApiTests(TestCase):
    """`GET /catalog/stats/` - uniquement des comptages de contenu réel, jamais
    d'effectifs d'abonnés/élèves (voir catalog.views.PlatformStatsView)."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")

    def test_counts_only_validated_content_in_active_countries(self):
        Lesson.objects.create(
            title="Corrigé validé", subject=self.subject, lesson_type=LessonType.CORR,
            epreuve_source="src", statut=StatutContenu.VALIDE,
        )
        Lesson.objects.create(
            title="Brouillon", subject=self.subject, lesson_type=LessonType.CORR,
            epreuve_source="src2", statut=StatutContenu.BROUILLON,
        )
        Lesson.objects.create(
            title="Fiche validée", subject=self.subject, lesson_type=LessonType.FICHE,
            statut=StatutContenu.VALIDE,
        )
        Cours.objects.create(external_id="c1", titre="Cours validé", subject=self.subject, statut=StatutContenu.VALIDE)

        inactive_country = Country.objects.create(code="TD", label="Tchad", actif=False)
        inactive_subject = Subject.objects.create(country=inactive_country, code="MATHS", label="Mathématiques")
        Lesson.objects.create(
            title="Pays inactif", subject=inactive_subject, lesson_type=LessonType.CORR,
            epreuve_source="src3", statut=StatutContenu.VALIDE,
        )

        response = self.client.get(reverse("catalog:platform-stats"))
        data = response.json()

        self.assertEqual(data["corriges_disponibles"], 1)
        self.assertEqual(data["cours_disponibles"], 1)
        self.assertEqual(data["pays_actifs"], Country.objects.filter(actif=True).count())
        self.assertNotIn("abonnes", data)
        self.assertNotIn("eleves", data)


class IngestionAdminBackgroundRunTests(TestCase):
    """Reproduit un blocage réel : le bouton "Lancer l'ingestion" de l'admin renvoyait
    "Internal Server Error" (page de gunicorn, pas une 500 Django) sur un dossier
    ingest/ de ~5 200 fichiers. Cause : run_ingestion tournait dans le thread de
    requête et dépassait le `--timeout 30` de gunicorn (voir backend/entrypoint.sh),
    qui tuait le worker en plein run - l'ingestion ayant déjà écrit en base, l'erreur
    ne disait rien de ce qui avait été fait. Le run part désormais dans un processus
    détaché et le rapport est relu sur disque (voir catalog.ingestion.queue_ingestion)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200077", password="x")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)
        self.url = reverse("admin:catalog_lesson_ingestion")

    def test_post_spawns_a_detached_process_instead_of_ingesting_inline(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "ingestion_report.json"
            with patch("catalog.ingestion.subprocess.Popen") as popen, \
                    patch("catalog.admin.read_ingestion_report", side_effect=lambda: read_ingestion_report(report_path)), \
                    patch("catalog.admin.queue_ingestion", side_effect=lambda p: queue_ingestion(p, report_path)), \
                    patch("catalog.ingestion.run_ingestion") as run:
                response = self.client.post(self.url)

                self.assertEqual(response.status_code, 302)
                run.assert_not_called()
                args = popen.call_args[0][0]
                self.assertIn("ingest_corrections", args)
                self.assertIn(str(report_path), args)

            # Le rapport "running" est écrit avant même que le processus démarre, pour
            # que la page affiche tout de suite l'état du run.
            self.assertEqual(read_ingestion_report(report_path)["status"], "running")

    def test_post_refuses_a_second_run_while_one_is_already_running(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "ingestion_report.json"
            write_ingestion_report(
                {"status": "running", "started_at": timezone.now().isoformat()}, report_path,
            )

            with patch("catalog.ingestion.subprocess.Popen") as popen, \
                    patch("catalog.admin.read_ingestion_report", side_effect=lambda: read_ingestion_report(report_path)):
                response = self.client.post(self.url, follow=True)

            popen.assert_not_called()
            self.assertTrue(any("déjà en cours" in str(m) for m in get_messages(response.wsgi_request)))

    def test_get_shows_the_last_report_and_stays_available_without_any_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "ingestion_report.json"

            with patch("catalog.admin.read_ingestion_report", side_effect=lambda: read_ingestion_report(report_path)):
                # Aucun run encore effectué : la page doit s'afficher quand même.
                self.assertEqual(self.client.get(self.url).status_code, 200)

                write_ingestion_report(
                    {
                        "status": "done", "started_at": timezone.now().isoformat(),
                        "finished_at": timezone.now().isoformat(), "files_found": 3, "created": 1,
                        "skipped": 1, "errors": ["fichier.json: JSON invalide"], "pdf_status": "done",
                    },
                    report_path,
                )
                response = self.client.get(self.url)

        self.assertContains(response, "JSON invalide")

    def test_command_writes_the_report_the_admin_page_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
            source_dir.mkdir(parents=True)
            (source_dir / "exercice_1.json").write_text(
                json.dumps(_exercise_payload("bac-maths-2024.pdf")), encoding="utf-8",
            )
            report_path = Path(tmp) / "ingestion_report.json"

            # generate_sujet_pdfs (Playwright) n'a rien à faire dans un test : seul
            # compte ici le rapport écrit par l'ingestion elle-même.
            with patch("catalog.management.commands.ingest_corrections.call_command"):
                call_command("ingest_corrections", str(Path(tmp) / "ingest"), report_json=str(report_path))

            report = read_ingestion_report(report_path)

        self.assertEqual(report["status"], "done")
        self.assertEqual(report["created"], 1)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["pdf_status"], "done")

    def test_command_reports_an_error_status_when_the_run_dies_in_one_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ingest").mkdir()
            report_path = Path(tmp) / "ingestion_report.json"

            with patch("catalog.management.commands.ingest_corrections.run_ingestion", side_effect=OSError("disque")):
                with self.assertRaises(OSError):
                    call_command("ingest_corrections", str(Path(tmp) / "ingest"), report_json=str(report_path))

            report = read_ingestion_report(report_path)

        self.assertEqual(report["status"], "error")
        self.assertIn("disque", report["detail"])


class EspagnolSubjectIngestionTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 5 fichiers (bepc-espagnol-2018-cameroun)
    échouaient à chaque run sur "Matière inconnue : 'Espagnol'" - l'espagnol, deuxième
    langue vivante examinée au BEPC camerounais, n'existait ni dans MATIERE_MAP ni au
    référentiel. Décision utilisateur du 2026-08-15 : Subject à part entière (voir
    catalog.ingestion.MATIERE_MAP et la migration 0044_seed_espagnol), jamais un alias
    vers ANGLAIS."""

    def test_espagnol_is_seeded_for_every_country(self):
        for country in Country.objects.all():
            self.assertTrue(
                Subject.objects.filter(country=country, code="ESPAGNOL").exists(),
                f"Subject ESPAGNOL manquante pour {country}",
            )

    def test_an_espagnol_exercise_is_ingested_under_its_own_subject(self):
        payload = _exercise_payload("bepc-espagnol-2018-cameroun.pdf")
        payload["matiere"] = "Espagnol"
        payload["examen"] = "bepc"
        payload.pop("serie", None)

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bepc-espagnol-2018-cameroun"
            source_dir.mkdir(parents=True)
            (source_dir / "exercice_1.json").write_text(json.dumps(payload), encoding="utf-8")

            report = run_ingestion(Path(tmp))

        self.assertEqual(report["errors"], [])
        self.assertEqual(report["created"], 1)
        lesson = Lesson.objects.get(epreuve_source="bepc-espagnol-2018-cameroun.pdf")
        self.assertEqual(lesson.subject.code, "ESPAGNOL")


class CoursSansRappelSourceTests(TestCase):
    """Reproduit un blocage d'ingestion réel : 87 fichiers cours (bac-a-anglais-2014 à
    2017-cameroun, 85 ; bac-c-maths-1986-cameroun, 2) échouaient à chaque run sur
    "RappelDeMethode introuvable". La passe cours avait généré un cours par QUESTION
    ("rdm-...-ex1-qI.3-0") quand la passe exercices n'émettait qu'un rappel par
    EXERCICE ("rdm-...-ex1-0") : du contenu réel, jamais publié. Le cours est désormais
    rattaché à son épreuve via source.epreuve_source (voir ingest_cours) - seul le lien
    rappel -> cours reste absent, faute de rappel où l'accrocher."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="ANGLAIS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="A")
        self.lesson = Lesson.objects.create(
            title="Anglais BAC A 2014", subject=self.subject, lesson_type=LessonType.CORR,
            epreuve_source="bac-a-anglais-2014-cameroun.pdf", statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)

    def _payload(self, rappel_id, epreuve_source="bac-a-anglais-2014-cameroun.pdf", cours_id="cours-for-vs-since"):
        return {
            "cours_id": cours_id,
            "source": {"rappel_id": rappel_id, "epreuve_source": epreuve_source},
            "meta": {"titre": "For vs since avec le present perfect", "matiere": "Anglais", "serie": "A"},
            "sections": [{"type": "definition", "titre": "Définition", "contenu": "For + durée."}],
        }

    def test_cours_is_published_under_its_epreuve_when_its_rappel_does_not_exist(self):
        cours, created = ingest_cours(self._payload("rdm-bac-a-anglais-2014-cameroun-ex1-qI.3-0"))

        self.assertTrue(created)
        self.assertEqual(cours.statut, StatutContenu.VALIDE)
        # Pays, matière et cursus hérités de l'épreuve, pas devinés.
        self.assertEqual(cours.subject, self.subject)
        self.assertEqual(list(cours.cursus.all()), [self.cursus])
        # Le seul manque assumé : aucun rappel ne pointe vers ce cours.
        self.assertFalse(RappelDeMethode.objects.filter(cours=cours).exists())

    def test_an_existing_rappel_is_still_linked_as_before(self):
        exercise = Exercise.objects.create(lesson=self.lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        rappel = RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-bac-a-anglais-2014-cameroun-ex1-0",
            competence="For vs since", contenu_markdown="...",
        )

        cours, _ = ingest_cours(self._payload("rdm-bac-a-anglais-2014-cameroun-ex1-0"))

        rappel.refresh_from_db()
        self.assertEqual(rappel.cours, cours)

    def test_an_unidentifiable_epreuve_still_fails_rather_than_attaching_at_random(self):
        with self.assertRaises(IngestionError) as ctx:
            ingest_cours(self._payload("rdm-inconnu-0", epreuve_source="epreuve-qui-nexiste-pas.pdf"))

        self.assertIn("epreuve_source", str(ctx.exception))
        self.assertFalse(Cours.objects.filter(external_id="cours-for-vs-since").exists())

    def test_the_epreuve_is_found_from_the_folder_when_the_json_does_not_name_it(self):
        # Cas majoritaire des 87 fichiers : 76 ne portent aucun `source.epreuve_source`.
        # Seuls les fichiers exercices du dossier le déclarent - voir _lesson_from_source_dir.
        payload = self._payload("rdm-bac-a-anglais-2014-cameroun-ex1-qI.3-0")
        payload["source"].pop("epreuve_source")

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "bac-a-anglais-2014-cameroun"
            source_dir.mkdir(parents=True)
            (source_dir / "exercice_1.json").write_text(
                json.dumps(_exercise_payload("bac-a-anglais-2014-cameroun.pdf")), encoding="utf-8",
            )

            cours, created = ingest_cours(payload, source_dir=source_dir)

        self.assertTrue(created)
        self.assertEqual(list(cours.cursus.all()), [self.cursus])

    def test_a_folder_mixing_several_epreuves_is_refused_rather_than_guessed(self):
        payload = self._payload("rdm-inconnu-0")
        payload["source"].pop("epreuve_source")

        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "ingest" / "cm" / "lot-melange"
            source_dir.mkdir(parents=True)
            for n, src in enumerate(["bac-a-anglais-2014-cameroun.pdf", "bac-a-anglais-2015-cameroun.pdf"]):
                (source_dir / f"exercice_{n}.json").write_text(
                    json.dumps(_exercise_payload(src)), encoding="utf-8",
                )

            with self.assertRaises(IngestionError):
                ingest_cours(payload, source_dir=source_dir)
