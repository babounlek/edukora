# 10 - Audit produit « l'outil idéal de l'élève qui prépare son examen »

Date : vendredi 2026-11-13 (J-18 avant le lancement du 1er décembre, J-199 avant le BEPC 2027).
Angle : expérience de l'élève abonné, caractère ludique, fonctionnalités, exploitation des données. Complète les audits 00 à 09 (prêt au lancement, SEO, visiteur) sans les refaire.

## 1. Verdict

EduKora a déjà ce que la plupart des concurrents n'ont pas : un contenu profond (2 149 épreuves corrigées, 15 061 cours, 25 442 items de quiz, 257 inédites en base locale), une séance du jour justifiée par « ce qui tombe », et une couche ludique réelle (points, niveaux, série, objectif, mascotte, sons, confettis, partage).

Ce qui l'empêche d'être l'outil idéal tient en cinq points :

1. **La boucle effort → retour → progrès visible fuit.** Un quiz réussi ne déplace rien à l'écran de progression ; l'unité affichée (« 5 savoirs maîtrisés sur 977 », 13 matières à 0-3 %) décourage.
2. **Les meilleures données ne sont pas réunies là où l'élève décide.** Barème par question, difficulté, fréquence par année, taux de réussite par matière, notes de simulation : tout existe, presque rien n'est croisé ni montré.
3. **L'erreur n'est pas un objet de travail.** Aucune page « mes erreurs », aucune reprise transversale ; la répétition espacée gradue un thème le jour même.
4. **L'entraînement en conditions d'examen est caché et ne rapporte rien.** Un seul bouton par épreuve, simulations introuvables après coup, ni points ni jour de série.
5. **Quatre défauts d'exécution sur mobile** cassent le parcours principal (bouton « Question suivante », débordement de la page matière, fil de la séance rompu, messages contradictoires à l'accueil).

Le soupçon de départ est fondé : les données sont bonnes, la présentation n'en tire pas parti. La section 6 liste 14 données précises et ce qu'on peut en faire.

## 2. Méthode et limites

- **Parcours vécu** sur le site local (`http://localhost`), mobile 375 x 812, compte `[TEST] Élève abonné` (id 116, BEPC) : accueil, séance du jour (exercice puis quiz), résultat, Ma progression, page matière, Réviser, Quiz, fiche d'épreuve, compte, carnet, historique.
- **Lecture du code** en trois passes parallèles (moteur pédagogique backend, espace élève frontend, contenus et examens blancs), puis contrôle par moi des constats cités ci-dessous (`fichier:ligne`).
- **Statut des constats** : « Vérifié » = vu dans le navigateur ou relu dans le code par moi ; « Relevé » = rapporté par une passe de lecture, non recontrôlé ; « Hypothèse » = à confirmer avec de vrais élèves.
- **Limites** : base locale, pas la production (en local 56 % des items de quiz sont des QCM, 14 372 sur 25 442 ; la production en compte davantage) ; un seul cursus joué (BEPC) ; le navigateur d'audit tourne avec « animations réduites » ; pas de test sur un vrai téléphone ni en réseau bridé ; aucun vrai élève interrogé. Les efforts (S ≤ 1 jour, M = 2 à 4 jours, L ≥ 1 semaine) sont des estimations.
- **Effets de bord en base locale** : 1 code de connexion créé et consommé (compte 116), session de quiz 535 terminée (séance du jour validée, points gagnés), session 536 laissée en cours (1 réponse), exercice 11294 marqué « fait ». Aucun paiement, aucun fichier du projet modifié hors ce rapport.

## 3. Ce qui est déjà bon (à ne pas casser)

- Séance du jour choisie par fréquence × coefficient, avec les raisons dites à l'élève et trois durées (10, 25, 45 min).
- Lecteur d'exercice par thème : « Essaie d'abord », correction question par question, questions du thème surlignées, barème affiché.
- Corrigés structurés (rappel de méthode, corrigé, piège, conseil) et cours à sept sections.
- Retour immédiat en quiz : mascotte, points, combo « 3 d'affilée », sons, barre colorée.
- Écran de résultat riche, rebonds (« Encore 5 questions », « Bats ton score », partage WhatsApp).
- Inédites et simulations : chrono serveur, auto-notation par grille, points perdus par cause, position parmi les candidats.
- Série tolérante (un repos pardonné par semaine), objectif réglable, bilan hebdomadaire au parent par e-mail.
- Rendu mobile du contenu : formules et tableaux défilants, figures agrandissables.

## 4. Défauts vérifiés à corriger avant le 1er décembre

**Statut au 2026-11-13 (après-midi) : B1 à B8 corrigés en local, non committés, non déployés.** Écarts par rapport au correctif proposé dans le tableau :
- **B5** : seules la copie au chrono en cours et la copie encore vierge sont rouvertes. Un entraînement libre déjà entamé ne l'est pas (le mode examen ne peut plus y être lancé) ; il ne se retrouvera qu'avec « Mes examens blancs » (R11). La dernière note s'affiche dans le bouton de la fiche.
- **B6** : le minimum pour « maîtrisé » est de 3 réponses et non 4, pour reprendre la définition de « consolidé » déjà utilisée par le bilan et la trajectoire (une seule constante, `REPONSES_MIN_THEME_CONSOLIDE`, dans `quiz/services.py`). La répétition espacée n'avance plus qu'à l'échéance.
- **B8** : le niveau et la flamme se touchent pour afficher la phrase sur la ligne du rappel (le record de série y est ajouté) ; le compteur de la page Quiz est écrit sous les matières.
- Vérifié dans le navigateur (375 px, animations réduites) : B1, B2, B3, B4, B8. Vérifié par tests seulement : B5, B6. À rejouer sur un vrai Android avec les animations actives.

| # | Constat | Preuve | Correctif | Effort |
|---|---|---|---|---|
| B1 | **Quiz sur mobile : « Question suivante » inatteignable ou hors écran.** Avec les animations système réduites, le bouton est recouvert par la barre d'onglets (le point central du bouton tombe sur la barre). Avec les animations, la barre « fixe » s'ancre au bas de la page et non de l'écran : il faut défiler jusqu'au bout après chaque correction. | Navigateur : bouton à 756-800 px, barre d'onglets à 755-812 px, `z-40` contre `z-30`. Cas animé simulé en forçant le `transform` du conteneur : bouton à 1 564 px sur 1 700, hors écran. Code : `frontend/src/pages/QuizSessionPage.tsx:368` et `:702`, `frontend/src/index.css:186-207`. | Sortir la barre du conteneur animé, la poser à `bottom-[var(--bottom-tab-bar,0px)]` comme `ThemeExerciceLecturePage.tsx:215`, ou masquer les onglets pendant un quiz (voir U3). | S |
| B2 | **Page matière de « Ma progression » plus large que l'écran** à 375 px : les cartes « À faire maintenant » mesurent 445 px, la page défile de côté et la barre d'onglets se décale. | Navigateur : `scrollWidth` 516 pour 375. Code : `frontend/src/pages/ParcoursSubjectPage.tsx:747-751` (grille sans colonne contrainte, puce de cours en `truncate`). | `grid-cols-1` (ou `min-w-0` sur la carte). | S |
| B3 | **Deux phrases contradictoires sur la carte d'accueil** : « Ce thème t'a déjà posé problème » et, juste dessous, « Tu ne l'as encore jamais travaillé ». | Navigateur (thème Puissance électrique). Code : repli de `backend/quiz/accueil.py:575-583` contre `backend/quiz/services.py:2471-2479`. | Quand la raison « échec » manque, reprendre la raison réellement calculée au lieu du repli. | S |
| B4 | **Le fil de la séance se rompt à l'étape « exercice ».** Après « Exercice validé », le bouton principal est « Exercice suivant du thème » ; rien ne mène au quiz qui valide la séance. Il faut revenir à l'accueil. | Navigateur. Code : la séance ouvre `ThemeExerciceLecturePage` (`frontend/src/lib/seance.ts:14`), mais la barre et le bouton d'étape suivante ne reconnaissent que les adresses en `/lire` (`frontend/src/components/BarreSeance.tsx:35-52`). | Faire reconnaître l'adresse de l'exercice par thème et y monter `EtapeSuivante`. | S |
| B5 | **Simulation d'annale : une nouvelle copie à chaque clic, aucune liste.** Une simulation interrompue ou terminée ne se retrouve plus. | `backend/simulations/views.py:430` crée toujours ; `listMySimulations` (`frontend/src/api/endpoints.ts:933`) n'a aucun appelant. | Reprendre la simulation en cours de la même épreuve ; afficher la dernière note sur la fiche. La liste complète vient avec F4. | S à M |
| B6 | **Un thème peut être déclaré « maîtrisé » sur une seule bonne réponse**, et la répétition espacée avance à chaque bonne réponse sans attendre l'échéance : trois réussites dans le même quiz sortent le thème de la file le jour même. | `backend/quiz/services.py:1260` (aucun minimum de réponses), `:651-661` (pas de test sur `due_at`). | Minimum de 4 réponses pour « maîtrisé » ; un seul palier franchi par jour et par thème, seulement à l'échéance. | S |
| B7 | Lien mort vers `/fiches` (la route redirige vers l'accueil). | `frontend/src/pages/SubscribePage.tsx:941`. | Retirer le lien. | S |
| B8 | Informations portées par la seule infobulle, donc invisibles au doigt : points avant le niveau suivant, jour de repos pardonné, sens du compteur « 19/1241 » sur la page Quiz. (Relevé) | `frontend/src/components/NiveauXp.tsx:21`, `LigneJour.tsx:67`, `pages/QuizStartPage.tsx:155`. | Les écrire en clair. | S |

## 5. Constats par axe

### 5.1 Expérience

- **U1 - L'action principale de l'accueil est trop basse.** Le bouton « Commencer » est à 662 px sur un écran de 812 ; sur un téléphone d'entrée de gamme (environ 640 px utiles) il est sous le pli. À la première visite, le guide en trois étapes le recouvre, puis l'encart « Comment marche ta séance ? » le repousse encore. La carte porte une quinzaine d'informations ; la page fait 3 574 px (4,4 écrans). (Vérifié)
- **U2 - Les pages de travail s'ouvrent sur une affiche.** `/quiz` : le premier écran entier est un titre de présentation, « Lancer mon quiz » est plusieurs écrans plus bas (page de 3 601 px). `/cm/epreuves` : encart d'aide puis bandeau « Toutes les annales corrigées », la liste commence vers 700 px. Un abonné n'a plus à être convaincu. (Vérifié)
- **U3 - Le quiz n'a pas de mode concentration.** En-tête du site, barre d'onglets, bouton « Télécharger la fiche PDF » en haut, lien de sortie « Exercices corrigés sur ce thème » placé avant « Question suivante ». (Vérifié)
- **U4 - L'écran de résultat demande de choisir entre plus de dix boutons** et ne dit pas ce que le quiz a changé (aucun « ce thème passe à solide »). « Mon compte » figure parmi les sorties. (Vérifié)
- **U5 - « Ce que j'ai fait » est rangé à quatre endroits** : Mon historique (menu de l'avatar), Ma progression (onglet), Mon carnet (signets et notes, pas les erreurs), « Ton bilan » dans Mon compte. Le taux de réussite par matière, la donnée la plus lisible, n'est que dans Mon compte. (Vérifié)
- **U6 - Deux lecteurs, deux comportements opposés.** Le lecteur d'épreuve montre le corrigé d'emblée et replie l'énoncé (`frontend/src/components/EnonceToggle.tsx:25`, choix assumé) ; le lecteur par thème masque le corrigé. Le lien « Lire le corrigé de cet exercice » de la fiche arrive sur la page où tous les corrigés voisins sont ouverts. (Vérifié)
- **U7 - Le quiz lancé depuis Ma progression s'ouvre dans un nouvel onglet** (`ParcoursSubjectPage.tsx:519`), déroutant sur téléphone. (Vérifié dans le code)
- **U8 - Vocabulaire flottant** : « parcours » (étapes de la séance, page matière, adresse de Ma progression), « séance » (du jour, quiz libre), « test de niveau » et « test de positionnement », « savoirs » et « thèmes » dans le même bloc. (Relevé)
- **U9 - Cibles tactiles sous 44 px** sur les boutons par thème du résultat et de la page Quiz, et erreurs de chargement sans bouton « Réessayer ». (Relevé)

### 5.2 Caractère ludique

- **L1 - L'unité de progrès décourage.** « 5 savoirs maîtrisés sur 977 », anneau à 1 %, treize matières entre 0 et 3 %. Après un quiz à 4 sur 6, rien ne bouge sur cet écran. La page Mathématiques fait 7 940 px pour 111 thèmes, dont plusieurs se recouvrent (Factorisation, Facteur commun, Identités remarquables, Différence de deux carrés). L'accueil a déjà un garde-fou (« Savoirs maîtrisés : 5. Prochain palier : 10 ») que Ma progression n'a pas. (Vérifié)
- **L2 - La liste compte des matières que l'élève ne passe pas** (Allemand et Espagnol ensemble, Dessin). Le choix des matières n'est proposé qu'aux candidats GCE (`AccueilEleve.tsx:135-136`), alors que `voir_seulement_mes_matieres` existe sur le profil. Le dénominateur de 977 en est gonflé. (Vérifié)
- **L3 - Les niveaux s'épuisent en un mois.** Cinq rangs, le dernier à 1 000 points (`backend/quiz/xp.py:51`). Ma séance de test a rapporté 42 points : à ce rythme le rang maximal est atteint en 25 jours, pour un examen à 199 jours. (Vérifié)
- **L4 - Les récompenses ne se gardent pas.** Les jalons s'affichent une fois puis disparaissent, sans page de collection ; le record de série est envoyé par l'API et jamais montré ; `prochainJalon()` est écrit et jamais appelé. Seule la flamme est visible en permanence. (Relevé)
- **L5 - L'effort le plus exigeant ne rapporte rien.** Une simulation ou une inédite terminée ne donne ni points, ni jour de série, ni maîtrise (`SourceXP`, `backend/quiz/models.py:623-627`). À l'inverse, cocher deux exercices « faits » suffit à atteindre l'objectif minimal et à prolonger la série. (Vérifié pour le barème, `xp.py:36-48`)
- **L6 - La question ouverte n'est pas un jeu** : lire, se noter. « Partiel » rapporte 2 points mais compte comme un échec dans le score, la maîtrise et le combo (`backend/quiz/models.py:381`). Je sais que le demi-point a été écarté le 2 novembre ; le signal reste double pour l'élève (« Presque ! » puis 0). Moins sensible en production où les QCM dominent. (Vérifié)
- **L7 - Le rendez-vous hebdomadaire est sous-joué.** La mini-inédite de la semaine n'a ni récompense ni comparaison ; la bande de classement anonyme n'apparaît qu'au résultat de quiz et à partir de 30 abonnés du cursus. (Relevé)

### 5.3 Moteur pédagogique

- **M1 - Pas d'oubli.** La maîtrise est une moyenne à vie ; un thème « maîtrisé » en novembre l'est encore en mai sans avoir été revu. (Vérifié, commentaire `services.py:1237-1240`)
- **M2 - Le plan préfère le neuf au fragile.** Tant qu'il reste un thème jamais travaillé, un thème à 40 % sorti de la file ne revient pas (`services.py:1732-1735`). (Relevé)
- **M3 - La séance se valide sans rien réussir** : terminer le quiz suffit, même à 0 sur 7 (`backend/quiz/views.py:673-689`). Acceptable pour la motivation, à condition de reprogrammer le thème. (Vérifié)
- **M4 - L'exercice de la séance colle mal au thème.** Séance « Puissance électrique » : l'exercice proposé a 1 question sur 6 sur le thème, 0,75 point sur 5. (Vérifié)
- **M5 - La difficulté ne sert à rien pour l'élève** alors qu'elle est renseignée sur tous les items de quiz et 95 % des questions d'annales. Le temps de réponse est collecté et jamais exploité. (Relevé)
- **M6 - Rappels** : en français seulement, premier profil du compte seulement, notifications push codées mais inactives sans clés VAPID, aucune relance d'inactivité ni de fin d'abonnement. À vérifier en production. (Relevé)
- **M7 - Hors-ligne étroit** : figures non gardées, quiz et exercices par thème non couverts, et le service est coupé quand le navigateur est en économie de données (`frontend/src/lib/pwa.ts:37-41`), précisément le public visé. Chaque lecture envoie le texte deux fois (`backend/access/views.py:85` et `:98`). (Vérifié pour ces deux lignes)

## 6. Données présentes, présentation à revoir

| # | Donnée (où) | Aujourd'hui | Ce qu'on peut en faire |
|---|---|---|---|
| D1 | Barème par exercice (85 % des 9 436 exercices) et par question (10 894) | Affiché, jamais utilisé | Auto-notation « combien de points sur 5 ? » à la fin de chaque corrigé ; base de la note estimée (F2) |
| D2 | Difficulté (tous les quiz, 95 % des questions d'annales, inédites) | Jamais envoyée à l'élève | Pastille de niveau, tri du plus simple au plus dur, « plus facile » après un échec |
| D3 | 18 240 QCM d'annales avec la bonne réponse | Texte statique, réponse juste dessous | QCM cliquables dans les lecteurs |
| D4 | Fréquence d'un thème, année de chaque épreuve | Un pourcentage global | « Tombé en 2021, 2023, 2024 ; dernière fois en 2024 » |
| D5 | Maîtrise et avancement par thème | Absents de la page « Thèmes qui tombent » | « Tombe à 93 %, tu es à 40 % » ; tri par priorité personnelle |
| D6 | Taux de réussite par matière, avant et maintenant sur 30 jours | Dans Mon compte | En tête de Ma progression |
| D7 | Bilan de la semaine | Reçu par l'accueil, rangé sous une clé que personne ne lit (`AccueilEleve.tsx:75` contre `BilanDePeriode.tsx:23`) | « Ta semaine » le lundi : jours, questions, thèmes consolidés |
| D8 | Notes de simulation (note, barème, dates) | Liste jamais appelée | « Mes examens blancs » avec courbe des notes |
| D9 | Exercices faits | Visibles dans le lecteur seulement | « 2/4 faits » sur les cartes ; filtre « commencées » ; reprise à l'exercice suivant |
| D10 | Structure du corrigé (méthode, corrigé, piège, conseil) | Affichée d'un bloc | Indices progressifs sans écrire de contenu : la méthode d'abord, puis la solution |
| D11 | Synthèse, formules et erreurs classiques de 15 061 cours | Lues dans le cours seulement | Cartes de révision et formulaire par matière ; le lecteur de cartes existe déjà, sans contenu (`FicheReader.tsx`) |
| D12 | Exercice d'origine d'un item de quiz (23 638 items) | Traçabilité interne | « Ce type de question est tombé au BEPC 2022, exercice 2 » |
| D13 | Causes de perte de points par copie (temps, notion, méthode, calcul, inattention) | Par copie | Cumul : « 40 % de tes points perdus viennent du calcul » |
| D14 | Record de série, prochain jalon, temps par question | Envoyés ou calculés, jamais montrés | Record à côté de la flamme, « encore 2 thèmes pour le prochain palier », « juste mais lent » |

## 7. Recommandations

### Vague 0 - avant le 1er décembre (corrections, sans nouvelle fonction)

| # | Action | Effort | Critère de validation |
|---|---|---|---|
| R1 | Corriger B1 à B8 | S chacune | Sur un vrai Android, animations coupées puis actives : « Question suivante » visible sans défiler ; `/parcours/10` sans défilement horizontal ; séance enchaînée exercice → quiz sans repasser par l'accueil |
| R2 | Accueil : un premier écran = compte à rebours sur une ligne, thème, une seule raison, bouton. Le guide ne recouvre jamais le bouton ; l'encart « Comment marche ta séance ? » passe sous le bouton | S | Bouton « Commencer » au-dessus de 560 px à 375 x 640, première visite comprise |
| R3 | Retirer les bandeaux de présentation et encarts d'aide ouverts pour un abonné sur `/quiz` et `/cm/epreuves` ; « Lancer mon quiz » dans le premier écran | S | Contenu utile avant 300 px |
| R4 | Ma progression : reprendre le garde-fou de l'accueil (« À découvrir » au lieu de « 0 % », palier suivant au lieu de « sur 977 ») et afficher le taux de réussite par matière déjà calculé (D6) | S | Plus aucun « 0 % » sur une matière jamais ouverte |

**Statut au 2026-11-13 (après-midi) : R2, R3 et R4 codés en local, non committés, non déployés (frontend seul).**
- **R2** : bande du compte à rebours resserrée sur une ligne tant que l'anneau n'est pas affiché ; raisons secondaires et aide « Comment marche ta séance ? » passées sous les boutons. Mesuré à 375 x 640 : bouton entre 438 et 486 px (bande de 188 px ramenée à 66 px). Restes : avec une carte « Quiz en cours » au-dessus, le bouton descend à 566 px, à la limite du pli ; la première étape du guide de bienvenue recouvre encore le bas de l'écran (la deuxième centre le bouton).
- **R3** : bandeaux de présentation retirés pour un abonné sur `/quiz` et `/cm/epreuves` (titre gardé pour les lecteurs d'écran, discret sur la page des inédites). Le pied de la carte de configuration (récapitulatif et « Lancer mon quiz ») reste collé au bas de l'écran sur téléphone tant que la carte est visible, puis reprend sa place en fin de carte ; mesuré à 375 x 640 : bouton entre 489 et 533 px, au-dessus de la barre d'onglets, dès l'ouverture de la page. Rien ne change à partir de 640 px de large.
- **R4** : sur Ma progression, « À découvrir » pour une matière jamais ouverte, « En cours » et « N savoirs travaillés sur M » pour une matière travaillée sans maîtrise, palier suivant sous 10 %, et « Ton bilan » (réussite par matière sur 30 jours) sous le résumé. Le critère « plus aucun 0 % sur une matière jamais ouverte » est vérifié dans le navigateur.

### Vague 1 - décembre et janvier : rendre le progrès visible et l'erreur utile

| # | Action | Détail | Effort |
|---|---|---|---|
| R5 | **« Mes erreurs »** : une page et un bouton « Refaire mes erreurs » | Banque des questions ratées, toutes matières, rejouable en un geste par paquets de 5 à 10, depuis l'accueil et l'onglet Ma progression. Le serveur a déjà l'historique des items (`quiz/services.py:460-484`) et « refaire les ratées » par session ; il manque l'entrée transversale. Remplace l'ambiguïté de « Mon carnet » | M |
| R6 | **Jauge par thème à quatre crans** (découvert, en cours, solide, maîtrisé) et regroupement en 10 à 15 chapitres par matière | Chaque quiz fait avancer une jauge visible ; l'écran de résultat annonce « Puissance électrique : en cours → solide ». Les 111 thèmes de maths restent le détail d'un chapitre | M (affichage) + L (regroupement éditorial) |
| R7 | **Choix des matières pour tous les cursus** | Étendre l'invitation GCE aux francophones (LV2, matières facultatives) ; retire les matières non passées des listes et des dénominateurs | S à M |
| R8 | **Auto-notation au barème** dans les deux lecteurs | À la fin d'un corrigé : « Combien de points sur 5 ? » (0, moitié, presque tout, tout), à la place du seul « Je l'ai fait ». Alimente la maîtrise du thème et D1 | M |
| R9 | **« Essaie d'abord » dans le lecteur d'épreuve** | Même bascule que le lecteur par thème, préférence mémorisée ; le lien « corrigé de cet exercice » n'ouvre que cet exercice. Décision à prendre sur le réglage par défaut (section 9) | S à M |
| R10 | **Mode concentration en quiz** et résultat resserré | Pendant le quiz : ni en-tête du site, ni onglets, ni PDF. Résultat : score, ce qui a changé, un bouton principal (« Refaire mes 2 erreurs » ou « Séance validée, à demain »), le reste replié | M |
| R11 | **« Mes examens blancs »** | Sous-onglet de Réviser : annales simulables de mon cursus, copie en cours à reprendre, notes passées et courbe (D8). Une simulation terminée compte pour la série et rapporte un forfait de points | M |
| R12 | **Niveaux qui durent et récompenses qui se gardent** | 15 à 20 rangs étalés jusqu'à l'examen, page « Mes réussites » (jalons atteints, record de série, prochain palier), jour de repos affiché en clair. Badges liés à des faits d'étude : premier examen blanc, 10 thèmes qui tombent souvent maîtrisés, série de 7 et de 30 | M |
| R13 | **Répétition espacée fiable** | En plus de B6 : paliers J+1, J+3, J+7, J+16, J+35 ; un thème maîtrisé non revu depuis 30 jours passe « à rafraîchir » ; le plan sert un thème fragile avant un thème neuf un jour sur deux | M |
| R14 | **Notifications push** | Générer les clés VAPID et vérifier l'envoi en production ; rappels par profil et en anglais pour le GCE. Sur Android, c'est le levier de retour quotidien le moins cher | S à M |

### Vague 2 - février à mai : se projeter sur l'examen

| # | Action | Détail | Effort |
|---|---|---|---|
| R15 | **Bulletin prévisionnel** | Par matière : « environ 9 à 11 sur 20 », calculé sur les points des thèmes maîtrisés pondérés par leur fréquence, avec les coefficients, et « les 3 thèmes qui te rapportent le plus de points ». Toujours une fourchette, affichée seulement après assez de réponses et recalée sur les notes de simulation | L |
| R16 | **Plan de révision daté** | La trajectoire existe (`quiz/accueil.py:310-391`) ; la rendre concrète : « Cette semaine : 5 thèmes », calendrier jusqu'au jour J, effet d'une séance de plus par semaine | M |
| R17 | **Défi de la semaine** | La mini-inédite du cursus, même sujet pour tous, résultat le dimanche avec la bande anonyme existante et un badge | M |
| R18 | **Cartes de révision et formulaire** à partir des cours (D11) | Sans nouveau contenu à écrire : règle, formule, erreur classique ; revues selon la répétition espacée | M à L |
| R19 | **QCM d'annales cliquables, indices progressifs, difficulté visible** (D2, D3, D10) | Dans les lecteurs et les quiz ; « plus facile » après un échec, « plus dur » après une réussite | M |
| R20 | **Thèmes qui tombent, version personnelle** (D4, D5) | Années de sortie, ma maîtrise, tri « à travailler d'abord », accès direct au cours | S à M |
| R21 | **Hors-ligne par paquet** | « Télécharger ce thème » (cours, exercices, figures) ; ne plus couper le service en économie de données quand l'élève le demande ; ne plus envoyer le texte en double | M |
| R22 | **Signaler une question, passer une question** | Un bouton discret ; boucle de qualité avec l'équipe et confiance de l'élève | S à M |
| R23 | **Synthèse des points perdus** (D13) et bilan parent proposé au moment du paiement | « Tes points partent surtout en calcul » ; le bilan hebdomadaire existe, il est désactivé par défaut | S à M |

## 8. Ce que je ne recommande pas

- **Classement nominatif ou ligue** : public mineur, comparaison décourageante pour la moitié basse ; la bande anonyme suffit.
- **Vies, cœurs, monnaie virtuelle, boutique, avatars** : mécaniques de rétention sans lien avec l'examen, coûteuses à tenir, et contraires à la promesse faite aux parents.
- **Gel de série payant** : le jour de repos automatique fait déjà le travail, il suffit de le montrer.
- **Réponses ouvertes corrigées par une IA** dans cette phase : coût par réponse et risque d'erreur de notation ; l'auto-notation au barème (R8) donne 80 % du bénéfice.

## 9. Décisions à prendre

1. **Lecteur d'épreuve** : garder le corrigé ouvert par défaut (choix actuel) ou passer à « Essaie d'abord » pour un abonné (R9) ?
2. **Examens blancs** : acceptez-vous qu'une simulation terminée compte pour la série et rapporte des points (R11) ? Les quiz chronométrés restent neutres par choix du 2 novembre.
3. **Note estimée** (R15) : afficher une fourchette de note engage la crédibilité du produit ; à valider avec un enseignant avant tout affichage.
4. **Regroupement en chapitres** (R6) : travail éditorial par matière ; par quelles matières commencer (proposition : Mathématiques et PCT du BEPC) ?
5. **« Partiel »** : le demi-point reste écarté ; à défaut, l'afficher à part (« 4 justes, 1 presque ») sans casser le combo ?

## 10. À vérifier avec de vrais élèves

Cinq à huit entretiens de 15 minutes sur leur téléphone suffisent pour trancher : trouvent-ils « Commencer » sans défiler ; que comprennent-ils de « 5 savoirs maîtrisés » ; où cherchent-ils leurs erreurs ; lancent-ils une simulation sans aide ; reviennent-ils le lendemain sans rappel. Les constats « Hypothèse » et l'ordre des vagues 1 et 2 en dépendent.
