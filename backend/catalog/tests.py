import json
import tempfile
from io import StringIO
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

from unittest.mock import patch

from rest_framework.test import APIClient

from access.models import LectureProgress
from users.models import User

from .admin import ExerciseAdmin
from .ingestion import IngestionError, _country_code_from_path, ingest_cours, ingest_exercise, run_ingestion
from .ingestion_repairs import _dedupe_question_enonce
from .models import Cours, Country, Cursus, Difficulte, Examen, ExamenLabel, Exercise, Figure, Lesson, LessonType, Origine, Question, Series, StatutContenu, Subject, Tag, TypeReponse, figure_upload_to, resolve_examen_label
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
        self.assertEqual(Subject.objects.filter(country=bj).count(), 11)
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
        self.assertEqual(Subject.objects.filter(country=bj).count(), 11)
        self.assertEqual(Cursus.objects.filter(country=bj).count(), 15)

    def test_rejects_code_that_is_not_two_letters(self):
        with self.assertRaises(CommandError):
            self._run("ben", "Bénin")

    def test_does_not_touch_other_countries_referentiel(self):
        cm_subject_count = Subject.objects.filter(country__code="CM").count()
        self._run("bj", "Bénin")
        self.assertEqual(Subject.objects.filter(country__code="CM").count(), cm_subject_count)


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


class SitemapCountryFanOutTests(TestCase):
    """`/{code}` et `/{code}/cours` doivent apparaître une fois par pays - voir
    catalog.sitemap._PER_COUNTRY_PAGES (les fiches Lesson/Cours, elles, restent à
    une URL plate, inchangée)."""

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
        # Chimie comme deux matières distinctes alors que le référentiel les regroupe
        # en une seule Subject PHYSIQUE_CHIMIE, et "Langue française" est un synonyme
        # de FRANCAIS - voir MATIERE_MAP.
        for matiere, expected_code in [("Physique", "PHYSIQUE_CHIMIE"), ("Chimie", "PHYSIQUE_CHIMIE"), ("Langue française", "FRANCAIS")]:
            payload = self._payload(matiere=matiere)
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
