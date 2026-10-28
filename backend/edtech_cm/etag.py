"""ETag et réponses 304 pour les GET JSON de l'API.

Sur une connexion mobile payée au Mo, le gros du poids d'une visite répétée est l'API : listes de
catalogue, matières, cursus... qui n'ont presque jamais changé depuis la dernière visite. Le
navigateur les redemande (sans date de fraîcheur, il revalide à chaque fois) et le serveur renvoyait
tout le corps. Avec un ETag (empreinte du corps), il répond 304 sans corps quand rien n'a bougé.

Aucun risque d'exposition entre comptes : l'ETag est l'empreinte du corps CALCULÉ pour la requête en
cours (avec son jeton d'authentification), pas une clé de cache. Un 304 n'est émis que si le corps
du compte courant est identique, octet pour octet, à celui que le navigateur détient déjà.

`Cache-Control: private, no-cache` par défaut : jamais de copie dans un cache partagé, et une
revalidation à chaque usage (pas de donnée périmée servie sans demander). Les vues qui posent leur
propre Cache-Control (ou no-store, comme les routes de PDF) ne sont pas touchées.

Placé juste après CorsMiddleware (voir settings.MIDDLEWARE) : un 304 ne conserve que quelques
en-têtes de la réponse d'origine, les en-têtes CORS doivent donc être ajoutés après lui.
"""
from django.utils.cache import get_conditional_response, patch_cache_control, set_response_etag


class EtagJsonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method not in ("GET", "HEAD") or response.status_code != 200 or response.streaming:
            return response
        if not response.get("Content-Type", "").startswith("application/json"):
            return response
        cache_control = response.get("Cache-Control", "")
        if "no-store" in cache_control:
            return response
        if not response.has_header("ETag"):
            set_response_etag(response)
        if not cache_control:
            patch_cache_control(response, private=True, no_cache=True)
        return get_conditional_response(request, etag=response.get("ETag"), response=response) or response
