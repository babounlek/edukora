# Purge des données de test — Phase 1 : analyse (lecture seule)

Date : 2026-10-27. Aucune donnée modifiée, aucun fichier supprimé. Sur la production, une seule session SSH a exécuté des `count()` et des `SELECT` dans le conteneur backend, avec `SET default_transaction_read_only = on` (PostgreSQL a confirmé `on`). Les adresses e-mail de la prod ne sont citées que masquées.

Sources : introspection Django des 84 modèles locaux (`apps.get_models()`, sans écriture), lecture du code (`users`, `payments`, `subscriptions`, `revendeurs`, `access`, `quiz`, `analytics`, `inedit`, `fiches`, `synchro`, `settings.py`, `docker-compose*.yml`), comptages locaux et prod.

---

## 1. Ce qui compte pour la suite

1. **En production, aucun compte ne porte le marqueur strict de `seed_donnees_test`** (`+edukora-test-` dans l'adresse ET nom `[TEST] …`). Sur les 5 comptes prod, aucun n'est donc identifiable « avec certitude » par le mécanisme existant. Selon ta règle, rien n'est supprimable aujourd'hui sans une liste validée par toi (section 5).
2. **Les paiements de la prod ne sont pas tous des paiements de test** : 5 paiements manuels dont **4 `APPROVED`**, 4 abonnements (répartis sur les comptes 110 et 112) et 4 inscriptions inédites (leur répartition n'a pas été relevée). Ce sont peut-être de vrais paiements Mobile Money. Ils restent protégés tant que tu n'as pas dit lesquels sont de test.
3. **Le code de la prod n'est pas celui de `main`.** Le clone prod est à `f0ddc317` ; le modèle `revendeurs.CandidatureRevendeur` n'y existe pas encore (83 modèles prod contre 84 en local). La commande doit donc résoudre les modèles par `apps.get_model` avec repli, et tu devras la livrer par `docker cp` ou par un déploiement.
4. **La prod n'a aucun fichier à supprimer aujourd'hui** : 0 `ManualPayment.proof`, 0 PDF de `QuizSession`, 0 `FicheGeneree`. Les 3 seules catégories de fichiers que l'usage crée sont vides. La suppression de fichiers peut donc sortir du périmètre de la première version (section 7).
5. **`CAMPAY_ENVIRONMENT=DEV`** dans le `.env` prod, mais `Transaction` est vide : aucun paiement CamPay n'a été fait. Les 5 paiements sont tous des `ManualPayment`.

## 2. Architecture réellement présente

- **Base** : PostgreSQL (service `db`, volume `postgres_data`). **Médias** : DigitalOcean Spaces en prod (`SPACES_BUCKET` renseigné, vérifié `True` dans le conteneur prod), disque local `./media` en dev. Quatre stockages privés (`inedit_protected`, `fiches_protected`, `quiz_protected`, `cours_protected`) en plus du stockage public.
- **9 champs fichier** : `catalog.Lesson.sujet_pdf`, `catalog.Figure.image`, `payments.ManualPayment.proof`, `quiz.CompetenceItemFigure.image`, `quiz.QuizSession.sujet_pdf` et `corrige_pdf`, `inedit.EpreuveInedite.sujet_pdf`, `fiches.FicheGeneree.sujet_pdf` et `corrige_pdf`. Seuls `ManualPayment.proof`, les deux PDF de `QuizSession` et ceux de `FicheGeneree` sont produits par l'usage ; les autres sont du contenu.
- **Aucun champ « compte de test »** sur `User` ni `Profil` (champs lus : téléphone, e-mail, `email_verified`, `full_name`, `pseudo`, `is_staff`, `referral_code`, `rappels_actifs`, PIN…). Le seul marqueur est la convention de `seed_donnees_test`, qui vit dans le code de la commande, pas dans la base.
- **Signaux** : aucun `post_delete`/`pre_delete` applicatif. Seul `synchro/moteur.py` connecte temporairement `post_save`/`post_delete`/`m2m_changed` pendant l'application d'un lot, puis les déconnecte. Une purge lancée pendant un lot en cours serait vue par ce moteur : il faut tenir son verrou consultatif (`synchro.moteur.Verrou`, `pg_try_advisory_lock(VERROU_ID)`).
- **Commandes existantes** : `seed_donnees_test` (créer/lister/supprimer les comptes marqués), `purge_otp_codes` (rétention minimale pour ne pas casser les plafonds anti-pumping), `purger_telechargements` (journal de téléchargements et compteurs, 90 jours). Aucune commande de purge globale.
- **Sauvegarde** : `deploy/sync-lot.sh sauvegarde <id>` (`pg_dump --format=custom`, refus d'un dump < 1000 octets, copie Spaces `edukora-backups`, marqueur `.hors-site`) et `test-restauration <fichier.dump>` (base jetable, comparaison de compteurs, testé le 2026-10-26). Rien à écrire de ce côté.

## 3. Graphe de suppression

Ce qu'un `User.delete()` fait vraiment (relevé des `on_delete`) :

**CASCADE depuis `User`** : `Profil`, `AuthIdentity`, `Subscription`, `InscriptionInedite`, `InscriptionRepetiteur`, `AttributionRevendeur` (côté client), `FicheGeneree` (→ `FicheItem`), `whatsapp.OptIn`, `relances.RelanceEnvoyee`, `relances.AbonnementPush`, `ParrainageRecompense` (côté **parrain ET filleul**).
**CASCADE depuis `Profil`** : `LectureProgress`, `ExerciceFait`, `MarqueEtude`, `QuizSession` (→ `QuizQuestion` → `QuizAnswer`, et `GainXP` en SET_NULL), `RevisionSchedule`, `SeanceJournaliere`, `ObjectifMatiere`, `VisiteAccueil`, `GainXP`, `JourXP`, `TentativeInedite` (→ `TentativeReponse`), `SimulationEpreuve` (→ `SimulationReponse`), `Subscription`, `InscriptionInedite`, `InscriptionRepetiteur`.
**PROTECT (bloque la suppression)** : `payments.Transaction.user/profil`, `payments.ManualPayment.user/profil`, `revendeurs.Revendeur.user`, `revendeurs.CandidatureRevendeur.user`, `revendeurs.Commission.client`. Ordre obligatoire : commissions, puis versements, puis paiements, puis comptes.
**SET_NULL (survit, anonymisé)** : `AnalyticsEvent.user`, `User.referred_by`, `ManualPayment.reviewed_by`, `Versement.paye_par`, `Transaction.subscription`.
**`figer_puis_detacher`** (propre au projet) : `QuizQuestion.question` et `.competence_item` — l'historique d'un élève survit à la suppression d'un contenu, ce qui est sans effet pour une purge d'utilisateurs.

Pièges relevés :
- **`ParrainageRecompense` en CASCADE sur `filleul`** : supprimer un filleul de test **supprime aussi le crédit accordé à son parrain**, même si le parrain est un vrai utilisateur. Il faut le détecter avant suppression et le traiter comme ambigu.
- **`AnalyticsEvent`** : l'événement reste avec `user = NULL` après suppression du compte. Les événements de test qui n'étaient pas rattachés à un compte (visiteurs anonymes) ne sont pas attribuables.
- **Quotas** : `CompteurQuota.cle` et `TelechargementPdf.demandeur` valent `p:<profil_id>`, `c:<user_id>`, `v:<visiteur>` ou `r:<réseau>`. Les clés `p:`/`c:` d'un compte de test sont attribuables ; `v:` et `r:` ne le sont pas.
- **`recherche.RechercheSansResultat`** et **`TermeRecherche`** : agrégats sans lien utilisateur, donc non attribuables à un compte de test.
- **`admin.LogEntry`** (journal d'admin) : 0 en prod, 3 en local ; c'est de la traçabilité, protégé.
- **`sessions.Session`** : 3 en prod ; la clé de l'utilisateur est dans les données encodées, pas dans une colonne.
- **Contenu** : aucun compteur d'usage dans `CompetenceItem` (vérifié) ; supprimer des utilisateurs ne change pas les contenus. Je n'ai pas vérifié ce point pour les autres modèles pédagogiques.

## 4. Classification des catégories

« Prod » = volumétrie au 2026-10-27 ; « Local » = base de ce poste.

| Catégorie | Modèles | Nature | Prod | Local | Identification fiable aujourd'hui | Proposition |
|---|---|---|---|---|---|---|
| Comptes de test marqués | `User`, `Profil`, `AuthIdentity` | test | **0** | 5 | oui, marqueur strict | supprimable (liste explicite) |
| Comptes de test non marqués | idem | **à valider** | 0 certain, 4 comptes non classés | 4 (110, 114, 115, 121) | non | seulement par liste validée |
| Abonnements et inscriptions d'un compte de test | `Subscription`, `InscriptionInedite`, `InscriptionRepetiteur` | dépend du compte | 4 + 4 + 0 | 7 + 6 + 0 | via le compte | suit le compte validé (cascade) |
| Paiements d'un compte de test | `ManualPayment`, `Transaction`, `Commission` | **sensible** | 5 (dont 4 APPROVED) + 0 + 0 | 4 + 0 + 0 | via le compte, mais comptable | **décision à prendre** (section 6) |
| Progression et quiz de profils de test | `LectureProgress`, `ExerciceFait`, `MarqueEtude`, `QuizSession/Question/Answer`, `RevisionSchedule`, `SeanceJournaliere`, `GainXP`, `JourXP`, `VisiteAccueil`, `ObjectifMatiere`, `TentativeInedite/Reponse`, `SimulationEpreuve/Reponse` | test | lectures 33, exercices faits 9, marques 4 ; 29 sessions de quiz, 62 réponses ; 51 XP, 51 séances, 9 jours XP, 5 visites ; 13 tentatives inédites ; 5 simulations | lectures 39, exercices faits 9, marques 7 ; 40 sessions de quiz, 218 questions, 86 réponses ; 69 XP, 49 séances, 11 jours XP, 8 visites ; 15 tentatives inédites ; 4 simulations | via le profil | suit le compte (cascade) |
| Analytics d'un compte de test | `AnalyticsEvent` | opérationnel | 1420 au total | 1727 | via `user_id` seulement | optionnel : supprimer ceux du compte plutôt que l'anonymiser |
| Quotas et téléchargements d'un compte de test | `CompteurQuota`, `TelechargementPdf` | opérationnel | 140 + 8 | 7 + 4 | clés `p:`/`c:` seulement | optionnel ; l'existant `purger_telechargements` couvre la rétention |
| Notifications et relances d'un compte de test | `RelanceEnvoyee`, `AbonnementPush`, `OptIn` | opérationnel | 2 + 0 + 1 | 0 | via le compte | suit le compte |
| Sessions | `sessions.Session` | opérationnel | 3 | 3 | via décodage | sessions expirées ou des comptes supprimés seulement |
| OTP | `users.OTPCode` | opérationnel (anti-abus) | 26 | 26 | non (clé = destination) | **laisser à `purge_otp_codes`** |
| Recherches sans résultat | `RechercheSansResultat` | opérationnel | 19 | 6 | non | exclu par défaut |
| Journal de synchro | `LotSynchro`, `OperationSynchro`, `ContenuSynchro` | traçabilité | 24 lots | 0 | — | protégé |
| Journal d'admin | `admin.LogEntry` | traçabilité | 0 | 3 | — | protégé |
| Réglages | `ReglagesTelechargement`, `MobileMoneyAccount`, `Plan` | production | 1, 2, 46 | idem | — | protégé |
| Revendeurs | `Revendeur`, `AttributionRevendeur`, `Commission`, `Versement`, `CandidatureRevendeur` | opérationnel / comptable | 0 (prod) | 1 revendeur | — | protégé, et à surveiller côté PROTECT |
| Contenu pédagogique | `Subject`, `Lesson`, `Cours`, `Exercise`, `Question`, `Figure`, `Tag`, `CompetenceItem(+Figure)`, `Blueprint`, `EpreuveInedite` et enfants, `Module`, `Savoir`, `Country`, `Filiere`, `Series`, `Cursus`, `ExamSession`, `ExamenLabel`, `Temoignage`, index de recherche | **pédagogique** | 2081 leçons, 14260 cours, 9235 exercices, 20542 items, 165 inédites | idem | — | **jamais touché** |
| Comptes admin réels | `User` avec `is_staff`/`is_superuser` | production | 1 (id 1) | 1 | — | protégé |

## 5. Comptes : état réel

**Production (5)** — à classer par toi, je ne tranche pas :

| id | adresse | nom | rôle | inscrit | profils | abonnements | paiements manuels | identités |
|---|---|---|---|---|---|---|---|---|
| 1 | bab***@yahoo.fr | BABOUNLEK Serge Guyguy | staff + superuser | 2026-07-14 | 4 | 0 | 0 | email, phone |
| 110 | mbo***@gmail.com | Serge Guyguy BABOUNLEK | — | 2026-10-12 | 4 | 3 | 3 | email, google |
| 112 | fab***@gmail.com | Fabiola Diondou Nana | — | 2026-10-21 | 1 | 1 | 2 | google |
| 113 | mfe***@gmail.com | (vide) | — | 2026-10-23 | 1 | 0 | 0 | email |
| 114 | ths***@gmail.com | Thierry NGOMPE SAHA | — | 2026-10-23 | 1 | 0 | 0 | google |

Aucun n'a le marqueur. Le compte 1 est l'administrateur réel : intouchable. Le 110 porte l'adresse que le dépôt associe à ton compte personnel de recette. Le 112 a 2 paiements, le 114 un nom complet : ce sont peut-être de vraies personnes. Je n'en classe aucun.

**Local (10)** : 1 admin ; 110 (ton adresse Google, supprimée le 12/10 puis recréée) ; 114 et 115 (`test-eleve@example.test`, `test-nonabonne@example.test`, créés le 24/10, sans le marqueur parce qu'ils viennent d'un autre outil) ; 116 à 120 (marqueur strict, créés le 24/10 par le seed) ; 121 (téléphone seul, 0 profil, 26/10). Le seed ne couvre donc que 5 des 9 comptes non administrateurs : **les comptes `*@example.test` et le 121 échappent à la règle actuelle**.

## 6. Décisions à prendre avant la phase 2

1. **Quels comptes de la prod sont des comptes de test ?** (110, 112, 113, 114). Pour chacun : test, réel, ou à conserver. Tant que tu ne réponds pas, la liste de purge prod est vide.
2. **Paiements et abonnements d'un compte de test** : supprimer (cohérent avec `CAMPAY_ENVIRONMENT=DEV`) ou conserver comme trace comptable ? Les 4 paiements `APPROVED` sont la question : si l'un a réellement été encaissé, il ne doit pas disparaître.
3. **Marqueur pour l'avenir** : veux-tu un champ explicite (par exemple `Profil`/`User.compte_test`, avec migration) ou une table d'exceptions validées ? Un champ rend la purge reproductible mais demande une migration prod ; une liste d'ids validée ne touche pas au schéma.
4. **Parrainages** : si un compte de test est le filleul d'un vrai parrain, bloquer ou supprimer le crédit ?
5. **Analytics, quotas, sessions** : supprimer ceux des comptes purgés, ou laisser l'anonymisation `SET_NULL` ? (aucun risque ni pour l'un ni pour l'autre ; le second est plus simple).
6. **Fichiers** : accepter de ne rien supprimer sur Spaces dans la première version (prod = 0 fichier d'usage) et de seulement les lister ?
7. **Date de la purge** : après tes dernières recettes et avant le 1er décembre, avec une seconde simulation juste avant (des vrais utilisateurs peuvent s'inscrire entre-temps).

## 7. Stratégie proposée pour la phase 2

- **Liste blanche explicite** : la commande ne supprime que les `User` dont l'id figure dans un fichier de périmètre que tu valides (JSON : id + adresse + motif), plus, comme garde supplémentaire, elle refuse tout id d'admin et tout id dont les paiements `APPROVED` n'ont pas été explicitement acceptés. Le marqueur du seed reste un second moyen d'ajouter un compte au périmètre, jamais le seul.
- **Réutiliser** `seed_donnees_test` (nom `[TEST]`, garde `ALLOW_TEST_DATA`) et `sync-lot.sh` (sauvegarde + `test-restauration`) ; la nouvelle commande ne fait que la purge.
- **Ordre de suppression** dans une transaction unique : `Commission` → `Versement` (si besoin) → `ManualPayment` → `Transaction` → événements/quotas des ids ciblés → `User` (la cascade fait le reste). Un `ParrainageRecompense` d'un vrai parrain ou un `Revendeur` lié fait échouer la simulation (code 2), pas la suppression.
- **Simulation par défaut**, jeton de confirmation lié au périmètre et aux comptages, verrou `synchro` + vérification qu'aucun lot n'est en cours, code de sortie 0/1/2.
- **Compatibilité prod** : `apps.get_model` avec repli pour les modèles absents (`CandidatureRevendeur`), livraison par `docker cp` sans rebuild (backend sans bind mount, à vérifier que le fichier arrivé est le bon).
- **Sauvegarde exigée par la commande** : dump `.dump` récent avec `.hors-site` et `test-restauration` réussie ; sinon refus.
- **Pas de suppression de fichiers en v1** ; le rapport liste les fichiers d'usage rattachés aux lignes supprimées (0 aujourd'hui).
- **Tests** : modèles et dépendances réels du dépôt (PostgreSQL du conteneur), comme énoncé dans le prompt.

## 8. Ce que je n'ai pas vérifié

- Le rapport entre les comptes prod et des personnes réelles (je n'ai pas la liste de tes testeurs).
- Le contenu des 3 sessions prod et des événements d'analytics (pas décodés, pas lus).
- Les conséquences de la suppression pour les modèles pédagogiques autres que `CompetenceItem` (absence de compteurs d'usage) : un `grep` des champs numériques de `Lesson`/`Cours`/`Exercise` reste à faire en phase 2.
- L'état du bucket Spaces (contenu, versionnage) : je n'ai pas interrogé le stockage.
- Si `f0ddc317` est le bon commit prod : la note du 26/10 donnait `1313fc6c` ; le clone a avancé depuis, je n'ai relevé que le résultat de `git rev-parse`.
- Que `./media` local contient des fichiers d'usage : non regardé (hors périmètre prod).
