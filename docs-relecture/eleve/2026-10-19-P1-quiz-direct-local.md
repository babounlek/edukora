# Test élève P1 : arrivée directe sur /quiz (local)

## 1. En-tête

- Date : 2026-10-19. Début 12:46 UTC, fin 12:51 UTC (environ 5 min de session).
- Terrain : local (http://localhost), navigateur intégré, réseau non bridé.
- URL de départ : http://localhost/quiz (arrivée directe, sans passage par l'accueil).
- Persona : Brice, élève de 3e à Douala, prépare le BEPC, maths et physique faibles, Android d'entrée de gamme, données comptées.
- Viewport : mobile 375x812 (remis en desktop à la fin).
- Compte : visiteur anonyme (aucun compte créé, aucun mot de passe saisi, aucun paiement).
- Mode d'exécution : sous-agent à contexte neuf.

## 2. Verdict de la mission

**Réussie avec effort.** La mission est menée à terme (quiz BEPC Maths de 6 questions jusqu'au résultat 2/6, puis page des prix), mais l'examen BEPC n'est pas repéré : il faut le chercher en faisant défiler une rangée de pastilles horizontale où il est caché en 6e position, alors que BAC A est présélectionné.

Ce que Brice retient : « Un site qui me donne des quiz avec correction pour mon BEPC, gratuit sans compte, et qui coûte 15 000 FCFA en Mobile Money si je veux tout. »

Temps indicatifs : sens de la page en moins de 10 s (titre « Un quiz qui cible tes lacunes, thème par thème » + carte « Essaie gratuitement, sans compte »). Mais la pastille BEPC n'a été trouvée qu'après environ 4 gestes (défilement vertical, puis horizontal trois fois, puis recherche). Un vrai élève pressé aurait pu croire que BEPC n'existe pas, ou lancer un quiz BAC A sans s'en rendre compte. Lancement du quiz BEPC : environ 45 à 60 s après l'arrivée.

## 3. Journal (extrait significatif)

1. Arrivée /quiz. Je vois : logo EduKora, loupe, menu, bouton « Connexion », un bandeau « Choisis ton examen pour recevoir ta séance du jour » avec BAC A, BAC C, BAC D, BAC E, puis onglets Épreuves / Cours / Thèmes / Quiz, un grand titre « Un quiz qui cible tes lacunes, thème par thème. ». Je comprends : un site de quiz scolaire. Pas de mention de BEPC en vue. Je veux : savoir si c'est pour moi. Je fais : je descends.
2. Carte orange « Essaie gratuitement, sans compte. Un thème complet par matière, avec la correction de chaque question. Choisis ton examen, puis lance. » Rangée EXAMEN : « BAC - A » (vert, présélectionné), BAC - C, BAC - D, « BAC » coupé au bord. Je ne vois pas BEPC. Je pense : c'est pour les grands, pas pour moi. Ça m'agace. Je fais : je fais glisser la rangée vers la droite.
3. Après un glissement : Probatoire - A, Probatoire - C, un « P » coupé. Encore pas de BEPC. Je continue.
4. Au bout de la rangée : Probatoire - E, Probatoire - TI. Fin, pas de BEPC. Je crois que BEPC n'existe pas ici. (Je n'aurais pas trouvé la suite sans l'outil de recherche de texte : la pastille BEPC est entre « BAC - TI » et « Probatoire - A ».) Je fais défiler un peu en arrière et je vois enfin « BEPC ». Je clique.
5. Liste des matières BEPC : Allemand, Anglais, Espagnol, Français, Géographie, Histoire, Informatique, Mathématiques, Physique-Chimie-Technologie, SVT. Chaque ligne : matière, thème (par ex. « Identité remarquable »), « 6 questions », bouton vert « Essayer ». Clair. Je veux maths : je clique « Essayer ».
6. Écran quiz (URL /quiz/essai). Barre de 6 segments, « Question 1 sur 6 », « 0 / 0 juste », pastilles « Mathématiques », « BEPC », « Identité remarquable ». Le bandeau « Choisis ton examen » (BAC A/C/D/E) est toujours en haut, alors que j'ai déjà choisi BEPC : il prend environ 150 px d'écran. Q1 : « Démontrer que (a+b)³ − (a−b)³ = 2b(3a²+b²) ». Cubes de binômes : trop dur pour moi, je pense que c'est au-dessus de mon niveau de 3e. Bouton « Voir la correction ».
7. Correction Q1 : encadré bleu « Rappel de méthode », lien « Voir le cours complet : Développer le carré d'une somme contenant un radical » (ne correspond pas à la question, qui parle de cubes), puis « Corrigé » pas à pas, avec une vérification numérique. Lisible. Je me note « Échec ». Message : « Une erreur comprise, c'est un point gagné pour l'examen. » Bienveillant, pas humiliant. Un bloc « Exercices corrigés sur ce thème » et une carte « Créer mon compte » apparaissent plus bas.
8. Q2 : « Simplifier, pour tout réel x ≠ −5, (x²−25)/(x²+10x+25) ». La fraction est bien rendue. Le corrigé est clair, mais la chaîne d'égalités avec fractions est rétrécie à une taille minuscule à la fin (illisible sans zoom). Je me note « Partiel » : « Presque ! Il t'a manqué peu de chose. »
9. Q3 : « Développer et réduire (5x − 2)² ». Niveau BEPC, ça va. Corrigé clair. « Réussi » : un message vert s'affiche, mais sous les boutons, hors de l'écran sans défilement.
10. Q4 : QCM « Sans poser l'opération, calculer 997 × 1003 », 4 options A à D. Je choisis B (fausse). Au défilement : la bonne réponse A est en vert avec une coche, ma réponse B en rouge avec une croix, texte « La bonne réponse était A. », section repliable « Comprendre la correction ». Retour très net.
11. Q5 : « Factoriser 9x² − 64 ». Niveau BEPC, bien. « Réussi » : « Tu maîtrises ! »
12. Q6 : « Factoriser (2x+3)² − (x−1)² ». Plus dur mais accessible. « Partiel ». Le bouton du bas devient « Voir mon résultat ».
13. Résultat (/quiz/essai/resultat) : « Essai gratuit · BEPC », « Chaque quiz te rapproche de l'examen. Relis les corrections puis refais l'essai : tu verras la différence. » Score « 2 / 6 bonnes réponses », barre par thème « Identité remarquable 2 / 6 ». Boutons « Refaire cet essai », « Défier un camarade », « Exercices corrigés sur ce thème ». Ton encourageant, pas d'humiliation.
14. Plus bas : carte « Ce n'était qu'un thème. Avec un abonnement, le quiz couvre tout ton programme... » avec « Voir les abonnements » et « Créer mon compte ». Mention « Ton score de cet essai n'est pas enregistré : il disparaît quand tu fermes l'onglet. » Lien « Essayer un autre thème gratuit ». Je comprends exactement la suite possible.
15. Clic « Voir les abonnements » : page Prix, « Un seul prix, jusqu'à ton examen. 15 000 FCFA par enfant, puis 12 000 FCFA pour chaque enfant supplémentaire », « Mobile Money (MTN, Orange) », « Aucun prélèvement automatique », « Activé après vérification (≈ 3 heures) ». Choix du cursus (BEPC, Probatoire A à TI, BAC A à TI, GCE). Je m'arrête : arrêt de branche volontaire (pas de paiement).
16. Menu hamburger : Épreuves (avec un point orange), Cours, Prix, bascule FR / EN, sélecteur de pays « Cameroun », mode sombre. Pas de lien « Quiz » ni « Accueil ». Le clic sur le logo EduKora mène à l'accueil.
17. Accueil /cm : une fenêtre « Quel examen prépares-tu ? » (BEPC, Probatoire, BAC, lien Switch to English, « Passer ») s'affiche en premier avec BEPC en tête, contrairement à /quiz. Après « Passer » : « Chaque jour, on te dit quoi réviser. », boutons « Lire un corrigé gratuitement » et « Quiz gratuit, sans compte ». Clair.

## 4. Ce qui marche bien

- Le titre de /quiz et la carte « Essaie gratuitement, sans compte » disent tout de suite l'offre et la gratuité sans compte.
- Un seul tap sur « Essayer » lance le quiz : pas de compte, pas de formulaire, pas de pop-up bloquant à l'arrivée.
- Liste des matières BEPC complète et lisible : un thème et un nombre de questions par ligne, boutons assez grands pour un pouce.
- Chargement très rapide en local (DOMContentLoaded environ 80 ms) et site léger : environ 490 Ko compressés.
- Mécanique du quiz : question, « Voir la correction », auto-évaluation « Réussi / Partiel / Échec » (honnête et sans note imposée), puis bouton fixe en bas « Question suivante » / « Voir mon résultat ». Barre de progression colorée (rouge, orange, vert) et score en cours.
- QCM : retour visuel très net (vert/coche, rouge/croix, bonne réponse énoncée).
- Corrigés pas à pas avec « Rappel de méthode » et « Vérification numérique », très pédagogiques. Les formules (puissances, fractions) sont globalement bien rendues sur mobile.
- Ton bienveillant (« Une erreur comprise, c'est un point gagné pour l'examen », « Presque ! ») : aucune humiliation à 2/6.
- Écran de résultat honnête sur ce qui est enregistré ou non, et invitation à s'inscrire non agressive. Le prix est clair et adapté au contexte (Mobile Money, sans prélèvement automatique).
- Logo cliquable vers l'accueil, qui explique le site et propose « Quiz gratuit, sans compte ».

## 5. Frictions

| Id | Sév. | Catégorie | Étape | Observé | Attendu | Preuve (capture) | Confiance |
|---|---|---|---|---|---|---|---|
| F1 | S2 | UX | Arrivée /quiz, carte d'essai | Dans la carte « Essaie gratuitement », la rangée EXAMEN démarre sur « BAC - A » présélectionné. BEPC est la 6e pastille sur 14, après BAC - TI, invisible sans balayage horizontal, et rien n'indique que la rangée défile (seule la dernière pastille est coupée). Un élève de 3e voit d'abord BAC et Probatoire et peut conclure que le site n'est pas pour lui. | Examen de l'élève présélectionné ou BEPC en premier ; ou pastilles sur plusieurs lignes ; ou invite « glisse → ». | Capture à 375x812 : carte orange, « EXAMEN », pastilles BAC - A (vert), BAC - C, BAC - D, « BAC » coupé au bord droit. Liste en dessous : Allemand « Antonymes », Anglais « Texte à trous », etc. (contenu BAC A). | Élevée |
| F2 | S2 | UX | Arrivée /quiz, bandeau du haut | Le bandeau « Choisis ton examen pour recevoir ta séance du jour » ne montre que BAC A, BAC C, BAC D, BAC E ; BEPC (et Probatoire) sont cachés à droite dans une rangée qui défile, sans indice visible. Ce bandeau reste aussi affiché pendant tout le quiz, après le choix de BEPC (environ 150 px d'écran perdus sur 812) et sur les pages Quiz/Prix. | Bandeau montrant BEPC en premier ou disparaissant une fois l'examen choisi/le quiz lancé. Sur l'accueil, la fenêtre « Quel examen prépares-tu ? » liste bien BEPC en premier : incohérent avec /quiz. | Captures de l'écran d'arrivée et de chaque question : bandeau vert clair avec 4 pastilles BAC en haut, au-dessus de « Quitter le quiz » / « Partager ce quiz ». | Élevée |
| F3 | S3 | contenu | Q1 du quiz BEPC Maths | « Démontrer que (a+b)³ − (a−b)³ = 2b(3a²+b²) » : développement de cubes de binômes, avec démonstration générale sur des réels. Cela semble au-dessus du niveau BEPC (3e) pour l'élève faible décrit. À noter : c'est la toute première question de l'essai gratuit, donc la première impression du niveau. | Première question représentative du BEPC (ex. développer (5x−2)²). Les Q3 à Q5 sont bien au niveau. | Capture Q1 : « Démontrer que, pour tous réels a et b, on a l'égalité (a+b)³ − (a−b)³ = 2b(3a²+b²) » avec pastilles Mathématiques / BEPC / Identité remarquable. | Moyenne (jugement du testeur, pas de relecture du programme officiel) |
| F4 | S3 | contenu | Q1, correction, « Voir le cours complet » | Le lien de cours proposé est « Développer le carré d'une somme contenant un radical », qui ne correspond pas à la question (cubes). Les Q2, Q5 et Q6 renvoient bien vers un cours cohérent. | Cours lié en rapport avec la question (cubes de somme). | Capture : encadré bleu « Rappel de méthode », lien vert « Voir le cours complet » puis « · Développer le carré d'une somme contenant un radical ». | Moyenne |
| F5 | S3 | accessibilité | Q2, corrigé | Dans le corrigé, les égalités de fractions longues ((x²−25)/(x²+10x+25) = (x−5)(x+5)/(x+5)(x+5) = (x−5)/(x+5)) sont réduites à une très petite taille pour tenir en largeur : illisibles sans zoom sur un petit écran. | Formule retournée à la ligne ou défilement horizontal à taille normale. | Capture après « Partiel » en Q2 : ligne de fractions en caractères nettement plus petits que le texte. | Moyenne |
| F6 | S4 | accessibilité | Q5, Q6, corrigés | Certaines expressions sont coupées en milieu de formule : « (3x − / 8)(3x + 8) », « (A − / B)(A + B) », « (2 + 4)(3 × 2 + / 2) ». Lisible mais moins confortable. | Retour à la ligne aux opérateurs principaux ou formule non coupée. | Captures des corrigés de Q5 et Q6 : le facteur (3x−8) coupé sur deux lignes. | Élevée |
| F7 | S4 | UX | Q3, Q5, Q6 (après auto-évaluation) | Après avoir cliqué sur Réussi/Partiel/Échec, le message de retour (« Tu maîtrises ! », « Presque ! ») apparaît sous les boutons, parfois hors de l'écran, et les boutons se grisent sans autre signe. Le bouton fixe « Question suivante » est la seule indication qu'on peut continuer. | Retour visible sans défilement. | Capture juste après le clic sur Réussi (Q3) : boutons grisés, pas de message visible ; il faut défiler pour le voir. | Moyenne |
| F8 | S4 | UX | Arrivée en début de corrigé | Les pages de correction sont longues (rappel + corrigé + vérification) : il faut défiler 8 à 10 crans pour atteindre les boutons d'auto-évaluation. Normal pour un corrigé, mais sur mobile cela alourdit. Un bouton « aller à l'auto-évaluation » ne serait pas superflu. | Raccourci vers la fin du corrigé. | Captures de Q1 : corrigé sur plusieurs écrans avant « Sois honnête avec toi-même ». | Faible |
| F9 | S4 | confiance/vente | Quiz et résultat | Deux cartes « Créer mon compte » empilées sur l'écran de résultat (celle du quiz et la carte de pied de page « commence gratuitement »), et la carte d'inscription est déjà visible dès la Q1. Pas agressif, mais répétitif. | Une seule invitation par écran. | Capture du résultat : « Voir les abonnements » / « Créer mon compte » puis, plus bas, de nouveau « Corrigés détaillés... commence gratuitement. [Créer mon compte] ». | Faible |
| F10 | S3 | UX | Menu hamburger | Le menu contient Épreuves, Cours, Prix, mais pas « Quiz » ni « Accueil » : pour retrouver le quiz ou l'accueil, il faut cliquer sur le logo (qui ne ressemble pas forcément à un bouton) ou le chemin d'onglets de la page. Le menu a un point orange sur « Épreuves » non expliqué. | « Quiz » et « Accueil » dans le menu. | Capture du menu : Épreuves (point orange), Cours, Prix (surligné), FR/EN, Cameroun, icône lune. | Moyenne |
| F11 | S4 | UX | Menu, logo | Le premier clic sur le logo juste après avoir fermé le menu n'a rien fait (le deuxième a fonctionné). Probablement l'animation de fermeture du menu ; impression unique. | Réaction au premier clic. | Capture après le clic : toujours sur la page Prix. | Faible |
| F12 | S4 | UX | Accueil /cm | La fenêtre « Quel examen prépares-tu ? » s'affiche d'emblée sur l'accueil (modale pleine, avec « Passer »), alors qu'elle n'apparaît pas sur /quiz : l'élève arrivé en direct ne l'a jamais vue et n'a pas de moyen simple d'indiquer BEPC. | Même mémorisation d'examen sur toutes les entrées. | Capture : fenêtre blanche, BEPC / Probatoire / BAC, lien « Switch to English », « Passer ». | Moyenne |
| F13 | S4 | langue | Arrivée | Un message « Tu prépares le GCE (sous-système anglophone) ? Switch to English » apparaît sous le bandeau, en français suivi d'un lien en anglais. Pertinent pour un anglophone, mais sans importance pour Brice et ajoute du texte sur l'écran d'arrivée. | Message plus discret ou conditionné. | Capture d'arrivée : texte gris + lien vert « Switch to English ». | Faible |

## 6. Mesures

Mesurées sur /quiz au rechargement (cache navigateur chaud, réseau local non bridé : les chiffres de temps ne sont pas représentatifs d'un téléphone en 3G).

- Chargement : DOMContentLoaded environ 80 ms, événement load environ 84 ms.
- Requêtes : 50 ressources (35 JS, 1 CSS, 9 polices woff2, 5 appels API).
- Poids compressé (corps encodé) : environ 490 Ko au total : JS 261 Ko, CSS 38 Ko, polices 169 Ko, API 22 Ko. Décompressé : environ 1,3 Mo.
- Estimation 3G : 490 Ko, soit environ 5 à 10 s au premier passage (1 Mo ≈ 10 à 20 s), puis beaucoup moins en cache. Acceptable, mais les 9 fichiers de polices (169 Ko) pèsent presque autant que tout le code.
- Pas de données mesurées pour le quiz lui-même (une requête /quiz/essais/ au chargement ; les questions sont chargées sans erreur).
- Erreurs console : 401 sur /auth/me/ et /auth/token/refresh/ (normal pour un visiteur) ; erreurs « An unknown error occurred when fetching the script » (enregistrement du service worker, à ignorer dans ce navigateur) ; avertissements GSI_LOGGER « google.accounts.id.initialize() is called multiple times » (3 à 4 occurrences) : un défaut mineur de la page (initialisation Google Sign-In répétée), à vérifier. Un avertissement « Deprecated API for given entry type ».
- Parcours : arrivée, carte d'essai, BEPC, Maths, 6 questions, résultat : environ 25 clics et défilements ; le quiz lui-même est fluide, sans temps d'attente visible (screenshots parfois en retard d'un rendu, sans conséquence).

## 7. Idées d'amélioration

| Idée | Effet attendu | Effort |
|---|---|---|
| Présélectionner l'examen d'après le pays/langue ou montrer BEPC en premier dans la rangée de pastilles (carte d'essai et bandeau), ou afficher les pastilles sur plusieurs lignes au lieu d'une rangée défilante | Le BEPC est trouvé en moins de 5 s, plus aucun risque de croire que le site n'est pas pour soi (F1, F2) | Faible |
| Masquer le bandeau « Choisis ton examen » dès qu'un examen est choisi ou qu'un quiz est lancé, ou le replier | Plus d'espace d'écran pendant le quiz (F2) | Faible |
| Mémoriser l'examen choisi dans la carte d'essai et le reprendre dans le reste du site (accueil, prix, épreuves) | Moins de redemandes, parcours cohérent (F12) | Moyen |
| Ouvrir l'essai par une question plus accessible (difficulté croissante) et revoir le lien de cours de la Q1 | Première impression de niveau juste, moins de risque de découragement (F3, F4) | Faible à moyen |
| Réduire la largeur des formules en les faisant défiler horizontalement ou en les retournant à la ligne | Corrigés lisibles sur petit écran (F5, F6) | Moyen |
| Faire défiler automatiquement vers le message de retour après l'auto-évaluation, ou l'afficher au-dessus des boutons | Retour immédiat sans geste (F7) | Faible |
| Ajouter « Quiz » et « Accueil » dans le menu hamburger | Retrouver le site plus facilement après un lien WhatsApp (F10) | Faible |
| Ne garder qu'une carte d'inscription par écran de résultat | Moins de répétition, ton plus calme (F9) | Faible |
| Réduire à 2 ou 3 graisses de police (ou précharger seulement celles du premier écran) | Environ 100 Ko de moins au premier chargement, utile en 3G (mesures) | Faible |

## 8. Ce que cette session ne dit pas

- Pas de mesure de la motivation réelle ni de la patience d'un vrai élève : le testeur est simulé, avec une patience prescrite par le scénario.
- Réseau non bridé et cache chaud : les temps réels sur un Android d'entrée de gamme en 3G ne sont pas mesurés, seulement estimés d'après le poids.
- Viewport émulé à 375x812 dans un navigateur de bureau : pas de test sur un vrai téléphone (rendu des polices, clavier, défilement tactile).
- Pas de relecture scientifique des énoncés ni des corrigés (niveau BEPC et exactitude jugés à vue seulement).
- Un seul quiz (Maths BEPC, thème « Identité remarquable ») ; les autres matières et thèmes, y compris Physique-Chimie, n'ont pas été essayés.
- Visiteur anonyme uniquement : aucun test du compte, du paiement, ni de ce que devient le score après inscription.
- Le chronométrage de la mission (moins de 60 s) est approximatif : les captures d'écran de l'outil arrivaient parfois avant le rendu.

## 9. Dédoublonnage et calibrage (opérateur, après la phase A)

État du navigateur remis à zéro avant la session (localStorage, service worker, caches) : l'examen BAC C déclaré lors de mes vérifications précédentes aurait faussé la première visite. Le skill n'était pas chargeable dans cette session (« Unknown skill ») : protocole suivi à la main, sous-agent à contexte neuf, jamais d'accès au code.

**Calibrage : réussi.** Le testeur a retrouvé seul le résidu d'un défaut déjà connu : F1 est le pendant de l'ancien F4 du rapport P2 (essais gratuits qui s'ouvrent sur « BAC - A »). Le correctif du 2026-10-19 (`QuizStartPage` lit l'examen déclaré en localStorage) ne joue que lorsqu'un examen a été déclaré ; sur une arrivée directe sans déclaration, le premier cursus de la langue reste présélectionné, donc BAC A.

| Id | Statut | Remarque |
|----|--------|----------|
| F1 | **résiduel de F4 (P2)** | Sans examen déclaré, BAC A présélectionné et BEPC 6e pastille sur 14. Non couvert par le correctif. |
| F2, F12 | **nouvelles, même famille** | `BandeauCursus` n'affiche que BAC A, C, D, E, reste affiché pendant le quiz ; la fenêtre « Quel examen prépares-tu ? » n'apparaît que sur `/cm` (`CATALOGUE_HOME_RE`), jamais sur un lien direct. À traiter ensemble avec F1. |
| F3, F4 | nouvelles (contenu) | Q1 de l'essai BEPC « Identité remarquable » (cubes de binômes) et son cours lié ; jugement du testeur, à confirmer par une relecture de contenu (rôle du skill enseignant, non écrit). |
| F5, F6 | nouvelles | Formules longues réduites ou coupées sur mobile ; à confirmer en phase B (cousin de la mise en page KaTeX, voir le skill audit-qualite-rendu). |
| F7, F8, F9, F10, F11, F13 | nouvelles, S3-S4 | F11 (impression unique) et F13 (message GCE sur l'arrivée) sont à faible confiance. |

Rien n'a été vérifié en phase B ni corrigé pour ce second rapport.

## 10. Persistance de l'examen choisi sur tous les filtres (2026-10-19, non committé)

**Diagnostic** (code puis navigateur) : l'examen déclaré par un visiteur vit dans `localStorage` (`edukamer_cursus_prepare_en_attente`), celui d'un élève connecté sur son compte. Un seul hook (`useCursusDeclare`) les unifiait, mais seuls l'accueil, la recherche, les inédites et les essais du quiz le lisaient. `useFiltreCursusParDefaut` (`lib/filtreCursus.tsx`) faisait `isAuthenticated ? user.cursus_prepare : null` : pour un visiteur, le pré-filtrage valait toujours null. Mesuré avant correction, visiteur ayant déclaré BAC C : `/cm/epreuves` 1 326 épreuves sans `?cursus=`, `/cm/cours` et `/cm/themes-frequents` non filtrés, `/tarifs` sans présélection.

**Correction** (une source de vérité) :
- `lib/cursusAccueil.ts` : `useCursusPrepareDeclare(country)` rend l'examen en entier, celui du compte ou celui du visiteur retrouvé dans la liste des examens du pays (la liste n'est demandée que si un visiteur a déclaré quelque chose).
- `lib/filtreCursus.tsx` : le pré-filtrage des listes (épreuves, cours, thèmes fréquents) utilise ce hook. Règles conservées : un défaut et jamais une frontière (« Voir tout le catalogue », `tout=1`), un `?cursus=` explicite l'emporte, un examen d'une autre langue que l'interface ne filtre pas, un examen d'un autre pays ne filtre rien.
- `pages/PricingPage.tsx` : l'examen du visiteur est présélectionné comme celui d'un compte (le compte à rebours s'affiche).
- Ordre des examens : `trierCursus` (`lib/cursus.ts`) donne BEPC, Probatoire, BAC, puis le GCE, dans le bandeau « Choisis ton examen » ; côté serveur, `quiz/essai.py` trie la liste des essais gratuits dans le même ordre (alphabétique, elle ouvrait la carte d'essai sur « BAC - A » : F1 du rapport P1).
- `components/BandeauCursus.tsx` : masqué pendant un essai de quiz (`/quiz/essai`), F2 du rapport P1.

**Vérifié dans le navigateur** (visiteur BAC C) : `/cm/epreuves` passe à 309 épreuves avec `?cursus=20` et « Voir tout le catalogue », `/cm/cours` et `/cm/themes-frequents` reçoivent `cursus=20`, `/tarifs` présélectionne BAC C (« 249 jours avant ton BAC »). Visiteur sans examen sur `/quiz` : le bandeau commence par BEPC, la carte d'essai présélectionne BEPC, et le bandeau disparaît dès le début d'un essai.

**Tests** : filtreCursus (6 cas visiteur et 4 existants adaptés), `trierCursus` (2), `test_essai` (ordre scolaire). Frontend : 83 fichiers, 760 tests verts ; backend `quiz` : 508 verts.

**Décisions prises sans vous redemander**, selon ma recommandation : invite non bloquante pour un lien direct (le bandeau, déjà existant, avec BEPC en tête) plutôt que d'ouvrir la fenêtre d'examen ; pas de puce supplémentaire dans les listes (le bandeau « Tu vois les épreuves de … » existant suffit).

**Restent** : la fenêtre d'examen qui n'apparaît que sur `/cm` (F12 du rapport P1, volontaire) ; les pages Parcours et Historique lisent encore seulement le compte (réservées aux connectés) ; synchronisation entre onglets (le magasin local n'écoute pas l'évènement `storage`).

## 11. Suite : F4, F7, F10, F5, F6 (2026-10-19, non committé)

| Id | Résultat |
|----|----------|
| **F4** | **Cause trouvée, pas de correction de code.** Le lien « Voir le cours complet » est calculé à la lecture (`quiz/views._cours_pour_theme`) : parmi les 25 cours BEPC de maths portant le tag « identité remarquable », le moins mauvais par mots communs (« développer », « somme ») est retenu. Il n'existe aucun cours sur les cubes en BEPC (le seul titre avec « cube » parle de volumes). Surtout, l'item 2558 (cubes de binômes, difficulté ELEVEE) vient de **Mathématiques BAC D 2006** et est rattaché à 9 cursus, BEPC compris : le niveau, pas le lien, est le défaut (c'est F3). Un seuil de mots communs ne le règle pas (le cours retenu partage deux mots avec la question). 105 items vitrine du BEPC dont 14 « ELEVEE » : même question pour 13 autres items. **Décision à prendre** : détacher l'item 2558 du BEPC (le quiz gratuit passe à 5 questions, il reste complet), ou créer un cours sur le cube d'un binôme. À ranger avec la relecture de contenu du BEPC. |
| **F7** | Non reproduit tel quel (le message était visible à 390 px, barre fixe à 743 px). Garde-fou ajouté : `QuizSessionPage` amène le message de retour à l'écran (`scrollIntoView` « nearest », marge basse pour la barre) quand une réponse vient d'être enregistrée, jamais à l'ouverture d'une question déjà répondue. 2 tests (`QuizSessionPage.retour.test.tsx`). |
| **F10** | Le menu mobile des visiteurs contient maintenant Accueil, Épreuves, Cours, Quiz, Prix (`Header.tsx`, clés `nav.accueil` et `nav.quiz`). « Accueil » n'apparaît que dans le menu mobile (le logo y mène déjà sur grand écran) ; « Quiz » apparaît aussi dans la barre. **Écart assumé avec le commentaire du fichier**, qui retirait « Quiz » du menu des élèves qui suivent un plan : cela ne vaut pas pour un visiteur, pour qui l'essai sans compte est la porte d'entrée. Vérifié en navigateur ; pas de test de composant (aucun test existant pour `Header`, trop de dépendances). |
| **F5** | **Cause : pas une formule `$…$`, mais `$$…$$` sur une seule ligne.** `remark-math` lit un `$$…$$` d'une ligne comme une formule EN LIGNE : fractions à 70 %, bornes des sommes et intégrales en exposant. La chaîne de l'item 2556 n'était donc pas dans un `.katex-display`. Correction : `normalizeMathBlocks` (`lib/markdown.ts`) passe en bloc display un `$$…$$` d'une ligne seul sur sa ligne, quand il contient `\frac`, `\sum`, `\int`, `\lim`, `\prod` ou `\binom` (pas dans une phrase, pas dans une citation). Mesure sur la base : 1 936 items de quiz, 1 971 exercices et 545 cours concernés, environ 25 900 formules ; **0 erreur KaTeX en mode display sur ces 25 877 formules** (moteur réel, en ligne et en display). Complément : `agrandirFractionsEnLigne` passe en `\dfrac` les vraies formules `$…$` qui enchaînent au moins deux fractions ou contiennent une égalité (347 items de quiz, 671 exercices et 357 cours ont un `\frac` en ligne). Tests : 5 + 6 cas dans `markdown.test.ts`. |
| **F6** | **Confirmé, non corrigé (S4).** KaTeX découpe une formule en ligne en blocs `.base` à chaque opérateur binaire ou relation, parenthèses comprises : dans un conteneur étroit `(a−b)(a+b)` peut passer à la ligne entre « (a− » et « b) ». Réglages possibles : formules insécables (risque de débordement horizontal de la page), ou `\left( … \right)` autour des parenthèses (réécriture fragile de milliers de contenus). Pas retenu : gain faible pour un risque réel. |

**Limite de F5 constatée à la vérification** : la chaîne de l'item 2556 (`a/b = c/d = e/f`) passe maintenant à taille normale mais mesure 345 px pour 269 px disponibles sur un téléphone de 375 px : sa dernière partie défile horizontalement, comme tout formule display trop large sur le site, sans indication. Essayé et retiré : réduire les formules display à 1,1 em sur mobile (314 px, ne suffit pas, et change toutes les formules). Pistes si le défilement gêne : un indice de défilement (comme pour les tableaux, F3) ou découper automatiquement les chaînes à plusieurs égalités avec `aligned`.

Tests : frontend 84 fichiers, 773 verts, `tsc` propre.

## 12. F4 / F3 : item 2558 détaché du BEPC (2026-10-19, base locale uniquement, non committé)

**Décision de l'utilisateur** : détacher l'item 2558 du cursus BEPC en local.

**Fait** (shell Django, puis `definir_quiz_vitrine --appliquer`) :
- Item `2558` (`external_id` `cqc-identite-remarquable-elevee-0`, « Démontrer que, pour tous réels a et b, (a+b)³ − (a−b)³ = 2b(3a²+b²) », difficulté ELEVEE, source Mathématiques BAC D 2006) : cursus avant `[14, 15, 16, 19, 20, 21, 22, 23, 24]`, après `[15, 16, 19, 20, 21, 22, 23, 24]` (le BEPC, id 14, est retiré ; les 8 autres cursus gardent l'item).
- Réalignement de la vitrine par la commande du projet : l'item n'appartient plus à un quiz gratuit retenu, il est décoché (`est_vitrine` True → False) ; items gratuits 503 → 502, aucun autre changement.

**Vérifié** :
- Le thème « identité remarquable » en BEPC Maths compte 5 items VALIDE (2553 à 2557), tous gratuits : le quiz reste **complet** (`themes_gratuits_par_matiere` : 6 → 5 questions).
- API publique `/quiz/essais/` : « BEPC · Mathématiques · identité remarquable · 5 questions » ; `/quiz/essais/demarrer/` renvoie 5 questions (carré de (5x−2), simplification de (x²−25)/(x²+10x+25), 997 × 1003, factorisation de 9x²−64, factorisation de (2x+3)²−(x−1)²), aucune question de cubes.

**Hors de cette passe** : l'index de recherche n'a pas été reconstruit (l'item reste cherchable avec l'ancien rattachement jusqu'au prochain `indexer_recherche`) ; les 13 autres items « ELEVEE » du quiz gratuit BEPC ne sont pas traités.

**À rejouer en prod** (modification de données, pas de code) : dans le shell Django, retirer le BEPC de l'item d'`external_id` `cqc-identite-remarquable-elevee-0` (`item.cursus.remove(Cursus.objects.get(country__code="CM", examen="BEPC"))`), puis `definir_quiz_vitrine --appliquer`. **Attention** : une réingestion du JSON source de ce lot de quiz remettrait le BEPC. **Pour annuler en local** : `item.cursus.add(bepc)` puis `definir_quiz_vitrine --appliquer`.
