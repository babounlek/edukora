# 13 - Audit de l'accueil d'un abonné (/cm, page « Aujourd'hui ») - 2026-11-16

Objectif : même barre que pour la vitrine (rapport 12), le niveau des meilleures edtech mondiales.
Rien n'a été modifié : audit en lecture seule.

## Méthode et limites
- **Vu à l'écran** : compte `[TEST] Élève abonné` (BEPC, 3 séances terminées, un quiz en cours, une lecture en cours, 18 erreurs), en local (image caddy, http://localhost/cm), bureau 1280x800 et mobile 375x812, page entière ; interface anglaise (/en/cm) en mobile.
- **Mesuré** : appels réseau et fichiers chargés (API Performance du navigateur), position du bouton principal échantillonnée toutes les 40 ms pendant le chargement, hauteur des blocs, taille des cibles tactiles, titres et sections ; côté serveur, temps, nombre de requêtes SQL et profil d'exécution de chaque appel (client de test Django dans le conteneur).
- **Lu** : `AccueilEleve.tsx`, `TeteAccueil.tsx`, `SeanceDuJour.tsx` (parties), `lib/cursusAccueil.ts`, `lib/accueilCache.ts`, `lib/guides/`, `context/AuthContext.tsx`, `backend/quiz/accueil.py` (parties).
- **Non vu à l'écran** : « Séance faite », premier jour d'un abonné (`premiers_pas`), veille, jour J et après l'examen, abonné GCE, parent à deux profils, thème sombre. Lus dans le code seulement.
- **Non mesuré** : LCP et INP (le navigateur d'audit ne les remonte pas), téléphone d'entrée de gamme, 3G réelle. Les temps serveur sont ceux du poste local en mode débogage : le nombre de requêtes SQL et la répartition sont fiables, les millisecondes sont un ordre de grandeur.
- **Effet de bord** : aucun en base, hormis l'écriture que fait la page elle-même à chaque ouverture (date de dernière visite).
- **Comparaison** : d'après les pratiques connues de Duolingo, Khan Academy, Brilliant, Quizlet et Seneca. Leurs pages n'ont pas été reparcourues aujourd'hui.

## Verdict
C'est la meilleure page du produit, et elle est déjà proche du bon niveau sur le fond : une seule action, une raison chiffrée de la faire, une durée au choix, un objectif du jour, la semaine en cours. Note d'ensemble (jugement de l'auditeur) : **3,7 / 5**, contre 2,8 pour la vitrine avant travaux.

Ce qui la sépare du meilleur niveau, par ordre d'importance :
1. **Elle est lente à dire la vérité du jour.** L'appel qui porte la page fait 172 requêtes SQL et environ une seconde de calcul, dont 86 % pour un bloc situé trois écrans plus bas.
2. **Le bouton principal bouge pendant le chargement** quand un quiz est en cours : 128 px vers le bas, 30 ms après son apparition.
3. **Trop de choses demandent l'attention.** Dix blocs, six « reprises » concurrentes, et douze commandes dans la carte de la séance.
4. **La progression affiche trois zéros** à un élève qui a fait trois séances et a 30 thèmes en révision.
5. **Deux défauts de fonctionnement** : le tutoriel de bienvenue rejoué à un abonné expérimenté, et l'accueil dégradé quand la langue de l'interface n'est pas celle de l'examen.

## Grille de notation
| Critère | Note | Constat principal |
|---------|------|-------------------|
| Une action claire | 4,5 / 5 | « Commencer : faire un exercice » domine, visible sans défiler sur bureau et sur mobile. |
| Raison de faire cette séance | 4,5 / 5 | Phrase du coach faite de faits (« raté il y a 23 jours »), fréquence à l'examen vérifiable, coefficient. Rare, même chez les meilleurs. |
| Habitude et motivation | 4 / 5 | Objectif de points, niveau, semaine en cours, palier franchi, défi de la semaine. |
| Densité et hiérarchie | 3 / 5 | Voir B. Carte de séance de 1 057 px sur mobile, page de 4,6 écrans. |
| Progression | 3 / 5 | Voir B5. Trajectoire et plan jusqu'au jour J bien pensés, mais l'affichage décourage au début. |
| Vitesse | 2,5 / 5 | Voir A. Vingt appels d'API, une seconde de calcul, 535 Ko de JavaScript. |
| Stabilité de l'affichage | 3 / 5 | Voir A3. Un saut du bouton principal, puis la page s'allonge quatre fois. |
| Accessibilité | 3 / 5 | Voir D. Tous les boutons sont nommés ; pas de titre de niveau 1, cibles tactiles petites. |
| Justesse (langue, états) | 3 / 5 | Voir C. |
| Mesure | 4 / 5 | Le délai jusqu'à « Commencer » et l'entrée utilisée sont déjà envoyés. |

## A. Vitesse et stabilité (faits mesurés)
| ID | Constat | Preuve |
|----|---------|--------|
| A1 | `GET /quiz/accueil/` : **172 requêtes SQL, 750 à 1 050 ms** en local. `resume_parcours` en prend 86 % (1,02 s sur 1,18 s sous profilage) : il construit le parcours complet des 11 matières pour remplir « Où j'en suis », affiché en bas de page. Le plan du jour, qui porte le bouton, ne coûte que 57 ms. | Profil d'exécution ; `quiz/views.py:1153`, `quiz/services.py:1319` |
| A2 | **20 appels d'API** à l'ouverture, alors que la page est conçue autour d'un seul. Détail : `/auth/me/` répond 401 à chaque démarrage, puis `/auth/token/refresh/`, puis `/auth/me/` à nouveau (trois allers-retours en série avant tout affichage) ; `/quiz/plan-du-jour/` est demandé par l'en-tête 150 ms avant que `/quiz/accueil/` ne le recalcule ; la liste des inédites est demandée deux fois (sans examen, puis pour l'examen) ; `/catalog/stats/` part avant que le pied de page sache qu'il s'agit d'un abonné. | Liste des appels ; `AuthContext.tsx:32`, `Footer.tsx:164`, `TeteAccueil.tsx:55` |
| A3 | Avec un quiz en cours, la carte de séance s'affiche à 72 px du haut puis descend à 200 px **30 ms plus tard** : la bande « Quiz en cours » a sa propre requête et s'insère au-dessus. Le bouton passe de 500 à 628 px. Ensuite la page grandit de 2 524 à 2 944 px en quatre étapes (cartes, défi, inédites, tentatives). | Échantillonnage ; `AccueilEleve.tsx:130` |
| A4 | La ligne « Prochaine épreuve inédite » télécharge la liste entière : **70 requêtes SQL, 26 Ko**, pour un titre et un nombre. | Mesure serveur ; `lib/cursusAccueil.ts` (`useInedites`) |
| A5 | **535 Ko de JavaScript compressé** (1,63 Mo décompressé) en 73 fichiers. Le moteur de rendu Markdown et KaTeX pèse 147 Ko, soit 27 %, et n'affiche rien sur cette page : il est tiré par la ligne des cartes de révision, qui était vide pendant le test. | `CartesDeRevision.tsx:8` importe `PaquetDeCartes` |
| A6 | La page d'hier est affichée depuis le navigateur en attendant le serveur, jusqu'à trois jours après. Le lendemain d'une séance, l'élève voit donc « Séance faite » ou le thème de la veille pendant toute la durée de A1 et A2. | `lib/accueilCache.ts` (`AGE_MAX_MS`) |

## B. Hiérarchie et contenu (faits observés)
| ID | Constat | Preuve |
|----|---------|--------|
| B1 | Dix blocs : quiz en cours, séance, lecture en cours, mes erreurs, palier franchi, défi de la semaine, rappel par e-mail, à reprendre, où j'en suis, prochaine inédite. 2 783 px sur bureau (3,5 écrans), **3 745 px sur mobile (4,6 écrans)**. | Mesure des blocs |
| B2 | Six blocs proposent chacun de reprendre ou de faire autre chose que la séance, sans ordre entre eux : quiz en cours, lecture en cours, mes erreurs, défi, à reprendre, inédite. | Captures |
| B3 | La carte de séance contient douze commandes sur mobile et mesure **1 057 px (1,3 écran)** : bouton principal, quiz express, fréquence, revoir l'aide, trois durées, points, niveau, voir le détail, autre chose, matière de la semaine. | Capture mobile |
| B4 | Sur mobile, les titres sont coupés au mot utile : « Mini-inédite … » dans le défi (la matière disparaît) et « Mini-inédite Franç… » pour l'inédite. Le libellé au-dessus prend trois lignes. | Capture mobile |
| B5 | L'élève a terminé 3 séances et a 30 thèmes en révision en mathématiques. La page lui montre « 1 » dans l'anneau, « aujourd'hui 0 % », « Mathématiques 0 % », « Français 0 % » et « 0/111 maîtrisés ». | Capture ; rejoint l'hypothèse UX-22 du rapport 06 |
| B6 | « +22 j » à côté d'un thème à reprendre n'est pas expliqué. | `fr.ts:503` (`depuis.jours_retard`) |
| B7 | Sur bureau, l'examen et le compte à rebours sont dits trois fois dans le premier écran : pastille « BEPC · J-196 » de l'en-tête, pastille « BEPC » de la carte, « 196 jours avant l'examen ». | Capture bureau |

## C. Défauts de fonctionnement
| ID | Constat | Sévérité | Preuve |
|----|---------|----------|--------|
| C1 | Le tutoriel « Bienvenue sur EduKora, étape 1 sur 3 » s'ouvre pour un abonné qui a déjà trois séances, dès qu'il change d'appareil ou vide son navigateur. Sur mobile il couvre 40 % de l'écran et reste affiché pendant le défilement. La mémoire des guides est gardée par appareil et la condition ne regarde pas l'ancienneté. | Majeur | `lib/guides/contenu.ts:65`, `lib/guides/store.ts` |
| C2 | Quand la langue de l'interface n'est pas celle de l'examen (élève du BEPC sur /en/cm), l'accueil perd « Mes erreurs » et le défi de la semaine, et la ligne des inédites propose celles du GCE : « 100 original papers, Mini Original Paper … GCE O Level ». Le cas inverse (élève du GCE sur l'interface française) suit le même code. | Majeur, cas peu fréquent | `lib/cursusAccueil.ts` (`useCursusAccueil` rend `null`) |
| C3 | Même cas : la phrase du coach et la ligne du coefficient restent en français dans une interface anglaise. C'est voulu (les textes du serveur suivent la langue de l'examen), mais la page mêle alors deux langues. | Mineur | `quiz/accueil.py:588` |

## D. Accessibilité
| ID | Constat | Preuve |
|----|---------|--------|
| D1 | Aucun titre de niveau 1. Deux titres de niveau 2 seulement ; « Bonjour Test » n'est pas un titre. | Relevé des titres |
| D2 | Quatre sections sur dix n'ont pas de nom accessible (quiz en cours, lecture en cours, défi, inédite). | Relevé des sections |
| D3 | Cibles tactiles sous 44 px : « Voir le détail », « Propose-moi autre chose », « Me concentrer sur une matière », « Toutes les minis » et « Les 55 » font 18 px de haut ; le bouton de fermeture 28 px ; les durées, « Ajouter mon e-mail » et « Non merci » 36 px. | Mesure à 375 px |
| D4 | Texte très petit : les lettres des jours de la semaine à 9,6 px, « aujourd'hui 0 % » et « l'essentiel » à 10,4 px. | Mesure |
| D5 | Bon point : aucun bouton ni lien sans nom, pas de débordement horizontal à 375 px. | Mesure |

## E. Ce qui est au niveau
- La recommandation est justifiée par des faits que l'élève peut vérifier (fréquence aux épreuves, date du dernier échec, coefficient). Duolingo et Quizlet ne le font pas.
- Une seule action principale, et un raccourci honnête (« Quiz express ») pour qui a peu de temps.
- Les reprises urgentes passent avant la séance (épreuve au chrono lancé, quiz en cours).
- L'élève peut refuser la proposition (« Propose-moi autre chose ») sans quitter la page.
- La page se met à jour au retour sur l'onglet et s'affiche hors connexion.
- Le délai jusqu'au premier clic est déjà mesuré.

## F. Recommandations
### Lot 1 : vitesse et défauts, sans décision de produit
| ID | Action | Effet attendu |
|----|--------|---------------|
| R1 | Calculer le résumé de « Où j'en suis » par des agrégats (ou le sortir de `/quiz/accueil/` et le charger après la carte de séance). | L'appel principal passe d'environ 1 s à moins de 200 ms. |
| R2 | Mettre le quiz en cours, les cartes dues, le défi et la prochaine inédite dans la réponse de `/quiz/accueil/`. | Plus de saut du bouton, page rendue en une fois, quatre appels en moins, A4 réglé. |
| R3 | Charger le paquet de cartes (et donc le moteur Markdown) à l'ouverture d'un paquet seulement. | 147 Ko de moins sur l'accueil. |
| R4 | Au démarrage, appeler directement le rafraîchissement de session quand aucun jeton n'est en mémoire ; ne plus demander le plan du jour depuis l'en-tête sur l'accueil ; attendre la session avant les appels de vitrine. | Deux allers-retours en série et trois appels en moins. |
| R5 | Ne plus afficher l'état de séance d'un autre jour depuis le cache : garder l'en-tête et la progression, mettre la carte de séance en attente. | Plus de « Séance faite » de la veille. |
| R6 | Ne pas lancer le tutoriel de bienvenue quand `premiers_pas` est faux. | C1 réglé. |
| R7 | Sur l'accueil de l'abonné, prendre l'examen du compte quelle que soit la langue de l'interface. | C2 réglé. |
| R8 | Titre de niveau 1, noms des sections, cibles de 44 px, titres sur deux lignes au lieu d'être coupés, « en retard de 22 jours ». | D1 à D3, B4, B6. |

### Lot 2 : structure de la page, à valider
| ID | Action | Effet attendu |
|----|--------|---------------|
| R9 | Replier la durée, « autre chose » et « matière de la semaine » sous un seul lien « Régler ma séance ». Garder visibles le bouton, le quiz express, la fréquence et la ligne du jour. | Carte de séance d'environ 600 px sur mobile au lieu de 1 057. |
| R10 | Réunir les reprises dans un seul bloc « À continuer », trois lignes au plus, classées par urgence ; le reste derrière « Tout voir ». | Six blocs deviennent un. Page d'environ 3 écrans sur mobile. |
| R11 | Tant que la maîtrise est sous le seuil d'affichage de l'anneau, montrer l'effort : thèmes travaillés et thèmes en révision, par matière. Le pourcentage de maîtrise revient quand il a de quoi dire. | B5 réglé, sans mentir sur le niveau. |
| R12 | Retirer la pastille d'examen de la carte quand l'en-tête l'affiche déjà (bureau, un seul abonnement). | B7. |

### Lot 3 : à vérifier avant de décider
- Rejouer à l'écran « Séance faite » et le premier jour d'un abonné : ce sont les deux états qui décident du retour le lendemain, et ils n'ont pas été vus dans cet audit.
- Mesurer en production le temps de `/quiz/accueil/` et le délai jusqu'à « Commencer », avant et après le lot 1.

## G. Lot 1 codé (2026-11-16, en local, non committé, non déployé)
Décision de l'utilisateur du 2026-11-16 : coder le lot 1. Le lot 2 (structure de la page) n'est pas codé.

| Mesure, même compte, mobile 375x812 | Avant | Après |
|-------------------------------------|-------|-------|
| `GET /quiz/accueil/`, côté serveur | 172 requêtes SQL, 750 à 1 050 ms | 81 requêtes SQL, 170 à 200 ms (cache rempli) ; 167 requêtes et environ 1,1 s au premier appel après un vidage |
| Appels d'API à l'ouverture | 20 | 13, plus l'envoi de mesure d'audience |
| Position du bouton « Commencer » pendant le chargement | 500 px puis 628 px | 628 px dès le premier affichage |
| JavaScript chargé (compressé) | 535 Ko, moteur de formules compris | 332 Ko, sans le moteur de formules |
| Tutoriel « Bienvenue » pour un abonné qui a 3 séances | Affiché | Absent |
| Interface anglaise, élève du BEPC | Sans « Mes erreurs » ni défi, inédites du GCE | « My mistakes », défi et inédite du BEPC |
| Titre de niveau 1, sections nommées | 0 titre, 4 sections sans nom | 1 titre, toutes nommées |

| ID | Ce qui est en place | Où |
|----|---------------------|----|
| R1 | Le classement des thèmes d'une matière est coupé en deux : la part commune à tous les élèves est gardée en cache (dossier de fichiers, partagé entre les processus, une heure), la progression de l'élève est lue une fois pour toutes ses matières. Le cache est vidé quand un lot de contenu est appliqué. | `quiz/services.py` (`squelette_par_frequence`, `progression_par_theme`, `oublier_squelettes`), `edtech_cm/settings.py` (`CACHES`, `PARCOURS_CONTENU_CACHE_SECONDES`), `synchro/moteur.py` |
| R2 | Quiz en cours, cartes dues, défi de la semaine et épreuves inédites entamées arrivent dans la réponse de l'accueil, sous la forme exacte de leurs routes ; le frontend les dépose dans le cache de ces routes. | `quiz/views.py` (`_reprises`), `AccueilEleve.tsx` (`deposerReprises`) |
| R3 | Le paquet de cartes se charge à l'ouverture d'un paquet. | `CartesDeRevision.tsx` |
| R4 | Au démarrage, le jeton est demandé avant le compte : plus de 401 sur `/auth/me/`. Sur l'accueil d'un abonné, l'en-tête ne redemande plus le plan du jour ; le pied de page attend de savoir s'il s'agit d'un abonné. | `api/client.ts` (`restaurerSession`), `AuthContext.tsx`, `FlammeSerie.tsx`, `Footer.tsx` |
| R5 | Une page gardée d'un autre jour n'affiche plus sa carte de séance : celle-ci attend le serveur, le reste s'affiche. Hors connexion ou après un échec, la page d'hier reste entière. | `AccueilEleve.tsx` (`seanceEnAttente`) |
| R6 | Le tutoriel de bienvenue et l'aide « Comment marche ta séance ? » ne s'ouvrent plus d'eux-mêmes pour un élève qui a terminé une séance. Ils restent disponibles à la demande. | `lib/guides/contenu.ts`, repère `eleve-installe` dans `AccueilEleve.tsx` |
| R7 | L'accueil d'un abonné garde l'examen du compte quelle que soit la langue de l'interface. | `lib/cursusAccueil.ts` (`toutesLangues`) |
| R8 | Titre de niveau 1, sections nommées, titres du défi et de l'inédite sur deux lignes, durées, fermeture du palier et boutons de rappel à 44 px, « à revoir depuis 22 j ». | `AccueilEleve.tsx`, `DefiDeLaSemaine.tsx`, `SeanceDuJour.tsx`, `Moments.tsx`, `RappelsEmail.tsx`, `fr.ts`, `en.ts` |

Tests : 1 614 tests frontend ; backend, 2 333 tests (quiz, inedit, synchro, catalog, access) et ceux de users et subscriptions, puis 537 tests relancés dans l'image reconstruite. Nouveau fichier `quiz/test_cache_parcours.py` (9 tests : la progression d'un élève n'est jamais servie à un autre, le résumé est le même avec et sans cache, un contenu publié apparaît dès que le cache est vidé).

### Écarts par rapport à la recommandation
- **R2, prochaine inédite : non faite.** L'en-tête demande la même liste sur toutes les pages (pastille de nouveauté) : la retirer de l'accueil ne supprimait aucun appel. Le constat A4 reste ouvert (70 requêtes SQL, 26 Ko) ; il se règle dans la liste elle-même.
- **R4, appels de vitrine : en partie.** Les chiffres de la plateforme ne partent plus. La liste des inédites sans examen et la campagne partent encore avant la session : elles viennent de l'en-tête et des bandeaux, communs à toutes les pages.
- **R8, liens « Propose-moi autre chose » et « Me concentrer sur une matière » : 38 px** de zone de toucher, pas 44, parce qu'ils sont empilés et que 44 les ferait se chevaucher. Les pastilles « points », « niveau », « fréquence » et « Voir mes 11 matières » restent à 26 ou 36 px. Le titre de « Lecture en cours » est encore coupé sur mobile.
- **R6 étendu** à l'aide de la séance : sans cela elle prenait la place du tutoriel (400 px dans la carte), constaté à l'écran après la première correction.

### Décisions prises en codant, à valider
- **Durée du cache : une heure.** Un thème, un quiz ou un cours modifié dans l'admin (hors lot) met jusqu'à une heure à apparaître dans le parcours et le résumé de progression. Un lot appliqué vide le cache tout de suite. Réglable par `PARCOURS_CONTENU_CACHE_SECONDES` (0 le désactive).
- **Premier appel après un vidage : toujours une seconde environ**, une fois par examen et par heure, pour l'élève qui tombe dessus.
- **« +22 j » devient « à revoir depuis 22 j »** (« due 22 d ago » en anglais).

### Déploiement
Aucune migration. Rebuild du backend et de caddy. Le cache s'écrit dans le dossier temporaire du conteneur (`PARCOURS_CACHE_DOSSIER` pour le déplacer) et se perd à chaque reconstruction, sans conséquence.

## H. Lot 2 codé (2026-11-16, en local, non committé, non déployé)
Décision de l'utilisateur du 2026-11-16 : coder le lot 2. Frontend seul : aucun changement côté serveur.

| Mesure, même compte | À l'audit | Après le lot 2 |
|---------------------|-----------|----------------|
| Blocs de la page | 10 | 6 |
| Carte de séance, mobile 375 px | 1 057 px | 925 px (1 109 px réglages ouverts) |
| Carte de séance, bureau 1 280 px | 702 px | 624 px : elle tient entière dans le premier écran |
| Reprises sous la séance, mobile | 5 blocs, 694 px | 1 bloc, 420 px |
| Page entière, mobile | 3 745 px (4,6 écrans) | 3 397 px (4,2 écrans), dont 2 596 px de contenu (3,2 écrans) |
| Page entière, bureau | 2 783 px | 2 475 px |
| Zéros dans « Où j'en suis » | « 1 », « aujourd'hui 0 % », « 0 % » deux fois, « 0/111 maîtrisés » | « Thèmes déjà travaillés : 41 », « 31 travaillés », « 1 travaillé », « aujourd'hui » |

| ID | Ce qui est en place | Où |
|----|---------------------|----|
| R9 | « Régler ma séance » : la durée, « Propose-moi autre chose » et la matière de la semaine sont repliés sous un seul lien en bas de la carte, fermé au départ. Une matière de la semaine déjà choisie reste visible, parce qu'elle explique le sujet de la séance. La séance verrouillée d'un non-abonné et la séance faite ne changent pas. | `SeanceDuJour.tsx` (`ReglagesSeance`) |
| R10 | « À continuer » : un seul bloc sous la séance, trois lignes au plus, le reste derrière « Voir N de plus ». Ordre : copie entamée, copie à finir de noter, lecture ouverte ; défi de la semaine non relevé ; prochaine inédite ; thèmes à reprendre, erreurs, cartes dues ; défi déjà relevé. L'épreuve au chrono lancé et le quiz commencé restent au-dessus de la séance. « Depuis la dernière fois » ne garde que ce qui a bougé. | `AccueilEleve.tsx` (`AContinuer`), `DefiDeLaSemaine.tsx`, `MesErreurs.tsx`, `CartesDeRevision.tsx` |
| R11 | Tant que la maîtrise est sous le seuil de début, la phrase et l'anneau disent les thèmes travaillés, puis les maîtrisés et le prochain palier. Une matière travaillée sans thème maîtrisé affiche « N travaillés, sur E thèmes » au lieu de « 0 % » et « 0/E maîtrisés ». La barre de trajectoire dit « aujourd'hui » sans « 0 % ». | `OuJenSuis.tsx` |
| R12 | Avec un seul abonnement, l'examen n'est plus redit à côté de « Bonjour » à partir de la largeur où l'en-tête l'affiche. | `TeteAccueil.tsx` (`CursusPreparePuce`) |

Tests : 1 618 tests frontend, dont 4 nouveaux (réglages repliés puis ouverts, ordre et limite des trois lignes, bloc absent sans rien à reprendre, défi en rangée) et 2 mis à jour.

### Écarts par rapport à la recommandation
- **R9 : 925 px sur mobile, pas « environ 600 ».** L'estimation était trop optimiste : les trois réglages pesaient environ 140 px, pas 450. Le reste de la carte est fait du titre, de la phrase du coach, des pastilles, des deux boutons, de la ligne du jour et du parcours, que la recommandation gardait visibles. Descendre plus bas demande de replier aussi la ligne du jour ou le parcours : c'est une autre décision.
- **R10 : page de 4,2 écrans sur mobile, pas « environ 3 »** (3,2 écrans hors pied de page).
- **R12 : non vu à l'écran.** Le compte de test a deux abonnements, donc le sélecteur d'examen, qui reste affiché partout. Le cas à un seul abonnement n'est couvert que par la lecture du code.

### Décisions prises en codant, à valider
- **Cartes dues : la ligne mène à « Mes cartes »** au lieu d'ouvrir le paquet sur place. Un paquet déplié au milieu d'un bloc de trois lignes repoussait tout le reste. Un toucher de plus.
- **« Toutes les minis » et « Les 55 » ne sont plus sur l'accueil.** La ligne du défi et celle de l'inédite mènent à leur fiche ; les listes restent dans « Réviser ».
- **La prochaine épreuve inédite est remontée** juste après le défi de la semaine (validé par l'utilisateur le 2026-11-16) : c'est le contenu que l'abonné paie, il reste visible sans ouvrir « Voir N de plus ». Elle ne passe derrière que si trois choses sont déjà commencées ou à échéance.
- **Quand la séance du jour est la lecture en cours, cette lecture n'apparaît plus ailleurs sur la page.** Elle était redite en bas, dans « Depuis la dernière fois ».
- **L'anneau du début affiche les thèmes travaillés** (41) et non plus les maîtrisés (1), pour porter le même nombre que le début de la phrase.

### Déploiement
Rebuild de caddy seul.
