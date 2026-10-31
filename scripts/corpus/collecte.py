"""Modes RECHERCHE (validation d'URL sans téléchargement) et COLLECTE (téléchargement dans la zone de dépôt).

Règles non négociables (D4, §6.2) :
  - HEAD d'abord : 200 + application/pdf + taille plausible, sinon on ne télécharge pas ;
  - un site à la fois, pause >= 2 s, arrêt sur 429/500 répétés, robots.txt lu ;
  - JAMAIS de contournement de Cloudflare, de CAPTCHA, de mur de connexion, de paiement, de Google Drive sans
    lien direct : le lien est consigné dans « Liens à ouvrir à la main » et on passe au suivant ;
  - aucun fichier de la zone n'est écrasé, supprimé ni déplacé ; un `.part` n'est jamais pris pour valide ;
  - chaque fichier a une fiche dans `provenance.jsonl` (URL, source, date, SHA-256, taille, pages, page de garde
    lue, décision, score), seule trace de décision.
"""
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

import qualification
import registre
import sources
from commun import AUDIT, ZONE_EN, ZONE_FR, ecrire_jsonl, lire_jsonl, slug

AGENT = "EduKora-veille-corpus/1.0 (collecte de sujets d'examen publics ; contact : equipe EduKora)"
PAUSE_MINIMALE = 2.0
HOTES_MANUELS = sources.hotes_manuels()  # tout site non automatisable du registre (sources.json)
TAILLE_MIN = 20 * 1024            # un sujet de plusieurs pages sous 20 ko est suspect (§6.2)
TAILLE_MAX = 80 * 1024 * 1024
LIENS_MANUELS = os.path.join(AUDIT, "corpus", "liens_a_ouvrir_a_la_main.jsonl")

_dernier_passage = {}
_echecs = {}


class RefusProtege(Exception):
    """Le site oppose une protection (403/503 Cloudflare, CAPTCHA, connexion) : on ne la contourne pas."""


def _hote(url):
    return urllib.parse.urlparse(url).netloc.lower()


def _pause(hote):
    """Une requête à la fois par site, au moins PAUSE_MINIMALE secondes entre deux."""
    attente = PAUSE_MINIMALE - (time.monotonic() - _dernier_passage.get(hote, 0.0))
    if attente > 0:
        time.sleep(attente)
    _dernier_passage[hote] = time.monotonic()


def robots_autorise(url, ouvrir=urllib.request.urlopen):
    """robots.txt du site : True si le chemin n'est pas interdit (en cas d'échec de lecture : autorisé, prudence en aval)."""
    parties = urllib.parse.urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        requete = urllib.request.Request("%s://%s/robots.txt" % (parties.scheme, parties.netloc), headers={"User-Agent": AGENT})
        with ouvrir(requete, timeout=15) as reponse:
            rp.parse(reponse.read().decode("utf-8", "ignore").splitlines())
    except Exception:  # noqa: BLE001
        return True
    return rp.can_fetch(AGENT, url)


def verifier_url(url, ouvrir=urllib.request.urlopen):
    """
    HEAD d'une URL de PDF, sans la télécharger. Retourne
    {"ok", "statut", "type", "taille", "motif", "manuel"} ; `manuel` = à ouvrir à la main (protection, Drive).
    """
    hote = _hote(url)
    sortie = {"url": url, "ok": False, "statut": None, "type": None, "taille": None, "motif": "", "manuel": False}
    if any(h in hote for h in HOTES_MANUELS):
        sortie.update(motif="hôte à ouvrir à la main (pas de lien direct)", manuel=True)
        return sortie
    if _echecs.get(hote, 0) >= 3:
        sortie["motif"] = "arrêt : trop d'échecs consécutifs sur ce site (429/500)"
        return sortie
    _pause(hote)
    requete = urllib.request.Request(url, method="HEAD", headers={"User-Agent": AGENT})
    try:
        with ouvrir(requete, timeout=30) as reponse:
            entetes = {k.lower(): v for k, v in reponse.headers.items()}
            sortie["statut"] = getattr(reponse, "status", 200)
    except urllib.error.HTTPError as exc:
        sortie["statut"] = exc.code
        entetes = {k.lower(): v for k, v in (exc.headers or {}).items()}
        if exc.code in (429, 500, 502, 503, 504):
            _echecs[hote] = _echecs.get(hote, 0) + 1
        if exc.code in (403, 503) or "cf-mitigated" in entetes or "cloudflare" in entetes.get("server", "").lower():
            sortie.update(motif="protection du site (HTTP %s) : non contournée" % exc.code, manuel=True)
        else:
            sortie["motif"] = "HTTP %s" % exc.code
        return sortie
    except Exception as exc:  # noqa: BLE001 - réseau, DNS, délai : jamais bloquant, jamais contourné
        _echecs[hote] = _echecs.get(hote, 0) + 1
        sortie["motif"] = "échec réseau : %s" % exc
        return sortie
    _echecs[hote] = 0
    sortie["type"] = entetes.get("content-type", "").split(";")[0].strip().lower()
    try:
        sortie["taille"] = int(entetes.get("content-length", ""))
    except ValueError:
        sortie["taille"] = None
    if sortie["statut"] != 200:
        sortie["motif"] = "HTTP %s" % sortie["statut"]
    elif sortie["type"] != "application/pdf":
        sortie.update(motif="pas un PDF (%s) : page de référencement, à ouvrir à la main" % (sortie["type"] or "type inconnu"), manuel=True)
    elif sortie["taille"] is not None and not (TAILLE_MIN <= sortie["taille"] <= TAILLE_MAX):
        sortie["motif"] = "taille implausible (%d octets)" % sortie["taille"]
    else:
        sortie["ok"] = True
    return sortie


def zone_de(langue):
    if langue not in ("fr", "en"):
        raise ValueError("langue attendue : fr ou en (la zone se choisit sur la langue de l'épreuve, jamais sur le site)")
    return ZONE_FR if langue == "fr" else ZONE_EN


def nom_normalise(examen, serie, matiere, annee, paper, source):
    """<examen>_<série>_<matière>_<année>_<paper>_<source>.pdf, sans accent ni ambiguïté."""
    morceaux = [examen, serie or "toutes", matiere, str(annee or "annee-inconnue"), "p%s" % paper if paper else "sujet", source]
    return "_".join(slug(m, 40) for m in morceaux) + ".pdf"


def nom_libre(zone, nom):
    """Suffixe _2, _3... : aucun fichier existant n'est jamais écrasé."""
    base, ext = os.path.splitext(nom)
    candidat, n = nom, 1
    while os.path.exists(os.path.join(zone, candidat)):
        n += 1
        candidat = "%s_%d%s" % (base, n, ext)
    return candidat


def deja_collecte(zone, url):
    return any(f.get("url") == url and f.get("fichier") for f in lire_jsonl(os.path.join(zone, "provenance.jsonl")))


def _sha(chemin):
    from commun import sha256_fichier
    return sha256_fichier(chemin)


def _fiche_par_sha(zone, sha):
    """Première fiche de la zone portant ce SHA-256 avec un fichier réel, ou None."""
    for f in lire_jsonl(os.path.join(zone, "provenance.jsonl")):
        if f.get("sha256") == sha and f.get("fichier") and f.get("decision") != "DOUBLON_EXACT":
            return f
    return None


def lien_a_ouvrir(url, cible, motif):
    ecrire_jsonl(LIENS_MANUELS, {"url": url, "cible": cible, "motif": motif, "date": registre.aujourdhui()})


def collecter(url, langue, nom, cible=None, source=None, ouvrir=urllib.request.urlopen, controle=None):
    """
    Télécharge un PDF dans la zone (fr|en), le qualifie, écrit sa fiche. Retourne la fiche (dict).
    `controle` : callable (chemin_pdf, cible) -> dict de qualification (injectable pour les tests).
    """
    zone = zone_de(langue)
    os.makedirs(zone, exist_ok=True)
    if deja_collecte(zone, url):
        return {"url": url, "decision": "DÉJÀ COLLECTÉ", "fichier": None}
    if not robots_autorise(url, ouvrir):
        lien_a_ouvrir(url, cible, "interdit par robots.txt")
        return {"url": url, "decision": "ROBOTS", "fichier": None, "liens_proposes": sources.liens_proposes(cible, url, "interdit par robots.txt")}
    tete = verifier_url(url, ouvrir)
    if not tete["ok"]:
        if tete["manuel"]:
            lien_a_ouvrir(url, cible, tete["motif"])
        return {"url": url, "decision": "NON TÉLÉCHARGÉ", "motif": tete["motif"], "manuel": tete["manuel"], "fichier": None,
                "liens_proposes": sources.liens_proposes(cible, url, tete["motif"])}
    final = nom_libre(zone, nom)
    chemin, partiel = os.path.join(zone, final), os.path.join(zone, final + ".part")
    hote = _hote(url)
    _pause(hote)
    requete = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with ouvrir(requete, timeout=120) as reponse, open(partiel, "wb") as sortie:
            total = 0
            for bloc in iter(lambda: reponse.read(1 << 16), b""):
                total += len(bloc)
                if total > TAILLE_MAX:
                    raise RuntimeError("taille maximale dépassée")
                sortie.write(bloc)
    except Exception as exc:  # noqa: BLE001 - jamais de fichier partiel pris pour valide
        return {"url": url, "decision": "ÉCHEC", "motif": str(exc), "fichier": None, "partiel": partiel}
    sha = _sha(partiel)
    existante = _fiche_par_sha(zone, sha)
    if existante:
        # Même document, autre site : une seule entrée, une provenance de plus. Le fichier téléchargé est un
        # temporaire du skill (.part), pas un fichier de la zone : on peut le retirer sans rien perdre.
        os.remove(partiel)
        fiche = {"url": url, "source": source or hote, "date": registre.aujourdhui(), "fichier": existante["fichier"],
                 "zone": zone, "sha256": sha, "decision": "DOUBLON_EXACT", "controleur": "automatique", "cible": cible,
                 "provenance_supplementaire_de": existante["url"]}
        ecrire_jsonl(os.path.join(zone, "provenance.jsonl"), fiche)
        return fiche
    os.replace(partiel, chemin)
    qualifier = controle or qualification.qualifier
    q = qualifier(chemin, cible)
    fiche = {
        "url": url, "source": source or hote, "date": registre.aujourdhui(), "fichier": final, "zone": zone,
        "sha256": q.get("sha256"), "taille": q.get("taille"), "pages": q.get("pages"), "garde": q.get("garde"),
        "decision": q.get("decision"), "score": q.get("score"),
        "eliminatoires": [list(e) for e in q.get("eliminatoires", [])],
        "avertissements": q.get("avertissements", []), "controleur": "automatique", "cible": cible,
    }
    ecrire_jsonl(os.path.join(zone, "provenance.jsonl"), fiche)
    return fiche
