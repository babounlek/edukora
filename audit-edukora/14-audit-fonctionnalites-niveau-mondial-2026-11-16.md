# 14 - Audit de toutes les fonctionnalités face aux meilleures edtech mondiales

Date : lundi 2026-11-16 (J-15 avant le lancement du 1er décembre).
Question posée : que manque-t-il à EduKora, fonctionnalité par fonctionnalité, pour être au niveau de Khan Academy, Duolingo, Seneca, Save My Exams, UWorld, Brilliant, Quizlet, uLesson ?
Complète les audits 00 à 13 sans les refaire : leurs recommandations déjà codées (R1 à R23 de l'audit 10) ne sont pas reprises.

## 1. Verdict

EduKora est déjà au niveau mondial sur trois points que peu de concurrents réunissent : la profondeur du contenu d'examen (2 150 annales corrigées, 15 181 cours, 25 946 items de quiz), une séance du jour qui décide à la place de l'élève selon ce qui tombe à l'examen, et une première question posée en deux touchers sans compte.

Il n'y est pas sur six points, classés par poids :

1. **Le produit ne sait pas faire revenir ni faire renouveler.** Push éteint, aucun rappel avant la fin de l'abonnement ni après une absence, parent joint par e-mail seulement. Avec un abonnement au mois sans prélèvement, chaque mois est une nouvelle vente que rien ne prépare.
2. **Le paiement n'est pas fiable de bout en bout.** Un paiement Mobile Money validé après deux minutes n'active jamais l'accès ; aucun reçu ; le repli manuel prend jusqu'à 3 h.
3. **Le moteur d'apprentissage suit des règles, il n'apprend pas des réponses.** Difficulté fixée à la main, maîtrise en moyenne à vie, deux formats de question, aucune statistique par question.
4. **Le contenu est du texte et des formules.** 7 cours sur 15 181 contiennent une image ; ni figure dans un cours de géométrie, ni exemple dévoilé pas à pas, ni aide à la demande.
5. **Personne d'autre que l'élève ne voit le travail.** Pas de vue parent dans l'application, rien pour un enseignant, un répétiteur ou un établissement, personne ne lit une copie.
6. **L'équipe pilote à l'aveugle.** Suivi d'erreurs non branché, pas de tableau de bord, pas de quoi comparer deux variantes, tests du frontend hors intégration continue.

Vingt-trois défauts précis sont à corriger avant le lancement (section 4). Aucun ne demande plus d'une journée.

## 2. Méthode et limites

- **Six lectures parallèles du code**, une par domaine (moteur d'apprentissage, contenu, examens blancs, conversion et paiement, rétention et parents, qualité technique), chacune rendue avec ses preuves `fichier:ligne`.
- **Contrôle par moi** des constats qui portent une décision : relecture du code cité, deux requêtes de comptage en base locale (lecture seule), et un passage dans le navigateur sur le site local à 375 x 812 avec le compte de test abonné (accueil, quiz, progression, liste des cours, un cours).
- **Statut** : « Vérifié » = relu ou mesuré par moi ; « Relevé » = rapporté par une lecture, non recontrôlé ; « À vérifier en production » = dépend du serveur ou du `.env`, invisibles d'ici.
- **Limites** : rien n'a été vu en production (CamPay, SMTP, SMS, clés push, Sentry) ; base locale (356 réponses de quiz, aucune donnée d'usage réel) ; pas de mesure sur un vrai téléphone ni en 3G ; les comparaisons avec les autres produits reposent sur leur fonctionnement public connu, pas sur un essai de chacun ce jour ; les efforts (S ≤ 1 jour, M = 2 à 4 jours, L ≥ 1 semaine) sont des estimations.
- **Effets de bord** : aucun fichier du projet modifié hors ce rapport ; aucune écriture en base (le quiz en cours du compte de test a été ouvert, pas répondu).

## 3. Tableau de situation

| Domaine | Niveau | Meilleure référence | Écart principal |
|---|---|---|---|
| Contenu d'examen (annales, corrigés, cours structurés) | Au niveau | Save My Exams, Physics & Maths Tutor | Aucune date de relecture, aucun signalement sur un corrigé |
| Formats de contenu | En retard | Brilliant, Photomath, uLesson | Texte et formules seuls ; exemples affichés d'un bloc |
| Recherche | Au niveau | - | Deux moteurs différents (global, listes) |
| Séance du jour et plan de révision | Au niveau | Duolingo (parcours unique) | Validée sans rien réussir |
| Maîtrise et répétition espacée | En retard | Khan Academy, Anki (FSRS) | Moyenne à vie ; une erreur renvoie au premier palier |
| Questions et retour sur l'erreur | En retard | Seneca, Quizlet Learn, Brilliant | Deux formats ; rien par mauvais choix ; aucune statistique par question |
| Ludification | Au niveau (choix assumés) | Duolingo | Objectif du jour atteint à la 2e question |
| Examens blancs | Proche | Bluebook, UWorld | Notes comparées non protégées ; note estimée éteinte ; aucune copie lue |
| Première visite et inscription | Au niveau | Duolingo (inscription repoussée) | - |
| Paiement et abonnement | En retard | Wave, M-Pesa, uLesson | Activation non garantie, pas de reçu, un seul palier |
| Rappels et retour | En retard | Duolingo | Push éteint ; 4 types de relance en tout |
| Parents | Partiel | Seneca, Atom Learning | E-mail seul, bilan éteint par défaut, aucune vue dans l'application |
| Enseignants, établissements | Absent | Khan Academy, Google Classroom | Aucune classe, aucun devoir assigné |
| Aide à la demande | Absent | Khanmigo, Gauth | Aucun tuteur, humain ou IA |
| Mesure et expérimentation | En retard | Duolingo | Ni tableau de bord, ni test A/B, ni suivi d'erreurs |
| Poids, hors ligne, application | Correct | Khan Academy Lite, Duolingo | 334 Ko de scripts à l'accueil ; figures absentes hors ligne ; pas sur le Play Store |
| Sécurité et vie privée des mineurs | En retard | RGPD art. 8 et 17, COPPA | Ni suppression de compte, ni âge, ni consentement parental |
| Bilinguisme, accessibilité | Correct | Khan Academy | E-mails en français pour le GCE ; pas de réglage de taille du texte |

## 4. Défauts à corriger avant le 1er décembre

Tous S (une journée ou moins chacun).

**Statut au 2026-11-16 (après-midi) : sur les 23 défauts, 16 corrigés en local, 4 corrigés en partie, 1 écarté, 2 à faire sur le serveur. Rien n'est committé ni déployé.** Détail en 4.5, liste de déploiement en 4.6.

### 4.1 Argent et accès

| # | Constat | Preuve | Correctif | Statut |
|---|---|---|---|---|
| A1 | **Un paiement CamPay validé tard n'active jamais l'accès.** L'état d'une transaction n'est relu que par la page d'abonnement, qui cesse de sonder après 2 minutes. Page fermée ou validation lente : payé, pas d'accès, et la relance écrit « rien n'a été débité ». | `backend/payments/views.py:166` (seul appelant de `sync_status`) ; `frontend/src/pages/SubscribePage.tsx:47,353` | Resynchroniser les transactions en attente de moins de 48 h dans la boucle des relances, et à l'ouverture de `/abonnement` et `/mes-paiements` | Vérifié |
| A2 | **Faux signal de fraude contre les revendeurs.** L'adresse enregistrée à la déclaration de paiement est celle du conteneur Caddy, la même pour tous : dès 3 clients en 24 h, les commissions sont retenues. | `backend/payments/serializers.py:148` ; `backend/revendeurs/fraude.py:27-41` | Passer par `_client_ip` | Vérifié |
| A3 | **Plafonds par adresse calculés sur celle de Cloudflare.** Codes SMS (30/h), e-mail, comptes invités, quiz d'essai et quota PDF des visiteurs sont partagés par tous les élèves d'un même nœud : blocages collectifs possibles au pic. Un plafond global de 1 000 codes par jour coupe la connexion pour tous. | `backend/users/views.py:106-129` ; aucun `trusted_proxies` dans `docker/caddy/Caddyfile` ; `backend/edtech_cm/settings.py:135-140` | Déclarer Cloudflare en proxy de confiance, lire `CF-Connecting-IP` ; relever le plafond global | Code vérifié ; effet à vérifier en production |
| A4 | `CAMPAY_ENVIRONMENT` vaut `DEV` par défaut (serveur de démonstration). | `backend/payments/campay_client.py:14` | Contrôler le `.env` de production | À vérifier en production |
| A5 | **Ni reçu ni notification fiable.** Un succès CamPay n'envoie rien ; le SMS de validation part vers le numéro du compte, vide pour un compte e-mail ou Google ; « Mes paiements » ne liste que les déclarations manuelles. | `backend/payments/models.py:345,497` ; `frontend/src/pages/MesPaiementsPage.tsx:71` | Notifier le numéro payeur et l'e-mail ; lister les transactions CamPay | Relevé |
| A6 | Captures de SMS Mobile Money stockées en lecture publique si le stockage Spaces est actif, sans contrôle de type ni de taille. | `backend/payments/serializers.py:88` ; `settings.py:425` | Stockage privé, types et taille limités | Relevé |

### 4.2 Voir et faire revenir

| # | Constat | Preuve | Correctif | Statut |
|---|---|---|---|---|
| V1 | **Lancement sans suivi d'erreurs.** La clé Sentry du frontend n'est pas transmise au build de production ; aucun projet Sentry créé ; aucune sonde de disponibilité. | `.github/workflows/release.yml:95-100` ; `docker/caddy/Dockerfile:15` | Créer le projet, passer les deux clés, sonde externe sur `/healthz` | Vérifié (build) ; backend à vérifier en production |
| V2 | **Notifications push éteintes** : clés VAPID jamais générées (déjà signalé le 14 novembre). | `backend/relances/push.py:49-50` ; `settings.py:119-122` | `generer_cles_vapid`, puis `verifier_push --envoyer` | À faire sur le serveur |
| V3 | **L'e-mail de 17 h empêche le push du soir.** Le push écarte tout élève déjà relancé dans la journée, quel que soit le canal. | `backend/relances/push.py:147-149` | Filtrer sur le canal push | Vérifié |
| V4 | Le rappel WhatsApp ignore l'abonnement et la séance déjà faite, et s'ajoute aux autres canaux ; modèle en français en dur pour le GCE ; opt-in accepté sans numéro, retenté à chaque tour. | `backend/whatsapp/services.py:76-107` ; `backends.py:70` ; `views.py:13-16` | Mêmes filtres que l'e-mail ; langue du compte ; refuser sans numéro | Relevé |
| V5 | E-mails de rappel et bilan parent en français seulement, y compris pour les familles GCE. | `backend/relances/services.py:146` ; `bilan_parent.py:144` | Lire `User.langue` | Relevé |
| V6 | Purges des comptes invités et des codes expirés écrites, jamais planifiées. | aucune occurrence de `purger_invites` dans `docker-compose*.yml` ni `deploy/` | Les ajouter à l'ordonnanceur des relances | Relevé |

### 4.3 Justesse du quiz et des examens blancs

| # | Constat | Preuve | Correctif | Statut |
|---|---|---|---|---|
| Q1 | **La bonne réponse d'un QCM se lit avant de répondre** : la route qui révèle le corrigé ne vérifie ni le type de question ni l'existence d'une réponse. | `backend/quiz/views.py:585-599` | Refuser pour un QCM sans réponse | Vérifié |
| Q2 | **Une réponse se réécrit après correction** tant que le quiz est ouvert ; la maîtrise lit la réponse réécrite. L'interface bloque, le serveur non. | `backend/quiz/views.py:710` | Refuser une seconde réponse | Vérifié |
| Q3 | La séance du jour se clôt sans aucune réponse par deux routes. | `backend/quiz/views.py:790-797`, `:1281-1289` | Exiger au moins une réponse | Relevé |
| Q4 | **Examen blanc : durée fausse après abandon.** Une copie laissée ouverte est rendue à l'heure de la requête suivante, pas à l'échéance : 48 h affichées, mauvaise semaine du défi. | `backend/inedit/views.py:168-170` ; `backend/simulations/views.py:118` | Dater le rendu à l'échéance | Vérifié |
| Q5 | Les choix d'un QCM ne sont jamais mélangés : « refaire mes erreurs » récompense le souvenir de la lettre. | `frontend/src/pages/QuizSessionPage.tsx:543` | Mélanger à la création de l'instantané | Relevé |

### 4.4 Divers

| # | Constat | Preuve | Correctif | Statut |
|---|---|---|---|---|
| D1 | **Cache hors ligne vidé à la déconnexion seulement**, pas au changement de profil : un enfant non abonné peut relire hors ligne le corrigé gardé par son frère abonné. | `frontend/src/context/AuthContext.tsx:113` ; `frontend/vite.config.ts:84-91` | Vider le cache à chaque changement de profil | Code vérifié ; non reproduit |
| D2 | Route d'événements ouverte à tous, sans plafond : un tiers peut remplir la table. Aucune limitation de débit par défaut sur l'API. | `backend/analytics/views.py:14-37` ; `settings.py:142-153` | Plafond par adresse | Vérifié |
| D3 | Aucun en-tête de sécurité posé par le serveur web (HSTS, `nosniff`, `frame-ancestors`, `Referrer-Policy`). | `docker/caddy/Caddyfile:8-10` | Quatre lignes d'en-têtes | Vérifié (Cloudflare peut en ajouter : à vérifier) |
| D4 | Tests du frontend (1 450) et contrôle de types absents de l'intégration continue ; seuls les tests Django tournent. | `.github/workflows/release.yml:55` | Ajouter `vitest` et `tsc` au flux de publication | Vérifié |
| D5 | Un cours est lu deux fois par un élève connecté ; l'en-tête charge sur chaque page la liste complète des inédites (41 Ko décodés) pour savoir s'il en existe une. | `frontend/src/pages/CoursReaderPage.tsx:119` ; `frontend/src/components/Header.tsx:353-356` | Retirer `cours` des dépendances de l'effet ; demander une page d'un élément | Vérifié (navigateur et code) |
| D6 | La liste des cours s'ouvre, pour un abonné, sur un encart d'aide et un bandeau de présentation : premier cours à 730 px. L'audit 10 (R3) l'avait corrigé pour les quiz et les épreuves, pas ici. | Navigateur, `/cm/cours` à 375 px | Même traitement que `/quiz` | Vérifié |

### 4.5 Ce qui a été corrigé le 2026-11-16

| # | Statut | Ce qui a changé | Où |
|---|---|---|---|
| A1 | Corrigé | Les transactions CamPay en attente (de 3 minutes à 48 heures) sont relues auprès de l'agrégateur à chaque tour de l'ordonnanceur des relances, avant toute relance, et à l'ouverture de l'application pour le compte connecté (une lecture par minute au plus). L'activation passe toujours par `Transaction.sync_status`. | `backend/payments/rattrapage.py`, `relances/management/commands/planifier_relances.py`, `relances/views.py` |
| A2 | Corrigé | L'adresse retenue à la déclaration est celle du client. | `backend/payments/serializers.py` |
| A3 | Corrigé, à vérifier en production | Caddy déclare les plages de Cloudflare comme proxy de confiance, lit `CF-Connecting-IP` et transmet l'adresse du client dans un en-tête qu'il écrase à chaque requête (`X-Client-IP`). Une seule fonction la lit pour tout le projet : codes de connexion, comptes invités, quota de PDF, quiz d'essai, recherche, aide, mesure. Le plafond global de 1 000 codes par jour n'a pas été modifié (`OTP_DAILY_GLOBAL_CAP` dans le `.env` : c'est un garde-fou de coût, à régler par vous). | `docker/caddy/Caddyfile`, `backend/users/ip.py` |
| A4 | À faire sur le serveur | Contrôler `CAMPAY_ENVIRONMENT` dans le `.env` de production. | - |
| A5 | En partie | Fait : un succès CamPay envoie un reçu (SMS au numéro du compte, à défaut au numéro payeur ; e-mail en plus si l'adresse est confirmée), une seule fois ; même règle pour la déclaration, la validation et le rejet d'un paiement manuel ; une panne de SMS ne fait plus échouer la déclaration. Non fait : la liste des transactions CamPay dans « Mes paiements ». | `backend/payments/models.py` |
| A6 | En partie | Fait : la preuve doit être une image (JPG, PNG, WebP) ou un PDF de 5 Mo au plus, contrôlée sur sa signature, rangée sous un nom neutre. Non fait : le stockage privé (il demande une migration et une vue d'admin qui sert le fichier). | `backend/payments/serializers.py` |
| V1 | En partie | Fait : la clé Sentry du frontend est transmise au build (`vars.VITE_SENTRY_DSN`). À faire par vous : créer le projet Sentry, renseigner cette variable du dépôt et `SENTRY_DSN` sur le serveur, poser une sonde externe sur `/healthz`. | `.github/workflows/release.yml` |
| V2 | À faire sur le serveur | `generer_cles_vapid`, puis `verifier_push --envoyer --email …`. | - |
| V3 | Corrigé | Un seul rappel par jour, la notification d'abord : dès que le push est configuré, un élève qui a un appareil abonné n'est plus servi par l'e-mail de 17 h. | `backend/relances/services.py` |
| V4 | Corrigé | Le rappel WhatsApp exige un numéro, un abonnement actif et une séance pas déjà terminée ; il n'écrit pas à qui a déjà été prévenu dans la journée ; il part avant l'e-mail ; le modèle est demandé dans la langue du compte ; l'accord est refusé sans numéro. La version anglaise du modèle devra être approuvée par Meta comme la française. | `backend/whatsapp/services.py`, `backends.py`, `views.py` |
| V5 | Corrigé | Rappel quotidien (texte et HTML) et bilan du parent en anglais pour un compte en anglais ou un examen du GCE. | `backend/relances/services.py`, `bilan_parent.py`, gabarit `rappel_seance.html` |
| V6 | Corrigé | Les deux purges tournent chaque nuit à 3 h dans l'ordonnanceur ; celui-ci referme aussi les connexions mortes avant chaque tour. | `planifier_relances.py` |
| Q1 | Corrigé | La route du corrigé refuse un QCM sans réponse (409). | `backend/quiz/views.py` |
| Q2 | Corrigé | Une seconde réponse différente est refusée (409) ; la même réponse rejouée (réseau lent) est acceptée sans rien recompter. | `backend/quiz/views.py` |
| Q3 | Corrigé | Un quiz clos sans une seule réponse ne valide plus la séance ; « J'ai fini » est refusé quand la séance a un quiz. | `backend/quiz/views.py` |
| Q4 | Corrigé | Une copie est datée au plus tard de la fin de son temps imparti (inédites et simulations). | `backend/inedit/views.py`, `simulations/views.py` |
| Q5 | Écarté | Mélanger les choix contredirait les corrigés : sur 4 000 QCM sondés en base locale, 3 864 corrigés citent la lettre de la bonne réponse. À reprendre avec une réécriture des corrigés. | - |
| D1 | Corrigé | Le cache de lecture hors ligne est vidé dès qu'un autre enfant du compte prend la main. Contrepartie : les thèmes téléchargés par l'enfant précédent sont à retélécharger. | `frontend/src/context/AuthContext.tsx`, `lib/changerProfilActif.ts` |
| D2 | Corrigé | 120 événements par minute par compte ou par adresse ; valeurs simples de 200 caractères au plus. | `backend/analytics/views.py` |
| D3 | Corrigé | `Strict-Transport-Security` (180 jours, sans sous-domaines), `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, posés seulement quand Django ne les envoie pas déjà. | `docker/caddy/Caddyfile` |
| D4 | Corrigé | Les tests du frontend tournent avant la construction des images. | `.github/workflows/release.yml` |
| D5 | En partie | Fait : un cours n'est plus lu qu'une fois. Laissé : la liste des inédites chargée par l'en-tête partage volontairement son cache avec l'accueil d'un visiteur ; la réduire ferait deux requêtes au lieu d'une pour lui. | `frontend/src/pages/CoursReaderPage.tsx` |
| D6 | Corrigé | Pour un abonné, la liste des cours n'affiche plus le bandeau de présentation : premier lien de cours à 499 px au lieu de 730 (mesuré à 375 px). | `frontend/src/pages/CoursListPage.tsx` |

Vérifications : voir 4.7.

### 4.6 À faire au déploiement

1. Reconstruire `backend` et `caddy` ensemble (le backend lit l'en-tête `X-Client-IP` que seul le nouveau Caddyfile pose). Aucune migration.
2. Relancer le service `relances` : il porte le rattrapage des paiements et les purges.
3. Vérifier l'adresse du client derrière Cloudflare : déclarer un paiement de test, puis lire `declared_ip` dans l'admin ; elle doit être celle du téléphone, pas une adresse de Cloudflare ni `172.x`.
4. Variable du dépôt `VITE_SENTRY_DSN`, puis `SENTRY_DSN` dans le `.env` du serveur.
5. `generer_cles_vapid`, puis `verifier_push --envoyer`.
6. Contrôler `CAMPAY_ENVIRONMENT` et `OTP_DAILY_GLOBAL_CAP` dans le `.env`.
7. Le premier push vers `main` lancera les tests du frontend dans le flux de publication (environ deux minutes de plus).

### 4.7 Vérifications

- **Tests Django** des applications touchées (quiz, inedit, simulations, access, aide, recherche, revendeurs, subscriptions, users, analytics, whatsapp, payments, relances), lancés dans le conteneur backend : 2 384 tests, tous verts après adaptation de trois tests de séance qui terminaient à la main une séance avec quiz. 60 tests ajoutés pour les correctifs.
- **Tests du frontend** : 1 621 verts (trois ajoutés pour le changement d'enfant).
- **Navigateur**, site local, 375 px, compte de test abonné : un cours lu une seule fois ; liste des cours remontée ; révélation du corrigé puis réponse à une question de quiz acceptées ; en-têtes de sécurité présents sur les pages et non doublés sur l'API. Configuration Caddy validée par `caddy validate`.
- **Non vérifié** : l'adresse du client derrière Cloudflare (seulement en production), un vrai paiement CamPay rattrapé (agrégateur simulé dans les tests), l'envoi réel des SMS, e-mails et messages WhatsApp, la suite `catalog` (non touchée).

**La publication sur GitHub échouait déjà avant ces correctifs.** Le flux `release.yml` est rouge sur `main` depuis le matin du 16 novembre : 8 tests en échec, images non construites, donc rien de déployable depuis. Aucun ne vient de ce lot :

| Test | Cause apparente |
|---|---|
| `catalog.test_segments_url` (règle d'aperçu de Caddy) | Le Caddyfile compte 4 règles `path_regexp ^/(en/)?…` depuis le commit de l'accueil visiteur ; le test en attend 2 |
| `aide.tests` (robots vers l'aperçu des articles) | Même commit, même fichier |
| `catalog.test_pages_statiques` (4 tests) | Pages prérendues de l'accueil et des listes |
| `catalog.test_pdf_fin` (bloc de fin en anglais du GCE) | Bloc de fin des PDF |
| `access.test_quota` (requêtes simultanées) | À examiner |

Tant qu'ils échouent, aucun commit, celui-ci compris, ne produit d'image.

## 5. Écarts par domaine et recommandations

### 5.1 Faire revenir et faire renouveler

Duolingo doit l'essentiel de sa rétention à ses rappels (heure apprise, « série en danger », arrêt après une semaine de silence) et teste chaque message. uLesson envoie le rapport hebdomadaire au parent par SMS. EduKora a un ordonnanceur propre (un envoi tracé, unique, désabonnement signé) mais seulement quatre types de message, tous réservés aux abonnés actifs.

| # | Recommandation | Effort |
|---|---|---|
| F1 | **Relance de fin d'abonnement** à J-3, J0 et J+3, au payeur, avec lien direct `/abonnement?cursus=…&profil=…`. Premier levier de revenu récurrent. | M |
| F2 | **Relance d'absence** à J+2 et J+7 puis silence ; annonce du défi de la semaine le dimanche. | S à M |
| F3 | **WhatsApp pour le parent** : faire approuver deux modèles Meta (rappel, bilan, en français et en anglais), brancher le bilan du dimanche dessus, proposer l'envoi au numéro du payeur au moment du paiement. Le bilan est aujourd'hui éteint par défaut et exige une adresse e-mail confirmée. | M |
| F4 | **Notes d'examens blancs dans le bilan parent** : dernière note chronométrée, évolution, première cause de points perdus. | S |
| F5 | **Page « Mes enfants »** en mode parent : chaque enfant côte à côte, objectif hebdomadaire réglable. Le calcul existe (`bilan_du_profil`). | M |
| F6 | **Parrainage récompensé** : 7 jours offerts au parrain et au filleul au premier paiement du filleul. Le lien et le crédit de jours existent déjà. | M |
| F7 | **Palier semaine** (environ 600 FCFA) pour un premier achat ; le modèle `Plan` le permet. | S |
| F8 | **Invite d'installation** après le premier quiz, puis publication sur le Play Store en TWA (l'application web emballée, sans réécriture). | S puis M |

### 5.2 Moteur d'apprentissage

Khan Academy fait monter et descendre le niveau d'une compétence ; Anki (FSRS) et Duolingo estiment la mémoire par élément ; Duolingo estime ensemble le niveau de l'élève et la difficulté de chaque exercice. EduKora applique des règles lisibles et bien gardées, mais rien n'est appris des réponses.

| # | Recommandation | Effort |
|---|---|---|
| M1 | **Juger un thème à la fin du quiz, pas à chaque réponse** : 80 % et plus fait monter d'un palier, 50 à 79 % le maintient, moins le fait reculer d'un palier. Aujourd'hui une seule erreur renvoie un thème de J+35 à J+1 (`quiz/services.py:682-691`, vérifié), et la révision due passe avant tout thème neuf. | S |
| M2 | **Maîtrise sur les réponses récentes** (les 8 dernières premières tentatives), réponse avec coup de pouce comptée à moitié, rétrogradation visible. Rend crédibles les jauges et la note estimée. | M |
| M3 | **Statistiques par question**, calculées la nuit : taux de réussite, répartition des mauvais choix, temps médian ; alerte dans l'admin quand un mauvais choix bat la bonne réponse (clé fausse probable) ; difficulté mesurée dès 30 réponses. Les données sont déjà stockées et jamais agrégées. Préalable : un champ `correcte` sur `QuizAnswer`, qui allège aussi les calculs de l'accueil. | M |
| M4 | **Réponse numérique corrigée par la machine** (maths, PCT), puis texte à trous (langues). 11 067 items sur 25 946 sont des questions ouvertes que l'élève note lui-même ; l'exemple vu dans le navigateur (« énergie d'un radiateur de 1 500 W pendant 4 h ») attend un nombre. | M par format |
| M5 | **« Pourquoi ce choix est faux »** : une ligne par mauvais choix, affichée sous le choix cliqué ; contenu produit par lots. | S (code) + M (contenu) |
| M6 | Objectif du jour à 30, 50 ou 80 points (aujourd'hui 10, 20, 30 pour 10 points par QCM) ; les cartes de révision et les inédites rendues comptent pour les points et la série. | S |
| M7 | Tirage visant environ 75 % de réussite (niveau de l'élève par thème contre difficulté mesurée de la question), une fois M3 en place. | L |

### 5.3 Contenu

Save My Exams affiche l'auteur, le relecteur et la date de chaque page ; Photomath dévoile une étape à la fois ; Brilliant fait manipuler. Les cours d'EduKora ont déjà la structure nécessaire (règle, étapes d'exemple avec action, justification et résultat, erreurs classiques).

| # | Recommandation | Effort |
|---|---|---|
| C1 | **Signaler une erreur sur un corrigé ou une section de cours** (aujourd'hui possible sur les quiz seulement) et afficher « relu le… ». Boucle de qualité sur 2 150 corrigés, argument de confiance pour les parents. | M |
| C2 | **Exemples résolus pas à pas** : montrer l'action, laisser chercher, révéler le résultat. Aucun contenu à écrire, 15 181 cours concernés. | S à M |
| C3 | **Des figures dans les cours** : 7 cours sur 15 181 en contiennent une (mesuré) ; le cours « Théorème de Thalès » n'en a aucune (vu). Commencer par la géométrie, puis PCT et SVT, avec les outils de dessin déjà utilisés pour les épreuves. | L (éditorial) |
| C4 | **Figures gardées hors ligne** : le paquet d'un thème ne garde que le texte, alors que le message promet « son cours et ses exercices ». Annoncer le poids avant de télécharger. | S à M |
| C5 | Exercices d'un thème triés du plus simple au plus difficile, barème affiché (la difficulté existe et ne sert pas ici) ; filtre par année sur les épreuves. | S à M |
| C6 | Signets et notes dans le lecteur par thème (celui que la séance ouvre), reprise à l'endroit quitté, réglage de la taille du texte. | S chacun |
| C7 | PDF du corrigé pour l'abonné ; lecture d'une épreuve sans le texte en double (fait pour les cours seulement). | M ; S |
| C8 | **Pages indexables par thème d'examen** (« Théorème de Thalès au BEPC : tombé 15 fois sur 28 », cours, deux exercices, quiz). La donnée existe, la page non. | M à L |

### 5.4 Examens blancs

Bluebook (SAT numérique) garde les réponses sur l'appareil et les envoie après une coupure ; UWorld affiche un score prédit et le taux de réussite de chaque question ; Gradescope note des photos de copies sur grille. EduKora a un moteur unique de note et de rapport, un chrono serveur et un mode papier.

| # | Recommandation | Effort |
|---|---|---|
| E1 | **Protéger les notes comparées.** Tant que le chrono n'est pas lancé, la copie arrive avec ses corrigés, et le chrono peut encore démarrer ensuite (`inedit/views.py:148`, `:715`, vérifié) ; une épreuve se repasse après lecture du corrigé et la meilleure note compte. Ne servir le corrigé qu'après un choix « libre » enregistré ; ne compter au classement que la première copie chronométrée. | M |
| E2 | **Réponses gardées sur le téléphone** pendant une coupure, envoyées ensuite, avec quelques minutes de tolérance pour ce qui a été répondu avant l'échéance. Aujourd'hui la file vit en mémoire et se perd au rechargement. | M |
| E3 | **Activer la note estimée** : relecture par un enseignant (seul blocage), recalage sur les inédites chronométrées et non sur les copies libres. | S + relecture |
| E4 | **Examen blanc national mensuel** par cursus, sur un week-end, résultat le lundi : le seul moyen d'atteindre les cohortes de 20 à 30 candidats qu'exigent le percentile et la bande du défi. | M |
| E5 | **Second avis sur une copie** : photo facultative d'un exercice, corrigée en différé par une IA contre la grille de critères (présente dans 155 fichiers d'épreuve sur 165), affichée à côté de l'auto-note. À essayer d'abord sur le défi de la semaine. | L |

### 5.5 Aide à la demande, enseignants, établissements

Khanmigo guide l'élève sans donner la réponse ; Seneca et Khan Academy vendent ou offrent un accès école avec devoirs assignés. EduKora n'a rien dans ces deux cases.

| # | Recommandation | Effort |
|---|---|---|
| H1 | **« Explique-moi autrement »** après une erreur : explication produite par une IA, bornée au corrigé et au rappel de méthode de la question, avec quota quotidien et cache par question (la même explication sert à tous les élèves qui ratent la même question, donc le coût baisse avec l'usage). | L |
| H2 | **Code de classe** pour un répétiteur ou un établissement : bilan du groupe, un thème assigné, lots de mois vendus par le module revendeurs. Après le lancement. | L |

### 5.6 Piloter

| # | Recommandation | Effort |
|---|---|---|
| G1 | Envoyer chaque lundi à l'équipe l'entonnoir et la rétention J+1 / J+7 (les deux calculs existent en commande, sans envoi ni tableau de bord). | S |
| G2 | Affectation d'une variante par hachage du profil, servie dans `/auth/me` et notée dans les événements : de quoi comparer deux textes de rappel ou deux écrans de paiement. | M |
| G3 | Temps de premier affichage réels (LCP, INP, CLS) remontés dans la mesure d'usage maison. | S |
| G4 | Cinq parcours de bout en bout automatisés (quiz d'essai, connexion par code, lecture d'un corrigé, paiement déclaré, hors ligne) ; tests Django sur Postgres. | M |
| G5 | Une pile de recette sur le serveur (`ROBOTS_TAG=noindex`) pour ne plus déployer droit en production. | S |

### 5.7 Confiance et capacité

| # | Recommandation | Effort |
|---|---|---|
| T1 | **Suppression et export du compte en libre-service**, âge ou case « parent » à l'inscription, durées de conservation écrites. Aucune route de suppression n'existe (`backend/users/urls.py`, vérifié). La conformité à la loi camerounaise sur les données personnelles est à faire valider par un juriste. | M |
| T2 | Session : « déconnecter les autres appareils », alerte au-delà de N appareils (un compte à 2 000 FCFA peut servir à une classe ; le jeton vit 30 jours sans rotation). | M |
| T3 | Codes de connexion tirés avec `secrets` ; double facteur sur `/admin`. | S |
| T4 | Envoi des e-mails et SMS hors de la requête (trois envois lents suffisent à bloquer les 3 workers), test de charge avant le lancement. | M |
| T5 | Premier affichage : 334 Ko de scripts compressés en 70 fichiers à l'accueil d'un abonné, 500 Ko sur un cours, 13 et 20 appels d'API (mesuré en local). Scinder le dictionnaire de textes par page, différer KaTeX hors des lecteurs, budget de poids en intégration continue. | M à L |

## 6. Ordre proposé

- **Avant le 1er décembre** : la section 4 entière, en commençant par A1, A2, A3, V1, V2, Q1, Q2.
- **Décembre et janvier, le revenu et la confiance** : F1 à F4, F6, C1, M1, M3, E1, E3, T1, G1.
- **Février à mai, la pédagogie** : M2, M4, M5, C2, C3, C4, E2, E4, F5, F8, H1.
- **Après la session 2027** : H2, E5, M7, C8, T5, autres pays.

## 7. Ce que je ne recommande pas

- **Vidéo** : coût de production et de données hors de portée ; les exemples pas à pas et les figures donnent l'essentiel du bénéfice.
- **Forum ou entraide entre élèves** : public mineur, modération à tenir.
- **Recherche par photo d'un exercice** : coût par requête, et le corpus répond déjà à la plupart des recherches par mots.
- **Application native réécrite** : la publication de l'application web sur le Play Store suffit.
- **Ligues et classements nominatifs, vies, monnaie virtuelle** : écartés par l'audit 10, rien ne change cet avis.

## 8. Décisions à prendre

1. **IA côté élève** (H1, E5) : l'audit 10 l'écartait « dans cette phase ». Accepter un coût par usage, borné par quota et cache, à partir de février ?
2. **WhatsApp pour les parents** (F3) : lancer la demande d'approbation des modèles Meta maintenant, le délai ne dépend pas de l'équipe.
3. **Classement des examens blancs** (E1) : une seule copie chronométrée comptée par épreuve ?
4. **Offre** : palier semaine (F7) et 7 jours offerts au parrainage (F6) ?
5. **Play Store** (F8) : ouvrir un compte développeur ?
6. **Figures dans les cours** (C3) : par quelles matières commencer (proposition : géométrie du BEPC, puis PCT) ?
