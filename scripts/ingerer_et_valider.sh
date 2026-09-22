#!/usr/bin/env bash
# Ingestion + tunnel de validation en une commande, sur un périmètre exact (pas de fenêtre
# "--since 2h" à deviner : l'instant de départ est relevé sur l'horloge du conteneur).
#
#   scripts/ingerer_et_valider.sh cm/bac-ti-si-2025-officiel-cameroun
#   scripts/ingerer_et_valider.sh cm/bac-ti-si-2025-officiel-cameroun --strict
#
# Le dossier est relatif à backend/ingest/ (déjà monté dans le conteneur, contrairement au
# code backend). Code de sortie != 0 si l'ingestion a des erreurs OU si le tunnel échoue :
# ne pas déclarer le round terminé dans ce cas.
set -u

CIBLE="${1:?usage: ingerer_et_valider.sh <pays/dossier> [--strict]}"
shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -e "$ROOT/backend/ingest/$CIBLE" ]; then
  echo "Introuvable : backend/ingest/$CIBLE" >&2
  exit 2
fi

# Une minute de marge : les objets modifiés pendant l'ingestion portent un updated_at postérieur.
DEPART="$(docker exec edukora-backend-1 date -u -d '1 minute ago' +%Y-%m-%dT%H:%M:%S+00:00)"

echo "=== Ingestion de $CIBLE (périmètre du tunnel : depuis $DEPART) ==="
# MSYS_NO_PATHCONV : sans lui, Git Bash réécrit "/app/..." en "C:/Program Files/Git/app/...".
SORTIE="$(MSYS_NO_PATHCONV=1 docker exec edukora-backend-1 python manage.py ingest_corrections "/app/ingest/$CIBLE" 2>&1 | grep -Ev '^\([0-9.]+\) ')"
echo "$SORTIE"

if echo "$SORTIE" | grep -qE "erreur\(s\) :|CommandError|Traceback"; then
  echo
  echo "INGESTION EN ERREUR - corriger les JSON sources puis relancer ; tunnel non lancé." >&2
  exit 1
fi

if echo "$SORTIE" | grep -q "^0 objet(s) créé(s)\|Aucun fichier .json"; then
  echo
  echo "Rien de nouveau ingéré (contenu déjà en base) : pas de périmètre à valider."
  exit 0
fi

echo
"$ROOT/scripts/tunnel_validation.sh" "$DEPART" "$@"
