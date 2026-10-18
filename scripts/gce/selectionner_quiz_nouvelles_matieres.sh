#!/usr/bin/env bash
# Sélection brute (select_quiz_batch, --limit 400) pour chaque matière GCE sans quiz, écrite dans
# backend/ingest/_quiz/_sel_<CODE>.json (dossier partagé avec le conteneur). Étape 1 de preparer_quiz_vague.js.
set -u
export MSYS_NO_PATHCONV=1  # Git Bash réécrirait /app/... en C:/Program Files/Git/app/...
cd "$(dirname "$0")/../.."
while read -r m; do
  [ -z "$m" ] && continue
  docker exec edukora-backend-1 python manage.py select_quiz_batch --pays cm --matiere "$m" --limit 400 --floor 6 \
    --output "/app/ingest/_quiz/_sel_${m}.json" > /dev/null 2>&1
  echo "$m -> $(node -e "try{console.log(JSON.parse(require('fs').readFileSync('backend/ingest/_quiz/_sel_${m}.json','utf8')).length)}catch(e){console.log('ECHEC')}")"
done < backend/ingest/_quiz/_codes_gce_nouveaux.txt
