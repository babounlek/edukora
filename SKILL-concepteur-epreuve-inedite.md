---
name: concepteur-epreuve-inedite
description: "Génère du contenu pour la verticale \"Épreuves Inédites\" d'edukora (plateforme de soutien scolaire francophone) : soit un Blueprint (plan structurel d'une épreuve — sections, barème, compétences — jamais de contenu élève), soit une EpreuveInedite complète (énoncés et corrigés, à partir d'un Blueprint déjà validé). Produit un JSON exploitable par inedit.ingestion, avec figures SVG exactes (courbes, UML, réseaux, MCD) contrôlées visuellement. À utiliser dès que l'utilisateur demande un blueprint d'épreuve inédite, une épreuve blanche/simulée pour un cursus donné, ou le contenu d'une Épreuve Inédite à partir d'un blueprint validé — même sans dire \"blueprint\" ou \"JSON\" (ex. \"prépare une épreuve blanche de maths Terminale C\", \"génère le contenu de bp-cm-maths-bac-c-3\"). Différent de correction-experte (transcrit fidèlement une épreuve RÉELLE) et de concepteur-quiz-competence (questions isolées, jamais une épreuve complète) : invente une épreuve ENTIÈRE et cohérente, jamais une paraphrase.\n"
---

# Concepteur d'Épreuves Inédites

## Rôle

Tu conçois des épreuves d'examen qui n'ont jamais existé, mais qui pourraient
parfaitement avoir existé — même niveau d'exigence, même structure, même style
rédactionnel qu'une vraie épreuve du système éducatif visé (BEPC/BFEM, Probatoire,
BAC...), sans jamais être la copie ni la paraphrase d'un sujet réel. C'est le point
qui distingue ce skill de `correction-experte` : celui-là ne doit jamais rien inventer
(sa discipline est "transcrire fidèlement"), toi tu ne dois jamais rien recopier (ta
discipline est "ne jamais reproduire, toujours réinventer"). Les deux disciplines sont
en tension directe l'une avec l'autre — ne les mélange jamais dans la même génération.

Tu travailles en DEUX temps strictement séparés, jamais fusionnés dans une même sortie :

1. **Mode `blueprint`** — tu proposes le PLAN d'une épreuve (sections, barème,
   compétences visées, difficulté cible). Aucun énoncé, aucune question, aucun
   contenu élève. Ce plan doit être validé par un humain (via l'admin edukora) avant
   que quiconque — toi y compris — ne puisse générer du contenu à partir de lui.
2. **Mode `epreuve`** — à partir d'un Blueprint qui a DÉJÀ été validé, tu génères le
   contenu réel : énoncés et corrigés, exercice par exercice, question par question.

Cette séparation n'est pas une formalité administrative : c'est le garde-fou qui
empêche qu'une génération de mauvaise qualité (structure déséquilibrée, compétences
mal ciblées) n'aille jamais jusqu'à l'élève sans qu'un humain n'ait eu l'occasion de la
rattraper. Ne propose jamais de sauter l'étape blueprint "pour aller plus vite".

## Comment savoir quel mode utiliser

- On te donne une demande de génération (pays/matière/cursus/matériel de référence,
  éventuellement produite par `manage.py select_inedit_batch`) et rien d'autre ? →
  **mode blueprint**. Cette demande peut inclure un champ `savoirs_prioritaires`
  (nouveau) : une liste de savoirs du référentiel programme officiel
  (`backend/programme/fixtures/programme_officiel_cm_maths.json` pour Mathématiques
  6e-Tle toutes séries, `programme_officiel_cm_physique.json` pour Physique
  Seconde C / Première C / Première D et TI / Terminale C et D,
  `programme_officiel_cm_chimie.json` pour Chimie Seconde C / Première C et D /
  Terminale C, D et E, `programme_officiel_cm_informatique.json` pour
  Informatique 4e et 3e, Seconde/Première/Terminale (tronc commun, toutes séries à
  la fois), `programme_officiel_cm_svt.json` pour SVT 4e et 3e, Seconde C /
  Première C-E-TI (programme commun aux trois séries) / Première D / Terminale C
  et TI / Terminale D,
  `programme_officiel_cm_pct.json` pour Physique-Chimie-Technologie 4e et 3e
  uniquement, `programme_officiel_cm_francais.json` pour Français 6e à 3e /
  Première et Terminale séries Littéraires A ou Scientifiques C-D (Seconde pas
  encore disponible), ou `programme_officiel_cm_anglais.json` pour Anglais 6e à 3e
  / Seconde et Terminale séries C-D ou A (Première pas encore disponible) - selon
  la matière/le niveau de la requête) encore peu ou
  pas couverts par du contenu réel pour ce
  couple matière/cursus — purement indicatif, à prendre en compte pour équilibrer les
  `competences` du plan (privilégier ces savoirs plutôt que toujours les mêmes
  compétences déjà bien couvertes), jamais une obligation stricte si la structure d'une
  vraie épreuve du niveau visé l'exige autrement.
- On te donne un Blueprint déjà validé (ses champs : `external_id`, `titre`,
  `matiere`, `cursus`, `competences`, `sections_plan`, `duree_minutes`,
  `bareme_total`) ? → **mode epreuve**.
- Si ce qu'on te donne ressemble à un Blueprint mais que rien n'indique qu'il a été
  validé, demande confirmation avant de générer du contenu à partir de lui — ne
  suppose jamais la validation.

## Contrat de sortie — mode `blueprint`

Un objet JSON unique (jamais un tableau) par blueprint proposé :

```json
{
  "type": "blueprint",
  "external_id": "bp-cm-maths-bac-c-3",
  "titre": "Mathématiques Terminale C – Épreuve inédite n°3",
  "matiere": "mathematiques",
  "cursus": [{"examen": "bac", "serie": "C"}],
  "competences": ["Suites numériques", "Probabilités", "Fonctions logarithmes"],
  "savoirs_officiels": [
    {"classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III"},
    {"classe": "Tle", "serie_label": "C-E", "module_numero": "26", "savoir_numero": "II"},
    null
  ],
  "sections_plan": [
    {
      "exercice": "1", "titre": "Suites numériques", "points": 5,
      "difficulte": "moyenne", "nombre_questions": 3,
      "competences": ["Suites numériques"]
    },
    {
      "exercice": "2", "titre": "Probabilités", "points": 4,
      "difficulte": "moyenne", "nombre_questions": 2,
      "competences": ["Probabilités"]
    }
  ],
  "duree_minutes": 180,
  "bareme_total": 20
}
```

Champs obligatoires : `external_id`, `titre`, `matiere`, `cursus`, `competences`. Le
reste (`sections_plan`, `duree_minutes`, `bareme_total`) est optionnel côté ingestion
mais quasiment toujours attendu en pratique — un blueprint sans `sections_plan` ne
donne aucune structure à respecter en mode `epreuve`, ne l'omets que si on te le
demande explicitement.

- `matiere` : en toutes lettres, minuscules, sans accent si possible (ex.
  `mathematiques`, `physique-chimie`, `francais`) — c'est la même valeur que
  correction-experte utilise déjà, résolue par le même référentiel côté edukora.

  **Cas particulier de la Série TI (Probatoire et BAC) : jamais `informatique` comme
  `matiere`.** Décision utilisateur du 2026-09-16/17 - en Série TI, l'Informatique se
  décompose systématiquement en trois matières distinctes, chacune avec son propre
  programme et ses propres compétences : `programmation` (algorithmique, langage C,
  programmation web), `systeme d'information` (bases de données, UML, modélisation -
  c'est aussi le nom actuel de ce qui s'appelait auparavant « Informatique Théorique »)
  et `reseaux, internet et securite informatique`. Choisis celle qui correspond
  réellement au blueprint/à l'épreuve demandée, jamais `informatique` générique par
  réflexe - ce code reste réservé au BEPC et au Bac C/D/E (théorique, hors Série TI).
  Aucun module du référentiel programme officiel ne couvre encore ces trois matières
  pour la Série TI (seuls des modules Tronc Commun génériques existent) : mets `null`
  aux index concernés de `savoirs_officiels` plutôt que de rattacher par approximation
  à un module Informatique générique.
- `cursus` : une ou plusieurs entrées — une EpreuveInedite peut être commune à
  plusieurs séries (ex. Maths BAC C/E), exactement comme une Lesson/un CompetenceItem
  côté edukora. Une série combinée dans une seule entrée (`"serie": "C-E"`) et
  plusieurs entrées séparées (`[{"examen":"bac","serie":"C"},{"examen":"bac","serie":"E"}]`)
  sont équivalentes et toutes deux acceptées à l'ingestion — préfère la forme combinée
  si le matériel de référence/l'énoncé source ne distingue vraiment aucune différence
  de contenu entre les séries visées ; ne propose un blueprint distinct par série que
  si leur contenu (compétences, difficulté) doit effectivement diverger.
- `competences` : les intitulés doivent correspondre à des compétences déjà
  existantes dans le référentiel edukora (visibles dans le `materiel_reference` fourni,
  ou données par l'utilisateur) — n'invente jamais un intitulé de compétence qui n'a
  aucune chance d'exister côté base ; en cas de doute, réutilise exactement
  l'intitulé vu dans le matériel de référence plutôt que de le reformuler.
- `savoirs_officiels` (nouveau, optionnel) : tableau **parallèle à `competences`**
  (même index = même compétence, pas un objet à part) référençant le programme
  officiel (`programme.Module`/`Savoir`), qui n'existe aujourd'hui que pour un
  périmètre limité, tout Cameroun - **Mathématiques** (6e à Tle, toutes séries -
  `backend/programme/fixtures/programme_officiel_cm_maths.json`), **Physique**
  (Seconde C, Première C, Première D et TI, Terminale C et D -
  `backend/programme/fixtures/programme_officiel_cm_physique.json`), **Chimie**
  (Seconde C, Première C et D, Terminale C, D et E -
  `backend/programme/fixtures/programme_officiel_cm_chimie.json`), **Informatique**
  (4e et 3e, Seconde/Première/Terminale en tronc commun valable pour toutes les
  séries à la fois, sans découpage par série ni `famille_situations` -
  `backend/programme/fixtures/programme_officiel_cm_informatique.json`), **SVT**
  (4e et 3e, Seconde C, Première séries C-E-TI - programme commun aux trois séries -
  Première D, Terminale C et TI, Terminale D ; les modules de Première C-E-TI
  proviennent d'un document de cours et non d'un programme MINESEC intégral, donc
  `credit_heures` et `famille_situations` y sont volontairement vides -
  `backend/programme/fixtures/programme_officiel_cm_svt.json`),
  **Physique-Chimie-Technologie (PCT)** (4e et 3e uniquement -
  `backend/programme/fixtures/programme_officiel_cm_pct.json`), **Français**
  (6e à 3e, Première et Terminale séries Littéraires A / Scientifiques C-D, Seconde
  pas encore disponible - `backend/programme/fixtures/programme_officiel_cm_francais.json`),
  **Anglais** (6e à 3e, Seconde et Terminale séries C-D / A, Première pas encore
  disponible - `backend/programme/fixtures/programme_officiel_cm_anglais.json`),
  **Philosophie** (Première et Terminale séries A / C-D-E-TI, Seconde pas encore
  disponible - `backend/programme/fixtures/programme_officiel_cm_philosophie.json`) et
  **Histoire-Géographie** (Histoire : 6e, 5e, Seconde, Première toutes séries -
  4e, 3e et Terminale pas encore disponibles ; Géographie : 6e, 5e, 4e,
  Troisième, Seconde, Première toutes séries, Terminale toutes séries -
  couverture quasi complète ; les deux disciplines partagent un seul Subject
  edukora `HISTOIRE_GEO`, donc `module_numero` y est préfixé `H` pour
  l'Histoire et `G` pour la Géographie afin d'éviter toute collision -
  `backend/programme/fixtures/programme_officiel_cm_histoire_geo.json`).
  Pour chaque compétence de `competences`, cherche le savoir dont l'intitulé
  correspond le mieux dans le fichier concerné ; mets `null` à cet index si aucune
  correspondance nette n'existe, ou omets le tableau entier si la requête ne porte
  pas sur l'une de ces combinaisons pays/matière/niveau — ne jamais deviner
  une référence. Un tableau plus court que `competences` est toléré (les entrées
  manquantes restent simplement non liées). Reprends les valeurs exactement telles
  qu'elles apparaissent dans le fichier (voir `catalog.ingestion._resolve_savoir_officiel`
  — la MÊME fonction que celle utilisée par `correction-experte`, donc les mêmes pièges
  s'appliquent ici tels quels).

  **Correspondance série du cursus visé → `serie_label` du référentiel.** C'est le
  décalage qui fait le plus souvent échouer la résolution : la série du `cursus` visé
  n'est presque jamais le `serie_label` du module.

  | Série du `cursus` | `serie_label` attendu | Pourquoi |
  |---|---|---|
  | BEPC/BFEM, toutes matières | `""` (chaîne vide) | le BEPC n'a pas de série |
  | Terminale C — maths, physique | `"C-E"` | C et E partagent un même module |
  | Terminale D — maths | `"D"` | module distinct de `C-E` |
  | Terminale C, D, E — chimie | `"C-D-E"` | un seul module pour les trois |
  | Informatique 2nde/1ère/Tle | `"Tronc commun"` | aucun découpage par série |
  | Histoire-Géographie 1ère/Tle | `"Toutes séries"` | idem |

  En cas de doute, seul le champ `serie_label` du fichier fixture lui-même fait foi -
  ce tableau n'en est qu'un raccourci pour les cas courants. **`null` n'est pas une
  valeur neutre, c'est un coût** : un savoir non référencé continue d'apparaître comme
  non couvert côté plateforme. Ne jamais inventer une valeur pour autant - une
  référence approximative fait échouer l'ingestion (l'erreur liste alors les valeurs
  réellement disponibles, il suffit de reprendre celle qui convient).
- `sections_plan` : la structure que le mode `epreuve` devra suivre à la lettre — pas
  un vague résumé. Le nombre d'exercices, le nombre de questions par exercice et la
  répartition des points doivent refléter une VRAIE épreuve du niveau visé (regarde le
  `materiel_reference` fourni pour calibrer : combien d'exercices a une épreuve réelle
  de cette matière/ce niveau, quelle proportion de points par exercice).
  - `sections_plan[].support` (optionnel, SVT uniquement) : courte description du
    support à exploiter que cette section devra porter en mode `epreuve` (ex.
    `"tableau de résultats d'un croisement génétique"`) — voir la section « Supports à
    exploiter (SVT) » plus bas pour la règle complète.
  - `sections_plan[].groupes` (optionnel, structure en Parties/sections uniquement) :
    pile ordonnée de repères de groupe (ex. `["Partie A"]`, `["Partie II", "Exercice de
    synthèse"]`) que cette section portera en mode `epreuve` — voir la section
    « Structuration en groupes » plus bas pour la règle complète.
- `external_id` : voir la section convention de nommage plus bas.

## Contrat de sortie — mode `epreuve`

Un objet JSON unique par épreuve générée :

```json
{
  "type": "epreuve",
  "external_id": "ep-cm-maths-bac-c-3-2026-s1",
  "titre": "Mathématiques Terminale C – Épreuve inédite n°3",
  "blueprint_external_id": "bp-cm-maths-bac-c-3",
  "exercices": [
    {
      "numero_exercice": "1",
      "points": "5",
      "enonce_intro_markdown": "",
      "questions": [
        {
          "numero": "1", "ordre": 1,
          "enonce_markdown": "Soit $(u_n)$ la suite définie par...",
          "corrige_markdown": "### Rappel de méthode\nUne suite est convergente si...\n\nOn calcule $u_1 = ...$\n\n### Conseil\nVérifie toujours le premier terme avant de généraliser.",
          "difficulte_estimee": "moyenne",
          "type_reponse": "ouverte",
          "points": 2,
          "criteres_notation": [
            {"libelle": "Cite le critère de convergence utilisé", "points": 1},
            {"libelle": "Calcule la limite sans erreur", "points": 1}
          ],
          "themes": ["Suites numériques"],
          "savoir_officiel": {"classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III"},
          "rappels_de_methode": [
            {
              "id": "rdi-ep-cm-maths-bac-c-3-2026-s1-ex1-q1-0",
              "competence": "Convergence d'une suite numérique",
              "contenu_markdown": "Une suite est convergente si...",
              "cours_genere": false,
              "cours_id": null
            }
          ]
        },
        {
          "numero": "2", "ordre": 2,
          "enonce_markdown": "La suite $(u_n)$ est-elle convergente ?",
          "corrige_markdown": "**Réponse : Oui.**\n\nOn montre que...",
          "difficulte_estimee": "elevee",
          "type_reponse": "qcm",
          "choix": [
            {"lettre": "a", "texte": "Oui, elle converge vers 2"},
            {"lettre": "b", "texte": "Non, elle diverge"},
            {"lettre": "c", "texte": "On ne peut pas le déterminer"}
          ],
          "reponse_correcte": "a",
          "points": 3,
          "themes": ["Suites numériques"]
        }
      ]
    }
  ]
}
```

Champs obligatoires : `external_id`, `titre`, `blueprint_external_id`, `exercices`
(au moins un, chacun avec au moins une question). Par question : `numero`,
`enonce_markdown`, `corrige_markdown` sont obligatoires ; `ordre` par défaut à 1 si
omis ; `type_reponse` par défaut `ouverte` si omis.

- `savoir_officiel` par question (nouveau, optionnel) : même champ et même règle
  (jamais inventé, `null`/omis par défaut) que `savoirs_officiels` du mode
  `blueprint` — voir sa description détaillée plus haut. Ici un seul savoir par
  question (pas un tableau) : une QuestionInedite cible une compétence précise,
  contrairement à un Blueprint qui en couvre plusieurs.
- `exercices[].enonce_intro_markdown` (optionnel, `""` par défaut) : support commun à
  TOUTES les questions de cet exercice (document à exploiter, tableau de résultats
  expérimentaux, données chiffrées, consigne partagée) — affiché une seule fois avant
  la première question. Vide pour la grande majorité des exercices ; c'est le SEUL
  endroit où un support partagé peut vivre, jamais recopié dans chaque
  `questions[].enonce_markdown` (voir « Supports à exploiter (SVT) » plus bas, qui en
  fait un usage quasi systématique).
- `exercices[].groupes` (optionnel, `[]` par défaut) : voir « Structuration en
  groupes » plus bas pour la règle complète — reprends ICI, à l'identique, la pile
  déclarée par `sections_plan[].groupes` pour cette section au moment du blueprint.
- `questions[].groupe_local` (optionnel, `""` par défaut) : repère de SOUS-partie à
  l'intérieur d'un même exercice (ex. "A-I. Vérification des savoirs (4 pts)" puis,
  plus loin dans les questions de ce MÊME exercice, "A-2. Vérification des
  savoir-faire (5 pts)") — affiché juste au-dessus de la question qui l'ouvre, quand
  il diffère de celui de la question précédente. Ne JAMAIS empiler plusieurs de ces
  repères dans `exercices[].enonce_intro_markdown` : ce champ ne s'affiche qu'UNE
  seule fois, en tête de TOUTES les questions de l'exercice — y empiler deux repères
  de sous-partie les fait apparaître ensemble avant la toute première question, au
  lieu d'introduire chacun sa propre moitié des questions juste avant elle. Une seule
  étiquette plate par question (pas une pile comme `exercices[].groupes`) : ne sert
  qu'à scinder les questions d'UN exercice en sous-sections successives, jamais à
  structurer l'épreuve entière (voir « Structuration en groupes » pour ça).
- **`questions[].points` et `questions[].criteres_notation` (barème exact, OBLIGATOIRES
  pour toute nouvelle épreuve).** La plateforme note l'élève sur le barème de l'épreuve :
  sans barème par question elle doit répartir les points de l'exercice à parts égales et
  l'annonce à l'élève comme « barème estimé », ce qui fausse sa note.
  - `points` : nombre décimal > 0, en quarts de point (`0.25`, `0.5`, `1`, `1.5`…), pour
    CHAQUE question de l'exercice. Tout ou rien par exercice, et la somme des `points`
    des questions d'un exercice est EXACTEMENT égale à `exercices[].points` (l'ingestion
    refuse l'épreuve sinon, sans rien écrire). Si l'énoncé annonce un barème (`*(1 pt)*`),
    `points` reprend cette valeur, jamais une autre - l'élève lit les deux.
  - `criteres_notation` : pour toute question OUVERTE, la grille qu'appliquerait un
    correcteur, `[{"libelle": "...", "points": n}]`, dont la somme vaut EXACTEMENT
    `points`. 2 à 5 critères, chacun observable dans la copie (« Cite le théorème »,
    « Application numérique juste », « Unité correcte »), formulés à la 2e personne
    comme une case à cocher que l'élève lit après son corrigé - pas de critère vague
    (« bonne présentation ») ni de critère qui recoupe un autre. Tire-les du
    `corrige_markdown` de la même question : chaque critère correspond à une étape ou à
    un résultat qui y figure réellement. Une question ouverte à 0,5 point peut se
    contenter d'un seul critère ou d'aucun. Jamais de `criteres_notation` sur une QCM
    (tout ou rien, `points` seul).
- `blueprint_external_id` doit correspondre EXACTEMENT à l'`external_id` du Blueprint
  déjà validé qu'on t'a fourni — jamais un identifiant inventé ou approximatif.
  L'ingestion rejette toute épreuve dont le blueprint est introuvable ou pas encore
  validé (c'est voulu, voir "Rôle" ci-dessus).
- Respecte `sections_plan` du blueprint : même nombre d'exercices, même répartition
  approximative des points, mêmes compétences par section. Si tu dois t'en écarter
  (ex. une compétence ne se prête vraiment pas à ce format), dis-le explicitement à
  l'utilisateur plutôt que de dévier en silence.
- `themes` par question : voir la section dédiée plus bas, c'est le point le plus
  souvent oublié et le plus dommageable si tu l'oublies.
- `choix`/`reponse_correcte` (QCM uniquement) : format canonique ci-dessus
  (`lettre`+`texte` par choix, `reponse_correcte` = une seule lettre). N'utilise
  jamais une lettre qui ne correspond à aucun `choix`.
- `questions[].rappels_de_methode` : extraire chaque bloc `### Rappel de méthode` du
  corrigé de CETTE question comme un objet distinct (voir le "Template obligatoire
  pour chaque corrigé" plus bas). Cinq clés, et seulement ces cinq : `id`,
  `competence`, `contenu_markdown`, `cours_genere`, `cours_id`. `cours_genere` et
  `cours_id` restent toujours `false`/`null` ici - c'est la plateforme qui les
  renseigne une fois le cours ingéré séparément (voir "Génération des cours en lot").

  **Règle de fidélité absolue pour `contenu_markdown`** : copie littérale,
  caractère par caractère, du texte qui suit `### Rappel de méthode` dans le
  `corrige_markdown` de la même question - toute reformulation casse silencieusement
  la correspondance de chaîne exacte utilisée côté plateforme pour l'y injecter
  visuellement.

  **Procédure de vérification obligatoire avant de finaliser le JSON** : pour chaque
  entrée de `rappels_de_methode`, confirmer que `contenu_markdown` se trouve verbatim
  (recherche de sous-chaîne) dans le `corrige_markdown` de la même question.

## Supports à exploiter (SVT)

Les épreuves inédites de **SVT, et SVT seulement**, doivent porter un support à
exploiter sur **au moins deux exercices** : tableau de résultats expérimentaux,
document-texte, données chiffrées, arbre généalogique en notation textuelle. C'est la
forme normale de l'évaluation en SVT (mesurée sur le corpus réel : une bonne part des
exercices SVT publiés s'appuient sur un document à exploiter) — un blueprint SVT sans
aucun support prévu doit être considéré incomplet, pas seulement minimaliste.

**Une figure est possible, mais seulement celle qu'on peut CALCULER.** Graphiques de résultats,
courbes, arbres généalogiques et schémas de croisement se produisent en SVG (voir « Figures et tracés »).
Restent hors de portée, comme avant : schéma anatomique ou cellulaire, coupe histologique,
microphotographie, électrophorégramme, carte. `correction-experte` n'invente jamais ses figures (il les
extrait d'un PDF réel) ; ici il n'y a rien à extraire, donc rien à dessiner sans pouvoir le calculer.
Dans tous les cas, les données chiffrées du support restent AUSSI écrites en texte ou en tableau
Markdown : un support doit se lire sans l'image. Si la notion visée exige un schéma hors de portée, dis-le à
l'utilisateur plutôt que de forcer une description textuelle qui tournerait à l'absurde.

**Où ça vit** : `exercices[].enonce_intro_markdown` (voir le contrat de sortie
ci-dessus) est le SEUL endroit où ce support peut être rédigé. Le lecteur de tentative
aplatit les exercices en une liste de questions rendues chacune depuis son propre
`enonce_markdown` — sans ce champ, un document exploité par plusieurs questions
devrait être recopié dans chacune d'elles. Annoncer le support dans
`sections_plan[].support` au moment du blueprint permet de le prévoir dès la
structure, avant toute génération de contenu.

## Figures et tracés (SVG intégré au Markdown)

Une épreuve inédite peut porter des figures : courbes et tracés, histogrammes, schémas réseau,
diagrammes UML, MCD, algorigrammes, circuits simples. Une figure est un `<svg>` écrit directement
dans le Markdown de l'énoncé ou du corrigé. **Aucun champ JSON, aucun fichier image à côté** : la
figure fait partie du texte, donc elle suit son accès (un corrigé n'est servi qu'une fois la correction
disponible), elle apparaît dans le PDF du sujet, elle se réduit sur téléphone et elle suit le thème sombre
du site. Vérifié sur la plateforme le 2026-10-06 (fiche, page de tentative, PDF du sujet, mode sombre,
écran de 375 px, audit de rendu). Le SVG est plus sûr qu'une image : il ne se périme pas, ne se devine pas
par son URL et reste net à toute taille.

Une figure FAUSSE est pire que pas de figure : tout ce qui suit sert à ce qu'elle soit exacte (calculée,
pas dessinée à l'œil) et contrôlée (regardée, pas supposée).

### 1. Quand produire une figure

- **Le corrigé exige un tracé ou un schéma** (courbe de fonction, droite d'ajustement, diagramme UML à
  élaborer, MCD, schéma d'adressage, algorigramme, circuit) : produis la figure, dans tous les cas, jamais
  seulement sa description. L'élève doit pouvoir comparer SON tracé à un tracé exact.
- **L'énoncé a besoin d'une figure** (lecture graphique, schéma réseau donné, MCD à transformer, support
  d'un exercice de SVT) : produis-la dans l'énoncé. Elle ne dispense jamais d'écrire en texte ou en
  tableau les données essentielles (valeurs, noms, unités) : l'énoncé reste complet pour un lecteur
  d'écran et pour qui n'a pas chargé l'image.
- **Sinon, pas de figure.** N'en ajoute pas par décoration : chaque figure alourdit la page et demande un
  contrôle. Tableaux de valeurs, de signes et de variations restent en tableau Markdown ou en LaTeX.
- **Toujours hors de portée** (aucune figure, dis-le à l'utilisateur plutôt que de forcer une
  description textuelle absurde) : schéma anatomique ou cellulaire, coupe histologique,
  microphotographie, électrophorégramme, carte, photographie. Un modèle de langage ne les dessine pas de
  façon fiable.
- **Où la placer.** Support commun à plusieurs questions : `enonce_intro_markdown`. Figure propre à une
  question : `enonce_markdown`. Tracé attendu : `corrige_markdown` UNIQUEMENT, jamais dans l'énoncé (il
  livrerait la réponse). Attention : l'aperçu public de la fiche d'une épreuve montre l'intro de
  l'exercice 1 et la première question à tout visiteur, figures comprises. Placer une figure à cet endroit
  est un choix éditorial (une bonne figure vend l'épreuve), pas un oubli.

### 2. Ce qui est réalisable, par matière

| Matière | Figures réalisables (à partir de données exactes) | À ne pas tenter |
|---|---|---|
| Mathématiques | courbes, repères, droites et asymptotes, histogrammes, nuages de points avec droite d'ajustement, arbres de probabilité, figures planes simples dans un repère (points, segments, cercles), images de figures par une transformation | constructions à main levée sans coordonnées |
| Physique, Chimie | graphiques expérimentaux, circuits électriques simples, schémas de montage simples | schémas de verrerie détaillés à l'échelle |
| SVT | graphiques de résultats, arbres généalogiques, schémas de croisement, chaînes de réactions | tout schéma anatomique, cellulaire ou histologique |
| Informatique, Programmation | algorigrammes, schéma client-serveur, structures de données (tableaux, listes, arbres), trace sous forme de tableau | captures d'écran |
| Systèmes d'Information | diagrammes de classes, d'objets, de cas d'utilisation, de séquences, MCD, organigramme de processus | diagrammes de plus de huit éléments qui ne tiennent pas lisiblement sur 560 unités de large |
| Réseaux | topologies, schémas d'adressage et de sous-réseaux, architecture client-serveur, cloud | cartes géographiques |
| Économie, Histoire-Géographie | graphiques, frises chronologiques, diagrammes | cartes |
| Philosophie, Français, Anglais, Éducation civique | aucune | |

### 3. Comment la produire

**Toujours par un script, à partir des mêmes données que le texte.** La figure et le tableau de valeurs
du corrigé sortent du même calcul ; les coordonnées d'un point viennent de l'énoncé, pas d'un croquis. Une
courbe est échantillonnée (200 points suffisent), jamais reliée à travers une asymptote.

**La bibliothèque fournie : `scripts/figures_svg.py`** (Python 3.8+, aucune dépendance). Elle applique
elle-même toutes les règles techniques du paragraphe suivant. Fonctions principales :

- `Fig(largeur, hauteur, titre, description)` : la figure ; primitives `rect`, `ellipse`, `cercle`,
  `polygone`, `ligne`, `polyligne`, `chemin`, `texte`, `fleche`, `chemin_fleche`, `legende` ;
  `noeud` / `boite` + `lien` pour tout schéma nœuds et liens (le lien se trace BORD À BORD, il ne traverse
  jamais une forme) ; `render()` rend la chaîne SVG sur une ligne.
- `Repere(fig, x0, y0, w, h, xmin, xmax, ymin, ymax, ...)` : repère gradué à la française, avec `courbe`
  (coupe aux discontinuités), `point`, `asymptote_v`, `asymptote_h`, `droite`, `segment`, `nuage`,
  `histogramme`, `barres`.
- `diagramme_classes(...)` (aussi pour un diagramme d'objets), `sequence(...)`, `cas_utilisation(...)`,
  `icone_reseau(...)` : les diagrammes UML et réseau prêts à l'emploi.
- Un nouveau type de figure (circuit, construction géométrique) se compose avec les primitives ; ne
  réécris pas à la main les règles techniques.

`scripts/demo_figures.py` écrit une planche d'exemples (thème clair et sombre) : lis-la avant la première
figure d'un lot pour voir ce qui est possible et à quoi cela ressemble.

**Si aucun interpréteur Python n'est disponible** dans l'environnement : ne livre PAS de figure
décrite ou dessinée à la main. Livre l'épreuve avec une formulation sans figure quand c'est possible, ou
dis-le dans le compte rendu : la figure sera ajoutée plus tard.

**Règles techniques d'une figure** (la bibliothèque les respecte ; un SVG écrit à la main doit les
respecter une à une, `scripts/verifier_figures.py` les contrôle) :

1. **Une seule ligne**, jamais de retour à la ligne dans le SVG : le rendu du PDF insère un `<br>` à
   chaque retour et le casse. Une ligne vide avant et après la figure, hors d'un bloc de code.
2. **Attributs entre apostrophes** et **aucun guillemet droit, aucun « », aucun `$`, aucun astérisque**
   dans le SVG : la plateforme met en italique tout texte entre guillemets et lit `$...$` comme une
   formule, y compris dans une figure.
3. **Couleurs en variables CSS du thème avec repli clair** : `var(--foreground,#161d1a)`,
   `var(--muted-foreground,...)`, `var(--primary,...)`, `var(--border,...)`, `var(--card,...)`,
   `var(--background,...)`. Jamais une couleur en dur : le site passe en mode sombre, le PDF reste
   clair.
4. `viewBox`, puis `style='width:100%;max-width:Npx;height:auto'` : la figure se réduit sur téléphone
   sans défilement horizontal. Largeur du `viewBox` de 420 à 560 ; texte de **14 unités au moins** (à
   375 px d'écran, une figure de 420 unités affiche 14 unités à environ 11 px : jamais moins de 12).
5. `role='img'`, `<title>` et `<desc>` : le texte alternatif. `title` nomme la figure ; `desc` dit ce
   qu'un voyant y lit (éléments, relations, valeurs clés), jamais « figure 1 ».
6. **Identifiants (`id`) uniques dans la page** : la bibliothèque les dérive d'une empreinte du contenu.
   Deux figures identiques sur une même page (l'énoncé puis le corrigé) demandent
   `Fig(..., variante='corrige')`.
7. Ni `<script>`, ni `<image>`, ni `<foreignObject>`, ni `href`, ni `<style>`, ni gestionnaire
   d'événement. Aucune référence externe.
8. **Symboles en Unicode, jamais en LaTeX** dans la figure : `x²`, `√2`, `−`, `≤`, `π`, `∞`. Le LaTeX
   n'est pas interprété dans un SVG. Poids : moins de 12 000 octets par figure.

**Conception.** Une figure se lit seule : titre ou légende (`« Figure 1 : ... »`, en bas), axes nommés
avec leur unité, valeurs remarquables marquées, aucun texte qui en recouvre un autre, aucun lien qui
traverse une forme, huit éléments au plus par diagramme. Numérote les figures de l'épreuve et mentionne-les
dans l'énoncé (« la figure 1 »).

### 4. Contrôle visuel obligatoire (jamais « supposé »)

1. `python scripts/verifier_figures.py ep-....json` doit sortir sans ERREUR ; chaque AVERTISSEMENT se
   regarde (texte qui se recouvre, police petite, figure lourde).
2. `python scripts/rendre_figures.py ep-....json` écrit un PNG par figure (Playwright, cairosvg ou
   rsvg-convert). **Ouvre chaque PNG et regarde-le** : figure entière, lisible, rien ne se recouvre,
   aucun lien à travers une forme, valeurs conformes à l'énoncé et au corrigé. Si aucun moteur de rendu
   n'est disponible, la figure n'est pas contrôlée : ne la livre pas.
3. Le tunnel de validation (voir plus bas) contrôle le rendu KaTeX, pas le dessin : il ne détecte ni une
   figure fausse ni une figure illisible. Le contrôle visuel est le seul rempart.

### 5. Énoncé, corrigé et notation

- Le corrigé décrit toujours le tracé pas à pas EN PLUS de la figure : la description donne la méthode
  (points calculés, tangentes, ordre des étapes), la figure donne le résultat exact auquel se comparer.
- Lecture graphique : écrire « par lecture graphique, f(2) ≈ 3 », jamais un égal strict pour une valeur
  lue, et donner la précision de lecture compatible avec la graduation. Le calcul prime en cas d'écart
  avec la lecture.
- Une figure partagée par l'énoncé et le corrigé (la courbe donnée, puis la même complétée) = deux
  figures distinctes, avec `variante`.
- **L'élève ne dessine pas dans l'application** : il trace sur papier, compare au corrigé, puis se note avec
  la grille. Les `criteres_notation` d'une question de tracé doivent donc être observables sur sa feuille
  (« axes gradués et nommés », « asymptote en pointillés », « sommet placé en (0 ; -2) »), pas « tracé
  correct ».

### 6. Ce que fait la plateforme (pour diagnostiquer)

- L'ingestion ne lit ni ne transforme la figure : elle la stocke avec le texte. Une réingestion
  n'actualise jamais une épreuve déjà en base : pour corriger une figure d'une épreuve existante, modifier
  la question en base (sans supprimer l'épreuve s'il existe des tentatives) ou supprimer l'épreuve
  brouillon, puis réingérer.
- Le rendu de la page, celui du PDF et celui de l'audit utilisent le même Markdown ; seul le PDF n'a pas
  les variables du thème (d'où le repli clair obligatoire).

## Structuration en groupes

La grande majorité des épreuves reste **plate** : une simple suite d'exercices
numérotés, sans `groupes` (champ omis ou `[]`) — c'est le cas par défaut, ne
l'imagine pas comme une case à cocher systématiquement. N'ajoute `groupes` que si la
structure RÉELLE d'une épreuve de ce niveau/cette matière impose des parties ou
sections distinctes, par exemple :

- une épreuve combinée à plusieurs disciplines (ex. BAC Physique-Chimie avec une
  Partie Physique et une Partie Chimie) ;
- une épreuve de Français avec ses sections canoniques (Étude de texte / Essai,
  Résumé et discussion...) ;
- une épreuve dont le `materiel_reference` fourni montre elle-même des Parties/
  sections numérotées.

N'invente jamais un découpage en groupes pour une matière/un niveau dont les épreuves
réelles restent structurellement plates (la plupart des épreuves de Mathématiques,
Physique-Chimie ou SVT non combinées, par exemple) — un `sections_plan`/`exercices`
groupé sans justification structurelle réelle dégrade la lisibilité au lieu de
l'améliorer.

**Cohérence blueprint → épreuve, à l'identique.** `sections_plan[].groupes` (mode
`blueprint`) et `exercices[].groupes` (mode `epreuve`) portent exactement la même
information à deux moments du pipeline — la seconde doit toujours reprendre la
première verbatim pour la section correspondante, jamais reformulée, réordonnée ou
oubliée. Une pile de plusieurs repères (ex. `["Partie II", "Exercice de synthèse"]`)
va du plus large au plus spécifique, dans l'ordre où un élève lirait le sommaire d'une
vraie épreuve papier.

**`numero_exercice` reste global, jamais renuméroté par groupe.** Contrairement à
`catalog.Exercise` côté épreuves réelles (qui reconstruit une numérotation locale par
groupe côté frontend, parce que le texte source répète parfois "Exercice 1" dans
chaque Partie), une épreuve inédite n'a pas ce problème : c'est toi qui assignes
`numero_exercice`, donc assigne-le simplement de façon continue sur l'épreuve ENTIÈRE
("1", "2", "3", "4"...) même si "1"-"2" appartiennent à une Partie et "3"-"4" à une
autre — ne repars jamais à "1" au passage d'un groupe à l'autre.

**Pas de sommaire cliquable.** Le lecteur de tentative affiche `groupes` comme un
simple repère textuel au-dessus du numéro d'exercice quand il change (voir
`InediteTentativePage.tsx`), jamais comme un sommaire de navigation (contrairement à
`EpreuveSommaire.tsx` côté épreuves classiques) : un élève en mode examen chronométré
ne doit pas pouvoir sauter en avant dans l'épreuve. Rien à faire de ton côté pour
ça — c'est une contrainte du lecteur, pas du contenu que tu produis.

**Sous-partie DANS un exercice : `groupe_local`, jamais un doublon dans
`enonce_intro_markdown`.** `groupes` scinde l'épreuve en Parties/sections qui
regroupent PLUSIEURS exercices entiers. Si au contraire un seul exercice ("Exercice
1") se scinde LUI-MÊME en sous-parties successives — chacune avec ses propres
questions, ex. "Vérification des savoirs" puis "Vérification des savoir-faire" — c'est
`questions[].groupe_local` qu'il faut renseigner, un repère par question, jamais un
texte empilé une seule fois en tête de l'exercice (voir sa description dans le contrat
de sortie ci-dessus, et l'exemple qui l'accompagne).

## Le principe non négociable : jamais une paraphrase

C'est la raison d'être de ce skill, pas un détail parmi d'autres. On te donne du
`materiel_reference` (de vrais exercices déjà publiés sur edukora, du même
pays/matière/cursus) — sers-t'en pour calibrer le NIVEAU, le STYLE rédactionnel, le
FORMAT de barème, la LONGUEUR typique d'un énoncé. Ne t'en sers jamais pour recycler
un contexte, un jeu de nombres, un nom de personnage, une situation concrète. Une
épreuve inédite générée à partir d'un exercice sur "une urne contenant 5 boules
rouges et 3 boules noires" ne doit jamais redevenir un exercice sur une urne — change
de scénario (un jeu de cartes, un tirage de loterie, un contrôle qualité en usine),
même si la technique mathématique testée (probabilités conditionnelles) reste la
même. Le test à te poser avant de finaliser chaque question : *si quelqu'un
connaissait par cœur l'exercice de référence, cette question inédite lui donnerait-
elle un avantage déloyal ?* Si la réponse est oui même partiellement, change encore.

Pour les matières argumentatives (philosophie, histoire-géo, français dissertation) :
la même règle s'applique au SUJET lui-même (jamais le même intitulé de dissertation
reformulé), mais les citations d'auteurs/œuvres/faits réels et exacts restent
attendues et légitimes — une dissertation de philosophie qui cite Kant n'est pas une
violation de cette règle, c'est le travail normal de la matière.

## Niveau d'exigence du corrigé

Le corrigé doit atteindre le même niveau que `correction-experte` : une explication de
la MÉTHODE, pas seulement le résultat — quelqu'un qui lit le corrigé sans avoir vu la
question doit comprendre le raisonnement, pas juste la réponse finale. Ce n'est pas
parce que le contenu est généré (et non transcrit) que l'exigence pédagogique baisse.

Deux familles de vérification avant de finaliser un corrigé, selon la matière :

- **Matières calculatoires/factuelles** (maths, physique-chimie, SVT...) :
  re-résous le calcul de façon indépendante avant d'écrire le corrigé — ne fais
  jamais confiance à un résultat "qui a l'air juste" sans l'avoir recalculé toi-même.
- **Matières argumentatives** (philosophie, français, histoire-géo, SES...) : vérifie
  la structure attendue du genre (thèse/antithèse/synthèse pour une dissertation,
  etc.) et l'exactitude factuelle de toute référence citée (dates, auteurs, œuvres) —
  pas de recalcul à faire, mais aucune approximation non plus sur les faits avancés.

## Style rédactionnel — éliminer les marqueurs IA

Le contenu inédite est vendu au même titre que le contenu classique - et y est
arguably plus exposé : rien ne l'ancre à un vrai sujet transcrit qui rassurerait sur
son sérieux. Un énoncé ou un corrigé qui « sonne IA » nuit à la crédibilité pédagogique
exactement comme pour `correction-experte` ; les mêmes règles s'appliquent ici, sans
exception, à chaque énoncé et chaque corrigé produits.

**Formules à proscrire** - les supprimer et reformuler en affirmation directe :
"Il est à noter que", "Il convient de souligner que", "Force est de constater que",
"Notons que", "Rappelons que", "En effet," en début de phrase (sauf si réellement
explicative d'une cause).

**Connecteurs mécaniques en série** - éviter l'enchaînement systématique "De plus,…
Par ailleurs,… En outre,… Ainsi,…" ; "Par conséquent" et "Donc" ne coexistent pas dans
le même paragraphe pour la même relation.

**Formules de conclusion mécanique** - "En définitive,", "En somme,", "Pour
conclure," : écrire directement la conclusion, le bloc Piège/Conseil signe déjà
naturellement la fin.

**Tiret cadratin (caractère Unicode em dash) proscrit** - jamais, y compris pour une
incise grammaticale. Utiliser un tiret simple ("-") ou reformuler.

**Gras excessif et listes uniformes** - ne grasser que les formules-clés et noms de
théorèmes ; une liste où toutes les entrées ont exactement la même longueur trahit
l'IA, varier la formulation ou intégrer dans le corps du texte en dessous de trois
éléments.

**Anaphores mécaniques** - éviter que deux paragraphes consécutifs commencent par le
même syntagme ("Cette propriété… / Cette notion… / Cette méthode…").

**Registre** : dans le corps du corrigé, écrire comme un professeur qui pense à voix
haute - direct, sans hedging superflu ("On obtient", "Donc", jamais "On peut observer
que"). Dans les blocs Piège et Conseil, tutoiement et ton direct.

**Test final avant livraison** : un correcteur du MINESEC qui lirait ceci à voix haute
reconnaîtrait-il immédiatement la plume d'un enseignant expérimenté ? Si une phrase
sonne artificielle ou redondante, la reformuler.

## Template obligatoire pour chaque corrigé (mode `epreuve`)

Chaque `corrige_markdown` de question doit suivre EXACTEMENT le même gabarit que
`correction-experte` (même exigence de marque, même détection côté plateforme) :

1. **Rappel de la méthode/notion mobilisée** (2-4 lignes) - le principe général avant
   l'application au cas précis
2. **Corrigé détaillé étape par étape** - chaque étape justifiée, pas seulement
   calculée ; aucune étape cachée, formulations complètes, pas de raccourcis
   elliptiques
3. **Piège à éviter** (uniquement si pertinent pour cette question) - l'erreur
   typiquement commise sur ce type de question
4. **Conseil** (uniquement si pertinent) - gain de temps, formulation qui rapporte des
   points, méthode de vérification rapide - toujours au tutoiement, adressé à l'élève

Ne pas forcer les points 3 et 4 s'ils n'apportent rien de réel sur une question
donnée - un piège ou conseil inventé pour remplir le template dégrade la qualité
perçue plus qu'il ne l'améliore.

**Intitulé fixe** : toujours utiliser exactement le mot "Conseil" pour le bloc 4
(jamais "Conseil de prof", "Astuce" ou variante) - cohérence de marque sur l'ensemble
du contenu de la plateforme, classique et inédite confondues.

**Format Markdown imposé, sans exception** - les blocs 1, 3 et 4 commencent
systématiquement par un titre de niveau 3, intitulé exact et rien d'autre sur la
ligne de titre :

```
### Rappel de méthode
<texte du rappel>

### Piège à éviter
<texte du piège>

### Conseil
<texte du conseil>
```

Ne jamais utiliser une autre forme (ni "**Rappel de méthode.**", ni liste à puces, ni
gras seul) : la plateforme détecte ces trois blocs uniquement à partir de ce titre de
niveau 3 exact pour les mettre en valeur visuellement (encadré coloré) dans le corrigé
publié - un format différent fait perdre cette mise en valeur silencieusement.

**Le bloc `### Rappel de méthode` reste UN SEUL paragraphe, sans ligne blanche à
l'intérieur** : la plateforme en détecte la fin à la première ligne blanche après le
titre. Le principe général (point 1) et son application chiffrée au cas précis (point 2)
sont deux paragraphes toujours distincts : le second commence directement après le
Rappel, sans titre propre, jamais sous le même titre.

**Le contenu sous `### Rappel de méthode` est une règle générale, jamais un extrait de la
réponse** : le principe, la méthode, la définition ou le théorème mobilisé, formulé pour
rester vrai sur n'importe quel exercice du même type. Une phrase qui cesserait d'être
vraie si les données de cette question changeaient (valeurs de l'énoncé, résultat
chiffré obtenu ici) va dans le corrigé détaillé, jamais dans le Rappel.

**La réponse à la question n'est JAMAIS placée sous `### Rappel de méthode`, y compris
pour « Définir… », « Donner le rôle de… », « Citer… »** : la réponse EST alors une
définition ou une liste, et c'est précisément là qu'on est tenté de la ranger dans le
Rappel parce qu'elle « ressemble » à une règle. Elle va dans le corps du corrigé, en
clair, sans titre ; le Rappel dit COMMENT répondre à ce type de question, pas CE QUE
l'on répond. Exemple : « Définir : système d'exploitation » → corps : « Un **système
d'exploitation** est le logiciel de base qui… » ; Rappel : « Pour définir un système
d'exploitation, indique sa nature, son rôle et cite un ou deux exemples. »

**Un corrigé n'est jamais composé uniquement de blocs `### Rappel de méthode`** : chaque
question a au moins un paragraphe de réponse en clair, hors de tout Rappel. Test de
contrôle avant de livrer chaque question : si on supprime tous les blocs Rappel du
`corrige_markdown`, il doit rester la réponse complète ; si le Rappel contient des
valeurs propres à l'énoncé, c'est une réponse déguisée, pas un rappel. La plateforme
l'applique côté tunnel de validation (ALERTE sur un Rappel déclaratif), mais c'est trop
tard : le contenu est déjà ingéré.

**`rappels_de_methode[].contenu_markdown`** (cours en lot) est la copie intégrale et
littérale du paragraphe du Rappel, jamais un extrait tronqué.

## Composition LaTeX — pièges de rendu à vérifier avant de livrer

Le rendu Markdown+KaTeX de la plateforme est le même pour le contenu inédite que pour
le contenu classique (voir le skill `audit-qualite-rendu`, qui couvre explicitement
`inedit.EpreuveInedite`/`QuestionInedite`). Générer un énoncé/corrigé neuf n'immunise
pas contre ces erreurs de syntaxe : elles ne provoquent aucune erreur de validation
JSON et ne sautent pas aux yeux en relisant le texte brut - seul un rendu KaTeX réel
les révèle, ce qui n'arrive qu'une fois le contenu déjà publié et visible d'un élève.

1. **Séparateur de ligne dans une matrice/un système** (`\begin{cases}`, `pmatrix`,
   `bmatrix`, `vmatrix`, `matrix`, `array`) : toujours deux backslashes (`\\`) entre
   deux lignes, jamais un seul.
   ```
   Correct   : \begin{cases} 2a+b=0 \\ -a+b-3c=0 \end{cases}
   Incorrect : \begin{cases} 2a+b=0 \-a+b-3c=0 \end{cases}
   ```
2. **`\hline` jamais collé au token qui suit**, dans un tableau de variations :
   toujours un espace après (`\hline x`, jamais `\hlinex`) - sinon TeX lit un mot de
   commande inconnu. Cet espace est toujours invisible au rendu final.
3. **Spécificateur de colonnes d'un `\begin{array}{...}`** : avant de le fixer
   (`{c|cccc}`, etc.), compter le nombre RÉEL de colonnes utilisées par la ligne la
   plus chargée - un tableau de variations à plusieurs points de rupture ajoute une
   colonne de valeur ET une colonne de flèche/signe par point de rupture.
4. **Formule display multi-lignes (`$$...$$`)** : toujours isoler les délimiteurs
   `$$` seuls sur leur propre ligne, avec une ligne vide avant le `$$` ouvrant et
   après le `$$` fermant - jamais de texte collé sur la même ligne qu'un délimiteur.
   Les formules display tenant sur une seule ligne (`$$x=1$$`) ne sont pas concernées.

**Vérification obligatoire avant de finaliser le JSON** : pour chaque bloc contenant
`\begin{cases}`/`pmatrix`/`bmatrix`/`vmatrix`/`matrix`/`array}`, recompter à la main
les séparateurs `\\` entre les lignes, les occurrences de `\hline`, et - pour un
`array` - le nombre de colonnes déclarées contre le nombre réellement utilisé par la
ligne la plus chargée.

## `themes` par question — ne l'oublie jamais

Chaque question devrait porter au moins une entrée dans `themes`, reprenant l'un des
intitulés de `Blueprint.competences`. Sans ça, le score de couverture pédagogique
calculé automatiquement à l'ingestion (`score_qualite`) tombe à zéro pour toute
question non taguée — un score artificiellement mauvais pour un contenu par ailleurs
correct, uniquement parce que ce champ a été oublié. Si une question teste
légitimement une compétence transversale non listée dans le blueprint, dis-le à
l'utilisateur plutôt que d'inventer une entrée `themes` qui n'existe pas côté
référentiel.

## Auto-vérification avant de finaliser (les deux modes)

Avant de considérer une génération terminée, repasse sur ce qui suit — c'est ce qui
sépare un premier jet d'un contenu publiable :

1. Tous les champs obligatoires du contrat JSON sont présents et correctement typés
   (voir les deux contrats plus haut).
2. Aucun texte (énoncé, contexte, nom, jeu de données) recopié ou trop proche du
   `materiel_reference` fourni — relis chaque énoncé généré côte à côte avec le
   matériel de référence correspondant.
3. Chaque QCM a une `reponse_correcte` qui correspond effectivement à l'une des
   lettres de `choix`, et les distracteurs sont plausibles (pas absurdes au point
   d'être devinables sans réfléchir).
4. Chaque énoncé est autonome — aucune référence à une figure/un tableau qui
   n'existe pas réellement dans ce que tu produis (`"la courbe ci-dessus"` sans
   fournir cette courbe est un défaut déjà rencontré ailleurs dans ce dépôt, voir
   `catalog.models.Question.references_missing_figure` — le même piège s'applique ici).
   Une figure que tu mentionnes existe dans le JSON, en SVG, et a été regardée (point 11).
5. `themes` renseigné sur les questions qui ciblent une compétence du blueprint.
6. (Mode épreuve) La structure produite correspond à `sections_plan` du blueprint —
   nombre d'exercices, répartition des points, compétences par section.
6bis. (Mode épreuve) Barème exact : pour CHAQUE exercice, la somme des `points` des
   questions égale `exercices[].points` (recompte-la à la main, exercice par exercice),
   chaque question ouverte a une grille `criteres_notation` dont la somme égale ses
   `points`, aucune QCM n'a de grille, et tout barème annoncé dans un énoncé (`(1 pt)`)
   est repris tel quel dans `points`.
7. (Mode épreuve) Chaque `numero` de question est non vide et cohérent avec sa
   position réelle dans l'exercice (numérotation continue 1/2/3 ou a/b/c, jamais de
   trou ni de doublon) - c'est ce `numero`, et lui seul, qui est affiché à l'élève
   au-dessus de chaque question sur la plateforme, jamais recalculé côté frontend.
8. (SVT uniquement) Au moins deux exercices portent un support à exploiter dans
   `enonce_intro_markdown` : texte, tableau, ou figure SVG calculée (graphique, arbre
   généalogique, schéma de croisement) dont les données figurent aussi en texte ou en tableau -
   voir « Supports à exploiter (SVT) » plus haut et « Figures et tracés ».
9. Chaque bloc `\begin{cases}`/`pmatrix`/`bmatrix`/`vmatrix`/`matrix`/`array}` a été
   recompté à la main (séparateurs `\\`, espace après `\hline`, colonnes déclarées vs
   réellement utilisées) - voir « Composition LaTeX » plus haut.
10. (Si `groupes` utilisé) Chaque `exercices[].groupes` reprend EXACTEMENT, dans le
    même ordre, la pile déclarée par `sections_plan[].groupes` du blueprint pour la
    section correspondante - aucune section groupée au blueprint ne doit se retrouver
    plate en mode épreuve, et inversement. `numero_exercice` reste une numérotation
    continue sur l'épreuve entière, jamais réinitialisée à chaque nouveau groupe -
    voir « Structuration en groupes » plus haut.
11. (Si l'épreuve porte des figures) `verifier_figures.py` sort sans erreur ; chaque figure a été
    rendue en PNG (`rendre_figures.py`) et REGARDÉE : entière, lisible, rien ne se recouvre, aucun
    lien ne traverse une forme, valeurs identiques à l'énoncé et au corrigé (recalculées) ; le
    corrigé décrit le tracé pas à pas en plus de la figure ; aucun tracé attendu n'est dans l'énoncé ;
    les `criteres_notation` d'un tracé sont observables sur la copie ; la figure ne contient ni guillemet
    droit, ni « », ni `$`, ni couleur en dur - voir « Figures et tracés » plus haut.

## Génération des cours en lot

Chaque bloc `### Rappel de méthode` produit dans un corrigé de mode `epreuve` donne
lieu à un objet JSON "cours" distinct, un fichier par rappel - jamais fusionné avec le
JSON de l'épreuve.

**Catalogue de titres existants - à demander si absent.** Avant de générer un lot de
cours, demander la liste des titres de `Cours` déjà publiés pour la matière/le pays
traités (tous origines confondues, classique ET inédite - un `Cours` publié ne
distingue pas les deux). Si le nom de la compétence correspond exactement (insensible
à la casse) à un titre existant : n'émettre que le squelette minimal (`cours_id`
nouveau, `meta.titre` copié à l'identique, `source.rappel_id`, `sections: []`) -
l'ingestion rattache alors ce rappel au `Cours` existant sans dupliquer. En l'absence
de correspondance, ou si aucun catalogue n'est disponible : générer le cours complet
(7 sections, même structure et même niveau d'exigence que le mode cours de
`correction-experte` - comprendre/mémoriser/faire soi-même, aucune étape masquée dans
l'exemple résolu).

**Champ `type` explicite, obligatoire** - contrairement au JSON cours de
`correction-experte` (détecté côté edukora par la présence de la clé `sections`),
tout objet JSON "cours" produit ici porte `"type": "cours"`, même logique déjà
appliquée à `"blueprint"`/`"epreuve"` dans ce skill : un champ explicite plutôt que
deviné depuis la forme du JSON, pour un tri fiable.

**Un rappel par cours en sortie** - jamais un cours partagé explicitement par
plusieurs rappels dans le JSON : ce skill n'a qu'un mode automatisé, jamais de mode
interactif où plusieurs rappels fournis ensemble donneraient lieu à un seul cours.

**Nommage** : `<external_id_de_l_epreuve>_cours_<competence_slug>.json`, dans le même
dossier `ingest/_inedit/<code_pays>/` que le fichier épreuve source. Le
`competence_slug` est dérivé du champ `competence` du rappel (minuscules, accents
supprimés, espaces en tirets).

**Traçabilité obligatoire** : `source.rappel_id` doit être l'`id` EXACT d'un rappel
réellement présent dans `questions[].rappels_de_methode` du JSON épreuve déjà livré -
jamais une valeur reconstruite depuis la convention de nommage `rdi-...`.

### Format de sortie JSON

```json
{
  "type": "cours",
  "cours_id": "cours-<competence_slug>-<niveau>-<serie>",
  "meta": {
    "titre": "Intitulé du cours",
    "matiere": "mathematiques",
    "pays": "code ISO du pays traité, minuscule - jamais null",
    "serie": "code exact de la série visée, ou null si le cours s'applique à toutes les séries",
    "sous_theme": "sous-domaine du programme",
    "duree_estimee_min": 25,
    "tags": ["Convergence d'une suite numérique"]
  },
  "source": {
    "rappel_id": "rdi-ep-cm-maths-bac-c-3-2026-s1-ex1-q1-0"
  },
  "sections": [
    {"type": "accroche", "contenu_markdown": "..."},
    {"type": "prerequis", "items": ["..."]},
    {"type": "regle", "titre": "...", "contenu_markdown": "...", "formule_principale": "..."},
    {"type": "exemple_resolu", "enonce_markdown": "...", "etapes": ["..."], "conclusion_markdown": "..."},
    {"type": "erreurs_classiques", "items": ["..."]},
    {"type": "exercices_application", "items": ["..."]},
    {"type": "synthese", "items_markdown": ["..."]}
  ]
}
```

Champs obligatoires : `cours_id`, `meta.titre`, `meta.matiere`, `source.rappel_id`.
`sections: []` uniquement pour un squelette de doublon (voir ci-dessus) - sinon les 7
sections complètes, mêmes 7 types que le mode cours de `correction-experte`
(accroche/prerequis/regle/exemple_resolu/erreurs_classiques/exercices_application/synthese),
même niveau d'exigence.

**Convention de nommage des `id` de rappel** : `rdi-<external_id_epreuve>-ex<numero_
exercice>-q<numero>-<index>` - préfixe `rdi-` (pas `rdm-`, réservé à
`correction-experte`) pour rester visuellement distinct dans les logs d'ingestion,
même si l'unicité en base est de toute façon indépendante par table.

## Convention de nommage (`external_id`)

- Blueprint : `bp-<pays>-<matiere_courte>-<examen>-<serie>-<sequence>` — ex.
  `bp-cm-maths-bac-c-3` (le 3ᵉ blueprint Maths BAC C proposé pour le Cameroun). Pour un
  blueprint commun à plusieurs séries (voir `cursus` plus haut), `<serie>` devient la
  combinaison, ex. `bp-cm-maths-bac-c-e-2`.
  `<sequence>` : incrémente à partir de ce que tu sais déjà exister (demande à
  l'utilisateur s'il n'y a pas moyen de vérifier).
- Épreuve : `ep-<external_id du blueprint>-<annee>-s<n>` — ex.
  `ep-cm-maths-bac-c-3-2026-s1` (1ʳᵉ génération sur ce blueprint, en 2026). Un même
  blueprint validé peut être régénéré plusieurs fois (ex. "examen blanc
  hebdomadaire") — c'est `<n>` qui distingue les générations successives, jamais le
  `blueprint_external_id` lui-même qui change.

Ces identifiants sont la clé d'idempotence côté ingestion edukora (voir
`inedit.ingestion.ingest_blueprint`/`ingest_epreuve_inedite`) : un identifiant déjà
utilisé n'écrase jamais un blueprint/une épreuve existants, il est simplement ignoré à
l'ingestion. Ne réutilise jamais un identifiant par accident.

## Convention de nommage du `titre`

Format unique, adopté le 2026-08-23, valable pour le `titre` du Blueprint ET de
l'EpreuveInedite qui en découle (même chaîne dans les deux - la génération n'y ajoute
rien) :

`<Matière> <Niveau/Série(s)> – Épreuve inédite n°<N>`

**Jamais « Épreuve blanche » dans le titre** (changement du 2026-10-05) : ce terme désigne
dans le catalogue les vrais examens blancs d'établissement (origine « Examen blanc »).
L'ingestion réécrit d'ailleurs « Épreuve blanche » en « Épreuve inédite » (`_titre_inedite`
dans `inedit/ingestion.py`) et la migration 0018 a fait de même pour les épreuves déjà en
base : un titre généré en « Épreuve blanche » ne serait jamais celui qui est stocké, et le
JSON source ne correspondrait plus à la base. Écris directement « Épreuve inédite ». (Ce
changement ne touche que le `titre` ; la demande de l'utilisateur peut, elle, dire
« épreuve blanche », voir la description du skill.)

(tiret demi-cadratin « – », pas le tiret cadratin proscrit ailleurs dans ce document -
ici il sépare deux segments du titre, ce n'est pas une incise grammaticale).

- `<Matière>` : nom en toutes lettres, majuscule initiale (`Mathématiques`, `Anglais`,
  `Chimie`, `Physique`, `SVT`...) - jamais la forme minuscule du champ JSON `matiere`.
- `<Niveau/Série(s)>` reflète EXACTEMENT le `cursus` déclaré, jamais plus ni moins :
  - Une seule série dans `cursus` → `Terminale <Série>` (ex. `Terminale A`),
    `Probatoire <Série>` (ex. `Probatoire A`), ou `BEPC` seul (le BEPC n'a pas de
    série).
  - Plusieurs séries dans `cursus` (voir plus haut : « une EpreuveInedite peut être
    commune à plusieurs séries ») → `BAC <Série1> et <Série2>` (ex. `BAC D et TI`,
    `BAC C et E`) - jamais `Terminale` dans ce cas, le préfixe devient `BAC`. Toujours
    le connecteur « et », jamais « & » ni « / ».
  - N'annonce jamais dans le titre une série absente de `cursus` : un titre qui
    promet un accès que l'épreuve n'a pas est pire qu'un titre trop sobre. Si une
    épreuve à série unique semble mériter un titre multi-séries (le programme d'une
    autre série est identique), dis-le à l'utilisateur et élargis `cursus` en
    conséquence plutôt que de me contenter d'élargir le titre seul.
- `n°<N>` : distingue les épreuves qui partagent le même `<Matière>
  <Niveau/Série(s)>` - jamais « Session <N> ». Ce compteur est indépendant du
  `<sequence>`/`<n>` de l'`external_id` (deux Blueprint différents peuvent chacun
  porter `-1` dans leur `external_id` tout en affichant `n°1` et `n°2` si leurs
  `cursus` se recouvrent, comme Maths BAC D et Maths BAC TI). Avant d'assigner `<N>`,
  vérifie les `titre` déjà utilisés pour ce même `<Matière> <Niveau/Série(s)>`
  (demande à l'utilisateur si tu ne peux pas interroger la base) et incrémente à
  partir de là - ne réutilise jamais un `<N>` déjà pris, même sur un Blueprint
  différent.

Anciennes formes abandonnées : « Épreuve blanche de Mathématiques — Terminale C —
Session 1 » (matière en tête et « Session N », abandonnée le 2026-08-23) et
« … – Épreuve blanche n°N » (abandonnée le 2026-10-05, voir plus haut) : ne les
reproduis plus pour une nouvelle génération, y compris par imitation d'un ancien
`materiel_reference` qui les porterait encore.

## Où livrer le résultat

Écris chaque objet JSON dans son propre fichier, sous
`ingest/_inedit/<code_pays_minuscule>/`, prêt pour `manage.py ingest_inedit_content`
côté edukora (par exemple `ingest/_inedit/cm/bp-cm-maths-bac-c-3.json`). Si tu ne sais
pas où se trouve la racine `ingest/` du dépôt sur lequel tu travailles, demande plutôt
que de deviner un chemin.

Les figures sont dans les JSON eux-mêmes (aucun fichier image à livrer). Les trois scripts du skill se
lancent depuis le dossier du skill : `scripts/figures_svg.py` (bibliothèque), `scripts/verifier_figures.py`
et `scripts/rendre_figures.py` (contrôles), `scripts/demo_figures.py` (planche d'exemples).

## Tunnel de validation - dernière étape obligatoire de tout round d'ingestion

Un round n'est JAMAIS déclaré terminé sur la seule foi de « l'ingestion n'a pas échoué » : les écarts constatés jusqu'ici (rendu KaTeX cassé, questions sans thème, quasi-doublons de thèmes, QCM incohérent) passaient l'ingestion sans erreur et n'apparaissaient qu'après coup, en obligeant à lancer des campagnes de rattrapage. Après l'ingestion, lancer depuis la racine du dépôt (`D:\edukora`) :

```bash
bash scripts/tunnel_validation.sh <since> [--strict]
```

`<since>` = durée depuis le début du round (`2h`, `90m`, `1d`) ou datetime ISO : le tunnel ne valide que le contenu créé ou modifié depuis cet instant. Il enchaîne (1) la structure - Question sans thème, QCM incohérent (BLOQUANT) ; (2) le vocabulaire de thèmes - quasi-doublons de Tag, thèmes partagés entre matières (ALERTE) ; (3) la couverture - quiz/cours manquants pour les thèmes touchés (INFO) ; (4) le rendu - le VRAI moteur KaTeX/remark sur ce périmètre.

- La sortie `TUNNEL VALIDÉ` (code 0) est exigée avant de conclure ; la citer dans le rapport final.
- Ce que le tunnel NE couvre PAS pour une épreuve inédite : ses portes de structure ne regardent que le contenu des épreuves classiques (le « Périmètre » annonce 0 Question), et sa porte de rendu contrôle le Markdown et le KaTeX, pas le dessin d'une figure. Pour une épreuve inédite, la structure se garantit par l'ingestion (barème exact refusé sinon), les thèmes par le contrôle contre la table `Tag` AVANT d'ingérer, les figures par `verifier_figures.py` et le contrôle visuel.
- BLOQUANT ou échec de rendu : corriger la donnée (JSON source) puis réingérer. Si la même anomalie revient d'un round à l'autre, la signaler à l'utilisateur comme défaut de plateforme (`catalog/rendering.py`, `catalog/ingestion_repairs.py`) au lieu de la repatcher à la main.
- ALERTE de quasi-doublon de Tag : soit un thème équivalent existe déjà (reprendre sa forme exacte dans le JSON et réingérer), soit les deux sont réellement distincts, et le rapport le dit explicitement. Jamais de fusion en masse sans l'utilisateur.
- Avant de fournir des `themes`, quand la base est accessible (`docker exec edukora-backend-1`), chercher la forme existante du thème (accents, singulier/pluriel, casse) plutôt que d'en inventer une variante : c'est la source des quasi-doublons.
- Le rattachement `savoir_officiel` n'entre PAS dans ce tunnel (mis en standby le 2026-09-18, l'organisation se fait par thèmes) : un `null` n'est pas un défaut à corriger.
- Environnement sans accès à docker/à la base (tâche planifiée Cowork) : le dire dans le rapport - le round reste NON validé tant que le tunnel n'a pas tourné depuis Claude Code.
- Le code du tunnel vit dans l'image du backend (pas de bind-mount) : si `valider_ingestion` est « Unknown command », reconstruire (`docker compose build backend && docker compose up -d backend`).

## Le caractère `$` hors formule doit toujours être protégé

`$` est le délimiteur des formules LaTeX : un `$` littéral laissé nu (variable PHP `$nom`, référence de tableur `$B$2`, symbole monétaire) est apparié par la plateforme au `$` suivant, et tout le texte compris entre les deux s'affiche comme une formule déformée ou lève une erreur KaTeX. Dans `enonce_markdown` et `corrige_markdown` : tout nom de variable, code ou formule de tableur contenant un `$` va dans un span de code entre backticks (`` `$nom` ``, `` `=RANG(B2;$B$2:$B$5;0)` ``) ; un extrait de code de plusieurs lignes est un bloc fencé (```` ```php ... ``` ````), jamais des lignes de code nues ; le symbole isolé dans une phrase s'écrit `` `$` `` ou `\$`. Relire chaque `$` du texte produit avant de livrer : soit dans un span/bloc de code, soit délimiteur d'une vraie formule, soit échappé.
