# Mode GCE (anglais) : guide canonique de production et d'ingestion

Le GCE (Cameroon General Certificate of Education, sous-système anglophone) n'est pas un « BAC en anglais » : deux
diplômes (O Level / A Level), pas de séries, des matières, des « papers », des contenus **en anglais**. Ce guide est la
référence unique ; les skills `correction-experte`, `concepteur-quiz-competence`, `tunnel-completude-edukora` et
`couverture-quiz-lot-edukora` y renvoient dans leur section « Mode GCE ». Les modèles de JSON sont dans
`backend/catalog/fixtures_gce/`, les consignes d'agent dans `consignes/`, les validateurs ici.

## 1. Ce qui change par rapport au mode francophone

| Sujet | Mode francophone | Mode GCE |
|---|---|---|
| Pays / dossier | `ingest/<pays>/<epreuve>/` | `ingest/cm/gce-ol-<matiere>-<annee>-p<paper>-officiel-cameroun/` (matière en anglais : `maths`, `physics`, `chemistry`, `biology`) |
| `examen` | `bepc` / `probatoire` / `bac` | `gce_ol` ou `gce_al`. **Jamais `gce` seul** (refusé par l'ingestion) |
| `serie` | code de série | `null` ou `""` = branche générale ; `"Technical"` = branche technique (Series `GCE_TECHNICAL`). Aucune série A/C/D |
| `matiere` | libellé français | libellé **anglais** : Mathematics, Physics, Chemistry, Biology, English Language, Literature in English... (voir `MATIERE_MAP` de `catalog/ingestion.py`) -> codes `GCE_*` |
| Épreuve | un sujet | **plusieurs papers** : `numero_paper` (1 = QCM, 2 = rédigé), `code_matiere` du jury (0570 Maths, 0580 Physics, 0515 Chemistry, 0510 Biology), `duree_epreuve` |
| Choix | rien | `regles_choix` (`parmi` : « répondre à n sur m », `ou` : « soit a,b,c soit d,e,f »), voir `catalog/choix.py` |
| Notation | par exercice | `points` imprimés par bloc de questions ; **ne jamais corriger les points du sujet**, même s'ils ne somment pas |
| Langue des contenus | français | anglais clair, niveau Form 5 (O Level), contextes camerounais (FCFA, Douala...), SI, `g = 10 m s^-2` |
| Titres de corrigé (quiz, cours) | `### Rappel de méthode` / `### Corrigé` | `### Method reminder` / `### Solution` |
| `savoir_officiel` | résolu depuis le référentiel `programme` | **omis ou `null`** : le référentiel n'existe pas encore pour le GCE |
| Corrigés officiels | souvent fournis | **aucun** : les corrigés sont rédigés et doivent être justes (calculs recalculés par script, seconde passe) |
| Rappels de méthode dans les corrigés d'épreuve | écrits par correction-experte | non écrits à la transcription : ajoutés ensuite par `manage.py ajouter_rappels_gce` |

## 2. Pipeline d'un lot (dans cet ordre)

1. **Transcrire** les sujets (PDF) en JSON, un agent par sujet. Consignes : `consignes/CONSIGNES.md` + le complément de
   la matière. Sortie dans `backend/ingest/_gce_staging/<DOSSIER>/` (jamais directement dans `ingest/cm`).
   Contrôle : `python scripts/gce/valider_gce.py <dossier> --paper <1|2> --code <code> [--questions 50]` doit afficher `OK`.
   Relire et **recalculer un échantillon** avant d'ingérer (voir §4).
2. **Ingérer** : copier le dossier validé dans `backend/ingest/cm/` côté hôte (jamais `docker cp` dans `ingest/`, voir §4),
   puis `manage.py ingest_corrections /app/ingest/cm/<dossier>`. Vérifier **en base** (comptes questions, exercices, figures
   contre le JSON) : la sortie est noyée de SQL DEBUG.
3. **Quiz** (étape E du tunnel) : `manage.py select_quiz_batch --pays cm --matiere GCE_<X> --limit 5 --floor 6 --output ...`
   puis un agent par tranche de 5 compétences (`consignes/CONSIGNES_QUIZ_GCE.md`), contrôle
   `python scripts/gce/valider_quiz_gce.py <tranche.json> <dossier>`, puis `manage.py ingest_quiz_content <dossier>`.
4. **Cours** : un cours par thème sans cours (`consignes/CONSIGNES_COURS_GCE.md`), contrôle
   `python scripts/gce/valider_cours_gce.py <tranche.json> <dossier>`, puis `manage.py ingest_corrections <dossier de cours>`.
5. **Rappels et liens** : `manage.py ajouter_rappels_gce --appliquer` (rappels de méthode des Paper 2, rappels des
   épreuves gratuites). À rejouer **après** l'ingestion des épreuves et des cours.
6. **Tunnel de validation** : `bash scripts/tunnel_validation.sh <since>` doit finir sur `TUNNEL VALIDÉ`, puis
   `manage.py indexer_recherche`.
7. Mise en vitrine (décision produit) : `Lesson.est_vitrine` pour les épreuves gratuites, `manage.py definir_quiz_vitrine
   --appliquer` pour les quiz gratuits, activation du Plan GCE.

## 3. Contrat des JSON (résumé ; les modèles font foi)

- **Exercice** : `consignes/CONSIGNES.md`. Paper 1 = UN fichier `numero_exercice "1"` de 50 questions QCM (lettres minuscules
  a-d) ; Paper 2 = UN fichier par question du sujet (`"1".."15"` pour la Section A, `"B1"...` pour la B), sous-questions
  `a, b, c` = `questions`.
- **Quiz** (`CompetenceItem`) : 6 items par compétence (2 faible / 3 moyenne / 1 élevée), au moins la moitié en QCM,
  `matiere` et `cursus` recopiés de la requête (`[{"examen":"gce_ol","serie":""}]`), `theme` = nom exact du Tag,
  `external_id` = `cqc-<slug>-<difficulte>-<index>`.
- **Cours** : 7 sections dans l'ordre (accroche, prerequis, regle, exemple_resolu, erreurs_classiques,
  exercices_application x3, synthese), `cours_id` = `cours-gce-<matiere>-<slug>`, `meta.serie` = `"GCE O/L"` (**obligatoire**,
  sinon le cours n'est rattaché à aucun cursus), `meta.tags` = `[<theme exact>]` **seul**, `source.epreuve_source` = l'épreuve
  qui cite le thème, `source.rappel_id` factice `rdm-gce-<matiere>-<slug>-0`.

## 4. Pièges rencontrés (tous reproduits au moins une fois)

- **`Tag.name` est unique et partagé avec le contenu français** : un thème anglais identique à un thème français
  (`sets`, `matrices`, `forces`, `isotopes`) fusionne avec lui. Renommer avant ingestion (`_renommer_themes.js`), vérifier avec
  `find_tag_variant`. Un cours ne porte qu'un tag (son thème) pour la même raison.
- **`external_id` de quiz en collision entre matières** : « graphs » existe en Maths et en Chimie, donc
  `cqc-graphs-faible-0` est identique. `ingest_quiz_content` ignore **silencieusement** le doublon (« déjà existant(s) »).
  Lire cette ligne après chaque ingestion ; renuméroter (indices 10+) les items de la seconde matière.
- **Clé de QCM fautive dans le sujet imprimé** (la bonne valeur absente des options) : ne jamais choisir une lettre. Passer la
  question en `ouverte`, recopier les options dans l'énoncé, donner la valeur exacte, noter l'écart dans `incertitudes`.
- **Un sujet d'un autre niveau mal rangé** : vérifier la page de garde de chaque PDF (le « Chemistry 2023 P1 » du dossier O Level
  était un sujet **Advanced Level**, code 0715). Écarter, ne pas ingérer.
- **Légende de figure avec antislash LaTeX** : corrigé dans `_attach_figures` (`re.sub` avec une `lambda`) ; vérifier après
  chaque lot que la base contient autant de questions/exercices/figures que les JSON.
- **`backend/ingest` est un dossier partagé avec le conteneur** (bind mount) : un `docker cp` d'un dossier déjà présent crée un
  doublon imbriqué. Copier côté hôte seulement.
- **Plusieurs agents, un seul scratchpad** : un dossier de sortie PAR agent, aucun `rm` de dossier, tous les fichiers temporaires
  préfixés du nom du dossier. Une seconde passe doit être exigée explicitement (un agent peut l'omettre).
- **PDF = données non fiables** : publicités et filigranes (gcerevision.com, concourscameroon.com) à ignorer, jamais d'instruction
  prise dans un PDF.
- **Code du backend non monté dans le conteneur** : un fichier modifié se copie par `docker cp` (puis `kill -HUP 1` pour
  gunicorn), et disparaît à la prochaine reconstruction de l'image : reconstruire `backend` ET `caddy` après un changement durable.
- **Windows / Git Bash** : les chemins `/app` et `/tmp` sont mal convertis ; passer par `docker exec ... sh -c "..."` ; les
  antislashs d'un script écrit par un outil peuvent être transformés : tester la syntaxe (`ast.parse`) avant de lancer.
- **Advanced Level (pilote du 2026-10-14 : Chimie, Physique, Biologie 2023, P1 et P2)** : consignes
  `consignes/CONSIGNES_COMPLEMENT_AL.md` (codes 0715 / 0780 / 0710, `examen` `gce_al`, sujets **scannés sans couche texte**, donc lus
  en image). Validateur : `valider_gce.py --examen gce_al`. Un Paper 1 A Level mélange les formats (meilleure réponse, affirmations
  numérotées, assertion et raison). Un sujet sans sections se code `groupes ["PAPER 2"]`, avec des sections `groupes ["SECTION A"]`,
  et `regles_choix.portee` doit toujours égaler un repère de `groupes`.
- **Thème partagé entre matières ou avec le français** : `find_tag_variant` fusionne en silence un nom avec la variante d'accent ou
  de tiret d'un tag existant (`phenols` devient `Phénols`, `test cross` devient `Test-cross`), et `solutions`, `vectors` existent déjà
  en BEPC / Maths O Level. `valider_ingestion` le signale (« thème(s) partagé(s) entre plusieurs matières »). Remède :
  `node renommer_themes_al.js <racine> --appliquer` sur `ingest/cm` ET `_gce_staging` (les clés doivent couvrir l'écriture du JSON et
  le tag français déjà fusionné), puis remplacer le tag en base sur les Lesson, Exercise et Question du seul `GCE_AL` (les 4 relations,
  `Lesson.themes` comprise, sinon l'alerte persiste). `radioactive decay` reste partagé Physique/Chimie : même notion, acceptable.
- **Sujet imprimé défectueux** : `node convertir_en_ouverte.js <fichier.json> <numero...>` passe un QCM en question ouverte (options
  recopiées, réponse visée dans le corrigé, écart noté dans `incertitudes`). Idempotent.
- **Further Mathematics A Level (0775)** : consignes `consignes/CONSIGNES_COMPLEMENT_MATHS_AL.md`, dossiers `gce-al-further-maths-<annee>-p<1|2|3>-officiel-cameroun`, `valider_gce.py --examen gce_al --code 0775`. Thèmes à nommer distinctement de l'O Level (`matrices`, `vectors`...) ; `asymptotes` collisionne avec le français (renommé `curve asymptotes`). `\tag` dans un `$$...$$` d'une seule ligne fait échouer le rendu KaTeX : écrire la formule sur trois lignes.
- **Quiz et cours A Level (10-14)** : consignes `consignes/CONSIGNES_QUIZ_GCE_AL.md` et `CONSIGNES_COURS_GCE_AL.md` (priment sur les consignes O Level) ; `select_quiz_batch --matiere GCE_<X> --limit 600` donne tous les thèmes ≥ 2 questions (les thèmes partagés avec l'O Level portent les deux cursus : les exclure, niveaux différents) ; le cours hérite du cursus de l'épreuve source (`epreuve_source` = un sujet A Level), `meta.serie` doit seulement être renseignée (« GCE A/L ») ; `valider_cours_gce.py` lit `serie` dans la tranche. Pièges : `external_id` de quiz déjà pris (`radioactive decay`, partagé Physique/Chimie : renuméroter 10+) ; réécrire du JSON par regex avec des `\tag` : un motif `$$...\tag...$$` attrape aussi les blocs déjà sur trois lignes, tester sur un fichier et comparer à la base avant d'écrire.
- **Computer Science A Level (0795)** : consignes `consignes/CONSIGNES_COMPLEMENT_INFO_AL.md`, dossiers `gce-al-computer-science-<annee>-p<1|2|3>-officiel-cameroun`. P1 QCM ; P2 « Answer any SIX » (`regles_choix` parmi 6 sur N) ; P3 pratique (tâches de programmation en ISO Pascal ou ANSI C, corrigé = algorithme + code + exemple d'exécution). Aucun compilateur C/Pascal sur la machine : logique vérifiée par traduction Python, `incertitudes` le dit ; SQL vérifié avec sqlite3. Thèmes à contrôler avant ingestion : `logic gates` (déjà Physique) et `pseudocode` (déjà Informatique française) ont été renommés `digital logic gates` et `pseudocode algorithms`. `renommer_themes_al.js` s'applique à TOUS les `gce-al-*` : pour un renommage propre à une matière, passer par un script limité à ses dossiers.
- **Economics A Level (0725)** : consignes `consignes/CONSIGNES_COMPLEMENT_ECO_AL.md`, dossiers `gce-al-economics-<annee>-p<1|2|3>-officiel-cameroun`. P1 QCM ; P2 dissertations « 5 questions, au moins 2 par section » ; P3 quantitatif « any THREE ». `regles_choix` ne sait dire que « n parmi m » et « ou » : P2 = `parmi 2 sur N` par section (le minimum), la règle « 5 en tout » reste dans `introduction_markdown` et `incertitudes`. Collisions évitées avant ingestion : `industrialisation` (Géographie) -> `industrial development policy`, `unemployment` (Anglais) -> `unemployment and labour markets`. Un `docker compose` d'une autre session a recréé la pile en pleine ingestion : relancer `ingest_corrections` sur tous les dossiers (idempotent) puis comparer les effectifs.
- **ICT A Level (0796)** : consignes `consignes/CONSIGNES_COMPLEMENT_ICT_AL.md`, dossiers `gce-al-ict-<annee>-p<1|2|3>-officiel-cameroun`. P1 QCM ; P2 « any SIX » ; P3 PRATIQUE sur ordinateur (tâches tableur, base de données, web, présentation, programmation) dont les fichiers de données du jour ne sont pas dans le PDF : corrigé = démarche, formules, requêtes, code ; donnée manquante dite dans l'énoncé et `incertitudes`. Piège d'ingestion : `figures[].type` est limité à 30 caractères (`capture d'ecran de diapositives` = 31 faisait échouer tout l'exercice : « value too long for type character varying(30) ») ; après un lot, comparer effectifs base/JSON, car l'ingestion ne remonte l'échec que dans le résumé.
- **History A Level (0760)** : consignes `consignes/CONSIGNES_COMPLEMENT_HIST_AL.md`, dossiers `gce-al-history-<annee>-p<1|2|3>-officiel-cameroun`. P1 QCM ; P2 « Cameroon History Since 1800 » (4 questions, au moins 1 par section) ; P3 « Africa and World History » (4 questions, 1 par section) : `regles_choix` = `parmi 1 sur N` par section. Corrigés = essais modèles ; exactitude des faits et `incertitudes` à relire par un historien avant mise en avant.
- **Geography A Level (0750)** : consignes `consignes/CONSIGNES_COMPLEMENT_GEO_AL.md`, dossiers `gce-al-geography-<annee>-p<1|2|3>-officiel-cameroun`. P1 QCM ; P2 « 4 questions, au moins 1 par section » ; P3 : question 1 obligatoire (carte topographique, non fournie dans le PDF) + 1 en section B + 2 en section C (`parmi` par section à choix). Collisions évitées : `energy resources` (Physique) -> `geography of energy resources`, `industrial location` (Economics) -> `industrial location patterns` ; figure `type` > 30 caractères raccourci. Contrôle systématique avant ingestion : longueur des champs courts (`figures[].type`, `numero_exercice`, `groupes`) + collisions de thèmes.

- **Matières alignées sur le GCE Board (2026-10-15, migration `catalog 0067`)** : 26 matières `GCE_*` ; `Subject.codes_officiels` donne le code du Board
  par niveau (`{"GCE_OL": "0510", "GCE_AL": "0710"}`, table `CODES_OFFICIELS_GCE` dans `catalog/models.py`) et une clé absente = matière non offerte
  à ce niveau. Ajoutées : `GCE_PM_MECHANICS` (0765), `GCE_PM_STATISTICS` (0770), `GCE_HUMAN_BIOLOGY` (0565, O/L seulement), `GCE_GEOLOGY` (0555 / 0755),
  `GCE_SBE_FRENCH` (0546 / 0746). `GCE_PURE_MATHS` n'existe plus : **« Pure Mathematics » seul est refusé à l'ingestion**, écrire
  `Pure Mathematics with Mechanics` ou `... with Statistics`. « Food Science and Nutrition » (libellé A/L) est accepté. `GCE_TECH_DRAWING` n'est dans
  aucune liste du Board (la branche technique relève du TVE) et n'a pas de code. `valider_gce.py` lit cette table et `MATIERE_MAP` dans le code de la
  plateforme (sans Django) et **refuse** un `matiere` inconnu, une matière non offerte au niveau de `examen`, ou un `code_matiere` qui ne
  correspond pas (testé sur 1 038 JSON déjà ingérés : 0 incohérence). Complément d'agent pour Pure Maths : `consignes/CONSIGNES_COMPLEMENT_PURE_MATHS_AL.md`
  (sources : `GCE_AL_MATHS_MECHANICS_*` et `GCE_AL_MATHS_STATISTICS_*`, 24 PDF chacun, 2019-2026). Autres matières dont les PDF sont téléchargés mais
  qui n'ont pas encore de complément : Geology, English Language, Literature, Philosophy, Religious Studies, Special Bilingual (A/L).

- **Pure Mathematics with Mechanics / Statistics (0765 / 0770), 48 sujets 2019-2026 ingérés (2026-10-16)** : dossiers `gce-al-pm-<mechanics|statistics>-<annee>-p<1|2|3>-officiel-cameroun`. **La section Pure Maths de P1 (Q1-35) et une grande partie de P2 sont communes aux deux matières d'une même session** (sauf 2023) : deux agents qui lisent la même page divergent (coefficient, exposant, base de log, mot « sum and product/difference »). Après chaque vague, comparer les deux sujets (type, clé, options des questions au même numéro), trancher sur la PAGE imprimée (lire le PDF), recopier la bonne lecture dans l'autre fichier ; si le sujet est déjà ingéré, supprimer ses `Exercise` puis sa `Lesson` (`Exercise.lesson` est PROTECT) et réingérer. P1 = 50 QCM, section A Pure Maths Q1-35 puis section B (Mechanics ou Statistics) Q36-50 ; P2 = 10 questions « answer ALL » (3 h) surtout Pure Maths ; P3 = 8 questions de 13 points, 100 % Mechanics (+ une de probabilités) ou 100 % Statistics. Un sujet partiel existe : Statistics 2021 P1 (questions 22-50 seulement, le validateur échoue exprès). Le validateur refuse maintenant `\tag` sur une seule ligne et un libellé/code de matière incohérent.

- **Règles de choix, quatre formes (2026-10-18)** : `parmi` (n sur m d'un groupe), `ou` (jeux de sous-questions), **`section_unique`** (`{"type":"section_unique","portee":"PAPER 3","repondre":4}` : n questions, TOUTES dans une seule section ; la simulation ne compte alors que la meilleure section, voir `simulations/choix.py`) et **`consigne`** (`{"type":"consigne","portee":"SECTION I","texte":"..."}` : texte libre dans la langue du sujet, sans effet sur la note). Sans règle `section_unique`, le barème d'un sujet comme Religious Studies Paper 3 additionnerait ses 36 questions. Les règles sont exposées par `/access/read/` et `/access/preview/` (`regles_choix`) et affichées au-dessus du sommaire (`components/inedit/ReglesChoix.tsx`, sans `traites` = sujet lu en ligne, avec = simulation).
  **Limite connue** : « n questions au total, au moins une par section » (History, Geography, Economics, Philosophy, English...) reste codé par un `parmi 1` PAR section : la simulation ne compte alors que la meilleure question de chaque section, donc un élève qui traite deux questions d'une même section en perd une. À traiter par une cinquième forme (`total` + minimum par groupe).
- **Sommaire des longues épreuves (2026-10-18)** : au-delà de 6 exercices (`MIN_EXERCICES_SECTIONS`), tous groupés en au moins 2 sections, la fiche présente des sections repliables et la lecture une barre à deux rangées (`sectionsDEpreuve`, `components/EpreuveSommaire.tsx`). **Convention de transcription** : dans un sujet à sections, `enonce_intro_markdown` de chaque exercice porte le titre de SA SECTION (identique pour toute la section) ; l'intitulé de section de l'écran est le titre majoritaire, et un titre propre à l'exercice (« Exercice 1 : Chimie organique ») reste son libellé.

## 5. Ce qui manque encore (au 2026-10-14)

- Syllabus officiels du GCE Board (matière première du futur référentiel `programme` GCE, donc de `savoir_officiel`).
- Échelle de notes A-E (les seuils du Board ne figurent pas sur les sujets), `regles_choix` consommées par la simulation.
- Reste de l'A Level (Maths, Mécanique, Statistiques, Further Maths, Informatique, Économie...), branche Technical, sujets O Level 2024-2026 et « mocks » : téléchargés, non ingérés. Quiz et cours A Level : 100 thèmes faits sur 439 (les 25 plus fréquents de chaque matière) ; plan A Level créé et activé en local.
