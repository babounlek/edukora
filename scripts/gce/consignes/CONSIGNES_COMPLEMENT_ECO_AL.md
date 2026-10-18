# Complément aux consignes - GCE ADVANCED LEVEL, ECONOMICS (code 0725)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce
fichier. **Ce fichier prime** pour tout ce qui touche à Economics : codes, noms de dossier, papers, règles de choix, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Economics"`, `code_matiere` `"0725"`
  (page de garde : « ADVANCED LEVEL », « 0725 »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-economics-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_ECONOMICS_<ANNEE>_P<n>.pdf`
  (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir `CONSIGNES_COMPLEMENT_AL.md`). Un QCM numérique
  (élasticité, multiplicateur, revenu national, taux de change...) se justifie par le calcul. Un graphique imprimé (courbes d'offre et de demande, tableau
  de données) se recopie : tableau Markdown pour des données, PNG recadré pour une courbe.
- **Paper 2** : 3 h, dissertations. Page de garde : « Answer FIVE questions, choosing AT LEAST TWO from each section ». Lis le sujet pour repérer les sections
  (souvent SECTION A et SECTION B). UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé (ou `"B1"`... si une section renumérote), sous-questions
  (a), (b)... = `questions`. `groupes` = le repère de section de la question (`["SECTION A"]`, `["SECTION B"]`), identique dans tous les fichiers d'une section.
  « 5 questions en tout, au moins 2 par section » se code par UNE règle `{"type":"total","portee":"PAPER 2","repondre":5,"minimum":2,"groupes":["SECTION A","SECTION B"]}`
  (et non par un `parmi` par section : la simulation ne compterait que 2 questions par section). Recopie TOUTE la consigne dans `introduction_markdown`. Tous les fichiers du dossier portent les mêmes `regles_choix`.
- **Paper 3** : 1h45, questions quantitatives (« Answer ANY THREE questions », calculatrice permise). Même forme que le Paper 2 : un fichier par question,
  `regles_choix` `[{"type":"parmi","portee":"PAPER 3","repondre":3,"sur":<N imprimé>}]` avec `groupes` `["PAPER 3"]` partout (ou par section si le sujet en a).
- Les points : « All questions carry equal marks » ; `points` de l'exercice = le total imprimé s'il y en a un, sinon `""`.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"`, `"3h"` ou `"1h45"` selon la page de garde.

## Corrigés

- Niveau Advanced : définitions précises (valeur de l'élasticité, coût d'opportunité, multiplicateur...), analyse (effets, limites, exemples), évaluation (jugement argumenté),
  structure de dissertation (introduction, développement, conclusion) pour les questions rédigées. Une réponse modèle complète, avec des exemples camerounais ou africains
  quand c'est pertinent (CEMAC, XAF/FCFA, cacao, café, pétrole, coton, Douala), sans inventer de statistiques précises : n'invente aucun chiffre réel, donne des ordres de grandeur
  qualitatifs ou écris « for example, suppose ... ».
- Les calculs (Paper 3 et QCM) sont recalculés avec Python ; formule, remplacement, résultat avec unités et monnaie (FCFA), arrondi demandé.
- Un diagramme que le candidat doit dessiner (offre/demande, coûts, IS-LM, frontière des possibilités de production) : décris-le précisément dans le corrigé (axes, courbes,
  points d'équilibre, déplacements) ; produis un PNG (matplotlib, `D:\edukora\venv\Scripts\python.exe`, fond blanc, axes légendés) seulement quand il rend la réponse réellement compréhensible,
  et déclare-le dans `figures` avec son placeholder `![fig-1](...)`.
- Formules en LaTeX entre `$...$`, antislash doublé dans le JSON ; équation numérotée avec `\\tag` : formule sur trois lignes (`$$`, formule, `$$`).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, propres à l'économie, par exemple : `demand and supply`, `price elasticity`, `consumer behaviour`, `costs and revenue`,
`market structures`, `monopoly power`, `factors of production`, `national income accounting`, `economic growth`, `economic development`, `public finance`, `taxation`,
`money and banking`, `central banking`, `monetary policy`, `fiscal policy`, `unemployment`, `price level changes`, `international trade`, `exchange rates`, `balance of payments`,
`regional integration`, `population and labour`, `agricultural economics`, `industrialisation`, `economic planning`, `multiplier and accelerator`, `externalities and market failure`.
`Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières : jamais un mot qui existe tel quel en français (« inflation », « population », « agriculture », « production »,
« taxation » seuls...) ni le nom d'un thème d'une autre matière. Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans
`D:\edukora\backend\ingest\cm\gce-al-economics-*\*.json` et `_gce_staging\gce-al-economics-*\*.json` : réutilise le nom quand la notion est la même.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0725 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS
l'ingestion, ne touche ni à la base ni à Docker ni à git.
