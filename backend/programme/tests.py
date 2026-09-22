import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, override_settings

from catalog.ingestion import ingest_exercise
from catalog.models import Cours, Country, Cursus, Difficulte, Examen, Series, StatutContenu, Subject, Tag, TypeReponse
from quiz.models import CompetenceItem
from .models import Module, Savoir


def _exercise_payload(epreuve_source, examen="BAC", serie="C", theme="pgcd"):
    return {
        "epreuve_source": epreuve_source,
        "numero_exercice": "1",
        "matiere": "Mathématiques",
        "serie": serie,
        "examen": examen,
        "questions": [
            {"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": [theme]},
        ],
    }


def _entry(classe, numero, serie_label, series, examen, savoirs=None, **overrides):
    return {
        "country": "CM",
        "subject": "MATHS",
        "classe": classe,
        "examen": examen,
        "series": series,
        "serie_label": serie_label,
        "numero": numero,
        "titre": overrides.get("titre", f"Module {numero} ({serie_label or classe})"),
        "credit_heures": overrides.get("credit_heures", 10),
        "famille_situations": overrides.get("famille_situations", ""),
        "ordre": overrides.get("ordre", 0),
        "savoirs": savoirs or [],
    }


class LoadProgrammeOfficielCommandTests(TestCase):
    """`manage.py load_programme_officiel` - voir
    programme.management.commands.load_programme_officiel. Utilise un petit fixture
    ad hoc (pas le vrai programme_officiel_cm_maths.json, dont le contenu peut
    évoluer indépendamment de ces tests)."""

    def _run(self, entries, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(entries), encoding="utf-8")
            call_command("load_programme_officiel", str(path), stdout=StringIO(), **kwargs)

    def test_creates_modules_and_savoirs(self):
        entries = [
            _entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
                {"numero": "I", "intitule": "Notion 1", "ordre": 0},
                {"numero": "II", "intitule": "Notion 2", "ordre": 1},
            ]),
        ]
        self._run(entries)

        module = Module.objects.get(classe="1ere", serie_label="D", numero="21")
        self.assertEqual(module.titre, "Module 21 (D)")
        self.assertEqual(module.credit_heures, 10)
        self.assertEqual(list(module.savoirs.values_list("intitule", flat=True)), ["Notion 1", "Notion 2"])

    def test_distinguishes_modules_sharing_the_same_numero_across_series(self):
        # Régression : le programme officiel repart à 21 pour chaque série d'une
        # même classe (1ère D, 1ère C-E ont chacune un "Module 21" distinct) - le
        # numéro seul ne suffit pas à identifier un module, voir Module.serie_label.
        entries = [
            _entry("1ere", "21", "C-E", ["C", "E"], Examen.PROBATOIRE, titre="Relations C-E"),
            _entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, titre="Relations D"),
        ]
        self._run(entries)

        self.assertEqual(Module.objects.filter(classe="1ere", numero="21").count(), 2)
        ce = Module.objects.get(classe="1ere", serie_label="C-E", numero="21")
        d = Module.objects.get(classe="1ere", serie_label="D", numero="21")
        self.assertEqual(ce.titre, "Relations C-E")
        self.assertEqual(d.titre, "Relations D")

    def test_resolves_combined_series_label_to_every_underlying_cursus(self):
        entries = [_entry("1ere", "21", "C-E", ["C", "E"], Examen.PROBATOIRE)]
        self._run(entries)

        module = Module.objects.get(classe="1ere", serie_label="C-E", numero="21")
        cm = Country.objects.get(code="CM")
        expected = set(Cursus.objects.filter(country=cm, examen=Examen.PROBATOIRE, series__code__in=["C", "E"]))
        self.assertEqual(set(module.cursus.all()), expected)
        self.assertEqual(module.cursus.count(), 2)

    def test_leaves_module_unattached_when_examen_is_null(self):
        # Cas de la 2nde : pas d'examen national au Cameroun, donc aucun Cursus à
        # rattacher - le module reste dans le référentiel mais isolé.
        entries = [_entry("2nde", "17", "A", [], None)]
        self._run(entries)

        module = Module.objects.get(classe="2nde", numero="17")
        self.assertEqual(module.cursus.count(), 0)

    def test_resolves_bepc_single_cursus_without_series(self):
        entries = [_entry("6e", "1", "", [], Examen.BEPC)]
        self._run(entries)

        module = Module.objects.get(classe="6e", numero="1")
        cm = Country.objects.get(code="CM")
        self.assertEqual(list(module.cursus.all()), [Cursus.objects.get(country=cm, examen=Examen.BEPC, series__isnull=True)])

    def test_is_idempotent(self):
        entries = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE)]
        self._run(entries)
        self._run(entries)

        self.assertEqual(Module.objects.filter(classe="1ere", serie_label="D", numero="21").count(), 1)

    def test_resyncs_savoirs_on_reload_instead_of_merging(self):
        entries_v1 = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
            {"numero": "I", "intitule": "Ancienne notion", "ordre": 0},
        ])]
        entries_v2 = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
            {"numero": "I", "intitule": "Notion corrigée", "ordre": 0},
        ])]
        self._run(entries_v1)
        self._run(entries_v2)

        module = Module.objects.get(classe="1ere", serie_label="D", numero="21")
        self.assertEqual(list(module.savoirs.values_list("intitule", flat=True)), ["Notion corrigée"])

    def test_reload_preserves_savoir_pk_and_fk_links_when_unchanged(self):
        # Régression du 2026-08-12 : un premier passage (delete-all + bulk_create)
        # recréait chaque Savoir avec un nouveau pk à chaque rechargement, ce qui
        # mettait à NULL en cascade (Tag.savoir_officiel, on_delete=SET_NULL) tout
        # rattachement déjà établi par une passe de curation - silencieusement, sans
        # jamais passer par _link_tags_to_savoir (qui, lui, protège bien ces liens).
        entries = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
            {"numero": "I", "intitule": "Notion stable", "ordre": 0},
        ])]
        self._run(entries)
        savoir = Savoir.objects.get(module__classe="1ere", module__serie_label="D", numero="I")
        tag = Tag.objects.create(name="notion stable tag", savoir_officiel=savoir)

        self._run(entries)  # même contenu, deuxième passage

        savoir.refresh_from_db()
        tag.refresh_from_db()
        self.assertEqual(Savoir.objects.get(module__classe="1ere", module__serie_label="D", numero="I").pk, savoir.pk)
        self.assertEqual(tag.savoir_officiel_id, savoir.pk)

    def test_reload_removes_savoir_no_longer_in_fixture(self):
        entries_v1 = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
            {"numero": "I", "intitule": "Notion A", "ordre": 0},
            {"numero": "II", "intitule": "Notion B", "ordre": 1},
        ])]
        entries_v2 = [_entry("1ere", "21", "D", ["D"], Examen.PROBATOIRE, savoirs=[
            {"numero": "I", "intitule": "Notion A", "ordre": 0},
        ])]
        self._run(entries_v1)
        self._run(entries_v2)

        module = Module.objects.get(classe="1ere", serie_label="D", numero="21")
        self.assertEqual(list(module.savoirs.values_list("numero", flat=True)), ["I"])

    def test_reports_unattached_module_count(self):
        entries = [_entry("2nde", "17", "A", [], None)]
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(entries), encoding="utf-8")
            call_command("load_programme_officiel", str(path), stdout=out)

        self.assertIn("1 module(s) sans Cursus", out.getvalue())


class ModuleUniqueConstraintTests(TestCase):
    """Verrou en base pour la même raison que le test de régression ci-dessus :
    (subject, classe, serie_label, numero) doit rester la clé naturelle complète."""

    def setUp(self):
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")

    def test_rejects_duplicate_natural_key(self):
        Module.objects.create(subject=self.maths, classe="1ere", serie_label="D", numero="21", titre="A")
        with self.assertRaises(IntegrityError):
            Module.objects.create(subject=self.maths, classe="1ere", serie_label="D", numero="21", titre="B")

    def test_allows_same_numero_with_a_different_serie_label(self):
        Module.objects.create(subject=self.maths, classe="1ere", serie_label="C-E", numero="21", titre="A")
        Module.objects.create(subject=self.maths, classe="1ere", serie_label="D", numero="21", titre="B")
        self.assertEqual(Module.objects.filter(classe="1ere", numero="21").count(), 2)


class SavoirTests(TestCase):
    def test_str_without_numero_omits_the_leading_dot(self):
        maths = Subject.objects.get(country__code="CM", code="MATHS")
        module = Module.objects.create(subject=maths, classe="6e", numero="2", titre="Organisation")
        savoir = Savoir.objects.create(module=module, numero="", intitule="Proportionnalité")

        self.assertEqual(str(savoir), "Proportionnalité")


class MapTagsToSavoirOfficielCommandTests(TestCase):
    """`manage.py map_tags_to_savoir_officiel` - voir programme.management.commands.
    map_tags_to_savoir_officiel. N'utilise que la règle arithmétique (pgcd -> ARITHMETIQUE)
    du jeu de règles réel : le but ici est la mécanique (dry-run, non-écrasement,
    désambiguïsation par l'usage), pas la couverture des règles elles-mêmes."""

    def setUp(self):
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")

    def _make_savoir(self, classe, serie_label, numero, savoir_numero, intitule, module_titre="RELATIONS ET OPERATIONS FONDAMENTALES"):
        module = Module.objects.create(subject=self.maths, classe=classe, serie_label=serie_label, numero=numero, titre=module_titre)
        return Savoir.objects.create(module=module, numero=savoir_numero, intitule=intitule)

    def _tag_a_real_question(self, epreuve_source="bac-maths-map", **payload_overrides):
        # Le queryset de la commande ne considère que les Tag réellement en usage
        # (`lessons_as_theme__...`) - un Tag.objects.create() nu, jamais rattaché à
        # aucun contenu, n'entre jamais dans son périmètre (fidèle aux vraies données :
        # les 1523 tags maths CM viennent tous d'un usage réel). D'où ce passage par
        # ingest_exercise plutôt qu'une simple création de Tag dans ces tests.
        ingest_exercise(
            _exercise_payload(epreuve_source, **payload_overrides),
            source_dir=Path(f"ingest/cm/{epreuve_source}"),
        )
        return Tag.objects.get(name=payload_overrides.get("theme", "pgcd"))

    def test_dry_run_writes_nothing(self):
        self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        tag = self._tag_a_real_question()

        call_command("map_tags_to_savoir_officiel", "--dry-run", stdout=StringIO())

        tag.refresh_from_db()
        self.assertIsNone(tag.savoir_officiel_id)

    def test_unambiguous_match_gets_linked(self):
        savoir = self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        tag = self._tag_a_real_question()

        call_command("map_tags_to_savoir_officiel", stdout=StringIO())

        tag.refresh_from_db()
        self.assertEqual(tag.savoir_officiel_id, savoir.pk)

    def test_never_overwrites_an_existing_link(self):
        self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        other_savoir = self._make_savoir("Tle", "D", "91", "I", "AUTRE NOTION", module_titre="AUTRE MODULE")
        tag = self._tag_a_real_question()
        tag.savoir_officiel = other_savoir
        tag.save(update_fields=["savoir_officiel"])

        call_command("map_tags_to_savoir_officiel", stdout=StringIO())

        tag.refresh_from_db()
        self.assertEqual(tag.savoir_officiel_id, other_savoir.pk)

    def test_ambiguous_candidates_left_unmapped_without_usage_signal(self):
        # Aucun des deux savoirs candidats n'a de Cursus rattaché : même avec un usage
        # réel du tag, rien ne permet de départager - reste non rattaché plutôt que deviné.
        self._make_savoir("1ere", "C-E", "90", "I", "ARITHMETIQUE")
        self._make_savoir("Tle", "C-E", "91", "I", "ARITHMETIQUE", module_titre="AUTRE MODULE")
        tag = self._tag_a_real_question()

        call_command("map_tags_to_savoir_officiel", stdout=StringIO())

        tag.refresh_from_db()
        self.assertIsNone(tag.savoir_officiel_id)

    def test_ambiguous_candidates_disambiguated_by_actual_usage(self):
        cm = Country.objects.get(code="CM")
        cursus_probatoire_c = Cursus.objects.get(country=cm, examen=Examen.PROBATOIRE, series__code="C")
        cursus_bac_c = Cursus.objects.get(country=cm, examen=Examen.BAC, series__code="C")

        s_1ere = self._make_savoir("1ere", "C-E", "90", "I", "ARITHMETIQUE")
        s_1ere.module.cursus.set([cursus_probatoire_c])
        s_tle = self._make_savoir("Tle", "C-E", "91", "I", "ARITHMETIQUE", module_titre="AUTRE MODULE")
        s_tle.module.cursus.set([cursus_bac_c])

        # Le tag n'est utilisé que sur du contenu Probatoire (1ère) - un seul des deux
        # savoirs candidats partage un Cursus avec cet usage réel.
        ingest_exercise(
            _exercise_payload("bac-maths-map-usage", examen="PROBATOIRE"),
            source_dir=Path("ingest/cm/bac-maths-map-usage"),
        )

        call_command("map_tags_to_savoir_officiel", stdout=StringIO())

        tag = Tag.objects.get(name="pgcd")
        self.assertEqual(tag.savoir_officiel_id, s_1ere.pk)

    def test_savoirs_of_another_subject_are_never_candidates(self):
        # Régression du 2026-08-16 : les Savoir candidats étaient pris dans TOUT le
        # référentiel alors que les tags étaient filtrés par matière. Un homonyme dans une
        # autre matière rendait donc le tag « ambigu » et bloquait son rattachement - à
        # l'échelle réelle, la règle « fonctions » remontait 75 candidats (dont 28 savoirs
        # de Français) et bloquait à elle seule 163 tags de maths.
        savoir_maths = self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        physique = Subject.objects.get(country__code="CM", code="PHYSIQUE")
        homonyme = Module.objects.create(
            subject=physique, classe="Tle", serie_label="C", numero="90", titre="ARITHMETIQUE",
        )
        Savoir.objects.create(module=homonyme, numero="I", intitule="ARITHMETIQUE")
        tag = self._tag_a_real_question()

        call_command("map_tags_to_savoir_officiel", stdout=StringIO())

        tag.refresh_from_db()
        self.assertEqual(tag.savoir_officiel_id, savoir_maths.pk)

    def test_subject_without_rules_is_refused_without_writing(self):
        # Ne jamais retomber sur le jeu de règles d'une autre matière : lancée sur
        # PHYSIQUE, la commande rattachait 7 tags via des règles de maths (« intégrales »,
        # « fonctions »), donc 7 liens faux et définitifs.
        self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        tag = self._tag_a_real_question()

        err = StringIO()
        call_command("map_tags_to_savoir_officiel", subject="ANGLAIS", stdout=StringIO(), stderr=err)

        self.assertIn("Aucun jeu de règles", err.getvalue())
        tag.refresh_from_db()
        self.assertIsNone(tag.savoir_officiel_id)

    def _tag_used_in_two_cursus(self):
        savoir = self._make_savoir("Tle", "C-E", "90", "I", "ARITHMETIQUE")
        savoir.module.cursus.set(Cursus.objects.filter(country__code="CM"))
        for source, examen in (("bac-maths-multi", "BAC"), ("proba-maths-multi", "PROBATOIRE")):
            ingest_exercise(
                _exercise_payload(source, examen=examen),
                source_dir=Path(f"ingest/cm/{source}"),
            )
        return Tag.objects.get(name="pgcd"), savoir

    def test_tag_used_across_several_cursus_is_skipped_by_default(self):
        # `Tag.savoir_officiel` est une FK unique : pour un tag qui vit dans deux
        # programmes à la fois, tout lien retenu est faux pour l'un des deux usages. Et
        # comme rien ne l'écrase ensuite, l'erreur serait définitive - alors même que les
        # outils de pilotage font confiance à ce champ dès qu'il est renseigné.
        tag, _ = self._tag_used_in_two_cursus()

        out = StringIO()
        call_command("map_tags_to_savoir_officiel", stdout=out)

        tag.refresh_from_db()
        self.assertIsNone(tag.savoir_officiel_id)
        self.assertIn("à usage transverse", out.getvalue())

    def test_allow_multi_cursus_is_an_explicit_opt_in(self):
        tag, savoir = self._tag_used_in_two_cursus()

        call_command("map_tags_to_savoir_officiel", allow_multi_cursus=True, stdout=StringIO())

        tag.refresh_from_db()
        self.assertEqual(tag.savoir_officiel_id, savoir.pk)

    def test_physique_rules_apply_to_physique_tags(self):
        physique = Subject.objects.get(country__code="CM", code="PHYSIQUE")
        module = Module.objects.create(
            subject=physique, classe="Tle", serie_label="C", numero="2",
            titre="MOUVEMENTS ET INTERACTIONS : EVOLUTIONS TEMPORELLES DES SYSTEMES MÉCANIQUES",
        )
        savoir = Savoir.objects.create(
            module=module, numero="I", intitule="Analyse des interactions entre objets dues à leur masse",
        )
        ingest_exercise(
            {**_exercise_payload("bac-physique-map", theme="Lois de Kepler"), "matiere": "Physique"},
            source_dir=Path("ingest/cm/bac-physique-map"),
        )

        call_command("map_tags_to_savoir_officiel", subject="PHYSIQUE", stdout=StringIO())

        self.assertEqual(Tag.objects.get(name="Lois de Kepler").savoir_officiel_id, savoir.pk)


class AuditCoherenceTagsSavoirCommandTests(TestCase):
    """`manage.py audit_coherence_tags_savoir` - voir programme.management.commands.
    audit_coherence_tags_savoir. Réutilise catalog.ingestion._tag_en_conflit_avec_un_
    autre_savoir (même détection que les gardes de _link_tags_to_savoir), rejouée sur
    des tags déjà rattachés plutôt qu'au moment de l'ingestion - le but est de retrouver
    après coup un rattachement posé avant l'existence des gardes (ou à la main dans
    TagAdmin), comme "racine évidente" -> TRIGONOMETRIE le 2026-09-07."""

    def setUp(self):
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C-E", numero="90", titre="Module test")
        self.savoir_a = Savoir.objects.create(module=module, numero="I", intitule="Savoir A")
        self.savoir_b = Savoir.objects.create(module=module, numero="II", intitule="Savoir B")
        self.savoir_b_ref = {"classe": "Tle", "serie_label": "C-E", "module_numero": "90", "savoir_numero": "II"}

    def test_flags_a_tag_conflicting_with_a_question_pointing_elsewhere(self):
        # Simule un rattachement déjà posé avant l'existence des gardes (ou via
        # TagAdmin, formulaire libre sans garde) - la commande doit le retrouver.
        Tag.objects.create(name="conflit", savoir_officiel=self.savoir_a)

        payload = _exercise_payload("bac-maths-audit-1", theme="conflit")
        payload["questions"][0]["savoir_officiel"] = self.savoir_b_ref
        ingest_exercise(payload, source_dir=Path("ingest/cm/bac-maths-audit-1"))

        out = StringIO()
        call_command("audit_coherence_tags_savoir", subject="MATHS", stdout=out)

        self.assertIn("'conflit'", out.getvalue())
        self.assertIn("1/1 tag(s)", out.getvalue())

    def test_does_not_flag_a_tag_without_any_conflicting_usage(self):
        Tag.objects.create(name="tranquille", savoir_officiel=self.savoir_a)

        out = StringIO()
        call_command("audit_coherence_tags_savoir", subject="MATHS", stdout=out)

        self.assertNotIn("tranquille", out.getvalue())
        self.assertIn("aucun conflit", out.getvalue())


class AuditCouvertureProgrammeCommandTests(TestCase):
    """`manage.py audit_couverture_programme` - voir
    programme.management.commands.audit_couverture_programme. Les quatre sections
    (périmètre, contenu, ingestion bloquée, références manquantes) sont testées
    indépendamment - chacune doit fonctionner (et ne rien écrire) même quand les autres
    sont hors sujet."""

    def setUp(self):
        self.cm = Country.objects.get(code="CM")
        self.maths = Subject.objects.get(country=self.cm, code="MATHS")
        self.cursus_bac_c = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="C")
        self.cursus_bac_d = Cursus.objects.get(country=self.cm, examen=Examen.BAC, series__code="D")
        # BASE_DIR neutralisé par défaut : la section (4) lit le dossier ingest/<pays>
        # réel du dépôt (plusieurs milliers de fichiers) si on la laisse pointer dessus -
        # les tests des sections 1/2/3 deviendraient à la fois lents et dépendants du
        # contenu du dépôt à un instant donné. Chaque test de la section (4) peuple ce
        # dossier temporaire avec exactement les fichiers dont il a besoin.
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)

    def _run(self, **kwargs):
        out = StringIO()
        with override_settings(BASE_DIR=self.base_dir):
            call_command("audit_couverture_programme", stdout=out, skip_ingestion_check=True, **kwargs)
        return out.getvalue()

    def _write_ingest(self, folder, filename, payload):
        """Dépose un fichier JSON dans le dossier ingest temporaire vu par la section (4)."""
        target = self.base_dir / "ingest" / "cm" / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / filename).write_text(json.dumps(payload), encoding="utf-8")

    def _maths_module_with_savoir(self):
        """Un module MATHS suffit à rendre la matière "couverte par le référentiel" -
        condition d'entrée des sections 1, 2 et 4."""
        module = Module.objects.create(
            subject=self.maths, classe="Tle", serie_label="C", numero="1", titre="Module audit",
        )
        module.cursus.set([self.cursus_bac_c])
        Savoir.objects.create(module=module, numero="I", intitule="Notion audit")
        return module

    def _tag_a_real_question(self, epreuve_source, theme, **payload_overrides):
        ingest_exercise(
            _exercise_payload(epreuve_source, theme=theme, **payload_overrides),
            source_dir=Path(f"ingest/cm/{epreuve_source}"),
        )
        return Tag.objects.get(name=theme)

    # --- Section 1 : périmètre ---

    def test_scope_gap_confirmed_when_content_exists_without_module(self):
        # Un module MATHS doit déjà exister ailleurs, sinon la matière est hors
        # référentiel et la section est sautée entièrement (voir test dédié plus bas).
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C", numero="1", titre="Autre module")
        module.cursus.set([self.cursus_bac_c])
        # Du contenu réel existe pour BAC D, mais aucun module officiel ne le couvre.
        ingest_exercise(
            _exercise_payload("bac-d-maths-audit", examen="BAC", serie="D"),
            source_dir=Path("ingest/cm/bac-d-maths-audit"),
        )

        output = self._run(subject="MATHS")

        self.assertIn("[CONFIRMÉ]", output)
        self.assertIn(str(self.cursus_bac_d), output)

    def test_scope_gap_to_verify_when_no_content_and_no_module(self):
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C", numero="1", titre="Autre module")
        module.cursus.set([self.cursus_bac_c])

        output = self._run(subject="MATHS")

        self.assertIn("[à vérifier]", output)
        self.assertIn(str(self.cursus_bac_d), output)
        self.assertNotIn("[CONFIRMÉ]", output)

    def test_no_scope_gap_when_every_real_cursus_is_covered(self):
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="", numero="1", titre="Couverture totale")
        module.cursus.set(Cursus.objects.filter(country=self.cm))

        output = self._run(subject="MATHS")

        self.assertIn("Aucun trou de périmètre détecté.", output)

    def test_subject_absent_from_referential_skips_sections_one_and_two_only(self):
        output = self._run(subject="ANGLAIS")

        self.assertIn("Aucune matière du référentiel programme officiel", output)
        self.assertNotIn("[CONFIRMÉ]", output)
        self.assertNotIn("[à vérifier]", output)

    # --- Section 2 : contenu ---

    def test_content_gap_reports_missing_catalog_and_quiz(self):
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C", numero="2", titre="Module savoir")
        module.cursus.set([self.cursus_bac_c])
        Savoir.objects.create(module=module, numero="I", intitule="Notion vide")

        output = self._run(subject="MATHS")

        self.assertIn("Notion vide", output)
        self.assertIn("aucune Question d'épreuve", output)
        self.assertIn("aucun CompetenceItem de quiz", output)

    def test_content_gap_cleared_once_both_catalog_and_quiz_exist(self):
        module = Module.objects.create(subject=self.maths, classe="Tle", serie_label="C", numero="2", titre="Module savoir")
        module.cursus.set([self.cursus_bac_c])
        savoir = Savoir.objects.create(module=module, numero="I", intitule="Notion couverte")

        tag = self._tag_a_real_question("bac-c-maths-audit-covered", "notion couverte tag", examen="BAC", serie="C")
        tag.savoir_officiel = savoir
        tag.save(update_fields=["savoir_officiel"])
        item = CompetenceItem.objects.create(
            theme=tag, subject=self.maths, enonce_markdown="Énoncé.", corrige_markdown="Corrigé.",
            difficulte_estimee=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, statut=StatutContenu.VALIDE,
        )
        item.cursus.add(self.cursus_bac_c)

        output = self._run(subject="MATHS")

        self.assertNotIn("Notion couverte", output)
        self.assertIn("Aucun trou de contenu détecté.", output)

    def test_content_gap_cleared_by_a_question_linked_directly(self):
        # Sans passer par le moindre Tag rattaché : c'est tout l'intérêt du rattachement
        # direct, la question porte elle-même sa référence (voir Question.savoir_officiel).
        module = self._maths_module_with_savoir()
        savoir = module.savoirs.get(numero="I")
        ingest_exercise(
            {
                **_exercise_payload("bac-c-maths-lien-direct", theme="theme non rattache"),
                "questions": [{
                    "numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.",
                    "themes": ["theme non rattache"],
                    "savoir_officiel": {
                        "classe": "Tle", "serie_label": "C", "module_numero": "1", "savoir_numero": "I",
                    },
                }],
            },
            source_dir=Path("ingest/cm/bac-c-maths-lien-direct"),
        )
        item = CompetenceItem.objects.create(
            theme=Tag.objects.get(name="theme non rattache"), subject=self.maths,
            enonce_markdown="Énoncé.", corrige_markdown="Corrigé.",
            difficulte_estimee=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE,
            statut=StatutContenu.VALIDE,
        )
        item.cursus.add(self.cursus_bac_c)

        output = self._run(subject="MATHS")

        self.assertNotIn(savoir.intitule, output)
        self.assertIn("Aucun trou de contenu détecté.", output)

    # --- Section 3 : ingestion bloquée ---

    def test_blocked_ingestion_lists_broken_cours_without_writing_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ingest_dir = tmp_path / "ingest" / "cm"
            ingest_dir.mkdir(parents=True)
            broken_cours = {
                "cours_id": "cours-audit-broken",
                "meta": {"titre": "Cours cassé (audit)", "matiere": "Mathématiques"},
                "source": {"rappel_id": "rappel-inexistant-audit"},
                "sections": [],
            }
            (ingest_dir / "cours.json").write_text(json.dumps(broken_cours), encoding="utf-8")

            out = StringIO()
            with override_settings(BASE_DIR=tmp_path):
                call_command("audit_couverture_programme", stdout=out)
            output = out.getvalue()

        self.assertIn("1 fichier(s) bloqué(s)", output)
        self.assertIn("RappelDeMethode introuvable", output)
        self.assertFalse(Cours.objects.filter(external_id="cours-audit-broken").exists())

    def test_ingestion_check_skipped_on_demand(self):
        output = self._run(subject="ANGLAIS")  # skip_ingestion_check=True baked into _run
        self.assertNotIn("Ingestion bloquée", output)

    def test_missing_ingest_folder_reports_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = StringIO()
            with override_settings(BASE_DIR=Path(tmp)):
                call_command("audit_couverture_programme", stdout=out)
            output = out.getvalue()

        self.assertIn("Dossier introuvable, section sautée", output)

    # --- Section 4 : références programme manquantes ---
    #
    # Contrepartie amont de la section 2 : celle-ci dit qu'un savoir n'a pas de contenu,
    # celle-là montre que du contenu existe mais arrive sans `savoir_officiel`. La
    # distinction "champ présent mais null" / "champ absent" est le cœur du signal : la
    # première population est un défaut de génération actif, la seconde une dette
    # antérieure au champ. Les confondre ferait passer un bug courant pour de l'histoire.

    def test_missing_ref_reported_when_field_is_present_but_null(self):
        self._maths_module_with_savoir()
        payload = _exercise_payload("bac-c-maths-sans-ref")
        payload["questions"][0]["savoir_officiel"] = None
        payload["questions"].append({
            "numero": "2", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.",
            "themes": ["autre"], "savoir_officiel": None,
        })
        self._write_ingest("bac-c-maths-sans-ref", "exercice_1.json", payload)

        output = self._run(subject="MATHS")

        self.assertIn("Champ présent mais laissé null", output)
        self.assertIn("bac-c-maths-sans-ref : 2/2 question(s) sans référence", output)
        self.assertNotIn("Champ absent", output)

    def test_missing_ref_classified_as_legacy_when_the_key_is_absent(self):
        self._maths_module_with_savoir()
        self._write_ingest("bac-c-maths-ancien", "exercice_1.json", _exercise_payload("bac-c-maths-ancien"))

        output = self._run(subject="MATHS")

        self.assertIn("Champ absent", output)
        self.assertIn("[MATHS] 1 question(s) sur 1 épreuve(s)", output)
        self.assertNotIn("Champ présent mais laissé null", output)

    def test_question_carrying_a_reference_is_not_reported(self):
        self._maths_module_with_savoir()
        payload = _exercise_payload("bac-c-maths-avec-ref")
        payload["questions"][0]["savoir_officiel"] = {
            "classe": "Tle", "serie_label": "C", "module_numero": "1", "savoir_numero": "I",
        }
        self._write_ingest("bac-c-maths-avec-ref", "exercice_1.json", payload)

        output = self._run(subject="MATHS")

        self.assertIn("Toutes les questions des matières du référentiel portent une référence", output)

    def test_subject_without_referential_is_never_reported_as_a_gap(self):
        # Le cas "null légitime" : sans référentiel pour cette matière (EPS, Espagnol...),
        # il n'existe aucun savoir auquel rattacher la question - la signaler serait un
        # faux positif permanent. Pas de --subject ici : c'est bien l'absence de module
        # pour ANGLAIS qui doit l'écarter, pas le filtre de la commande.
        self._maths_module_with_savoir()
        payload = {**_exercise_payload("bepc-anglais-hors-perimetre"), "matiere": "Anglais"}
        self._write_ingest("bepc-anglais-hors-perimetre", "exercice_1.json", payload)

        output = self._run()

        self.assertNotIn("bepc-anglais-hors-perimetre", output)

    def test_cours_files_are_not_counted(self):
        # Un cours porte bien un `meta.savoir_officiel`, mais il ne pèse sur aucun des
        # trois outils de pilotage (qui comptent des Question et des CompetenceItem) -
        # l'inclure diluerait le signal sans rien rendre actionnable.
        self._maths_module_with_savoir()
        self._write_ingest("bac-c-maths-cours", "cours.json", {
            "cours_id": "cours-audit-section-4",
            "meta": {"titre": "Cours audit", "matiere": "Mathématiques", "savoir_officiel": None},
            "source": {"rappel_id": "peu-importe"},
            "sections": [],
        })

        output = self._run(subject="MATHS")

        self.assertNotIn("bac-c-maths-cours", output)
