#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
valider_schema.py - barriere de conformite sur le corpus JSON, et migration de l'ancien schema.

Pourquoi ce fichier existe
--------------------------
`themes` manquait sur 1 528 questions (20,4 %, 77 epreuves) sans que personne ne le voie. La
raison n'est pas un oubli de redaction : c'est qu'aucun controle ne portait sur les cles de
QUESTION. Les verifications faites apres chaque lot validaient les cles d'EXERCICE et s'arretaient
la. Une derive de schema a donc traverse tout le corpus en silence.

Le meme diagnostic vaut pour trois autres champs, absents exactement sur les memes 1 528
questions - c'est une cohorte d'ancien schema, pas un defaut aleatoire :

    themes, difficulte_estimee, type_reponse   1528   (20,4 %)
    choix                                      1592   (21,3 %)
    reponse_correcte                           3865   (51,6 %)
    savoir_officiel                            6774   (90,4 %)

Ancien schema de question : {numero, points, enonce_markdown, figures, rappels_de_methode,
corrige_markdown}, avec `rappels_de_methode[] = {cours_id, texte}`.
Schema actuel : voir QUESTION_REQUISE ci-dessous, avec `rappels_de_methode[] = {id, competence,
contenu_markdown}`.

Deux usages
-----------
    python valider_schema.py ../json                # controle seul, code de sortie 1 si non conforme
    python valider_schema.py ../json --migrer       # ajoute les cles manquantes, backfill `themes`

Le backfill de `themes` ne devine rien : il reprend les `meta.tags` et `meta.sous_theme` du cours
deja rattache a la question via `rappels_de_methode[].cours_id`. Ces tags ont ete rediges pour
cette notion precise, ils sont donc plus fiables qu'une inference depuis l'enonce.

A brancher en fin de chaque lot, avant le deplacement des PDF vers `traites/`.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXERCICE_REQUISE = [
    "epreuve_source", "numero_exercice", "pays", "matiere", "nature_epreuve", "serie",
    "examen", "origine", "etablissement", "annee", "duree_epreuve", "coefficient",
    "points", "figures", "enonce_intro_markdown", "questions", "mots_cles_recherche",
    "incertitudes", "statut",
]
QUESTION_REQUISE = [
    "numero", "enonce_markdown", "corrige_markdown", "themes", "savoir_officiel",
    "difficulte_estimee", "type_reponse", "choix", "reponse_correcte", "rappels_de_methode",
]
# Valeurs canoniques recopiees de SKILL.md (lignes 356, 359, 375-376, 392, 506-510).
# Ne pas les "corriger" de memoire : `élevée` porte bien ses accents, et `origine` compte
# quatre valeurs dont deux ne sont pas des mots simples.
LISTES_FERMEES = {
    "statut": {"brouillon"},
    "origine": {"officiel", "examen blanc", "etablissement", "autre"},
    "nature_epreuve": {"theorique", "pratique", None},
    "difficulte_estimee": {"faible", "moyenne", "élevée"},
    "type_reponse": {"ouverte", "qcm"},
}
#: Valeur posee quand la cle est absente. `None` signifie "inconnu, a renseigner",
#: jamais "vide" - la distinction est ce qui rend le rattrapage possible plus tard.
DEFAUTS_QUESTION = {
    "themes": None, "savoir_officiel": None, "difficulte_estimee": None,
    "type_reponse": None, "choix": [], "reponse_correcte": "",
}


def indexer_cours(racine: Path) -> dict[str, dict]:
    """cours_id -> contenu du cours, pour le backfill des themes."""
    index: dict[str, dict] = {}
    for p in racine.rglob("*_cours_*.json"):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if c.get("cours_id"):
            index[c["cours_id"]] = c
    return index


def themes_depuis_cours(question: dict, index: dict[str, dict]) -> list[str] | None:
    """Reconstitue `themes` depuis les tags du cours deja rattache. None si aucune source."""
    tags: list[str] = []
    for r in question.get("rappels_de_methode") or []:
        c = index.get(r.get("cours_id") or "")
        if not c:
            continue
        meta = c.get("meta") or {}
        tags += list(meta.get("tags") or [])
        if meta.get("sous_theme"):
            tags.append(meta["sous_theme"])
    if not tags:
        return None
    vus: dict[str, None] = {}
    for t in tags:                       # dedoublonnage en conservant l'ordre
        vus.setdefault(t, None)
    return list(vus)


def traiter(racine: Path, migrer: bool) -> int:
    index = indexer_cours(racine) if migrer else {}
    manques: Counter[str] = Counter()
    invalides: Counter[str] = Counter()
    backfill = Counter()
    invalides_ignores: Counter[str] = Counter()
    fichiers_touches: set[Path] = set()
    sans_source: dict[str, int] = defaultdict(int)
    nq = 0

    for f in sorted(racine.rglob("*_exercice_*.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            invalides["JSON illisible"] += 1
            continue

        # Pierres tombales volontaires : fichier remplace, conserve pour tracer la redirection
        # ({deprecated, raison, remplace_par, action_requise}). Hors perimetre du schema.
        if j.get("deprecated"):
            invalides_ignores["fichier deprecated (ignore)"] += 1
            continue

        change = False
        for k in EXERCICE_REQUISE:
            if k not in j:
                manques[f"exercice.{k}"] += 1
        for champ, permis in LISTES_FERMEES.items():
            if champ in j and j[champ] not in permis and j[champ] is not None:
                invalides[f"exercice.{champ}={j[champ]!r}"] += 1

        for q in j.get("questions", []):
            nq += 1
            for k in QUESTION_REQUISE:
                if k not in q:
                    manques[f"question.{k}"] += 1
                    if migrer:
                        if k == "themes":
                            t = themes_depuis_cours(q, index)
                            q["themes"] = t
                            backfill["themes reconstitues" if t else "themes laisses a None"] += 1
                            if not t:
                                sans_source[j.get("matiere") or "?"] += 1
                        else:
                            q[k] = DEFAUTS_QUESTION.get(k)
                        change = True
            for champ in ("difficulte_estimee", "type_reponse"):
                v = q.get(champ)
                if v is not None and v not in LISTES_FERMEES[champ]:
                    invalides[f"question.{champ}={v!r}"] += 1

        if change and migrer:
            f.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
            fichiers_touches.add(f)

    print(f"{nq} questions controlees"
          + (f"  ({sum(invalides_ignores.values())} fichiers deprecated ignores)"
             if invalides_ignores else ""))
    if manques:
        print("\ncles manquantes :")
        for k, v in sorted(manques.items(), key=lambda kv: -kv[1]):
            print(f"  {k:<32} {v:>6}  {100*v/max(nq,1):5.1f} %")
    if invalides:
        print("\nvaleurs hors liste fermee :")
        for k, v in invalides.most_common(15):
            print(f"  {k:<44} {v:>5}")
    if migrer:
        print(f"\nmigration appliquee sur {len(fichiers_touches)} fichiers")
        for k, v in backfill.most_common():
            print(f"  {k:<32} {v:>6}")
        if sans_source:
            print("\n`themes` restant a None faute de cours rattache, par matiere :")
            for m, n in sorted(sans_source.items(), key=lambda kv: -kv[1])[:10]:
                print(f"  {n:>5}  {m}")
    if not manques and not invalides:
        print("\nCorpus conforme.")
        return 0
    return 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    raise SystemExit(traiter(Path(args[0] if args else "../json"), "--migrer" in sys.argv))
