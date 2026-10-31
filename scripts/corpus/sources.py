"""Registre des sites de sujets et génération des liens pertinents (§ collecte, « liens à ouvrir à la main »).

Le skill ne télécharge que sur les sites `automatisable`. Pour tous les autres, il fournit à l'utilisateur
des liens ciblés : la recherche du site sur la cible, une recherche Google limitée au site, les rubriques utiles.
"""
import json
import os
import urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "sources.json")

COURT = {"GCE_OL": "O Level", "GCE_AL": "A Level", "OL": "O Level", "AL": "A Level"}
NIVEAUX = {"GCE_OL": "Ordinary Level", "GCE_AL": "Advanced Level", "OL": "Ordinary Level", "AL": "Advanced Level"}
EXAMENS = {"bepc": "BEPC", "probatoire": "Probatoire", "bac": "BAC", "cap": "CAP"}


ACCES_LISIBLE = {
    "pdf_direct": "PDF direct", "api_wp": "API WordPress", "page_html": "épreuve transcrite en page HTML", "drive": "via Google Drive",
    "bloque_automate": "bloque les accès automatiques", "visionneuse_integree": "PDF dans une visionneuse", "gestionnaire": "gestionnaire de téléchargement",
    "raccourci": "liens raccourcis", "payant_en_partie": "en partie payant", "navigateur_utilisateur": "votre Chrome connecté",
    "connexion": "connexion requise", "a_explorer": "à explorer",
}


def charger(chemin=FICHIER):
    with open(chemin, encoding="utf-8") as fh:
        return json.load(fh)["sources"]


def hotes(source):
    return [source["domaine"]] + list(source.get("hotes_supplementaires", []))


def source_de_url(url, sources=None):
    """La source du registre à laquelle appartient une URL (par hôte, sous-domaines compris), ou None."""
    hote = urllib.parse.urlparse(url).netloc.lower()
    for s in sources or charger():
        for h in hotes(s):
            if hote == h or hote.endswith("." + h):
                return s
    return None


def hotes_manuels(sources=None):
    """Hôtes que le skill ne télécharge jamais seul."""
    return tuple(h for s in sources or charger() if not s.get("automatisable") for h in hotes(s))


def _matiere_lisible(matiere):
    if not matiere:
        return ""
    m = str(matiere)
    if m.startswith("GCE_"):
        m = m[4:]
    return m.replace("_", " ").title() if m.isupper() or "_" in m else m


def terme_de_recherche(cible):
    """Requête de recherche déduite de la cible {niveau, matiere, annee, paper, examen, serie}."""
    cible = cible or {}
    morceaux = []
    niveau = str(cible.get("niveau") or "")
    if niveau.upper() in NIVEAUX:
        morceaux += ["GCE", NIVEAUX[niveau.upper()]]
    elif cible.get("examen"):
        morceaux.append(EXAMENS.get(str(cible["examen"]).lower(), str(cible["examen"])))
    morceaux.append(_matiere_lisible(cible.get("matiere")))
    if cible.get("serie"):
        morceaux.append("série %s" % cible["serie"])
    if cible.get("paper"):
        morceaux.append("paper %s" % cible["paper"])
    if cible.get("annee"):
        morceaux.append("june %s" % cible["annee"] if niveau.upper() in NIVEAUX else str(cible["annee"]))
    return " ".join(m for m in morceaux if m)


def systeme_de(cible):
    cible = cible or {}
    if str(cible.get("niveau") or "").upper() in NIVEAUX or str(cible.get("langue") or "") == "en":
        return "en"
    return "fr"


def liens_de_recherche(cible, sources=None):
    """
    Liste de liens utiles pour trouver une cible. Chaque lien :
    {source, nom, type, url, automatisable, note}. `type` : recherche_site | api | google_site | rubrique | scribd.
    """
    sources = sources or charger()
    systeme = systeme_de(cible)
    terme = terme_de_recherche(cible)
    q = urllib.parse.quote_plus(terme)
    liens = []
    for s in sources:
        if systeme not in s.get("systemes", []) or "a_explorer" in s.get("acces", []) or s["id"] in ("drive", "camgceb", "gcepanel"):
            continue
        rec = s.get("recherche", {})
        base = {"source": s["id"], "nom": s["nom"], "automatisable": bool(s.get("automatisable"))}
        if rec.get("wp_search"):
            liens.append(dict(base, type="recherche_site", url=rec["wp_search"].format(q=q), note="recherche du site"))
        if rec.get("scribd_search"):
            liens.append(dict(base, type="scribd", url=rec["scribd_search"].format(q=q),
                              note="à ouvrir dans votre Chrome connecté ; le skill peut lire, le téléchargement attend votre accord"))
        if rec.get("google"):
            liens.append(dict(base, type="google_site", url="https://www.google.com/search?q=" + urllib.parse.quote_plus("site:%s %s" % (s["domaine"], terme)),
                              note="recherche Google limitée au site"))
        niveau = str((cible or {}).get("niveau") or "").upper()
        for nom, url in rec.get("categories", {}).items():
            pertinent = (niveau in COURT and nom.startswith("GCE") and COURT[niveau] in nom) or \
                        (cible and cible.get("examen") and EXAMENS.get(str(cible["examen"]).lower(), "").lower() in nom.lower()) or \
                        (not niveau and not (cible and cible.get("examen")))
            if pertinent:
                liens.append(dict(base, type="rubrique", url=url, note=nom))
    return liens


def liens_proposes(cible, url_echouee=None, motif="", sources=None):
    """Liens à donner à l'utilisateur quand le téléchargement direct est impossible (succinct, sans les sites exclus)."""
    sources = sources or charger()
    liens = liens_de_recherche(cible, sources)
    pris = []
    if url_echouee:
        pris.append({"source": (source_de_url(url_echouee, sources) or {}).get("id", "autre"), "type": "lien_trouve", "url": url_echouee,
                     "note": motif or "lien repéré, à ouvrir à la main", "automatisable": False})
    return pris + liens


def rapport_markdown(cible, sources=None):
    """Rapport lisible : ce que le skill peut télécharger seul, puis les liens à ouvrir à la main, par site."""
    sources = sources or charger()
    liens = liens_de_recherche(cible, sources)
    par_id = {s["id"]: s for s in sources}
    lignes = ["# Liens pour : %s" % (terme_de_recherche(cible) or "(cible non précisée)"), ""]
    auto = [l for l in liens if l["automatisable"]]
    manuel = [l for l in liens if not l["automatisable"]]
    if auto:
        lignes += ["## Téléchargeables par le skill (HEAD puis téléchargement)", ""]
        lignes += ["- [%s : %s](%s)" % (l["nom"], l["note"], l["url"]) for l in auto]
        lignes.append("")
    lignes += ["## À ouvrir à la main", ""]
    courant = None
    for l in manuel:
        if l["source"] != courant:
            courant = l["source"]
            lignes.append("**%s** (%s)" % (l["nom"], ", ".join(ACCES_LISIBLE.get(a, a) for a in par_id[courant].get("acces", []))))
        lignes.append("- [%s](%s)" % (l["note"], l["url"]))
    lignes += ["", "Contrôlez la page de garde (niveau, code, session, paper) avant de me déposer le PDF dans `trous/en` ou `trous/fr`."]
    return "\n".join(lignes) + "\n"
