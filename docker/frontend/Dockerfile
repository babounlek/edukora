FROM node:22-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/. ./

RUN ls -la

RUN find /app -maxdepth 2

RUN npm run build