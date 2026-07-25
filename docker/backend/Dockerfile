# Image officielle Playwright : Chromium + toutes ses dépendances système
FROM mcr.microsoft.com/playwright/python:v1.61.0-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=edtech_cm.settings

WORKDIR /app

# Installation des dépendances Python
COPY backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Vérifie que la version de Chromium attendue est bien installée
RUN python -m playwright install --with-deps chromium

# Copie du backend Django
COPY backend/ .

# Rend le script de démarrage exécutable
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]