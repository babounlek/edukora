\
# -*- coding: utf-8 -*-
import json, os, glob, re, sys

DIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-c-d-anglais-2012-cameroun"

errors = []
warnings = []

# ---- 0. no temp files ----
tmp_files = [f for f in os.listdir(DIR) if f.startswith("_tmp")]
if tmp_files:
    errors.append(f"Fichiers temporaires restants: {tmp_files}")
else:
    print("OK: aucun fichier temporaire restant (hors sous-dossier _tmp_pages)")

# ---- 1. load exercises ----
ex_files = sorted(glob.glob(os.path.join(DIR, "*_exercice_*.json")))
print("Exercice files:", [os.path.basename(f) for f in ex_files])
if len(ex_files) != 4:
    errors.append(f"Nombre d'exercices != 4 : {len(ex_files)}")

all_cours_ids_referenced = set()
all_rappel_count = 0
all_question_count = 0

REQUIRED_EX_FIELDS = ["epreuve_source","numero_exercice","matiere","serie","examen","origine",
    "etablissement","annee","duree_epreuve","coefficient","points","figures",
    "enonce_intro_markdown","questions","mots_cles_recherche","incertitudes","statut"]

REQUIRED_Q_FIELDS = ["numero","enonce_markdown","corrige_markdown","themes","difficulte_estimee",
    "type_reponse","choix","reponse_correcte","rappels_de_methode"]

for ef in ex_files:
    data = json.load(open(ef, encoding="utf-8"))
    base = os.path.basename(ef)
    for field in REQUIRED_EX_FIELDS:
        if field not in data:
            errors.append(f"{base}: champ manquant '{field}'")
    if data.get("statut") != "brouillon":
        errors.append(f"{base}: statut != brouillon")
    qs = data.get("questions", [])
    all_question_count += len(qs)
    for q in qs:
        for field in REQUIRED_Q_FIELDS:
            if field not in q:
                errors.append(f"{base} q{q.get('numero')}: champ manquant '{field}'")
        cm = q.get("corrige_markdown", "")
        # template checks
        if "### Rappel de méthode" not in cm and q.get("rappels_de_methode"):
            errors.append(f"{base} q{q.get('numero')}: rappels_de_methode present mais pas de titre '### Rappel de méthode' dans corrige_markdown")
        if "### Corrigé" not in cm:
            errors.append(f"{base} q{q.get('numero')}: pas de titre '### Corrigé' dans corrige_markdown")
        # forbidden em dash character
        if "—" in cm or "—" in q.get("enonce_markdown",""):
            errors.append(f"{base} q{q.get('numero')}: tiret cadratin (em dash) détecté")
        # qcm check
        if q.get("type_reponse") == "qcm":
            choix = q.get("choix", [])
            rc = q.get("reponse_correcte", "")
            if not rc:
                errors.append(f"{base} q{q.get('numero')}: qcm sans reponse_correcte")
            else:
                if choix and isinstance(choix[0], dict):
                    lettres = [c["lettre"] for c in choix]
                    if rc not in lettres:
                        errors.append(f"{base} q{q.get('numero')}: reponse_correcte '{rc}' absente des lettres {lettres}")
                elif choix:
                    if rc not in choix:
                        errors.append(f"{base} q{q.get('numero')}: reponse_correcte '{rc}' absente de choix {choix}")
        # rappels verbatim check
        for r in q.get("rappels_de_methode", []):
            all_rappel_count += 1
            all_cours_ids_referenced.add(r.get("cours_id"))
            if r.get("contenu_markdown") not in cm:
                errors.append(f"{base} q{q.get('numero')} rappel {r.get('id')}: contenu_markdown NON verbatim dans corrige_markdown")
            if r.get("cours_genere") is not True:
                warnings.append(f"{base} q{q.get('numero')} rappel {r.get('id')}: cours_genere != true")
            if not r.get("cours_id"):
                errors.append(f"{base} q{q.get('numero')} rappel {r.get('id')}: cours_id manquant")
    # figures placeholder check
    figs = data.get("figures", [])
    fig_ids = {f["id"] for f in figs}
    full_text = data.get("enonce_intro_markdown","") + "".join(q.get("enonce_markdown","")+q.get("corrige_markdown","") for q in qs)
    placeholders = set(re.findall(r"!\[(fig-\d+)\]", full_text))
    if placeholders - fig_ids:
        errors.append(f"{base}: placeholders orphelins {placeholders - fig_ids}")

print(f"Total questions: {all_question_count}")
print(f"Total rappels: {all_rappel_count}")
print(f"Cours ids referenced: {len(all_cours_ids_referenced)}")

# ---- 2. load courses ----
cours_files = sorted(glob.glob(os.path.join(DIR, "*_cours_*.json")))
print("Cours files count:", len(cours_files))

cours_by_id = {}
for cf in cours_files:
    data = json.load(open(cf, encoding="utf-8"))
    base = os.path.basename(cf)
    cid = data.get("cours_id")
    if cid in cours_by_id:
        errors.append(f"cours_id dupliqué: {cid}")
    cours_by_id[cid] = data
    # meta / source required
    if "meta" not in data or "titre" not in data.get("meta", {}):
        errors.append(f"{base}: meta.titre manquant")
    if "source" not in data:
        errors.append(f"{base}: source manquante")
    else:
        src = data["source"]
        for f in ["epreuve_id","epreuve_titre","exercice_numero","rappel_id"]:
            if src.get(f) in (None, ""):
                if f != "epreuve_id" and f != "epreuve_titre":
                    pass
                if src.get(f) is None and f == "rappel_id":
                    errors.append(f"{base}: source.rappel_id manquant")
    sections = data.get("sections", [])
    if sections:
        # FULL course: check 7 sections structure
        types = [s["type"] for s in sections]
        expected_types = ["accroche","prerequis","regle","exemple_resolu","erreurs_classiques","exercices_application","synthese"]
        if types != expected_types:
            errors.append(f"{base}: structure sections incorrecte: {types}")
        for s in sections:
            if s["type"] == "prerequis" and len(s.get("items", [])) == 0:
                errors.append(f"{base}: prerequis vide")
            if s["type"] == "erreurs_classiques":
                n = len(s.get("items", []))
                if not (2 <= n <= 4):
                    errors.append(f"{base}: erreurs_classiques a {n} items (attendu 2-4)")
                for it in s.get("items", []):
                    for f in ["erreur_markdown","pourquoi_faux","correction_markdown"]:
                        if f not in it:
                            errors.append(f"{base}: erreurs_classiques item manque champ {f}")
            if s["type"] == "exercices_application":
                n = len(s.get("items", []))
                if n != 3:
                    errors.append(f"{base}: exercices_application a {n} items (attendu exactement 3)")
                diffs = [it.get("difficulte") for it in s.get("items", [])]
                for it in s.get("items", []):
                    for f in ["numero","difficulte","enonce_markdown","solution_markdown"]:
                        if f not in it:
                            errors.append(f"{base}: exercice_application item manque champ {f}")
            if s["type"] == "synthese":
                n = len(s.get("items_markdown", []))
                if not (4 <= n <= 6):
                    errors.append(f"{base}: synthese a {n} items (attendu 4-6)")
            if s["type"] == "exemple_resolu":
                if not s.get("etapes"):
                    errors.append(f"{base}: exemple_resolu sans etapes")
                if "conclusion_markdown" not in s:
                    errors.append(f"{base}: exemple_resolu sans conclusion_markdown")
    else:
        # skeleton: must have empty sections, but meta.titre + source.rappel_id present
        pass
    if data.get("meta", {}).get("statut") != "brouillon":
        errors.append(f"{base}: meta.statut != brouillon")

# ---- 3. cross-check cours_id referenced in exercises vs files present ----
missing_cours = all_cours_ids_referenced - set(cours_by_id.keys())
if missing_cours:
    errors.append(f"cours_id référencés dans exercices mais fichier absent: {missing_cours}")

extra_cours = set(cours_by_id.keys()) - all_cours_ids_referenced
if extra_cours:
    warnings.append(f"cours_id présents mais non référencés par un rappel: {extra_cours}")

print(f"Total cours files: {len(cours_files)} (full: {sum(1 for c in cours_by_id.values() if c['sections'])}, skeleton: {sum(1 for c in cours_by_id.values() if not c['sections'])})")

# ---- report ----
print("\n=== WARNINGS ===")
for w in warnings:
    print("WARN:", w)

print("\n=== ERRORS ===")
for e in errors:
    print("ERROR:", e)

if errors:
    print(f"\nVALIDATION FAILED: {len(errors)} error(s)")
    sys.exit(1)
else:
    print("\nVALIDATION PASSED")
