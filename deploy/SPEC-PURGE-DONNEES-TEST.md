# Purge des données de test — Phase 2 : spécification (aucun code écrit)

Date : 2026-10-27. Suite de [ANALYSE-PURGE-DONNEES-TEST.md](ANALYSE-PURGE-DONNEES-TEST.md). Ce document ne modifie rien. Il part de **réponses par défaut, les plus prudentes**, aux décisions de la section 6 de l'analyse ; chacune est à confirmer ou à changer (section 9).

## 1. Hypothèses retenues (à confirmer)

| # | Décision | Valeur retenue par défaut |
|---|---|---|
| D1 | Comptes prod 110, 112, 113, 114 | **non classés → périmètre prod vide** tant que tu n'as pas fourni la liste |
| D2 | Paiements/abonnements d'un compte de test | **conservés par défaut** ; supprimés seulement si tu coches la catégorie ET nommes les paiements (par id) |
| D3 | Marqueur | **fichier de périmètre** (liste d'ids validée), aucune migration ; le marqueur du seed ne sert qu'à *pré-remplir* ce fichier |
| D4 | Filleul de test d'un vrai parrain | **bloque** (code de sortie 2), jamais de suppression silencieuse du crédit |
| D5 | Analytics, quotas, sessions | **anonymisation existante conservée** pour les analytics (`SET_NULL`) ; quotas/téléchargements de ces comptes supprimables en option ; sessions des comptes supprimés supprimées |
| D6 | Fichiers | **jamais supprimés en v1** ; listés dans le rapport |
| D7 | Date | après tes dernières recettes, nouvelle simulation le jour même |

## 2. Nom, emplacement, conventions

Le dépôt nomme ses commandes en français ou en « purge_* » (`purger_telechargements`, `purge_otp_codes`, `seed_donnees_test`). Proposition : **`purger_donnees_test`**, dans `backend/users/management/commands/` (à côté de `seed_donnees_test`, dont elle partage la logique de marqueur), avec la logique dans `backend/users/purge_test.py` (importable par les tests, sans I/O de console). Elle suit le style de `sync_contenu` : sous-commandes, sortie JSON sur une ligne avec `--json`, codes de sortie documentés.

Sous-commandes :
- `purger_donnees_test perimetre --email-base … [--ids …] > perimetre.json` : propose un fichier de périmètre. Pré-remplit avec les comptes au marqueur strict (lecture seule) ; ne retient **jamais** un compte à partir de son ancienneté, de son nom ou de son adresse seuls.
- `purger_donnees_test simuler --perimetre perimetre.json` : rapport + **jeton**. Aucune écriture.
- `purger_donnees_test executer --perimetre perimetre.json --jeton … --sauvegarde avant-….dump --confirme-production`.
- `purger_donnees_test verifier --perimetre perimetre.json` : après la purge, doit trouver 0 ligne ciblée et les mêmes contenus.

## 3. Fichier de périmètre

JSON validé à la main, committé ou non (je recommande de ne **pas** le committer : il contient des adresses). Pour chaque compte :

```json
{
  "version": 1,
  "comptes": [
    {"user_id": 114, "email_attendu": "ths***@gmail.com", "motif": "compte de recette de <nom>", "valide_par": "<nom>", "date": "2026-11-xx"}
  ],
  "paiements_a_supprimer": [{"type": "manual", "id": 12, "motif": "…"}],
  "options": {"quotas": true, "analytics": false, "sessions": true}
}
```

Règles de garde, vérifiées à chaque exécution, avant toute écriture :
1. L'`user_id` existe **et** son e-mail correspond à `email_attendu` (masqué par les mêmes 3 premiers caractères et le domaine, puis comparé en entier côté serveur à une empreinte stockée dans le fichier) : un id réaffecté ou une faute de frappe est refusé.
2. Aucun compte avec `is_staff` ou `is_superuser`, jamais, même listé.
3. Un compte qui a des paiements, des transactions, des commissions, un revendeur, une candidature ou un parrainage : chacun doit apparaître explicitement dans `paiements_a_supprimer` ou le compte est **refusé** (sortie 2). Un paiement `APPROVED` ou un crédit de parrainage lié à un compte hors périmètre ajoute un avertissement bloquant.
4. Un compte absent du fichier n'est jamais touché, quel que soit son marqueur.

## 4. Catégories de suppression (toutes désactivées sauf « comptes »)

Les catégories se choisissent avec `--categories` (liste séparée par des virgules, vide par défaut = rien). Seule la catégorie `comptes` est requise pour que les autres aient un sens.

| Catégorie | Cible | Mécanisme | Par défaut |
|---|---|---|---|
| `comptes` | `User`, `Profil`, `AuthIdentity` des ids du périmètre ; en cascade abonnements, inscriptions, progression, quiz, tentatives inédites, simulations, XP, séances, relances, push, opt-in WhatsApp | `User.delete()` dans la transaction, après les suppressions explicites ci-dessous | active si listée |
| `paiements` | `ManualPayment`, `Transaction`, `Commission`/`Versement` exactement nommés dans `paiements_a_supprimer` | suppression explicite avant le compte (PROTECT) | **inactive** |
| `quotas` | `CompteurQuota` et `TelechargementPdf` dont la clé est `p:<profil_id>` ou `c:<user_id>` d'un compte ciblé | filtre exact sur ces clés | inactive |
| `analytics` | `AnalyticsEvent` des comptes ciblés (avant suppression du compte, sinon `user` devient `NULL` et on ne les retrouve plus) | filtre `user_id` | inactive |
| `sessions` | `django_session` dont la donnée décodée contient `_auth_user_id` d'un compte ciblé | décodage avec `SessionStore`, suppression par clé | active si `comptes` |

Jamais proposés, quelle que soit l'option : contenu pédagogique, plans, index de recherche, `Plan`, `MobileMoneyAccount`, `ReglagesTelechargement`, `LogEntry`, `LotSynchro`/`OperationSynchro`/`ContenuSynchro`, `Revendeur`/`Versement` hors périmètre, `RechercheSansResultat`, `OTPCode` (voir `purge_otp_codes`), comptes admin.

## 5. Ordre des opérations et sûreté

Une seule transaction `atomic()` pour la base :

1. **Verrous** : verrou consultatif `pg_try_advisory_lock(VERROU_ID = 727368)` (celui de `synchro.moteur`) — si pris, sortie 2 « lot en cours » ; le script serveur tient en plus le `flock` de `$LOTS/.sync.lock` (partagé avec `deploy.sh` et `sync-lot.sh`).
2. **Recalcul du périmètre** et comparaison avec le jeton. Le jeton est un SHA-256 de : version, ids, e-mails attendus, comptages par table concernée, `max(updated)` des paiements ciblés, liste des paiements nommés, options. Si quelque chose a changé depuis la simulation (nouveau paiement, nouvelle tentative), il devient invalide : sortie 2, relancer la simulation.
3. **Garde production** : l'option `--confirme-production` exige aussi la variable `ALLOW_TEST_DATA=1` passée à `docker compose exec -e`, jamais écrite dans le `.env`, comme `seed_donnees_test`. En dehors de DEBUG, sans ces deux éléments : refus.
4. **Garde sauvegarde** (voir §6) vérifiée avant le premier `DELETE`.
5. Suppressions dans cet ordre : `Commission` → `Versement` nommés → `ManualPayment`, `Transaction` nommés → `AnalyticsEvent` ciblés (si option) → `CompteurQuota`, `TelechargementPdf` (si option) → `Session` ciblées → `User.delete()`.
6. **Contrôles internes avant commit** : le nombre de lignes supprimées par modèle est comparé à ce que la simulation avait annoncé ; tout écart (même de +1) ou toute `ProtectedError`/`IntegrityError` provoque un `rollback` complet et un code 1. Aucun `try/except` qui poursuit : une erreur n'est jamais « partielle ».
7. Après commit seulement : recomptage. Si le recomptage ne vaut pas « cibles à 0, contenu inchangé », sortie 1 avec le détail (la base est déjà commitée : le plan de retour est la restauration du §7).
8. **Interruption** : transaction annulée par le SGBD ; une relance repart d'une simulation propre. La commande est **idempotente** : un compte déjà supprimé est signalé « absent » (compté en « ignorés »), pas en erreur.

Rapport par catégorie : ciblés / supprimés / conservés / ignorés / erreurs, avec les ids. Sortie console + `--json`. Codes : **0** terminé et vérifié, **1** échec (rien d'écrit si la transaction a échoué), **2** garde refusée ou ambiguïté (aucune suppression), **3** indéterminé (connexion coupée pendant le commit : à vérifier par `verifier`).

## 6. Sauvegarde et restauration

Réutilisation de `deploy/sync-lot.sh` :

1. `sync-lot.sh sauvegarde <batch_id>` : `pg_dump --format=custom`, taille minimale, `pg_restore --list`, présence des tables de contenu, copie hors site (Spaces `edukora-backups`), marqueur `.hors-site`. `<batch_id>` : `AAAAMMJJ-HHMMSS-<8 hex>` (format imposé par le script).
2. `sync-lot.sh test-restauration avant-<batch_id>.dump` : restaure dans `edukora_restore_test` et compare cinq tables de contenu. **Limite à corriger en phase 3** : il ne contrôle ni `users_user` ni les tables de paiement/progression, qui sont justement celles que la purge modifie. Je propose d'ajouter `users_user`, `users_profil`, `payments_manualpayment`, `subscriptions_subscription` à la liste (sans toucher au comportement actuel : ajout de lignes dans le tableau `tables`).
3. `executer` **refuse** de commencer si : le nom de dump n'est pas dans `/srv/edukora-lots/sauvegardes/`, le marqueur `.hors-site` est absent, le dump a plus de 24 h, ou la dernière `test-restauration` n'est pas enregistrée comme réussie pour ce dump (un fichier de preuve `<dump>.restauration-ok` écrit par le script serveur après la comparaison, jamais par la commande Django).

Restauration en cas de problème (à documenter et à tester sur base jetable en phase 3) :

```bash
# 1. arrêter les écritures
docker compose stop backend caddy
# 2. restaurer en remplaçant le contenu (le dump est en format custom, sans propriétaire)
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' < /srv/edukora-lots/sauvegardes/avant-<batch_id>.dump
# 3. redémarrer et contrôler
docker compose start backend caddy
```
La commande exacte (avec `IMAGE_TAG` et les `-f`) sera donnée avec le fichier compose réel de la prod ; je ne l'exécute pas avant la phase 3, sur base jetable seulement.

## 7. Livraison sans reconstruction d'image

Le conteneur backend n'a pas de bind mount de code. Deux voies, à choisir :
- **`docker cp`** des deux fichiers (`purge_test.py`, `purger_donnees_test.py`) dans `/app/users/…` puis `docker compose exec backend python manage.py check` ; nécessite de contrôler la bonne version (SHA-256 du fichier avant/après copie, comparé à celui du poste). Le fichier copié disparaît à la prochaine reconstruction : acceptable, la commande est éphémère.
- **Déploiement normal** (Release + Deploy) : plus propre mais plus long, et la prod est déjà décalée de `main` (voir analyse §1). Je recommande `docker cp` pour la purge, car les deux fichiers n'importent que des modèles existants.

Compatibilité avec la prod actuelle (`f0ddc317`) : la commande ne doit pas importer `revendeurs.CandidatureRevendeur` en tête de module ; elle résout les modèles optionnels par `apps.get_model(...)` dans un `try/except LookupError` et note « modèle absent » dans le rapport.

## 8. Script de poste et script serveur

- **`deploy/purge-test.sh`** (serveur, même style que `sync-lot.sh` : liste blanche d'arguments, JSON sur une ligne, `flock` partagé) : sous-commandes `sauvegarde` (appelle `sync-lot.sh sauvegarde`), `tester-restauration` (appelle `sync-lot.sh test-restauration` et écrit le fichier de preuve), `simuler`, `executer`, `verifier`. `executer` ne se lance jamais seul : il exige le jeton, le dump et la phrase de confirmation passés en arguments.
- **`scripts/edukora.ps1`** : nouvelles commandes `purge-simuler`, `purge-sauvegarder`, `purge-executer`, `purge-verifier` (ajoutées au `ValidateSet`). `purge-executer` affiche le rapport de simulation, puis **demande de taper** `PURGER <n> COMPTES` ; sans réponse exacte, code 5 (« validation humaine manquante », déjà défini dans le script). Aucune suppression automatique, aucune option `-Oui` ou `-Force`.
- Réutilisation de la clé SSH `edukora_lots_ed25519`, de `edukora_known_hosts` et de la routine « envoyer un script par stdin » déjà au point (astuce PS 5.1 : retirer les `\r`, `exec -T` sans `<`).

## 9. Plan de tests (phase 3), mappé sur ta liste

| Exigence | Test |
|---|---|
| Simulation sans modification | empreinte (comptage + somme `md5` des ids) de chaque table avant/après, y compris `django_session` ; échec si la simulation écrit une ligne |
| Suppression correcte des données identifiées | compte du périmètre supprimé avec profils, abonnements, progression, quiz, XP, séances, relances ; autres comptes identiques |
| Contenus conservés | comptages et empreintes de `Lesson`, `Cours`, `Exercise`, `Question`, `CompetenceItem`, `EpreuveInedite`, `Plan`, `Tag` identiques |
| Admins et vrais utilisateurs protégés | un `is_superuser` dans le périmètre est refusé (code 2) ; un compte hors périmètre au marqueur strict n'est pas touché |
| Fichiers encore utilisés conservés | stockage `InMemoryStorage` : aucun fichier supprimé, la commande les liste seulement |
| Erreur ⇒ pas de purge partielle | un `Commission` ou `ParrainageRecompense` non listé provoque `ProtectedError`/refus ; exception injectée entre deux suppressions : base strictement inchangée |
| Seconde exécution sans effet | relancer avec le même périmètre renvoie 0 supprimé, aucune autre table modifiée |
| Jeton invalide | un paiement ajouté entre simulation et exécution refuse l'exécution |
| Parrainage | filleul de test d'un vrai parrain : code 2, crédit du parrain intact |
| Paiements | catégorie `paiements` inactive par défaut : paiements du compte conservés et le compte refusé ; avec `paiements_a_supprimer` : seuls les ids nommés partent |
| Modèle absent | `CandidatureRevendeur` indisponible simulé : la commande tourne et le signale |
| Configuration Docker | `docker compose exec backend python manage.py test users.test_purge_test` sur l'image du dépôt, et une simulation sur la copie restaurée de la prod (base jetable), jamais sur la prod |

Tests dans `backend/users/test_purge_test.py`, base PostgreSQL du conteneur (cascades `PROTECT` réelles, `SQLite` ne les rendrait pas fidèlement). Les échecs préexistants du dépôt (`payments`, `vapid`) seront relevés avant, pour ne pas les confondre avec les miens.

## 10. Ce que je n'écrirai pas

- Aucune détection automatique « ce compte a l'air d'un test ».
- Aucun nettoyage du stockage Spaces.
- Aucune migration, aucun champ ajouté en v1 (D3).
- Aucune modification de `seed_donnees_test` (sauf si tu veux qu'il écrive le fichier de périmètre, à voir en phase 3).

## 11. Risques résiduels

- Un compte classé « test » par erreur : la garde d'e-mail attendu et ta validation sont les seuls rempart ; la restauration du dump annule, au prix de toute écriture faite depuis la sauvegarde. D'où : sauvegarde < 24 h et exécution dans une fenêtre sans trafic.
- Écritures de vrais utilisateurs entre la sauvegarde et la purge, perdues si on restaure : à signaler dans la procédure (rejouer ou accepter la perte).
- Le jeton protège contre un changement des cibles, pas contre une écriture sur un compte hors périmètre.
- `test-restauration` ne vérifie que ce qu'on lui fait vérifier : limite corrigée en §6 (ajout de tables), mais une restauration complète à blanc reste le seul vrai test.
- Le code de la prod n'est pas celui de `main` : la commande est testée sur le schéma de `main`, l'écart (`CandidatureRevendeur`) est géré par repli, mais un autre écart ne serait vu qu'à la simulation prod.

## 12. Décisions à confirmer pour passer en phase 3

1. D1 à D7 ci-dessus : acceptées telles quelles, ou lesquelles changer ?
2. Livraison par `docker cp` (recommandée) ou par déploiement.
3. Ajout de 4 tables au contrôle de `test-restauration` (OK ?).
4. Quels comptes de la prod mettre dans le premier fichier de périmètre (peut être vide au départ : la commande sera alors testée en simulation pure).
