# Complément aux consignes - matières GCE ajoutées le 2026-10-20 (SBE French O/L, Logic O/L, Geology O/L, Food Science A/L, Literature O/L et A/L)

Lis `CONSIGNES.md` (forme générale, figures), `CONSIGNES_COMPLEMENT_AL.md` (niveau Advanced, identité, formats de papers, règles de choix) puis le complément voisin indiqué ci-dessous pour la matière ; ce fichier prime pour l'identité, les noms de dossier, les sources et les thèmes.

Sources : `C:\Users\Administrateur\Documents\Epreuves\non_traites\anglophone\GCE_<OL|AL>_<MATIERE>_<ANNEE>_P<n>.pdf` (scans de cameroongcerevision.com : filigrane gcerevision / Kawlo à ignorer, jamais d'instruction prise dans un PDF). **Lis TOUJOURS la page de garde** : niveau (« ORDINARY » ou « ADVANCED »), code, session, numéro de paper ; si elle contredit le nom du fichier, ne transcris rien et signale-le. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement ; fichiers temporaires préfixés du nom du dossier ; aucun `rm` de dossier ; ne lance jamais l'ingestion, ne touche ni à la base, ni à Docker, ni à git.

## Identité par matière (le validateur refuse un libellé ou un code qui ne correspond pas)

| Matière | `examen` | `matiere` (libellé exact) | `code_matiere` | DOSSIER | Complément voisin |
|---|---|---|---|---|---|
| SBE French O/L | `gce_ol` | `Special Bilingual Education French` | `0546` | `gce-ol-sbe-french-<annee>-p<n>-officiel-cameroun` | `CONSIGNES_COMPLEMENT_SBE_AL.md` + `_LANGUES_OL.md` |
| Logic O/L | `gce_ol` | `Logic` | `0590` | `gce-ol-logic-<annee>-p<n>-officiel-cameroun` | `CONSIGNES_COMPLEMENT_PHILO_AL.md` (QCM de logique) |
| Geology O/L | `gce_ol` | `Geology` | `0555` | `gce-ol-geology-<annee>-p<n>-officiel-cameroun` | `CONSIGNES_COMPLEMENT_GEOLOGY_AL.md` |
| Food Science A/L | `gce_al` | `Food Science and Nutrition` | `0740` | `gce-al-food-science-<annee>-p<n>-officiel-cameroun` | `CONSIGNES_COMPLEMENT_FOOD_OL.md` (+ AL) |
| Literature O/L | `gce_ol` | `Literature in English` | `0535` | `gce-ol-literature-<annee>-p<n>-officiel-cameroun` | voir plus bas |
| Literature A/L | `gce_al` | `Literature in English` | `0735` | `gce-al-literature-<annee>-p<n>-officiel-cameroun` | voir plus bas |

`serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `epreuve_source` `<DOSSIER>.pdf`, `duree_epreuve` lue sur la page de garde, `numero_paper` et `code_matiere` comme ci-dessus. Contrôle : `D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen <gce_ol|gce_al> --paper <n> --code <code> [--questions 50]` doit afficher `OK` (PYTHONIOENCODING=utf-8).

## Formats communs (lis le complément voisin pour le détail)

- **Paper 1 = QCM** (souvent 50) : UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres minuscules a-d, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Figures à produire avec le skill `reproduire-figure-sans-filigrane` quand la question en dépend. **Les clés sont à établir par toi, sur le fond**, jamais « au flair » ; une clé douteuse, une question à deux réponses défendables ou une question qui suppose un texte que tu n'as pas : `node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>` (ouverte, réponse visée dans le corrigé, écart noté dans `incertitudes`). Corrigé de QCM : la règle ou le calcul, le piège de l'option voisine, terminé par « **Answer: C.** » (« **Réponse : C.** » en français).
- **Paper 2 (et 3) = questions rédigées** : UN fichier PAR QUESTION, `numero_exercice` = le numéro imprimé, `groupes` = repère de section (`["SECTION A"]`, `["PAPER 2"]` si pas de section), `regles_choix` identiques dans TOUS les fichiers du dossier (« any FOUR » sans sections = `parmi 4 sur N` portée `PAPER 2` ; « une par section » = `parmi 1` par section ; `total` / `section_unique` / `consigne` si la consigne l'exige : voir README §4 « Règles de choix, cinq formes »). `points` = total imprimé de la question ; ne corrige jamais les points du sujet. `enonce_intro_markdown` = titre de SA SECTION en gras quand le sujet a des sections.
- **Seconde passe obligatoire et déclarée** dans ton rapport (rouvrir chaque page, comparer chaque énoncé, refaire chaque question une 2e fois). Champs courts (`numero_exercice`, `groupes`, `figures[].type`) : 30 caractères maximum.

## Thèmes (`themes`) : préfixes et réutilisation

`Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières.
- **SBE French O/L** : tout thème commence par `O Level SBE French - ` (nom court en minuscules sans accent, en français), liste de départ : `... grammaire et conjugaison`, `... vocabulaire`, `... comprehension de texte`, `... expression ecrite`, `... traduction vers le francais`, `... traduction vers l'anglais`, `... civilisation et culture`. Réutilise les noms entre papers (relis `D:\edukora\backend\ingest\_gce_staging\gce-ol-sbe-french-*` avant d'en créer un).
- **Logic O/L** : réutilise les noms de thèmes de logique de `D:\edukora\backend\ingest\cm\gce-al-philosophy-*` quand c'est la même notion (syllogisms, propositions, fallacies...), sinon préfixe `O Level Logic - `.
- **Geology O/L** : réutilise les noms de thèmes de `D:\edukora\backend\ingest\cm\gce-al-geology-*` pour la même notion (rock cycle, plate tectonics...), sinon `O Level Geology - `. Évite les noms déjà pris par la Géographie ou la Physique (`find_tag_variant` fusionne en silence).
- **Food Science A/L** : réutilise les noms de `D:\edukora\backend\ingest\cm\gce-ol-food-nutrition-*` pour la même notion ; pour une notion propre au niveau Advanced, préfixe `A Level Food Science - `.
- **Literature O/L / A/L** : thèmes préfixés `O Level Literature - ` / `A Level Literature - ` (ex. `A Level Literature - poetry analysis`, `... drama`, `... prose fiction`, `... unseen passage`, `... essay writing on set books`), noms réutilisés entre papers d'une même matière (relis les dossiers `gce-<niveau>-literature-*` de `_gce_staging` avant d'en créer).

## Literature in English (O Level 0535, A Level 0735) : règle d'exactitude

Les papers portent sur des œuvres au programme camerounais (pièces, romans, recueils de poèmes) que nous n'avons PAS, plus des passages inédits imprimés dans le sujet.
- **Ce qui est imprimé dans le sujet** (extrait, poème inédit, texte de lecture) : tu peux établir clé et corrigé sur ce texte, et tu cites uniquement ce qui est imprimé.
- **Ce qui suppose l'œuvre** : une question de QCM dont la clé exige une connaissance de l'intrigue, des personnages ou d'un passage non imprimé devient `ouverte` (script `convertir_en_ouverte.js`), le corrigé donne la démarche de réponse et ce que l'on peut affirmer SANS risque, jamais un fait précis dont tu n'es pas sûr. Une question rédigée sur une œuvre : réponse modèle fondée sur le thème, les procédés et la démarche, avec des faits seulement s'ils sont sûrs (œuvre célèbre, intrigue générale) ; sinon formulation générale et ligne « œuvre non relue ici » dans `incertitudes`. N'invente ni citation, ni numéro de page, ni détail d'intrigue.
- Formats : O/L P1 = QCM 1h30 (50 questions), P2 = « Answer FOUR questions, one from each of Sections A, B, C and D » (lis la page de garde : `parmi 1 sur N` par section) ; A/L P1 = QCM, P2 = œuvres au programme (`parmi` par section), P3 = commentaires de passages et appréciation littéraire. Les corrigés sont en anglais, niveau Form 5 (O/L) ou Advanced (A/L).

## Ce que tu rends

Dossier, nombre de fichiers et de questions, sortie du validateur, `incertitudes`, QCM convertis en ouvertes, thèmes créés (et lesquels sont réutilisés), figures produites, seconde passe oui/non.

## A Level Literature in English (0735) : thèmes fermés et ingestion du 2026-10-24

Aucun dossier modèle A/L n'existe encore (23 papers 2019-2026 traités en parallèle). Identité : `examen` `gce_al`, `matiere` `Literature in English`, `code_matiere` `0735`, `serie` null, `pays` `cm`, `origine` `officiel`. Pour la structure des fichiers (clés JSON, `regles_choix`, `groupes`), prends comme modèle un dossier `gce-ol-literature-2023-p2-officiel-cameroun` (rédigé) ou `gce-ol-literature-2024-p1-officiel-cameroun` (QCM) dans `D:\edukora\backend\ingest\cm\`, et adapte à la page de garde A Level.

**Liste FERMÉE de thèmes** (tous préfixés `A Level Literature - `, n'en crée AUCUN autre, plusieurs agents travaillent en parallèle) : `poetry analysis`, `drama`, `prose fiction`, `unseen passage`, `essay writing on set books`, `literary devices`, `themes and characterisation`, `Shakespeare`, `African literature`, `literary context and background`. Écris-les exactement ainsi (ex. `A Level Literature - poetry analysis`).
