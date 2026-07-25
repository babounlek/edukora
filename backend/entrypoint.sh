#!/bin/bash
set -euo pipefail

# db healthy (voir la condition service_healthy de docker-compose.yml) garantit déjà
# que Postgres accepte des connexions avant que ce script démarre - migrate peut donc
# s'exécuter directement, sans boucle d'attente supplémentaire ici.

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn edtech_cm.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 30 \
    --access-logfile - \
    --error-logfile -
