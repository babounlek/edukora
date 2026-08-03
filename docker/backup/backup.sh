#!/bin/bash
set -euo pipefail

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

fail() {
    log "ERROR: $*"
    if [ -n "${HEALTHCHECK_URL:-}" ]; then
        wget -q -T 10 -O /dev/null "${HEALTHCHECK_URL}/fail" 2>/dev/null || true
    fi
    exit 1
}

: "${DB_HOST:?}" "${DB_PORT:?}" "${DB_USER:?}" "${DB_NAME:?}" "${DB_PASSWORD:?}"
: "${SPACES_BACKUP_BUCKET:?}"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DAY_OF_MONTH="$(date -u +%d)"
DAY_OF_WEEK="$(date -u +%u)"

# Classe la sauvegarde du jour (daily/weekly/monthly) - la retention de chaque
# classe est geree par une regle de cycle de vie sur le bucket Spaces, jamais par
# ce script, pour ne pas dependre d'un etat local perdu si le Droplet meurt.
if [ "$DAY_OF_MONTH" = "01" ]; then
    TIER="monthly"
elif [ "$DAY_OF_WEEK" = "7" ]; then
    TIER="weekly"
else
    TIER="daily"
fi

DUMP_NAME="edukora_${TIMESTAMP}.dump"
LOCAL_PATH="/tmp/${DUMP_NAME}"
REMOTE_PATH="spaces:${SPACES_BACKUP_BUCKET}/postgres/${TIER}/${DUMP_NAME}"

cleanup() { rm -f "$LOCAL_PATH"; }
trap cleanup EXIT

log "Waiting for ${DB_HOST}:${DB_PORT}..."
export PGPASSWORD="$DB_PASSWORD"
for i in $(seq 1 30); do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        break
    fi
    if [ "$i" = "30" ]; then
        fail "database not reachable after 60s"
    fi
    sleep 2
done

log "Dumping ${DB_NAME} (tier=${TIER})..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=custom --compress=5 --no-owner --no-privileges \
    -f "$LOCAL_PATH" \
    || fail "pg_dump failed"

SIZE=$(stat -c%s "$LOCAL_PATH")
if [ "$SIZE" -lt 1000 ]; then
    fail "dump suspiciously small (${SIZE} bytes), aborting upload"
fi

log "Uploading ${DUMP_NAME} to Spaces (${SIZE} bytes, tier=${TIER})..."
rclone copyto "$LOCAL_PATH" "$REMOTE_PATH" || fail "upload to Spaces failed"

log "Backup OK: ${TIER}/${DUMP_NAME}"

if [ -n "${HEALTHCHECK_URL:-}" ]; then
    wget -q -T 10 -O /dev/null "${HEALTHCHECK_URL}" 2>/dev/null || true
fi
