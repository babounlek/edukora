import os

from django.db import connection
from django.http import JsonResponse


def healthz(request):
    """
    Point de contrôle du déploiement (deploy/deploy.sh) et de la supervision externe.

    Contrairement à la page d'accueil (servie par Caddy, qui répond même backend à l'arrêt),
    celle-ci traverse Caddy -> Django -> Postgres : un 200 prouve que la chaîne complète vit.
    `version` est l'étiquette d'image injectée par le déploiement (APP_VERSION) : le script
    vérifie qu'elle est bien celle qu'il vient de lancer, et non celle d'un conteneur resté
    de l'ancienne version. Aucune donnée sensible, aucune écriture.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "db_indisponible"}, status=503)
    return JsonResponse({"status": "ok", "version": os.environ.get("APP_VERSION", "dev")})
