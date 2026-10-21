# Session élève : Gogo / recherche « pythagoras theorem » (lien partagé) / local

- Date : 2026-10-20 (heures non relevées ; session d'environ 10 minutes) ; commit local : 9adaece5 + changements non committés
- Terrain : local ; URL de départ : `http://localhost/en/cm/search?q=pythagoras+theorem`
- Persona : Gogo (Form 5, GCE O Level, interface anglaise), compte déjà connecté, profil actif « Gogo » au départ (aucune bascule, aucun code demandé) ; **appareil : bureau** (l'émulation 375x812 n'a pas pris : `innerWidth` 1534)
- Mode d'exécution : **sous-agent à contexte neuf**, piloté dans Chrome
- Calibrage : non testé cette session

## Verdict de mission
**Réussie** en environ 2 minutes utiles : Gogo trouve la leçon, un quiz de 6 questions et 10 exercices d'annales sur Pythagoras, ouvre un corrigé d'annale et répond à deux questions. Ce qu'il retient : le site a une leçon gratuite claire, des annales corrigées et un quiz sur le sujet. Ce qui lui échappe : ce que veut dire « Included » (F2), et que la leçon le renvoie à d'autres leçons plutôt que vers l'entraînement (F7).

## Journal (extrait)
1. **Page de recherche** : filtre « My exam · GCE O Level » déjà actif, 16 résultats, compteurs Sujet (Mathematics 12, Additional Mathematics 4) et Type (Past papers 6, Lessons 9, Topics 1), bloc « START HERE » (1 leçon, 10 exercices, 6 questions de quiz, bouton « Test my knowledge »). Tout est en anglais, aucun contenu BEPC/BAC. La leçon est en tête ; « Circle Theorems » en deuxième, du bruit. Extraits de « Vectors » sans formules.
2. **Leçon** (carte « Free ») : chapeau local (un peintre à Kumba), table des matières, 5 sections, 25 min, KaTeX propre, solutions de l'exercice 1 à la demande. Pas de schéma de triangle. En bas : seulement « Other Mathematics lessons ».
3. **Quiz** : session de 6 questions. Q1 « essaie sur brouillon puis voir la solution » avec auto-évaluation (Right / Partly right / Wrong), Q2 QCM (isocèle 17, 17, 16 : aire 120 cm²) vert, série, « Understand the solution ». Compteur « 25 / 20 points » dès la Q1.
4. **« Solved exercises on this topic »** (nouvel onglet) : « Exercises on Pythagoras theorem », 10 exercices par année, « 50 % of the official sessions, 8 of 16 », progression 1/10. Un exercice 2025 P2 : énoncé, bloc « On your topic », solution de la question a (PQ = 50 km) avec rappel de méthode. Titre « Exercice 4 » en français.
5. **Retour arrière vers le quiz** : l'URL passe de `/quiz/session/467` à `/468` : nouvelle question 1/6, 0/0 correct, 40 points conservés.
6. **Recherches affinées** : « pythagorus » → un seul résultat, correction proposée « pythagore » (français) ; « Pythagoras' theorem » → mêmes 16 résultats ; « right-angled triangle » → 37 résultats, extraits sans chiffres ; filtre Quiz → en-tête « 37 results » pour 3 cartes ; « All exams » + Quiz → page vide, « 19 results », aucun message.
7. **Fiche d'annale 2023 Paper 2** : Solution, 14 exercices, 2 h 30, « Read the solution », « Take it in exam conditions », « Download the paper » (non cliqué) ; arrivée non ancrée sur l'exercice du thème.

## Ce qui marche bien (à ne pas casser)
- Le lien partagé arrive déjà filtré sur l'examen de l'élève (GCE O Level) : rien en français, rien du BEPC ou du BAC.
- Le bloc « START HERE » résume le sujet en trois chiffres et propose un seul gros bouton.
- La leçon est bien écrite (accroche locale, plan, « Common mistakes », solutions à la demande, « Key points »), KaTeX propre.
- Le quiz : retour immédiat, points, série, solution détaillée avec « Method reminder » et pont vers les annales.
- La page « Exercises on Pythagoras theorem » (50 % des sessions, rang, progression) répond exactement à la phrase du professeur ; « On your topic » met la sous-question visée en évidence.
- Apostrophe gérée (« Pythagoras' theorem »), recherche en direct, défilement restauré au retour, 0 erreur console, réponse de la recherche ~0,3 s.

## Frictions
| Id | Sév. | Catégorie | Étape | Observé | Attendu | Preuve | Confiance | Statut |
|---|---|---|---|---|---|---|---|---|
| P-F1 | S2 | langue | Exercice d'annale | Titre « Exercice 4 », onglet « Exercice 4 - Pythagoras theorem », énoncé « Exercice 4 (4 points) » sur une page anglaise ; les cartes de résultats disent « Corrigé d'annale » alors que la fiche dit « Solution » | « Exercise 4 », « Past paper with solutions » | captures, `document.title` | élevée | nouvelle (même famille que les restes de langue déjà traités) |
| P-F2 | S2 | fonctionnel | « All exams » avec le type Quiz actif | Page vide : « 19 results » en tête, Quiz 0, aucune carte, aucun message d'état vide (alors que « My exam » donnait 3 quiz dont « pythagoras theorem ») | Le filtre se réinitialise, ou un état vide explique | capture | élevée | nouvelle |
| P-F3 | S3 | langue | « pythagorus » | Correction proposée « pythagore » (mot français) ; un seul résultat au lieu de 16 | « pythagoras », mêmes résultats que la requête juste | texte sous le compteur | élevée | nouvelle |
| P-F4 | S3 | contenu | Résultats | Les formules disparaissent des extraits : « gives the length of the hypotenuse: . in a right-angled triangle », « measures cm », « The inverse of is a) b) c) d) » | Extraits lisibles | cartes Vectors, Papers, Quiz | élevée | nouvelle |
| P-F5 | S3 | UX | Fin de leçon | Seulement « Other Mathematics lessons » (Probability, Polynomials…) ; rien vers le quiz de 6 questions ni les 10 exercices d'annales du même thème | Un bloc « Practise this topic » | capture du bas de page | élevée | nouvelle |
| P-F6 | S3 | confiance/vente | Résultats | « Free » (leçons) et « Included » (annales, exercices, quiz) sans explication ni infobulle ; rien n'indique ce qui deviendrait payant | « Included in your plan » | DOM, pas de `title` | moyenne (compte abonné ; écran visiteur non vu) | proche de R-F8 / E-F5 |
| P-F7 | S3 | UX | Recherche | Le bloc annonce 10 exercices, la liste n'en montre que 5 (et 1 annale) ; l'annale ouverte n'est pas ancrée sur l'exercice du thème | Compteur cohérent, lien vers les 10, ancre | texte de la page | moyenne | nouvelle |
| P-F8 | S3 | fonctionnel | Retour vers le quiz | `/quiz/session/467` devient `/468` : nouvelle question 1/6, la session en cours est perdue | Retrouver la session | captures, URL | moyenne | nouvelle |
| P-F9 | S3 | UX | Quiz | Compteur « 25 / 20 points » dès la Q1, puis « 30 / 20 », « 40 / 20 » | Un libellé qui dit de quoi il s'agit (hypothèse : l'objectif quotidien de 20 points dépassé) | captures | élevée sur le fait, faible sur la cause | nouvelle |
| P-F10 | S4 | UX | Filtre Type = Quiz | En-tête « 37 results » pour 3 cartes affichées | « 3 results » | capture | élevée | nouvelle |
| P-F11 | S4 | UX | Leçon | « Exercises » dans la table des matières ajoute une entrée d'historique au hash français `#exercices_application` ; deux retours pour revenir | Hash anglais ou pas d'entrée d'historique | URL | élevée | nouvelle |
| P-F12 | S4 | UX | Quiz | « Solved exercises on this topic » s'ouvre dans un nouvel onglet sans préavis | Même onglet | onglet apparu | élevée | nouvelle |
| P-F13 | S4 | contenu | Leçon | Aucun schéma de triangle rectangle | Un schéma a, b, c | lecture complète | moyenne | nouvelle |
| P-F14 | S4 | contenu | Quiz | La Q1 (7, 24, 25) reprend l'exercice 2b de la leçon ; une option « 46.0 cm² » | Variété ; valeur entière | comparaison, capture | moyenne / faible | nouvelle |
| P-F15 | S4 | UX | « All exams » | Bruit : Philosophy A Level 2023 via « DeMorgan's Theorem » ; « Circle Theorems » deuxième pour « pythagoras » | Meilleur classement | liste | moyenne | nouvelle |
| P-F16 | — | outil | — | Émulation mobile inopérante | — | `innerWidth` 1534 | élevée | limite du test |

## Mesures (bureau, cache chaud)
- Page de recherche : ~95 ms de navigation, 50 ressources, ~12,7 Ko transférés au premier chargement ; `/recherche/` ~280 ms, 3,6 Ko transférés ; autres appels `/catalog/…` 50 à 120 ms.
- La leçon appelle deux fois `/access/cours/read/…` et trois fois `/catalog/cours/…` : doublons mineurs.
- Console : aucune erreur.

## Idées d'amélioration (classées effet / effort)

**1. Effet élevé, effort faible**
- **Corriger l'état vide et le compteur du filtre Type** (P-F2, P-F10) : un message quand un filtre ne laisse rien (« No quiz for All exams. Clear the filter »), et un compteur d'en-tête qui suit le filtre. Aujourd'hui l'élève peut croire que le site n'a pas de quiz.
- **Traduire « Exercice » et « Corrigé d'annale » côté anglais** (P-F1) : même chantier que les restes de langue précédents ; un balayage des libellés de l'espace annales en anglais éviterait d'y revenir un par un.
- **Proposer la bonne correction orthographique** (P-F3) : pour « pythagorus » proposer « pythagoras » (la langue de l'examen filtre déjà les résultats ; la suggestion doit suivre la même règle).
- **Garder les nombres dans les extraits** (P-F4).

**2. Effet élevé, effort moyen**
- **Fin de leçon : « Practise this topic »** (P-F5) avec le quiz du thème et les exercices d'annales (le site les a déjà, la page « Exercises on Pythagoras theorem » existe). C'est le chaînon manquant entre comprendre et s'entraîner.
- **Rendre le quiz repris** (P-F8) : revenir sur la session en cours plutôt qu'en créer une nouvelle ; **ouvrir « Solved exercises » dans le même onglet** (P-F12).
- **Expliquer « Free » / « Included »** (P-F6) par une infobulle ou une ligne sous la liste ; à voir aussi côté visiteur.

**3. Effet moyen**
- **Compteur du quiz** (P-F9) : nommer le total (« 25 pts today · goal 20 ») ou le plafonner visuellement.
- **Ancrer l'annale sur l'exercice du thème** et aligner « 10 exercices » avec la liste (P-F7).
- Un schéma de triangle rectangle dans la leçon (P-F13), un hash de section en anglais (P-F11).

## Diagnostic [phase B]
Non fait. À regarder en premier si vous le demandez : P-F2 / P-F10 (les compteurs et le filtre Type sont calculés dans `recherche/moteur.py` et le frontend de recherche), P-F3 (`corrige` dans `recherche/moteur.py` : la liste de mots proposée n'est pas filtrée par la langue de l'examen, comme l'était `completer` avant la correction d'hier), P-F8 (démarrage de session quiz au retour arrière).

## Ce que cette session ne dit pas
- Pas de rendu mobile (émulation inopérante) : tactile, 3G, hauteur d'écran restent à tester.
- Compte abonné : l'écran d'un visiteur (cadenas, mur de paiement, ce qui est vraiment gratuit) n'a pas été vu.
- 2 questions de quiz sur 6 ; « Take it in exam conditions », « Download the paper » et la page des tarifs non essayés ; aucun test de requête française comme élève GCE.
- Pas de mesure de motivation ni de relecture scientifique du contenu ; testeur simulé.

## Corrections, 1er lot : P-F2, P-F10, P-F3, P-F4 (2026-10-20, non committé)

| Friction | Cause | Correction | Preuve |
|---|---|---|---|
| P-F3 « pythagorus » → « pythagore » | Phase B : `_recherche` passe à `corriger` la RACINE du mot (« pythagor » en anglais), dont le voisin le plus proche et le plus fréquent du catalogue est le mot français « pythagore » (1 résultat) ; la langue de l'examen n'entrait pas dans le choix | `moteur.proposer` classe jusqu'à 4 voisins (prononciation d'abord, puis fautes de frappe) ; `_recherche` essaie jusqu'à 6 jeux de corrections et garde celui qui donne le PLUS de résultats dans les filtres (examen, langue). `corriger` garde son contrat | 3 tests (`test_langue.py` : GCE → « pythagoras », francophone → « pythagore », classement des voisins) ; **le test GCE échoue quand on limite à un seul essai** ; sur les vraies données : « pythagorus » → « pythagoras », **20 résultats au lieu de 1** |
| P-F4 formules absentes des extraits | `texte.nettoyer` retirait toute formule, y compris pour l'affichage | `nettoyer(..., formules=True)` (utilisé par `apercu` et `extrait`) convertit la formule en texte lisible (`formule_lisible` : `a² + b² = c²`, `3/4`, `√25`, `90°`, `∠ ABC`, `×`…), « … » au-delà de 60 caractères ; le texte INDEXÉ garde le retrait (les lettres a, b, c ne deviennent pas des mots à chercher) ; les formules sont réinsérées après le nettoyage (leurs `<`, `>` ne sont pas pris pour du HTML) | 4 tests `recherche/tests.py` ; sur les vraies données après réindexation : « …interior angles of a triangle is a) 90° b) 270° c) 360° d) 180° » au lieu de « … is a) b) c) d) » |
| P-F10 « 37 results » pour 3 cartes | En-tête = total de toute la recherche | Dans un onglet, le nombre est celui de l'onglet | 1 test `RecherchePage.test.tsx` |
| P-F2 page vide avec « All exams » + Quiz | **Réinterprété** : ce n'était pas une incohérence du moteur (les « 3 quiz » du filtre « My exam » appartenaient à la requête « right-angled triangle », pas à « pythagoras theorem », qui n'a aucun quiz) : l'onglet Quiz restait dans l'adresse alors que la requête n'en donnait pas, et la page était vide sans un mot | Un message (« Aucun résultat de type « Quiz » pour « … » avec ces filtres ») et un bouton « Voir les N résultats, tous types confondus » qui retire le type | 1 test |

**Vérification** : backend `recherche` 207 verts ; frontend 94 fichiers, 844 verts, `tsc` propre ; caddy reconstruit, backend patché (`docker cp` + redémarrage) et **index de recherche reconstruit en local** (`indexer_recherche`, 85 s, 74 600 lignes) pour que les aperçus stockés prennent les formules. Résultat non revu à l'écran.

**À rejouer en production** : rebuild caddy + backend, puis **`manage.py indexer_recherche`** (les aperçus stockés changent).

**Non traitées** (hors de ce lot) : P-F1 (« Exercice 4 », « Corrigé d'annale » en français sur une page anglaise : libellés de l'espace annales), P-F5 (fin de leçon sans lien vers quiz et annales), P-F6 (« Free / Included » inexpliqué), P-F7, P-F8 (retour arrière = nouvelle session de quiz), P-F9 (compteur « 25 / 20 points »), P-F11 à P-F15.

## Corrections, 2e lot : ce qui était clair (2026-10-20, non committé)

| Friction | Correction | Preuve |
|---|---|---|
| P-F1 « Exercice 4 » / « Corrigé d'annale » en français | Fiche d'exercice d'un thème (`ThemeExerciceLecturePage`) : `libelleTitreExercice` (« Exercice 4 » devient « Exercise 4 » hors français, titre d'onglet compris) et `libelleEnteteExercice` sur l'énoncé (« **Exercice 4 (4 points)** » devient « **Exercise 4 (4 marks)** »). Cartes de recherche : le type d'une épreuve était cherché par le libellé exact (« Corrigé »), or le serveur envoie « Corrigé d'annale » ; il est maintenant reconnu par son début, et traduit hors français (le français reste inchangé) | tests `libellesEpreuve.test.ts` et `RecherchePage.test.tsx` (« Solution · … » en anglais, « Corrigé d'annale · … » en français) |
| P-F6 « Free » / « Included » inexpliqués | Infobulles « Gratuit pour tous, sans abonnement. » / « Compris dans ton abonnement. » (et leurs versions anglaises) | 1 test |
| P-F11 hash français et entrées d'historique | Le sommaire d'un cours ou d'une épreuve défile jusqu'à la section et met l'adresse à jour avec `replaceState` : plus d'entrée d'historique à chaque clic (le hash garde l'identifiant interne de la section) | 1 test (`SommaireNav.test.tsx`) |
| P-F9 « 25 / 20 points » | C'était l'objectif d'XP du jour dépassé : au-delà, l'en-tête du quiz et la fin de séance disent « 35 points · objectif atteint » (l'accueil le disait déjà) | test `SemaineDeSerie.test.tsx` adapté |

**Vérification** : frontend 95 fichiers, 848 verts, `tsc` propre, caddy reconstruit. Non revu à l'écran.

**Laissé, avec la raison.**
- **P-F5** (fin de leçon vers quiz et annales du thème) : l'idée est claire, mais un lien sans contenu derrière (thème sans quiz ou sans exercices) serait pire que rien ; il faut d'abord savoir si le thème de la leçon a un quiz et des exercices (une requête de plus par leçon). À cadrer.
- **P-F7** (« 10 exercices » annoncés, 5 listés) : les deux nombres comptent des choses différentes (exercices rattachés au thème, contre exercices trouvés par le texte de la requête, 5 par page avec « Voir les N ») ; ce n'est pas une erreur de comptage mais un libellé ambigu. À trancher avec vous.
- **P-F8** (retour arrière = nouvelle session de quiz) : cause non établie (reprise de session ou création au chargement de `/quiz?theme=`) ; phase B à faire avant de toucher.
- **P-F12** (« Solved exercises » dans un nouvel onglet) : choix qui garde la séance de quiz ouverte, probablement voulu ; à confirmer.
- **P-F13, P-F14, P-F15** : contenu (schéma, doublon quiz/leçon, option « 46.0 cm² ») et classement de recherche ; ni l'un ni l'autre ne se règle par un correctif simple.

## Analyse des quatre frictions laissées et propositions (2026-10-20, lecture seule, rien modifié)

### P-F8 : le retour arrière crée une nouvelle session de quiz : **cause établie, correctif d'une ligne**

- Le bouton « Test my knowledge » mène à `/quiz?cursus=…&theme=…`. Cette page lance la séance toute seule (effet d'auto-lancement de `QuizStartPage`, `themeAutoLanceRef`), puis fait `navigate("/quiz/session/467")` **sans `replace`** (`QuizStartPage.tsx`, fonction `lancer`).
- Historique : `[recherche, /quiz?…&theme=…, /quiz/session/467]`. « Retour » depuis la séance ramène sur `/quiz?…&theme=…`, qui **se remonte et relance une séance** : `/quiz/session/468`, question 1/6, la 467 abandonnée. Les liens `DepuisLaDerniereFois`, `ThemesFrequents` et `InediteResultPage` passent tous par ce même auto-lancement : le défaut est général.
- **Proposition** : quand la séance vient de l'auto-lancement (paramètre `theme` dans l'adresse), `navigate(…, { replace: true })`. « Retour » sort alors du quiz vers la page d'où l'élève venait (ici la recherche). Un lancement manuel depuis le formulaire garde l'historique normal. **Effort : faible** (1 appel + 1 test de `QuizStartPage`). Aucun risque pour la reprise : la séance 467 reste rejoignable par son adresse.

### P-F12 : « Solved exercises on this topic » s'ouvre dans un nouvel onglet : **voulu, mais mal servi**

- Le code le dit : « dans un nouvel onglet pour ne pas perdre le fil de la séance » (`QuizSessionPage.tsx`, `target="_blank"`). Raison valable avant ; aujourd'hui, une séance de quiz est **enregistrée côté serveur et se rouvre par son adresse**, donc revenir en arrière ne la perd pas, à condition que P-F8 soit corrigé (sinon « Retour » en crée une nouvelle).
- Coût du nouvel onglet : sur téléphone, un onglet de plus sans signal visible (aucune icône « lien externe »), et un fil d'historique séparé pour l'exercice.
- **Options** : (A) garder l'onglet et ajouter l'icône de lien externe + « (new tab) » dans le libellé ; (B) **même onglet** (recommandé, une fois P-F8 corrigé) : « Retour » ramène à la même question du quiz. **Recommandation : B**, mobile d'abord. **Effort : faible** (retirer `target` et `rel`, 1 test). À décider avec vous.

### P-F7 : « 10 exercices » annoncés, 5 listés : **deux univers de comptage**

Mesuré sur « pythagoras theorem » (GCE O Level) : le thème a `nb_exercices = 10` (exercices **rattachés au thème** : c'est la liste de la page « Exercises on Pythagoras theorem »), alors que la liste de résultats contient 5 exercices et 1 annale (exercices dont le **texte** contient la requête, 5 par page, « Voir les N » pour le reste). Les deux sont justes ; l'élève lit « 10 » puis voit « 5 ».
- **Option A (recommandée, effort faible)** : quand un thème est mis en avant (« START HERE »), **ne pas lister d'exercices à part** s'ils sont déjà ceux du thème ; garder le bouton unique « 10 solved exercises » qui mène à la page du thème. Une seule source, un seul nombre.
- **Option B (effort moyen)** : remplacer, dans la liste, les exercices trouvés par le texte par les exercices du thème, les plus fréquents à l'examen d'abord.
- **Option C (effort très faible, pas de fond)** : renommer le groupe « Exercices mentionnant « pythagoras theorem » » pour dire la différence.
- Liée à P-F7 : l'annale (« Mathematics 2023 Paper 2 ») s'ouvre en haut de page, pas sur l'exercice du thème. Une ancre `#exercice-N` dans le lien de la carte règle cette moitié (**effort faible**, `ancre_exercice` existe déjà dans `recherche/texte.py`).

### P-F5 : fin de leçon sans lien vers l'entraînement : **le risque de cul-de-sac est faible, à mesurer côté serveur**

Mesure sur la base locale : sur 14 192 cours validés, **98,5 % (13 982) ont un thème qui a des exercices d'annales et 74 % (10 568) un quiz**. Les compteurs existent déjà (`nb_quiz`, `nb_exercices` du thème indexé pour la recherche).
- **Proposition** : l'API d'un cours renvoie `entrainement` : jusqu'à 2 thèmes de la leçon qui ont du contenu `{theme_id, nom, nb_quiz, nb_exercices}` (lu dans l'index de recherche, sans requête de plus par thème). Le frontend affiche en fin de leçon, **seulement si la liste n'est pas vide**, un bloc « Practise this topic » avec deux boutons : « Quiz · 6 questions » (`/quiz?cursus=…&theme=…`) et « Solved exam exercises · 10 » (page du thème). Chaque bouton n'apparaît que si son compteur est supérieur à zéro : aucun lien mort.
- **Effort : moyen** (champ serveur + composant + 2 tests). **Effet : élevé** : c'est le chaînon « j'ai compris, je m'entraîne » que le rapport pointe (P-F5), et le bloc réutilise ce que le site a déjà.
- À décider : le bloc doit-il aussi apparaître **avant** les exercices d'application du cours (au milieu) pour l'élève qui n'arrive jamais en bas ? Je propose la fin de leçon d'abord, à mesurer ensuite.

### Ordre conseillé
1. **P-F8** (1 ligne, bug réel, S3).
2. **P-F12 option B** une fois P-F8 en place.
3. **P-F7 option A + ancre de l'annale** (même zone de code que la recherche déjà retouchée).
4. **P-F5** (le plus gros, le plus utile).

## Corrections, 3e lot : P-F8 et P-F12 (2026-10-20, non committé)

| Friction | Correction | Preuve |
|---|---|---|
| P-F8 retour arrière = nouvelle séance | `QuizStartPage.lancer(theme, depuisLeLien)` : l'auto-lancement d'un lien `/quiz?…&theme=…` fait `navigate("/quiz/session/N", { replace: true })` ; un lancement manuel depuis le formulaire garde l'historique normal. Corrige aussi les liens `DepuisLaDerniereFois`, `ThemesFrequents` et `InediteResultPage`, qui passent par le même auto-lancement | test `QuizStartPage.test.tsx` (historique `[recherche, /quiz?…&theme=7]` : après la séance, « Retour » arrive sur `/recherche` et **une seule** séance est créée) ; **le test échoue** quand on remet `replace: false` |
| P-F12 exercices du thème dans un nouvel onglet | Le pont « Exercices corrigés sur ce thème » est un `Link` de l'application, dans le même onglet (plus de `target="_blank"`) : « Retour » rouvre la séance, qui est enregistrée côté serveur | test `QuizSessionPage.retour.test.tsx` (adresse `/cm/themes-frequents/7/exercices?subject=MATHS&cursus=14`, pas de `target`) |

**Vérification** : frontend 95 fichiers, 850 verts, `tsc` propre, caddy reconstruit. Non revu à l'écran (parcours à rejouer sous Gogo : recherche → « Test my knowledge » → réponse → « Exercices corrigés » → Retour doit revenir à la même question, puis Retour doit quitter le quiz sans nouvelle séance).

**Reste** (non demandé dans ce lot) : P-F7 (option A + ancre de l'annale) et P-F5 (bloc « Practise this topic »), décrits plus haut.
