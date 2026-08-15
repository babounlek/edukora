"""
Callable de storage pour FicheGeneree.sujet_pdf/corrige_pdf - jamais la valeur
`storages(...)` résolue directement dans models.py (voir inedit.storage, même
raisonnement : un callable reste correct même si le backend/l'environnement du
process courant n'était pas garanti chargé au moment de l'import, et sérialise
proprement dans les migrations comme `fiches.storage.protected_storage`).

Voir edtech_cm.settings.STORAGES["fiches_protected"] pour ce que ce storage est
réellement (S3 privé en prod, un dossier hors MEDIA_ROOT jamais servi en dev/tests) -
un emplacement dédié, distinct de "inedit_protected" bien qu'identique en substance :
une fiche de répétiteur n'a rien à voir avec une Épreuve Inédite, mélanger les deux
storages compliquerait inutilement un futur changement de rétention/politique propre
à l'un des deux.
"""

from django.core.files.storage import storages


def protected_storage():
    return storages["fiches_protected"]
