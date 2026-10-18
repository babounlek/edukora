# Complément aux consignes - GCE ADVANCED LEVEL, ENGLISH LANGUAGE (code 0730)

Lis `CONSIGNES.md` (forme générale, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis `CONSIGNES_COMPLEMENT_LANGUES_OL.md` (corrigés de langue, QCM à établir par la règle, compositions modèles, thèmes préfixés),
puis ce fichier. **Ce fichier prime** pour l'A Level : codes, noms de dossier, papers, préfixe de thèmes. Niveau Advanced (Lower et Upper Sixth), pas Form 5.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"English Language"`, `code_matiere` `"0730"` (page de garde : « ADVANCED LEVEL », « 0730 ENGLISH LANGUAGE »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-english-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_ENGLISH_LANGUAGE_<ANNEE>_P<n>.pdf` (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30, tout obligatoire. Il enchaîne des SECTIONS imprimées (en 2024 : SECTION A reading comprehension sur un long passage, 16 questions ; SECTION B grammar, 22 questions ; puis d'autres sections de langue :
  vocabulaire, structure, etc. : lis la page de garde et les titres de CHAQUE année). UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre,
  `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Le passage de compréhension se recopie UNE fois, intégralement, avec ses numéros de ligne (les questions renvoient à « (L51-52) »), dans l'`enonce_markdown` de la première
  question qui s'y rapporte, sous un titre en gras, et les suivantes commencent par « (Passage for questions 1 to 16 above) » (voir `CONSIGNES_COMPLEMENT_LANGUES_OL.md`). Le texte imprimé garde ses fautes éventuelles
  (note-les dans `incertitudes`). Les mots soulignés ou en gras de l'énoncé gardent leur mise en forme (écris-les en gras).
  Chaque clé se justifie par la règle (grammaire, vocabulaire, figure de style, ton, inférence dans le passage) : relis l'énoncé en insérant chaque option ; deux options défendables ou clé douteuse : convertis en `ouverte`
  (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- **Paper 2** (3 h) : « Answer BOTH questions in SECTION A and ONE EACH from SECTIONS B and C in the SAME Answer Booklet » (intitulé : SECTION A SUMMARY AND TEXT RECONSTRUCTION, SECTION B COMPOSITION, SECTION C PRESCRIBED TEXTS ; lis
  la page de garde de CHAQUE année). UN fichier PAR QUESTION ou par SUJET : `numero_exercice` `"1"` et `"2"` (section A : question 1 summary, question 2 text reconstruction ; `groupes` `["SECTION A"]`, aucune règle car tout est
  obligatoire), `"B1"`, `"B2"`... (`groupes` `["SECTION B"]`), `"C1"`, `"C2"`... (`groupes` `["SECTION C"]`). `regles_choix`, identiques dans TOUS les fichiers du dossier :
  `{"type":"parmi","portee":"SECTION B","repondre":1,"sur":<N sujets de B>}` et `{"type":"parmi","portee":"SECTION C","repondre":1,"sur":<N sujets de C>}`. Recopie la consigne complète dans `introduction_markdown` et rappelle-la dans `incertitudes`.
  `points` : le total imprimé (« 15 marks »...). Les rappels de la page de garde (use your own words, no pre-prepared composition) se recopient dans `introduction_markdown`.
  - **Summary** (« not more than 150 words, using your own words ») : recopie le passage en entier ; corrigé : un résumé modèle dans la limite (compte les mots par script), la liste des points de contenu attendus, la grille et deux erreurs fréquentes
    (copier le texte, dépasser la limite, commenter).
  - **Text reconstruction** : recopie le texte à transformer et la consigne ; corrigé : le texte reconstruit COMPLET, puis un tableau « avant / après / règle ».
  - **Composition** : un fichier par sujet ; corrigé : un plan de 4 à 5 lignes, une composition modèle complète de la longueur demandée (compte les mots par script), la grille et deux erreurs fréquentes ; un sujet à IMAGES (Picture A, Picture B) :
    produis l'image comme figure si la reproduction est propre (skill, jamais `pdftoppm`) ; une photographie impossible à rendre sans filigrane se décrit précisément dans l'énoncé (« [Picture A: ...] ») et se signale dans `incertitudes` ;
    la composition modèle s'appuie sur l'image nommée.
  - **Prescribed texts** (œuvres au programme) : tu n'as pas les œuvres. Recopie l'énoncé et le passage imprimé ; réponds uniquement avec ce que le passage et l'énoncé permettent d'établir (analyse du passage, ton, procédés, structure d'une réponse),
    sans résumé d'intrigue ni détail d'œuvre que tu ne peux pas vérifier ; une question qui exige une connaissance de l'œuvre hors du passage reçoit un corrigé de MÉTHODE (plan, critères) et la mention « corrigé de méthode : œuvre non disponible » dans
    `incertitudes`. N'invente ni personnage, ni événement, ni citation.
- **Paper 3** (présent seulement certaines années : 2025, 2026 ; 2h15 en 2025) : SECTION A SUMMARY WRITING, SECTION B TEXT RECONSTRUCTION, SECTION C EDITING, « ALL THE QUESTIONS ARE COMPULSORY. THEY CARRY EQUAL MARKS ».
  UN fichier PAR QUESTION, `groupes` `["SECTION A"]`..., `regles_choix` `[]`. L'editing (repérer et corriger des fautes) se corrige faute par faute : texte original, correction, règle ; compte les fautes par script.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"`, `"3h"` ou la durée imprimée (`"2h15"`).

## Corrigés

Tout ce que tu écris est en anglais clair et exact. Établis chaque clé et chaque réponse modèle sur la langue, jamais sur l'intuition ; une réponse modèle de rédaction est un texte COMPLET, irréprochable, de niveau Advanced
(registre soutenu, structure, connecteurs variés, aucune faute). Compte les mots par script (hors titres). Pas de tiret cadratin. N'invente aucun fait hors sujet ; les contextes sont camerounais ou internationaux, et les passages sont des
textes adaptés d'auteurs réels dont tu ne reproduis que ce que le sujet imprime.

## Thèmes (`themes`) : collisions

`Tag.name` est UNIQUE et PARTAGÉ avec plus de 2 000 thèmes d'anglais et de français et avec l'O Level. **Tout thème commence par le préfixe `A Level English - `**, suivi d'un nom court en minuscules (jamais de thème sans préfixe).
Réutilise le vocabulaire de `CONSIGNES_COMPLEMENT_LANGUES_OL.md` avec le préfixe A Level (`A Level English - reading comprehension`, `... verb tenses`, `... conditionals`, `... relative clauses`, `... connectors`, `... word formation`,
`... argumentative composition`...) et ajoute au besoin : `A Level English - summary writing`, `... text reconstruction`, `... editing and proofreading`, `... sentence structure`, `... tone and attitude`, `... figures of speech`,
`... vocabulary in context`, `... prescribed texts`, `... narrative composition`, `... descriptive composition`, `... formal letter and report`. Avant d'en créer un, fais un `Grep` des valeurs `"themes"` dans
`D:\edukora\backend\ingest\cm\gce-al-english-*\*.json` et `_gce_staging\gce-al-english-*\*.json` pour réutiliser les noms des autres papers (plusieurs agents travaillent en parallèle : relis les dossiers des autres avant de créer un nom).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0730 [--questions 50]
```

Il doit afficher `OK`. Vérifie en plus par script que chaque `themes` commence par `A Level English - `, que les `regles_choix` sont identiques dans tous les fichiers d'un dossier et que résumés et compositions respectent la limite de mots.
Puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
