#!/bin/bash
set -euo pipefail

# db healthy (voir la condition service_healthy de docker-compose.yml) garantit déjà
# que Postgres accepte des connexions avant que ce script démarre - migrate peut donc
# s'exécuter directement, sans boucle d'attente supplémentaire ici.

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Index de la recherche globale : construit une seule fois, au tout premier démarrage (--si-vide ne
# fait rien dès qu'il existe), et EN ARRIÈRE-PLAN - une trentaine de secondes qui ne doivent pas
# retarder gunicorn. Ensuite il se rafraîchit à la demande (manage.py indexer_recherche, lancé
# par scripts/ingerer_et_valider.sh après un lot). Un échec n'arrête jamais le démarrage.
(python manage.py indexer_recherche --si-vide || echo "Indexation de la recherche en échec (voir ci-dessus).") &

echo "Starting gunicorn..."
# GUNICORN_RELOAD=1 (voir docker-compose.dev.yml) : worker redémarré sur toute
# modification d'un fichier .py source - seule façon de voir un changement de code
# sans docker cp + rebuild quand /app est bind-mounté sur le dépôt en dev solo (voir
# feedback_docker_backend_no_bind_mount_safe_patch : par défaut, sans ce fichier
# override, l'image reste figée - toujours le mode sûr en cas de session concurrente).
# Jamais activé en prod (GUNICORN_RELOAD absent de .env côté serveur).
RELOAD_FLAG=()
if [ "${GUNICORN_RELOAD:-0}" = "1" ]; then
    echo "Rechargement automatique activé (GUNICORN_RELOAD=1)."
    RELOAD_FLAG=(--reload)
fi
exec gunicorn edtech_cm.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    "${RELOAD_FLAG[@]}"
