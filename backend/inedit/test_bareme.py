"""Barème exact par question : ingestion, contrôle de complétude, rétro-remplissage."""

import json
import tempfile
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from catalog.ingestion import IngestionError
from catalog.models import Country, Tag

from . import bareme
from .ingestion import ingest_blueprint, ingest_epreuve_inedite
from .models import QuestionInedite
from .tests import _blueprint_payload, _epreuve_payload, _make_published_epreuve


def _question(numero, points=None, criteres=None, **extra):
    data = {
        "numero": numero, "ordre": int(numero), "enonce_markdown": f"Énoncé {numero}.",
        "corrige_markdown": f"Corrigé {numero}.", "type_reponse": "ouverte", **extra,
    }
    if points is not None:
        data["points"] = points
    if criteres is not None:
        data["criteres_notation"] = criteres
    return data


class IngestionBaremeTests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        blueprint.statut = "VALIDE"
        blueprint.save(update_fields=["statut"])

    def ingerer(self, questions, points_exercice="8"):
        payload = _epreuve_payload(exercices=[{"numero_exercice": "1", "points": points_exercice, "questions": questions}])
        return ingest_epreuve_inedite(payload, self.country)[0]

    def test_points_et_criteres_sont_enregistres(self):
        epreuve = self.ingerer([
            _question("1", 5, [{"libelle": "Formule", "points": 2}, {"libelle": "Calcul", "points": 3}]),
            _question("2", 3),
        ])
        q1, q2 = QuestionInedite.objects.filter(exercice__epreuve=epreuve).order_by("ordre")
        self.assertEqual(q1.points, Decimal("5"))
        self.assertEqual([c["points"] for c in q1.criteres_notation], [2.0, 3.0])
        self.assertEqual(q2.points, Decimal("3"))
        self.assertEqual(q2.criteres_notation, [])
        self.assertEqual(bareme.verifier_epreuve(epreuve), [])

    def test_le_bareme_reste_optionnel_a_l_ingestion(self):
        epreuve = self.ingerer([_question("1"), _question("2")])
        self.assertIsNone(QuestionInedite.objects.filter(exercice__epreuve=epreuve).first().points)

    def test_somme_des_questions_differente_de_l_exercice_refusee(self):
        with self.assertRaisesMessage(IngestionError, "totalisent 7"):
            self.ingerer([_question("1", 4), _question("2", 3)])

    def test_bareme_a_moitie_renseigne_refuse(self):
        with self.assertRaisesMessage(IngestionError, "tout ou rien"):
            self.ingerer([_question("1", 8), _question("2")])

    def test_criteres_qui_ne_totalisent_pas_les_points_refuses(self):
        with self.assertRaisesMessage(IngestionError, "critères totalisent"):
            self.ingerer([_question("1", 8, [{"libelle": "Tout", "points": 5}])])

    def test_criteres_sans_points_ou_libelle_refuses(self):
        with self.assertRaises(IngestionError):
            self.ingerer([_question("1", 8, [{"libelle": "", "points": 8}])])
        with self.assertRaises(IngestionError):
            self.ingerer([_question("1", 8, [{"libelle": "A", "points": 0}])])

    def test_une_qcm_n_a_pas_de_grille(self):
        qcm = _question(
            "1", 8, [{"libelle": "A", "points": 8}], type_reponse="qcm",
            choix=[{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}], reponse_correcte="a",
        )
        with self.assertRaisesMessage(IngestionError, "tout ou rien"):
            self.ingerer([qcm])

    def test_l_echec_ne_laisse_aucune_epreuve_partielle(self):
        with self.assertRaises(IngestionError):
            self.ingerer([_question("1", 4), _question("2", 3)])
        self.assertFalse(QuestionInedite.objects.exists())


class VerifierEpreuveTests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.epreuve = _make_published_epreuve(self.country)
        self.exercice = self.epreuve.exercices.get()

    def test_un_bareme_absent_est_signale_comme_incomplet(self):
        anomalies = bareme.verifier_epreuve(self.epreuve)
        self.assertTrue(any("barème par question absent" in a for a in anomalies))
        self.assertEqual(bareme.verifier_epreuve(self.epreuve, exiger_complet=False), [])

    def test_un_enonce_qui_annonce_d_autres_points_est_signale(self):
        q1, q2 = self.exercice.questions.order_by("ordre")
        q1.points, q2.points = Decimal("4"), Decimal("4")
        q1.enonce_markdown = "Question. (1 pt)"
        q1.save()
        q2.save()
        anomalies = bareme.verifier_epreuve(self.epreuve)
        self.assertEqual(len(anomalies), 1)
        self.assertIn("annonce 1", anomalies[0])

    def test_une_annonce_qui_est_le_total_d_une_sous_partie_est_acceptee(self):
        # « (8 points) » en tête de Q1 : total de Q1 + Q2 (5 + 3), pas le barème de Q1 seule.
        q1, q2 = self.exercice.questions.order_by("ordre")
        q1.points, q2.points = Decimal("5"), Decimal("3")
        q1.enonce_markdown = "Situation-problème (8 points). Question."
        q1.save()
        q2.save()
        self.assertEqual(bareme.verifier_epreuve(self.epreuve), [])

    def test_une_annonce_qui_ne_correspond_a_aucune_somme_consecutive_est_signalee(self):
        q1, q2 = self.exercice.questions.order_by("ordre")
        q1.points, q2.points = Decimal("5"), Decimal("3")
        q1.enonce_markdown = "Question. (6 points)"
        q1.save()
        q2.save()
        self.assertEqual(len(bareme.verifier_epreuve(self.epreuve)), 1)

    def test_epreuves_validees_non_conformes_indexees_par_identifiant(self):
        self.assertIn(self.epreuve.external_id, bareme.verifier_epreuves_validees())


class AppliquerBaremeCommandTests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.epreuve = _make_published_epreuve(self.country)
        self.dossier = Path(tempfile.mkdtemp())

    def fichier(self, questions, nom="bareme.json", epreuve=None):
        chemin = self.dossier / nom
        chemin.write_text(json.dumps({"epreuve": epreuve or self.epreuve.external_id, "questions": questions}), encoding="utf-8")
        return chemin

    def lancer(self, *args):
        sortie, erreur = StringIO(), StringIO()
        call_command("appliquer_bareme_inedites", *map(str, args), stdout=sortie, stderr=erreur)
        return sortie.getvalue()

    def bareme_complet(self):
        return [
            {"exercice": "1", "numero": "1", "points": 3},
            {"exercice": "1", "numero": "2", "points": 5, "criteres_notation": [
                {"libelle": "Méthode", "points": 2}, {"libelle": "Résultat", "points": 3},
            ]},
        ]

    def test_applique_le_bareme_et_l_epreuve_devient_conforme(self):
        with mock.patch("inedit.management.commands.appliquer_bareme_inedites._source_json", return_value=None):
            self.lancer(self.fichier(self.bareme_complet()))

        q1, q2 = QuestionInedite.objects.filter(exercice__epreuve=self.epreuve).order_by("ordre")
        self.assertEqual((q1.points, q2.points), (Decimal("3"), Decimal("5")))
        self.assertEqual(len(q2.criteres_notation), 2)
        self.call_verifier_ok()

    def call_verifier_ok(self):
        self.assertIn("conforme", self.lancer("--verifier"))

    def test_dry_run_ne_touche_pas_la_base(self):
        sortie = self.lancer(self.fichier(self.bareme_complet()), "--dry-run")
        self.assertIn("dry-run", sortie)
        self.assertFalse(QuestionInedite.objects.filter(exercice__epreuve=self.epreuve, points__isnull=False).exists())

    def test_fichier_incomplet_refuse_sans_rien_ecrire(self):
        with self.assertRaises(CommandError):
            self.lancer(self.fichier(self.bareme_complet()[:1]))
        self.assertFalse(QuestionInedite.objects.filter(exercice__epreuve=self.epreuve, points__isnull=False).exists())

    def test_somme_incoherente_refusee_sans_rien_ecrire(self):
        incoherent = self.bareme_complet()
        incoherent[0]["points"] = 4
        with self.assertRaises(CommandError):
            self.lancer(self.fichier(incoherent))
        self.assertFalse(QuestionInedite.objects.filter(exercice__epreuve=self.epreuve, points__isnull=False).exists())

    def test_question_inconnue_refusee(self):
        with self.assertRaises(CommandError):
            self.lancer(self.fichier(self.bareme_complet() + [{"exercice": "9", "numero": "9", "points": 1}]))

    def test_le_bareme_est_reporte_dans_le_json_source(self):
        source = self.dossier / "source.json"
        source.write_text(json.dumps({"exercices": [{"numero_exercice": "1", "questions": [
            {"numero": "1"}, {"numero": "2"},
        ]}]}), encoding="utf-8")

        with mock.patch("inedit.management.commands.appliquer_bareme_inedites._source_json", return_value=source):
            self.lancer(self.fichier(self.bareme_complet()))

        questions = json.loads(source.read_text(encoding="utf-8"))["exercices"][0]["questions"]
        self.assertEqual(questions[0]["points"], 3.0)
        self.assertNotIn("criteres_notation", questions[0])
        self.assertEqual(len(questions[1]["criteres_notation"]), 2)

    def test_verifier_echoue_tant_que_le_bareme_est_incomplet(self):
        with self.assertRaises(CommandError):
            self.lancer("--verifier")
