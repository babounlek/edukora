"""
Essai d'ingestion de vrais sujets du GCE (O/L, juin 2019) : fixtures_gce/*.json.

Ce que ces sujets imposent au modèle - et que les épreuves francophones n'avaient jamais exigé :
plusieurs « papers » par matière et par année (QCM, questions rédigées), un code de matière du
jury, des sections, des points imprimés par bloc de questions, et des questions à choix
(« 4 sur 5 », « soit a, b, c soit d, e, f »).
"""
import json
from pathlib import Path

from django.test import SimpleTestCase, TestCase

from .choix import valider_regles_choix
from .ingestion import IngestionError, _resolve_cursus_list, ingest_exercise
from .models import Cursus, Examen, Lesson, Question, Subject, TypeReponse

FIXTURES = Path(__file__).parent / "fixtures_gce"


def _charger(nom):
    return json.loads((FIXTURES / nom).read_text(encoding="utf-8"))


def _ingerer(nom, **surcharges):
    data = {**_charger(nom), **surcharges}
    dossier = Path("ingest/cm") / nom.removesuffix(".json")
    return ingest_exercise(data, source_dir=dossier, exiger_themes=True)


class _Base(TestCase):
    def setUp(self):
        _resolve_cursus_list.cache_clear()

    def tearDown(self):
        _resolve_cursus_list.cache_clear()


class PapersDistinctsTests(_Base):
    def test_paper_1_et_paper_2_sont_deux_epreuves_aux_titres_distincts(self):
        p1, _ = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        p2, _ = _ingerer("gce_ol_maths_2019_p2_a1.json")

        self.assertNotEqual(p1.lesson_id, p2.lesson_id)
        self.assertEqual(p1.lesson.title, "Mathematics GCE Ordinary Level 2019 - Paper 1")
        self.assertEqual(p2.lesson.title, "Mathematics GCE Ordinary Level 2019 - Paper 2")
        self.assertEqual((p1.lesson.numero_paper, p2.lesson.numero_paper), (1, 2))
        self.assertEqual({p1.lesson.code_matiere_officiel, p2.lesson.code_matiere_officiel}, {"0570"})

    def test_rattachement_au_cursus_general_de_l_ordinary_level(self):
        exercice, _ = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        lesson = exercice.lesson
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        self.assertEqual(list(lesson.cursus.all()), [cursus])
        self.assertEqual(lesson.subject.code, "GCE_MATHS")
        self.assertEqual(lesson.subject.langue, "en")
        self.assertEqual(lesson.institution, "Cameroon GCE Board")
        self.assertEqual(lesson.duree_epreuve, "1h30")
        self.assertEqual(lesson.year, 2019)

    def test_les_exercices_d_un_meme_paper_partagent_une_seule_epreuve(self):
        a1, _ = _ingerer("gce_ol_maths_2019_p2_a1.json")
        a2, _ = _ingerer("gce_ol_maths_2019_p2_a2.json")
        a3, _ = _ingerer("gce_ol_maths_2019_p2_a3.json")
        self.assertEqual(len({a1.lesson_id, a2.lesson_id, a3.lesson_id}), 1)
        lesson = a1.lesson
        self.assertEqual(lesson.exercises.count(), 3)
        for exercice in (a1, a2, a3):
            self.assertEqual(exercice.groupes, ["SECTION A"])
        self.assertEqual([e.points for e in lesson.exercises.order_by("numero_exercice")], ["4", "6", "7"])

    def test_reingerer_ne_duplique_rien(self):
        premier, cree = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        second, cree_bis = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        self.assertTrue(cree)
        self.assertFalse(cree_bis)
        self.assertEqual(premier.pk, second.pk)
        self.assertEqual(Lesson.objects.filter(epreuve_source="GCE_OL_MATHS_2019_P1.pdf").count(), 1)

    def test_deux_papers_meme_nom_de_source_restent_separes_par_leur_numero(self):
        # Un fichier mal nommé (même epreuve_source pour les deux papers) ne doit pas les fusionner.
        p1, _ = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        p2, _ = _ingerer("gce_ol_maths_2019_p2_a1.json", epreuve_source="GCE_OL_MATHS_2019_P1.pdf")
        self.assertNotEqual(p1.lesson_id, p2.lesson_id)


class QcmDuPaper1Tests(_Base):
    def test_cinquante_qcm_a_quatre_choix_corriges_automatiquement(self):
        exercice, _ = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        questions = list(exercice.questions.order_by("ordre"))
        self.assertEqual(len(questions), 6)
        for question in questions:
            self.assertEqual(question.type_reponse, TypeReponse.QCM)
            self.assertEqual([c["lettre"] for c in question.choix], ["a", "b", "c", "d"])
            self.assertIn(question.reponse_correcte, "abcd")
            self.assertIsNone(question.points)  # toutes les questions valent autant
        self.assertEqual([q.reponse_correcte for q in questions], ["c", "b", "c", "d", "a", "a"])


class PointsEtSectionsTests(_Base):
    def test_points_imprimes_par_bloc_conserves_tels_quels(self):
        exercice, _ = _ingerer("gce_ol_chimie_2019_p2_a1.json")
        self.assertEqual(exercice.points, "10")
        self.assertEqual([q.points for q in exercice.questions.order_by("ordre")], [3, 3, 3, 3])
        # Les points imprimés (12) ne tombent pas juste sur le total annoncé (10) : jamais corrigés ni refusés.
        self.assertEqual(sum(q.points for q in exercice.questions.all()), 12)
        self.assertTrue(any("12" in note for note in exercice.incertitudes))

    def test_points_de_question_illisibles_restent_vides(self):
        from .ingestion import _resolve_points_question

        self.assertEqual(_resolve_points_question("3 marks"), 3)
        self.assertEqual(_resolve_points_question(3), 3)
        self.assertIsNone(_resolve_points_question(""))
        self.assertIsNone(_resolve_points_question("beaucoup"))
        self.assertIsNone(_resolve_points_question(None))
        self.assertIsNone(_resolve_points_question(True))

    def test_physique_points_par_bloc_somment_au_total_de_la_question(self):
        exercice, _ = _ingerer("gce_ol_physique_2019_p2_ii7.json")
        self.assertEqual(exercice.points, "20")
        points = {q.numero: q.points for q in exercice.questions.all()}
        self.assertEqual(points, {"a": 8, "b": 7, "c": 5, "d": 8, "e": 7, "f": 5})
        self.assertEqual(points["a"] + points["b"] + points["c"], 20)
        self.assertEqual(points["d"] + points["e"] + points["f"], 20)


class ReglesDeChoixTests(_Base):
    def test_chimie_n_sur_m_par_section(self):
        lesson = _ingerer("gce_ol_chimie_2019_p2_a1.json")[0].lesson
        self.assertEqual(lesson.code_matiere_officiel, "0515")
        self.assertEqual(lesson.regles_choix, [
            {"type": "parmi", "portee": "SECTION A", "repondre": 4, "sur": 5},
            {"type": "parmi", "portee": "SECTION B", "repondre": 2, "sur": 3},
            {"type": "parmi", "portee": "SECTION C", "repondre": 2, "sur": 2},
        ])
        self.assertIn("answer 4 questions out of 5", lesson.introduction_markdown)

    def test_physique_soit_a_b_c_soit_d_e_f(self):
        exercice, _ = _ingerer("gce_ol_physique_2019_p2_ii7.json")
        regle = exercice.lesson.regles_choix[0]
        self.assertEqual(regle["type"], "ou")
        self.assertEqual(regle["options"], [["a", "b", "c"], ["d", "e", "f"]])
        # Les repères des options sont bien les numéros des sous-questions de l'exercice.
        numeros = {q.numero for q in exercice.questions.all()}
        self.assertEqual({r for jeu in regle["options"] for r in jeu}, numeros)

    def test_epreuve_sans_choix_a_une_liste_vide(self):
        lesson = _ingerer("gce_ol_maths_2019_p2_a1.json")[0].lesson
        self.assertEqual(lesson.regles_choix, [])

    def test_header_info_expose_paper_code_et_regles(self):
        lesson = _ingerer("gce_ol_chimie_2019_p2_a1.json")[0].lesson
        entete = lesson.header_info()
        self.assertEqual(entete["paper"], 2)
        self.assertEqual(entete["code_matiere"], "0515")
        self.assertEqual(entete["regles_choix"][0]["repondre"], 4)
        self.assertEqual(entete["institution"], "Cameroon GCE Board")
        self.assertEqual(entete["examen"], "GCE Ordinary Level")

    def test_une_regle_invalide_refuse_l_exercice_avant_toute_ecriture(self):
        avant = Lesson.objects.count()
        with self.assertRaisesMessage(IngestionError, "repondre"):
            _ingerer("gce_ol_chimie_2019_p2_a1.json", regles_choix=[
                {"type": "parmi", "portee": "SECTION A", "repondre": 6, "sur": 5},
            ])
        self.assertEqual(Lesson.objects.count(), avant)


class ChampsDuPaperRefusesQuandIllisiblesTests(_Base):
    def test_numero_de_paper(self):
        from .ingestion import _resolve_numero_paper

        self.assertEqual(_resolve_numero_paper(2), 2)
        self.assertEqual(_resolve_numero_paper("2"), 2)
        self.assertEqual(_resolve_numero_paper("Paper 3"), 3)
        self.assertIsNone(_resolve_numero_paper(None))
        for invalide in (0, 10, "deux", True, "Paper"):
            with self.assertRaises(IngestionError):
                _resolve_numero_paper(invalide)

    def test_code_matiere_trop_long_refuse(self):
        with self.assertRaises(IngestionError):
            _ingerer("gce_ol_maths_2019_p1_ex1.json", code_matiere="0570-0570-0570")

    def test_les_epreuves_francophones_n_ont_ni_paper_ni_code(self):
        from .tests import _exercise_payload

        exercice, _ = ingest_exercise(_exercise_payload("bac-maths-2024"), source_dir=Path("ingest/cm/bac-maths-2024"))
        lesson = exercice.lesson
        self.assertIsNone(lesson.numero_paper)
        self.assertEqual(lesson.code_matiere_officiel, "")
        self.assertEqual(lesson.regles_choix, [])
        self.assertNotIn("Paper", lesson.title)


class BrancheTechniqueTests(_Base):
    def test_un_sujet_technique_va_au_cursus_technique(self):
        exercice, _ = _ingerer("gce_ol_maths_2019_p1_ex1.json", serie="Technical")
        (cursus,) = exercice.lesson.cursus.all()
        self.assertEqual(cursus.series.code, "GCE_TECHNICAL")


class ReglesChoixUnitairesTests(SimpleTestCase):
    def test_aucune_regle_est_valide(self):
        self.assertEqual(valider_regles_choix(None), [])
        self.assertEqual(valider_regles_choix([]), [])

    def test_normalise_les_textes(self):
        regles = valider_regles_choix([
            {"type": "parmi", "portee": "  SECTION B ", "repondre": 2, "sur": 3},
            {"type": "ou", "portee": "SECTION II", "options": [[" a ", "b"], ["c"]]},
        ])
        self.assertEqual(regles[0]["portee"], "SECTION B")
        self.assertEqual(regles[1]["options"], [["a", "b"], ["c"]])

    def test_refus(self):
        invalides = [
            "pas une liste",
            ["pas un objet"],
            [{"type": "parmi", "repondre": 1, "sur": 2}],  # portée manquante
            [{"type": "parmi", "portee": "A", "repondre": 0, "sur": 2}],
            [{"type": "parmi", "portee": "A", "repondre": 3, "sur": 2}],
            [{"type": "parmi", "portee": "A", "repondre": "2", "sur": 3}],
            [{"type": "parmi", "portee": "A", "repondre": True, "sur": 3}],
            [{"type": "ou", "portee": "A", "options": [["a"]]}],
            [{"type": "ou", "portee": "A", "options": [["a"], []]}],
            [{"type": "ou", "portee": "A", "options": [["a", "b"], ["b", "c"]]}],  # repère partagé
            [{"type": "au_choix", "portee": "A"}],
        ]
        for regles in invalides:
            with self.assertRaises(ValueError, msg=repr(regles)):
                valider_regles_choix(regles)

    def test_repondre_egal_sur_est_valide(self):
        self.assertEqual(
            valider_regles_choix([{"type": "parmi", "portee": "C", "repondre": 2, "sur": 2}])[0]["sur"], 2,
        )


class ApiExposePaperTests(_Base):
    def test_liste_des_epreuves_porte_paper_et_code_de_matiere(self):
        _ingerer("gce_ol_maths_2019_p1_ex1.json")
        _ingerer("gce_ol_maths_2019_p2_a1.json")
        reponse = self.client.get("/catalog/lessons/", {"country": "cm", "subject": "GCE_MATHS"})
        self.assertEqual(reponse.status_code, 200)
        lignes = {ligne["title"]: ligne for ligne in reponse.json()["results"]}
        self.assertEqual(lignes["Mathematics GCE Ordinary Level 2019 - Paper 1"]["numero_paper"], 1)
        self.assertEqual(lignes["Mathematics GCE Ordinary Level 2019 - Paper 2"]["numero_paper"], 2)
        self.assertEqual(lignes["Mathematics GCE Ordinary Level 2019 - Paper 2"]["code_matiere_officiel"], "0570")
