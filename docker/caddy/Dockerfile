# --- Stage 1 : build frontend React/Vite ---
FROM node:22-alpine AS frontend-build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ .

ARG VITE_API_BASE_URL=
ARG VITE_SITE_NAME=EduKora
ARG VITE_SITE_URL=https://edukora.africa

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_SITE_NAME=${VITE_SITE_NAME}
ENV VITE_SITE_URL=${VITE_SITE_URL}

RUN npm run build


# --- Stage 2 : serveur Caddy ---
FROM caddy:2-alpine

COPY --from=frontend-build /app/dist /srv/frontend

COPY docker/caddy/Caddyfile /etc/caddy/Caddyfile