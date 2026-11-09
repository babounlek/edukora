"""Découpe d'une COMPILATION de sujets en un PDF par épreuve (mode QUALIFICATION).

Une compilation (par exemple « Tout le BEPC de 2026 à 2020 », ~140 épreuves en 297 pages) ne se qualifie pas d'un
bloc : chaque épreuve a sa matière, son année, ses éventuels doublons. Le découpage repose sur les PAGES DE GARDE :
une page de garde annonce « Épreuve d'<matière> », puis l'examen et l'année. Les pages publicitaires (pack payant,
groupe WhatsApp) sont retirées de chaque épreuve.

N'écrit que dans le dossier de sortie demandé, jamais dans `trous/` ni dans `ingest/cm/`. Les PDF produits portent
le filigrane et les mentions du site d'origine : ils ne sont PAS le document officiel.
"""
import json
import os
import re

import qualification
from commun import normaliser, sha256_fichier, slug

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

# Valeur par défaut : pages de garde Ndolomath « Troisieme / Epreuve d'Allemand / BEPC 2026 ». Un autre format se
# décrit par `--garde` : une expression avec les groupes nommés (?P<matiere>…) et (?P<annee>…).
GARDE_PAR_DEFAUT = r"Epreuve\s+d.\s*(?P<matiere>[^\n]+?)\s*\n?\s*(?P<examen>BEPC|PROBATOIRE|BAC)\s*(?P<annee>(?:19|20)\d{2})"


def trouver_epreuves(doc, garde=GARDE_PAR_DEFAUT):
    """Liste d'épreuves [{matiere, examen, annee, pages: [numéros 1-based], pages_publicitaires: [...]}]."""
    motif = re.compile(garde, re.IGNORECASE)
    epreuves, courante = [], None
    for numero, page in enumerate(doc, 1):
        texte = page.get_text()
        m = motif.search(texte)
        if m:
            groupes = m.groupdict()
            courante = {"matiere": " ".join(groupes["matiere"].split()), "examen": (groupes.get("examen") or "").upper(),
                        "annee": int(groupes["annee"]), "pages": [], "pages_publicitaires": []}
            epreuves.append(courante)
        if courante is None:
            continue
        if qualification.page_publicitaire(texte):
            courante["pages_publicitaires"].append(numero)
        else:
            courante["pages"].append(numero)
    return epreuves


def nom_fichier(epreuve):
    return "-".join(x for x in (slug(epreuve["examen"]), slug(epreuve["matiere"]), str(epreuve["annee"])) if x) + ".pdf"


def decouper(chemin_pdf, dossier_sortie=None, garde=GARDE_PAR_DEFAUT):
    """
    Retourne la liste des épreuves trouvées. Si `dossier_sortie` est donné, écrit un PDF par épreuve et un
    `decoupes.json` (sha256 de la compilation, pages source, nom de sortie) ; sinon, simple inventaire.
    """
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) est requis : utiliser l'interpréteur Anaconda (C:\\ProgramData\\anaconda3\\python.exe -I).")
    with fitz.open(chemin_pdf) as doc:
        epreuves = trouver_epreuves(doc, garde)
        vus = {}
        for e in epreuves:
            base = nom_fichier(e)
            vus[base] = vus.get(base, 0) + 1
            e["fichier"] = base if vus[base] == 1 else base[:-4] + "-%d.pdf" % vus[base]
            e["pages_source"] = "%d-%d" % (e["pages"][0], e["pages"][-1]) if e["pages"] else ""
        if dossier_sortie:
            os.makedirs(dossier_sortie, exist_ok=True)
            for e in epreuves:
                if not e["pages"]:
                    continue
                sortie = fitz.open()
                for numero in e["pages"]:
                    sortie.insert_pdf(doc, from_page=numero - 1, to_page=numero - 1)
                sortie.save(os.path.join(dossier_sortie, e["fichier"]))
                sortie.close()
            with open(os.path.join(dossier_sortie, "decoupes.json"), "w", encoding="utf-8") as fh:
                json.dump({"source": os.path.basename(chemin_pdf), "sha256_source": sha256_fichier(chemin_pdf),
                           "epreuves": epreuves}, fh, ensure_ascii=False, indent=2)
    return epreuves
