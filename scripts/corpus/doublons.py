"""Doublons et versions (§8) : exact (SHA-256), probable (texte normalisé), visuel (hash perceptuel des scans).

Un document est comparé à toutes les zones connues : zones de dépôt `trous/fr` et `trous/en`, PDF déjà téléchargés
(`non_traites`, `ingest/_telechargements_*`). Le module ne supprime, ne déplace ni ne fusionne rien : il propose.
"""
import json
import os

from commun import normaliser, sha256_fichier, sha256_texte

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

MOTS_BRUIT = ("more questions at www meetlearn com", "gcerevision com", "kawlo", "cgce revision", "sujetexa",
              "for more visit", "scanned by camscanner")


def _texte_normalise(doc, pages=2, limite=1500):
    brut = " ".join(doc[i].get_text() for i in range(min(pages, len(doc))))
    n = normaliser(brut)
    for bruit in MOTS_BRUIT:
        n = n.replace(bruit, " ")
    return " ".join(n.split())[:limite]


def hash_perceptuel(page, cote=8):
    """Hash moyen (aHash) 8x8 de la première page : stable à la résolution et au léger bruit d'un scan."""
    pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), colorspace=fitz.csGRAY)
    largeur, hauteur, donnees = pix.width, pix.height, pix.samples
    cellules = []
    for gy in range(cote):
        for gx in range(cote):
            x0, x1 = gx * largeur // cote, max(gx * largeur // cote + 1, (gx + 1) * largeur // cote)
            y0, y1 = gy * hauteur // cote, max(gy * hauteur // cote + 1, (gy + 1) * hauteur // cote)
            total = n = 0
            for y in range(y0, y1):
                ligne = donnees[y * largeur + x0: y * largeur + x1]
                total += sum(ligne)
                n += len(ligne)
            cellules.append(total / max(1, n))
    moyenne = sum(cellules) / len(cellules)
    return "".join("1" if v > moyenne else "0" for v in cellules)


def distance_hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def empreintes(chemin_pdf):
    """{'sha256', 'pages', 'texte' (sha du texte normalisé, ou None si scan), 'phash'} d'un PDF."""
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) est requis pour les empreintes de texte et visuelles.")
    sortie = {"sha256": sha256_fichier(chemin_pdf), "pages": None, "texte": None, "phash": None,
              "taille": os.path.getsize(chemin_pdf)}
    try:
        with fitz.open(chemin_pdf) as doc:
            sortie["pages"] = len(doc)
            texte = _texte_normalise(doc)
            if len(texte) >= 120:
                sortie["texte"] = sha256_texte(texte)
            if len(doc):
                sortie["phash"] = hash_perceptuel(doc[0])
    except Exception:  # noqa: BLE001 - un PDF illisible n'a simplement pas d'empreinte exploitable
        pass
    return sortie


def construire_index(dossiers, cache=None):
    """Index {chemin: empreintes} de tous les PDF des dossiers donnés (cache JSON optionnel, clé taille+mtime)."""
    memoire = {}
    if cache and os.path.isfile(cache):
        with open(cache, encoding="utf-8") as fh:
            memoire = json.load(fh)
    index = {}
    for dossier in dossiers:
        if not os.path.isdir(dossier):
            continue
        for nom in sorted(os.listdir(dossier)):
            if not nom.lower().endswith(".pdf"):
                continue
            chemin = os.path.join(dossier, nom)
            cle = "%s|%d|%d" % (chemin, os.path.getsize(chemin), int(os.path.getmtime(chemin)))
            if cle not in memoire:
                memoire[cle] = empreintes(chemin)
            index[chemin] = memoire[cle]
    if cache:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        with open(cache, "w", encoding="utf-8") as fh:
            json.dump(memoire, fh)
    return index


def chercher(chemin_pdf, index, seuil_visuel=6):
    """
    Compare un PDF à l'index. Retourne [(niveau, chemin_existant, detail)] :
      exact     : même SHA-256 ;
      probable  : même texte normalisé des premières pages ;
      visuel    : scans sans texte, première page quasi identique (distance de Hamming <= seuil).
    Le fichier lui-même est ignoré.
    """
    mien = empreintes(chemin_pdf)
    trouves = []
    for autre, e in index.items():
        if os.path.abspath(autre) == os.path.abspath(chemin_pdf):
            continue
        if e["sha256"] == mien["sha256"]:
            trouves.append(("exact", autre, "SHA-256 identique"))
        elif mien["texte"] and e["texte"] == mien["texte"]:
            trouves.append(("probable", autre, "texte normalisé des premières pages identique"))
        elif (not mien["texte"] and not e["texte"] and mien["phash"] and e["phash"]
              and e["pages"] == mien["pages"] and distance_hamming(mien["phash"], e["phash"]) <= seuil_visuel):
            trouves.append(("visuel", autre, "première page quasi identique (hash perceptuel), même nombre de pages"))
    ordre = {"exact": 0, "probable": 1, "visuel": 2}
    return sorted(trouves, key=lambda t: ordre[t[0]])


# Un même sujet physique peut porter deux matières : PM Mechanics (765) et PM Statistics (770) partagent des P2
# identiques. C'est UNE épreuve à deux rattachements, jamais un doublon à écarter.
PAIRES_SUJET_COMMUN = ({"GCE_PM_MECHANICS", "GCE_PM_STATISTICS"},)


def est_sujet_commun(matiere_a, matiere_b):
    return any({matiere_a, matiere_b} == paire for paire in PAIRES_SUJET_COMMUN)


def verdict(niveau_doublon, matiere_cible, matiere_existante):
    """Décision proposée pour un doublon trouvé : jamais d'écrasement, jamais de fusion automatique."""
    if niveau_doublon == "exact" and matiere_cible != matiere_existante and est_sujet_commun(matiere_cible, matiere_existante):
        return "RATTACHEMENT_MULTIPLE"
    return {"exact": "DOUBLON", "probable": "DOUBLON_PROBABLE", "visuel": "DOUBLON_VISUEL_A_VERIFIER"}[niveau_doublon]
