"""Fonctions communes du skill veille-corpus-epreuves (stdlib uniquement)."""
import hashlib
import os
import re
import unicodedata

RACINE_DEPOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INGEST = os.path.join(RACINE_DEPOT, "backend", "ingest")
AUDIT = os.path.join(INGEST, "_audit")
EPREUVES = os.environ.get("CORPUS_EPREUVES", r"C:\Users\Administrateur\Documents\Epreuves")
ZONE_FR = os.path.join(EPREUVES, "trous", "fr")
ZONE_EN = os.path.join(EPREUVES, "trous", "en")


def normaliser(texte):
    """Minuscules, sans accents, ponctuation réduite à des espaces : base de toutes les comparaisons."""
    texte = unicodedata.normalize("NFD", str(texte or "").lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", texte)).strip()


def slug(texte, longueur=70):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normaliser(texte))).strip("-")[:longueur]


def sha256_fichier(chemin, bloc=1 << 20):
    h = hashlib.sha256()
    with open(chemin, "rb") as fh:
        for morceau in iter(lambda: fh.read(bloc), b""):
            h.update(morceau)
    return h.hexdigest()


def sha256_texte(texte):
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


# --- noms de dossiers d'ingestion -------------------------------------------------------------

_ANNEE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
FAUTES_CONNUES = ("phylosophie", "allemend", "georgraphie", "epagnol", "phydique", "zeo")


def dossier_depuis_epreuve_source(epreuve_source):
    """`bac-a-x-2020-cameroun.pdf` -> `bac-a-x-2020-cameroun` (certains dossiers n'ont pas le suffixe .pdf)."""
    nom = str(epreuve_source or "").strip()
    return nom[:-4] if nom.lower().endswith(".pdf") else nom


def annee_du_nom(nom):
    """Dernière année plausible lue dans un nom de dossier ou de fichier, sinon None."""
    annees = _ANNEE.findall(str(nom or ""))
    return int(annees[-1]) if annees else None


def est_dossier_epreuve(nom):
    """Un dossier de `cm/` qui est une épreuve (pas un dossier de cours, de staging ou d'archive)."""
    return bool(nom) and not nom.startswith(("_", "cours-")) and "." not in nom


def lister_dossiers(chemin):
    if not os.path.isdir(chemin):
        return []
    return sorted(d for d in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, d)))


def lister_pdf(chemin):
    if not os.path.isdir(chemin):
        return []
    return sorted(f for f in os.listdir(chemin) if f.lower().endswith(".pdf"))


# --- noms de PDF GCE ---------------------------------------------------------------------------

_PDF_GCE = re.compile(r"^GCE_(OL|AL)_(.+?)_(\d{4})_P(\d)(.*)\.pdf$", re.I)
_ALIAS_MATIERE = {
    "additional_maths": "add_maths", "add_maths": "add_maths", "computer_science": "computer_sci",
    "human_biology": "human_biology", "food_nutrition": "food_nutrition", "further_maths": "further_maths",
    "pm_mechanics": "pm_mechanics", "pm_statistics": "pm_statistics", "mathematics": "maths",
    "religious_studies": "religion", "sbe_french": "sbe_french",
}


def analyser_nom_pdf_gce(nom):
    """GCE_OL_ENGLISH_2013_P1_doublon_scan.pdf -> dict(niveau, matiere, annee, paper, reste) ou None."""
    m = _PDF_GCE.match(os.path.basename(nom))
    if not m:
        return None
    niveau, matiere, annee, paper, reste = m.groups()
    matiere = re.sub(r"_(0560|5175)$", "", matiere.lower())
    return {
        "niveau": "GCE_" + niveau.upper(),
        "matiere": _ALIAS_MATIERE.get(matiere, matiere),
        "annee": int(annee),
        "paper": int(paper),
        "reste": reste.strip("_"),
    }


def ecrire_jsonl(chemin, enregistrement):
    import json
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(enregistrement, ensure_ascii=False) + "\n")


def lire_jsonl(chemin):
    import json
    if not os.path.isfile(chemin):
        return []
    sortie = []
    with open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                sortie.append(json.loads(ligne))
            except ValueError:
                continue  # ligne partielle d'une interruption : jamais prise pour valide
    return sortie


def epreuve_source_du_dossier(chemin_dossier):
    """`epreuve_source` déclaré dans le premier JSON d'exercice d'un dossier d'ingestion (None si illisible).

    Sert à rapprocher un dossier de sa Lesson sans se fier au nom du dossier (plusieurs dossiers portent un nom
    différent de leur `epreuve_source`)."""
    import json
    try:
        for entree in sorted(os.scandir(chemin_dossier), key=lambda e: e.name):
            if entree.is_file() and "_exercice_" in entree.name and entree.name.endswith(".json"):
                with open(entree.path, encoding="utf-8") as fh:
                    source = json.load(fh).get("epreuve_source")
                return dossier_depuis_epreuve_source(source) if source else None
    except (OSError, ValueError):
        return None
    return None
