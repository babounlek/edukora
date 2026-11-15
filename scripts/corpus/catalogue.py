"""Catalogues des sources : on moissonne l'INDEX des sites (titres, dates, liens), jamais les PDF.

Un catalogue = `backend/ingest/_audit/corpus/catalogues/<source>.jsonl`, une ligne par article :
    {"source", "id", "date", "titre", "lien", "categories"}
Le moissonnage est incrémental (seuls les articles parus depuis la dernière lecture sont demandés).
Les accès réseau passent par `curl` (client du système, vérification TLS active) : le Python d'Anaconda
rejette le certificat de sujetexa.com (OpenSSL 1.1.1q), ce n'est pas un contournement.

`analyser_titre` déduit d'un titre : examen, matière, séries, année, nature (officiel, corrigé, blanc...).
`rapprocher` croise le catalogue avec la matrice de la cartographie et classe chaque entrée.
"""
import csv
import html
import json
import os
import re
import subprocess
import time

import registre
from commun import AUDIT, ecrire_jsonl, lire_jsonl, normaliser

CATALOGUES = os.path.join(AUDIT, "corpus", "catalogues")
PAUSE = 2.0  # secondes entre deux requêtes d'un même site

# --- analyse de titre ---------------------------------------------------------------------------

MATIERES = (  # (motif sur le titre normalisé, code de la matrice) ; le premier qui correspond gagne
    (r"\bmathematiques?\b|\bmaths?\b", "MATHS"),
    (r"\bphysique chimie\b|\bpct\b", "PHYSIQUE_CHIMIE"),
    (r"\bphysiques?\b", "PHYSIQUE"),
    (r"\bchimie\b", "CHIMIE"),
    (r"\bsvt|sciences de la vie", "SVT"),
    (r"\blitterature\b", "LITTERATURE"),
    (r"\blangue francaise\b|\bfrancais\b|\bexpression ecrite\b", "FRANCAIS"),
    (r"\bphilosophie\b", "PHILOSOPHIE"),
    (r"\bhistoire\b", "HISTOIRE"),
    (r"\bgeographie\b", "GEOGRAPHIE"),
    (r"\becm\b|education civique|education a la citoyennete", "EDUCATION_CIVIQUE"),
    (r"\banglais\b|\benglish\b", "ANGLAIS"),
    (r"\ballemand\b", "ALLEMAND"),
    (r"\bespagnol\b", "ESPAGNOL"),
    (r"\binformatique\b", "INFORMATIQUE"),
    (r"\beps\b|education physique", "EPS"),
    (r"\bmusique\b", "MUSIQUE"),
    (r"\btravail manuel\b|\btm\b", "TRAVAIL_MANUEL"),
    (r"\bsciences\b", "SCIENCES"),
    (r"\beconomie\b", "ECONOMIE"),
)
MARQUEURS_ETABLISSEMENT = (
    "college", "lycee", "groupe", "complexe", "collectif", "institut", "ecole", "centre", "externat",
    "sequence", "trimestre", "devoir", "evaluation", "controle continu", "ds n", "ds ", "travaux diriges",
    "feuille de", "repetition", "fordi", "prof ", "examinateur", "propose par", "proposee par",
)
MARQUEURS_BLANC = ("blanc", "regional", "provincial", "dres ", "dres de", "preparation", "mock", "simule")
SERIES_FILTRE = re.compile(r"\b(a[1-5]?|abi|c|d|e|ti|f\d?|g\d?|esf|sh|ac|acc|aca|cg|stt|bt|ih)\b")


def _series(texte_norm):
    """Séries ramenées aux séries de la matrice (A, C, D, E, TI). Les séries techniques sont ignorées."""
    morceau = texte_norm
    m = re.search(r"\b(?:serie|series|probatoire|baccalaureat|bac)\b(.*)", morceau)
    if m:
        morceau = m.group(1)
    morceau = re.sub(r"\bsession\b.*", "", morceau)
    trouvees = []
    for s in SERIES_FILTRE.findall(morceau):
        if re.fullmatch(r"a[1-5]?|abi|sh|ac|aca", s):
            s = "A"
        elif s in ("c", "d", "e", "ti"):
            s = s.upper()
        else:
            continue
        if s not in trouvees:
            trouvees.append(s)
    return trouvees


def analyser_titre(titre):
    """Retourne examen, matiere, series, annee, nature, partie (theorique|pratique|None)."""
    brut = html.unescape(str(titre or ""))
    n = normaliser(brut)
    r = {"titre": brut, "examen": None, "matiere": None, "series": [], "annee": None, "nature": "autre", "partie": None}
    if re.search(r"\bprobatoire\b", n):
        r["examen"] = "PROBATOIRE"
    elif re.search(r"\bbaccalaureat\b|\bbac\b", n):
        r["examen"] = "BAC"
    elif re.search(r"\bbepc\b|\bbrevet\b", n):
        r["examen"] = "BEPC"
    for motif, code in MATIERES:
        if re.search(motif, n):
            r["matiere"] = code
            break
    if re.search(r"\bpratique\b", n):
        r["partie"] = "pratique"
    elif re.search(r"\btheorique\b", n):
        r["partie"] = "theorique"
    session = re.search(r"\bsession (?:de )?(?:\w+ )?((?:19|20)\d{2})\b", n)
    annees = re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)", n)
    plage = re.search(r"(?<!\d)((?:19|20)\d{2}) ?(?:/|-| )((?:19|20)\d{2})(?!\d)", n)
    if session:
        r["annee"] = int(session.group(1))
    elif annees and not plage:
        r["annee"] = int(annees[-1])
    if r["examen"] in ("BAC", "PROBATOIRE"):
        r["series"] = _series(n)
    # nature : on part du plus restrictif
    avec_corrige = bool(re.search(r"\bcorrige\b|\bcorrection\b|proposition de (?:corrige|solution)|\bbareme\b", n))
    if re.search(r"cote d.?ivoire|\bsenegal\b|\bbenin\b|\btogo\b|\bmali\b|burkina|\bgabon\b|\btchad\b|\bcongo\b|\bguinee\b"
                 r"|\bniger\b|madagascar|\bmaroc\b|algerie|tunisie|\bhaiti\b|\brdc\b|centrafrique", n):
        r["nature"] = "autre_pays"
    elif re.search(r"\bfascicules?\b|anciennes epreuves|compilation|\btoutes? les epreuves\b", n):
        r["nature"] = "fascicule"
    elif re.search(r"\bcorrige harmonise\b|^\W*corrige\b|\bcorrection de\b", n) and not re.search(r"\+ ?corrige", brut.lower()):
        r["nature"] = "corrige"
    elif re.search(r"\bepreuve zero\b", n):
        r["nature"] = "zero"
    elif any(m in n for m in MARQUEURS_ETABLISSEMENT) or "blanc" in n:
        r["nature"] = "blanc_ou_etablissement"
    elif any(m in n for m in MARQUEURS_BLANC):
        r["nature"] = "blanc_ou_etablissement"
    elif r["examen"] and r["matiere"] and r["annee"]:  # titre court sans "session" (anciens dépôts : « maths bac C 2019 »)
        r["nature"] = "officiel_avec_corrige" if avec_corrige else "officiel"
    if r["examen"] == "BEPC" and r["matiere"] == "PHYSIQUE_CHIMIE":
        r["matiere"] = "PHYSIQUE_CHIMIE_TECH"
    return r


# --- moissonnage sujetexa (API WordPress) -------------------------------------------------------------

def _curl_json(url):
    p = subprocess.run(["curl", "-s", "-S", "-m", "90", "-w", "\n%{http_code}", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    corps, _, code = p.stdout.rpartition("\n")
    return int(code or 0), corps


def moissonner_sujetexa(chemin=None, plein=False, par_page=100, pause=PAUSE, limite_pages=None, log=print):
    """Ajoute au catalogue les articles parus depuis la dernière lecture. Retourne le nombre d'ajouts."""
    chemin = chemin or os.path.join(CATALOGUES, "sujetexa.jsonl")
    existants = {} if plein else {e["id"]: e for e in lire_jsonl(chemin)}
    apres = ""
    if existants:
        derniere = max(e["date"] for e in existants.values())
        apres = "&after=" + derniere[:10] + "T00:00:00"  # marge d'un jour : dédoublonné par id
    nouveaux, page = [], 1
    while limite_pages is None or page <= limite_pages:
        url = ("https://sujetexa.com/wp-json/wp/v2/posts?per_page=%d&page=%d&orderby=date&order=desc"
               "&_fields=id,date,link,title,categories%s" % (par_page, page, apres))
        code, corps = _curl_json(url)
        if code == 400:  # page au-delà de la dernière
            break
        if code != 200:
            raise RuntimeError("sujetexa : HTTP %s sur la page %d" % (code, page))
        lot = json.loads(corps)
        if not lot:
            break
        for p in lot:
            if p["id"] not in existants:
                e = {"source": "sujetexa", "id": p["id"], "date": p["date"][:10],
                     "titre": html.unescape(p["title"]["rendered"]).strip(), "lien": p["link"],
                     "categories": p["categories"]}
                existants[p["id"]] = e
                nouveaux.append(e)
        log("sujetexa page %d : %d articles lus, %d nouveaux au total" % (page, len(lot), len(nouveaux)))
        if len(lot) < par_page:
            break
        page += 1
        time.sleep(pause)
    if nouveaux:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        for e in sorted(nouveaux, key=lambda x: x["id"]):
            ecrire_jsonl(chemin, e)
    return len(nouveaux)


# --- moissonnage Ndolomath (inventaire dans la page de rubrique) ------------------------------------------

RUBRIQUES_NDOLOMATH = (  # (examen, série, URL de rubrique)
    ("BEPC", "", "https://www.ndolomath.com/tous-les-sujets-du-bepc/"),
    ("PROBATOIRE", "A", "https://www.ndolomath.com/tous-les-sujets-de-probatoire-a/"),
    ("PROBATOIRE", "C", "https://www.ndolomath.com/toutes-les-epreuves-de-probatoire-c/"),
    ("PROBATOIRE", "D", "https://www.ndolomath.com/tous-les-sujets-de-probatoire-d/"),
    ("BAC", "A", "https://www.ndolomath.com/toutes-les-epreuves-de-bac-a/"),
    ("BAC", "C", "https://www.ndolomath.com/les-epreuves-de-bac-c/"),
    ("BAC", "D", "https://www.ndolomath.com/toutes-les-epreuves-du-bac-d/"),
)


def extraire_liens_ndolomath(page_html):
    """Objets `const ndolo…Links={…}` des scripts base64 de la page : {nom_objet: {matière: {année: {view, pdf}}}}.
    Le texte décodé est lu comme donnée (jamais exécuté)."""
    import base64
    trouves = {}
    for m in re.finditer(r"base64,([A-Za-z0-9+/=]{200,})", page_html):
        try:
            code = base64.b64decode(m.group(1)).decode("utf-8", "replace")
        except ValueError:
            continue
        for d in re.finditer(r"const (ndolo\w*Links)=", code):
            debut = d.end()
            profondeur, fin = 0, None
            for i in range(debut, len(code)):
                if code[i] == "{":
                    profondeur += 1
                elif code[i] == "}":
                    profondeur -= 1
                    if profondeur == 0:
                        fin = i + 1
                        break
            if fin:
                try:
                    trouves[d.group(1)] = json.loads(code[debut:fin])
                except ValueError:
                    pass
    return trouves


def entrees_ndolomath(examen, serie, liens, date=""):
    """Une entrée par case dont le lien PDF est renseigné. Titre normalisé pour `analyser_titre`."""
    sorties = []
    for matiere, annees in liens.items():
        for annee, fichiers in annees.items():
            pdf = (fichiers or {}).get("pdf") or ""
            if not pdf:
                continue
            titre = "%s %s %s session %s" % (matiere, examen, ("série " + serie) if serie else "", annee)
            mois = re.search(r"/uploads/(\d{4})/(\d{2})/", pdf)
            sorties.append({"source": "ndolomath", "id": "%s-%s-%s-%s" % (examen, serie, matiere, annee),
                            "date": ("%s-%s" % mois.groups()) if mois else date, "titre": re.sub(r"\s+", " ", titre).strip(),
                            "lien": pdf, "categories": [], "retranscription": True})
    return sorties


def moissonner_ndolomath(chemin=None, pause=PAUSE, log=print):
    """Relit les rubriques (7 pages) et réécrit le catalogue (petit : relecture complète à chaque fois)."""
    chemin = chemin or os.path.join(CATALOGUES, "ndolomath.jsonl")
    toutes = []
    for examen, serie, url in RUBRIQUES_NDOLOMATH:
        p = subprocess.run(["curl", "-s", "-S", "-L", "-m", "60", url], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        objets = extraire_liens_ndolomath(p.stdout)
        liens = {k: v for k, v in objets.items() if "compilation" not in k.lower()}
        if not liens:
            log("ndolomath %s %s : aucun inventaire lu (page vide ou modifiée)" % (examen, serie))
        for nom, contenu in liens.items():
            toutes += entrees_ndolomath(examen, serie, contenu)
        log("ndolomath %s %s : %d fichiers" % (examen, serie, sum(1 for e in toutes if e["id"].startswith("%s-%s-" % (examen, serie)))))
        time.sleep(pause)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fh:
        for e in toutes:
            fh.write(json.dumps(e, ensure_ascii=False) + chr(10))
    return len(toutes)


# --- moissonnage sujetexam.com (pages HTML /?p=N, pas d'API) -------------------------------------------------

_CARTE_SUJETEXAM = re.compile(
    r'<a href="(/epreuve/(\d+)-[^"]+/)" class="card-title[^"]*">(.*?)</a>(.*?)<div class="card-actions">', re.S)


def _reparer_mojibake(texte):
    """Certains titres de la source sont doublement encodés (« Ã‰preuve », « CollÃ¨ge »)."""
    if "Ã" in texte or "â€" in texte:
        try:
            return texte.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return texte
    return texte


def extraire_cartes_sujetexam(page_html):
    """Cartes d'une page de liste : [{id, titre, lien, date}]. La date affichée est celle de la mise en ligne
    (souvent celle du jour pour de vieux sujets) : jamais un millésime."""
    cartes = []
    for m in _CARTE_SUJETEXAM.finditer(page_html):
        d = re.search(r"(\d{2})/(\d{2})/(\d{4})", m.group(4))
        cartes.append({"source": "sujetexam", "id": int(m.group(2)),
                       "date": ("%s-%s-%s" % (d.group(3), d.group(2), d.group(1))) if d else "",
                       "titre": re.sub(r"\s+", " ", _reparer_mojibake(html.unescape(re.sub(r"<[^>]+>", "", m.group(3))))).strip(),
                       "lien": "https://sujetexam.com" + m.group(1), "categories": []})
    return cartes


def moissonner_sujetexam(chemin=None, plein=False, pause=1.5, limite_pages=None, log=print):
    """Lit les pages de liste (du plus récent au plus ancien). Incrémental : s'arrête à la première page
    dont toutes les fiches sont déjà connues. Retourne le nombre d'ajouts."""
    chemin = chemin or os.path.join(CATALOGUES, "sujetexam.jsonl")
    existants = {} if plein else {e["id"]: e for e in lire_jsonl(chemin)}
    nouveaux, page, total = [], 1, None
    while limite_pages is None or page <= limite_pages:
        for essai in range(3):  # une coupure réseau (code 0) se retente ; un refus (403...) non
            code, corps = _curl_json("https://sujetexam.com/?p=%d" % page)
            if code != 0:
                break
            time.sleep(10 * (essai + 1))
        if code != 200:
            raise RuntimeError("sujetexam : HTTP %s sur la page %d (arrêt, ne pas insister)" % (code, page))
        if total is None:
            dernieres = [int(n) for n in re.findall(r'class="page-numbers" href="/\?p=(\d+)"', corps)]
            total = max(dernieres) if dernieres else page
        cartes = extraire_cartes_sujetexam(corps)
        if not cartes:
            break
        neufs = [c for c in cartes if c["id"] not in existants]
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        for c in sorted(neufs, key=lambda x: x["id"]):  # écrit page par page : une coupure ne perd rien
            existants[c["id"]] = c
            nouveaux.append(c)
            ecrire_jsonl(chemin, c)
        log("sujetexam page %d/%s : %d fiches, %d nouvelles" % (page, total, len(cartes), len(nouveaux)))
        if not neufs and not plein:
            break
        page += 1
        if page > total:
            break
        time.sleep(pause)
    return len(nouveaux)


# --- rapprochement avec la matrice ----------------------------------------------------------------

def charger_matrice(chemin_tsv):
    with open(chemin_tsv, encoding="utf-8", newline="") as fh:
        return [l for l in csv.DictReader(fh, delimiter="\t") if l["systeme"] == "fr"]


def _index_matrice(lignes):
    return {(l["examen"], l["serie"], l["matiere"], str(l["annee"])): l for l in lignes}


NATURES_SUJET = ("officiel", "officiel_avec_corrige", "zero")


def rapprocher(entrees, lignes_matrice, annee_min=2019, registre_chemin=None):
    """Classe chaque entrée de catalogue exploitable. Retourne une liste de dicts."""
    index = _index_matrice(lignes_matrice)
    derniers = {}
    for fait in (registre.charger(registre_chemin) if registre_chemin else registre.charger()):
        derniers[fait.get("cible")] = fait
    sorties = []
    for e in entrees:
        a = analyser_titre(e["titre"])
        if not (a["examen"] and a["matiere"] and a["annee"] and a["annee"] >= annee_min):
            continue
        if a["nature"] not in NATURES_SUJET + ("corrige",):
            continue
        series = a["series"] if a["examen"] != "BEPC" else [""]
        if a["examen"] != "BEPC" and not series:
            continue
        for s in series:
            ligne = index.get((a["examen"], s, a["matiere"], str(a["annee"])))
            if ligne is None:
                classe = "hors_matrice"
            elif a["nature"] == "corrige":
                classe = "corrige_seul_case_manquante" if ligne["etat"] == "MANQUANT" else "corrige_case_deja_couverte"
            elif ligne["etat"] == "MANQUANT":
                if a["nature"] == "zero":
                    classe = "epreuve_zero_case_manquante"
                elif any(l["examen"] == ligne["examen"] and l["matiere"] == ligne["matiere"] and str(l["annee"]) == str(ligne["annee"])
                         and l["serie"] != ligne["serie"] and l["etat"] != "MANQUANT" for l in lignes_matrice):
                    classe = "serie_a_rattacher_probable"  # même épreuve déjà en base pour une autre série : sujet commun ?
                else:
                    classe = "candidat_nouveau"
            else:
                classe = "deja_en_base"
            cible = registre.cle_cible_fr(a["examen"].lower(), s, a["matiere"], a["annee"])
            dernier = derniers.get(cible)
            sorties.append({
                "classe": classe, "examen": a["examen"], "serie": s, "matiere": a["matiere"], "annee": a["annee"],
                "partie": a["partie"], "nature": a["nature"], "titre": a["titre"], "date": e["date"], "lien": e["lien"],
                "source": e["source"], "registre": (dernier or {}).get("resultat"),
            })
            if sorties[-1]["classe"] == "candidat_nouveau" and sorties[-1]["registre"] in ("inexistant", "trouve", "ecarte"):
                sorties[-1]["classe"] = "deja_tranche_au_registre"
    return sorties


def ecrire_rapprochement(sorties, dossier, date):
    os.makedirs(dossier, exist_ok=True)
    tsv = os.path.join(dossier, "rapprochement_%s.tsv" % date)
    champs = ["classe", "examen", "serie", "matiere", "annee", "partie", "nature", "registre", "source", "date", "titre", "lien"]
    with open(tsv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=champs, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(sorties, key=lambda s: (s["classe"], s["examen"], s["annee"], s["matiere"], s["serie"])))
    comptes = {}
    for s in sorties:
        comptes[s["classe"]] = comptes.get(s["classe"], 0) + 1
    md = os.path.join(dossier, "rapprochement_%s.md" % date)
    with open(md, "w", encoding="utf-8") as fh:
        fh.write("# Rapprochement catalogue / matrice - %s\n\n" % date)
        for k, v in sorted(comptes.items()):
            fh.write("- %s : %d\n" % (k, v))
        for classe, titre in (("candidat_nouveau", "Candidats nouveaux (case manquante, sujet officiel trouvé, non tranché au registre)"),
                              ("serie_a_rattacher_probable", "Même épreuve déjà en base pour une autre série (sujet commun probable : rattachement à confirmer sur la page de garde)"),
                              ("epreuve_zero_case_manquante", "Épreuve zéro seulement (ne comble pas la case)"),
                              ("deja_tranche_au_registre", "Sujet vu mais case déjà tranchée au registre (trouvé, inexistant ou écarté)"),
                              ("corrige_seul_case_manquante", "Corrigé trouvé, sujet à chercher (case manquante)"),
                              ("hors_matrice", "Hors matrice (série ou matière non attendue : à examiner)")):
            lignes = [s for s in sorties if s["classe"] == classe]
            fh.write("\n## %s (%d)\n\n" % (titre, len(lignes)))
            for s in sorted(lignes, key=lambda s: (s["examen"], s["annee"], s["matiere"], s["serie"])):
                fh.write("- %s %s %s %s%s | %s | %s | %s | %s%s\n" % (
                    s["examen"], s["serie"] or "-", s["matiere"], s["annee"], (" " + s["partie"]) if s["partie"] else "",
                    s["source"], s["date"], s["titre"][:90], s["lien"], (" | registre : " + s["registre"]) if s["registre"] else ""))
    return tsv, md
