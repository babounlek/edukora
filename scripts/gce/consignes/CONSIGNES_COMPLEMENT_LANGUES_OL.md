# Complément aux consignes - English Language (0530) et French (0545), O Level

Lis `CONSIGNES.md` puis `CONSIGNES_COMPLEMENT_PHYSIQUE.md` : les règles générales (vérification du niveau sur la page de garde,
option de QCM fautive = question ouverte, SECONDE PASSE OBLIGATOIRE, un dossier par agent, fichiers temporaires préfixés, validateur)
s'appliquent telles quelles. Ce complément dit ce qui change pour les deux matières de LANGUE. Les corrigés d'une matière de langue
ne sont pas des calculs : ce sont des **réponses modèles** à écrire avec le plus grand soin, dans la langue de la matière.

## Identité

| | English Language | French |
|---|---|---|
| `matiere` | "English Language" | "French" |
| `code_matiere` | "0530" | "0545" |
| DOSSIER | `gce-ol-english-<annee>-p<paper>-officiel-cameroun` | `gce-ol-french-<annee>-p<paper>-officiel-cameroun` |
| validateur | `--code 0530` | `--code 0545` |
| `duree_epreuve` | lue sur le sujet (en général P1 "1h30", P2 "2h") | lue sur le sujet (en général "1h30" les deux) |

`examen` "gce_ol", `serie` null. Le contenu des JSON (énoncés recopiés, consignes, rubriques) reste tel qu'imprimé ; tout ce que TU
écris (corrigés, notes de correction) est en **anglais clair**, sauf les réponses modèles elles-mêmes : pour French, ce sont des
textes en **français correct et naturel**, niveau Form 5.

## Aucun corrigé officiel : la justesse linguistique est ton travail

- Chaque clé de QCM est à établir toi-même, sur la langue, pas sur l'intuition : conjugaison, accord, préposition, registre. Relis
  l'énoncé en insérant chaque option. Quand deux options sont défendables, choisis celle qu'attend le Board (usage standard, niveau Form 5)
  et dis pourquoi l'autre ne convient pas ; si le doute reste réel, écris-le dans `incertitudes` (numéro de question + les deux options).
- N'écris JAMAIS un corrigé de QCM qui contredit une règle de grammaire pour « coller » à la lettre choisie.
- Termine chaque corrigé de QCM par « **Answer: C.** » et donne la règle en une phrase (« after "il faut", the infinitive is used... »).

## Paper 1 : 50 QCM (1 fichier, `numero_exercice` "1")

Même contrat que les autres matières (50 questions "1" à "50", `type_reponse` "qcm", lettres minuscules a-d, `points` "", `groupes` []).

- **Textes et passages communs** (compréhension, texte à trous, document) : recopie le passage UNE fois, dans l'`enonce_markdown` de la
  PREMIÈRE question du groupe, sous un titre en gras (« **Passage for questions 11 to 20** »), et fais-le précéder, dans les questions
  suivantes, de la mention « (Passage for questions 11 to 20 above) ». Un passage ne se coupe jamais : si la copie est illisible,
  `incertitudes`.
- **English P1 - Section A, listening comprehension** : le texte lu par l'examinateur est imprimé dans les pages « Instructions for the
  conduct of Section A » (réservées au professeur). L'élève ne l'entend pas : recopie ce texte en intégralité, SANS les barres obliques
  de pause, sous le titre « **Listening passage (read aloud once by the examiner in the real exam - read it once, then answer)** » dans
  l'énoncé de la première question de la section. Garde les repères « Section 1/2/3 » du texte, car les questions s'y rapportent.
  Ne recopie pas les consignes de conduite de l'épreuve (minutage, annonces de l'examinateur).
- **Questions d'accentuation** (« same stress pattern as... ») : transcris la graphie telle qu'imprimée ; le corrigé donne l'accentuation
  (syllabe accentuée en majuscules : PHYsical).
- **French P1** : accents, élisions, tirets et traits de remplissage (`------`) exactement comme sur le sujet ; écris le blanc `____`.
  Une question à deux blancs (« ---- plus ---- que ») garde ses deux blancs et ses options couplées telles quelles.
- Les thèmes de P1 sont fins (un thème par règle testée : 1 à 2 par question).

## Paper 2 : rédaction, un fichier par bloc du sujet

### English Language 2 (Directed Writing + Composition)

- **Section A, Directed Writing** (30 points : Content 14, Expression and Accuracy 12, Slanting 4) : fichier `numero_exercice` "1",
  `groupes` ["SECTION A"], `points` "30". Recopie la situation et TOUTES les puces de contenu. Corrigé : (1) un paragraphe modèle UNIQUE
  d'au plus 150 mots qui choisit les bonnes puces (celles qui servent le but, dans la bonne direction : « slanting »), sans recopier
  les puces ; (2) un petit tableau de correction (Content / Expression and Accuracy / Slanting) disant ce qui rapporte les points ;
  (3) deux ou trois erreurs fréquentes (copier le texte, hors sujet, plusieurs paragraphes).
- **Section B, Composition** (40 points : Content and Organisation 12, Expression 16, Accuracy 12), « Choose ONE topic » : UN fichier
  PAR SUJET de composition, `numero_exercice` "B1", "B2"... (dans l'ordre a, b, c...), `groupes` ["SECTION B"], `points` "40",
  `enonce_markdown` = le sujet recopié, et sur chaque fichier la même règle :
  `regles_choix` = `[{"type":"parmi","portee":"SECTION B","repondre":1,"sur":<nombre de sujets>}]`.
  Corrigé de chaque sujet : un plan en 4 ou 5 lignes, puis une composition modèle COMPLÈTE de 450 à 500 mots (la longueur demandée),
  puis la grille (Content and Organisation / Expression / Accuracy) et 2 erreurs fréquentes. Une lettre suit le format formel ou
  informel demandé (adresse, date, salutation, corps, formule finale, nom). Respecte les noms et adresses imposés par le sujet.
  Un sujet qui repose sur des IMAGES (« one of the following pictures ») : les images sont des figures indispensables, à produire ;
  la composition modèle s'appuie sur l'une d'elles, nommée.
- Le sujet est en anglais, les contextes sont camerounais : n'invente pas de faits hors sujet.

### French 2 (Translation + Essay)

- **Question 1, Translation into French** (80 points) : fichier `numero_exercice` "1", `groupes` ["QUESTION 1"], `points` "80".
  Recopie le texte à traduire en entier. Corrigé : la traduction modèle en français correct (temps cohérents : narration au passé,
  imparfait et passé composé bien distingués), puis un tableau « point de traduction - piège - bonne forme » pour les 6 à 10 difficultés
  du texte (accord du participe, choix du temps, expressions idiomatiques, pronoms, prépositions).
- **Question 2, Essay** (80 points), « ONE of the following topics » : UN fichier PAR SUJET, `numero_exercice` "2a", "2b", "2c"
  (les lettres du sujet), `groupes` ["QUESTION 2"], `points` "80", et sur chacun
  `regles_choix` = `[{"type":"parmi","portee":"QUESTION 2","repondre":1,"sur":<nombre de sujets>}]`.
  Recopie la consigne générale (longueur : au moins 140 et au plus 150 mots, contraintes de nom et d'adresse pour un sujet donné)
  dans `enonce_intro_markdown` de chaque fichier. Un sujet à images : les images sont des figures indispensables ; décris dans le corrigé
  les six vignettes dans l'ordre, puis écris le récit. Corrigé : un essai modèle en français de 140 à 150 mots (compte-les par script,
  hors chiffres, mots entre parenthèses, noms de personnes et de lieux), avec une phrase d'analyse du temps choisi, puis les critères
  (exactitude, variété d'expressions, de verbes, de vocabulaire et d'idiomes) et 2 erreurs fréquentes.
- Consignes de l'élève et rubriques restent en anglais comme imprimées ; seules les réponses modèles sont en français.

## Thèmes (TRÈS IMPORTANT : collisions)

Tag.name est UNIQUE et PARTAGÉ avec TOUT le contenu de la plateforme, qui compte déjà plus de 2 000 thèmes d'anglais (examens
francophones : « Articles a et an », « Although vs despite »...) et des centaines de thèmes de français. Un thème GCE au même nom
FUSIONNERAIT avec eux. Règle absolue : **tout thème commence par un préfixe de matière**, `O Level English - ` ou `O Level French - `,
suivi d'un nom court en minuscules. Aucun autre thème, jamais sans préfixe.

Vocabulaire à réutiliser (en n'inventant un thème qu'en cas de vrai manque, toujours préfixé) :

- English : `O Level English - listening comprehension`, `... reading comprehension`, `... vocabulary in context`, `... word stress`,
  `... phrasal verbs`, `... idioms and proverbs`, `... verb tenses`, `... subject-verb agreement`, `... prepositions`, `... articles and
  determiners`, `... pronouns`, `... reported speech`, `... conditionals`, `... passive voice`, `... relative clauses`, `... connectors`,
  `... word formation`, `... spelling and punctuation`, `... directed writing`, `... formal letter`, `... informal letter`,
  `... narrative composition`, `... descriptive composition`, `... argumentative composition`.
- French : `O Level French - verb conjugation`, `... tenses and moods`, `... agreement`, `... gender and number`, `... articles`,
  `... pronouns`, `... relative pronouns`, `... negation`, `... prepositions`, `... comparison`, `... vocabulary`, `... idioms`,
  `... word families`, `... numbers and fractions`, `... translation into French`, `... narrative essay`, `... letter writing`,
  `... picture story`.

## Contrôle final

Le validateur de CONSIGNES.md (`valider_gce.py <dossier> --paper <1|2> --code <0530|0545> [--questions 50]`) doit afficher `OK`.
Vérifie en plus, par script, que (a) chaque `themes` commence par le préfixe de la matière, (b) chaque `regles_choix` est identique dans
tous les fichiers d'un même groupe, (c) un essai ou une composition modèle respecte la longueur demandée (compte de mots), et (d) aucun
tiret cadratin n'est présent.

## Ce que tu rends

Comme dans CONSIGNES.md, plus : la liste des questions de QCM dont la clé n'est pas certaine (avec les deux options en concurrence) et
les comptes de mots des réponses modèles.
