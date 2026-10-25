# Tunnel de mise en ligne - manuel d'exploitation

Complète [README.md](README.md) (provisionnement initial du Droplet, DNS, Spaces, pare-feu) : ce
document décrit la vie **après** la première mise en ligne. Quatre canaux, chacun avec son
déclencheur, ses garde-fous et son retour arrière.

| Canal | Quoi | Déclencheur | Script serveur |
|---|---|---|---|
| Application | backend, frontend, sauvegarde | Actions > **Deploy** | `deploy/deploy.sh` |
| Contenu | cours, épreuves, inédites, quiz, programme (créations, depuis git) | Actions > **Contenu** | `deploy/contenu.sh` |
| **Contenu par lots** | exercices, cours, quiz : créations **et corrections** sans rebuild | `scripts/edukora.ps1 publish` (poste Windows) | `deploy/sync-lot.sh` + `manage.py sync_contenu` |
| Données de test | comptes fictifs de recette | SSH, une commande | `manage.py seed_donnees_test` |
| Retour arrière | images précédentes | SSH (ou **Deploy** avec un ancien SHA) | `deploy/rollback.sh` |

Le canal **Contenu par lots** (corrections de contenu, retraits, sauvegarde vérifiée, reprise après coupure) est décrit dans
[README-SYNC-CONTENU.md](README-SYNC-CONTENU.md). Il partage le verrou `/srv/edukora-lots/.sync.lock` avec `deploy.sh` et `contenu.sh`.

Le build des images est automatique à chaque push sur `main` (**Release**, tests inclus) ; aucun
déploiement ne part tout seul (CamPay fait transiter de vrais paiements).

## Principes

1. **La base ne se copie jamais, elle se met à jour par l'application.** Le schéma par les
   migrations Django ; le contenu par les commandes d'ingestion rejouées sur des JSON versionnés ;
   les corrections de contenu par des commandes de correctif versionnées. Un seul chargement de
   départ fait exception (voir plus bas).
2. **Aucune modification manuelle de la base, ni locale ni en prod.** Toute campagne qui change des
   données existantes (fusion de Tags, rattachements, dépublications...) doit devenir une commande
   idempotente committée, sinon elle n'atteindra jamais la prod. Modèle :
   `quiz/management/commands/appliquer_correctifs_quiz_2026_10_04.py`.
3. **Migrations rétro-compatibles.** Elles tournent *avant* la bascule et un retour arrière
   d'images ne les défait pas : ajouter (colonne nullable ou avec défaut) d'abord, renommer ou
   supprimer dans un déploiement ultérieur.
4. **Une image = un SHA.** Déployer ou revenir en arrière, c'est choisir un SHA ; rien n'est
   reconstruit sur le serveur.
5. **Application d'abord, contenu ensuite.** Le contenu déployé est celui du commit déployé.

## Réglages à faire une fois

- GitHub > Settings > Actions > General > Workflow permissions : **Read and write** (pousser sur GHCR).
- GitHub > Settings > Secrets and variables > Actions > **Variables** : `SITE_DOMAIN`,
  `VITE_GOOGLE_CLIENT_ID` (public par nature).
- GitHub > Settings > Environments > `production` : **Required reviewers** = vous (approbation
  explicite avant chaque déploiement ou mise à jour de contenu).
- Sur le Droplet : `docker login ghcr.io` avec un jeton personnel limité à `read:packages` (les
  images contiennent le code, elles restent privées).
- Sur le Droplet : le clone doit rester **propre** (aucun fichier suivi modifié), sinon
  `git checkout` refusera de changer de version. Le `.env` est ignoré par git, il n'est pas concerné.
- Rotation des secrets (CamPay PROD, SMTP, Spaces, LMT, WhatsApp) : à faire avant le lancement
  public, notamment si ces valeurs ont transité par un fichier suivi par git ou une conversation.

## Routine : déployer l'application

1. Fusionner dans `main` ; attendre **Release** vert (tests + 3 images).
2. Actions > **Deploy** > Run workflow (branche `main`, `sha` vide = tête de `main`) > approuver.
3. Le workflow vérifie que les images de ce SHA existent, puis `deploy.sh` : contrôles (DEBUG
   interdit, 5 Go libres) → sauvegarde Postgres → pull → migrations → bascule → **/healthz doit
   répondre avec le SHA déployé** → sinon retour arrière automatique des images.
4. Contrôle final depuis l'extérieur (même vérification, via HTTPS public).

## Routine : mettre à jour le contenu

1. En local, comme aujourd'hui : ingestion + `scripts/tunnel_validation.sh` (porte de rendu KaTeX
   comprise) ; committer les JSON ; pousser ; déployer l'application si besoin.
2. Actions > **Contenu** > Run workflow, **simulation cochée** (défaut) : relire le plan (dossiers,
   fichiers) et la liste des fichiers *modifiés*.
3. Relancer **simulation décochée**. Ordre : programme → corrections → inédites → quiz →
   `valider_ingestion --since` → `indexer_recherche`. Le point de départ n'avance que si tout est vert.

**Limite à connaître** : l'ingestion ignore ce qui existe déjà. Un JSON *modifié* après coup
n'est pas appliqué ; le rapport le signale. Utiliser l'action admin « Réingérer depuis le fichier
JSON » (exercices) ou une commande de correctif versionnée. Les épreuves inédites arrivent en
**brouillon** : la publication reste un geste humain dans l'admin.

## Données de test

```bash
# Le drapeau est passé à la commande, jamais écrit dans le .env : rien ne reste activé après coup.
docker compose exec -e ALLOW_TEST_DATA=1 backend python manage.py seed_donnees_test --email-base vous@gmail.com
```

Crée 5 comptes marqués (`vous+edukora-test-<rôle>@gmail.com`, nom `[TEST] ...`) : élève abonné,
élève sans abonnement, élève expiré, parent à deux profils, paiement manuel en attente. Ils se
connectent par **code e-mail** (le code arrive dans votre boîte). Aucun téléphone n'est posé : aucun
SMS LMT ni message WhatsApp ne peut partir ; `rappels_actifs` et `email_verified` sont faux, donc
toutes les relances les ignorent ; aucun appel CamPay. Idempotent.

- **Ne validez pas** le paiement en attente (l'admin enverrait un SMS à un numéro vide) : rejetez-le.
- Le compte administrateur n'est pas créé par le seed : `manage.py createsuperuser`.
- Avant le lancement public : `exec -e ALLOW_TEST_DATA=1 backend python manage.py seed_donnees_test
  --purge` (liste seulement), puis `--purge --oui`. La purge ne touche que les comptes portant les
  deux marques (adresse `+edukora-test-` ET nom `[TEST] `).

## Si ça tourne mal

| Symptôme | Action |
|---|---|
| `deploy.sh` échoue à la vérification de santé | Retour arrière automatique des images. Lire `docker compose logs backend caddy`. |
| Mauvaise version en ligne, site fonctionnel | `deploy/rollback.sh` (ou **Deploy** avec l'ancien SHA). |
| Migration destructive ou données abîmées | Restaurer la sauvegarde prise juste avant (`docker compose exec backup ./restore.sh postgres/<classe>/<fichier>.dump <base>`), **après** avoir arrêté `backend` et `relances`, puis redéployer l'ancien SHA avec `--sans-migration`. Tester d'abord sur une base jetable (étape 9 du README). |
| Contenu ingéré mais `valider_ingestion` en échec | Le point de départ n'a pas avancé : corriger les JSON, repousser, relancer **Contenu** (l'ingestion ignore ce qui existe, seul le reste est repris). |
| Historique des opérations | `.deploy/historique.log` sur le serveur. |

## Chargement de départ du contenu (une seule fois)

Les JSON seuls ne redonnent pas la base locale (fusions de Tags, rattachements et dépublications
faites hors ingestion). Le contenu de départ est donc posé **une fois** par restauration des seules
tables de contenu (jamais les utilisateurs, paiements, abonnements ni l'activité des élèves), puis
tout passe par l'application. La méthode exacte dépend de l'état du serveur : lancer d'abord
`deploy/diagnostic-serveur.sh` (lecture seule, sortie sans donnée personnelle ni secret).
