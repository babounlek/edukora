"""appliquer_savoirs_json : le seul champ savoir_officiel, jamais d'écrasement, simulation par défaut."""
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from programme.models import Module, Savoir

from .ingestion import ingest_exercise
from .models import Subject, Tag

REF = {"classe": "3e", "serie_label": "", "module_numero": "13", "savoir_numero": "II"}


def _payload(savoir=None, theme="fractions"):
    q = {"numero": "1", "enonce_markdown": "Énoncé.", "corrige_markdown": "Corrigé.", "themes": [theme]}
    if savoir:
        q["savoir_officiel"] = savoir
    return {
        "epreuve_source": "bepc-test-2026", "numero_exercice": "1", "matiere": "Mathématiques", "serie": "",
        "examen": "BEPC", "annee": 2026, "questions": [q],
    }


class AppliquerSavoirsJsonTests(TestCase):
    def setUp(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        module = Module.objects.create(subject=subject, classe="3e", serie_label="", numero="13", titre="Calcul")
        self.savoir = Savoir.objects.create(module=module, numero="II", intitule="Fractions et radicaux")
        self.autre = Savoir.objects.create(module=module, numero="III", intitule="Identités")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dossier = Path(self.tmp.name) / "ingest" / "cm" / "bepc-test-2026"
        self.dossier.mkdir(parents=True)
        # L'exercice est déjà en base SANS savoir (c'est l'état de la production avant la campagne).
        self.exercice, _ = ingest_exercise(_payload(), source_dir=self.dossier)
        self.question = self.exercice.questions.get()

    def _lancer(self, *options, savoir=REF, theme="fractions"):
        (self.dossier / "bepc-test-2026_exercice_1.json").write_text(
            json.dumps(_payload(savoir, theme), ensure_ascii=False), encoding="utf-8")
        sortie = StringIO()
        call_command("appliquer_savoirs_json", str(self.dossier), *options, stdout=sortie)
        self.question.refresh_from_db()
        return sortie.getvalue()

    def test_simulation_par_defaut_n_ecrit_rien(self):
        sortie = self._lancer()

        self.assertIn("SIMULATION", sortie)
        self.assertIsNone(self.question.savoir_officiel_id)

    def test_ecrire_remplit_le_savoir_vide(self):
        self._lancer("--ecrire")

        self.assertEqual(self.question.savoir_officiel_id, self.savoir.pk)

    def test_un_savoir_deja_pose_n_est_jamais_ecrase(self):
        self.question.savoir_officiel = self.autre
        self.question.save()

        sortie = self._lancer("--ecrire")

        self.assertEqual(self.question.savoir_officiel_id, self.autre.pk)
        self.assertIn("conserve_different", sortie)

    def test_ne_touche_a_aucun_autre_champ_ni_aux_themes(self):
        avant = (self.question.enonce_markdown, self.question.corrige_markdown, self.question.points)
        themes_avant = set(self.question.themes.values_list("name", flat=True))

        # Le JSON porte d'AUTRES thèmes : ils ne doivent jamais arriver en base.
        self._lancer("--ecrire", theme="un thème que la base ne connaît pas")

        self.assertEqual((self.question.enonce_markdown, self.question.corrige_markdown, self.question.points), avant)
        self.assertEqual(set(self.question.themes.values_list("name", flat=True)), themes_avant)
        self.assertFalse(Tag.objects.filter(name="un thème que la base ne connaît pas").exists())

    def test_reference_invalide_signalee_et_ignoree(self):
        sortie = self._lancer("--ecrire", savoir={**REF, "module_numero": "99"})

        self.assertIsNone(self.question.savoir_officiel_id)
        self.assertIn("reference_invalide", sortie)

    def test_exercice_absent_de_la_base_n_est_pas_cree(self):
        (self.dossier / "autre_exercice_9.json").write_text(
            json.dumps({**_payload(REF), "numero_exercice": "9"}, ensure_ascii=False), encoding="utf-8")
        avant = self.exercice.lesson.exercises.count()

        call_command("appliquer_savoirs_json", str(self.dossier / "autre_exercice_9.json"), "--ecrire", stdout=StringIO())

        self.assertEqual(self.exercice.lesson.exercises.count(), avant)

    def test_lier_themes_utilise_les_themes_de_la_base_pas_ceux_du_json(self):
        self._lancer("--ecrire", "--lier-themes", theme="thème du json seulement")

        tag_base = Tag.objects.get(name="fractions")
        self.assertEqual(tag_base.savoir_officiel_id, self.savoir.pk)
        self.assertFalse(Tag.objects.filter(name="thème du json seulement").exists())


class ExportCompactTests(AppliquerSavoirsJsonTests):
    """Le serveur n'a pas les JSON : on exporte un fichier compact, puis on l'applique seul."""

    def test_l_export_ne_contient_que_des_identifiants_et_des_savoirs(self):
        (self.dossier / "bepc-test-2026_exercice_1.json").write_text(json.dumps(_payload(REF), ensure_ascii=False), encoding="utf-8")
        sortie = Path(self.tmp.name) / "export.json"

        call_command("appliquer_savoirs_json", str(self.dossier), "--exporter-vers", str(sortie), stdout=StringIO())

        export = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(len(export), 1)
        self.assertEqual(export[0]["pays"], "cm")
        self.assertEqual(export[0]["questions"], [{"numero": "1", "savoir_officiel": REF}])
        self.assertNotIn("Énoncé.", sortie.read_text(encoding="utf-8"))
        self.question.refresh_from_db()
        self.assertIsNone(self.question.savoir_officiel_id)

    def test_appliquer_depuis_le_fichier_d_export_seul(self):
        (self.dossier / "bepc-test-2026_exercice_1.json").write_text(json.dumps(_payload(REF), ensure_ascii=False), encoding="utf-8")
        export = Path(self.tmp.name) / "export.json"
        call_command("appliquer_savoirs_json", str(self.dossier), "--exporter-vers", str(export), stdout=StringIO())
        (self.dossier / "bepc-test-2026_exercice_1.json").unlink()

        call_command("appliquer_savoirs_json", str(export), "--ecrire", stdout=StringIO())

        self.question.refresh_from_db()
        self.assertEqual(self.question.savoir_officiel_id, self.savoir.pk)
