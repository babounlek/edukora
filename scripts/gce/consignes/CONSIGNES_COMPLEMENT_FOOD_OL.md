# Complément aux consignes - GCE ORDINARY LEVEL, FOOD AND NUTRITION (code 0540)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à Food and Nutrition : codes, noms de dossier, papers, règles de choix, corrigés, thèmes.
Niveau O Level (Form 5).

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Food and Nutrition"`, `code_matiere` `"0540"` (page de garde : « ORDINARY LEVEL », « 0540 FOOD AND NUTRITION »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-food-nutrition-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30, calculatrice non programmable permise. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules,
  `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Un QCM de calcul (valeur énergétique, pourcentage, quantités d'une recette, coût) se justifie par le calcul recalculé avec Python.
  Un QCM factuel dont deux options sont défendables, ou dont le fait imprimé est inexact : convertis en `ouverte` (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- **Paper 2** : 2h30, « Answer ANY FOUR questions », questions à 25 points (lis la page de garde de CHAQUE année : le nombre de questions et d'éventuelles sections peut changer ; « Tabulate wherever possible and use
  diagrams where appropriate »). UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions (a), (b), (c)... = `questions`. Sans sections : `groupes` `["PAPER 2"]` dans chaque fichier et
  `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":4,"sur":<N questions imprimées>}]`, identique dans TOUS les fichiers. Avec des sections à nombres imposés : une règle `parmi` par section (le minimum),
  `groupes` = le repère de section, consigne complète dans `introduction_markdown` et `incertitudes`. Points : `points` de l'exercice = le total imprimé (« Total = 25 marks »), points des sous-questions entre crochets.
- `introduction_markdown` : la consigne de la page de garde, identique dans tous les fichiers du dossier. `duree_epreuve` : `"1h30"` ou `"2h30"`.

## Corrigés (exactitude avant tout)

- Anglais clair niveau Form 5 : réponses courtes et exactes, au nombre exact d'éléments demandé (« state five », « list four », « outline seven » : ni plus ni moins, chacun distinct et défendable ; ajoute une courte
  explication quand le verbe le demande : « explain », « outline », « discuss »). Un tableau demandé (« in a tabular form », « classify ») se rend en tableau Markdown.
  Programme : alimentation et nutriments (glucides, lipides, protéines, vitamines, sels minéraux, eau, fibres) et groupes d'aliments, digestion, besoins nutritionnels selon l'âge et l'état (enfant, adolescent, femme enceinte,
  malade, personne âgée), planification des repas et budget, achat et étiquetage des aliments, méthodes de cuisson, préparation des viandes, poissons, œufs, légumes, produits laitiers, pâtisserie (pâte brisée, gâteau),
  conservation des aliments (réfrigérateur, congélateur, séchage, fumage, salage), hygiène et sécurité dans la cuisine, premiers secours, équipement de cuisine, service de table, plats traditionnels du Cameroun.
- **N'invente aucun chiffre** (teneur nutritive, calories, durée de conservation, température) hors des valeurs classiques d'un cours de niveau O Level, que tu recalcules ou que tu formules avec prudence
  (« about », « usually ») ; trace dans `incertitudes` tout fait que tu n'as pas pu établir avec certitude. Plats et ingrédients locaux (ndolé, achu, eru, koki, plantain, cassava) : exemples concrets, jamais de composition chiffrée inventée.
  Un calcul (énergie : 1 g de glucide ou de protéine ≈ 17 kJ ≈ 4 kcal, 1 g de lipide ≈ 37 kJ ≈ 9 kcal ; proportions d'une recette ; coût) se recalcule avec Python (`D:\edukora\venv\Scripts\python.exe`).
- Le `$` d'un prix s'écrit `\$` hors formule (le FCFA se note en toutes lettres ou `FCFA`). Un schéma ou une illustration imprimés (appareil digestif, équipement, plat, boîte de premiers secours) : suis la section Figures de
  `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ; `figures[].type` : 30 caractères MAXIMUM. Un schéma à dessiner par le candidat se décrit dans le corrigé (légende, éléments à nommer).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, **propres à Food and Nutrition** : par exemple `food groups and balanced diet`, `nutrients and their functions in food`, `carbohydrates in the diet`,
`proteins in the diet`, `vitamins and mineral salts in food`, `digestion of food in the human body`, `meal planning for the family`, `nutritional needs of special groups`, `methods of cooking food`,
`food preservation methods`, `food additives and labelling`, `pastry and cake making`, `kitchen hygiene and food safety`, `kitchen equipment and its care`, `first aid in the home`,
`table setting and meal service`, `traditional cameroonian dishes`, `refrigerator and freezer use`, `egg cookery`, `milk and milk products`.
`Tag.name` est UNIQUE et PARTAGÉ avec la Biologie / SVT, la Human Biology, l'Économie familiale française et les autres matières : n'emploie pas un mot qui existe tel quel en français ou en Biology
(`digestion`, `nutrition`, `proteins`, `vitamins`, `hygiene`, `first aid`, `carbohydrates`, `diet`...) ni une variante d'accent ou de pluriel : préfère des noms qualifiés de 3 à 5 mots, avec la mention de la cuisine ou de l'alimentation.
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-ol-human-biology-*\*.json` et `cm\gce-ol-biology-*\*.json` (pour NE PAS les réutiliser) et dans
`cm\gce-ol-food-nutrition-*` et `_gce_staging\gce-ol-food-nutrition-*` (pour RÉUTILISER les noms des autres papers de Food and Nutrition : plusieurs agents travaillent en parallèle, relis les dossiers des autres
avant de créer un nom, n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code 0540 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
