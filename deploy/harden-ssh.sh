#!/bin/bash
set -euo pipefail

# A executer SEPAREMENT de setup-droplet.sh, uniquement APRES avoir verifie dans un
# AUTRE terminal que la connexion SSH par cle avec le nouvel utilisateur fonctionne
# (voir le message affiche a la fin de setup-droplet.sh). Desactive la connexion
# root et l'authentification par mot de passe - un Droplet mal configure a partir
# d'ici ne se recupere plus que via la console web DigitalOcean (recovery), plus du
# tout en SSH classique. A executer en session interactive, jamais via un script
# non surveille : la confirmation ci-dessous est un vrai garde-fou, pas une
# formalite.

if [ "$(id -u)" -ne 0 ]; then
    echo "A executer en root." >&2
    exit 1
fi

read -r -p "As-tu deja verifie, dans un AUTRE terminal, que la connexion SSH avec le nouvel utilisateur fonctionne ? (oui/non) " confirmation
if [ "$confirmation" != "oui" ]; then
    echo "Annule - verifie d'abord cet acces avant de relancer ce script." >&2
    exit 1
fi

SSHD_CONFIG="/etc/ssh/sshd_config"
cp "$SSHD_CONFIG" "${SSHD_CONFIG}.bak.$(date +%Y%m%d%H%M%S)"

sed -i \
    -e 's/^#\?PermitRootLogin.*/PermitRootLogin no/' \
    -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
    -e 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' \
    "$SSHD_CONFIG"

# Verifie la syntaxe AVANT de redemarrer le service - une config invalide ne doit
# jamais atteindre un sshd deja actif, sous peine de perdre tout acces SSH.
sshd -t

systemctl restart ssh

echo "SSH durci : connexion root et par mot de passe desactivees. Sauvegarde : ${SSHD_CONFIG}.bak.*"
