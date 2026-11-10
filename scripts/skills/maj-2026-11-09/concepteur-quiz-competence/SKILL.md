---
name: concepteur-quiz-competence
description: "Génère des items de quiz d'auto-évaluation (CompetenceItem) pour edukora - questions entièrement autonomes, une par compétence pédagogique, jamais un extrait d'épreuve. Couvre toutes les matières de correction-experte (maths, physique-chimie, SVT, français, philosophie, histoire-géo, anglais, économie/droit). Produit aussi les courbes et figures qu'un corrigé exige (PNG joint). À utiliser dès que l'utilisateur demande de peupler/alimenter le Mode Quiz, de générer des questions d'auto-évaluation ou de test de niveau, une banque d'items par compétence/thème, ou mentionne CompetenceItem - même sans dire \"génère un quiz\" (ex. \"il faut du contenu pour le quiz sur les dérivées\", \"peuple le quiz de Terminale C en probabilités\", \"j'ai besoin de 20 questions autonomes sur la compétence X\"). Différent de correction-experte (qui transcrit fidèlement une épreuve réelle) : ce skill invente des énoncés neufs à partir d'exercices déjà corrigés et validés, jamais une copie."
---

# Concepteur de quiz par compétence

Tu conçois des questions de quiz d'auto-évaluation pour edukora, une plateforme de
préparation aux examens d'Afrique francophone (BEPC/Probatoire/BAC - Cameroun,
Sénégal, Côte d'Ivoire, Bénin, et au-delà), toutes matières confondues - maths,
sciences, langues, lettres et sciences humaines. Chaque question que tu produis
devient un `CompetenceItem` : un objet servi seul dans une session de quiz - jamais
accompagné du reste d'un exercice, jamais lu à côté d'une question voisine.

## Le problème que ce skill résout

edukora servait auparavant des sous-questions extraites d'épreuves réelles
(`catalog.Question`, produites par `correction-experte`) directement dans le quiz.
Ça semblait raisonnable - chaque sous-question a son propre énoncé et son propre
corrigé - mais une sous-question d'épreuve est écrite pour être lue *dans le récit
complet de son exercice*, pas seule : un préambule de "Partie B" ne vit souvent que
dans le texte de la première sous-question de cette partie, et "d'après le résultat
de la question précédente" est une tournure normale à l'intérieur d'une épreuve,
insoluble une fois isolée. Ce n'est pas propre aux maths : une question de
dissertation qui renvoie au texte cité "dans le document ci-dessus", ou une question
d'histoire qui suppose acquise la date établie à la question 1, ont exactement le
même défaut. Aucune quantité de patch après-coup ne répare ça complètement, parce que
le problème vient du matériau lui-même : un extrait reste un extrait.

Ta mission est donc structurellement différente de celle de `correction-experte`.
Ce skill-là doit rester fidèle au texte source - jamais inventer. Toi, c'est
l'inverse : jamais copier, toujours inventer un énoncé neuf qui teste la même
compétence. Ne mélange jamais les deux disciplines - si une phrase de ton énoncé
pourrait être confondue avec une phrase d'un exercice source, tu as échoué.

## Toutes les matières de correction-experte, avec ses propres conventions

Ce skill s'applique à n'importe quelle matière que `correction-experte` traite déjà :
mathématiques, physique-chimie, SVT, français, philosophie, histoire-géographie,
anglais, économie/droit (SES), et au-delà. Pour le registre, le niveau de langue, la
structure attendue par matière (dissertation en 2-3 parties, explication de texte,
plan dialectique thèse/antithèse/synthèse, démarche loi → application numérique →
résultat avec unité, etc.), applique exactement les mêmes conventions que
`correction-experte` (sa section "Spécificités pédagogiques par matière") - ne les
réinvente pas, elles sont déjà calibrées sur les attentes réelles des correcteurs.
Ce skill-ci n'ajoute que ses propres exigences, par-dessus : autonomie totale,
non-copie, variété du lot - détaillées plus bas.

## Musique et Travail manuel (matières du Probatoire A, ajoutées le 2026-11-09)

Codes `MUSIQUE` et `TRAVAIL_MANUEL`, famille MIXTE comme l'EPS. Le tunnel exige pourtant au moins 6 QCM par thème (`MIN_QCM_PAR_THEME` dans `backend/catalog/tunnel.py`, le code fait foi sur ce tableau) : dans ces deux matières, fais donc les 6 items de la compétence en QCM.
- **Musique** : noms de notes (notation française), degrés de la gamme (tonique, sus-tonique, médiante, sous-dominante, dominante, sus-dominante, sensible), séries de quatre notes (tétracordes), clés, valeurs de durée, instruments, histoire de la musique. Un item qui dépend d'une portée décrit la position de chaque note en toutes lettres (« sur la deuxième ligne de la clé de sol ») ou joint un PNG de portée exact ; recalcule les hauteurs avant d'écrire la clé.
- **Travail manuel** : définitions techniques, choix d'un outil ou d'un matériau, ordre des étapes d'un processus, règles de sécurité, calcul simple d'un devis (recalculé par script). Jamais un item qui exige de dessiner ou de réaliser.

## D'où vient ton matériau de référence

Tu ne pars jamais de zéro : on te fournit toujours du matériel de référence -
des `Exercise`/`Question` déjà corrigés et validés par `correction-experte`,
taggés avec la compétence que tu dois couvrir. Ce matériau te sert à comprendre :
- la technique/le raisonnement que la compétence recouvre réellement (pas juste son
  nom - deux exercices tagués "dérivation" peuvent tester des réflexes très différents,
  deux exercices tagués "dissertation philosophique" peuvent porter sur des notions
  du programme très différentes)
- le niveau de difficulté et de registre attendu pour le cursus/la série visée
- le style de formulation propre à la matière (une question de grammaire anglaise ne
  se pose pas comme un exercice de probabilités, un sujet de dissertation ne se pose
  pas comme une question de cours d'histoire)

Ce matériau ne te sert JAMAIS de source à recopier, même partiellement reformulée. Vois-le
comme une leçon apprise, pas comme un brouillon à retoucher.

## Entrée attendue

Une requête de génération, typiquement :

```json
{
  "competence": "Dérivation et étude de fonctions",
  "pays": "cm",
  "matiere": "Mathématiques",
  "cursus": [{"examen": "bac", "serie": "C"}, {"examen": "bac", "serie": "D"}],
  "savoir_officiel": {"classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III"} ou null,
  "cible": {
    "nombre_items": 6,
    "repartition_difficulte": {"FAIBLE": 2, "MOYENNE": 3, "ELEVEE": 1}
  },
  "materiel_reference": [
    {"exercise_id": 512, "enonce_markdown": "...", "corrige_markdown": "..."},
    {"exercise_id": 730, "enonce_markdown": "...", "corrige_markdown": "..."}
  ]
}
```

**`savoir_officiel` dans la requête (nouveau)** : quand présent, recopie-le tel quel
dans `savoir_officiel` de chaque item produit (voir le contrat de sortie plus bas) -
c'est déjà résolu et validé côté sélection, tu n'as rien à en déduire.

**Cas particulier : `competence` décrit un savoir jamais encore couvert.** Si
`materiel_reference` est vide ET que `competence` a la forme "TITRE DU MODULE -
INTITULÉ DU SAVOIR" (au lieu d'un nom de compétence court habituel), c'est que ce
savoir officiel n'a encore strictement aucun contenu côté edukora - il n'existe pas de
`Tag`/matériel à réutiliser. Dans ce cas seulement, choisis toi-même un intitulé de
`theme` court et naturel pour cette compétence (ex. "Nombres complexes : approche
géométrique" plutôt que de recopier le `competence` verbeux tel quel) - l'ingestion
autorise exceptionnellement la création de ce nouveau `theme` parce qu'il est ancré à
`savoir_officiel`, qui a déjà été vérifié comme existant dans le référentiel programme
officiel (voir `catalog.ingestion._resolve_savoir_officiel`). En dehors de ce cas
précis, `theme` doit toujours correspondre à un `Tag` déjà existant, comme avant.

`matiere`/`cursus` suivent exactement le même référentiel que `correction-experte`
(voir sa section "Référentiel") - `matiere` est un libellé français ("Mathématiques",
"Philosophie", "Anglais"...), `examen` vaut `bac`/`probatoire`/`bepc`/`bfem`/`autre`,
`serie` est le code exact du pays traité (`serie` omis ou vide pour un examen sans
série, ex. bepc/bfem). Ne réinvente jamais un code de série ou un nom de matière : si
tu n'es pas certain qu'un couple (matière, série) existe pour ce pays, demande plutôt
que de deviner - une compétence n'est pas limitée aux matières scientifiques,
"Français", "Philosophie", "Histoire", "Géographie", "Anglais" suivent le même
schéma ; seul le contenu de `enonce_markdown`/`corrige_markdown` change de nature (un
sujet de dissertation et son plan corrigé, plutôt qu'un calcul et sa résolution).

**Cas particulier de la Série TI (Probatoire et BAC) : jamais `"Informatique"` comme
`matiere`.** Décision utilisateur du 2026-09-16/17 - en Série TI, l'Informatique se
décompose systématiquement en trois matières distinctes, chacune avec son propre
programme et ses propres compétences : `"Programmation"` (algorithmique, langage C,
programmation web), `"Systèmes d'Information"` (bases de données, UML, modélisation -
c'est aussi le nom actuel de ce qui s'appelait auparavant « Informatique Théorique »)
et `"Réseaux, Internet et Sécurité Informatique"`. Choisis celle qui correspond
réellement à la compétence demandée, jamais `"Informatique"` générique par réflexe -
ce code reste réservé au BEPC et au Bac C/D/E (théorique, hors Série TI). Aucun
module du référentiel programme officiel ne couvre encore ces trois matières pour la
Série TI (seuls des modules Tronc Commun génériques existent) : omets `savoir_officiel`
plutôt que de le rattacher par approximation à un module Informatique générique.

Si l'utilisateur ne précise pas `nombre_items`/`repartition_difficulte`, propose un
lot raisonnable (6 à 10 items, réparti FAIBLE/MOYENNE/ELEVEE dans des proportions
proches de 30/45/25) plutôt que de bloquer sur la clarification - c'est un paramètre
qu'on peut ajuster après coup, contrairement à une erreur factuelle ou mathématique
dans un corrigé.

## Sortie attendue

Un tableau JSON, un objet par item, prêt à être ingéré comme `CompetenceItem` (voir
`quiz.ingestion.ingest_competence_item`) :

```json
[
  {
    "external_id": "cqc-derivation-etude-fonctions-moyenne-0",
    "theme": "Dérivation et étude de fonctions",
    "savoir_officiel": {"classe": "Tle", "serie_label": "C-E", "module_numero": "25", "savoir_numero": "III"},
    "matiere": "Mathématiques",
    "cursus": [{"examen": "bac", "serie": "C"}, {"examen": "bac", "serie": "D"}],
    "enonce_markdown": "Soit $g$ la fonction définie sur $\\mathbb{R}$ par $g(x) = x^3 - 3x + 1$...",
    "corrige_markdown": "### Rappel de méthode\n\nPour étudier les variations d'une fonction polynôme, on calcule sa dérivée $g'$, on détermine son signe, puis on en déduit le sens de variation de $g$.\n\n### Corrigé\n\n$g'(x) = 3x^2 - 3 = 3(x-1)(x+1)$...",
    "difficulte_estimee": "MOYENNE",
    "type_reponse": "OUVERTE",
    "choix": [],
    "reponse_correcte": "",
    "source_exercises": [512],
    "figures": []
  }
]
```

`figures` : `[]` ou champ omis quand l'item n'a aucune figure ; sinon une entrée par
image produite (schéma complet dans « Figures et tracés dans les items »).

Règles de champs :
- `external_id` : identifiant déterministe et unique dans le lot, jamais vide en mode
  automatisation - sert de clé d'idempotence à l'ingestion (relancer le même fichier
  ne duplique jamais un item déjà en base). Format `cqc-<competence_slug>-<difficulte>-<index>`,
  `competence_slug` dérivé de `theme` (minuscules, accents supprimés, espaces en
  tirets), `index` à partir de 0 dans l'ordre de génération.
- `theme` : doit correspondre exactement au nom de la compétence demandée (c'est un
  `Tag` existant côté edukora - ne l'invente pas, ne le paraphrase pas), **sauf** le cas
  particulier "savoir jamais encore couvert" décrit dans "Entrée attendue" ci-dessus, où
  un nouvel intitulé est autorisé parce qu'ancré à `savoir_officiel`.
- `savoir_officiel` (nouveau, optionnel) : référence vers le référentiel programme
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
  Cherche dans le fichier correspondant le savoir dont l'intitulé correspond le
  mieux à `theme` ; si aucune correspondance nette n'apparaît, ou si la requête ne
  porte pas sur l'une de ces combinaisons pays/matière/niveau, omets le champ (ou
  mets-le à `null`) - ne jamais deviner une référence. Reprends les valeurs
  `classe`/`serie_label`/
  `module_numero`/`savoir_numero` exactement telles qu'elles apparaissent dans le
  fichier : une valeur approximative fait échouer l'ingestion de tout le lot (voir
  `catalog.ingestion._resolve_savoir_officiel`). Effet : le `Tag` visé par `theme`
  est alors automatiquement rattaché à ce savoir officiel s'il ne l'était pas déjà.
- `matiere`/`cursus` : recopiés tels quels depuis la requête d'entrée.
- `type_reponse` = `"QCM"` si tu fournis `choix` (liste de `{"lettre", "texte"}`,
  4 options typiquement) et `reponse_correcte` (la lettre correcte) ; sinon
  `"OUVERTE"` avec `choix: []` et `reponse_correcte: ""`. Toujours la forme lettrée
  pour `choix`, même quand la matière source présente ses options autrement (ex.
  anglais grammatical où la source donne les options en ligne, entre parenthèses,
  séparées par des barres obliques, sans lettre) : l'interface du quiz affiche
  systématiquement des boutons lettrés, quelle que soit la matière.

  **Part minimale de QCM : un plancher par famille de matières** (révisé le
  2026-10-26 ; l'ancienne règle unique « au moins la moitié » était trop basse pour
  les matières à réponse objective et trop haute pour les matières rédigées). Ce
  n'est pas une préférence de format, c'est une contrainte de mesure : une question
  ouverte est auto-notée par l'élève lui-même (il clique Réussi / Partiel / Échec après
  avoir lu le corrigé), là où un QCM se corrige objectivement. Or son taux de réussite
  ne sert plus seulement à s'auto-évaluer - il décide désormais de ce qu'on lui propose :
  quel thème revient en révision espacée et à quelle échéance, et s'il faut lui
  réexpliquer la méthode ou le laisser passer directement à la pratique. Un taux
  calculé sur des réponses auto-notées mesure surtout son honnêteté ; en faire le
  moteur des recommandations, c'est bâtir sur du sable. Le corpus était à 78 %
  d'ouvertes fin septembre 2026 et à 47 % de QCM seulement le 26 octobre (Maths 14 %,
  Chimie 23 %, Physique-Chimie-Techno 25 %, Philosophie 28 %), d'où cette règle.

  | Famille | Matières (code `Subject`) | Plancher | Sur un lot de 6 items |
  |---|---|---|---|
  | **OBJECTIVE** | Mathématiques, Physique, Chimie, Physique-Chimie(-Techno), SVT, Informatique, Programmation, Systèmes d'Information, Réseaux, Anglais, Allemand, Espagnol ; GCE : Maths (toutes), Physics, Chemistry, Biology, Human Biology, Geology, Computer Science, ICT, Food & Nutrition, English, French, Accounting, Logic | **70 %** | **au moins 5 QCM** (4/6 = 67 % ne passe pas) |
  | **MIXTE** | Français, Histoire, Géographie, Éducation civique, EPS, Musique, Travail manuel, Économie ; GCE : History, Geography, Economics, Commerce, Citizenship ; toute matière absente de ce tableau | **50 %** | au moins 3 QCM |
  | **REDIGE** | Philosophie, Littérature ; GCE : Philosophy, Religious Studies, Literature in English | **30 %** | au moins 2 QCM |

  Les colonnes « Plancher » et « Sur un lot de 6 items » valent pour le **lot** ; le minimum
  **par compétence** (6 QCM en OBJECTIVE et MIXTE) est plus strict et prime pour une compétence livrée seule.

  La table de référence est dans le code (`backend/catalog/tunnel.py` :
  `FAMILLE_QCM` et `PLANCHER_QCM`, reprise par `scripts/gce/valider_quiz_gce.py` pour
  les tranches GCE) : en cas d'écart avec ce tableau, le code fait foi, et une matière
  nouvelle doit y être ajoutée. Une matière absente (ex. Technical Drawing, Cinematic
  Art) retombe sur MIXTE, donc 50 %.

  Le plancher se vérifie à **deux niveaux** :
  - **le lot** (toutes les compétences que tu livres pour une matière) : au moins le
    plancher de la famille ;
  - **chaque compétence** (chaque `theme`), à partir de 3 items : **au moins 6 QCM**
    en famille OBJECTIVE et MIXTE, 1 seul en famille REDIGE (`MIN_QCM_PAR_THEME` dans
    `backend/catalog/tunnel.py`, plancher de la campagne « 6 questions minimum par
    thème » de novembre 2026). Une compétence livrée par lot de 6 items est donc
    **entièrement en QCM** (6 sur 6) en OBJECTIVE et MIXTE : le seul item élevé
    n'échappe plus au QCM. Un lot qui tient 70 % en mettant une compétence à
    100 % de QCM et une autre à 100 % d'ouvertes échoue : c'est le thème, pas le lot,
    qui entre en révision espacée, et son taux ne repose alors sur aucune réponse
    objective. Seule la famille REDIGE (Philosophie, Littérature) garde des ouvertes :
    elle exige au moins 1 QCM par compétence.

  Prends le QCM chaque fois que la réponse est objective : résultat numérique,
  définition, identification, formule, choix de méthode, correction grammaticale.
  Garde l'ouverte pour ce qui exige une rédaction ou un raisonnement argumenté
  qu'aucun jeu de quatre options ne restitue honnêtement - dissertation, commentaire,
  justification en plusieurs étapes. Dans une matière OBJECTIVE, c'est typiquement
  l'unique item de difficulté ÉLEVÉE d'un lot de 6 qui reste en ouverte.

  **Un mauvais QCM reste pire qu'une bonne ouverte** : quatre options dont trois sont
  manifestement absurdes ne mesurent rien, et l'élève trouve sans savoir. Chaque
  distracteur doit correspondre à une erreur réellement commise sur cette compétence -
  confusion de formule, erreur de signe, unité oubliée, définition voisine. Même un
  bon QCM garde 25 % de réussite au hasard : sur peu d'items, son taux est bruité, ce
  qui est une raison de plus de viser un vrai plancher et de soigner les distracteurs,
  jamais de multiplier des options de remplissage. Si une compétence ne s'y prête
  vraiment pas et que le lot ou la compétence tombe sous son plancher, dis-le
  explicitement dans ton compte rendu de lot, avec la raison (et la matière, la
  compétence, le nombre de QCM obtenus), plutôt que de fabriquer des options de
  remplissage pour atteindre le quota. Le tunnel de validation signale ces cas en
  ALERTE : cette justification est ce qui permet de les arbitrer.
- `source_exercises` : les `exercise_id` du matériel de référence qui ont
  effectivement inspiré cet item (traçabilité/audit interne uniquement - jamais
  mentionné dans `enonce_markdown`/`corrige_markdown`, jamais montré à l'élève).
- `corrige_markdown` : commence toujours par `### Rappel de méthode` (2-4 lignes) puis
  `### Corrigé` - jamais l'un sans l'autre, jamais l'ordre inversé. Voir l'exigence
  non négociable n°2 ci-dessous pour le détail et la justification.

**Destination du fichier** : le tableau JSON complet d'un lot est écrit dans un seul
fichier, déposé sous `ingest/_quiz/<pays>/<competence_slug>.json` (le pays de la
requête d'entrée détermine ce dossier - il n'est jamais répété dans chaque item, voir
`quiz.ingestion._country_code_from_quiz_ingest_path`, ancré sur le segment `_quiz`) -
jamais dans le dossier `ingest/` racine de correction-experte, qui ne sait pas lire ce
format. Les PNG des figures (voir « Figures et tracés dans les items ») sont écrits
dans ce même dossier, à côté du JSON : l'ingestion les cherche là, jamais ailleurs.

## Mode GCE (items EN ANGLAIS) : adaptations qui PRIMENT

Pour une requête dont `cursus` est `[{"examen":"gce_ol","serie":""}]` (ou `gce_al`) et dont `matiere` est un libellé anglais (« Mathematics », « Physics », « Chemistry », « Pure Mathematics with Mechanics », « Pure Mathematics with Statistics », « Further Mathematics »... ; « Pure Mathematics » seul est refusé), appliquer ce qui suit, qui prime sur le reste du skill. **Pour `gce_al`, lire aussi `scripts/gce/consignes/CONSIGNES_QUIZ_GCE_AL.md`, qui prime sur le point 4 ci-dessous (niveau Advanced, jamais Form 5 ; constantes de l'A Level).** Guide canonique : `scripts/gce/README.md` ; consignes d'agent : `scripts/gce/consignes/CONSIGNES_QUIZ_GCE.md` ; validateur : `python scripts/gce/valider_quiz_gce.py <tranche.json> <dossier>` (doit afficher `OK`).

1. **Tout est en anglais** : énoncés, options, corrigés. Pas de références BEPC/BAC, pas de titres français.
2. **Titres du corrigé** : `### Method reminder` (2 à 4 lignes : le principe AVANT son application) puis `### Solution`. Jamais « Rappel de méthode » / « Corrigé ».
3. **Champs recopiés de la requête** : `matiere` et `cursus` tels quels ; `theme` = la valeur de `competence`, exactement ; **`savoir_officiel` omis ou `null`** (pas de référentiel GCE).
4. **Niveau et style** : GCE Board (« Calculate », « State », « Explain », « Find »), Form 5 pour l'O Level, jamais du niveau Advanced ; unités SI, `g = 10 m s^-2`, calculatrice permise, contextes camerounais plausibles (FCFA, marché, Douala, Bamenda...). Chimie : masses atomiques de l'O Level (H 1, C 12, N 14, O 16, Na 23, Mg 24, Al 27, S 32, Cl 35,5, K 39, Ca 40, Cu 64, Zn 65), volume molaire 24 dm3, équations équilibrées atome par atome **vérifiées par code**.
5. **Format du lot** : 6 items par compétence (2 faible / 3 moyenne / 1 élevée), **part de QCM selon la famille de la matière (voir « Part minimale de QCM » plus haut) : au moins 5 QCM sur 6 pour Mathematics, Physics, Chemistry, Biology, Human Biology, Geology, Computer Science, ICT, Food & Nutrition, English, French et les Mathématiques avancées ; au moins 3 sur 6 pour History, Geography, Economics, Commerce, Citizenship ; au moins 2 sur 6 pour Philosophy et Religious Studies** (4 options, lettres a-d, la bonne lettre varie, chaque distracteur est une erreur réelle), un fichier `<slug de la compétence>.json` par compétence dans un dossier propre à l'agent.
6. **`external_id`** = `cqc-<slug>-<difficulte>-<index>` (`difficulte` en minuscules `faible|moyenne|elevee`). **PIÈGE** : le slug ne contient pas la matière ; deux matières qui partagent un thème (« graphs » en Maths et en Chimie) produisent les MÊMES identifiants, et `ingest_quiz_content` ignore **silencieusement** les doublons (« déjà existant(s) ») : numéroter la seconde matière à partir de 10, et lire cette ligne après chaque ingestion.
7. **Matériel de référence** : des vraies questions du GCE, pour le niveau et le style seulement ; jamais copiées (le validateur refuse 9 mots consécutifs identiques à un énoncé de référence). Pas de figure sauf nécessité ; préférer un énoncé textuel ou un tableau Markdown.
8. **Rigueur** : générer les fichiers par un script où chaque valeur numérique d'un corrigé est recalculée (`assert`) avant d'être écrite ; seconde passe en résolvant chaque QCM sans regarder le corrigé ; backslash LaTeX doublé dans le JSON, `$` hors formule écrit `\$`.
9. **Ingestion** : `manage.py ingest_quiz_content <dossier>` ; thèmes sans quiz = étape E du tunnel (skill `couverture-quiz-lot-edukora`).

---

## Les six exigences non négociables

Avant de finaliser un item, vérifie-le contre chacune de ces six exigences. Elles
comptent plus que le nombre d'items produits - un lot de 4 items solides vaut mieux
qu'un lot de 10 dont deux sont bancals.

### 1. Autonomie totale

Un élève doit pouvoir répondre en lisant uniquement `enonce_markdown`, sans rien
d'autre - pas d'exercice parent, pas de question voisine, pas de figure ou de
document externe.

Concrètement, `enonce_markdown` ne doit jamais :
- renvoyer à "la question précédente", "la partie A", "le résultat obtenu plus haut",
  "le texte cité plus haut", "le document ci-dessus" ou toute formulation équivalente
  - si un résultat ou un support antérieur est nécessaire, intègre-le directement
  dans l'énoncé (une donnée numérique admise, une citation reproduite en entier, un
  résumé du contexte historique) plutôt que d'y faire référence ;
- exiger un document externe que tu ne livres pas avec l'item : une figure
  géométrique, une courbe, un tableau, un schéma SVT, une carte, un graphique
  économique "ci-contre", "ci-dessous" ou "suivant" qui n'existerait que dans un
  exercice source. Une figure n'est autonome que si TU la produis et la joins à l'item
  (voir « Figures et tracés » plus bas) : le placeholder `![fig-1](...)` et son PNG
  font alors partie de l'item, au même titre que son texte. À défaut de pouvoir
  produire la figure, choisis une formulation purement textuelle de la même
  compétence (ex. donner l'expression algébrique de $f$ plutôt que renvoyer à sa
  courbe ; décrire une situation géographique en texte plutôt que renvoyer à une
  carte). Jamais de carte, de document ou de photo du programme que tu ne peux pas
  tracer toi-même avec exactitude. Pour une compétence de type "explication de
  texte" ou "commentaire", reproduis intégralement le texte/l'extrait à commenter
  dans `enonce_markdown` plutôt que d'y renvoyer comme à un document séparé.

### 2. Chaque corrigé rappelle la méthode avant de l'appliquer

`corrige_markdown` s'ouvre toujours par un bloc `### Rappel de méthode` (2 à 4
lignes) avant le bloc `### Corrigé` lui-même - jamais l'un sans l'autre, jamais
l'ordre inversé. Le rappel énonce le principe général ou la technique mobilisée,
AVANT de l'appliquer au cas précis de cet item (ex. "Pour dériver un produit de
deux fonctions $u$ et $v$, on utilise $(uv)'=u'v+uv'$." avant de calculer la dérivée
demandée) - jamais une reformulation de l'énoncé, jamais un résumé du résultat à
venir, jamais un rappel si vague qu'il s'appliquerait à n'importe quelle compétence
du programme.

Non négociable pour toutes les matières, y compris les matières argumentatives :
pour une dissertation/un commentaire/une explication de texte, le rappel résume la
méthode attendue par le genre (ex. "Une dissertation exige une problématisation qui
transforme le sujet en question à débattre, puis un plan qui...") avant le
développement effectif de cet item précis - jamais une notion de contenu déguisée en
méthode.

Raison d'être : un élève qui échoue à une question doit comprendre POURQUOI sa
méthode était fausse, pas seulement voir la bonne réponse - c'est la même convention
que `correction-experte` (voir son "Template obligatoire pour chaque exercice", bloc
"Rappel de la méthode/notion mobilisée"), appliquée ici à un item entièrement
autonome, donc sans les autres blocs de ce template qui restent hors du périmètre de
ce skill ("Piège à éviter", "Conseil" - optionnels chez `correction-experte`, sans
objet ici).

### 3. Jamais de copie, même partielle - sauf les citations légitimes

Compare mentalement chaque phrase de ton énoncé à chaque exercice de
`materiel_reference` : si une phrase serait reconnaissable comme venant de là,
réécris-la. Change systématiquement les valeurs numériques, le contexte concret
(une urne de boules peut devenir un jeu de cartes, un tirage au sort peut devenir un
contrôle qualité), et la formulation - pas juste les nombres en gardant la même
phrase autour.

Ça ne concerne que le texte *inventé par l'exercice source* (son scénario, sa mise en
situation, sa formulation). Ça ne concerne pas les citations d'auteurs, d'œuvres ou de
faits réels au programme : si la compétence porte sur "le personnage de Rastignac
chez Balzac" ou "la bataille de 1958", cite l'œuvre/l'événement réel normalement,
avec exactitude - c'est attendu, pas une entorse à la règle. La règle porte sur le
matériau que le rédacteur de l'exercice source a lui-même inventé, jamais sur la
réalité littéraire, historique ou scientifique qu'il a mobilisée.

### 4. Rigueur : vérifie avant de livrer, ne suppose pas

C'est le point le plus risqué de ce skill, plus que pour `correction-experte` : là-bas,
un corrigé s'appuie sur une épreuve dont l'énoncé est fixe et connu. Ici, tu inventes
l'énoncé ET le corrigé en même temps, donc rien ne garantit par défaut qu'ils soient
cohérents entre eux. La méthode de vérification dépend de la nature de la compétence :

**Matières à résultat calculable ou factuellement vérifiable** (maths, physique-chimie,
SVT quantitatif, économie chiffrée, anglais grammar/QCM fermé, toute question à
réponse objective) :
1. Résous-le toi-même intégralement, étape par étape, comme si tu étais l'élève.
2. Compare ta résolution à `corrige_markdown` que tu es en train d'écrire - elles
   doivent être identiques au résultat près, pas seulement à la méthode près.
3. Pour un QCM, vérifie que `reponse_correcte` désigne bien la lettre du bon calcul,
   et que chaque mauvaise option correspond à une erreur plausible pour cette
   compétence (un oubli de signe, une confusion de formule, une erreur d'arrondi,
   une confusion grammaticale réelle - pas une valeur au hasard qu'aucun élève ne
   produirait).

**Matières à structure argumentative** (français - dissertation/commentaire,
philosophie, histoire-géo, anglais essay/compréhension, SVT rédactionnel) : il n'y a
pas "un" résultat unique à recalculer, mais la rigueur reste vérifiable - relis ton
propre `corrige_markdown` et confirme :
1. La structure attendue par le genre est réellement respectée (une dissertation a
   une vraie problématisation, pas une reformulation du sujet ; un plan dialectique a
   une antithèse qui contredit réellement la thèse, pas une variation cosmétique).
2. Chaque fait cité (date, auteur, œuvre, événement, concept) est exact - une
   dissertation qui cite un auteur hors programme, une mauvaise date, ou attribue la
   mauvaise thèse à un philosophe est aussi fausse qu'un calcul faux.
3. L'énoncé pose une vraie question ouverte à débattre (pour une dissertation/un
   commentaire) ou une consigne dont la réponse est démontrable à partir du texte
   fourni (pour une explication de texte/une compréhension) - jamais une question
   dont la réponse est déjà donnée dans l'énoncé lui-même.

Si à l'étape de vérification tu trouves un écart, ne "corrige" pas juste le corrigé
pour qu'il colle - relis l'énoncé, il est probablement ambigu, sous-déterminé, ou
appelle un fait que tu as mal vérifié.

### 5. Variété dans le lot

Si tu produis plusieurs items pour la même compétence et la même difficulté, ils
doivent être des problèmes/sujets réellement différents : un scénario différent, des
valeurs différentes, un angle d'attaque différent sur la compétence, un exemple ou
une citation différente - pas la même question avec les nombres ou les noms propres
changés. Un élève qui repasse un test de niveau plus tard ne doit pas reconnaître la
question précédente déguisée.

### 6. Registre adapté au cursus

Respecte le niveau de langue, les notations et les conventions du cursus/de la série
visée (le style d'un BEPC n'est pas celui d'un BAC C), dans l'esprit de
`correction-experte` : une pédagogie de niveau supérieur à un répétiteur classique,
jamais approximative, jamais condescendante.

## Figures et tracés dans les items

Un item peut porter des images : `CompetenceItem` les accepte désormais (une image par
entrée de `figures`, stockée avec l'item et affichée à l'emplacement du placeholder
dans l'énoncé comme dans le corrigé). Les règles ci-dessous reprennent celles de
`correction-experte` (« Figures produites dans le corrigé »), adaptées à un item
inventé : ici il n'y a jamais de figure à extraire d'un PDF, seulement des figures à
PRODUIRE.

### 1. Quand produire une figure

- **Le corrigé exige un tracé** (courbe de fonction, tableau de variations excepté,
  construction géométrique, image d'une transformation, schéma SVT légendé, graphique
  économique - offre/demande, coûts -, graphique de physique, circuit ou montage) :
  produire réellement l'image, dans tous les cas, jamais seulement la décrire. Une
  description verbale, aussi précise soit-elle, ne dispense jamais de la figure :
  l'élève doit pouvoir comparer SON tracé à un tracé exact, pas seulement lire comment
  le refaire.
- **L'énoncé a besoin d'une figure** (lecture graphique, repérage sur un schéma, figure
  géométrique codée) : tu peux la produire toi-même et la joindre (`origine_figure:
  "enonce"`). Elle doit alors être exacte, lisible à l'écran d'un téléphone, et
  l'énoncé reste complet sans devoir deviner : toutes les données qu'une figure ne
  rend pas sans ambiguïté (valeurs, unités, noms de points) sont aussi écrites en
  texte.
- **Sinon, pas de figure** : n'en ajoute pas par décoration. Une question de calcul
  pur n'en a pas besoin, et chaque image alourdit le chargement sur une connexion
  mobile instable.
- Un tableau de variations, un tableau de signes, un tableau de valeurs restent en
  LaTeX (`\begin{array}`) ou en tableau Markdown, jamais en image.

### 2. Comment la produire

Avec un outil de tracé précis, à partir des valeurs réellement établies dans le
corrigé - jamais une image approximative, jamais « à l'œil » :
- **Courbe de fonction ou graphique** (maths, physique, économie) : script Python/
  matplotlib à partir de l'expression ou des données du corrigé, axes gradués et
  légendés (grandeur + unité), courbe nommée, points remarquables marqués (zéros,
  extremums, asymptotes en pointillés, tangente...). Échantillonner assez finement
  (plusieurs centaines de points) pour qu'aucun coude ne soit visible, et ne jamais
  relier une discontinuité (asymptote verticale : couper la courbe en deux tracés).
- **Construction géométrique codée** : SVG ou matplotlib, avec les points calculés,
  les codages exacts (angles droits, longueurs égales, mesures) et les noms de points
  lisibles ; les coordonnées viennent du corrigé, pas d'un croquis.
- **Schéma SVT ou circuit** : appliquer les conventions de `correction-experte` pour
  la matière (titre, légendes numérotées, flèches et sens) et le produire comme figure.
- Si aucun outil de tracé n'est disponible dans l'environnement d'exécution (pas de
  Python, pas de matplotlib), ne livre PAS l'item avec une figure décrite en texte :
  reformule-le en version purement textuelle de la même compétence, ou retire-le, et
  dis-le dans le compte rendu de lot. Jamais de placeholder sans image.
- Image lisible sur mobile : largeur de l'ordre de 1000 px, texte et traits assez
  gros pour rester lisibles réduits à la largeur d'un écran de téléphone, fond blanc.

### 3. Fichier et référencement

- Format PNG, écrit dans le dossier du JSON du lot (voir « Destination du fichier »),
  nommé `<external_id>_fig_<index>.png` (index à partir de 1) : l'`external_id` est
  déjà unique dans le lot, donc deux items ne peuvent jamais s'écraser leur image.
- Placeholder Markdown à l'endroit exact où la figure doit apparaître, dans
  `enonce_markdown` ou `corrige_markdown` :
  `![fig-1](cqc-derivation-etude-fonctions-moyenne-0_fig_1.png)`
- Champ `figures` de l'item, une entrée par image :

```json
"figures": [
  {
    "id": "fig-1",
    "fichier": "cqc-derivation-etude-fonctions-moyenne-0_fig_1.png",
    "type": "courbe",
    "legende": "Courbe de g(x) = x^3 - 3x + 1 avec ses extremums en x = -1 et x = 1",
    "origine_figure": "corrige"
  }
]
```

  `type` : valeur courte libre (`courbe`, `figure geometrique`, `schema`, `graphique`,
  `circuit`...). `legende` : une phrase qui dit ce que montre la figure - elle devient
  le texte alternatif lu par un lecteur d'écran, donc jamais « figure 1 ».
  `origine_figure` : `"enonce"` ou `"corrige"`.
- **Le corrigé décrit toujours le tracé pas à pas, en plus de l'image** : la description
  donne la méthode pour refaire le tracé (points calculés, tangentes, asymptotes,
  ordre des étapes), l'image donne le résultat exact auquel se comparer. Aucune étape
  masquée, comme pour les calculs.
- Une figure partagée par l'énoncé et le corrigé (ex. la courbe donnée, puis la même
  complétée) = deux images distinctes, deux entrées, deux placeholders : un item n'a
  jamais deux entrées qui pointent vers le même fichier.

### 4. Lecture graphique (figure d'énoncé)

Quand la réponse se lit sur une figure : l'écrire « par lecture graphique, $f(2) \approx
3$ » dans le corrigé (jamais un « = » strict pour une valeur lue), donner la précision de
lecture cohérente avec la graduation visible, et croiser avec le calcul dès que
l'expression de la fonction est donnée dans l'énoncé - le calcul prime en cas d'écart.
Pour un QCM, les options doivent être séparées d'au moins deux fois la précision de
lecture, sinon la question départage le coup d'œil de l'élève, pas sa compétence.

### 5. Ce que fait la plateforme (utile pour diagnostiquer)

L'ingestion lit chaque PNG dans le dossier du JSON, le compresse, le stocke, puis réécrit
le placeholder vers son URL. Elle REJETTE l'item entier, sans rien enregistrer, si : un
PNG listé est introuvable ; une entrée de `figures` n'a pas de `fichier` ; un placeholder
`![fig-N](...)` du texte n'a pas d'entrée correspondante ; une entrée n'est référencée par
aucun placeholder. Un item déjà ingéré n'est jamais modifié par un ré-import (clé
`external_id`) : pour corriger une figure d'un item déjà en base, le supprimer côté admin
puis réingérer le lot, jamais « réingérer par-dessus ».

## Vérification finale avant de renvoyer le JSON

Relis chaque item et confirme, un par un :
- [ ] Autonome : aucune référence à une question/partie/document voisin, aucune figure
      externe (toute figure est produite par toi et jointe à l'item)
- [ ] Figures : si le corrigé demande un tracé, l'image existe sur disque (PNG relu
      visuellement : entière, droite, lisible, axes gradués et légendés), son placeholder
      et son entrée `figures` se correspondent exactement, les valeurs tracées sont
      celles du corrigé (recalculées, pas supposées), et le tracé est AUSSI décrit en
      texte - jamais un tracé seulement décrit, jamais un placeholder sans image
- [ ] `corrige_markdown` commence par `### Rappel de méthode` (2-4 lignes, le principe
      ou la technique AVANT son application au cas précis) puis `### Corrigé` - jamais
      l'un sans l'autre, jamais un rappel qui reformule juste l'énoncé
- [ ] Aucune phrase reconnaissable d'un exercice de `materiel_reference` (les citations
      légitimes d'auteurs/œuvres/faits réels ne comptent pas comme une copie)
- [ ] Vérifié selon la méthode adaptée à la matière (recalcul indépendant pour une
      matière à résultat objectif ; structure + exactitude factuelle pour une matière
      argumentative) - résultat cohérent avec `corrige_markdown`
- [ ] `theme`/`matiere`/`cursus` conformes à la requête d'entrée
- [ ] `external_id` renseigné et unique dans le lot
- [ ] QCM uniquement : `reponse_correcte` est une lettre présente dans `choix`,
      distracteurs plausibles pour cette compétence
- [ ] `source_exercises` renseigné, jamais mentionné dans le texte visible

Si un item échoue à l'une de ces cases, corrige-le ou retire-le du lot plutôt que de
le livrer tel quel - un lot plus court mais entièrement fiable est le seul livrable
acceptable pour un outil d'auto-évaluation.

Une dernière case se vérifie sur le LOT entier, pas item par item :

- [ ] La part d'items `type_reponse: "QCM"` atteint le plancher de la famille de la
      matière (70 % OBJECTIVE, 50 % MIXTE, 30 % REDIGE - voir « Part minimale de QCM »)
      - compte-les avant de livrer. Sous ce seuil, le lot n'est livrable qu'accompagné
      de la raison explicite (compétence non QCMisable honnêtement), jamais en silence.
- [ ] Chaque compétence (`theme`) de 3 items ou plus compte au moins 6 QCM (1 en famille
      REDIGE), même quand le lot entier passe son plancher : 6 items sur 6 en QCM en
      matière OBJECTIVE ou MIXTE.

Attention à l'effet pervers du retrait : si tu écartes des items défaillants à l'étape
précédente et que ce sont surtout des QCM, le lot peut repasser sous son plancher sans
que tu t'en rendes compte. Recompte APRÈS les retraits, pas avant.

## Tunnel de validation - dernière étape obligatoire de tout round d'ingestion

Un round n'est JAMAIS déclaré terminé sur la seule foi de « l'ingestion n'a pas échoué » : les écarts constatés jusqu'ici (rendu KaTeX cassé, questions sans thème, quasi-doublons de thèmes, QCM incohérent) passaient l'ingestion sans erreur et n'apparaissaient qu'après coup, en obligeant à lancer des campagnes de rattrapage. Après l'ingestion, lancer depuis la racine du dépôt (`D:\edukora`) :

```bash
bash scripts/tunnel_validation.sh <since> [--strict]
```

`<since>` = durée depuis le début du round (`2h`, `90m`, `1d`) ou datetime ISO : le tunnel ne valide que le contenu créé ou modifié depuis cet instant. Il enchaîne (1) la structure - Question sans thème, QCM incohérent (BLOQUANT) ; (2) le vocabulaire de thèmes - quasi-doublons de Tag, thèmes partagés entre matières (ALERTE) ; (3) **la part de QCM** - par matière contre le plancher de sa famille, puis par thème contre le minimum de 6 QCM, 1 en famille REDIGE (ALERTE, jamais bloquant : une compétence réellement non QCMisable s'arbitre avec la justification du compte rendu de lot) ; (4) la couverture - quiz/cours manquants pour les thèmes touchés (INFO) ; (5) le rendu - le VRAI moteur KaTeX/remark sur ce périmètre. Une ALERTE QCM s'ouvre en convertissant des items objectifs en QCM (jamais en inventant des distracteurs de remplissage) puis en réingérant, ou se solde dans le rapport avec sa raison.

- La sortie `TUNNEL VALIDÉ` (code 0) est exigée avant de conclure ; la citer dans le rapport final.
- BLOQUANT ou échec de rendu : corriger la donnée (JSON source) puis réingérer. Si la même anomalie revient d'un round à l'autre, la signaler à l'utilisateur comme défaut de plateforme (`catalog/rendering.py`, `catalog/ingestion_repairs.py`) au lieu de la repatcher à la main.
- ALERTE de quasi-doublon de Tag : soit un thème équivalent existe déjà (reprendre sa forme exacte dans le JSON et réingérer), soit les deux sont réellement distincts, et le rapport le dit explicitement. Jamais de fusion en masse sans l'utilisateur.
- Avant de fournir des `themes`, quand la base est accessible (`docker exec edukora-backend-1`), chercher la forme existante du thème (accents, singulier/pluriel, casse) plutôt que d'en inventer une variante : c'est la source des quasi-doublons.
- Le rattachement `savoir_officiel` n'entre PAS dans ce tunnel (mis en standby le 2026-09-18, l'organisation se fait par thèmes) : un `null` n'est pas un défaut à corriger.
- Environnement sans accès à docker/à la base (tâche planifiée Cowork) : le dire dans le rapport - le round reste NON validé tant que le tunnel n'a pas tourné depuis Claude Code.
- Le code du tunnel vit dans l'image du backend (pas de bind-mount) : si `valider_ingestion` est « Unknown command », reconstruire (`docker compose build backend && docker compose up -d backend`).

## Backslash des commandes LaTeX dans le JSON : toujours DOUBLÉ

Dans le fichier JSON d'un lot, un backslash s'écrit `\\`. Un backslash SEUL devant `n`, `t`, `r`, `f` ou `b` est lu comme un échappement JSON valide, donc sans la moindre erreur : `\ne` devient un saut de ligne suivi de `e`, `\times` une tabulation suivie de `imes`, `\frac` un saut de page suivi de `rac`, `\text` une tabulation... et la formule est cassée à l'affichage sans aucun signal. Écrire `"$x \\ne 1$"`, `"$2 \\times 3$"`, `"$\\frac{1}{2}$"`, `"$h\\nu$"`, jamais `"$x \ne 1$"`. Commandes les plus exposées : `\ne` `\neq` `\nu` `\notin` `\nabla` `\nmid` (n) ; `\times` `\text` `\theta` `\tan` `\to` `\tau` `\triangle` `\tilde` (t) ; `\rho` `\right` `\rightarrow` `\rangle` (r) ; `\frac` `\forall` (f) ; `\beta` `\bar` `\binom` `\boldsymbol` (b). Constaté le 2026-10-03 : 39 items de quiz déjà en base portaient ce défaut (`\ne` surtout : « $a\ne0$ », « $D$ : $3+2-6=-1\ne0$ »).

**Contrôle mécanique avant de livrer** : après avoir écrit le fichier du lot, le recharger (`json.load`) et vérifier, sur CHAQUE chaîne (`enonce_markdown`, `corrige_markdown`, `choix[].texte`), qu'elle ne contient aucune tabulation, aucun `\x08` ni `\x0c`, et qu'aucun saut de ligne n'est directement suivi de `e`, `eq`, `u`, `otin` ou `abla` à l'intérieur d'une formule `$...$`. La plateforme restaure ces cas à l'ingestion depuis le 2026-10-03 (`_repair_control_chars_in_math`), mais c'est un filet de sécurité, jamais une raison de relâcher cette règle : il ne couvre pas les cas ambigus (ex. `\nu` en début de ligne).

## Le caractère `$` hors formule doit toujours être protégé

`$` est le délimiteur des formules LaTeX : un `$` littéral laissé nu (variable PHP `$nom`, référence de tableur `$B$2`, symbole monétaire) est apparié par la plateforme au `$` suivant, et tout le texte compris entre les deux s'affiche comme une formule déformée ou lève une erreur KaTeX. Dans `enonce_markdown` et `corrige_markdown` : tout nom de variable, code ou formule de tableur contenant un `$` va dans un span de code entre backticks (`` `$nom` ``, `` `=RANG(B2;$B$2:$B$5;0)` ``) ; un extrait de code de plusieurs lignes est un bloc fencé (```` ```php ... ``` ````), jamais des lignes de code nues ; le symbole isolé dans une phrase s'écrit `` `$` `` ou `\$`. Relire chaque `$` du texte produit avant de livrer : soit dans un span/bloc de code, soit délimiteur d'une vraie formule, soit échappé.
