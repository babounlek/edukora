"""inedit.controle et la commande controler_epreuve_inedite : le contrôle indépendant d'une épreuve
générée, avant ingestion."""
import copy
import io
import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from catalog.models import Tag

from .controle import controler_epreuve

BLUEPRINT = {
    "type": "blueprint", "external_id": "bp-x", "titre": "Épreuve de test", "matiere": "mathematiques",
    "cursus": [{"examen": "bepc"}], "competences": ["Notion T"],
    "sections_plan": [{
        "exercice": "1", "titre": "Ex", "points": 2, "difficulte": "faible", "nombre_questions": 1,
        "competences": ["Notion T"], "notes": "",
    }],
}
EPREUVE = {
    "type": "epreuve", "external_id": "ep-x", "titre": "Épreuve de test", "blueprint_external_id": "bp-x",
    "exercices": [{
        "numero_exercice": "1", "points": "2", "enonce_intro_markdown": "",
        "questions": [{
            "numero": "1", "ordre": 1, "enonce_markdown": "Calcule $2+2$. *(2 pts)*",
            "corrige_markdown": "### Rappel de méthode\nOn additionne terme à terme.\n\nRéponse : $4$.",
            "difficulte_estimee": "faible", "type_reponse": "ouverte", "points": 2,
            "criteres_notation": [{"libelle": "Additionne", "points": 1}, {"libelle": "Conclut", "points": 1}],
            "themes": ["Notion T"],
            "rappels_de_methode": [{
                "id": "rdi-ep-x-ex1-q1-0", "competence": "Additionner", "contenu_markdown": "On additionne terme à terme.",
            }],
        }],
    }],
}
COURS_COMPLET = {
    "type": "cours", "cours_id": "cours-additionner-x",
    "meta": {"titre": "Additionner deux nombres (test)", "matiere": "mathematiques", "pays": "cm", "serie": None},
    "source": {"rappel_id": "rdi-ep-x-ex1-q1-0"},
    "sections": [{"type": t} for t in [
        "accroche", "prerequis", "regle", "exemple_resolu", "erreurs_classiques", "exercices_application", "synthese",
    ]],
}
COURS_COMPLET["sections"][2]["formule_principale"] = "a+b"


class ControleEpreuveTests(TestCase):
    def setUp(self):
        Tag.objects.create(name="Notion T")
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dossier = Path(self._tmp.name)
        self.ep = copy.deepcopy(EPREUVE)
        self.cours = copy.deepcopy(COURS_COMPLET)

    def _ecrire(self, cours=True, nom_cours="ep-x_cours_additionner.json"):
        (self.dossier / "bp-x.json").write_text(json.dumps(BLUEPRINT), encoding="utf-8")
        (self.dossier / "ep-x.json").write_text(json.dumps(self.ep), encoding="utf-8")
        if cours:
            (self.dossier / nom_cours).write_text(json.dumps(self.cours), encoding="utf-8")
        return str(self.dossier / "ep-x.json")

    def _erreurs(self, **kwargs):
        return controler_epreuve(self._ecrire(**kwargs)).erreurs

    def test_une_epreuve_conforme_passe(self):
        resultat = controler_epreuve(self._ecrire())
        self.assertEqual(resultat.erreurs, [])
        self.assertEqual((resultat.questions, resultat.cours_complets, resultat.squelettes, resultat.rappels), (1, 1, 0, 1))

    def test_le_numero_repete_en_tete_est_signale(self):
        self.ep["exercices"][0]["questions"][0]["enonce_markdown"] = "**1.** Calcule $2+2$. *(2 pts)*"
        self.assertTrue(any("numéro est répété" in e for e in self._erreurs()))

    def test_une_somme_de_criteres_fausse_est_signalee(self):
        self.ep["exercices"][0]["questions"][0]["criteres_notation"][1]["points"] = 0.5
        self.assertTrue(any("somme critères" in e for e in self._erreurs()))

    def test_un_bareme_annonce_different_des_points_est_signale(self):
        self.ep["exercices"][0]["questions"][0]["enonce_markdown"] = "Calcule $2+2$. *(1 pt)*"
        self.assertTrue(any("barème annoncé" in e for e in self._erreurs()))

    def test_un_tag_inexistant_est_signale(self):
        self.ep["exercices"][0]["questions"][0]["themes"] = ["Notion inconnue"]
        self.assertTrue(any("Tag inexistant" in e for e in self._erreurs()))

    def test_un_rappel_non_verbatim_est_signale(self):
        self.ep["exercices"][0]["questions"][0]["rappels_de_methode"][0]["contenu_markdown"] = "Autre texte."
        self.assertTrue(any("non verbatim" in e for e in self._erreurs()))

    def test_un_tiret_cadratin_est_signale(self):
        self.ep["exercices"][0]["questions"][0]["corrige_markdown"] += " Résultat — 4."
        self.assertTrue(any("interdit" in e for e in self._erreurs()))

    def test_un_rappel_sans_fichier_de_cours_est_signale(self):
        self.assertTrue(any("rappels sans fichier de cours" in e for e in self._erreurs(cours=False)))

    def test_un_squelette_vers_un_cours_inexistant_est_signale(self):
        self.cours["sections"] = []
        erreurs = self._erreurs()
        self.assertTrue(any("squelette sans Cours existant" in e for e in erreurs), erreurs)

    def test_deux_fichiers_de_cours_pour_un_meme_rappel_sont_signales(self):
        chemin = self._ecrire()
        (self.dossier / "ep-x_cours_doublon.json").write_text(json.dumps(self.cours), encoding="utf-8")
        erreurs = controler_epreuve(chemin).erreurs
        self.assertTrue(any("plusieurs fichiers de cours" in e for e in erreurs), erreurs)

    def test_une_formule_principale_avec_dollar_est_signalee(self):
        self.cours["sections"][2]["formule_principale"] = "$a+b$"
        self.assertTrue(any("formule_principale" in e for e in self._erreurs()))

    def test_la_commande_echoue_sur_une_erreur_et_reussit_sinon(self):
        sortie = io.StringIO()
        call_command("controler_epreuve_inedite", self._ecrire(), stdout=sortie)
        self.assertIn("CHECK_OK", sortie.getvalue())

        self.ep["exercices"][0]["questions"][0]["themes"] = ["Notion inconnue"]
        with self.assertRaises(CommandError):
            call_command("controler_epreuve_inedite", self._ecrire(), stdout=io.StringIO())
