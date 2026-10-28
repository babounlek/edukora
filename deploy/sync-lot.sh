#!/usr/bin/env bash
# Côté SERVEUR de la chaîne de synchronisation des contenus (voir deploy/SPEC-SYNC-CONTENU.md §8).
# Appelé par `scripts/edukora.ps1` via SSH, jamais à la main sauf pour diagnostiquer. Chaque sous-commande
# valide ses arguments (liste blanche de caractères) : rien de ce qui arrive du poste n'est interprété
# par un shell. Toute sortie destinée au poste est du JSON sur une seule ligne, sur la sortie standard.
#
#   sync-lot.sh diagnostic                         prérequis du serveur (lecture seule)
#   sync-lot.sh preparer-dossiers                  crée /srv/edukora-lots (droits 700), une seule fois
#   sync-lot.sh ouvrir-lot <batch_id>              crée incoming/<batch_id>/ (droits 700) avant le transfert
#   sync-lot.sh verifier-archive <batch_id>        SHA-256 de l'archive reçue (incoming/<id>/)
#   sync-lot.sh recevoir <batch_id>                copie dans le conteneur + `sync_contenu recevoir`
#   sync-lot.sh sauvegarde <batch_id> [--max-age-h N]   sauvegarde Postgres VÉRIFIÉE (+ copie hors site)
#   sync-lot.sh planifier <batch_id>               simulation (aucune écriture)
#   sync-lot.sh appliquer <batch_id> [--confirme-retraits] [--sans-post-traitement]    détaché
#   sync-lot.sh reprendre <batch_id> [--confirme-retraits]                            détaché
#   sync-lot.sh statut <batch_id>                  état du lot (répond sans rien rejouer)
#   sync-lot.sh post-traiter <batch_id>            PDF de sujet, index de recherche (reprenable)
#   sync-lot.sh reference                          empreintes appliquées en production
#   sync-lot.sh verifier-fichiers                  références sans fichier (rapport seul)
#   sync-lot.sh nettoyer [--apres-jours N] [--appliquer]   anciens fichiers remplacés
#   sync-lot.sh test-restauration <fichier.dump>   restaure dans une base jetable et compare les compteurs
#
# Codes de sortie : 0 ok · 1 échec · 2 usage · 75 verrou pris (autre lot ou déploiement en cours).
# Le verrou (flock sur $LOTS/.sync.lock) est partagé avec deploy/deploy.sh : un lot et un déploiement
# ne s'exécutent jamais en même temps. Un lot appliqué tient ce verrou pendant TOUTE son exécution,
# détachée de la session SSH (setsid + nohup) : une coupure réseau n'interrompt rien.
set -uo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"
LOTS="${EDUKORA_LOTS_DIR:-/srv/edukora-lots}"
VERROU="$LOTS/.sync.lock"
# Serveur déployé par deploy.sh : l'override de production exige IMAGE_TAG (la version déployée) pour CHAQUE
# commande compose, même un simple `exec`. Serveur pas encore passé par deploy.sh : pile construite sur place,
# fichier compose de base seul.
if [ -f .deploy/current_tag ]; then
  IMAGE_TAG="$(tr -dc '0-9a-f' < .deploy/current_tag)"
  export IMAGE_TAG
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
else
  COMPOSE=(docker compose)
fi
EN_CONTENEUR="/tmp/lots-recus"

json() { printf '%s\n' "$*"; }
echec() {  # echec <code> <message>
  local code="$1"; shift
  printf '{"statut":"refuse","erreur":"%s"}\n' "$(printf '%s' "$*" | sed 's/["\\]/ /g')"
  exit "$code"
}

# --- Validation des arguments : liste blanche, jamais d'interprétation ---------------------------
valider_batch_id() { [[ "${1:-}" =~ ^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$ ]] || echec 2 "batch_id invalide"; }
valider_entier() { [[ "${1:-}" =~ ^[0-9]{1,5}$ ]] || echec 2 "entier invalide"; }
valider_dump() { [[ "${1:-}" =~ ^[A-Za-z0-9._-]{1,120}\.dump$ ]] || echec 2 "nom de sauvegarde invalide"; }

SOUS="${1:-}"
[ -n "$SOUS" ] || { sed -n '2,26p' "$0"; exit 2; }
shift

manage() { "${COMPOSE[@]}" exec -T backend python manage.py "$@"; }
# Le conteneur logge chaque requête SQL en DEBUG ; seule la dernière ligne JSON nous intéresse.
derniere_json() { grep -E '^\{' | tail -n 1; }

verrou_libre() {
  mkdir -p "$LOTS" 2>/dev/null || true
  ( exec 9>"$VERROU"; flock -n 9 )
}

assurer_recu() {  # assurer_recu <batch_id> : (re)copie et (re)reçoit l'archive, idempotent
  local batch="$1" dossier="$LOTS/incoming/$1" sha
  [ -f "$dossier/lot.zip" ] || echec 1 "archive absente du serveur : renvoyer le lot"
  sha="$(awk '{print tolower($1)}' "$dossier/lot.zip.sha256" | head -n 1)"
  "${COMPOSE[@]}" exec -T backend mkdir -p "$EN_CONTENEUR" || echec 1 "conteneur injoignable"
  "${COMPOSE[@]}" cp "$dossier/lot.zip" "backend:$EN_CONTENEUR/$batch.zip" >/dev/null 2>&1 || echec 1 "copie dans le conteneur impossible"
  manage sync_contenu recevoir "$EN_CONTENEUR/$batch.zip" --sha256 "$sha" >/dev/null 2>&1 || echec 1 "réception du lot refusée"
}

lancer_detache() {  # lancer_detache <batch_id> <journal> <commande...>
  local batch="$1" journal="$2"; shift 2
  verrou_libre || { printf '{"statut":"verrou_pris"}\n'; exit 75; }
  mkdir -p "$LOTS/journaux"
  # setsid + nohup : le processus survit à la fin de la session SSH. Le sous-shell prend le verrou et le
  # garde jusqu'à la fin de la commande ; si un déploiement l'a pris entre-temps, rien n'est exécuté.
  setsid nohup bash -c '
    exec 9>"$1"; shift
    journal="$1"; shift
    if ! flock -n 9; then echo "verrou pris au lancement" >> "$journal"; exit 75; fi
    echo "[$(date -u +%FT%TZ)] début : $*" >> "$journal"
    "$@" >> "$journal" 2>&1
    code=$?
    echo "[$(date -u +%FT%TZ)] fin (code $code)" >> "$journal"
  ' _ "$VERROU" "$journal" "$@" > /dev/null 2>&1 < /dev/null &
  printf '{"statut":"lance","batch_id":"%s","journal":"%s"}\n' "$batch" "$journal"
}

case "$SOUS" in

  diagnostic)
    docker_ok=false; docker info >/dev/null 2>&1 && docker_ok=true
    flock_ok=false; command -v flock >/dev/null 2>&1 && flock_ok=true
    dossier_ok=false; [ -d "$LOTS" ] && dossier_ok=true
    droits=""; [ -d "$LOTS" ] && droits="$(stat -c %a "$LOTS")"
    commande_ok=false
    if $docker_ok && manage help sync_contenu >/dev/null 2>&1; then commande_ok=true; fi
    version="$(cat .deploy/current_tag 2>/dev/null || echo inconnue)"
    libre_go="$(df --output=avail -BG "${LOTS%/*}" 2>/dev/null | tail -1 | tr -dc '0-9')"
    printf '{"statut":"ok","docker":%s,"flock":%s,"dossier_lots":%s,"droits_dossier_lots":"%s","commande_sync_contenu":%s,"version_deployee":"%s","disque_libre_go":%s,"utilisateur":"%s"}\n' \
      "$docker_ok" "$flock_ok" "$dossier_ok" "$droits" "$commande_ok" "$version" "${libre_go:-0}" "$(id -un)"
    ;;

  preparer-dossiers)
    # /srv appartient d'ordinaire à root : le dossier racine se crée UNE fois avec sudo (voir le message).
    if ! mkdir -p "$LOTS/incoming" "$LOTS/sauvegardes" "$LOTS/journaux" "$LOTS/archives" 2>/dev/null \
       || ! chmod 700 "$LOTS" "$LOTS/incoming" "$LOTS/sauvegardes" "$LOTS/journaux" "$LOTS/archives" 2>/dev/null; then
      echec 1 "impossible de creer $LOTS avec les droits de $(id -un) : sudo install -d -m 700 -o $(id -un) -g $(id -un) $LOTS puis relancer"
    fi
    printf '{"statut":"ok","dossier":"%s"}\n' "$LOTS"
    ;;

  ouvrir-lot)
    valider_batch_id "${1:-}"
    mkdir -p "$LOTS/incoming/$1" && chmod 700 "$LOTS/incoming/$1" || echec 1 "dossier du lot impossible à créer"
    printf '{"statut":"ok","dossier":"%s"}
' "$LOTS/incoming/$1"
    ;;

  verifier-archive)
    valider_batch_id "${1:-}"; batch="$1"
    dossier="$LOTS/incoming/$batch"
    [ -f "$dossier/lot.zip" ] && [ -f "$dossier/lot.zip.sha256" ] || echec 1 "archive ou empreinte absente"
    attendu="$(awk '{print tolower($1)}' "$dossier/lot.zip.sha256" | head -n 1)"
    [[ "$attendu" =~ ^[0-9a-f]{64}$ ]] || echec 1 "fichier .sha256 invalide"
    obtenu="$(sha256sum "$dossier/lot.zip" | awk '{print $1}')"
    if [ "$attendu" = "$obtenu" ]; then
      printf '{"statut":"ok","sha256":"%s"}\n' "$obtenu"
    else
      printf '{"statut":"refuse","erreur":"SHA-256 differente : transfert corrompu","attendu":"%s","obtenu":"%s"}\n' "$attendu" "$obtenu"
      exit 1
    fi
    ;;

  recevoir)
    valider_batch_id "${1:-}"; batch="$1"
    dossier="$LOTS/incoming/$batch"
    [ -f "$dossier/lot.zip" ] || echec 1 "archive absente"
    sha="$(awk '{print tolower($1)}' "$dossier/lot.zip.sha256" | head -n 1)"
    [[ "$sha" =~ ^[0-9a-f]{64}$ ]] || echec 1 "fichier .sha256 invalide"
    "${COMPOSE[@]}" exec -T backend mkdir -p "$EN_CONTENEUR" || echec 1 "conteneur injoignable"
    "${COMPOSE[@]}" cp "$dossier/lot.zip" "backend:$EN_CONTENEUR/$batch.zip" >/dev/null 2>&1 || echec 1 "copie dans le conteneur impossible"
    manage sync_contenu recevoir "$EN_CONTENEUR/$batch.zip" --sha256 "$sha" 2>&1 | derniere_json
    exit "${PIPESTATUS[0]}"
    ;;

  sauvegarde)
    valider_batch_id "${1:-}"; batch="$1"; shift
    age_max=0
    while [ $# -gt 0 ]; do
      case "$1" in
        --max-age-h) valider_entier "${2:-}"; age_max="$2"; shift 2 ;;
        *) echec 2 "option inconnue" ;;
      esac
    done
    mkdir -p "$LOTS/sauvegardes"
    # Un lot qui ne fait que créer peut se contenter d'une sauvegarde récente (< N heures).
    # Seule une sauvegarde dont la COPIE HORS SITE a réussi (marqueur .hors-site) est réutilisable : un dump resté
    # sur le disque après un échec de backup.sh ne protège pas d'une perte du disque.
    if [ "$age_max" -gt 0 ]; then
      recent="$(find "$LOTS/sauvegardes" -maxdepth 1 -name '*.dump' -mmin "-$((age_max * 60))" 2>/dev/null | sort | while read -r f; do [ -f "$f.hors-site" ] && echo "$f"; done | tail -n 1)"
      if [ -n "$recent" ] && "${COMPOSE[@]}" exec -T db sh -c 'pg_restore --list > /dev/null' < "$recent" 2>/dev/null; then
        printf '{"statut":"ok","reutilisee":true,"dump":"%s","octets":%s,"hors_site":true}\n' "$(basename "$recent")" "$(stat -c %s "$recent")"
        exit 0
      fi
    fi
    dump="avant-$batch.dump"
    chemin="$LOTS/sauvegardes/$dump"
    # 1. dump complet vers l'hôte, sans passer par un fichier dans le conteneur ; format custom compressé.
    "${COMPOSE[@]}" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-privileges' > "$chemin.partiel" 2>"$LOTS/journaux/$dump.err" \
      || { rm -f "$chemin.partiel"; echec 1 "pg_dump en échec"; }
    taille="$(stat -c %s "$chemin.partiel")"
    [ "$taille" -gt 1000 ] || { rm -f "$chemin.partiel"; echec 1 "sauvegarde suspecte (trop petite)"; }
    # 2. intégrité : le sommaire du dump doit se lire et contenir les tables de contenu.
    sommaire="$("${COMPOSE[@]}" exec -T db sh -c 'pg_restore --list' < "$chemin.partiel" 2>/dev/null)" \
      || { rm -f "$chemin.partiel"; echec 1 "dump illisible par pg_restore"; }
    for table in catalog_exercise catalog_question catalog_lesson; do
      grep -q "TABLE DATA public $table " <<< "$sommaire" || { rm -f "$chemin.partiel"; echec 1 "table $table absente du dump"; }
    done
    mv "$chemin.partiel" "$chemin"
    chmod 600 "$chemin"
    # 3. copie hors site par la sauvegarde existante (Spaces) : son échec annule aussi l'opération.
    "${COMPOSE[@]}" exec -T backup ./backup.sh >/dev/null 2>&1 || echec 1 "copie hors site (backup.sh) en échec"
    : > "$chemin.hors-site"   # marqueur : cette sauvegarde est aussi copiée hors site
    # Rotation : on garde les 8 dernières sauvegardes de lot (et leur marqueur).
    ls -1t "$LOTS"/sauvegardes/avant-*.dump 2>/dev/null | tail -n +9 | while read -r vieux; do rm -f "$vieux" "$vieux.hors-site"; done
    printf '{"statut":"ok","reutilisee":false,"dump":"%s","octets":%s,"hors_site":true}\n' "$dump" "$taille"
    ;;

  planifier)
    valider_batch_id "${1:-}"
    assurer_recu "$1"
    manage sync_contenu planifier "$1" 2>&1 | derniere_json
    exit "${PIPESTATUS[0]}"
    ;;

  appliquer|reprendre)
    valider_batch_id "${1:-}"; batch="$1"; shift
    args=(sync_contenu "$SOUS" "$batch" --confirme)
    while [ $# -gt 0 ]; do
      case "$1" in
        --confirme-retraits) args+=(--confirme-retraits "$batch") ;;
        --sans-post-traitement) args+=(--sans-post-traitement) ;;
        *) echec 2 "option inconnue" ;;
      esac
      shift
    done
    assurer_recu "$batch"
    lancer_detache "$batch" "$LOTS/journaux/$batch.log" "${COMPOSE[@]}" exec -T backend python manage.py "${args[@]}"
    ;;

  statut)
    valider_batch_id "${1:-}"
    manage sync_contenu statut "$1" 2>&1 | derniere_json
    # Les codes 3 (indéterminé) et 4 (conflits) de la commande sont des réponses, pas des pannes.
    ;;

  post-traiter)
    valider_batch_id "${1:-}"
    assurer_recu "$1"
    lancer_detache "$1" "$LOTS/journaux/$1.post.log" "${COMPOSE[@]}" exec -T backend python manage.py sync_contenu post-traiter "$1"
    ;;

  reference)
    manage sync_contenu exporter-reference 2>&1 | grep -E '^\{' | tail -n 1
    exit "${PIPESTATUS[0]}"
    ;;

  verifier-fichiers)
    manage sync_contenu verifier-fichiers 2>&1 | derniere_json
    ;;

  nettoyer)
    args=(sync_contenu nettoyer)
    while [ $# -gt 0 ]; do
      case "$1" in
        --apres-jours) valider_entier "${2:-}"; args+=(--apres-jours "$2"); shift 2 ;;
        --appliquer) args+=(--appliquer); shift ;;
        *) echec 2 "option inconnue" ;;
      esac
    done
    verrou_libre || { printf '{"statut":"verrou_pris"}\n'; exit 75; }
    manage "${args[@]}" 2>&1 | derniere_json
    ;;

  test-restauration)
    valider_dump "${1:-}"; dump="$LOTS/sauvegardes/$1"
    [ -f "$dump" ] || echec 1 "sauvegarde introuvable"
    base="edukora_restore_test"
    tables=(catalog_lesson catalog_exercise catalog_question catalog_cours quiz_competenceitem)
    compter() {  # compter <base> <table>
      "${COMPOSE[@]}" exec -T db sh -c "psql -U \"\$POSTGRES_USER\" -d $1 -tAc 'SELECT count(*) FROM $2'" 2>/dev/null | tr -dc '0-9'
    }
    "${COMPOSE[@]}" exec -T db sh -c "dropdb -U \"\$POSTGRES_USER\" --if-exists $base && createdb -U \"\$POSTGRES_USER\" $base" >/dev/null 2>&1 \
      || echec 1 "création de la base jetable impossible"
    "${COMPOSE[@]}" exec -T db sh -c "pg_restore -U \"\$POSTGRES_USER\" -d $base --no-owner --no-privileges" < "$dump" >/dev/null 2>&1
    # Tables d'usage que la purge des données de test modifie (deploy/SPEC-PURGE-DONNEES-TEST.md) : users_user doit
    # être non vide (il y a au moins un administrateur) ; les trois autres peuvent légitimement être vides, on exige
    # seulement que la table existe dans la restauration et on en rapporte le compte.
    tables_usage=(users_user users_profil payments_manualpayment subscriptions_subscription)
    sortie='{"statut":"ok","tables":{'; ok=true; sep=""
    for t in "${tables[@]}" "${tables_usage[@]}"; do
      orig="$("${COMPOSE[@]}" exec -T db sh -c "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -tAc 'SELECT count(*) FROM $t'" 2>/dev/null | tr -dc '0-9')"
      rest="$(compter "$base" "$t")"
      # La production a pu bouger depuis la sauvegarde : on exige seulement que la restauration ne soit pas vide.
      case " ${tables_usage[*]} " in
        *" $t "*) case "$t" in
                    users_user) [ -n "$rest" ] && [ "$rest" -gt 0 ] || ok=false ;;
                    *) [ -n "$rest" ] || ok=false ;;
                  esac ;;
        *) [ -n "$rest" ] && [ "$rest" -gt 0 ] || ok=false ;;
      esac
      sortie+="$sep\"$t\":{\"production\":${orig:-0},\"restauree\":${rest:-0}}"; sep=","
    done
    "${COMPOSE[@]}" exec -T db sh -c "dropdb -U \"\$POSTGRES_USER\" --if-exists $base" >/dev/null 2>&1
    sortie+='}}'
    if $ok; then printf '%s\n' "$sortie"; else printf '%s\n' "${sortie/\"ok\"/\"refuse\"}"; exit 1; fi
    ;;

  *)
    echec 2 "sous-commande inconnue"
    ;;
esac
