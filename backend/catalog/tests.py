from io import StringIO
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .ingestion import IngestionError, _country_code_from_path, ingest_exercise
from .models import Cours, Country, Cursus, Difficulte, Examen, ExamenLabel, Exercise, Lesson, LessonType, Question, Series, StatutContenu, Subject, Tag, TypeReponse, resolve_examen_label
from .sujet_pdf import _render_html


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
        Subject.objects.create(country=self.bj, code="MATHS", label="Mathématiques")
        response = self.client.get(reverse("catalog:subject-list"), {"country": "bj"})
        codes = [item["code"] for item in response.json()]
        self.assertEqual(codes, ["MATHS"])

    def test_cursus_clean_rejects_series_from_another_country(self):
        cm_series_c = Series.objects.get(country__code="CM", code="C")
        cursus = Cursus(country=self.bj, examen=Examen.BAC, series=cm_series_c)
        with self.assertRaises(ValidationError):
            cursus.full_clean()


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
        response = self.client.get(reverse("catalog:cursus-list"), {"country": "sn"})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], cursus.id)
        self.assertEqual(data[0]["examen_display"], "BFEM")


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
