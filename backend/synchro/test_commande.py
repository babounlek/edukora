"""La commande `sync_contenu` de bout en bout : sorties JSON et codes de sortie (voir son en-tête)."""
import io
import json

from django.core.management import call_command
from catalog.models import Exercise, Question

from . import moteur
from .models import ContenuSynchro, LotSynchro, StatutLot
from .test_moteur import Banc, DOSSIER, EX_ID


class CommandeTests(Banc):
    def sync(self, *args):
        """Retourne (code de sortie, dernière sortie JSON)."""
        sortie = io.StringIO()
        code = 0
        try:
            call_command("sync_contenu", *args, stdout=sortie, stderr=io.StringIO())
        except SystemExit as exc:
            code = exc.code or 0
        lignes = [l for l in sortie.getvalue().splitlines() if l.strip()]
        return code, (json.loads(lignes[-1]) if lignes else None)

    def archive(self):
        _, res = self.preparer()
        return res

    def test_cycle_complet_recevoir_planifier_appliquer_statut(self):
        res = self.archive()
        code, recu = self.sync("recevoir", res["archive"], "--sha256", res["sha256_archive"])
        self.assertEqual(code, 0, recu)
        batch = recu["batch_id"]
        self.assertEqual(recu["statut"], StatutLot.VERIFIE)
        self.assertEqual(recu["operations"], 3)

        code, plan = self.sync("planifier", batch)
        self.assertEqual(code, 0, plan)
        self.assertEqual(plan["bloquants"], 0)
        self.assertFalse(Exercise.objects.exists())  # la simulation n'a rien écrit

        code, applique = self.sync("appliquer", batch, "--confirme", "--sans-post-traitement")
        self.assertEqual(code, 0, applique)
        self.assertEqual(applique["statut"], StatutLot.REUSSI)
        self.assertEqual(Exercise.objects.count(), 1)

        code, etat = self.sync("statut", batch)
        self.assertEqual(code, 0)
        self.assertEqual(etat["statut"], StatutLot.REUSSI)
        code, detail = self.sync("statut", batch, "--detail")
        self.assertEqual(len(detail["operations"]), 3)

    def test_appliquer_exige_confirme(self):
        res = self.archive()
        _, recu = self.sync("recevoir", res["archive"])
        code, sortie = self.sync("appliquer", recu["batch_id"])
        self.assertEqual(code, 5)
        self.assertFalse(Exercise.objects.exists())
        self.assertEqual(LotSynchro.objects.get().statut, StatutLot.VERIFIE)

    def test_appliquer_deux_fois_est_sans_effet(self):
        res = self.archive()
        _, recu = self.sync("recevoir", res["archive"])
        self.sync("appliquer", recu["batch_id"], "--confirme", "--sans-post-traitement")
        code, sortie = self.sync("appliquer", recu["batch_id"], "--confirme", "--sans-post-traitement")
        self.assertEqual(code, 0)
        self.assertTrue(sortie["deja_applique"])

    def test_conflit_donne_le_code_4_et_statut_aussi(self):
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="retouche")
        res = self.corriger_et_publier(2)
        _, recu = self.sync("recevoir", str(next(self.lots.glob(f"lot-{res.batch_id}.zip"))))
        code, sortie = self.sync("appliquer", recu["batch_id"], "--confirme", "--sans-post-traitement")
        self.assertEqual(code, 4, sortie)
        self.assertEqual(sortie["statut"], StatutLot.PARTIEL)
        code, etat = self.sync("statut", recu["batch_id"])
        self.assertEqual(code, 4)
        # Un lot partiel ne se relance pas à l'aveugle.
        code, sortie = self.sync("appliquer", recu["batch_id"], "--confirme", "--sans-post-traitement")
        self.assertEqual(code, 1)

    def test_sha256_incorrect_refuse_le_lot(self):
        res = self.archive()
        code, sortie = self.sync("recevoir", res["archive"], "--sha256", "0" * 64)
        self.assertEqual(code, 1)
        self.assertEqual(sortie["statut"], "refuse")
        self.assertFalse(LotSynchro.objects.exists())

    def test_statut_d_un_lot_inconnu(self):
        code, etat = self.sync("statut", "20260101-000000-deadbeef")
        self.assertEqual(code, 1)
        self.assertEqual(etat["statut"], "inconnu")

    def test_confirme_retraits_doit_repeter_le_batch_id(self):
        res = self.archive()
        _, recu = self.sync("recevoir", res["archive"])
        code, sortie = self.sync("appliquer", recu["batch_id"], "--confirme", "--confirme-retraits", "autre-id",
                                 "--sans-post-traitement")
        self.assertEqual(code, 1)
        self.assertFalse(Exercise.objects.exists())

    def test_exporter_reference_dans_un_fichier(self):
        self.appliquer_initial()
        sortie = self.tmp / "reference.json"
        code, res = self.sync("exporter-reference", "--sortie", str(sortie))
        self.assertEqual(code, 0)
        self.assertEqual(res["contenus"], 3)
        ref = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertIn(f"exercice|{EX_ID}", ref["contenus"])

    def test_verifier_fichiers_et_nettoyer(self):
        self.appliquer_initial()
        code, res = self.sync("verifier-fichiers", "--sha")
        self.assertEqual(code, 0, res)
        code, res = self.sync("nettoyer", "--apres-jours", "0")
        self.assertEqual(code, 0)
        self.assertEqual(res["candidats"], [])
