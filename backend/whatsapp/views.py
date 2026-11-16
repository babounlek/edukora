from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services


@api_view(["GET"])
def my_status(request):
    return Response({"opted_in": services.is_opted_in(request.user)})


@api_view(["POST"])
def opt_in(request):
    # Sans numéro sur le compte (inscription par e-mail ou par Google), il n'y a nulle part où écrire :
    # l'accord était enregistré quand même, et chaque tour de l'ordonnanceur échouait sur ce compte.
    if not request.user.phone_number:
        return Response(
            {"error": "Ajoute d'abord ton numéro WhatsApp dans Mon compte.", "code": "numero_requis"}, status=400,
        )
    services.opt_in(request.user)
    return Response({"opted_in": True})


@api_view(["POST"])
def opt_out(request):
    services.opt_out(request.user)
    return Response({"opted_in": False})
