"""Tests de synchro.outil_lot : analyse d'unités, préparation de lots, inventaire (git temporaire)."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile

_ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("outil_lot", os.path.join(_ICI, "outil_lot.py"))
outil = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(outil)

PNG = b"\x89PNG\r\n\x1a\n-fausse-image-"


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def sauver(data, chemin):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def lire_octets(chemin):
    with open(chemin, "rb") as f:
        return f.read()


def lire_texte(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()



def exercice(numero="1", figure=None, **extra):
    data = {"epreuve_source": "bac-test-2020.pdf", "numero_exercice": numero, "matiere": "Maths", "annee": 2020,
            "statut": "brouillon", "questions": [{"numero": "1", "enonce_markdown": "q", "corrige_markdown": "c"}]}
    if figure:
        data["figures"] = [{"id": "fig-1", "fichier": figure}]
    data.update(extra)
    return data


def cours(cours_id="c-1"):
    return {"cours_id": cours_id, "meta": {"titre": "T"}, "sections": [{"type": "x", "contenu_markdown": "y"}]}


class Banc(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="synchro-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.ingest = os.path.join(self.tmp, "ingest")
        self.lots = os.path.join(self.tmp, "lots")
        self.validations = os.path.join(self.tmp, "validations")
        for d in (self.ingest, self.lots, self.validations):
            os.makedirs(d)

    def ecrire(self, rel, data, brut=None):
        chemin = os.path.join(self.ingest, *rel.split("/"))
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "wb") as f:
            f.write(brut if brut is not None else json.dumps(data, ensure_ascii=False).encode("utf-8"))
        return chemin

    def png(self, rel):
        chemin = os.path.join(self.ingest, *rel.split("/"))
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "wb") as f:
            f.write(PNG)

    def valider(self, unite, tunnel="valide", locale="ok", empreinte=None):
        a = outil.analyser_unite(self.ingest, unite)
        emp = empreinte or outil.empreinte_unite(a)
        with open(os.path.join(self.validations, outil.slug_unite(unite) + ".json"), "w", encoding="utf-8") as f:
            json.dump({"unite": unite, "empreinte_unite": emp, "locale": locale, "tunnel": tunnel}, f)

    def lancer(self, *argv):
        sortie, erreur = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
            code = outil.main(list(argv))
        texte = sortie.getvalue().strip() or erreur.getvalue().strip()
        return code, (json.loads(texte) if texte.startswith("{") else texte)

    def preparer(self, *unites, approuve="moi", **options):
        argv = ["preparer", "--ingest", self.ingest, "--lots", self.lots, "--validations", self.validations,
                "--unites", *unites]
        if approuve:
            argv += ["--approuve-par", approuve]
        for cle, val in options.items():
            argv += [f"--{cle.replace('_', '-')}"] + ([] if val is True else [str(val)])
        return self.lancer(*argv)


class AnalyseTests(Banc):
    def test_unite_valide(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(figure="f.png"))
        self.png("cm/dos/f.png")
        self.ecrire("cm/dos/dos_cours_a.json", cours())
        a = outil.analyser_unite(self.ingest, "cm/dos")
        self.assertEqual(a["erreurs"], [])
        self.assertEqual({e["type"] for e in a["elements"]}, {"exercice", "cours"})
        ex = next(e for e in a["elements"] if e["type"] == "exercice")
        self.assertEqual(ex["id_stable"], "cm/dos/dos_exercice_1")
        self.assertEqual(ex["fichiers"][0]["sha256"], hashlib.sha256(PNG).hexdigest())

    def test_figure_declaree_introuvable(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(figure="absente.png"))
        a = outil.analyser_unite(self.ingest, "cm/dos")
        self.assertTrue(any("introuvable" in e for e in a["erreurs"]))

    def test_json_invalide_et_bom(self):
        self.ecrire("cm/dos/a.json", None, brut=b"{pas du json")
        self.ecrire("cm/dos/b.json", None, brut=b"\xef\xbb\xbf" + json.dumps(exercice("2")).encode())
        a = outil.analyser_unite(self.ingest, "cm/dos")
        self.assertTrue(any("illisible" in e for e in a["erreurs"]))
        self.assertTrue(any("BOM" in w for w in a["avertissements"]))

    def test_quiz_sans_external_id_et_doublon(self):
        item = {"external_id": "q-1", "theme": "t", "enonce_markdown": "e", "corrige_markdown": "c"}
        self.ecrire("_quiz/cm/f.json", [item, dict(item), {"theme": "t", "enonce_markdown": "e", "corrige_markdown": "c"}])
        a = outil.analyser_unite(self.ingest, "_quiz/cm/f.json")
        self.assertTrue(any("sans identifiant stable" in e for e in a["erreurs"]))
        self.assertTrue(any("déjà vu" in e for e in a["erreurs"]))

    def test_champ_obligatoire_manquant(self):
        data = exercice()
        data["questions"] = []
        self.ecrire("cm/dos/dos_exercice_1.json", data)
        a = outil.analyser_unite(self.ingest, "cm/dos")
        self.assertTrue(any("obligatoires" in e for e in a["erreurs"]))

    def test_type_hors_v1_ignore_sans_erreur(self):
        self.ecrire("cm/dos/rapport.json", {"x": 1})
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        a = outil.analyser_unite(self.ingest, "cm/dos")
        self.assertEqual(a["erreurs"], [])
        self.assertTrue(any("rapport.json" in i for i in a["ignores"]))

    def test_statut_du_json_ne_change_pas_l_empreinte(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(statut="brouillon"))
        e1 = outil.analyser_unite(self.ingest, "cm/dos")["elements"][0]["empreinte_source"]
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(statut="valide"))
        e2 = outil.analyser_unite(self.ingest, "cm/dos")["elements"][0]["empreinte_source"]
        self.assertEqual(e1, e2)

    def test_contenu_modifie_change_l_empreinte_d_unite(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        e1 = outil.empreinte_unite(outil.analyser_unite(self.ingest, "cm/dos"))
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(enonce_intro_markdown="corrigé"))
        e2 = outil.empreinte_unite(outil.analyser_unite(self.ingest, "cm/dos"))
        self.assertNotEqual(e1, e2)


class PreparationTests(Banc):
    def monter(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(figure="f.png"))
        self.png("cm/dos/f.png")
        self.ecrire("cm/dos/dos_cours_a.json", cours())
        self.valider("cm/dos")

    def test_refuse_sans_validation_locale(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        code, res = self.preparer("cm/dos")
        self.assertEqual(code, 1)
        self.assertTrue(any("aucune validation locale" in e for e in res["erreurs"]))
        self.assertEqual(os.listdir(self.lots), [])

    def test_refuse_validation_perimee(self):
        self.monter()
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(enonce_intro_markdown="modifié après validation"))
        code, res = self.preparer("cm/dos")
        self.assertEqual(code, 1)
        self.assertTrue(any("périmée" in e for e in res["erreurs"]))

    def test_refuse_tunnel_non_rejoue_sans_option_explicite(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        self.valider("cm/dos", tunnel="non_rejoue")
        code, _ = self.preparer("cm/dos")
        self.assertEqual(code, 1)
        code, res = self.preparer("cm/dos", accepter_sans_tunnel=True)
        self.assertEqual(code, 0, res)
        manifeste = charger(os.path.join(res["dossier"], "manifest.json"))
        self.assertEqual(manifeste["contenus"][0]["validation"]["tunnel"], "non_rejoue")

    def test_approbation_requise_et_rien_n_est_ecrit(self):
        self.monter()
        code, res = self.preparer("cm/dos", approuve=None)
        self.assertEqual(code, 5)
        self.assertEqual(res["statut"], "approbation_requise")
        self.assertEqual(os.listdir(self.lots), [])

    def test_lot_complet_et_verifiable(self):
        self.monter()
        code, res = self.preparer("cm/dos", nom="essai")
        self.assertEqual(code, 0, res)
        racine = res["dossier"]
        manifeste = charger(os.path.join(racine, "manifest.json"))
        self.assertEqual(manifeste["schema_sync"], 1)
        self.assertEqual({c["operation"] for c in manifeste["contenus"]}, {"create"})
        self.assertTrue(manifeste["options"]["reference_absente"])
        self.assertEqual(manifeste["approbation"]["par"], "moi")
        # SHA256SUMS couvre tous les fichiers (hors lui-même) et dit vrai.
        lignes = [l.split("  ", 1) for l in lire_texte(os.path.join(racine, "SHA256SUMS")).splitlines()]
        rels = {r for _, r in lignes}
        self.assertIn("manifest.json", rels)
        self.assertIn("ingest/cm/dos/f.png", rels)
        for sha, rel in lignes:
            self.assertEqual(hashlib.sha256(lire_octets(os.path.join(racine, *rel.split("/")))).hexdigest(), sha)
        # Copie octet pour octet du JSON d'ingestion (le serveur recalcule les empreintes dessus).
        self.assertEqual(lire_octets(os.path.join(racine, "ingest", "cm", "dos", "dos_exercice_1.json")),
                         lire_octets(os.path.join(self.ingest, "cm", "dos", "dos_exercice_1.json")))
        # L'archive correspond au dossier et à son .sha256.
        with zipfile.ZipFile(res["archive"]) as z:
            self.assertIn("manifest.json", z.namelist())
            self.assertIn("SHA256SUMS", z.namelist())
        attendu = lire_texte(res["archive"] + ".sha256").split()[0]
        self.assertEqual(attendu, hashlib.sha256(lire_octets(res["archive"])).hexdigest())

    def test_classement_avec_reference_noop_update_create(self):
        self.monter()
        self.ecrire("cm/dos/dos_exercice_2.json", exercice("2"))
        self.valider("cm/dos")
        a = {e["id_stable"]: e for e in outil.analyser_unite(self.ingest, "cm/dos")["elements"]}
        reference = {"genere_le": "2026-11-01T00:00:00Z", "contenus": {
            "exercice|cm/dos/dos_exercice_1": {"empreinte_source": a["cm/dos/dos_exercice_1"]["empreinte_source"]},
            "exercice|cm/dos/dos_exercice_2": {"empreinte_source": "ancienne-version"},
        }}
        chemin_ref = os.path.join(self.tmp, "ref.json")
        sauver(reference, chemin_ref)
        code, res = self.preparer("cm/dos", reference=chemin_ref)
        self.assertEqual(code, 0, res)
        ops = {c["id_stable"]: c for c in charger(os.path.join(res["dossier"], "manifest.json"))["contenus"]}
        self.assertEqual(ops["cm/dos/dos_exercice_1"]["operation"], "noop")
        self.assertIsNone(ops["cm/dos/dos_exercice_1"]["fichier"])
        self.assertEqual(ops["cm/dos/dos_exercice_2"]["operation"], "update")
        self.assertEqual(ops["cm/dos/dos_exercice_2"]["version_reference"], "ancienne-version")
        self.assertEqual(ops["c-1"]["operation"], "create")
        # Un noop n'embarque pas son fichier.
        self.assertFalse(os.path.exists(os.path.join(res["dossier"], "ingest", "cm", "dos", "dos_exercice_1.json")))

    def test_lot_sans_changement(self):
        self.monter()
        a = outil.analyser_unite(self.ingest, "cm/dos")["elements"]
        reference = {"contenus": {f"{e['type']}|{e['id_stable']}": {"empreinte_source": e["empreinte_source"]} for e in a}}
        chemin_ref = os.path.join(self.tmp, "ref.json")
        sauver(reference, chemin_ref)
        code, res = self.preparer("cm/dos", reference=chemin_ref)
        self.assertEqual(code, 0)
        self.assertEqual(res["statut"], "rien_a_publier")
        self.assertEqual(os.listdir(self.lots), [])

    def test_retrait_exige_motif(self):
        self.monter()
        retraits = os.path.join(self.tmp, "retraits.json")
        sauver([{"type": "exercice", "id_stable": "cm/dos/dos_exercice_1", "motif": ""}], retraits)
        code, res = self.preparer("cm/dos", retraits=retraits)
        self.assertEqual(code, 1)

    def test_retrait_incompatible_avec_une_publication_du_meme_contenu(self):
        self.monter()
        retraits = os.path.join(self.tmp, "retraits.json")
        sauver([{"type": "exercice", "id_stable": "cm/dos/dos_exercice_1", "motif": "sujet retiré"}], retraits)
        code, res = self.preparer("cm/dos", retraits=retraits)  # le contenu serait créé dans le même lot
        self.assertEqual(code, 1)
        self.assertTrue(any("incompatible" in e for e in res["erreurs"]))

    def test_retrait_remplace_l_entree_inchangee(self):
        self.monter()
        a = {e["id_stable"]: e for e in outil.analyser_unite(self.ingest, "cm/dos")["elements"]}
        reference = {"contenus": {f"{e['type']}|{e['id_stable']}": {"empreinte_source": e["empreinte_source"]} for e in a.values()}}
        chemin_ref = os.path.join(self.tmp, "ref.json")
        sauver(reference, chemin_ref)
        retraits = os.path.join(self.tmp, "retraits.json")
        sauver([{"type": "exercice", "id_stable": "cm/dos/dos_exercice_1", "motif": "sujet retiré par l'examinateur"}], retraits)
        code, res = self.preparer("cm/dos", retraits=retraits, reference=chemin_ref)
        self.assertEqual(code, 0, res)
        contenus = charger(os.path.join(res["dossier"], "manifest.json"))["contenus"]
        operations = {c["id_stable"]: c["operation"] for c in contenus}
        self.assertEqual(operations["cm/dos/dos_exercice_1"], "retirer")
        self.assertEqual(sum(1 for c in contenus if c["id_stable"] == "cm/dos/dos_exercice_1"), 1)

    def test_une_absence_n_est_jamais_un_retrait(self):
        # Le contenu connu de la référence mais absent du lot ne produit aucune opération.
        self.monter()
        chemin_ref = os.path.join(self.tmp, "ref.json")
        sauver({"contenus": {"exercice|cm/autre/x": {"empreinte_source": "z"}}}, chemin_ref)
        code, res = self.preparer("cm/dos", reference=chemin_ref)
        self.assertEqual(code, 0)
        ids = [c["id_stable"] for c in charger(os.path.join(res["dossier"], "manifest.json"))["contenus"]]
        self.assertNotIn("cm/autre/x", ids)

    def test_identifiants_de_lot_distincts_si_contenu_different(self):
        self.monter()
        _, r1 = self.preparer("cm/dos")
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(figure="f.png", enonce_intro_markdown="v2"))
        self.valider("cm/dos")
        _, r2 = self.preparer("cm/dos")
        self.assertNotEqual(r1["batch_id"].split("-")[-1], r2["batch_id"].split("-")[-1])


class InventaireTests(Banc):
    def test_inventaire_distingue_suivis_non_suivis_et_base(self):
        repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(repo, "backend"))
        os.rename(self.ingest, os.path.join(repo, "backend", "ingest"))
        self.ingest = os.path.join(repo, "backend", "ingest")
        with open(os.path.join(repo, ".gitignore"), "w") as f:
            f.write("backend/ingest/\n")
        subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "t"], check=True)
        self.ecrire("cm/suivi/suivi_exercice_1.json", exercice())
        self.ecrire("cm/neuf/neuf_exercice_1.json", exercice("1", epreuve_source="neuf.pdf"))
        self.ecrire("cm/neuf/neuf_exercice_2.json", exercice("2", epreuve_source="neuf.pdf"))
        self.ecrire("_gce_staging/neuf/neuf_exercice_1.json", exercice())
        self.ecrire("_audit/x.json", {"x": 1})
        subprocess.run(["git", "-C", repo, "add", "-f", "backend/ingest/cm/suivi/suivi_exercice_1.json"], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "init"], check=True)
        base = os.path.join(self.tmp, "base.json")
        sauver({"exercices": ["neuf.pdf|1"], "cours": [], "items": []}, base)
        sortie = os.path.join(self.tmp, "inv")
        code, res = self.lancer("inventaire", repo, "--sortie", sortie, "--base", base)
        self.assertEqual(code, 0, res)
        self.assertEqual(res["totaux"]["unites_avec_non_suivis"], 1)
        self.assertEqual(res["totaux"]["json_non_suivis"], 2)
        inv = charger(os.path.join(sortie, "inventaire.json"))
        unite = inv["unites"][0]
        self.assertEqual(unite["unite"], "cm/neuf")
        self.assertEqual(unite["statut"], "partiellement_ingere")
        self.assertEqual((unite["elements_en_base_locale"], unite["elements_absents_base_locale"]), (1, 1))
        self.assertTrue(unite["copie_dans_gce_staging"])
        self.assertTrue(os.path.isfile(os.path.join(sortie, "inventaire-unites.tsv")))


if __name__ == "__main__":
    unittest.main()


class ResolutionTests(Banc):
    def lot_pret(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        self.ecrire("cm/dos/dos_exercice_2.json", exercice("2"))
        self.valider("cm/dos")
        code, res = self.preparer("cm/dos")
        self.assertEqual(code, 0, res)
        # Fichier de suivi du poste : ne doit jamais entrer dans l'archive.
        sauver({"etat": "pret_local"}, os.path.join(res["dossier"], "etat.json"))
        return res

    def plan(self, res, **detail_par_id):
        manifeste = charger(os.path.join(res["dossier"], "manifest.json"))
        entrees = []
        for c in manifeste["contenus"]:
            entrees.append({"type": c["type"], "id_stable": c["id_stable"], "operation": c["operation"],
                            "resultat_prevu": detail_par_id.get(c["id_stable"], ("cree", {}))[0],
                            "detail": detail_par_id.get(c["id_stable"], ("cree", {}))[1]})
        chemin = os.path.join(self.tmp, "plan.json")
        sauver({"plan": entrees}, chemin)
        return chemin

    def resoudre(self, res, plan, *argv):
        return self.lancer("resoudre", "--lot", res["dossier"], "--plan", plan, "--par", "moi@poste", *argv)

    def test_ecraser_cite_l_etat_vu_et_la_version_proposee_et_reconstruit_l_archive(self):
        res = self.lot_pret()
        un, deux = "cm/dos/dos_exercice_1", "cm/dos/dos_exercice_2"
        plan = self.plan(res, **{
            un: ("adoption_a_confirmer", {"empreinte_etat_prod_vue": "e" * 64, "diff": ["x"]}),
            deux: ("conflit_etat", {"empreinte_etat_prod_vue": "f" * 64, "version_prod_vue": "v" * 64}),
        })
        code, sortie = self.resoudre(res, plan, "--decision", "ecraser", "--motif", "correction relue")
        self.assertEqual(code, 0, sortie)
        self.assertEqual(sortie["posees"], 2)
        decisions = {d["id_stable"]: d for d in charger(os.path.join(res["dossier"], "approbations.json"))["decisions"]}
        manifeste = {c["id_stable"]: c for c in charger(os.path.join(res["dossier"], "manifest.json"))["contenus"]}
        self.assertEqual(decisions[un]["empreinte_etat_prod_vue"], "e" * 64)
        self.assertEqual(decisions[deux]["version_prod_vue"], "v" * 64)
        for id_stable in (un, deux):
            self.assertEqual(decisions[id_stable]["version_proposee"], manifeste[id_stable]["version_proposee"])
            self.assertEqual(decisions[id_stable]["par"], "moi@poste")
        # L'archive reflète le nouveau fichier et reste cohérente ; etat.json n'y est pas.
        with zipfile.ZipFile(sortie["archive"]) as z:
            noms = z.namelist()
            self.assertIn("approbations.json", noms)
            self.assertNotIn("etat.json", noms)
            sommes = dict(l.split("  ", 1)[::-1] for l in z.read("SHA256SUMS").decode().splitlines())
            self.assertEqual(sommes["approbations.json"], hashlib.sha256(z.read("approbations.json")).hexdigest())
            self.assertNotIn("etat.json", sommes)
        attendu = lire_texte(sortie["archive"] + ".sha256").split()[0]
        self.assertEqual(attendu, hashlib.sha256(lire_octets(sortie["archive"])).hexdigest())

    def test_ecraser_exige_un_motif(self):
        res = self.lot_pret()
        code, _ = self.resoudre(res, self.plan(res), "--decision", "ecraser")
        self.assertEqual(code, 2)

    def test_garder_prod_ne_cite_pas_d_etat_et_ignore_les_conflits_d_identite(self):
        res = self.lot_pret()
        un, deux = "cm/dos/dos_exercice_1", "cm/dos/dos_exercice_2"
        plan = self.plan(res, **{un: ("adoption_a_confirmer", {"empreinte_etat_prod_vue": "e" * 64}),
                                 deux: ("conflit_identite", {"objet_journal_present": False, "journal_objet_pk": 9})})
        code, sortie = self.resoudre(res, plan, "--decision", "garder_prod")
        self.assertEqual(sortie["posees"], 1)
        self.assertEqual(len(sortie["ignorees"]), 1)
        decisions = charger(os.path.join(res["dossier"], "approbations.json"))["decisions"]
        self.assertEqual([d["id_stable"] for d in decisions], [un])
        self.assertNotIn("empreinte_etat_prod_vue", decisions[0])

    def test_recreer_ne_vaut_que_pour_un_contenu_purge_et_exige_des_ids(self):
        res = self.lot_pret()
        un, deux = "cm/dos/dos_exercice_1", "cm/dos/dos_exercice_2"
        plan = self.plan(res, **{un: ("conflit_identite", {"objet_journal_present": False, "journal_objet_pk": 42}),
                                 deux: ("conflit_identite", {"objet_journal_present": True, "journal_objet_pk": 7})})
        code, _ = self.resoudre(res, plan, "--decision", "recreer")
        self.assertEqual(code, 2)
        code, sortie = self.resoudre(res, plan, "--decision", "recreer", "--ids", un, deux)
        self.assertEqual(sortie["posees"], 1)
        decision = charger(os.path.join(res["dossier"], "approbations.json"))["decisions"][0]
        self.assertEqual((decision["id_stable"], decision["objet_pk_absent"]), (un, 42))

    def test_ids_limitent_les_decisions_et_les_decisions_precedentes_sont_conservees(self):
        res = self.lot_pret()
        un, deux = "cm/dos/dos_exercice_1", "cm/dos/dos_exercice_2"
        plan = self.plan(res, **{un: ("adoption_a_confirmer", {"empreinte_etat_prod_vue": "e" * 64}),
                                 deux: ("adoption_a_confirmer", {"empreinte_etat_prod_vue": "f" * 64})})
        self.resoudre(res, plan, "--decision", "garder_prod", "--ids", un)
        self.resoudre(res, plan, "--decision", "ecraser", "--motif", "relu", "--ids", deux)
        decisions = {d["id_stable"]: d["decision"] for d in charger(os.path.join(res["dossier"], "approbations.json"))["decisions"]}
        self.assertEqual(decisions, {un: "garder_prod", deux: "ecraser"})
