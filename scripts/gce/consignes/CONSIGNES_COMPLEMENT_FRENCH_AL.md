# Complément aux consignes - GCE ADVANCED LEVEL, FRENCH (code 0745)

Lis `CONSIGNES.md` (forme générale), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis `CONSIGNES_COMPLEMENT_SBE_AL.md` (matière jumelle en français : corrigés rédigés en français, thèmes préfixés, aucune citation inventée), puis ce fichier. **Ce fichier prime** pour cette matière.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"French"`, `code_matiere` `"0745"` (page de garde : « ADVANCED LEVEL », « 0745 », « Paper 2 - LITERATURE »). Autre niveau ou autre code : ne transcris rien, signale-le.
- DOSSIER = `gce-al-french-<annee>-p2-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf` ; `duree_epreuve` `"3h"` ; `numero_paper` 2.
- Sources (scans, lis chaque page en image avec Read, paramètre `pages` ; le filigrane sujetexa.com / maxiepreuves.com est à ignorer) :
  `D:\edukora\backend\ingest\_telechargements_gce_ol_manquantes_2026-10-19\sujetexa\` : `SX_AL_FRENCH_2023_P2_b.pdf` (et `_a.pdf` = même sujet, autre filigrane : sert de seconde lecture) ; `SX_AL_FRENCH_2024_P2.pdf`.
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement. Fichiers temporaires préfixés du nom du dossier, aucun `rm` de dossier.

## Structure du Paper 2 (Literature, 3 h)

« Answer THREE questions: ONE from each of Sections A, B and C. » Tous les sujets valent 20 points (8 compréhension et pertinence, 5 organisation et analyse, 5 langue, 2 présentation en 2023 ; le sujet 2024 imprime le même barème). Les réponses peuvent être en anglais ou en français, sauf le sujet 2 (poème inédit) qui exige le FRANÇAIS en 2024 (vérifie ce que dit chaque page de garde).
- Section A - Introduction to Poetry : sujet 1 (Baudelaire, *Les Fleurs du Mal*, dissertation) et sujet 2 (poème inédit : Ronsard en 2023, Charles d'Orléans en 2024, six sous-questions avec points).
- Section B - Drama : sujets 3 (Marivaux, *Les Fausses Confidences*) et 4 (Aimé Césaire, *La Tragédie du Roi Christophe*).
- Section C - Prose : sujets 5 (Victor Hugo, *Le Dernier Jour d'un condamné*), 6 (Nkoa Atenga, *L'Enfant de la révolte muette*), 7 (Francis Bebey, *Le Fils d'Agatha Moudio*).

UN fichier PAR SUJET : `numero_exercice` = le numéro imprimé (`"1"` à `"7"`), `points` `"20"`, `groupes` `["SECTION A"]`, `["SECTION B"]` ou `["SECTION C"]`, `enonce_intro_markdown` = le titre de SA SECTION en gras (ex. `**Section A - Introduction to Poetry**`, identique pour tous les sujets de la section, convention du sommaire), `introduction_markdown` = toute la consigne de la page de garde, identique partout.
`regles_choix`, identiques dans TOUS les fichiers du dossier :
`{"type":"parmi","portee":"SECTION A","repondre":1,"sur":2}`, `{"type":"parmi","portee":"SECTION B","repondre":1,"sur":2}`, `{"type":"parmi","portee":"SECTION C","repondre":1,"sur":3}`.
Le sujet 2 a six sous-questions imprimées avec points (i à vi) : une `question` par sous-question (`numero` `"i"` ... `"vi"`), `points` de chaque sous-question = l'imprimé (entier ; « 2x2=4 pts » en 2023 : 4), le poème recopié INTÉGRALEMENT et fidèlement (vers, strophes, ponctuation, mots entre parenthèses « livrée : ... ») dans `enonce_intro_markdown` après le titre de section ou dans l'énoncé de la première sous-question. Les autres sujets : une seule `question` `numero` `"1"`.
Recopie les énoncés tels qu'imprimés : accents, guillemets français « », ponctuation française. Corrige seulement les artefacts évidents du scan, jamais le sens ; un mot illisible = `incertitudes`.

## Corrigés : en FRANÇAIS, niveau Advanced Level

- Sujets de dissertation / de débat (1, 3 à 7) : un corrigé = plan apparent puis rédaction modèle COMPLÈTE d'environ 450 à 550 mots (compte par script, hors titres) : introduction (amorce, reformulation, problématique, annonce du plan), développement en deux ou trois parties avec arguments et exemples tirés de l'œuvre, conclusion ; puis une courte grille (compréhension et pertinence 8, organisation et analyse 5, langue 5, présentation 2) et deux erreurs fréquentes. Respecte la demande précise du sujet (« au moins deux poèmes », « votre expérience de la vie ET l'œuvre », « localité », etc.). Le candidat ayant le droit de répondre en anglais, le corrigé reste en français.
- Sujet 2 (poème inédit, répondre en français) : réponse modèle à chaque sous-question, appuyée sur le texte imprimé (relevés de mots, vers cités tels qu'imprimés). Vérifie par relecture les faits de métrique et de grammaire : ronsard 2023 = sonnet (14 vers : deux quatrains, deux tercets, alexandrins) ; Charles d'Orléans 2024 = rondeau (refrain « Le temps a laissé son manteau »). Compte les vers du poème imprimé avant d'écrire sur sa structure ; si l'impression ou le scan rend un vers douteux, `incertitudes`. Le 2024 vi) « Quels sont vos sentiments à la lecture ? » : réponse personnelle modèle, argumentée, sans position excentrique.
- **Exactitude littéraire** : n'écris que des faits SÛRS des œuvres (personnages, grandes situations, procédés). Œuvres : Baudelaire, *Les Fleurs du Mal* (spleen et idéal, « L'Albatros », « Correspondances », « Spleen », « L'Invitation au voyage », « Harmonie du soir », « La Beauté » : cite un poème seulement si tu es sûr du titre et de son idée, jamais de vers que tu ne recopies pas de mémoire sûre) ; Marivaux, *Les Fausses Confidences* (Dorante, Araminte, Dubois, Madame Argante, Marton, Arlequin, le Comte, Monsieur Remy ; la ruse de Dubois, la lettre, le portrait) ; Aimé Césaire, *La Tragédie du Roi Christophe* (Haïti, Christophe, la citadelle, Hugonin, Vastey, Métellus, Pétion, Madame Christophe, l'archevêque, le Président Pétion au Sud, Christophe roi au Nord, le Cap, le travail forcé, la révolte et la mort de Christophe) ; Victor Hugo, *Le Dernier Jour d'un condamné* (narrateur anonyme, Bicêtre, la Conciergerie, l'aumônier, la fille Marie, la Grève, le journal des dernières heures, plaidoyer contre la peine de mort) ; Nkoa Atenga, *L'Enfant de la révolte muette* (Nathalie et Jean Marie, d'après le sujet) ; Francis Bebey, *Le Fils d'Agatha Moudio* (Mbenda, Fida, Agatha Moudio, Sanga, Bomana, Dibango, le village de pêcheurs douala ; le chef Mbenda, la tradition, l'enfant né de Agatha, le mariage arrangé). Pour tout détail dont tu n'es pas certain, formulation générale + une ligne dans `incertitudes` (« œuvre non relue ici »). N'invente ni citation, ni numéro de page, ni détail d'intrigue douteux.
- Pas de tiret cadratin ni demi-cadratin ; guillemets français « » dans les textes de corrigé.

## Thèmes (`themes`) : préfixe obligatoire

`Tag.name` est UNIQUE et PARTAGÉ avec des centaines de thèmes de français (BEPC, Probatoire, BAC) et d'autres matières. **Tout thème commence par `A Level French - `** (suivi d'un nom court en minuscules sans accent, 1 à 3 thèmes par question) :
`A Level French - poesie de baudelaire`, `... analyse de poeme inedit`, `... theatre de marivaux`, `... theatre de cesaire`, `... roman de victor hugo`, `... roman africain`, `... dissertation litteraire`. Réutilise ces noms entre les deux papers (relis `D:\edukora\backend\ingest\_gce_staging\gce-al-french-*` avant de créer un nom : l'autre paper est traité en parallèle ; le premier agent qui a créé un nom le fait foi). Évite tout nom déjà présent dans `D:\edukora\backend\ingest\cm\gce-al-sbe-french-*` (autre préfixe, pas de collision attendue).

## Autres papers et autres années (extension du 2026-10-20)

**Sources de la vague 2** : `C:\Users\Administrateur\Documents\Epreuves\non_traites\anglophone\GCE_AL_FRENCH_<annee>_P<n>.pdf` (scans de cameroongcerevision.com, filigrane gcerevision/Kawlo à ignorer ; lis TOUJOURS la page de garde : « ADVANCED LEVEL », code 0745, session, paper ; autre niveau ou autre matière : ne transcris rien et signale-le). Sortie : `D:\edukora\backend\ingest\_gce_staging\gce-al-french-<annee>-p<n>-officiel-cameroun\`.

### Paper 2 (2019, 2020, 2021, 2022, 2025, 2026)

Même contrat que 2023/2024 ci-dessus. Les œuvres au programme, la numérotation et le nombre de sujets peuvent changer d'une année à l'autre : transcris ce qui est imprimé, adapte `groupes` et `regles_choix` à la consigne de la page de garde (« ONE from each of Sections A, B and C », ou autre), et dis-le dans `incertitudes`. Pour une œuvre nouvelle (jamais vue dans les corrigés ci-dessus), formulation générale, aucun fait précis non sûr, ligne « œuvre non relue ici ». Dossier d'exemple fini : `D:\edukora\backend\ingest\cm\gce-al-french-2023-p2-officiel-cameroun\`.

### Paper 1 (QCM, 1h30, 50 questions attendues)

DOSSIER = `gce-al-french-<annee>-p1-officiel-cameroun` ; `duree_epreuve` lue sur la page de garde ; UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (nombre réel imprimé : si le sujet est incomplet, dis-le et `--questions N` du validateur), `type_reponse` `"qcm"`, `choix` = lettres MINUSCULES a-d (le sujet imprime A-D), `reponse_correcte` une lettre minuscule, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Le sujet est en FRANÇAIS (rubriques « Concepts et notions littéraires », « Grammaire », « Vocabulaire et expressions », éventuellement un texte de compréhension) : recopie tel qu'imprimé (accents, mots soulignés : mets-les en `*italique*` ou `__gras__` pour garder l'information « le mot souligné », et dis-le dans l'énoncé si besoin). Un passage commun à plusieurs questions : recopié UNE fois dans la première question du groupe (« **Texte pour les questions 40 à 45** »), les suivantes renvoient à lui (« (Texte des questions 40 à 45 ci-dessus) »). Les traits de remplissage `___` des blancs sont recopiés `____`.
**Les clés sont à établir toi-même, sur la langue** (grammaire, conjugaison, figures de style, notions littéraires), jamais « au flair » : relis l'énoncé en insérant chaque option. Une question dont la clé imprimée ou les options sont défectueuses, ou à deux réponses défendables : `node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>` (question ouverte, réponse attendue dans le corrigé, écart noté dans `incertitudes`). Une question qui suppose l'œuvre au programme (pas le texte imprimé) : ouverte aussi, sauf si la réponse est certaine. Corrigés en FRANÇAIS, brefs : la règle en une phrase, pourquoi la bonne option est juste, le piège de l'option voisine, terminés par « **Réponse : C.** ».
**Thèmes P1 (une liste FERMÉE, partagée entre tous les agents ; 1 à 2 par question)** : `A Level French - figures de style`, `A Level French - notions litteraires`, `A Level French - grammaire de la phrase`, `A Level French - conjugaison et accord`, `A Level French - vocabulaire et expressions`, `A Level French - comprehension de texte`. N'en crée un autre que si aucun ne convient (relis alors `D:\edukora\backend\ingest\_gce_staging\gce-al-french-*` d'abord).

### Paper 3 (Essay writing and Translation, 3 h)

DOSSIER = `gce-al-french-<annee>-p3-officiel-cameroun` ; `duree_epreuve` `"3h"`. Consigne type : « Answer only ONE essay question and ALL translation questions » ; barème de l'essai (compréhension 25, organisation 25, langue 40, présentation 10 = 100) et traduction 100 (lis la page de garde de CHAQUE année : les chiffres varient).
- **Question 1 : rédaction** (n sujets, « about 350 words », 100 points chacun) : UN fichier PAR SUJET, `numero_exercice` `"1"`, `"2"`... (numéros imprimés), `groupes` `["QUESTION 1"]`, `points` `"100"`, `regles_choix` `[{"type":"parmi","portee":"QUESTION 1","repondre":1,"sur":<n>}]` identique partout. Recopie le sujet EN ENTIER, citation, source et question compris. `enonce_intro_markdown` = `**Question 1 - Essay writing**` + la consigne de longueur.
- **Question 2 : traduction** (n textes, tous obligatoires, « Translate ALL ») : UN fichier PAR TEXTE, `numero_exercice` `"2.1"`, `"2.2"`... (numéros imprimés), `groupes` `["QUESTION 2"]`, aucune règle (tout est obligatoire), `points` `""` (les « 100 marks » imprimés valent pour l'ensemble : à dire dans `introduction_markdown` et `incertitudes`), `enonce_intro_markdown` = `**Question 2 - Translation**`. Recopie chaque texte à traduire EN ENTIER, sans la mention « (Inédit) » ni les numéros de revue qui ne font pas partie du texte (garde-les entre parenthèses si le sujet les imprime : mieux vaut recopier que perdre).
- **Corrigés** : essais en FRANÇAIS, essai modèle COMPLET d'environ 350 mots (330 à 380, compte par script hors titres) avec plan apparent, arguments, exemples camerounais précis mais sûrs, puis critères (25/25/40/10) et deux erreurs fréquentes. Traductions : traduction modèle COMPLÈTE et fidèle (français correct ou anglais correct selon le sens), suivie d'un tableau « difficulté / piège / bonne forme » de 6 à 10 lignes (accords, temps, faux amis, expressions, ponctuation). Pas de fait politique ou statistique inventé.
- **Thèmes P3** : `A Level French - redaction argumentative`, `A Level French - traduction vers le francais`, `A Level French - traduction vers l'anglais`, `A Level French - expression ecrite et reflexion sur la societe` (pour un sujet de société ou d'actualité), sans autre nom sauf nécessité.

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM. Pas de figures attendues.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0745 [--questions 50 pour le P1]
```

Il doit afficher `OK`. Vérifie en plus par script que chaque `themes` commence par `A Level French - ` et que les `regles_choix` sont identiques dans tous les fichiers du dossier. Puis la SECONDE PASSE obligatoire et DÉCLARÉE dans ton rapport (rouvrir chaque page, comparer chaque énoncé et chaque point imprimé, relire les corrigés pour les faits). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.

## Ce que tu rends

Dossier, nombre de fichiers et de questions, sortie du validateur, `incertitudes`, passages douteux, thèmes créés, seconde passe faite oui/non.
