---
name: "correction-experte"
description: "Rédige des corrigés d'exercices et d'épreuves (BEPC/BFEM, Probatoire, BAC, tout niveau/matière du système éducatif francophone d'Afrique - Cameroun, Sénégal, Côte d'Ivoire, Bénin et au-delà) d'un niveau pédagogique supérieur à celui d'un répétiteur classique. À utiliser dès que l'utilisateur demande de corriger un exercice, une épreuve complète (PDF à plusieurs exercices), rédiger un corrigé, préparer une fiche de révision, expliquer un sujet d'examen, ou produire du contenu pédagogique pour la vente sur la plateforme de soutien scolaire - même sans le mot corrige (ex. voici un sujet de maths Terminale C qu'en fais-tu, fiche sur les suites numériques, traite les PDF de ce dossier). Génère également les cours et fiches de révision associés à une notion (mode cours). Gère aussi le mode traitement en lot/automatisé (dossier de PDF surveillé) en produisant une sortie JSON structurée par exercice, plus un cours complet par rappel de méthode identifié, le tout prêt pour ingestion en base de données."
---

# Correction Experte d'Épreuves et d'Exercices

## Objectif

Produire des corrigés dont la qualité pédagogique dépasse celle d'un répétiteur moyen : pas seulement "la bonne réponse", mais la méthode transférable, les pièges identifiés, et les automatismes qu'un examinateur valorise. Le corrigé doit donner à l'élève une compétence réutilisable sur tout exercice du même type, pas seulement la solution de celui-ci.

---

## Référentiel : le système scolaire dépend du pays traité

Edukora dessert plusieurs pays d'Afrique francophone, pas seulement le Cameroun. La nomenclature des examens et des séries n'est pas universelle : un même code de série peut ne pas exister d'un pays à l'autre, et certains pays n'ont pas de niveau d'examen intermédiaire entre le collège et le lycée.

### Déterminer le pays traité

- **Mode automatisation** : le pays se déduit du dossier source de l'épreuve, convention `ingest/<code_pays>/<epreuve>/...` (ex. `ingest/sn/bac-maths-2024/...` = Sénégal). Repérer ce code avant le Cadrage (étape 1) : il détermine quel référentiel ci-dessous s'applique, et il est recopié tel quel dans le champ `pays` de chaque JSON produit (exercices et cours).
- **Mode interactif** : si le pays n'est pas explicite dans la demande de l'utilisateur ou dans l'épreuve elle-même (en-tête ministériel, ex. « MINESEC » pour le Cameroun, « Office du Bac » pour le Sénégal), le demander plutôt que de supposer le Cameroun par défaut.

### Référentiels confirmés

| Pays (code dossier) | Examens | Séries |
|---|---|---|
| Cameroun (`cm`) | BEPC (fin de 3e, pas de série), Probatoire (fin de Première), BAC (Terminale) | A (Lettres-Philo), SES (Sciences Économiques et Sociales), C (Maths), D (Sciences), E (Mathématiques et Techniques), TI (Techniques Industrielles), COM (Techniques Commerciales et de Gestion) |
| Sénégal (`sn`) | BFEM (fin de collège - jamais « BEPC », utiliser le code `bfem` en sortie JSON, voir Mode automatisation), BAC (pas de Probatoire) | L (Lettres), S (Sciences), G (Gestion) |
| Côte d'Ivoire (`ci`) | BEPC (fin de collège), BAC (pas de Probatoire) | A1 (Lettres-Philo), A2 (Lettres-Langues), C (Maths-Sciences Physiques), D (Maths-Sciences de la Vie et de la Terre). Les séries techniques (E, F1-F7, G1, G2) existent dans le vrai système ivoirien mais ne sont pas encore intégrées côté plateforme - si l'épreuve relève d'une série technique, le signaler dans `incertitudes` plutôt que d'assigner un code au hasard |
| Bénin (`bj`) | BEPC (fin de collège), BAC (pas de Probatoire) | A (Lettres), C (Mathématiques-Physique), D (Sciences Expérimentales), G (Économie-Gestion) |

**Cameroun - codes de série : jamais de sous-série inventée.** La Série A camerounaise s'écrit `"A"` (avec `filiere_serie_a: "abi"` pour l'A4 Bilingue), jamais `"A1,A2,A3,A4,A5"` ni `"A1"` : A1/A2 sont des codes ivoiriens (tableau ci-dessus) et l'ingestion échoue avec « Cursus introuvable pour pays=Cameroun, examen='probatoire', série='A1' ». Constaté sur probatoire-a-informatique-theorique-2026 (3 exercices rejetés). Un en-tête qui annonce « Séries A1 à A5 » pour le Cameroun désigne la Série A.

**Coefficients indicatifs Terminale, Cameroun uniquement** (pour calibrer l'exigence quand le coefficient n'est pas indiqué sur l'épreuve) :
- Série C : Maths (coeff élevé), Physique-Chimie, Français, Philosophie, Anglais
- Série D : Maths, Physique-Chimie, SVT (coeff élevé), Français, Philosophie, Anglais
- Série A : Français, Philosophie, Histoire-Géo, Anglais, Maths (coeff réduit)
- Série SES : Économie, Droit, Maths, Français, Philosophie
- Série E : Mathématiques (coeff élevé), Techniques/Sciences de l'Ingénieur, Physique-Chimie

Pour les autres pays, utiliser le coefficient indiqué sur l'épreuve elle-même quand il est disponible ; à défaut, traiter l'exercice avec la même rigueur que les matières à coefficient élevé plutôt que de deviner une pondération.

### Pays sans référentiel confirmé

Les dossiers `ingest/` existent aussi pour d'autres pays (Togo, Burkina Faso, Tchad, Gabon, Centrafrique, RD Congo, Congo-Brazzaville, Guinée-Bissau, Mali, Niger) dont le référentiel réel n'a pas encore été vérifié - la base de données contient pour l'instant, à titre provisoire, une copie du référentiel camerounais qui n'est pas garantie correcte pour ces pays. Ne jamais réutiliser silencieusement les codes camerounais pour l'un de ces pays : le nom de l'examen de fin de collège, l'existence d'un niveau intermédiaire et les codes de série peuvent tous différer. Si une épreuve de l'un de ces pays doit être traitée avant que son référentiel ne soit confirmé, signaler explicitement dans `incertitudes` (« référentiel non confirmé pour ce pays - série/examen à valider avant publication ») et, en mode interactif, demander confirmation à l'utilisateur plutôt que de trancher.

Utiliser ce référentiel lors du **Cadrage** (étape 1) pour identifier précisément le pays, l'examen visé, la série et le coefficient, afin de régler le niveau d'exigence en conséquence.

---

## Processus en 5 étapes (à suivre pour chaque exercice/épreuve)

### 0. Segmentation (uniquement si l'entrée est une épreuve complète contenant plusieurs exercices, ex. un PDF scanné ou natif)
Avant tout traitement, découper l'épreuve en unités indépendantes :
- Identifier chaque exercice/partie via sa numérotation explicite ("Exercice 1", "Partie A", "Situation-problème") et son nombre de points s'il est indiqué
- Repérer les sous-questions (1.a, 1.b, 2...) comme unités à corriger dans l'ordre, mais rattachées à leur exercice parent pour le cadrage (un exercice = un cadrage commun, sauf s'il change explicitement de matière/thème en cours de route)
- Si le PDF est scanné, lire chaque page comme une image et reconstituer le texte et les formules avec la même exigence de fidélité que pour un corrigé (ne jamais deviner une donnée illisible - signaler "donnée illisible à la page X" plutôt que d'inventer une valeur plausible)
- Traiter ensuite chaque exercice comme une unité indépendante en répétant les étapes 1 à 5 ci-dessous
- Si l'épreuve contient des figures, appliquer la section « Traitement des figures et images » avant de corriger



Traitement des figures et images (obligatoire dès qu'une épreuve contient des éléments graphiques)

Une épreuve peut contenir des figures indispensables à la résolution : figure géométrique codée, courbe à exploiter, tableau scanné, schéma de circuit, document SVT, carte, graphique économique. Un pipeline qui extrait uniquement le texte perd ces figures silencieusement et produit un corrigé faux ou incomplet. Les règles suivantes s'appliquent en mode interactif comme en mode automatisation.

1. Détection et inspection visuelle - jamais d'extraction texte seule


Avant tout traitement, détecter les pages contenant des images. En mode automatisé : PyMuPDF (page.get_images() et page.get_drawings() - ce second appel détecte les figures vectorielles natives, invisibles pour get_images()). Un PDF entièrement scanné compte comme "toutes pages avec image".
Toute page contenant au moins une image ou un dessin vectoriel significatif doit être lue visuellement (rendu de la page en image, jamais extraction texte seule). Le texte extrait sert de support, la lecture visuelle fait foi pour les figures.
Exclure les éléments décoratifs : logos, en-têtes d'établissement, cachets, filigranes. Ils ne sont ni extraits ni référencés.
Si une figure indispensable est illisible (scan dégradé, résolution insuffisante), ne jamais deviner son contenu : signaler "figure illisible, page X, exercice Y" dans incertitudes et corriger uniquement les questions qui n'en dépendent pas.


2. Extraction des figures - crops PNG du PDF original

Pour chaque figure rattachée à un exercice :


Découper la zone de la figure depuis le rendu de la page (crop) et l'enregistrer en PNG. Résolution cible : rendu à un zoom de 2x minimum (Matrix(2, 2) dans PyMuPDF) pour rester lisible sur mobile.
Nommage : <nom_epreuve>_exercice_<numero>_fig_<index>.png, index à partir de 1 dans l'ordre d'apparition. Fichiers placés dans le même dossier que les JSON de l'épreuve.
Le crop inclut la légende et les codages de la figure (mesures, angles droits, flèches) mais exclut le texte d'énoncé environnant.
Une figure partagée par plusieurs exercices est extraite une fois par exercice qui l'utilise (chaque JSON reste autonome pour l'ingestion).


3. Référencement dans le Markdown et le JSON


Dans enonce_markdown (et corrige_markdown si le corrigé renvoie à la figure), insérer le placeholder à l'endroit exact où la figure apparaît :
![fig-1](<nom_epreuve>_exercice_<numero>_fig_1.png)
Ajouter au JSON de chaque exercice le champ figures :


json"figures": [
  {
    "id": "fig-1",
    "fichier": "BAC-C-2024-MATHS_exercice_3_fig_1.png",
    "page_source": 2,
    "type": "figure geometrique | courbe | tableau | schema | document | carte | graphique",
    "legende": "description courte de ce que montre la figure",
    "indispensable": true,
    "lisibilite": "bonne | partielle | illisible"
  }
]


indispensable: true signifie que l'exercice ne peut pas être résolu sans la figure. Si indispensable: true et lisibilite: "illisible", l'exercice entier passe en incertitude majeure : le mentionner en premier dans incertitudes.
Liste vide "figures": [] si l'exercice n'en contient aucune - le champ est toujours présent en mode automatisation.


4. Lecture graphique - règles de rigueur

Quand une question exige de lire des valeurs sur une courbe ou un graphique :


Annoncer explicitement qu'il s'agit d'une lecture graphique : "Par lecture graphique, f(2) ≈ 3" - jamais un signe "=" strict pour une valeur lue.
Donner la précision de lecture cohérente avec la graduation visible (ex. à 0,5 près si le carreau vaut 1).
Croiser avec le calcul chaque fois qu'une expression de la fonction est disponible : la lecture graphique confirme le calcul, elle ne le remplace pas. En cas d'écart, le calcul prime et l'écart est signalé.
Toute valeur lue qui conditionne la suite du corrigé est listée dans incertitudes avec sa précision (ex. "x₀ ≈ 1,5 lu sur la courbe, précision ±0,25").


5. Figures produites dans le corrigé - le tracé demandé doit être réalisé, jamais seulement décrit

Quand le corrigé exige lui-même un tracé (construction géométrique, courbe de fonction, schéma SVT légendé, graphique économique, circuit ou montage en physique) : produire réellement l'image, dans tous les cas, pas seulement l'expliquer en mots. Une description verbale de la construction, aussi précise soit-elle, ne dispense jamais de la figure elle-même - l'élève doit pouvoir comparer son propre tracé à un tracé correct, pas seulement lire comment le refaire.

Produire la figure avec un outil de tracé précis, à partir des valeurs réellement établies dans le corrigé (coordonnées, angles, distances, graduations) - jamais une image approximative :
- Courbe de fonction ou graphique (économie, physique) : générer via un script (ex. Python/matplotlib) à partir de l'expression ou des données du corrigé, avec axes gradués et légendés.
- Construction géométrique codée (figure à compléter, image d'une transformation, tracé à la règle et au compas) : générer en SVG ou via le même outil de tracé, en reprenant exactement les codages (angles droits, mesures, égalités de longueur) et les points calculés dans le corrigé.
- Schéma SVT : appliquer les règles de la section "Sciences de la Vie et de la Terre" plus bas (titre, légendes numérotées, flèches et sens) et le produire comme figure, pas seulement le décrire.

Enregistrer le résultat en PNG, même convention de nommage que les figures extraites : <nom_epreuve>_exercice_<numero>_fig_<index>.png, dans le même dossier que les JSON de l'épreuve. Insérer le placeholder ![fig-X](...) dans corrige_markdown à l'endroit exact où la construction est demandée, et ajouter l'entrée correspondante dans figures avec "origine_figure": "corrige" en plus des champs standard ; les figures extraites de l'épreuve portent "origine_figure": "enonce".

Décrire malgré tout la construction pas à pas dans le corrigé (mêmes règles que les calculs : aucune étape masquée) : la description reste obligatoire en complément de l'image, jamais à sa place - elle donne à l'élève la méthode pour reproduire le tracé lui-même, l'image lui donne le résultat exact auquel se comparer.

Le tableau de variations reste en LaTeX (\begin{array}), jamais en image : cette règle ne concerne que les tracés géométriques, courbes, schémas et graphiques, pas les tableaux.


6. Vérification spécifique aux figures (à ajouter à l'étape 4 - Vérification renforcée)


Vérifier que chaque placeholder ![fig-X](...) du Markdown correspond exactement à une entrée figures[].id et à un fichier PNG réellement écrit sur disque, et réciproquement (aucune figure orpheline, aucun placeholder mort).
Relire chaque crop produit : la figure est-elle entière, droite, lisible, débarrassée du texte d'énoncé voisin ?
Vérifier que les valeurs numériques utilisées dans le corrigé correspondent bien aux codages visibles sur la figure (une mesure lue sur la figure prime sur une valeur supposée).
Vérifier qu'aucun tracé demandé par le corrigé (construction, courbe, schéma, graphique) n'est resté seulement décrit en texte sans image produite - un corrigé qui explique un tracé sans le réaliser est incomplet, quelle que soit la qualité de la description.


### 1. Cadrage
Identifier avant de rédiger :
- Pays traité (voir **Référentiel** ci-dessus - détermine la nomenclature valide pour tout ce qui suit)
- Matière, niveau (6e à Terminale), série si pertinente pour ce pays, examen visé. **Relire l'intégralité de l'en-tête/bandeau du sujet source pour la série, jamais seulement la série demandée au départ ou celle qui saute aux yeux sur le nom du fichier fourni** : un en-tête qui porte « Séries : C et E » (ou toute liste de plusieurs codes) engage TOUTES les séries listées dans `serie`, même si une seule a été demandée ou évoquée en amont. Voir le « Piège déjà rencontré » sous la règle `serie` en mode automatisation plus bas pour deux cas réels manqués de cette façon.
- Nature de l'épreuve (champ `origine` en mode automatisation - sa nature, pas son pays) : épreuve officielle, examen blanc, sujet zéro (spécimen officiel, pas un entraînement), ou épreuve propre à un établissement (en-tête d'établissement scolaire plutôt que ministériel, mention « Blanc ») - noter le nom de l'établissement le cas échéant
- Consulter le **Référentiel** ci-dessus pour vérifier les coefficients (Cameroun) et ajuster l'exigence
- Type d'exercice (problème classique, question de cours, dissertation, commentaire, etc.)
- Si un barème officiel est fourni ou disponible, l'utiliser pour calibrer le niveau d'exigence et la pondération des étapes
- **Ouvrir le programme officiel de la matière, avant de rédiger quoi que ce soit** (facultatif : `savoir_officiel` est en standby depuis le 2026-09-18, voir sa spécification plus bas - le remplir n'est plus attendu) : lire `backend/programme/fixtures/programme_officiel_cm_<matiere>.json`, y repérer les modules de la (classe, série) traitée, et garder leur liste de savoirs sous les yeux pendant toute la correction. C'est cette liste - jamais la mémoire, jamais une reconstruction de tête - qui alimente le champ `savoir_officiel` de chaque sous-question. Un `null` n'est plus un défaut tant que le rattachement au référentiel est en standby.

### 2. Identification du motif (pattern)
Avant de résoudre, nommer le type d'exercice s'il correspond à un motif classique du programme ("ceci est un exercice standard d'étude de fonction avec asymptote oblique", "ceci suit le schéma classique de la dissertation philosophique en 3 parties dialectiques"). Un élève qui reconnaît le motif retient la méthode bien au-delà de cet exercice précis.

### 3. Rédaction selon le template obligatoire
Voir section Template ci-dessous - appliquer à chaque exercice, sans exception de forme (le contenu de chaque bloc peut être court si non pertinent, mais la structure reste fixe).

**Règle absolue - aucune étape masquée** : chaque étape intermédiaire d'un calcul, d'une démonstration ou d'un raisonnement doit apparaître explicitement, y compris les étapes "évidentes" pour un expert (développement d'un produit, simplification d'une fraction, factorisation, calcul d'un conjugué, application numérique intermédiaire). Interdiction des formulations qui sautent une étape : "on en déduit directement que…", "un calcul immédiat donne…", "après simplification…" sans montrer la simplification elle-même. Un élève doit pouvoir reconstituer chaque ligne à la main sans avoir à deviner ce qui s'est passé entre deux lignes. Le seul cas où une étape peut être abrégée est un calcul mental trivial explicitement qualifié comme tel (ex. "2+2=4"), jamais un calcul qui mobilise une compétence du programme.

**Clause - angles et valeurs remarquables redémontrés, pas récités** : pour identifier un angle (argument d'un complexe, angle d'une similitude, valeur trigonométrique remarquable), toujours calculer cos(θ) et sin(θ) séparément puis identifier θ à partir de ces deux valeurs, plutôt que d'affirmer directement "arg(...) = ..." comme un fait mémorisé. Exception : si la valeur a déjà été établie plus tôt dans le même corrigé, on peut la citer en la référençant explicitement ("comme établi en question X").

**Clause - justification par propriété locale plutôt que règle générale non prouvée** : quand un raisonnement peut s'appuyer soit sur une propriété générale invoquée sans démonstration (ex. "un cercle centré au centre d'une similitude a une image de même centre"), soit sur un fait local justifiable en une ligne (ex. "A est le centre de la similitude, donc A est un point invariant, donc son image est A"), toujours préférer la seconde option quand elle est disponible.

### 4. Vérification renforcée (obligatoire pour matières scientifiques : maths, physique-chimie, SVT quantitatif)
- Refaire le calcul indépendamment, de zéro, sans relire la première rédaction pendant cette vérification
- Vérifier unités, ordres de grandeur, cohérence dimensionnelle
- Si un barème est disponible, vérifier que chaque étape rédigée correspond à un point du barème
- En cas de doute réel sur un résultat (calcul complexe, ambiguïté de l'énoncé), le signaler explicitement à l'utilisateur plutôt que de trancher silencieusement - ne jamais laisser une incertitude non signalée dans un corrigé destiné à la vente

### 5. Relecture pédagogique finale
Se demander : "Un élève moyen qui lit uniquement ce corrigé, sans prof, comprend-il non seulement la réponse mais aussi comment y arriver seul la prochaine fois ?" Si non, enrichir avant de livrer.

### Exemple illustratif - piège classique des asymptotes log-exponentielles
Pour une fonction du type $f(x) = \ln(e^x + \text{terme}) - x$, l'intuition suggère souvent une asymptote oblique liée à $y=x$, parce que $\ln(e^x+\cdots)$ "ressemble" à $x$ pour x grand. C'est trompeur : il faut réécrire $f(x)$ pour faire apparaître la limite réelle (ex. factoriser par $e^x$ dans le logarithme, utiliser $x=\ln(e^x)$ pour regrouper les termes), puis appliquer les croissances comparées. Le résultat peut être une asymptote horizontale (ex. y=0) alors que l'intuition de départ pointait vers une oblique. Toujours démontrer, jamais déduire l'asymptote par ressemblance visuelle de la formule.

---

## Template obligatoire pour chaque exercice

Pour chaque exercice ou sous-question corrigée, structurer ainsi. En mode automatisation, une sous-question correspond directement à une entrée de `questions` dans le JSON (voir plus bas) : le template s'applique à chacune indépendamment, pas une seule fois pour l'exercice entier - un exercice à 3 sous-questions produit 3 corrigés structurés séparément, chacun avec son propre Rappel de méthode/Piège/Conseil si pertinent.

1. **Rappel de la méthode/notion mobilisée** (2-4 lignes) - le principe général avant l'application au cas précis
2. **Corrigé détaillé étape par étape** - chaque étape justifiée, pas seulement calculée ; formulations complètes, pas de raccourcis elliptiques
3. **Piège à éviter** (uniquement si pertinent pour cet exercice) - l'erreur que les élèves commettent typiquement sur ce type de question
4. **Conseil** (uniquement si pertinent) - gain de temps le jour J, formulation qui rapporte des points au barème, méthode de vérification rapide du résultat

Ne pas forcer les points 3 et 4 s'ils n'apportent rien de réel sur un exercice donné - un piège ou conseil inventé pour remplir le template dégrade la qualité perçue plus qu'il ne l'améliore.

**Intitulé fixe** : toujours utiliser exactement le mot "Conseil" pour le bloc 4 (jamais "Conseil de prof", "Conseil malin", "Astuce" ou variante) - cohérence de marque sur l'ensemble du contenu vendu.

**Format Markdown imposé, sans exception** : les blocs 1, 3 et 4 (Rappel de méthode, Piège à éviter, Conseil) doivent systématiquement commencer par un titre de niveau 3, avec l'intitulé exact et rien d'autre sur la ligne de titre :

```
### Rappel de méthode
<texte du rappel>

### Piège à éviter
<texte du piège>

### Conseil
<texte du conseil>
```

Ne jamais utiliser une autre forme (ni "**Rappel de méthode.** texte...", ni liste à puces, ni gras seul) : la plateforme détecte ces trois blocs uniquement à partir de ce titre de niveau 3 exact pour les mettre en valeur visuellement (encadré coloré) dans le corrigé publié. Un format différent fait perdre cette mise en valeur silencieusement.

**Le contenu sous `### Rappel de méthode` est une règle générale, jamais un extrait de la réponse** : ce qui suit ce titre est le principe, la méthode, la définition ou le théorème mobilisé, formulé pour rester vrai sur n'importe quel exercice du même type - jamais une phrase qui ne vaut que pour CET exercice (valeurs numériques de l'énoncé, notation indexée propre au corrigé, résultat chiffré obtenu ici). Une phrase qui cesserait d'être vraie une fois les données de cet exercice changées n'appartient pas à ce bloc : elle va dans le point 2 (Corrigé détaillé étape par étape), jamais dans le Rappel. Ce même texte est ensuite recopié verbatim dans `questions[].rappels_de_methode[].contenu_markdown` en mode automatisation (voir plus bas) : un Rappel réduit à un extrait de la réponse y est donc doublement fautif - inutilisable pour un autre exercice, et sans valeur pédagogique propre une fois recopié isolément dans le champ JSON.

**La réponse à la question n'est JAMAIS placée sous `### Rappel de méthode` - y compris pour les questions « Définir… », « Donner le rôle de… », « Citer… », « Dire de quel type… »** : pour ces questions la réponse EST une définition, une liste ou une phrase de cours, et c'est précisément là qu'on est tenté de la ranger dans le Rappel, puisqu'elle « ressemble » à une règle. Ne pas le faire. La réponse rédigée pour CETTE question (la définition du terme demandé, l'énumération, la justification avec les données de l'énoncé) va dans le corps du corrigé, en clair, sans titre. Le Rappel qui la suit dit COMMENT répondre à ce type de question, pas CE QUE l'on répond. Exemples :
- « Définir : système d'exploitation » → corps : « Un **système d'exploitation** est le logiciel de base qui… » ; Rappel : « Pour définir un système d'exploitation, indique sa nature, son rôle et cite un ou deux exemples. » (jamais la définition elle-même sous le titre).
- « Donner le nombre de lignes de pixels » → corps : « Le nombre de lignes est de **600 pixels**… » ; Rappel : « Pour trouver le nombre de lignes, lis la définition écrite « lignes × colonnes » : la première valeur est le nombre de lignes. »
- « Citer trois caractéristiques d'achat d'un disque dur » → corps : les trois caractéristiques ; Rappel : la démarche pour les retrouver.

**Un corrigé n'est jamais composé uniquement de blocs `### Rappel de méthode`** : chaque sous-question doit avoir au moins un paragraphe de réponse en clair, hors de tout bloc Rappel. Erreur constatée : sur toute une épreuve (probatoire-blanc-ti-SI-bayangam-2023, 31 sous-questions sur 5 exercices), chaque `corrige_markdown` ne contenait qu'un ou plusieurs `### Rappel de méthode` dont le texte était la réponse elle-même, et les `contenu_markdown` des rappels en étaient des extraits tronqués - la plateforme ne pouvait plus rattacher les liens « Voir le cours complet » à leur encadré (tous entassés en fin d'exercice), et l'élève voyait « Rappel de méthode » là où se trouvait la correction. Test de contrôle avant de livrer chaque sous-question : si on supprime tous les blocs `### Rappel de méthode` du `corrige_markdown`, il doit rester la réponse complète ; si le Rappel contient des valeurs propres à l'énoncé (« 600 pixels », « M. MOTCHO », « 2,7 GHz »), c'est une réponse déguisée, pas un rappel.

**Le bloc `### Rappel de méthode` reste UN SEUL paragraphe, sans aucune ligne blanche à l'intérieur** : la plateforme détecte la fin de ce bloc à la première ligne blanche rencontrée après le titre - tout ce qui suit cette ligne blanche (deuxième paragraphe compris) n'est jamais mis en valeur dans l'encadré, et le lien "Voir le cours complet" qui s'y rattache automatiquement ne le retrouve plus. Le principe général (2-4 lignes, point 1) et son application chiffrée au cas précis (point 2, "Corrigé détaillé étape par étape") sont donc deux paragraphes TOUJOURS distincts : le second ne doit jamais rejoindre le premier sous le même titre, même séparé d'une seule ligne blanche - il commence directement après, sans titre propre, à la suite naturelle du bloc Rappel. Erreur constatée : un Rappel rédigé sur deux paragraphes - le principe général, une ligne blanche, puis l'application numérique à cet exercice précis (valeurs, notation indexée du type $C_1, C_2...$) - au lieu de couper après la seule phrase de principe général (bac-blanc-c-d-e-chimie-2026-cameroun exercice 2, sous-question 1a ; scan corpus du 2026-08-31, lien "Voir le cours complet" alors introuvable sous son propre encadré). La même épreuve traitait pourtant correctement des sous-questions voisines (le principe général seul dans le Rappel, l'application détachée juste après) : relire chaque bloc Rappel une fois rédigé pour vérifier qu'aucune ligne blanche n'y apparaît avant son titre suivant (`### Piège à éviter`/`### Conseil`) ou avant la sous-question suivante.

**Correspondance stricte entre `rappels_de_methode` et les titres du corrigé.** Pour chaque sous-question, le nombre d'objets dans `questions[].rappels_de_methode` est égal au nombre de titres `### Rappel de méthode` de son `corrige_markdown`, chacun dans son PROPRE bloc (un titre + un paragraphe par rappel : jamais deux rappels fusionnés sous un seul titre). Trois défauts constatés, tous bloquants au tunnel (« N rappel(s) en base mais 0 titre(s) `### Rappel de méthode` dans le corrigé ») : (a) les rappels sont déclarés dans le JSON mais leur texte n'apparaît nulle part dans le corrigé (bac-ti-programmation-2024 : 19 ; bac-ti-SI-2024 : 21) ; (b) le rappel est écrit en ligne « **Rappel de methode.** texte… » au lieu du titre de niveau 3 (bac-ti-programmation-2025, bac-ti-reseau-2023, probatoire 2026, vogt-2021 : 50+) ; (c) deux rappels d'une même sous-question réunis dans un bloc unique (vogt-2021 q1, reseau-2023 ex.2/3 : « 3 rappels, 2 titres »). Le titre s'écrit avec l'accent : `### Rappel de méthode`. (d) **`contenu_markdown` différent du bloc du corrigé** : le rappel déclaré contient la RÉPONSE (ou une reformulation) alors que le bloc du corrigé contient la méthode - la plateforme apparie par préfixe exact, ne trouve aucun bloc et entasse tous les « Voir le cours complet » en fin d'exercice au lieu de les placer sous chaque encadré (constaté le 2026-09-20 : 56 rappels sur 5 lots, reseau-2023, probatoire 2026 A et C/D/E, programmation-2025, vogt-2021). Règle : copier-coller, caractère pour caractère, le paragraphe qui suit le titre dans `contenu_markdown` ; si deux rappels partagent un bloc, ils portent le même texte.

**Ne pas fusionner vérification et conseil** : la vérification renforcée de l'étape 4 du processus (ex. recalcul indépendant d'une distance pour confirmer un rayon) est une étape de fiabilité interne, pas un conseil pédagogique pour l'élève. Si elle a une valeur pédagogique réelle pour l'élève (ex. "voici comment vous-même vérifier votre résultat le jour J"), elle peut apparaître dans le bloc Conseil - mais alors reformulée du point de vue de l'élève, pas comme un aparté d'auto-contrôle du rédacteur.

---

## Spécificités pédagogiques par matière

Ces règles s'appliquent en plus du template générique. Elles reflètent les attentes concrètes des correcteurs du MINESEC.

### Mathématiques (toutes séries)
- Cite explicitement chaque théorème ou propriété utilisé (nom + énoncé bref si non trivial)
- Tableau de variations obligatoire pour toute étude de fonction ; branches infinies systématiquement traitées
- Pour les calculs de limites : écrire la forme indéterminée avant de la lever
- Encadre les formules-clés en début d'exercice pour que l'élève les mémorise

### Physique-Chimie
Ces règles pédagogiques s'appliquent aussi bien à une épreuve classée `"matiere": "Physique"` ou `"Chimie"` qu'à une épreuve réellement mixte classée `"Physique-Chimie"` (voir la règle `matiere` du mode automatisation plus haut - Physique et Chimie sont deux matières distinctes dans le JSON produit, ce titre de section regroupe simplement leurs conventions rédactionnelles communes).

- Rappelle les unités SI à chaque grandeur dès sa première apparition
- Démarche obligatoire : loi (formule littérale) → application numérique → résultat **avec unité**
- Vérification des ordres de grandeur obligatoire
- Pour la chimie : équilibre des équations avant tout calcul stœchiométrique

### Sciences de la Vie et de la Terre (SVT)
- Vocabulaire strictement conforme aux termes du programme officiel
- Tout schéma demandé : titre + légendes numérotées + flèches et sens - produit comme figure réelle (voir « Figures produites dans le corrigé »), jamais seulement décrit dans le texte
- Respecter le format imposé par le sujet (texte, schéma, tableau) - ne pas substituer un format à un autre

### Français
- **Dissertation** : introduction (accroche + problématique + annonce du plan) ; développement en 2 ou 3 parties avec exemples tirés de la littérature francophone ; conclusion (bilan + ouverture). L'introduction et la conclusion sont notées séparément par les correcteurs.
- **Explication de texte** : introduction (situation du passage), explication linéaire ou thématique selon la consigne, conclusion
- Signaler explicitement quand plusieurs plans sont académiquement valables

### Philosophie
- **Problématisation obligatoire** en introduction : montrer la tension ou contradiction non immédiatement visible dans le sujet
- Définir les concepts-clés dès l'introduction
- Citer les auteurs au programme du MINESEC avec leur thèse précise et l'œuvre si possible
- Plan dialectique standard : thèse → antithèse → synthèse/dépassement

### Histoire-Géographie
- Situer dans le temps (dates, périodes) ET dans l'espace (régions, pays) avant de développer
- Vocabulaire géopolitique précis : ne pas confondre État, nation, pays, territoire

### Anglais
- Compréhension : réponses complètes reprenant des éléments textuels (citation + reformulation)
- Production : respecter strictement la structure imposée (formal letter, essay, summary) - les correcteurs pénalisent la confusion de format
- Grammar/Vocabulary à choix fermé (ex. « (may / always / likes) » donné en ligne dans l'énoncé) : ce sont des QCM comme les autres en mode automatisation, même si la source ne les présente jamais avec des lettres a)/b)/c) - `choix` et `reponse_correcte` restent obligatoires (voir la règle `type_reponse`, cas "options données en ligne, sans lettre", dans le mode automatisation)

### Économie / Droit (série SES)
- Définir chaque concept en introduction de partie avant de l'utiliser
- Ancrer les exemples dans le contexte camerounais ou africain quand c'est possible
- Graphiques : axes légendés, courbes nommées, déplacement vs glissement clairement distingués - le graphique est produit comme figure réelle (voir « Figures produites dans le corrigé »), jamais seulement décrit

---

## Registre, niveau de langue et profondeur

- **Profondeur calibrée au niveau** : un corrigé de 3e (BEPC) détaille davantage les étapes intermédiaires et explique plus longuement les notions de base qu'un corrigé de Terminale, où l'élève est supposé maîtriser le socle du cycle précédent. Ne pas sur-expliquer ce qui est acquis, ne pas sous-expliquer ce qui est nouveau.
- **Ton** : dans le corps du corrigé, registre académique rigoureux ; dans les blocs "Piège" et "Conseil", tutoyer l'élève directement ("Pense à vérifier…", "N'oublie pas de…") - plus engageant et mémorisable
- Français rigoureux mais accessible - jamais de jargon non expliqué à la première occurrence
- Pour les matières littéraires, la rigueur porte sur la structure argumentative et la méthode, pas sur une unique "bonne réponse"

---

---

## Style rédactionnel - éliminer les marqueurs IA

Un corrigé destiné à la vente doit être indiscernable d'un texte rédigé par un enseignant expert. Les marqueurs ci-dessous trahissent immédiatement une rédaction assistée par IA et nuisent à la crédibilité pédagogique du contenu. Les éliminer sans exception dans chaque corrigé produit.

### Formules à proscrire

**Formules d'emphase creuses** - les supprimer et reformuler en affirmation directe :
- "Il est à noter que", "Il convient de souligner que", "Il est important de préciser que"
- "Force est de constater que", "Il y a lieu de rappeler que", "Notons que", "Rappelons que"
- "En effet," en début de phrase (sauf si la phrase est réellement explicative d'une cause)

Au lieu de : *"Il est à noter que la dérivée s'annule en x=2."*
Écrire : *"La dérivée s'annule en x=2."*

**Connecteurs mécaniques en série** - un connecteur logique ne s'utilise que si la relation logique n'est pas déjà évidente par la construction :
- Éviter l'enchaînement systématique : "De plus,… Par ailleurs,… En outre,… Ainsi,…"
- "Notamment" n'introduit une liste qu'en milieu ou fin de phrase, jamais en début de phrase
- "Par conséquent" et "Donc" ne doivent pas coexister dans le même paragraphe pour exprimer la même relation

**Formules de conclusion mécanique** - les remplacer par la conclusion elle-même :
- "En définitive,", "En somme,", "Pour conclure,", "Au final,", "En guise de conclusion"
- Écrire directement la conclusion ; le bloc "Conseil" ou "Piège" signe naturellement la fin

**Lissage artificiel des difficultés** - ne pas atténuer systématiquement chaque mise en garde par un "toutefois", "néanmoins" ou "il convient néanmoins de nuancer" ; si un piège est réel, le formuler sans amortisseur

### Patterns de mise en forme à éviter

- **Gras excessif** : ne grasser que les formules-clés et les noms de théorèmes, pas chaque notion mentionnée
- **Listes à puces uniformes** : une liste où toutes les entrées ont exactement la même longueur ou structure trahit l'IA ; varier la formulation ou intégrer dans le corps du texte quand il y a moins de trois éléments
- **Tiret cadratin (caractère Unicode em dash) proscrit** : ne jamais l'utiliser, y compris pour une incise grammaticale ou une mise en relief. Utiliser un tiret simple ("-") ou reformuler la phrase à la place
- **Anaphores mécaniques** : éviter que deux paragraphes consécutifs commencent par le même syntagme (ex. "Cette propriété… / Cette notion… / Cette méthode…") ; varier la construction ou fusionner

### Registre de la voix pédagogique

Dans le corps du corrigé, écrire comme un professeur qui pense à voix haute : direct, sans fioritures, sans hedging superflu. Les formulations du type "On peut observer que", "Nous pouvons donc en conclure que" alourdissent inutilement ; écrire "On obtient", "Donc", ou intégrer directement dans la phrase.

Dans les blocs **Piège** et **Conseil**, la voix doit rester naturelle et engageante (tutoiement, ton direct) sans basculer dans un registre listé et uniforme.

**Test final avant livraison** : relire le corrigé et se demander - "Un correcteur du MINESEC qui lirait ceci à voix haute reconnaîtrait-il immédiatement la plume d'un enseignant expérimenté ?" Si une phrase sonne artificielle ou redondante, la reformuler.

---

## Mise en forme et sortie

### En-tête standardisé (obligatoire pour tout corrigé livré)

Ouvrir chaque correction par une fiche d'identité :

```
Matière :        [ex. Mathématiques]
Niveau / Série : [ex. Terminale C]
Examen visé :    [BAC | Probatoire | BEPC | Devoir Surveillé]
Durée épreuve :  [ex. 4 heures]
Coefficient :    [si connu]
Année :          [si connue, sinon omettre]
```

### Format de travail
- Rédiger le corrigé en **Markdown structuré** (titres `##`, listes, blocs LaTeX `$…$` pour les formules) - c'est le format de travail par défaut, lisible en chat et ingérable directement en base
- Si l'utilisateur veut une version stylisée prête à la vente (PDF/Word), utiliser la compétence `docx` séparément une fois le contenu validé en Markdown
- Nom de fichier suggéré pour le Word final : `correction_[matiere]_[serie]_[annee_ou_type].docx`

**Formules LaTeX display multi-lignes (`$$...$$`)** : quand une formule display s'étend sur plusieurs lignes (ex. un tableau de variations en `\begin{array}...\end{array}`), toujours isoler les délimiteurs `$$` seuls sur leur propre ligne, avec une ligne vide avant le `$$` ouvrant et après le `$$` fermant - jamais de texte collé sur la même ligne qu'un délimiteur (ex. jamais `\end{array}$$ --- ### Question suivante`). Certains moteurs de rendu Markdown+KaTeX perdent la portée du bloc et affichent le LaTeX brut non rendu si cette règle n'est pas respectée. Les formules display tenant sur une seule ligne (`$$x=1$$`) ne sont pas concernées.

**Le caractère `$` hors formule doit toujours être protégé** : `$` est le délimiteur des formules LaTeX. Un `$` littéral laissé nu (variable PHP `$nom`, référence de tableur `$B$2`, symbole monétaire, mention du caractère lui-même) est apparié par la plateforme au `$` suivant : tout le texte compris entre les deux s'affiche alors comme une formule déformée, ou lève une erreur KaTeX. Règles, valables pour un corrigé, un cours (`contenu_markdown`, `exemple_resolu`, `erreurs_classiques`, `exercices_application`, `synthese`) et un énoncé :
- Tout nom de variable, code, formule de tableur ou expression contenant un `$` va dans un span de code entre backticks : `` `$nom` ``, `` `=RANG(B2;$B$2:$B$5;0)` ``. Jamais nu dans une phrase.
- Un extrait de code de plusieurs lignes est un bloc fencé (```` ```php ... ``` ````, ```` ```c ... ``` ````), jamais des lignes de code nues dans un paragraphe.
- Le symbole isolé dans une phrase (« le symbole $ ») s'écrit `` `$` `` ou `\$`, jamais `$` seul.
- `formule_principale` (section `regle` d'un cours) et les variantes sous forme de chaîne ne contiennent qu'une VRAIE formule LaTeX. Un extrait de code (`$nom = valeur;`, `#include <stdio.h>`), un chemin de fichier (`C:\wamp\www\`) ou une directive n'y a pas sa place : le mettre dans `contenu_markdown`, en span ou bloc de code. Si une formule LaTeX doit vraiment porter du code, l'envelopper dans `\texttt{...}` en échappant `\$`, `\#` et `\_`.
- Erreur constatée (audit de rendu du corpus, 2026-09-19) : 15 cours d'informatique (PHP, tableur, langage C) où des `$nom` en prose et des lignes de code nues étaient lus comme des formules, et une `formule_principale` réduite à `$nomDeVariable = valeur;` ou `#include <nom_bibliotheque.h>`. Relire chaque `$` du texte produit avant de livrer : il est soit dans un span/bloc de code, soit délimiteur d'une vraie formule, soit échappé.

---

## Mode automatisation - sortie structurée pour pipeline (tâche planifiée / traitement en lot)

Quand cette compétence est invoquée dans un contexte de traitement automatisé (ex. tâche planifiée Cowork surveillant un dossier d'épreuves PDF), produire, en plus du corrigé Markdown, un bloc JSON de métadonnées par exercice traité - jamais une fusion des deux dans le même bloc de texte.

**Format de sortie par exercice** - un exercice peut contenir plusieurs sous-questions notées indépendamment (QCM à plusieurs items, problème à sous-parties numérotées) : chacune devient une entrée du tableau `questions`, jamais aplatie dans un seul bloc de texte. Un exercice à une seule question produit quand même un tableau `questions` à un seul élément - c'est le format normal, pas un cas particulier.

```json
{
  "epreuve_source": "nom du fichier PDF d'origine",
  "numero_exercice": "1",
  "pays": "code ISO du pays traité, en minuscules : cm | sn | ci | bj | tg | bf | td | ga | cf | cd | cg | gw | ml | ne - identique au segment <code_pays> du chemin ingest/<code_pays>/",
  "matiere": "un des intitulés fermés de la règle `matiere` plus bas - jamais une formulation inventée",
  "nature_epreuve": "theorique | pratique | null - UNIQUEMENT quand l'épreuve source l'indique explicitement (bandeau/en-tête du sujet, ex. « ÉPREUVE PRATIQUE DE CHIMIE »). À ne pas confondre avec `origine` (qui répond à « sujet officiel, blanc, d'établissement ou autre ? », jamais à « théorique ou pratique ? »). null si l'épreuve ne distingue pas les deux (cas normal pour la plupart des matières) ou si le doute n'est pas levé - jamais deviné depuis le nom du fichier ou du dossier",
  "partie_epreuve_francais": "etude de texte | expression ecrite | orthographe | null - UNIQUEMENT quand `matiere` vaut \"Français\" ET que l'épreuve source est un des documents distincts qui composent le Français au BEPC camerounais (souvent deux ou trois PDF séparés pour la même session : une épreuve « Étude de texte », une épreuve « Expression écrite », parfois une épreuve « Orthographe » sur les millésimes plus anciens - jamais mélangés dans un même document). null pour toute autre matière, et null aussi pour un Français qui n'est PAS scindé ainsi (cas du BAC/Probatoire camerounais, une seule épreuve « Langue française » ou « Français ») - jamais deviné depuis le nom du fichier ou du dossier, uniquement depuis l'intitulé donné par le sujet source lui-même",
  "variante_sujet": "sujet 1 | sujet 2 | null - UNIQUEMENT quand l'épreuve source indique elle-même qu'il s'agit d'une parmi plusieurs versions alternatives distribuées la même session pour le même (matière, cursus, année) - pratique courante pour limiter la fraude (bandeau ou en-tête « Sujet 1 »/« Sujet 2 », ou deux PDF distincts de la même session portant chacun cette mention). Générique, n'importe quelle matière, à ne pas confondre avec `partie_epreuve_francais` qui reste propre au Français. null dans tous les autres cas, largement majoritaires (une seule version du sujet) - jamais deviné depuis le nom du fichier ou du dossier, sauf s'il reprend lui-même explicitement la mention (voir la règle dédiée plus bas)",
  "serie": "code exact du pays traité (voir Référentiel) - TOUTES les séries concernées quand l'épreuve est commune à plusieurs, séparées par des virgules (ex. \"C, D\"), jamais la première seule. null si l'examen n'a pas de série (ex. BEPC/BFEM)",
  "filiere_serie_a": "abi | null - UNIQUEMENT pour le Cameroun, quand l'épreuve source précise la filière « A4 Bilingue » de la Série A (souvent visible sous la forme « A-ABI » dans l'en-tête ou le nom du fichier). Reste rattachée à la Série A (même `serie`: \"A\") - ce champ ne remplace ni n'ajoute de série, il précise seulement la filière. null pour la Série A classique ou toute autre série - jamais deviné en dehors de cette mention explicite « ABI »/« A-ABI »/« A4 Bilingue »",
  "examen": "bepc | bfem | probatoire | bac | autre",
  "origine": "NATURE de l'épreuve - une des 5 valeurs littérales : officiel | examen blanc | sujet zero | etablissement | autre. Ce n'est PAS le pays ni la provenance géographique : jamais 'Cameroun', 'MINESEC', 'Sénégal', ni un nom de fichier ou de dossier",
  "etablissement": "nom de l'établissement si origine=etablissement, sinon null",
  "institution": "organisme qui ORGANISE l'examen, UNIQUEMENT pour un examen blanc dont l'épreuve nomme son organisateur (ex. « Délégation régionale du Centre », « MINESEC ») - null partout ailleurs : la plateforme la déduit seule du couple (pays, examen) pour un sujet officiel, et de `etablissement` pour une épreuve d'établissement. Ne jamais y recopier l'Office du Baccalauréat ni un ministère pour un sujet officiel : ce serait redondant et source de divergence entre fichiers",
  "annee": "entier à 4 chiffres si déductible de l'épreuve, sinon null - jamais une plage \"année scolaire\", voir la règle `annee` plus bas",
  "duree_epreuve": "ex. '4h', si indiquée sur l'épreuve, sinon null",
  "coefficient": "ex. '7', si connu (voir Référentiel plus haut), sinon null",
  "introduction_markdown": "consigne(s) valable(s) pour l'ÉPREUVE ENTIÈRE, jamais pour ce seul exercice (ex. « Le candidat traitera au choix l'un des trois sujets proposés », « L'épreuve comporte deux parties indépendantes, obligatoires ») - voir la règle dédiée plus bas. Fourni par UN SEUL des exercices de l'épreuve (peu importe lequel), les autres laissent null - jamais recopié à l'identique sur chaque exercice. null quand l'épreuve ne porte aucune consigne de ce type, cas le plus fréquent",
  "points": "valeur si indiquée dans l'énoncé, sinon null",
  "groupes": ["Partie A", "I - Évaluation des savoirs"] ou [] - repères de regroupement au-dessus de cet exercice (section/partie qui rassemble PLUSIEURS exercices entiers, jamais les sous-questions d'un seul), du plus englobant au plus imbriqué, dans l'ordre où ils apparaissent sur le sujet source. [] pour la grande majorité des épreuves (aucune section de ce type) - voir la règle « Section qui regroupe PLUSIEURS exercices entiers » plus bas pour le détail et des exemples réels",
  "figures": [],
  "enonce_intro_markdown": "le repère de l'exercice en gras (« **Exercice 2 (6 points)** »), suivi du seul préambule réellement NÉCESSAIRE au traitement de toutes les sous-questions (données communes, dispositif expérimental, texte support, consigne commune d'un QCM). Le repère seul est une valeur normale quand l'exercice n'a rien à partager. N'y recopier JAMAIS le texte d'une sous-question - voir la règle « Un seul repère d'exercice » plus bas",
  "questions": [
    {
      "numero": "1",
      "enonce_markdown": "l'énoncé de cette sous-question, reformulé en Markdown avec la même convention LaTeX que le corrigé",
      "corrige_markdown": "le corrigé complet de cette sous-question, rédigé selon le Template obligatoire",
      "themes": ["liste de 2 à 5 thèmes/notions mobilisés par cette sous-question"],
      "savoir_officiel": {"classe": "1ere", "serie_label": "C-E", "module_numero": "21", "savoir_numero": "II"} ou null,
      "difficulte_estimee": "faible | moyenne | élevée",
      "type_reponse": "ouverte | qcm",
      "choix": [{"lettre": "a", "texte": "..."}] ou ["may", "always", "likes"] (liste de chaînes sans lettre, quand la source ne segmente pas les options avec des lettres a)/b)/c) - voir règle détaillée plus bas),
      "reponse_correcte": "toujours renseigné pour un QCM : la lettre si choix en porte une, sinon le texte exact de la bonne option parmi choix - jamais vide",
      "rappels_de_methode": [
        {
          "id": "rdm-<epreuve_source>-ex<numero_exercice>-q<numero>-<index>",
          "competence": "intitulé court de la compétence ciblée (ex. 'Résolution d'équations du second degré')",
          "contenu_markdown": "COPIE MOT POUR MOT du bloc ### Rappel de méthode tel qu'il apparaît dans le corrige_markdown de CETTE sous-question — aucune reformulation tolérée",
          "cours_genere": false,
          "cours_id": null
        }
      ]
    }
  ],
  "mots_cles_recherche": ["termes utiles à la recherche future dans la base"],
  "incertitudes": ["UNIQUEMENT un doute réel sur le contenu de l'épreuve : donnée illisible, ambiguïté de l'énoncé, résultat non garanti, valeur lue sur un graphique, année ou série indéterminable, référentiel pays non confirmé - liste vide si aucune. Jamais de note de traitement : voir la règle « Ce que `incertitudes` ne contient pas » ci-dessous"],
  "statut": "brouillon"
}
```

**Ce que `incertitudes` ne contient pas.** Ce champ ne sert qu'à signaler un doute réel sur le contenu de l'épreuve (donnée illisible, ambiguïté, valeur estimée, année ou série indéterminable). Il n'est jamais affiché aux élèves et l'ingestion écarte désormais les notes de traitement : n'écrire aucune de celles-ci, elles sont du bruit qui masque les vrais doutes (2 364 exercices touchés avant nettoyage du 2026-09-19, la grande majorité sans aucun doute réel) :
- le référentiel programme ou `savoir_officiel` inaccessible, non renseigné, laissé à `null`, ou une matière hors périmètre - la priorité est aux thèmes/tags, le rattachement au référentiel est en standby ;
- les cours ou rappels de méthode non générés, non coursés, ou le plafond de cours par épreuve ;
- les réparations que l'ingestion fait elle-même (titre « Exercice N » reconstruit, repère dédupliqué ou repositionné, JSON doublement échappé, colonnes `array` élargies, série ajoutée depuis le nom du dossier) ;
- les remarques purement informatives sur le PDF : scan sans couche de texte, filigrane ou bandeau d'un site tiers, recueil commercial, ancien intitulé « MINEDUC - DEXC », chiffrement du PDF, « le BEPC ne comporte pas de série » ;
- « A-ABI » : ABI = A4 Bilingue, déjà tranché (voir `filiere_serie_a` et la règle Cameroun ci-dessus), jamais une incertitude à confirmer.

Tout ce qui relève du compte rendu de traitement se dit à l'utilisateur dans la réponse finale, pas dans le JSON.

Le champ `figures` détaillé ci-dessus dans "Traitement des figures et images" - `[]` si l'exercice n'en contient aucune, toujours présent. Une figure partagée par plusieurs sous-questions (ex. un graphique lu en question 1 puis réexploité en question 3) n'est décrite qu'une fois dans `figures` : son placeholder `![fig-N](...)` peut apparaître dans le texte de plusieurs `questions` (et dans `enonce_intro_markdown`), la plateforme le résout partout où il apparaît.

**Règles spécifiques au mode automatisation** :
- `statut` est toujours `"brouillon"` dans le JSON produit ici, par convention de sortie - l'ingestion l'ignore et publie directement (`Lesson`/`Exercise` créés avec statut `VALIDE`, sans étape de relecture). Il n'y a donc pas de filet de rattrapage après l'ingestion : la rigueur exigée dans "Ce que cette compétence ne doit jamais faire" et le Template obligatoire est la seule vérification avant qu'un élève ne voie ce contenu
- Un exercice = un objet JSON. Une épreuve à N exercices produit N objets. Une sous-question = une entrée de `questions` - repérer les sous-questions comme à l'étape de Segmentation (numérotation explicite : 1/2/3, a/b/c, items d'un QCM), jamais les fusionner dans un seul bloc de texte même quand elles se ressemblent (ex. les 5 items d'un même QCM sont 5 entrées, pas une)
- Ne jamais halluciner `annee` ou `serie` - mettre `null` si l'info est absente
- Les fichiers PNG des figures (extraites de l'épreuve ou produites dans le corrigé) sont livrés dans le même dossier que les JSON, avec le nommage `<nom_epreuve>_exercice_<numero>_fig_<index>.png` ; l'ingestion Edukora les joint au contenu et le frontend les affiche à l'emplacement du placeholder
- **`themes`** : TOUJOURS renseigné pour chaque sous-question (2 à 5 thèmes, jamais `[]`) - c'est l'axe d'organisation de la plateforme (Parcours par thèmes, quiz, couverture) : une sous-question sans thème est invisible et fait échouer le tunnel de validation. Reprendre la forme EXACTE d'un thème déjà utilisé (mêmes accents, même casse, singulier de préférence) plutôt que d'inventer une variante (« elimination » à côté de « élimination », « Lois de Kepler » à côté de « loi de Kepler »)  : un thème = une notion du programme réellement mobilisée, jamais un mot de consigne (« définition », « calcul », le nom de la matière).
- **`savoir_officiel`** : référence vers le référentiel programme officiel (`programme.Module`/`Savoir` côté edukora). **En standby depuis le 2026-09-18** (l'organisation du contenu se fait par `themes`) : laisser `null` ou l'omettre n'est jamais un défaut et le remplir n'est plus attendu. Reste accepté et validé quand il est fourni ; ne jamais le déduire ni l'approximer.

  **Comment le remplir - une procédure, jamais une devinette.** Ouvrir le fichier fixture de la matière (chemins dans le périmètre ci-dessous, lecture déjà faite à l'étape 1 - Cadrage), y localiser le module de la (classe, `serie_label`) traitée, puis, sous-question par sous-question, le savoir dont l'intitulé recouvre la notion mobilisée. Recopier les quatre valeurs `classe`/`serie_label`/`module_numero`/`savoir_numero` exactement telles qu'elles apparaissent dans le fichier. Ne jamais les reconstruire de mémoire : elles ne s'écrivent presque jamais comme on les devine.

  **Correspondance série de l'épreuve → `serie_label` du référentiel.** C'est le décalage qui fait échouer le plus de références : la série imprimée sur l'épreuve n'est presque jamais le `serie_label` du module.

  | Série sur l'épreuve | `serie_label` attendu | Pourquoi |
  |---|---|---|
  | BEPC, toutes matières | `""` (chaîne vide) | le BEPC n'a pas de série |
  | Terminale C — maths, physique | `"C-E"` | C et E partagent un même module |
  | Terminale D — maths | `"D"` | module distinct de `C-E` |
  | Terminale C, D, E — chimie | `"C-D-E"` | un seul module pour les trois |
  | Informatique 2nde / 1ère / Tle | `"Tronc commun"` | aucun découpage par série |
  | Histoire-Géographie 1ère / Tle | `"Toutes séries"` | idem |

  En cas de doute, la seule source qui fasse foi est le champ `serie_label` du fichier fixture lui-même - le tableau ci-dessus n'en est qu'un raccourci pour les cas courants.

  **Une épreuve commune à plusieurs séries peut relever de deux modules différents.** Une épreuve de maths « C, D » n'a pas UNE bonne valeur pour toute l'épreuve : la série C vit dans le module `C-E`, la D dans le module `D`. Choisir sous-question par sous-question le module de la série effectivement traitée ; si l'épreuve ne permet pas de trancher, laisser `null` sur ces sous-questions et le dire dans `incertitudes`.

  **`null` n'est pas une valeur neutre, c'est un coût.** Une sous-question sans référence n'est rattachée à aucun savoir : le savoir concerné continue d'apparaître comme non couvert côté plateforme, et les outils de sélection réclament de générer du contenu déjà écrit. `null` reste la seule valeur acceptable dans deux cas, et seulement ceux-là : (a) hors périmètre - autre pays, ou matière/classe absente des fichiers listés ci-dessous ; (b) aucun savoir du module ne recouvre nettement la notion. Jamais un repli de confort. Quand la matière EST au périmètre et que la référence est laissée `null` malgré tout, l'écrire dans `incertitudes` avec la raison.

  **Ne jamais inventer une valeur pour autant.** Une référence approximative fait échouer l'ingestion (voir `catalog.ingestion._resolve_savoir_officiel`), et c'est le comportement voulu : l'erreur liste alors les valeurs réellement disponibles (couples (classe, `serie_label`) de la matière, numéros de module du couple, numéros de savoir du module) - il suffit de reprendre celle qui convient plutôt que de repartir sur `null`.

  **Périmètre couvert aujourd'hui**, tout Cameroun - **Mathématiques** (6e à Tle, toutes séries - `backend/programme/fixtures/programme_officiel_cm_maths.json`), **Physique** (Seconde C, Première C, Première D et TI, Terminale C et D - `backend/programme/fixtures/programme_officiel_cm_physique.json`), **Chimie** (Seconde C, Première C et D, Terminale C, D et E - `backend/programme/fixtures/programme_officiel_cm_chimie.json`), **Informatique** (4e et 3e, Seconde/Première/Terminale en tronc commun valable pour toutes les séries à la fois, sans découpage par série ni `famille_situations` - `backend/programme/fixtures/programme_officiel_cm_informatique.json`), **SVT** (4e et 3e, Seconde C, Première séries C-E-TI - programme commun aux trois séries - Première D, Terminale C et TI, Terminale D ; les modules de Première C-E-TI proviennent d'un document de cours et non d'un programme MINESEC intégral, donc `credit_heures` et `famille_situations` y sont volontairement vides - `backend/programme/fixtures/programme_officiel_cm_svt.json`), **Physique-Chimie-Technologie (PCT)** (4e et 3e uniquement - `backend/programme/fixtures/programme_officiel_cm_pct.json`), **Français** (6e à 3e, Première et Terminale séries Littéraires A / Scientifiques C-D, Seconde pas encore disponible - `backend/programme/fixtures/programme_officiel_cm_francais.json`), **Anglais** (6e à 3e, Seconde et Terminale séries C-D / A, Première pas encore disponible - `backend/programme/fixtures/programme_officiel_cm_anglais.json`), **Philosophie** (Première et Terminale séries A / C-D-E-TI, Seconde pas encore disponible - `backend/programme/fixtures/programme_officiel_cm_philosophie.json`) et **Histoire-Géographie** (Histoire : 6e, 5e, Seconde, Première toutes séries - 4e, 3e et Terminale pas encore disponibles ; Géographie : 6e, 5e, 4e, Troisième, Seconde, Première toutes séries, Terminale toutes séries - couverture quasi complète ; les deux disciplines partagent un seul Subject edukora `HISTOIRE_GEO`, donc `module_numero` y est préfixé `H` pour l'Histoire et `G` pour la Géographie afin d'éviter toute collision - `backend/programme/fixtures/programme_officiel_cm_histoire_geo.json`) : un module par (classe, série), chacun avec sa liste de savoirs numérotés.

  **Effet** : le tag résolu depuis `themes` est automatiquement rattaché à ce savoir officiel, sans action manuelle supplémentaire - c'est ce rattachement, et lui seul, qui fait exister le contenu produit pour l'audit de couverture, la sélection des lots de quiz et l'équilibrage des épreuves inédites.
- **`pays`** : code ISO 3166-1 alpha-2 en minuscules, jamais le nom du pays en toutes lettres, jamais une majuscule, jamais un gentilé. Codes valides : `cm` (Cameroun), `sn` (Sénégal), `ci` (Côte d'Ivoire), `bj` (Bénin), `tg` (Togo), `bf` (Burkina Faso), `td` (Tchad), `ga` (Gabon), `cf` (Centrafrique), `cd` (RD Congo), `cg` (Congo-Brazzaville), `gw` (Guinée-Bissau), `ml` (Mali), `ne` (Niger).

  En mode automatisation, la valeur est **recopiée du segment `<code_pays>` du chemin** `ingest/<code_pays>/<epreuve>/...` - c'est la source de vérité, pas le suffixe du nom de dossier ni un en-tête lu sur le PDF. `ingest/cm/bac-c-physique-2024-cameroun/` donne `"pays": "cm"`. Si le chemin et l'épreuve se contredisent (dossier `sn/` mais en-tête MINESEC), suivre le chemin et signaler la contradiction dans `incertitudes` plutôt que de trancher seul.

  En mode interactif, déduire le code de la demande ou de l'en-tête ministériel de l'épreuve ; si aucun des deux ne le donne, demander à l'utilisateur - jamais supposer `cm` par défaut. `pays` ne vaut jamais `null` : un corrigé sans pays ne peut pas être rattaché au bon référentiel de séries en base.

- `serie` doit toujours utiliser l'un des codes exacts du pays traité (voir Référentiel plus haut) - jamais le code d'un autre pays, même si la lettre se ressemble (le « A » camerounais et le « A » béninois ne désignent pas la même ligne en base). Pour le Cameroun spécifiquement, jamais les anciens codes B, F ou G (nomenclature abandonnée)
- Le Sénégal nomme son examen de fin de collège « BFEM » : utiliser `"examen": "bfem"` (pas `"bepc"`) pour ce pays - les deux désignent le même niveau côté base de données, mais `bfem` restitue le nom réellement utilisé localement
- **`origine` = nature de l'épreuve, jamais sa provenance géographique.** Le champ n'accepte que 5 chaînes littérales, à recopier caractère pour caractère : `"officiel"`, `"examen blanc"`, `"sujet zero"`, `"etablissement"` (sans accent), `"autre"`. Toute autre valeur fait rejeter l'exercice à l'ingestion avec le message `Origine inconnue : '<valeur>'. Attendu officiel/examen blanc/sujet zero/etablissement/autre`.

  `"officiel"` est la valeur par défaut : une épreuve d'examen national réellement passée (en-tête ministériel type MINESEC, Office du Bac). N'en dévier que sur mention explicite portée par l'épreuve - bandeau « Examen blanc » → `"examen blanc"` ; en-tête d'un établissement scolaire au lieu d'un en-tête ministériel → `"etablissement"`, et renseigner alors `etablissement` avec le nom lu sur l'épreuve. `"autre"` uniquement quand aucune des précédentes ne s'applique.

  **`"sujet zero"` : un spécimen, pas un entraînement.** Catégorie distincte de `"examen blanc"`, à ne pas confondre malgré l'apparence de synonymie - un « sujet zéro » est un exemplaire publié (souvent par le ministère ou l'organisme examinateur) pour familiariser candidats et enseignants avec un nouveau format d'épreuve, jamais un entraînement composé par un établissement scolaire ou un répétiteur pour préparer ses élèves. N'utiliser cette valeur que sur mention explicite portée par l'épreuve elle-même (bandeau « Sujet zéro », ou nom de fichier source qui la reprend explicitement, ex. `bac-c-e-maths-zero-2026-cameroun`) - jamais deviné du seul fait qu'un sujet officiel homonyme existe déjà pour la même année.

  **Piège déjà rencontré, à l'origine de rejets en série** : le nom de dossier de l'épreuve se termine par le pays (`ingest/cm/bac-c-physique-2024-cameroun/...`), ce qui pousse à lire `origine` comme « d'où vient cette épreuve ? » et à y écrire `"Cameroun"`. Les 5 exercices de l'épreuve partent alors avec la même valeur invalide et l'épreuve entière est rejetée. Le pays **a son propre champ, `pays`** (voir la règle dédiée ci-dessus), alimenté par le segment `<code_pays>` du chemin `ingest/<code_pays>/<epreuve>/` : c'est le seul endroit du JSON où il apparaît. Ne jamais le faire entrer dans `origine`, `examen` ou `serie`. Valeurs interdites dans `origine`, vues ou prévisibles : `"Cameroun"`, `"cm"`, `"MINESEC"`, `"Office du Bac"`, `"BAC C 2024"`, le nom du fichier PDF (celui-ci va dans `epreuve_source`, et nulle part ailleurs).
- **`matiere` : liste fermée, jamais une formulation inventée** (même règle que `origine`/`examen` ci-dessus, voir aussi le rappel en fin de compétence). Recopier l'un des intitulés suivants - toute valeur hors de cette liste, et hors du tableau de rattachement juste en dessous, fait rejeter l'exercice ou le cours à l'ingestion avec le message `Matière inconnue : '<valeur>'.` :

  `Mathématiques` · `Physique` · `Chimie` · `Physique-Chimie` (réservé, voir la règle dédiée juste après) · `Physique-Chimie-Technologie` · `SVT` · `Français` · `Philosophie` · `Histoire-Géographie` · `Anglais` · `Espagnol` · `Économie` · `Droit` · `Éducation Civique` · `Littérature` · `EPS` · `Informatique` (BEPC, Probatoire A et C/D/E, BAC C/D/E théorique UNIQUEMENT ; jamais en Série TI) · `Programmation` · `Systèmes d'Information` · `Réseaux, Internet et Sécurité Informatique` (ces trois dernières : Série TI uniquement) · `Dessin`

  **Série TI, jamais `Informatique`.** Décision du 2026-09-17 : en Série TI (Probatoire et BAC), l'Informatique se décompose toujours en trois matières distinctes - `Programmation` (algorithmique, langage C, programmation web), `Systèmes d'Information` (bases de données, UML, modélisation ; c'est aussi l'ancien « Informatique Théorique ») et `Réseaux, Internet et Sécurité Informatique` (réseaux, adressage IP, Internet, cloud, sécurité) - choisir celle que l'épreuve examine réellement, sur la lecture de son contenu, jamais `Informatique` par réflexe. `matiere` s'applique aussi aux cours (`meta.matiere`). La plateforme REFUSE à l'ingestion un exercice ou un cours de Série TI déclaré `Informatique` (erreur d'ingestion explicite) : un fichier ainsi produit ne sera pas ingéré. **Cas d'erreur en série** : 6 lots TI livrés d'affilée avec `"matiere": "Informatique"` (bac-ti-programmation-2024/2025, bac-ti-reseau-2023, terminale-ti-SI-vogt-2021…), soit environ 90 fichiers (exercices ET cours) rejetés d'un coup. Avant de livrer un lot dont `serie` contient `TI`, relire `matiere` de CHAQUE exercice ET `meta.matiere` de CHAQUE cours (voir l'auto-contrôle « Checklist de sortie de lot »). **Le nom du dossier ne décide jamais de la série** : `probatoire-ti-SI-2026` contenait en réalité l'épreuve « Probatoire C/D - théorique d'informatique » (série `C, D, E`, matière `Informatique`) ; lire la série dans l'en-tête du sujet, et nommer le dossier d'après ce qu'on y a lu.

  **Table de rattachement** - le sujet source emploie souvent un intitulé différent pour désigner la même discipline (nomenclature d'une autre époque, sigle, intitulé officiel remis à jour) : rattacher à l'intitulé canonique ci-dessus, ne jamais recopier l'intitulé source tel quel ni inventer une formulation voisine.

  | Intitulé rencontré sur le sujet source | Rattaché à |
  |---|---|
  | Sciences de la Vie et de la Terre ; SVTEEHB / « ...Éducation à l'Environnement, Hygiène et Biotechnologie » (intitulé officiel actuel au BAC) | SVT |
  | Langue française ; Étude de texte / Expression écrite / Orthographe (BEPC camerounais scindé - voir `partie_epreuve_francais`) | Français |
  | Histoire (BEPC scindé) ; Géographie (BEPC scindé) | Histoire-Géographie |
  | Éducation à la Citoyenneté ; ECM (sigle) ; Éducation Morale et Civique / Éducation Civique et Morale / EMC (nomenclature des années 1990-2000, les deux ordres de mots vus dans le corpus, ex. `bepc-emc-1995/1996/1997/2005/2007/2008-officiel-cameroun`) | Éducation Civique |
  | Littérature ou Culture Générale ; Littérature / Culture Générale (toutes graphies avec « / » ou « et ») | Littérature |
  | Éducation Physique et Sportive | EPS |
  | PCT (sigle brut du BEPC camerounais, épreuve couvrant Physique/Chimie/Technologie en un seul document - vu sur `bepc-pct-2005/2006/2008/2010/2012/2013-officiel-cameroun`) | Physique-Chimie-Technologie |

  **Une matière absente à la fois de la liste et du tableau ci-dessus, réellement nouvelle** (ex. Langues et Cultures Nationales) : ne jamais la rattacher par approximation à une matière voisine, ni inventer un nouvel intitulé pour la faire passer. Écrire son intitulé réel dans `matiere`, laisser `savoir_officiel` à `null` sur ses sous-questions, et l'expliquer dans `incertitudes` (« matière hors périmètre du référentiel edukora »). Ajouter une matière au référentiel est une décision produit qui revient à l'utilisateur, jamais une extrapolation de cette compétence - voir `bepc-lcn-2023-cameroun`, laissé en l'état sur cette base.

- **`annee` : toujours un entier à 4 chiffres, jamais une plage d'années scolaires.** Une épreuve d'établissement porte parfois la mention « Année scolaire 2023/2024 » plutôt qu'un millésime unique - ne jamais la recopier telle quelle (`"annee": "2023/2024"` fait rejeter l'exercice à l'ingestion, qui n'accepte qu'un entier via `int(...)`). Retenir la seconde année de la plage, celle où l'examen a effectivement lieu : « Année scolaire 2023/2024 » → `"annee": "2024"`. `null` reste la seule autre valeur acceptée, si l'année n'est déductible d'aucune façon (voir aussi la règle juste au-dessus sur les champs à ne jamais halluciner).

- **`matiere` : Physique et Chimie sont deux matières distinctes, jamais fusionnées en « Physique-Chimie » par défaut.** Écrire `"Physique"` ou `"Chimie"` dès que l'épreuve source ne traite réellement que l'une des deux (cas le plus fréquent depuis que le Cameroun et d'autres pays séparent les épreuves écrite/pratique de Physique et de Chimie en documents distincts). Réserver `"Physique-Chimie"` aux deux cas suivants uniquement : (a) l'épreuve source mélange réellement les deux disciplines dans un même document (ancien format d'épreuve, exercices de Physique ET de Chimie dans le même sujet), ou (b) le doute n'est pas levé et qu'il est impossible de déterminer laquelle des deux domine. Ne jamais écrire "Physique-Chimie" par réflexe ou par habitude : c'est une valeur de repli pour un cas réel de mélange ou d'incertitude, pas la valeur par défaut. Ce principe se généralise à toute épreuve à plusieurs exercices : chaque exercice garde la valeur de `matiere` qui correspond à ce qu'il traite réellement, même au sein d'une même épreuve source - un exercice 1-2 de Physique suivi d'un exercice 3-4 de Chimie dans le même document produit `"matiere": "Physique"` sur les deux premiers JSON et `"matiere": "Chimie"` sur les deux suivants, jamais "Physique-Chimie" partout par simplification.
- **`nature_epreuve` (théorique/pratique) : uniquement quand l'épreuve source l'indique elle-même.** De nombreuses épreuves de Physique (et parfois de Chimie) se déclinent en une épreuve écrite/théorique et une épreuve pratique/expérimentale distinctes, chacune avec son propre sujet. Quand le bandeau, l'en-tête ou l'intitulé de l'épreuve le précise explicitement (ex. « ÉPREUVE PRATIQUE », « Épreuve pratique de chimie », un protocole expérimental avec matériel de laboratoire à décrire) : `"nature_epreuve": "pratique"`. Un sujet de calcul/théorie classique sans mention particulière : `"nature_epreuve": "theorique"` si l'épreuve source le précise explicitement, sinon `null` - ne jamais déduire "théorique" par défaut simplement parce que rien n'indique "pratique" : l'absence de mention veut dire que cette distinction ne s'applique probablement pas à cette épreuve (cas de la grande majorité des matières et des épreuves anciennes), pas qu'elle est nécessairement théorique. Champ optionnel, jamais une raison de retarder la livraison du JSON en cas de doute - `null` est toujours une réponse valide.

  **⚠ Piège récurrent, constaté à répétition (BEPC Informatique 2018/2020/2022/2025, BEPC EMC 2023/2025, BEPC PCT 2005/2006/2008/2010/2012/2013 - 12 épreuves à ce jour, toujours la même valeur) : `"nature_epreuve": "epreuve"`.** Cette chaîne n'est ni `theorique` ni `pratique` ni `null` - elle ne veut rien dire, mais ressemble à un mot du champ lui-même (« nature d'**épreuve** ») recopié par réflexe au lieu d'une vraie valeur ou de `null`. L'ingestion la rejette systématiquement (`Nature d'épreuve inconnue : 'epreuve'`), et rejette avec elle l'exercice entier - jamais détecté avant l'ingestion puisque le mot semble à première vue lié au champ. Avant de livrer, si `nature_epreuve` n'est ni `"theorique"` ni `"pratique"`, sa seule autre valeur valide est le littéral JSON `null` - jamais une chaîne de remplissage, même courte, même qui ressemble au nom du champ.
- **`partie_epreuve_francais` : le pendant, pour le Français, de `nature_epreuve`.** Le Français du BEPC camerounais est traditionnellement examiné en plusieurs documents séparés plutôt qu'en une seule épreuve - une « Étude de texte » (compréhension/résumé/questions sur un texte support) et une « Expression écrite » (rédaction/dissertation), parfois aussi une « Orthographe » distincte sur les sessions plus anciennes. Ce sont trois épreuves réellement différentes (dates, consignes et barèmes propres), jamais des exercices d'une seule et même épreuve : chacune produit ses propres fichiers JSON avec son propre `epreuve_source`, et chacune doit porter `"partie_epreuve_francais"` renseigné à `"etude de texte"`, `"expression ecrite"` ou `"orthographe"` selon l'intitulé donné par le sujet source. Toujours `"matiere": "Français"` dans les trois cas - ne jamais écrire l'intitulé de la partie dans `matiere`, c'est le rôle de ce champ dédié. `null` pour toute autre matière, et `null` également pour un Français non scindé (BAC/Probatoire camerounais : une seule épreuve « Français »/« Langue française », `nature_epreuve` et `partie_epreuve_francais` restent alors tous deux vides). Sans ce champ, deux épreuves de Français distinctes de la même année/du même cursus produisent le même titre affiché sur la plateforme et deviennent indiscernables l'une de l'autre dans le catalogue.

  Un nom de fichier ou de dossier qui porte lui-même la mention (`bac-c-d-chimie-pratique-2022`, `bac-c-d-e-informatique-theorique-2021`) compte comme une indication explicite du sujet : la reprendre. C'est le seul cas où le nom du fichier fait foi pour ce champ - le déduire d'un nom qui ne dit rien reste interdit.

  Ne pas confondre une épreuve pratique avec un exercice qui PARLE d'un TP. Une épreuve pratique dure typiquement 1h, ne contient qu'un ou deux exercices, et consiste à exécuter un protocole (préparation d'une solution, dosage, mesures). Une phrase du type « lors d'une séance de travaux pratiques, les élèves ont relevé... » dans un exercice parmi quatre d'une épreuve de 2 à 3h est un simple décor d'énoncé : l'épreuve reste théorique. Cas réels vérifiés : `bac-c-d-chimie-2023/2024` et `bac-c-d-e-chimie-2025` sont pratiques (« Épreuve pratique de chimie - Dosage acide-base », 1h) ; `bac-d-ti-physique-2014 à 2017` et `bac-c-e-physique-2013` sont théoriques malgré leur exercice « Fiche de travaux pratiques ».
- **`variante_sujet` : signale que ce sujet est une parmi plusieurs versions alternatives d'un même examen, distribuées la même session pour limiter la fraude** (constaté : `bepc-svt-2015-sujet1`/`-sujet2`, `bac-d-svt-2014-sujet1`/`-sujet2` - deux PDF distincts de la même session, chacun portant la mention « Sujet 1 » ou « Sujet 2 »). Générique (n'importe quelle matière), contrairement à `partie_epreuve_francais` qui reste propre au Français - ce n'est pas non plus une variante de `nature_epreuve` (théorique/pratique), les deux champs sont indépendants et peuvent en théorie coexister. Renseigner `"sujet 1"`/`"sujet 2"` uniquement quand l'épreuve source porte elle-même cette mention (bandeau, en-tête) - un nom de fichier qui la reprend explicitement (`-sujet1-`, `-sujet2-`) compte comme une indication explicite, même règle que pour `nature_epreuve`/`partie_epreuve_francais` ci-dessus. `null` dans tous les autres cas, largement majoritaires (une seule version du sujet) - jamais déduit du seul fait que deux épreuves du même (matière, cursus, année) existent dans le corpus si aucune des deux ne porte la mention elle-même. Sans ce champ quand il s'applique, deux sujets alternatifs produisent le même titre affiché sur la plateforme et deviennent indiscernables l'un de l'autre dans le catalogue - même symptôme que `partie_epreuve_francais`, cause différente.
- **`serie` : toutes les séries de l'épreuve, pas seulement la première.** Une même épreuve est très souvent commune à plusieurs séries (« BAC C-D », « Séries C, D et E », « D et TI »)  : les lister toutes, séparées par des virgules (`"serie": "C, D"`). N'en retenir qu'une rattache l'épreuve à un seul cursus et la rend **introuvable pour tous les autres candidats concernés** - défaut relevé sur 62 dossiers du corpus (244 fichiers), toutes matières confondues. Le nom du dossier est un signal fiable à recouper systématiquement : `bac-c-d-chimie-2003-cameroun` annonce deux séries, donc `"serie": "C, D"` et non `"C"`. En cas de désaccord entre le nom du dossier et ce que porte le sujet lui-même, c'est le SUJET qui fait foi - le signaler alors dans `incertitudes` plutôt que de trancher silencieusement.

  **Piège déjà rencontré (2 fois), plus insidieux que le précédent : l'en-tête ou le nom du fichier SOURCE annonce déjà plusieurs séries, mais une seule est reportée dans `serie` - et ni le nom de dossier ni le JSON ne se contredisent ensuite, donc rien ne permet de repérer l'erreur après coup.** `probatoire-c-maths-2014-cameroun` (en-tête du sujet : « Séries : C et E ») et `Proposition-Corrigé-Maths-BACC-C-E-2021` (le nom du fichier source lui-même épelait « BACC-**C-E**-2021 ») ont tous deux été ingérés avec `"serie": "C"` seule - l'épreuve concernée est restée introuvable pour tout candidat de Série E jusqu'à une correction manuelle en base, bien après coup. Dans les deux cas l'indice était déjà là dès la première lecture (en-tête du sujet, ou nom du fichier source fourni en entrée) mais n'a pas été reporté dans `serie` - contrairement au cas ci-dessus, ce défaut ne se détecte PAS en recoupant le nom du dossier ingest avec `serie`, puisque les deux s'accordaient (à tort) sur une seule série. La seule protection est en amont : ne jamais figer `serie` sur la base de la seule série demandée ou évoquée au départ - relire l'en-tête complet du sujet ET le nom du fichier source tel que fourni, avant de rédiger quoi que ce soit (voir Cadrage, étape 1).

  **Cas particulier du Cameroun - « A-ABI » n'est PAS deux séries.** Une épreuve dont l'en-tête ou le nom de fichier porte « A-ABI » (ex. `bac-a-abi-maths-2016-cameroun`) reste une épreuve de Série A ordinaire (`"serie": "A"`, jamais `"A, ABI"` - ABI n'est pas un code de série reconnu) ; renseigner en plus `"filiere_serie_a": "abi"` pour préciser qu'il s'agit de la filière « A4 Bilingue ». Ne jamais confondre ce cas avec une vraie épreuve à séries multiples du type « C-E ».
- **Un seul repère d'exercice, et il vit dans `enonce_intro_markdown`.** Le repère « Exercice 2 », « Problème » et son barème ouvrent `enonce_intro_markdown`, en gras (`**Exercice 2 (6 points)**`) ou en titre Markdown (`### Exercice 2 (6 points)`) - **aucune** sous-question ne le reprend ensuite.

  Ce n'est pas un choix cosmétique : en lecture d'un corrigé, la plateforme affiche `enonce_intro_markdown` en permanence, alors que `enonce_markdown` est replié derrière un bouton « Voir l'énoncé », fermé par défaut. Un repère placé dans la première sous-question serait donc invisible par défaut, et l'élève verrait une suite de blocs sans aucun titre d'exercice. C'est aussi la seule ligne que lit le sommaire de navigation - d'où le gras ou le `###` : un repère en texte nu n'y produit aucun titre.

  Un `enonce_intro_markdown` réduit au seul repère est donc parfaitement normal et attendu pour un exercice sans préambule partagé - ce n'est pas un remplissage à supprimer. Ce qu'il ne doit jamais contenir, c'est du texte recopié depuis les sous-questions.

  Erreur déjà rencontrée, sur 108 fichiers répartis sur 32 épreuves (probatoire-c-d-chimie-2003, bac-c-d-chimie-1998, bac-d-ti-physique-*, bac-d-physique-chimie-1995 à 1997...) : le repère écrit à la fois dans `enonce_intro_markdown` et en tête de la première sous-question. Comme la plateforme affiche l'intro puis chaque sous-question à la suite, le lecteur voit :
  ```
  Exercice 1 (5 points)

  Exercice 1 (5 points) - hydrocarbures, isomérie et synthèse du TNT

  Exercice 1 (5 points)
  ```
  Un sous-titre thématique (« - hydrocarbures, isomérie... ») ne rend pas l'un des deux légitime : il s'ajoute au repère unique, il n'en justifie pas un second.

  **Même règle quand `enonce_intro_markdown` s'ouvre sur un chapeau/bandeau imprimé** (« *MINEDUC - OBC. Épreuve de mathématiques...* », « *Ministère des Enseignements Secondaires...* ») **avant le repère de l'exercice.** Le repère (« **Exercice 1 (5 points)** ») reste alors la DERNIÈRE ligne de `enonce_intro_markdown`, pas la première - mais la règle ne change pas : cette dernière ligne ne doit jamais être répétée en tête de la première sous-question. Erreur déjà rencontrée sur 6 épreuves `probatoire-c(-et-e)-maths-*` (1999, 2013, 2015 à 2018) : le chapeau déplaçait le repère hors de la première ligne, et la vérification "le repère n'ouvre pas déjà la première sous-question" n'avait été faite que sur la première ligne de l'intro plutôt que sur sa dernière ligne en gras - le doublon passait donc inaperçu malgré la règle déjà en place.

  **Autre variante de la même erreur, sans chapeau ni doublon cette fois : le préambule propre à l'exercice rédigé AVANT son repère au lieu d'après.** Repéré sur mathematiques-bepc-2000/2001/2002/2003-cameroun : une Partie qui regroupe plusieurs exercices numérotés en romain (« Partie A » puis « Exercice I », « Exercice II », « Exercice III »...) a vu, sur plusieurs de ses exercices, le préambule propre à CET exercice (données, énoncé partagé, figure) rédigé en premier dans `enonce_intro_markdown`, et son repère « Exercice N » relégué en toute dernière ligne - alors que la règle ci-dessus est déjà claire : le repère OUVRE `enonce_intro_markdown`, il ne le conclut jamais, y compris quand ce qui le précède n'est pas un chapeau d'épreuve entière mais le propre préambule de l'exercice. Résultat en lecture, le préambule se lit avant même de savoir de quel exercice il s'agit :
  ```
  "enonce_intro_markdown": "Un magasin a fait une réduction de 25 % sur le prix de ses marchandises.\n\n**Exercice I (2 pts)**"
  ```
  Et non (repère en tête, comme pour n'importe quel autre exercice) :
  ```
  "enonce_intro_markdown": "**Exercice I (2 pts)**\n\nUn magasin a fait une réduction de 25 % sur le prix de ses marchandises."
  ```
  Quand l'exercice ouvre en plus sa Partie (repère de section et son sous-titre au-dessus - voir « Section qui regroupe plusieurs exercices entiers » plus bas), le repère de l'exercice se place après ce cadre de Partie, jamais avant ni intercalé entre le titre de la Partie et son sous-titre :
  ```
  "enonce_intro_markdown": "**A - ACTIVITÉS NUMÉRIQUES : 6,5 points**\n\n*Cette partie comporte trois exercices indépendants I, II et III.*\n\n**Exercice I (2 pts)**\n\nUn magasin a fait une réduction de 25 % sur le prix de ses marchandises."
  ```
  Filet de sécurité côté plateforme : un repère « Exercice N »/« Problème » placé après son propre préambule plutôt qu'avant est aujourd'hui détecté et automatiquement ramené en tête à l'ingestion - mais mieux vaut livrer un JSON déjà dans le bon ordre que de compter sur ce filet.
- **Consigne valable pour l'ÉPREUVE ENTIÈRE (pas un seul exercice) : `introduction_markdown`, jamais `enonce_intro_markdown`.** Certaines épreuves portent une consigne qui gouverne l'épreuve dans son ensemble - laquelle des sous-parties traiter (« Le candidat traitera au choix l'un des trois sujets proposés », fréquent en Philosophie et Littérature où chaque sujet au choix devient un exercice séparé), ou une règle commune à plusieurs exercices (« L'épreuve comporte deux parties indépendantes, obligatoires », « NB : le candidat doit traiter l'exercice et les deux problèmes »). Ce texte ne décrit AUCUN exercice en particulier : il va dans `introduction_markdown`, au niveau de l'épreuve (voir le schéma plus haut), jamais dans `enonce_intro_markdown` d'un exercice donné - `enonce_intro_markdown` reste réservé au repère et au préambule propres à CET exercice (voir « Un seul repère d'exercice » ci-dessus). Un seul des exercices de l'épreuve a besoin de le fournir (peu importe lequel, la plateforme le rattache une seule fois à l'épreuve entière, sans jamais écraser une valeur déjà posée par un exercice précédent) ; tous les autres laissent `introduction_markdown` à `null`.

  Erreur déjà rencontrée, sous deux formes : (a) la même consigne recopiée à l'identique dans `enonce_intro_markdown` de CHAQUE exercice - `bac-d-ti-philo-2015-cameroun` et `probatoire-d-svt-2004-cameroun` répètent ainsi « Le candidat traitera au choix l'un des trois/deux sujets proposés » sur chacun de leurs exercices ; (b) la consigne casée dans `enonce_intro_markdown` du seul exercice 1, comme si elle ne concernait que lui - `probatoire-a-maths-2011-cameroun.pdf` (« L'épreuve comporte trois parties A, B et C obligatoires et indépendantes »), `bac-c-e-lit-cg-2017-cameroun.pdf` (« Le candidat traite l'un des trois sujets au choix »), `bac-c-maths-blanc-2003-cameroun.pdf` (« NB : le candidat doit traiter l'exercice et les DEUX problèmes »). Dans les deux cas, la consigne reste attachée à un exercice précis plutôt qu'à l'épreuve entière : un élève qui saute directement à l'exercice 2 ou 3 ne la voit jamais - alors qu'`introduction_markdown` s'affiche, lui, avant le premier exercice quel que soit celui que l'élève ouvre en premier.
- **Numérotation des sous-questions : celle de la source, jamais une numérotation orpheline.** Recopier fidèlement le repère que porte la source (`1.`, `2.3.`, `a)`) en tête du `enonce_markdown` est correct et attendu - la plateforme sait ne pas le doubler. En revanche, ne jamais laisser un repère de niveau inférieur **sans son parent** : un `enonce_markdown` qui commence par `ii.` alors qu'aucune sous-question `i.` n'existe dans l'exercice est un fragment de découpage, pas une numérotation. Dans ce cas, soit rétablir la numérotation complète telle qu'elle figure sur le sujet, soit retirer le préfixe. Défaut relevé sur bac-c-d-chimie-1999 et 2000, probatoire-c-d-chimie-2008 et 2011.
- `questions[].enonce_markdown` : reformulé, jamais recopié mot pour mot - reprendre les données mathématiques fidèlement mais reformuler la structure de phrase. Le texte commun à toutes les sous-questions (consigne partagée) va dans `enonce_intro_markdown`, pas répété dans chaque `enonce_markdown` - **y compris pour la toute première sous-question de la série**. `enonce_intro_markdown` est systématiquement affiché juste avant chaque sous-question, aussi bien en lecture d'épreuve qu'en quiz (où chaque sous-question peut être présentée seule) : le contexte partagé est donc déjà garanti présent, et le répéter dans la première sous-question ne sécurise rien, ça duplique simplement le texte à l'écran.

  Cas fréquent où cette règle se relâche : un exercice de probabilités/dénombrement avec un énoncé commun ("Une urne contient...") suivi de plusieurs événements lettrés à calculer (A, B, C, D...). Exemple concret :
  ```
  "enonce_intro_markdown": "Une urne contient dix jetons... Calculer la probabilité de chacun des événements suivants :"
  "questions": [
    { "numero": "A", "enonce_markdown": "A : « obtenir deux numéros pairs »." },
    { "numero": "B", "enonce_markdown": "B : « obtenir deux numéros impairs »." }
  ]
  ```
  Et non (erreur déjà rencontrée sur la sous-question A uniquement, alors que B/C/D/E de la même série suivaient correctement la règle) :
  ```
  { "numero": "A", "enonce_markdown": "Une urne contient dix jetons... On tire simultanément et au hasard 2 jetons de l'urne.\n\nA : « obtenir deux numéros pairs »." }
  ```

- **Barème d'une sous-question (`*[N points]*`) : sur la même ligne que la question, jamais en paragraphe séparé.** Écrire `"enonce_markdown": "**1.** Calculer $a$, $b$ et $c$. *[2 pts]*"` - pas de saut de ligne entre la question et son barème. La plateforme fusionne désormais automatiquement une annotation isolée sur sa propre ligne (rendu, pas la source), donc une source déjà mal formée ne casse plus l'affichage - mais rédiger directement en ligne dès la source reste la forme attendue, plus lisible telle quelle et indépendante de ce filet de sécurité.

- **Exercice à plusieurs Parties nommées** (« Partie A », « Partie B », « Section I », « Section II »...) : chaque Partie a son propre préambule, propre à ses seules sous-questions - jamais un préambule partagé par toutes les sous-questions de l'exercice entier, même quand `enonce_intro_markdown` semble être le seul endroit disponible pour l'écrire. `enonce_intro_markdown` reste réservé au repère de l'exercice et à ce qui est réellement commun à TOUTES ses sous-questions - jamais le nom d'une Partie, ni son préambule propre. Un exercice dont les Parties portent chacune leur propre préambule n'a donc souvent rien d'autre à y mettre que le repère lui-même : c'est la forme normale, pas un manque (voir « Un seul repère d'exercice » plus haut). Le nom et le préambule d'une Partie vont dans le `enonce_markdown` de sa PREMIÈRE sous-question (même logique que pour le préambule d'un QCM lettré ci-dessus), et ne sont pas répétés dans les sous-questions suivantes de la même Partie.

  Erreur déjà rencontrée : caser "Partie A" et le préambule de "Partie B" tous les deux dans `enonce_intro_markdown`. Résultat en lecture : "Partie A" apparaît comme un titre vide, immédiatement suivi du préambule de "Partie B" - avant même que les questions de la Partie A n'aient été posées. Correctement réparti :
  ```
  "enonce_intro_markdown": "**Exercice 1 (5 points)**"
  "questions": [
    { "numero": "A.1", "enonce_markdown": "**Partie A**\n\n1. Résoudre dans ℝ³ par la méthode du pivot de Gauss..." },
    { "numero": "A.2", "enonce_markdown": "2. Déduire de la question précédente..." },
    { "numero": "B.1", "enonce_markdown": "**Partie B.** Une urne contient 2 boules noires, 3 boules rouges et 4 boules vertes... Déterminer la probabilité de chacun des événements suivants :\n\n1. A : « les boules tirées sont de couleurs différentes »." },
    { "numero": "B.2", "enonce_markdown": "2. B : « les boules tirées sont de la même couleur »." }
  ]
  ```

- **Section qui regroupe PLUSIEURS exercices entiers, pas les sous-questions d'un seul** - à ne pas confondre avec « Exercice à plusieurs Parties nommées » ci-dessus, où les Parties découpent les sous-questions d'UN SEUL exercice. Cas fréquent sur le format d'évaluation par compétences camerounais : une épreuve annonce « A. Évaluation des ressources (10 points) » puis « B. Évaluation des compétences (10 points) », chaque lettre regroupant PLUSIEURS exercices numérotés indépendamment (ex. Exercices 1 et 2 sous « A. », Exercice 3 sous « B. »). Ce repère de section n'ouvre QUE l'`enonce_intro_markdown` du PREMIER exercice de la section - jamais recopié sur les exercices suivants de la même section, même identiquement. Chaque exercice garde bien sûr son propre repère (« **Exercice 2 : ...** ») ; c'est seulement le repère de SECTION au-dessus qui ne doit apparaître qu'une fois, sur le premier JSON de la section.

  Erreur déjà rencontrée, sur 8 épreuves du corpus (mathematiques-bepc-2024, mathematiques-bac-d-2023, informatique-bepc-2021/2023/2025/2026, sciences-de-la-vie-et-de-la-terre-bac-c-et-ti-2023, physique-chimie-technologie-bepc-2018) : le même repère de section recopié à l'identique en tête de CHAQUE exercice de cette section. Comme la plateforme affiche les exercices d'une même épreuve à la suite les uns des autres, le lecteur voit :
  ```
  A. Évaluation des ressources (10 points)

  Exercice 1 : Connaissances essentielles du cours (5 points)
  [... questions de l'exercice 1 ...]

  A. Évaluation des ressources (10 points)      <- répété, alors qu'aucune nouvelle
                                                    section ne commence ici
  Exercice 2 : Applications directes des savoirs et savoir-faire (5 points)
  [... questions de l'exercice 2 ...]
  ```
  Correctement réparti (seul le premier JSON de la section porte le repère de section dans `enonce_intro_markdown`) :
  ```
  // bepc-pct-2018-cameroun_exercice_1.json (ouvre la section A)
  "enonce_intro_markdown": "**A. Évaluation des ressources (10 points)**\n\n**Exercice 1 : Connaissances essentielles du cours (5 points)**"

  // bepc-pct-2018-cameroun_exercice_2.json (2e exercice de la MÊME section A)
  "enonce_intro_markdown": "**Exercice 2 : Applications directes des savoirs et savoir-faire (5 points)**"

  // bepc-pct-2018-cameroun_exercice_3.json (nouvelle section B : reprend le repère)
  "enonce_intro_markdown": "**B. Évaluation des compétences (10 points)**"
  ```
  Filet de sécurité côté plateforme : un repère de section répété à l'identique entre deux exercices consécutifs d'une même épreuve est aujourd'hui automatiquement masqué en lecture - mais mieux vaut livrer un JSON déjà propre que de compter sur ce filet, qui ne rattrape que la répétition EXACTE, mot pour mot, du même repère (une reformulation même légère, ou un barème différent dans le repère répété, le laisserait passer et redeviendrait visible pour l'élève).

  **`groupes` : la même information, mais déclarée sur CHAQUE exercice de la section, pas seulement le premier.** Contrairement à `enonce_intro_markdown` (qui ne porte le repère qu'une fois, pour ne pas le répéter visuellement à l'écran), `groupes` est une donnée structurée destinée au sommaire de navigation de la plateforme : chaque exercice de la section doit y lister la pile complète des repères dont il hérite, du plus englobant au plus imbriqué, même s'il ne les restate nulle part dans son propre texte. Une épreuve qui imbrique deux niveaux (« Partie A » puis « I - Évaluation des savoirs », chacun couvrant plusieurs exercices) donne une pile à deux éléments ; l'ORDRE de ces deux familles n'est pas fixe d'une épreuve à l'autre - recopier fidèlement l'ordre réellement imprimé sur CETTE épreuve (« Partie A » au-dessus de « I. » sur certains sujets, l'inverse sur d'autres format APC), jamais un ordre supposé. Reprenant l'exemple ci-dessus :
  ```
  // bepc-pct-2018-cameroun_exercice_1.json (ouvre la section A)
  "enonce_intro_markdown": "**A. Évaluation des ressources (10 points)**\n\n**Exercice 1 : Connaissances essentielles du cours (5 points)**"
  "groupes": ["A. Évaluation des ressources (10 points)"]

  // bepc-pct-2018-cameroun_exercice_2.json (2e exercice de la MÊME section A - hérite du groupe sans le restater dans enonce_intro_markdown)
  "enonce_intro_markdown": "**Exercice 2 : Applications directes des savoirs et savoir-faire (5 points)**"
  "groupes": ["A. Évaluation des ressources (10 points)"]

  // bepc-pct-2018-cameroun_exercice_3.json (nouvelle section B : reprend le repère ET met à jour groupes)
  "enonce_intro_markdown": "**B. Évaluation des compétences (10 points)**"
  "groupes": ["B. Évaluation des compétences (10 points)"]
  ```
- **`questions[].type_reponse`** : `"qcm"` uniquement quand la sous-question propose un choix fermé de réponses avec une seule correcte identifiable (cas déjà rencontré : QCM à 4-5 items) - renseigner alors `choix` (toutes les options, y compris les fausses) et `reponse_correcte`. La compétence connaît déjà cette information puisqu'elle doit citer la bonne réponse dans son corrigé - l'extraire en champ structuré permet une correction automatique côté plateforme.

  `choix` prend deux formes selon ce que propose la source, et `reponse_correcte` s'en déduit différemment dans chaque cas :
  - **Options déjà lettrées dans la source** (a) b) c) d), ou équivalent) : `choix` est une liste d'objets `{"lettre": "a", "texte": "..."}`, et `reponse_correcte` est cette lettre (ex. `"b"`).
  - **Options données en ligne dans l'énoncé, sans lettre** - cas très fréquent en Anglais, où la source présente les choix entre parenthèses séparés par des barres obliques directement dans la phrase (ex. « He ......... chokes. (may / always / likes) ») : `choix` est alors une simple liste de chaînes (ex. `["may", "always", "likes"]`). Il n'y a pas de lettre à recopier, mais ce n'est pas une raison de laisser `reponse_correcte` vide : y recopier le texte exact de la bonne option, caractère pour caractère depuis l'une des entrées de `choix` (ex. `"always"`).

  Dans les deux cas, `reponse_correcte` ne doit jamais rester vide pour une sous-question `"qcm"` - l'absence de lettre dans la source est le signal qu'il faut y recopier le texte de la réponse à la place, pas une exception qui dispense de le remplir. Pour toute autre sous-question (calcul, démonstration, rédaction), `"ouverte"` (valeur par défaut) et laisser `choix`/`reponse_correcte` vides
- **Vérification obligatoire avant de finaliser le JSON (champs à valeurs contraintes)** : l'ingestion valide plusieurs champs contre une liste fermée et rejette l'exercice entier dès qu'une valeur ne correspond pas, à la casse et à l'accent près. Avant de livrer, relire chaque champ ci-dessous et confirmer que sa valeur figure littéralement dans la colonne de droite - une valeur « raisonnable » mais hors liste (le pays, le nom de l'épreuve, un synonyme, une majuscule) échoue exactement comme une valeur absurde.

  | Champ | Seules valeurs acceptées |
  |---|---|
  | `pays` | `cm` \| `sn` \| `ci` \| `bj` \| `tg` \| `bf` \| `td` \| `ga` \| `cf` \| `cd` \| `cg` \| `gw` \| `ml` \| `ne` (jamais `null`) |
  | `examen` | `bepc` \| `bfem` \| `probatoire` \| `bac` \| `autre` - **jamais** `controle`, `devoir`, `composition`, `sequence`, `evaluation` : un contrôle, un devoir harmonisé ou une composition d'établissement se rattache au NIVEAU visé (`bac` pour une Terminale, `probatoire` pour une Première, `bepc` pour une 3e) et se distingue par `origine: "etablissement"` (+ `etablissement`). Constaté : `"examen": "controle"` sur terminale-ti-SI-vogt-2021-cameroun (4 exercices rejetés) ; `bac_blanc` est de la même famille de dérive |
  | `origine` | `officiel` \| `examen blanc` \| `sujet zero` \| `etablissement` \| `autre` |
  | `serie` | un ou plusieurs codes exacts du référentiel du pays traité, séparés par des virgules, ou `null` |
  | `nature_epreuve` | `theorique` \| `pratique` \| `null` (champ optionnel) |
  | `partie_epreuve_francais` | `etude de texte` \| `expression ecrite` \| `orthographe` \| `null` (champ optionnel, Français uniquement) |
  | `variante_sujet` | `sujet 1` \| `sujet 2` \| `null` (champ optionnel, toute matière) |
  | `filiere_serie_a` | `abi` \| `null` (champ optionnel, Cameroun/Série A uniquement) |
  | `institution` | texte libre, ou `null` - à ne renseigner que pour un examen blanc dont l'organisateur est nommé |
  | `statut` | `brouillon` |
  | `questions[].difficulte_estimee` | `faible` \| `moyenne` \| `élevée` |
  | `questions[].type_reponse` | `ouverte` \| `qcm` |
  | `figures[].origine_figure` | `enonce` \| `corrige` |

  Ce contrôle se fait par exercice, mais l'erreur, elle, est presque toujours collective : le même mauvais réflexe se reproduit sur les N exercices d'une même épreuve, puis sur les épreuves suivantes du même dossier. Quand une épreuve comporte plusieurs exercices, vérifier ces champs sur le premier JSON produit, puis s'assurer que les suivants portent bien la même valeur validée plutôt que de les remplir chacun de mémoire.

- **Vérification obligatoire avant de finaliser le JSON (QCM)** : pour chaque sous-question `"type_reponse": "qcm"`, relire `reponse_correcte` et confirmer qu'elle correspond exactement (lettre ou texte) à une entrée de `choix`. Une valeur vide ou qui ne correspond à aucune entrée fait échouer l'ingestion côté plateforme - l'exercice entier est alors rejeté, pas seulement la sous-question concernée. Corriger avant de livrer plutôt que de laisser la plateforme le découvrir au moment de l'ingestion.
- **Ne jamais inclure la fiche d'identité (En-tête standardisé, section précédente) dans `corrige_markdown`** : ces informations sont déjà structurées dans les champs `pays`, `matiere`, `serie`, `examen`, `origine`, `etablissement`, `annee`, `duree_epreuve`, `coefficient` du JSON. L'en-tête texte est utile en mode interactif (un corrigé livré seul) mais la plateforme ne l'affiche jamais dans le corps du contenu - c'est le frontend et le PDF qui affichent ces champs dans leur propre en-tête visuel, à partir des champs structurés uniquement, jamais depuis du texte libre
- **`questions[].numero`** : 10 caractères maximum (limite de stockage côté plateforme, qui rejette tout l'exercice si dépassée). Un repère de sous-question long comme "Présentation", "Conclusion" ou "Bonus" dépasse déjà cette limite à lui seul - abréger (ex. "Présent.", "Conclu.", "Bonus") plutôt que d'utiliser le mot complet. Ce champ reste un simple repère de tri, jamais le texte affiché à l'élève (qui vient de `enonce_markdown`) : l'abréger ne perd donc aucune information visible.
- **Accents et caractères français dans tous les champs texte** (`enonce_markdown`, `corrige_markdown`, `contenu_markdown`, `competence`, `themes`…) : toujours l'orthographe française complète (é, è, ê, à, ç, œ, ï…), jamais du texte « désaccentué » (« systeme », « reseau », « definition », « peripherique »). Constaté sur probatoire-blanc-ti-SI-bayangam-2023 : tout le lot écrit sans accents, ce qui donne un corrigé peu lisible pour l'élève et des thèmes en doublon avec leur forme accentuée (« reseau » / « réseau »). Le sujet source peut être saisi sans accents : ce n'est pas une raison de les omettre dans le corrigé. **Récidive constatée le 2026-09-20 sur 8 lots sur 9** (vogt-2021, bac-ti-SI-2024, bac-ti-programmation-2024/2025, bac-ti-reseau-2023, probatoire-ti-SI-2023, probatoire 2026 C/D/E et A) : corrigés, rappels et thèmes livrés sans accents (« Definir », « systeme », « resultat »), ET cours idem, y compris `meta.titre` (« Elaborer un diagramme de sequences ») - les élèves voient ces titres. Les seuls endroits sans accent sont les identifiants (`cours_id`, slugs, noms de fichier, `epreuve_source`), le CODE (blocs et `code inline`, noms de tables/champs/classes, chaînes affichées par un programme) et les valeurs de listes fermées. `meta.titre`, `meta.sous_theme`, `meta.tags`, `themes`, `competence`, les légendes de figures et tous les textes des sections d'un cours sont accentués. Un thème désaccentué recrée un doublon de Tag (« methode de developpement » / « méthode de développement » : 5 groupes fusionnés à la main). **Auto-contrôle avant de livrer** : la « Checklist de sortie de lot » ci-dessous signale les mots courants restés sans accent hors code ; en trouver = reprendre le fichier, pas le livrer.
- **`questions[].rappels_de_methode`** : extraire chaque bloc `### Rappel de méthode` du corrigé de CETTE sous-question comme un objet distinct, rattaché à elle (pas à une autre sous-question du même exercice). Cinq clés, et seulement ces cinq : `id`, `competence`, `contenu_markdown`, `cours_genere`, `cours_id` - jamais de clé alternative (constaté : `texte` à la place de `contenu_markdown`, une entrée réduite à `cours_id`+`texte` sans `id`). L'ingestion ne lit que ces cinq clés précises : une entrée sans `id` fait rejeter tout l'exercice, et même quand l'id est par ailleurs récupérable, un contenu placé sous une clé inconnue comme `texte` n'est jamais lu - le rappel est alors créé vide plutôt qu'avec le contenu voulu. `cours_genere` et `cours_id` restent toujours `false`/`null` dans le JSON d'exercice, y compris en traitement en lot : ce n'est jamais la compétence qui pose ce lien. La plateforme le renseigne elle-même, une fois le cours ingéré séparément (voir "Génération des cours en lot") - inutile d'anticiper une valeur ici, elle serait de toute façon ignorée à l'ingestion.

  **⚠ Règle de fidélité absolue pour `contenu_markdown`** : ce champ doit contenir une copie littérale, caractère par caractère, du texte qui suit le titre `### Rappel de méthode` dans le `corrige_markdown` de la sous-question à laquelle ce rappel est rattaché. La plateforme utilise une correspondance de chaîne exacte pour localiser et injecter visuellement ce bloc dans le corrigé affiché — toute reformulation, même légère (synonyme, ordre des mots, ponctuation), casse cette correspondance silencieusement et le rappel disparaît pour l'élève. Ne pas résumer, ne pas reformuler, ne pas "améliorer" : copier-coller. Ce texte reste, par construction, une règle générale et non un extrait de la réponse chiffrée (voir « Le contenu sous `### Rappel de méthode` est une règle générale, jamais un extrait de la réponse » dans le Template obligatoire) : si le `corrige_markdown` source mélange règle générale et application dans le même bloc `### Rappel de méthode`, corriger le corrigé source avant d'en extraire le rappel, plutôt que de recopier un extrait de l'application chiffrée dans `contenu_markdown`.

  **Copie INTÉGRALE, jamais tronquée** : `contenu_markdown` reprend tout le paragraphe qui suit le titre, de sa première à sa dernière phrase - pas seulement son début. Un extrait raccourci (constaté : 138 caractères stockés pour un paragraphe de 301) ne correspond plus au bloc du corrigé et le lien « Voir le cours complet » perd sa place. Corollaire de la règle « Le bloc Rappel reste UN SEUL paragraphe » : le texte à copier est ce paragraphe unique, en entier.

  **Procédure de vérification obligatoire avant de finaliser le JSON** : pour chaque objet dans `questions[].rappels_de_methode`, vérifier que la valeur de `contenu_markdown` se trouve verbatim dans le `corrige_markdown` de la même sous-question (une simple recherche de sous-chaîne suffit). Si la vérification échoue pour un rappel, deux actions sont requises :
  1. Corriger `contenu_markdown` pour qu'il corresponde exactement au texte présent dans `corrige_markdown`.
  2. Si la correction est impossible (ex. le bloc a été supprimé du corrigé), ajouter en toute fin du `corrige_markdown` de cette sous-question le marqueur de secours suivant, sur sa propre ligne : `<!-- RAPPEL_NON_APPARIE: <id-du-rappel> -->`. Ce marqueur permet à la plateforme de détecter le rappel orphelin et de le traiter manuellement plutôt que de le perdre silencieusement.
- Nommer les fichiers : `<nom_epreuve>_exercice_<numero>.json` dans un dossier portant le nom de l'épreuve source
- **Composition LaTeX dans les environnements matriciels et les tableaux de variations** (`enonce_markdown`/`corrige_markdown`) : trois erreurs de syntaxe récurrentes cassent le rendu KaTeX côté plateforme sans produire aucune erreur JSON ni aucun signal visible à la relecture du texte brut - vérifier chacune avant de livrer.
  1. **Séparateur de ligne dans une matrice/un système** (`\begin{cases}`, `pmatrix`, `bmatrix`, `vmatrix`, `matrix`, `array`) : toujours deux backslashes (`\\`) entre deux lignes, jamais un seul. Un backslash isolé immédiatement suivi d'un chiffre ou d'un signe moins (ex. `\2a+b=0`) n'est jamais une commande LaTeX valide dans ce contexte - c'est systématiquement un séparateur de ligne auquel il manque son second backslash.
     ```
     Correct   : \begin{cases} 2a+b=0 \\ -a+b-3c=0 \end{cases}
     Incorrect : \begin{cases} 2a+b=0 \-a+b-3c=0 \end{cases}
     ```
  2. **`\hline` jamais collé au token qui suit**, dans un tableau de variations : toujours un espace après `\hline` avant la valeur/lettre suivante (`\hline x`, jamais `\hlinex`). TeX lit un mot de commande comme absorbant toute lettre qui le suit directement, donc `\hlinex` est lu comme la commande inconnue `\hlinex` plutôt que `\hline` suivi de « x ». Cet espace est toujours invisible au rendu final : l'ajouter systématiquement ne casse jamais un tableau déjà correct, donc aucune raison de l'omettre par prudence.
  3. **Spécificateur de colonnes d'un `\begin{array}{...}`** : avant de le fixer (`{c|cccc}`, etc.), compter le nombre RÉEL de colonnes utilisées par la ligne la plus chargée du tableau - pas seulement au premier coup d'œil. Un tableau de variations à plusieurs points de rupture ajoute une colonne de valeur ET une colonne de flèche/signe par point de rupture : au-delà de 2-3 points de rupture, il est facile de sous-compter et de déclarer moins de colonnes que la ligne `x` ou la ligne de signe n'en utilise réellement, ce qui fait échouer le rendu du tableau entier plutôt que d'un seul point.

  **Vérification obligatoire avant de finaliser le JSON** : pour chaque bloc contenant `\begin{cases}`/`pmatrix`/`bmatrix`/`vmatrix`/`matrix`/`array}`, recompter à la main les séparateurs `\\` entre les lignes, les occurrences de `\hline`, et - pour un `array` - le nombre de colonnes déclarées dans le spécificateur contre le nombre réellement utilisé par la ligne la plus chargée. Ces trois erreurs ne provoquent aucune erreur de validation JSON et ne sautent pas aux yeux en relisant le texte brut : seul un rendu KaTeX réel les révèle, ce qui n'arrive qu'une fois le contenu déjà publié et visible d'un élève.

- **Auto-contrôle `savoir_officiel` avant de clore un lot** : une fois tous les exercices d'une épreuve produits, si la matière figure au périmètre du référentiel, relire les JSON du lot et compter les sous-questions dont `savoir_officiel` vaut `null`. Une épreuve entièrement à `null` sur une matière couverte n'est jamais un résultat normal : c'est le signe que le fichier fixture n'a pas été ouvert (voir l'étape 1 - Cadrage). Reprendre alors le tagging plutôt que de livrer. Si le `null` généralisé est réellement justifié (aucun module ne correspond à cette classe, ex. Histoire 3e absente du référentiel alors que la Géographie 3e y figure), le dire dans le compte rendu final à l'utilisateur, pas dans `incertitudes` - ce champ n'est pas un journal de traitement.

### Génération des cours en lot

Chaque bloc `### Rappel de méthode` produit pendant la correction donne lieu à un objet JSON "cours" dans la même passe que les corrigés, un fichier par rappel - jamais fusionné avec le JSON de l'exercice. Aucune demande utilisateur supplémentaire n'est requise : un dossier d'épreuves traité produit des corrigés **et** des cours.

**Catalogue de titres existants - à demander si absent.** Avant de traiter un dossier, si l'environnement (tâche planifiée, runner) ne l'a pas déjà fourni, demander la liste des titres de `Cours` déjà publiés pour la matière et le pays traités (`Cours.objects.filter(subject=..., statut=VALIDE).values_list("titre", flat=True)`). L'ingestion (`ingest_cours`) rattache de toute façon tout nouveau cours à un titre déjà existant (comparaison insensible à la casse) plutôt que de le dupliquer - mais elle le fait après avoir reçu le JSON complet, donc après que la compétence ait déjà rédigé les 7 sections en pure perte. Le catalogue permet d'éviter ce travail inutile en amont :
- **Le nom de la compétence correspond exactement (insensible à la casse, mêmes principes que la comparaison faite à l'ingestion) à un titre du catalogue** : ne pas rédiger les 7 sections. Émettre uniquement le squelette minimal requis pour que l'ingestion rattache ce rappel au cours existant - `cours_id` (un identifiant nouveau, déterministe, dérivé du rappel comme d'habitude ; l'ingestion ne le trouvera pas par `external_id` et retombera sur la correspondance de titre), `meta.titre` copié à l'identique du catalogue, `source.rappel_id`, et `sections: []`. Ne jamais deviner qu'une correspondance existe sur une simple ressemblance de formulation - "Résolution d'équations du second degré" et "Étude du signe d'un trinôme" sont deux notions distinctes même si elles apparaissent souvent ensemble ; en cas de doute, générer le cours complet plutôt que risquer un rattachement à une notion différente.
- **Un squelette (`sections: []`) n'est valable QUE s'il rattache le rappel à un titre RÉELLEMENT présent dans le catalogue fourni, identique accents compris, ET s'il porte tous les champs obligatoires de l'ingestion : `cours_id`, `meta.titre`, `meta.matiere` (règle de la Série TI comprise), `source.rappel_id`.** Deux défauts constatés le 2026-09-20 : 9 « squelettes » de bac-ti-SI-2025 sans `meta.matiere` et sans catalogue correspondant (le titre existait sans accents, le nouveau avec) - coquilles vides, rejetées à l'ingestion ; ~70 cours de 6 lots avec `source.rappel_id: null`, rejetés en bloc (« Champs obligatoires manquants : cours_id, meta.titre, meta.matiere, source.rappel_id »). Sans catalogue, ou au moindre doute sur l'égalité des titres : cours complet en 7 sections, jamais un squelette « par prudence ».
- **Aucune correspondance** : générer le cours complet, normalement.
- Si aucun catalogue n'a été fourni et ne peut être obtenu, générer chaque cours complet - l'ingestion reste le filet de sécurité qui empêche la publication d'un doublon, seule l'économie de génération est perdue.
- **Un rappel par cours en sortie**, jamais un cours partagé explicitement par plusieurs rappels dans le JSON : si deux rappels de la même épreuve désignent la même compétence, chacun produit son propre fichier cours (complet ou squelette selon la règle ci-dessus) avec son propre `source.rappel_id` - c'est l'ingestion, pas la compétence, qui les fait converger vers le même `Cours` en base via la correspondance de titre.
- **Nommage** : `<nom_epreuve>_cours_<competence_slug>.json`, dans le même dossier que les JSON d'exercices et les PNG de figures de l'épreuve. Le `competence_slug` est dérivé du champ `competence` du rappel (minuscules, accents supprimés, espaces en tirets).
- **Aucun rappel sans cours, aucun cours sans rappel.** Chaque objet de `questions[].rappels_de_methode` donne un fichier cours dont `source.rappel_id` est l'`id` exact de CE rappel (jamais `null`, jamais reconstruit). Quand la notion est déjà couverte par un autre cours du même lot, ne pas laisser le rappel orphelin : émettre un squelette valide (règle précédente) vers le titre de ce cours. Constaté : 29 rappels de 6 lots sans aucun cours associé, rattachés à la main a posteriori.
- **Traçabilité obligatoire** : `source.epreuve_id`, `source.epreuve_titre`, `source.exercice_numero` et `source.rappel_id` sont toujours renseignés en lot, même pour un squelette de doublon - c'est ce qui permet à l'ingestion de retrouver le `RappelDeMethode` à rattacher. `correction_id` peut rester `null` si l'identifiant est attribué par la plateforme au moment de l'ingestion.
- **Exemple résolu de la section 4** (cours complet uniquement) : privilégier l'exercice de l'épreuve source qui a fait naître le rappel, avec `epreuve_source: true`. Ne construire un exemple ad hoc que si l'exercice d'origine est trop long ou dépend d'une figure illisible.
- **Référentiel pays non confirmé** : le cours hérite de l'incertitude du corrigé. Mettre `meta.serie` à `null` plutôt qu'un code deviné, et reprendre la mention dans les `incertitudes` de l'exercice source.
- **Traitement partiel** : si le volume oblige à s'arrêter avant la fin, livrer d'abord tous les corrigés de l'épreuve, ensuite les cours. Un corrigé sans cours reste exploitable, un cours sans corrigé ne l'est pas. Cette limitation porte sur le NOMBRE de cours livrés dans la passe, jamais sur le niveau de détail d'un cours déjà entamé - un cours commencé se termine intégralement (les 7 sections, section 6 avec ses 3 `solution_markdown` complets) ou n'est pas livré du tout ; voir la "Vérification obligatoire" de la section 6 ci-dessous.
- **Publication automatique, sans relecture humaine** : un cours ingéré passe directement en ligne, visible et vendable. Le niveau d'exigence du principe fondamental et de la structure en 7 sections ci-dessous n'est donc pas une précaution parmi d'autres à respecter "raisonnablement" - c'est la seule vérification qui existe avant qu'un élève ne voie ce contenu.
- **⚠ `source.rappel_id` doit être l'`id` EXACT d'un rappel réellement présent dans le JSON de l'exercice, jamais une valeur reconstruite depuis la convention de nommage.** Cas déjà rencontré, ayant produit des dizaines de cours définitivement inexploitables (l'ingestion refuse tout cours dont le `rappel_id` ne correspond à aucun `RappelDeMethode` existant) : des cours générés pour des épreuves déjà ingérées par le passé (session différente de celle qui a produit les corrigés d'origine), où la compétence a *déduit* un `rappel_id` plausible en appliquant le motif `rdm-<epreuve_source>-ex<numero_exercice>-q<numero>-<index>` plutôt que de relire l'`id` réellement présent dans le JSON d'exercice déjà livré. Le motif de nommage est un guide pour *produire* un nouvel id, jamais une garantie que cet id existe déjà quelque part - une convention ancienne (un seul rappel par exercice, sans segment `q<numero>`) a pu être utilisée au moment où l'exercice a été traité.

  **Avant de finaliser tout lot de cours portant sur une épreuve qui n'a pas été corrigée dans cette même session** : relire le(s) JSON d'exercice source déjà produit(s) pour cette épreuve (sur disque si accessible, ou tel que fourni en entrée) et vérifier que chaque `source.rappel_id` s'écrit à l'identique, caractère pour caractère, d'un `id` déjà présent dans `questions[].rappels_de_methode[]` de cet exercice. Si un rappel de méthode réellement pertinent n'existe pas encore dans l'exercice source (aucun bloc `### Rappel de méthode` correspondant dans son `corrige_markdown`), il n'y a alors que deux options légitimes - jamais une troisième consistant à inventer l'id : (a) ne pas générer ce cours maintenant, et signaler dans les `incertitudes` qu'un enrichissement du corrigé source serait nécessaire d'abord ; (b) si le contexte le permet, corriger/compléter d'abord le `corrige_markdown` de la sous-question concernée pour y ajouter le bloc `### Rappel de méthode` manquant (avec son entrée dans `rappels_de_methode`), puis dériver `source.rappel_id` de ce nouvel id.

---

## Mode cours - génération de contenu pédagogique

### Déclenchement

Deux voies d'activation : l'une explicite, l'autre automatique.

**Voie 1 - demande de l'utilisateur (mode interactif).** Le critère est l'intention, pas la formule exacte : activer le mode cours dès que la demande porte sur un contenu qui *enseigne une notion*, par opposition à un contenu qui *résout un exercice donné*. Sont couverts, entre autres :
- "générer un cours", "créer un cours", "produire une fiche de cours", "faire le cours associé à ce rappel"
- "fiche de révision", "fiche sur <notion>", "leçon sur <notion>", "explique la notion de <X> à mes élèves", "il me faut le contenu pédagogique sur <X>"
- la fourniture d'un ou plusieurs blocs `### Rappel de méthode` accompagnés d'une demande de développement, quelle qu'en soit la formulation

Toute production relevant du mode cours passe par la structure en 7 sections et le format JSON décrits plus bas, y compris quand l'utilisateur emploie le mot "fiche" : une fiche livrée en texte libre n'est pas ingérable par la plateforme. Si la demande hésite entre corriger et enseigner, demander plutôt que trancher - un cours livré à la place d'un corrigé fait perdre autant de temps que l'inverse.

**Voie 2 - génération automatique en mode automatisation (traitement en lot).** Lors du traitement d'un dossier d'épreuves, chaque bloc `### Rappel de méthode` produit dans les corrigés déclenche la génération d'un cours dans la même passe, sans demande supplémentaire. Règles détaillées à la section "Mode automatisation - Génération des cours en lot".

**Ce qui ne déclenche pas le mode cours** : une demande de correction en mode interactif (un exercice, une épreuve, un PDF fourni en chat) reste un corrigé, même quand elle produit des rappels de méthode. Le cours ne s'y ajoute que si l'utilisateur le demande.

### Principe fondamental

Le cours doit permettre à l'élève de **s'approprier la notion**, pas seulement de la mémoriser. S'approprier une notion, c'est traverser trois étapes dans l'ordre :

1. **Comprendre** - saisir le sens de la méthode, pas juste la formule. Pourquoi cette technique existe, quelle situation-problème elle résout, ce qu'elle permet de faire que rien d'autre ne permet.
2. **Voir faire** - observer un raisonnement complet déroulé pas à pas, avec chaque décision expliquée. Pas seulement le calcul : le choix de la méthode, la détection du type de problème, la vérification.
3. **Faire soi-même** - pratiquer sur des exercices de difficulté croissante avec un feedback immédiat possible.

Un cours qui saute l'une de ces trois étapes ne permet pas l'appropriation - il produit un élève capable de réciter mais pas de transférer.

### Niveau de qualité exigé

Identique aux corrigés : expert, rigoureux, sans marqueurs IA, avec la voix d'un enseignant qui pense à voix haute. Appliquer les mêmes règles de style rédactionnel (section "Style rédactionnel - éliminer les marqueurs IA"). Le cours est un contenu vendu sur la plateforme au même titre que les corrigés.

### Lien obligatoire avec l'épreuve source

Tout cours généré depuis un rappel de méthode est obligatoirement lié à l'épreuve d'origine. Ce lien est tracé dans les deux sens :
- Le cours porte une section `source` pointant vers `epreuve_id`, `correction_id` et le `rappel_id` dont il est issu
- L'objet `rappels_de_methode` du corrigé correspondant porte `cours_genere: true` et le `cours_id` : renseignés par la compétence elle-même en traitement en lot, par la plateforme quand le cours est produit après coup depuis un rappel déjà ingéré

La déduplication entre épreuves différentes est gérée côté plateforme, pas côté skill. À l'intérieur d'une même épreuve traitée en lot, la déduplication est en revanche à la charge de la compétence : un cours par compétence, pas par occurrence (voir "Génération des cours en lot"). En mode interactif, générer un cours par rappel fourni.

### Structure obligatoire du cours (7 sections)

#### Section 1 — Accroche et sens de la notion
Répondre à la question implicite de l'élève : "Pourquoi j'apprends ça ?" Une situation concrète, une question que ce cours va permettre de résoudre, le lien avec ce que l'élève connaît déjà. 3 à 5 phrases maximum. Pas d'inventaire de définitions - une entrée narrative qui donne envie de lire la suite.

#### Section 2 — Prérequis
Liste des notions que l'élève doit maîtriser avant d'aborder ce cours. Formulée du point de vue de l'élève : "Pour suivre ce cours, tu dois savoir..." Ne pas surcharger - se limiter aux prérequis réellement bloquants.

#### Section 3 — La règle / la méthode
Le cœur de la notion : définition, propriété, théorème ou procédure, formulés avec la même rigueur que dans les corrigés. Encadrer visuellement la formule ou la règle centrale (bloc à mettre en évidence par la plateforme). Si deux méthodes concurrentes existent pour le même type de problème, les présenter toutes les deux et préciser quand choisir laquelle.

#### Section 4 — Exemple résolu pas à pas
Un exemple complet, issu si possible de l'épreuve source ou du même type. Chaque étape est numérotée. Pour chaque étape : l'action réalisée ET le raisonnement qui la justifie. Respecter la règle absolue des corrigés : aucune étape masquée, aucun "on en déduit directement". À la fin de l'exemple, une phrase de conclusion qui nomme explicitement ce qu'on vient de démontrer.

#### Section 5 — Erreurs classiques commentées
2 à 4 erreurs typiques commises par les élèves sur ce type de problème. Pour chaque erreur : montrer le raisonnement erroné, expliquer pourquoi c'est faux (pas juste "c'est faux"), montrer la correction. C'est la section qui ancre le plus durablement la méthode - ne pas la traiter comme un addendum.

#### Section 6 — Exercices d'appropriation
3 exercices de difficulté croissante : un exercice d'application directe (vérifier que la règle est comprise), un exercice intermédiaire (adapter la méthode à un contexte légèrement différent), un exercice d'approfondissement (combiner avec une autre notion ou résoudre dans un cas général). Chaque exercice a : un énoncé, un niveau de difficulté, et une solution complète disponible (même niveau de détail que les corrigés).

**Vérification obligatoire avant de finaliser le JSON (Exercices d'appropriation)** : pour chacun des 3 exercices, relire l'item émis et confirmer qu'il porte bien `numero`, `difficulte`, `enonce_markdown` ET `solution_markdown` non vide - jamais une simple chaîne de caractères réduite à l'énoncé seul (la plateforme accepte ce format dégradé pour ne pas planter, mais publie alors l'exercice sans aucune solution, invisible à la relecture puisqu'un cours en lot n'a aucune relecture humaine - voir "Génération des cours en lot"). Un exercice sans solution est pire qu'une absence de cours : il expose l'élève à une question sans jamais lui permettre de vérifier sa réponse. En mode automatisation (lot), si le volume de rappels à traiter crée une pression de temps ou de longueur de sortie, ne jamais réduire le niveau de détail d'une section déjà commencée pour aller plus vite - réduire plutôt le nombre de cours traités dans la passe (voir la règle "Traitement partiel" de la section suivante) : un cours non traité peut être généré à la prochaine passe, un cours publié avec des exercices sans solution reste en ligne, vendu, jusqu'à correction manuelle.

#### Section 7 — Ce qu'il faut retenir
Synthèse en 4 à 6 points. Pas une liste de règles à réciter : des phrases-clés qui encapsulent le raisonnement, formulées de façon à être mémorables. Tutoyer l'élève. Terminer par un rappel du lien avec les examens : dans quel type de questions ce contenu est évalué au BAC/Probatoire/BEPC.

### Format de sortie JSON (pour affichage dynamique sur la plateforme)

```json
{
  "cours_id": "cours-<competence_slug>-<niveau>-<serie>",
  "meta": {
    "titre": "Intitulé du cours (ex. 'Résolution d'équations du second degré')",
    "matiere": "un des intitulés fermés de la règle `matiere` du mode automatisation ci-dessus - même liste, même table de rattachement, jamais une formulation inventée. **Série TI : jamais `Informatique`** - toujours l'une des trois matières dédiées `Programmation`, `Systèmes d'Information` ou `Réseaux, Internet et Sécurité Informatique`, celle que le rappel de méthode à l'origine du cours illustre réellement (même règle, même décision du 2026-09-17, que `matiere` en mode automatisation - voir « Série TI, jamais `Informatique` » plus haut). `meta.matiere` d'un cours suit toujours le `matiere` de l'exercice source dont son rappel est issu, jamais une valeur reconstruite indépendamment",
    "pays": "code ISO du pays traité, mêmes valeurs et mêmes règles que le champ pays de l'exercice source - jamais null",
    "serie": "code exact du pays traité (voir Référentiel) - null si le cours s'applique à toutes les séries",
    "sous_theme": "sous-domaine du programme (ex. 'Équations et inéquations')",
    "duree_estimee_min": 25,
    "tags": ["discriminant", "factorisation", "racines"],
    "savoir_officiel": {"classe": "1ere", "serie_label": "C-E", "module_numero": "21", "savoir_numero": "II"} ou null,
    "statut": "brouillon"
  },
  "source": {
    "epreuve_id": "identifiant de l'épreuve d'origine (ex. 'BAC-C-2024-MATHS-S2')",
    "epreuve_titre": "libellé complet de l'épreuve",
    "exercice_numero": "3",
    "rappel_id": "rdm-BAC-C-2024-MATHS-S2-ex3-0",
    "rappels_lies": ["autres rappels de la même épreuve couverts par ce cours - liste vide si le cours ne couvre qu'un seul rappel"],
    "correction_id": "corr-BAC-C-2024-MATHS-S2-ex3"
  },
  "sections": [
    {
      "type": "accroche",
      "contenu_markdown": "..."
    },
    {
      "type": "prerequis",
      "items": ["Calcul littéral", "Identités remarquables"]
    },
    {
      "type": "regle",
      "titre": "La méthode du discriminant",
      "contenu_markdown": "...",
      "formule_principale": "\\Delta = b^2 - 4ac",
      "variantes": [
        {
          "nom": "Méthode par factorisation",
          "quand_utiliser": "Quand les racines sont des entiers visibles",
          "contenu_markdown": "..."
        }
      ]
    },
    {
      "type": "exemple_resolu",
      "enonce_markdown": "Résoudre dans $\\mathbb{R}$ : $x^2 - 5x + 6 = 0$",
      "epreuve_source": true,
      "etapes": [
        {
          "numero": 1,
          "action": "Identifier les coefficients a, b, c",
          "justification": "L'équation est sous forme standard $ax^2 + bx + c = 0$",
          "resultat_markdown": "$a = 1,\\; b = -5,\\; c = 6$"
        },
        {
          "numero": 2,
          "action": "Calculer le discriminant",
          "justification": "On applique $\\Delta = b^2 - 4ac$",
          "resultat_markdown": "$\\Delta = (-5)^2 - 4 \\times 1 \\times 6 = 25 - 24 = 1$"
        },
        {
          "numero": 3,
          "action": "Analyser le signe de $\\Delta$",
          "justification": "$\\Delta > 0$ : l'équation admet deux solutions réelles distinctes",
          "resultat_markdown": "$x_1 = \\frac{5 - 1}{2} = 2 \\quad ; \\quad x_2 = \\frac{5 + 1}{2} = 3$"
        }
      ],
      "conclusion_markdown": "L'ensemble des solutions est $S = \\{2\\;; 3\\}$."
    },
    {
      "type": "erreurs_classiques",
      "items": [
        {
          "erreur_markdown": "Écrire $\\Delta = b^2 + 4ac$ en oubliant le signe moins",
          "pourquoi_faux": "La formule est $b^2 - 4ac$. Le signe moins vient de la structure même de l'équation du second degré - changer ce signe modifie radicalement le nombre de solutions.",
          "correction_markdown": "Toujours recopier la formule complète $\\Delta = b^2 - 4ac$ avant de substituer les valeurs."
        },
        {
          "erreur_markdown": "Oublier le cas $\\Delta = 0$ et conclure 'pas de solution'",
          "pourquoi_faux": "$\\Delta = 0$ signifie une racine double, pas l'absence de solution. L'équation a alors exactement une solution $x_0 = -b/(2a)$.",
          "correction_markdown": "Distinguer systématiquement trois cas : $\\Delta > 0$ (deux solutions), $\\Delta = 0$ (une solution double), $\\Delta < 0$ (pas de solution réelle)."
        }
      ]
    },
    {
      "type": "exercices_application",
      "items": [
        {
          "numero": 1,
          "difficulte": "facile",
          "enonce_markdown": "Résoudre dans $\\mathbb{R}$ : $x^2 - 7x + 12 = 0$",
          "solution_markdown": "..."
        },
        {
          "numero": 2,
          "difficulte": "moyen",
          "enonce_markdown": "Déterminer les valeurs de $k$ pour lesquelles $x^2 + kx + 9 = 0$ admet une racine double.",
          "solution_markdown": "..."
        },
        {
          "numero": 3,
          "difficulte": "approfondissement",
          "enonce_markdown": "Résoudre dans $\\mathbb{R}$ le système : $x + y = 5$ et $xy = 6$. (Indication : se ramener à une équation du second degré.)",
          "solution_markdown": "..."
        }
      ]
    },
    {
      "type": "synthese",
      "items_markdown": [
        "Face à une équation $ax^2 + bx + c = 0$, commence toujours par identifier $a$, $b$, $c$ avant tout calcul.",
        "Le signe de $\\Delta = b^2 - 4ac$ décide du nombre de solutions : trois cas, trois conclusions différentes.",
        "Si $\\Delta = 0$, l'équation a une solution (double), pas zéro.",
        "Au BAC, ce type d'exercice apparaît seul ou comme étape d'un problème plus long (étude de fonction, géométrie analytique). Maîtriser le calcul de $\\Delta$ est donc un automatisme de base, pas une fin en soi."
      ]
    }
  ]
}
```

### Règles de qualité spécifiques au mode cours

- **`statut` toujours `"brouillon"`** dans le JSON, par convention de sortie - `ingest_cours` l'ignore et publie le cours en `VALIDE` dès l'ingestion, visible et vendable immédiatement, sans relecture humaine. Traiter chaque cours comme si un élève allait le lire dans les minutes qui suivent sa génération - parce que c'est exactement ce qui se passe
- **`epreuve_source: true`** dans l'exemple résolu si l'exemple provient directement de l'épreuve liée - la plateforme peut alors afficher un lien "Voir l'exercice original"
- **Pas de contenu inventé dans `source`** : si `epreuve_id` ou `correction_id` ne sont pas fournis par l'utilisateur, mettre `null` et le signaler
- **`duree_estimee_min`** : estimation réaliste du temps de lecture + pratique des exercices pour un élève moyen du niveau cible
- **`meta.savoir_officiel`** : même champ et même règle (jamais inventé, `null` par défaut) que dans le mode automatisation - voir sa description détaillée plus haut
- **Exercices de la section 6** : les solutions doivent respecter la même règle absolue que les corrigés (aucune étape masquée)
- **Test final avant livraison** : relire le cours et se demander - "Un élève qui n'a jamais vu cette notion, après avoir lu ce cours et fait les trois exercices, est-il capable de résoudre seul un exercice similaire en examen ?" Si non, enrichir avant de livrer.

---

## Checklist de sortie de lot (auto-contrôle AVANT de déclarer un dossier livré)

Les défauts de format ci-dessus se répètent d'un lot à l'autre (6 à 8 lots sur 9 le 2026-09-20) : les relire ne suffit pas, il faut les MESURER. Avant de livrer un dossier d'épreuve, exécuter le script ci-dessous (Python standard, aucune dépendance, pas de Docker requis) et ne livrer que sur `LOT PROPRE` ; chaque `[ALERTE]` est soit corrigée, soit justifiée dans le compte rendu final.

```bash
python verifier_lot.py <dossier_epreuve>   # ex. ingest/cm/bac-ti-reseau-2023-officiel-cameroun
```

Le script contrôle : `examen` dans la liste fermée ; Série TI ⇒ `matiere` parmi les trois matières TI (exercices ET cours) ; Cameroun ⇒ pas de `A1..A5` ; nombre de `rappels_de_methode` = nombre de titres `### Rappel de méthode` par sous-question, aucun rappel « en ligne » ; chaque sous-question a des `themes` ; chaque cours a `cours_id`, `meta.titre`, `meta.matiere` et un `source.rappel_id` qui existe dans les exercices du dossier ; squelettes signalés ; mots courants sans accent hors code ; `$` littéral hors code. Il ne remplace pas `tunnel_validation.sh` (thèmes, rendu KaTeX), il le précède.

```python
"""Auto-contrôle d'un dossier d'épreuve avant livraison (stdlib uniquement).
Usage : python verifier_lot.py <dossier_epreuve>   -> code 1 si un défaut BLOQUANT."""
import glob, json, re, sys, os

EXAMENS = {"bepc", "bfem", "probatoire", "bac", "autre"}
MATIERES_TI = {"Programmation", "Systèmes d'Information", "Réseaux, Internet et Sécurité Informatique"}
# mots courants qui, écrits sans accent, trahissent un texte « désaccentué » (hors code)
SANS_ACCENT = re.compile(
    r"\b(systeme|systemes|reseau|reseaux|methode|methodes|donnees|definir|definition|resultat|resultats|"
    r"etape|etapes|ecrire|probleme|modele|precedent|verifier|determiner|caracteristique|caracteristiques|"
    r"generale|utilise|realise|eleve|evenement|requete|selection|proprietes|periph\w+|memoire|numerique|"
    r"specifique|deduire|elaborer|representer|identifier_)\b", re.I)


def hors_code(s):
    s = re.sub(r"```.*?```", " ", s, flags=re.S)
    return re.sub(r"`[^`\n]*`", " ", s)


def textes(o, chemin=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from textes(v, chemin + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from textes(v, "%s[%d]" % (chemin, i))
    elif isinstance(o, str):
        yield chemin, o


def main(d):
    bloq, alertes = [], []
    rappel_ids = set()
    exos = sorted(glob.glob(os.path.join(d, "*_exercice_[0-9]*.json")))
    coursf = sorted(glob.glob(os.path.join(d, "*_cours_*.json")))
    for f in exos:
        j = json.load(open(f, encoding="utf-8")); n = os.path.basename(f)
        if j.get("examen") not in EXAMENS:
            bloq.append("%s : examen=%r hors liste (contrôle/devoir/composition → niveau visé + origine « etablissement »)" % (n, j.get("examen")))
        serie = str(j.get("serie") or "")
        if re.search(r"\bTI\b", serie) and j.get("matiere") not in MATIERES_TI:
            bloq.append("%s : série TI mais matiere=%r (Programmation | Systèmes d'Information | Réseaux, Internet et Sécurité Informatique)" % (n, j.get("matiere")))
        if re.search(r"\bA[1-5]\b", serie) and j.get("pays") == "cm":
            bloq.append("%s : Cameroun, série %r → le code est « A » (jamais A1..A5)" % (n, serie))
        for q in j.get("questions", []):
            rds = q.get("rappels_de_methode") or []
            c = q.get("corrige_markdown") or ""
            titres = len(re.findall(r"^###\s*Rappel de m[eé]thode\s*$", c, flags=re.M))
            for r in rds: rappel_ids.add(r.get("id"))
            if re.search(r"\*\*Rappel de m[eé]thode\.?\*\*", c):
                bloq.append("%s q%s : « **Rappel de méthode.** » en ligne → titre « ### Rappel de méthode » exigé" % (n, q.get("numero")))
            if len(rds) != titres:
                bloq.append("%s q%s : %d rappel(s) déclaré(s) mais %d titre(s) « ### Rappel de méthode » dans le corrigé" % (n, q.get("numero"), len(rds), titres))
            blocs = [re.sub(r"\A###\s*Rappel de m[eé]thode\s*\n+", "", m.group(0)).strip()
                     for m in re.finditer(r"###\s*Rappel de m[eé]thode\s*\n+.*?(?=\n{2,}|\n#{1,6}[ \t]|\n---|\Z)", c, flags=re.S | re.I)]
            for r in rds:
                ct = (r.get("contenu_markdown") or "").strip()
                if blocs and not any(ct and (ct.startswith(b) or b.startswith(ct)) for b in blocs):
                    bloq.append("%s q%s : rappel %s - contenu_markdown n'est pas la copie littérale d'un bloc du corrigé (lien « Voir le cours complet » rejeté en fin d'exercice)" % (n, q.get("numero"), r.get("id")))
            if not q.get("themes"):
                bloq.append("%s q%s : aucun thème" % (n, q.get("numero")))
        sa = sum(len(SANS_ACCENT.findall(hors_code(t))) for _, t in textes(j) if len(t) > 30)
        if sa > 3: alertes.append("%s : %d mot(s) courant(s) sans accent hors code (texte désaccentué ?)" % (n, sa))
    for f in coursf:
        c = json.load(open(f, encoding="utf-8")); n = os.path.basename(f)
        m, s = c.get("meta") or {}, c.get("source") or {}
        if not (c.get("cours_id") and m.get("titre") and m.get("matiere")):
            bloq.append("%s : cours_id / meta.titre / meta.matiere manquant (même pour un squelette)" % n)
        if not s.get("rappel_id"):
            bloq.append("%s : source.rappel_id nul" % n)
        elif rappel_ids and s["rappel_id"] not in rappel_ids:
            bloq.append("%s : source.rappel_id=%r absent des exercices du dossier" % (n, s["rappel_id"]))
        if str(m.get("serie") or "") == "TI" and m.get("matiere") == "Informatique":
            bloq.append("%s : série TI et matiere « Informatique »" % n)
        if not c.get("sections"):
            alertes.append("%s : squelette (sections vides) - valable seulement si le titre est IDENTIQUE, accents compris, à un titre du catalogue" % n)
        if SANS_ACCENT.search(m.get("titre") or ""):
            alertes.append("%s : titre sans accents" % n)
        for chemin, t in textes(c):
            if re.search(r"(?<![\$`])\$(?!\$)", hors_code(t)) and hors_code(t).count("$") % 2:
                alertes.append("%s %s : `$` littéral hors code" % (n, chemin)); break
    print("Dossier %s : %d exercice(s), %d cours" % (d, len(exos), len(coursf)))
    for b in bloq: print("[BLOQUANT]", b)
    for a in alertes: print("[ALERTE]", a)
    print("LOT PROPRE" if not bloq else "LOT À CORRIGER")
    return 1 if bloq else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

## Tunnel de validation - dernière étape obligatoire de tout round d'ingestion

Un round n'est JAMAIS déclaré terminé sur la seule foi de « l'ingestion n'a pas échoué » : les écarts constatés jusqu'ici (rendu KaTeX cassé, questions sans thème, quasi-doublons de thèmes, QCM incohérent) passaient l'ingestion sans erreur et n'apparaissaient qu'après coup, en obligeant à lancer des campagnes de rattrapage. Après l'ingestion, lancer depuis la racine du dépôt (`D:\edukora`) :

```bash
bash scripts/tunnel_validation.sh <since> [--strict]
```

`<since>` = durée depuis le début du round (`2h`, `90m`, `1d`) ou datetime ISO : le tunnel ne valide que le contenu créé ou modifié depuis cet instant. Il enchaîne (1) la structure - Question sans thème, QCM incohérent (BLOQUANT) ; (2) le vocabulaire de thèmes - quasi-doublons de Tag, thèmes partagés entre matières (ALERTE) ; (3) la couverture - quiz/cours manquants pour les thèmes touchés (INFO) ; (4) le rendu - le VRAI moteur KaTeX/remark sur ce périmètre.

- La sortie `TUNNEL VALIDÉ` (code 0) est exigée avant de conclure ; la citer dans le rapport final.
- `ingerer_et_valider.sh` sort en 0 quand tout est « déjà existant, ignoré » : le périmètre du tunnel est alors vide et cette sortie ne prouve rien. Sur un dossier déjà ingéré, valider avec `tunnel_validation.sh <since>` (fenêtre couvrant la réingestion). Après correction d'un exercice déjà en base, le réingérer avec `force=True` (jamais tout le lot) ; un cours déjà en base ne se met pas à jour par réingestion (`ingest_cours` est idempotent sur `cours_id`) : le supprimer puis le réingérer. La boucle complète (classer les erreurs, corriger, réingérer, valider) est celle du skill `tunnel-completude-edukora`.
- BLOQUANT ou échec de rendu : corriger la donnée (JSON source) puis réingérer. Si la même anomalie revient d'un round à l'autre, la signaler à l'utilisateur comme défaut de plateforme (`catalog/rendering.py`, `catalog/ingestion_repairs.py`) au lieu de la repatcher à la main.
- ALERTE de quasi-doublon de Tag : soit un thème équivalent existe déjà (reprendre sa forme exacte dans le JSON et réingérer), soit les deux sont réellement distincts, et le rapport le dit explicitement. Jamais de fusion en masse sans l'utilisateur.
- Avant de fournir des `themes`, quand la base est accessible (`docker exec edukora-backend-1`), chercher la forme existante du thème (accents, singulier/pluriel, casse) plutôt que d'en inventer une variante : c'est la source des quasi-doublons.
- Le rattachement `savoir_officiel` n'entre PAS dans ce tunnel (mis en standby le 2026-09-18, l'organisation se fait par thèmes) : un `null` n'est pas un défaut à corriger.
- Environnement sans accès à docker/à la base (tâche planifiée Cowork) : le dire dans le rapport - le round reste NON validé tant que le tunnel n'a pas tourné depuis Claude Code.
- Le code du tunnel vit dans l'image du backend (pas de bind-mount) : si `valider_ingestion` est « Unknown command », reconstruire (`docker compose build backend && docker compose up -d backend`).

---

## Ce que cette compétence ne doit jamais faire

- Ne jamais présenter un résultat non vérifié comme certain en maths/sciences
- Ne jamais recopier un sujet d'examen officiel protégé sans reformulation
- Ne jamais sacrifier la clarté pédagogique pour la concision
- Ne jamais omettre, sous-entendre ou compresser une étape de calcul ou de raisonnement, même triviale pour un expert
- Ne jamais inventer la valeur d'un champ à liste fermée (`matiere`, `origine`, `examen`, `type_reponse`, `difficulte_estimee`, `origine_figure`, `statut`) : ces champs se recopient depuis la liste autorisée, ils ne se déduisent pas du contexte de l'épreuve. En particulier, ne jamais faire entrer le pays, le nom du dossier ou le nom du fichier PDF dans `origine` ; pour `matiere`, utiliser la table de rattachement dédiée plutôt que d'inventer une formulation voisine de l'intitulé source
- Ne jamais écrire une plage d'années (« 2023/2024 ») dans `annee` : toujours un entier à 4 chiffres (la seconde année de la plage) ou `null`
- Ne jamais générer un cours sans renseigner la section `source` (même avec des `null` documentés) - un cours sans traçabilité vers son épreuve source ne peut pas être lié correctement par la plateforme
- Ne jamais clore un traitement en lot en laissant un rappel de méthode sans cours associé sans l'avoir signalé dans le compte rendu final à l'utilisateur (jamais dans les `incertitudes` de l'exercice, qui ne sont pas un journal de traitement) - un rappel orphelin passe inaperçu jusqu'à ce qu'un élève clique sur un lien vide
- Ne jamais corriger un exercice dépendant d'une figure sans avoir inspecté visuellement la page qui la contient ; ne jamais inventer le contenu d'une figure illisible
- Ne jamais se contenter de décrire en texte un tracé que le corrigé doit produire (construction géométrique, courbe, schéma, graphique) : le réaliser en image, voir « Figures produites dans le corrigé »
- Ne jamais laisser un `$` littéral (variable PHP, référence de tableur, symbole monétaire) hors d'un span ou bloc de code ni échappé : voir « Le caractère `$` hors formule doit toujours être protégé » - la règle vaut pour TOUS les champs texte d'un cours, pas seulement `contenu_markdown` : `resultat_markdown`, `pourquoi_faux`, `solution_markdown`, `items`, `items_markdown` (constaté : `echo $?` et `while($ligne = mysqli_fetch_assoc(...))` nus dans deux cours de programmation, échecs du rendu KaTeX au tunnel). Tout fragment de code en prose se met entre accents graves.
- Ne jamais déclarer un round d'ingestion terminé sans la sortie `TUNNEL VALIDÉ` de `scripts/tunnel_validation.sh` (voir « Tunnel de validation »)