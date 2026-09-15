"""
Callable de storage pour QuizSession.fiche_pdf - jamais la valeur `storages(...)`
résolue directement dans models.py (voir fiches.storage/inedit.storage, même
raisonnement : un callable reste correct même si le backend/l'environnement du process
courant n'était pas garanti chargé au moment de l'import, et sérialise proprement dans
les migrations comme `quiz.storage.protected_storage`).

Voir edtech_cm.settings.STORAGES["quiz_protected"] pour ce que ce storage est
réellement (S3 privé en prod, un dossier hors MEDIA_ROOT jamais servi en dev/tests).
"""

from django.core.files.storage import storages


def protected_storage():
    return storages["quiz_protected"]
