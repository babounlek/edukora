# Complément aux consignes - GCE ADVANCED LEVEL, COMPUTER SCIENCE (code 0795)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce
fichier. **Ce fichier prime** pour tout ce qui touche à Computer Science : codes, noms de dossier, papers, thèmes, code source.
Les compléments Chimie / Physique / Biologie / Maths ne te concernent pas.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Computer Science"`, `code_matiere` `"0795"`
  (page de garde : « ADVANCED LEVEL », « 0795 »). Une autre matière, un autre code ou un autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-computer-science-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_COMPUTER_SCIENCE_<ANNEE>_P<n>.pdf`
  (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir `CONSIGNES_COMPLEMENT_AL.md`).
  Un QCM de code ou de logique se justifie par une trace d'exécution ou une table de vérité. Un schéma imprimé (circuit logique, arbre) se recadre en PNG.
- **Paper 2** : 2h30, « Answer any SIX questions », 17 points chacune. UN fichier PAR QUESTION du sujet, sous-questions (a), (b)... = `questions`.
  `regles_choix` identiques dans TOUS les fichiers, du type `[{"type":"parmi","portee":"PAPER 2","repondre":6,"sur":<N imprimé>}]`, avec `groupes` `["PAPER 2"]`
  partout (si le sujet est en sections, `groupes` et règles par section, `portee` égal à un repère de `groupes`). Points de l'exercice : `"17"`.
- **Paper 3 (pratique)** : 2h, « Carry out ALL the tasks given », tâches de programmation, d'algorithmique et de conception ; le candidat écrit en **Standard ISO Pascal
  ou ANSI C**. UN fichier PAR TÂCHE (`numero_exercice` `"1"`, `"2"`... ou le repère imprimé), `regles_choix` `[]`, `groupes` `[]` sauf sections imprimées.
  Le corrigé donne : l'algorithme (pseudocode), puis le programme complet en ANSI C (bloc de code Markdown ```c), commenté, avec un exemple d'exécution (entrées, sorties).
  Si le sujet impose un autre langage ou un outil (tableur, base de données), suis le sujet. `duree_epreuve` : `"1h30"`, `"2h30"` ou `"2h"` selon la page de garde.
- `introduction_markdown` : la consigne de la page de garde, identique partout.

## Corrigés : code et algorithmes

- Niveau Advanced : structures de données (piles, files, listes, arbres), algorithmes (tri, recherche, récursivité), complexité, bases de données et SQL, réseaux,
  architecture, systèmes d'exploitation, logique booléenne, représentation des données, langages et traduction, génie logiciel.
- **Aucun compilateur C ou Pascal n'est disponible sur la machine.** Écris le code avec une extrême rigueur (déclarations, types, `;`, `begin`/`end`, `#include`,
  `%d`/`%s`), puis VÉRIFIE la logique par une traduction fidèle en Python que tu exécutes (mêmes entrées, mêmes sorties, cas limites) et copie dans le corrigé
  la sortie réellement obtenue. Dans `incertitudes`, écris que le code C/Pascal n'a pas été compilé et que sa logique a été vérifiée par une simulation Python.
- SQL : vérifie chaque requête avec `sqlite3` (module Python) sur des données d'exemple ; indique les différences de dialecte éventuelles.
- Tables de vérité, conversions de bases, ordonnancements, calculs de débit ou de capacité : recalcule par script.
- Blocs de code dans le Markdown : bloc clôturé par trois accents graves et le nom du langage (`c`, `pascal`, `sql`). Ne mets pas de `$` autour du code.
  Les indentations sont conservées ; échappe correctement les antislashs dans le JSON (`\\n` pour un `\n` du programme).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, propres au niveau Advanced, par exemple : `data structures`, `stacks and queues`, `linked lists`,
`binary trees`, `sorting algorithms`, `searching algorithms`, `recursion`, `algorithm complexity`, `boolean algebra`, `logic gates`, `number systems`,
`data representation`, `relational databases`, `sql queries`, `normalisation`, `computer networks`, `network protocols`, `operating systems`, `memory management`,
`process scheduling`, `computer architecture`, `translators and compilers`, `programming in c`, `pascal programming`, `file handling`, `software engineering`,
`data security`, `artificial intelligence`. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières : n'emploie pas un mot qui existe
tel quel en français ni le nom d'un thème d'une autre matière. Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans
`D:\edukora\backend\ingest\cm\gce-al-computer-science-*\*.json` et `_gce_staging\gce-al-computer-science-*\*.json` : réutilise le nom quand la notion est la même.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0795 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS
l'ingestion, ne touche ni à la base ni à Docker ni à git.
