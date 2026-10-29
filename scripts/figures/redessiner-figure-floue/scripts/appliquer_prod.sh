#!/usr/bin/env bash
# Applique une figure redessinée en PRODUCTION. À lancer depuis Git Bash, SEULEMENT sur demande explicite de l'utilisateur.
#
#   appliquer_prod.sh <id_figure> <fichier_png> <nom_du_fichier_webp> [simulation|appliquer]
#
# Exemple : appliquer_prod.sh 2189 figure_finale.png probatoire-a-abi-svt-2024-officiel-cameroun_exercice_2_fig_1.webp simulation
#
# 1. vérifie en prod que la figure <id> existe et porte bien ce nom de fichier ;
# 2. dépose le PNG et lance appliquer_figures_propres (simulation, ou --appliquer) dans le conteneur backend ;
# 3. (appliquer seulement) remplace AUSSI le fichier du dossier /srv/edukora/media, celui que Caddy sert, après sauvegarde ;
# 4. contrôle l'URL publique. Le cache Cloudflare (max-age=14400) reste à purger à la main par l'utilisateur.
set -euo pipefail

ID="${1:?id de Figure}"
PNG="${2:?chemin du PNG}"
NOM="${3:?nom du fichier .webp (sans dossier)}"
MODE="${4:-simulation}"
HOTE="157.245.140.254"
SSH_OPTS=(-i "$HOME/.ssh/edukora_lots_ed25519" -o IdentitiesOnly=yes -o "UserKnownHostsFile=$HOME/.ssh/edukora_known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes -o ConnectTimeout=15)
ssh_prod() { ssh "${SSH_OPTS[@]}" "deploy@$HOTE" "$@"; }

echo "== 1. Vérification de la figure $ID en prod"
echo "from catalog.models import Figure
f = Figure.objects.get(pk=$ID)
print('FIG', f.id, f.image.name, '|', f.exercise.lesson.title[:70])" |
  ssh_prod 'cd /srv/edukora && docker compose exec -T backend python manage.py shell' 2>&1 | grep '^FIG' | tee /tmp/fig_prod_verif.txt
grep -q "$NOM" /tmp/fig_prod_verif.txt || { echo "ERREUR : la figure $ID de prod ne porte pas le nom $NOM. Arrêt."; exit 1; }

echo "== 2. Dépôt du PNG et commande ($MODE)"
printf '{"id": %s, "statut": "redessinee"}\n' "$ID" > /tmp/rapport_prod.jsonl
cp "$PNG" "/tmp/$ID.png"
scp "${SSH_OPTS[@]}" "/tmp/$ID.png" /tmp/rapport_prod.jsonl "deploy@$HOTE:/tmp/"
OPT=""; [ "$MODE" = "appliquer" ] && OPT="--appliquer"
ssh_prod "cd /srv/edukora && C=\$(docker compose ps -q backend) && docker exec \$C mkdir -p /tmp/lot_flou && docker cp /tmp/$ID.png \$C:/tmp/lot_flou/$ID.png && docker cp /tmp/rapport_prod.jsonl \$C:/tmp/lot_flou/rapport.jsonl && docker compose exec -T backend python manage.py appliquer_figures_propres --dossier /tmp/lot_flou --statuts redessinee --ids $ID $OPT; rm -f /tmp/$ID.png /tmp/rapport_prod.jsonl" 2>&1 | grep -v 'level=warning\|^(0'

if [ "$MODE" != "appliquer" ]; then echo "Simulation terminée. Relancer avec 'appliquer' pour écrire."; exit 0; fi

echo "== 3. Fichier servi par Caddy (/srv/edukora/media)"
# Pays : ce script suppose figures/cm/ ; pour un autre pays, adapter le chemin (celui de image.name, vu à l'étape 1).
# Le fichier copié est celui que Django vient d'écrire sur Spaces : octet pour octet ce que la base référence.
ssh_prod "cd /srv/edukora/media \
  && cp --update=none figures/cm/$NOM figures_avant_filigrane/${ID}_$NOM \
  && curl -s -m 30 -o /tmp/nouvelle.webp https://edukora-media.sfo3.digitaloceanspaces.com/figures/cm/$NOM \
  && ls -l /tmp/nouvelle.webp figures/cm/$NOM \
  && cp /tmp/nouvelle.webp figures/cm/$NOM \
  && rm /tmp/nouvelle.webp \
  && ls -l figures/cm/$NOM"

echo "== 4. URL publique (avec contournement du cache)"
curl -s -m 25 -L -o /dev/null -w "public : %{http_code} %{size_download} octets\n" "https://edukora.africa/media/figures/cm/$NOM?x=$RANDOM"
echo "Reste à faire par l'utilisateur : purger l'URL dans Cloudflare (Caching > Purge Cache > Custom Purge)."
