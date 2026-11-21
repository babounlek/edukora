# 16 - Audit des trois accueils : visiteur, connecté sans abonnement, abonné (profil Guyguy)

Date : samedi 2026-11-21. Site local, image `caddy` reconstruite le jour même à 17 h 54 (elle contient le code de la copie de travail, modifications non committées comprises).
Question posée : pour chacun des trois publics de `/cm`, que faut-il changer pour améliorer l'expérience, l'attractivité, la rétention et l'incitation à l'abonnement ?
Complète les rapports 12 (vitrine, 2026-11-15) et 13 (accueil abonné, 2026-11-16) sans les refaire : ce qu'ils ont fait corriger n'est repris que là où l'écran d'aujourd'hui le contredit. Rien n'a été modifié dans le code.

## 1. Verdict

Les trois accueils ne sont pas au même niveau, et le plus faible est celui du public le plus proche de payer.

| Public | Note (jugement de l'auditeur) | En une phrase |
|---|---|---|
| Visiteur | 3,6 / 5 (2,8 le 15 novembre) | La promesse a maintenant un bouton et une vraie première question à un toucher. Il manque la preuve, et rien ne retient celui qui repart. |
| Connecté sans abonnement | 2,4 / 5 | C'est la page du visiteur avec une porte fermée posée dessus. Rien n'y est personnel, le prix n'est pas à côté du bouton, et ce qu'il peut faire gratuitement est à deux écrans. |
| Abonné (Guyguy) | 4 / 5 (3,7 le 16 novembre) | Une action, une raison, une série, un défi : c'est la meilleure page du produit. Rien n'y prépare le renouvellement, et deux messages découragent. |

Les cinq points qui pèsent le plus, dans l'ordre :

1. **Le connecté sans abonnement n'a pas de page à lui.** Il a donné le signal le plus fort (un compte, un examen) et il reçoit l'argumentaire écrit pour un inconnu : « Comment ça marche », « Faut-il créer un compte ? », « Ta première séance ».
2. **Le prix n'est jamais à côté du bouton qui vend.** « Débloquer ma séance » ne dit ni 2 000 FCFA ni Mobile Money. Le premier prix de la page est à 1 775 px sur mobile (2,2 écrans), à 1 073 px sur bureau (sous le premier écran).
3. **Rien ne prépare la fin d'un abonnement.** Avec un abonnement au mois sans prélèvement, chaque mois est une nouvelle vente. L'accueil de l'abonné ne dit jamais la date de fin, et aucun message ne part avant l'échéance.
4. **Aucune preuve sociale en production.** L'API publique de l'accueil renvoie toujours zéro avis publié.
5. **Trois défauts d'affichage vérifiés**, dont deux touchent le premier jour : le tutoriel qui recouvre « Commencer » chez le visiteur qui revient, le tutoriel qui décale la carte de séance, les cartes de matière qui débordent chez l'abonné sur mobile.

## 2. Méthode et limites

- **Vu à l'écran**, mobile 375 x 812 et bureau 1 366 x 800, page entière :
  - visiteur : première visite, examen choisi (BEPC), puis retour après une séance gratuite jouée (état simulé en posant la mémoire locale `edukora:seances-jouees`) ;
  - connecté sans abonnement : compte `[TEST] Élève sans abonnement` (BAC C), et compte `[TEST] Élève abonnement expiré` (accès échu le 14 novembre) ;
  - abonné : le profil **Guyguy** du compte de l'utilisateur (BEPC, 10 séances terminées, niveau 5, série de 1 jour, un défi de la semaine entamé).
- **Mesuré dans le navigateur** : hauteur des pages et des blocs, position des boutons et des prix, largeur des cartes, défilement interne des cartes, appels d'API.
- **Lu** : `CataloguePage.tsx`, `PremiereSeance.tsx`, `SeanceDuJour.tsx` (séance verrouillée, séance faite), `AccueilEleve.tsx`, `TeteAccueil.tsx` (structure), `OuJenSuis.tsx`, `lib/guides/` et `GuideHost.tsx`, `lib/trajectoire.ts`, `relances/models.py`, `subscriptions/models.py` (parrainage), `Header.tsx`.
- **Production** : une lecture de l'API publique `https://edukora.africa/catalog/accueil/` (1 620 épreuves, 14 164 cours, 26 matières, `temoignages: []`) et de `/subscriptions/campagne/` (aucune campagne en cours).
- **Statut des constats** : « Vérifié » = vu ou mesuré par moi ce jour ; « Code » = lu dans le code, non vu à l'écran ; « Hypothèse » = à confirmer par la mesure d'usage.
- **Limites** :
  - Aucune donnée d'usage réel n'a été lue. Les recommandations de conversion et de rétention sont des hypothèses raisonnées, pas des résultats : chacune est à juger par les évènements déjà posés (`accueil_bouton_clic`, `plan_affiche`, `plan_verrouille_clic`).
  - Non vus à l'écran : « Séance faite », le premier jour d'un abonné, un abonné à quelques jours de son échéance (aucun compte de test dans ce cas), le GCE et l'interface anglaise, le thème sombre, un vrai téléphone, un réseau lent.
  - Temps d'affichage non mesurés : le navigateur d'audit tournait en arrière-plan, ses temps de peinture ne valent rien. Côté serveur, `/quiz/accueil/` a répondu en 330 ms pour Guyguy, en local.
  - Les comparaisons avec d'autres produits reposent sur leur fonctionnement public connu, pas sur un essai fait ce jour.
- **Effets de bord** : en base locale, la date de dernière visite du profil Guyguy et quelques évènements de mesure, écrits par la page elle-même. Les sessions ont été ouvertes par des jetons locaux, sans code de connexion ; le navigateur d'audit a été remis à l'état visiteur.

## 3. Notes par axe

| Axe | Visiteur | Connecté sans abonnement | Abonné (Guyguy) |
|---|---|---|---|
| Expérience | 4 / 5. Un toucher pour l'examen, un toucher pour la première question. Page de 8,1 écrans sur mobile. | 2,5 / 5. Deux « séances » se contredisent, l'action possible est au 3e écran, 8,2 écrans en tout. | 4 / 5. « Commencer » à 490 px, visible sans défiler. Carte de séance de 969 px, un débordement. |
| Attractivité | 3,5 / 5. La carte montre le produit. Aucun avis, aucune image du produit en marche. | 2,5 / 5. Le premier écran est une carte verrouillée, sans salutation ni rien qui lui appartienne. | 4 / 5. Bandeau vert, flamme, niveau, défi : la page a une identité. |
| Rétention | 2,5 / 5. La carte avance d'une matière à chaque retour, c'est tout : ni rappel, ni installation, ni raison de laisser un contact. | 2 / 5. Aucune habitude gratuite proposée, ses points et sa série ne sont pas montrés. | 4 / 5. Série, objectif, défi daté, « depuis ce matin », palier. Un message de trajectoire décourageant. |
| Incitation à l'abonnement | 3 / 5. Prix dit tôt (787 px). Rien ne relie l'essai réussi à l'offre sur cette page. | 2 / 5. Bouton sans prix, sans date, sans preuve ; deux boutons concurrents pour l'ancien abonné. | 1,5 / 5 pour le renouvellement : la date de fin n'apparaît que dans le menu du compte. |

## 4. Défauts vérifiés, à corriger d'abord

Chacun demande moins d'une journée.

| # | Public | Constat | Preuve | Correctif proposé |
|---|---|---|---|---|
| D1 | Visiteur qui revient | **Le tutoriel « Bienvenue sur EduKora » s'ouvre par-dessus la carte « première séance » et recouvre « Commencer, sans compte » sur mobile.** Il ne s'ouvre pas à la toute première visite, seulement dès qu'un examen est choisi et que la page est rechargée : c'est-à-dire pour le visiteur qui revient, le plus proche de s'inscrire. Sur bureau il s'ouvre aussi, en bas à droite, sans rien recouvrir. | 3 rechargements sur 3. Panneau du guide de 559 à 812 px, bouton de 566 à 610 px ; l'élément au centre du bouton est le guide. Cause lue : le guide automatique est décidé dès que l'identité est connue (`GuideHost.tsx:51-59`), avant que la page, chargée à la demande, ait posé la carte ; la condition `!ciblePresente("premiere-seance")` (`lib/guides/contenu.ts:135`) est donc vraie à cet instant. L'attente de la page n'existe que pour l'élève (`GuideHost.tsx:48-49`). | Faire attendre le tutoriel du visiteur comme celui de l'élève (observer la page tant que la carte n'est pas montée), ou le supprimer sur l'accueil : la carte dit déjà la même chose. |
| D2 | Connecté sans abonnement (et probablement nouvel abonné) | **L'étape 3 du tutoriel fait défiler la carte de séance sur elle-même.** Après « Suivant » puis « Terminer », le titre de la séance (« Aujourd'hui · Tableau de variation ») a disparu en haut de la carte et 160 px de vide restent en bas, jusqu'au rechargement. | Rejoué avec de vrais clics : `scrollTop` de la carte à 0 à l'étape 2, à 144 à l'étape 3, inchangé après « Terminer ». Cause : `scrollIntoView` (`lib/guides/cibles.ts:59`) fait défiler tout ancêtre défilable, y compris une carte en `overflow-hidden` dont un décor dépasse (hauteur de contenu 1 091 px pour 947). La carte de l'abonné a la même structure (`TeteAccueil.tsx:97`) : non vu chez lui, à contrôler. | `overflow-clip` à la place de `overflow-hidden` sur les deux cartes (un élément rogné ainsi ne défile pas), ou faire défiler la fenêtre à la main. |
| D3 | Abonné, mobile | **Les deux cartes « Tes 2 matières où il y a le plus à faire » débordent** : 387 px de large dans une grille de 302 px. La pastille « À découvrir » est coupée (« À déc »), le bord droit des cartes est hors de l'écran. | Mesure à 375 px ; cause probable : la grille (`OuJenSuis.tsx:105`) laisse sa colonne s'élargir au contenu, et « Sciences de la Vie et de la Terre » ne se tronque pas. | `min-w-0` sur la carte, ou une colonne `minmax(0, 1fr)`. |
| D4 | Ancien abonné | **Deux boutons pour la même chose, dans le mauvais ordre.** « Se réabonner » (contour) mène droit au bon profil et au bon examen ; juste dessous, « Débloquer ma séance » (plein, le plus visible) mène à la page générique des prix. | Capture mobile ; `SeanceDuJour.tsx:37-55` et `:498-516`. | Quand l'accès est échu, un seul bouton plein : « Me réabonner », avec le lien direct. |
| D5 | Connecté, bureau | L'examen est dit deux fois dans l'en-tête, et le second est tronqué : « BAC C · vers mai 2027 » puis « B. ». | Capture à 1 366 px. | Une seule pastille. |
| D6 | Connecté | La carte gratuite s'appelle « Ta première séance » et son nom accessible dit « sans compte », pour quelqu'un qui a un compte et, peut-être, dix quiz derrière lui. | `PremiereSeance.tsx:113`, `:229`. | Voir N1 : cette carte change de rôle pour un connecté. |
| D7 | Visiteur sans examen | L'épreuve inédite mise en vitrine est la plus récente du pays, quelle qu'elle soit : ce jour, « Mini-inédite Travail manuel Probatoire n°2 ». Une matière que peu d'élèves passent, pour le seul exemple du produit payant. | Texte de la page ; `CataloguePage.tsx:191-192`. | Sans examen choisi, préférer une inédite de mathématiques ou de français, ou attendre le choix de l'examen pour montrer ce bloc. |

## 5. Le visiteur

### Ce qui marche et ne doit pas bouger
- Le premier écran mobile tient la promesse, la question « Tu prépares quel examen ? » et les onze examens. Un toucher donne une vraie séance : « Identité remarquable, Mathématiques, 5 questions, tombé dans 26 épreuves sur 28, J-191 ».
- Le prix est dit à 787 px, sous la carte : « Gratuit pour essayer. Ensuite 2 000 FCFA par mois, par Mobile Money, sans engagement. »
- La carte avance : au retour, « Ta séance suivante · 2 sur 10 », sur une autre matière. Dix séances gratuites pour le BEPC.
- Le ton reste honnête : « Les annales et leurs corrigés existent déjà gratuitement sur Internet. Voici ce qu'EduKora fait en plus. »

### Constats
| # | Constat | Preuve | Statut |
|---|---|---|---|
| V1 | **Aucune preuve sociale en production.** La section n'apparaît qu'à partir de trois avis publiés ; il y en a zéro. Le recueil dans l'application existe depuis le 16 novembre. | `GET https://edukora.africa/catalog/accueil/` : `temoignages: []` | Vérifié |
| V2 | **La page fait 8,1 écrans sur mobile** (6 583 px, dont 986 px de pied de page). L'extrait de corrigé seul fait 1 374 px, soit 1,7 écran de calcul de fractions avant « Comment ça marche ». Le rapport 12 annonçait 6,9 écrans : c'est ce que je mesure aussi avant le chargement différé de l'extrait (5 605 px), sa mesure était donc probablement prise trop tôt. | Mesure après défilement complet | Vérifié |
| V3 | **Après le premier écran, plus aucune action ne suit le visiteur.** Entre la carte (331 px) et « Voir les prix » (5 473 px), cinq écrans sans bouton pour commencer. | Relevé des boutons | Vérifié |
| V4 | **La promesse dit « un cours, un vrai exercice, un quiz, 25 minutes » ; la démonstration est un quiz de 5 questions.** Le visiteur ne voit jamais à quoi ressemble la séance qu'il achèterait. Déjà noté le 13 novembre (inventaire, A12), non tranché. | Carte du hero ; `inventaire-gratuit…md`, décision 3 | Vérifié |
| V5 | **Rien ne retient le visiteur qui repart.** Sa progression tient dans la mémoire du navigateur (`lib/seancesGratuites.ts` le dit : autre appareil ou stockage vidé, tout repart de zéro). L'accueil ne propose ni d'installer l'application, ni de garder ses points en créant un compte, ni un rappel. | Code et page | Vérifié |
| V6 | Le seul bouton de l'en-tête est « Connexion », libellé pour qui a déjà un compte. « Créer mon compte » n'existe que dans le pied de page (5 775 px). | Relevé des liens | Vérifié |
| V7 | Le visiteur qui a fait ses séances gratuites retrouve une carte qui lui parle du nombre de séances, pas de son résultat : ses scores sont pourtant gardés (`scoresDesSeances`). | `PremiereSeance.tsx`, `lib/seancesGratuites.ts` | Code |
| V8 | Les blocs réservés à l'abonné (quiz en cours, cartes de révision, mes erreurs, jalons, cache d'accueil) sont téléchargés par le visiteur. | Liste des fichiers chargés | Vérifié, poids non mesuré |

### Recommandations
| # | Action | Axe | Effort |
|---|---|---|---|
| RV1 | **Obtenir les trois premiers avis.** Le mécanisme est en place, il manque les avis : en demander à dix élèves et parents connus, les publier, et relire la formule de consentement (attendue depuis le 16 novembre). En attendant, écrire la ligne « qui rédige et relit les corrigés » avec les faits réels. | Attractivité, abonnement | S, hors code |
| RV2 | **Raccourcir à 5 écrans.** Borner l'extrait de corrigé à 420 px avec un fondu et « Lire la suite du corrigé » ; replier le bloc parent en trois lignes dépliables sur mobile ; alléger le pied de page du visiteur. | Expérience | S |
| RV3 | **Une barre « Commencer » qui suit le défilement sur mobile**, dès que la carte du hero est sortie de l'écran : l'examen choisi et le bouton, rien d'autre. Disparaît au bas de page. | Expérience, abonnement | S |
| RV4 | **Montrer la séance entière sous la carte** : « Comprendre, S'entraîner, Vérifier », avec la mention « avec l'abonnement, chaque jour ». Le composant du parcours verrouillé existe déjà. Trancher la décision 3 de l'inventaire. | Attractivité, abonnement | S à M |
| RV5 | **Le visiteur qui revient voit ce qu'il a fait** : « 2 séances faites, meilleur score 4 sur 5 », puis une invitation datée, « Crée ton compte pour garder tes points ». Après la troisième séance gratuite, pas avant. | Rétention | S |
| RV6 | **Invite d'installation sur l'accueil du visiteur qui revient** (elle n'existe que sur le résultat d'un quiz, `QuizResultPage.tsx`) : « Garde EduKora sur ton téléphone, ça marche sans réseau ». Une invitation à la fois, comme aujourd'hui. | Rétention | S |
| RV7 | Corriger D1 et D7. | Expérience | S |

## 6. Le connecté sans abonnement

C'est le public que cet audit regardait pour la première fois à l'écran, et c'est là qu'est le plus gros gain.

### Ce qu'il voit, dans l'ordre (mobile)
| Position | Bloc | Pour lui |
|---|---|---|
| 72 px | Séance du jour verrouillée : « Tableau de variation, tombé dans 28 épreuves sur 45, coefficient 7 », « Débloquer ma séance », « Montrer à mes parents », le parcours en trois étapes | Une porte fermée. Bien faite, mais sans prix. |
| 1 084 px | « Reprendre ma lecture » | Utile. |
| 1 160 px | Le hero du visiteur : « Chaque jour, on te dit quoi réviser. » | Il le sait déjà. |
| 1 419 px | « Ta première séance : Équation différentielle, 6 questions, tombé dans 7 épreuves sur 45 », bouton « Commencer » à 1 654 px | **La seule chose qu'il peut faire**, au troisième écran, sur un autre thème que celui qu'on vient de lui recommander. |
| 1 775 px | Première mention du prix | 2,2 écrans après le bouton « Débloquer ». |
| 2 165 à 5 575 px | Extrait de corrigé, « Comment ça marche » (« 1. Tu dis ce que tu prépares »), inédite, « Tu es parent ? », questions fréquentes (« Faut-il créer un compte ? »), « Prêt à commencer ? » | L'argumentaire d'un inconnu. |

Total : 6 638 px, 8,2 écrans. Sur bureau, la carte verrouillée occupe tout le premier écran ; la séance gratuite et le prix sont dessous.

### Constats
| # | Constat | Preuve | Statut |
|---|---|---|---|
| C1 | **« Débloquer ma séance » ne dit pas combien.** Ni prix, ni Mobile Money, ni durée. La seule phrase d'offre de la carte est « Avec l'abonnement, tu choisis la durée de ta séance : 10 min, 25 min, 45 min », un avantage mineur. | Capture ; `SeanceDuJour.tsx:498-516`, `:1084-1090` | Vérifié |
| C2 | **Deux séances se contredisent.** En haut, « Aujourd'hui : Tableau de variation » (28 épreuves sur 45), fermée. Plus bas, « Ta première séance : Équation différentielle » (7 sur 45), ouverte. La carte gratuite annonce « un thème qui tombe souvent » ; la carte fermée montre qu'un autre tombe quatre fois plus. | Texte de la page | Vérifié |
| C3 | **Rien n'est personnel.** Pas de « Bonjour », pas de compte à rebours au premier écran sur mobile, pas de points ni de niveau, alors qu'un quiz gratuit joué par un connecté crédite de vrais points (inventaire du 13 novembre, B2). La flamme n'apparaît dans l'en-tête qu'avec une série en cours. | Capture ; en-tête mobile : « Test » | Vérifié (points réels : relevé le 13 novembre, non recontrôlé) |
| C4 | **L'ancien abonné ne voit rien de ce qu'il perd.** « Ton accès a pris fin le 14 novembre 2026. Réabonne-toi pour reprendre ta séance. » Aucun rappel de ses thèmes en révision, de ses erreurs à refaire, de son niveau, de sa série. Sa séance dit « Tu ne l'as encore jamais travaillé ». | Capture du compte expiré | Vérifié |
| C5 | Le tutoriel de ce public tient en trois phrases qui décrivent la porte fermée (« Elle reste fermée tant que tu n'es pas abonné : ce bouton te montre comment l'ouvrir »). Il ne dit pas ce qui est gratuit. | Texte des trois étapes | Vérifié |
| C6 | « Un devoir bientôt ? Me concentrer sur une matière cette semaine » reste affiché dans une séance qu'il ne peut pas ouvrir. | Capture | Vérifié, effet du clic non testé |
| C7 | La page des prix, elle, est prête : examen présélectionné, total collant « 6 000 FCFA pour 3 mois », bouton « Continuer ». Trois mois sont présélectionnés (défaut non validé, noté le 11 novembre), et la première pastille dit « Activé après vérification (≈ 3 heures) ». | `/tarifs` vu en mobile | Vérifié |

### Recommandations
| # | Action | Axe | Effort |
|---|---|---|---|
| N1 | **Une page à lui : « Aujourd'hui », version gratuite.** Garder la carte de séance en tête, mais la rendre faisable : son bouton principal lance la séance gratuite du jour (le thème gratuit suivant, celui de la carte du hero), sous le titre « Ta séance gratuite d'aujourd'hui ». La séance complète recommandée (« Tableau de variation, 28 sur 45 ») devient la deuxième ligne de la carte : « La séance complète du jour, avec l'abonnement ». Une seule carte, une seule séance, une action possible au premier écran. | Expérience, rétention | M |
| N2 | **Mettre le prix sous le bouton.** « 2 000 FCFA par mois · Orange Money ou MTN MoMo · sans engagement », et, quand la date de l'examen est connue, « J-191 : il reste 27 semaines ». Une ligne, sous « Débloquer ma séance ». | Abonnement | S |
| N3 | **Retirer l'argumentaire du visiteur pour un connecté.** Garder : la carte, la reprise de lecture, l'extrait de corrigé de son examen, l'inédite de son examen, le bloc parent réduit à « Montrer à mes parents ». Retirer : le hero, « Comment ça marche », la question « Faut-il créer un compte ? », « Preparing the GCE? ». Cible : 3 à 4 écrans. La vitrine complète reste celle des visiteurs et des robots. | Expérience | S à M |
| N4 | **Lui montrer ce qu'il a déjà.** En tête : « Bonjour Test », ses points, son niveau, ses séances gratuites faites (« 3 sur 10 »). C'est la base de l'habitude gratuite, et ce qui rend la suite désirable. | Rétention, attractivité | S à M |
| N5 | **Remplacer la porte fermée par un aperçu.** Laisser ouverte la première étape de la séance complète (« Relire la méthode » : d'après l'inventaire du 13 novembre, un cours se lit déjà sans payer) et fermer les deux suivantes. L'élève commence, puis rencontre le verrou au moment où il veut continuer. Décision de produit : elle touche à ce qui est gratuit. | Abonnement | M |
| N6 | **Pour l'ancien abonné, dire ce qui l'attend** : par exemple « 12 thèmes en révision et 18 erreurs à refaire t'attendent », son niveau, puis un seul bouton « Me réabonner ». Les chiffres existent côté serveur (`revisions`, `erreurs_total`). Jamais de reproche, seulement ce qui est à lui. | Abonnement, rétention | S à M |
| N7 | **Réécrire le tutoriel de ce public** : étape 1 inchangée ; étape 2, « Voici ce que tu peux faire gratuitement chaque jour » ; étape 3, ce que l'abonnement ajoute, avec le prix. | Expérience | S |
| N8 | Corriger D2, D4, D5, D6 ; retirer C6 d'une séance fermée. | Expérience | S |

## 7. L'abonné (profil Guyguy)

### Ce qui marche et ne doit pas bouger
- Le premier écran mobile : « Bonjour Guyguy · BEPC », « 191 jours avant l'examen », le thème, la raison (« Ce thème t'a déjà posé problème : 15 minutes pour le fixer avant qu'il ne s'efface »), la fréquence (8 sur 28), et « Commencer : faire un exercice » à 490 px.
- « Quiz express, 3 questions, jusqu'à 30 points » : une sortie honnête pour le jour sans temps.
- « À continuer » en trois lignes, dans l'ordre de ce qui presse : la copie du défi (« Encore 1 jour, le même sujet pour tous »), la lecture, la prochaine inédite.
- « Depuis ce matin : 1 séance, 19 questions travaillées. Passés en solide : Logiciel de base, Masse molaire. 1 révision qui a tenu. » C'est le meilleur texte de la page : des faits, à lui.
- Page de 4,3 écrans sur mobile (3 485 px), 14 appels d'API, réponse de l'accueil en 330 ms en local. Sur bureau, la carte de séance tient dans le premier écran.

### Constats
| # | Constat | Preuve | Statut |
|---|---|---|---|
| G1 | **Rien ne prépare le renouvellement.** La date de fin n'est écrite que dans le menu du compte. L'accueil ne l'annonce pas à l'approche, et aucun message ne part : les six types de relance couvrent la séance, le paiement abandonné, le bilan parent et l'absence, pas l'échéance. Recommandé le 16 novembre (rapport 14, F1), non fait. | `Header.tsx:101-110`, `relances/models.py:4-10` | Code |
| G2 | **Un message de trajectoire qui décourage.** « À ce rythme (2,3 séances par semaine), tu couvres 17 % de l'essentiel le jour J. Le temps manque pour tout : vise ce qui tombe le plus. » Dit à un élève actif, à 191 jours de l'examen. La phrase qui donne un levier (« N séances de plus par semaine et tu y es ») ne s'affiche que quand l'objectif entier est atteignable. | Capture ; `lib/trajectoire.ts:27-31` | Vérifié (le calcul lui-même n'a pas été recontrôlé) |
| G3 | **Des zéros dans les matières à faire.** « Français, À découvrir, 0/96 maîtrisés », « Sciences de la Vie et de la Terre, 0/91 maîtrisés », sans bouton pour commencer. Le correctif du 16 novembre (R11) ne couvrait que les matières déjà travaillées. | Capture | Vérifié |
| G4 | La carte de séance fait 969 px sur mobile (1,2 écran). Entre les pastilles et le bouton, le lien « Revoir cette aide » occupe 44 px pour un élève qui a dix séances. | Mesure | Vérifié |
| G5 | Le titre du défi est coupé sur mobile : « Mini-inédite Mathématiques… ». La ligne porte cinq informations sur quatre lignes. | Capture | Vérifié |
| G6 | Textes très petits, déjà signalés le 16 novembre et toujours là : jours de la semaine à 9,6 px, « aujourd'hui 4 % » et « l'essentiel » à 10,4 px. | Mesure | Vérifié |
| G7 | **L'accueil ne demande jamais rien à l'abonné satisfait** : ni inviter un camarade, ni montrer son bilan à ses parents. Le partage n'existe que sur le résultat d'un quiz et dans « Mon compte ». Le parrainage est un simple lien, sans récompense, par décision du 28 septembre. | `ParrainageHint.tsx`, `subscriptions/models.py:699-707` | Code |
| G8 | Le bilan du parent est éteint par défaut et l'accueil ne propose pas de l'allumer. Or c'est le parent qui paiera le mois suivant. C'est un réglage du titulaire du compte. | `users/models.py:220-221` (`default=False`) ; aucune mention dans `AccueilEleve.tsx` ni `TeteAccueil.tsx` | Code |
| G9 | L'accueil de l'abonné déclenche encore des appels de vitrine avant de savoir qui regarde (liste des inédites du pays, chiffres de la plateforme, campagne). | Liste des appels | Vérifié |

### Recommandations
| # | Action | Axe | Effort |
|---|---|---|---|
| A1 | **Préparer le renouvellement, en trois temps.** À J-7 : une ligne sobre en tête de l'accueil, « Ton accès se termine le 13 décembre », avec ce qu'il a fait ce mois-ci (par exemple « 14 séances, 6 thèmes devenus solides ») et « Montrer à mes parents ». À J-3 et le jour même : un message au payeur (e-mail, puis WhatsApp quand les modèles seront approuvés) avec le lien direct `/abonnement?cursus=…&profil=…`, qui existe déjà. À J+1 : la page de l'ancien abonné (N6). Jamais de compte à rebours anxiogène pour l'élève : c'est le parent qu'on informe. | Abonnement, rétention | M |
| A2 | **Réécrire le message de trajectoire quand tout n'est pas atteignable.** Dire le pas suivant, pas le verdict : « Avec une séance de plus par semaine, tu passes de 17 % à 24 % de l'essentiel. » Garder « vise ce qui tombe le plus » comme conseil. Le serveur calcule déjà le rythme et la part couverte. | Rétention | S |
| A3 | **Une matière jamais ouverte s'affiche comme une invitation** : « Français : 96 thèmes, commence par celui qui tombe le plus », avec un bouton. Plus de « 0/96 maîtrisés ». | Rétention, expérience | S |
| A4 | **Proposer le bilan du parent depuis l'accueil**, une fois, après la troisième séance : « Tes parents peuvent recevoir ton bilan chaque dimanche. » Le réglage appartient au titulaire du compte : pour un profil enfant, la ligne devient un message à envoyer au parent, pas un interrupteur. Même place et même règle que l'invitation aux rappels (une invitation à la fois). | Abonnement, rétention | S |
| A5 | Alléger la carte : « Revoir cette aide » passe dans « Régler ma séance » pour un élève installé ; le titre du défi sur deux lignes entières. | Expérience | S |
| A6 | Corriger D3 ; remonter les trois textes sous 11 px à 12 px. | Expérience | S |
| A7 | **Rejouer à l'écran « Séance faite » et le premier jour d'un abonné**, avec un compte de test neuf. Ce sont les deux états qui décident du retour le lendemain ; ils n'ont été vus ni le 16 novembre ni aujourd'hui. Le code de « Séance faite » annonce bien ce qui revient demain (`phraseDeDemain`). | Rétention | S |

## 8. Recommandations classées, tous publics

### Lot 1 : une à deux journées, sans décision de produit
D1, D2, D3, D4, D5, D7 ; N2 (prix sous le bouton) ; A2 (trajectoire) ; A3 (matières à zéro) ; A5, A6 ; RV2 (longueur de la vitrine).

### Lot 2 : la page du connecté sans abonnement (3 à 5 jours)
N1, N3, N4, N6, N7. C'est le chantier au meilleur rapport : il ne touche ni au contenu gratuit ni au prix, seulement à l'ordre et au ton d'une page que voient tous les inscrits avant de payer.

### Lot 3 : le renouvellement (3 à 5 jours)
A1, A4. Sans lui, la rétention gagnée sur l'accueil s'arrête au trentième jour.

### Lot 4 : le visiteur
RV1 (avis, hors code), RV3, RV4, RV5, RV6.

### À mesurer avant et après
| Question | Évènement déjà posé | Ce qu'il manque |
|---|---|---|
| Combien de connectés sans abonnement cliquent « Débloquer » ? | `plan_affiche` (avec `verrouillee`), `plan_verrouille_clic` | Rien : le rapport se lit déjà dans l'admin |
| Combien lancent la séance gratuite depuis l'accueil, connectés ou non ? | `accueil_bouton_clic`, cible `premiere_seance` | Distinguer connecté et visiteur dans l'évènement |
| Le visiteur revient-il ? | Aucun | Un évènement « séance suivante affichée » avec le rang (2 sur 10) |
| Combien d'abonnés renouvellent ? | Aucun sur l'accueil | Un évènement à l'affichage et au clic de la ligne de fin d'accès (A1) |

## 9. Ce que je ne recommande pas

- **Un compte à rebours ou une promotion à durée inventée** pour presser l'achat. La seule échéance vraie est celle de l'examen : « J-191 » suffit, et le public est mineur.
- **Fermer davantage le gratuit** pour pousser à l'abonnement. Les séances gratuites sont ce qui amène l'élève jusqu'à la carte verrouillée ; le problème mesuré ici est l'ordre de la page, pas la générosité.
- **Une fenêtre qui s'ouvre toute seule** à l'arrivée (inscription, promotion, installation). D1 montre ce que coûte une fenêtre mal placée ; les invitations restent dans la page, une à la fois.
- **Ligues, classements nominatifs, vies, monnaie virtuelle** : écartés par les rapports 10 et 14, rien ne change cet avis.
- **Récompenser le parrainage** sans rouvrir la décision du 28 septembre : la proposition F6 du rapport 14 attend toujours une réponse, elle n'est pas reprise ici.

## 10. Décisions à prendre

1. **Page du connecté sans abonnement (N1, N3)** : lui retirer l'argumentaire du visiteur et lui donner une page « Aujourd'hui » gratuite ? Le commentaire de `CataloguePage.tsx` dit que la vitrine est « sa page de conversion » : cet audit propose de garder l'intention et de changer la forme.
2. **Aperçu de la séance complète (N5, RV4)** : laisser ouverte la première étape pour un non-abonné, ou seulement montrer la structure ?
3. **Renouvellement (A1)** : à qui parle-t-on avant l'échéance, l'élève dans l'application, le parent par message, ou les deux ? Et à combien de jours ?
4. **Durée présélectionnée sur la page des prix** : trois mois (6 000 FCFA) ou un mois (2 000 FCFA, le prix annoncé partout sur l'accueil) ? En attente depuis le 11 novembre.
5. **Avis (RV1)** : relire la formule de consentement et publier les premiers avis.

## 11. Lot 1 codé (2026-11-21, en local, non committé, non déployé)

Décision de l'utilisateur du 2026-11-21 : coder le lot 1. Frontend seul, aucun changement côté serveur, aucune migration.

| Mesure, mobile 375 x 812 | À l'audit | Après le lot 1 |
|---|---|---|
| Visiteur qui revient (examen choisi) : tutoriel par-dessus « Commencer, sans compte » | 3 rechargements sur 3 | 0 sur 3 |
| Tutoriel du connecté, étape 3 : défilement interne de la carte de séance | 144 px, titre masqué | 0 px, la fenêtre défile et centre la cible |
| Vitrine du visiteur, page entière | 6 583 px (8,1 écrans) | 5 579 px (6,9 écrans) |
| Extrait de corrigé | 1 374 px | 744 px (extrait borné à 416 px, avec un fondu) |
| « Comment ça marche » | 841 px | 697 px |
| « Tu es parent ? » | 793 px | 635 px |
| Compte sans abonnement : premier prix | 1 775 px du haut | sous « Débloquer ma séance », au premier écran |
| Compte expiré : boutons pour se réabonner | 2 (« Se réabonner » en contour, « Débloquer ma séance » plein vers la page générique) | 1, plein : « Me réabonner », vers `/abonnement?cursus=…&profil=…` |
| Guyguy : cartes « Tes 2 matières… » | 387 px dans 302, pastille coupée | 302 px dans 302 |
| Guyguy : bouton « Commencer » | 490 px du haut | 438 px |
| Guyguy : carte de séance | 969 px | 921 px |
| Guyguy : textes sous 11,5 px | 7 | 0 |

| ID | Ce qui est en place | Où |
|---|---|---|
| D1 | Le tutoriel du visiteur ne se décide qu'une fois l'accueil monté (repère `accueil-vitrine`), et l'hôte des guides observe la page pour un visiteur comme pour un élève. | `lib/guides/contenu.ts`, `components/guides/GuideHost.tsx`, `pages/CataloguePage.tsx` |
| D2 | Un guide amène sa cible à l'écran en faisant défiler la fenêtre seule, plus par `scrollIntoView`. Vaut pour tous les guides et toutes les cartes, celle de l'abonné comprise. | `lib/guides/cibles.ts` |
| D3 | La grille des matières ne s'élargit plus au contenu. | `components/OuJenSuis.tsx` |
| D4 | Accès échu : le message et la date dans le bandeau, un seul bouton plein « Me réabonner » qui mène au bon profil et au bon examen. | `components/SeanceDuJour.tsx` |
| D5 | Le compte à rebours ne redit plus l'examen quand il est écrit à côté : en-tête (« vers mai 2027 » puis « BAC C ») et carte « première séance ». | `components/CompteAReboursBadge.tsx`, `Header.tsx`, `PremiereSeance.tsx` |
| D7 | Sans examen choisi, l'inédite mise en vitrine est prise parmi les récentes en mathématiques, puis en français (ce jour : « Mini-inédite Français Probatoire C, D, E et TI n°2 »). Examen choisi : inchangé. | `pages/CataloguePage.tsx` |
| N2 | « 2 000 FCFA par mois, par Mobile Money (Orange ou MTN), sans engagement. » juste sous le bouton de la séance verrouillée. | `components/SeanceDuJour.tsx`, textes |
| A2 | Quand la cible entière n'est plus à portée : « Avec une séance de plus par semaine, tu passes à 22 %. » (Guyguy : de 17 à 22 %). Le chiffre vient du serveur, qui le calculait déjà pour « Mon plan ». Sans gain lisible, l'ancien texte. | `lib/trajectoire.ts`, textes |
| A3 | Une matière jamais ouverte dit « 96 thèmes · commence par celui qui tombe le plus » au lieu de « 0/96 maîtrisés ». | `components/OuJenSuis.tsx`, textes |
| A5 | « Revoir cette aide » est rangé dans « Régler ma séance » ; le titre d'une copie entamée tient sur trois lignes. | `components/SeanceDuJour.tsx`, `AccueilEleve.tsx` |
| A6 | Jours de la semaine, « aujourd'hui 4 % » et « l'essentiel » à 12 px. | `components/LigneJour.tsx`, `OuJenSuis.tsx` |
| RV2 | Extrait de corrigé borné avec un fondu (le bouton « Lire le corrigé complet » est juste dessous) ; sur un téléphone, les étapes de « Comment ça marche » et le bloc parent passent en lignes, numéro ou icône à gauche. Texte entier dans tous les cas. | `pages/CataloguePage.tsx`, `components/SectionParents.tsx` |

Tests : 1 706 tests frontend au vert après les modifications, puis les suites des composants, des pages et des bibliothèques relancées après les deux derniers ajustements (1 769 exécutions, toutes vertes) ; contrôle des types sans erreur. Cinq tests ajoutés : le tutoriel du visiteur attend la page et ne recouvre pas la carte (deux), le défilement de la fenêtre seule (deux), le message de trajectoire (un).

Vérifié à l'écran sur l'image `caddy` reconstruite : visiteur (première visite, examen choisi, trois rechargements), compte sans abonnement (mobile et bureau, tutoriel rejoué en vrais clics), compte expiré, profil Guyguy (réglages ouverts).

### Écarts par rapport à la recommandation
- **RV2 : 6,9 écrans, pas 5.** Le pied de page du visiteur (986 px) n'a pas été touché : il est commun à toutes les pages. L'atteindre demande de l'alléger ou de retirer une section.
- **N2 : la ligne « J-191 : il reste 27 semaines » n'est pas écrite**, seulement le prix.
- **A5 : le sous-titre « Durée, autre thème, matière de la semaine » n'annonce pas l'aide.** Avec « , aide » il passait sur deux lignes à 375 px et renvoyait le chevron seul sur une troisième.
- **D6 non traité** (« Ta première séance », « sans compte » pour un connecté) : il relève du lot 2, où cette carte change de rôle.

### Décisions prises en codant, à valider
- **« Me réabonner »** remplace « Se réabonner » sur la carte de séance (la page « Mes accès » garde « Se réabonner »).
- **L'extrait de corrigé est aussi borné sur bureau**, où il dépassait 416 px.
- **Le prix affiché sous le bouton est le prix normal** (`PRIX_MOIS_FCFA`), comme dans le hero : une campagne en cours n'y est pas reprise.

### Vu en passant, non traité
- Le tutoriel de bienvenue s'ouvre pour un ancien abonné sur un nouvel appareil (« Étape 1 sur 3 »), comme pour un nouvel inscrit.
- La console du navigateur d'audit a affiché plusieurs fois « An unknown error occurred when fetching the script » pendant la session, au fil des trois redémarrages du conteneur. `sw.js` répond 200 et aucun fichier du service worker n'a été touché : non étudié.

### Déploiement
Rebuild de `caddy` seul.

## 12. Lot 2 codé (2026-11-21, en local, non committé, non déployé)

Décision de l'utilisateur du 2026-11-21 : coder le lot 2, la page du connecté sans abonnement. Frontend seul : le serveur donnait déjà tout (plan du jour, points, niveau, série, erreurs, révisions) à un compte sans abonnement. Aucune migration.

| Mesure, compte `[TEST] Élève sans abonnement`, mobile 375 x 812 | À l'audit | Après le lot 2 |
|---|---|---|
| Première chose de la page | Séance verrouillée, « Débloquer ma séance » | « Bonjour Test · BAC C », puis sa séance gratuite |
| Bouton « Commencer » (la seule action gratuite) | 1 654 px du haut, 3e écran | 395 px, premier écran |
| Séances proposées | 2 qui se contredisent | 1 gratuite à faire, 1 complète fermée dessous |
| Ses points, son niveau, sa semaine | Absents | Sous le bouton (« 2 points · objectif 50 » après une réponse) |
| Premier prix | 1 775 px | 960 px, sous « Débloquer ma séance » |
| Page entière | 6 638 px (8,2 écrans) | 4 220 px (5,2 écrans), dont 983 px de pied de page |
| Titre de la page | « Corrigés BEPC, Probatoire, BAC - Cameroun » | « Aujourd'hui » |
| Bureau 1 366 x 800 | Carte verrouillée sur tout le premier écran | Les deux étages et le prix dans le premier écran |

| ID | Ce qui est en place | Où |
|---|---|---|
| N1 | Une carte « Aujourd'hui » : la salutation, l'examen (qu'il peut changer) et le compte à rebours ; puis « Ta séance gratuite · 1 sur 10 », le thème gratuit suivant de son examen, lancée en un toucher. C'est le seul bouton plein du premier écran. Toutes jouées : il le lit, peut en refaire une. | `components/AccueilDecouverte.tsx` |
| N1 | Dessous, dans la même carte : « La séance complète du jour · avec l'abonnement », en version courte (thème, fréquence, « Comprendre → S'entraîner → Vérifier », deux raisons), le bouton, le prix, « Montrer à mes parents ». | `SeanceCompleteVerrouillee` dans `components/SeanceDuJour.tsx` |
| N3 | Pour ce public, la page ne garde de la vitrine que la reprise de lecture, l'extrait de corrigé de son examen, l'épreuve inédite de son examen, les avis et « Prêt à commencer ? ». Le hero, les chiffres, « Comment ça marche », « Tu es parent ? » et les questions fréquentes ne lui sont plus montrés. La vitrine du visiteur et des robots est inchangée. | `pages/CataloguePage.tsx` (`decouverte`) |
| N4 | Ses points du jour, son niveau, sa série et sa semaine, par le même composant que chez l'abonné. Un quiz commencé se reprend en tête de page (« Quiz en cours · 1 / 6 répondues »). | `AccueilDecouverte.tsx` (`LigneJour`, `ReprendreQuiz`) |
| N6 | Ancien abonné : la date de fin, « Tu retrouves ce que tu as construit : 12 thèmes en révision, 3 thèmes maîtrisés et 18 erreurs à refaire. » quand il y a de quoi dire, et un seul bouton « Me réabonner » vers le bon profil. Les chiffres viennent de `/quiz/accueil/`, demandé seulement pour lui. | `SeanceCompleteVerrouillee`, `CeQuiAttend` |
| N7 | Tutoriel réécrit, en trois étapes : la bienvenue, « Ta séance gratuite » sur le bouton « Commencer », « Ce que l'abonnement ajoute » sur le bouton « Débloquer », avec le prix. Version 2 : il sera reproposé une fois à qui avait vu l'ancien. | `lib/guides/contenu.ts`, `lib/guides/textes.ts`, textes |
| D6 | « Ta première séance » et « sans compte » ne sont plus dits à un connecté. | `AccueilDecouverte.tsx` |
| - | Pendant que la session se retrouve, un élève connecté, abonné ou non, voit un squelette et non le hero du visiteur. | `pages/CataloguePage.tsx` (indice `edukora:accueil-eleve`) |
| - | Nouvelle valeur de mesure : `accueil_bouton_clic` avec `cible: seance_gratuite`, distincte de `premiere_seance` (visiteur). Répond à la ligne 2 du tableau « À mesurer » de la section 8. | `AccueilDecouverte.tsx` ; commentaire dans `backend/analytics/models.py` |

Tests : 1 714 tests frontend au vert, contrôle des types sans erreur. Huit tests de plus qu'après le lot 1 : sept pour la nouvelle page (séance gratuite lancée, points et séance complète avec prix, matière suivante, tour fait, ancien abonné avec et sans historique, plan sans séance), et le test du tutoriel de ce public remplacé par deux (les trois étapes avec le prix ; l'étape « gratuit » sautée quand tout est joué). Deux autres tests des guides adaptés.

Vérifié à l'écran sur l'image `caddy` reconstruite : compte sans abonnement en mobile et sur bureau, tutoriel rejoué en vrais clics (cibles amenées à l'écran, carte non décalée), « Commencer » qui ouvre la question 1 sur 6, retour avec la ligne « Quiz en cours » et les points à jour, compte expiré, puis visiteur et profil Guyguy pour contrôle : inchangés (5 579 px et 3 493 px).

### Écarts par rapport à la recommandation
- **N1 : le titre est « Ta séance gratuite · 1 sur 10 », pas « Ta séance gratuite d'aujourd'hui ».** Les séances gratuites sont une liste finie, une par matière : elles avancent quand on en joue une, pas chaque jour. Le nom ne promet pas une nouveauté quotidienne.
- **N3 : 5,2 écrans, pas 3 à 4.** Le pied de page pèse 983 px ; le contenu propre fait 4 écrans. « Tu es parent ? » est retiré en entier plutôt que réduit : « Montrer à mes parents » est dans la carte.
- **N4 : « 3 sur 10 séances faites » se lit dans le titre de la carte** (« · 4 sur 10 »), pas dans une ligne à part. Ce compte reste gardé sur l'appareil, comme pour le visiteur : sur un autre téléphone il repart de 1.
- **N5 non fait** (laisser ouverte la première étape de la séance complète) : c'est une décision de produit, toujours en attente.
- **N6 : non vu à l'écran avec des chiffres.** Le compte de test expiré n'a aucun historique ; la phrase est couverte par deux tests, pas par une capture.

### Décisions prises en codant, à valider
- **La séance complète est montrée en version courte** : plus de parcours détaillé à trois cartes, plus de « Avec l'abonnement, tu choisis la durée », plus de « Un devoir bientôt ? Me concentrer sur une matière » (réglage inutile sur une séance fermée, constat C6).
- **Deux liens gratuits sous la carte** : « Lire un corrigé gratuit » et « Les thèmes qui tombent le plus à ton examen ». Ils étaient dans le hero retiré.
- **Le tutoriel passe en version 2**, donc se rejoue une fois pour un élève sans abonnement qui avait fermé l'ancien.
- **L'ancienne carte verrouillée en grand reste dans le code** pour un seul cas : un compte abonné à un examen qui en regarde un autre.

### Vu en passant, non traité
- En base locale, le quiz gratuit de mathématiques du BAC C est fait de six questions à rédiger (« garde un brouillon ») : c'est la première chose que lance le bouton « Commencer ». La base locale est en retard sur la production pour les questions à choix (noté le 2026-11-17) : à contrôler en production avant de juger.
- Avec un quiz gratuit en cours sur le thème de la carte, « Commencer » et « Reprendre » coexistent. Non étudié : ce que fait le serveur d'un second lancement du même thème.

### Déploiement
Rebuild de `caddy` seul. Le changement de `backend/analytics/models.py` est un commentaire.
