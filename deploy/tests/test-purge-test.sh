#!/usr/bin/env bash
# Tests des gardes de deploy/purge-test.sh avec un faux `docker` (rien n'est exécuté en vrai).
#   docker cp deploy edukora-backend-1:/tmp/deploy-tests && docker exec edukora-backend-1 bash /tmp/deploy-tests/tests/test-purge-test.sh
set -uo pipefail
ICI="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d /tmp/test-purge-test.XXXXXX)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/repo/deploy" "$T/bin" "$T/lots/sauvegardes" "$T/lots/purge"
cp "$ICI/purge-test.sh" "$T/repo/deploy/"; chmod +x "$T/repo/deploy/purge-test.sh"
touch "$T/repo/docker-compose.yml"
cat > "$T/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "docker $*" >> "$FAKE/appels.log"
case "$*" in
  *"purger_donnees_test executer"*) echo '{"statut":"ok","comptes":{"supprimes":1}}' ;;
  *"purger_donnees_test simuler"*) echo '{"statut":"ok","jeton":"0123456789abcdef0123"}' ;;
esac
exit 0
STUB
chmod +x "$T/bin/docker"
export EDUKORA_REPO="$T/repo" FAKE="$T" PATH="$T/bin:$PATH" EDUKORA_LOTS_DIR="$T/lots"
PT="$T/repo/deploy/purge-test.sh"
OK=0; KO=0
verif() { if [ "$2" = "$3" ]; then OK=$((OK+1)); echo "  ok   - $1"; else KO=$((KO+1)); echo "  FAIL - $1 (attendu $2, obtenu $3)"; fi; }
DUMP="avant-20261101-100000-0123abcd.dump"; JETON="0123456789abcdef0123"
echo '{"version":1,"comptes":[]}' > "$T/lots/purge/perimetre.json"
: > "$T/appels.log"

echo "== gardes de executer =="
"$PT" executer "../../etc/passwd" "$JETON" >/dev/null; verif "nom de dump invalide refusé (2)" 2 $?
"$PT" executer "$DUMP" "pas-un-jeton" >/dev/null; verif "jeton invalide refusé (2)" 2 $?
"$PT" executer "$DUMP" "$JETON" >/dev/null; verif "dump introuvable refusé (2)" 2 $?
: > "$T/lots/sauvegardes/$DUMP"
"$PT" executer "$DUMP" "$JETON" >/dev/null; verif "sans copie hors site refusé (2)" 2 $?
: > "$T/lots/sauvegardes/$DUMP.hors-site"
"$PT" executer "$DUMP" "$JETON" >/dev/null; verif "sans restauration testée refusé (2)" 2 $?
: > "$T/lots/sauvegardes/$DUMP.restauration-ok"
touch -d '3 days ago' "$T/lots/sauvegardes/$DUMP"
"$PT" executer "$DUMP" "$JETON" >/dev/null; verif "dump trop ancien refusé (2)" 2 $?
grep -q "purger_donnees_test executer" "$T/appels.log"; verif "aucune exécution lancée pendant les refus" 1 $?
touch "$T/lots/sauvegardes/$DUMP"
sortie="$("$PT" executer "$DUMP" "$JETON")"; verif "toutes les gardes remplies : exécution (0)" 0 $?
grep -q "ALLOW_TEST_DATA=1" "$T/appels.log"; verif "ALLOW_TEST_DATA passé à la commande" 0 $?
grep -q "PURGE_SAUVEGARDE_VERIFIEE=$DUMP" "$T/appels.log"; verif "dump vérifié passé à la commande" 0 $?
grep -q -- "--confirme-production" "$T/appels.log"; verif "--confirme-production passé" 0 $?

echo "== verrou partagé =="
( exec 9>"$T/lots/.sync.lock"; flock -n 9; "$PT" executer "$DUMP" "$JETON" >/dev/null; echo $? > "$T/code" ) 
verif "verrou pris par un lot : 75" 75 "$(cat "$T/code")"

echo "== autres =="
"$PT" inconnue >/dev/null; verif "sous-commande inconnue (2)" 2 $?
rm "$T/lots/purge/perimetre.json"
"$PT" simuler >/dev/null; verif "simulation sans périmètre refusée (2)" 2 $?
echo; echo "$OK/$((OK+KO)) vérifications réussies"; [ "$KO" = 0 ]
