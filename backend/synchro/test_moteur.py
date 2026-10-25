"""
Tests du moteur de synchronisation (voir deploy/SPEC-SYNC-CONTENU.md §12). Chaque test construit de
vrais lots avec l'outil du poste (`outil_lot`), les reçoit et les applique avec le moteur, sur une base
de test et un stockage temporaire : aucun test ne touche à la base ni aux médias de développement.
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.storage import default_storage
from django.test import TestCase, override_settings
from PIL import Image

from access.models import ExerciceFait
from catalog.ingestion import ingest_exercise
from catalog.models import Cours, Exercise, Figure, Lesson, Question, RappelDeMethode, StatutContenu, Tag
from quiz.models import CompetenceItem
from users.models import User

from . import empreintes as emp
from . import moteur, outil_lot
from . import projection as proj
from .models import ContenuSynchro, LotSynchro, OperationSynchro, ResultatOperation as R, StatutLot

DOSSIER = "cm/bac-test-2024"
EX_REL = f"{DOSSIER}/bac-test-2024_exercice_1.json"
EX_ID = f"{DOSSIER}/bac-test-2024_exercice_1"
COURS_REL = f"{DOSSIER}/bac-test-2024_cours_notion.json"
QUIZ_REL = "_quiz/cm/notion-test.json"


def png(couleur):
    tampon = io.BytesIO()
    Image.new("RGB", (40, 30), couleur).save(tampon, format="PNG")
    return tampon.getvalue()


def exercice(version=1, avec_figure=True, rappel_titre=True, numero_exercice="1", questions=2):
    corrige1 = f"{'### Rappel de méthode' if rappel_titre else 'Rappel'}\n\nTexte v{version}.\n\n### Corrigé\n\nRéponse 1 v{version}"
    qs = [
        {"numero": "1", "enonce_markdown": f"Question 1 v{version} ![fig-1](f1.png)" if avec_figure else f"Question 1 v{version}",
         "corrige_markdown": corrige1, "themes": ["Thème de test"],
         "rappels_de_methode": [{"id": "rdm-test-1", "competence": f"Compétence v{version}", "contenu_markdown": f"Rappel v{version}"}]},
        {"numero": "2", "enonce_markdown": f"Question 2 v{version}", "corrige_markdown": f"Réponse 2 v{version}",
         "themes": ["Thème de test"]},
    ][:questions]
    data = {
        "epreuve_source": "bac-test-2024", "numero_exercice": numero_exercice, "matiere": "Mathématiques",
        "serie": "C", "examen": "BAC", "annee": 2024, "statut": "brouillon", "questions": qs,
        "enonce_intro_markdown": f"Introduction v{version}",
    }
    if avec_figure:
        data["figures"] = [{"id": "fig-1", "fichier": "f1.png", "type": "graphique", "legende": f"Légende v{version}"}]
    return data


def cours(version=1):
    return {
        "cours_id": "cours-test-notion",
        "meta": {"titre": "Cours de test", "matiere": "Mathématiques", "serie": None, "tags": ["Thème de test"]},
        "source": {"rappel_id": "rdm-test-1", "epreuve_source": "bac-test-2024"},
        "sections": [{"type": "accroche", "contenu_markdown": f"Accroche v{version}"}],
    }


def item(version=1):
    return [{
        "external_id": "cqc-notion-test-faible-0", "theme": "Thème de test", "matiere": "Mathématiques",
        "cursus": [{"examen": "BAC", "serie": "C"}],
        "enonce_markdown": f"Quel est le résultat v{version} ?", "corrige_markdown": f"### Corrigé\n\nRéponse v{version}",
        "difficulte_estimee": "faible", "type_reponse": "ouverte",
    }]


class Banc(TestCase):
    """Poste simulé : un dossier `ingest/`, des enregistrements de validation, des lots, un stockage temporaire."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="synchro-moteur-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.media = self.tmp / "media"
        self.media.mkdir()
        reglage = override_settings(MEDIA_ROOT=str(self.media))
        reglage.enable()
        self.addCleanup(reglage.disable)
        self.ingest = self.tmp / "ingest"
        self.lots = self.tmp / "lots"
        self.recus = self.tmp / "recus"
        self.valid = self.tmp / "valid"
        for d in (self.ingest, self.lots, self.recus, self.valid):
            d.mkdir()
        self.ecrire(EX_REL, exercice())
        self.png(f"{DOSSIER}/f1.png", "red")
        self.ecrire(COURS_REL, cours())
        self.ecrire(QUIZ_REL, item())

    # ------------------------------------------------------------------ poste

    def ecrire(self, rel, data):
        chemin = self.ingest / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def png(self, rel, couleur):
        chemin = self.ingest / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(png(couleur))

    def valider(self, unite):
        analyse = outil_lot.analyser_unite(str(self.ingest), unite)
        assert not analyse["erreurs"], analyse["erreurs"]
        (self.valid / (outil_lot.slug_unite(unite) + ".json")).write_text(json.dumps({
            "unite": unite, "empreinte_unite": outil_lot.empreinte_unite(analyse), "locale": "ok", "tunnel": "valide",
        }), encoding="utf-8")

    def preparer(self, unites=(DOSSIER, QUIZ_REL), reference=None, retraits=None, **options):
        for u in unites:
            self.valider(u)
        argv = ["preparer", "--ingest", str(self.ingest), "--lots", str(self.lots), "--validations", str(self.valid),
                "--unites", *unites, "--approuve-par", "test"]
        if reference is not None:
            chemin = self.tmp / "reference.json"
            chemin.write_text(json.dumps(reference), encoding="utf-8")
            argv += ["--reference", str(chemin)]
        if retraits is not None:
            chemin = self.tmp / "retraits.json"
            chemin.write_text(json.dumps(retraits), encoding="utf-8")
            argv += ["--retraits", str(chemin)]
        if options.get("tout_ou_rien"):
            argv.append("--tout-ou-rien")
        if options.get("adopter"):
            argv.append("--adopter")
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            code = outil_lot.main(argv)
        resultat = json.loads(sortie.getvalue())
        return code, resultat

    def lot(self, **kwargs):
        code, res = self.preparer(**kwargs)
        self.assertEqual(code, 0, res)
        self.assertEqual(res["statut"], "pret", res)
        return moteur.recevoir(res["archive"], res["sha256_archive"], racine=self.recus)

    def appliquer(self, lot, **kwargs):
        kwargs.setdefault("post_traitement", False)
        return moteur.appliquer(lot, **kwargs)

    def vp(self, lot, id_stable):
        """`version_proposee` du manifeste : une décision `ecraser` doit la citer."""
        manifeste = json.loads((Path(lot.dossier) / "manifest.json").read_text(encoding="utf-8"))
        return next(c["version_proposee"] for c in manifeste["contenus"] if c["id_stable"] == id_stable)

    def resultats(self, lot):
        return {(o.type, o.id_stable): o.resultat for o in lot.operations.all()}

    def appliquer_initial(self):
        lot = self.lot()
        res = self.appliquer(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI, res)
        return lot

    def corriger_et_publier(self, version=2, **options):
        """Modifie les trois contenus et prépare un lot avec la référence de production courante."""
        self.ecrire(EX_REL, exercice(version))
        self.png(f"{DOSSIER}/f1.png", "blue")
        self.ecrire(COURS_REL, cours(version))
        self.ecrire(QUIZ_REL, item(version))
        return self.lot(reference=moteur.exporter_reference(), **options)


# ============================================================================ T1 création

class CreationTests(Banc):
    def test_creation_des_trois_types_avec_figure_et_journal(self):
        lot = self.appliquer_initial()
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Cours.objects.filter(external_id="cours-test-notion").count(), 1)
        self.assertEqual(CompetenceItem.objects.filter(external_id="cqc-notion-test-faible-0").count(), 1)
        self.assertEqual(ContenuSynchro.objects.count(), 3)
        self.assertEqual(set(self.resultats(lot).values()), {R.CREE})
        figure = Figure.objects.get()
        self.assertRegex(figure.image.name, r"-[0-9a-f]{8}\.webp$")
        self.assertTrue(default_storage.exists(figure.image.name))
        self.assertIn(figure.image.url, Question.objects.get(numero="1").enonce_markdown)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)

    def test_le_journal_conserve_les_empreintes(self):
        self.appliquer_initial()
        j = ContenuSynchro.objects.get(type="exercice")
        self.assertEqual(j.id_stable, EX_ID)
        self.assertEqual(j.version, 1)
        self.assertEqual(j.empreinte_etat, proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get())))
        self.assertEqual(j.fichiers["fig-1"]["chemin"], Figure.objects.get().image.name)

    def test_parite_creation_sync_et_creation_historique(self):
        """Même JSON sans figure : le moteur produit exactement l'état que l'ingestion historique."""
        self.ecrire(EX_REL, exercice(avec_figure=False))
        self.appliquer_initial()
        via_sync = proj.projeter_exercice(Exercise.objects.get())
        Exercise.objects.all().delete()
        Lesson.objects.all().delete()
        source = self.tmp / "hist" / "ingest" / "cm" / "bac-test-2024"
        source.mkdir(parents=True)
        ex, _ = ingest_exercise(exercice(avec_figure=False), source_dir=source, exiger_themes=True)
        self.assertEqual(proj.difference(via_sync, proj.projeter_exercice(ex)), [])


# ============================================================================ T2 / T4 rejeu

class RejeuTests(Banc):
    def test_un_lot_deja_applique_ne_fait_rien(self):
        lot = self.appliquer_initial()
        avant = list(ContenuSynchro.objects.values_list("version", "applique_le"))
        res = self.appliquer(moteur.recevoir(next(self.lots.glob("lot-*.zip")), racine=self.recus))
        self.assertTrue(res["deja_applique"])
        self.assertEqual(list(ContenuSynchro.objects.values_list("version", "applique_le")), avant)
        self.assertEqual(LotSynchro.objects.count(), 1)

    def test_meme_contenu_dans_un_nouveau_lot_est_inchange_sans_ecriture(self):
        self.appliquer_initial()
        modifie_le = Exercise.objects.get().updated_at
        # Pas de référence : le lot dit « create » ; le serveur reconnaît la même version.
        code, res = self.preparer()
        self.assertEqual(code, 0)
        lot2 = moteur.recevoir(res["archive"], racine=self.recus)
        self.appliquer(lot2)
        self.assertEqual(set(self.resultats(lot2).values()), {R.INCHANGE})
        self.assertEqual(Exercise.objects.get().updated_at, modifie_le)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)

    def test_lot_sans_changement_avec_reference_ne_produit_aucun_lot(self):
        self.appliquer_initial()
        code, res = self.preparer(reference=moteur.exporter_reference())
        self.assertEqual(code, 0)
        self.assertEqual(res["statut"], "rien_a_publier")

    def test_recevoir_est_idempotent(self):
        code, res = self.preparer()
        a = moteur.recevoir(res["archive"], res["sha256_archive"], racine=self.recus)
        b = moteur.recevoir(res["archive"], res["sha256_archive"], racine=self.recus)
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(OperationSynchro.objects.filter(lot=a).count(), 3)


# ============================================================================ T3 correction

class CorrectionTests(Banc):
    def test_correction_sur_place_sans_doublon_ni_perte_d_activite(self):
        self.appliquer_initial()
        user = User.objects.create_user(phone_number="677200001", password="x")
        exercice_avant = Exercise.objects.get()
        fait = ExerciceFait.objects.create(profil=user.profils.first(), exercise=exercice_avant)
        pk_exercice, pks_questions = exercice_avant.pk, set(Question.objects.values_list("pk", flat=True))
        ancien_fichier = Figure.objects.get().image.name

        lot = self.corriger_et_publier(2)
        res = self.appliquer(lot)

        self.assertEqual(res["statut"], StatutLot.REUSSI, res)
        self.assertEqual(set(self.resultats(lot).values()), {R.MIS_A_JOUR})
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(Exercise.objects.get().pk, pk_exercice)
        self.assertEqual(set(Question.objects.values_list("pk", flat=True)), pks_questions)
        self.assertTrue(ExerciceFait.objects.filter(pk=fait.pk).exists())
        question1 = Question.objects.get(numero="1")
        self.assertIn("v2", question1.corrige_markdown)
        self.assertIn("v2", Exercise.objects.get().enonce_intro_markdown)
        self.assertEqual(RappelDeMethode.objects.get().contenu_markdown, "Rappel v2")
        self.assertEqual(Cours.objects.get(external_id="cours-test-notion").sections_raw[0]["contenu_markdown"], "Accroche v2")
        self.assertIn("v2", CompetenceItem.objects.get(external_id="cqc-notion-test-faible-0").enonce_markdown)
        self.assertEqual(set(ContenuSynchro.objects.values_list("version", flat=True)), {2})
        # Image remplacée : nouveau fichier adressé, ancien conservé jusqu'à `nettoyer`.
        figure = Figure.objects.get()
        self.assertNotEqual(figure.image.name, ancien_fichier)
        self.assertTrue(default_storage.exists(ancien_fichier))
        self.assertTrue(default_storage.exists(figure.image.name))
        self.assertIn(figure.image.url, question1.enonce_markdown)
        detail = OperationSynchro.objects.get(lot=lot, type="exercice").detail
        self.assertIn(ancien_fichier, detail["a_supprimer"])
        self.assertTrue(any(d.startswith("questions.1.corrige_markdown") for d in detail["diff"]))

    def test_une_figure_inchangee_n_est_pas_reecrite(self):
        self.appliquer_initial()
        figure_avant = Figure.objects.get().image.name
        self.ecrire(EX_REL, exercice(2))  # texte modifié, même PNG
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(Figure.objects.get().image.name, figure_avant)
        self.assertEqual(OperationSynchro.objects.get(lot=lot, type="exercice").detail["a_supprimer"], [])

    def test_ne_touche_ni_statut_ni_published_at(self):
        self.appliquer_initial()
        Exercise.objects.update(statut=StatutContenu.BROUILLON)  # dépublié à la main par l'admin
        Cours.objects.update(statut=StatutContenu.BROUILLON)
        CompetenceItem.objects.update(statut=StatutContenu.BROUILLON, est_vitrine=True)
        # Ces modifications admin ne figurent pas dans la projection d'état (statut exclu).
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.BROUILLON)
        self.assertEqual(Cours.objects.get(external_id="cours-test-notion").statut, StatutContenu.BROUILLON)
        item_ = CompetenceItem.objects.get(external_id="cqc-notion-test-faible-0")
        self.assertEqual(item_.statut, StatutContenu.BROUILLON)
        self.assertTrue(item_.est_vitrine)

    def test_planifier_n_ecrit_rien(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)
        avant = {
            "q": list(Question.objects.values_list("corrige_markdown", flat=True)),
            "media": sorted(p.name for p in self.media.rglob("*") if p.is_file()),
            "journal": list(ContenuSynchro.objects.values_list("version", flat=True)),
        }
        plan = moteur.planifier(lot)
        self.assertEqual(plan["bloquants"], 0)
        self.assertEqual({p["resultat_prevu"] for p in plan["plan"]}, {R.MIS_A_JOUR})
        apres = {
            "q": list(Question.objects.values_list("corrige_markdown", flat=True)),
            "media": sorted(p.name for p in self.media.rglob("*") if p.is_file()),
            "journal": list(ContenuSynchro.objects.values_list("version", flat=True)),
        }
        self.assertEqual(avant, apres)
        lot.refresh_from_db()
        self.assertEqual(lot.statut, StatutLot.PRET)


# ============================================================================ T5 conflits

class ConflitsTests(Banc):
    def test_modification_en_production_n_est_jamais_ecrasee(self):
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="Corrigé retouché à la main en production")
        lot = self.corriger_et_publier(2)
        res = self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)
        self.assertEqual(Question.objects.get(numero="2").corrige_markdown, "Corrigé retouché à la main en production")
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)
        # Les autres contenus du lot sont appliqués, le lot est partiel et le dit.
        self.assertEqual(self.resultats(lot)[("cours", "cours-test-notion")], R.MIS_A_JOUR)
        self.assertEqual(res["statut"], StatutLot.PARTIEL)

    def test_decision_ecraser_liee_a_l_etat_vu(self):
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="retouche")
        lot = self.corriger_et_publier(2)
        etat_vu = proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get()))
        approbations = Path(lot.dossier) / "approbations.json"

        # Décision prise sur un AUTRE état que l'actuel : sans effet.
        approbations.write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "ecraser", "empreinte_etat_prod_vue": "0" * 64,
             "version_proposee": self.vp(lot, EX_ID)}]}), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)

        # Décision sur l'état réellement vu : appliquée par `reprendre`.
        approbations.write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "ecraser", "empreinte_etat_prod_vue": etat_vu,
             "version_proposee": self.vp(lot, EX_ID)}]}), encoding="utf-8")
        lot.refresh_from_db()
        self.appliquer(lot, reprise=True)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.MIS_A_JOUR)
        self.assertIn("v2", Question.objects.get(numero="2").corrige_markdown)

    def test_garder_la_version_de_production(self):
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="retouche")
        lot = self.corriger_et_publier(2)
        (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "garder_prod"}]}), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.GARDE_PROD)
        self.assertEqual(Question.objects.get(numero="2").corrige_markdown, "retouche")

    def test_conflit_de_version_quand_la_production_a_avance(self):
        self.appliquer_initial()
        reference = moteur.exporter_reference()
        # Un autre lot a fait avancer la production depuis la référence utilisée par le poste.
        ContenuSynchro.objects.filter(type="cours").update(empreinte_source="autre-version-appliquee")
        self.ecrire(COURS_REL, cours(2))
        lot = self.lot(reference=reference, unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("cours", "cours-test-notion")], R.CONFLIT_VERSION)
        self.assertIn("v1", Cours.objects.get(external_id="cours-test-notion").sections_raw[0]["contenu_markdown"])

    def test_identite_changee(self):
        self.appliquer_initial()
        self.ecrire(EX_REL, exercice(2, numero_exercice="7"))  # même chemin, autre clé naturelle
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_IDENTITE)
        self.assertEqual(Exercise.objects.count(), 1)

    def test_tout_ou_rien_n_applique_rien_au_moindre_conflit(self):
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="retouche")
        lot = self.corriger_et_publier(2, tout_ou_rien=True)
        res = self.appliquer(lot)
        self.assertEqual(res["statut"], StatutLot.ECHOUE)
        self.assertIn("v1", Cours.objects.get(external_id="cours-test-notion").sections_raw[0]["contenu_markdown"])
        self.assertEqual(set(ContenuSynchro.objects.values_list("version", flat=True)), {1})


# ============================================================================ T6 retraits

class RetraitsTests(Banc):
    def test_retrait_exige_la_confirmation_et_ne_supprime_rien(self):
        self.appliquer_initial()
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,),
                       retraits=[{"type": "exercice", "id_stable": EX_ID, "motif": "sujet retiré"}])
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.ERREUR)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)
        lot.refresh_from_db()
        self.appliquer(lot, reprise=True, confirme_retraits=True)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.RETIRE)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.REJETE)
        self.assertEqual(Question.objects.count(), 2)  # aucune suppression
        self.assertEqual(Figure.objects.count(), 1)

    def test_un_contenu_absent_du_lot_n_est_jamais_touche(self):
        self.appliquer_initial()
        self.ecrire(QUIZ_REL, item(2))
        lot = self.lot(reference=moteur.exporter_reference(), unites=(QUIZ_REL,))
        self.appliquer(lot)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)
        self.assertEqual(ContenuSynchro.objects.get(type="quiz").version, 2)

    def test_reintegration(self):
        self.appliquer_initial()
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,),
                       retraits=[{"type": "cours", "id_stable": "cours-test-notion", "motif": "erreur"}])
        self.appliquer(lot, confirme_retraits=True)
        self.assertEqual(Cours.objects.get(external_id="cours-test-notion").statut, StatutContenu.REJETE)


# ============================================================================ T7 interruptions

class InterruptionTests(Banc):
    def test_exception_pendant_un_contenu_annule_ce_contenu_seulement(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)
        with mock.patch("synchro.adaptateurs.ingest_exercise", side_effect=RuntimeError("panne simulée")):
            res = self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.ERREUR)
        self.assertIn("panne simulée", OperationSynchro.objects.get(lot=lot, type="exercice").detail["erreur"])
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)
        self.assertEqual(self.resultats(lot)[("quiz", "cqc-notion-test-faible-0")], R.MIS_A_JOUR)
        self.assertEqual(res["statut"], StatutLot.PARTIEL)
        # La reprise n'exécute que ce qui reste.
        lot.refresh_from_db()
        res2 = self.appliquer(lot, reprise=True)
        self.assertEqual(res2["statut"], StatutLot.REUSSI)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 2)
        self.assertEqual(ContenuSynchro.objects.get(type="quiz").version, 2)  # pas rejoué

    def test_echec_d_ecriture_de_fichier_ne_change_rien_en_base(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)
        with mock.patch("catalog.ingestion._affecter_image", side_effect=OSError("disque plein")):
            self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.ERREUR)
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)
        self.assertEqual(Figure.objects.count(), 1)

    def test_processus_mort_apres_lancement_devient_a_verifier_puis_reprend(self):
        lot = self.lot()
        lot.statut, lot.pid = StatutLot.EN_COURS, 2_000_000_000  # aucun processus
        lot.battement_le = lot.recu_le - moteur.SEUIL_BATTEMENT * 2
        lot.save()
        self.assertEqual(moteur.statut(lot.batch_id)["statut"], StatutLot.A_VERIFIER)
        with self.assertRaises(moteur.ErreurLot):
            self.appliquer(LotSynchro.objects.get(pk=lot.pk))  # pas de relance aveugle
        res = self.appliquer(LotSynchro.objects.get(pk=lot.pk), reprise=True)
        self.assertEqual(res["statut"], StatutLot.REUSSI)
        self.assertEqual(ContenuSynchro.objects.count(), 3)

    def test_un_processus_vivant_empeche_la_relance(self):
        lot = self.lot()
        lot.statut, lot.pid, lot.battement_le = StatutLot.EN_COURS, os.getpid(), lot.recu_le
        lot.save()
        with self.assertRaises(moteur.ErreurLot):
            self.appliquer(LotSynchro.objects.get(pk=lot.pk), reprise=True)


# ============================================================================ T8 fichiers

class FichiersTests(Banc):
    def test_verifier_fichiers_signale_reference_sans_fichier_et_sha_divergent(self):
        self.appliquer_initial()
        self.assertEqual(moteur.verifier_fichiers(avec_sha=True), {"references_sans_fichier": [], "sha_divergents": []})
        nom = Figure.objects.get().image.name
        chemin = Path(default_storage.path(nom))
        chemin.write_bytes(b"corrompu")
        self.assertEqual(len(moteur.verifier_fichiers(avec_sha=True)["sha_divergents"]), 1)
        chemin.unlink()
        rapport = moteur.verifier_fichiers(avec_sha=True)
        self.assertTrue(any(nom in r for r in rapport["references_sans_fichier"]))
        self.assertTrue(Figure.objects.exists())  # rapport seulement, rien n'est supprimé

    def test_nettoyer_supprime_l_ancien_fichier_seulement_s_il_n_est_plus_reference(self):
        self.appliquer_initial()
        ancien = Figure.objects.get().image.name
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        lot.refresh_from_db()
        # Trop récent : rien à nettoyer.
        self.assertEqual(moteur.nettoyer(apres_jours=7)["candidats"], [])
        res = moteur.nettoyer(apres_jours=0)
        self.assertEqual(res["candidats"], [ancien])
        self.assertTrue(default_storage.exists(ancien))  # liste seulement par défaut
        moteur.nettoyer(apres_jours=0, appliquer_suppression=True)
        self.assertFalse(default_storage.exists(ancien))
        self.assertTrue(default_storage.exists(Figure.objects.get().image.name))
        # Un fichier encore référencé n'est jamais supprimé, même listé.
        OperationSynchro.objects.filter(lot=lot, type="exercice").update(
            detail={"a_supprimer": [Figure.objects.get().image.name]})
        self.assertEqual(moteur.nettoyer(apres_jours=0)["candidats"], [])


# ============================================================================ T11 garde / données opérationnelles

class GardeTests(Banc):
    def test_ecriture_hors_perimetre_est_refusee(self):
        from catalog.models import Country

        def malveillant(data, source_dir=None, **kw):
            Country.objects.create(code="ZZ", label="Interdit")
            raise AssertionError("ne doit pas être atteint")

        lot = self.lot(unites=(DOSSIER,))
        with mock.patch("synchro.adaptateurs.ingest_exercise", side_effect=malveillant):
            self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.ERREUR)
        self.assertTrue(op.detail["garde"])
        self.assertFalse(Country.objects.filter(code="ZZ").exists())

    def test_suppression_pendant_un_lot_est_refusee(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)

        def destructeur(data, source_dir=None, **kw):
            Tag.objects.filter(name="Thème de test").delete()

        with mock.patch("synchro.adaptateurs.ingest_exercise", side_effect=destructeur):
            self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.ERREUR)
        self.assertTrue(Tag.objects.filter(name="Thème de test").exists())

    def test_les_donnees_operationnelles_sont_intactes_apres_une_correction(self):
        self.appliquer_initial()
        user = User.objects.create_user(phone_number="677200002", password="x")
        ExerciceFait.objects.create(profil=user.profils.first(), exercise=Exercise.objects.get())
        etat = (User.objects.count(), user.profils.count(), ExerciceFait.objects.count())
        self.appliquer(self.corriger_et_publier(2))
        self.assertEqual((User.objects.count(), user.profils.count(), ExerciceFait.objects.count()), etat)


# ============================================================================ T13 / T14 structure et porte

class StructureEtPorteTests(Banc):
    def test_question_absente_du_json_n_est_jamais_supprimee(self):
        self.appliquer_initial()
        self.ecrire(EX_REL, exercice(2, questions=1))
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.STRUCTURE_MODIFIEE)
        self.assertTrue(any("question 2" in s for s in op.detail["structure"]))
        self.assertEqual(Question.objects.count(), 2)
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)

    def test_la_porte_rejette_une_correction_qui_casse_l_exercice_publie(self):
        self.appliquer_initial()
        self.ecrire(EX_REL, exercice(2, rappel_titre=False))  # rappel jamais affiché : BLOQUANT
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.REJETE_VALIDATION)
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)  # jamais rétrogradé
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)


# ============================================================================ T15 adoption

class AdoptionTests(Banc):
    def creer_historique(self, version=1):
        """Contenu déjà en base, créé par l'ingestion historique : aucune ligne de journal."""
        source = self.tmp / "hist" / "ingest" / "cm" / "bac-test-2024"
        source.mkdir(parents=True, exist_ok=True)
        (source / "f1.png").write_bytes(png("red"))
        ingest_exercise(exercice(version), source_dir=source, exiger_themes=True)

    def test_contenu_existant_non_journalise_exige_une_approbation(self):
        self.creer_historique(1)
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(unites=(DOSSIER,), adopter=True)
        self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.ADOPTION_A_CONFIRMER)
        self.assertTrue(op.detail["diff"])
        self.assertEqual(ContenuSynchro.objects.filter(type="exercice").count(), 0)
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)

    def test_adoption_approuvee_puis_corrections_normales(self):
        self.creer_historique(1)
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(unites=(DOSSIER,), adopter=True)
        vu = proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get()))
        (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "ecraser", "empreinte_etat_prod_vue": vu,
             "version_proposee": self.vp(lot, EX_ID)}]}), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.MIS_A_JOUR)
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertIn("v2", Question.objects.get(numero="1").corrige_markdown)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)

    def test_adoption_sans_difference_est_journalisee_sans_approbation(self):
        self.creer_historique(1)
        self.ecrire(EX_REL, exercice(1))
        lot = self.lot(unites=(DOSSIER,))
        modifie_le = Exercise.objects.get().updated_at
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.INCHANGE)
        self.assertEqual(ContenuSynchro.objects.filter(type="exercice").count(), 1)
        self.assertEqual(Exercise.objects.get().updated_at, modifie_le)

    def test_decision_garder_prod_pour_un_contenu_non_journalise(self):
        self.creer_historique(1)
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(unites=(DOSSIER,))
        (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "garder_prod"}]}), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.GARDE_PROD)


# ============================================================================ réception / sécurité

class ReceptionTests(Banc):
    def test_sha256_de_l_archive_incorrect(self):
        _, res = self.preparer()
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(res["archive"], "0" * 64, racine=self.recus)

    def test_archive_alteree_apres_preparation(self):
        import zipfile
        _, res = self.preparer()
        alteree = self.tmp / "alteree.zip"
        with zipfile.ZipFile(res["archive"]) as src, zipfile.ZipFile(alteree, "w") as dst:
            for nom in src.namelist():
                contenu = src.read(nom)
                if nom.endswith("_exercice_1.json"):
                    contenu = contenu.replace(b"Question 1", b"Question X")
                dst.writestr(nom, contenu)
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(alteree, racine=self.recus)

    def test_empreinte_du_manifeste_falsifiee(self):
        import zipfile
        _, res = self.preparer()
        falsifiee = self.tmp / "falsifiee.zip"
        with zipfile.ZipFile(res["archive"]) as src, zipfile.ZipFile(falsifiee, "w") as dst:
            for nom in src.namelist():
                contenu = src.read(nom)
                if nom == "manifest.json":
                    manifeste = json.loads(contenu)
                    manifeste["contenus"][0]["version_proposee"] = "f" * 64
                    contenu = json.dumps(manifeste).encode("utf-8")
                dst.writestr(nom, contenu)
        # SHA256SUMS ne couvre plus manifest.json -> refus par la cohérence de l'archive.
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(falsifiee, racine=self.recus)

    def test_chemin_dangereux_dans_l_archive(self):
        import zipfile
        _, res = self.preparer()
        piegee = self.tmp / "piegee.zip"
        with zipfile.ZipFile(res["archive"]) as src, zipfile.ZipFile(piegee, "w") as dst:
            for nom in src.namelist():
                dst.writestr(nom, src.read(nom))
            dst.writestr("../evasion.txt", b"x")
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(piegee, racine=self.recus)

    def test_schema_non_supporte(self):
        import zipfile
        _, res = self.preparer()
        futur = self.tmp / "futur.zip"
        with zipfile.ZipFile(res["archive"]) as src, zipfile.ZipFile(futur, "w") as dst:
            for nom in src.namelist():
                contenu = src.read(nom)
                if nom == "manifest.json":
                    m = json.loads(contenu)
                    m["schema_sync"] = 99
                    contenu = json.dumps(m).encode("utf-8")
                dst.writestr(nom, contenu)
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(futur, racine=self.recus)

    def test_exporter_reference(self):
        self.appliquer_initial()
        ref = moteur.exporter_reference()
        self.assertEqual(len(ref["contenus"]), 3)
        self.assertIn(f"exercice|{EX_ID}", ref["contenus"])
        self.assertEqual(len(ref["contenus"][f"exercice|{EX_ID}"]["empreinte_source"]), 64)


class PlanTests(Banc):
    def test_le_plan_d_un_premier_lot_voit_les_contenus_precedents(self):
        """Un cours dépend de son exercice, un quiz de ses thèmes : le plan les simule dans l'ordre."""
        lot = self.lot()
        plan = moteur.planifier(lot)
        self.assertEqual(plan["bloquants"], 0, plan)
        self.assertEqual({p["resultat_prevu"] for p in plan["plan"]}, {R.CREE})
        self.assertFalse(Exercise.objects.exists())
        self.assertFalse(Cours.objects.exists())
        self.assertFalse(any(self.media.rglob("*.webp")))

    def test_tout_ou_rien_applique_un_premier_lot_sans_conflit(self):
        code, res = self.preparer(tout_ou_rien=True)
        lot = moteur.recevoir(res["archive"], res["sha256_archive"], racine=self.recus)
        self.assertEqual(self.appliquer(lot)["statut"], StatutLot.REUSSI)
        self.assertEqual(ContenuSynchro.objects.count(), 3)
