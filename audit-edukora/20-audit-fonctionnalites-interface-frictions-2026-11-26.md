# 20 - Audit des fonctionnalités : interface, visuel, frictions, intuitivité

Date : jeudi 2026-11-26 (J-5 avant le lancement du 1er décembre). Site local, image `caddy` du 26 novembre (`index-VEhovt27.js`).
Question posée : fonctionnalité par fonctionnalité, l'interface est-elle claire, belle, sans friction et facile à comprendre ?
Complète les rapports 15 (convivialité) et 18 (cohérence des chiffres) sans les refaire. Aucun fichier du code n'a été modifié.

## 1. Verdict

**L'interface est propre et aimable, mais les écrans de travail sont encombrés.** Les couleurs sont tenues, le ton est juste, le mode sombre fonctionne, et le quiz comme l'accueil abonné sont au niveau. Depuis le rapport 15, plusieurs défauts ont été corrigés (section 3).

Les frictions ont changé de place. Elles ne sont plus dans les écrans vedettes, mais là où l'élève passe le plus de temps : catalogue des cours, lecteurs, exercice de la séance, recherche. Elles viennent aussi de la navigation : trop d'entrées qui se recouvrent, trop d'encarts et de barres empilés.

Les cinq points qui comptent le plus :

1. **Le catalogue des cours du BEPC s'ouvre sur 24 cours d'EPS** (gymnastique, volley-ball). Le tri par défaut met les derniers cours ajoutés en premier, et aucun bouton ne permet de changer ce tri.
2. **L'exercice de la séance propose cinq façons d'avancer.** La plus visible, « Suivante », fait sortir de la séance. Quatre couches fixes ne laissent que 70 % de l'écran au contenu.
3. **Le contenu demandé arrive sous le pli.** Résultats de recherche à 884 px, premier titre d'un cours à 997 px, titre de « Ma progression » à 934 px, sur un écran de 812 px. En cause : les encarts « Comment… ? » et des en-têtes chargés.
4. **Les listes envoient de faux signaux.** Chaque cours gratuit porte un cadenas. Les titres d'épreuves sont coupés juste là où ils se distinguent (« Français BEPC 2026 - Expres… » et « Étude … »).
5. **L'accessibilité a des trous précis.** Les messages d'erreur sont illisibles en mode sombre (2,8:1). Des paires de boutons de 32 px sont collées. La barre de progression du quiz est muette pour un lecteur d'écran. Onze écrans profonds n'offrent aucun « Réessayer » en cas d'erreur.

Aucun défaut bloquant. La plupart des correctifs demandent une journée ou moins (section 7).

| Axe | Jugement | En une phrase |
|---|---|---|
| Visuel | Bon | Palette et typographie tenues ; 54 couleurs brutes seulement, presque toutes voulues |
| Cohérence des composants | Moyen | 159 boutons faits main contre 382 du système, environ 130 cartes faites main en 4 arrondis, titres de 20 à 36 px pour des pages sœurs |
| Intuitivité de la navigation | Moyen | Trois menus se recouvrent, des noms différents pour le même écran, deux écrans sans retour |
| Frictions dans les écrans de travail | Faible | Contenu sous le pli, actions concurrentes, couches fixes |
| Accessibilité | Moyen | Bonnes bases (textes alternatifs, noms des boutons icônes) ; contrastes en sombre, cibles tactiles, quiz au lecteur d'écran |
| Ordinateur | Correct | Lisible ; premier contenu du lecteur au bas du premier écran, pas de sommaire latéral |
| Anglais, mode sombre | Bon | Un seul écart vu de chaque côté |

## 2. Méthode et limites

- **Navigateur intégré**, site local `http://localhost` (pile Docker), à 375 x 812 puis à 1 366 x 768.
  - En **visiteur neuf** (stockage vidé) : accueil, choix du BEPC, quiz d'essai de 5 questions (une réponse fausse exprès), résultat, menu, liste des épreuves, fiche et lecteur de Mathématiques BEPC 2026, liste des cours, recherche « thales », cours « Théorème de Thalès », centre d'aide, mini-inédite, onglet « Mes notes ».
  - Avec le **compte de test abonné BEPC** (`+edukora-test-eleve-abonne`, profil 37, jeton local) : accueil, Réviser, Ma progression, Mes notes, exercice de la séance, menu du compte, menu principal, ordinateur (accueil et lecteur), interface anglaise, mode sombre (accueil et lecteur).
- **Deux lectures de code en parallèle**, par agents : cohérence visuelle et accessibilité ; navigation et états d'écran.
- **Statuts** :
  - « Vérifié » : vu ou mesuré par moi dans le navigateur.
  - « Code » : lu dans le code par moi.
  - « Relevé » : rapporté par une lecture de code, non recontrôlé.
  - J'ai recontrôlé sept constats des agents : contraste des erreurs en sombre (calculé, 2,83:1), boutons de 32 px du résultat de quiz, barre de progression du quiz, onglets qui mènent à un mur pour le visiteur, écran d'erreur figé, erreur du lecteur sans relance, menu qui répète la barre du bas.
- **Limites** :
  - Pas de vrai téléphone ni de réseau bridé. Le volet du navigateur peint les animations à la capture : aucune conclusion de vitesse.
  - Accessibilité déduite du code et de contrastes calculés, sans lecteur d'écran réel.
  - Non rejoués ce jour : parent, connecté sans abonnement, accès expiré, paiement, GCE, examen blanc complet.
  - Base locale, pas la production.
- **Effets de bord** :
  - Un quiz d'essai joué en visiteur (session 644).
  - Une séance commencée sur le compte de test : l'exercice a été ouvert et la séance est passée à l'étape 2.
  - Mode sombre basculé, puis stockage vidé et déconnexion.

## 3. Depuis les rapports 15 à 18 : ce qui a bougé (vérifié aujourd'hui)

| Défaut d'avant | Aujourd'hui |
|---|---|
| D1 (15) : « Passer au quiz » recouvert par la barre de la séance | **Corrigé.** Le bouton est dégagé, la barre est bien fixée à l'écran |
| D2 et L6 (15) : bouton principal du résultat refusé au visiteur, à 1 089-1 561 px | **Corrigé.** « Essayer une autre matière gratuite » à 645 px, visible sans défiler |
| L6 (15) : première épreuve de la liste à 1 161 px | **Mieux** : 703 px. L'encart d'aide prend encore 240 px (F5) |
| L2 (15) : récompenses invisibles | **Corrigé.** Niveau, record, prochain jalon et « Tous mes jalons » en tête de Ma progression |
| P7 (18) : onglet actif hors écran | **Corrigé** |
| 5.2 (18) : épreuve sans lien vers le quiz, cours sans lien vers les épreuves | **Corrigé.** « Quiz sur ces thèmes » et « Où cette notion est tombée » sont présents |
| T3 (15) : « Tu as raté ce thème » | **En partie** : « Ce thème t'a résisté il y a 14 jours » |
| D8 (15) : « Tu maîtrises ! » sur trois lignes, le « ! » seul | **Toujours là**, et pareil pour « Excellent ! » (F12) |
| L7 (15) : cours de géométrie sans figure | **Toujours là** : « Théorème de Thalès », 0 image |

## 4. Constats par fonctionnalité

Gravité : **Majeur** = gêne la plupart des élèves sur un écran fréquent ; **Mineur** = gêne réelle mais rare ou contournable ; **Cosmétique** = finition.

### 4.1 Catalogues et recherche

| # | Constat | Preuve | Correctif proposé | Gravité, statut |
|---|---|---|---|---|
| F1 | **Les 24 premiers cours du BEPC sont d'EPS** (« Sécuriser une démonstration de gymnastique », « Organiser un échange de volley-ball »…), sur 2 866 cours. L'élève qui vient chercher ses maths croit le catalogue hors sujet. Aucun choix de tri sur la page. | Tri par défaut `["-created_at"]` : `backend/catalog/views.py:541`. Le tri « fréquent » n'est demandé qu'avec un filtre : `CoursListPage.tsx:211`. Capture `captures/20-F1-cours-bepc-commencent-par-eps.jpg` | Par défaut, trier sur « tombe le plus souvent » (le tri existe déjà), ou grouper par matière, maths et français d'abord | Majeur. Vérifié, code lu |
| F2 | **Un cadenas sur chaque cours gratuit.** Le visiteur voit un cadenas ouvert de 14 px sur chaque ligne, avec pour nom « Accès inclus dans ton abonnement », alors qu'il n'a pas d'abonnement et que l'aide dit « Les cours sont gratuits ». Sur la liste des épreuves, le même cadenas ouvert est accompagné de « Gratuit ». | `CoursListRow.tsx:80-81` ; `fr.ts:1768` | Rien quand tout est libre ; sinon le badge « Gratuit » des épreuves | Majeur (compréhension de l'offre). Vérifié |
| F3 | **Titres d'épreuves coupés à 375 px** : « Mathématiques B… », « Physique-Chimie-… », « Français BEPC 2026 - Expres… » à côté de « Français BEPC 2026 - Étude … ». L'année figure deux fois, dans le titre et en pastille, ce qui prend la place. | Liste `/cm/epreuves`, mode liste. Capture `20-F3-titres-epreuves-coupes.jpg` | Titre sur deux lignes ; retirer la pastille d'année quand le titre la contient, et l'examen quand il est déjà filtré | Majeur. Vérifié |
| F4 | **Recherche : aucun résultat visible à la première visite.** Après avoir tapé « thales », l'élève voit l'encart « Comment chercher ? » (330 px), l'accroche « Un mot, et on te dit par où commencer », puis les filtres. « La réponse en bref » commence à 884 px. | Mesure ; capture `20-F4-recherche-resultats-sous-le-pli.jpg` | Pas d'encart ni d'accroche quand une recherche est en cours ; filtres repliés en une ligne | Majeur. Vérifié |
| F5 | **Six cours pour une seule notion.** « thales » renvoie 6 cours BEPC aux titres voisins (« Théorème de Thalès », « Appliquer le théorème de Thalès… », « Justifier un parallélisme et appliquer… », « Le théorème de Thalès entre deux droites sécantes », « Pythagore et Thalès… », la réciproque). L'élève ne sait pas lequel lire. « La réponse en bref » limite le mal. | Recherche « thales » | Un cours principal par notion, les autres sous « Pour aller plus loin » (décision de contenu) | Mineur. Vérifié |

### 4.2 Lecteurs (épreuve, cours)

| # | Constat | Preuve | Correctif proposé | Gravité, statut |
|---|---|---|---|---|
| F6 | **Lecteur d'épreuve : la carte de la fiche est répétée.** Après « Lire le corrigé », l'élève revoit le même titre, les mêmes pastilles et le même bouton de téléchargement ; le premier contenu de l'exercice 1 arrive à 781 px. En haut, deux retours concurrents : « Retour au catalogue · » et « Retour à la fiche de l'épreuve » (le point séparateur reste seul en fin de ligne). | `/cm/epreuves/mathematiques-bepc-2026/lire` | En-tête d'une ligne (titre + menu ⋯) dans le lecteur ; un seul retour, vers la page d'où l'on vient | Majeur. Vérifié |
| F7 | **Lecteur de cours : premier titre à 997 px.** Au-dessus : titre, 4 pastilles, trois boutons pleine largeur l'un sous l'autre (Partager, Télécharger en PDF, Lire sans réseau), puis l'encart « Comment lire ce cours ? ». | `/cours/theoreme-de-thales/lire` | Les trois actions en une rangée d'icônes ou dans un menu ⋯ ; encart replié | Majeur. Vérifié |
| F8 | **« Autres cours de Mathématiques » hors niveau** sous un cours de BEPC : « Résoudre une équation du second degré à coefficients complexes » et « Résoudre ax + by = c en nombres entiers » (Terminale). | Bas du cours Thalès. Cause probable : sans examen connu, le filtre ne retient que la matière et le pays (`RelatedCours.tsx:27`) | Toujours filtrer sur l'examen choisi par le visiteur | Mineur. Vérifié (cause : code, probable) |
| F9 | **« Exercice 1 » puis « Exercice 1 (2 points) »** sur la fiche et dans le lecteur : deux titres et deux barèmes pour la même chose. | Fiche et lecteur de Mathématiques BEPC 2025 et 2026 | Masquer le titre interne quand il répète celui de la carte | Cosmétique. Vérifié |
| F10 | **Barèmes en notation anglaise** : « 3.5 pts », « 3.25 pts ». | `EpreuveDetailPage.tsx:203, 404` affiche le nombre brut | Format français (« 3,5 pts ») | Cosmétique. Vérifié, code lu |
| F11 | **Ordinateur, 1 366 x 768** : le premier contenu du lecteur d'épreuve est à 730 px, au bas du premier écran. La colonne fait environ 980 px de large, soit des lignes longues pour lire (probable : plus de 100 caractères), et aucun sommaire latéral alors que la place existe. | Capture faite, non jointe | Sommaire des exercices en colonne à gauche sur grand écran ; largeur de texte limitée | Mineur. Vérifié (longueur de ligne : estimée) |

### 4.3 Séance, quiz et résultat

| # | Constat | Preuve | Correctif proposé | Gravité, statut |
|---|---|---|---|---|
| F12 | **Exercice de la séance : cinq façons d'avancer.** Trois mènent à l'exercice suivant du thème : la flèche en haut (« 1 / 12 › »), la barre fixe « Suivante » (verte, pleine largeur, la plus visible) et « Exercice suivant du thème ». Deux poursuivent la séance : « Passer au quiz » au bas de l'exercice, et « Continuer » dans le bandeau de séance. L'élève qui touche le bouton le plus voyant quitte sa séance. | Capture `20-F12-exercice-seance-sorties.jpg` ; `ThemeExerciceLecturePage.tsx` | Dans une séance : la barre fixe devient « Passer au quiz » ; « Précédente / Suivante » disparaissent | Majeur. Vérifié |
| F13 | **Exercice de la séance : quatre couches fixes.** En-tête (69 px), bouton « Note » flottant et son astuce, barre « Précédente / Suivante » (69 px), barre du bas avec la pastille « BEPC · J-186 » (109 px). Il reste 565 px sur 812 pour l'exercice. À l'ouverture, « J'ai compris » de l'encart d'aide est caché sous la barre et sous le bouton « Note ». | Mesure : barre de 634 à 703 px, « J'ai compris » de 613 à 657 px, « Note » de 579 à 623 px. Capture `20-F13-exercice-seance-couches.jpg` | Mode concentration pendant la lecture : sans barre du bas (`App.tsx` a déjà une notion de `concentre` pour l'en-tête) | Majeur. Vérifié |
| F14 | **Ponctuation seule sur une ligne** : « Tu maîtrises / ! », « Excellent / ! » dans le retour d'une bonne réponse. 166 chaînes de `fr.ts` finissent par une espace ordinaire avant « ! », « ? », « : » ou « ; ». | `fr.ts:2132, 2135` ; capture `20-F14-tu-maitrises-ponctuation.png` | Espace insécable avant la ponctuation haute, en une passe sur `fr.ts` | Mineur (vu à chaque bonne réponse). Vérifié |
| F15 | **Petits boutons collés sur le résultat et le lancement du quiz** : « Exercices », « Cours », « Quiz » font 32 px de haut (`h-8 text-xs`), à 6 px les uns des autres. | `QuizResultPage.tsx:288, 296, 304`, mesuré 32 px ; aussi `QuizStartPage.tsx:238, 247`, `ThemesFrequentsPage.tsx:134-148` (relevé) | 44 px sur téléphone (`min-h-11 sm:h-8`) | Majeur (doigts, écrans fissurés). Vérifié pour le résultat |
| F16 | **Barre de progression du quiz** : les boutons de navigation sont placés dans un `role="progressbar"`, que les lecteurs d'écran lisent comme un bloc. Juste, faux et partiel ne se distinguent que par la couleur ; le nom dit seulement « Question n ». | `QuizSessionPage.tsx:482-499`, couleurs `:77-85` | Un groupe de boutons nommés avec leur état ; barre de progression à part | Majeur (accessibilité). Code lu |
| F17 | **Chrono en urgence** : texte à 2,6:1, clignotement qui ignore le réglage « moins d'animations », bouton œil de 24 px. | `ChronoQuiz.tsx:37, 49` | `text-gold-text`, `motion-safe:animate-pulse`, bouton de 44 px | Mineur. Relevé |

### 4.4 Accueil abonné, Réviser, progression, notes

| # | Constat | Preuve | Correctif proposé | Gravité, statut |
|---|---|---|---|---|
| F18 | **« Ma progression » : le titre de la page est à 934 px.** Avant lui : une phrase de filtre, l'encart d'aide, le niveau, le record, le prochain jalon. | `/parcours`, mesure | Titre et anneau d'abord ; récompenses juste en dessous | Mineur. Vérifié |
| F19 | **Petits textes et petite cible sur l'accueil abonné** : le texte « essentiel » est à 9,6 px, l'unité de jours à 10,4 px, et le sélecteur d'examen fait environ 24 px de haut. | `TeteAccueil.tsx:454, 404, 250` | `text-xs` au minimum, cible de 44 px | Mineur. Relevé |
| F20 | **Barre du bas** : « Ma progression » passe sur deux lignes. La barre mesure 75 px sur l'accueil, mais 109 px ailleurs, où s'ajoute la pastille « BEPC · J-186 ». L'onglet actif ne se distingue que par la couleur. | Mesure ; `BottomTabBar.tsx:85-110` | « Progrès » ou une ligne ; pastille seulement sur l'accueil ; trait sous l'onglet actif | Cosmétique. Vérifié (couleur seule : relevé) |
| F21 | **Mes notes : bon état vide** (trois façons d'écrire une note, bouton « Nouvelle note »). | `/carnet` | À garder | Vérifié |

## 5. Constats transverses

### 5.1 Navigation : trop d'entrées, des noms qui changent

| # | Constat | Preuve | Gravité, statut |
|---|---|---|---|
| N1 | **Trois menus se recouvrent chez l'abonné.** Barre du bas (Aujourd'hui, Réviser, Ma progression, Mes notes), menu ☰ (Aujourd'hui, Réviser, Ma progression, mode sombre : rien de plus, et pas de choix de langue, que le visiteur a) et menu du compte (Mon compte, Mes accès, Mes notes, Mon historique, Mes paiements). « Mes notes » est accessible à cinq endroits. | Vu ; `Header.tsx:400`, `BottomTabBar.tsx:71` | Mineur. Vérifié |
| N2 | **Deux navigations « Réviser » qui ne concordent pas.** La page Réviser a 9 cartes ; la rangée d'onglets en a 7, dans un autre ordre. Mes erreurs et Mes cartes manquent aux onglets, et aucun onglet ne ramène à la page Réviser. Sur ces deux écrans, on ne repart que par la barre du bas. | `ReviserPage.tsx:61-113`, `ReviserTabs.tsx:33-43` | Majeur. Code lu |
| N3 | **Visiteur : deux onglets mènent à un mur.** « Mes notes » et « Examens blancs » s'affichent sur Épreuves et Cours. Le clic ouvre une demande de connexion (polie), et la rangée d'onglets disparaît. | Vu ; `ReviserTabs.tsx:40-42` | Mineur. Vérifié |
| N4 | **Un objet, plusieurs noms.** « Mes notes », « Ce que tu as gardé » et « carnet ». « Examens blancs », « Mes examens blancs » et « Tes examens blancs ». « Fiche » désigne les Fiches EduKora, les fiches de révision et la page d'une épreuve. « Retour au catalogue » mène à trois endroits. Le fil d'Ariane dit « Accueil » à un élève dont l'accueil s'appelle « Aujourd'hui ». Enfin, le bouton du mode sombre s'appelle « Changer de thème », sur un site où « thème » est une notion d'examen. | Relevé ; « Ce que tu as gardé », « Retour à la fiche de l'épreuve » et « Changer de thème » vus | Mineur. Relevé, en partie vérifié |
| N5 | **Le retour ne revient pas d'où l'on vient.** « Retour au catalogue » mène toujours à la liste, que l'élève vienne d'un thème, de la recherche ou de la séance. | `EpreuveReaderPage.tsx:300`, `EpreuveDetailPage.tsx:224` | Mineur. Relevé |
| N6 | **Écrans enterrés** : l'historique et les paiements ne sont que dans le menu du compte. Un compte connecté sans examen déclaré garde la navigation du visiteur, sans barre du bas. | `Header.tsx:202, 232, 240, 399` | Mineur. Relevé |

### 5.2 Encarts et couches empilés

C'est le défaut le plus répandu. Chaque écran de travail a son encart « Comment… ? » à fermer :

| Encart | Écran | Hauteur |
|---|---|---|
| « Comment trouver une annale ? » | Épreuves | 240 px |
| « Comment trouver un cours ? » | Cours | 240 px |
| « Comment chercher ? » | Recherche | 330 px |
| « Comment lire ce cours ? » | Cours | environ 190 px |
| « Comment travailler cet exercice ? » | Exercice de séance | environ 180 px |
| « Comment lire ta progression ? » | Ma progression | environ 200 px |

**Rectification (même jour, en codant le lot 1)** : le moteur des aides n'en ouvre qu'**une seule automatiquement par visite** (`lib/guides/moteur.ts`, `peutDeclencherAuto`), et ne remontre jamais une aide déjà fermée. J'en ai vu plusieurs à la suite parce que je rechargeais chaque page, ce qui ouvre une nouvelle visite. Un élève neuf en voit donc une par visite, six visites de suite, et chacune au-dessus du contenu de la page où elle tombe. Le défaut est réel mais moins lourd qu'écrit plus haut ; le pire cas reste la recherche, où l'aide passe au-dessus des résultats demandés.

Sous l'en-tête, jusqu'à six bandeaux peuvent s'empiler : examen à choisir, fin de campagne, langue, reprise de paiement, hors ligne, séance (`App.tsx:161-166`, relevé). Le premier visiteur sans examen choisi voit déjà « Choisis ton examen » (vérifié).

Proposition : un seul guide à la première visite, puis une ligne « ? Comment ça marche » repliée. Jamais d'encart au-dessus du contenu qu'on vient de demander (résultats de recherche, lecteur). Un seul bandeau à la fois, par ordre de priorité.

### 5.3 États d'écran

| Écrans | Chargement | Erreur | Vide |
|---|---|---|---|
| Listes, recherche, thèmes, Mes erreurs, Mes cartes, Mes notes, Examens blancs | squelette | message avec « Réessayer » | message avec une action |
| Lecteurs et détails d'épreuve, de cours, d'inédite ; quiz et son résultat ; tentative et résultat d'inédite ; Ma progression | squelette | **texte rouge, sans « Réessayer »** | - |
| Fiches EduKora, exercices d'un thème, programme indisponible | squelette | message avec « Réessayer » | **message sec, sans action** |
| Compte, Mes accès, Historique | **zone blanche** pendant la vérification de session | partiel | - |

Sur un réseau mobile instable, ce sont justement les écrans profonds qui échouent. Sans « Réessayer », il ne reste que le retour au catalogue. Source : la lecture de code (onze écrans cités, dont `EpreuveReaderPage.tsx:181`, vérifié). En plus, l'écran d'erreur générale ne se referme pas quand on change de page : il faut recharger (`ErrorBoundary` sans réinitialisation, `App.tsx:168`, code lu).

### 5.4 Visuel et cohérence des composants

- **Ce qui est bon** : couleurs tirées de jetons presque partout (54 classes de couleur brute, dans 6 fichiers, la plupart voulues : couleurs des matières, feuilles imprimées). Tous les blocs de texte suivent le mode sombre, toutes les images ont un texte alternatif, tous les dialogues ont un titre, tous les boutons icônes ont un nom (relevé).
- **Ce qui dérive** (relevé) :
  - 159 boutons faits main contre 382 boutons du système, dont 92 forcés en arrondi complet. Le bouton principal de l'accueil est une pilule de 48 px, celui du quiz un rectangle arrondi.
  - Environ 130 cartes faites main, en 4 arrondis différents, contre 29 cartes du système.
  - Titre de page sur téléphone : 20 px sur Épreuves et Cours, 24 px sur Thèmes, Recherche et Quiz, 30 px sur Réviser, Mes erreurs et Mes cartes, 36 px sur Fiches EduKora.
  - Emoji 📖 ⚠️ 💡 dans les encadrés (« 📖 Rappel de méthode », vu), alors que tout le reste utilise des icônes au trait. Leur rendu change selon le téléphone.
  - Trois confirmations par la fenêtre native du navigateur (`window.confirm`) au lieu du dialogue du site.
- **Effet pour l'élève** : rien de choquant, mais un site qui paraît assemblé page par page dès qu'on passe d'une rubrique à l'autre.

### 5.5 Accessibilité et confort

| # | Constat | Preuve | Gravité, statut |
|---|---|---|---|
| A1 | **Messages d'erreur illisibles en mode sombre** : rouge à 2,83:1 sur le fond, 2,65:1 sur une carte (minimum 4,5:1). 84 usages, dont le quiz, son résultat et la connexion. | `index.css:84` ; calcul refait | Majeur. Vérifié par calcul |
| A2 | Boutons du système sous 44 px : taille par défaut 40 px, petite taille 36 px (134 usages). Croix de fermeture de 20 à 32 px (recherche, dialogues, menu mobile, notes). | `button.tsx`, `dialog.tsx:35`, `sheet.tsx:48`, `RecherchePage.tsx:408` | Mineur. Relevé |
| A3 | Anneau de focus clavier à 2,2:1 ; le champ de recherche des épreuves à 1,5:1 ; un lien de résultat de recherche sans anneau. | `button.tsx:8`, `EpreuvesListPage.tsx:493`, `ResultatRecherche.tsx:176` | Mineur. Relevé |
| A4 | Pas de `color-scheme` en mode sombre : cases à cocher, listes et barres de défilement restent claires. | `index.css` | Mineur. Relevé |
| A5 | Texte blanc sur vert de réussite (2,96:1 en sombre), icône blanche sur la couleur de la matière (de 2,0 à 2,8:1), « OM » blanc sur orange (2,6:1). | `BlocReussites.tsx:31`, `ParcoursSubjectPage.tsx:608`, `SubscribePage.tsx:142` | Mineur. Relevé |
| A6 | Champs de saisie en 14 px : sur iPhone, la page zoome à chaque saisie (connexion, paiement). 3 champs sur 34 sont en 16 px. | `input.tsx:11` | Mineur. Relevé, effet probable |

### 5.6 Anglais et mode sombre

- **Anglais** : sur l'interface anglaise, un élève francophone garde une phrase française en tête de séance (« Ce thème t'a résisté… »). Le serveur choisit la langue d'après l'examen, pas d'après l'interface. Cas rare, d'autant qu'un bandeau prévient (« This page is shown in English, but you are preparing your exam in French »). `quiz/textes.py:145`. Cosmétique, vérifié.
- **Mode sombre** : accueil et lecteur propres. Seuls écarts : les erreurs (A1), les contrôles natifs (A4), et les figures d'épreuve sur fond blanc, ce qui est acceptable.

## 6. Ce qui marche et ne doit pas bouger

- L'entrée du visiteur : un examen, puis un thème qui « tombe dans 26 épreuves sur 28 », puis « Commencer, sans compte ». Deux touchers.
- Le quiz : retour vert ou rouge, Kora, « Pas tout à fait, mais c'est comme ça qu'on retient. », « Comprendre mon erreur ».
- Le résultat, désormais court en tête : anneau, phrase de Kora, bouton principal visible sans défiler.
- L'accueil abonné : la séance du jour en un bloc, la reprise en un toucher, « À continuer » avec « 22 erreurs à corriger ».
- La page Réviser : trois familles claires (S'entraîner, Apprendre, Revoir) avec des compteurs utiles.
- « Essaie d'abord / Tout afficher » dans les lecteurs, et la barre des exercices collante.
- « La réponse en bref » et « Commence par ici » dans la recherche.
- L'état vide de Mes notes, le mur poli de connexion, le centre d'aide.
- La palette, la typographie des titres et un mode sombre soigné.

## 7. Plan proposé

Effort : S = une journée ou moins, M = 2 à 4 jours.

### Lot 1 : avant le 1er décembre, sans décision de produit

| # | Action | Traite | Effort |
|---|---|---|---|
| 1 | Cours : tri par défaut sur « tombe le plus souvent » | F1 | S |
| 2 | Cours : pas de cadenas sur un cours libre, badge « Gratuit » comme les épreuves | F2 | S |
| 3 | Épreuves : titres sur deux lignes, sans l'année ni l'examen redondants | F3 | S |
| 4 | Exercice dans une séance : une seule action fixe, « Passer au quiz » ; pas de barre du bas en lecture | F12, F13 | S |
| 5 | Pas d'encart d'aide au-dessus des résultats de recherche ; encarts repliés en une ligne après la première fois | F4, 5.2 | S |
| 6 | Erreurs lisibles en mode sombre, `color-scheme: dark` | A1, A4 | S |
| 7 | Boutons de 44 px sur téléphone (résultat de quiz, lancement, thèmes, croix) | F15, A2 | S |
| 8 | « Réessayer » sur les onze écrans profonds ; écran d'erreur réinitialisé au changement de page | 5.3 | S |
| 9 | Espaces insécables avant « ! ? : ; » dans `fr.ts` ; barèmes au format français | F14, F10 | S |
| 10 | Visiteur : masquer « Mes notes » et « Examens blancs » dans les onglets | N3 | S |

### Lot 2 : décembre

| # | Action | Traite | Effort |
|---|---|---|---|
| 11 | Une seule liste pour la page Réviser et ses onglets (avec Mes erreurs et Mes cartes) et un retour vers Réviser | N2 | S |
| 12 | Un mot par objet : glossaire court (notes, examens blancs, fiche, retour, accueil, mode sombre), puis passe sur `fr.ts` et `en.ts` | N4 | M |
| 13 | Lecteurs : en-tête d'une ligne, actions secondaires dans un menu ⋯, retour vers la page d'origine | F6, F7, N5 | M |
| 14 | Quiz accessible : barre de progression séparée, état de chaque question nommé ; chrono | F16, F17 | S |
| 15 | Cours voisins filtrés sur l'examen choisi | F8 | S |
| 16 | Un seul bandeau à la fois, par priorité | 5.2 | S |
| 17 | Ordinateur : sommaire latéral dans les lecteurs, largeur de texte limitée | F11 | M |
| 18 | Composants : bouton principal et carte uniques ; échelle de titres fixée (une taille par type de page) | 5.4 | M |

### Lot 3 : avec une décision ou du contenu

- Un cours principal par notion, les autres en « pour aller plus loin » (F5).
- Figures dans les cours de géométrie (L7 du rapport 15).
- Rôle du menu ☰ chez l'abonné : le retirer, ou y mettre ce que la barre du bas n'a pas (langue, aide, compte) (N1).

### Mesures de réussite

| Indicateur | Aujourd'hui | Cible |
|---|---|---|
| Premier contenu demandé, à 375 x 812, première visite (recherche, cours, lecteur d'épreuve) | 884, 997, 781 px | sous 600 px |
| Couches fixes sur l'exercice de séance | 4, 565 px utiles sur 812 | 2, plus de 680 px utiles |
| Écrans profonds sans « Réessayer » | 11 | 0 |
| Contraste des erreurs en mode sombre | 2,83:1 | 4,5:1 ou plus |
| Aides ouvertes au-dessus du contenu demandé (recherche faite) | 1 par visite, au-dessus des résultats | 0 |

## 8. Ce que je ne recommande pas

- **Une refonte visuelle.** La palette, les polices et le ton fonctionnent. Le problème est la densité et l'empilement, pas le style.
- **Ajouter des guides ou des encarts pour expliquer les écrans.** Il y en a déjà un par écran : mieux vaut que l'écran se comprenne seul.
- **Retirer la barre du bas.** Elle est le meilleur repère de l'abonné. Il suffit de la masquer pendant la lecture.
- **Toucher au quiz à choix.** C'est le cœur réussi du produit ; seuls ses boutons secondaires et son accessibilité sont en cause.

## 9. Décisions à prendre

1. **Tri par défaut des cours** : « tombe le plus souvent », ou groupés par matière ?
2. **Dans une séance**, garder la navigation entre les exercices du thème, ou n'offrir que « Passer au quiz » ?
3. **Encarts d'aide** : une seule fois par compte, ou les retirer des écrans de travail ?
4. **Quatrième onglet du bas** : « Mes notes », ou « À revoir » (erreurs, cartes, notes réunies, comme le bloc « À revoir aujourd'hui » de Ma progression) ?

## Captures (dossier `captures/`)

- `20-F1-cours-bepc-commencent-par-eps.jpg`
- `20-F3-titres-epreuves-coupes.jpg`
- `20-F13-exercice-seance-couches.jpg` et `20-F12-exercice-seance-sorties.jpg`
- `20-F4-recherche-resultats-sous-le-pli.jpg`
- `20-F14-tu-maitrises-ponctuation.png`

## 10. Suite donnée le 2026-11-26 : lot 1 codé (local, non committé, non déployé)

Les sections 1 à 9 décrivent l'état **avant** ces correctifs.

### 10.1 Fait

| # | Ce qui change | Où |
|---|---|---|
| 1 | Liste des cours triée par défaut sur « tombe le plus souvent » (les autres suivent, plus récents d'abord) : le BEPC s'ouvre sur l'algorithmique, les maths, l'histoire | `CoursListPage.tsx` (`ordering: "frequent"`) |
| 2 | Plus de cadenas sur un cours ouvert ; livre ouvert au lieu du cadenas ouvert sur les cartes de cours | `CoursListRow.tsx`, `CoursCard.tsx` |
| 3 | Liste des épreuves : titre sur deux lignes au lieu d'être coupé, année seulement si le titre ne la porte pas, cadenas seulement sur un corrigé fermé (« Gratuit » dit le reste) | `EpreuveListRow.tsx` |
| 4 | Exercice dans une séance : la barre fixe ne propose plus que « Passer au quiz » ; la barre d'onglets s'efface sur la page d'exercice (674 px utiles sur 812, contre 565) ; hors séance, « Précédente / Suivante » reste | `ThemeExerciceLecturePage.tsx`, `lib/concentration.ts` (`definirSansOnglets`), `App.tsx` |
| 5 | Recherche faite : l'aide ne s'ouvre plus d'elle-même et l'accroche disparaît sur téléphone ; premier résultat à 653 px au lieu de 884, bandeau « Choisis ton examen » compris | `RecherchePage.tsx`, `AideContextuelle.tsx` (prop `auto`) |
| 6 | Mode sombre : rouge des erreurs à 5,3:1 sur le fond et 5,0:1 sur une carte (2,8 avant), texte foncé sur fond rouge ; contrôles natifs sombres (`color-scheme`) | `index.css`, test ajouté dans `index.css.test.ts` |
| 7 | 44 px sur téléphone pour les petits boutons du résultat et du lancement du quiz et des thèmes (60 mesurés sur la page des thèmes) ; zone de toucher élargie des croix (recherche, listes, dialogues, menu) sans déplacer l'icône | `QuizResultPage`, `QuizStartPage`, `ThemesFrequentsPage`, `ThemesFrequents`, `dialog.tsx`, `sheet.tsx`, `RecherchePage`, `CoursListPage`, `EpreuvesListPage` |
| 8 | « Réessayer » qui relance vraiment le chargement sur les onze écrans profonds ; un 404 dit « introuvable » sans relance ; le texte du serveur n'est montré que s'il est écrit pour l'élève (plus de « No QuizSession matches the given query. ») ; l'écran d'erreur général s'efface au changement de page | les onze pages, `ErreurChargement.tsx` (`messagePourEleve`, `estIntrouvable`), `ErrorBoundary.tsx` |
| 9 | Espace insécable avant « ! ? : ; » en français, posée à l'affichage par `t()` : « Tu / maîtrises ! » au lieu de « Tu / maîtrises / ! » ; barèmes au format français (« 3,25 pts ») | `lib/i18n/index.ts` (`insecables`), `lib/notation.ts` (`formatBareme`) |
| 10 | Visiteur : plus d'onglets « Mes notes » ni « Examens blancs », qui ne menaient qu'à la connexion | `ReviserTabs.tsx` |

Le point 8 a été codé par un agent sur mes consignes, puis relu et complété par moi (règle des messages, cas introuvable du quiz et des copies).

### 10.2 Écarts et choix faits en codant

- **Espaces insécables** : écrites d'abord dans `fr.ts` (560 remplacements), elles faisaient échouer 55 tests qui cherchent le texte avec une espace ordinaire, et auraient piégé chaque test écrit ensuite. Elles sont donc posées par `t()` à l'affichage, en français seulement, et pas sous Vitest (`import.meta.env.MODE === "test"`). `fr.ts` reste écrit normalement. Les textes français qui viennent du serveur (phrases de la séance, par exemple) ne sont pas couverts.
- **Encarts d'aide** : seul le cas de la recherche est traité. Le moteur limite déjà les aides automatiques à une par visite (voir la rectification en 5.2) ; replier les autres reste une décision (section 9, question 3).
- **Épreuves en grille** : le cadenas ouvert de `EpreuveCard` est gardé, car il y oppose « Lire le corrigé » à « Sujet libre · corrigé payant » sur un même écran.
- **Dix clés de traduction** devenues inutiles retirées de `fr.ts` et `en.ts` ; une ajoutée (`qs.introuvable`).
- **ParcoursPage** (agent) : l'ancien texte rouge du bas de page a disparu ; si un rafraîchissement en arrière-plan échoue alors que les matières sont déjà affichées, plus rien ne le signale.

### 10.3 Vérifications

- **Tests** : suite complète du frontend, 1 841 tests passent, 17 ignorés (comme avant), 218 fichiers. Ajouts : `ErreurChargement.test.tsx`, `insecables` dans `i18n.test.ts`, contraste du texte d'erreur, onglets du visiteur, et les tests de relance de l'agent (`ErrorBoundary`, `InediteResultPage`, `ParcoursPage`, `EpreuveInediteDetailPage`).
- **Types** : `tsc -b` sans erreur. **Linter** : rien de nouveau sur les fichiers touchés.
- **Navigateur** (image `caddy` reconstruite, 375 x 812) : liste des cours (12 premiers : informatique, maths, histoire ; 0 cadenas), liste des épreuves (titres entiers, cadenas sur les payants seulement, pas d'onglets de compte pour le visiteur), recherche « thales » (pas d'aide, premier résultat à 653 px), quiz d'essai (« maîtrises ! » sur une ligne, espace insécable lue dans la page), exercice de la séance (barre « Passer au quiz », pas de barre d'onglets, qui revient en quittant la page ; hors séance « Précédente / Suivante »), page des thèmes en mode sombre (rouge clair, contrôles sombres, boutons de 44 px), épreuve et quiz introuvables (pas de « Réessayer »).
- **Non vus à l'écran** : la relance après une vraie coupure réseau (couverte par des tests), l'écran d'erreur général, l'ordinateur et l'anglais après correctifs.

### 10.4 À prévoir au déploiement

Frontend seul : reconstruire `caddy`. Aucune migration, aucun changement backend.
