#!/usr/bin/env bash
# Côté SERVEUR de la purge des comptes de test (voir deploy/SPEC-PURGE-DONNEES-TEST.md et README-PURGE-DONNEES-TEST.md).
# Appelé par `scripts/edukora.ps1` via SSH. Arguments validés par liste blanche ; sortie destinée au poste = JSON.
#
#   purge-test.sh preparer                      crée $LOTS/purge (droits 700)
#   purge-test.sh installer-commande           copie les 2 fichiers de $LOTS/purge/code dans le conteneur (sans rebuild), contrôle leur SHA-256
#   purge-test.sh recevoir-perimetre            lit le fichier de périmètre sur l'entrée standard (JSON), le range en 600
#   purge-test.sh simuler                       simulation : RIEN n'est persisté ; affiche le rapport et le jeton
#   purge-test.sh sauvegarde                    sauvegarde Postgres vérifiée (+ copie hors site) PUIS test de restauration
#   purge-test.sh executer <dump> <jeton>       exige dump récent + hors site + restauration testée + jeton de simulation
#   purge-test.sh verifier                      plus aucun compte ciblé
#
# Codes de sortie : 0 ok · 1 échec · 2 usage ou garde refusée · 75 verrou pris (lot ou déploiement en cours).
# Ne supprime jamais rien de lui-même : seule la commande Django `purger_donnees_test executer` supprime.
set -uo pipefail

REPO="${EDUKORA_REPO:-/srv/edukora}"   # le script peut vivre hors du clone (poste : scripts/edukora.ps1 purge-installer)
cd "$REPO" || { echo "{\"statut\":\"refuse\",\"erreur\":\"dépôt introuvable\"}"; exit 2; }
LOTS="${EDUKORA_LOTS_DIR:-/srv/edukora-lots}"
PURGE="$LOTS/purge"
VERROU="$LOTS/.sync.lock"
AGE_MAX_MIN="${PURGE_AGE_MAX_MIN:-1440}"   # une sauvegarde de plus de 24 h n'est pas acceptée
if [ -f .deploy/current_tag ]; then
  IMAGE_TAG="$(tr -dc '0-9a-f' < .deploy/current_tag)"
  export IMAGE_TAG
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
else
  COMPOSE=(docker compose)
fi
EN_CONTENEUR="/tmp/purge"
FICHIERS=("users/purge_test.py" "users/management/commands/purger_donnees_test.py")
SYNC="$REPO/deploy/sync-lot.sh"

echec() {  # echec <code> <message>
  local code="$1"; shift
  printf '{"statut":"refuse","erreur":"%s"}\n' "$(printf '%s' "$*" | sed 's/["\\]/ /g')"
  exit "$code"
}
valider_dump() { [[ "${1:-}" =~ ^avant-[0-9]{8}-[0-9]{6}-[0-9a-f]{8}\.dump$ ]] || echec 2 "nom de sauvegarde invalide"; }
valider_jeton() { [[ "${1:-}" =~ ^[0-9a-f]{20}$ ]] || echec 2 "jeton invalide"; }
manage() { "${COMPOSE[@]}" exec -T backend python manage.py "$@" </dev/null; }
derniere_json() { grep -E '^\{' | tail -n 1; }
preparer() { mkdir -p "$PURGE/code" 2>/dev/null && chmod 700 "$LOTS" "$PURGE" "$PURGE/code" 2>/dev/null || echec 1 "dossier $PURGE inutilisable (lancer d'abord sync-lot.sh preparer-dossiers)"; }
avec_perimetre() {
  [ -f "$PURGE/perimetre.json" ] || echec 2 "aucun fichier de périmètre reçu (purge-test.sh recevoir-perimetre)"
  "${COMPOSE[@]}" exec -T backend mkdir -p "$EN_CONTENEUR" </dev/null >/dev/null 2>&1 || echec 1 "dossier $EN_CONTENEUR inutilisable dans le conteneur"
  "${COMPOSE[@]}" cp "$PURGE/perimetre.json" "backend:$EN_CONTENEUR/perimetre.json" >/dev/null 2>&1 || echec 1 "copie du périmètre dans le conteneur impossible"
}

SOUS="${1:-}"
[ -n "$SOUS" ] || { sed -n '2,15p' "$0"; exit 2; }
shift

case "$SOUS" in
  preparer)
    preparer
    printf '{"statut":"ok","dossier":"%s"}\n' "$PURGE"
    ;;

  installer-commande)
    preparer
    for f in "${FICHIERS[@]}"; do
      src="$PURGE/code/$(basename "$f")"
      [ -f "$src" ] || echec 2 "fichier absent : $src"
      "${COMPOSE[@]}" cp "$src" "backend:/app/$f" >/dev/null 2>&1 || echec 1 "copie de $f impossible"
      attendu="$(sha256sum "$src" | cut -d' ' -f1)"
      obtenu="$("${COMPOSE[@]}" exec -T backend sha256sum "/app/$f" </dev/null 2>/dev/null | cut -d' ' -f1)"
      [ "$attendu" = "$obtenu" ] || echec 1 "SHA-256 différent après copie de $f"
    done
    manage purger_donnees_test --help >/dev/null 2>&1 || echec 1 "la commande purger_donnees_test ne se charge pas dans le conteneur"
    printf '{"statut":"ok","fichiers":%s}\n' "${#FICHIERS[@]}"
    ;;

  recevoir-perimetre)
    preparer
    tmp="$PURGE/perimetre.json.partiel"
    head -c 1048576 > "$tmp"
    [ -s "$tmp" ] || { rm -f "$tmp"; echec 2 "périmètre vide"; }
    mv "$tmp" "$PURGE/perimetre.json"; chmod 600 "$PURGE/perimetre.json"
    printf '{"statut":"ok","octets":%s}\n' "$(stat -c %s "$PURGE/perimetre.json")"
    ;;

  simuler)
    avec_perimetre
    manage purger_donnees_test simuler --perimetre "$EN_CONTENEUR/perimetre.json" --json 2>&1 | derniere_json
    exit "${PIPESTATUS[0]}"
    ;;

  sauvegarde)
    id="$(date +%Y%m%d-%H%M%S)-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
    sauv="$(bash "$SYNC" sauvegarde "$id" | derniere_json)"
    case "$sauv" in
      *'"statut":"ok"'*) ;;
      *) printf '%s\n' "$sauv"; echec 1 "sauvegarde en échec" ;;
    esac
    dump="avant-$id.dump"
    [ -f "$LOTS/sauvegardes/$dump" ] && [ -f "$LOTS/sauvegardes/$dump.hors-site" ] || echec 1 "sauvegarde non confirmée hors site"
    rest="$(bash "$SYNC" test-restauration "$dump" | derniere_json)"
    case "$rest" in
      *'"statut":"ok"'*) : > "$LOTS/sauvegardes/$dump.restauration-ok" ;;   # preuve lue par `executer` ; jamais écrite par la commande Django
      *) printf '%s\n' "$rest"; echec 1 "restauration de test en échec : pas de preuve écrite" ;;
    esac
    printf '{"statut":"ok","dump":"%s","restauration":%s}\n' "$dump" "$rest"
    ;;

  executer)
    valider_dump "${1:-}"; dump="$1"
    valider_jeton "${2:-}"; jeton="$2"
    f="$LOTS/sauvegardes/$dump"
    [ -f "$f" ] || echec 2 "sauvegarde introuvable"
    [ -f "$f.hors-site" ] || echec 2 "sauvegarde sans copie hors site"
    [ -f "$f.restauration-ok" ] || echec 2 "restauration de cette sauvegarde non testée (purge-test.sh sauvegarde)"
    [ -n "$(find "$f" -maxdepth 0 -mmin "-$AGE_MAX_MIN" 2>/dev/null)" ] || echec 2 "sauvegarde trop ancienne (> $AGE_MAX_MIN min) : en refaire une"
    avec_perimetre
    # Même verrou que lots et déploiements : aucun ne s'exécute pendant la purge.
    exec 9>"$VERROU"
    flock -n 9 || { printf '{"statut":"verrou_pris"}\n'; exit 75; }
    "${COMPOSE[@]}" exec -T -e ALLOW_TEST_DATA=1 -e "PURGE_SAUVEGARDE_VERIFIEE=$dump" backend \
      python manage.py purger_donnees_test executer --perimetre "$EN_CONTENEUR/perimetre.json" --jeton "$jeton" \
      --sauvegarde "$dump" --confirme-production --json </dev/null 2>&1 | derniere_json
    exit "${PIPESTATUS[0]}"
    ;;

  verifier)
    avec_perimetre
    manage purger_donnees_test verifier --perimetre "$EN_CONTENEUR/perimetre.json" --json 2>&1 | derniere_json
    exit "${PIPESTATUS[0]}"
    ;;

  *)
    echec 2 "sous-commande inconnue"
    ;;
esac
