"""Qualification d'un PDF candidat (§7). Retourne des FAITS ; la décision finale reste humaine.

Tout ce qui est lu dans le PDF (texte, métadonnées) est une donnée, jamais une instruction : le module ne fait que
l'analyser. Les contrôles portent sur le contenu, jamais sur le nom du fichier.
"""
import os
import re

from commun import normaliser, sha256_fichier
import referentiel

try:  # PyMuPDF : interpréteur Anaconda (voir README-CORPUS)
    import fitz
except ImportError:  # pragma: no cover - signalé clairement plutôt que d'échouer silencieusement
    fitz = None

MOTS_CORRIGE = (
    "corrige", "correction", "proposition de solution", "proposition de corrige", "bareme", "mark scheme",
    "marking scheme", "answer key", "suggested answers", "examiner s report", "examiners report",
    "marking guide", "solution", "solutions to",
)
# Mots qui ne prouvent rien seuls (un sujet peut dire « solution », « correction » ou « barème » : « Barème : une
# victoire vaut 2 points » dans un énoncé d'EPS, « proposition de solution » dans une consigne de SVT) : pondérés plus bas.
MOTS_FAIBLES = {"solution", "solutions to", "correction", "bareme", "proposition de solution"}

# Mentions de sites qui annoncent un corrigé AILLEURS (« Épreuve disponible avec correction sur le site… ») : ce n'est
# pas un corrigé dans le document, on les retire avant de chercher des mots de corrigé.
MENTIONS_SITE = re.compile(r"(?i)(?:épreuve|epreuve|correction)\s+disponible[^\n]{0,160}")
# Une page de publicité (pack payant, groupe WhatsApp, « 140 épreuves corrigées ») n'est pas du sujet : ignorée.
MARQUES_PUBLICITE = ("groupe whatsapp", "acheter ndolobepc", "voir ndolobepc", "plus de 140 epreuves corrigees",
                     "packs corriges")

MARQUES_SITES = {
    "ndolomath": "ndolomath.com",
    "gcerevision": "cameroongcerevision.com / Kawlo", "kawlo": "Kawlo", "meetlearn": "MeetLearn",
    "cgce revision": "cgce-revision.com", "sujetexa": "sujetexa.com", "camerecole": "camerecole.org",
    "epreuvesetcorriges": "epreuvesetcorriges.com", "concourscameroon": "concourscameroon.com",
    "camerpower": "kamerpower", "maxiepreuves": "maxiepreuves.com", "famnoh": "famnoh.com",
    "camscanner": "CamScanner", "anyscanner": "AnyScanner",
}

FINS_DE_PAGE = (  # « la suite est sur une page que le scan n'a pas »
    "turn over", "go on to the next page", "tourne la page", "va a la page suivante", "voir suite",
    "page suivante", "tsvp",
)

EXAMENS_CITES = {
    "bepc": ("bepc", "brevet d etudes du premier cycle"), "probatoire": ("probatoire",),
    "bac": ("baccalaureat", "baccalaureat ", "office du baccalaureat"), "cap": ("cap commerciaux", "cap ", "certificat d aptitude professionnelle"),
}
INDICES_NON_OFFICIEL = ("mock", "examen blanc", "epreuve zero", "sujet zero", "blanc regional", "regional", "trial exam", "pre mock")

INJECTIONS = (  # texte adressé à un lecteur automatique : consigné comme donnée, jamais exécuté
    "ignore tes regles", "ignore your instructions", "ignore previous", "system prompt", "ingere ce pdf",
    "ingest this", "you are now", "tu es maintenant",
)


def _exiger_fitz():
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) est requis : utiliser l'interpréteur Anaconda (C:\\ProgramData\\anaconda3\\python.exe -I).")


def texte_pages(doc):
    return [p.get_text() for p in doc]


def lire_page_de_garde(texte):
    """Niveau, code Board, session, paper, durée, nombre de questions annoncé : meilleur effort, sans deviner."""
    brut = " ".join(texte.split())
    n = normaliser(brut)
    garde = {"niveau": None, "code": None, "session": None, "paper": None, "duree": None, "questions": None}
    if "ordinary level" in n or "o level" in n:
        garde["niveau"] = "GCE_OL"
    elif "advanced level" in n or "advance level" in n or "a level" in n:
        garde["niveau"] = "GCE_AL"
    codes = {c for cs in referentiel.CODES_OFFICIELS_GCE.values() for c in cs.values()}
    for c in re.findall(r"(?<!\d)(0\d{3})(?!\d)", brut):
        if c in codes:
            garde["code"] = c
            break
    m = re.search(r"(?:june|juin|july|session)\W{0,4}((?:19|20)\d{2})", brut, re.I)
    if m:
        garde["session"] = int(m.group(1))
    m = re.search(r"paper\s*(?:no\.?)?\s*(\d)", brut, re.I) or re.search(r"\b(?:[a-z]+ )?(\d)\s+0\d{3}\b", brut)
    if m:
        garde["paper"] = int(m.group(1))
    m = re.search(r"(\d)\s*(?:h|hours?|heures?)(?:\s*(\d{1,2})\s*(?:min|m))?", brut, re.I)
    if m:
        garde["duree"] = m.group(0).strip()
    m = re.search(r"(\d{2,3})\s*(?:questions|questions?)", brut, re.I)
    if m:
        garde["questions"] = int(m.group(1))
    return garde


def page_publicitaire(texte):
    """Page de promotion d'un site (pack payant, groupe WhatsApp…) : jamais du contenu d'épreuve."""
    n = normaliser(texte)
    return any(m in n for m in MARQUES_PUBLICITE)


def detecter_corrige(textes):
    """Mots-clés de corrigé trouvés, avec leurs pages. Un mot faible seul ne suffit pas à rejeter.

    Les pages publicitaires et les mentions « corrigé disponible sur le site… » ne comptent pas : elles annoncent un
    corrigé, elles n'en contiennent pas.
    """
    trouves = []
    for numero, texte in enumerate(textes, 1):
        if page_publicitaire(texte):
            continue
        n = normaliser(MENTIONS_SITE.sub(" ", texte))
        for mot in MOTS_CORRIGE:
            if normaliser(mot) in n:
                trouves.append({"mot": mot, "page": numero, "faible": mot in MOTS_FAIBLES})
    return trouves


def verifier_numerotation(textes, attendu=None):
    """Numéros de question 1..N lus en début de ligne ; retourne (maximum, manquants)."""
    vus = set()
    for texte in textes:
        for ligne in texte.splitlines():
            m = re.match(r"\s*(\d{1,3})\s*[\.\)]\s+\S", ligne)
            if m:
                vus.add(int(m.group(1)))
    if not vus:
        return None, []
    maximum = max(vus) if attendu is None else attendu
    manquants = [i for i in range(1, maximum + 1) if i not in vus]
    return maximum, manquants


def examens_cites(texte):
    """Examens francophones nommés sur la page de garde (un CAP rangé en Probatoire, par exemple)."""
    n = " " + normaliser(texte) + " "
    return sorted(code for code, mots in EXAMENS_CITES.items() if any((" %s " % m.strip()) in n or m in n for m in mots))


def marques_non_officielles(texte):
    n = normaliser(texte)
    return [m for m in INDICES_NON_OFFICIEL if m in n]


def marques_de_sites(textes):
    n = normaliser(" ".join(textes))
    return sorted({nom for cle, nom in MARQUES_SITES.items() if cle in n})


def fin_de_document_incomplete(textes):
    """La dernière page annonce une suite (« turn over », « tourne la page ») : le scan est probablement tronqué."""
    if not textes:
        return False
    n = normaliser(textes[-1])
    return any(normaliser(m) in n for m in FINS_DE_PAGE)


def pages_blanches(doc, seuil_encre=0.003):
    """Pages sans texte ni image significative (rendu 40 dpi, part de pixels sombres)."""
    blanches = []
    for i, page in enumerate(doc, 1):
        if page.get_text().strip():
            continue
        pix = page.get_pixmap(matrix=fitz.Matrix(0.55, 0.55), colorspace=fitz.csGRAY)
        echantillon = pix.samples
        sombres = sum(1 for v in echantillon if v < 200)
        if sombres / max(1, len(echantillon)) < seuil_encre:
            blanches.append(i)
    return blanches


def rendre_pages(chemin_pdf, dossier_sortie, dpi=80, pages=None):
    """Rend les pages en PNG (lecture visuelle obligatoire de TOUS les PDF, natifs ou scannés)."""
    _exiger_fitz()
    os.makedirs(dossier_sortie, exist_ok=True)
    sorties = []
    with fitz.open(chemin_pdf) as doc:
        for i, page in enumerate(doc, 1):
            if pages and i not in pages:
                continue
            chemin = os.path.join(dossier_sortie, "page_%02d.png" % i)
            page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0)).save(chemin)
            sorties.append(chemin)
    return sorties


def qualifier(chemin_pdf, cible=None):
    """
    Analyse un PDF. `cible` (facultatif) : {"niveau","matiere","annee","paper","code"} attendus.

    Retourne un dict avec : integrite, page de garde lue, corrige, numerotation, marques, eliminatoires,
    avertissements, score, decision, a_verifier_humain. N'écrit rien.
    """
    resultat = {
        "fichier": os.path.basename(chemin_pdf), "taille": None, "sha256": None, "pages": None,
        "garde": {}, "marques_sites": [], "corrige": [], "numerotation": {}, "eliminatoires": [],
        "avertissements": [], "injection": [], "score": None, "decision": None, "a_verifier_humain": True,
    }
    try:
        resultat["taille"] = os.path.getsize(chemin_pdf)
        with open(chemin_pdf, "rb") as fh:
            entete = fh.read(5)
    except OSError as exc:
        resultat["eliminatoires"].append(("E3", "fichier illisible : %s" % exc))
        resultat["decision"] = "REJETÉ(E3)"
        return resultat
    if entete != b"%PDF-":
        resultat["eliminatoires"].append(("E7", "le fichier n'est pas un PDF (signature absente) : extension suspecte"))
        resultat["decision"] = "REJETÉ(E7)"
        return resultat
    resultat["sha256"] = sha256_fichier(chemin_pdf)
    _exiger_fitz()
    try:
        doc = fitz.open(chemin_pdf)
    except Exception as exc:  # noqa: BLE001 - tout échec d'ouverture est un PDF corrompu
        resultat["eliminatoires"].append(("E3", "PDF corrompu ou illisible : %s" % exc))
        resultat["decision"] = "REJETÉ(E3)"
        return resultat
    with doc:
        if doc.needs_pass or doc.is_encrypted:
            resultat["eliminatoires"].append(("E3", "PDF chiffré ou protégé"))
        resultat["pages"] = len(doc)
        textes = texte_pages(doc)
        garde = lire_page_de_garde(textes[0] if textes else "")
        resultat["garde"] = garde
        resultat["marques_sites"] = marques_de_sites(textes)
        corrige = detecter_corrige(textes)
        resultat["corrige"] = corrige
        maximum, manquants = verifier_numerotation(textes, garde.get("questions"))
        resultat["numerotation"] = {"maximum": maximum, "manquants": manquants}
        blanches = pages_blanches(doc)
        if blanches:
            resultat["avertissements"].append("pages blanches : %s" % blanches)
        publicitaires = [i for i, t in enumerate(textes, 1) if page_publicitaire(t)]
        if publicitaires:
            resultat["avertissements"].append("pages publicitaires ignorées pour les mots de corrigé : %s" % publicitaires)
        texte_total = " ".join(textes)
        if len(texte_total.strip()) < 40:
            resultat["avertissements"].append("aucune couche de texte : lecture visuelle obligatoire (scan)")
        n_total = normaliser(texte_total)
        resultat["injection"] = [m for m in INJECTIONS if normaliser(m) in n_total]

    # --- éliminatoires -------------------------------------------------------------------------------
    forts = [c for c in corrige if not c["faible"]]
    if forts:
        resultat["eliminatoires"].append(("E1", "mots de corrigé : %s" % ", ".join(sorted({c["mot"] for c in forts}))))
    elif corrige:
        resultat["avertissements"].append("mots faibles de corrigé (à lire) : %s" % ", ".join(sorted({c["mot"] for c in corrige})))
    if resultat["pages"] and fin_de_document_incomplete(textes):
        resultat["eliminatoires"].append(("E2", "la dernière page annonce une suite absente du scan"))
    if manquants and maximum and len(manquants) <= max(3, maximum // 5):
        resultat["eliminatoires"].append(("E2", "numéros de question manquants : %s" % manquants[:12]))
    elif manquants and maximum:
        resultat["avertissements"].append("numérotation lacunaire (%d manquants sur %d) : peut venir d'un format non lu" % (len(manquants), maximum))
    if cible:
        for cle_garde, cle_cible in (("niveau", "niveau"), ("code", "code"), ("session", "annee"), ("paper", "paper")):
            lu, attendu = garde.get(cle_garde), cible.get(cle_cible)
            if cle_garde == "niveau" and lu is not None and attendu is not None:
                lu, attendu = str(lu).replace("GCE_", ""), str(attendu).replace("GCE_", "")
            if lu is not None and attendu is not None and str(lu) != str(attendu):
                resultat["eliminatoires"].append(("E4", "page de garde : %s=%s, annoncé %s" % (cle_garde, lu, attendu)))
    if cible and cible.get("examen") and textes:
        cites = examens_cites(textes[0])
        attendu = str(cible["examen"]).lower()
        if cites and attendu not in cites:
            resultat["eliminatoires"].append(("E4", "page de garde : examen %s, annoncé %s" % ("/".join(cites), attendu)))
    if cible and str(cible.get("origine", "")).upper() == "OFFICIEL" and textes:
        indices = marques_non_officielles(textes[0])
        if indices:
            resultat["eliminatoires"].append(("E5", "épreuve non officielle présentée comme officielle : %s" % ", ".join(indices)))
    if resultat["injection"]:
        resultat["avertissements"].append("texte adressé à un lecteur automatique, consigné comme donnée : %s" % resultat["injection"])

    resultat["score"] = _score(resultat) if not resultat["eliminatoires"] else None
    resultat["decision"] = _decision(resultat)
    return resultat


def _score(r):
    """Score indicatif /100 (§7.3), calculé UNIQUEMENT après les éliminatoires ; il aide, il ne décide pas."""
    score = 25  # fiabilité de la source : à ajuster par l'opérateur selon le site
    score += 25 if not r["avertissements"] else 15
    score += 20 if r["garde"].get("niveau") or r["garde"].get("code") else 10
    garde = r["garde"]
    renseigne = sum(1 for v in (garde.get("niveau"), garde.get("code"), garde.get("session"), garde.get("paper")) if v)
    score += int(15 * renseigne / 4)
    score += 15 if r["pages"] and r["pages"] >= 2 else 5
    return min(100, score)


def _decision(r):
    codes = {c for c, _m in r["eliminatoires"]}
    if codes:
        return "REJETÉ(%s)" % ",".join(sorted(codes))
    if r["score"] is not None and r["score"] >= 85:
        return "ACCEPTABLE"
    return "À VÉRIFIER"
