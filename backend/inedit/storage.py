"""
Callable de storage pour EpreuveInedite.sujet_pdf - jamais la valeur `storages(...)`
résolue directement dans models.py, qui figerait le backend au moment de l'import (avant
que les settings/l'environnement du process courant ne soient garantis chargés) ; un
callable est le pattern documenté par Django pour un FileField dont le storage doit
rester résolu paresseusement, et sérialise proprement dans les migrations
(`inedit.storage.protected_storage`, pas un objet backend figé).

Voir edtech_cm.settings.STORAGES["inedit_protected"] pour ce que ce storage est
réellement (S3 privé en prod, un dossier hors MEDIA_ROOT jamais servi en dev/tests) -
jamais le même storage "default" que Figure.image/Lesson.sujet_pdf, public par nature.
"""

from django.core.files.storage import storages


def protected_storage():
    return storages["inedit_protected"]
