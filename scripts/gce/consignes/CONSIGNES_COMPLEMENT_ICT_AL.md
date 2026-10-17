# Complément aux consignes - GCE ADVANCED LEVEL, INFORMATION AND COMMUNICATION TECHNOLOGIES (ICT, code 0796)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce
fichier. **Ce fichier prime** pour tout ce qui touche à l'ICT : codes, noms de dossier, papers, code source, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"ICT"`, `code_matiere` `"0796"`
  (page de garde : « ADVANCED LEVEL », « 0796 », « Information and Communication Technologies »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-ict-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_ICT_<ANNEE>_P<n>.pdf`
  (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30, calculatrice interdite. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir `CONSIGNES_COMPLEMENT_AL.md`).
  Un QCM de conversion, de logique ou de tableur se justifie par le calcul ou la trace.
- **Paper 2** : 2h30, « Answer any SIX questions », 17 points chacune. UN fichier PAR QUESTION du sujet, sous-questions (a), (b)... = `questions`.
  `regles_choix` identiques dans TOUS les fichiers : `[{"type":"parmi","portee":"PAPER 2","repondre":6,"sur":<N imprimé>}]` avec `groupes` `["PAPER 2"]` partout
  (ou par section si le sujet en a, `portee` égal à un repère de `groupes`). Points de l'exercice : `"17"` ; points des sous-questions entre crochets.
- **Paper 3** : épreuve PRATIQUE sur ordinateur (« Group 1 », « Answer ALL tasks », 2 h) : traitement de texte, tableur, base de données, présentation, web, programmation
  (Standard ISO Pascal ou ANSI C). UN fichier PAR TÂCHE (`numero_exercice` = repère imprimé : `"1"`, `"2"`... ou `"A1"`), `regles_choix` `[]`, `groupes` `[]` sauf sections imprimées.
  Le candidat travaille sur des fichiers fournis le jour de l'examen : **ces fichiers ne sont pas dans le PDF**. Pour chaque tâche : recopie fidèlement l'énoncé (y compris les
  tableaux de données imprimés) ; le corrigé donne la démarche exacte (étapes dans le logiciel, formules de tableur avec références de cellules, requêtes SQL, structure des tables et relations, mise en page demandée, code C/Pascal) et, quand un résultat se calcule à partir des données imprimées, la valeur obtenue (recalculée par script).
  Si une donnée manque (fichier non fourni), dis-le dans l'énoncé transcrit (« [data file supplied on the day, not reproduced here] ») et dans `incertitudes`, et donne une réponse générique correcte (formule type, requête type) plutôt que d'inventer des valeurs.
  `duree_epreuve` selon la page de garde (souvent `"2h"`). Un grand sujet pratique peut compter 8 à 12 pages : lis tout, y compris les annexes.
- `introduction_markdown` : la consigne de la page de garde, identique partout.

## Corrigés

- Niveau Advanced : systèmes d'information, matériel et logiciel, réseaux et communication, bases de données et SQL, tableurs (formules, fonctions RECHERCHEV/SI/SOMME.SI, tableaux croisés), traitement de texte et publication, présentation, web (HTML/CSS), sécurité et protection des données, impacts sociaux et éthiques, analyse et conception de systèmes, programmation.
- **Aucun compilateur C/Pascal n'est disponible** : écris le code avec rigueur et VÉRIFIE sa logique par une traduction fidèle en Python exécutée ; note dans `incertitudes` que le code C/Pascal n'a pas été compilé. SQL : vérifie avec `sqlite3` (module Python). Formules de tableur : donne la syntaxe anglaise standard (`IF`, `SUM`, `VLOOKUP`, `COUNTIF`) et vérifie le résultat par Python.
- Conversions de bases, tailles de fichiers, débits, tables de vérité, sous-réseaux : recalcule par script.
- Blocs de code : bloc clôturé par trois accents graves et le nom du langage (`c`, `pascal`, `sql`, `html`). Échappe correctement les antislashs dans le JSON.
- Un schéma imprimé (réseau, organigramme, MCD) se recadre en PNG ; un schéma à produire par le candidat se décrit dans le corrigé.
- Équation numérotée avec `\\tag` : formule sur trois lignes (`$$`, formule, `$$`).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, propres au niveau Advanced, par exemple : `computer hardware`, `system software`, `application software`, `spreadsheet modelling`,
`word processing and publishing`, `presentation software`, `relational databases`, `sql queries`, `database design`, `computer networks`, `internet and web technologies`, `html and css`,
`data security and privacy`, `data representation`, `number systems`, `systems analysis and design`, `software development`, `programming in c`, `pascal programming`, `social and ethical issues`,
`emerging technologies`, `information systems in organisations`. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières (dont Computer Science) : jamais un mot qui existe tel
quel en français, ni le nom d'un thème de Computer Science ou d'une autre matière. Pour une notion commune avec Computer Science, choisis un nom distinct (par exemple `ict network protocols`, pas
`network protocols`). Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans `D:\edukora\backend\ingest\cm\gce-al-ict-*\*.json` et `_gce_staging\gce-al-ict-*\*.json` :
réutilise le nom quand la notion est la même.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0796 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS
l'ingestion, ne touche ni à la base ni à Docker ni à git.
