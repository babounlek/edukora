# Veille du corpus d'épreuves (skill veille-corpus-epreuves)

Code : `scripts/corpus/`. Skill à installer depuis `scripts/corpus/skill/veille-corpus-epreuves/SKILL.md` (geste « Save skill » du Desktop).
Spécification d'origine : `deploy/PROMPT-SKILL-AUDIT-CORPUS.md`.

## Commandes
| Commande | Effet | Écrit |
|---|---|---|
| `audit [--rafraichir]` | cartographie base + disque + référence prod | `ingest/_audit/corpus/<date>/` |
| `qualifier <pdf>` | éliminatoires E1-E7, score, doublons | rien |
| `head <url>` | HEAD sans téléchargement | rien |
| `collecter <url> --langue` | télécharge en zone de dépôt | zone + `provenance.jsonl` |
| `controle <dossier>` | qualifie tous les PDF | rien |
| `synchroniser … --lecture-validee` | copie vers `ingest/_telechargements_*` | cette copie |
| `registre lister/ajouter/a-refaire` | mémoire des recherches | `registre_recherches.jsonl` |

| `sources` | liste des sites et modes d'accès (`sources.json`) | rien |
| `liens --niveau … --matiere … --annee … --paper …` | liens de recherche par site (Scribd, ndolomath, sujetexa, CGR, concourscameroon, …) | rien |

Contrôle base : `docker cp scripts/corpus/controle_base.py edukora-backend-1:/tmp/` puis `manage.py shell -c "exec(open('/tmp/controle_base.py').read())"`.

## Sites
Registre : `scripts/corpus/sources.json` (domaine, systèmes, mode d'accès, `automatisable`, notes, `verifie_le`). Seuls epreuvesetcorriges.com et camgceb.org sont téléchargés automatiquement ; les autres (dont ndolomath.com et scribd.com) donnent des liens à ouvrir à la main. Scribd : lecture via Claude in Chrome (compte déjà connecté), téléchargement avec accord de l'utilisateur fichier par fichier.

## Limites connues
- L'état « publié en prod » est déduit de `batches/_reference-prod.json` (`Lesson.published_at` est vide).
- `backend/ingest/` et `media/` sont ignorés par git : le registre et les zones ne sont pas sauvegardés par git.
- Tests : `python -I scripts/tests/test_corpus.py` (33 cas, hors réseau et prod). Pas de test de reprise après interruption réseau au-delà du `.part`.
