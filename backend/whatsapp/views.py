from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services


@api_view(["GET"])
def my_status(request):
    return Response({"opted_in": services.is_opted_in(request.user)})


@api_view(["POST"])
def opt_in(request):
    services.opt_in(request.user)
    return Response({"opted_in": True})


@api_view(["POST"])
def opt_out(request):
    services.opt_out(request.user)
    return Response({"opted_in": False})
