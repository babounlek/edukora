"""
Tests de non-régression des défauts relevés par la revue indépendante du moteur (phase 4). Chaque test porte
le numéro du constat (H = haute, M = moyenne, B = basse) et reproduit le scénario qui échouait.
"""
import json
import zipfile
from pathlib import Path
from unittest import mock

from django.core.files.storage import default_storage

from catalog.models import Cours, Exercise, Figure, Lesson, Question, RappelDeMethode, StatutContenu
from quiz.models import CompetenceItem

from . import moteur
from . import projection as proj
from .models import ContenuSynchro, OperationSynchro, ResultatOperation as R, StatutLot
from .test_moteur import COURS_REL, DOSSIER, EX_ID, EX_REL, QUIZ_REL, Banc, cours, exercice, item, png

EX2_REL = f"{DOSSIER}/bac-test-2024_exercice_2.json"
EX2_ID = f"{DOSSIER}/bac-test-2024_exercice_2"


def exercice2(rappel=False):
    q = {"numero": "1", "enonce_markdown": "Deuxième exercice", "corrige_markdown": "Réponse", "themes": ["Thème de test"]}
    if rappel:
        q["corrige_markdown"] = "### Rappel de méthode\n\nTexte.\n\n### Corrigé\n\nRéponse"
        q["rappels_de_methode"] = [{"id": "rdm-test-2", "competence": "autre", "contenu_markdown": "autre rappel"}]
    return {"epreuve_source": "bac-test-2024", "numero_exercice": "2", "matiere": "Mathématiques",
            "serie": "C", "examen": "BAC", "annee": 2024, "statut": "brouillon", "questions": [q]}


def reecrire_archive(chemin_source, chemin_cible, modifs):
    """Copie une archive en remplaçant des fichiers et en recalculant SHA256SUMS ; `None` supprime le fichier."""
    import hashlib
    contenus = {}
    with zipfile.ZipFile(chemin_source) as z:
        for nom in z.namelist():
            contenus[nom] = z.read(nom)
    for nom, valeur in modifs.items():
        if valeur is None:
            contenus.pop(nom, None)
        else:
            contenus[nom] = valeur
    contenus.pop("SHA256SUMS", None)
    contenus["SHA256SUMS"] = "".join(
        f"{hashlib.sha256(v).hexdigest()}  {n}\n" for n, v in sorted(contenus.items())).encode("utf-8")
    with zipfile.ZipFile(chemin_cible, "w") as z:
        for nom, valeur in contenus.items():
            z.writestr(nom, valeur)
    return chemin_cible


# ============================================================================ H1 nettoyer

class NettoyageSecuriseTests(Banc):
    def test_h1_une_image_citee_dans_un_texte_n_est_jamais_supprimee(self):
        """L'URL d'une image vit aussi dans les textes (énoncés compilés, instantanés de quiz déjà joués)."""
        self.appliquer_initial()
        ancien = Figure.objects.get().image.name
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        # Un texte figé (ici le corrigé d'un item ; en production : QuizQuestion.snapshot) cite l'ancienne URL.
        CompetenceItem.objects.update(corrige_markdown=f"voir ![f](/media/{ancien})")
        res = moteur.nettoyer(apres_jours=0, appliquer_suppression=True)
        self.assertEqual(res["supprimes"], [])
        self.assertEqual(res["conserves_car_references"], [ancien])
        self.assertTrue(default_storage.exists(ancien))
        # Le texte ne cite plus l'image : elle peut partir.
        CompetenceItem.objects.update(corrige_markdown="plus de figure")
        Question.objects.update(enonce_markdown="x", corrige_markdown="y")
        res = moteur.nettoyer(apres_jours=0, appliquer_suppression=True)
        self.assertEqual(res["supprimes"], [ancien])


# ============================================================================ M1 / M7 identité

class IdentiteTests(Banc):
    def test_m1_deux_lessons_pour_la_meme_cle_ne_creent_pas_de_doublon(self):
        self.appliquer_initial()
        exercice_ = Exercise.objects.get()
        origine = exercice_.lesson
        copie = Lesson.objects.get(pk=origine.pk)
        copie.pk, copie.slug = None, "copie-de-la-lesson"
        copie.title = origine.title + " (copie)"
        copie.save()
        copie.cursus.set(origine.cursus.all())
        exercice_.lesson = copie  # l'exercice vit dans la copie ; l'originale (plus ancienne) est vide
        exercice_.save()
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_IDENTITE)
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").objet_pk, exercice_.pk)

    def test_m7_un_fichier_renomme_est_un_conflit_d_identite_clair(self):
        self.appliquer_initial()
        (self.ingest / EX_REL).rename(self.ingest / DOSSIER / "bac-test-2024_exercice_renomme.json")
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        plan = moteur.planifier(lot)
        cible = next(p for p in plan["plan"] if p["id_stable"].endswith("renomme"))
        self.assertEqual(cible["resultat_prevu"], R.CONFLIT_IDENTITE)
        self.assertIn("déjà journalisé", cible["detail"]["raison"])
        self.appliquer(lot)  # pas d'IntegrityError : un conflit propre
        self.assertNotIn(R.ERREUR, self.resultats(lot).values())
        self.assertEqual(Exercise.objects.count(), 1)

    def test_m14_recreer_un_contenu_purge_en_production(self):
        self.appliquer_initial()
        pk_absent = ContenuSynchro.objects.get(type="exercice").objet_pk
        Exercise.objects.all().delete()  # purge admin ; le poste, sans référence à jour, republie le contenu
        lot = self.lot(unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_IDENTITE)
        (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "recreer", "objet_pk_absent": pk_absent,
             "version_proposee": self.vp(lot, EX_ID)}]}), encoding="utf-8")
        self.appliquer(lot, reprise=True)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CREE)
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 2)


# ============================================================================ M2 / B8 approbations

class ApprobationsTests(Banc):
    def setUp(self):
        super().setUp()
        self.appliquer_initial()
        Question.objects.filter(numero="2").update(corrige_markdown="retouche")

    def test_m2_les_decisions_ajoutees_a_un_lot_deja_recu_sont_prises_en_compte(self):
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)
        vu = proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get()))
        archive = next(self.lots.glob(f"lot-{lot.batch_id}.zip"))
        decisions = {"decisions": [{"id_stable": EX_ID, "decision": "ecraser", "empreinte_etat_prod_vue": vu,
                                    "version_proposee": self.vp(lot, EX_ID)}]}
        renvoye = reecrire_archive(archive, self.tmp / "renvoye.zip",
                                   {"approbations.json": json.dumps(decisions).encode("utf-8")})
        lot2 = moteur.recevoir(renvoye, racine=self.recus)
        self.assertEqual(lot2.pk, lot.pk)
        self.appliquer(lot2, reprise=True)
        self.assertEqual(self.resultats(lot2)[("exercice", EX_ID)], R.MIS_A_JOUR)

    def test_b8_une_decision_ne_vaut_que_pour_la_version_relue(self):
        lot = self.corriger_et_publier(2)
        vu = proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get()))
        for version in (None, "f" * 64):
            decision = {"id_stable": EX_ID, "decision": "ecraser", "empreinte_etat_prod_vue": vu}
            if version:
                decision["version_proposee"] = version
            (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [decision]}), encoding="utf-8")
            lot.refresh_from_db()
            self.appliquer(lot, reprise=lot.statut != StatutLot.VERIFIE)
            self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)
        self.assertEqual(Question.objects.get(numero="2").corrige_markdown, "retouche")


# ============================================================================ M3 / M4 post-traitement

class PostTraitementTests(Banc):
    def test_m3_m4_le_post_traitement_est_persistant_reprenable_et_ne_supprime_rien(self):
        lot = self.lot()
        self.appliquer(lot)  # post-traitement différé
        lot.refresh_from_db()
        self.assertFalse(lot.rapport["post_traitement"].get("fait", False))
        lesson = Lesson.objects.get()
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF-1 v1"), \
                mock.patch("synchro.moteur.call_command") as commandes:
            res = moteur.post_traiter(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI)
        lesson.refresh_from_db()
        premier = lesson.sujet_pdf.name
        self.assertRegex(premier, r"-[0-9a-f]{8}\.pdf$")
        self.assertEqual({c.args[0] for c in commandes.call_args_list}, {"indexer_recherche", "calculer_frequences_cours"})

        # Correction : le PDF est regénéré SOUS UN AUTRE NOM, l'ancien est conservé et proposé au nettoyage.
        lot2 = self.corriger_et_publier(2)
        self.appliquer(lot2)
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF-1 v2"), mock.patch("synchro.moteur.call_command"):
            moteur.post_traiter(lot2)
        lesson.refresh_from_db()
        self.assertNotEqual(lesson.sujet_pdf.name, premier)
        self.assertTrue(default_storage.exists(premier))
        lot2.refresh_from_db()
        self.assertEqual(lot2.rapport["a_supprimer"], [premier])
        self.assertEqual(moteur.nettoyer(apres_jours=0)["candidats"].count(premier), 1)

    def test_m3_un_echec_de_post_traitement_se_rejoue(self):
        lot = self.lot()
        self.appliquer(lot)
        with mock.patch("synchro.moteur.generate_sujet_pdf", side_effect=RuntimeError("chromium absent")), \
                mock.patch("synchro.moteur.call_command"):
            res = moteur.post_traiter(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI_AVEC_AVERTISSEMENTS)
        self.assertIn("chromium absent", res["avertissements"][0])
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF"), mock.patch("synchro.moteur.call_command"):
            res = moteur.post_traiter(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI)
        self.assertTrue(Lesson.objects.get().sujet_pdf)


# ============================================================================ M5 courses

class IndexRechercheTests(Banc):
    """Le sitemap est reconstruit à chaque requête ; seul l'index de recherche est à rafraîchir après un lot."""

    def noms(self, commandes):
        return [c.args[0] for c in commandes.call_args_list]

    def test_un_lot_sans_lecon_touchee_reindexe_quand_meme(self):
        lot = self.lot()
        self.appliquer(lot)
        lot.operations.update(detail={"lessons": []})  # comme un lot de cours ou de quiz seuls
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF"), \
                mock.patch("synchro.moteur.call_command") as commandes:
            res = moteur.post_traiter(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI)
        self.assertEqual(set(self.noms(commandes)), {"indexer_recherche", "calculer_frequences_cours"})

    def test_un_echec_d_indexation_se_rejoue_puis_ne_se_repete_plus(self):
        lot = self.lot()
        self.appliquer(lot)
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF"), \
                mock.patch("synchro.moteur.call_command", side_effect=RuntimeError("base occupée")):
            res = moteur.post_traiter(lot)
        self.assertEqual(res["statut"], StatutLot.REUSSI_AVEC_AVERTISSEMENTS)
        with mock.patch("synchro.moteur.generate_sujet_pdf", return_value=b"%PDF"), \
                mock.patch("synchro.moteur.call_command") as commandes:
            res = moteur.post_traiter(lot)
            self.assertEqual(res["statut"], StatutLot.REUSSI)
            self.assertEqual(len(commandes.call_args_list), 2)
            moteur.post_traiter(lot)  # déjà fait : aucune nouvelle indexation
            self.assertEqual(len(commandes.call_args_list), 2)


class CourseTests(Banc):
    def test_m5_une_modification_d_admin_pendant_le_traitement_n_est_pas_ecrasee(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)
        reel = moteur.classer

        def classer_puis_edition_admin(*args, **kwargs):
            resultat = reel(*args, **kwargs)
            Question.objects.filter(numero="2").update(corrige_markdown="retouche concurrente")
            return resultat

        with mock.patch("synchro.moteur.classer", side_effect=classer_puis_edition_admin):
            self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)
        self.assertEqual(Question.objects.get(numero="2").corrige_markdown, "retouche concurrente")

    def test_m5_statut_et_vitrine_modifies_pendant_le_traitement_sont_conserves(self):
        self.appliquer_initial()
        lot = self.corriger_et_publier(2)
        reel = moteur.classer

        def classer_puis_edition_admin(*args, **kwargs):
            resultat = reel(*args, **kwargs)
            CompetenceItem.objects.update(statut=StatutContenu.BROUILLON, est_vitrine=True)
            Cours.objects.update(statut=StatutContenu.BROUILLON)
            Exercise.objects.update(statut=StatutContenu.BROUILLON)
            return resultat

        with mock.patch("synchro.moteur.classer", side_effect=classer_puis_edition_admin):
            self.appliquer(lot)
        i = CompetenceItem.objects.get()
        self.assertEqual((i.statut, i.est_vitrine), (StatutContenu.BROUILLON, True))
        self.assertEqual(Cours.objects.get().statut, StatutContenu.BROUILLON)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.BROUILLON)
        self.assertIn("v2", i.enonce_markdown)


# ============================================================================ M6 porte

class PorteTests(Banc):
    def test_m6_un_exercice_sain_n_est_pas_rejete_a_cause_d_un_defaut_herite(self):
        self.appliquer_initial()
        # Défaut historique d'un AUTRE exercice de la même épreuve : un rappel dont le titre a disparu.
        Exercise.objects.filter(numero_exercice="1").update(corrige_markdown="plus de titre")
        self.ecrire(EX2_REL, exercice2())
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX2_ID)], R.CREE)

    def test_m6_un_defaut_de_l_exercice_lui_meme_reste_bloquant(self):
        self.appliquer_initial()
        defectueux = exercice2(rappel=True)
        defectueux["questions"][0]["corrige_markdown"] = "pas de titre de rappel"
        self.ecrire(EX2_REL, defectueux)
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX2_ID)], R.REJETE_VALIDATION)
        self.assertEqual(Exercise.objects.count(), 1)


# ============================================================================ M8 / M9 / B4 projection

class ProjectionTests(Banc):
    def test_m8_une_correction_hors_perimetre_n_avance_pas_le_journal(self):
        self.appliquer_initial()
        data = exercice(1)
        data["introduction_markdown"] = "Consigne corrigée de l'épreuve"  # champ de la Lesson, non synchronisé
        data["duree_epreuve"] = "3h"
        self.ecrire(EX_REL, data)
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.CORRECTION_HORS_PERIMETRE)
        self.assertEqual(ContenuSynchro.objects.get(type="exercice").version, 1)
        self.assertNotEqual(Lesson.objects.get().introduction_markdown, "Consigne corrigée de l'épreuve")

    def test_m9_une_retouche_manuelle_d_un_champ_compile_est_un_conflit(self):
        self.appliquer_initial()
        Exercise.objects.update(corrige_markdown="Corrigé compilé retouché dans l'admin")
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.CONFLIT_ETAT)
        self.assertEqual(Exercise.objects.get().corrige_markdown, "Corrigé compilé retouché dans l'admin")

    def test_m9_le_contenu_compile_d_un_cours_est_protege_aussi(self):
        self.appliquer_initial()
        Cours.objects.update(content_markdown="retouche manuelle du cours")
        lot = self.corriger_et_publier(2)
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("cours", "cours-test-notion")], R.CONFLIT_ETAT)

    def test_b4_l_empreinte_est_calculee_sur_l_objet_relu_en_base(self):
        data = cours()
        data["meta"]["duree_estimee_min"] = "30"  # chaîne dans le JSON, entier en base
        self.ecrire(COURS_REL, data)
        self.appliquer_initial()
        self.assertEqual(Cours.objects.get().duree_estimee_min, 30)
        j = ContenuSynchro.objects.get(type="cours")
        self.assertEqual(j.empreinte_etat, proj.empreinte_etat(proj.projeter_cours(Cours.objects.get())))
        data2 = cours(2)
        data2["meta"]["duree_estimee_min"] = "30"
        self.ecrire(COURS_REL, data2)
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("cours", "cours-test-notion")], R.MIS_A_JOUR)


# ============================================================================ M10 cours dédoublonné

class DoublonCoursTests(Banc):
    def test_m10_un_cours_dedoublonne_garde_le_rattachement_du_rappel(self):
        self.ecrire(EX2_REL, exercice2(rappel=True))
        lot0 = self.lot()
        self.appliquer(lot0)
        second = cours()
        second["cours_id"] = "cours-test-doublon"
        second["source"]["rappel_id"] = "rdm-test-2"
        self.ecrire(f"{DOSSIER}/bac-test-2024_cours_doublon.json", second)
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("cours", "cours-test-doublon")], R.IGNORE_DEDOUBLONNE)
        self.assertEqual(Cours.objects.count(), 1)
        self.assertEqual(RappelDeMethode.objects.get(external_id="rdm-test-2").cours.external_id, "cours-test-notion")


# ============================================================================ M11 fichiers

class FichiersOrphelinsTests(Banc):
    def test_m11_un_rejet_laisse_des_orphelins_connus_et_la_reprise_reutilise_le_fichier(self):
        self.appliquer_initial()
        # Correction qui écrit une nouvelle image PUIS est rejetée par la porte (rappel sans titre).
        self.png(f"{DOSSIER}/f1.png", "green")
        self.ecrire(EX_REL, exercice(2, rappel_titre=False))
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.REJETE_VALIDATION)
        orphelins = op.detail["orphelins"]
        self.assertEqual(len(orphelins), 1)
        self.assertTrue(default_storage.exists(orphelins[0]))
        self.assertNotEqual(Figure.objects.get().image.name, orphelins[0])

        # Contenu corrigé, même image : le fichier déjà présent est référencé tel quel (pas de copie suffixée).
        self.ecrire(EX_REL, exercice(2))
        lot2 = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot2)
        self.assertEqual(Figure.objects.get().image.name, orphelins[0])

    def test_m11_l_ecriture_est_relue_et_comparee(self):
        self.appliquer_initial()
        self.png(f"{DOSSIER}/f1.png", "yellow")
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        from django.core.files.storage import FileSystemStorage
        reel = FileSystemStorage._save

        def tronque(self_, name, content):
            return reel(self_, name, type(content)(content.read()[:5], name=name))

        with mock.patch.object(FileSystemStorage, "_save", tronque):
            self.appliquer(lot)
        op = OperationSynchro.objects.get(lot=lot, type="exercice")
        self.assertEqual(op.resultat, R.ERREUR)
        self.assertIn("non conforme", op.detail["erreur"])
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)


# ============================================================================ M12 plan avec retrait

class PlanRetraitTests(Banc):
    def test_m12_le_plan_d_un_lot_avec_retrait_n_est_pas_bloquant(self):
        self.appliquer_initial()
        lot = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,),
                       retraits=[{"type": "exercice", "id_stable": EX_ID, "motif": "sujet retiré"}])
        plan = moteur.planifier(lot)
        self.assertEqual(plan["bloquants"], 0, plan)
        retrait = next(p for p in plan["plan"] if p["operation"] == "retirer")
        self.assertEqual(retrait["resultat_prevu"], R.RETIRE)
        self.assertTrue(retrait["detail"]["confirmation_requise"])
        lot.refresh_from_db()
        self.assertEqual(lot.statut, StatutLot.PRET)
        self.assertEqual(Exercise.objects.get().statut, StatutContenu.VALIDE)


# ============================================================================ B1 / B2 / B3 archive

class ArchiveTests(Banc):
    def test_b1_un_chemin_du_manifeste_hors_du_lot_est_refuse(self):
        _, res = self.preparer()
        with zipfile.ZipFile(res["archive"]) as z:
            manifeste = json.loads(z.read("manifest.json"))
        quiz = next(c for c in manifeste["contenus"] if c["type"] == "quiz")
        quiz["fichier"] = "../../../../etc/hostname"
        piege = reecrire_archive(res["archive"], self.tmp / "piege.zip",
                                 {"manifest.json": json.dumps(manifeste).encode("utf-8")})
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(piege, racine=self.recus)
        self.assertEqual(list(self.recus.iterdir()), [])  # rien ne reste extrait

    def test_b2_une_figure_declaree_absente_du_lot_est_une_erreur_de_lot(self):
        _, res = self.preparer()
        manquante = reecrire_archive(res["archive"], self.tmp / "manquante.zip", {f"ingest/{DOSSIER}/f1.png": None})
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(manquante, racine=self.recus)

    def test_b2_une_archive_tronquee_est_une_erreur_de_lot(self):
        _, res = self.preparer()
        tronquee = self.tmp / "tronquee.zip"
        tronquee.write_bytes(Path(res["archive"]).read_bytes()[:80])
        with self.assertRaises(moteur.ErreurLot):
            moteur.recevoir(tronquee, racine=self.recus)

    def test_b3_un_quiz_est_designe_par_son_identifiant_pas_par_sa_position(self):
        deux = item() + [{**item()[0], "external_id": "cqc-notion-test-moyenne-1", "enonce_markdown": "Autre question"}]
        self.ecrire(QUIZ_REL, deux)
        lot = self.lot()
        manifeste = json.loads((Path(lot.dossier) / "manifest.json").read_text(encoding="utf-8"))
        manifeste["contenus"] = [c for c in manifeste["contenus"] if c["type"] != "quiz"] + [
            {**c, "index": 0} for c in manifeste["contenus"] if c["id_stable"] == "cqc-notion-test-moyenne-1"]
        (Path(lot.dossier) / "manifest.json").write_text(json.dumps(manifeste), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(CompetenceItem.objects.get(external_id="cqc-notion-test-moyenne-1").enonce_markdown, "Autre question")


# ============================================================================ B5 poste

class PosteTests(Banc):
    def test_b5_deux_fichiers_pour_le_meme_exercice_sont_refuses_a_la_preparation(self):
        self.ecrire(f"{DOSSIER}/bac-test-2024_exercice_1_bis.json", exercice(2))
        code, res = self.preparer()
        self.assertEqual(code, 1)
        self.assertTrue(any("clé naturelle en double" in e for e in res["erreurs"]))


# ============================================================================ adoption : prendre la production pour base

class BaselineTests(Banc):
    def test_garder_la_production_d_un_contenu_historique_en_fait_la_base_des_corrections_futures(self):
        # Contenu historique en base (aucun journal), dont le texte diffère du JSON du poste.
        source = self.tmp / "hist" / "ingest" / "cm" / "bac-test-2024"
        source.mkdir(parents=True)
        (source / "f1.png").write_bytes(png("red"))
        from catalog.ingestion import ingest_exercise
        ingest_exercise(exercice(1), source_dir=source, exiger_themes=True)
        self.ecrire(EX_REL, exercice(2))
        lot = self.lot(unites=(DOSSIER,))
        (Path(lot.dossier) / "approbations.json").write_text(json.dumps({"decisions": [
            {"id_stable": EX_ID, "decision": "garder_prod"}]}), encoding="utf-8")
        self.appliquer(lot)
        self.assertEqual(self.resultats(lot)[("exercice", EX_ID)], R.GARDE_PROD)
        self.assertIn("v1", Question.objects.get(numero="1").corrige_markdown)  # production inchangée
        journal = ContenuSynchro.objects.get(type="exercice")
        self.assertEqual(journal.empreinte_etat, proj.empreinte_etat(proj.projeter_exercice(Exercise.objects.get())))

        # Le même lot revu plus tard est « inchangé » (plus proposé en adoption) ...
        code, res = self.preparer(unites=(DOSSIER,))
        rejoue = moteur.recevoir(res["archive"], racine=self.recus)
        self.appliquer(rejoue)
        self.assertEqual(self.resultats(rejoue)[("exercice", EX_ID)], R.INCHANGE)

        # ... et une correction ultérieure s'applique proprement par-dessus l'état de la production.
        self.ecrire(EX_REL, exercice(3))
        lot3 = self.lot(reference=moteur.exporter_reference(), unites=(DOSSIER,))
        self.appliquer(lot3)
        self.assertEqual(self.resultats(lot3)[("exercice", EX_ID)], R.MIS_A_JOUR)
        self.assertIn("v3", Question.objects.get(numero="1").corrige_markdown)
