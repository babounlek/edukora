"""
PDF « sujet » d'une épreuve classique (Lesson.sujet_pdf) : public par nature (support marketing, jamais le corrigé),
mais SERVI par Django, jamais par une adresse directe, pour que le quota de téléchargements s'applique (voir
access.quota). L'API n'expose plus que l'adresse de cette route.

Le fichier peut être sur le disque (contenu historique, que Caddy servait depuis MEDIA_ROOT) ou sur le stockage par
défaut (Spaces pour les fichiers récents) : on essaie le disque d'abord, comme catalog.sujet_pdf._resolve_media_paths.
"""
from pathlib import Path

from django.conf import settings


def url_sujet(request, lesson):
    """Adresse de la route de téléchargement (absolue si on a la requête), ou None si le sujet n'a pas de PDF."""
    if not lesson.sujet_pdf:
        return None
    chemin = f"/access/lessons/{lesson.pk}/sujet.pdf"
    return request.build_absolute_uri(chemin) if request is not None else chemin


def ouvrir_sujet(lesson):
    local = Path(settings.MEDIA_ROOT) / lesson.sujet_pdf.name
    if local.is_file():
        return open(local, "rb")
    return lesson.sujet_pdf.open("rb")
