#!/bin/bash
set -euo pipefail

# Provisionnement initial d'un Droplet Ubuntu fraichement cree - a executer UNE
# SEULE FOIS en SSH en tant que root (cle SSH du compte root fournie a la creation
# du Droplet, ou console DO).
#
# Usage :
#   ./setup-droplet.sh <utilisateur> "<cle-ssh-publique>"
#   ex.  ./setup-droplet.sh deploy "ssh-ed25519 AAAA... deploy@github-actions"
#
# La cle publique passee ici doit correspondre a la cle privee stockee dans le
# secret GitHub Actions DEPLOY_SSH_KEY (voir .github/workflows/deploy.yml) - c'est
# la meme paire de cles, dediee au deploiement, jamais celle d'un poste personnel.
#
# N'active PAS le durcissement SSH (desactivation de root/mot de passe) - voir
# harden-ssh.sh, un script SEPARE a executer seulement apres avoir verifie que la
# connexion SSH avec ce nouvel utilisateur fonctionne. Les deux etapes sont
# volontairement separees : tout regrouper en un seul script ferait courir le
# risque de couper l'acces root avant meme d'avoir confirme que le nouvel
# utilisateur peut se connecter.

if [ "$(id -u)" -ne 0 ]; then
    echo "A executer en root." >&2
    exit 1
fi

DEPLOY_USER="${1:?usage: setup-droplet.sh <utilisateur> \"<cle-ssh-publique>\"}"
SSH_PUBLIC_KEY="${2:?usage: setup-droplet.sh <utilisateur> \"<cle-ssh-publique>\"}"

echo "==> Mise a jour du systeme..."
apt-get update -y
apt-get upgrade -y

echo "==> Utilisateur ${DEPLOY_USER}..."
if ! id "$DEPLOY_USER" >/dev/null 2>&1; then
    adduser --disabled-password --gecos "" "$DEPLOY_USER"
    usermod -aG sudo "$DEPLOY_USER"
fi

install -d -m 700 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/home/${DEPLOY_USER}/.ssh"
echo "$SSH_PUBLIC_KEY" > "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chmod 600 "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chown "$DEPLOY_USER:$DEPLOY_USER" "/home/${DEPLOY_USER}/.ssh/authorized_keys"

echo "==> Docker..."
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
usermod -aG docker "$DEPLOY_USER"

echo "==> Pare-feu (UFW) - seuls SSH/HTTP/HTTPS sont exposes, tout le reste refuse..."
# Aucun autre service du docker-compose ne publie de port sur l'hote (voir
# docker-compose.yml : seul "caddy" a un bloc ports:) - db/backend/backup/frontend
# ne sont deja joignables que via le reseau Docker interne, jamais depuis l'exterieur,
# meme sans ce pare-feu. UFW est une couche de defense supplementaire, pas la seule.
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> fail2ban (protection brute-force SSH)..."
apt-get install -y fail2ban
systemctl enable --now fail2ban

echo "==> Mises a jour de securite automatiques..."
apt-get install -y unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades

cat <<EOF

==================================================================
 Etape suivante - NE FERME PAS cette session root maintenant :

 1. Dans un AUTRE terminal, verifie la connexion avec le nouvel
    utilisateur :
      ssh ${DEPLOY_USER}@<ip-du-droplet>

 2. Une fois connecte, verifie que Docker fonctionne pour lui :
      docker ps
    (une reconnexion peut etre necessaire pour que l'appartenance
    au groupe docker prenne effet)

 3. Seulement une fois ces deux points confirmes, revient sur CETTE
    session root et lance :
      ./harden-ssh.sh
==================================================================
EOF
