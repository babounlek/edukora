"""
Stockage des images de notes (access.models.NoteLibre.image) : privé, comme les PDF de fiches (voir fiches.storage). Une
photo de brouillon ou de cahier est personnelle : jamais public-read, jamais d'URL construite côté client. Seul point de
sortie : access.views.note_image, qui vérifie que la note est celle du profil actif puis renvoie le fichier.

Un callable (et non la valeur résolue) : il se sérialise proprement dans les migrations.
"""

from django.core.files.storage import storages


def protected_storage():
    return storages["notes_protected"]
