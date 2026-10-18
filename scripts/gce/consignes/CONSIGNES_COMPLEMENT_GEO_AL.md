# Complément aux consignes - GCE ADVANCED LEVEL, GEOGRAPHY (code 0750)

Lis `CONSIGNES.md` (forme générale, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce fichier.
**Ce fichier prime** pour tout ce qui touche à la Géographie : codes, noms de dossier, papers, règles de choix, cartes, corrigés, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Geography"`, `code_matiere` `"0750"`
  (page de garde : « ADVANCED LEVEL », « 0750 »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-geography-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_GEOGRAPHY_<ANNEE>_P<n>.pdf`
  (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30, calculatrice permise. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir `CONSIGNES_COMPLEMENT_AL.md`). Un QCM numérique (échelle,
  gradient, densité, pente) se justifie par le calcul ; un QCM factuel ambigu ou une clé imprimée douteuse : convertis en `ouverte` (`convertir_en_ouverte.js`).
  Une carte, un graphique ou un schéma imprimé dont dépend le QCM se recadre en PNG.
- **Paper 2** : 3 h, « Answer FOUR questions, choosing at least ONE from each Section », 25 points chacune. Repère les sections imprimées (SECTION A, B...). UN fichier PAR QUESTION,
  `numero_exercice` = le numéro imprimé (ou `"B1"`... si une section renumérote), `groupes` = le repère de section. `regles_choix` : UNE règle
  `{"type":"total","portee":"PAPER 2","repondre":4,"minimum":1,"groupes":["SECTION A","SECTION B","SECTION C"]}` (les sections imprimées), identique dans tous les fichiers du dossier ;
  recopie la consigne complète dans `introduction_markdown`. Si le sujet dit « ONE from each section » avec autant de sections que de questions à traiter, un `parmi` 1 par section est exact.
- **Paper 3** : 3h15, « Answer FOUR questions in all » : la question 1 (cartographie / carte topographique, ~31 points) est OBLIGATOIRE ; une question à choisir dans la SECTION B et DEUX dans la
  SECTION C (lis la page de garde, ces nombres varient selon les années). UN fichier PAR QUESTION. `groupes` : `["SECTION A"]` pour la question 1 (ou le repère imprimé), `["SECTION B"]`, `["SECTION C"]` ;
  `regles_choix` : `parmi` par section à choix (`repondre` = le nombre exigé, `sur` = le nombre de questions de la section), rien pour la question obligatoire. Matériel annoncé (« topographic map, graph paper,
  outline maps of Cameroon ») : **les cartes et le papier ne sont pas dans le PDF** ; transcris l'énoncé fidèlement, écris dans l'énoncé « [topographic map supplied on the day, not reproduced here] » quand
  une carte manque, et donne en corrigé la MÉTHODE (calculs d'échelle, d'intervalle de courbes, de gradient, de coupe, d'orientation, lecture de références de grille) avec des exemples génériques, sans inventer
  des valeurs de la carte absente ; signale-le dans `incertitudes`.
- Sous-questions (a), (b)... = `questions` ; points entre crochets dans `points`. `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"`, `"3h"` ou `"3h15"`.

## Corrigés

- Niveau Advanced : définitions précises, exemples localisés (Cameroun, Afrique, monde), schémas et cartes annotés décrits, argumentation et évaluation pour « discuss / account for / assess ».
  Une réponse modèle complète, avec des exemples réels RECONNUS ; **n'invente aucune statistique précise, date, nom de lieu inexistant ou citation** ; en cas de doute, formulation prudente (« about », « in
  the early 2000s ») ou retrait du détail ; consigne dans `incertitudes` tout fait non certain.
- Calculs (échelle, densité, indices statistiques, coefficient de corrélation de rang de Spearman, gradient, pente) : recalcule avec Python ; formule, remplacement, résultat avec unités.
- Un schéma ou une carte que le candidat doit dessiner : décris-le précisément dans le corrigé (légende, éléments à annoter). Tu peux produire un PNG (matplotlib, `D:\edukora\venv\Scripts\python.exe`, fond blanc,
  légendé) seulement quand il rend la réponse réellement compréhensible ; déclare-le dans `figures` (`type` de figure : 30 caractères MAXIMUM) avec son placeholder `![fig-1](...)`.
- Une carte, un graphique ou un diagramme imprimé dans le sujet se recadre en PNG, déclaré dans `figures`.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, propres à la géographie : par exemple `map reading and interpretation`, `topographic map skills`, `drainage basins`, `river processes`, `weathering and mass movement`,
`coastal landforms`, `glaciation`, `karst landscapes`, `volcanic and tectonic activity`, `climate and weather systems`, `tropical rainforest ecosystem`, `savanna ecosystems`, `soil formation`, `water resources`,
`population distribution and migration`, `rural settlement patterns`, `urban growth and planning`, `agricultural systems`, `industrial location`, `energy resources`, `transport networks`, `regional development in cameroon`,
`environmental hazards`, `sustainable resource management`, `geographical statistics`. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français (Géographie BEPC/Probatoire/BAC) : n'emploie pas un mot
qui existe tel quel en français (« population », « urbanisation », « climat »...) ni une variante d'accent ou de pluriel d'un thème français : préfère des noms qualifiés comme ci-dessus. Avant de créer un nom, fais un
`Grep` des valeurs `"themes"` déjà utilisées dans `D:\edukora\backend\ingest\cm\gce-al-geography-*\*.json` et `_gce_staging\gce-al-geography-*\*.json` : réutilise le nom quand la notion est la même.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0750 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS
l'ingestion, ne touche ni à la base ni à Docker ni à git.
