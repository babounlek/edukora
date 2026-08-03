# Déploiement DigitalOcean - checklist

Runbook des étapes ponctuelles côté compte DigitalOcean/GitHub qui ne laissent
aucune trace dans le repo (dashboard, secrets). Pour le détail de chaque
mécanisme (pourquoi tel choix, comment ça marche), voir les commentaires dans
les fichiers référencés - ce document ne fait que fixer l'ordre à suivre.

## 1. Créer le Droplet

- Ubuntu 24.04 LTS, 2 vCPU / 4 Go RAM minimum (Playwright/Chromium consomme
  facilement 300-500 Mo par génération de PDF), région `fra1` (Frankfurt -
  cohérent avec les buckets Spaces créés à l'étape 3).
- Ajouter la clé SSH du compte root à la création (celle qui servira une seule
  fois, pour lancer `setup-droplet.sh`).

## 2. DNS

Pointer `edukora.africa` (enregistrement A) vers l'IP du Droplet **avant**
le premier démarrage de Caddy - le TLS automatique (Let's Encrypt) a besoin
que le DNS résolve déjà vers le Droplet pour obtenir le certificat.

## 3. Buckets DigitalOcean Spaces (deux, pas un)

Dashboard DO > Spaces > Create Bucket, région `fra1` :

- **`edukora-media`** (public) - contenu servi aux visiteurs (figures, PDF de
  sujet). Activer le CDN si voulu (`SPACES_CDN_DOMAIN` dans `.env`).
- **`edukora-backups`** (privé, ne jamais rendre public) - dumps Postgres +
  copie du média historique. Ajouter des règles de cycle de vie sur les
  préfixes `postgres/daily/`, `postgres/weekly/`, `postgres/monthly/` (ex.
  expiration à 8j / 35j / 190j).

Puis Spaces > Manage Keys > créer une clé d'accès dédiée (jamais une clé de
compte personnel) - donne `SPACES_ACCESS_KEY_ID` / `SPACES_SECRET_ACCESS_KEY`.

## 4. DO Cloud Firewall

Networking > Firewalls > Create, autoriser TCP 22/80/443 en entrée, attacher
au Droplet. Ou via `doctl` :

```bash
doctl compute firewall create --name edukora-fw \
  --inbound-rules "protocol:tcp,ports:22,address:0.0.0.0/0,address:::0 protocol:tcp,ports:80,address:0.0.0.0/0,address:::0 protocol:tcp,ports:443,address:0.0.0.0/0,address:::0" \
  --outbound-rules "protocol:tcp,ports:all,address:0.0.0.0/0,address:::0 protocol:udp,ports:all,address:0.0.0.0/0,address:::0" \
  --droplet-ids <droplet-id>
```

Complète [deploy/setup-droplet.sh](setup-droplet.sh) (pare-feu UFW côté OS),
ne le remplace pas - les deux couches sont voulues.

## 5. Provisionner le Droplet

Sur ta machine, générer une paire de clés SSH **dédiée au déploiement**
(jamais celle de ton poste perso) :

```bash
ssh-keygen -t ed25519 -C "deploy@edukora" -f ./edukora_deploy_key
```

Puis, en SSH sur le Droplet en tant que root :

1. Copier `deploy/setup-droplet.sh` sur le Droplet et l'exécuter :
   `./setup-droplet.sh deploy "$(cat edukora_deploy_key.pub)"`
2. **Dans un AUTRE terminal**, vérifier que `ssh deploy@<ip>` et `docker ps`
   fonctionnent (voir le message affiché à la fin du script).
3. Seulement après cette vérification, revenir sur la session root et lancer
   `deploy/harden-ssh.sh`.

## 6. Cloner le repo et configurer `.env`

En tant qu'utilisateur `deploy` :

```bash
git clone https://github.com/babounlek/edukora.git /srv/edukora
cd /srv/edukora
cp .env.example .env
```

Remplir `.env` avec les vraies valeurs (voir les commentaires du fichier pour
le détail de chaque variable) : `SECRET_KEY` frais, identifiants CamPay PROD,
`DB_PASSWORD`, les deux buckets Spaces + leur clé d'accès. Puis :

```bash
chmod 600 .env
```

## 7. Premier démarrage

```bash
docker compose up -d --build
docker compose logs -f
```

Vérifier que `https://edukora.africa` répond (le premier démarrage de Caddy
peut prendre quelques secondes le temps d'obtenir le certificat TLS).

## 8. Brancher GitHub Actions

Settings > Secrets and variables > Actions du repo GitHub, ajouter :
`DEPLOY_HOST`, `DEPLOY_USER` (`deploy`), `DEPLOY_SSH_KEY` (la clé **privée**
générée à l'étape 5), `DEPLOY_PATH` (`/srv/edukora`).

Les déploiements suivants se déclenchent depuis l'onglet Actions > Deploy >
Run workflow (voir [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) -
volontairement manuel, jamais automatique sur push).

## 9. Valider les sauvegardes

Ne pas attendre le premier cron (02h/03h) pour le découvrir cassé :

```bash
docker compose exec backup ./backup.sh
docker compose exec backup ./restore.sh postgres/daily/<fichier>.dump edukora_restore_test
docker compose exec db dropdb -U <DB_USER> edukora_restore_test
```

## 10. Optionnel - monitoring

Activer les alertes Droplet gratuites de DO (CPU/RAM/disque) dans le
dashboard - utile vu la consommation mémoire potentielle de Chromium.
