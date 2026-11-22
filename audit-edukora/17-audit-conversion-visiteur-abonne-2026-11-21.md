# 17 - Du visiteur à l'abonné : où l'on perd les gens, et quoi faire

Date : samedi 2026-11-21 (soir). Question posée : parcourir tout le site comme un visiteur et proposer les actions pour le convertir « dans 95 % des cas » en abonné.
Complète les rapports 12, 14 et 16 sans les refaire. Rien n'a été modifié dans le code.

## 1. Réponse courte

**95 % des visiteurs, aucun site ne l'obtient.** Un produit gratuit à l'essai et payant ensuite transforme en général quelques visiteurs sur cent (ordre de grandeur connu du secteur, pas une mesure d'EduKora). Ce qui peut viser 95 %, c'est **chaque marche du tunnel une fois la décision prise** : quelqu'un qui clique « Continuer » sur la page des prix doit arriver à un accès ouvert presque à coup sûr. Aujourd'hui c'est la partie la plus fragile du site.

Les trois visiteurs simulés disent la même chose : le gratuit convainc (Q1 4 sur 5 pour les trois, aucun blocage), et aucun ne paie ce soir (« peut-être » pour les trois). L'envie est créée par les pages de contenu ; elle se perd entre le verrou, la page des prix, l'écran de connexion et l'écran de paiement.

Les cinq points qui pèsent le plus :

1. **Le paiement automatique est coupé en production.** `https://edukora.africa/payments/config/` répond `campay_active: false`. Tout achat passe par : créer un compte, lire un numéro, sortir du site, faire un transfert, revenir, saisir le numéro de transaction, attendre « ≈ 3 heures ».
2. **Un message d'erreur rouge accueille le nouveau venu qui veut payer.** « Session expirée - Reconnecte-toi pour continuer. » s'affiche à un visiteur sans compte qui clique « Continuer » sur les prix. Reproduit trois fois, cause trouvée.
3. **Le verrou du corrigé ne vend pas.** Sur la page où arrive un visiteur de Google, le bloc cadenas ne dit ni le prix, ni un extrait, ni qu'il existe 25 corrigés gratuits du même examen. Relevé par les trois visiteurs.
4. **Rien ne rassure celui qui paie.** Zéro avis publié, aucun nom, un bénéficiaire qui est une personne et pas la société, une aide qui décrit une autre offre et un autre prix que la page des prix.
5. **Personne ne relance l'inscrit qui n'a pas payé.** Les relances visent les abonnés et les paiements CamPay échoués. Avec CamPay coupé, il n'existe aucun paiement « abandonné » à relancer.

## 2. Méthode et limites

- **Trois visiteurs simulés**, chacun dans un contexte neuf, sans accès au code ni aux rapports, mobile 375 x 812, anonymes, arrêtés à l'écran qui demande un e-mail ou un numéro :
  - Mme Tchamba, mère d'un élève de Terminale D, site local (`docs-relecture/eleve/2026-11-21-tchamba-parent-M1-M6-conversion-local.md`) ;
  - Collins, Form 5, GCE O Level, interface anglaise, site local (`…-collins-gce-ol-M7-M2-M6-conversion-local.md`) ;
  - Nadège, Terminale C, arrivée par une page d'épreuve comme depuis Google, **site public** (`…-nadege-tleC-M3-M2-M6-conversion-prod.md`, visite de 22 h 39 à 22 h 47 UTC, séance de quiz 516 et tentative d'inédite 210 à exclure des statistiques).
- **Vu par moi** en local, mobile : la page des prix en visiteur puis avec le compte de test sans abonnement, l'écran d'abonnement jusqu'au numéro à créditer (aucune déclaration envoyée), et le passage prix → connexion rejoué en navigation vierge.
- **Lu dans le code** : `LoginPage.tsx`, `SubscribePage.tsx`, `ManualPaymentPanel.tsx`, `CodeRevendeur.tsx`, `relances/services.py`, `relances/absence.py`, `relances/models.py`, `analytics/models.py`, `analytics/funnel.py`, les textes des prix et du paiement.
- **Production, en lecture publique** : `/payments/config/`, `/catalog/accueil/` (`temoignages: []`), `/subscriptions/campagne/` (aucune campagne). L'interface en ligne n'a pas encore les lots 1 à 4 du rapport 16 (textes absents du script servi).
- **Limites** :
  - **L'entonnoir réel n'a pas été lu.** La commande `rapport_entonnoir` existe, mais la lecture du serveur m'a été refusée par le garde-fou de permissions et je ne l'ai pas contournée. L'ordre des priorités ci-dessous est donc un raisonnement, pas une mesure.
  - Satisfaction simulée, réseau non bridé, pas de vrai téléphone. Trois sessions, une par persona : un indice, pas une statistique.
  - Rien vu après l'écran de connexion côté visiteur ; côté compte, rien au-delà de l'affichage du numéro. La création de compte par code (e-mail ou SMS) n'a pas été rejouée ce jour (dernier essai : 2026-10-24, abandon quand le code part vers la boîte d'un parent).
  - La base locale est en retard sur la production pour les questions à choix : le quiz d'essai vu par la mère (6 questions à rédiger) n'est pas celui de la production.

## 3. Le tunnel, marche par marche

| Marche | Ce que vit le visiteur | État | Perte probable |
|---|---|---|---|
| 1. Arrivée (accueil ou page d'épreuve) | Promesse comprise, prix dit tôt sur l'accueil, sujet lisible | Bon sur l'accueil, faible sur la page d'épreuve verrouillée | Moyenne |
| 2. Essai gratuit | Quiz sans compte, corrigés libres, mini-inédite sans compte : le pic d'humeur des trois visiteurs | Bon | Faible |
| 3. Envie de payer | Verrou sans prix ni extrait ; l'offre payante jamais montrée en entier ; « le gratuit est tellement fourni que mon père dira de s'en contenter » (Nadège) | Faible | **Forte** |
| 4. Convaincre le payeur | « Montrer à mes parents » existe, message invisible avant l'envoi ; zéro avis, aucun nom ; aide contradictoire | Faible | **Forte** |
| 5. Page des prix | Récapitulatif clair (pic d'humeur de la mère) ; 3 mois présélectionnés (6 000 FCFA) ; « ≈ 3 heures » | Correct | Moyenne |
| 6. Connexion | Bandeau rouge « Session expirée » ; titre « Connexion » ; e-mail d'abord, téléphone derrière un lien | Défaut vérifié | **Forte** |
| 7. Paiement | Transfert à la main, numéro à 2 écrans du haut, bénéficiaire au nom d'une personne, déclaration avec numéro de transaction, 3 heures | Défaut de fond | **Forte** |
| 8. Après un abandon | Aucun message | Absent | Forte |

## 4. Constats vérifiés

### 4.1 Paiement et connexion

| # | Constat | Preuve | Statut |
|---|---|---|---|
| P1 | **Paiement automatique coupé en production.** Seul reste le transfert manuel vérifié par l'équipe. | `GET https://edukora.africa/payments/config/` : `{"campay_active": false}` ; page des prix : « Activé après vérification (≈ 3 heures) » | Vérifié |
| P2 | **« Session expirée - Reconnecte-toi pour continuer. » pour un visiteur sans compte**, au clic sur « Continuer » de la page des prix. | Vu par la mère (`localhost`) et par Collins (`127.0.0.1`), rejoué par moi en navigation vierge. Cause : l'écran d'abonnement monte le champ « code revendeur », qui appelle `/revendeurs/rattachement/` sans session (`CodeRevendeur.tsx:33`) ; réponse 401, rafraîchissement refusé, bandeau, puis renvoi vers `/connexion`. Non vu par Nadège en production : à contrôler en ligne. | Vérifié en local |
| P3 | **L'écran de connexion ne dit pas qu'il crée un compte.** Titre « Connexion », « Connecte-toi en quelques secondes ». E-mail en premier, téléphone derrière le lien « Utiliser plutôt mon numéro de téléphone ». « Recevoir le code » ne dit pas par où il arrive. | Écran d'arrêt décrit à l'identique par les trois visiteurs ; `LoginPage.tsx:74-79` (e-mail par défaut pour réduire la facture de SMS) | Vérifié |
| P4 | **« Plus qu'une étape pour finaliser ton abonnement »** alors qu'il en reste cinq : code, numéro à lire, transfert, déclaration, attente. | Texte `sb.intent` ; rapport Nadège F7 | Vérifié |
| P5 | **Écran d'abonnement, mobile : le numéro à créditer est à 1 691 px du haut et « J'ai effectué le paiement » à 1 869 px** (2,3 écrans), pour une page de 3 099 px. Avant lui : la durée redemandée (déjà choisie sur les prix), le champ « Un revendeur t'a recommandé Edukora ? ». | Mesure avec le compte de test sans abonnement, 375 x 812 | Vérifié |
| P6 | **Le bénéficiaire affiché est une personne** (« Fabiola DIONDOU NANA », numéro 689492625), alors que le site signe « Kora SARL ». Le visiteur ne le voit qu'après avoir créé un compte. | Écran d'abonnement en local ; donnée de la base locale, **à contrôler en production** | Vérifié en local |
| P7 | **Deux phrases se contredisent sur le même écran** : « Vérifiée par notre équipe sous 3 heures » en haut, « Paiement sécurisé - ton abonnement s'active dès la confirmation du paiement » en bas. | Texte de l'écran | Vérifié |
| P8 | **La déclaration exige le numéro de transaction** du SMS de l'opérateur (« Ex : OM240101.1234 »), à recopier à la main. | `ManualPaymentPanel.tsx`, texte `mp.erreur_reference` | Code |
| P9 | **Trois mois présélectionnés** : 6 000 FCFA, alors que tout le site annonce 2 000. Pour le BAC C, l'accès s'arrête le 19 février, avant l'examen. Décision en attente depuis le 11 novembre. | Page des prix ; rapports Nadège F5 et Collins F15 | Vérifié |
| P10 | **Aucune relance pour un inscrit sans paiement.** Rappel de séance, absence et fin d'abonnement exigent un abonnement actif ; la relance de paiement ne lit que les transactions CamPay. Avec CamPay coupé, quelqu'un qui a vu le numéro et n'a pas payé ne reçoit rien. | `relances/services.py:243`, `:304-320` ; `relances/absence.py:164` | Code |

### 4.2 Le verrou et l'offre

| # | Constat | Preuve | Statut |
|---|---|---|---|
| O1 | **Le bloc « Débloque le corrigé complet » ne donne ni prix, ni extrait, ni lien vers les corrigés gratuits.** Le bloc d'une épreuve inédite, lui, dit « Débloquer l'accès - 2 000 FCFA · par mois ». | Nadège F1 (production), Collins F4, mère F11 | Vérifié |
| O2 | Deux boutons « S'abonner (C) » et « S'abonner (D) » pour quelqu'un qui a choisi BAC D ; le mot « cursus » dans le texte. | Mère F11 | Vérifié |
| O3 | **« Montrer à mes parents » n'ouvre que « WhatsApp » et « Copier le lien »** : le message promis n'est pas lisible avant l'envoi. | Nadège F4, Collins F5 | Vérifié (contenu du message non vu : envoi interdit au testeur) |
| O4 | **Le visiteur ne voit jamais l'offre payante en marche** : ni une séance complète, ni le rapport de fin d'une épreuve inédite de 4 heures. | Nadège, demandes 4 et 5 ; décision 2 du rapport 16, toujours ouverte | Vérifié |
| O5 | **La comparaison de la page des prix vise un « fascicule de corrigés »**, pas les PDF gratuits que l'élève a déjà. | Nadège, demande 3 | Vérifié |
| O6 | La frontière compte gratuit / abonnement est floue sur `/quiz` : « Avec un compte, chaque séance s'adapte à tes erreurs », que la page des prix range dans l'abonnement. | Nadège F10, mère (« compte veut dire payant ou non ? ») | Vérifié |
| O7 | L'examen choisi se perd : arrivée depuis une épreuve de BAC C, il faut le redire sur les prix, puis sur l'accueil, puis le bandeau « Choisis ton examen » revient sur la connexion. | Nadège F6 | Vérifié |

### 4.3 Confiance

| # | Constat | Preuve | Statut |
|---|---|---|---|
| T1 | **Zéro avis publié, aucun nom de personne, aucune adresse plus précise que « Yaoundé ».** « À propos » n'est accessible que dans un tiroir du pied de page. | `temoignages: []` en production ; mère F6, F7 | Vérifié |
| T2 | **L'aide décrit une autre offre.** « L'abonnement « Jusqu'à l'Examen »… pour un paiement unique » ; « à partir du deuxième [enfant], un prix famille s'applique » ; « Clique sur « S'abonner » » ; « Mode 1 : paiement automatique » décrit en premier. | Mère F1, F2, F3 ; Collins F2 ; Nadège F11 | Vérifié |
| T3 | **Le non-remboursement n'est dit que dans les CGU et un article d'aide**, pas dans « Avant de payer ». | Mère F14 | Vérifié |
| T4 | **Le bilan du dimanche**, seule preuve pour un parent que l'enfant travaille, n'est pas cité dans « Tu es parent ? » ; il part par e-mail seulement. | Mère F8 | Vérifié |
| T5 | Le parent est tutoyé sur tout le chemin d'achat. | Mère F9 | Vérifié |
| T6 | Chiffres différents selon la page : 1 621 épreuves (accueil), 2 591 (« À propos »). | Mère F15 | Vérifié |

### 4.4 Contenu qui casse l'élan

| # | Constat | Preuve |
|---|---|---|
| C1 | **Français sur un sujet du GCE** : « Exercice 1 (8 points) » à « Exercice 7 (20 points) » sous les en-têtes anglais de Physics O Level 2026 Paper 2 ; en-tête « Exercice 1 » sur Physics 2023 Paper 1. Seul S2 de la visite anglophone. | Collins F1 |
| C2 | **Le quiz d'essai « BAC C » est du niveau Première** et affiche « Niveau 1 · Débutant » après 5 sur 6. La mini-inédite, elle, est au niveau. | Nadège F8 (production) |
| C3 | La séance suivante proposée au visiteur du GCE est « Additional Mathematics », une matière que le site n'a jamais demandée. | Collins F6 |
| C4 | « 43ii. (ii) convergente. » dans l'exercice 3 de Maths BAC C 2024 ; un titre de cours en LaTeX brut. | Nadège F2, F3 (production) |

## 5. Actions proposées

Effort : S = une journée ou moins, M = quelques jours. Chaque action cite le constat qu'elle traite.

### Lot A : réparer les dernières marches (le tunnel de paiement)

| # | Action | Constat | Effort |
|---|---|---|---|
| A1 | **Supprimer le bandeau « Session expirée »** : ne pas monter le champ revendeur (ni l'écran d'abonnement) tant que la session n'est pas établie. | P2 | S |
| A2 | **Remettre le paiement automatique en service en production** (compte CamPay en mode réel, `CAMPAY_ACTIVE`, `CAMPAY_ENVIRONMENT` ; le correctif A1 du rapport 14 sur les paiements validés tard doit être en ligne avant). C'est l'action au plus fort effet de tout ce rapport : elle ramène le paiement à un numéro saisi et une confirmation sur le téléphone. | P1 | Hors code, puis S |
| A3 | **Tant que le transfert manuel reste : ouvrir l'accès dès la déclaration**, pour 24 heures, et le confirmer ou le retirer à la vérification. Le risque est borné (une journée d'accès) ; l'attente de 3 heures tombe au moment exact où l'élève voulait travailler. Décision de produit. | P1, P7 | M |
| A4 | **Écran d'abonnement : le numéro, le montant et le bénéficiaire au premier écran.** La durée choisie sur les prix n'est plus redemandée (une ligne « 3 mois · 6 000 FCFA · modifier »), le champ revendeur passe sous le paiement. Un bouton qui compose le transfert sur le téléphone (lien d'appel avec le code de l'opérateur ; la syntaxe exacte Orange et MTN est à vérifier auprès d'eux). | P5, P8 | S à M |
| A5 | **Bénéficiaire au nom de la société**, ou à défaut « Compte de Kora SARL, au nom de … », et **montré sur la page des prix avant la création du compte**. | P6 | S, plus une démarche opérateur |
| A6 | **Écran de connexion sur le chemin d'achat** : titre « Crée ton compte ou connecte-toi », téléphone et e-mail au même niveau (le téléphone d'abord quand on vient des prix : le payeur a un numéro Mobile Money, pas toujours une boîte qu'il relève), « Tu reçois un code par SMS ». Le coût d'un SMS est faible devant une vente à 2 000 FCFA ; garder l'e-mail d'abord partout ailleurs. Le texte « Plus qu'une étape » devient la liste vraie des étapes. | P3, P4 | S |
| A7 | **Trancher la durée présélectionnée** : 1 mois (2 000 FCFA, le prix annoncé partout) pour un premier achat, avec « jusqu'à l'examen » proposé à côté et son total. | P9 | S |
| A8 | **Relancer l'inscrit qui n'a pas payé** : un message le lendemain et un autre à J+3 à qui a ouvert l'écran d'abonnement sans paiement ni déclaration (l'évènement `abonnement_ouvert` existe), avec le lien direct vers son examen. Même règle de silence que les autres relances. | P10 | M |
| A9 | Une seule phrase sur le délai d'activation, selon le mode réellement proposé. | P7 | S |

### Lot B : faire naître l'envie au bon endroit (le verrou)

| # | Action | Constat | Effort |
|---|---|---|---|
| B1 | **Bloc cadenas des annales** : le prix (« 2 000 FCFA par mois, par Mobile Money »), le corrigé du premier exercice visible avec un fondu, et « Lis d'abord un corrigé gratuit du BAC C (25) ». Un seul bouton, pour l'examen déjà choisi. | O1, O2 | S à M (l'extrait touche à ce qui est gratuit : décision) |
| B2 | **« Montrer à mes parents » : afficher le message avant l'envoi**, et faire pointer son lien vers une page écrite pour le parent : ce que l'enfant a déjà fait (score du quiz, corrigé qu'il veut), le total jusqu'à l'examen, le bénéficiaire, le bilan du dimanche, un contact. | O3, T4 | M |
| B3 | **Un essai du payant** : une séance complète gratuite (cours, exercice d'examen, quiz), ou le rapport de fin d'une épreuve inédite montré en exemple. Tranche la décision 2 du rapport 16. Le palier semaine du rapport 14 (F7) répond au même besoin par le prix. | O4 | M, décision |
| B4 | **Comparer avec ce que l'élève a déjà** : remplacer « fascicule » par « les PDF gratuits », avec une colonne « déjà gratuit sur EduKora ». | O5 | S |
| B5 | Une ligne nette sur `/quiz` et sur la carte de résultat : compte gratuit = tes points et ton historique ; abonnement = la séance du jour, tous les corrigés, les inédites. | O6 | S |
| B6 | Déduire l'examen de la page consultée et le garder jusqu'au paiement ; retirer le bandeau « Choisis ton examen » de l'écran de connexion quand un choix d'abonnement est en cours. | O7 | S |

### Lot C : rassurer celui qui paie

| # | Action | Constat | Effort |
|---|---|---|---|
| C1 | **Publier les trois premiers avis réels** (recommandé depuis le 16 novembre, hors code) et écrire qui rédige et relit les corrigés, avec des noms. | T1 | Hors code |
| C2 | **Réécrire les articles d'aide périmés** : contenu et durée de l'abonnement, plusieurs enfants, comment payer (le mode réellement proposé en premier, le vrai nom du bouton). | T2 | S |
| C3 | Dire la règle de remboursement dans « Avant de payer ». Mieux : une garantie simple et vraie (par exemple remboursé si l'accès n'est pas activé sous 24 heures). Décision. | T3 | S |
| C4 | Annoncer le bilan du dimanche dans « Tu es parent ? » ; lancer la demande d'approbation des modèles WhatsApp (rapport 14, F3), le délai ne dépend pas de l'équipe. | T4 | S, puis hors code |
| C5 | « À propos » et « Parents » dans le menu ; vouvoyer dans le bloc parents et la page écrite pour le parent ; les mêmes chiffres partout. | T1, T5, T6 | S |

### Lot D : contenu

| # | Action | Constat | Effort |
|---|---|---|---|
| D1 | Retirer les lignes françaises des sujets du GCE (un passage du contrôle des épreuves anglophones sur « Exercice N (x points) »). | C1 | S à M |
| D2 | Quiz d'essai des Terminales : première séance au niveau de l'examen, et ne pas afficher « Débutant » après un bon score. | C2 | S à M |
| D3 | GCE : demander les matières, ou commencer par celles que presque tous présentent. | C3 | S |
| D4 | Corriger les deux défauts de la page Maths BAC C 2024. | C4 | S |

### Mesurer avant et après

- Lire l'entonnoir réel : `python manage.py rapport_entonnoir --jours 60` dans le conteneur `backend` de production, ou la page correspondante de l'admin.
- Je n'ai vu aucun évènement sur l'écran de connexion dans la liste des évènements mesurés : ajouter « code demandé », « code validé », « numéro affiché », « déclaration envoyée ». C'est la partie du tunnel où ce rapport situe la plus grosse perte, et c'est la seule qui ne se mesure pas.

## 6. Ordre proposé

1. **Cette semaine** : A1, A9, A7, C2, B4, B5, D4 (petits, sans décision), et la démarche A2 auprès de CamPay.
2. **Ensuite** : A4, A5, A6, B1, B2, A8.
3. **Sur décision** : A3 (accès dès la déclaration), B3 (essai du payant ou palier semaine), C3 (garantie).
4. **Hors code, à lancer tout de suite** : C1 (avis), C4 (WhatsApp), A5 (compte marchand).

## 7. Ce que je ne recommande pas

- **Fermer le gratuit** pour forcer l'achat : c'est lui qui a donné leur meilleur moment aux trois visiteurs. Le problème est que le payant n'est pas montré, pas que le gratuit est généreux.
- **Fausse urgence** (compte à rebours de promotion, « plus que 3 places ») : public mineur, déjà écarté au rapport 16.
- **Exiger un compte avant l'essai** : les trois personas avaient « je pars si je dois m'inscrire avant de voir » comme critère d'abandon.
- **Faux avis ou avis rédigés par l'équipe** : la page « À propos » promet le contraire.

## 7 bis. A1 codé (2026-11-21, en local, non committé, non déployé)

Décision de l'utilisateur : corriger le bandeau « Session expirée ». Frontend seul.

| Mesure, visiteur sans compte, mobile 375 x 812 | Avant | Après |
|---|---|---|
| Clic sur « Continuer » de `/tarifs` : bandeau « Session expirée » sur `/connexion` | 3 fois sur 3 | absent |
| Lien `/abonnement?cursus=…&mois=…` ouvert directement | non testé avant | renvoi vers `/connexion`, sans bandeau |
| Appel à `/revendeurs/rattachement/` sans session | 1 (réponse 401) | 0 |

- **Ce qui est en place** : l'écran d'abonnement ne monte plus rien tant que la session n'est pas établie (un indicateur de chargement pendant qu'elle se retrouve, rien pour un visiteur, que l'effet existant envoie à la connexion). Le champ revendeur et le panneau de paiement manuel, qui appellent des routes réservées aux comptes, ne partent donc plus sans session. `frontend/src/pages/SubscribePage.tsx`.
- **Tests** : trois de plus dans `SubscribePage.test.tsx` (visiteur : aucun bloc réservé monté ; session en cours : attente sans formulaire ; compte connecté : les deux blocs montés). Suite complète du frontend : 1 739 tests au vert, contrôle des types sans erreur.
- **Vérifié à l'écran** sur l'image `caddy` reconstruite : les deux parcours du visiteur ci-dessus, puis le compte de test sans abonnement, qui voit toujours le champ revendeur, le numéro à créditer et son total.
- **Non fait** : la cause plus générale reste (toute route réservée appelée sans session affiche ce bandeau, `api/client.ts:373`) ; aucune autre page ne l'a montré aux trois visiteurs. Non vérifié en production, où Nadège ne l'a pas vu.
- **Déploiement** : rebuild de `caddy` seul.

## 7 ter. Le mot du fondateur (2026-11-22, en local, non committé, non déployé)

Répond en partie au constat T1 (aucun nom de personne sur le site). Texte choisi par l'utilisateur, qui est à la fois le fondateur et le parent d'un élève de troisième :

> « J'ai créé EduKora pour mon fils, qui prépare le BEPC. Je voulais le suivre moi-même au lieu de payer un répétiteur sans savoir ce qui se faisait. Depuis trois mois, nous n'en avons plus, et je vois chaque semaine où il en est. »
> Serge G. Babounlek, parent d'un élève de 3e et fondateur d'EduKora

- **Où** : page « À propos », sous la carte de l'éditeur ; accueil du visiteur, dans le bloc « Tu es parent ? », entre les trois lignes et « Comment payer ? ». Sous le titre « Pourquoi j'ai créé EduKora », jamais dans la section des avis, qui reste réservée aux avis vérifiés. Français et anglais.
- **Fichiers** : `components/MotDuFondateur.tsx` (nouveau), `components/SectionParents.tsx`, `pages/AboutPage.tsx`, textes `fondateur.*`.
- **Tests** : trois pour le bloc (titre, signature « parent et fondateur », aucune promesse pour l'enfant d'un autre), un pour le bloc parents.
- **Mesuré à l'écran**, mobile 375 px : le bloc fait 276 px de haut, sans débordement. L'accueil du visiteur passe de 5 579 à 5 874 px (de 6,9 à 7,2 écrans) : c'est le prix de ce bloc sur une page que le rapport 16 avait raccourcie.
- **À revoir** : « Depuis trois mois » est vrai au 2026-11-22 et vieillira ; le remplacer par le mois d'arrêt du répétiteur. Ce mot ne remplace pas les trois avis extérieurs (C1), toujours à obtenir.
- **Déploiement** : rebuild de `caddy` seul.

## 7 quater. Recommandations validées, première tranche (2026-11-22, en local, non committé, non déployé)

Décision de l'utilisateur du 2026-11-22 : « je valide toutes tes autres recommandations ». Codé dans cette tranche :

| ID | Ce qui est en place | Où |
|---|---|---|
| A7 | La durée proposée d'office est **1 mois** (2 000 FCFA), sur les prix et sur l'écran d'abonnement. | `lib/tarifs.ts` |
| A9 | Une seule phrase sur le délai, celle du mode choisi : sous un transfert manuel, « s'active dès que notre équipe a vérifié ton transfert, généralement sous 3 heures ». | `SubscribePage.tsx`, textes |
| A6 | Chemin d'achat : titre « Crée ton compte ou connecte-toi », « Ton compte d'abord, le paiement juste après », le **téléphone avant l'e-mail** (seulement si un SMS peut réellement partir, et tant que la personne n'a pas choisi elle-même), et sous le bouton « Tu reçois un code par SMS (ou par e-mail), à saisir à l'écran suivant ». Partout : « Pas encore de compte ? Il se crée ici, sans mot de passe. » | `LoginPage.tsx`, `lib/paymentConfig.ts` |
| A4 | Écran d'abonnement : la durée choisie sur les prix est rappelée, pas redemandée (« Changer le nombre de mois ») ; le code revendeur passe sous le paiement ; sur un téléphone, un bouton « Composer #150# pour ouvrir Orange Money » (ou `*126#` pour MTN) ouvre le menu de l'opérateur, sans rien pré-remplir. | `SubscribePage.tsx`, `ManualPaymentPanel.tsx` |
| A5 | Le nom du bénéficiaire et l'opérateur sont dits sur la page des prix, avant le compte. Le numéro reste réservé à l'écran de paiement. | `payments/views.py` (`/payments/config/`), `PricingPage.tsx` |
| A8 | Relance par e-mail de l'inscrit qui a ouvert l'écran d'abonnement sans payer ni déclarer : un message entre 20 heures et 3 jours, un dernier entre 3 et 7 jours, deux au plus par 30 jours. Jamais si un paiement existe, si la relance de paiement abandonné s'applique, si l'examen est passé. Lien d'arrêt propre (table `RefusRelance`). | `relances/inscrit_sans_paiement.py`, migration `relances 0007` |
| B1 | Bloc cadenas des annales : le prix, « Lis d'abord un corrigé gratuit du BAC C » vers la liste filtrée, un seul bouton pour l'examen déjà choisi, « cursus » retiré du texte. | `components/BlocCorrigeVerrouille.tsx` |
| B2 | « Lire le message avant de l'envoyer » sous « Montrer à mes parents » : le texte exact qui partira. Sur les deux murs payants des corrigés. | `components/BoutonParents.tsx`, `AccesRefuse.tsx` |
| B4 | Le comparatif de la page des prix vise « un fascicule ou des PDF gratuits », et dit ce qui est gratuit aussi sur EduKora. | textes |
| B5 | Page Quiz : « un compte gratuit garde tes points et ton historique. Avec l'abonnement, chaque séance s'adapte à tes erreurs ». | textes |
| C2 | Articles d'aide réécrits (comment payer, délai d'activation, choisir son examen, contenu de l'abonnement, paiement refusé, plusieurs enfants), en français et en anglais. **Constat** : les phrases fausses vues par les visiteurs n'étaient plus dans les fichiers depuis le 13 novembre ; elles restaient en base parce que `charger_aide` n'avait pas été relancé. La production est probablement dans le même état. | `backend/aide/articles/` |
| C3 | « Puis-je être remboursé ? » dans « Avant de payer », avec la règle des conditions d'utilisation, sans rien y ajouter. | `PricingPage.tsx`, textes |
| C4 | Le bloc parents de l'accueil cite le bilan du dimanche, et ne dit plus « tu peux tout voir ». | textes |
| C5 | « À propos » dans le menu mobile du visiteur. | `Header.tsx` |
| - | « Comment ça se passe » dit l'ordre vrai : l'examen et les mois, puis le compte. L'évènement `abonnement_ouvert` porte l'examen visé. Le mot du fondateur calcule sa durée (« depuis trois mois », puis quatre...). | textes, `SubscribePage.tsx`, `MotDuFondateur.tsx` |

**Tests** : interface 1 759 tests au vert (dont une vingtaine de nouveaux), compilation de production sans erreur ; serveur : `payments` 95 tests, `relances` 160 tests (39 nouveaux), `aide` 24 tests.

**Mesuré à l'écran**, image locale reconstruite, mobile 375 x 812 :

| Mesure | Avant | Après |
|---|---|---|
| Page des prix, BEPC choisi : bouton | « Continuer · 3 mois · 6 000 FCFA » | « Continuer · 1 mois · 2 000 FCFA » |
| Écran de connexion après « Continuer » | « Connexion », e-mail d'abord, bandeau rouge | « Crée ton compte ou connecte-toi », téléphone d'abord, aucun bandeau |
| Écran d'abonnement : « Numéro à créditer » | 1 691 px du haut | 1 304 px |
| Écran d'abonnement : « J'ai effectué le paiement » | 1 869 px | 1 536 px |
| Bloc cadenas (Maths BAC C et E 2024) | ni prix ni lien | prix, lien vers les corrigés gratuits du BAC C, message aux parents lisible |

**Écarts et limites**
- **A4 : le numéro est encore à 1,6 écran du haut**, pas au premier. Il reste devant lui l'en-tête décoré, le bilan, la carte de l'offre et le choix de l'opérateur. Le remonter davantage demande de revoir l'ordre des deux cartes sur mobile.
- **A5 : le nom seulement, pas le numéro**, pour ne pas inviter à payer sans compte (donc sans pouvoir déclarer). En local les deux bénéficiaires sont des personnes : le passage à un compte au nom de la société reste une démarche.
- **A6 dépend du serveur** : le téléphone ne passe devant que si `SMS_BACKEND` n'est pas la console. À vérifier en production.
- **A8 ajoute une table** (`RefusRelance`) et une route d'arrêt, au-delà des deux types de relance prévus : le réglage « rappels » ne permettait pas de distinguer « n'a rien demandé » de « ne veut plus rien ». Aucun envoi réel n'a été fait ; aucun évènement local ne porte encore l'examen visé.
- **B1 sans extrait du corrigé** : il demande au serveur de servir une partie d'un corrigé payant, donc une décision sur ce qui est gratuit.
- **Codes des opérateurs** `#150#` et `*126#` : relevés sur des guides publics, non composés sur un téléphone.
- **Non fait dans cette tranche** : A2 et A5 (démarches), A3 (accès dès la déclaration), B3 (essai du payant), B6 (examen déduit de la page), C1 (avis), le vouvoiement du parent, les chiffres différents selon la page, tout le lot D (contenu), les évènements de mesure de l'écran de connexion.

**Déploiement** : `migrate relances` (0007, une table), rebuild de `backend`, de `relances` et de `caddy`, puis **`charger_aide`** en production après avoir vérifié qu'aucun article n'y a été retouché à la main. Avant le premier tour réel : `envoyer_relances --seulement inscrit_sans_paiement --dry-run`.

## 7 quinquies. Deuxième tranche (2026-11-22, en local, non committé, non déployé)

| ID | Ce qui est en place | Où |
|---|---|---|
| D1 | **Plus de français sur la fiche d'un sujet du GCE lu en anglais.** L'en-tête « **Exercice 1 (8 points)** » est dans les données de 2 819 exercices du GCE (base locale) ; la réécriture en « Exercise 1 (8 marks) » existait dans le lecteur, elle manquait sur la fiche de l'épreuve et dans les titres du sommaire. Les données ne sont pas touchées. | `pages/EpreuveDetailPage.tsx`, `components/EpreuveSommaire.tsx` |
| B6 | L'examen suit la personne : « Voir les prix » sous un corrigé verrouillé emmène l'examen de l'épreuve (`/tarifs?cursus=…`) ; un visiteur qui choisit son examen sur les prix n'a plus à le redire sur l'accueil ; le bandeau « Choisis ton examen » ne s'affiche plus sur l'écran de connexion (il était exclu de `/login`, pas de `/connexion`). | `PricingPage.tsx`, `BlocCorrigeVerrouille.tsx`, `BandeauCursus.tsx` |
| T5 | Le bloc parents de l'accueil vouvoie : « Vous êtes parent ? », « ce que votre enfant obtient », « Vous gardez la main ». C'est le seul bloc de l'accueil qui parle au payeur. | textes |
| Mesure | Trois évènements de plus : `connexion_code_demande` et `connexion_reussie` (méthode, et si l'on vient des prix), `paiement_numero_affiche` (opérateur). Jamais d'adresse ni de numéro. Leur écart dira combien de codes n'aboutissent pas, et combien voient le numéro sans déclarer. | `analytics/models.py`, migration `analytics 0019`, `LoginPage.tsx`, `ManualPaymentPanel.tsx` |

**Tests** : interface 1 760 tests au vert, compilation de production sans erreur ; serveur : `analytics` au vert.

**Vérifié à l'écran**, mobile, image locale reconstruite : Physics GCE O Level 2026 Paper 2 en anglais affiche « Exercise 1 (8 marks) » à « Exercise 4 (5 marks) » et plus aucun « Exercice » ; `/tarifs?cursus=20` arrive sur « BAC - Série C » et « Continuer · 1 mois · 2 000 FCFA » ; pas de bandeau d'examen sur `/connexion` ; le bloc parents vouvoie.

**Écarts et limites**
- **T5 partiel** : seul le bloc parents de l'accueil vouvoie. La page des prix, l'écran de paiement et l'aide tutoient toujours : ils sont lus par l'élève comme par le parent.
- **T6 non modifié** : « À propos » annonce plus d'épreuves que l'accueil parce qu'il compte toute la plateforme, et sa légende le dit déjà (« examens francophones et GCE confondus »). L'accueil compte l'examen du pays et de la langue.
- **D1 à l'affichage seulement**, et selon la langue de l'interface : un sujet du GCE lu avec l'interface en français garde « Exercice 1 ». Corriger les données elles-mêmes demanderait un lot de contenu vers la production.
- **Non fait** : D2 (niveau du quiz d'essai de Terminale, libellé « Débutant »), D3 (matières du GCE), D4 (deux défauts de la page Maths BAC C 2024, dans les données), A3, B3, la garantie, les démarches.

**Déploiement** (en plus de la première tranche) : migration `analytics 0019` (aucun changement de table).

## 8. Décisions à prendre

1. Accès ouvert dès la déclaration d'un transfert (A3) : oui ou non, et pour combien d'heures ?
2. Durée présélectionnée (A7) : 1 mois ou 3 mois ?
3. Téléphone d'abord sur le chemin d'achat (A6), malgré le coût des SMS ?
4. Essai du payant (B3) : une séance complète gratuite, un palier semaine, ou rien ?
5. Extrait du corrigé dans le bloc cadenas (B1) : le premier exercice, ou seulement le prix et le lien vers les corrigés gratuits ?
6. Garantie de remboursement (C3) : laquelle ?
