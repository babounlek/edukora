# Complément aux consignes - GCE ADVANCED LEVEL, PHILOSOPHY (code 0790)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce fichier.
**Ce fichier prime** pour tout ce qui touche à la Philosophie : codes, noms de dossier, papers, règles de choix, logique, dissertations, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Philosophy"`, `code_matiere` `"0790"` (page de garde : « ADVANCED LEVEL », « 0790 PHILOSOPHY »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-philosophy-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_PHILOSOPHY_<ANNEE>_P<n>.pdf` (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30 (logique : formes d'argument, syllogismes, sophismes, tables de vérité, déduction immédiate, dilemmes, enthymèmes ; et philosophie). UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`,
  `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Les symboles de logique s'écrivent en LaTeX (voir plus bas) ; une table de vérité ou une
  figure d'un syllogisme (Figure 1 à 4) s'écrit en tableau Markdown ou se recadre en PNG. Une question imprimée avec deux variantes (« OR ») : transcris la première comme question, dis-le et recopie la seconde dans `incertitudes` ;
  si les deux variantes ont la même clé, mentionne-le. Un QCM dont deux options sont défendables ou dont la clé semble fausse : convertis en `ouverte` (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`),
  jamais une lettre au hasard.
- **Paper 2 (Philosophical Writing and Analysis)** : 3 h, « Answer FOUR questions, choosing at least ONE question from each section », 25 points chacune. Sections typiques : SECTION ONE: WESTERN PHILOSOPHY, SECTION TWO: AFRICAN PHILOSOPHY,
  SECTION THREE: TEXTUAL ANALYSIS (lis la page de garde de CHAQUE année : noms et nombre de sections peuvent changer). UN fichier PAR QUESTION, `numero_exercice` = le numéro imprimé, `groupes` = le repère de section
  (`["SECTION ONE"]`, `["SECTION TWO"]`, `["SECTION THREE"]`), `regles_choix` identiques dans TOUS les fichiers : UNE règle
  `{"type":"total","portee":"PAPER 2","repondre":4,"minimum":1,"groupes":["SECTION ONE","SECTION TWO","SECTION THREE"]}` (quatre au total, au moins une par section).
  La consigne complète va aussi dans `introduction_markdown`.
  Les critères de notation de la page de garde (cohérence, problématique, thèse-antithèse-synthèse-conclusion) se recopient dans `introduction_markdown`.
- **Paper 3 (Critical Thinking)** : 3 h, « Answer FOUR questions, choosing TWO from each section », 25 points chacune. Sections typiques : SECTION ONE: LOGIC (questions à sous-parties chiffrées, parfois « OR » entre deux jeux de sous-questions)
  et SECTION TWO: PHILOSOPHICAL PROBLEMS (dissertations). UN fichier PAR QUESTION, `groupes` = `["SECTION ONE"]` / `["SECTION TWO"]`, règle `parmi` par section avec `repondre` 2 et `sur` le nombre de questions de la section.
  Quand une question de logique offre deux jeux de sous-questions « OR », transcris les DEUX jeux, en numérotant (a)...(d) puis `(a) OR`, etc. si l'identité des sous-questions l'impose, recopie le « OR » dans l'énoncé
  et signale dans `incertitudes` que le candidat ne traite qu'un des deux jeux.
- Sous-questions (a), (b)... = `questions` ; points entre crochets dans `points`. `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"` ou `"3h"`.

## Corrigés (exactitude avant tout)

- **Logique** : chaque réponse est RECALCULÉE avec Python (`D:\edukora\venv\Scripts\python.exe`, `itertools.product` pour les tables de vérité, validité, tautologie / contradiction / contingence ; ensembles pour un syllogisme catégorique).
  Donne la table complète, la forme symbolique, la règle ou le sophisme exact (illicit major / illicit minor / undistributed middle / four terms / begging the question / false cause...), la figure et le mode d'un syllogisme,
  la traduction en logique des prédicats avec le schéma de lettres imprimé. Mentionne la convention existentielle quand elle compte (la forme universelle « All S are P » est-elle lue avec ou sans import existentiel) et trace-la dans `incertitudes`
  quand le manuel du programme et la logique moderne divergent.
- **Notation en LaTeX** (dans le JSON, antislash doublé) : conditionnel `\supset`, équivalence `\equiv`, négation `\sim`, conjonction `\cdot`, disjonction `\vee`, donc `\therefore`, quantificateurs `(x)` et `(\exists x)`,
  contradictoire `\overline{...}` seulement si imprimé ainsi. Un tableau de vérité se rend en tableau Markdown de V/F ou T/F tel qu'imprimé.
- **Dissertations et analyse de texte** : réponse modèle en anglais clair niveau Advanced, structurée comme les critères de la page de garde : introduction avec problématique, thèse, antithèse, synthèse, conclusion (titres courts,
  environ 500 à 800 mots par dissertation), arguments attribués à des philosophes RÉELS et à leurs positions CONNUES (Anaximandre et l'apeiron, Platon, Aristote, Descartes et le cogito, Locke, Hume, Kant, Sartre, Marx, Mill...
  philosophie africaine : Tempels, Mbiti, Senghor, Nkrumah, Gyekye, Wiredu, Hountondji, Oruka, Nyerere, Kagame, Eboussi Boulaga, Towa...). **N'invente ni citation, ni titre d'ouvrage, ni date, ni numéro de page** : en cas de doute,
  paraphrase prudente (« for Descartes... ») et trace dans `incertitudes`. Une question qui exige de situer précisément un auteur peu courant : formulation générale. Analyse de texte : recopie le passage tel qu'imprimé (guillemets, coupures),
  réponds à chaque sous-question avec points sur le texte, jamais de contresens du passage.
- Pas de position partisane sur les questions politiques ou religieuses : expose les positions et leurs raisons, et conclus sur l'argument le mieux étayé.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, **propres à la Philosophie** : par exemple `categorical syllogisms and their rules`, `logical fallacies in arguments`, `truth tables and propositional logic`, `predicate logic and symbolisation`,
`immediate inference and oppositions`, `dilemmas and disjunctive arguments`, `cartesian epistemology`, `rationalism and empiricism`, `pre-socratic cosmology`, `african ethno-philosophy debate`, `force-being and african metaphysics`,
`moral responsibility and free will`, `arguments for the existence of god`, `state and human freedom`, `locke and innate ideas`, `ethics and moral theories`, `personal identity and the mind`, `political philosophy and the state`.
`Tag.name` est UNIQUE et PARTAGÉ avec la Philosophie française (BAC) et les autres matières : n'emploie pas un mot qui existe tel quel en français ou ailleurs (`logic`, `ethics`, `freedom`, `morality`, `knowledge`, `existence`...)
ni une variante d'accent ou de pluriel ; préfère des noms qualifiés de 3 à 5 mots, ou suffixés par « (philosophy) ».
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-al-philosophy-*\*.json` et `_gce_staging\gce-al-philosophy-*\*.json` (pour RÉUTILISER les noms des autres papers de Philosophy :
plusieurs agents travaillent en parallèle, relis les dossiers des autres avant de créer un nom, n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0790 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
