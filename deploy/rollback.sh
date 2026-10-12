#!/usr/bin/env bash
# Retour arrière MANUEL vers la version précédente (ou vers un SHA donné).
#
#   deploy/rollback.sh              # revient à la version qui précédait la courante
#   deploy/rollback.sh <sha>        # revient à un SHA précis (ses images doivent exister sur GHCR)
#
# Ne revient que sur les IMAGES : ni sauvegarde, ni migrations. Le schéma de la base reste celui
# de la version la plus récente, ce qui est sans danger tant que les migrations sont
# rétro-compatibles (voir l'en-tête de deploy.sh). Si une migration a cassé les données, c'est
# une restauration de la sauvegarde qu'il faut (deploy/README-TUNNEL.md).
set -euo pipefail

cd "$(dirname "$0")/.."
CIBLE="${1:-$(cat .deploy/previous_tag 2>/dev/null || true)}"
[ -n "$CIBLE" ] || { echo "Aucune version précédente connue : précisez un SHA (rollback.sh <sha>)." >&2; exit 1; }
echo "Retour arrière vers $CIBLE"
exec deploy/deploy.sh "$CIBLE" --sans-sauvegarde --sans-migration
