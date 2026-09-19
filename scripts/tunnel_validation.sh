#!/usr/bin/env bash
# Tunnel de validation post-ingestion : portes base (valider_ingestion) puis vrai moteur
# de rendu KaTeX (vitest) sur le seul périmètre récemment ingéré.
#
#   scripts/tunnel_validation.sh 2h            # contenu modifié depuis 2 heures
#   scripts/tunnel_validation.sh 2h --strict   # les ALERTE font aussi échouer
#
# Code de sortie != 0 si l'une des deux étapes échoue. Le backend n'étant pas bind-monté,
# reconstruire l'image après tout changement de catalog/tunnel.py.
set -u

SINCE="${1:?usage: tunnel_validation.sh <since: 90m|2h|1d|ISO> [--strict]}"
shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DUMP_HOST="$ROOT/backend/ingest/_audit/rendu_tunnel.json"

rm -f "$DUMP_HOST"

echo "=== Portes base (structure, thèmes, couverture) ==="
# Le conteneur logge chaque requête SQL en DEBUG : filtrées, le code de sortie est celui de manage.py.
docker exec edukora-backend-1 python manage.py valider_ingestion --since "$SINCE" "$@" 2>&1 | grep -Ev '^\([0-9.]+\) '
DB_STATUS=${PIPESTATUS[0]}

if [ ! -f "$DUMP_HOST" ]; then
  echo "Dump de rendu absent : la commande base a échoué avant de l'écrire." >&2
  exit 1
fi

echo
echo "=== Porte rendu (vrai moteur remark/rehype-katex) ==="
(cd "$ROOT/frontend" && AUDIT_RENDU_DUMP="$DUMP_HOST" npx vitest run src/lib/audit-rendu.test.ts)
RENDER_STATUS=$?

echo
if [ $DB_STATUS -ne 0 ] || [ $RENDER_STATUS -ne 0 ]; then
  echo "TUNNEL NON VALIDÉ (base=$DB_STATUS rendu=$RENDER_STATUS) - corriger avant de déclarer le round terminé."
  exit 1
fi
echo "TUNNEL VALIDÉ."
