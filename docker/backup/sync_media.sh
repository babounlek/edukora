#!/bin/bash
set -euo pipefail

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

: "${SPACES_BACKUP_BUCKET:?}"

# copy, jamais sync : Spaces recoit aussi en continu les NOUVEAUX fichiers ecrits
# directement par Django (voir edtech_cm/settings.py, STORAGES) - un rclone sync
# depuis /media (qui ne contient que l'ancien contenu) supprimerait ces fichiers
# recents cote Spaces a chaque run, puisqu'ils sont absents de la source locale.
# --update ignore les fichiers deja presents et inchanges, pour des runs rapides
# apres le premier.
log "Copie de /media (contenu historique) vers spaces:${SPACES_BACKUP_BUCKET}..."
rclone copy /media "spaces:${SPACES_BACKUP_BUCKET}" --update

log "Sync media OK"
