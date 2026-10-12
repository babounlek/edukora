#!/usr/bin/env bash
# Mise à jour du CONTENU (cours, épreuves, inédites, quiz, programme) de la prod, PAR
# L'APPLICATION : on ne copie jamais de base, on rejoue les commandes d'ingestion de Django sur
# les JSON versionnés dans git. À lancer sur le serveur, normalement par .github/workflows/contenu.yml.
#
#   deploy/contenu.sh auto                    # tout ce qui a changé depuis la dernière mise à jour
#   deploy/contenu.sh auto --depuis <commit>  # idem, depuis un commit précis
#   deploy/contenu.sh auto --tout             # premier chargement : TOUS les dossiers
#   deploy/contenu.sh auto --simulation       # affiche ce qui serait fait, ne touche à rien
#
# La version du contenu est celle du commit DÉPLOYÉ (.deploy/current_tag, écrit par deploy.sh) :
# contenu et application restent toujours alignés. Déployez d'abord l'application, ensuite le contenu.
#
# Ordre fixe, imposé par les dépendances : programme officiel -> corrections (Lesson/Exercise/Cours)
# -> épreuves inédites -> quiz. Puis portes de validation de la base (valider_ingestion --since)
# et reconstruction de l'index de recherche.
#
# LIMITE CONNUE : les commandes d'ingestion IGNORENT ce qui existe déjà (clé external_id / titre).
# Modifier un JSON déjà ingéré n'a donc AUCUN effet ici. Une correction de contenu existant passe
# par (1) l'action admin « Réingérer depuis le fichier JSON » pour un exercice, ou (2) une commande
# de correctif versionnée et idempotente (comme quiz/management/commands/appliquer_correctifs_*).
# Le rapport signale les fichiers modifiés qui sont dans ce cas.
#
# La porte de rendu KaTeX (vitest) n'est pas rejouée ici : le serveur n'a pas Node. Elle reste
# une condition de commit, validée en local par scripts/tunnel_validation.sh.
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"
ETAT="$ROOT/.deploy"
mkdir -p "$ETAT"

[ "${1:-}" = "auto" ] || { sed -n '2,25p' "$0"; exit 2; }
shift

DEPUIS=""
TOUT=0
SIMULATION=0
STRICT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --depuis) DEPUIS="${2:?--depuis demande un commit}"; shift ;;
    --tout) TOUT=1 ;;
    --simulation) SIMULATION=1 ;;
    --strict) STRICT="--strict" ;;
    *) echo "Option inconnue : $1" >&2; exit 2 ;;
  esac
  shift
done

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
log() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

# --- Version cible et point de départ -----------------------------------------------------
CIBLE="$(git rev-parse HEAD)"
DEPLOYE="$(cat "$ETAT/current_tag" 2>/dev/null || true)"
if [ -n "$DEPLOYE" ] && [ "$(git rev-parse "$DEPLOYE" 2>/dev/null || echo x)" != "$CIBLE" ]; then
  echo "Le clone est sur $(git rev-parse --short HEAD) mais la version déployée est $DEPLOYE :" >&2
  echo "alignez-les (git checkout --detach $DEPLOYE) pour que contenu et application concordent." >&2
  [ "$SIMULATION" = 1 ] || exit 1
fi

if [ "$TOUT" = 1 ]; then
  BASE=""
elif [ -n "$DEPUIS" ]; then
  BASE="$DEPUIS"
elif [ -f "$ETAT/contenu_commit" ]; then
  BASE="$(cat "$ETAT/contenu_commit")"
else
  echo "Aucun point de départ : c'est le premier chargement. Utilisez --tout (tout ingérer) ou --depuis <commit>." >&2
  exit 1
fi
log "Contenu : ${BASE:-(tout)} -> $(git rev-parse --short "$CIBLE")"

# --- Fichiers concernés ------------------------------------------------------------------
if [ -z "$BASE" ]; then
  LISTE="$(git ls-files backend/ingest backend/programme/fixtures | grep '\.json$' || true)"
  MODIFIES=""
else
  LISTE="$(git diff --name-only --diff-filter=A "$BASE" "$CIBLE" -- backend/ingest backend/programme/fixtures | grep '\.json$' || true)"
  MODIFIES="$(git diff --name-only --diff-filter=M "$BASE" "$CIBLE" -- backend/ingest backend/programme/fixtures | grep '\.json$' | grep -Ev '/_(audit|quiz/_|batch)' || true)"
fi

PROGRAMMES=(); DOSSIERS=(); INEDITES=(); QUIZ=()
declare -A VU=()
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in
    backend/programme/fixtures/*.json) PROGRAMMES+=("/app/${f#backend/}") ;;
    backend/ingest/_inedit/*) INEDITES+=("/app/${f#backend/}") ;;
    backend/ingest/_quiz/*/*) QUIZ+=("/app/${f#backend/}") ;;
    backend/ingest/_*) ;;   # _audit, brouillons, journaux : jamais ingérés
    backend/ingest/*/*/*)
      dossier="$(echo "$f" | cut -d/ -f3-4)"   # <pays>/<dossier>
      if [ -z "${VU[$dossier]:-}" ]; then VU[$dossier]=1; DOSSIERS+=("/app/ingest/$dossier"); fi ;;
  esac
done <<< "$LISTE"

log "À ingérer : ${#PROGRAMMES[@]} programme(s), ${#DOSSIERS[@]} dossier(s) de corrections, ${#INEDITES[@]} fichier(s) inédites, ${#QUIZ[@]} fichier(s) quiz."
if [ -n "$MODIFIES" ]; then
  log "ATTENTION - fichiers MODIFIÉS (déjà ingérés, donc ignorés par l'ingestion) :"
  echo "$MODIFIES" | sed 's/^/    /'
  log "Les appliquer demande une réingestion admin ou une commande de correctif (voir l'en-tête)."
fi

if [ "$SIMULATION" = 1 ]; then
  log "SIMULATION : rien n'est exécuté."
  for p in "${PROGRAMMES[@]}"; do echo "  load_programme_officiel $p"; done
  for d in "${DOSSIERS[@]}"; do echo "  ingest_corrections $d"; done
  for i in "${INEDITES[@]}"; do echo "  ingest_inedit_content $i"; done
  for q in "${QUIZ[@]}"; do echo "  ingest_quiz_content $q"; done
  echo "  valider_ingestion --since <début> ${STRICT}"
  echo "  indexer_recherche"
  exit 0
fi

# --- Exécution ---------------------------------------------------------------------------
manage() { "${COMPOSE[@]}" exec -T backend python manage.py "$@" 2>&1; }

DEBUT="$("${COMPOSE[@]}" exec -T backend date -u -d '1 minute ago' +%Y-%m-%dT%H:%M:%S+00:00)"
ECHECS=0

lancer() {  # lancer <commande> <chemin>
  local sortie
  sortie="$(manage "$1" "$2" || true)"
  echo "$sortie" | tail -n 6
  if echo "$sortie" | grep -qE 'erreur\(s\) :|CommandError|Traceback'; then
    log "ERREUR sur $1 $2"
    ECHECS=$((ECHECS + 1))
  fi
}

for p in "${PROGRAMMES[@]}"; do lancer load_programme_officiel "$p"; done
for d in "${DOSSIERS[@]}"; do lancer ingest_corrections "$d"; done
for i in "${INEDITES[@]}"; do lancer ingest_inedit_content "$i"; done
for q in "${QUIZ[@]}"; do lancer ingest_quiz_content "$q"; done

if [ "$ECHECS" -gt 0 ]; then
  echo "$ECHECS ingestion(s) en erreur : corrigez les JSON sources, repoussez, relancez. Point de départ NON avancé." >&2
  exit 1
fi

log "Portes de validation de la base..."
if ! manage valider_ingestion --since "$DEBUT" $STRICT; then
  echo "valider_ingestion a échoué : contenu ingéré mais NON validé. Point de départ NON avancé." >&2
  exit 1
fi

log "Index de la recherche globale..."
manage indexer_recherche | tail -n 3

echo "$CIBLE" > "$ETAT/contenu_commit"
echo "$(date -u +%FT%TZ) contenu jusqu'a $CIBLE (depuis ${BASE:-tout})" >> "$ETAT/historique.log"
log "Contenu à jour : $(git rev-parse --short "$CIBLE")"
