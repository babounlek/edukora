"""
Validateur autonome d'un lot de cours GCE (JSON mode cours, en anglais) avant ingestion.

Usage :
    D:\\edukora\\venv\\Scripts\\python.exe valider_cours_gce.py <tranche.json> <dossier_du_lot>

`<tranche.json>` = la liste des thèmes confiés à l'agent (matiere, theme, epreuve_source, references) ;
`<dossier_du_lot>` = où il a écrit `<cours_id>.json` (un objet par thème).
Code de sortie 0 = aucun défaut bloquant (« warn » = à relire). Reprend le contrat de catalog.ingestion.ingest_cours :
champs obligatoires, 7 sections dans l'ordre, une seule étiquette (le thème), LaTeX, anglais, non-copie des références.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ORDRE = ["accroche", "prerequis", "regle", "exemple_resolu", "erreurs_classiques", "exercices_application", "synthese"]
# code GCE_* -> (libellé anglais attendu dans meta.matiere, forme courte des identifiants `cours-gce-<court>-<thème>`).
# Toutes les matières du GCE Board (catalog.models.CODES_OFFICIELS_GCE) : « Pure Mathematics » seul n'existe pas.
_MATIERES_COURT = {
    "GCE_MATHS": ("Mathematics", "maths"), "GCE_ADD_MATHS": ("Additional Mathematics", "add-maths"),
    "GCE_PM_MECHANICS": ("Pure Mathematics with Mechanics", "pm-mechanics"),
    "GCE_PM_STATISTICS": ("Pure Mathematics with Statistics", "pm-statistics"),
    "GCE_FURTHER_MATHS": ("Further Mathematics", "further-maths"),
    "GCE_PHYSICS": ("Physics", "physics"), "GCE_CHEMISTRY": ("Chemistry", "chemistry"), "GCE_BIOLOGY": ("Biology", "biology"),
    "GCE_HUMAN_BIOLOGY": ("Human Biology", "human-biology"), "GCE_GEOLOGY": ("Geology", "geology"),
    "GCE_COMPUTER_SCI": ("Computer Science", "computer-science"), "GCE_ICT": ("ICT", "ict"),
    "GCE_ECONOMICS": ("Economics", "economics"), "GCE_COMMERCE": ("Commerce", "commerce"), "GCE_ACCOUNTING": ("Accounting", "accounting"),
    "GCE_GEOGRAPHY": ("Geography", "geography"), "GCE_HISTORY": ("History", "history"),
    "GCE_CITIZENSHIP": ("Citizenship Education", "citizenship"), "GCE_RELIGION": ("Religious Studies", "religious-studies"),
    "GCE_PHILOSOPHY": ("Philosophy", "philosophy"), "GCE_LOGIC": ("Logic", "logic"),
    "GCE_ENGLISH": ("English Language", "english"), "GCE_LITERATURE": ("Literature in English", "literature"),
    "GCE_FRENCH": ("French", "french"), "GCE_SBE_FRENCH": ("Special Bilingual Education French", "sbe-french"),
    "GCE_FOOD_NUTRITION": ("Food and Nutrition", "food-nutrition"),
}
MATIERES = {code: libelle for code, (libelle, _) in _MATIERES_COURT.items()}
COURT = {code: court for code, (_, court) in _MATIERES_COURT.items()}
DIFFS = ["facile", "moyen", "approfondissement"]
RENVOIS = re.compile(r"\b(previous question|question above|figure above|diagram above|as above|the figure below|the diagram below|shown below)\b", re.I)


def slug(texte):
    s = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def shingles(texte, n=9):
    mots = re.findall(r"[a-z0-9]+", texte.lower())
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


def textes(obj):
    """Toutes les chaînes d'un objet JSON imbriqué."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from textes(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from textes(v)


def verifier_texte(t, e, erreurs, warns):
    if re.search(r"[\t\x08\x0c\x07\x0b]", t):
        erreurs.append(f"{e}: caractère de contrôle (backslash LaTeX non doublé ?)")
    if re.search(r"\$[^$\n]*\n(e|eq|u|otin|abla)", t):
        erreurs.append(f"{e}: saut de ligne dans une formule suivi de e/eq/u (\\ne, \\nu cassé ?)")
    if t.replace("\\$", "").count("$") % 2 == 1:
        erreurs.append(f"{e}: nombre impair de $")
    if "\u2014" in t or "\u2013" in t:
        erreurs.append(f"{e}: tiret cadratin/demi-cadratin")
    sans_latex = re.sub(r"\\[A-Za-z]+", " ", t)
    if re.search(r"\b(le|la|les|des|est|une|pour|dans)\b", sans_latex) and not re.search(r"\b(the|is|of|and|to|a)\b", sans_latex):
        warns.append(f"{e}: texte qui semble français (le lot est en anglais)")
    if re.search(r"!\[[^\]]*\]\(", t):
        erreurs.append(f"{e}: image interdite (aucune figure dans les cours GCE)")
    if RENVOIS.search(t):
        warns.append(f"{e}: renvoi à un support voisin (autonomie ?)")


def valider(demande, chemin, vus_ids, vus_titres):
    erreurs, warns = [], []
    nom = chemin.name
    try:
        d = json.loads(chemin.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"{nom}: JSON illisible ({exc})"], []
    if not isinstance(d, dict):
        return [f"{nom}: doit contenir UN objet JSON (pas un tableau)"], []

    code = demande["matiere_code"]
    attendu_id = f"cours-gce-{COURT[code]}-{slug(demande['theme'])}"
    if d.get("cours_id") != attendu_id:
        erreurs.append(f"{nom}: cours_id attendu {attendu_id!r} (reçu {d.get('cours_id')!r})")
    if d.get("cours_id") in vus_ids:
        erreurs.append(f"{nom}: cours_id dupliqué")
    vus_ids.add(d.get("cours_id"))

    meta = d.get("meta") or {}
    for cle in ("titre", "matiere", "pays", "serie", "sous_theme", "duree_estimee_min", "tags"):
        if meta.get(cle) in (None, "", []):
            erreurs.append(f"{nom}: meta.{cle} manquant ou vide")
    if meta.get("matiere") != MATIERES[code]:
        erreurs.append(f"{nom}: meta.matiere doit valoir {MATIERES[code]!r}")
    if meta.get("pays") != "cm":
        erreurs.append(f"{nom}: meta.pays doit valoir 'cm'")
    serie_attendue = demande.get("serie", "GCE O/L")  # « GCE A/L » pour une tranche Advanced Level
    if meta.get("serie") != serie_attendue:
        erreurs.append(f"{nom}: meta.serie doit valoir {serie_attendue!r} (sinon le cours n'est rattaché à aucun cursus)")
    if meta.get("tags") != [demande["theme"]]:
        erreurs.append(f"{nom}: meta.tags doit valoir exactement [{demande['theme']!r}]")
    if meta.get("savoir_officiel"):
        erreurs.append(f"{nom}: savoir_officiel doit être null")
    titre = (meta.get("titre") or "").strip()
    if titre.lower() == demande["theme"].lower():
        erreurs.append(f"{nom}: le titre ne doit pas être le thème nu")
    if titre.lower() in vus_titres:
        erreurs.append(f"{nom}: titre dupliqué dans le lot")
    vus_titres.add(titre.lower())
    duree = meta.get("duree_estimee_min")
    if not isinstance(duree, int) or not 10 <= duree <= 60:
        warns.append(f"{nom}: duree_estimee_min inhabituelle ({duree!r})")

    src = d.get("source") or {}
    if src.get("epreuve_source") != demande["epreuve_source"]:
        erreurs.append(f"{nom}: source.epreuve_source doit être {demande['epreuve_source']!r}")
    if src.get("rappel_id") != f"rdm-gce-{COURT[code]}-{slug(demande['theme'])}-0":
        erreurs.append(f"{nom}: source.rappel_id attendu rdm-gce-{COURT[code]}-{slug(demande['theme'])}-0")

    sections = d.get("sections")
    if not isinstance(sections, list) or [s.get("type") for s in sections] != ORDRE:
        erreurs.append(f"{nom}: les sections doivent être exactement {ORDRE} dans cet ordre")
        return erreurs, warns
    par_type = {s["type"]: s for s in sections}

    if not (par_type["accroche"].get("contenu_markdown") or "").strip():
        erreurs.append(f"{nom}: accroche vide")
    pre = par_type["prerequis"].get("items")
    if not isinstance(pre, list) or not 2 <= len(pre) <= 4:
        erreurs.append(f"{nom}: prerequis doit avoir 2 à 4 items")
    regle = par_type["regle"]
    if not (regle.get("titre") and regle.get("contenu_markdown")):
        erreurs.append(f"{nom}: regle sans titre ou contenu")
    else:
        mots = len(re.findall(r"\w+", regle["contenu_markdown"]))
        if mots < 120:
            warns.append(f"{nom}: regle courte ({mots} mots)")
    var = regle.get("variantes")
    if not isinstance(var, list) or not 1 <= len(var) <= 3 or any(
            not (v.get("nom") and v.get("quand_utiliser") and v.get("contenu_markdown")) for v in var if isinstance(v, dict)):
        erreurs.append(f"{nom}: regle.variantes doit avoir 1 à 3 entrées (nom, quand_utiliser, contenu_markdown)")
    ex = par_type["exemple_resolu"]
    etapes = ex.get("etapes")
    if not ex.get("enonce_markdown") or not ex.get("conclusion_markdown") or ex.get("epreuve_source") is not False:
        erreurs.append(f"{nom}: exemple_resolu : enonce_markdown, conclusion_markdown et epreuve_source=false requis")
    if not isinstance(etapes, list) or not 3 <= len(etapes) <= 6:
        erreurs.append(f"{nom}: exemple_resolu.etapes doit avoir 3 à 6 étapes")
    else:
        for k, et in enumerate(etapes, 1):
            if et.get("numero") != k or not (et.get("action") and et.get("justification") and et.get("resultat_markdown")):
                erreurs.append(f"{nom}: étape {k} incomplète ou mal numérotée")
    err = par_type["erreurs_classiques"].get("items")
    if not isinstance(err, list) or not 3 <= len(err) <= 5 or any(
            not (i.get("erreur_markdown") and i.get("pourquoi_faux") and i.get("correction_markdown")) for i in err):
        erreurs.append(f"{nom}: erreurs_classiques doit avoir 3 à 5 items complets")
    exo = par_type["exercices_application"].get("items")
    if not isinstance(exo, list) or [i.get("difficulte") for i in exo] != DIFFS or any(
            not (i.get("enonce_markdown") and i.get("solution_markdown")) or i.get("numero") != k
            for k, i in enumerate(exo, 1)):
        erreurs.append(f"{nom}: exercices_application doit avoir exactement 3 exercices numérotés 1-3, difficultés {DIFFS}")
    syn = par_type["synthese"].get("items_markdown")
    if not isinstance(syn, list) or not 4 <= len(syn) <= 6:
        erreurs.append(f"{nom}: synthese.items_markdown doit avoir 4 à 6 points")

    for k, t in enumerate(textes(d)):
        verifier_texte(t, f"{nom} str#{k}", erreurs, warns)

    reference = set()
    for ref in demande.get("references", []):
        reference |= shingles(ref.get("enonce", ""))
    corps = " ".join(textes({"ex": ex.get("enonce_markdown"), "exo": [i.get("enonce_markdown") for i in (exo or [])]}))
    commun = shingles(corps) & reference
    if commun:
        erreurs.append(f"{nom}: énoncé trop proche d'une question de référence (ex. « {next(iter(commun))} »)")
    return erreurs, warns


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    tranche = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dossier = Path(sys.argv[2])
    erreurs, warns = [], []
    attendus, vus_ids, vus_titres = set(), set(), set()
    for demande in tranche:
        nom = f"cours-gce-{COURT[demande['matiere_code']]}-{slug(demande['theme'])}.json"
        attendus.add(nom)
        chemin = dossier / nom
        if not chemin.is_file():
            erreurs.append(f"fichier manquant : {nom} (thème {demande['theme']!r})")
            continue
        er, wa = valider(demande, chemin, vus_ids, vus_titres)
        erreurs += er
        warns += wa
    for extra in sorted(p.name for p in dossier.glob("*") if p.name not in attendus):
        warns.append(f"fichier inattendu : {extra}")
    print(f"{len(tranche)} cours attendu(s)")
    for w in warns:
        print("warn ", w)
    for e in erreurs:
        print("ERREUR", e)
    print("OK" if not erreurs else f"ECHEC ({len(erreurs)} erreur(s))")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
