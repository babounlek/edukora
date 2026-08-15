# --- Stage 1 : build frontend React/Vite ---
FROM node:22-alpine AS frontend-build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ .

ARG VITE_API_BASE_URL=
ARG VITE_SITE_NAME=EduKora
ARG VITE_SITE_URL=https://edukora.africa
ARG VITE_SENTRY_DSN=
# Identifiant client OAuth Google, identique à GOOGLE_CLIENT_ID côté backend (voir
# users.google) - la vérification de la claim `aud` échoue si les deux divergent.
# Doit être un ARG et non une variable d'exécution : Vite fige les VITE_* dans le
# bundle au moment du build, un `docker compose up` avec la variable dans .env
# n'aurait aucun effet sur du JavaScript déjà compilé. Vide par défaut = bouton
# Google absent et backend en 503, ce qui reste l'état voulu tant que la console
# Google n'est pas configurée.
ARG VITE_GOOGLE_CLIENT_ID=

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_SITE_NAME=${VITE_SITE_NAME}
ENV VITE_SITE_URL=${VITE_SITE_URL}
ENV VITE_SENTRY_DSN=${VITE_SENTRY_DSN}
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}

RUN npm run build


# --- Stage 2 : serveur Caddy ---
FROM caddy:2-alpine

COPY --from=frontend-build /app/dist /srv/frontend

COPY docker/caddy/Caddyfile /etc/caddy/Caddyfile