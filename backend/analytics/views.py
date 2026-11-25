from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from users.ip import client_ip
from users.profils import profil_actif

from .funnel import entonnoir
from .models import AnalyticsEvent, EventName
from .semaine import demander_avis_seance

# Plafond de clés dans `properties` - un contexte minimal (ex. {"cursus_id": 3}) tient
# largement dedans ; au-delà, c'est le signe que ce point d'entrée est détourné vers
# autre chose que ce pour quoi il est prévu (voir AnalyticsEvent.properties).
_MAX_PROPERTIES_KEYS = 10
# Une valeur est un identifiant, un nombre, un mot : jamais un texte. Sans ce plafond, dix clés pouvaient
# porter chacune un texte de taille arbitraire.
_MAX_VALEUR = 200


class EvenementsThrottle(SimpleRateThrottle):
    """Plafond par compte, sinon par adresse : la route est ouverte à tous et écrit une ligne par appel. Elle
    n'avait aucune limite - un tiers pouvait remplir la table. 120 par minute laissent passer la navigation la
    plus rapide d'un élève, pas un script. Compteur en mémoire de chaque processus, comme les autres garde-fous
    de débit (voir access.quota.QuotaThrottle) ; coupé pendant les tests pour la même raison."""

    scope = "analytics_evenements"
    rate = "120/min"

    def allow_request(self, request, view):
        if not getattr(settings, "THROTTLE_PDF_ACTIF", True):
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        ident = f"u{request.user.pk}" if request.user.is_authenticated else (client_ip(request) or "inconnu")
        return self.cache_format % {"scope": self.scope, "ident": ident}


def _valeur_acceptable(valeur):
    if valeur is None or isinstance(valeur, (bool, int, float)):
        return True
    return isinstance(valeur, str) and len(valeur) <= _MAX_VALEUR


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([EvenementsThrottle])
def track_event(request):
    """
    Point d'entrée unique de la reco 5.3 de l'audit UX - volontairement permissif sur
    l'authentification (un visiteur anonyme génère la majorité des évènements utiles,
    ex. une recherche sans résultat avant toute connexion) mais strict sur la forme :
    un nom hors du vocabulaire fermé (EventName) ou des `properties` mal formées sont
    rejetés plutôt qu'enregistrés tels quels - pour que ce point d'entrée ne devienne
    jamais un sink de texte libre arbitraire (voir la docstring d'AnalyticsEvent).
    """
    name = request.data.get("name")
    if name not in EventName.values:
        return Response({"error": f"name invalide : {name!r}. Attendu {EventName.values}."}, status=400)

    properties = request.data.get("properties", {})
    if not isinstance(properties, dict) or len(properties) > _MAX_PROPERTIES_KEYS:
        return Response({"error": f"properties doit être un objet d'au plus {_MAX_PROPERTIES_KEYS} clés."}, status=400)
    if not all(len(str(cle)) <= _MAX_VALEUR and _valeur_acceptable(valeur) for cle, valeur in properties.items()):
        return Response(
            {"error": f"properties : valeurs simples (texte de {_MAX_VALEUR} caractères au plus, nombre, booléen)."},
            status=400,
        )

    AnalyticsEvent.objects.create(
        name=name,
        user=request.user if request.user.is_authenticated else None,
        properties=properties,
    )
    # {} explicite, jamais Response(status=201) sans corps : côté frontend,
    # apiRequest() lit response.json() dès que Content-Type dit json - un corps vide
    # y lève une SyntaxError plutôt que de résoudre proprement (déjà rencontré ailleurs
    # dans ce projet), même si trackEvent() l'avale de toute façon (fire-and-forget).
    return Response({}, status=201)


@api_view(["GET"])
def avis_seance_view(request):
    """GET : faut-il poser « Cette séance t'a aidé ? » à cet élève ? (voir analytics.semaine.demander_avis_seance)."""
    return Response({"demander": demander_avis_seance(request.user, profil_actif(request))})


@api_view(["GET"])
@permission_classes([IsAdminUser])
def entonnoir_view(request):
    """Entonnoir inscription -> paiement (voir analytics.funnel) - réservé à l'équipe :
    ce sont des chiffres internes, jamais servis à un élève."""
    try:
        jours = int(request.GET.get("jours", 30))
    except ValueError:
        return Response({"error": "jours doit être un entier."}, status=400)
    if not 1 <= jours <= 365:
        return Response({"error": "jours doit être compris entre 1 et 365."}, status=400)
    return Response(entonnoir(jours))
