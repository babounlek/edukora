from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = "catalog"

    def ready(self):
        # Branche le signal qui dépublie l'avis d'un profil supprimé (voir catalog.avis._depublier_les_avis).
        from . import avis  # noqa: F401
