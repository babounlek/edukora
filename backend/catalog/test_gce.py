from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from recherche import indexation, intention

from .ingestion import IngestionError, MATIERE_MAP, _resolve_cursus_list, _resolve_subject
from .libelles import libelle_cursus, libelle_series
from .models import (
    CODES_OFFICIELS_GCE,
    EXAMENS_GCE,
    SERIE_GCE_TECHNIQUE,
    Country,
    Cursus,
    Examen,
    ExamSession,
    Langue,
    Series,
    Subject,
    institution_officielle,
    langue_examen,
)
from .views import EXAMEN_RANG


class GceEnumTests(SimpleTestCase):
    def test_deux_niveaux_et_plus_de_code_unique(self):
        self.assertEqual(Examen.GCE_OL.label, "GCE O Level")
        self.assertEqual(Examen.GCE_AL.label, "GCE A Level")
        self.assertNotIn("GCE", Examen.values)
        self.assertEqual(EXAMENS_GCE, {Examen.GCE_OL, Examen.GCE_AL})

    def test_langue_par_examen(self):
        self.assertEqual(langue_examen(Examen.GCE_AL), Langue.EN)
        self.assertEqual(langue_examen(Examen.GCE_OL), Langue.EN)
        for francophone in (Examen.BEPC, Examen.PROBATOIRE, Examen.BAC, Examen.CAP, Examen.AUTRE):
            self.assertEqual(langue_examen(francophone), Langue.FR)

    def test_rangs_alignes_sur_le_niveau_scolaire(self):
        # O Level = niveau Probatoire, A Level = niveau BAC.
        self.assertEqual(EXAMEN_RANG[Examen.GCE_OL], EXAMEN_RANG[Examen.PROBATOIRE])
        self.assertEqual(EXAMEN_RANG[Examen.GCE_AL], EXAMEN_RANG[Examen.BAC])
        self.assertEqual(indexation.RANG_EXAMEN[Examen.GCE_OL], indexation.RANG_EXAMEN[Examen.PROBATOIRE])
        self.assertEqual(indexation.RANG_EXAMEN[Examen.GCE_AL], indexation.RANG_EXAMEN[Examen.BAC])

    def test_institution_officielle(self):
        self.assertEqual(institution_officielle("CM", Examen.GCE_OL), "Cameroon GCE Board")
        self.assertEqual(institution_officielle("CM", Examen.GCE_AL), "Cameroon GCE Board")
        self.assertEqual(institution_officielle("CM", "GCE"), "")

    def test_libelles_de_la_branche_technique(self):
        self.assertEqual(libelle_series([SERIE_GCE_TECHNIQUE]), "Technical")
        # Les séries francophones gardent leur libellé accordé.
        self.assertEqual(libelle_series(["C", "D"]), "Séries C et D")


class GceReferentielTests(TestCase):
    """Données semées par la migration 0063 (le Cameroun existe déjà dans la base de test)."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")

    def test_quatre_cursus_deux_niveaux_general_et_technique(self):
        cursus = Cursus.objects.filter(country=self.cm, examen__in=EXAMENS_GCE)
        self.assertEqual(cursus.count(), 4)
        for niveau in EXAMENS_GCE:
            self.assertTrue(Cursus.objects.filter(country=self.cm, examen=niveau, series__isnull=True).exists())
            self.assertTrue(
                Cursus.objects.filter(country=self.cm, examen=niveau, series__code=SERIE_GCE_TECHNIQUE).exists(),
            )

    def test_serie_technique_est_du_groupe_technique(self):
        serie = Series.objects.get(country=self.cm, code=SERIE_GCE_TECHNIQUE)
        self.assertEqual(serie.groupe, "TECHNIQUE")
        self.assertIsNone(serie.filiere_id)
        serie.full_clean()

    def test_matieres_gce_en_anglais_avec_codes_distincts(self):
        gce = Subject.objects.filter(country=self.cm, code__startswith="GCE_")
        self.assertGreaterEqual(gce.count(), 20)
        self.assertEqual(set(gce.values_list("langue", flat=True)), {Langue.EN})
        # Aucune matière francophone n'a changé de langue ni été écrasée.
        self.assertEqual(Subject.objects.get(country=self.cm, code="MATHS").langue, Langue.FR)
        self.assertEqual(Subject.objects.get(country=self.cm, code="MATHS").label, "Mathématiques")
        self.assertTrue(all(len(code) <= 20 for code in gce.values_list("code", flat=True)))

    def test_sessions_2026_dupliquees_sur_les_deux_niveaux(self):
        self.assertFalse(ExamSession.objects.filter(examen="GCE").exists())
        ol = ExamSession.objects.get(country=self.cm, examen=Examen.GCE_OL, annee=2026)
        al = ExamSession.objects.get(country=self.cm, examen=Examen.GCE_AL, annee=2026)
        self.assertEqual((ol.date_debut, ol.date_fin), (al.date_debut, al.date_fin))
        self.assertIsNotNone(al.date_fin)

    def test_compte_a_rebours_disponible_pour_les_deux_niveaux(self):
        for niveau in EXAMENS_GCE:
            cursus = Cursus.objects.get(country=self.cm, examen=niveau, series__isnull=True)
            resultat = ExamSession.compte_a_rebours_pour(cursus)
            self.assertIsNotNone(resultat)
            self.assertGreaterEqual(resultat["date_examen"], timezone.now().date())

    def test_le_cursus_gce_sans_contenu_n_est_pas_propose_aux_eleves(self):
        reponse = self.client.get(reverse("catalog:cursus-list"), {"country": "cm"})
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse([c for c in reponse.json() if c["examen"] in EXAMENS_GCE])

    def test_langue_du_cursus(self):
        self.assertEqual(Cursus.objects.filter(examen=Examen.GCE_AL).first().langue, Langue.EN)
        self.assertEqual(Cursus.objects.filter(examen=Examen.BAC).first().langue, Langue.FR)

    def test_libelle_cursus_technique(self):
        technique = Cursus.objects.select_related("series", "country").get(
            country=self.cm, examen=Examen.GCE_AL, series__code=SERIE_GCE_TECHNIQUE,
        )
        general = Cursus.objects.select_related("series", "country").get(
            country=self.cm, examen=Examen.GCE_AL, series__isnull=True,
        )
        self.assertEqual(libelle_cursus([technique]), "GCE A Level - Technical")
        self.assertEqual(libelle_cursus([general]), "GCE A Level")


class GceIngestionTests(TestCase):
    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        _resolve_cursus_list.cache_clear()

    def tearDown(self):
        _resolve_cursus_list.cache_clear()

    def _un(self, examen, serie=""):
        (cursus,) = _resolve_cursus_list(examen, serie, self.cm)
        return cursus

    def test_branche_generale_sans_serie(self):
        for brut, attendu in (("GCE_OL", Examen.GCE_OL), ("GCE Advanced Level", Examen.GCE_AL), ("A Level", Examen.GCE_AL)):
            cursus = self._un(brut)
            self.assertEqual(cursus.examen, attendu)
            self.assertIsNone(cursus.series_id)
        self.assertEqual(self._un("GCE_AL", "general").series_id, None)

    def test_branche_technique(self):
        cursus = self._un("GCE_OL", "Technical")
        self.assertEqual((cursus.examen, cursus.series.code), (Examen.GCE_OL, SERIE_GCE_TECHNIQUE))

    def test_gce_sans_niveau_est_refuse(self):
        with self.assertRaisesMessage(IngestionError, "sans niveau"):
            _resolve_cursus_list("GCE", "", self.cm)

    def test_serie_francophone_refusee_au_gce(self):
        with self.assertRaisesMessage(IngestionError, "inconnue pour le GCE"):
            _resolve_cursus_list("GCE_AL", "C", self.cm)

    def test_les_examens_francophones_ne_changent_pas(self):
        _resolve_cursus_list.cache_clear()
        self.assertEqual(self._un("BEPC").examen, Examen.BEPC)
        (c,) = _resolve_cursus_list("BAC", "C", self.cm)
        self.assertEqual((c.examen, c.series.code), (Examen.BAC, "C"))

    def test_matieres_anglaises_vers_codes_gce(self):
        for libelle, code in (
            ("Mathematics", "GCE_MATHS"), ("Further Mathematics", "GCE_FURTHER_MATHS"),
            ("Literature in English", "GCE_LITERATURE"), ("Physics", "GCE_PHYSICS"),
        ):
            self.assertEqual(_resolve_subject(libelle, self.cm).code, code)

    def test_matieres_francaises_inchangees(self):
        self.assertEqual(_resolve_subject("Mathématiques", self.cm).code, "MATHS")
        self.assertEqual(_resolve_subject("Anglais", self.cm).code, "ANGLAIS")
        self.assertEqual(MATIERE_MAP["maths"], "MATHS")

    def test_toutes_les_cibles_gce_existent_en_base(self):
        codes = {code for code in MATIERE_MAP.values() if code.startswith("GCE_")}
        existants = set(Subject.objects.filter(country=self.cm, code__in=codes).values_list("code", flat=True))
        self.assertEqual(codes, existants)


class GceMatieresOfficiellesTests(TestCase):
    """Référentiel des matières aligné sur les listes du GCE Board (camgceb.org, 2026-10-15)."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")

    def test_matieres_manquantes_ajoutees_avec_leurs_codes(self):
        attendus = {
            "GCE_PM_MECHANICS": ("Pure Mathematics with Mechanics", {"GCE_AL": "0765"}),
            "GCE_PM_STATISTICS": ("Pure Mathematics with Statistics", {"GCE_AL": "0770"}),
            "GCE_HUMAN_BIOLOGY": ("Human Biology", {"GCE_OL": "0565"}),
            "GCE_GEOLOGY": ("Geology", {"GCE_OL": "0555", "GCE_AL": "0755"}),
            "GCE_SBE_FRENCH": ("Special Bilingual Education French", {"GCE_OL": "0546", "GCE_AL": "0746"}),
        }
        for code, (libelle, codes) in attendus.items():
            matiere = Subject.objects.get(country=self.cm, code=code)
            self.assertEqual((matiere.label, matiere.codes_officiels, matiere.langue), (libelle, codes, Langue.EN), code)

    def test_pure_maths_est_scindee(self):
        self.assertFalse(Subject.objects.filter(country=self.cm, code="GCE_PURE_MATHS").exists())
        self.assertNotIn("GCE_PURE_MATHS", MATIERE_MAP.values())
        self.assertEqual(_resolve_subject("Pure Mathematics with Mechanics", self.cm).code, "GCE_PM_MECHANICS")
        self.assertEqual(_resolve_subject("Pure Mathematics with Statistics", self.cm).code, "GCE_PM_STATISTICS")

    def test_pure_maths_seule_est_refusee(self):
        # Ni Mechanics (0765) ni Statistics (0770) : l'ingestion ne devine pas.
        for libelle in ("Pure Mathematics", "Pure Maths"):
            with self.assertRaises(IngestionError, msg=libelle):
                _resolve_subject(libelle, self.cm)

    def test_libelles_du_board_resolus(self):
        for libelle, code in (
            ("Human Biology", "GCE_HUMAN_BIOLOGY"), ("Geology", "GCE_GEOLOGY"),
            ("Special Bilingual Education French", "GCE_SBE_FRENCH"),
            ("Food Science and Nutrition", "GCE_FOOD_NUTRITION"),
        ):
            self.assertEqual(_resolve_subject(libelle, self.cm).code, code)

    def test_la_base_suit_la_table_des_codes_officiels(self):
        for code, codes in CODES_OFFICIELS_GCE.items():
            self.assertEqual(Subject.objects.get(country=self.cm, code=code).codes_officiels, codes, code)

    def test_codes_du_board_bien_formes(self):
        # 4 chiffres ; 05xx au O Level, 07xx à l'A Level ; un code n'est attribué qu'à une seule matière par niveau.
        vus = {}
        for code, codes in CODES_OFFICIELS_GCE.items():
            for niveau, numero in codes.items():
                self.assertRegex(numero, r"^0(5|7)\d\d$", f"{code} {niveau}")
                self.assertEqual(numero[:2], "05" if niveau == "GCE_OL" else "07", f"{code} {niveau}")
                self.assertNotIn((niveau, numero), vus, f"{code} partage {numero} avec {vus.get((niveau, numero))}")
                vus[(niveau, numero)] = code

    def test_chaque_matiere_gce_a_ses_codes_sauf_dessin_technique(self):
        sans_codes = set(
            Subject.objects.filter(country=self.cm, code__startswith="GCE_", codes_officiels={}).values_list("code", flat=True)
        )
        self.assertEqual(sans_codes, {"GCE_TECH_DRAWING"})

    def test_matieres_francophones_sans_codes_officiels(self):
        self.assertEqual(Subject.objects.filter(langue=Langue.FR).exclude(codes_officiels={}).count(), 0)


class GceRechercheTests(TestCase):
    def setUp(self):
        self.cm = Country.objects.get(code="CM")

    def test_mot_gce_vise_les_deux_niveaux(self):
        ids, libelle = intention._cursus_et_series(["gce"], self.cm, set())
        attendus = set(Cursus.objects.filter(country=self.cm, examen__in=EXAMENS_GCE).values_list("id", flat=True))
        self.assertEqual(set(ids), attendus)
        self.assertEqual(libelle, "GCE")

    def test_advanced_vise_le_seul_niveau_avance(self):
        ids, libelle = intention._cursus_et_series(["advanced", "level"], self.cm, set())
        cursus = Cursus.objects.filter(id__in=ids)
        self.assertEqual({c.examen for c in cursus}, {Examen.GCE_AL})
        self.assertEqual(libelle, "GCE A Level")

    def test_examens_francophones_inchanges(self):
        ids, libelle = intention._cursus_et_series(["bac", "c"], self.cm, set())
        self.assertEqual(libelle, "BAC C")
        self.assertEqual(len(ids), 1)
