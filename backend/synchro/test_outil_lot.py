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


class CampagneTests(Banc):
    """C1 : la relecture indépendante est une condition de `prepare` pour une campagne."""

    def monter(self):
        self.ecrire("cm/dos/dos_exercice_1.json", exercice())
        self.ecrire("cm/dos/dos_cours_a.json", cours())
        self.valider("cm/dos")
        a = outil.analyser_unite(self.ingest, "cm/dos")
        return {(e["type"], e["id_stable"]): e["empreinte_source"] for e in a["elements"]}

    def campagne(self, verdicts, taux=1.0):
        dossier = os.path.join(self.tmp, "campagnes")
        os.makedirs(dossier, exist_ok=True)
        sauver({"verdicts": [{"type": t, "id_stable": i, "empreinte_source": e, "verdict": v, "relecteur": "x"}
                             for (t, i, e, v) in verdicts]}, os.path.join(dossier, "relecture.json"))
        chemin = os.path.join(dossier, "essai.json")
        sauver({"nom": "essai", "relecture": {"taux": taux, "rapport": "relecture.json"}}, chemin)
        return chemin

    def test_une_campagne_de_conversion_ne_livre_que_son_perimetre(self):
        item = lambda n, **x: {"external_id": f"cqc-t-faible-{n}", "theme": "t", "matiere": "Maths",
                               "cursus": [{"examen": "bepc", "serie": ""}], "enonce_markdown": f"q{n}",
                               "corrige_markdown": "c", "type_reponse": "ouverte", **x}
        self.ecrire("_quiz/cm/t.json", [item(0), item(1)])
        self.valider("_quiz/cm/t.json")
        empreintes = {i: e for (t, i), e in
                      ((k, v) for k, v in
                       {(e["type"], e["id_stable"]): e["empreinte_source"]
                        for e in outil.analyser_unite(self.ingest, "_quiz/cm/t.json")["elements"]}.items())}
        dossier = os.path.join(self.tmp, "campagnes")
        os.makedirs(dossier)
        sauver([{"external_id": "cqc-t-faible-0"}], os.path.join(dossier, "props.json"))
        sauver({"verdicts": [{"type": "quiz", "id_stable": "cqc-t-faible-0", "empreinte_source": empreintes["cqc-t-faible-0"],
                              "verdict": "accord", "relecteur": "x"}]}, os.path.join(dossier, "relecture.json"))
        chemin = os.path.join(dossier, "essai.json")
        sauver({"nom": "essai", "relecture": {"taux": 1.0, "rapport": "relecture.json"},
                "conversion": {"propositions": "props.json"}}, chemin)
        code, res = self.preparer("_quiz/cm/t.json", campagne=chemin)
        self.assertEqual(code, 0, res)
        manifeste = charger(os.path.join(res["dossier"], "manifest.json"))
        self.assertEqual([c["id_stable"] for c in manifeste["contenus"]], ["cqc-t-faible-0"])
        self.assertTrue(any("hors du périmètre" in a for a in res["avertissements"]))

    def test_une_campagne_n_ecarte_pas_les_retraits_demandes(self):
        item = lambda n: {"external_id": f"cqc-t-faible-{n}", "theme": "t", "matiere": "Maths",
                          "cursus": [{"examen": "bepc", "serie": ""}], "enonce_markdown": f"q{n}",
                          "corrige_markdown": "c", "type_reponse": "ouverte"}
        self.ecrire("_quiz/cm/t.json", [item(0), item(1)])
        self.valider("_quiz/cm/t.json")
        empreintes = {e["id_stable"]: e["empreinte_source"]
                      for e in outil.analyser_unite(self.ingest, "_quiz/cm/t.json")["elements"]}
        dossier = os.path.join(self.tmp, "campagnes")
        os.makedirs(dossier)
        sauver([{"external_id": "cqc-t-faible-0"}], os.path.join(dossier, "props.json"))
        sauver({"verdicts": [{"type": "quiz", "id_stable": "cqc-t-faible-0", "empreinte_source": empreintes["cqc-t-faible-0"],
                              "verdict": "accord", "relecteur": "x"}]}, os.path.join(dossier, "relecture.json"))
        chemin = os.path.join(dossier, "essai.json")
        sauver({"nom": "essai", "relecture": {"taux": 1.0, "rapport": "relecture.json"},
                "conversion": {"propositions": "props.json"}}, chemin)
        chemin_ref = os.path.join(self.tmp, "ref.json")
        sauver({"contenus": {"quiz|cqc-t-faible-1": {"empreinte_source": empreintes["cqc-t-faible-1"]}}}, chemin_ref)
        retraits = os.path.join(self.tmp, "retraits.json")
        sauver([{"type": "quiz", "id_stable": "cqc-t-faible-1", "motif": "avis enseignant"}], retraits)
        code, res = self.preparer("_quiz/cm/t.json", campagne=chemin, retraits=retraits, reference=chemin_ref)
        self.assertEqual(code, 0, res)
        contenus = charger(os.path.join(res["dossier"], "manifest.json"))["contenus"]
        self.assertEqual({c["id_stable"]: c["operation"] for c in contenus},
                         {"cqc-t-faible-0": "create", "cqc-t-faible-1": "retirer"})

    def test_sans_rapport_le_lot_est_refuse(self):
        self.monter()
        code, res = self.preparer("cm/dos", campagne=self.campagne([]))
        self.assertEqual(code, 1)
        self.assertEqual(res["statut"], "relecture_requise")
        self.assertEqual(os.listdir(self.lots), [])

    def test_relecture_complete_accepte_et_marque_faite(self):
        empreintes = self.monter()
        verdicts = [(t, i, e, "accord") for (t, i), e in empreintes.items()]
        code, res = self.preparer("cm/dos", campagne=self.campagne(verdicts))
        self.assertEqual(code, 0, res)
        manifeste = charger(os.path.join(res["dossier"], "manifest.json"))
        self.assertEqual(manifeste["campagne"]["nom"], "essai")
        self.assertEqual({c["validation"]["relecture_humaine"] for c in manifeste["contenus"]}, {"faite"})

    def test_relecture_perimee_apres_modification(self):
        empreintes = self.monter()
        verdicts = [(t, i, e, "accord") for (t, i), e in empreintes.items()]
        chemin = self.campagne(verdicts)
        self.ecrire("cm/dos/dos_exercice_1.json", exercice(enonce_intro_markdown="modifie apres relecture"))
        self.valider("cm/dos")
        code, res = self.preparer("cm/dos", campagne=chemin)
        self.assertEqual(code, 1)
        self.assertIn("exercice_1", " ".join(res["erreurs"]))

    def test_un_desaccord_bloque_meme_a_taux_reduit(self):
        empreintes = self.monter()
        cles = sorted(empreintes)
        verdicts = [(cles[0][0], cles[0][1], empreintes[cles[0]], "desaccord"),
                    (cles[1][0], cles[1][1], empreintes[cles[1]], "accord")]
        code, res = self.preparer("cm/dos", campagne=self.campagne(verdicts, taux=0.5))
        self.assertEqual(code, 1)
        self.assertIn("désaccord", " ".join(res["erreurs"]))

    def test_taux_reduit_accepte_un_echantillon(self):
        empreintes = self.monter()
        cle = sorted(empreintes)[0]
        verdicts = [(cle[0], cle[1], empreintes[cle], "accord")]
        code, res = self.preparer("cm/dos", campagne=self.campagne(verdicts, taux=0.5))
        self.assertEqual(code, 0, res)

    def test_sans_campagne_rien_ne_change(self):
        self.monter()
        code, res = self.preparer("cm/dos")
        self.assertEqual(code, 0, res)
        manifeste = charger(os.path.join(res["dossier"], "manifest.json"))
        self.assertIsNone(manifeste["campagne"])
        self.assertEqual({c["validation"]["relecture_humaine"] for c in manifeste["contenus"]}, {"non_requise"})


class ReecritureQuizTests(Banc):
    def quiz(self):
        item = {"external_id": "cqc-t-faible-0", "theme": "t", "matiere": "Maths", "cursus": [{"examen": "bepc", "serie": ""}],
                "enonce_markdown": "Combien font $2+2$ ?", "corrige_markdown": "Quatre.", "type_reponse": "ouverte"}
        self.ecrire("_quiz/cm/t.json", [item])
        return outil._empreinte_texte_item(item["enonce_markdown"], item["corrige_markdown"])

    def proposition(self, **extra):
        p = {"external_id": "cqc-t-faible-0", "corrige_markdown": "Quatre, car $2+2=4$.", "reponse_correcte": "b",
             "choix": [{"lettre": "a", "texte": "3"}, {"lettre": "b", "texte": "4"}, {"lettre": "c", "texte": "5"}]}
        p.update(extra)
        chemin = os.path.join(self.tmp, "props.json")
        sauver([p], chemin)
        return chemin

    def originaux(self, sha):
        chemin = os.path.join(self.tmp, "orig.json")
        sauver({"1": {"external_id": "cqc-t-faible-0", "sha256": sha}}, chemin)
        return chemin

    def chemin_item(self):
        return os.path.join(self.ingest, "_quiz", "cm", "t.json")

    def test_simulation_n_ecrit_rien(self):
        sha = self.quiz()
        avant = lire_octets(self.chemin_item())
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(),
                                "--originaux", self.originaux(sha))
        self.assertEqual(code, 0, res)
        self.assertEqual(res["compteurs"], {"a_convertir": 1})
        self.assertEqual(lire_octets(self.chemin_item()), avant)

    def test_conversion_ecrit_les_champs_et_rien_d_autre(self):
        sha = self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(),
                                "--originaux", self.originaux(sha), "--appliquer")
        self.assertEqual(code, 0, res)
        item = charger(self.chemin_item())[0]
        self.assertEqual((item["type_reponse"], item["reponse_correcte"]), ("qcm", "b"))
        self.assertEqual(item["theme"], "t")
        self.assertEqual(item["cursus"], [{"examen": "bepc", "serie": ""}])
        self.assertEqual(item["enonce_markdown"], "Combien font $2+2$ ?")

    def test_empreinte_divergente_est_ignoree(self):
        self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(),
                                "--originaux", self.originaux("0" * 64), "--appliquer")
        self.assertEqual(res["compteurs"], {"empreinte_divergente": 1})
        self.assertEqual(charger(self.chemin_item())[0]["type_reponse"], "ouverte")

    def test_rejoue_est_idempotent(self):
        sha = self.quiz()
        argv = ["reecrire-quiz", self.ingest, "--propositions", self.proposition(),
                "--originaux", self.originaux(sha), "--appliquer"]
        self.lancer(*argv)
        code, res = self.lancer(*argv)
        self.assertEqual(res["compteurs"], {"deja_qcm": 1})
        self.assertEqual(res["fichiers_ecrits"], [])

    def test_corriger_un_qcm_deja_converti(self):
        sha = self.quiz()
        self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(), "--originaux", self.originaux(sha), "--appliquer")
        converti = charger(self.chemin_item())[0]
        sha2 = outil._empreinte_texte_item(converti["enonce_markdown"], converti["corrige_markdown"])
        argv = ["reecrire-quiz", self.ingest, "--propositions", self.proposition(corrige_markdown="Quatre, sans notion hors programme."),
                "--originaux", self.originaux(sha2), "--corriger"]
        code, res = self.lancer(*argv)
        self.assertEqual((code, res["compteurs"]), (0, {"a_corriger": 1}))
        self.assertIn("car $2+2=4$", charger(self.chemin_item())[0]["corrige_markdown"])  # simulation : rien n'est ecrit
        code, res = self.lancer(*argv, "--appliquer")
        self.assertEqual(res["compteurs"], {"corrige": 1})
        self.assertEqual(charger(self.chemin_item())[0]["corrige_markdown"], "Quatre, sans notion hors programme.")
        code, res = self.lancer(*argv, "--appliquer")  # rejoue : le contenu n'est plus celui qui a ete relu
        self.assertEqual(res["compteurs"], {"empreinte_divergente": 1})

    def test_corriger_refuse_une_question_encore_ouverte(self):
        sha = self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(),
                                "--originaux", self.originaux(sha), "--corriger", "--appliquer")
        self.assertEqual(res["compteurs"], {"pas_encore_qcm": 1})
        self.assertEqual(charger(self.chemin_item())[0]["type_reponse"], "ouverte")

    def test_corriger_exige_les_originaux(self):
        self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(), "--corriger")
        self.assertEqual(code, 2)
        self.assertEqual(res["statut"], "usage")

    def interdits(self):
        chemin = os.path.join(self.tmp, "interdits.json")
        sauver({"notions": [
            {"id": "equation-cartesienne", "gravite": "bloquant", "motif": "x", "motifs": ["cart[ée]sienne"]},
            {"id": "niveau-cite", "gravite": "alerte", "motif": "x", "motifs": ["Seconde"]}]}, chemin)
        return chemin

    def test_notion_hors_programme_refusee(self):
        sha = self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions",
                                self.proposition(corrige_markdown="Une équation cartésienne de la droite."),
                                "--originaux", self.originaux(sha), "--interdits", self.interdits(), "--appliquer")
        self.assertEqual(code, 1)
        self.assertEqual(res["compteurs"], {"proposition_invalide": 1})
        self.assertEqual(charger(self.chemin_item())[0]["type_reponse"], "ouverte")

    def test_alerte_signalee_sans_bloquer(self):
        sha = self.quiz()
        sortie = os.path.join(self.tmp, "rapport.json")
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions",
                                self.proposition(corrige_markdown="Notion de Seconde, donc $2+2=4$."),
                                "--originaux", self.originaux(sha), "--interdits", self.interdits(), "--sortie", sortie)
        self.assertEqual((code, res["compteurs"]), (0, {"a_convertir": 1}))
        self.assertIn("niveau-cite", charger(sortie)["items"][0]["alertes"][0])

    def test_proposition_invalide_refusee(self):
        sha = self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest, "--propositions", self.proposition(reponse_correcte="z"),
                                "--originaux", self.originaux(sha), "--appliquer")
        self.assertEqual(code, 1)
        self.assertEqual(res["compteurs"], {"proposition_invalide": 1})
        self.assertEqual(charger(self.chemin_item())[0]["type_reponse"], "ouverte")

    def test_item_introuvable(self):
        sha = self.quiz()
        code, res = self.lancer("reecrire-quiz", self.ingest,
                                "--propositions", self.proposition(external_id="cqc-autre-0"), "--originaux", self.originaux(sha))
        self.assertEqual(code, 1)
        self.assertEqual(res["compteurs"], {"introuvable": 1})


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
