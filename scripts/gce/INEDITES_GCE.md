# Épreuves inédites GCE : règles de conception pour tous les types de papers

Guide canonique du « Mode GCE » du skill `concepteur-epreuve-inedite` (le skill y renvoie, comme `correction-experte` renvoie à
`scripts/gce/README.md`). Il est né de l'étalonnage du 2026-10-19 : conception de **Mathematics GCE O Level Paper 1, épreuve inédite n°1**
(50 QCM, `ep-cm-gce-ol-maths-p1-1-2026-s1`), calibrée sur les 8 vrais Paper 1 de 2019 à 2026, puis relevé des 18 047 questions de papers réels
(2 895 fichiers, 2019-2026) déjà ingérés pour en tirer le profil de CHAQUE type de paper. Tout chiffre ci-dessous est mesuré sur ce corpus (`backend/ingest/cm/gce-*`), pas
supposé. Ce qui est une décision à prendre, ou un défaut de plateforme, est marqué **DÉCISION** ou **DÉFAUT**.

Le skill actuel a été écrit pour le système francophone (BEPC, Probatoire, BAC, séries, exercices numérotés, points sur 20). Le GCE n'est pas un
« BAC en anglais » (voir `scripts/gce/README.md` §1) : le contrat JSON reste celui du skill, mais le plan d'une épreuve, son barème, son
vocabulaire et ses contrôles changent.

## 1. Le contrat JSON, version GCE

| Champ | Valeur GCE | Pourquoi |
|---|---|---|
| `matiere` | libellé anglais : `Mathematics`, `Physics`, `Chemistry`, `Biology`, `English Language`... (`MATIERE_MAP` de `catalog/ingestion.py`) | résolu en `GCE_*` |
| `cursus` | `[{"examen":"gce_ol","serie":""}]` (ou `gce_al`) ; `"Technical"` seulement pour la branche technique | jamais `gce` seul, jamais de série A/C/D |
| `savoirs_officiels` / `savoir_officiel` | **omis** | le référentiel `programme` n'existe pas pour le GCE |
| `external_id` | `bp-cm-gce-<ol\|al>-<matiere>-p<paper>-<n>` et `ep-<id du bp>-<annee>-s<k>` | le numéro de paper entre dans l'id : le modèle n'a pas de champ `numero_paper` (DÉFAUT 4) |
| `titre` | `<Subject> GCE <O Level\|A Level> Paper <p> – Original Paper No. <N>` | « Original Paper » est le mot de l'interface anglaise (`ep.seo_inedites`) ; « GCE O Level » rend `public_dans_titre` vrai, l'en-tête du PDF ne répète donc pas le public ; le `n°` français devient `No.` |
| Langue du contenu | anglais clair, niveau Form 5 (O/L) ou Upper Sixth (A/L), contextes camerounais (FCFA, Buea, Bamenda, Douala...), SI, `g = 10 m s^-2`, **point décimal**, milliers par `\,` | `Subject.langue = en` : la plateforme choisit alors le PDF et l'interface anglais |
| Repères de structure | restent **en français** dans le JSON : `### Rappel de méthode`, `### Piège à éviter`, `### Conseil` | le frontend (`lib/markdown.ts`) les détecte par ce titre exact, `catalog/pdf_textes.py` les traduit à l'affichage (`Method reminder`, `Common pitfall`, `Tip`). Les titres `### Method reminder` ne sont détectés que dans les quiz et cours |
| `duree_minutes` / `bareme_total` | durée **réelle** du paper (90, 120, 150, 180) et total de points du paper | seuls porteurs de la durée : le chrono lit `Blueprint.duree_minutes` |
| `competences` / `themes` | noms de `Tag` **existants**, en minuscules, vocabulaire du lot (`scripts/gce/consignes/CONSIGNES.md`) | `Tag.name` est unique et partagé avec le contenu français (collisions : README §4) |
| `rappels_de_methode[].competence` | le **titre exact du `Cours` existant** du thème (ex. `Vectors: column vectors, magnitude and direction`) | l'égalité de chaîne est ce qui relie le rappel à un cours déjà publié sans le regénérer ; fichier `scripts/gce/inedites/cours_titres_gce_maths_ol.json` pour les Maths O/L |
| Corrigé d'une QCM | `### Rappel de méthode` (règle générale, un paragraphe) + résolution + `**Answer: C.**` + `### Piège à éviter` + `### Conseil` si pertinents | même gabarit que `correction-experte` en Mode GCE ; la lettre est recalculée par le générateur, jamais tapée |
| Tirets | ni cadratin ni demi-cadratin dans le contenu ; `–` seulement dans le `titre` | règle du skill et de `CONSIGNES.md` |

## 2. Ce que la plateforme sait représenter aujourd'hui, et ce qu'elle ne sait pas

Représentable : un exercice unique de 50 QCM ; plusieurs exercices avec `groupes` (`SECTION A`, `SECTION B`) ; barème exact par question et grille
`criteres_notation` ; figures SVG intégrées au Markdown ; durée du paper (`Blueprint.duree_minutes`) ; PDF du sujet en anglais.

Non représentable (relevé le 2026-10-19 dans `inedit/models.py`, `inedit/ingestion.py`, `inedit/views.py`) :

- **DÉFAUT 1 (corrigé le 2026-10-19, non committé) : les options des QCM étaient absentes du PDF du sujet et du texte compilé.**
  `EpreuveInedite.compile_from_exercices` n'écrivait que `question.enonce_markdown` ; le lecteur à l'écran affichait `choix`, pas le PDF
  (constaté sur le Paper 1 étalon : 7 pages, 50 énoncés, aucune option). Correctif : pour une question `QCM` portant `choix`, une option par ligne
  (`a) texte`) est ajoutée après l'énoncé dans `enonce_markdown` et `corrige_markdown` compilés, comme le fait
  `catalog.rendering._render_question_enonce` ; test `CompileFromExercicesTests.test_qcm_options_are_rebuilt_from_choix_in_both_documents`.
  **Même défaut dans l'aperçu public de la fiche** (constaté le 2026-10-19 sur les trois Paper 1 publiés : la question 1 s'affichait sans ses options a) à d)) : `catalog.inedit_bridge._apercu_enonce` passe maintenant
  par `QuestionInedite.enonce_avec_options()`, la même méthode que la compilation ; test dédié ; vérifié dans le navigateur. L'aperçu d'un Paper 2 montre l'intro de l'exercice 1 et sa première sous-question seulement.
  Les 19 épreuves inédites à QCM (64 questions) de la base locale ont été recompilées et leurs PDF régénérés. En production : reconstruire l'image
  `backend`, puis recompiler et régénérer de même. Ne jamais recopier les options dans `enonce_markdown` (affichées deux fois à l'écran).
- **DÉFAUT 2 : `score_originalite` ne mesure pas l'originalité d'un QCM de syllabus.** C'est le `1 - max(difflib ratio)` entre un énoncé et 500
  questions du corpus : les énoncés courts et gabarités (« Given that ..., the value of ... is ») atteignent 0,85 contre n'importe quel énoncé réel
  voisin. Le Paper 1 étalon sort à **13** alors que `controle_inedite_gce.py` (comparaison énoncé + options + nombres contre 810 questions réelles de
  Maths O/L) ne trouve aucun doublon. Le score reste informatif ; ne jamais exiger « > 80 » pour un QCM.
- **DÉFAUT 3 : le titre d'exercice du PDF reste en français** (« Exercice 1 (50 marks) ») : `adapter_markdown` traduit `**Exercice` en gras, pas
  `### Exercice`. Pour une épreuve à exercice unique, l'en-tête n'apporte rien.
- **DÉFAUT 4 : ni `numero_paper`, ni `code_matiere`, ni `regles_choix` dans le modèle inédit.** Les règles de choix (`parmi`, `ou`, `total`,
  `section_unique`) n'existent que pour les épreuves classiques (`catalog/choix.py`, `simulations/choix.py`). Conséquence de conception au §4.
- **DÉFAUT 5 (corrigé le 2026-10-19, non committé) : les exercices étaient triés par `numero_exercice` en texte** : « 10 » passait avant « 2 ». Sans effet pour un
  Paper 1 (un seul exercice) ; pour un Paper 2 de 14 exercices, le lecteur, la copie et le PDF mélangeaient l'ordre. Correctif : `EpreuveInedite.exercices_ordonnes()`
  (clé `cle_numero_exercice` : « 2 » avant « 10 », les numéros purs avant « B1 ») utilisée par la compilation, le lecteur et la notation (`inedit/models.py`,
  `inedit/views.py`) et par l'aperçu de la fiche (`catalog/inedit_bridge.py`) ; deux tests. Les numéros à deux chiffres du Paper 2 étalon (`01` à `10`) n'étaient
  qu'un contournement : ils restent valides, mais un nouveau paper peut numéroter `1` à `10`. En production : reconstruire l'image `backend`.
- **DÉFAUT 6 (corrigé le 2026-10-19, non committé) : le PDF et le texte compilé n'imprimaient pas les points de chaque sous-question.** Seul l'en-tête d'exercice portait le total
  (« Exercice 3 (10 marks) ») alors que les vrais sujets impriment « [3 marks] » après chaque partie ; le champ `points` n'était affiché qu'au lecteur à l'écran. Correctif :
  `QuestionInedite.mention_points()` (`*[n pts]*`, vide pour une QCM et sans barème) est ajouté à la fin de l'énoncé de chaque question rédigée par `compile_from_exercices`, dans l'énoncé
  ET le corrigé compilés (jamais dans `enonce_markdown`, que le lecteur affiche avec `points`) ; `adapter_markdown` le traduit en `*[3 marks]*` pour le PDF anglais. Deux tests ; 149 épreuves
  à parties recompilées et leurs PDF régénérés en base locale (français compris : « [1.25 pts] »). En production : reconstruire l'image `backend`, puis recompiler et régénérer de même.
  La phrase « the approximate mark for each part of a question is indicated » des Paper 2 de Maths, Biology et Physics est donc VRAIE ; le Chemistry P2 ne la porte pas (retirée avant le
  correctif), sans conséquence.
- **DÉFAUT 7 (corrigé le 2026-10-20, committé avec l'étalon Additional Maths) : une inégalité « $-3<k<3$ » cassait le PDF du sujet.** `catalog.sujet_pdf._restore_math` remettait les formules dans le HTML
  sans les échapper : `<k` était lu comme une balise et avalait les options suivantes (Paper 1 Add. Maths, question 5 : « b) $-3 c) $-6 d) »). Seule une lettre APRÈS le signe `<` déclenche le défaut
  (« x<3 » passait). Correctif : `html.escape(span, quote=False)` à la restauration (`catalog/sujet_pdf.py`, utilisé aussi par `inedit/sujet_pdf.py`, `fiches/pdf.py` et `quiz/pdf.py`) ; test
  `catalog/test_sujet_pdf_math_html.py`. Balayage de la base locale : **54 leçons et 5 épreuves inédites** (dont le Maths P1 étalon, id 162) avaient un PDF touché ; tous régénérés. En production :
  reconstruire `backend`, puis régénérer les PDF dont le Markdown contient `$...<[A-Za-z]...$` (même balayage), et vérifier les PDF des fiches et des quiz.
- Pas d'image PNG : figures SVG calculées seulement (`figures_svg.py`). Cartes, schémas anatomiques ou de verrerie, microphotographies restent
  hors de portée.
- Le barème est **exact** : la somme des `points` des questions d'un exercice vaut `exercices[].points`. Les sujets réels, eux, ne somment pas
  toujours (Maths P2 : 103 à 144 selon l'année, parce que la transcription ne corrige jamais le sujet imprimé). Une inédite, elle, se
  construit avec un total propre.

## 3. Étalon : Paper 1 de Mathematics O Level (0570)

Mesuré sur 2019-2026 (8 papers, 400 questions). C'est le patron de TOUT Paper 1 QCM ; les écarts par matière sont au §5.

| Mesure | Réel | Étalon inédit n°1 |
|---|---|---|
| Structure | 1 exercice, 50 QCM, `points` vide (« all questions carry equal marks ») | 1 exercice `"1"`, 50 QCM, 1 point chacune, `points "50"` |
| Durée | 1h30, calculatrice non programmable | `duree_minutes 90`, `bareme_total 50`, mêmes consignes dans `enonce_intro_markdown` |
| Options | 4 (`a` à `d`), 391 questions sur 400 ; clés a 106 / b 99 / c 98 / d 88 | 4 options, clés a 13 / b 13 / c 12 / d 12, jamais 3 de suite |
| Ordre | **ordre du syllabus**, identique d'une année à l'autre : nombres et rapports (1-10), ensembles et logique (11-14), fonctions (15-18), angles, mensuration, cercle (19-30), géométrie analytique et graphes (28-33), algèbre (31-41), réseaux, trigonométrie (38-45), vecteurs, matrices, transformations (42-48), statistiques puis probabilités (46-50) | même ordre, 11 blocs inscrits dans `sections_plan[0].repartition` |
| Poids des thèmes (moyenne par sujet) | mensuration 4,5 ; angles 3,8 ; expressions algébriques 3,3 ; statistiques 3,3 ; ensembles 3,1 ; vecteurs 3,1 ; fonctions 3 ; arithmétique 2,9 ; trigonométrie 2,4 ; matrices 2,4 ; probabilités 1,3 | mêmes ordres de grandeur, 36 thèmes sur 40 présents dans le corpus |
| Difficulté (estimée) | 61 % faible, 38 % moyenne, 0,25 % élevée | 26 faible (52 %), 22 moyenne (44 %), 2 élevée (4 %) |
| Énoncé | 85 caractères en moyenne ; 80-90 % se terminent par « is / are / gives » ; aucune question « ? » | même gabarit, une consigne par énoncé, contexte réel seulement pour les rapports et l'arithmétique commerciale |
| Options « all / none / both of the above » | 0 à 2 % en Maths (jusqu'à 9 % en Biologie) | aucune |
| Figures | 14, 12, 5, 10, 9, 11, 3, 2 par sujet (tendance récente : 2-3) ; 10-30 % des questions | 12 figures SVG calculées, numérotées « Figure 1 » à « Figure 12 » dans l'ordre des questions |

Méthode de fabrication retenue (à reprendre pour tout QCM) : un **générateur** (`generer_maths_p1.py`) et non du JSON tapé à la main.

1. Chaque question est une entrée de données : thèmes, difficulté, énoncé, bonne option, trois distracteurs, rappel, résolution, piège, figure.
2. Les clés sont **placées par le générateur** (suite équilibrée et déterministe), la lettre de `**Answer: X.**` est recalculée. Une clé tapée à
   la main dérive vers « b » et « c » : mesuré sur les sujets réels (a 27 %, d 22 %).
3. Les distracteurs sont des **erreurs types nommées**, jamais des valeurs absurdes : l'ordre des opérations de gauche à droite, le signe oublié,
   le dénominateur pris sur la mauvaise base, la formule d'une autre grandeur, le volume au lieu de l'aire. Le bloc `### Piège à éviter` du corrigé
   dit lequel mène à quelle option : c'est ce qui rend le corrigé utile à qui a répondu faux.
4. **Recalcul indépendant** (`verifier_reponses_maths_p1.py`) : la valeur attendue est recalculée depuis les données de l'énoncé, les quatre options
   sont lues (nombre, ensemble, point, vecteur, matrice, expression évaluée en plusieurs points) et la clé doit être la **seule** égale. Testé par
   mutation (clé faussée, bonne réponse dupliquée) : les deux sont détectées. Les corrigés ne servent jamais de source du calcul.
5. Les figures sortent d'un script à partir des constantes de l'énoncé (118°, 8-15-17, cap 072°) ; contrôle `verifier_figures.py` puis rendu PNG
   **regardé**.

Contrôles de fin (ordre) : `generer_maths_p1.py` ; `verifier_reponses_maths_p1.py` (0 écart) ; `controle_inedite_gce.py` (0 erreur) ;
`verifier_figures.py` (0 erreur) + rendu des figures ; rendu KaTeX par le vrai moteur (`audit-rendu.test.ts` sur un dump des champs) ;
**ingestion à blanc** dans une transaction annulée (blueprint passé VALIDE à l'intérieur de la transaction seulement) ; PDF du sujet
regardé page par page.

## 4. Règles communes à tous les papers

**Blueprint d'abord, validé par un humain.** Règle inchangée du skill. Le blueprint GCE porte, dans `sections_plan`, ce que le modèle ne sait
pas porter ailleurs : `format`, `ordre`, `repartition` (blocs et nombre de questions), `repartition_difficulte`, `figures_prevues`, et pour un paper à
choix la règle réelle en clair. Un blueprint sans ce plan chiffré est incomplet.

**Fidélité au vrai paper : la STRUCTURE se copie, le CONTENU ne se copie jamais.** On reproduit le nombre de questions, l'ordre du syllabus, le
format des options, la répartition de difficulté, la densité de figures, la durée, les consignes. On ne reprend aucune donnée, aucun contexte, aucun
nom, aucune figure, aucun jeu d'options d'un sujet réel. Le gabarit de question de syllabus (« The median of ... is ») revient forcément : le test
est « les mêmes données ou le même contexte ? », pas « le même début de phrase ? ». Contrôle outillé `controle_inedite_gce.py` (il refuse aussi tout caractère de contrôle dans le contenu : un `
ightarrow` écrit dans une chaîne Python non brute devient « ightarrow » à l'écran et passe le rendu KaTeX sans erreur) :
énoncé + options + nombres contre toutes les questions réelles de la matière, ERREUR si texte ≥ 0,82 et nombres communs ≥ 0,5 ou si 3 options non
triviales sont identiques ; AVERTISSEMENT dès 0,66. Les avertissements se relisent à la main (Étalon : deux, des gabarits de matrices avec d'autres
valeurs).

**Corrigés justes, recalculés.** Il n'existe aucun corrigé officiel : la justesse est entièrement la nôtre. Matière calculatoire : recalcul par
script (Python, `fractions`, `math`), jamais « ça a l'air juste ». Matière factuelle : chaque fait (date, auteur, valeur) vérifié, `incertitudes` dit
le reste. Code (Pascal, C) sans compilateur sur la machine : logique vérifiée par traduction Python, et le dire.

**Pas de choix offert tant que la plateforme ne le note pas (DÉCISION, à confirmer).** Les papers réels à choix (« answer any 5 of 8 ») sont
représentés dans le catalogue par `regles_choix`, absentes des inédites (DÉFAUT 4). Règle provisoire : l'inédite contient **exactement les
questions que le candidat doit traiter** (version « answer ALL »), la règle réelle est rappelée dans `enonce_intro_markdown`, et le blueprint la
consigne. Alternative non retenue : offrir les m questions, ce qui fausserait barème et rapport de fin. Chantier de plateforme : reprendre
`catalog/choix.py` dans `inedit`.

**Session de papers (décidé le 2026-10-19).** Les papers d'une même matière et d'un même niveau forment une **session** : le Paper 1 et le Paper 2
« Original Paper No. 1 » se conçoivent ensemble, se valident ensemble, se publient ensemble. Concrètement : (1) le blueprint de chaque paper porte un bloc
`session` : `papier_jumeau`, `numero_session`, `themes_communs_aux_deux_papers`, `themes_propres_au_paper_N` et la règle « aucune donnée, aucun contexte, aucune
figure partagés » ; (2) le numéro `No. N` est le même pour tous les papers de la session ; (3) `controle_inedite_gce.py --jumeau <autre paper>` compare
chaque question à l'épreuve jumelle en plus du corpus réel ; (4) les papers de la session passent au statut Validé en même temps. Ce qui n'est PAS groupé :
la génération (un paper après l'autre, chacun avec ses quatre contrôles) et le calibrage (un type de paper n'est généré en série qu'une fois son étalon fait). La
session reste une convention tant que le modèle n'a pas de champ de regroupement ni de note globale.

**Statut.** Brouillon à l'ingestion, toujours ; blueprint validé par un humain dans l'admin ; l'épreuve est publiée par un geste humain.

**Après l'ingestion.** `bash scripts/tunnel_validation.sh <since>` (périmètre inédit : voir limites dans le skill), `manage.py indexer_recherche`,
génération des cours manquants (un par `### Rappel de méthode` dont la compétence n'a pas de `Cours`, `type: "cours"`, `meta.serie` = `"GCE O/L"`
ou `"GCE A/L"`, `meta.tags` = le thème seul).

## 5. Profil et règles par type de paper

Profil mesuré (2019-2026, `n` = nombre de sujets ingérés, `q` = questions, durée imprimée). **Toutes les matières ont un Paper 1 de 50 QCM de
1h30** ; ce qui varie est le reste.

| Type | Papers concernés | Structure réelle | Règle de choix réelle |
|---|---|---|---|
| **A. QCM** | P1 de toutes les matières O/L et A/L | 1 exercice, 50 questions, 4 options, 1h30 (Religious Studies A/L : 40-50) | aucune |
| **B. Structuré, tout obligatoire** | Maths O/L P2 ; Further Maths A/L P2 et P3 ; Pure Maths with Mechanics / Statistics A/L P2 et P3 | Maths O/L P2 : A 10 questions courtes (4-5 points, 43-45 au total) + B 4 questions de 15 points, 2h30 | aucune (« Answer ALL ») |
| **C. Structuré, avec choix** | Biology, Chemistry, Human Biology, Citizenship, Commerce, Economics, Food and Nutrition, Geography, History, Computer Science, Physics (`ou`), Additional Mathematics (`section_unique`) O/L P2 ; Biology, Geology, ICT, Computer Science A/L P2 | 5 à 14 questions à sous-parties `a, b, c`, souvent 2 à 4 sections | `parmi` (n sur m), `ou`, `total`, `section_unique` |
| **D. Essai / dissertation** | History, Religious Studies, Philosophy, Geography, Economics A/L P2-P3 ; History et Geography O/L sections B-C ; Literature (aucun paper ingéré à ce jour) | 4 à 12 sujets de 15 à 25 points, un par section | `total` (« au moins une par section »), `section_unique`, `parmi 1 sur n` |
| **E. Langue** | English Language et French O/L P2 (modèle de composition : environ 630 mots en English O/L) ; English A/L P2-P3 ; SBE French | 3 à 9 questions de 30 à 80 points : compréhension, résumé, rédaction | `parmi` |
| **F. Pratique / applications** | Computer Science O/L et A/L P3 ; ICT A/L P3 ; Geography A/L P3 (carte) | 2 à 12 tâches ; données du jour absentes du PDF | `parmi`, parfois `ou` |
| **G. Quantitatif multi-parties** | Economics A/L P3 ; Mechanics et Statistics A/L P3 (8 questions de 13 points) ; Physics A/L P2 | 5 à 8 questions de 13 à 25 points, tableaux et calculs | `parmi` ou aucune |

### A. Paper 1 QCM (toutes matières)

- 1 exercice `"1"`, 50 questions numérotées `"1"` à `"50"`, `type_reponse: "qcm"`, `points` 1, exercice `points "50"`, `groupes: []`,
  `duree_minutes: 90`. Consignes du vrai sujet dans `enonce_intro_markdown`.
- 4 options `a`-`d`, `reponse_correcte` en minuscule, jamais `criteres_notation`.
- Ordre du syllabus, bloc par bloc (§3). Les 4 à 5 premières questions sont les plus simples de leur thème ; la difficulté monte à l'intérieur d'un
  bloc, pas sur le paper entier.
- Difficulté : 45 à 70 % faibles, 1 à 4 élevées ; le contrôle avertit hors de ces bornes.
- Options homogènes (même nature, même format, même précision), jamais « all/none of the above » en Maths, Add. Maths, Physics, Chemistry, Computer
  Science, Economics, Commerce ; toléré à moins de 10 % en Biologie, Human Biology, Citizenship, Geography.
- Par matière (mesuré) : **Maths** 80-90 % d'énoncés en « is », 10-30 % de figures ; **Physics** 15-40 % de figures et 25-40 % de questions en « ? » ;
  **Biology / Human Biology** 8-18 % de figures (schémas : hors de portée, voir §6), questions en « ? » 17-51 % ; **History / Citizenship / Commerce /
  Food** aucune figure, faits exacts, jamais de date ou de nom non vérifié ; **English / French** aucun calcul, un énoncé ne contient jamais deux
  réponses admissibles, textes originaux (jamais un extrait publié).
- **A Level** : la première question d'un Paper 1 mélange les formats (meilleure réponse, affirmations numérotées `1, 2, 3` avec « 1 and 2 only »,
  assertion et raison). Un format par bloc de questions, annoncé dans `groupes` seulement si le vrai sujet le fait ; options de combinaison
  rédigées en toutes lettres (`a) 1 and 2 only`).
- **O Level Chemistry** : 0 à 6 questions par sujet en « completion multiple » (réponses 1 à 4) et « assertion-raison », en blocs consécutifs, consigne imprimée répétée dans chaque
  question, options à **ordre imposé** (voir l'étalon Chemistry au §5C) ; le contrôle d'originalité retire la consigne imprimée avant de comparer.
- Une question à figure dont la clé dépend de la lecture d'un détail fin est interdite : la clé doit se retrouver par calcul sur les données
  écrites en texte (`desc` du SVG comprise).

### B. Structuré, tout obligatoire (Maths O/L P2 comme étalon)

- Format récent (2023, 2025, 2026) : exercices `"1"` à `"10"` en `SECTION A` (une à trois sous-questions, 4 à 5 points chacune), exercices
  `"B1"` à `"B4"` en `SECTION B` (15 points chacun, 5 à 8 sous-questions). Total de **105** (A 45, B 60), comme
  les sujets complets de 2023 et 2025 (A 45) et celui de 2026 (A 43) : on reprend la somme du dernier sujet, on ne la « nettoie » pas à 100. Les sujets de 2019-2022
  avaient 15 questions en A : ne pas les imiter.
- Sous-question = une `question` de `numero` `a`, `b`, `c`... ; `points` et `criteres_notation` obligatoires : critères observables sur la copie
  (« Writes the formula », « Substitutes correctly », « Answer with unit »), somme exacte, 2 à 5 critères.
- Les consignes du vrai sujet y figurent : « show all steps », « 2 decimal places », « leave your answer in surd form », « give reasons ».
- Mélange attendu en Section B : un problème de **graphe à tracer** (tableau de valeurs, courbe SVG dans le corrigé seulement), un problème de
  **statistiques** (tableau de fréquences, moyenne, médiane, histogramme ou diagramme), une **construction ou transformation**, un problème
  **vecteurs/matrices**. Poids mesurés dans P2 : statistics 3-6 par sujet, graphs 3-6, set theory 3-5, graph theory 2-4, matrix 2-5, probability 1-4.
- **Étalon produit le 2026-10-19** : `ep-cm-gce-ol-maths-p2-1-2026-s1` (`generer_maths_p2.py`, `questions_maths_p2_a.py`, `questions_maths_p2_b.py`,
  `figs_maths_p2.py`). 14 exercices, 62 sous-questions, 105 points, 150 minutes, difficulté 37 faibles / 23 moyennes / 2 élevées (60 / 37 / 3 %, corpus réel
  2023-2026 : 50-62 % de faibles), 5 figures dont **une seule dans un énoncé** (le réseau de la question 6) : le tracé attendu (droite numérique, Venn, construction,
  parabole) ne vit que dans le corrigé. Section A : fractions, indices, changement de sujet, ensembles, matrices, réseau, vecteurs, système, inéquation, probabilités.
  Section B : arithmétique commerciale, statistiques groupées et ensembles, fonctions, suite géométrique et construction, courbe et équation du second degré.
  19 thèmes communs avec le Paper 1, 1 propre au Paper 2 (`geometric construction`) : les thèmes se recoupent par nature, jamais les données ni les contextes.
- Barème : chaque sous-question a ses `points` et une grille `criteres_notation` de 1 à 4 critères observables (« You write `$x(x+3)=40$` and expand »), somme exacte.
  Un tracé ou une construction est noté sur la copie papier : critères « axes gradués avec l'échelle demandée », « points placés avec précision », « courbe lisse ».
  Une mesure lue sur un dessin admet une tolérance écrite dans le critère et dans le corrigé (« toute valeur de 5,0 à 5,2 cm »).
- Un paper rédigé est vérifié sous-question par sous-question : `verifier_reponses_maths_p2.py` relit la ligne `**Answer: ...**` de chacune des 62 sous-questions,
  recalcule la valeur par une autre méthode (force brute, évaluation numérique de formules, comptage) et contrôle les valeurs intermédiaires citées (tableaux
  de calcul, chiffres des étapes). Contrôle de structure : `controle_inedite_gce.py --type redige --sections "SECTION A:10:45,SECTION B:4:60" --jumeau <P1>`.
- Le corrigé est le **corrigé d'un candidat qui prend tous les points** : étapes, formules, valeurs, conclusion, `**Answer: ...**` en gras.
- Figures : celles du `Tracé attendu` vont au corrigé uniquement (le skill) ; les figures de données d'énoncé sont SVG calculés.

### C. Structuré avec choix (Biology, Chemistry, History, Geography, Economics, Commerce, Food, Human Biology, Citizenship, Computer Science)

- Reproduire la **forme** : sections (`groupes`), nombre de sous-parties, points par sous-partie imprimés (Chemistry O/L P2 : 5 questions de 10 en A,
  2 de 20 en B, 3 de 20 en C ; Biology O/L P2 : A 3 × 20, B 4 × 20 ; Human Biology : A 5 × 20, B 4 × 20).
- **La règle de choix du vrai sujet ne se code pas** (DÉFAUT 4) : version « answer ALL » limitée aux questions à traiter (§4), règle réelle en clair
  dans le blueprint et dans l'intro. Exemple : History O/L (« 2 en A, 1 en B, 1 en C ») donne 4 questions, pas 17.
- Matières factuelles : corrigé = **réponse modèle complète** d'un candidat qui obtient tous les points ; chaque point de barème correspond à un fait
  ou à une idée distincte du corrigé ; dates, auteurs, lieux et chiffres vérifiés avant d'écrire (pas de recalcul possible, aucune approximation).
- Matières scientifiques : un support (tableau, courbe, texte expérimental) par question de données ; les données restent aussi écrites en texte ou
  tableau ; schémas anatomiques ou de verrerie : jamais (le dire dans le compte rendu).
- Sujets camerounais : contextes locaux réels (cultures, climat, institutions) ; aucune donnée statistique inventée présentée comme réelle (en Geography
  et Economics, étiqueter « Source: adapted data » seulement si les chiffres sont réellement des données publiées, sinon les présenter comme
  un cas d'étude fictif).

- **Étalon produit le 2026-10-19 : session Biology O Level n°1** (`ep-cm-gce-ol-biology-p1-1-2026-s1` et `ep-cm-gce-ol-biology-p2-1-2026-s1`, générateurs
  `generer_biology_p1.py` et `generer_biology_p2.py`, questions dans `questions_biology_p1.py` et `questions_biology_p2.py`, figures `figs_biology_p1.py` et
  `figs_biology_p2.py`, vérificateurs `verifier_reponses_biology_p1.py` et `_p2.py`). Mesuré sur 14 vrais papers de Biology 2019-2026 :
  - **Paper 1** : 50 QCM, ordre **mélangé** (aucun bloc par chapitre, contrairement aux Maths), 57 % de questions faibles, 41 % moyennes, 1 % élevées, clés a 26 % / b 23 % /
    c 25 % / d 25 %, 4 à 8 figures par sujet (schémas de cellules, d'organes, de cycles), énoncés en « ? » 16 à 38 %, « all / none of the above » sous 10 %. Inédite : 50 QCM,
    62 % faibles / 36 % moyennes / 2 % élevée, 40 thèmes, 5 figures de **données** (activité d'une enzyme selon la température, photosynthèse selon la lumière, transpiration au
    cours de la journée, rythme cardiaque après l'effort, réseau trophique) à la place des schémas anatomiques. 10 questions sur 50 se recalculent (grandeurs, lecture de données,
    croisements, comptage de chaînes alimentaires) ; les 40 autres sont du rappel de cours relu à la main : une clé fausse n'y est détectable que par relecture, d'où la règle
    « un seul fait par question, une seule option défendable ».
  - **Paper 2** : 7 questions de 20 points, chacune en trois parties `a`, `b`, `c` à points imprimés (5-9), « ALL THREE of Section A and any TWO of Section B », 2 h 30. Types de
    parties : définitions, « describe/explain », conception d'expérience, comparaison en tableau, **dessin annoté** (un par sujet). Inédite : **5 questions** (3 en Section A, 2 en
    Section B, version « answer ALL »), 100 points, 15 sous-questions, grilles de 3 à 6 critères, tableau de résultats pour 2 questions, un seul tracé (le réseau trophique, dans le
    corrigé). Le **dessin** demandé (coupe de l'œil) n'est pas produit : le corrigé décrit ce qui doit figurer, partie par partie, comme le font les corrigés réels ingérés, et la
    grille note le dessin sur la copie (« grand, titré, étiquettes à la règle »).
  - Vocabulaire de thèmes : 210 `Tag` O Level en base, très fragmentés (« transpiration » et « transpiration in plants », « food chains » et « food webs »...). Toujours reprendre la
    **forme la plus fréquente** de la notion ; 25 seulement ont un `Cours` O Level, les autres rappels portent une compétence sans cours (à générer ensuite).
  - **Pas de fuite d'un paper vers l'autre** : un énoncé ou une option du Paper 1 ne doit pas donner la réponse d'une question du Paper 2 de la même session (ex. « la lentille devient
    plus épaisse » en QCM alors que le Paper 2 demande d'expliquer l'accommodation). Les 7 questions du Paper 1 qui recoupaient le Paper 2 ont été remplacées.

- **Étalon produit le 2026-10-19 : session Physics O Level n°1** (`ep-cm-gce-ol-physics-p1-1-2026-s1` et `-p2-1-2026-s1`, générateurs `generer_physics_p1.py` et `_p2.py`, questions
  `questions_physics_p1.py` et `_p2.py`, figures `figs_physics_p1.py` et `_p2.py`, vérificateurs `verifier_reponses_physics_p1.py` et `_p2.py`). Mesuré sur 14 vrais papers 2019-2026 :
  - **Paper 1** : 50 QCM, ordre mélangé par grappes de 1 à 3 questions d'un même chapitre, 66 % de questions faibles / 33 % moyennes / 1 % élevées, clés a 23 % / b 24 % /
    c 25 % / d 25 %, 6 à 11 figures (schémas d'appareils, circuits, graphiques à choisir parmi A à D), un tiers des questions chiffrées. Inédite : 29 faibles / 20 moyennes / 1 élevée,
    6 figures calculées (vitesse-temps, règle en équilibre, courbe de chauffe, réflexion, circuit, quatre graphiques en options), **36 questions sur 50 recalculées** (la clé d'une
    question dont les options sont les panneaux A à D d'une figure est FIXÉE par la figure : le générateur place les autres clés autour).
  - **Paper 2** : Section I de 6 questions courtes (8, 7, 9, 5, 6, 5 = 40 points), Section II de 3 questions de 20 points avec « EITHER a, b and c OR d, e and f » ; 2 h 30. Inédite :
    même structure, **une seule branche par question de la Section II** (version « answer ALL »), 46 sous-questions, 21 réponses chiffrées recalculées sur les constantes des figures
    (circuit, ressort), graphique de Hooke tracé dans le corrigé seulement (points, droite des moindres carrés passant par l'origine, pente), tolérances de lecture écrites dans les
    critères (« toute valeur de 1,9 à 2,0 N/cm »).
  - Calcul : toute question chiffrée a une **erreur type par distracteur** (oubli du facteur ½, temps en minutes pris pour des secondes, distance aller-retour non divisée par deux,
    rapport inversé) ; `g = 10 m/s²` écrit dans l'énoncé quand il sert.
- **Étalon produit le 2026-10-19 : session Chemistry O Level n°1** (`ep-cm-gce-ol-chemistry-p1-1-2026-s1` et `-p2-1-2026-s1`, générateurs `generer_chemistry_p1.py` et `_p2.py`, questions
  `questions_chemistry_p1.py` et `_p2.py`, figures `figs_chemistry_p1.py` et `_p2.py`, vérificateurs `verifier_reponses_chemistry_p1.py` et `_p2.py`, cours en `cours_titres_gce_chemistry_ol.json`).
  Mesuré sur 6 vrais Paper 1 (2019-2022, 2024, 2025 ; ni 2023 ni 2026 n'existent) et 8 Paper 2 (2019-2026) :
  - **Paper 1** : 50 QCM, ordre mélangé par grappes de 1 à 3 questions d'un même chapitre, 60 % de questions faibles / 39 % moyennes / 1 % élevée, clés a 26 % / b 26 % / c 25 % / d 19 %
    (+ quelques questions sans clé dans la transcription), 0 à 5 figures, 4 à 8 questions chiffrées (moles, concentration, formule empirique, volumes de gaz). **Chaque sujet réel contient 0 à 6 questions
    de format spécial, aussi à l'O Level** : « completion multiple » (réponses numérotées 1 à 4, options FIXES « 1, 2 and 3 only / 1 and 3 only / 2 and 4 only / 4 only ») et « assertion-raison » (deux
    énoncés en tableau, quatre options fixes A à D) ; **la consigne imprimée est répétée dans l'énoncé de chaque question du bloc** (« Instructions (Questions 27-29) »). Inédite : 30 faibles / 19 moyennes / 1 élevée,
    un bloc de 3 « completion multiple » et un bloc de 2 « assertion-raison », 3 figures de données (courbe de solubilité, volume de gaz en fonction du temps, profil énergétique), **17 questions sur 50 recalculées**
    (le reste est du rappel de cours, relu à la main). Les options d'un bloc spécial sont à **ordre imposé** : la clé découle du contenu (`ordre=` dans `Q()`), le générateur place les 45 autres
    autour (12-13 par lettre, jamais 3 de suite) et vérifie que le bloc tombe bien aux numéros annoncés dans la consigne.
  - **Paper 2** : 10 exercices, Section A 5 × 10 (« answer ALL, the best 4 are graded »), Section B 2 × 20 obligatoires (une manipulation, souvent avec une figure ; une analyse qualitative en tableau
    « test / observation / inférence »), Section C 3 × 20 (« answer ONLY TWO »), 2 h 30. Inédite : **4 + 2 + 2 exercices = 120 points** (version « answer ALL », règle réelle rappelée en clair dans l'introduction et le
    blueprint), 33 sous-questions, 16 faibles / 15 moyennes / 2 élevées, 2 figures de données en énoncé (courbe de pH d'un titrage, deux courbes de volume de gaz), 10 sous-questions chiffrées recalculées. Le vérificateur
    contrôle aussi les **liens entre données et figure** : le saut de pH doit encadrer le titre moyen, la masse de marbre doit valoir le volume final divisé par le volume molaire, les deux courbes finissent au même volume.
  - **Fuites d'un paper vers l'autre, corrigées avant publication** (le rappel et le corrigé d'un QCM comptent autant que l'énoncé) : un QCM sur « les alcanes ne décolorent pas l'eau de brome » donnait le résultat de
    l'éthane demandé au Paper 2 ; un rappel du procédé de contact citait « 450 °C », la température du Haber demandée au Paper 2 ; le QCM sur le monoxyde de carbone donnait l'inférence d'une question de combustion ;
    un rappel définissait le polymère d'addition que le Paper 2 fait expliquer ; un QCM de vitesse de réaction donnait l'explication par les collisions ; l'énoncé du Paper 2 « les tests montrent que Q contient
    l'ion zinc » donnait la réponse de la sous-question voisine. **Relire les deux papers l'un contre l'autre, énoncé, rappel ET corrigé, avant de les ingérer.**
  - Données lues sur un graphe : toute valeur qu'une sous-question demande de lire est placée sur une graduation (20 s, 60 cm³), pour qu'aucune lecture à ±1 ne change la réponse.
  - **Contrôle d'originalité** : la consigne imprimée d'un bloc spécial (« Instructions (Questions ...) » et l'en-tête « First statement / Second statement ») est retirée par `corps()` avant la comparaison ; sans cela
    deux questions d'assertion-raison étaient refusées pour 3 options identiques, alors que ces options sont la forme imposée du sujet, pas son contenu.
- **Étalon produit le 2026-10-20 : session Additional Mathematics O Level n°1** (`ep-cm-gce-ol-addmaths-p1-1-2026-s1` et `-p2-1-2026-s1`, générateurs `generer_addmaths_p1.py` et `_p2.py`, questions
  `questions_addmaths_p1_a.py`, `_p1_b.py`, `_p2_a.py` (Section A) et `_p2_b.py` (Section B), figures `figs_addmaths_p1.py` et `_p2.py`, vérificateurs `verifier_reponses_addmaths_p1.py` et `_p2.py`,
  cours en `cours_titres_gce_add_maths_ol.json`). Mesuré sur 7 vrais Paper 1 (2019-2021, 2023-2026 ; pas de 2022) et 7 Paper 2 :
  - **Paper 1** : 50 QCM dans l'ORDRE DU SYLLABUS (indices, logarithmes, polynômes, suites, binôme, dénombrement, trigonométrie, géométrie analytique, inéquations, fonctions, matrices, groupes
    `binary operations`, vecteurs, dérivation, intégration), 57 % faibles / 40 % moyennes / 3 % élevées, clés a 24 % / b 28 % / c 24 % / d 22 %, 1 à 5 figures. Inédite : 28 / 20 / 2, 3 figures
    (triangle de la règle des sinus, droite coupant les axes, région définie par trois droites), **50 questions sur 50 recalculées** par une voie indépendante (force brute, dérivation
    numérique, parcours de grille pour la région, vérification des axiomes d'un sous-groupe, comparaison des fonctions en plusieurs points pour les expressions).
  - **Paper 2** : 14 exercices, Section A de 8 questions obligatoires (7 à 10 points, 62 à 68 au total : polynômes et racines, dénombrement et binôme, suites en contexte, groupe et matrice,
    inéquations et région, trigonométrie, vecteurs, calcul), Section B de 3 questions de Mécanique de 17 points, Section C de 3 questions de Statistiques et Probabilités de 17 points ;
    « Answer ALL of A and ANY TWO of EITHER B OR C, never a mixture », 2 h 30. Inédite : **A en entier + deux questions de Mécanique de B = 100 points** (version « answer ALL », règle réelle
    rappelée dans l'introduction), 39 sous-questions, 18 faibles / 20 moyennes / 1 élevée, 3 figures (machine d'Atwood en énoncé ; région et courbe trigonométrique dans le corrigé seulement),
    36 sous-questions recalculées. La Section C (Statistiques et Probabilités) n'est pas couverte : à faire dans une session n°2.
  - **Le gabarit de syllabus revient, les DONNÉES ne doivent jamais revenir.** Le contrôle a fait ressortir des questions de syllabus qui se répètent d'un sujet à l'autre (inverse d'une matrice 2×2, vecteur
    $\overrightarrow{AB}$, comités de 3 garçons et 2 filles) ; la lecture des plus proches énoncés réels a trouvé **quatre vraies collisions de données** : la matrice $\begin{pmatrix}2&1\\5&3\end{pmatrix}$ et son
    inverse (sujet 2021), le point $A(1,2)$, le comité de 6 garçons et 4 filles à 3 et 2 (même réponse 120), et la dérivée de $\dfrac{x^{2}}{x+1}$ (sujet 2023) ; la table d'une opération
    sur $\{1,2,3,4\}$ modulo 5 (sujet 2021) et le gabarit « Taking 2 cm to represent $\pi/6$ ... draw the graph ... estimate the maximum » (sujet 2025) ont été changés pour d'autres structures. **Comparer les
    données et la structure de chaque question de syllabus au plus proche énoncé réel, pas seulement ses mots.**
  - **Mise en page des parties** : la plateforme veut un `numero` UNIQUE par exercice et imprime le `groupe_local` (« (i) ») une fois au-dessus de ses parties : le générateur garde le numéro de travail du vrai
    sujet (`i-a`) et le convertit (`NUMEROS` dans `questions_addmaths_p2_a.py` : `a`, `b`, `c`... avec groupe local « (i) », « (ii) ») ; le préfixe « (i)(a) » est retiré de l'énoncé (sinon « i-a. (i)(a) ... » en double).
    Les fractions des options et des énoncés d'un QCM s'écrivent `\frac` (style texte), pas `\dfrac` : une fraction empilée déborde de la ligne d'une option dans le PDF.
- **Incident d'originalité (2026-10-19) : un contrôle aveugle laisse passer une question identique à une vraie.** Le premier contrôle comparait l'énoncé de l'inédite à l'énoncé de la
  vraie question **précédé de la consigne de l'exercice** (« Multiple choice questions ... ») : cette consigne diluait la ressemblance et un énoncé court identique mot pour mot
  (« Which of the following electromagnetic waves has the longest wavelength? ») passait. Le score plateforme (`score_originalite` à 0) l'a révélé après publication, et le contrôle
  corrigé a trouvé 3 questions de Biology et 2 de Physics déjà publiées qui reformulaient des questions réelles (mêmes faits, mêmes options). Règles désormais appliquées par
  `controle_inedite_gce.py` : (1) comparer l'énoncé avec ET sans la consigne ; (2) refuser tout énoncé de 40 caractères ou plus, sans nombres, à 0,90 ou plus d'un énoncé réel ;
  (3) un jeu de 3 options communes n'est une copie que si l'énoncé ressemble aussi à 0,60 ou plus ; (4) le plus proche énoncé réel est retenu à part, indépendamment du score
  combiné (les nombres communs masquaient l'identité). **Pour une matière de pur rappel de cours (Biology, Physics, Chemistry, History...), changer le FAIT demandé, jamais seulement les
  mots** : « où se fait l'échange gazeux ? » devient « pourquoi la paroi des alvéoles est-elle mince ? ».

### D. Essais (History, Religious Studies, Philosophy, Literature, Geography, Economics)

- Un sujet de dissertation inédit **n'est jamais l'intitulé d'un sujet réel reformulé** (règle du skill pour les matières argumentatives). Les
  citations d'auteurs, de textes sacrés et de faits sont exactes et attendues.
- Corrigé = **plan détaillé et essai modèle** : introduction, 3 à 5 parties, conclusion, avec les faits, dates, exemples et références
  qu'un correcteur cherche ; longueur calée sur les corrigés modèles déjà ingérés (médiane par question : History A/L P2 et P3 environ 740 mots, Economics A/L P2 450, History O/L P2 230 par sous-question, Philosophy A/L 220) : mesurer le corpus de la matière avant d'écrire, ne pas deviner.
- `criteres_notation` d'un essai : contenu et connaissances, exactitude des faits, structure et argumentation, exemples et illustrations, qualité de la
  langue. Points répartis selon le barème du vrai sujet (15-25 par essai) ; critère observable (« Defines the term in the introduction », « Gives at
  least three dated examples »).
- **History / Religious Studies / Literature** : périmètre du syllabus du Board seulement (Cameroon History Since 1800, Africa and World History ;
  Literature : œuvres inscrites au programme de l'année, jamais une œuvre hors liste). Faits relus par un historien avant mise en avant (README §4,
  History A/L).
- Philosophy : thèse, antithèse, synthèse ; auteurs cités avec œuvre exacte.

### E. Langues (English Language, French, SBE French, Literature)

- Textes de compréhension et textes à résumer : **originaux**, jamais un extrait publié (droit d'auteur) ; niveau de lecture et longueur calés sur
  le vrai sujet (mesurer le nombre de mots du texte des sujets réels avant d'écrire) ; thèmes camerounais plausibles.
- Un Paper 1 de langue contrôle grammaire, vocabulaire, usage, synonymes, ponctuation : une seule réponse défendable par question (relecture
  par un second passage : « existe-t-il une deuxième option acceptable ? »).
- P2 : sections (compréhension, résumé, composition ou lettre, grammaire) avec leur barème ; composition notée sur contenu, organisation, expression,
  orthographe ; corrigé = **texte modèle** et liste des éléments attendus.
- Aucune figure.

- **Étalon produit le 2026-10-20 : English Language O Level, Paper 1 n°1** (`ep-cm-gce-ol-english-p1-1-2026-s1`, blueprint `bp-cm-gce-ol-english-p1-1`, code du Board 0530,
  générateur `generer_english_p1.py`, questions `questions_english_p1.py`, vérificateur `verifier_reponses_english_p1.py`, titres de cours `cours_titres_gce_english_ol.json`).
  - **Structure mesurée sur les 5 vrais Paper 1 (2021, 2023, 2024, 2025, 2026), identique d'une année à l'autre** : 50 QCM à 4 options, 90 minutes, quatre sections
    **A écoute 1-10** (un texte lu une seule fois par l'examinateur, en trois parties « Section One/Two/Three » de 4, 3 et 3 questions, 404 à 598 mots), **B lecture 11-25** (un ou deux
    textes, 455 à 905 mots), **C grammaire 26-40**, **D vocabulaire 41-50**. Difficulté : 10-27 faibles, 23-31 moyennes, 0-9 élevées ; clés a 7-14, b 7-14, c 12-15, d 7-11.
    Poids par thème et par paper : écoute, 8,6 questions de compréhension orale (le reste : accent de mot, synonymes) ; lecture, 12,8 de compréhension, 1,2 de classes de mots,
    0,4 de figures de style ; grammaire, 1 à 1,2 chacun pour conditionnels, temps, connecteurs, discours indirect, orthographe et ponctuation, adverbes, pronoms, tags, puis 0,2 à 0,8
    pour les autres ; vocabulaire, 3,4 de contexte, 3,4 de synonymes et antonymes, 1,4 de formation de mots, 0,8 d'idiomes.
  - **Inédite** : 10 + 15 + 15 + 10 questions, 24 faibles / 24 moyennes / 2 élevées, 13-13-12-12 clés placées par le script, deux textes originaux (une causerie suivie d'un récit, 441 mots ;
    un récit de lecture en six paragraphes numérotés, 532 mots), insérés dans l'énoncé de la question 1 et de la question 11 comme dans les vrais sujets. Thèmes préfixés `O Level English - ` (forme des `Tag`).
  - **Contrôles propres à une langue** (une clé de langue ne se recalcule pas) : chaque question de texte porte une `preuve`, phrase du texte retrouvée MOT POUR MOT par le vérificateur ; chaque
    question à trou porte sa phrase complète, comparée à l'énoncé rempli ; aucune suite de 7 mots commune à un texte ou à un énoncé de l'inédite et à un vrai sujet (les étiquettes de format et
    « is used as a/an » sont écartées) ; la bonne option n'est la plus longue que dans 10 questions sur 50. **Il reste un second passage humain** (« existe-t-il une deuxième option
    acceptable ? ») : il a écarté, avant écriture, les questions de figure de style ambiguës (personnification contre comparaison) et les mots à double sens (`frail`/`feeble`).
  - **Ne pas imiter** les questions « Options as printed » des vrais sujets (7 à 8 par paper en 2025-2026) : ce sont des artefacts d'extraction du PDF, jamais une forme à reproduire.
  - **Limites connues** : 7 thèmes sans `Cours` O Level (verb tenses, passive voice, reported speech, subject-verb agreement, phrasal verbs, confusable words, idioms and proverbs) : leurs rappels
    ne sont pas rattachés (compétence = le thème) tant que les cours ne sont pas générés ; la plateforme met en italique le discours direct entre guillemets droits ; dans le PDF, le numéro de la question
    qui porte le texte (1 et 11) précède le texte, et l'énoncé de cette question suit le texte sans numéro (même forme que les vrais sujets).
- **Étalon produit le 2026-10-20 : English Language O Level, Paper 2 n°1** (`ep-cm-gce-ol-english-p2-1-2026-s1`, blueprint `bp-cm-gce-ol-english-p2-1`, générateur `generer_english_p2.py`, contenu
  `questions_english_p2.py`, vérificateur `verifier_reponses_english_p2.py`).
  - **Structure mesurée sur les 8 vrais Paper 2 (2019-2026), identique d'une année à l'autre** : 2 heures, 70 points. **Section A, écriture dirigée (30 points : contenu 14, expression et correction 12,
    orientation persuasive 4)** : une consigne de rôle et de destinataire (« You are ... Selecting relevant material from the passage below, write a talk / article / report ... »), un texte de 412 à 633 mots,
    une réponse en DEUX paragraphes d'au plus 150 mots, orientée pour convaincre ; le texte contient toujours des points à écarter. **Section B, composition (40 points : contenu et organisation 12,
    expression 16, correction 12)** : 8 sujets a-h dont UN SEUL à traiter : récit terminé par une phrase donnée, description, sujet en un mot, « Do you agree? », récit illustrant un proverbe, exposé
    (effets, causes, avantages et inconvénients), lettre, et un sujet à partir d'images (h). Les corrigés réels portent, pour chaque sujet, un plan, un modèle de 451 à 499 mots, la grille et les erreurs courantes ;
    pour la Section A un modèle de 127 à 148 mots, « pourquoi il fonctionne » (sélection et orientation), la grille et les erreurs courantes.
  - **Inédite** : la plateforme ne code pas les choix, donc la Section B est UNE question de 40 points qui liste sept sujets a-g et dit « choose ONE », avec un plan et un modèle (451 à 497 mots) pour CHAQUE
    sujet ; le sujet h (images) est omis, aucune figure. Deux exercices (`1` groupe SECTION A, `B1` groupe SECTION B), une question chacun, deux grilles à trois critères observables dont les points
    font 30 et 40. Texte de la Section A de 501 mots sur un thème absent des 8 vrais sujets (déchets plastiques), un paragraphe de procédés industriels à écarter ; modèle de 125 mots en deux paragraphes.
  - **Contrôles** : modèle A à deux paragraphes et 150 mots au plus, chacun de ses points repris d'une phrase du texte retrouvée mot pour mot, aucun point hors sujet ; modèles B de 440 à 510 mots, contrainte propre
    à chaque sujet (le récit finit par la phrase donnée, la lettre porte adresse, date, formule d'appel et de politesse) ; aucune fuite de nom, de lieu ni de mot-clé depuis le Paper 1 de la session ;
    aucune suite de 7 mots commune avec un vrai sujet ou le Paper 1 inédit (les gabarits d'examen imprimés sont écartés : ligne « Mark distribution », « Write in TWO paragraphs of not more than 150 words »,
    « your address is P.O. Box », « Selecting relevant material from the passage below »). **La qualité de la langue des modèles (grammaire, ton, naturel) ne se vérifie pas par machine : relecture humaine.**
  - **Limites** : pas de cours O Level « Directed Writing » (compétence du rappel non rattachée) ; la plateforme n'a pas de champ pour une règle de choix ; le PDF du sujet n'imprime que les énoncés.

- **Étalon produit le 2026-10-20 : French O Level, session n°1** (code du Board 0545 ; `ep-cm-gce-ol-french-p1-1-2026-s1` et `-p2-1-2026-s1`, générateurs `generer_french_p1.py` et `_p2.py`, contenus
  `questions_french_p1.py` et `questions_french_p2.py`, vérificateurs `verifier_reponses_french_p1.py` et `_p2.py`, titres de cours `cours_titres_gce_french_ol.json`, les 19 thèmes ont un cours O Level).
  - **Paper 1 (mesuré sur 6 vrais sujets : 2020-2023, 2025, 2026)** : 50 QCM en 1h30 : 45 questions isolées (grammaire, conjugaison, accords, pronoms, articles, vocabulaire, expressions, traduction de
    proverbes anglais, nombres) puis un texte à trous de 5 questions (46-50). Par paper : vocabulaire 7,2, temps et modes 6,8, accords 6, conjugaison 4,8, pronoms 4,7, compréhension 4,3, articles 3,8, expressions 2,8,
    prépositions 2,5, traduction 1,8, nombres 1,8, négation 1, relatifs 1 ; difficulté 13-28 faibles, 20-33 moyennes, 2-5 élevées. Contenu en français, explications en anglais. **Pour chaque distracteur, une raison écrite
    de son erreur** (`Q(..., [(option, raison)] x 3, ...)`) : c'est le second passage « existe-t-il une deuxième option acceptable ? » noir sur blanc, et le piège du corrigé est composé de ces raisons.
    Écartés après relecture : « ces élèves » (peut être féminin), « calmées » (participe possible), « il ne reste personne dans le frigo » (grammatical mais absurde), une traduction littérale d'un proverbe (acceptable).
  - **Paper 2 (mesuré sur 8 vrais sujets : 2019-2023, 2025, 2026 ; 1h30 puis 2h)** : 80 points, deux questions égales de 40. **Question 1** : traduction de l'anglais vers le français d'un texte de quatre paragraphes ;
    corrigé = traduction modèle, tableau des pièges (forme fautive, forme correcte), note, erreurs courantes. **Question 2** : une rédaction de 140 à 150 mots (hors chiffres, mots entre parenthèses, abréviations, noms propres de
    personnes et de lieux) à choisir parmi trois sujets : (a) récit guidé en trois puces, (b) lettre avec NOM et ADRESSE imposés (introduction de 20 mots au plus), (c) sujet fondé sur des images. Inédite : Question 2 = UNE question
    qui liste les sujets et dit « choose ONE », avec un modèle pour chacun ; le sujet (c) à images est REMPLACÉ par un sujet guidé sans images ; deux exercices `1` et `2`, quatre critères de notation pour la traduction
    (12 + 10 + 10 + 8) et cinq pour la rédaction (16 + 6 + 6 + 6 + 6).
  - **Contrôles** : Paper 1 : clé unique, raison de chaque distracteur citée dans le corrigé, phrase complète recomposée depuis l'énoncé rempli (39 cas), texte à trous rempli avec les cinq réponses = texte complet ;
    Paper 2 : même nombre de paragraphes et de phrases entre texte et traduction modèle, chaque ligne du tableau des pièges retrouvée dans le modèle, décompte des mots selon la règle du sujet (143-146), couverture de
    chaque puce par un extrait du modèle ; aucune fuite entre papers ; aucune suite de 6 mots commune avec un vrai sujet (les consignes d'examen imprimées sont écartées). **La correction du français lui-même (accords,
    temps, naturel) n'est pas vérifiable par machine : relecture humaine par un enseignant de français.**
  - **Pièges de plateforme rencontrés** : `\"` dans une chaîne brute Python garde son antislash (normalisé dans `Q()`) ; une question dont l'énoncé n'est qu'une étiquette (« Space 47 ») est jugée trop proche d'un vrai sujet par
    `controle_inedite_gce.py` quand l'étiquette est la même : reformuler l'étiquette.

### F. Pratique et applications (Computer Science, ICT, Geography A/L P3)

- Les données et fichiers « du jour » des vrais sujets ne sont pas dans le PDF : l'inédite doit être **complète en soi**. Toute donnée nécessaire (table,
  fichier de valeurs, jeu d'essai) est écrite dans l'énoncé.
- Programmation : énoncé de tâche, spécification d'entrées et sorties, jeu d'essai ; corrigé = algorithme (pseudo-code), code (ISO Pascal ou ANSI C
  comme le vrai sujet), exemple d'exécution. **Le code est exécuté ou traduit en Python et la trace est comparée**, sinon `incertitudes` le dit
  (aucun compilateur C/Pascal sur la machine).
- ICT : tâches tableur (formules `=SUM(B2:B9)` en code, `$` protégé), base de données, web, présentation ; corrigé = démarche, formules, requêtes SQL
  vérifiées avec `sqlite3`.
- Geography A/L P3 : carte topographique hors de portée (jamais d'imitation). Si la question exige une carte, ne pas la produire : le dire.
- Figures : algorigrammes, structures de données et tableaux de trace sont réalisables (§6).

### G. Quantitatif multi-parties (Economics P3, Mechanics, Statistics, Physics A/L)

- 5 à 8 questions de 13 à 25 points, chaque question en parties `(a)`, `(b)`, `(c)` avec leurs points imprimés ; données chiffrées dans un tableau
  Markdown ; unités SI ; `g = 10 m s^-2`.
- Calcul entièrement recalculé par script ; chaque question a un fil (le résultat de `(a)` sert à `(b)`) sans que l'erreur de `(a)` ne puisse
  propager un faux corrigé : le corrigé donne le résultat de `(a)` avant de l'utiliser.
- Mécanique et Statistics : la partie Pure Maths de ces papers est **partagée** entre les deux matières d'une même session (README §4) : une inédite
  `Mechanics` et une inédite `Statistics` ne partagent aucune question entre elles.

## 6. Figures : ce que le GCE permet de produire (SVG calculé)

| Matière | Réalisable | Hors de portée |
|---|---|---|
| Mathematics, Add. Maths, Further, Pure Maths | repères, courbes, droites, histogrammes, diagrammes en barres, diagrammes de Venn, diagrammes sagittaux, réseaux, figures planes (angles, triangles, cercles avec centre et angle inscrit, polygones, solides en perspective cavalière), droites graduées, cap et nord | constructions à main levée sans coordonnées |
| Physics, Chemistry | graphiques expérimentaux, circuits simples, schémas de montage simples | verrerie détaillée, optique à l'échelle |
| Biology, Human Biology, Geology | graphiques de résultats, arbres généalogiques, croisements, chaînes de réactions | schémas anatomiques, cellulaires, histologiques, coupes géologiques |
| Computer Science, ICT | algorigrammes, structures de données, tableaux de trace | captures d'écran |
| Economics, Commerce | courbes d'offre et de demande, graphiques, diagrammes en barres, frises | tableaux photographiés |
| Geography, History | graphiques, frises | **cartes**, photographies |
| English, French, Literature, Religious Studies, Philosophy, Citizenship | aucune | |

Règles d'un SVG de paper (en plus de celles du skill) : **point décimal** et graduations anglaises (la bibliothèque graduait avec la virgule : le
générateur remplace `figures_svg.fmt`) ; vrai signe moins `−` ; légendes `Figure n` continues sur l'épreuve entière dans l'ordre des questions ; texte
de figure en anglais ; les arcs et marques d'angle droit dessinés **par-dessus** le remplissage d'une forme (couche 3) ; chaque donnée utile de la figure
répétée dans `<desc>` et, quand elle ne se déduit pas de l'énoncé, dans le texte ; une figure d'énoncé ne contient jamais la réponse.

## 7. Étalonnage du skill : ce qui lui manquait

1. Il ne connaissait ni le Mode GCE, ni le Paper 1 de 50 QCM, ni les papers : il supposait des exercices numérotés sur 20 points et des séries.
2. Il n'avait aucune règle de **calibrage chiffré** (nombre de questions, ordre, poids des thèmes, difficulté, options, figures) : tout vient du
   corpus réel, désormais outillé (`controle_inedite_gce.py`).
3. Il demandait de « re-résoudre le calcul » sans outil : `verifier_reponses_maths_p1.py` en est la version exécutable pour une QCM (la clé est la
   seule option égale à la valeur recalculée).
4. Il ne disait pas où va le numéro de paper, ni la règle de choix, ni le code matière : conventions §1 et §4.
5. Il ne prévoyait pas la **lettre de la clé** : placée et citée par le générateur.
6. Ses figures graduaient en français : correction §6.
7. Rien ne contrôlait le PDF du sujet (c'est lui qui a révélé le DÉFAUT 1) : le contrôle visuel doit inclure le PDF, page par page.
8. Le tunnel de validation ne regarde pas le contenu des épreuves inédites : la structure se garantit par `controle_inedite_gce.py` et l'ingestion
   à blanc, les thèmes par le contrôle contre le corpus.

## 8. Reste à faire (hors de cet étalonnage)

- Sessions inédites publiées en base LOCALE seulement : Maths, Biology, Physics, Chemistry, Additional Mathematics (O Level, n°1) et, produites par d'autres sessions, English Language et French.
  Suivantes proposées : Human Biology (jumeau de Biology), Computer Science (type pratique, à étalonner d'abord), une matière à essais (Commerce ou Economics) pour étalonner ce type, puis une
  session Additional Mathematics n°2 avec la Section C (Statistiques et Probabilités). Rejouer en production : pousser, rebuild `backend`, `ingest_inedit_content`, valider les blueprints, publier, `save_sujet_pdf`, `indexer_recherche`.
- Rejouer en production le correctif DÉFAUT 6 (rebuild backend, recompiler les épreuves à parties, régénérer leurs PDF).
- Rejouer en production le correctif DÉFAUT 1 (rebuild backend, recompiler les 19 épreuves à QCM, régénérer leurs PDF).
- Décider DÉFAUT 4 : porter `numero_paper`, `code_matiere` et `regles_choix` dans `inedit` (sinon les papers à choix restent en « answer ALL »).
- Étalonner un paper de chaque type C, D, E, F, G avec les mêmes quatre contrôles ; l'étalon est entièrement chiffré pour A et B (Maths O/L P1 et P2), qualitatif
  pour les autres (aucun paper inédit de ces types n'a encore été produit).
- Cours des 2 thèmes sans cours (`change of subject`, `circle`) : leurs rappels portent une compétence sans `Cours` existant.
