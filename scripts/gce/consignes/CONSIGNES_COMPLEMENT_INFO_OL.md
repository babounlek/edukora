# Complément aux consignes - GCE ORDINARY LEVEL, COMPUTER SCIENCE (code 0595)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_INFO_AL.md` (code source sans compilateur, vérification par Python/sqlite, forme des corrigés de
programmation), puis ce fichier. **Ce fichier prime** pour l'O Level : codes, noms de dossier, papers, niveau, thèmes. Niveau Form 5, pas Advanced.

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Computer Science"`, `code_matiere` `"0595"`
  (page de garde : « ORDINARY LEVEL », « 0595 »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-computer-science-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre,
  `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Un QCM de conversion, de logique ou de trace se justifie par le calcul ou la trace (Python). Un schéma imprimé se recadre en PNG.
- **Paper 2** : 2 h, « Answer any FIVE questions », 20 points chacune (lis la page de garde de CHAQUE année : le nombre de questions et de sections peut changer). UN fichier PAR QUESTION,
  sous-questions (a), (b)... = `questions`. Sans sections : `groupes` `["PAPER 2"]` partout et `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":5,"sur":<N imprimé>}]`, identique dans tous les fichiers.
  Avec sections à nombres imposés : une règle `parmi` par section (le minimum), `groupes` = le repère de section, consigne complète dans `introduction_markdown` et `incertitudes`.
- **Paper 3 (pratique sur ordinateur)** : 2h30, « Do all the tasks », souvent plusieurs GROUPES (« Group One/Two/Three ») dans un même PDF, ou un PDF par « DAY ». Chaque candidat ne passe qu'UN groupe ou UN jour.
  Un fichier PAR TÂCHE : `numero_exercice` = `G<n>-T<m>` (groupe n, tâche m) ou `D<n>-T<m>` (jour n), 30 caractères maximum ; `groupes` = `["GROUP <n>"]` ou `["DAY <n>"]` (laisse `[]` s'il n'y a qu'un
  groupe) ; `regles_choix` `[]` ; dis dans `introduction_markdown` et `incertitudes` que le candidat ne traite qu'un groupe (ou un jour) : non exprimable. Les fichiers de données du jour (documents, tableurs,
  images) ne sont PAS dans le PDF : recopie fidèlement l'énoncé, écris « [data file supplied on the day, not reproduced here] » quand une donnée manque, et donne en corrigé la démarche exacte (étapes dans le logiciel,
  formules de tableur avec références de cellules, mise en forme demandée, programme) plutôt que des valeurs inventées. Chaque tâche a ses points entre crochets : `points` de chaque sous-question.
  Pour un PDF qui contient plusieurs jours ou groupes, UN seul dossier par PDF de session (le DOSSIER `...-p3-officiel-cameroun`), avec tous les groupes/jours ; ne crée jamais de dossier supplémentaire.
- `introduction_markdown` : la consigne de la page de garde, identique dans tous les fichiers du dossier. `duree_epreuve` : `"1h30"`, `"2h"` ou `"2h30"` selon la page de garde.

## Corrigés

- Niveau Form 5 : notions du programme O Level (matériel, logiciels, représentation des données, algorithmique de base, programmation simple en Pascal ou C, bases de données élémentaires, tableur, traitement de texte, réseaux,
  Internet, sécurité, impact social). Réponses courtes et exactes ; pseudocode ou organigramme décrit quand demandé.
- **Aucun compilateur C/Pascal n'est disponible** : écris le code avec rigueur, vérifie sa logique par une traduction fidèle en Python exécutée (mêmes entrées, mêmes sorties, cas limites), copie la sortie obtenue et note dans
  `incertitudes` que le code n'a pas été compilé. SQL éventuel : vérifie avec `sqlite3`. Formules de tableur : syntaxe anglaise standard (`IF`, `SUM`, `AVERAGE`, `VLOOKUP`, `COUNTIF`), résultat recalculé par Python.
- Conversions de bases, tables de vérité, tailles de fichiers, débits : recalcule par script. Blocs de code : bloc clôturé et nom du langage (`c`, `pascal`, `sql`) ; antislashs correctement échappés dans le JSON.
- N'invente aucun fait (versions de logiciels, noms de produits précis) : formulation générique en cas de doute, trace dans `incertitudes`.

**Signe dollar dans un tableur** : une référence comme `A$2`, `$A$2` ou `2$A` écrite dans un énoncé, une option de QCM ou un corrigé, HORS d'un bloc de code, est lue par le rendu comme une formule (le `$` disparaît et la référence est faussée). Mets un antislash devant chaque `$` (`A\$2` dans le JSON) ou écris la référence entre accents graves. `valider_gce.py` avertit.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. **Réutilise le nom d'un thème de Computer Science A Level ou O Level quand c'est la même notion** (Grep des valeurs `"themes"` dans
`D:\edukora\backend\ingest\cm\gce-al-computer-science-*\*.json`, `gce-ol-computer-science-*\*.json` et `_gce_staging\gce-ol-computer-science-*\*.json` : plusieurs agents travaillent en parallèle, relis les dossiers des autres
avant de créer un nom, n'invente pas trois noms pour la même notion). Noms déjà décidés : `digital logic gates` (jamais `logic gates`, pris par Physique), `pseudocode algorithms` (jamais `pseudocode`, pris par l'Informatique
française). `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières (dont ICT) : évite les mots français tels quels et les noms d'ICT ; pour une notion commune avec l'ICT, un nom distinct.

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2|3> --code 0595 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
