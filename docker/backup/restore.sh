#!/bin/bash
set -euo pipefail

# Usage : docker compose exec backup ./restore.sh postgres/daily/edukora_XXXX.dump nom_db_cible
# TARGET_DB doit toujours differer de $DB_NAME : un drill de restauration ne doit
# jamais pouvoir ecraser la base de production en cours d'utilisation.

REMOTE_OBJECT="${1:?usage: restore.sh <postgres/tier/file.dump> <target-db-name>}"
TARGET_DB="${2:?usage: restore.sh <postgres/tier/file.dump> <target-db-name>}"

: "${DB_HOST:?}" "${DB_PORT:?}" "${DB_USER:?}" "${DB_NAME:?}" "${DB_PASSWORD:?}"
: "${SPACES_BACKUP_BUCKET:?}"

if [ "$TARGET_DB" = "$DB_NAME" ]; then
    echo "Refus : TARGET_DB (${TARGET_DB}) est identique a \$DB_NAME - choisis un autre nom de base pour ce test de restauration." >&2
    exit 1
fi

TMP_FILE="/tmp/restore_$$.dump"
trap 'rm -f "$TMP_FILE"' EXIT

echo "Telechargement de spaces:${SPACES_BACKUP_BUCKET}/${REMOTE_OBJECT}..."
rclone copyto "spaces:${SPACES_BACKUP_BUCKET}/${REMOTE_OBJECT}" "$TMP_FILE"

export PGPASSWORD="$DB_PASSWORD"

echo "Creation de la base ${TARGET_DB}..."
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TARGET_DB"

echo "Restauration dans ${TARGET_DB}..."
pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TARGET_DB" \
    --no-owner --no-privileges "$TMP_FILE"

echo "Restauration OK dans ${TARGET_DB}. Verifie les donnees, puis supprime avec :"
echo "  docker compose exec db dropdb -U ${DB_USER} ${TARGET_DB}"
