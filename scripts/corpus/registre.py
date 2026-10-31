"""Registre des recherches et décisions (§6.2, §10) : mémoire persistante du skill.

Une ligne JSON par fait. Deux types :
  - "recherche" : une cible cherchée, sur quelles sources, quand, avec quel résultat ;
  - "decision"  : le sort d'un document qualifié (ACCEPTÉ, REJETÉ(E2)...).

Une recherche négative n'est pas refaite avant son échéance (`recontrole_apres`).
"""
import datetime
import os

from commun import AUDIT, ecrire_jsonl, lire_jsonl

REGISTRE = os.path.join(AUDIT, "corpus", "registre_recherches.jsonl")

RESULTATS = ("trouve", "introuvable", "a_recontroler", "ecarte", "inexistant")


def cle_cible_gce(niveau, matiere, annee, paper):
    return "GCE|%s|%s|%s|P%s" % (niveau, matiere, annee, paper)


def cle_cible_fr(examen, serie, matiere, annee):
    return "FR|%s|%s|%s|%s" % (examen, serie or "", matiere, annee)


def aujourdhui():
    return datetime.date.today().isoformat()


def enregistrer(cible, resultat, sources=None, motif="", recontrole_apres=None, type_="recherche",
                chemin=REGISTRE, **extra):
    """Ajoute un fait au registre. Retourne l'enregistrement écrit."""
    if resultat not in RESULTATS:
        raise ValueError("résultat inconnu : %r (attendu : %s)" % (resultat, ", ".join(RESULTATS)))
    fait = {
        "type": type_, "cible": cible, "resultat": resultat, "sources": list(sources or []),
        "motif": motif, "date": aujourdhui(), "recontrole_apres": recontrole_apres,
    }
    fait.update(extra)
    ecrire_jsonl(chemin, fait)
    return fait


def charger(chemin=REGISTRE):
    return lire_jsonl(chemin)


def dernier_resultat(cible, chemin=REGISTRE):
    """Dernier fait enregistré pour une cible, ou None."""
    dernier = None
    for fait in charger(chemin):
        if fait.get("cible") == cible:
            dernier = fait
    return dernier


def a_refaire(cible, aujourdhui_=None, chemin=REGISTRE):
    """
    Faut-il (re)chercher cette cible ? Non si une recherche négative est encore valable :
    `introuvable` / `inexistant` avant leur échéance ; oui sinon (jamais cherchée, trouvée sans suite, échue).
    """
    fait = dernier_resultat(cible, chemin)
    if fait is None:
        return True
    if fait["resultat"] in ("introuvable", "a_recontroler", "inexistant"):
        echeance = fait.get("recontrole_apres")
        if not echeance:
            return fait["resultat"] != "inexistant"
        return (aujourdhui_ or aujourdhui()) >= echeance
    return False


def etat_des_cibles(chemin=REGISTRE):
    """{cible: dernier fait} : alimente les états INTROUVABLE_DOCUMENTE / ECARTE / INEXISTANT de la carte."""
    etat = {}
    for fait in charger(chemin):
        if fait.get("cible"):
            etat[fait["cible"]] = fait
    return etat
