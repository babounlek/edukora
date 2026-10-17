"""
Validateur autonome d'un lot de quiz GCE (items CompetenceItem en anglais) avant ingestion.

Usage :
    D:\\edukora\\venv\\Scripts\\python.exe valider_quiz_gce.py <fichier_batch.json> <dossier_du_lot>

`<fichier_batch.json>` = la tranche de requêtes de sélection (competence, cible, materiel_reference) confiée à l'agent ;
`<dossier_du_lot>` = où il a écrit `<competence_slug>.json` (un tableau d'items par compétence) et les PNG éventuels.
Code de sortie 0 = aucun défaut bloquant (« warn » = à relire). Reprend les exigences de quiz.ingestion
et du skill concepteur-quiz-competence : forme des items, QCM cohérents, répartition de difficulté, moitié de QCM,
autonomie, non-copie du matériel de référence, figures, LaTeX.
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DIFFS = ("FAIBLE", "MOYENNE", "ELEVEE")
PLACEHOLDER = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
RENVOIS = re.compile(
    r"\b(previous question|question above|part [A-Z]\b|figure above|diagram above|as above|"
    r"the figure below|the diagram below|shown below|in the table above|from part|earlier result)\b", re.I)


def slug(texte):
    s = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def shingles(texte, n=9):
    mots = re.findall(r"[a-z0-9]+", texte.lower())
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


def dollars_desequilibres(t):
    return t.replace("\\$", "").count("$") % 2 == 1


def valider_fichier(demande, chemin, dossier):
    erreurs, warns = [], []
    nom = chemin.name
    try:
        items = json.loads(chemin.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"{nom}: JSON illisible ({e})"], []
    if not isinstance(items, list) or not items:
        return [f"{nom}: doit contenir un tableau non vide"], []

    cible = demande["cible"]
    if len(items) != cible["nombre_items"]:
        erreurs.append(f"{nom}: {len(items)} item(s), {cible['nombre_items']} attendu(s)")
    repartition = Counter(i.get("difficulte_estimee") for i in items)
    for d in DIFFS:
        if repartition.get(d, 0) != cible["repartition_difficulte"].get(d, 0):
            warns.append(f"{nom}: difficulté {d} = {repartition.get(d, 0)}, cible {cible['repartition_difficulte'].get(d, 0)}")

    reference = set()
    for ref in demande.get("materiel_reference", []):
        reference |= shingles(ref.get("enonce_markdown", "")) | shingles(ref.get("corrige_markdown", ""))
    ids_exercices = {r.get("exercise_id") for r in demande.get("materiel_reference", [])}

    vus, nb_qcm, fichiers_figures, references = set(), 0, set(), set()
    slug_comp = slug(demande["competence"])
    for idx, it in enumerate(items):
        e = f"{nom} item#{idx}"
        for cle in ("external_id", "theme", "matiere", "cursus", "enonce_markdown", "corrige_markdown",
                    "difficulte_estimee", "type_reponse", "source_exercises"):
            if it.get(cle) in (None, "", []):
                erreurs.append(f"{e}: clé manquante ou vide : {cle}")
        if it.get("theme") != demande["competence"]:
            erreurs.append(f"{e}: theme doit être exactement {demande['competence']!r} (reçu {it.get('theme')!r})")
        if it.get("matiere") != demande["matiere"]:
            erreurs.append(f"{e}: matiere doit valoir {demande['matiere']!r}")
        if it.get("cursus") != demande["cursus"]:
            erreurs.append(f"{e}: cursus doit être recopié tel quel depuis la requête")
        eid = it.get("external_id", "")
        if not re.fullmatch(rf"cqc-{re.escape(slug_comp)}-(faible|moyenne|elevee)-\d+", eid):
            erreurs.append(f"{e}: external_id attendu cqc-{slug_comp}-<difficulte>-<index> (reçu {eid!r})")
        if eid in vus:
            erreurs.append(f"{e}: external_id dupliqué")
        vus.add(eid)
        if it.get("difficulte_estimee") not in DIFFS:
            erreurs.append(f"{e}: difficulte_estimee invalide ({it.get('difficulte_estimee')!r}), attendu FAIBLE|MOYENNE|ELEVEE")
        elif eid and it["difficulte_estimee"].lower() not in eid:
            warns.append(f"{e}: la difficulté de l'external_id ne suit pas difficulte_estimee")
        if not set(it.get("source_exercises") or []) <= ids_exercices:
            erreurs.append(f"{e}: source_exercises doit contenir des exercise_id du matériel de référence")
        if it.get("savoir_officiel"):
            erreurs.append(f"{e}: savoir_officiel doit être omis ou null pour le GCE")

        for champ in ("enonce_markdown", "corrige_markdown"):
            t = it.get(champ) or ""
            if re.search(r"[\t\x08\x0c\x07\x0b]", t):
                erreurs.append(f"{e} {champ}: caractère de contrôle (backslash LaTeX non doublé ?)")
            if re.search(r"\$[^$\n]*\n(e|eq|u|otin|abla)", t):
                erreurs.append(f"{e} {champ}: saut de ligne dans une formule suivi de e/eq/u (\\ne, \\nu cassé ?)")
            if dollars_desequilibres(t):
                erreurs.append(f"{e} {champ}: nombre impair de $")
            if "\u2014" in t or "\u2013" in t:
                warns.append(f"{e} {champ}: tiret cadratin/demi-cadratin")
            sans_latex = re.sub(r"\\[A-Za-z]+", " ", t)  # \le, \ne... ne sont pas des mots
            if re.search(r"\b(le|la|les|des|est|une|pour|dans)\b", sans_latex) and not re.search(r"\b(the|is|of|and|to|a)\b", sans_latex):
                warns.append(f"{e} {champ}: texte qui semble français (le lot est en anglais)")
            for ref in PLACEHOLDER.findall(t):
                references.add(ref)
                if not (dossier / ref).is_file():
                    erreurs.append(f"{e} {champ}: image introuvable {ref}")
        corr = it.get("corrige_markdown") or ""
        if not corr.lstrip().startswith("### Method reminder") or "### Solution" not in corr:
            erreurs.append(f"{e}: corrige_markdown doit commencer par « ### Method reminder » puis contenir « ### Solution »")
        elif corr.index("### Method reminder") > corr.index("### Solution"):
            erreurs.append(f"{e}: « ### Method reminder » doit précéder « ### Solution »")
        if RENVOIS.search(it.get("enonce_markdown") or "") and not PLACEHOLDER.search(it.get("enonce_markdown") or ""):
            warns.append(f"{e}: l'énoncé semble renvoyer à un support voisin (autonomie ?)")
        # non-copie : 9 mots consécutifs identiques à un énoncé ou corrigé de référence
        commun = shingles(it.get("enonce_markdown") or "") & reference
        if commun:
            erreurs.append(f"{e}: énoncé trop proche du matériel de référence (ex. « {next(iter(commun))} »)")

        figs = it.get("figures") or []
        for f in figs:
            fichiers_figures.add(f.get("fichier"))
            if not f.get("fichier") or not (dossier / f["fichier"]).is_file():
                erreurs.append(f"{e}: figure introuvable ({f.get('fichier')!r})")
            if f.get("origine_figure") not in ("enonce", "corrige"):
                erreurs.append(f"{e}: origine_figure doit valoir enonce|corrige")

        typ = it.get("type_reponse")
        if typ == "QCM":
            nb_qcm += 1
            choix = it.get("choix") or []
            lettres = [c.get("lettre") for c in choix if isinstance(c, dict)]
            if len(choix) < 4 or len(set(lettres)) != len(lettres):
                erreurs.append(f"{e}: QCM avec au moins 4 choix de lettres distinctes")
            if it.get("reponse_correcte") not in lettres:
                erreurs.append(f"{e}: reponse_correcte {it.get('reponse_correcte')!r} absente des choix")
            textes = [str(c.get("texte", "")).strip().lower() for c in choix if isinstance(c, dict)]
            if len(set(textes)) != len(textes) or any(not t for t in textes):
                erreurs.append(f"{e}: choix vides ou identiques")
        elif typ == "OUVERTE":
            if it.get("choix") or it.get("reponse_correcte"):
                erreurs.append(f"{e}: OUVERTE avec choix/reponse_correcte non vides")
        else:
            erreurs.append(f"{e}: type_reponse doit valoir QCM ou OUVERTE")

    if nb_qcm * 2 < len(items):
        erreurs.append(f"{nom}: {nb_qcm}/{len(items)} QCM, au moins la moitié exigée (sinon justifier dans le rapport)")
    for ref in references - fichiers_figures:
        erreurs.append(f"{nom}: placeholder {ref} sans entrée dans figures")
    for f in fichiers_figures - references - {None}:
        erreurs.append(f"{nom}: figure {f} jamais référencée par un placeholder")
    return erreurs, warns


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dossier = Path(sys.argv[2])
    erreurs, warns = [], []
    attendus = set()
    for demande in batch:
        chemin = dossier / f"{slug(demande['competence'])}.json"
        attendus.add(chemin.name)
        if not chemin.is_file():
            erreurs.append(f"fichier manquant : {chemin.name} (compétence {demande['competence']!r})")
            continue
        er, wa = valider_fichier(demande, chemin, dossier)
        erreurs += er
        warns += wa
    for extra in sorted(p.name for p in dossier.glob("*.json") if p.name not in attendus):
        warns.append(f"fichier inattendu : {extra}")
    print(f"{len(batch)} compétence(s) attendue(s)")
    for w in warns:
        print("warn ", w)
    for e in erreurs:
        print("ERREUR", e)
    print("OK" if not erreurs else f"ECHEC ({len(erreurs)} erreur(s))")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
