from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import paiement_a_reprendre, utilisateur_du_jeton


@require_http_methods(["GET", "POST"])
def desabonner_view(request, jeton):
    """Coupe les rappels quotidiens en un clic depuis le lien de l'e-mail - sans connexion :
    le jeton signé (voir services.jeton_desabonnement) désigne l'élève, et le seul effet
    possible est de lui écrire MOINS. Page volontairement minimale, lisible sur un
    téléphone d'entrée de gamme."""
    utilisateur = utilisateur_du_jeton(jeton)
    if utilisateur is None:
        titre, message, statut = "Lien invalide", "Ce lien de désabonnement n'est pas valide.", 400
    else:
        if utilisateur.rappels_actifs:
            utilisateur.rappels_actifs = False
            utilisateur.save(update_fields=["rappels_actifs"])
        titre = "C'est fait"
        message = "Tu ne recevras plus de rappel quotidien. Tu pourras les réactiver depuis ton compte."
        statut = 200

    corps = (
        "<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{escape(titre)}</title></head>"
        "<body style='font-family:sans-serif;max-width:32rem;margin:3rem auto;padding:0 1rem;line-height:1.5'>"
        f"<h1 style='font-size:1.4rem'>{escape(titre)}</h1><p>{escape(message)}</p>"
        f"<p><a href='{escape(settings.FRONTEND_URL)}'>Retour sur {escape(settings.SITE_NAME)}</a></p>"
        "</body></html>"
    )
    return HttpResponse(corps, status=statut)


@api_view(["GET"])
def paiement_a_reprendre_view(request):
    """La tentative de paiement que l'élève connecté n'a pas menée à terme, s'il y en a une
    - alimente la bannière « reprendre mon paiement » (voir services.paiement_a_reprendre,
    même règle que la relance par e-mail : les deux ne peuvent pas se contredire)."""
    transaction = paiement_a_reprendre(request.user)
    if transaction is None:
        return Response({"a_reprendre": False})
    return Response({
        "a_reprendre": True,
        "montant": transaction.amount,
        "cursus_id": transaction.plan.cursus_id,
        "statut": transaction.status,
        "depuis": transaction.created_at,
    })
