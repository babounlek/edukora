"""Retrait d'une épreuve remplacée : leçon entière, exercices jamais journalisés, clé naturelle seule."""
import contextlib
import io
import json

from catalog.models import Cours, Exercise, Lesson, StatutContenu

from . import empreintes as emp
from . import moteur, outil_lot
from .models import ContenuSynchro, StatutLot
from .test_moteur import DOSSIER, EX_ID, QUIZ_REL, Banc, R


class RetraitLeconTests(Banc):
    def retraits_de(self, unite=DOSSIER):
        chemin = self.tmp / "retraits-genere.json"
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            code = outil_lot.main(["retraits", str(self.ingest), unite, "--motif", "remplacée par deux sujets",
                                   "--sortie", str(chemin)])
        self.assertEqual(code, 0, sortie.getvalue())
        return json.loads(chemin.read_text(encoding="utf-8"))

    def test_la_commande_retraits_produit_les_exercices_et_la_lecon(self):
        retraits = self.retraits_de()
        types = sorted(r["type"] for r in retraits)
        self.assertEqual(types, [emp.TYPE_EXERCICE, emp.TYPE_LECON])
        lecon = next(r for r in retraits if r["type"] == emp.TYPE_LECON)
        self.assertEqual(lecon["cle_naturelle"]["epreuve_source"], "bac-test-2024")
        exercice = next(r for r in retraits if r["type"] == emp.TYPE_EXERCICE)
        self.assertEqual(exercice["id_stable"], EX_ID)
        self.assertEqual(exercice["cle_naturelle"]["pays"], "cm")

    def test_retrait_d_un_contenu_jamais_journalise_par_sa_cle_naturelle(self):
        self.appliquer_initial()
        ContenuSynchro.objects.all().delete()  # contenu ingéré à l'ancienne : l'objet existe, pas le journal
        lot = self.lot(unites=(QUIZ_REL,), retraits=self.retraits_de())
        self.appliquer(lot, confirme_retraits=True)
        lot.refresh_from_db()
        self.assertEqual(self.resultats(lot)[(emp.TYPE_EXERCICE, EX_ID)], R.RETIRE)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.REJETE)
        self.assertEqual(Lesson.objects.get().statut, StatutContenu.REJETE)
        self.assertEqual(Cours.objects.get(external_id="cours-test-notion").statut, StatutContenu.VALIDE)  # intact
        self.assertEqual(Exercise.objects.count(), 1)  # jamais de suppression

    def test_le_plan_prevoit_le_retrait_sans_rien_ecrire(self):
        self.appliquer_initial()
        ContenuSynchro.objects.all().delete()
        lot = self.lot(unites=(QUIZ_REL,), retraits=self.retraits_de())
        plan = moteur.planifier(lot)
        self.assertEqual(plan["bloquants"], 0)
        self.assertEqual(Lesson.objects.get().statut, StatutContenu.VALIDE)

    def test_sans_cle_naturelle_un_contenu_non_journalise_n_est_pas_retire(self):
        self.appliquer_initial()
        ContenuSynchro.objects.all().delete()
        sans_cle = [{k: v for k, v in r.items() if k != "cle_naturelle"} for r in self.retraits_de()]
        lot = self.lot(unites=(QUIZ_REL,), retraits=sans_cle)
        self.appliquer(lot, confirme_retraits=True)
        lot.refresh_from_db()
        self.assertEqual(self.resultats(lot)[(emp.TYPE_EXERCICE, EX_ID)], R.ERREUR)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)
        self.assertEqual(Lesson.objects.get().statut, StatutContenu.VALIDE)

    def test_une_epreuve_source_ambigue_n_est_jamais_retiree_au_hasard(self):
        self.appliquer_initial()
        ContenuSynchro.objects.all().delete()
        premiere = Lesson.objects.get()
        Lesson.objects.create(title="Doublon", slug="doublon", subject=premiere.subject, lesson_type=premiere.lesson_type,
                              epreuve_source=premiere.epreuve_source, year=premiere.year)
        lot = self.lot(unites=(QUIZ_REL,), retraits=[r for r in self.retraits_de() if r["type"] == emp.TYPE_LECON])
        self.appliquer(lot, confirme_retraits=True)
        lot.refresh_from_db()
        self.assertEqual(self.resultats(lot)[(emp.TYPE_LECON, f"cm/{premiere.epreuve_source}")], R.ERREUR)
        self.assertFalse(Lesson.objects.filter(statut=StatutContenu.REJETE).exists())

    def test_une_lecon_ne_se_publie_pas_par_lot(self):
        self.appliquer_initial()
        lot = self.lot(unites=(QUIZ_REL,), retraits=self.retraits_de())
        manifeste = moteur._manifeste(lot)
        entree = next(e for e in manifeste["contenus"] if e["type"] == emp.TYPE_LECON)
        entree["operation"] = "create"
        entree["fichier"] = "cm/x.json"
        with self.assertRaises(moteur.ErreurLot):
            moteur._verifier_entrees(manifeste, lot.dossier)
        self.assertNotEqual(lot.statut, StatutLot.ECHOUE)
