"""
Phase 1 ("socle données", voir l'audit "Épreuves Inédites") : ce module ne couvre que le
schéma lui-même - contraintes d'unicité conditionnelle (idempotence, même patron que
CompetenceItem.external_id), et la chaîne CASCADE bout en bout (même arbitrage que
quiz.tests.QuizQuestionDeletionTests, voir la docstring de TentativeInedite). Aucun
pipeline de génération, aucun endpoint : ces deux hors-scope pour cette phase.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.ingestion import IngestionError
from catalog.models import Cours, Country, Cursus, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject, Tag, TypeReponse
from programme.models import Module, Savoir
from quiz.models import RevisionSchedule
from subscriptions.models import InscriptionInedite
from users.models import User

from .ingestion import ingest_blueprint, ingest_cours_inedite, ingest_epreuve_inedite, run_ingestion, select_inedit_batch
from .models import (
    Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite,
    RappelDeMethodeInedite, ResultatDeclare, TentativeInedite, TentativeReponse,
)
from .quality import calculer_scores, score_originalite, score_qualite


def _make_blueprint(subject=None, cursus=None, **kwargs):
    subject = subject or Subject.objects.get(country__code="CM", code="MATHS")
    cursus = cursus or Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
    cursus_list = [cursus] if isinstance(cursus, Cursus) else list(cursus)
    kwargs.setdefault("titre", "Blueprint de test")
    blueprint = Blueprint.objects.create(subject=subject, **kwargs)
    blueprint.cursus.set(cursus_list)
    blueprint.competences.add(Tag.objects.create(name=f"competence-{blueprint.pk}"))
    return blueprint


def _make_epreuve(blueprint=None, **kwargs):
    blueprint = blueprint or _make_blueprint()
    kwargs.setdefault("titre", "Épreuve de test")
    epreuve = EpreuveInedite.objects.create(blueprint=blueprint, subject=blueprint.subject, **kwargs)
    epreuve.cursus.set(blueprint.cursus.all())
    return epreuve


def _make_question(epreuve=None, exercice=None, numero="1", ordre=1, type_reponse=TypeReponse.OUVERTE, **kwargs):
    if exercice is None:
        epreuve = epreuve or _make_epreuve()
        exercice = ExerciceInedite.objects.create(epreuve=epreuve, numero_exercice="1")
    return QuestionInedite.objects.create(
        exercice=exercice, numero=numero, ordre=ordre,
        enonce_markdown="Énoncé.", corrige_markdown="Corrigé.", type_reponse=type_reponse, **kwargs,
    )


class BlueprintConstraintTests(TestCase):
    """external_id : idempotence quand fourni, jamais bloquant quand vide - même
    contrainte que CompetenceItem.external_id (voir quiz.models)."""

    def test_two_blank_external_ids_are_allowed(self):
        _make_blueprint(external_id="")
        _make_blueprint(external_id="")  # ne doit pas lever

    def test_duplicate_non_blank_external_id_is_rejected(self):
        _make_blueprint(external_id="bp-cm-maths-1")
        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                _make_blueprint(external_id="bp-cm-maths-1")


class EpreuveInediteConstraintTests(TestCase):
    def test_two_blank_external_ids_are_allowed(self):
        _make_epreuve(external_id="")
        _make_epreuve(external_id="")

    def test_duplicate_non_blank_external_id_is_rejected(self):
        _make_epreuve(external_id="ep-cm-maths-1")
        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                _make_epreuve(external_id="ep-cm-maths-1")


class EpreuveInediteSlugTests(TestCase):
    """slug auto-généré depuis titre à la création - même mécanisme que
    catalog.models.Lesson.slug/Cours.slug (voir generate_unique_slug), désormais
    partagé plutôt que dupliqué (voir la note "SEO" de l'utilisateur qui a motivé
    ce champ : un id numérique dans l'URL ne dit rien du contenu)."""

    def test_slug_is_generated_from_titre_on_creation(self):
        epreuve = _make_epreuve(titre="Épreuve blanche de Mathématiques - Terminale D - Session 1")
        self.assertEqual(epreuve.slug, "epreuve-blanche-de-mathematiques-terminale-d-session-1")

    def test_duplicate_titre_gets_a_disambiguated_slug(self):
        first = _make_epreuve(titre="Même titre")
        second = _make_epreuve(titre="Même titre")

        self.assertEqual(first.slug, "meme-titre")
        self.assertEqual(second.slug, "meme-titre-2")

    def test_slug_is_never_regenerated_once_set(self):
        epreuve = _make_epreuve(titre="Titre original")
        original_slug = epreuve.slug

        epreuve.titre = "Titre modifié"
        epreuve.save(update_fields=["titre"])

        self.assertEqual(epreuve.slug, original_slug)


class ExerciceInediteConstraintTests(TestCase):
    def test_duplicate_numero_within_same_epreuve_is_rejected(self):
        epreuve = _make_epreuve()
        ExerciceInedite.objects.create(epreuve=epreuve, numero_exercice="1")
        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                ExerciceInedite.objects.create(epreuve=epreuve, numero_exercice="1")

    def test_same_numero_on_different_epreuves_is_allowed(self):
        ExerciceInedite.objects.create(epreuve=_make_epreuve(), numero_exercice="1")
        ExerciceInedite.objects.create(epreuve=_make_epreuve(), numero_exercice="1")  # ne doit pas lever


class QuestionInediteConstraintTests(TestCase):
    def test_duplicate_numero_within_same_exercice_is_rejected(self):
        exercice = ExerciceInedite.objects.create(epreuve=_make_epreuve(), numero_exercice="1")
        QuestionInedite.objects.create(
            exercice=exercice, numero="a", ordre=1, enonce_markdown="E1", corrige_markdown="C1",
        )
        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                QuestionInedite.objects.create(
                    exercice=exercice, numero="a", ordre=2, enonce_markdown="E2", corrige_markdown="C2",
                )


class RappelDeMethodeInediteConstraintTests(TestCase):
    def test_duplicate_external_id_is_rejected(self):
        exercice = ExerciceInedite.objects.create(epreuve=_make_epreuve(), numero_exercice="1")
        RappelDeMethodeInedite.objects.create(exercice=exercice, external_id="rdi-a", competence="C")
        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                RappelDeMethodeInedite.objects.create(exercice=exercice, external_id="rdi-a", competence="C")

    def test_cours_genere_reflects_cours_link(self):
        exercice = ExerciceInedite.objects.create(epreuve=_make_epreuve(), numero_exercice="1")
        rappel = RappelDeMethodeInedite.objects.create(exercice=exercice, external_id="rdi-a", competence="C")
        self.assertFalse(rappel.cours_genere)

        rappel.cours = Cours.objects.create(
            external_id="cours-a", titre="Cours A", subject=exercice.epreuve.subject, statut=StatutContenu.VALIDE,
        )
        rappel.save(update_fields=["cours"])
        self.assertTrue(rappel.cours_genere)


class TentativeInediteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300001", password="x")
        self.epreuve = _make_epreuve()

    def test_en_cours_is_true_until_submitted_at_is_set(self):
        tentative = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        self.assertTrue(tentative.en_cours)

        tentative.submitted_at = timezone.now()
        tentative.save(update_fields=["submitted_at"])
        self.assertFalse(tentative.en_cours)


class TentativeReponseTests(TestCase):
    """est_correcte : même arbitrage que quiz.QuizAnswer.est_correcte - QCM comparé
    objectivement à reponse_correcte, question ouverte auto-évaluée par l'élève."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300002", password="x")

    def test_qcm_answer_correctness_is_computed_objectively(self):
        question = _make_question(
            type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}],
            reponse_correcte="b",
        )
        tentative = TentativeInedite.objects.create(user=self.user, epreuve=question.exercice.epreuve)

        correcte = TentativeReponse.objects.create(tentative=tentative, question=question, reponse_choisie="b")
        self.assertTrue(correcte.est_correcte)

        question2 = _make_question(
            exercice=question.exercice, numero="2", ordre=2, type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}], reponse_correcte="b",
        )
        incorrecte = TentativeReponse.objects.create(tentative=tentative, question=question2, reponse_choisie="a")
        self.assertFalse(incorrecte.est_correcte)

    def test_open_question_correctness_relies_on_self_declared_result(self):
        question = _make_question(type_reponse=TypeReponse.OUVERTE)
        tentative = TentativeInedite.objects.create(user=self.user, epreuve=question.exercice.epreuve)

        reponse = TentativeReponse.objects.create(
            tentative=tentative, question=question, resultat_declare=ResultatDeclare.REUSSI,
        )
        self.assertTrue(reponse.est_correcte)

        reponse.resultat_declare = ResultatDeclare.ECHEC
        self.assertFalse(reponse.est_correcte)

    def test_duplicate_answer_to_same_question_in_same_tentative_is_rejected(self):
        question = _make_question(type_reponse=TypeReponse.QCM, reponse_correcte="a")
        tentative = TentativeInedite.objects.create(user=self.user, epreuve=question.exercice.epreuve)
        TentativeReponse.objects.create(tentative=tentative, question=question, reponse_choisie="a")

        with self.assertRaises(IntegrityError):
            with db_transaction.atomic():
                TentativeReponse.objects.create(tentative=tentative, question=question, reponse_choisie="a")


class CascadeDeletionTests(TestCase):
    """epreuve/question doivent être CASCADE, pas PROTECT : un admin doit pouvoir purger
    une EpreuveInedite rejetée même si des élèves l'ont déjà tentée - voir la docstring
    de TentativeInedite pour le même arbitrage que quiz.QuizQuestion."""

    def test_deleting_epreuve_cascades_through_exercices_questions_and_tentatives(self):
        user = User.objects.create_user(phone_number="677300003", password="x")
        question = _make_question(type_reponse=TypeReponse.QCM, reponse_correcte="a")
        epreuve = question.exercice.epreuve
        tentative = TentativeInedite.objects.create(user=user, epreuve=epreuve)
        TentativeReponse.objects.create(tentative=tentative, question=question, reponse_choisie="a")

        epreuve.delete()  # ne doit lever aucune ProtectedError

        self.assertFalse(ExerciceInedite.objects.exists())
        self.assertFalse(QuestionInedite.objects.exists())
        self.assertFalse(TentativeInedite.objects.exists())
        self.assertFalse(TentativeReponse.objects.exists())

    def test_deleting_blueprint_with_existing_epreuve_is_protected(self):
        epreuve = _make_epreuve()
        with self.assertRaises(ProtectedError):
            epreuve.blueprint.delete()


def _blueprint_payload(**overrides):
    payload = {
        "type": "blueprint",
        "external_id": "bp-cm-maths-bac-c-1",
        "titre": "Blueprint Maths BAC C - Session blanche 1",
        "matiere": "mathematiques",
        "cursus": [{"examen": "bac", "serie": "C"}],
        "competences": ["Suites numériques"],
        "sections_plan": [{"section": "Exercice 1", "points": 8}],
        "duree_minutes": 180,
        "bareme_total": 20,
    }
    payload.update(overrides)
    return payload


def _epreuve_payload(**overrides):
    payload = {
        "type": "epreuve",
        "external_id": "ep-cm-maths-bac-c-1-s1",
        "titre": "Épreuve blanche n°1",
        "blueprint_external_id": "bp-cm-maths-bac-c-1",
        "exercices": [
            {
                "numero_exercice": "1",
                "points": "8",
                "questions": [
                    {
                        "numero": "1", "ordre": 1,
                        "enonce_markdown": "Énoncé Q1.", "corrige_markdown": "Corrigé Q1.",
                        "difficulte_estimee": "moyenne", "type_reponse": "ouverte",
                    },
                ],
            },
        ],
    }
    payload.update(overrides)
    return payload


class IngestBlueprintTests(TestCase):
    """ingest_blueprint - jamais VALIDE à l'ingestion (voir la docstring de module de
    inedit.ingestion) : c'est la garantie centrale de la contrainte "un blueprint doit
    être validé avant génération"."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")

    def test_creates_blueprint_always_in_brouillon(self):
        blueprint, created = ingest_blueprint(_blueprint_payload(), self.country)

        self.assertTrue(created)
        self.assertEqual(blueprint.statut, StatutContenu.BROUILLON)
        self.assertEqual(blueprint.subject.code, "MATHS")
        self.assertEqual(blueprint.cursus.count(), 1)
        self.assertEqual(blueprint.cursus.get().examen, Examen.BAC)
        self.assertEqual(blueprint.cursus.get().series.code, "C")
        self.assertEqual(list(blueprint.competences.values_list("name", flat=True)), ["Suites numériques"])

    def test_missing_required_key_raises(self):
        payload = _blueprint_payload()
        del payload["titre"]
        with self.assertRaises(IngestionError):
            ingest_blueprint(payload, self.country)

    def test_idempotent_on_repeated_external_id_never_overwrites(self):
        first, created_first = ingest_blueprint(_blueprint_payload(), self.country)
        second, created_second = ingest_blueprint(_blueprint_payload(titre="Titre différent"), self.country)

        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(second.titre, first.titre)

    def test_unknown_competence_raises(self):
        payload = _blueprint_payload(competences=["Compétence inexistante"])
        with self.assertRaises(IngestionError):
            ingest_blueprint(payload, self.country)

    def test_combined_series_resolves_to_both_cursus(self):
        """Un Blueprint peut être commun à plusieurs séries (ex. Maths BAC C/E) - une
        `serie` combinée type 'C-E' résout vers les deux Cursus (voir
        _resolve_cursus_from_entries)."""
        payload = _blueprint_payload(cursus=[{"examen": "bac", "serie": "C-E"}])
        blueprint, _ = ingest_blueprint(payload, self.country)
        self.assertEqual(
            set(blueprint.cursus.values_list("series__code", flat=True)), {"C", "E"},
        )

    def test_multiple_cursus_entries_resolve_to_both_cursus(self):
        """Forme alternative du même besoin : deux entrées distinctes plutôt qu'une
        `serie` combinée - même résultat, voir _resolve_cursus_from_entries."""
        payload = _blueprint_payload(
            cursus=[{"examen": "bac", "serie": "C"}, {"examen": "bac", "serie": "E"}],
        )
        blueprint, _ = ingest_blueprint(payload, self.country)
        self.assertEqual(
            set(blueprint.cursus.values_list("series__code", flat=True)), {"C", "E"},
        )


class SavoirOfficielLinkingTests(TestCase):
    """`savoir_officiel`/`savoirs_officiels` (optionnels) lient les Tag résolus à leur
    Savoir officiel - voir catalog.ingestion._resolve_savoir_officiel/
    _link_tags_to_savoir. Un Blueprint vise plusieurs compétences à la fois (tableau
    parallèle "competences"/"savoirs_officiels"), contrairement à une QuestionInedite
    (un seul champ, comme catalog.Question)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.tag = Tag.objects.create(name="Suites numériques")
        maths = Subject.objects.get(country=self.country, code="MATHS")
        module = Module.objects.create(subject=maths, classe="Tle", serie_label="C", numero="25", titre="Module test")
        self.savoir = Savoir.objects.create(module=module, numero="I", intitule="Suites numériques")

    def test_blueprint_links_competences_via_parallel_array(self):
        payload = _blueprint_payload(savoirs_officiels=[
            {"classe": "Tle", "serie_label": "C", "module_numero": "25", "savoir_numero": "I"},
        ])
        ingest_blueprint(payload, self.country)

        self.tag.refresh_from_db()
        self.assertEqual(self.tag.savoir_officiel_id, self.savoir.pk)

    def test_blueprint_absent_field_is_a_no_op(self):
        ingest_blueprint(_blueprint_payload(), self.country)

        self.tag.refresh_from_db()
        self.assertIsNone(self.tag.savoir_officiel_id)

    def test_blueprint_shorter_savoirs_array_leaves_extra_competences_unlinked(self):
        other_tag = Tag.objects.create(name="Une autre competence")
        payload = _blueprint_payload(
            competences=["Suites numériques", "Une autre competence"],
            savoirs_officiels=[{"classe": "Tle", "serie_label": "C", "module_numero": "25", "savoir_numero": "I"}],
        )
        ingest_blueprint(payload, self.country)

        self.tag.refresh_from_db()
        other_tag.refresh_from_db()
        self.assertEqual(self.tag.savoir_officiel_id, self.savoir.pk)
        self.assertIsNone(other_tag.savoir_officiel_id)

    def test_question_inedite_links_theme_to_savoir(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        payload = _epreuve_payload()
        payload["exercices"][0]["questions"][0]["themes"] = ["Suites numériques"]
        payload["exercices"][0]["questions"][0]["savoir_officiel"] = {
            "classe": "Tle", "serie_label": "C", "module_numero": "25", "savoir_numero": "I",
        }
        ingest_epreuve_inedite(payload, self.country)

        self.tag.refresh_from_db()
        self.assertEqual(self.tag.savoir_officiel_id, self.savoir.pk)


class IngestEpreuveInediteTests(TestCase):
    """ingest_epreuve_inedite - le point qui fait respecter la contrainte "génération
    seulement depuis un blueprint déjà validé"."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")

    def _valid_blueprint(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        return blueprint

    def test_rejects_unknown_blueprint(self):
        payload = _epreuve_payload(blueprint_external_id="bp-inexistant")
        with self.assertRaises(IngestionError):
            ingest_epreuve_inedite(payload, self.country)

    def test_rejects_blueprint_still_in_brouillon(self):
        self._valid_blueprint()  # reste BROUILLON par défaut (voir IngestBlueprintTests)
        with self.assertRaises(IngestionError):
            ingest_epreuve_inedite(_epreuve_payload(), self.country)

    def test_creates_epreuve_with_exercices_and_questions_once_blueprint_is_valide(self):
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        epreuve, created = ingest_epreuve_inedite(_epreuve_payload(), self.country)

        self.assertTrue(created)
        self.assertEqual(epreuve.statut, StatutContenu.BROUILLON)  # jamais auto-validée
        self.assertEqual(epreuve.blueprint_id, blueprint.pk)
        self.assertEqual(epreuve.subject_id, blueprint.subject_id)
        self.assertEqual(set(epreuve.cursus.all()), set(blueprint.cursus.all()))
        self.assertEqual(epreuve.exercices.count(), 1)
        question = epreuve.exercices.get().questions.get()
        self.assertEqual(question.enonce_markdown, "Énoncé Q1.")

    def test_idempotent_on_repeated_external_id(self):
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        first, created_first = ingest_epreuve_inedite(_epreuve_payload(), self.country)
        second, created_second = ingest_epreuve_inedite(_epreuve_payload(titre="Autre titre"), self.country)

        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.pk, second.pk)

    def test_qcm_choices_are_normalized(self):
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        payload = _epreuve_payload(exercices=[{
            "numero_exercice": "1", "points": "4",
            "questions": [{
                "numero": "1", "ordre": 1,
                "enonce_markdown": "QCM ?", "corrige_markdown": "Corrigé.",
                "type_reponse": "qcm",
                "choix": [{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}],
                "reponse_correcte": "b",
            }],
        }])

        epreuve, _ = ingest_epreuve_inedite(payload, self.country)

        question = epreuve.exercices.get().questions.get()
        self.assertEqual(question.type_reponse, TypeReponse.QCM)
        self.assertEqual(question.reponse_correcte, "b")

    def test_exercice_without_questions_raises(self):
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        payload = _epreuve_payload(exercices=[{"numero_exercice": "1", "points": "4", "questions": []}])
        with self.assertRaises(IngestionError):
            ingest_epreuve_inedite(payload, self.country)

    def test_exercice_intro_is_ingested_and_em_dash_stripped(self):
        """Support partagé par les questions d'un exercice (voir
        ExerciceInedite.enonce_intro_markdown) - le cas SVT "Document 1 + questions qui
        l'exploitent", d'où le tableau Markdown ci-dessous plutôt qu'un texte nu."""
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        intro = "**Document 1** - résultats de l'expérience\n\n| t (min) | 0 | 10 |\n| --- | --- | --- |\n| Glycémie (g/L) | 0,90 | 1,45 |"
        payload = _epreuve_payload(exercices=[{
            "numero_exercice": "1", "points": "8",
            "enonce_intro_markdown": intro,
            "questions": [{
                "numero": "1", "ordre": 1,
                "enonce_markdown": "Exploite le document 1.", "corrige_markdown": "Corrigé.",
            }],
        }])

        epreuve, _ = ingest_epreuve_inedite(payload, self.country)

        exercice = epreuve.exercices.get()
        self.assertIn("Glycémie", exercice.enonce_intro_markdown)
        self.assertNotIn("—", exercice.enonce_intro_markdown)  # _strip_em_dash appliqué comme partout ailleurs

    def test_exercice_intro_defaults_to_empty_when_absent(self):
        """Champ optionnel : la grande majorité des exercices (hors SVT) n'a aucun support
        partagé, et son absence ne doit jamais échouer ni valoir "None" en base."""
        blueprint = self._valid_blueprint()
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        epreuve, _ = ingest_epreuve_inedite(_epreuve_payload(), self.country)

        self.assertEqual(epreuve.exercices.get().enonce_intro_markdown, "")


class IngestQuestionRappelsDeMethodeTests(TestCase):
    """Voir inedit.ingestion._ingest_question_inedite - rattachement à l'ExerciceInedite,
    jamais à la QuestionInedite, même patron que catalog.ingestion.ingest_exercise."""

    def setUp(self):
        self.epreuve = _make_epreuve()
        self.exercice = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="1")

    def _question_data(self, **overrides):
        data = {
            "numero": "1", "ordre": 1, "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.",
            "rappels_de_methode": [{"id": "rdi-a", "competence": "Notion A", "contenu_markdown": "Contenu A."}],
        }
        data.update(overrides)
        return data

    def test_rappel_is_attached_to_the_exercice_not_the_question(self):
        from .ingestion import _ingest_question_inedite
        _ingest_question_inedite(self.exercice, self._question_data(), self.epreuve.subject)

        rappel = RappelDeMethodeInedite.objects.get(external_id="rdi-a")
        self.assertEqual(rappel.exercice_id, self.exercice.id)
        self.assertEqual(rappel.competence, "Notion A")
        self.assertEqual(rappel.contenu_markdown, "Contenu A.")

    def test_missing_id_raises(self):
        from .ingestion import _ingest_question_inedite
        with self.assertRaises(IngestionError):
            _ingest_question_inedite(self.exercice, self._question_data(
                rappels_de_methode=[{"competence": "Sans id"}],
            ), self.epreuve.subject)

    def test_is_idempotent_via_get_or_create(self):
        from .ingestion import _ingest_question_inedite
        _ingest_question_inedite(self.exercice, self._question_data(), self.epreuve.subject)
        exercice2 = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="2")
        _ingest_question_inedite(exercice2, self._question_data(numero="1"), self.epreuve.subject)  # même rdi-a

        self.assertEqual(RappelDeMethodeInedite.objects.filter(external_id="rdi-a").count(), 1)

    def test_question_without_rappels_is_unaffected(self):
        from .ingestion import _ingest_question_inedite
        _ingest_question_inedite(self.exercice, self._question_data(rappels_de_methode=[]), self.epreuve.subject)
        self.assertFalse(RappelDeMethodeInedite.objects.exists())


class IngestCoursInediteTests(TestCase):
    """ingest_cours_inedite - miroir de catalog.ingestion.ingest_cours. Cours
    (catalog.models.Cours) est origine-agnostique : le dédoublonnage par titre porte
    sur TOUT Cours déjà validé, classique ou inédite - voir la docstring du modèle
    RappelDeMethodeInedite."""

    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.epreuve = _make_epreuve(blueprint=_make_blueprint(subject=self.subject, cursus=self.cursus))
        self.exercice = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="1")

    def _make_rappel(self, external_id="rdi-a", competence="Notion A", exercice=None):
        return RappelDeMethodeInedite.objects.create(
            exercice=exercice or self.exercice, external_id=external_id, competence=competence,
            contenu_markdown="Contenu.",
        )

    def _cours_payload(self, cours_id="cours-inedit-test", rappel_id="rdi-a", titre="Cours de test", **overrides):
        payload = {
            "type": "cours", "cours_id": cours_id,
            "meta": {"titre": titre, "matiere": "mathematiques"},
            "source": {"rappel_id": rappel_id}, "sections": [],
        }
        payload.update(overrides)
        return payload

    def test_creates_cours_and_links_rappel(self):
        self._make_rappel()
        cours, created = ingest_cours_inedite(self._cours_payload())

        self.assertTrue(created)
        self.assertEqual(cours.statut, StatutContenu.VALIDE)
        self.assertEqual(RappelDeMethodeInedite.objects.get(external_id="rdi-a").cours_id, cours.id)

    def test_missing_rappel_raises(self):
        with self.assertRaises(IngestionError):
            ingest_cours_inedite(self._cours_payload())

    def test_missing_required_key_raises(self):
        self._make_rappel()
        payload = self._cours_payload()
        del payload["meta"]["titre"]
        with self.assertRaises(IngestionError):
            ingest_cours_inedite(payload)

    def test_idempotent_on_repeated_cours_id(self):
        self._make_rappel()
        ingest_cours_inedite(self._cours_payload())
        cours2, created2 = ingest_cours_inedite(self._cours_payload())

        self.assertFalse(created2)
        self.assertEqual(Cours.objects.filter(external_id="cours-inedit-test").count(), 1)

    def test_dedups_against_an_existing_inedite_origin_cours_by_title(self):
        self._make_rappel("rdi-a")
        first, _ = ingest_cours_inedite(self._cours_payload(cours_id="cours-inedit-a", titre="Notion Partagée"))

        other_exercice = ExerciceInedite.objects.create(
            epreuve=_make_epreuve(blueprint=_make_blueprint(subject=self.subject, cursus=self.cursus)),
            numero_exercice="1",
        )
        rappel_b = self._make_rappel("rdi-b", "Notion Partagée bis", exercice=other_exercice)

        second, created = ingest_cours_inedite(
            self._cours_payload(cours_id="cours-inedit-b", rappel_id="rdi-b", titre="Notion Partagée"),
        )

        self.assertFalse(created)
        self.assertEqual(second.id, first.id)
        rappel_b.refresh_from_db()
        self.assertEqual(rappel_b.cours_id, first.id)

    def test_dedups_against_an_existing_classic_origin_cours_by_title(self):
        """Le scénario explicitement demandé : un rappel INÉDITE dont le titre de cours
        correspond à un Cours déjà publié par correction-experte (classique) doit s'y
        rattacher, jamais dupliquer - Cours est origine-agnostique (voir models.py)."""
        classic_cours = Cours.objects.create(
            external_id="cours-classic-pythagore", titre="Théorème de Pythagore",
            subject=self.subject, statut=StatutContenu.VALIDE,
        )
        self._make_rappel("rdi-pyth", "Pythagore")

        cours, created = ingest_cours_inedite(
            self._cours_payload(cours_id="cours-inedit-pyth", rappel_id="rdi-pyth", titre="Théorème de Pythagore"),
        )

        self.assertFalse(created)
        self.assertEqual(cours.id, classic_cours.id)
        self.assertEqual(RappelDeMethodeInedite.objects.get(external_id="rdi-pyth").cours_id, classic_cours.id)

    def test_pays_mismatch_raises(self):
        self._make_rappel()
        payload = self._cours_payload()
        payload["meta"]["pays"] = "sn"  # l'épreuve source est résolue au Cameroun
        with self.assertRaises(IngestionError):
            ingest_cours_inedite(payload)


class RunIneditIngestionTests(TestCase):
    """run_ingestion - scan de dossier ingest/_inedit/<code_pays>/..., dispatch par
    champ 'type', pays dérivé du chemin (voir _country_code_from_inedit_ingest_path)."""

    def setUp(self):
        Tag.objects.create(name="Suites numériques")

    def test_ingests_blueprint_then_epreuve_from_folder_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "_inedit" / "cm"
            root.mkdir(parents=True)
            (root / "bp1.json").write_text(json.dumps(_blueprint_payload()), encoding="utf-8")

            report = run_ingestion(root)

            self.assertEqual(report["blueprints_created"], 1)
            self.assertEqual(report["errors"], [])

            blueprint = Blueprint.objects.get(external_id="bp-cm-maths-bac-c-1")
            blueprint.statut = StatutContenu.VALIDE
            blueprint.save(update_fields=["statut"])

            (root / "ep1.json").write_text(json.dumps(_epreuve_payload()), encoding="utf-8")
            report2 = run_ingestion(root)

            # bp1.json est réingéré (idempotent, skip) en même temps que ep1.json (créé).
            self.assertEqual(report2["epreuves_created"], 1)
            self.assertEqual(report2["skipped"], 1)
            self.assertEqual(report2["errors"], [])
            self.assertTrue(EpreuveInedite.objects.filter(external_id="ep-cm-maths-bac-c-1-s1").exists())

    def test_unknown_type_field_is_reported_as_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "_inedit" / "cm"
            root.mkdir(parents=True)
            payload = _blueprint_payload()
            payload["type"] = "autre_chose"
            (root / "bad.json").write_text(json.dumps(payload), encoding="utf-8")

            report = run_ingestion(root)

            self.assertEqual(report["blueprints_created"], 0)
            self.assertEqual(len(report["errors"]), 1)

    def test_ingests_a_cours_file_and_links_it_to_the_epreuve_s_rappel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "_inedit" / "cm"
            root.mkdir(parents=True)
            (root / "bp1.json").write_text(json.dumps(_blueprint_payload()), encoding="utf-8")
            run_ingestion(root)
            Blueprint.objects.filter(external_id="bp-cm-maths-bac-c-1").update(statut=StatutContenu.VALIDE)

            epreuve_payload = _epreuve_payload(exercices=[{
                "numero_exercice": "1", "points": "8",
                "questions": [{
                    "numero": "1", "ordre": 1, "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.",
                    "rappels_de_methode": [
                        {"id": "rdi-ep1-ex1-q1-0", "competence": "Suites numériques", "contenu_markdown": "C."},
                    ],
                }],
            }])
            (root / "ep1.json").write_text(json.dumps(epreuve_payload), encoding="utf-8")
            (root / "ep1_cours_suites.json").write_text(json.dumps({
                "type": "cours", "cours_id": "cours-suites-numeriques-bac-c",
                "meta": {"titre": "Suites numériques", "matiere": "mathematiques"},
                "source": {"rappel_id": "rdi-ep1-ex1-q1-0"}, "sections": [],
            }), encoding="utf-8")

            report = run_ingestion(root)

            self.assertEqual(report["cours_created"], 1)
            self.assertEqual(report["errors"], [])
            rappel = RappelDeMethodeInedite.objects.get(external_id="rdi-ep1-ex1-q1-0")
            self.assertTrue(rappel.cours_genere)
            self.assertEqual(rappel.cours.titre, "Suites numériques")


class SelectInEditBatchTests(TestCase):
    """select_inedit_batch - sélection déterministe de couples (matière, cursus) sous-
    couverts, avec du matériel réel pour ancrer le style (voir sa docstring)."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        self.subject = Subject.objects.get(country=self.cm, code="MATHS")
        self.cursus = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")
        Tag.objects.create(name="Suites numériques")

    def _make_validated_lesson_with_exercise(self):
        lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus)
        Exercise.objects.create(
            lesson=lesson, numero_exercice="1", points="8",
            enonce_markdown="Énoncé réel.", corrige_markdown="Corrigé réel.", statut=StatutContenu.VALIDE,
        )
        return lesson

    def test_subject_cursus_pair_with_real_content_and_no_blueprint_is_selected(self):
        self._make_validated_lesson_with_exercise()

        requests = select_inedit_batch(self.cm, limit=5, floor=1)

        matieres = [r["matiere"] for r in requests]
        self.assertIn(self.subject.label, matieres)
        request = next(r for r in requests if r["matiere"] == self.subject.label)
        self.assertEqual(request["cursus"], [{"examen": "bac", "serie": "C"}])
        self.assertEqual(len(request["materiel_reference"]), 1)

    def test_pair_already_covered_is_not_selected(self):
        self._make_validated_lesson_with_exercise()
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.cm)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])

        requests = select_inedit_batch(self.cm, limit=5, floor=1)

        matieres = [r["matiere"] for r in requests]
        self.assertNotIn(self.subject.label, matieres)

    def test_pair_without_any_real_content_is_never_selected(self):
        requests = select_inedit_batch(self.cm, limit=5, floor=1)
        self.assertEqual(requests, [])

    def test_savoirs_prioritaires_ranks_least_covered_first(self):
        # Voir inedit.ingestion._savoirs_prioritaires : un simple indice informatif pour
        # le skill (pas un critère de sélection du couple matière/cursus lui-même).
        self._make_validated_lesson_with_exercise()
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero="90", titre="Module test")
        module.cursus.set([self.cursus])
        savoir_couvert = Savoir.objects.create(module=module, numero="I", intitule="Notion couverte")
        savoir_jamais_couvert = Savoir.objects.create(module=module, numero="II", intitule="Notion jamais couverte")

        Tag.objects.create(name="notion couverte tag", savoir_officiel=savoir_couvert)
        payload = {
            "epreuve_source": "bac-maths-savoirs-prio", "numero_exercice": "1",
            "matiere": "Mathématiques", "serie": "C", "examen": "BAC",
            "questions": [{"numero": "1", "enonce_markdown": "E.", "corrige_markdown": "C.", "themes": ["notion couverte tag"]}],
        }
        from catalog.ingestion import ingest_exercise
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-savoirs-prio"))

        requests = select_inedit_batch(self.cm, limit=5, floor=1)
        request = next(r for r in requests if r["matiere"] == self.subject.label)
        prioritaires = request["savoirs_prioritaires"]

        intitules = [p["intitule"] for p in prioritaires]
        self.assertIn("Notion jamais couverte", intitules)
        self.assertLess(intitules.index("Notion jamais couverte"), intitules.index("Notion couverte"))


def _make_epreuve_via_ingestion(country, **blueprint_overrides):
    blueprint, _ = ingest_blueprint(_blueprint_payload(**blueprint_overrides), country)
    blueprint.statut = StatutContenu.VALIDE
    blueprint.save(update_fields=["statut"])
    epreuve, _ = ingest_epreuve_inedite(_epreuve_payload(), country)
    return epreuve


class ScoreOriginaliteTests(TestCase):
    """score_originalite - similarité textuelle déterministe contre le corpus déjà
    publié du même (matière, cursus), voir sa docstring pour les arbitrages."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.subject = Subject.objects.get(country=self.country, code="MATHS")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")

    def _corpus_question(self, enonce_markdown):
        lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus)
        exercise = Exercise.objects.create(
            lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE,
            enonce_markdown="peu importe", corrige_markdown="peu importe",
        )
        Question.objects.create(
            exercise=exercise, numero="1", ordre=1, enonce_markdown=enonce_markdown, corrige_markdown="peu importe",
        )

    def test_returns_100_without_any_corpus_to_compare_against(self):
        epreuve = _make_epreuve_via_ingestion(self.country)
        self.assertEqual(score_originalite(epreuve), 100)

    def test_returns_100_when_epreuve_has_no_questions_yet(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject, titre="Vide",
        )
        epreuve.cursus.set(blueprint.cursus.all())
        self.assertEqual(score_originalite(epreuve), 100)

    def test_low_score_when_wording_matches_existing_corpus(self):
        # _epreuve_payload() génère une question dont enonce_markdown="Énoncé Q1."
        self._corpus_question("Énoncé Q1.")

        epreuve = _make_epreuve_via_ingestion(self.country)

        self.assertLess(score_originalite(epreuve), 20)

    def test_high_score_when_wording_is_unrelated_to_corpus(self):
        self._corpus_question(
            "Un texte complètement différent portant sur un tout autre sujet mathématique avancé et sans rapport.",
        )

        epreuve = _make_epreuve_via_ingestion(self.country)

        self.assertGreater(score_originalite(epreuve), 70)


class ScoreQualiteTests(TestCase):
    """score_qualite - part des compétences visées par le Blueprint réellement
    couvertes par au moins une QuestionInedite (voir QuestionInedite.themes)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        Tag.objects.create(name="Probabilités")

    def _blueprint_valide(self, competences=("Suites numériques",)):
        blueprint, _ = ingest_blueprint(_blueprint_payload(competences=list(competences)), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        return blueprint

    def test_full_coverage_scores_100(self):
        self._blueprint_valide()
        payload = _epreuve_payload(exercices=[{
            "numero_exercice": "1", "points": "8",
            "questions": [{
                "numero": "1", "ordre": 1, "enonce_markdown": "E1", "corrige_markdown": "C1",
                "themes": ["Suites numériques"],
            }],
        }])

        epreuve, _ = ingest_epreuve_inedite(payload, self.country)

        self.assertEqual(score_qualite(epreuve), 100)

    def test_no_coverage_scores_0(self):
        self._blueprint_valide()
        payload = _epreuve_payload(exercices=[{
            "numero_exercice": "1", "points": "8",
            "questions": [{"numero": "1", "ordre": 1, "enonce_markdown": "E1", "corrige_markdown": "C1"}],
        }])

        epreuve, _ = ingest_epreuve_inedite(payload, self.country)

        self.assertEqual(score_qualite(epreuve), 0)

    def test_partial_coverage_is_a_ratio(self):
        self._blueprint_valide(competences=["Suites numériques", "Probabilités"])
        payload = _epreuve_payload(exercices=[{
            "numero_exercice": "1", "points": "8",
            "questions": [{
                "numero": "1", "ordre": 1, "enonce_markdown": "E1", "corrige_markdown": "C1",
                "themes": ["Suites numériques"],
            }],
        }])

        epreuve, _ = ingest_epreuve_inedite(payload, self.country)

        self.assertEqual(score_qualite(epreuve), 50)


class ScoresAreComputedAtIngestionTests(TestCase):
    """calculer_scores est appelé automatiquement en fin d'ingest_epreuve_inedite -
    jamais un geste manuel séparé (voir sa docstring)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")

    def test_epreuve_has_scores_populated_right_after_ingestion(self):
        epreuve = _make_epreuve_via_ingestion(self.country)

        self.assertIsNotNone(epreuve.score_originalite)
        self.assertIsNotNone(epreuve.score_qualite)
        epreuve.refresh_from_db()
        self.assertIsNotNone(epreuve.score_originalite)
        self.assertIsNotNone(epreuve.score_qualite)


def _make_published_epreuve(country, cursus=None):
    """Épreuve complète, publiée (statut=VALIDE), avec une question QCM et une question
    ouverte, toutes deux taguées - pour exercer les endpoints d'API ci-dessous."""
    payload_blueprint = _blueprint_payload()
    if cursus is not None:
        payload_blueprint["cursus"] = [
            {"examen": cursus.examen.lower(), "serie": cursus.series.code if cursus.series else ""},
        ]
    blueprint, _ = ingest_blueprint(payload_blueprint, country)
    blueprint.statut = StatutContenu.VALIDE
    blueprint.save(update_fields=["statut"])

    payload = _epreuve_payload(exercices=[{
        "numero_exercice": "1", "points": "8",
        "questions": [
            {
                "numero": "1", "ordre": 1, "enonce_markdown": "QCM ?", "corrige_markdown": "Corrigé QCM.",
                "type_reponse": "qcm",
                "choix": [{"lettre": "a", "texte": "Un"}, {"lettre": "b", "texte": "Deux"}],
                "reponse_correcte": "b", "themes": ["Suites numériques"],
            },
            {
                "numero": "2", "ordre": 2, "enonce_markdown": "Question ouverte.", "corrige_markdown": "Corrigé ouvert.",
                "type_reponse": "ouverte", "themes": ["Suites numériques"],
            },
        ],
    }])
    epreuve, _ = ingest_epreuve_inedite(payload, country)
    epreuve.statut = StatutContenu.VALIDE
    epreuve.save(update_fields=["statut"])
    return epreuve


class ListMyInscriptionsInediteAPITests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.user = User.objects.create_user(phone_number="677500001", password="x")
        self.other_user = User.objects.create_user(phone_number="677500002", password="x")
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.get("/inedit/mes-inscriptions/")
        self.assertEqual(response.status_code, 401)

    def test_returns_only_the_authenticated_user_inscriptions(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=10),
        )
        InscriptionInedite.objects.create(
            user=self.other_user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=10),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/inedit/mes-inscriptions/")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["cursus"]["id"], self.cursus.pk)
        self.assertTrue(response.data[0]["is_active"])

    def test_empty_when_no_inscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/inedit/mes-inscriptions/")
        self.assertEqual(response.data, [])


class ListEpreuvesAPITests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="D")
        self.user = User.objects.create_user(phone_number="677400001", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_requires_cursus_param(self):
        response = self.client.get("/inedit/epreuves/")
        self.assertEqual(response.status_code, 400)

    def test_only_valide_epreuves_for_the_requested_cursus_are_listed(self):
        epreuve = _make_published_epreuve(self.country)
        autre_blueprint = Blueprint.objects.create(subject=epreuve.subject, titre="Autre cursus")
        autre_blueprint.cursus.set([self.other_cursus])

        response = self.client.get("/inedit/epreuves/", {"cursus": self.cursus.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([e["id"] for e in response.data], [epreuve.id])

    def test_exposes_indicative_duree_minutes_from_blueprint(self):
        epreuve = _make_published_epreuve(self.country)

        response = self.client.get("/inedit/epreuves/", {"cursus": self.cursus.pk})

        self.assertEqual(response.data[0]["duree_minutes"], epreuve.blueprint.duree_minutes)


class EpreuveInediteDetailAPITests(TestCase):
    """GET /inedit/epreuves/<id>/ - fiche détail, réutilisée par le catalogue fusionné
    (voir catalog.inedit_bridge.epreuve_inedite_catalogue_payload). Toujours 200, même
    anonyme - le gating vit dans has_access, jamais dans le statut HTTP (même patron
    que catalog.views.LessonDetailView)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400040", password="x")
        self.client = APIClient()

    def test_anonymous_sees_detail_with_has_access_false(self):
        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_access"])
        self.assertEqual(response.data["slug"], self.epreuve.slug)
        self.assertIsNone(response.data["lesson_type"])
        self.assertEqual(response.data["origine"], "INEDITE")

    def test_lookup_by_slug_resolves_the_same_epreuve_as_by_id(self):
        response = self.client.get(f"/inedit/epreuves/{self.epreuve.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.epreuve.id)

    def test_lookup_by_numeric_id_still_works(self):
        # Compat historique - un lien "/epreuves-inedites/<id>" partagé avant
        # l'introduction du slug (voir EpreuveInedite.slug) doit rester valide.
        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.epreuve.id)

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/inedit/epreuves/ce-slug-n-existe-pas/")
        self.assertEqual(response.status_code, 404)

    def test_has_access_true_with_active_inscription(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")

        self.assertTrue(response.data["has_access"])

    def test_404_for_brouillon(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(external_id="bp-brouillon-detail"), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve_brouillon, _ = ingest_epreuve_inedite(
            _epreuve_payload(external_id="ep-brouillon-detail", blueprint_external_id="bp-brouillon-detail"),
            self.country,
        )

        response = self.client.get(f"/inedit/epreuves/{epreuve_brouillon.id}/")

        self.assertEqual(response.status_code, 404)

    def test_related_cours_reflects_linked_rappel(self):
        exercice = self.epreuve.exercices.get()
        rappel = RappelDeMethodeInedite.objects.create(
            exercice=exercice, external_id="rdi-detail-test", competence="C",
        )
        cours = Cours.objects.create(
            external_id="cours-detail-test", titre="Cours lié",
            subject=self.epreuve.subject, statut=StatutContenu.VALIDE,
        )
        rappel.cours = cours
        rappel.save(update_fields=["cours"])

        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")

        self.assertEqual([c["titre"] for c in response.data["related_cours"]], ["Cours lié"])

    def test_related_cours_empty_when_no_rappel_linked(self):
        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")
        self.assertEqual(response.data["related_cours"], [])

    def test_apercu_enonce_markdown_is_the_first_questions_enonce(self):
        # _make_published_epreuve crée un seul exercice ("1"), questions "1" (ordre=1,
        # QCM, énoncé "QCM ?") et "2" (ordre=2) - le premier par ordre, jamais le
        # corrigé ni les questions suivantes (voir catalog.inedit_bridge._apercu_enonce).
        response = self.client.get(f"/inedit/epreuves/{self.epreuve.id}/")
        self.assertEqual(response.data["apercu_enonce_markdown"], "QCM ?")
        self.assertEqual(response.data["apercu_numero_exercice"], "1")

    def test_apercu_enonce_markdown_is_none_without_any_exercice(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(external_id="bp-vide-detail"), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve_vide = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject,
            titre="Sans exercice", statut=StatutContenu.VALIDE,
        )
        epreuve_vide.cursus.set(blueprint.cursus.all())

        response = self.client.get(f"/inedit/epreuves/{epreuve_vide.id}/")

        self.assertIsNone(response.data["apercu_enonce_markdown"])
        self.assertIsNone(response.data["apercu_numero_exercice"])


class ListMyTentativesInediteAPITests(TestCase):
    """Historique (AccountPage, "Mes épreuves inédites") - voir list_my_tentatives_inedites."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677500010", password="x")
        self.other_user = User.objects.create_user(phone_number="677500011", password="x")
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.get("/inedit/mes-tentatives/")
        self.assertEqual(response.status_code, 401)

    def test_returns_only_the_authenticated_user_tentatives_most_recent_first(self):
        TentativeInedite.objects.create(user=self.other_user, epreuve=self.epreuve)
        older = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        newer = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/inedit/mes-tentatives/")

        self.assertEqual([t["id"] for t in response.data], [newer.id, older.id])
        self.assertEqual(response.data[0]["epreuve_titre"], self.epreuve.titre)

    def test_includes_both_in_progress_and_submitted_tentatives(self):
        en_cours = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        soumise = TentativeInedite.objects.create(
            user=self.user, epreuve=self.epreuve, submitted_at=timezone.now(), score_obtenu=75,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/inedit/mes-tentatives/")

        by_id = {t["id"]: t for t in response.data}
        self.assertIsNone(by_id[en_cours.id]["submitted_at"])
        self.assertEqual(by_id[soumise.id]["score_obtenu"], 75)


class StartTentativeAPITests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400002", password="x")
        self.client = APIClient()

    def test_requires_authentication(self):
        response = self.client.post("/inedit/tentatives/", {"epreuve": self.epreuve.id})
        self.assertEqual(response.status_code, 401)

    def test_denied_without_active_inscription_inedite(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/inedit/tentatives/", {"epreuve": self.epreuve.id})
        self.assertEqual(response.status_code, 403)

    def test_base_subscription_alone_is_not_enough(self):
        from subscriptions.models import Subscription

        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/inedit/tentatives/", {"epreuve": self.epreuve.id})
        self.assertEqual(response.status_code, 403)

    def test_allowed_with_active_inscription_inedite(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/inedit/tentatives/", {"epreuve": self.epreuve.id})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(TentativeInedite.objects.filter(user=self.user, epreuve=self.epreuve).exists())
        self.assertEqual(len(response.data["exercices"]), 1)
        self.assertEqual(response.data["duree_minutes"], self.epreuve.blueprint.duree_minutes)
        # Mode libre par défaut (exam_mode_started_at jamais engagé) : le corrigé est
        # disponible dès la création, même confiance que le lecteur classique - voir
        # _correction_disponible. Seul un mode examen actif le masquerait.
        for question in response.data["exercices"][0]["questions"]:
            self.assertIn("corrige_markdown", question)

    def test_brouillon_epreuve_is_never_startable(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(external_id="bp-brouillon"), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve_brouillon, _ = ingest_epreuve_inedite(
            _epreuve_payload(external_id="ep-brouillon", blueprint_external_id="bp-brouillon"), self.country,
        )
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/inedit/tentatives/", {"epreuve": epreuve_brouillon.id})

        self.assertEqual(response.status_code, 404)


class TentativeFlowAPITests(TestCase):
    """reveal_corrige/answer_question/complete_tentative - le corrigé ne doit jamais
    fuiter avant réponse, et answer_question doit alimenter quiz.RevisionSchedule."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400010", password="x")
        self.other_user = User.objects.create_user(phone_number="677400011", password="x")
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tentative = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        exercice = self.epreuve.exercices.get()
        self.qcm_question = exercice.questions.get(numero="1")
        self.ouverte_question = exercice.questions.get(numero="2")

    def test_cannot_access_another_users_tentative(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")
        self.assertEqual(response.status_code, 404)

    def test_tentative_payload_exposes_exercice_intro(self):
        """Le support partagé est servi au niveau de l'exercice, jamais recopié dans
        chaque question : le frontend l'affiche une fois en tête d'exercice (voir
        InediteTentativePage.tsx). Sans ce champ dans le payload, un exercice de SVT
        bâti sur un document deviendrait insoluble question par question."""
        exercice = self.epreuve.exercices.get()
        exercice.enonce_intro_markdown = "**Document 1** : protocole expérimental."
        exercice.save(update_fields=["enonce_intro_markdown"])

        response = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")

        self.assertEqual(response.status_code, 200)
        exercice_payload = response.data["exercices"][0]
        self.assertEqual(exercice_payload["enonce_intro_markdown"], "**Document 1** : protocole expérimental.")
        self.assertNotIn("enonce_intro_markdown", exercice_payload["questions"][0])

    def test_reveal_corrige_does_not_record_an_answer(self):
        response = self.client.get(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.ouverte_question.id}/corrige/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["corrige_markdown"], "Corrigé ouvert.")
        self.assertFalse(
            TentativeReponse.objects.filter(tentative=self.tentative, question=self.ouverte_question).exists(),
        )

    def test_qcm_answer_requires_reponse_choisie(self):
        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/", {},
        )
        self.assertEqual(response.status_code, 400)

    def test_qcm_answer_is_recorded_and_scored_once_correction_available(self):
        # self.tentative n'engage jamais le mode examen ici, donc _correction_disponible
        # est déjà True dès la création (mode libre) - le corrigé apparaît donc bien à
        # la réponse, mais PAS parce qu'elle vient d'être enregistrée : voir
        # ExamModeAPITests.test_qcm_answer_during_exam_mode_withholds_corrige_and_est_correcte
        # pour le cas où répondre n'expose au contraire rien du tout.
        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "b"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["corrige_markdown"], "Corrigé QCM.")
        self.assertTrue(response.data["reponse"]["est_correcte"])

    def test_incorrect_answer_registers_a_revision_schedule_for_the_theme(self):
        self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "a"},
        )
        theme = Tag.objects.get(name="Suites numériques")
        self.assertTrue(RevisionSchedule.objects.filter(user=self.user, cursus=self.cursus, theme=theme).exists())

    def test_open_question_answer_requires_valid_resultat_declare(self):
        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.ouverte_question.id}/answer/",
            {"resultat_declare": "PAS_UNE_VALEUR"},
        )
        self.assertEqual(response.status_code, 400)

    def test_complete_tentative_computes_score_and_is_idempotent(self):
        self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "b"},
        )
        self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.ouverte_question.id}/answer/",
            {"resultat_declare": "ECHEC"},
        )

        response = self.client.post(f"/inedit/tentatives/{self.tentative.id}/completer/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["questions_repondues"], 2)
        self.assertEqual(response.data["score"], 50)
        self.tentative.refresh_from_db()
        self.assertIsNotNone(self.tentative.submitted_at)
        self.assertEqual(self.tentative.score_obtenu, 50)

        submitted_at_first = self.tentative.submitted_at
        self.client.post(f"/inedit/tentatives/{self.tentative.id}/completer/")
        self.tentative.refresh_from_db()
        self.assertEqual(self.tentative.submitted_at, submitted_at_first)


class CorrigeMarkdownCoursLinksAPITests(TestCase):
    """corrige_markdown doit porter les mêmes marqueurs [COURS_LINK:<slug>] que côté
    catalog (voir catalog.rendering.annotate_cours_links) - jusqu'ici jamais branché
    côté inédit alors que RappelDeMethodeInedite.cours est peuplé exactement pareil
    (voir inedit.ingestion.ingest_cours_inedite)."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677400020", password="x")
        self.epreuve = _make_epreuve()
        self.exercice = ExerciceInedite.objects.create(epreuve=self.epreuve, numero_exercice="1")
        self.cours = Cours.objects.create(
            external_id="cours-rdi-test", titre="Similitudes planes", subject=self.epreuve.subject,
        )
        self.question = QuestionInedite.objects.create(
            exercice=self.exercice, numero="1", ordre=1, enonce_markdown="Énoncé.",
            corrige_markdown="Corrigé.\n\n### Rappel de méthode\n\nContenu du rappel.",
            type_reponse=TypeReponse.OUVERTE,
        )
        RappelDeMethodeInedite.objects.create(
            exercice=self.exercice, external_id="rdi-test-1", competence="Test",
            contenu_markdown="Contenu du rappel.", cours=self.cours,
        )
        self.tentative = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_tentative_detail_includes_the_cours_link_marker(self):
        response = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")
        corrige = response.data["exercices"][0]["questions"][0]["corrige_markdown"]
        self.assertIn(f"[COURS_LINK:{self.cours.slug}]", corrige)

    def test_reveal_corrige_includes_the_cours_link_marker(self):
        response = self.client.get(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/corrige/",
        )
        self.assertIn(f"[COURS_LINK:{self.cours.slug}]", response.data["corrige_markdown"])

    def test_a_rappel_belonging_to_another_question_of_the_same_exercice_never_leaks(self):
        # RappelDeMethodeInedite est rattaché à l'exercice, pas à la question (voir sa
        # docstring) - un second rappel, dont le texte n'apparaît que dans une AUTRE
        # question du même exercice, ne doit jamais être injecté ici (append_unmatched=
        # False, voir annotate_cours_links) : sinon "Voir le cours complet" pointerait
        # vers un cours sans rapport avec ce que l'élève vient de lire.
        autre_cours = Cours.objects.create(
            external_id="cours-rdi-autre", titre="Un tout autre cours", subject=self.epreuve.subject,
        )
        QuestionInedite.objects.create(
            exercice=self.exercice, numero="2", ordre=2, enonce_markdown="Énoncé Q2.",
            corrige_markdown="Corrigé Q2.\n\n### Rappel de méthode\n\nContenu Q2 uniquement.",
            type_reponse=TypeReponse.OUVERTE,
        )
        RappelDeMethodeInedite.objects.create(
            exercice=self.exercice, external_id="rdi-test-2", competence="Test 2",
            contenu_markdown="Contenu Q2 uniquement.", cours=autre_cours,
        )

        response = self.client.get(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/corrige/",
        )

        self.assertNotIn(f"[COURS_LINK:{autre_cours.slug}]", response.data["corrige_markdown"])


class ExamModeAPITests(TestCase):
    """start_exam_mode/_correction_disponible/_auto_complete_if_expired - la vraie
    frontière anti-triche du module (voir la docstring de _correction_disponible)."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400020", password="x")
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tentative = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        exercice = self.epreuve.exercices.get()
        self.qcm_question = exercice.questions.get(numero="1")
        self.ouverte_question = exercice.questions.get(numero="2")

    def test_start_exam_mode_sets_timestamp_and_hides_corrige(self):
        response = self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["exam_mode_started_at"])
        self.assertFalse(response.data["correction_disponible"])

        detail = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")
        for question in detail.data["exercices"][0]["questions"]:
            self.assertNotIn("corrige_markdown", question)

    def test_start_exam_mode_requires_duree_minutes(self):
        blueprint, _ = ingest_blueprint(
            _blueprint_payload(external_id="bp-sans-duree", duree_minutes=None), self.country,
        )
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve_sans_duree, _ = ingest_epreuve_inedite(
            _epreuve_payload(external_id="ep-sans-duree", blueprint_external_id="bp-sans-duree"), self.country,
        )
        epreuve_sans_duree.statut = StatutContenu.VALIDE
        epreuve_sans_duree.save(update_fields=["statut"])
        tentative = TentativeInedite.objects.create(user=self.user, epreuve=epreuve_sans_duree)

        response = self.client.post(f"/inedit/tentatives/{tentative.id}/mode-examen/")

        self.assertEqual(response.status_code, 400)

    def test_start_exam_mode_rejected_after_first_answer(self):
        self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "b"},
        )
        response = self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")
        self.assertEqual(response.status_code, 409)

    def test_start_exam_mode_is_idempotent(self):
        first = self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")
        second = self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["exam_mode_started_at"], first.data["exam_mode_started_at"])

    def test_start_exam_mode_rejected_once_submitted(self):
        self.client.post(f"/inedit/tentatives/{self.tentative.id}/completer/")
        response = self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")
        self.assertEqual(response.status_code, 409)

    def test_qcm_answer_during_exam_mode_withholds_corrige_and_est_correcte(self):
        self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")

        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "b"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["reponse"]["reponse_choisie"], "b")
        self.assertNotIn("est_correcte", response.data["reponse"])
        self.assertNotIn("corrige_markdown", response.data)
        self.assertNotIn("reponse_correcte", response.data)

    def test_answer_rejected_after_time_expires(self):
        self.tentative.exam_mode_started_at = timezone.now() - timezone.timedelta(
            minutes=self.epreuve.blueprint.duree_minutes + 5,
        )
        self.tentative.save(update_fields=["exam_mode_started_at"])

        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.qcm_question.id}/answer/",
            {"reponse_choisie": "b"},
        )

        self.assertEqual(response.status_code, 409)
        self.tentative.refresh_from_db()
        # Auto-complétée par la garde de answer_question avant même le traitement de
        # cette réponse (jamais enregistrée) - score_obtenu reste donc None ici,
        # aucune réponse n'existait avant l'expiration (voir _tentative_resultat_payload,
        # score=None quand repondues=0).
        self.assertIsNotNone(self.tentative.submitted_at)

    def test_tentative_detail_auto_completes_and_reveals_corrige_after_expiry(self):
        self.tentative.exam_mode_started_at = timezone.now() - timezone.timedelta(
            minutes=self.epreuve.blueprint.duree_minutes + 5,
        )
        self.tentative.save(update_fields=["exam_mode_started_at"])

        response = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")

        self.assertIsNotNone(response.data["submitted_at"])
        self.assertTrue(response.data["correction_disponible"])
        for question in response.data["exercices"][0]["questions"]:
            self.assertIn("corrige_markdown", question)

    def test_reveal_corrige_blocked_during_active_exam_mode(self):
        self.client.post(f"/inedit/tentatives/{self.tentative.id}/mode-examen/")

        response = self.client.get(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.ouverte_question.id}/corrige/",
        )

        self.assertEqual(response.status_code, 403)

    def test_complete_tentative_exposes_temps_total_secondes_on_first_call(self):
        response = self.client.post(f"/inedit/tentatives/{self.tentative.id}/completer/")
        self.assertIsNotNone(response.data["temps_total_secondes"])

    def test_temps_total_secondes_is_null_before_submission(self):
        # Aucun endpoint HTTP n'expose _tentative_resultat_payload avant soumission
        # (complete_tentative soumet toujours) - on appelle directement la fonction
        # pour vérifier ce cas intermédiaire.
        from .views import _tentative_resultat_payload

        self.assertIsNone(_tentative_resultat_payload(self.tentative)["temps_total_secondes"])


class QuestionMarqueeAPITests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400030", password="x")
        self.other_user = User.objects.create_user(phone_number="677400031", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tentative = TentativeInedite.objects.create(user=self.user, epreuve=self.epreuve)
        self.question = self.epreuve.exercices.get().questions.get(numero="1")

    def test_toggle_adds_then_removes(self):
        first = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/marquer/",
        )
        self.assertEqual(first.data["questions_marquees"], [self.question.id])

        second = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/marquer/",
        )
        self.assertEqual(second.data["questions_marquees"], [])

    def test_flag_persists_in_tentative_detail(self):
        self.client.post(f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/marquer/")

        response = self.client.get(f"/inedit/tentatives/{self.tentative.id}/")

        self.assertEqual(response.data["questions_marquees"], [self.question.id])

    def test_cannot_flag_question_from_another_epreuve(self):
        autre_question = _make_question()  # épreuve distincte de self.tentative.epreuve

        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{autre_question.id}/marquer/",
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_flag_on_another_users_tentative(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            f"/inedit/tentatives/{self.tentative.id}/questions/{self.question.id}/marquer/",
        )

        self.assertEqual(response.status_code, 404)


class CompileFromExercicesTests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")

    def test_flattens_exercices_and_questions_in_order_and_saves(self):
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject, titre="Test",
        )
        epreuve.cursus.set(blueprint.cursus.all())
        exercice = ExerciceInedite.objects.create(epreuve=epreuve, numero_exercice="1", points="8")
        QuestionInedite.objects.create(
            exercice=exercice, numero="1", ordre=1,
            enonce_markdown="Énoncé Q1.", corrige_markdown="Réponse Q1.",
        )

        epreuve.compile_from_exercices()

        self.assertIn("Exercice 1", epreuve.enonce_markdown)
        self.assertIn("Énoncé Q1.", epreuve.enonce_markdown)
        self.assertNotIn("Réponse Q1.", epreuve.enonce_markdown)
        # corrige_markdown restitue l'énoncé ET la réponse - lisible seul (voir la docstring).
        self.assertIn("Énoncé Q1.", epreuve.corrige_markdown)
        self.assertIn("Réponse Q1.", epreuve.corrige_markdown)

        epreuve.refresh_from_db()
        self.assertIn("Réponse Q1.", epreuve.corrige_markdown)

    def test_exercice_intro_precedes_questions_once_in_both_documents(self):
        """Le support partagé doit précéder les questions dans l'énoncé compilé (dont
        dérive le PDF du sujet, voir inedit.sujet_pdf._render_html) ET dans le corrigé
        autonome - une seule fois, jamais répété par question."""
        blueprint, _ = ingest_blueprint(_blueprint_payload(), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject, titre="Test intro",
        )
        epreuve.cursus.set(blueprint.cursus.all())
        exercice = ExerciceInedite.objects.create(
            epreuve=epreuve, numero_exercice="1", points="8",
            enonce_intro_markdown="**Document 1** : courbe de croissance.",
        )
        QuestionInedite.objects.create(
            exercice=exercice, numero="1", ordre=1,
            enonce_markdown="Énoncé Q1.", corrige_markdown="Réponse Q1.",
        )
        QuestionInedite.objects.create(
            exercice=exercice, numero="2", ordre=2,
            enonce_markdown="Énoncé Q2.", corrige_markdown="Réponse Q2.",
        )

        epreuve.compile_from_exercices()

        for document in (epreuve.enonce_markdown, epreuve.corrige_markdown):
            self.assertEqual(document.count("**Document 1** : courbe de croissance."), 1)
            self.assertLess(document.index("Document 1"), document.index("Énoncé Q1."))
