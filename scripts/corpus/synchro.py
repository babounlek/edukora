"""Mode SYNCHRONISATION : copie les documents ACCEPTÉS vers la zone lue par la chaîne d'ingestion existante.

Copie (jamais déplacement) vers `backend/ingest/_telechargements_<nom>_<date>/`. Refuse tout document dont la fiche
de provenance n'est pas ACCEPTABLE/ACCEPTÉ ou dont la lecture humaine (page de garde + contrôles) n'est pas déclarée.
S'arrête avant `prepare -Approuver` : l'approbation et la publication restent un geste de l'utilisateur.
"""
import os
import shutil

import registre
from commun import INGEST, lire_jsonl, sha256_fichier

DECISIONS_ADMISES = ("ACCEPTÉ", "ACCEPTABLE")


def fiche_de(zone, nom_fichier):
    """Dernière fiche de provenance d'un fichier de la zone, ou None."""
    fiche = None
    for f in lire_jsonl(os.path.join(zone, "provenance.jsonl")):
        if f.get("fichier") == nom_fichier:
            fiche = f
    return fiche


def synchroniser(chemins_pdf, nom_lot, lecture_validee=False, date=None, ingest=INGEST):
    """Copie les PDF ACCEPTÉS. Retourne (copies, refus) ; n'écrit jamais ailleurs que dans `_telechargements_*`."""
    if not lecture_validee:
        raise PermissionError(
            "Un document ACCEPTÉ n'est jamais ingéré sans lecture humaine de sa page de garde et de la liste des "
            "contrôles : relancer avec --lecture-validee une fois cette lecture faite.")
    cible = os.path.join(ingest, "_telechargements_%s_%s" % (nom_lot, date or registre.aujourdhui()))
    copies, refus = [], []
    for chemin in chemins_pdf:
        zone, nom = os.path.dirname(os.path.abspath(chemin)), os.path.basename(chemin)
        fiche = fiche_de(zone, nom)
        if not fiche:
            refus.append((nom, "aucune fiche de provenance : document non qualifié"))
            continue
        if fiche.get("decision") not in DECISIONS_ADMISES:
            refus.append((nom, "décision %r : seuls les documents ACCEPTÉS sont copiés" % fiche.get("decision")))
            continue
        if fiche.get("sha256") and sha256_fichier(chemin) != fiche["sha256"]:
            refus.append((nom, "le fichier ne correspond plus à sa fiche (SHA-256 différent)"))
            continue
        os.makedirs(cible, exist_ok=True)
        destination = os.path.join(cible, nom)
        if os.path.exists(destination):
            if sha256_fichier(destination) == sha256_fichier(chemin):
                copies.append(destination)  # idempotent : déjà copié
                continue
            refus.append((nom, "un fichier différent de même nom existe déjà dans %s" % cible))
            continue
        shutil.copy2(chemin, destination)
        copies.append(destination)
    return copies, refus
