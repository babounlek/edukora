# -*- coding: utf-8 -*-
import json, os, re, glob

OUTDIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-blanc-d-ti-physique-2025-cameroun"

errors = []
warnings = []

ex_files = sorted(glob.glob(os.path.join(OUTDIR, "*_exercice_*.json")))
cours_files = sorted(glob.glob(os.path.join(OUTDIR, "*_cours_*.json")))

print(f"Found {len(ex_files)} exercise files, {len(cours_files)} cours files.")

# Load all cours ids
cours_ids = set()
cours_by_id = {}
for cf in cours_files:
    with open(cf, encoding="utf-8") as f:
        data = json.load(f)
    cid = data.get("cours_id")
    if not cid:
        errors.append(f"{cf}: missing cours_id")
        continue
    if cid in cours_ids:
        errors.append(f"{cf}: duplicate cours_id {cid}")
    cours_ids.add(cid)
    cours_by_id[cid] = (cf, data)

total_questions = 0
total_figures = 0
total_rappels = 0

for ef in ex_files:
    with open(ef, encoding="utf-8") as f:
        data = json.load(f)
    # basic required fields
    for field in ["epreuve_source","numero_exercice","matiere","serie","examen","origine",
                  "etablissement","annee","duree_epreuve","coefficient","points","figures",
                  "enonce_intro_markdown","questions","mots_cles_recherche","incertitudes","statut"]:
        if field not in data:
            errors.append(f"{ef}: missing field {field}")

    # figures check
    fig_ids = set()
    for fig in data.get("figures", []):
        fig_ids.add(fig["id"])
        total_figures += 1
        fpath = os.path.join(OUTDIR, fig["fichier"])
        if not os.path.isfile(fpath):
            errors.append(f"{ef}: figure file missing on disk: {fig['fichier']}")

    for q in data.get("questions", []):
        total_questions += 1
        qnum = q["numero"]
        corrige = q.get("corrige_markdown", "")
        enonce = q.get("enonce_markdown", "")

        # placeholder check within corrige+enonce+intro
        combined_text = data.get("enonce_intro_markdown","") + "\n" + enonce + "\n" + corrige
        placeholders = set(re.findall(r"!\[(fig-\d+)\]\([^)]+\)", combined_text))
        for ph in placeholders:
            if ph not in fig_ids:
                errors.append(f"{ef} q{qnum}: placeholder {ph} not in figures[] ids {fig_ids}")

        # QCM check
        if q.get("type_reponse") == "qcm":
            choix = q.get("choix", [])
            rc = q.get("reponse_correcte", "")
            if not rc:
                errors.append(f"{ef} q{qnum}: QCM with empty reponse_correcte")
            else:
                if choix and isinstance(choix[0], dict):
                    valid = {c["lettre"] for c in choix}
                else:
                    valid = set(choix)
                if rc not in valid:
                    errors.append(f"{ef} q{qnum}: reponse_correcte '{rc}' not in choix {valid}")

        # rappels verbatim check + cours_id validity
        for r in q.get("rappels_de_methode", []):
            total_rappels += 1
            contenu = r["contenu_markdown"]
            if contenu not in corrige:
                errors.append(f"{ef} q{qnum}: rappel contenu_markdown NOT found verbatim in corrige_markdown (id={r['id']})")
            cid = r.get("cours_id")
            if not cid:
                errors.append(f"{ef} q{qnum}: rappel {r['id']} has no cours_id")
            elif cid not in cours_ids:
                errors.append(f"{ef} q{qnum}: rappel {r['id']} references unknown cours_id {cid}")
            if r.get("cours_genere") is not True:
                warnings.append(f"{ef} q{qnum}: rappel {r['id']} cours_genere is not True")

    # JSON validity already implied by successful load
print(f"\nTotal questions: {total_questions}")
print(f"Total figures referenced: {total_figures}")
print(f"Total rappels: {total_rappels}")
print(f"Total cours files: {len(cours_files)}")

# check figure files on disk vs referenced, and no orphan placeholders overall
png_files = set(os.path.basename(p) for p in glob.glob(os.path.join(OUTDIR, "*.png")))
print(f"PNG files on disk: {sorted(png_files)}")

print("\n=== ERRORS ===")
if errors:
    for e in errors:
        print("ERROR:", e)
else:
    print("No errors.")

print("\n=== WARNINGS ===")
for w in warnings:
    print("WARNING:", w)

print("\nDONE" if not errors else "\nFAILED")
