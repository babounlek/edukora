from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AnalyticsEvent, EventName

# Plafond de clés dans `properties` - un contexte minimal (ex. {"cursus_id": 3}) tient
# largement dedans ; au-delà, c'est le signe que ce point d'entrée est détourné vers
# autre chose que ce pour quoi il est prévu (voir AnalyticsEvent.properties).
_MAX_PROPERTIES_KEYS = 10


@api_view(["POST"])
@permission_classes([AllowAny])
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
