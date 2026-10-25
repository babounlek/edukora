"""
Empreintes canoniques des contenus pédagogiques (chaîne de synchronisation, voir
deploy/SPEC-SYNC-CONTENU.md).

Bibliothèque en bibliothèque standard SEULE, sans import Django : le même fichier est utilisé
sur le poste Windows (préparation des lots) et sur le serveur (moteur de synchronisation). Toute
divergence entre les deux côtés rendrait les comparaisons fausses ; ne rien y ajouter qui dépende
de l'environnement.

Deux notions à ne pas confondre :
  - `empreinte_source` : empreinte du JSON d'ingestion (canonisé) et des fichiers qu'il déclare ;
  - `empreinte_etat`   : projection de l'objet EN BASE, calculée côté serveur (phase 4).
Ce module ne produit que la première, plus les identifiants et clés naturelles.
"""
import hashlib
import json
import unicodedata

# À incrémenter si la canonisation change : les empreintes déjà journalisées ne seraient plus comparables.
VERSION_EMPREINTE = 1

# Clés de premier niveau qui ne font pas partie du contenu : `statut` est « brouillon » dans tous
# les JSON de correction-experte et c'est l'ingestion qui publie ; il appartient à l'admin ensuite.
CLES_VOLATILES = ("statut",)

TYPE_EXERCICE = "exercice"
TYPE_COURS = "cours"
TYPE_QUIZ = "quiz"
TYPE_INEDITE = "inedite"
TYPE_INCONNU = "inconnu"
TYPES_V1 = (TYPE_EXERCICE, TYPE_COURS, TYPE_QUIZ)

CHUNK = 1024 * 1024


def _normaliser(valeur):
    if isinstance(valeur, str):
        return unicodedata.normalize("NFC", valeur).replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(valeur, list):
        return [_normaliser(v) for v in valeur]
    if isinstance(valeur, dict):
        return {_normaliser(k): _normaliser(v) for k, v in valeur.items()}
    return valeur


def canoniser(data, volatiles=CLES_VOLATILES):
    """Sérialisation déterministe : clés triées, NFC, fins de ligne \\n, sans clé volatile."""
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if k not in volatiles}
    return json.dumps(_normaliser(data), sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_octets(octets):
    return hashlib.sha256(octets).hexdigest()


def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        while True:
            bloc = f.read(CHUNK)
            if not bloc:
                break
            h.update(bloc)
    return h.hexdigest()


def empreinte_source(data, shas_fichiers=()):
    """SHA-256 du JSON canonique suivi de la liste triée des SHA-256 des fichiers déclarés."""
    morceaux = [canoniser(data)] + sorted(shas_fichiers)
    return sha256_octets("\n".join(morceaux).encode("utf-8", errors="surrogatepass"))


def lire_json(chemin):
    """Retourne (data, avertissements). Lève ValueError si le fichier n'est pas un JSON UTF-8 valide."""
    avertissements = []
    with open(chemin, "rb") as f:
        brut = f.read()
    if brut.startswith(b"\xef\xbb\xbf"):
        avertissements.append("BOM UTF-8 en tête de fichier")
        brut = brut[3:]
    try:
        return json.loads(brut.decode("utf-8")), avertissements
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"JSON illisible : {exc}") from exc


def identifiant_chemin(chemin_relatif):
    """Chemin relatif au dossier ingest/, sans extension, avec des '/'. Ex. cm/<dossier>/<fichier>."""
    p = chemin_relatif.replace("\\", "/").lstrip("/")
    return p[:-5] if p.lower().endswith(".json") else p


def segments(chemin_relatif):
    return [s for s in chemin_relatif.replace("\\", "/").split("/") if s]


def unite_de(chemin_relatif):
    """
    Unité de validation et de préparation d'un fichier :
      - corrections / cours : le dossier `<pays>/<dossier>` ;
      - quiz : le fichier lui-même (`_quiz/<pays>/<fichier>.json`).
    """
    segs = segments(chemin_relatif)
    if segs and segs[0] == "_quiz":
        return "/".join(segs)
    return "/".join(segs[:2])


def est_chemin_ingerable(chemin_relatif):
    """
    Vrai pour ce que le canal v1 sait porter : `<pays>/<dossier>/*.json` (aucun composant en `_`)
    et `_quiz/<pays>/*.json`. `_quiz/_audit`, `_quiz/_gce_al_slices`, `_inedit`, `_audit`,
    `_gce_staging`, `_telechargements*` sont exclus.
    """
    segs = segments(chemin_relatif)
    if not segs or not segs[-1].lower().endswith(".json"):
        return False
    if segs[0] == "_quiz":
        return len(segs) == 3 and not segs[1].startswith("_") and not segs[2].startswith("_")
    if any(s.startswith("_") for s in segs):
        return False
    return len(segs) >= 3


def type_de_contenu(chemin_relatif, data):
    segs = segments(chemin_relatif)
    if segs and segs[0] == "_inedit":
        return TYPE_INEDITE
    if segs and segs[0] == "_quiz":
        items = data if isinstance(data, list) else [data]
        if items and all(isinstance(i, dict) and "enonce_markdown" in i and "theme" in i for i in items):
            return TYPE_QUIZ
        return TYPE_INCONNU
    if isinstance(data, dict):
        if "sections" in data:
            return TYPE_COURS
        if "epreuve_source" in data and "numero_exercice" in data:
            return TYPE_EXERCICE
    return TYPE_INCONNU


def elements(chemin_relatif, data, type_contenu):
    """
    Éléments synchronisables d'un fichier : [(id_stable, data_de_l_element)].
    Un fichier de quiz peut contenir plusieurs items, chacun identifié par son `external_id`
    (jamais par sa position : un item sans external_id serait recréé à chaque lot).
    """
    if type_contenu == TYPE_QUIZ:
        items = data if isinstance(data, list) else [data]
        return [(str(i.get("external_id") or "").strip(), i) for i in items]
    if type_contenu == TYPE_COURS:
        return [(str(data.get("cours_id") or "").strip() or identifiant_chemin(chemin_relatif), data)]
    return [(identifiant_chemin(chemin_relatif), data)]


def cle_naturelle(type_contenu, chemin_relatif, element):
    """Clé servant à retrouver l'objet en production (voir spec §2). Immuable une fois journalisée."""
    segs = segments(chemin_relatif)
    if type_contenu == TYPE_EXERCICE:
        return {
            "pays": segs[0] if segs else "",
            "epreuve_source": element.get("epreuve_source"),
            "numero_exercice": str(element.get("numero_exercice")),
            "matiere": element.get("matiere"),
            "examen": element.get("examen"),
            "serie": element.get("serie"),
            "annee": element.get("annee"),
            "variante_sujet": element.get("variante_sujet") or "",
            "numero_paper": element.get("numero_paper") or "",
        }
    if type_contenu == TYPE_COURS:
        return {"cours_id": str(element.get("cours_id") or "")}
    if type_contenu == TYPE_QUIZ:
        return {"external_id": str(element.get("external_id") or "")}
    return {}


def noms_fichiers_declares(element):
    """Noms de fichiers image déclarés par `figures[]` (clé `fichier` ou `nom_fichier`, comme l'ingestion)."""
    noms = []
    figures = element.get("figures") if isinstance(element, dict) else None
    for fig in figures or []:
        if isinstance(fig, dict):
            nom = fig.get("fichier") or fig.get("nom_fichier")
            if nom:
                noms.append(str(nom))
    return noms
