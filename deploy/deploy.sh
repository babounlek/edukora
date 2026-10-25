#!/usr/bin/env bash
# Déploiement de l'APPLICATION (backend + frontend/Caddy + sauvegarde) sur le Droplet.
# À lancer sur le serveur, depuis le clone du dépôt, normalement par .github/workflows/deploy.yml.
#
#   deploy/deploy.sh <tag>                      # tag = SHA du commit construit par release.yml
#   deploy/deploy.sh <tag> --sans-sauvegarde    # à éviter : saute le pg_dump de précaution
#   deploy/deploy.sh <tag> --sans-migration     # retour arrière d'images (voir rollback.sh)
#
# Séquence : contrôles -> sauvegarde Postgres -> tirage des images -> migrations (avec la
# nouvelle image, AVANT de basculer) -> bascule -> vérification de santé (/healthz doit répondre
# avec la version déployée) -> retour arrière automatique des images si la vérification échoue.
#
# RÈGLE DES MIGRATIONS : elles tournent avant la bascule, donc l'ancien code sert un court
# instant sur le nouveau schéma, et un retour arrière d'images ne défait PAS le schéma. Toute
# migration doit donc être rétro-compatible avec la version précédente (ajouter avant de
# retirer : colonne nullable/par défaut d'abord, suppression ou renommage dans un déploiement
# ultérieur). Une migration destructive demande une fenêtre dédiée et une restauration de la
# sauvegarde prise ici (deploy/README-TUNNEL.md, section « Si ça tourne mal »).
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"

TAG="${1:?usage: deploy.sh <tag> [--sans-sauvegarde] [--sans-migration]}"
shift
SAUVEGARDE=1
MIGRATION=1
for arg in "$@"; do
  case "$arg" in
    --sans-sauvegarde) SAUVEGARDE=0 ;;
    --sans-migration) MIGRATION=0 ;;
    *) echo "Option inconnue : $arg" >&2; exit 2 ;;
  esac
done

if ! [[ "$TAG" =~ ^[0-9a-f]{7,40}$ ]]; then
  echo "Étiquette invalide « $TAG » : un SHA de commit est attendu (7 à 40 caractères hexadécimaux)." >&2
  exit 2
fi

ETAT="$ROOT/.deploy"
mkdir -p "$ETAT"

# Verrou partagé avec deploy/sync-lot.sh : un déploiement ne démarre pas pendant l'application d'un lot de
# contenu (et inversement). Le descripteur 9 reste ouvert jusqu'à la fin du script. Sans dossier des lots
# (chaîne de synchronisation pas encore installée), aucun verrou.
LOTS_DIR="${EDUKORA_LOTS_DIR:-/srv/edukora-lots}"
if [ -d "$LOTS_DIR" ]; then
  exec 9>"$LOTS_DIR/.sync.lock"
  if ! flock -n 9; then
    echo "Un lot de contenu est en cours d'application (verrou $LOTS_DIR/.sync.lock) : réessayez à sa fin." >&2
    exit 1
  fi
fi
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
SERVICES=(db backend relances caddy backup)

log() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

# --- Contrôles ---------------------------------------------------------------------------
[ -f .env ] || { echo ".env introuvable dans $ROOT." >&2; exit 1; }
DOMAINE="$(grep -E '^SITE_DOMAIN=' .env | tail -1 | cut -d= -f2- | tr -d '\r"' )"
[ -n "$DOMAINE" ] || { echo "SITE_DOMAIN absent de .env." >&2; exit 1; }
if grep -qE '^DEBUG=(True|true|1)' .env; then
  echo "Refusé : DEBUG est activé dans .env de ce serveur." >&2
  exit 1
fi

LIBRE_GO="$(df --output=avail -BG / | tail -1 | tr -dc '0-9')"
if [ "${LIBRE_GO:-0}" -lt 5 ]; then
  echo "Moins de 5 Go libres sur le disque (${LIBRE_GO} Go) : libérez de la place avant de déployer." >&2
  exit 1
fi

export IMAGE_TAG="$TAG"
"${COMPOSE[@]}" config -q

PRECEDENT="$(cat "$ETAT/current_tag" 2>/dev/null || true)"
log "Déploiement de $TAG sur $DOMAINE (version actuelle : ${PRECEDENT:-inconnue})"

# --- Santé ------------------------------------------------------------------------------
# --resolve : on interroge ce serveur lui-même mais avec le vrai nom de domaine, donc avec le
# vrai certificat TLS, sans dépendre du DNS ni d'un pare-feu sortant.
verifier_sante() {
  local attendu="$1" essais=45 reponse
  for ((i = 1; i <= essais; i++)); do
    reponse="$(curl -fsS --max-time 5 --resolve "$DOMAINE:443:127.0.0.1" "https://$DOMAINE/healthz" 2>/dev/null || true)"
    if [[ "$reponse" == *"\"version\": \"$attendu\""* ]] || [[ "$reponse" == *"\"version\":\"$attendu\""* ]]; then
      log "Santé OK ($reponse)"
      return 0
    fi
    sleep 2
  done
  log "Pas de réponse saine après $((essais * 2)) s (dernière : ${reponse:-aucune})."
  return 1
}

basculer() {
  IMAGE_TAG="$1" "${COMPOSE[@]}" up -d --no-build --remove-orphans "${SERVICES[@]}"
}

# --- Sauvegarde --------------------------------------------------------------------------
if [ "$SAUVEGARDE" = 1 ]; then
  log "Sauvegarde Postgres de précaution..."
  if ! "${COMPOSE[@]}" exec -T backup ./backup.sh; then
    echo "Sauvegarde en échec : déploiement annulé (rien n'a été modifié)." >&2
    exit 1
  fi
else
  log "ATTENTION : sauvegarde sautée (--sans-sauvegarde)."
fi

# --- Images ------------------------------------------------------------------------------
log "Tirage des images..."
"${COMPOSE[@]}" pull backend caddy backup

# --- Migrations --------------------------------------------------------------------------
if [ "$MIGRATION" = 1 ]; then
  EN_ATTENTE="$("${COMPOSE[@]}" run --rm --no-deps -T --entrypoint python backend manage.py showmigrations --plan | grep -E '^\[ \]' || true)"
  if [ -n "$EN_ATTENTE" ]; then
    log "Migrations à appliquer :"
    echo "$EN_ATTENTE"
  else
    log "Aucune migration à appliquer."
  fi
  "${COMPOSE[@]}" run --rm --no-deps -T --entrypoint python backend manage.py migrate --noinput
fi

# --- Bascule -----------------------------------------------------------------------------
log "Bascule..."
if basculer "$TAG" && verifier_sante "$TAG"; then
  [ -n "$PRECEDENT" ] && echo "$PRECEDENT" > "$ETAT/previous_tag"
  echo "$TAG" > "$ETAT/current_tag"
  echo "$(date -u +%FT%TZ) deploye $TAG (precedent: ${PRECEDENT:-aucun})" >> "$ETAT/historique.log"
  docker image prune -f >/dev/null
  log "Déploiement terminé : $TAG"
  exit 0
fi

# --- Échec : retour arrière des IMAGES ---------------------------------------------------
echo "ÉCHEC du déploiement de $TAG." >&2
if [ -n "$PRECEDENT" ]; then
  log "Retour arrière vers $PRECEDENT..."
  if basculer "$PRECEDENT" && verifier_sante "$PRECEDENT"; then
    echo "$(date -u +%FT%TZ) ECHEC $TAG, retour a $PRECEDENT" >> "$ETAT/historique.log"
    echo "Retour arrière réussi : $PRECEDENT sert de nouveau. Le schéma de la base, lui, n'a pas été défait." >&2
  else
    echo "Le retour arrière a lui aussi échoué : intervention manuelle (docker compose logs backend caddy)." >&2
  fi
else
  echo "Aucune version précédente connue (premier déploiement par ce script) : pas de retour arrière automatique." >&2
fi
exit 1
