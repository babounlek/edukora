#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner de lot pour le Mode Quiz edukora.

Pilote le passage `_batch_<pays>.json` -> `<pays>/<competence_slug>.json`, cote
deterministe uniquement : detection de ce qui reste a faire, validation de ce qui a
ete produit, journal d'etat. La generation elle-meme n'est PAS ici : elle est faite
par le skill `concepteur-quiz-competence`, une competence par contexte neuf.

Pourquoi un script plutot qu'une simple boucle "le fichier existe ?" :

- un fichier peut exister et etre invalide, tronque, ou vide (run interrompu) ; le
  seul critere fiable est "lisible + JSON valide + tableau non vide + conforme au
  schema d'ingestion" ;
- le slug ne doit etre calcule qu'a un seul endroit, sinon la detection et
  l'ecriture divergent sur les accents, apostrophes et parentheses ;
- `external_id` est la cle d'idempotence de `quiz.ingestion.ingest_competence_item` :
  une collision entre deux lots fait silencieusement ignorer des items a l'ingestion,
  ca ne se voit qu'en base. On la detecte ici, avant.

Le journal `_state_<pays>.jsonl` porte l'extension .jsonl a dessein :
`quiz.ingestion.run_ingestion` fait un `rglob("*.json")` sur l'arbre `_quiz/`, donc
tout .json depose sous `_quiz/<pays>/` est traite comme un lot d'items. Un manifeste
.json y serait ingere par erreur.

Usage :
    python _quiz_batch.py status  [--pays cm]
    python _quiz_batch.py next    [--pays cm] [--n 1]
    python _quiz_batch.py validate <fichier.json> --competence "similitude directe" [--pays cm]
    python _quiz_batch.py journal --competence "similitude directe" --statut ok [--pays cm]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------------
# Referentiel
# --------------------------------------------------------------------------------

REQUIRED_KEYS = ("theme", "matiere", "cursus", "enonce_markdown", "corrige_markdown")
DIFFICULTES = ("FAIBLE", "MOYENNE", "ELEVEE")

# Renvois qui pointent forcement HORS de l'item : un CompetenceItem est servi seul,
# ces formulations le rendent structurellement insoluble. Bloquant.
RENVOIS_BLOQUANTS = [
    r"questions?\s+pr[ée]c[ée]dentes?",
    r"\bpartie\s+[A-D]\b",
    r"d'apr[èe]s\s+(le|les)\s+r[ée]sultats?",
    r"(obtenu|[ée]tabli|d[ée]montr[ée]|vu)e?s?\s+(plus\s+haut|pr[ée]c[ée]demment)",
    r"\b(voir|cf\.?)\s+(la\s+)?question",
    r"le\s+texte\s+cit[ée]\s+plus\s+haut",
    r"du\s+document\s+(pr[ée]c[ée]dent|suivant)",
    r"\bl'annexe\b",
]

# Renvois directionnels et supports visuels : legitimes quand le referent est DANS
# l'enonce (options enumerees juste apres, texte reproduit en entier), fautifs sinon.
# Aucune regex ne peut trancher - donc avertissement a relire, jamais blocage.
RENVOIS_SUSPECTS = [
    r"ci-dessus",
    r"ci-dessous",
    r"ci-contre",
    r"ci-apr[èe]s",
    r"\bla\s+figure\b",
    r"\ble\s+sch[ée]ma\b",
    r"\ble\s+graphique\b",
    r"\bla\s+carte\b",
    r"\ble\s+tableau\s+suivant\b",
    r"\bla\s+courbe\s+(suivante|repr[ée]sent[ée]e\s+ci)",
]

# Enumeration lettree dans le corps de l'enonce : l'interface du quiz affiche
# systematiquement des boutons lettres a partir de `choix`, jamais a partir du texte.
OPTIONS_DANS_ENONCE = re.compile(r"^\s*(?:\*\*)?[A-E][\)\.]\s", re.MULTILINE)

SHINGLE = 10  # longueur en mots des n-grammes servant a detecter la recopie


# --------------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------------

def slugify(libelle: str) -> str:
    """Unique source de verite du nom de fichier d'une competence."""
    texte = unicodedata.normalize("NFD", str(libelle or ""))
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    texte = texte.lower().replace("'", " ").replace("’", " ")
    texte = re.sub(r"[^a-z0-9]+", "-", texte)
    return texte.strip("-")


def _mots(texte: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ſ0-9]+", (texte or "").lower())


def _shingles(texte: str, n: int = SHINGLE) -> set[str]:
    mots = _mots(texte)
    return {" ".join(mots[i:i + n]) for i in range(max(0, len(mots) - n + 1))}


def _cursus_cle(cursus) -> set:
    cle = set()
    for entree in cursus or []:
        if isinstance(entree, dict):
            cle.add((str(entree.get("examen") or "").lower(),
                     str(entree.get("serie") or "").upper()))
    return cle


# --------------------------------------------------------------------------------
# Validation d'un lot
# --------------------------------------------------------------------------------

def valider_lot(items, requete, external_ids_ailleurs=None):
    """
    Retourne (erreurs, avertissements). Un lot n'est ecrit sur disque que si
    `erreurs` est vide - un lot plus court mais fiable vaut mieux qu'un lot complet
    dont deux items sont bancals (exigence du SKILL.md).
    """
    erreurs, avertis = [], []
    externes_vus = set()
    externes_ailleurs = set(external_ids_ailleurs or ())

    if not isinstance(items, list):
        return ["Le fichier doit porter un tableau JSON d'items, pas un objet unique."], []
    if not items:
        return ["Tableau vide : aucun item genere."], []

    competence = requete.get("competence")
    matiere = requete.get("matiere")
    cursus_attendu = _cursus_cle(requete.get("cursus"))
    ids_reference = {
        r.get("exercise_id") for r in requete.get("materiel_reference") or []
        if isinstance(r, dict)
    }

    corpus = set()
    for ref in requete.get("materiel_reference") or []:
        if isinstance(ref, dict):
            corpus |= _shingles(ref.get("enonce_markdown", ""))
            corpus |= _shingles(ref.get("corrige_markdown", ""))

    repartition = {}

    for idx, item in enumerate(items):
        tag = f"item {idx}"
        if not isinstance(item, dict):
            erreurs.append(f"{tag} : n'est pas un objet JSON.")
            continue

        manquants = [k for k in REQUIRED_KEYS if not item.get(k)]
        if manquants:
            erreurs.append(f"{tag} : champs obligatoires manquants {manquants} "
                           f"(refuses par quiz.ingestion.ingest_competence_item).")

        ext = str(item.get("external_id") or "").strip()
        if not ext:
            erreurs.append(f"{tag} : external_id vide - perd l'idempotence a l'ingestion.")
        elif ext in externes_vus:
            erreurs.append(f"{tag} : external_id duplique dans le lot ({ext!r}).")
        elif ext in externes_ailleurs:
            erreurs.append(f"{tag} : external_id {ext!r} deja utilise par un autre lot - "
                           "l'ingestion ignorerait silencieusement cet item.")
        else:
            externes_vus.add(ext)

        theme = item.get("theme")
        if theme != competence:
            erreurs.append(f"{tag} : theme={theme!r} != competence demandee {competence!r} "
                           "(doit correspondre a un Tag existant, au caractere pres).")

        if item.get("matiere") != matiere:
            erreurs.append(f"{tag} : matiere={item.get('matiere')!r} != {matiere!r}.")

        if _cursus_cle(item.get("cursus")) != cursus_attendu:
            erreurs.append(f"{tag} : cursus different de la requete "
                           f"({item.get('cursus')!r}).")

        diff = item.get("difficulte_estimee")
        if diff not in DIFFICULTES:
            erreurs.append(f"{tag} : difficulte_estimee={diff!r} hors {DIFFICULTES}.")
        else:
            repartition[diff] = repartition.get(diff, 0) + 1

        type_rep = item.get("type_reponse")
        choix = item.get("choix") or []
        correcte = str(item.get("reponse_correcte") or "").strip()
        if type_rep == "QCM":
            lettres = []
            for c in choix:
                if not isinstance(c, dict) or not c.get("lettre") or not c.get("texte"):
                    erreurs.append(f"{tag} : choix QCM mal forme ({c!r}) - "
                                   "attendu {'lettre','texte'}.")
                else:
                    lettres.append(str(c["lettre"]).strip().upper())
            if len(set(lettres)) != len(lettres):
                erreurs.append(f"{tag} : lettres de choix dupliquees.")
            if correcte.upper() not in lettres:
                erreurs.append(f"{tag} : reponse_correcte={correcte!r} absente des choix "
                               f"{lettres}.")
            if len(lettres) < 3:
                avertis.append(f"{tag} : seulement {len(lettres)} options QCM (4 attendues).")
        elif type_rep == "OUVERTE":
            if choix:
                erreurs.append(f"{tag} : type_reponse=OUVERTE mais choix non vide.")
            if correcte:
                erreurs.append(f"{tag} : type_reponse=OUVERTE mais reponse_correcte non vide.")
        else:
            erreurs.append(f"{tag} : type_reponse={type_rep!r} hors QCM/OUVERTE.")

        sources = item.get("source_exercises") or []
        if not sources:
            avertis.append(f"{tag} : source_exercises vide - tracabilite d'audit perdue.")
        else:
            inconnus = [s for s in sources if s not in ids_reference]
            if inconnus:
                erreurs.append(f"{tag} : source_exercises {inconnus} absents du "
                               "materiel_reference de la requete.")

        enonce = item.get("enonce_markdown") or ""
        corrige = item.get("corrige_markdown") or ""

        for motif in RENVOIS_BLOQUANTS:
            trouve = re.search(motif, enonce, re.IGNORECASE)
            if trouve:
                erreurs.append(f"{tag} : autonomie rompue - l'enonce renvoie a un contexte "
                               f"absent ({trouve.group(0)!r}).")
        for motif in RENVOIS_SUSPECTS:
            trouve = re.search(motif, enonce, re.IGNORECASE)
            if trouve:
                avertis.append(f"{tag} : mention {trouve.group(0)!r} dans l'enonce - "
                               "verifier qu'aucun support externe n'est requis.")

        for texte, ou in ((enonce, "enonce"), (corrige, "corrige")):
            communs = _shingles(texte) & corpus
            if communs:
                extrait = sorted(communs)[0]
                avertis.append(f"{tag} : {ou} partage {len(communs)} sequence(s) de "
                               f"{SHINGLE} mots avec le materiel de reference "
                               f"(ex. \"{extrait[:70]}...\") - risque de recopie.")

        if OPTIONS_DANS_ENONCE.search(enonce):
            if type_rep == "QCM":
                erreurs.append(f"{tag} : les options sont enumerees dans "
                               "enonce_markdown ET dans `choix` - l'eleve les verrait "
                               "deux fois (l'interface affiche toujours des boutons "
                               "lettres). Retirer l'enumeration du texte.")
            else:
                erreurs.append(f"{tag} : enonce_markdown enumere des options lettrees "
                               "mais type_reponse=OUVERTE - aucun bouton ne sera "
                               "affiche. Passer en QCM avec `choix`.")

        for balise in ("![", "\\includegraphics", "<img"):
            if balise in enonce:
                erreurs.append(f"{tag} : l'enonce reference une image ({balise}) - "
                               "CompetenceItem n'a aucun mecanisme de piece jointe.")

    cible = (requete.get("cible") or {})
    voulu_total = cible.get("nombre_items")
    if voulu_total and len(items) != voulu_total:
        avertis.append(f"lot : {len(items)} items produits pour {voulu_total} demandes.")
    voulu_rep = cible.get("repartition_difficulte") or {}
    for niveau, attendu in voulu_rep.items():
        obtenu = repartition.get(niveau, 0)
        if obtenu != attendu:
            avertis.append(f"lot : {obtenu} item(s) {niveau} pour {attendu} demande(s).")

    return erreurs, avertis


# --------------------------------------------------------------------------------
# Etat du lot
# --------------------------------------------------------------------------------

def charger_batch(racine: Path, pays: str):
    fichier = racine / f"_batch_{pays}.json"
    if not fichier.exists():
        raise SystemExit(f"Batch introuvable : {fichier}")
    donnees = json.loads(fichier.read_text(encoding="utf-8"))
    if not isinstance(donnees, list):
        raise SystemExit(f"{fichier} : un tableau de requetes est attendu.")
    return donnees


def externals_par_fichier(dossier: Path):
    """external_id -> fichier, sur tous les lots deja ecrits."""
    index = {}
    if not dossier.exists():
        return index
    for chemin in sorted(dossier.glob("*.json")):
        try:
            items = json.loads(chemin.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("external_id"):
                    index[str(item["external_id"])] = chemin.name
    return index


def etat(racine: Path, pays: str):
    batch = charger_batch(racine, pays)
    dossier = racine / pays
    index_ext = externals_par_fichier(dossier)
    lignes = []

    for requete in batch:
        competence = requete.get("competence")
        slug = slugify(competence)
        chemin = dossier / f"{slug}.json"
        ligne = {
            "competence": competence,
            "slug": slug,
            "fichier": str(chemin),
            "requete": requete,
        }
        if not chemin.exists():
            ligne.update(statut="A_FAIRE", detail="fichier absent", erreurs=[], avertissements=[])
            lignes.append(ligne)
            continue
        try:
            items = json.loads(chemin.read_text(encoding="utf-8"))
        except Exception as exc:
            ligne.update(statut="A_REFAIRE", detail=f"JSON illisible ({exc})",
                         erreurs=[str(exc)], avertissements=[])
            lignes.append(ligne)
            continue

        ailleurs = {e for e, f in index_ext.items() if f != chemin.name}
        erreurs, avertis = valider_lot(items, requete, ailleurs)
        ligne.update(
            statut="A_REFAIRE" if erreurs else "FAIT",
            detail=f"{len(items) if isinstance(items, list) else 0} item(s)",
            erreurs=erreurs,
            avertissements=avertis,
        )
        lignes.append(ligne)
    return lignes


def journaliser(racine: Path, pays: str, enregistrement: dict):
    chemin = racine / f"_state_{pays}.jsonl"
    enregistrement = dict(enregistrement)
    enregistrement.setdefault("horodatage", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    with chemin.open("a", encoding="utf-8") as flux:
        flux.write(json.dumps(enregistrement, ensure_ascii=False) + "\n")
    return chemin


# --------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------

def main(argv=None):
    parseur = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("commande", choices=("status", "next", "validate", "journal"))
    parseur.add_argument("fichier", nargs="?", help="fichier a valider (commande validate)")
    parseur.add_argument("--racine", default=str(Path(__file__).resolve().parent),
                         help="dossier _quiz (defaut : dossier de ce script)")
    parseur.add_argument("--pays", default="cm")
    parseur.add_argument("--n", type=int, default=1, help="nombre de requetes a emettre")
    parseur.add_argument("--competence", help="libelle exact de la competence")
    parseur.add_argument("--statut", default="ok")
    args = parseur.parse_args(argv)

    racine = Path(args.racine).resolve()

    if args.commande == "status":
        lignes = etat(racine, args.pays)
        largeur = max((len(l["competence"] or "") for l in lignes), default=10)
        for ligne in lignes:
            print(f"{ligne['statut']:<10} {ligne['competence']:<{largeur}}  {ligne['detail']}")
            for err in ligne["erreurs"]:
                print(f"           ERREUR  {err}")
            for avert in ligne["avertissements"]:
                print(f"           avert.  {avert}")
        restants = [l for l in lignes if l["statut"] != "FAIT"]
        print(f"\n{len(lignes) - len(restants)}/{len(lignes)} competence(s) valides, "
              f"{len(restants)} a traiter.")
        return 0 if not restants else 1

    if args.commande == "next":
        lignes = [l for l in etat(racine, args.pays) if l["statut"] != "FAIT"]
        print(json.dumps([l["requete"] for l in lignes[:args.n]], ensure_ascii=False, indent=2))
        return 0

    if args.commande == "validate":
        if not args.fichier or not args.competence:
            raise SystemExit("validate exige <fichier.json> et --competence")
        batch = charger_batch(racine, args.pays)
        requete = next((r for r in batch if r.get("competence") == args.competence), None)
        if requete is None:
            raise SystemExit(f"Competence {args.competence!r} absente de _batch_{args.pays}.json")
        chemin = Path(args.fichier)
        items = json.loads(chemin.read_text(encoding="utf-8"))
        attendu = racine / args.pays / f"{slugify(args.competence)}.json"
        ailleurs = {e for e, f in externals_par_fichier(racine / args.pays).items()
                    if f != attendu.name}
        erreurs, avertis = valider_lot(items, requete, ailleurs)
        for err in erreurs:
            print(f"ERREUR  {err}")
        for avert in avertis:
            print(f"avert.  {avert}")
        if erreurs:
            print(f"\nREFUSE : {len(erreurs)} erreur(s). Ne pas ecrire dans {attendu}.")
            return 1
        print(f"\nOK : {len(items)} item(s) valides, {len(avertis)} avertissement(s). "
              f"Destination {attendu}")
        return 0

    if args.commande == "journal":
        if not args.competence:
            raise SystemExit("journal exige --competence")
        chemin = journaliser(racine, args.pays, {
            "competence": args.competence,
            "slug": slugify(args.competence),
            "statut": args.statut,
        })
        print(f"Journalise dans {chemin}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
