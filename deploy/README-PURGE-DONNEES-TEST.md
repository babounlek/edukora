# Purger les comptes de test avant le lancement

Spécification : [SPEC-PURGE-DONNEES-TEST.md](SPEC-PURGE-DONNEES-TEST.md) ; analyse : [ANALYSE-PURGE-DONNEES-TEST.md](ANALYSE-PURGE-DONNEES-TEST.md).
Rien de ce document ne supprime quoi que ce soit tout seul : seul `purge-executer`, après une confirmation tapée, supprime.

## Ce qui a été décidé (et ce qui diffère de la spécification)

- **Paiements d'un compte purgé** : supprimés avec le compte, **mais** seulement si le fichier de périmètre l'active (`"paiements": true`), et les paiements `APPROVED`/`SUCCESSFUL` exigent en plus `"paiements_approuves": true`. Sans ces options, la purge est refusée.
- **Simulation** : elle exécute les vraies suppressions dans une transaction PostgreSQL qu'elle annule toujours (comptes exacts, cascades comprises). Rien n'est persisté, mais des verrous de ligne existent le temps du calcul (quelques secondes). La spécification disait « aucune écriture » : en pratique, aucune écriture *persistante*.
- **Tests** : les tests Django du dépôt tournent sur SQLite en mémoire (`settings.py`, `"test" in sys.argv`), pas sur PostgreSQL comme la spécification le disait. Les cascades `PROTECT` sont gérées par Django et se comportent pareil ; le verrou consultatif PostgreSQL n'existe pas en SQLite et est testé avec un faux curseur. La commande a en plus été simulée sur la base PostgreSQL locale (annulée, 10 comptes avant et après).
- **Sauvegarde** : `purge-test.sh` écrit lui-même la preuve `.restauration-ok` après un `test-restauration` réussi. Ajouter 4 tables au contrôle de `sync-lot.sh test-restauration` est dans le dépôt mais n'agit en production qu'après un Deploy ; avec l'ancienne version, le contrôle porte sur les 5 tables de contenu seulement.
- **Livraison** : `purge-installer` envoie les 3 fichiers par SSH dans `/srv/edukora-lots/purge/` puis les copie dans le conteneur (`docker compose cp`), SHA-256 vérifié. Rien n'est écrit dans le clone `/srv/edukora` (un fichier modifié empêcherait `git checkout --detach` du Deploy). La copie disparaît à la prochaine reconstruction du conteneur ; une version déployée de `main` contiendra la commande.

## Le fichier de périmètre

Liste blanche validée par vous. Pour le produire (en local d'abord, ou sur le serveur) :

```bash
python manage.py purger_donnees_test perimetre --ids 110,112,113,114 > perimetre.json
```

(`--marque` propose les comptes au marqueur strict de `seed_donnees_test`.) La commande n'inclut jamais un administrateur. **Relisez, complétez `motif`, `valide_par`, `date`, retirez les comptes qui ne sont pas à purger**, puis activez les options voulues :

```json
"options": {"paiements": true, "paiements_approuves": true, "quotas": true, "analytics": true, "sessions": true}
```

Chaque compte porte l'empreinte SHA-256 de son e-mail (ou téléphone) : si l'id ne correspond plus à la même personne, la purge est refusée. Ne committez pas ce fichier (il contient des identifiants d'utilisateurs).

## Procédure en production, dans l'ordre

Toutes les commandes se lancent depuis votre poste Windows, dans `D:\edukora`.

```powershell
# 0. Vérifier l'accès au serveur (lecture seule)
.\scripts\edukora.ps1 doctor -Distant
```
```powershell
# 1. Envoyer la commande dans le conteneur (aucune donnée touchée)
.\scripts\edukora.ps1 purge-installer
```
```powershell
# 2. Simuler : affiche les comptes et le nombre de lignes par table, un jeton, ou les REFUS
.\scripts\edukora.ps1 purge-simuler -Perimetre D:\edukora\perimetre.json
```
Relisez : le nombre de comptes, les lignes par modèle, les fichiers d'usage listés, les refus et avertissements. Un refus (revendeur, parrainage avec un compte hors périmètre, paiement non activé…) se corrige dans le périmètre, pas en forçant.

```powershell
# 3. Sauvegarde PostgreSQL vérifiée + copie hors site + restauration de test
.\scripts\edukora.ps1 purge-sauvegarder
```
Notez le nom `avant-AAAAMMJJ-HHMMSS-xxxxxxxx.dump`.

```powershell
# 4. Exécuter (ré-affiche la simulation, compare le jeton, demande de taper « PURGER <n> COMPTES »)
.\scripts\edukora.ps1 purge-executer -Perimetre D:\edukora\perimetre.json -Jeton <jeton de l'étape 2> -Sauvegarde <dump de l'étape 3>
```
```powershell
# 5. Vérifier
.\scripts\edukora.ps1 purge-verifier -Perimetre D:\edukora\perimetre.json
.\scripts\edukora.ps1 purge-simuler  -Perimetre D:\edukora\perimetre.json   # doit montrer 0 compte présent
```

Gardes (aucune n'est contournable par une option) : sauvegarde de moins de 24 h, copie hors site, restauration testée, jeton identique à la simulation, `ALLOW_TEST_DATA=1` et `PURGE_SAUVEGARDE_VERIFIEE` posés par le script serveur (jamais dans le `.env`), verrou partagé avec les lots et les déploiements (`75` si pris).

Codes de sortie du poste : 0 ok · 1 échec (la transaction est annulée côté serveur) · 2 refus ou usage · 3 indéterminé (connexion coupée pendant l'exécution : lancer `purge-verifier`, ne jamais relancer à l'aveugle) · 5 confirmation manquante.

## Restauration en cas de problème

Quand : un compte purgé par erreur, ou un doute sur la base après la purge. Contre-indication : tout ce que de vrais utilisateurs ont écrit **après** la sauvegarde est perdu par la restauration. Si la purge a eu lieu en moins de quelques minutes après la sauvegarde, la perte est faible ; sinon, évaluer d'abord quels comptes réels se sont inscrits depuis.

Sur le serveur (`ssh deploy@157.245.140.254`, dans `/srv/edukora`). Si `.deploy/current_tag` existe, ajouter `-f docker-compose.yml -f docker-compose.prod.yml` et exporter `IMAGE_TAG` comme le fait `sync-lot.sh` ; sinon `docker compose` seul.

```bash
# 1. Arrêter les écritures
docker compose stop backend caddy
# 2. Restaurer la sauvegarde nommée par purge-sauvegarder
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' < /srv/edukora-lots/sauvegardes/avant-AAAAMMJJ-HHMMSS-xxxxxxxx.dump
# 3. Redémarrer
docker compose start backend caddy
```

Cette séquence (restauration `--clean --if-exists` d'un dump de 143 Mo dans une base jetable, après suppression d'un compte) a été **rejouée en local le 2026-10-27** : le compte supprimé est revenu, 10 comptes avant et après. Elle n'a pas été exécutée sur le serveur. La copie hors site est dans le bucket `edukora-backups` (Spaces).

## Tests

```bash
docker cp backend/users/purge_test.py edukora-backend-1:/app/users/purge_test.py
docker cp backend/users/test_purge_test.py edukora-backend-1:/app/users/test_purge_test.py
docker cp backend/users/management/commands/purger_donnees_test.py edukora-backend-1:/app/users/management/commands/purger_donnees_test.py
docker exec edukora-backend-1 python manage.py test users.test_purge_test users.test_seed_donnees_test --noinput
docker cp deploy edukora-backend-1:/tmp/deploy-tests && docker exec edukora-backend-1 bash /tmp/deploy-tests/tests/test-purge-test.sh
```

## Après la purge

- Comptes administrateurs et contenu pédagogique : jamais touchés (comptages comparés avant/après dans la transaction ; un écart l'annule).
- Fichiers : jamais supprimés. Ceux qui étaient rattachés aux lignes supprimées sont listés dans le rapport ; il n'y en a aucun en production aujourd'hui (aucune preuve de paiement, aucun PDF de quiz ni de fiche).
- `OTPCode`, journal de synchro, journal d'admin, réglages, revendeurs : hors périmètre (voir la spécification, section 4).
