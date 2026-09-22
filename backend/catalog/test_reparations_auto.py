"""Réparations automatiques à l'ingestion : `$` littéraux et proposition de thèmes."""

import json
import tempfile
from pathlib import Path

from django.test import TestCase

from .ingestion import run_ingestion
from .models import Question, Subject, Tag
from .reparations_auto import _echapper_dollars, _repair_literal_dollars, proposer_themes, vider_journal
from .tunnel import _VARIANT_INDEX


class EchapperDollarsTests(TestCase):
    def test_variable_php_en_fin_d_instruction_est_echappee(self):
        texte, n = _echapper_dollars("Écrire $nom = valeur; puis $age = 3; dans le script.")
        self.assertEqual(n, 2)
        self.assertEqual(texte, r"Écrire \$nom = valeur; puis \$age = 3; dans le script.")

    def test_superglobale_et_acces_tableau_php(self):
        texte, n = _echapper_dollars("Lire $_POST et $row['nom'] ici.")
        self.assertEqual(n, 2)
        self.assertIn(r"\$_POST", texte)
        self.assertIn(r"\$row['nom']", texte)

    def test_reference_de_tableur_en_contexte_de_formule(self):
        texte, n = _echapper_dollars("Taper =RANG(B2;$B$2:$B$5;0) puis valider.")
        self.assertEqual(n, 2)
        self.assertEqual(texte, r"Taper =RANG(B2;\$B$2:\$B$5;0) puis valider.")

    def test_evenements_numerotes_ne_sont_pas_des_references_de_tableur(self):
        source = "1. $A$1. $A$ : « aucune boule » et 2. $B$2. $B$ : « une boule »."
        self.assertEqual(_echapper_dollars(source), (source, 0))

    def test_formules_mathematiques_intactes(self):
        for source in (
            r"Soit $x \in [a;b]$ et $f(x)=2x$.",
            "On pose $a=1$; puis $b=2$.",
            r"L'ensemble $\{1;2\}$ et $$\int_0^1 x\,dx$$.",
        ):
            self.assertEqual(_echapper_dollars(source), (source, 0), source)

    def test_code_protege_et_idempotence(self):
        source = "```php\n$nom = 1;\n```\net `$x = 2;` puis \\$deja = 3;"
        self.assertEqual(_echapper_dollars(source), (source, 0))
        texte, _ = _echapper_dollars("Voir $nom = valeur;")
        self.assertEqual(_echapper_dollars(texte)[1], 0)

    def test_dollar_orphelin_devant_un_identifiant_long(self):
        source = 'Utilise pour le message ("Il y a $nbart articles...") de la page.'
        texte, n = _echapper_dollars(source)
        self.assertEqual(n, 1)
        self.assertIn(r"\$nbart", texte)

    def test_orphelin_ignore_si_formules_equilibrees_ou_ambigu(self):
        for source in (
            "Soit $ABC$ un triangle et $x$ un reel.",
            "Deux stray $abc et $def sans fermeture.",
            "Un seul $ ici sans identifiant.",
        ):
            self.assertEqual(_echapper_dollars(source), (source, 0), source)

    def test_champs_non_markdown_jamais_touches(self):
        vider_journal()
        data = {
            "titre": "Formulaire PHP : $_GET et $_POST",
            "tags": ["$_POST", "$_GET"],
            "themes": ["$_POST"],
            "sections": [{"items_markdown": ["Utiliser $_GET et $_POST"], "nom": "$_POST"}],
        }
        reparee, change = _repair_literal_dollars(data, "cours x")
        self.assertTrue(change)
        self.assertEqual(reparee["titre"], data["titre"])
        self.assertEqual(reparee["tags"], ["$_POST", "$_GET"])
        self.assertEqual(reparee["themes"], ["$_POST"])
        self.assertEqual(reparee["sections"][0]["nom"], "$_POST")
        self.assertEqual(reparee["sections"][0]["items_markdown"], [r"Utiliser \$_GET et \$_POST"])

    def test_repair_journalise_et_epargne_formule_principale(self):
        vider_journal()
        data = {"corrige_markdown": "Écrire $nom = valeur;", "formule_principale": "$nom = valeur;"}  # formule_principale : pas un champ _markdown
        reparee, change = _repair_literal_dollars(data, "epreuve#1")
        self.assertTrue(change)
        self.assertEqual(reparee["formule_principale"], "$nom = valeur;")
        self.assertEqual(reparee["corrige_markdown"], r"Écrire \$nom = valeur;")
        from .reparations_auto import JOURNAL
        self.assertTrue(any("epreuve#1" in ligne and "RÉPARÉ" in ligne for ligne in JOURNAL))


class ProposerThemesTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.filter(country__code="CM", code="MATHS").first()

    def test_themes_des_questions_soeurs(self):
        q_sans = {"numero": "3", "enonce_markdown": "x", "corrige_markdown": "y"}
        questions = [
            {"numero": "1", "themes": ["Dérivation"]},
            {"numero": "2", "themes": ["Dérivation", "Limites"]},
            q_sans,
        ]
        themes, origine = proposer_themes(q_sans, questions, {}, self.subject)
        self.assertEqual(themes[0], "Dérivation")
        self.assertIn("autres questions", origine)

    def test_rien_a_proposer_renvoie_liste_vide(self):
        q = {"numero": "1", "enonce_markdown": "zzzz qqqq", "corrige_markdown": "wwww"}
        self.assertEqual(proposer_themes(q, [q], {}, self.subject), ([], None))

    def test_mots_cles_reconnus_comme_tag_existant(self):
        Tag.objects.create(name="Suites géométriques")
        _VARIANT_INDEX["built_at"] = None
        q = {"numero": "1", "enonce_markdown": "aaa", "corrige_markdown": "bbb"}
        themes, origine = proposer_themes(q, [q], {"mots_cles_recherche": ["suites geometriques"]}, self.subject)
        self.assertEqual(themes, ["Suites géométriques"])
        self.assertIn("mots-clés", origine)


class IngestionAvecReparationsTests(TestCase):
    def _ecrire(self, tmp, questions, **extra):
        source_dir = Path(tmp) / "ingest" / "cm" / "bac-maths-2024"
        source_dir.mkdir(parents=True)
        fichier = source_dir / "bac-maths-2024_exercice_1.json"
        payload = {
            "epreuve_source": "bac-maths-2024.pdf", "numero_exercice": "1", "matiere": "Mathematiques",
            "serie": "C", "examen": "BAC", "questions": questions, **extra,
        }
        fichier.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return fichier

    def test_theme_propose_par_les_soeurs_puis_ecrit_dans_la_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = self._ecrire(tmp, [
                {"numero": "1", "enonce_markdown": "a", "corrige_markdown": "b", "themes": ["Dérivation"]},
                {"numero": "2", "enonce_markdown": "c", "corrige_markdown": "d"},
            ])
            report = run_ingestion(Path(tmp) / "ingest")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["created"], 1)
            self.assertTrue(any("À REVOIR" in ligne for ligne in report["reparations"]))
            self.assertEqual(
                sorted(Question.objects.get(numero="2").themes.values_list("name", flat=True)), ["Dérivation"],
            )
            reecrit = json.loads(fichier.read_text(encoding="utf-8"))
            self.assertEqual(reecrit["questions"][1]["themes"], ["Dérivation"])

    def test_sans_aucune_proposition_l_exercice_est_rejete(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._ecrire(tmp, [{"numero": "1", "enonce_markdown": "zzzz", "corrige_markdown": "qqqq"}])
            report = run_ingestion(Path(tmp) / "ingest")
        self.assertEqual(report["created"], 0)
        self.assertTrue(any("aucun thème" in e for e in report["errors"]))

    def test_dollars_litteraux_repares_a_l_ingestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._ecrire(tmp, [
                {"numero": "1", "enonce_markdown": "Écrire $nom = valeur;", "corrige_markdown": "ok", "themes": ["PHP"]},
            ])
            report = run_ingestion(Path(tmp) / "ingest")
        self.assertEqual(report["errors"], [])
        self.assertEqual(Question.objects.get().enonce_markdown, r"Écrire \$nom = valeur;")
        self.assertTrue(any("RÉPARÉ" in ligne for ligne in report["reparations"]))
