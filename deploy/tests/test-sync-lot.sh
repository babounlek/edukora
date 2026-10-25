#!/usr/bin/env bash
# Tests de deploy/sync-lot.sh et du verrou partagé (deploy.sh, contenu.sh) avec un faux `docker`.
# Nécessite bash, flock, setsid, sha256sum, stat, find : un Linux (le conteneur backend convient).
#
#   docker cp deploy edukora-backend-1:/tmp/deploy-tests && docker exec edukora-backend-1 bash /tmp/deploy-tests/tests/test-sync-lot.sh
#
# Rien n'est exécuté en vrai : `docker` est remplacé par un script qui journalise ses appels.
set -uo pipefail

ICI="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d /tmp/test-sync-lot.XXXXXX)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/repo/deploy" "$T/bin" "$T/fake" "$T/lots"
cp "$ICI/sync-lot.sh" "$ICI/deploy.sh" "$ICI/contenu.sh" "$T/repo/deploy/"
chmod +x "$T/repo/deploy/"*.sh
touch "$T/repo/docker-compose.yml" "$T/repo/docker-compose.prod.yml"

cat > "$T/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "IMAGE_TAG=${IMAGE_TAG:-} docker $*" >> "$FAKE/appels.log"
args="$*"
case "$args" in
  *" cp "*)
    src="${@: -2:1}"; dst="${@: -1}"
    cp "$src" "$FAKE/copie-$(basename "${dst#*:}")" ;;
  *"mkdir -p"*) ;;
  *"sync_contenu recevoir"*) echo "(0.001) SELECT 1;"; echo '{"batch_id": "x", "statut": "verifie", "operations": 3, "dossier": "/tmp/lots/x"}' ;;
  *"sync_contenu planifier"*) echo '{"batch_id": "x", "compteurs": {"cree": 3}, "bloquants": 0, "plan": []}' ;;
  *"sync_contenu statut"*) cat "$FAKE/statut.json" ;;
  *"sync_contenu appliquer"*|*"sync_contenu reprendre"*|*"sync_contenu post-traiter"*)
    sleep "${FAKE_SECONDES:-2}"; echo '{"statut": "reussi"}' ;;
  *"sync_contenu exporter-reference"*) echo '{"genere_le": "2026-10-25T00:00:00Z", "contenus": {}}' ;;
  *"sync_contenu verifier-fichiers"*) echo '{"references_sans_fichier": [], "sha_divergents": []}' ;;
  *"sync_contenu nettoyer"*) echo '{"candidats": [], "supprimes": [], "conserves_car_references": []}' ;;
  *"help sync_contenu"*) echo "usage" ;;
  *"pg_dump"*) head -c "${FAKE_DUMP_OCTETS:-5000}" /dev/zero ;;
  *"pg_restore --list"*)
    cat > /dev/null
    printf '100; 0 1 TABLE DATA public catalog_lesson -\n101; 0 2 TABLE DATA public catalog_exercise -\n102; 0 3 TABLE DATA public catalog_question -\n' ;;
  *"backup.sh"*) [ "${FAKE_BACKUP_KO:-0}" = 1 ] && exit 1; true ;;
  *" info"*) ;;
  *) ;;
esac
exit 0
STUB
chmod +x "$T/bin/docker"

export PATH="$T/bin:$PATH" FAKE="$T/fake" EDUKORA_LOTS_DIR="$T/lots"
SL="$T/repo/deploy/sync-lot.sh"
BATCH="20261025-101500-abcd1234"

echec=0; total=0
verifier() {  # verifier <description> <condition shell>
  total=$((total + 1))
  if eval "$2"; then echo "  ok   - $1"; else echo "  ECHEC - $1"; echec=$((echec + 1)); fi
}
lancer() { OUT="$("$@" 2>"$T/err")"; CODE=$?; }

echo "== arguments =="
lancer "$SL" inconnue
verifier "sous-commande inconnue refusée (2)" '[ $CODE = 2 ] && [[ "$OUT" == *refuse* ]]'
lancer "$SL"
verifier "sans sous-commande : usage (2)" '[ $CODE = 2 ]'
for sous in ouvrir-lot verifier-archive recevoir sauvegarde planifier appliquer reprendre statut post-traiter; do
  for mauvais in "" "bad" "../etc" "20261025-101500-ABCD1234" "20261025-101500-abcd1234;touch /tmp/pwn" '$(id)'; do
    lancer "$SL" "$sous" "$mauvais"
    verifier "$sous refuse le batch_id « $mauvais »" '[ $CODE = 2 ] && [[ "$OUT" == *refuse* ]]'
  done
done
verifier "aucune commande injectée" '[ ! -e /tmp/pwn ]'
lancer "$SL" sauvegarde "$BATCH" --max-age-h abc
verifier "entier invalide refusé" '[ $CODE = 2 ]'
lancer "$SL" appliquer "$BATCH" --nimporte-quoi
verifier "option inconnue refusée" '[ $CODE = 2 ]'
lancer "$SL" test-restauration "../../etc/passwd"
verifier "nom de sauvegarde invalide refusé" '[ $CODE = 2 ]'

echo "== dossiers =="
EDUKORA_LOTS_DIR=/etc/hostname/lots lancer "$SL" preparer-dossiers
verifier "dossier racine impossible a creer : echec explicite (1), pas de faux ok" '[ $CODE = 1 ] && [[ "$OUT" == *refuse* ]] && [[ "$OUT" == *"sudo install"* ]]'
rm -rf "$T/lots"
lancer "$SL" preparer-dossiers
verifier "dossiers créés en 700" '[ "$(stat -c %a "$T/lots")" = 700 ] && [ "$(stat -c %a "$T/lots/incoming")" = 700 ]'
lancer "$SL" diagnostic
verifier "diagnostic en JSON" '[[ "$OUT" == *\"docker\":true* ]] && [[ "$OUT" == *\"dossier_lots\":true* ]] && [[ "$OUT" == *\"commande_sync_contenu\":true* ]]'

echo "== archive =="
lancer "$SL" ouvrir-lot "$BATCH"
verifier "ouvrir-lot crée incoming/<id> en 700" '[ $CODE = 0 ] && [ "$(stat -c %a "$T/lots/incoming/$BATCH")" = 700 ]'
printf 'contenu du lot' > "$T/lots/incoming/$BATCH/lot.zip"
lancer "$SL" verifier-archive "$BATCH"
verifier "archive sans .sha256 refusée (1)" '[ $CODE = 1 ]'
sha256sum "$T/lots/incoming/$BATCH/lot.zip" | awk '{print $1"  lot.zip"}' > "$T/lots/incoming/$BATCH/lot.zip.sha256"
lancer "$SL" verifier-archive "$BATCH"
verifier "SHA-256 correcte acceptée" '[ $CODE = 0 ] && [[ "$OUT" == *\"statut\":\"ok\"* ]]'
printf 'altere' >> "$T/lots/incoming/$BATCH/lot.zip"
lancer "$SL" verifier-archive "$BATCH"
verifier "archive altérée refusée (1)" '[ $CODE = 1 ] && [[ "$OUT" == *corrompu* ]]'
printf 'contenu du lot' > "$T/lots/incoming/$BATCH/lot.zip"

echo "== réception et simulation =="
: > "$FAKE/appels.log"
lancer "$SL" recevoir "$BATCH"
verifier "recevoir renvoie la réponse JSON de la commande" '[ $CODE = 0 ] && [[ "$OUT" == *verifie* ]] && [[ "$OUT" != *SELECT* ]]'
verifier "l archive est copiée dans le conteneur" '[ -f "$FAKE/copie-$BATCH.zip" ]'
SHA="$(awk "{print \$1}" "$T/lots/incoming/$BATCH/lot.zip.sha256")"
verifier "la SHA-256 est transmise à la commande" 'grep -q -- "--sha256 $SHA" "$FAKE/appels.log"'
: > "$FAKE/appels.log"
lancer "$SL" planifier "$BATCH"
verifier "planifier reçoit d abord le lot (idempotent) puis simule" \
  'a=$(grep -n "sync_contenu recevoir" "$FAKE/appels.log" | head -1 | cut -d: -f1); b=$(grep -n "sync_contenu planifier" "$FAKE/appels.log" | head -1 | cut -d: -f1); [ -n "$a" ] && [ -n "$b" ] && [ "$a" -lt "$b" ] && [[ "$OUT" == *bloquants* ]]'

echo "== sauvegarde =="
lancer "$SL" sauvegarde "$BATCH"
verifier "sauvegarde vérifiée créée en 600" '[ $CODE = 0 ] && [[ "$OUT" == *\"hors_site\":true* ]] && [ "$(stat -c %a "$T/lots/sauvegardes/avant-$BATCH.dump")" = 600 ]'
lancer "$SL" sauvegarde "$BATCH" --max-age-h 24
verifier "sauvegarde récente réutilisée pour un lot de créations" '[ $CODE = 0 ] && [[ "$OUT" == *\"reutilisee\":true* ]]'
rm -f "$T/lots/sauvegardes/"*
FAKE_DUMP_OCTETS=10 lancer "$SL" sauvegarde "$BATCH"
verifier "dump trop petit refusé, aucun fichier laissé" '[ $CODE = 1 ] && [ -z "$(ls "$T/lots/sauvegardes")" ]'
FAKE_BACKUP_KO=1 lancer "$SL" sauvegarde "20261025-101501-abcd1234"
verifier "échec de la copie hors site : l opération échoue (1)" '[ $CODE = 1 ] && [[ "$OUT" == *hors* ]]'
verifier "un dump dont la copie hors site a échoué n a PAS de marqueur" '[ -f "$T/lots/sauvegardes/avant-20261025-101501-abcd1234.dump" ] && [ ! -f "$T/lots/sauvegardes/avant-20261025-101501-abcd1234.dump.hors-site" ]'
lancer "$SL" sauvegarde "20261025-101502-abcd1234" --max-age-h 24
verifier "ce dump sans copie hors site n est JAMAIS réutilisé : une sauvegarde complète est refaite" '[ $CODE = 0 ] && [[ "$OUT" == *\"reutilisee\":false* ]] && [ -f "$T/lots/sauvegardes/avant-20261025-101502-abcd1234.dump.hors-site" ]'
lancer "$SL" sauvegarde "20261025-101503-abcd1234" --max-age-h 24
verifier "avec marqueur : la sauvegarde recente est reutilisee" '[ $CODE = 0 ] && [[ "$OUT" == *\"reutilisee\":true* ]] && [[ "$OUT" == *avant-20261025-101502-abcd1234.dump* ]]'
rm -f "$T/lots/sauvegardes/"*

echo "== application détachée et verrou =="
export FAKE_SECONDES=3
debut=$(date +%s)
lancer "$SL" appliquer "$BATCH"
fin=$(date +%s)
verifier "appliquer rend la main aussitôt (< 3 s) avec « lance »" '[ $((fin - debut)) -lt 3 ] && [[ "$OUT" == *\"statut\":\"lance\"* ]]'
sleep 1
verifier "le verrou est tenu pendant l exécution" '! ( exec 9>"$T/lots/.sync.lock"; flock -n 9 )'
lancer "$SL" appliquer "$BATCH"
verifier "un second lot est refusé pendant ce temps (75)" '[ $CODE = 75 ] && [[ "$OUT" == *verrou_pris* ]]'
lancer "$SL" nettoyer
verifier "nettoyer est refusé pendant un lot (75)" '[ $CODE = 75 ]'
# deploy.sh et contenu.sh respectent le même verrou
lancer "$T/repo/deploy/deploy.sh" 1234567
verifier "deploy.sh refuse de démarrer pendant un lot (1)" '[ $CODE = 1 ] && grep -q "lot de contenu" "$T/err"'
lancer "$T/repo/deploy/contenu.sh" auto
verifier "contenu.sh refuse de démarrer pendant un lot (1)" '[ $CODE = 1 ] && grep -q "verrou" "$T/err"'
sleep 4
verifier "le journal consigne la fin du lot" 'grep -q "fin (code 0)" "$T/lots/journaux/$BATCH.log"'
verifier "le verrou est libéré à la fin" '( exec 9>"$T/lots/.sync.lock"; flock -n 9 )'
lancer "$T/repo/deploy/deploy.sh" 1234567
verifier "verrou libre : deploy.sh passe au contrôle suivant (.env absent)" '[ $CODE = 1 ] && grep -q "\.env introuvable" "$T/err"'
unset FAKE_SECONDES

echo "== versions : image de production ou pile construite sur place =="
rm -rf "$T/repo/.deploy"
: > "$FAKE/appels.log"
lancer "$SL" statut "$BATCH"
verifier "sans .deploy/current_tag : compose de base seul, sans IMAGE_TAG"   '! grep -q "docker-compose.prod.yml" "$FAKE/appels.log" && grep -q "^IMAGE_TAG= docker compose exec" "$FAKE/appels.log"'
mkdir -p "$T/repo/.deploy"; echo "0123abc" > "$T/repo/.deploy/current_tag"
: > "$FAKE/appels.log"
lancer "$SL" statut "$BATCH"
verifier "apres deploy.sh : override de production et IMAGE_TAG = version deployee"   'grep -q "docker-compose.prod.yml" "$FAKE/appels.log" && grep -q "^IMAGE_TAG=0123abc docker compose" "$FAKE/appels.log"'
echo "tag: 0123abc\$(id)" > "$T/repo/.deploy/current_tag"
: > "$FAKE/appels.log"
lancer "$SL" statut "$BATCH"
verifier "un current_tag corrompu ne peut rien injecter (caracteres hors [0-9a-f] retires)"   'grep -q "^IMAGE_TAG=0abc docker" "$FAKE/appels.log" || grep -q "^IMAGE_TAG=" "$FAKE/appels.log"'
rm -rf "$T/repo/.deploy"

echo "== consultation =="
echo '{"batch_id": "x", "statut": "reussi", "compteurs": {"cree": 3}}' > "$FAKE/statut.json"
lancer "$SL" statut "$BATCH"
verifier "statut transmet la réponse du moteur" '[[ "$OUT" == *reussi* ]]'
lancer "$SL" reference
verifier "reference renvoie le JSON des empreintes" '[[ "$OUT" == *contenus* ]]'
lancer "$SL" verifier-fichiers
verifier "verifier-fichiers renvoie son rapport" '[[ "$OUT" == *references_sans_fichier* ]]'

echo
echo "$((total - echec))/$total vérifications réussies"
[ "$echec" = 0 ]
