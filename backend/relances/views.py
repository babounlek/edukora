from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AbonnementPush
from .push import push_configure
from .bilan_parent import utilisateur_du_jeton_bilan
from .services import paiement_a_reprendre, utilisateur_du_jeton

# Garde-fous sur ce que le navigateur envoie : un point d'entrée ouvert à tout compte connecté
# ne doit pas devenir un endroit où ranger des chaînes de taille arbitraire.
_ENDPOINT_MAX = 2000
_CLE_MAX = 200


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
    return _page_minimale(titre, message, statut)


@require_http_methods(["GET", "POST"])
def desabonner_bilan_view(request, jeton):
    """Coupe le bilan hebdomadaire du parent en un clic depuis son e-mail - même principe que
    desabonner_view : jeton signé, pas de connexion, seul effet possible : écrire MOINS."""
    utilisateur = utilisateur_du_jeton_bilan(jeton)
    if utilisateur is None:
        return _page_minimale("Lien invalide", "Ce lien de désabonnement n'est pas valide.", 400)
    if utilisateur.bilan_parent_actif:
        utilisateur.bilan_parent_actif = False
        utilisateur.save(update_fields=["bilan_parent_actif"])
    return _page_minimale(
        "C'est fait", "Tu ne recevras plus le bilan de la semaine. Tu pourras le réactiver depuis ton compte.", 200,
    )


def _page_minimale(titre, message, statut):
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


@api_view(["GET"])
def push_cle_view(request):
    """La clé publique VAPID dont le navigateur a besoin pour s'abonner, ou `actif: false` quand
    le push n'est pas configuré - l'application masque alors l'interrupteur au lieu de proposer
    un réglage qui ne pourrait rien faire (voir relances.push.push_configure)."""
    if not push_configure():
        return Response({"actif": False, "cle": ""})
    return Response({"actif": True, "cle": settings.VAPID_PUBLIC_KEY})


@api_view(["POST"])
def push_abonner_view(request):
    """Enregistre l'appareil qui vient d'accepter les notifications. L'adresse (`endpoint`) est
    propre à un navigateur sur un appareil : si elle existe déjà, elle passe au compte
    connecté - un téléphone partagé qui change de compte ne doit pas continuer à recevoir les
    rappels de l'ancien."""
    if not push_configure():
        return Response({"error": "Les notifications ne sont pas activées sur ce serveur."}, status=409)
    endpoint = request.data.get("endpoint")
    cles = request.data.get("keys") or {}
    p256dh = cles.get("p256dh") if isinstance(cles, dict) else None
    auth = cles.get("auth") if isinstance(cles, dict) else None
    valide = (
        isinstance(endpoint, str) and endpoint.startswith("https://") and len(endpoint) <= _ENDPOINT_MAX
        and isinstance(p256dh, str) and 0 < len(p256dh) <= _CLE_MAX
        and isinstance(auth, str) and 0 < len(auth) <= _CLE_MAX
    )
    if not valide:
        return Response({"error": "Abonnement invalide."}, status=400)
    AbonnementPush.objects.update_or_create(
        endpoint=endpoint, defaults={"user": request.user, "p256dh": p256dh, "auth": auth},
    )
    return Response({"abonne": True}, status=201)


@api_view(["POST"])
def push_desabonner_view(request):
    """Retire l'appareil des notifications - seulement s'il appartient au compte connecté."""
    endpoint = request.data.get("endpoint")
    if not isinstance(endpoint, str):
        return Response({"error": "Abonnement invalide."}, status=400)
    AbonnementPush.objects.filter(user=request.user, endpoint=endpoint).delete()
    return Response({"abonne": False})
