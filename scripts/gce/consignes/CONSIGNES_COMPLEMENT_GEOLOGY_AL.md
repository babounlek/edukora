# Complément aux consignes - GCE ADVANCED LEVEL, GEOLOGY (code 0755)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce fichier.
**Ce fichier prime** pour tout ce qui touche à la Géologie : codes, noms de dossier, papers, règles de choix, schémas, corrigés, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Geology"`, `code_matiere` `"0755"` (page de garde : « ADVANCED LEVEL », « 0755 GEOLOGY »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-geology-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_GEOLOGY_<ANNEE>_P<n>.pdf` (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30, calculatrice non programmable permise. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre,
  `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Beaucoup de QCM s'appuient sur une figure (coupe de la Terre, axes cristallographiques, bloc-diagramme, carte géologique, diagramme de phase, fossile) :
  la figure se reproduit via le skill (jamais `pdftoppm`) et se rattache à la question qui la cite (« Study the figure... and answer questions 8 and 9 » : la même figure sert aux deux, dis-le dans l'énoncé de chacune).
  Un QCM numérique (âge radiométrique, demi-vie, échelle, pendage, épaisseur) se recalcule avec Python. Un QCM factuel dont deux options sont défendables, ou dont la clé semble fausse : convertis en `ouverte`
  (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- **Paper 2** : 3 h, « Answer FOUR questions. All questions carry equal marks » (6 questions de 25 points : lis la page de garde de CHAQUE année pour le nombre de questions et d'éventuelles sections ;
  « the value of clear sketches » est rappelée). UN fichier PAR QUESTION, `numero_exercice` = le numéro imprimé, sous-questions (a), (b), (c)... = `questions`. Sans sections : `groupes` `["PAPER 2"]` dans chaque fichier et
  `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":4,"sur":<N imprimé>}]`, identique dans TOUS les fichiers. Avec sections : une règle `parmi` par section, consigne complète dans `introduction_markdown`
  et `incertitudes`. `points` de l'exercice = le total imprimé (« Total = 25 marks »), points des sous-questions entre crochets.
- Les papers pratiques ou de terrain, s'il en existe un dans le lot : transcris l'énoncé, donne la méthode en corrigé, signale que les échantillons, cartes ou photographies fournis le jour de l'épreuve ne sont pas reproduits.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"` ou `"3h"`.

## Corrigés (exactitude avant tout)

- Niveau Advanced : réponse complète d'un candidat qui obtient tous les points (définition exacte, processus, exemples, schéma décrit ou légendé). Respecte « define », « state », « describe », « explain », « discuss »,
  « with the aid of a diagram », « outline » ; ne dépasse pas le nombre d'éléments demandés (« five differences » = cinq).
- Programme : astrogéologie et structure interne de la Terre, minéralogie et cristallographie (systèmes cristallins, groupes de minéraux, propriétés physiques), roches ignées (série de Bowen, structures intrusives et extrusives),
  roches sédimentaires (environnements, textures, structures), roches métamorphiques (métamorphisme de contact, régional, faciès), tectonique des plaques, séismes et ondes sismiques, géologie structurale (plis, failles, discordances),
  paléontologie et fossiles, stratigraphie et datation (relative, radiométrique), géomorphologie fluviale, côtière et glaciaire, ressources minérales, hydrogéologie, géologie de l'ingénieur et choix d'une carrière,
  géologie du Cameroun (volcans de la ligne du Cameroun, bassins sédimentaires, socle). Cartes géologiques : lecture, coupes, pendage et direction.
- **N'invente aucune donnée** : âges, coordonnées, noms de formations, valeurs de dureté, densités, compositions chimiques : valeurs classiques de cours, formulation prudente (« about », « typically ») en cas de doute,
  trace dans `incertitudes` tout fait local (un site, une formation ou une roche du Cameroun : composition, âge, localisation) que tu n'as pas pu établir avec certitude. Une datation radiométrique
  ($t = \dfrac{1}{\lambda}\ln\left(1+\dfrac{D}{P}\right)$, demi-vie) se recalcule avec Python ; une règle des phases ou un calcul de pendage se vérifie de même.
- Une coupe, un bloc-diagramme, une carte géologique imprimés : suis la section Figures de `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ; `figures[].type` : 30 caractères MAXIMUM.
  Un schéma que le candidat doit tracer se décrit dans le corrigé (éléments à dessiner, légende, titres des axes), jamais inventé en valeurs.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, **propres à la Géologie** : par exemple `crystallographic systems and axes`, `mineral groups and physical properties`, `bowen reaction series`,
`igneous rock structures and textures`, `sedimentary environments and structures`, `metamorphic rocks and metamorphism types`, `plate tectonics and sea floor spreading`, `earthquakes and seismic waves (geology)`,
`folds faults and unconformities`, `fossils and palaeoenvironments`, `radiometric dating methods`, `geological time scale and stratigraphy`, `river erosion and sedimentary landforms`, `coastal geology and landforms`,
`mineral resources and ore deposits`, `engineering geology and quarry site selection`, `groundwater and aquifers`, `geology of cameroon`, `astrogeology and the solar system`, `structure of the earth`.
`Tag.name` est UNIQUE et PARTAGÉ avec la SVT et la Géographie (françaises et GCE), la Chimie et la Physique : n'emploie pas un mot qui existe tel quel en français ou en Géographie
(`volcanisme`, `séismes`, `tectonique`, `roches`, `fossiles`, `erosion`, `rivers`, `earthquakes`, `volcanoes`, `rocks`, `minerals`, `plate tectonics`, `weathering`...) ni une variante d'accent ou de pluriel :
préfère des noms qualifiés (3 à 5 mots) ou suffixés par « (geology) ».
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-al-geography-*\*.json`, `gce-ol-geography-*`, `gce-ol-physics-*` et `gce-al-physics-*` (pour NE PAS les réutiliser)
et dans `cm\gce-al-geology-*` et `_gce_staging\gce-al-geology-*` (pour RÉUTILISER les noms des autres papers de Geology : plusieurs agents travaillent en parallèle, relis les dossiers des autres avant de créer un nom,
n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2> --code 0755 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
