# Basé sur postgres:17-alpine (et non un alpine nu + paquet postgresql-client) pour
# garantir que pg_dump/pg_restore matchent exactement la version du serveur de
# production - un client plus ancien que le serveur peut échouer ou tronquer le dump.
FROM postgres:17-alpine

RUN apk add --no-cache bash rclone tzdata

WORKDIR /app

COPY docker/backup/backup.sh docker/backup/restore.sh docker/backup/sync_media.sh ./
COPY docker/backup/crontab /etc/crontabs/root

RUN chmod +x backup.sh restore.sh sync_media.sh && chmod 600 /etc/crontabs/root

# -f : premier plan (le conteneur doit rester actif) - -d 8 : logs sur stderr au
# lieu de syslog, pour qu'ils remontent dans `docker compose logs backup`.
ENTRYPOINT ["crond", "-f", "-d", "8"]
